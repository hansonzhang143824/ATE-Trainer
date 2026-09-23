import json
import tempfile
import unittest
from pathlib import Path

import trial_directory


class TrialDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.original = trial_directory.ARTIFACT_ROOT
        self.temp = tempfile.TemporaryDirectory()
        trial_directory.ARTIFACT_ROOT = Path(self.temp.name) / "artifacts"

    def tearDown(self):
        trial_directory.ARTIFACT_ROOT = self.original
        self.temp.cleanup()

    def manifest(self, name: str, tm: str):
        folder = trial_directory.ARTIFACT_ROOT / name
        folder.mkdir(parents=True)
        (folder / "input-manifest.json").write_text(json.dumps({"tm": tm}), encoding="utf-8")
        return folder

    def test_returns_standard_path_when_no_trial_exists(self):
        self.assertEqual(trial_directory.resolve("TM107").name, "tm107-ptc")

    def test_reuses_only_matching_trial(self):
        matching = self.manifest("tm109-ptc-v2", "TM109")
        self.manifest("tm109-unrelated", "TM108")
        self.assertEqual(trial_directory.resolve("TM109"), matching.resolve())

    def test_rejects_two_matching_trials(self):
        self.manifest("tm108-ptc", "TM108")
        self.manifest("tm108-ptc-v2", "TM108")
        with self.assertRaisesRegex(ValueError, "multiple valid"):
            trial_directory.resolve("TM108")


if __name__ == "__main__":
    unittest.main()
