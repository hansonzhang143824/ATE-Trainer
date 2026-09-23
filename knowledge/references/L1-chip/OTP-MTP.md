# OTP / MTP — 芯片 NVM Block 介绍

> 依据：用户 2026-09-07 口述（初稿由对话解释整理，待用户补充芯片手册级细节后增强）。

## 概念

| | OTP | MTP |
|---|-----|-----|
| 全称 | One Time Program | Multiple Program（可反复擦写） |
| 烧录次数 | 一次 | 多次 |
| 典型容量 | 小（几十字节 eFuse 映射） | 大（百字节级信息页 + 扇区） |
| 读通路 | 烧录位直接内存映射，直读寄存器窗口 | 经 NVM 控制器：AP 写配置（切权限/选页/字节模式/使能键）后从固定数据端口顺序读 |
| 完整性校验 | 一般无 | **CRC**（因容量大、扇区编程，需防烧错/读错） |

## 在测试中的意义

1. **烧录内容的构成**：Trim BestCode（必须）+ Option bit（必须）+ 其他数据（可选：Gain/Offset 校准系数、SN 随机码、年月日、lot/wafer 追溯信息、程序版本）
2. **生命周期与产线流程的对应**：
   - 晶圆厂预烧 lot/wafer/XY 追溯信息（MTP 信息页）→ CP 阶段即可读
   - FT/Trim 阶段：Trim 求 BestCode → working 槽 → BURN 烧入 → POST 复验
   - 复流（QA/QUAL/TempChar/HTOL）：PRE 读回已烧内容装载 working/programmed，禁止重烧
3. **FRESH/BURNNED 的物理含义**：OTP 全零 = 未烧；MTP 由流程阶段与 CRC/comp 判定
4. **密钥机制**：烧录 = 数据 + 密钥；密钥真假按工位 FRESH/BURNNED 选择，防止已烧器件被二次编程损坏

## 关联

- 测试方法：`../L3-method/OTP-MTP-Readback-Burn.md`
- 黄金案例：`../L4-Golden-code/OTP_READ_PRE_POST_BURN-案例1~5.txt`（+ 同名 .md 注解）
- 参数类型索引：`../param_type_index.md`（OTP·MTP 行）
- 功能类型：`../func_type_index.md` #3（Readback）/#4（Burn）
