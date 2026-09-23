import os,hashlib,time
for p in [r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\t8-review-findings.json',
          r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\t8-review-findings.md',
          r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp',
          r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\implementation-manifest.json',
          r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\t7-selfcheck.md']:
    b=open(p,'rb').read()
    print('%-28s %8d  %s  mtime=%s' % (os.path.basename(p), len(b), hashlib.sha256(b).hexdigest(),
          time.strftime('%H:%M:%S', time.localtime(os.stat(p).st_mtime))))
