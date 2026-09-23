#!/usr/bin/env python3
"""Create a bounded raw OVERVIEW source view, never a DFT semantic verdict.

CLI: --run-id ID --tm TM109 [--tm TM110]. Only run/input is accessed.
The workspace is this trusted script's parent directory, not the shell cwd.
The output has immutable identity: repeated identical requests reuse exact bytes;
different content or a different TM selection cannot overwrite an existing view.
Host must bind stdout sha256/sourceSha256 in its own evidence and own the gate.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import threading
import zipfile

from material_plaintext_hash import sha256_plaintext

MAX_BYTES = 128 * 1024
MAX_WORKBOOK = 32 * 1024 * 1024
MAX_EXPANDED = 64 * 1024 * 1024
DEVICE = re.compile(r"^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)", re.I)
DIGEST = re.compile(r"^[a-f0-9]{64}$")


class Blocked(ValueError):
    pass


def safe(root: Path, file: Path, *, required=True):
    """Lexical containment plus every ancestor's link/reparse/identity checks."""
    file = Path(os.path.abspath(file))
    if not file.is_relative_to(root):
        raise Blocked("path escapes workspace")
    for part in (file, *file.parents):
        name = part.name
        if name and (DEVICE.match(name) or name.endswith((".", " ")) or re.search(r'[<>:"|?*]', name)):
            raise Blocked("unsafe Windows path")
        try:
            info = part.lstat()
        except FileNotFoundError:
            if part == file and not required:
                continue
            raise Blocked("required material path is absent")
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise Blocked("links and reparse points are forbidden")
        if part == file and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
            raise Blocked("material must be a private regular file")
    return file


def read_json(root, file):
    safe(root, file)
    if file.stat().st_size > 2 * 1024 * 1024:
        raise Blocked("metadata exceeds budget")
    return json.loads(file.read_text(encoding="utf-8-sig"))


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def identity(root, run_id, tms):
    run_rel = f"Training_Materials/runs/{run_id}"
    run = root / run_rel
    context = read_json(root, run / "run.json")
    if (context.get("schemaVersion") != 1 or context.get("runId") != run_id
            or context.get("mode") != "training" or context.get("profileSource") != "draft"
            or context.get("orchestrationSource") != "draft"
            or context.get("releaseId") is not None
            or str(context.get("artifactRoot", "")).replace("\\", "/") != run_rel):
        raise Blocked("invalid training run identity")
    manifest = read_json(root, run / "material-manifest.json")
    files, policies = manifest.get("files"), manifest.get("policies")
    if (manifest.get("schemaVersion") != 2 or manifest.get("runId") != run_id
            or not isinstance(files, list) or not isinstance(policies, list)
            or not isinstance(manifest.get("testItems"), list)
            or not set(tms).issubset(manifest["testItems"])):
        raise Blocked("invalid material manifest identity or TM scope")
    try:
        fingerprint = {"materials": [{"source": e["source"], "sha256": e["sha256"]} for e in files],
                       "policies": [{"path": e["path"], "sha256": e["sha256"]} for e in policies]}
        if any(not isinstance(e["sha256"], str) or not DIGEST.fullmatch(e["sha256"]) for e in files + policies):
            raise Blocked("invalid manifest digest")
        if hashlib.sha256(encoded(fingerprint)).hexdigest() != manifest.get("cacheKey"):
            raise Blocked("material manifest fingerprint mismatch")
    except (KeyError, TypeError) as exc:
        raise Blocked("malformed material manifest") from exc
    workbook_rel = f"{run_rel}/input/Dali_testmode.xlsx"
    entries = [e for e in files if e.get("path") == workbook_rel]
    if (len(entries) != 1 or entries[0].get("view") != "python-plaintext"
            or entries[0].get("source") != "Training_Materials/Input_GlobalMaterial/Dali_testmode.xlsx"):
        raise Blocked("missing or ambiguous canonical workbook manifest entry")
    workbook = safe(root, root / workbook_rel)
    if workbook.stat().st_size > MAX_WORKBOOK:
        raise Blocked("workbook exceeds byte budget")
    digest = sha256_plaintext(workbook)
    if digest != entries[0]["sha256"]:
        raise Blocked("frozen workbook hash mismatch")
    return run, workbook, manifest["cacheKey"], digest


def cell_record(cell):
    value = cell.value
    kind = type(value).__name__
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        value = value.isoformat()
    if not (value is None or isinstance(value, (str, int, float, bool))):
        raise Blocked(f"unsupported raw cell value at {cell.coordinate}")
    return {"coordinate": cell.coordinate, "value": value, "dataType": cell.data_type,
            "valueType": kind, "numberFormat": cell.number_format}


