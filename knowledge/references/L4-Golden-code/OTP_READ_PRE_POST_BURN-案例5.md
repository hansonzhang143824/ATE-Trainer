# OTP_READ_PRE_POST_BURN-案例5（MTP · PRE，与案例4 同项目）

> 黄金案例：**MTP 项目的 PRE 读** + 独有 **QC 码值变换层**（16bit 补码 → Gain/Offset 物理量）。
> 来源：用户 2026-09-07 对话粘贴转录（原文件未落盘；如与原始工程有出入以工程为准）。函数 `MTP_PRE_READ`，参数后缀 `*PreRd`。

## 结构要点（对照家族骨架）
- ①AFX 块 ~120 个 CParam（`*PreRd`）
- ②声明：`double *_Code_RB[]`（trim/sel 字段）+ ULONG Reg_0x70–0x8f + 校准/lot/wafer ULONG 数组 + `BOOL Burn_Same_As_Read_Flag / CRC_Read_Same_As_Burn_Flag`（声明未用）
- ③MTP 读（与案例4 READBACK 同协议）：cbite(VRECT/V5V/V1P8 Cap + SCL/SDA PU)→VRECT_FOVI+V5V_ACM→entertestmode→配置写→端口 0x13–0x16 顺序读→下电
- ④set_read_back：仅 trim 码区 reg0x0070–0x008f
- ⑤**【独有】QC 码值变换层**：`if (TRIM_FLOW == QC)`：16bit 组合（high*256+low）→ >32768 取负（补码）→ Gain=`1±code/1e4`、Offset=`±code/1e4` → 写**全局数组** `Gain_*_read/Offset_*_read` 供下游测试项消费；本项 datalog 仍用原始码
- ⑥datalog：trim()/sel().get_read_back → `*_Code_RB` → SetTestResult；原始字节（Gain/Offset/Dummy/CRC）直接 SetTestResult

## 与 OTP PRE 的关键差异（判据补充）
1. **无 comp_read(0) FRESH/BURNNED 判定、无 copy_read_to_work**——QC/CP 流器件全新，判状态无意义；fab 预烧的 lot/wafer 信息已在
2. 读出内容 = 全信息页（≥OTP PRE 的范围），含校准区与 CRC
3. 码值变换层把「读码」升级为「读物理量（供下游用）」——PRE 不只 snapshot，还是后续测试项的基准装载步骤

## 已知 bug（转录时以 NOTE(2026-09-07) 注释在源码中标记）
- VDD-Gain 变换段两个分支写 `Gain_GP4_read[site]`，应为 `Gain_VDD_read[site]`（copy-paste 残留）
- `MNT_V2X_Code_RB`、两个 Flag 声明未用
