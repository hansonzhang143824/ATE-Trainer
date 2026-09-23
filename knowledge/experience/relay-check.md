# 经验: 继电器/Cap 检查脚本实现陷阱 (relay-check)

> DALI 项目 `verify_relay_trace.py` (FR-001 反向检查 E) 实现/调试过程中的解析与检查经验。
> 检查脚本给出误报或漏检时, 先到这里找对应根因。由 experience-agent 维护 + 人工审核发布。

---

## 已落地根治: check E 以 TestItemMeta capAuthority 为权威, 对象名反推仅作降级 (2026-08-10)

| 字段 | 值 |
|------|-----|
| 来源 | daylog/2026-08-10.md (用户拍板: "选项A, 补全meta, 保证准确才是第一位的") |
| 适用项目 | DALI 类 (对 codegen 检查脚本权威源设计有参考价值) |
| 状态 | active (已实施 + 全量验证通过) |

### 经验
"哪个 PIN 被 FV 静态供电" 的**权威来源已接入 check E**:
- **DFT 意图层**: `TestItemMeta.capAuthority` 四权威集, 由 `Dali_testmode.xlsx /OVERVIEW` (DFT意图层) 派生
  - `powered_pins` 供电轨 = vset ∪ OVERVIEW Power列 ∪ Dynamic裸PIN (**不含 iset 输出负载** — VCC/VMCU 是 DUT 内部稳压输出, 测量目标非供电轨, test.cpp 从不闭 K0_VCC_Cap)
  - `mi_pins` 测电流 PIN (Check/Dynamic 列 I(pin)) → Cap 按 PIN 豁免
  - `ramp_pins` ramp 扫描源 (vset 同 pin ≥2 不同值 **且仅限 toggle 测试** — 非 toggle 的 2 值如 shipmode 掉电序列不算 ramp) → Cap 按 PIN 豁免
  - `testpad_pins` 测试垫偏置 (AMUX/VDM/ATEST/DTEST0/NTC) → 不查 Cap
- 生成器: `gen_testitems_meta.py` (OVERVIEW→JSON, 可复现, `--dump`/`--audit` 人工审核) → meta json; 校验器: `check_testitems_meta.py` (`--require-all`/`--require-scope` 收尾对账)
- check E 元权威分支: `meta_fn = meta_by_name.get(name)` → 用 capAuthority 判定, **豁免按 PIN 不按函数** (fam_intersect)
- 降级: 无 meta 函数走旧对象名反推 (`fv_supply_objs` + `is_testpad_bias`), 仅健壮性, 51 函数全有 meta

### 验证
- meta 派生与已验证 test.cpp 闭合状态 **0/51 mismatch** (强准确性信号)
- `--warn-as-error` 全量 PASSED, meta 覆盖 51/51, FR-001 反向 0 处 (与改造前基准一致, 无误报)
- 负测试 ×3 (TM114/TM204/TM116 删 K13 SetOn) → 正确捕获 WARN + 退出码 1; fallback (--meta 不存在) → meta 覆盖 0/51 降级正常
- fast_rebuild Release PASSED (0 errors 0 warnings)

### 遗留
SCH-Connect-Map 继电器链→PIN 映射层 (实现层) 仍未接入 check E 的供电判定 — map 不含 Cap 附件继电器, 且对象名与通路名不同构; 当前 meta 覆盖 51 函数已足够, 如需进一步权威化 map 层是下一步。

---

## 定点修复用函数块定位: count=1 全局正则替换会误修第一个匹配, 目标函数漏修 (2026-08-10)

| 字段 | 值 |
|------|-----|
| 来源 | daylog/2026-08-10.md (二次纠错) |
| 适用项目 | 所有 STS8300 项目 (对 codegen/check 脚本的修复操作有参考价值) |
| 状态 | active (已实施 + 验证通过) |

### 经验
**做"补某函数某处"的定点修复时, 禁止 `re.sub(pat, new, src, count=1)` 全局替换** —— count=1 只替换**第一个匹配**, 若文件里多个函数有同模式代码, 会误修排在前面的函数, 目标函数漏修, 而 verify 全量扫描会因为"第一个函数已修"看起来正常, 静默吞掉错误。**正确做法**: 先用 `fn_blocks` (DUT_API 签名切块) 定位目标函数 → 在函数块内做唯一替换 (块内 count 断言 ==1)。

### 背景
Trim_IZTC_RES (line 3830-3831) 需要补闭 K13_VBAT_Cap, 上次用 `re.sub(count=1)` 误修了同模式的 TM132/TM134 (碰巧也正确, 因两者都测 I(VDM) 不流经 VBAT), **Trim_IZTC_RES 漏修**。verify 报唯一 WARN 才暴露。

