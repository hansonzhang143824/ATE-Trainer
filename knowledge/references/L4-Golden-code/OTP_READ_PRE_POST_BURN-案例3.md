# OTP_READ_PRE_POST_BURN-案例3（OTP · 项目C）

> 黄金案例：OTP 三件套 + 两个独有要素——**地址变更特判**（ADDR_CHANGE）与**专用验证节点**（EFUSE_REG_REGISTER_BURN）、**流程门控的 copy_read_to_prog**（QA/QUAL/TempChar）。
> 来源：用户 2026-09-07 提供（DLP 加密 txt，用 DSH read 工具读取）。

## 函数清单
| 函数 | 行范围 | 职责 |
|------|--------|------|
| `OTP_Read_Pre` | 1–~318 | PRE：读 0xF0–0xFF；ADDR_CHANGE 特判；comp_read(0)→FRESH/BURNNED→BURN_FLAG；BURNNED: copy_read_to_work + （TEST_FLOW==QA/QUAL/TempChar 时）`copy_read_to_prog` |
| `OTP_BURN`（段名） | ~319–425 | BURN：working→BestCode；BurnKey=FRESH?0x01:0x00；FT/CP/HTOL_Burn 闸门内：烧前配置写（0x65/0x66 D2A_EN_MNT、0x57 TM_MUX_ATEST0）→ BestCode→0xF0–FF → BurnKey→0x53，delay 20ms；闸门内 copy_work_to_prog；`Burn_Done` 无条件 |
| `OTP_Read_Post` | 427–731 | POST：同 PRE 读；**`EFUSE_REG_REGISTER_BURN`.comp_prog_to_read** → `Check_pass[site]` → `Burn_Check_Pass->SetTestResult`（验证结果参数化）；被注释的 Part_Num==3326 分支 |

## 项目协议（变体）
- 窗口 0xF0–0xFF；DEV_ADDRESS 宏；`entertestmode_trim()`（PRE）/ `entertestmode()`（POST）
- 电源：VBAT_ACM + VCC_FOVI（+SW12_PGND_FOVI 只在 PRE）；POST 精简为 VBAT+VCC
- ADDR_CHANGE 特判：`Add_Read[site]==0xCE` 且 `spec[DEVICE_SEL]("ADDR_CHANGE")` → `trim_reg.sel("add_trim").set_read_back(0, site)`——把地址 trim 的读回值强制归 0（通信地址迁移场景）
- 烧前配置写（D2A_EN_MNT / TM_MUX_ATEST0）是三例中唯一的烧前 chip 配置

## 类判据增量（本项目独有贡献）
1. `copy_read_to_prog` 的流程门控（QA/QUAL/TempChar 复流把芯片实况登记进 programmed 槽）
2. 验证节点可细分：全寄存器组（REGISTER）vs 烧录子集（REGISTER_BURN）
3. 验证结果必须参数化出结果（Burn_Check_Pass）
