# -*- coding: utf-8 -*-
"""搜索 fpvi_gp_valid 在 DALI / 工厂 / SDK 的声明与定义"""
import io, glob, os

def scan(dirs, pats=('*.cpp', '*.h')):
    hits = {}
    for d in dirs:
        for p in pats:
            for f in glob.glob(os.path.join(d, p)):
                try:
                    t = io.open(f, encoding='utf-8-sig', errors='ignore').read()
                except Exception:
                    continue
                if 'fpvi_gp_valid' in t:
                    hits[f] = []
                    for ln, line in enumerate(t.splitlines(), 1):
                        if 'fpvi_gp_valid' in line:
                            hits[f].append((ln, line.strip()[:130]))
    return hits

print("=" * 70)
print("1) DALI source:")
r = scan([r'D:\PROJECT6-DALI\devel\source'])
for f, lines in r.items():
    print("  ", f)
    for ln, line in lines[:8]:
        print("      L%d: %s" % (ln, line))

print("=" * 70)
print("2) 工厂 D:\\Newtest\\CLAUDE_PROCESS\\Library-Functions\\test_method:")
r = scan([r'D:\Newtest\CLAUDE_PROCESS\Library-Functions\Test_Method'])
for f, lines in r.items():
    print("  ", f)
    for ln, line in lines[:8]:
        print("      L%d: %s" % (ln, line))

print("=" * 70)
print("3) SDK D:\\Newtest\\STS8300:")
r = scan([r'D:\Newtest\STS8300'])
for f, lines in r.items():
    print("  ", f)
    for ln, line in lines[:8]:
        print("      L%d: %s" % (ln, line))
