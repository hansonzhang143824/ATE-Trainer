# -*- coding: utf-8 -*-
"""并入 schematic-expert ②③（幂等）：
  ② **可检索性缺口**：§附六 标题须**并列英文名** `prose-substring ≠ structural presence`
     （否则按英文名 grep = 0 命中 ⇒ 后来者可能据此断言"该规则不存在" ⇒ 正是第七类的失效）；
  ③ **分类边界**：第 1–7 类都属"检测"阶段；"检测对了但值被抄错"属"搬运"阶段，
     由既有规则（哈希须脚本生成、禁手抄/转述）覆盖 ⇒ **不新增第八类**（防膨胀 + 防被读成有缺口）。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
before = len(t.encode('utf-8'))
print('登记 %d B' % os.path.getsize(REG))

# ② 标题并列英文名
EN = 'prose-substring ≠ structural presence'
OLD_H = '## 附六｜第七类：假匹配（假阳性）— 文案串 ≠ 结构存在'
NEW_H = OLD_H + '（`prose-substring ≠ structural presence`）'
if EN in t:
    print('  ② 已含英文名（幂等）')
elif OLD_H in t:
    t = t.replace(OLD_H, NEW_H, 1)
    print('  ② 已补英文名')
else:
    print('  WARN: ② 标题锚点未命中')

# ③ 边界说明（追加到 §附六·补 末尾 = 本文件当前末尾之前，故直接追加一节）
MARK3 = '### 附六·边界｜第 1–7 类都属"检测"阶段 —— **不新增第八类**'
if MARK3 in t:
    print('  ③ 已含边界说明（幂等）')
else:
    BLOCK = '''

''' + MARK3 + '''

> **边界**：**第 1–7 类都属"检测"阶段**（漏匹配／假匹配）；
> **"检测对了但值被抄错"属"搬运"阶段**，由既有规则覆盖
> （**哈希只允许由脚本在记录那一刻生成并直接写入产物，禁止手抄/转述/粘贴**）
> ⇒ **故不新增第八类**。

**理由（两条）**
1. **防止类别膨胀** —— 每遇新现象就加一类，会让清单**丧失判别力**；
2. **防止被读成有缺口** —— 后人见清单只到 7 类，可能以为"搬运错误没人管"从而**重复立规**。
'''
    t = t.rstrip() + BLOCK
    print('  ③ 已补边界说明')

io.open(REG, 'w', encoding='utf-8', newline='').write(t)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已写入: %d B（前 %d）/%s' % (os.path.getsize(REG), before, sha(REG)))
print('\n=== 自证（按英文名与中文名分别检索）===')
for k in (EN, '第七类', '假匹配', '文案串 ≠ 结构存在', '不新增第八类'):
    print('  %-42s 命中 = %s' % (k, k in t2))
