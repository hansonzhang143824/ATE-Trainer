# 规则注册表 Rules Registry

> **统一规则生命周期管理**: 所有规则 (global / specialized) 在此登记状态、来源、适用范围、版本。
> 维护方: `rules-agent`(提炼 + 写 draft 区) + 工程师(审核发布)。
> 关联: [[merge_rules]](合并规则 MR-0xx 专用)、`verify_merge_rules.py` / `verify_relay_trace.py`(强制层)。
> 使用方: dft-parse-agent、relay-agent、check-agent、各 verify 脚本。

---

## 规则状态机

```
draft (待审核) → active (生效) → retired (停用)
        │                │              │
    人工确认         同步verify脚本   保留历史(可回滚)
```

- **draft**: rules-agent 写入, 未审核
- **active**: 工程师确认, verify 脚本强制
- **retired**: 被推翻/被新规则取代, 保留历史可回滚

---

## 生效规则 (active)

| 规则ID | 类别 | 内容 | 适用范围 | 强制层 | 生效日期 | 来源 |
|--------|------|------|---------|--------|:---:|------|
| MR-000 | specialized (合并) | 零合并: 每个 DFT 项独立成函数 | 所有项目 | verify_merge_rules M001 | 2026-08-09 | 架构决策 |
| FR-001 | global (功能规则) | **Cap 稳压电容默认闭**: PIN 加电就需要其 Cap 稳压。仅两种情况**按 PIN** 移除该 PIN 的 Cap: ①该 PIN 被测电流(流经其 Cap, Cap 吃掉/掩盖真实 Iq) ②该 PIN 是 ramp/扫描电压源(Cap 拖慢/扭曲 ramp)。⚠**禁止按函数 MI 豁免**("函数里有 MIRET→整函数不闭"是反模式, 2026-08-10 重构)。**反向: PIN 被 FV 静态供电(非测该 PIN 电流/非 ramp 扫描源/非下电段)却未闭其 Cap → 缺陷(WARN)**; 测试垫偏置(AMUX/VDM/NTC)非供电轨不查。**检查E供电判定权威源 = TestItemMeta capAuthority** (OVERVIEW DFT意图层派生四集: powered_pins/mi_pins/ramp_pins/testpad_pins, 2026-08-10 已落地; 无 meta 函数降级对象名反推) | 所有项目 | verify_relay_trace 检查B + 反向检查E(meta capAuthority 权威) | 2026-08-10 | 用户纠正 |
| FR-002 | global (功能规则) | PU 开漏上拉: 观测开漏输出(NQON/QTMU/SDA_INT)时必需 | 所有项目 | verify_relay_trace 检查B/D | 2026-08-09 | 用户纠正 |
| FR-003 | global (功能规则) | P2P 继电器: 仅需 PIN 到地短路场景才接入 | 所有项目 | verify_relay_trace | 2026-08-09 | 用户纠正 |
| R-PON | global (上电规则组) | 上电序列铁律: vset→FV/iset→FI、MV无FI→FI=0+最小量程10UA、浮动源三阶段≤5V、大电流三段式(FV=0→FI=0→Clamp→FI)、**小电流两段式(FV电流<100uA→按 PIN 类型: power PIN 先100MA/digital PIN 先10MA 大量程上电稳定500us后切测量量程, ATEST 类模拟 PIN 直接测量量程无两段式; 未知按 power 保守, R-PON-09)**、量程≥2×取最小档、FPVI等电位 | 所有项目 | gen_power_sequence.py --audit-rules | 2026-08-09 | 架构脚本化 |
| R-POFF | global (下电规则组) | 下电序列铁律: 类型判定、普通三步(归零→delay_ms(1)→RELAY_OFF)、浮动反转台阶、FPVI最后RELAY_OFF、大电流FI=0→FV=0→OFF、RELAY_OFF统一量程(FPVI用1V/10MA非10A) | 所有项目 | gen_power_sequence.py --audit-rules | 2026-08-09 | 架构脚本化 |
| C-CBIT | global (CBIT继电器定义规则组) | 单点继电器定义: 动态读CBIT表(Excel权威)、F/S双线圈合并(KELVIN→_FS/其余去后缀)、FORCE/SENSE全词→_FOS_SNS、BUS方向合并(FH+SH/FL+SL)、同K号后缀拼接；V1~V8校验(位号不重复/通路完整性/命名一致/位号范围0~255/不遗漏/F-S成对/FPVI命名/功能分类一致) | 所有项目 | gen_cbit_defines.py --audit-rules | 2026-08-09 | 架构脚本化 |
| P-FINDER | global (通路追踪规则组) | 通路查找: BFS最短路径、稀缺源表识别(FPVIe/QTMU/QVM)、非稀缺源禁借道BUS、FPVIe域约束(FH/SH vs FL/SL)、跨域BUS短接约束、G6K/MOS/MOS2脚位通断、源端短接继电器排除(K86/K130,AGND/GND例外)、FPVIe通道分组(FH+SH/FL+SL)、F/S合并分类(Kelvin/PC短接/单线)、relay类型Excel权威(替代netlist误判)；**边界: 不生成SCH-Connect-Map(归sch-parse agent)** | 所有项目 | gen_paths.py --audit-rules | 2026-08-09 | 架构脚本化 |
| P-DEF | global (通路继电器定义生成规则组) | 通路继电器语义别名: 数据权威=SCH-Connect-Map `需闭合:` 全量 SetOn(非旧 relay.h 简化值, 已归档 _archive); 命名=cbit-path-namer 脚本化(FPVIe H/L→`K_FPVIH/L_TO_<PIN>`、QVM带极性→`K_<PIN>_QVMH/QVML`、ACM200/QTMU/FXVIe_PLUS/DCM→`K_<PIN>_ACM/QTMU/FXVI/DCM`); FPVIe CH0/CH1 双通道→`_A/_B`(禁并集短接两驱动线); 需闭合空(NC-only)→不定义; 同源同pin多通路→`_A/_B/_C`+agent复核; 值=需闭合位号逗号分隔(供 `cbite.SetOn(K_..., -1)`); 注释带 StdAfx.h 物理名; 追加到编译头 StdAfx.h include guard 内; **写入只经 DLP 字节模式且先编码后open('wb')(编码失败绝不截断目标文件)** | 所有项目 | gen_path_defines.py --audit-rules | 2026-08-10 | 架构脚本化 |
| R-LOG | global (LogData 单位规则) | **SetTestResult 结果值单位必须与 spec/DFT 预期单位一致**（DFT `Unit` 列权威）: MIRET 原始 A → 预期 uA 乘 1e6 / mA 乘 1e3 / nA 乘 1e9; MVRET 原始 V → mV 乘 1e3; 换算加在 GetMeasResult 赋值处带注释; 禁止按源表原始 A/V 直接 log | 所有项目 | check-agent E025 (有 DFT 判 FAIL, 无 DFT 判 WARN) | 2026-08-10 | 用户纠正 |
| R-HYS | global (Ramp Hys 单位规则) | **含 ramp 的 rise/fall/hys 测试: Hys 单位固定** — Hys 是电压量 → mV (原始 V 乘 1e3); Hys 是电流量 → mA (原始 A 乘 1e3)。Rise/Fall 是触发点 ramp 电压/电流(V/A), Hys=Rise−Fall 差值小, spec 预期 mV/mA; 换算加在 `hys[site]=rise-fall` 赋值处带注释, 禁止按原始 V/A 直接 log | 所有含 Hys 参数的 ramp 测试 (Toggle/AWG) | check-agent E026 (有 DFT 判 FAIL, 无 DFT 判 WARN) | 2026-08-10 | 用户纠正 |
| R-SETON | global (继电器格式规则) | **Step 1 (Connect) 必须始终有 cbite.SetOn(...)**: 即使所有继电器默认NC直连、无需闭合任何继电器, 也必须显式 `cbite.SetOn(-1)` + `delay_ms(3)` (STS8300 手册公共规范), 禁止只写 `delay_ms(3)` 空区块 | 所有项目 | verify_relay_trace.py 结构规则 / check-agent R004 | 2026-08-10 | 用户纠正 |
| R-VIR | global (测量规则) | **电阻 = 实测电压 / 实测电流**: 电阻计算必须用实测值 — R = `GetMeasResult(site, MVRET)` / `GetMeasResult(site, MIRET)`（同一源表同一次 MeasureVI 后读取）。禁止用理论设定电流（如 `Set(FI, 1e-5)` 的设定值 1e-5）或设定电压代入。FI 灌电流测 V 场景须同时读 MVRET+MIRET 再相除 | 所有项目 | check-agent E027 | 2026-08-10 | 用户纠正 |
| B-001 | specialized (批量生成纪律) | **整批 TM 生成先单函数冒烟**: 模板/数据 dict 有 bug = 整批一起错。先插 1 个代表函数 → 编译 + `check_testitems_meta.py --require-all` + `verify_relay_trace.py --meta --warn-as-error` 全绿 → 再批量放量。**占位符按长度降序替换** (前缀冲突: `__CONNECT_COMMENTS__`⊃`__CONNECT__` / `__RAMP_RANGE_COMMENT__`⊃`__RAMP_RANGE__` / `__RETCOMMENT__`⊃`__RET__`) + 替换后断言无残留 `__X__` (有→FAIL 不静默生成)。**生成后自检**: 分号在尾随注释前 (`* 1e3;  // comment`, 否则 C2143)、花括号配平、CRLF 字节干净 (DLP 源文件字节模式 `open('wb')`, 禁止文本模式 \r\r\n) | 批量 TM 生成 (codegen pipeline) | skill 纪律 (先单函数冒烟流程 + 降序替换) + verify_single_fn.py (无残留断言 + 分号/括号/CRLF) | 2026-08-10 | TM403-425 教训 |
| R-TRIM | specialized (Trim 判定铁律) | **Trim 项目判定铁律**: ① DFT Trim='Y' 或含 "Trim" 字样(不分大小写) 或参数名与 treg 文档同名 → **无条件走 trim 框架**(trim_reg.trim + PARAM_NODE.execute + step0~N + 8 后缀 + sub.cpp 尾部 ACTIVE measure)；② 执行中材料缺失/错误(treg 缺段/字段矛盾) → **报告用户具体不匹配点**, 禁止静默降级为「暂测默认值/普通测试直接测量」 | Trim 类项目 (DFT Trim=Y 或含 Trim 字样) | skill 纪律 (codegen Step3 类型判定 + Step7 材料核对; 判定表见 test-types.md 第1类) | 2026-08-16 | 用户纠正 (TM300/301 教训) |
| R-REF | global (reference 材料管理) | **reference 材料按参数同名联动 + 靠索引访问, 案例不物理迁移**: 四件套 `chip/`(是什么) + `method/`(怎么测) + `code/`(长啥样) + `debug/`(怎么排查, 按需) 按参数名归档; **索引分两层互不干涉**: `func_type_index.md`(功能类型→判据/框架/方法) + `param_type_index.md`(参数→四件套路径, 同名联动), 不靠物理目录结构/命名约定; **四件套文件夹内部平铺不建子文件夹**; **code/ 案例是工程源文件, 位置/名字/内容不允许变动** — 从工程源文件(VS 工程 devel/source)归档只 `Copy-Item` 进 `code/` 保持原名(字节级), 禁止 move/rename/编辑原文; **用户手交根目录的案例代码 → 直接 `Move-Item`(剪切) 进 `code/`, 根目录不留残留**; 新参数补材料按四件套归档, debug 按需(非必须) | reference 材料管理 (所有项目) | 人工纪律 + skill 纪律 (无自动脚本; param_type_index.md 单一索引) | 2026-08-16 | 用户确认 (纠正"案例迁移"误解) |
| R-BST-SW | specialized (黄金约束) | **BST-SW 台阶黄金约束 (Current Threshold/ZCD)**: BST≥SW、0≤BST-SW≤5V、目标 BST-SW=5V。HS=BOOST(PMID-SW) / LS=BUCK(SW-PGND)，均电流>200mA 用 FPVIe 浮动源 + BST 台阶上电; **LS 拓扑 SW=PGND=0 用 BST=5V(禁 10V)**、HS 用 BST=5V→10V 台阶; K57_CAP_BST_SW（BUBO BST−SW 对电容；SCH L904。注意: K45/K44 是 TRX 的 BST1/SW1、BST2/SW2 电容, 属 rampv 线不适用） 差分电容继电器必闭 | Current Threshold/ZCD 类 (TM607-609) | verify_bst_sw_sequence.py --src <test.cpp> (目标函数按 meta capAuthority 拓扑指纹派生: powered_pins 含 BST-SW→HS / 含 PMID-SW→LS; 量程按 max\|iset\|≥1A→10A, 否则 2A; 寄存器 LS→0x01/HS→0x02; 2026-08-24 参数化去硬编码) | 2026-08-23 | codex 黄金约束 (TM607-609 根因) |
| R-PATH-A | global (通路有效性规则组) | **禁止穿越固定电压节点**: 源表→PIN 通路不得穿越任何固定电压节点(地 AGND/DGND/JGND/AGND_* 0V ∪ 固定电源轨 S34_J+5V 5V/12V)。固定节点作**终点**合法(如 AGND_F 地脚), 作**中间节点**非法(源表与之对拉、无法独立控制通路电压)。判据=源表无法独立控制通路电压 | 所有项目 | sch_parse.py trace() + csv_pathproof_v2.py fixed_voltage_nets 剪枝 | 2026-08-24 | 用户规则 |
| R-PATH-B | global (通路有效性规则组) | **禁止穿越其他 PIN**: 源表→PIN 通路不得穿越其他 DUT PIN。BFS 到达含 DUT PIN 的 net 即记录 proof 并停止展开(terminal-stop)。合并短接节点(同 net 多 PIN)天然正确 | 所有项目 | sch_parse.py trace() + csv_pathproof_v2.py terminal_stop | 2026-08-24 | 用户规则 |
| R-P2P | global (通路分类规则组) | **P2P 短路分类(需闭合≤2)**: 继电器端点一侧=DUT PIN、另一侧=地脚(AGND_F)→P2P-到地; 两侧=两个不同 DUT PIN base→P2P-互短。需闭合(ON)继电器数≤2。按继电器端点 net 解析(不依赖 relay_class, 防 G6K 名带 P2P 误归 Share) | 所有项目 | sch_parse.py 列11 P2P 检测 | 2026-08-24 | 用户规则 |
| R-PUPD | global (通路分类规则组) | **上拉/下拉按连接分类, 不看电阻值**: PIN+电阻+继电器+上拉电源→上拉(固定5V轨≠源表可程控, 分「上拉-固定5V」「上拉-源表」两类标); PIN+电阻+继电器+地→下拉。Kelvin 电阻(两端 net 直接 F↔S 同 base)是排除判据不进。电阻角色靠名后缀 _PU_/_PD_(设计者编码), 方向子类靠连接终端 | 所有项目 | sch_parse.py 列11 上拉/下拉 | 2026-08-24 | 用户规则 |
| R-STAB | global (通路分类规则组) | **稳压按电容值≥100nF 判(不看名字)**: PIN+电容(≥100nF)+Cap继电器→稳压。值权威=CSV ComponentValue 列(adapter 嵌入合成 EDIF Property Value, 2026-08-25 起无需 .NET), 阈值 farad≥1e-7(100nF)。需闭合继电器=名含 Cap/CAP 的开关继电器 | 所有项目 | sch_parse.py 列11 稳压 | 2026-08-24 | 用户规则 |

