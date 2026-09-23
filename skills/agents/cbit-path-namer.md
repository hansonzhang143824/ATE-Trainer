---
name: cbit-path-namer
description: CBIT Phase4 — 根据Phase3通路列表，按命名优先级生成通路继电器#define（已脚本化→gen_path_defines.py，规格文档；多源同PIN尾缀_A/B/C属正常命名全部发布，仅⚠非有效不发布）
model: sonnet
tools: Read, Write
---

# CBIT Path Namer — Phase 4

> **已脚本化 (2026-08-10)** → **`D:\Newtest\CLAUDE_PROCESS\gen_path_defines.py`**（架构原则: 推理→agent, 固定→脚本）。
> 本文件降级为**规格文档**，保留规则溯源（下方命名优先级即脚本 RULE_COVERAGE P-DEF-01~13 的来源）。
> **脚本用法**:
> ```
> python gen_path_defines.py                                   # SCH-Connect-Map `需闭合:` → 352 通路 #define → StdAfx.h 2.x 段
> python gen_path_defines.py --no-write                        # 预览段 (不写)
> python gen_path_defines.py --verify                          # SCH-Connect-Map 一致性校验
> python gen_path_defines.py --verify                        # StdAfx.h 2.x 段权威校验
> python gen_path_defines.py --audit-rules                     # RULE_COVERAGE 机器自检 (P-DEF-01~13)
> ```
> **多源同 PIN 命名铁律（2026-08-26 用户拍板）**: 多个源/多个 FPVIe 通道连到同一 PIN → 在命名尾缀加 `_A/_B/_C` 区分（如 `K_FPVIH_TO_ACDRV1_A` / `K_FPVIH_TO_ACDRV1_B`）。**这是正常命名，不算 warning/歧义，全部发布**。只有 ⚠非有效（F/S 未同时闭合）通路不发布（脚本 parse 阶段已自动跳过）。`--verify` 与发布同预期。
> **仍需 agent (复核, 不脚本化)**: 仅 `_B` 类 CH0/CH1 双通道取舍（同一物理源表两个通道的取舍合理性）仍需本 agent 复核。
> **写入纪律**: StdAfx.h 是 DLP 编译头 → 脚本写入只经 **PowerShell 下 python**（沙箱 Bash 非写透明会清空文件）；脚本已先编码后 `open('wb')`（编码失败绝不截断）。

## 输入

来自 Phase 3 的 `path_list`:
```
[{dut_pin, source, side, via_relays[], intermediate_source}, ...]
```

## 通路类型

| 类型 | 源 | 目的地 | 格式 |
|------|-----|--------|------|
| 类型2 | 稀缺源表 | DUT_PIN | `K_<源>_TO_<PIN>` |
| 类型1 | 稀缺源表 | 公共节点 | `K_<源>_TO_<Net>` |
| 类型3 | 其他源 | DUT_PIN | `K_<PIN>_<源>` |

## 多路径命名优先级

**优先级 0 优先检测，检测到则跳过后续优先级。**

| 优先级 | 条件 | 格式 | 示例 |
|:---:|------|------|------|
| **0** (特殊) | 同一CBIT控制的FORCE+SENSE对 (全词) | `K_<源><side>_TO_<PIN>_FOS_SNS` | `K_FPVIH_TO_KLV_FOS_SNS` |
| **1** | 连接稀缺源表的 High/Low 端不同 | `K_<源>H_TO_<PIN>` / `K_<源>L_TO_<PIN>` | `K_FPVIH_TO_SW2` / `K_FPVIL_TO_SW2` |
| **2** | H/L 相同但途经其他源表不同 | `K_<源>_TO_<PIN>_<途经源>` | `K_FPVI_TO_SW2_ACM` / `K_FPVI_TO_SW2_FOVI` |
| **3** | 完全一致 | `K_<源>_TO_<PIN>_A/B/C` | `K_FPVI_TO_SW2_A` |

## 工作流

```
Step 1: 按 {dut_pin, source} 分组 paths
        ↓
Step 2: 每组内检测多路径冲突
        ↓
Step 2.5: FORCE/SENSE 合并检测（新增，优先级0）
        如果两个不同 dut_pin 的路径共享完全相同的 via_relays (CBIT集合相同):
          a. 比较 dut_pin 名称，去除站点后缀 _Sx 后:
             情况A: dut_pin_A = KLV_FORCE_S1, dut_pin_B = KLV_SENSE_S1
                    但实际是同一继电器的两个pole → 合并 dut_pin = KLV_FOS_SNS
             情况B: 名称仅 _FORCE / _SENSE 部分不同 + CBIT集相同
                    → 去除 _FORCE_Sx / _SENSE_Sx 后缀，加 _FOS_SNS
          b. 合并后: 两个路径合为一个，via_relays 不变
          c. 命名: K_<源><side>_TO_<merged_pin>
        ↓
Step 3: 按优先级选择命名:
        优先级1: side 不同 → H/L 后缀
        优先级2: intermediate_source 不同 → 源表后缀
        优先级3: 完全相同 → A/B/C
        唯一路径 → 直接用 K_<源>_TO_<PIN>
        ↓
Step 4: 生成 #define
        值 = via_relays 中各 relay 的 CBIT 值 (逗号分隔)
        ↓
Step 5: 同样方式处理类型1 (公共节点) 和类型3 (其他源)
```

## 输出格式

```cpp
// 2.1 FPVIe -> SPST BUS -> DUT Pin
// SW2 H: FPVIe_FH/SH_BUS -> K46 -> K49(SetOn) -> SW2
#define K_FPVIH_TO_SW2              46,49    // K46_BUS_SW1 + K49_ACM_SW2

// 2.3 Other Sources -> DUT Pin
// ACM200 -> SW2
#define K_SW2_ACM                    49       // = K49_ACM_SW2
```

## 铁律

- 命名优先级不可跳过 (先检查级1，再级2，再级3)
- 每个路径必须有对应的 CBIT 值来源
- via_relays 为空 → 路径无效，不定义
- 多源/多通道同 PIN → 尾缀 `_A/_B/_C` 属**正常命名**，全部发布；仅 ⚠非有效 不发布（2026-08-26 用户拍板）
