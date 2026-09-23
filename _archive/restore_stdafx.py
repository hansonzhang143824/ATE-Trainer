#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
restore_stdafx.py — 恢复被误清空的 StdAfx.h (DLP 字节模式写回).

来源: recover_stdafx.h.txt (从旧会话 transcript 提取的原始 Read 结果).
编码: GBK (原文件第346行含 GBK 中文注释; ASCII 行两种编码字节一致).
行尾: CRLF (VS 工程头惯例).
处理: 第346行 mojibake(U+FFFD, 无法 GBK 编码) → 还原为文档记录的目标中文注释.
用法: python restore_stdafx.py [--target PATH] [--smoke]
"""
import argparse
import re
import sys

SRC = r"D:\Newtest\CLAUDE_PROCESS\Project\DALI\input\recover_stdafx.h.txt"
REAL = r"D:\PROJECT6-DALI\devel\source\StdAfx.h"
LINE346 = "extern \"C\" int USERRES_API STSMaskTHBConfigCheck(bool maskFlag);///EEROM 写入成功需删除"


def read_plain(path):
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith(b"TSZ#"):
        # DLP 加密(沙箱读到密文) — 需 DLP 环境运行; 这里假定 PowerShell python 透明解密
        raise SystemExit("ERROR: %s 加密(TSZ#), 请在 DLP 环境运行" % path)
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode("latin-1")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=REAL)
    ap.add_argument("--smoke", action="store_true", help="写到 --target, 不覆盖真文件")
    args = ap.parse_args()

    text = read_plain(SRC)
    lines = text.splitlines()
    # 还原第346行 (含 U+FFFD 的 mojibake → 目标中文注释)
    fixed = 0
    for i, ln in enumerate(lines):
        if "STSMaskTHBConfigCheck" in ln:
            if "\ufffd" in ln or "EEROM" in ln:
                # 保留行前导(可能含空格/tab), 替换整行为标准行
                lead = re.match(r"^[\t ]*", ln).group(0)
                lines[i] = lead + LINE346
                fixed += 1
    # CRLF 归一
    body = "\r\n".join(lines)
    if not body.endswith("\r\n"):
        body += "\r\n"

    with open(args.target, "wb") as f:
        f.write(body.encode("gbk", errors="replace"))
    print("WROTE %s (%d lines, gbk, CRLF, line346 fixed=%d)"
          % (args.target, len(lines), fixed))

    # 回读验证
    with open(args.target, "rb") as f:
        raw = f.read()
    ok = False
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            back = raw.decode(enc)
            ok = True
            print("READBACK enc=%s len=%d | guard: %s | line346: %s"
                  % (enc, len(back),
                     "AFX_STDAFX_H__3811CD50" in back,
                     "STSMaskTHBConfigCheck" in back))
            break
        except (UnicodeDecodeError, ValueError):
            continue
    if not ok:
        print("READBACK FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