> FR-001~003 详细定义见 `knowledge/hardware/relays.md` §功能应用规则。
> MR-000 详细定义见 `knowledge/standards/merge_rules.md`。
> R-PON/R-POFF 明细 19 条 (R-PON-01~09 / R-POFF-01~06 / R-FLT / R-RNG / R-SRC / R-ST) 见 `agents/power-on-agent.md` + `agents/power-off-agent.md` 规格文档规则清单 + 脚本内置 `RULE_COVERAGE`（`--audit-rules` 机器自检）。R-PON-09 小电流两段式上电来源: 用户规则 2026-08-10（测量电流<100uA 时大量程上电加速稳定）；**2026-08-10 按 PIN 类型修正: 仅 power PIN 需 100MA 两段式, ATEST 类模拟 PIN(VDM/NTC/AMON)直接测量量程, digital PIN(GPx/KLV/SNSP/SNSN)用 10MA 两段式**。
> C-CBIT 明细 13 条 (C-P1/C-P1a/1b/1c/C-P2 单点合并 + C-CK-V1~V8 校验) 见 `agents/cbit-singlepoint-agent.md` + `agents/cbit-check-agent.md` 规格文档 + 脚本内置 `RULE_COVERAGE`（`gen_cbit_defines.py --audit-rules` 机器自检）。
> P-FINDER 明细 11 条 (P-P1~P-P11 通路追踪/类型/约束/合并) 见 `agents/cbit-path-finder.md` 规格文档 + 脚本内置 `RULE_COVERAGE`（`gen_paths.py --audit-rules` 机器自检）。
> P-DEF 明细 13 条 (P-DEF-01~13 数据源/解析/命名/碰撞/写入/校验) 见脚本内置 `RULE_COVERAGE`（`gen_path_defines.py --audit-rules` 机器自检）。SCH-Connect-Map 仍归 sch-parse agent 维护，脚本只读。**SCH-Connect-Map.txt 完整生成归 sch-parse agent（任务六），不脚本化；`gen_paths.py` 仅为通路追踪工具（BFS→path_list 兜底）。** F/S 状态一致性校验（同继电器在 F/S 中 state 互斥 → [F/S冲突]）在 `sch_parse.py` 的 `fs_conflict()`，规则见 `knowledge/hardware/schematic-parsing.md` §四。

