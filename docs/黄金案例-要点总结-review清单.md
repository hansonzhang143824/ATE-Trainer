# 黄金案例「要点总结」review 清单（待用户 action）

> 派生自 `knowledge/references/material_status.json` 的 `goldenCases` 段（`scripts/gen_material_status.py` 生成，重跑 `--write-review` 刷新）。
> 规则：**新增/修订的任何总结文档必须由用户 review 确认才算落地** —— `skills/nuvolta-codegen.md` §6.1 第 4 条（**自审不算过门**）。
> 状态：**全部未 review**（2026-09-13 用户要求登记为待办，见 `MEMORY.md` ▶ 待办第 3 条）。

## 一、怎么 review（对每份 `.md` 问 4 句）

1. **角色抽象对不对** —— 里面对 PIN/节点/源表的描述是「角色」还是本项目具体名字？能否跨项目迁移
2. **四类关键特殊结构齐不齐** —— ① 被测件本体结构 ② 大电流/差分路径→浮动源 ③ 配对/台阶结构 ④ 测试方法本质
3. **协议/变体有没有被误当类判据** —— 项目专有的寄存器/密钥/继电器/量程应标为「变体」，不能当该类的通用判据
4. **档位归属对不对** —— 该是 Tier1（通用方法）/ Tier2（类型层）/ Tier3（原文）？

## 二、待 review 清单（18 份，与台账一一对应）

| # | 要点总结 | 对应案例 | 总结类型 | 归属参数类型 | 总结大小 | review |
|---|---|---|---|---|---|:---:|
| 1 | `HS_ZCD.md` | `HS_ZCD.cpp` | 标准要点总结 | Current Threshold | 2K | ☐ |
| 2 | `LS_ZCD.md` | `LS_ZCD.cpp` | 标准要点总结 | Current Threshold | 2K | ☐ |
| 3 | `OTP_READ_PRE_POST_BURN-案例1.md` | `OTP_READ_PRE_POST_BURN-案例1.txt` | 分支注解 | OTP·MTP | 2K | ☐ |
| 4 | `OTP_READ_PRE_POST_BURN-案例2.md` | `OTP_READ_PRE_POST_BURN-案例2.txt` | 分支注解 | OTP·MTP | 1K | ☐ |
| 5 | `OTP_READ_PRE_POST_BURN-案例3.md` | `OTP_READ_PRE_POST_BURN-案例3.txt` | 分支注解 | OTP·MTP | 1K | ☐ |
| 6 | `OTP_READ_PRE_POST_BURN-案例4.md` | `OTP_READ_PRE_POST_BURN-案例4.txt` | 分支注解 | OTP·MTP | 3K | ☐ |
| 7 | `OTP_READ_PRE_POST_BURN-案例5.md` | `OTP_READ_PRE_POST_BURN-案例5.txt` | 分支注解 | OTP·MTP | 1K | ☐ |
| 8 | `OVP.md` | `OVP.cpp` | 标准要点总结 | VBAT OVP | 2K | ☐ |
| 9 | `Rdson.md` | `Rdson.cpp` | 标准要点总结 | RDSON | 2K | ☐ |
| 10 | `TM1205_TRX_BST_UV_GD.md` | `TM1205_TRX_BST_UV_GD.cpp` | 标准要点总结 | Diff Pair | 4K | ☐ |
| 11 | `TM130_Trim_VBG.md` | `TM130_Trim_VBG.cpp` | 标准要点总结 | VBG | 2K | ☐ |
| 12 | `TM130_sub_measure.md` | `TM130_sub_measure.cpp` | 标准要点总结 | VBG | 2K | ☐ |
| 13 | `TM623_Trim_BUCK_HS_Gain.md` | `TM623_Trim_BUCK_HS_Gain.cpp` | 标准要点总结 | BUCK HS Gain | 2K | ☐ |
| 14 | `TM623_sub_measure.md` | `TM623_sub_measure.cpp` | 标准要点总结 | BUCK HS Gain | 2K | ☐ |
| 15 | `UVLO.md` | `UVLO.cpp` | 标准要点总结 | PSM_THREHOLD, UVLO, VC_OFFSET | 2K | ☐ |
| 16 | `sub-measure-template.md` | `sub-measure-template.cpp` | 标准要点总结 | BUCK HS Gain, VBG | 2K | ☐ |
| 17 | `tm600-normal-highcurrent.md` | `tm600-normal-highcurrent.cpp` | 标准要点总结 | — | 2K | ☐ |
| 18 | `toggle-template.md` | `toggle-template.cpp` | 标准要点总结 | VAC GD present, VC_CLAMP_LOW | 2K | ☐ |

## 三、review 通过之后

1. 记录结论（在 `material_status.json` 对应案例记 `reviewed: true`，或直接在本清单勾选）
2. 若发现总结有误 → 改 `.md` → 重跑 `gen_material_status.py`（哈希变化会被 `--check` 报出）→ 再来一轮 review
3. 更新 `MEMORY.md` ▶ 待办第 3 条的进度
