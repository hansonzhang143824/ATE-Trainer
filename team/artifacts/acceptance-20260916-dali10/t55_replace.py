#!/usr/bin/env python3
"""t55 REPLACE: insert the delivered TM600/TM601 payload into the target tree.

SAFETY CONTRACT (all enforced in code, any failure => no/rolled-back write):
  1. byte-mode read/write only (the target is a DLP TSZ container; text mode corrupts CRLF)
  2. region identity asserted BEFORE writing:
       payload L1  == target L8879 (the "// ====" separator)
       payload L2  == target L8880 (the "// t5 implementation payload" header)
       payload L566 == "}"  == target L9353 (end of TM601) and target L9354 is empty
  3. target is backed up byte-for-byte before any write
  4. after writing: re-read and verify size/sha256/BOM/CRLF/lone-LF/content-keys/SetOn/function presence
  5. any post-write mismatch => restore the backup automatically and exit non-zero

Usage:  python t55_replace.py            # dry run (verify only, no write)
        python t55_replace.py --apply    # perform the replacement
"""
import hashlib
import os
import shutil
import sys
import re
import datetime

RUN = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(RUN, "implementation-payload-TM600-TM601.cpp")
TARGET = r"D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"
START_LINE = 8879          # 1-based, first line replaced in the target
END_LINE = 9353            # 1-based, last line replaced in the target
EXPECTED_TARGET_PRE = "15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a"
APPLY = "--apply" in sys.argv


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read_bytes(p):
    with open(p, "rb") as fh:
        return fh.read()


def decode_lines(b):
    """BOM-aware decode, split on \n keeping the \r (CRLF preserved on re-join)."""
    txt = b.decode("utf-8-sig")
    return txt.split("\n")


def main():
    tgt_before = read_bytes(TARGET)
    pay_b = read_bytes(PAYLOAD)
    print("target  : %d B  %s" % (len(tgt_before), sha(tgt_before)))
    print("payload : %d B  %s" % (len(pay_b), sha(pay_b)))

    ok = True
    if sha(tgt_before) != EXPECTED_TARGET_PRE:
        print("FAIL: target hash != expected pre-state (delivered tree already changed?)")
        ok = False

    tl = decode_lines(tgt_before)
    pl = decode_lines(pay_b)
    print("target lines %d   payload lines %d" % (len(tl), len(pl)))

    checks = [
        ("payload L1  == target L%d" % START_LINE, pl[0] == tl[START_LINE - 1]),
        ("payload L2  == target L%d" % (START_LINE + 1), pl[1] == tl[START_LINE]),
        ("payload L566 == target L%d" % END_LINE, pl[565] == tl[END_LINE - 1]),
        ("target L%d is empty" % (END_LINE + 1), tl[END_LINE].strip() == ""),
        ("payload L566 is the closing brace", pl[565].rstrip("\r") == "}"),
        ("target L%d is the closing brace" % END_LINE, tl[END_LINE - 1].rstrip("\r") == "}"),
    ]
    for label, res in checks:
        print("  %-42s %s" % (label, "OK" if res else "FAIL"))
        ok = ok and res

    # content-key preconditions on the payload
    st_pay = re.sub(r"//[^\n]*", "", pay_b.decode("utf-8-sig"))
    for key, want in (("K48_ACM5_AMP_REF", 1), ("K76_ACM_BST", 1),
                      ("K109_BUSL1_PB0", 0), ("K110_ACM18_BST", 0), ("K46_BUS", 0)):
        got = len(re.findall(re.escape(key), st_pay))
        print("  payload exec %-18s = %d (want %d) %s" % (key, got, want, "OK" if got == want else "FAIL"))
        ok = ok and got == want
    setons = re.findall(r"\.SetOn\([^;]*\);", st_pay)
    print("  payload SetOn calls = %d (want 2)" % len(setons))
    ok = ok and len(setons) == 2

    if not ok:
        print("\nDRY RUN: preconditions FAILED -- nothing written.")
        return 2

    new_lines = tl[:START_LINE - 1] + pl[:566] + tl[END_LINE:]
    new_txt = "\n".join(new_lines)
    new_b = b"\xef\xbb\xbf" + new_txt.encode("utf-8")
    print("\nplanned result: %d B  %s" % (len(new_b), sha(new_b)))

    if not APPLY:
        print("DRY RUN complete -- mapping verified, nothing written.  (use --apply)")
        return 0

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bdir = os.path.join(RUN, "backups", "t55-target-" + stamp)
    os.makedirs(bdir, exist_ok=True)
    shutil.copy2(TARGET, os.path.join(bdir, "test.cpp"))
    print("backup -> %s" % bdir)

    with open(TARGET, "wb") as fh:
        fh.write(new_b)

    # post-write verification
    after = read_bytes(TARGET)
    at = after.decode("utf-8-sig")
    st_after = re.sub(r"//[^\n]*", "", at)
    good = True
    def chk(label, cond):
        nonlocal_good = cond
        print("  %-46s %s" % (label, "OK" if cond else "FAIL"))
        return nonlocal_good
    good &= chk("hash matches planned", sha(after) == sha(new_b))
    good &= chk("BOM present", after[:3] == b"\xef\xbb\xbf")
    good &= chk("0 lone LF", at.count("\n") - at.count("\r\n") == 0)
    good &= chk("TM600_HS_RDSON present", "TM600_HS_RDSON" in at)
    good &= chk("TM601_LS_RDSON present", "TM601_LS_RDSON" in at)
    good &= chk("exec K48_ACM5_AMP_REF == 1", len(re.findall(r"K48_ACM5_AMP_REF", st_after)) == 1)
    good &= chk("exec K76_ACM_BST == 1", len(re.findall(r"K76_ACM_BST", st_after)) == 1)
    good &= chk("exec K109_BUSL1_PB0 == 0", len(re.findall(r"K109_BUSL1_PB0", st_after)) == 0)
    good &= chk("exec K110_ACM18_BST == 0", len(re.findall(r"K110_ACM18_BST", st_after)) == 0)

    if not good:
        shutil.copy2(os.path.join(bdir, "test.cpp"), TARGET)
        print("\nROLLBACK: post-write verification failed; original restored.")
        return 3

    print("\nREPLACE OK: %d B  %s" % (len(after), sha(after)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
