# -*- coding: utf-8 -*-
"""TM103 preparation: byte-exact backup + staged patch of D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp.
Span-limited: only the TM103 body lines (1-based 1826..1852) may change.
"""
import hashlib, sys, shutil
from pathlib import Path

SRC = Path(r"D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp")
ART = Path(r"D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm103-ptc\implementation")
BACKUP = ART / "backup" / "test.cpp.pre-tm103.bak"
STAGE = ART / "staging" / "test.cpp.tm103"

def sha(b): return hashlib.sha256(b).hexdigest()

data = SRC.read_bytes()
pre_sha = sha(data)
assert data[:3] == b"\xef\xbb\xbf", "expected UTF-8 BOM"
assert data.count(b"\n") == data.count(b"\r\n"), "expected CRLF-only line endings"

lines = data[3:].split(b"\r\n")
assert len(lines) == 9086, "unexpected line count %d" % len(lines)

# --- signed method contract: phaseStateTable PH-05 and powerDownPlan orderedActions V1..V5
NEW_VDM_FORCE = '    VDM_SDA_ACM.Set(FV, 1, ACM200_3p6V, ACM200_1UA, ACM200_RELAY_ON);'.encode()
NEW_V1 = '    VDM_SDA_ACM.Set(FV, 0, ACM200_3p6V, ACM200_1UA, ACM200_RELAY_ON);'.encode()
NEW_V2 = '    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);'.encode()
NEW_V4 = '    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'.encode()
NEW_V5 = '    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);'.encode()

EDITS = [
    (1829, 1829, b"10UA", b"1UA", "comment: signed range is the ACM200_1UA current range"),
    (1831, 1831, '    VDM_SDA_ACM.Set(FV, 1, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);'.encode(), NEW_VDM_FORCE, "PH-05"),
    (1840, 1840, '    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);'.encode(), NEW_V1, "PH-08 V1"),
    (1841, 1841, '    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);'.encode(), NEW_V2, "PH-08 V2"),
    (1843, 1843, '    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);'.encode(), NEW_V4, "PH-08 V4"),
    (1844, 1844, '    VDM_SDA_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);'.encode(), NEW_V5, "PH-08 V5"),
]

before = list(lines)
for lo, hi, old, new, why in EDITS:
    hits = lines[lo].count(old)
    assert hits == 1, "pattern %r matched %d times on line %d" % (old, hits, lo + 1)
    lines[lo] = lines[lo].replace(old, new)
    print("edit line %d (%s)" % (lo + 1, why))

changed = [i + 1 for i in range(len(before)) if before[i] != lines[i]]
print("changed 1-based lines:", changed)
assert changed == [1830, 1832, 1841, 1842, 1844, 1845], changed
assert [i for i in range(1801, 1853) if before[i] != lines[i]] == [1829, 1831, 1840, 1841, 1843, 1844]
for i in range(len(before)):
    if i not in (1829, 1831, 1840, 1841, 1843, 1844):
        assert before[i] == lines[i]

post = b"\xef\xbb\xbf" + b"\r\n".join(lines)
assert post.count(b"\n") == post.count(b"\r\n") and post[:3] == b"\xef\xbb\xbf"
assert len(lines) == 9086
post_sha = sha(post)

BACKUP.parent.mkdir(parents=True, exist_ok=True)
STAGE.parent.mkdir(parents=True, exist_ok=True)
BACKUP.write_bytes(data)
STAGE.write_bytes(post)
print("backup ", BACKUP, BACKUP.stat().st_size)
print("staged ", STAGE, STAGE.stat().st_size)
print("pre_sha256 ", pre_sha)
print("post_sha256", post_sha)
print("byte_delta", len(post) - len(data))
