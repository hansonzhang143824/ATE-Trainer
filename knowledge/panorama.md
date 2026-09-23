# B 路径全景流程（Offline Coding）

> 主地图：五大输入源 → 14 步 → 可编译 VS 工程。每一步标注落点文件 / 脚本。
> 源文件：用户手写 `Offline Coding 全景工作流.txt`（14 步细述，本文件为对齐后的正式版）。
> 分层：L0 规范层 `sources/` · L1 规则层 `standards/` · L2 经验层 `experience/` · 材料索引 `references/`。

---

## 一、五大输入源

| 输入源 | 内容 | 产物/落点 |
|---|---|---|
| 1. DFT | 测试意图（test-Condition） | `dft-parse-agent`（读意图）→ 分类 |
| 2. 原理图 | SCH-Connect-Map 通路 | `schematic-parsing.md` + `sch_parse.py` |
| 3. ChannelMap | 源表通道↔工位 + 继电器 CBIT 值 | `Pin_Channel_define.h` + `Hardware-Config.h`（他人负责，定义完成则跳过） |
| 4. 机台手册 | STS8300 API | `knowledge/sources/` |
| 5. 工程师经验 | 规则/经验/Library-Functions | `standards/` + `experience/` + `Library-Functions/` |

## 二、入口

- **固定入口**：`sch-parse` → ChannelMap（Pin_Channel_define）→ `dft-parse`（仅 DFT）

## 三、一次性搭建（步骤 1-4）

| 步骤 | 内容 | 落点 |
|---|---|---|
| 1 原理图解析 | Component-Map + 通路梳理（最短路径优先 + 第二短备用） | `schematic-parsing.md` + `sch_parse.py` |
| 2 DFT 解析 | test-Condition | dft-parse-agent（读意图）+ gen_testitems_meta.py（机械派生 meta） |
| 3 源表+继电器定义 | 与 DFT **独立、同等级、次序无关** | `cbit-mapping.md` + `gen_cbit_defines.py` + `gen_paths.py` + `gen_path_defines.py` |
| 4 Treg 定义 | Trim Library-Functions | `standards/treg.md` + `Library-Functions/treg/` |

## 四、逐项循环（步骤 5-14）

| 步骤 | 内容 | 落点 |
|---|---|---|
| 5 分类 | 两级：项目结构类型(7类)→具体参数类型 | `standards/test-types.md` + `references/L4-Golden-code·L1-chip·L3-method/` |
| 6 框架创建 | 选模板（普通/Toggle-AWG/Trim） | `standards/framework.md` |
| 7 变量定义 | CParam + 结果数组 + Trim 节点 | `standards/framework.md` + `naming.md` |
| 8 继电器闭合 | 闭环原则 + 工程应用 | `hardware/relays.md` + `experience/relay-check.md` |
| 9 上电 | 量程/不过冲/clamp/大电流 | `experience/power-sequence.md` §上电 + R-PON |
| 10 寄存器配置 | registermap 读取 | `standards/register-config.md` |
| 11 测量 | 采样/间隔/切量程/恢复 | `experience/measurement.md` + `standards/units.md` |
| 12 下电 | 下电次序/量程统一 | `experience/power-sequence.md` §下电 + R-POFF |
| 13 log | 单位规则 | `standards/units.md`（R-LOG） |
| 14 检验 | 两层（见 §六） | `standards/verification.md` |

## 五、两级分类模型（步骤 5 核心）

```
DFT 项 ──识别(无歧义)──▶ 项目结构类型(7类, 决定框架)
                              │
                              ▼
                        具体参数类型(被测参数名, 决定参照)
                              │
                              ▼
            references 四件套(同名联动): chip/<参数> + method/<参数> + code/<参数> + debug/<参数>(按需)
```

- 项目结构类型 = 7 类，按测试机制划分，判定顺序**命中即停**（DFT 字段类可脚本化，测试意图类解析 Notes）。
- 具体参数类型 = 被测参数名（ZCD/RDSON/UVLO…），决定参照材料。
- 示例：ZCD 需 ramp 阈值 → 项目结构类型 AWG → 具体参数 ZCD → 参照 chip/ZCD + method/ZCD + code/ZCD。

## 六、两层检验（步骤 14）

| 层 | 内容 | 落点 |
|---|---|---|
| 单项目冒烟自检 | 一个函数生成后秒级自检（5 项） | `verify_single_fn.py` ✅ 已实现 |
| 跨项目统一门禁 | 整批生成后脚本化校验 + 编译 | `check_testitems_meta.py --require-all/--require-scope` + `verify_relay_trace.py --meta` + `verify_awg_params.py` + `gen_cbit_defines.py` + `gen_path_defines.py` + `fast_rebuild.ps1` |

流程：冒烟脚本 → 编译 → 跨项目门禁 → 批量放量（对应 B-001）。

## 七、案例模板贯穿 5-14

「参考已有 code」= 案例模板，贯穿步骤 5~14：分类时看案例判定类型、测量时抄案例写法。落点 `references/L4-Golden-code/`。

## 八、留 Action 清单（待用户逐步完善）

| 步骤 | Action 内容 | 落点 | 状态 |
|---|---|---|---|
| 5 | 识别方法（7 类判定） | `test-types.md` | ✅ 已完成（2026-08-16） |
| 5 | 优秀案例/Block 介绍/典型方法 | `references/L4-Golden-code·L1-chip·L3-method/` | 🟡 待归档 |
| 9 | 上电绕法/台阶经验 | `power-sequence.md` §上电 | 🟡 骨架待填 |
| 10 | registermap 读取 | `register-config.md` | 🟡 骨架待填 |
| 11 | 采样/切量程/恢复经验 | `measurement.md` | 🟡 骨架待填 |
| 12 | 下电次序/量程统一教训 | `power-sequence.md` §下电 | 🟡 骨架待填 |
