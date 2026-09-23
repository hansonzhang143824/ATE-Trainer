"""Regression guard for the schematic staging directory's DACL.

Why this file exists: the generator used `tempfile.mkdtemp`, whose 0o700 mode becomes
an explicit, PROTECTED DACL on Windows. A protected DACL blocks inheritance, so the
staging directory never received the workspace's inheritable sandbox write grant and a
write-restricted child could neither write nor delete inside it — the whole
`PermissionError` / `WinError 5` investigation. The first test pins the observable
symptom (an inherited ACE must be present); the second pins the cause (the protected
0o700 path must not come back).

Run:  python -m unittest test_staging_directory -v   (from the scripts directory)
"""
import importlib.util
import io
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import tokenize
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "generate_schematic_txt.py"
IS_WINDOWS = sys.platform == "win32"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_schematic_txt", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def icacls(target) -> str:
    printed = subprocess.run(["icacls", str(target)], capture_output=True, encoding="utf-8", errors="replace")
    return printed.stdout or ""


def significant_code(path: Path) -> str:
    """The file's EXECUTABLE tokens: strings and comments stripped with a tokenizer.

    A substring search would fire on the docstrings that legitimately name
    `tempfile.mkdtemp` to explain why it is not used (that mistake made the first
    version of this guard fail against its own subject).
    """
    skip = {"STRING", "FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END", "COMMENT",
            "NL", "NEWLINE", "INDENT", "DEDENT", "ENCODING", "ENDMARKER"}
    with io.StringIO(path.read_text(encoding="utf-8-sig")) as handle:
        return " ".join(
            token.string
            for token in tokenize.generate_tokens(handle.readline)
            if tokenize.tok_name[token.type] not in skip
        )


class StagingDirectoryDacl(unittest.TestCase):
    def test_the_staging_directory_name_keeps_its_documented_shape(self):
        generator = load_generator()
        parent = Path(tempfile.mkdtemp(prefix="ptc-stage-parent-"))
        try:
            with generator.staging_directory(parent) as stage:
                self.assertTrue(stage.is_dir(), stage)
                self.assertRegex(stage.name, r"^schematic-full-[0-9a-f]{8}$")
            self.assertFalse(stage.exists(), "cleanup is best effort but must succeed on a writable parent")
        finally:
            shutil.rmtree(parent, ignore_errors=True)

    @unittest.skipUnless(IS_WINDOWS, "DACL inheritance is a Windows behaviour")
    def test_the_staging_directory_inherits_the_workspace_write_grant(self):
        """Workspace-equivalent: the parent carries the sandbox capability ACE.

        An earlier version of this test used an mkdtemp parent, which only proves the
        system temp ACL propagates — it would still pass if the capability SID this
        project's sandbox relies on were lost. The parent here is created inside the
        repository exactly the way the generator's own output directory is, and the
        assertion names the capability SID the boundary uses.
        """
        generator = load_generator()
        parent = Path(generator.ROOT).resolve() / "team" / f"_dacl-staging-test-{secrets.token_hex(4)}"
        parent.mkdir(parents=True, exist_ok=False)
        try:
            capability = set(re.findall(r"S-1-4-[0-9-]+", icacls(parent)))
            with generator.staging_directory(parent) as stage:
                listing = icacls(stage)
                self.assertIn("(I)", listing, f"the staging directory has no inherited ACE:\n{listing}")
                for sid in capability:
                    self.assertIn(sid, listing, f"the staging directory did not inherit {sid} from its parent:\n{listing}")
        finally:
            shutil.rmtree(parent, ignore_errors=True)

    def test_the_protected_mkdtemp_path_cannot_come_back(self):
        code = significant_code(GENERATOR)
        self.assertNotIn("mkdtemp", code, "mkdtemp's 0o700 creates a protected DACL that blocks the sandbox write grant")
        self.assertNotIn("TemporaryDirectory", code, "TemporaryDirectory uses mkdtemp under the hood")
        self.assertIn("staging_directory", code, "the replacement helper must exist and be used")
        self.assertRegex(GENERATOR.read_text(encoding="utf-8-sig"), re.compile(r"stage\.mkdir\(parents=True,\s*exist_ok=False\)"))

    def test_no_other_runtime_script_uses_the_protected_mkdtemp_path(self):
        """Repo-wide guard for the same bug class, which both reviewers asked for.

        Any *runtime* stage script that reaches for `tempfile.mkdtemp` /
        `TemporaryDirectory` inside a confined step gets the same protected 0o700 DACL
        and the same unwritable staging directory. Test modules are excluded on
        purpose: their fixtures use mkdtemp legitimately and they run unconfined, so
        they cannot fail this way.
        """
        offenders = sorted(
            path.name
            for path in HERE.glob("*.py")
            if not path.name.startswith("test_")
            and any(name in significant_code(path) for name in ("mkdtemp", "TemporaryDirectory"))
        )
        self.assertEqual(
            offenders, [],
            "runtime scripts must not use mkdtemp/TemporaryDirectory under the confined sandbox: " + ", ".join(offenders),
        )


if __name__ == "__main__":
    unittest.main()
