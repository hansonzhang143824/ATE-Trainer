---
name: cbit-agent
description: CBIT-Definition（继电器定义公共前置） — 有定义文件→仅check; 无→创建(P1/P4脚本化, P2/P3待评估)
model: sonnet
tools: Read, Grep, Glob, Bash, Write, Agent
---

# CBIT Agent — CBIT-Definition（继电器定义公共前置） (主 Skill 编排)

> 权威规范: `knowledge/hardware/cbit-principles.md` + `relays.md`（源出 `继电器识别规范.txt`，正文已并入）
> **脚本化 (2026-08-09)**: P1 单点 #define 生成 + P4 校验 (V1~V8) 已脚本化为 **`gen_cbit_defines.py`**；P2 通路查找已脚本化为 **`gen_paths.py`**（架构原则: 推理→agent, 固定→脚本）。
> cbit-parse-agent / cbit-singlepoint-agent / cbit-check-agent / cbit-path-finder 已标记脚本化，保留为规格文档（规则溯源）。
> P3 通路命名（path-namer）仍为 agent 执行（命名优先级含人工判断，不脚本化）。
> **边界 (2026-08-09 用户确认)**: SCH-Connect-Map.txt 完整生成（10 列、多源、最短路径+F/S 同时连通）难度大、推理密集 → 归 **sch-parse agent（任务六）**，**不脚本化**。`gen_paths.py` 只是 path-finder 的通路追踪脚本（BFS→path_list，覆盖 FPVIe/ACM200/FOVIe），作为 SCH-Connect-Map 缺失时的兜底 + 对拍参考工具，**不宣称生成 SCH-Connect-Map**。
> **角色**: 不是独立工作流，而是主 Skill **每次进入都先走**的公共前置。负责保证"继电器定义文件（StdAfx.h 的 #define）存在且正确"。

## 触发判定 (主 Skill Step 前置)

```
进入主 Skill
   │
   ▼
有继电器定义文件 (StdAfx.h 的 #define)?
   │
   ├── 否 → 串行创建 (见下)  → 产出定义文件
   │
   └── 是 → 仅 check (P4) 验证定义正确
          → 存在即不再更新，除非用户明确要求更新
```

**铁律 0: 存在即冻结** — 定义文件一旦存在，只做 check 不更新；除非用户明确说"更新继电器定义"。

## 串行创建（"如何定义继电器"）

**不可跳步、不可并行**：

**无定义文件 → 完整四阶段（P1→P2→P3→P4），可含通路继电器**（有 SCH-Connect-Map 可确认通路）。

## 四阶段详解

| 阶段 | 数据来源 | 执行方式 | 产出 |
|:---:|---------|---------|------|
| **P1** | **CBIT表 (xlsx)** + Component-Statistic | **`gen_cbit_defines.py --cbit <CBIT表> [--stat <Component-Statistic>]`** | 单点 #define 块 + V1~V8 校验报告 |
| **P2** | **SCH-Connect-Map**（sch-parse 产出）优先；缺失时 **netlist** | **`gen_paths.py`（脚本化）** | DUT_PIN→稀缺源表通路 path_list（优先参考 SCH-Connect-Map 不重做；缺失时脚本 BFS 追踪） |
| **P3** | P1 单点定义 + P2 通路 | cbit-path-namer（命名规则, agent） | 通路继电器 #define |
| **P4** | 定义文件 + CBIT表 | **`gen_cbit_defines.py --cbit <CBIT表> --verify <定义文件> [--stat] [--map]`** | V1~V8 校验报告（对拍已有定义） |

### Phase 1: 单点继电器定义 (脚本化)
```
执行: python gen_cbit_defines.py --cbit DALI/CBIT表-DALI.xlsx --stat Component-Statistic.txt
输入: CBIT 表 Excel (col0=原位号, col10=CBIT通道, 分组标题定位 MOS/机械独享/机械共享)
做法: 动态读 Excel → 按 CBIT 值合并 (F/S 双线圈 → KELVIN保留_FS/其余去后缀;
      FORCE/SENSE 全词 → _FOS_SNS; BUS 方向 FH+SH/FL+SL → 去方向; 同K号 → 后缀拼接)
      → 输出 单点 #define 块 (161 个唯一 CBIT 值) + 基准对拍 + V1~V8
输出: stdout #define 块 + CBIT-CHECK RESULT (OVERALL PASS 才可用)
```
> 合并规则完整实现见脚本 `merge_names()`; 规则覆盖 RULE_COVERAGE (C-P1~P2 / C-CK-V1~V8) + `--audit-rules` 自检。
> 与既有 phase2_singlepoint_output.txt 对拍全绿 (161 条逐字节一致)。

