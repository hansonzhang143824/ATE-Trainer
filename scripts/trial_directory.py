"""Deterministic per-TM trial directory selection for the PTC runner."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "team" / "artifacts"


def standard_name(tm: str) -> str:
    return f"{tm.lower()}-ptc"


def manifest_tm(directory: Path) -> str | None:
    try:
        value = json.loads((directory / "input-manifest.json").read_text(encoding="utf-8"))
        tm = value.get("tm")
        return tm.upper() if isinstance(tm, str) else None
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def resolve(tm: str, requested: str | None = None) -> Path:
    """Return one safe trial directory without asking for ordinary setup.

    A caller-provided directory wins.  Without one, reuse the sole existing
    directory whose manifest belongs to this TM; otherwise return the standard
    directory to be created by prepare-input.  Multiple valid histories are a
    real ambiguity and must be reported.
    """
    tm = tm.upper()
    if requested:
        candidate = Path(requested).resolve()
        root = ARTIFACT_ROOT.resolve()
        if candidate != root and root not in candidate.parents:
            raise ValueError("trial directory must be inside team/artifacts")
        return candidate
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    candidates = [path for path in ARTIFACT_ROOT.glob(f"{tm.lower()}-ptc*") if path.is_dir() and manifest_tm(path) == tm]
    if len(candidates) == 1:
        return candidates[0].resolve()
    if len(candidates) > 1:
        raise ValueError(f"multiple valid trial directories for {tm}: {', '.join(str(path) for path in candidates)}")
    return (ARTIFACT_ROOT / standard_name(tm)).resolve()
