# -*- coding: utf-8 -*-
import hashlib, sys
from pathlib import Path

TARGET = Path(r"D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp")
data = TARGET.read_bytes()
print("bytes", len(data))
print("bom", data[:3] == b"\xef\xbb\xbf", data[:3])
print("crlf", data.count(b"\r\n"), "lone_lf", data.count(b"\n") - data.count(b"\r\n"))
print("sha256_raw", hashlib.sha256(data).hexdigest())
lines = data.split(b"\r\n")
print("lines", len(lines))
for i in range(1795, 1855):
    print(i + 1, repr(lines[i].decode("utf-8")))