### 验证
函数块定位重修后, verify PASSED (FR-001 反向 0 处) + 负测试 (临时移除 Trim K13 → WARN 重新捕获) + fast_rebuild 0 errors/0 warnings。

---

## fast_rebuild -Incremental 的 PASSED 不能证明新代码被编译: 预存损坏会被增量缓存掩盖 (2026-08-10)

| 字段 | 值 |
|------|-----|
| 来源 | daylog/2026-08-10.md |
| 适用项目 | 所有 STS8300 项目 (对编译验证有效性判断有参考价值) |
| 状态 | active (已实施 + 验证通过) |

### 经验
**修完 test.cpp 后, fast_rebuild.ps1 -Incremental 显示 PASSED 不能证明新代码被编译** —— 若 test.cpp 文件 mtime 未变化, MSBuild 增量构建会跳过该编译单元直接用缓存目标。test.cpp 里**预存**的语法损坏 (如 `wo{`) 会一直潜伏, 直到某次改动让 test.cpp 被真正重编才暴露。**验证编译有效性的方法**: ①`--verify-src`/全量扫描确认改动函数被解析到 ②强制 `-Rebuild` 或 touch test.cpp 后再编译 ③编译日志确认 test.cpp 出现在 Compile 步骤。

### 背景
test.cpp line 1802 `wo{` (TM103 签名后 `{` 被污染成 `wo{`) 预存损坏, 60 函数全量字节扫描仅此 1 处。之前多次 fast_rebuild -Incremental PASSED, 因 test.cpp 未重编被缓存掩盖; 本次改动 test.cpp (Trim 修复) 触发真正重编, `error C3646: 'wo' : unknown override specifier` 才暴露。

### 验证
字节级定点修复 (`\r\nwo{\r\n` → `\r\n{\r\n`, count==1 断言) 后 fast_rebuild PASSED (0 errors/0 warnings)。

---

## 供电 PIN 判定: 权威来源是 DFT 意图 + SCH-Connect-Map 继电器链→PIN, 对象名反推是信息丢失后的兜底 (2026-08-10)

| 字段 | 值 |
|------|-----|
| 来源 | daylog/2026-08-10.md (用户纠正) |
| 适用项目 | DALI 类 (对其他 STS8300 项目检查脚本设计有参考价值) |
| 状态 | draft |

### 经验
检查脚本要判定"哪个 PIN 被 FV 静态供电", 权威信息有两个来源, 当前脚本都没吃:
- **DFT 意图层**: `vset[pin,...]` 明确"要上电哪个 PIN" (codegen 的 TestItemMeta/pinsInvolved 是现成的)
- **实现层**: `SCH-Connect-Map` 继电器链→PIN 映射明确"闭合哪些继电器→哪个 PIN 上电", 且含 `Relay-NC`(默认导通)语义——RC 通路供电**不需要任何 SetOn**

当前 `verify_relay_trace.py` 两者都没接, 只从 `obj.Set(FV,...)` 的**源表对象名拆 token 反推** PIN——这是信息丢失后的兜底, 在"产物文本"上猜。反推层固有缺陷:
1. **token 歧义**: 对象名混入驱动/通道 token (DRVH1/AMUX/…), 词表漏一个就误判/漏检
2. **纯 RC 供电不可见**: FXVIe_PLUS→VBAT 是 `K8(Relay-NC)`, 代码闭合列表里根本没有对应继电器 → 无论对象名反推还是 map 反查都拿不到(对象名反推因 Set(FV) 存在反而能看到)

**map 反查改造的硬约束** (不能只换反查来源):
- map **不含** Cap/PU/P2P 附件继电器 (稳压电容并联在 PIN 上, 不进通路表) → "VBAT 有没有 Cap" 这层 map 给不了
- 对象名 (`VBAT_PD3_FXVI`) 与 map 通路名 (`S3_FXVIe_PLUS_FH5`) **不同构**, 需 Pin_Channel_define.h 的 extern→类型→POGO 桥接
- "哪个 PIN 被测电流 (MIRET)" 是**测量动作**不是继电器动作, map 给不了 → 按 PIN 豁免 (fam & mi_pins) 仍依赖对象名/DFT

**结论**: 完整改造须**同时接入 DFT 意图层 + map 映射层**; 接入前对象名反推是兜底, 其 token 排除集必须覆盖驱动/通道变体 (DRVx/HT/…)。

### 背景
`VBUS_DRVH1_ACM` 末 token 是 DRVH1 (非供电), NON_SUPPLY_TOKENS 缺 'DRVH1' → VBUS 供电对检查对 TM114/124/127/128 不可见, 4 处 VBUS 静态供电未闭 K5 被掩盖; 同时 mi_pins 误收 DRVH1, 豁免错配。经用户纠正, 根因不是词表不全, 而是"用对象名反推供电 PIN"这个信息源本身就是信息丢失后的兜底。

