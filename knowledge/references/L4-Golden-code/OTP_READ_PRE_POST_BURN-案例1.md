# OTP_READ_PRE_POST_BURN-案例1（OTP · 项目A）

> 黄金案例：OTP 家族完整三件套（PRE / BURN / POST），最完整的 FT 复流场景（含 SN 随机生成与复烧保护）。
> 来源：用户 2026-09-07 提供（DLP 加密 txt，用 DSH read 工具读取；Bash/grep 只见密文）。

## 函数清单
| 函数 | 行范围 | 职责 |
|------|--------|------|
| `OTP_PRE_READ` | 1–623 | PRE：读 0xC0–0xEF（48B）+ 单独预读 0xBA + SN(0xEC–0xEF)；comp_read(0) 判 FRESH/BURNNED → 全局 BURN_FLAG；BURNNED 才 copy_read_to_work |
| `OTP_BURN` | 626–972 | BURN：working→BestCode；FT+fresh 随机生成 SN（`device_sn_assign_random`）+ PROG_VERSION 写 working；解锁 Key→烧写→结束命令→copy_work_to_prog |
| `OTP_POST_READ` | 974–1576 | POST：同 PRE 读流程；comp_prog_to_read + Program_version_check 双检 |

## 项目协议（变体，勿当类判据）
- 寄存器窗口 0xC0–0xEF；SN 在 0xEC–0xEF，程序版本 0xEB；预读 0xBA
- 电源：BAT_PMID_BTST_FOVI（0→5V 两步）+ REGN_ACM 5V；继电器含 K26_BAT_Cap/K4_REGN_Cap/K23_SDA_PU/K24_SCL_PU
- `entertestmode()` + `keyopen()`；`dcm.I2CConnect/Disconnect`
- 烧写解锁 Key：FRESH→0x80→0xA0 + 0x83→0xAA（BURNNED→全 0x00，假密钥）；写后读 0xAA 确认
- 烧写结束命令：0x01→0xBE，delay 50ms
- 验证节点名 `EFUSE_REGISTER`（案例2/3 用 `EFUSE_REG_REGISTER`——命名项目差异）
- BURN 项参数名为 `MTP_BURN`（遗留命名，实为 OTP 项目）
- POST 双检：`Read_same_as_burned`（comp_prog_to_read）+ `Program_version_check`（fresh 时比 REG_EB vs PROG_VERSION 常量）；`TRIM_FLOW!=1 || BURNNED` 强制 pass（仅 FT+fresh 真判）
- POST 强通逻辑意味着 comp 校验只在「FT 流 + fresh（刚烧完）」时有意义

## 类判据命中（对照 func_type_index #3/#4）
- 数据写+密钥写、密钥逐工位 FRESH 真/BURNNED 假 ✅
- working→BestCode→copy_work_to_prog ✅
- comp_read(0)→FRESH/BURNNED→BURN_FLAG 全局状态 ✅
- 无模拟量测量、出值全为代码快照 ✅

## 卫生问题（复制粘贴残留，非框架特征）
- PRE 注释编号跳号/重复（43 出现两次）；IREG/TRKL 相关数组顺序与编号错位
- BURN 中大段注释掉的 Key 备选写法
