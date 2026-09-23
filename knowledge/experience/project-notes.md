# 经验: 项目专属决策/工具记录 (project-notes)

> 项目专属的绕法、工具用法、决策记录。不做规则, 只留参考。由 experience-agent 维护 + 人工审核发布。

---

## Cap 修复后快速验证工具链用法 (2026-08-10)

| 字段 | 值 |
|------|-----|
| 来源 | daylog/2026-08-10.md |
| 适用项目 | DALI 类 |
| 状态 | draft |

### 经验
Cap/继电器类改动后的验证分两档, 结合用: ①严格全量扫描用 `verify_relay_trace.py --warn-as-error` (把 WARN 当失败, 避免误报漏过), 覆盖 FR-001 反向检查 + 功能规则; ②秒级编译检查用 `fast_rebuild.ps1 -Incremental` (增量构建需传 Path 参数), 5.1s 出 Release 0 errors/0 warnings。顺序一般是先脚本全量扫, 再增量编译。

### 背景
2026-08-10 Cap 默认闭重构 (14 处代码修复 + 脚本 3 处) 后, 用这套组合快速验证, 未触发完整编译即可确认无回归。

### 验证
fast_rebuild.ps1 -Incremental → Release 0 errors/0 warnings (5.1s); verify_relay_trace.py --warn-as-error → RELAY TRACE PASSED (49 函数, FR-001 反向 0 处)。

---

## 源表规格抽取与交叉验证方法 (2026-08-30)

| 字段 | 值 |
|------|-----|
| 来源 | daylog/2026-08-30.md |
| 适用项目 | DALI 类 |
| 状态 | draft |

### 经验
源表规格的三层权威与校验链:
1. **编程手册只有量程枚举无精度**; 精度表在硬件手册各板卡"技术指标"节 → 写码估精度查 `hardware-specs.md` (含 22 模块精度表)
2. **规格全在文字里**, pymupdf 抽取即可, 不需 vision (仅板卡框图需 vision, 届时再换模型)
3. **转写校验铁律**: 抽取文本 → hardware-specs.md 初稿后, 必须用工程实卡宏 (`Pin_Channel_define.h` 的 `_PIN_CHANNEL_DEFINE_*`/`_PIN_SITE_BIND_DEFINE_MD_*`) + SCH-Connect-Map 列1-10 对账; 能抓出自己的转写错误 (实测 5 处)
4. **DALI 工程源表清单** (实卡, 写码只出现这些): FXVIe_PLUS (8ch/卡×8) + ACM200 (24ch×8) + FPVIe (2ch×8) + QVMe/QTMUe (NOSITE 共享); 无 DCM/ACM/HVIE/HPVIe/HPSM → 写码不出现这些源
5. **浮动源判定** (配合 SCH-Connect-Map 末尾浮动源清单): 所有模拟源本质浮动, "接 AGND" 是继电器短接; 判断"当前是否浮动" = 看该源 Low 端路径上有无需闭合的继电器, 不闭合=浮动

### 背景
2026-08-30 通读硬件手册 Rev2.13 抽 22 模块特性, 初版 hardware-specs.md 有 5 处转写错误, 经全量通读 + 实卡宏对账抓出修正; 用户纠正"需要完全理解不是给我看"后改为内化+交叉验证。

### 验证
8 工位卡↔通道分配对账全绿; TM641 量程/精度对账全绿 (FPVIe ±5V `±(0.75mV+0.025%Rdg)`, ACM200 ±10V `±(1.5mV+0.025%Rdg)`)。