### 验证
NON_SUPPLY_TOKENS 加 'DRVH1' 并让 mi_pins 复用该集合后, `verify_relay_trace.py --warn-as-error` 暴露并修复 4 处隐藏漏检, 全量 PASSED (补丁层面验证; 信息源重构未做)。

---

## DLP 透明加密源文件修复: 文本模式写破坏 CRLF, 循环内改 txt 索引失效 (2026-08-10)

| 字段 | 值 |
|------|-----|
| 来源 | daylog/2026-08-10.md (R=V/I 修复二次纠错) |
| 适用项目 | 所有 STS8300 项目 (DLP 加密源文件: test.cpp/AI.cpp 等) |
| 状态 | active (已验证: 字节级修复后 verify PASSED + 全量 Rebuild 0 errors/0 warnings) |

### 经验
**修 DLP 透明加密源文件 (test.cpp 等) 必须用字节模式写**:
1. **禁止 `open(p, 'w', encoding='utf-8-sig')` 文本模式** — Windows 文本模式把 `\n` 转成 `\r\n`, 原 `\r\n` 变 `\r\r\n` (行数翻倍, 空行 55%), 整文件损坏。**必须 `open(p, 'wb')` 写 `bom + txt.encode('utf-8')`**, BOM(efbbbf)+CRLF 逐字节保留。
2. **禁止在循环内顺序替换并就地修改 txt** — `txt = txt[:s] + new + txt[e:]` 使 txt 变长, 后续块的 start/end 索引全部失效 → 错位插入 (头注释粘连/残片重复/行截断)。**必须反向迭代 (reversed(blocks)) 或每块重算索引**, 且每处替换前 `count==1` 断言。

### 背景
R=V/I 修复 (TM202/TM203 电阻改用实测 V/I) 第二次写入用文本模式 → CRLF 全局污染; 同时循环内顺序替换 → TM203 头注释粘连 (标题+签名挤一行) + TM204 头注释重复残片。

### 验证
字节级修复后: 5151 行 CRLF 全干净 (0 孤立 CR / 0 \r\r\n), 括号 479/479 配平, verify_relay_trace --warn-as-error PASSED (FR-001 反向 0 处, meta 54/54), fast_rebuild 全量 Rebuild 0 errors/0 warnings (test.obj 17:11:44 重编确认)。

---

## 测试垫偏置: "名字含供电 token ≠ 供电轨" 是对象名反推的固有歧义 (2026-08-10)

| 字段 | 值 |
|------|-----|
| 来源 | daylog/2026-08-10.md |
| 适用项目 | DALI 类 |
| 状态 | draft |

### 经验
判断"该对象驱动的是供电轨还是测试垫", 本质应来自 DFT 意图 + SCH-Connect-Map 通路末端节点 (AMUX/VDM/NTC/ATEST 是测试垫节点, 非供电轨)。当前脚本靠对象名反推, 产生歧义: 对象名含 cap 家族 token (VAC) 会被默认当供电轨查 Cap, 但实际驱动的是测试垫 → 误报。**兜底绕法**: 对象名**和**闭合 Share 继电器名**都**含测试垫 token 才判为测试垫偏置, 跳过 Cap 检查 (is_testpad_bias())。**注意这只是反推层的补丁**——根治仍在 DFT/map 的节点类型信息。

### 背景
`VAC123_AMUX_ACM` 名含 VAC (cap 家族), 但闭合 K20_ACM0_AMUX 驱动的是 AMUX 测试垫 → K21_VAC_Cap 检查误报 (TM132/134)。

### 验证
is_testpad_bias() 引入后消除 TM132/134 的 K21_VAC_Cap 误报, 全量 --warn-as-error PASSED。

---

## 豁免粒度反模式: 函数级/集合级豁免 (2026-08-10)

| 字段 | 值 |
|------|-----|
| 来源 | daylog/2026-08-10.md |
| 适用项目 | DALI 类 (反模式对审查其他 STS8300 项目代码有参考价值) |
| 状态 | draft |

### 经验
豁免条件要落到单个对象 (PIN) 粒度。两类同款反模式: ①"函数里有 MIRET → 整函数不闭 Cap" (函数级豁免); ②脚本 `if cap_relay in relays or mi_pins:` 中 mi_pins 是集合, 非空即整函数跳过 (集合级豁免)。两者共性都是"条件是非空集合就整体跳过"的写法。审查这类检查逻辑时, 遇到"集合非空即跳过"要警觉 — 该按 `fam & mi_pins` 把豁免交到 PIN 粒度。

### 背景
函数级豁免曾致 10 函数漏闭; verify_relay_trace.py 检查 E 里同款集合写法继续掩盖漏检, 改为按 PIN (fam & mi_pins) 后暴露。

### 验证
改后 --warn-as-error 全量 PASSED (49 函数, FR-001 反向 0 处)。