---

## 待审核 (draft)

| 规则ID | 候选类别 | 内容 | 来源 | 建议日期 |
|--------|---------|------|------|:---:|
| R-ACM-01 | global (功能规则) | **ACM 无法同时测压测流**（其余源表均可）: ACM 单板 24 通道，硬件手册概述明确"无法同时测压测流"，必须分步测（先测电压再测电流或反之） | 所有项目 (ACM 卡) | check-agent (人工; ACM 未用本项目) | 2026-08-30 | 硬件手册 Rev2.13 p78-80 |
| R-ACM-02 | global (功能规则) | **ACM 大小电流量程切换先断输出继电器**: 大电流量程(±500mA/±200mA/±20mA)与小电流量程(±2mA/±200μA/±20μA/±5μA)间切换时，硬件会先断开输出继电器→切量程→再接通；编程侧避免依赖切换瞬间的输出连续 | 所有项目 (ACM 卡) | check-agent (人工) | 2026-08-30 | 硬件手册 Rev2.13 p78-80 |

> rules-agent 提炼候选 → 写这里。工程师确认后移入 active 区并同步 verify 脚本。

---

## 已停用 (retired)

| 规则ID | 内容 | 停用日期 | 停用原因 | 被取代 |
|--------|------|:---:|------|------|
| _(空)_ | | | | |

---

## 发布流程 (human-in-the-loop)

1. `rules-agent` 从 `daylog/` 提炼候选 → 写 **draft** 区 (带来源/适用范围/建议类别)
2. 工程师审核 draft 条目
3. 确认 → 移入 **active** 区, 记录生效日期 + 来源
4. **同步强制层**: active 规则若有可自动判定的 → 更新 `verify_merge_rules.py` / `verify_relay_trace.py` / check-agent 错误码
5. 停用 → 移入 **retired** 区, 注明原因 + 被哪条取代

## 分类判定 (rules-agent 用)

| 类别 | 判定 | 示例 |
|------|------|------|
| **global** | 适用于大多数 STS8300 项目, 泛化价值明确 | 反短接、功能规则、量程≥2× |
| **specialized** | 只适用特定项目/测试类型/资源组合 | 合并规则 MR-0xx、某项目专属继电器组合 |
| 经验/子函数 | 转发给 experience-agent / sub-function-agent | — |
| 临时/无用 | 排除, 不进长期库 | — |

> 分类保守: 不确定 → 标 ⚠ 待人工确认。防"一次临时修复污染全局规则"。
