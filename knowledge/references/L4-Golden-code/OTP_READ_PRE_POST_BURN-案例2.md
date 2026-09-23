# OTP_READ_PRE_POST_BURN-案例2（OTP · 项目B）

> 黄金案例：OTP 三件套最简洁版（0xF0–0xFF 单窗口、单步上电），带多器件分支（NU6801/6802/6803）。
> 来源：用户 2026-09-07 提供（DLP 加密 txt，用 DSH read 工具读取）。

## 函数清单
| 函数 | 行范围 | 职责 |
|------|--------|------|
| `OTP_Read_Pre` | 1–~228 | PRE：读 0xF0–0xFF（16B）；先取 EFUSE_REG_FF working（working_value2，填后未用）；comp_read(0)→FRESH/BURNNED→BURN_FLAG；BURNNED 才 copy_read_to_work |
| `OTP_BURN`（名在文件中段） | ~229–347 | BURN：working→BestCode；BurnKey=FRESH?0x01:0x00；TEST_FLOW==FT/CP/HTOL_Burn 闸门内物理烧写（BestCode→0xF0–FF + BurnKey→0x53，delay 50ms）；copy_work_to_prog 无条件；`Burn_Done->SetTestResult(site,0,1)` |
| `OTP_Read_Post` | 349–579 | POST：同 PRE 读；`comp_prog_to_read`→ReadSameAsBurn（计算后未用——卫生残留）；get_read_back→PosRd 参数 |

## 项目协议（变体）
- 窗口 0xF0–0xFF；DEV_ADDR 宏；SITE_NUM；`entertestmode()`（无 keyopen）
- 电源：VBAT_ACM + VCC_ACM 双源单步 V_TYP_VBAT；继电器 K30_VBAT_Cap/K57_SDA_PU/K53_SCL_PU/K25_VCC_Cap
- 触发键 0x53 = NVM_PROG_ALL 字段（注释 `field[(NVM_PROG_ALL, 1)]`）
- 器件分支：`extractIntFromString(DEVICE_SEL)==6801/6803 → PART_ID_TRIM_PreRd；==6802 → PART_ID_TRIM_6802_PreRd`（PRE 与 POST 同构分支）
- PRE 里被注释的 `trim_reg.sel("addr_trim").set_working(1)` ——地址 trim 特殊处理的历史痕迹

## 教学价值
- 三个 OTP 项目中结构最干净，适合当「最小完整参照」
- POST 的 comp_prog_to_read 用法与案例1/3 一致，验证 `ReadSameAsBurn` 语义（read_back == programmed）