def source_rows(workbook, tms):
    # Bound ZIP expansion before openpyxl allocates cells/styles/shared strings.
    with zipfile.ZipFile(workbook) as archive:
        members = archive.infolist()
        if len(members) > 2048 or sum(x.file_size for x in members) > MAX_EXPANDED:
            raise Blocked("workbook ZIP expansion exceeds budget")
    import openpyxl
    book = openpyxl.load_workbook(workbook, data_only=False, read_only=False, keep_links=False)
    try:
        if "OVERVIEW" not in book.sheetnames:
            raise Blocked("workbook has no OVERVIEW sheet")
        sheet = book["OVERVIEW"]
        if sheet.max_row > 100000 or sheet.max_column > 256 or sheet.max_row * sheet.max_column > 300000:
            raise Blocked("OVERVIEW dimensions exceed scan budget")
        matches = {tm: [] for tm in tms}
        for row in sheet.iter_rows(min_col=1, max_col=1):
            cell = row[0]
            label = str(cell.value).strip().upper()
            if label in matches:
                matches[label].append(cell.row)
        items = []
        for tm, hits in matches.items():
            if not hits:
                raise Blocked(f"{tm} missing from OVERVIEW column A")
            if len(hits) != 1 or hits[0] == 1:
                raise Blocked(f"{tm} ambiguous OVERVIEW source rows")
            matched = hits[0]
            selected = {1, *range(max(1, matched - 2), min(sheet.max_row, matched + 2) + 1)}
            # Never show a partial merged range or silently drop its anchor.
            while True:
                expanded = set(selected)
                for area in sheet.merged_cells.ranges:
                    if any(area.min_row <= r <= area.max_row for r in selected):
                        expanded.update(range(area.min_row, area.max_row + 1))
                if len(expanded) > 200:
                    raise Blocked("merged source context exceeds row budget")
                if expanded == selected:
                    break
                selected = expanded
            items.append({"tm": tm, "sheet": "OVERVIEW", "matchedRow": matched, "headerRows": [1],
                          "contextRowNumbers": sorted(selected),
                          "mergedRanges": sorted(str(a) for a in sheet.merged_cells.ranges
                                                 if any(a.min_row <= r <= a.max_row for r in selected)),
                          "rows": [{"row": r, "cells": [cell_record(sheet.cell(r, c))
                                    for c in range(1, sheet.max_column + 1)]} for r in sorted(selected)]})
            if len(encoded(items)) > MAX_BYTES:
                raise Blocked("source view exceeds 128 KiB; nothing was truncated")
        return items
    finally:
        book.close()


def prepare(root, run_id, tms):
    if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", run_id)
            or DEVICE.match(run_id) or run_id.endswith(".")):
        raise Blocked("unsafe run id")
    if not tms or any(not re.fullmatch(r"TM[0-9]+", tm) for tm in tms):
        raise Blocked("invalid TM")
    tms = sorted(set(tms))
    run, workbook, cache_key, digest = identity(root, run_id, tms)
    view = {"schemaVersion": 1, "kind": "ptc-dft-source-view", "runId": run_id,
            "testItems": tms, "materialCacheKey": cache_key,
            "source": {"path": workbook.relative_to(root).as_posix(), "sha256": digest,
                       "view": "python-plaintext"},
            "selection": {"sheet": "OVERVIEW", "keyColumn": "A", "authority": "scripts/dft_source.py:rows_for",
                          "scope": "matching raw rows, first-row header and adjacent context; not the entire workbook",
                          "formulaValues": "formula text preserved; not evaluated or replaced by cached values"},
            "items": source_rows(workbook, tms)}
    payload = encoded(view) + b"\n"
    if len(payload) > MAX_BYTES:
        raise Blocked("source view exceeds 128 KiB; nothing was truncated")
    # Detect source/identity changes across extraction before committing any file.
    _, _, current_key, current_digest = identity(root, run_id, tms)
    if current_key != cache_key or current_digest != digest:
        raise Blocked("material changed while reading source rows")
    output = safe(root, run / "input/dft-source-view.json", required=False)
    reused = False
    try:
        with output.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        safe(root, output)
        if output.stat().st_size > MAX_BYTES or output.read_bytes() != payload:
            raise Blocked("existing source view differs; immutable snapshot not overwritten")
        reused = True
    return {"status": "SOURCE_VIEW", "runId": run_id, "path": output.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(payload).hexdigest(), "sourceSha256": digest,
            "testItems": tms, "reused": reused, "bytes": len(payload)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--tm", required=True, action="append")
    args = parser.parse_args()
    try:
        result = prepare(Path(os.path.abspath(__file__)).parent.parent, args.run_id, args.tm)
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, ensure_ascii=False), flush=True)
        return 2
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    def timeout():
        print('{"status":"BLOCKED","reason":"source view exceeded 25-second command budget"}', flush=True)
        os._exit(2)
    watchdog = threading.Timer(25, timeout)
    watchdog.daemon = True
    watchdog.start()
    try:
        raise SystemExit(main())
    finally:
        watchdog.cancel()