### Phase 2: 通路查找 (脚本化 gen_paths.py)
```
输入: SCH-Connect-Map (sch-parse 任务六产出) 优先; 缺失时 netlist + CBIT表
做法:
  ① SCH-Connect-Map 存在 → 直接参考解析 "需闭合:" 行 (确定性, 不重做原理图)
  ② SCH-Connect-Map 缺失 → 用 gen_paths.py 从 netlist 追踪通路 (path-finder 脚本化):
     python gen_paths.py --netlist Project/DALI/CSV_CONNECTIVITY.NET --cbit Project/DALI/CBIT表-DALI.xlsx --json
     → stdout 人类可读通路文档 + 尾部 PATH_LIST JSON (agent 规格 path_list)
输出: path_list [{dut_pin, source, side, via_relays[{name,cbit,type,state,annotation}], intermediate_source}]
边界: gen_paths.py 是通路追踪工具 (BFS→path_list), 不生成 SCH-Connect-Map;
      完整 SCH-Connect-Map.txt 生成归 sch-parse agent (任务六), 不脚本化
```

### Phase 3: 通路命名 (cbit-path-namer) [待评估]
```
输入: path_list + single_point_defines
做法: 通路继电器 #define 的命名只有本阶段产出（命名规则见 cbit-principles.md）
      → 输出 path_defines (#define 块)
```

### Phase 4: 验证 (脚本化)
```
执行: python gen_cbit_defines.py --cbit <CBIT表> --stat Component-Statistic.txt --verify <StdAfx.h>
      [加 --map SCH-Connect-Map.txt 跑 V2/V7]
输入: 定义文件 (或脚本刚生成的单点块) + cbit_map + (可选) Component-Statistic + SCH-Connect-Map
输出: V1~V8 校验报告:
      V1 no-dup / V2 path-integrity(--map) / V3 naming / V4 range / V5 coverage
      / V6 fs-pair / V7 fpvi-naming(--map) / V8 relay-state(--stat)
      → OVERALL PASS/FAIL + Issues 明细
```

**已有定义文件时的 check**: 独立运行 Phase 4（脚本 `--verify`），验证已有 StdAfx.h 定义正确。**存在即冻结：验证通过即可，不更新。**

## 编排器执行规则

**1. 禁止跳步:** Phase N 的结果确认前，不得开始 Phase N+1。

**2. 禁止并行:** 各 Phase 严格串行，因为每阶段依赖上一阶段输出。

**3. 失败处理:** 任一 Phase 返回 FAIL → 停止，报告用户，不继续。

**4. 执行方式:**
```
P1/P4: 直接调脚本 (gen_cbit_defines.py), 不调子 agent (脚本化)
P2:    优先参考 SCH-Connect-Map; 缺失时直接调脚本 (gen_paths.py --json), 不调子 agent (脚本化)
P3:    调子 agent (cbit-path-namer) — 命名优先级含人工判断, 不脚本化
```

## 铁律

**1. 阶段门控:** 串行四阶段，每阶段完成才进下一阶段。不可跳步、不可并行。

**2. 存在即冻结:** 定义文件已存在 → 仅 check，不更新（除非用户要求更新）。

**3. 数据来源固定:** 单点定义取 CBIT 表 + Component-Statistic（脚本动态读）；通路优先参考 SCH-Connect-Map（sch-parse 产出），缺失时用 gen_paths.py 从 netlist 追踪（不重做原理图解析，不生成 SCH-Connect-Map）。

**4. 跨项目隔离:** 每项目的继电器命名、通路拓扑独立，不确定就问用户。

**5. 验证必须有:** P4 校验必须执行——定义是否正确靠它把关。脚本 `--audit-rules` 确认规则覆盖未丢。

**6. 通路继电器来源:** 有 SCH-Connect-Map → 完整四阶段，可含通路继电器（本流程内定义）。
