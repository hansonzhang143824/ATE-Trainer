# OTP_READ_PRE_POST_BURN-案例4（MTP · 无线充项目）

> 黄金案例：MTP 家族（READBACK / BURN），唯一含 **CRC-16/XMODEM 完整性闭环** 与 **控制器命令式读/写端口** 的样本。
> 来源：用户 2026-09-07 提供（DLP 加密 txt，用 DSH read 工具读取；Bash/grep 只见密文）。**文件内含两个同名 `MTP_TRIM_READBACK`（1–874 与 1397–2271）——2026-09-07 经逐段比对（函数头/AFX/声明区/配置写/CRC 校验/comp 门控/datalog 尾全部一致），两版功能等价，属重复收录（样本整理时新旧版未改名或重复粘贴），保留不影响参考。**

## 函数清单
| 函数 | 行范围 | 职责 |
|------|--------|------|
| `MTP_TRIM_READBACK`（v1） | 1–874 | 回读：配置写→端口 0x0013–0x0016 顺序读全部信息页→set_read_back(reg0x0070–8f)→CRC 校验 + (TTR_MODE==CP) comp_prog_to_read→`_RB` 参数全量 datalog |
| `MTP_TRIM_BURN` | 877–1394 | 烧录：working（assy reg0x70–8f + 校准值 + lot/wafer/XY/版本）组 136B buffer→`do_crc` 算 CRC→CP 闸门内写使能 0x5A→写端口 0x001C–0x001F 逐字烧（每组 delay_us 500）→CRC 随数据烧入→copy_work_to_prog→CRC_CODE_CHECK_L/HByte 出结果 |
| `MTP_TRIM_READBACK`（v2） | 1397–2271 | 与 v1 同构的回读（待确认版本/flow 差异） |

## MTP 读/写协议（本项目实例——地址与键值全部是项目变体）
- 配置写（读）：0x1000=0xC0、0x1002=0x88（禁 MCU bit7/FORCE_OSC96M）、0x4918=0x80（MTP 读控制权切 AP）、0x0017=0x04（byte read）、0x0012=0xFF、0x0010=0x80（information 域）、**0x001A=0xA5（读使能）**
- 配置写（烧）：0x1002=0x8C（i2c_disMCU, burn only）、0x0012=0xFF（选全部 SECTOR）、0x0010=0x80+0x0011=0x00、**0x001A=0x5A（写使能）**
- 读端口 0x0013–0x0016（每 4 读=1 个 32bit 字，顺序消费）；写端口 0x001C–0x001F
- 信息页 136B 布局：trim 码区(reg0x70–8f, 32B)→RX/TX 校准区（SC/LC × 1Ball/4Ball Gain/Offset/Dummy）→VRECT/VOUT/VRECT2VOUT/GP2/GP4/VDD 校准区→lot id(8B)→wafer id(12B)→X/Y/版本→ATE_reserved(8B)→CRC(L/H)
- CRC：`do_crc(test_buff, 136)`，CRC-16/XMODEM（POLY16=0x1021，seed 0x0000），烧前算→随数据烧入→读后重算比对→`CRC_Read_Same_As_Burn_Flag`
- 电源：VRECT_BST1_PGND_FOVI + V5V_ACM；BURN 时 V5V 斜坡（0.5 slope 参数）

## 类判据增量（MTP 独有贡献）
1. 控制器命令式读/写：数据走固定端口，逻辑字地址只体现在 assy 节点名（reg0x00XX）
2. CRC 完整性闭环（烧前算+读后验）——MTP 大容量所需的防烧错机制
3. `Burn_Same_As_Read_Flag` / `CRC_Read_Same_As_Burn_Flag` 双验证
4. ~~`BurnKey 逐工位真假密钥`在本项目由 CP 流程闸门整体替代~~ **已确认（2026-09-07 用户）**：CP 流程全新故由流程闸门替代；**MTP 若有 FT 复烧场景，同样回到逐工位真假密钥**——密钥闸门是 OTP/MTP 家族通用机制，非 OTP 专属

## 卫生问题
- `Burn_Same_As_Read_Flag`/`CRC_Read_Same_As_Burn_Flag` 在 v1 中声明并赋值但未 datalog
- 大量 0x00 占位写（Dummy/Reserved 区）为协议要求，非遗漏
