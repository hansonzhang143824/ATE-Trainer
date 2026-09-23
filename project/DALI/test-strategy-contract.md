# DALI 测试策略契约（test-strategy-architect）

> 生成时间：2026-09-17 00:2x +0800 ｜ 每 TM 一张固定九行表；只列可执行内容。
> 来源键：`M` = `project/DALI/meta/dali_tm_meta.json`（`functions[i]` 索引）；`Y` = `project/DALI/meta/test_conditions.yaml`；`P` = `ForCodexDebug/source/Pin_Channel_define.h`（行号）；`S` = `ForCodexDebug/source/StdAfx.h`（行号）；`IR` = `project/DALI/schematic-ir.json`；`G` = `knowledge/references/L4-Golden-code/`。
> 已查证定义：源表对象名取自 `S`（`extern` 声明）与 `P`（通道宏）；继电器 K 号取自 `IR` 的 accepted proof 并集。
> 未在冻结输入中出现的内容，只在所属单元格写“定点补证：<具体缺口>”。

## 2. TM000 — `Iq_Standby`（Top；row 2；`M.functions[0]`；`Y L16`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | 睡眠静态电流；标称 23（无数字 iq 限定）；单位 uA（`M.functions[0].expectValue/unit`） |
| 2 | Golden依据 | 定点补证：Golden 未提供（`G` 无 Iq/待机电流案例） |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61） |
| 4 | CBIT闭合 | 无逐 TM 引脚绑定（`IR.pinsPerTm` = UNKNOWN）；定点补证：TM000 引脚绑定 |
| 5 | 上电 | ① `vbat=4.4`（ramp 100e-6）→ ② 写字段 `VAC1_APORT_DET_ENABLE=0,VAC2_APORT_DET_ENABLE=0,VAC_SNK_DET_SEL=0` → ③ `delay[10e-3]`（无 `en_tm`） |
| 6 | 寄存器 | 写：`VAC1_APORT_DET_ENABLE=0`、`VAC2_APORT_DET_ENABLE=0`、`VAC_SNK_DET_SEL=0`；无 DFT 读操作 |
| 7 | 测试 | 无激励；monitor = `I(VBAT)`；公式 `Iq=I(VBAT)`；限值 23 uA；定点补证：判定容差 |
| 8 | 下电 | ① 释放 VBAT 源 → ② `vbat` 归零 |
| 9 | Log | `Iq_uA[site]`；per-site；fail = 越 23 uA（容差定点补证） |
## 3. TM000_1 — `Iq_Standby`（w/ VAC_PLUG；row 3；`M.functions[1]`；`Y L42`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | 睡眠静态电流（VAC_PLUG 模块开启）；标称 = 无；单位 uA（`M.functions[1].expectValue` = null） |
| 2 | Golden依据 | 定点补证：Golden 未提供 |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61） |
| 4 | CBIT闭合 | 无逐 TM 引脚绑定；定点补证：TM000_1 引脚绑定 |
| 5 | 上电 | ① `vbat=4.4`（ramp 100e-6）→ ② 写字段 `VAC1_APORT_DET_ENABLE=1,VAC2_APORT_DET_ENABLE=1,VAC_SNK_DET_SEL=0`（无 delay） |
| 6 | 寄存器 | 写：`VAC1_APORT_DET_ENABLE=1`、`VAC2_APORT_DET_ENABLE=1`、`VAC_SNK_DET_SEL=0`；无 DFT 读操作 |
| 7 | 测试 | 无激励；monitor = `I(VBAT)`；公式 `Iq=I(VBAT)`；限值 = 无（`M.functions[1].expectValue` 空）；定点补证：限值与容差 |
| 8 | 下电 | ① 释放 VBAT 源 → ② `vbat` 归零 |
| 9 | Log | `Iq_uA[site]`；per-site；fail 判据定点补证：限值缺失 |
## 4. TM001 — `Iin_Suspend`（Top；row 4；`M.functions[2]`；`Y L69`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | 工作模式静态电流；标称 = 无；单位 uA（`M.functions[2].expectValue` = null） |
| 2 | Golden依据 | 定点补证：Golden 未提供 |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61） |
| 4 | CBIT闭合 | 无逐 TM 引脚绑定；定点补证：TM001 引脚绑定 |
| 5 | 上电 | ① `en_tm[]` → ② 写字段 `WAKE_UP=1,AC1_GATE_ON=1` → ③ `vbat=3.7`（ramp 100e-6）→ ④ `delay[10e-3]` |
| 6 | 寄存器 | 写：`WAKE_UP=1`、`AC1_GATE_ON=1`；无 DFT 读操作 |
| 7 | 测试 | 无激励；monitor = `I(VBAT)`；公式 `Iin=I(VBAT)`；限值 = 无；定点补证：限值与容差 |
| 8 | 下电 | ① 释放 VBAT 源 → ② `vbat` 归零 |
| 9 | Log | `Iin_uA[site]`；per-site；fail 判据定点补证：限值缺失 |
## 5. TM101 — `LP_VBG`（HSKP；row 5；`M.functions[3]`；`Y L95`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | 低压 BG 电压；标称 1.27；单位 V（`M.functions[3].expectValue/unit`） |
| 2 | Golden依据 | 定点补证：Golden 未提供 |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；VDM → `VDM_SDA_ACM`（P L22 / S L71）；ATEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | VDM 通路：`K58`+`K59`（用途：VDM/SDA 引脚接入，IR `pins[VDM_F_S1].requiredRelays=[58,86,137,141,142,143,144,152]` 中的 58/59）；VBAT 通路见 IR `pins[VBAT_F_S1]`；定点补证：ATEST0 引脚绑定 |
| 5 | 上电 | ① `vbat=4`（ramp 100e-6）→ ② `en_tm[]` → ③ `vset[vdm,1.2,100e-6,0]`（先对外部 pin 上电）→ ④ 写字段 `EN_ATEST0=1,ATEST0_MUX=1` → ⑤ `delay[1e-3]` → ⑥ `vset_off[vdm]` |
| 6 | 寄存器 | 写：`EN_ATEST0=1`、`ATEST0_MUX=1`；无 DFT 读操作 |
| 7 | 测试 | 无激励；monitor = `V(ATEST0)`；公式 `VBG=V(ATEST0)`；限值 1.27 V；定点补证：判定容差 |
| 8 | 下电 | ① `vset_off[vdm]` → ② VBAT 源释放 → ③ `vbat` 归零 → ④ 释放 monitor |
| 9 | Log | `VBG_V[site]`；per-site；fail = 越 1.27 V（容差定点补证） |
## 6. TM102 — `LP_VBG_BF`（HSKP；row 6；`M.functions[4]`；`Y L121`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | 低压 BG buffer 电压；标称 1.27；单位 V（`M.functions[4]`） |
| 2 | Golden依据 | 定点补证：Golden 未提供 |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；VDM → `VDM_SDA_ACM`（P L22 / S L71）；ATEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | VDM 通路：`K58`+`K59`（用途：VDM/SDA 引脚接入）；定点补证：ATEST0 引脚绑定 |
| 5 | 上电 | ① `vbat=4`（ramp 100e-6）→ ② `en_tm[]` → ③ `vset[vdm,1.2,100e-6,0]` → ④ 写字段 `EN_ATEST0=1,ATEST0_MUX=2` → ⑤ `delay[1e-3]` → ⑥ `vset_off[vdm]` |
| 6 | 寄存器 | 写：`EN_ATEST0=1`、`ATEST0_MUX=2`；无 DFT 读操作 |
| 7 | 测试 | 无激励；monitor = `V(ATEST0)`；公式 `V=V(ATEST0)`；限值 1.27 V；定点补证：判定容差 |
| 8 | 下电 | ① `vset_off[vdm]` → ② VBAT 源释放 → ③ `vbat` 归零 → ④ 释放 monitor |
| 9 | Log | `VBG_BF_V[site]`；per-site；fail = 越 1.27 V（容差定点补证） |
## 7. TM103 — `LP_HR_0P5U`（HSKP；row 7；`M.functions[5]`；`Y L147`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | 低压 HR 电流；标称 0.5；单位 uA（`M.functions[5]`） |
| 2 | Golden依据 | 定点补证：Golden 未提供 |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；ATEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | 定点补证：TM103 引脚绑定（`IR.pinsPerTm` = UNKNOWN） |
| 5 | 上电 | ① `vbat=4`（ramp 100e-6）→ ② `en_tm[]` → ③ 写字段 `EN_ATEST0=1,ATEST0_MUX=4` → ④ `delay[1e-3]` |
| 6 | 寄存器 | 写：`EN_ATEST0=1`、`ATEST0_MUX=4`；无 DFT 读操作 |
| 7 | 测试 | 无激励；monitor = `I(ATEST0)`；公式 `I=I(ATEST0)`；限值 0.5 uA；定点补证：量程档位与判定容差 |
| 8 | 下电 | ① VBAT 源释放 → ② `vbat` 归零 → ③ 释放 monitor |
| 9 | Log | `I_HR_uA[site]`；per-site；fail = 越 0.5 uA（容差定点补证） |
## 8. TM104 — `LP_PTAT_0P5U`（HSKP；row 8；`M.functions[6]`；`Y L173`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | 低压 PTAT 电流；标称 0.5；单位 uA（`M.functions[6]`） |
| 2 | Golden依据 | 定点补证：Golden 未提供 |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；ATEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | 定点补证：TM104 引脚绑定 |
| 5 | 上电 | ① `vbat=4`（ramp 100e-6）→ ② `en_tm[]` → ③ 写字段 `EN_ATEST0=1,ATEST0_MUX=5` → ④ `delay[1e-3]` |
| 6 | 寄存器 | 写：`EN_ATEST0=1`、`ATEST0_MUX=5`；无 DFT 读操作 |
| 7 | 测试 | 无激励；monitor = `I(ATEST0)`；公式 `I=I(ATEST0)`；限值 0.5 uA；定点补证：量程档位与容差 |
| 8 | 下电 | ① VBAT 源释放 → ② `vbat` 归零 → ③ 释放 monitor |
| 9 | Log | `I_PTAT_uA[site]`；per-site；fail = 越 0.5 uA（容差定点补证） |
## 9. TM105 — `VSPRE_MAX_CMP`（HSKP；row 9；`M.functions[7]`；`Y L199`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | VAC-VBAT 比较点；标称 `VAC-VBAT=~1V`；单位 V（`M.functions[7].expectValue/unit`） |
| 2 | Golden依据 | 定点补证：Golden 未提供（`G/toggle-template.md` 可作机制参考，未逐行核对） |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；VAC1 → `VAC123_AMUX_ACM`（P L15 / S L64）；DTEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | VAC1 通路：`K17`+`K70`（IR `pins[VAC1_F_S1].requiredRelays=[17,70,87,90,142,145,146]` 中的 17/70，用途：VAC1 引脚接入）；VBAT 通路见 IR `pins[VBAT_F_S1]`；定点补证：DTEST0 引脚绑定 |
| 5 | 上电 | ① `vbat=4`（ramp 100e-6）→ ② `en_tm[]` → ③ 写字段 `DMUX_EN=1,DMUX_SEL=0` → ④ VAC1 设定（`code2Raw` 内含 `vset[vac1,10,1e-3,0]` 与回零）→ ⑤ `delay[1e-3]` |
| 6 | 寄存器 | 写：`DMUX_EN=1`、`DMUX_SEL=0`；无 DFT 读操作 |
| 7 | 测试 | 激励 = VAC1 设定/回零（`code2Raw`）；monitor = `V(DTEST0)`；判据 `VAC-VBAT≈1 V`；定点补证：判定容差与量化方式 |
| 8 | 下电 | ① VAC1 回零 → ② VBAT 源释放 → ③ `vbat` 归零 → ④ 释放 monitor |
| 9 | Log | `V_CMP_V[site]`；per-site；fail 判据定点补证：容差未定 |
## 10. TM106 — `VBUS_PRST`（HSKP；row 10；`M.functions[8]`；`Y L225`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | VBUS PRST 上升阈值/滞回；标称 `rising vth 3.9V, hys 0.2V`；单位 V（`M.functions[8]`） |
| 2 | Golden依据 | 定点补证：Golden 未提供（`G/toggle-template.md` 可作机制参考） |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；VBUS → `VBUS_DRVH1_ACM`（P L25 / S L74）；DTEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | VBUS 通路：`K3`（IR `pins[VBUS_F_S1].requiredRelays=[3,142,145,146]`，用途：VBUS 引脚接入）；定点补证：DTEST0 引脚绑定 |
| 5 | 上电 | ① `vbat=3`（ramp 100e-6）→ ② `en_tm[]` → ③ 写字段 `DMUX_EN=1,DMUX_SEL=19` → ④ `vbus` 3（ignore=1）→ 3→5 V（ramp 1e-3）→ ⑤ `delay[1e-3]` |
| 6 | 寄存器 | 写：`DMUX_EN=1`、`DMUX_SEL=19`；无 DFT 读操作 |
| 7 | 测试 | 激励 = VBUS 3→5 V 斜坡（1 ms）；monitor = `V(DTEST0)`；判据 = 上升阈值 3.9 V、滞回 0.2 V；定点补证：判定容差 |
| 8 | 下电 | ① `vbus` 回零（ramp 1e-3）→ ② VBAT 源释放 → ③ `vbat` 归零 → ④ 释放 monitor |
| 9 | Log | `Rise[site]`、`Fall[site]`、`Hys[site]`；per-site；fail = 越 3.9 V/0.2 V（容差定点补证） |
## 11. TM108 — `VAC1_PRST`（HSKP；row 11；`M.functions[9]`；`Y L251`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | VAC1 PRST 上升阈值/滞回；标称 `rising vth 4.4V, hys 0.35V`；单位 V（`M.functions[9].expectValue/unit`） |
| 2 | Golden依据 | 定点补证：Golden 未提供（`G/toggle-template.md` 可作机制参考，未逐行核对） |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；VAC1 → `VAC123_AMUX_ACM`（P L15 / S L64）；DTEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | VAC1 通路：`K17`+`K70`（用途：VAC1 引脚接入，IR `pins[VAC1_F_S1].requiredRelays=[17,70,87,90,142,145,146]`）；VBAT 通路见 IR `pins[VBAT_F_S1]`；定点补证：DTEST0 引脚绑定 |
| 5 | 上电 | ① `vbat=3`（ramp 100e-6）→ ② `en_tm[]` → ③ 写字段 `DMUX_EN=1,DMUX_SEL=22` → ④ `vac1` 斜坡（`vset[vac1,10,1e-3,0]`，按 `notes` 3~5 V、1 V/ms）→ ⑤ `delay[1e-3]` |
| 6 | 寄存器 | 写：`DMUX_EN=1`、`DMUX_SEL=22`；无 DFT 读操作 |
| 7 | 测试 | 激励 = VAC1 3→5 V 斜坡（1 V/ms）；monitor = `V(DTEST0)`；判据 = 上升阈值 4.4 V、滞回 0.35 V；定点补证：判定容差 |
| 8 | 下电 | ① `vset[vac1,0,1e-3,0]` → ② VBAT 源释放 → ③ `vbat` 归零 → ④ 释放 monitor |
| 9 | Log | `Rise[site]`、`Fall[site]`、`Hys[site]`；per-site；fail = 越 4.4 V/0.35 V（容差定点补证） |
## 12. TM109 — `VAC2_PRST`（HSKP；row 12；`M.functions[10]`；`Y L277`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | VAC2 PRST 上升阈值/滞回；标称 `rising vth 4.4V, hys 0.35V`；单位 V（`M.functions[10]`） |
| 2 | Golden依据 | 定点补证：Golden 未提供 |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；VAC2 → `VAC123_AMUX_ACM`（P L15 / S L64）；DTEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | VAC2 通路：`K17`+`K19`（IR `pins[VAC2_F_S1].requiredRelays=[17,19,70,87,90,142,145,146]`，用途：VAC2 引脚接入）；定点补证：DTEST0 引脚绑定 |
| 5 | 上电 | ① `vbat=3`（ramp 100e-6）→ ② `en_tm[]` → ③ 写字段 `DMUX_EN=1,DMUX_SEL=21` → ④ `vac2` 斜坡（`vset[vac2,10,1e-3,0]`）→ ⑤ `delay[1e-3]` |
| 6 | 寄存器 | 写：`DMUX_EN=1`、`DMUX_SEL=21`；无 DFT 读操作 |
| 7 | 测试 | 激励 = VAC2 3→5 V 斜坡；monitor = `V(DTEST0)`；判据 = 4.4 V/0.35 V；定点补证：判定容差；注：`notes` 文字写 vac1，与字段 VAC2 不一致 |
| 8 | 下电 | ① `vset[vac2,0,1e-3,0]` → ② VBAT 源释放 → ③ `vbat` 归零 → ④ 释放 monitor |
| 9 | Log | `Rise[site]`、`Fall[site]`、`Hys[site]`；per-site；fail = 越 4.4 V/0.35 V（容差定点补证） |
## 13. TM110 — `VAC3_PRST`（HSKP；row 13；`M.functions[11]`；`Y L303`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | VAC3 PRST 上升阈值/滞回；标称 `rising vth 4.4V, hys 0.35V`；单位 V（`M.functions[11]`） |
| 2 | Golden依据 | 定点补证：Golden 未提供 |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；VAC3 → `VAC123_AMUX_ACM`（P L15 / S L64）；DTEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | VAC3 通路：`K17`+`K18`（IR `pins[VAC3_F_S1].requiredRelays=[17,18,70,87,90,142,145,146]`，用途：VAC3 引脚接入）；定点补证：DTEST0 引脚绑定 |
| 5 | 上电 | ① `vbat=3`（ramp 100e-6）→ ② `en_tm[]` → ③ 写字段 `DMUX_EN=1,DMUX_SEL=20` → ④ `vac3` 斜坡（`vset[vac3,10,1e-3,0]`）→ ⑤ `delay[1e-3]` |
| 6 | 寄存器 | 写：`DMUX_EN=1`、`DMUX_SEL=20`；无 DFT 读操作 |
| 7 | 测试 | 激励 = VAC3 3→5 V 斜坡；monitor = `V(DTEST0)`；判据 = 4.4 V/0.35 V；定点补证：判定容差 |
| 8 | 下电 | ① `vset[vac3,0,1e-3,0]` → ② VBAT 源释放 → ③ `vbat` 归零 → ④ 释放 monitor |
| 9 | Log | `Rise[site]`、`Fall[site]`、`Hys[site]`；per-site；fail = 越 4.4 V/0.35 V（容差定点补证） |
## 14. TM133 — `IZTC_1UA`（BG；row 14；`M.functions[12]`；`Y L329`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | ZTC 电流（trim 项）；标称 1；单位 uA（`M.functions[12]`；`Trim=Y`） |
| 2 | Golden依据 | 定点补证：Golden 未提供（`G/TM130_Trim_VBG.md` 可作 trim 机制参考） |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；AMUX → `VAC123_AMUX_ACM`（P L15 / S L64，AMUX 属该通道组）；ATEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | AMUX 通路：`K17`+`K18`+`K20`（IR `pins[AMUX_F_S1].requiredRelays=[17,18,20,86,137,141,142,143,144,145,146,154]`，用途：AMUX 引脚接入）；定点补证：ATEST0 引脚绑定 |
| 5 | 上电 | ① `vbat=5`（ramp 100e-6）→ ② `amux=1`（ramp 100e-6）→ ③ `en_tm[]` → ④ 写字段 `WAKE_UP=1,EN_ATEST0=1,ATEST0_MUX=8` → ⑤ `delay[1e-3]` |
| 6 | 寄存器 | 写：`WAKE_UP=1`、`EN_ATEST0=1`、`ATEST0_MUX=8`；无 DFT 读操作 |
| 7 | 测试 | 无激励；monitor = `I(ATEST0)`；公式 `I=I(ATEST0)`；限值 1 uA；定点补证：trim 目标值/步进与判定容差 |
| 8 | 下电 | ① AMUX 源释放 → ② VBAT 源释放 → ③ `vbat` 归零 → ④ 释放 monitor |
| 9 | Log | `IZTC_uA[site]`、`trimCode[site]`；per-site；fail = 越 1 uA（trim 目标定点补证） |
## 15. TM134 — `IPTAT_1UA`（BG；row 15；`M.functions[13]`；`Y L355`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | PTAT 电流；标称 1；单位 uA（`M.functions[13]`） |
| 2 | Golden依据 | 定点补证：Golden 未提供 |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；AMUX → `VAC123_AMUX_ACM`（P L15 / S L64）；ATEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | AMUX 通路：`K17`+`K18`+`K20`（用途：AMUX 引脚接入）；定点补证：ATEST0 引脚绑定 |
| 5 | 上电 | ① `vbat=5`（ramp 100e-6）→ ② `amux=1`（ramp 100e-6）→ ③ `en_tm[]` → ④ 写字段 `WAKE_UP=1,EN_ATEST0=1,ATEST0_MUX=9` → ⑤ `delay[1e-3]` |
| 6 | 寄存器 | 写：`WAKE_UP=1`、`EN_ATEST0=1`、`ATEST0_MUX=9`；无 DFT 读操作 |
| 7 | 测试 | 无激励；monitor = `I(ATEST0)`；公式 `I=I(ATEST0)`；限值 1 uA；定点补证：判定容差 |
| 8 | 下电 | ① AMUX 源释放 → ② VBAT 源释放 → ③ `vbat` 归零 → ④ 释放 monitor |
| 9 | Log | `IPTAT_uA[site]`；per-site；fail = 越 1 uA（容差定点补证） |
## 16. TM135 — `VREF_1P0`（BG；row 16；`M.functions[14]`；`Y L381`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | 1.0 V 基准电压（trim 项）；标称 1；单位 V（`M.functions[14]`；`Trim=Y`） |
| 2 | Golden依据 | 定点补证：Golden 未提供（`G/TM130_Trim_VBG.md` 可作 trim 机制参考） |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；ATEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | 定点补证：TM135 引脚绑定（IR `pinsPerTm` = UNKNOWN） |
| 5 | 上电 | ① `vbat=5`（ramp 100e-6）→ ② `en_tm[]` → ③ 写字段 `WAKE_UP=1,EN_ATEST0=1,ATEST0_MUX=10` → ④ `delay[1e-3]` |
| 6 | 寄存器 | 写：`WAKE_UP=1`、`EN_ATEST0=1`、`ATEST0_MUX=10`；无 DFT 读操作 |
| 7 | 测试 | 无激励；monitor = `V(ATEST0)`；公式 `VREF=V(ATEST0)`；限值 1 V；定点补证：trim 目标/步进与判定容差 |
| 8 | 下电 | ① VBAT 源释放 → ② `vbat` 归零 → ③ 释放 monitor |
| 9 | Log | `VREF_V[site]`、`trimCode[site]`；per-site；fail = 越 1 V（容差定点补证） |
## 17. TM422 — `VBAT_FB`（MNT；row 17；`M.functions[15]`；`Y L407`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | VBAT 分压反馈；标称 `VBAT*2/5`；单位 V（`M.functions[15]`；`Trim=Y`） |
| 2 | Golden依据 | 定点补证：Golden 未提供 |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；ATEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | 定点补证：TM422 引脚绑定 |
| 5 | 上电 | ① `vbat=4`（ramp 100e-6）→ ② `en_tm[]` → ③ 写字段 `WAKE_UP=1,EN_ATEST0=1,ATEST0_MUX=23` → ④ `delay[1e-3]` → ⑤ `vset[vbat,5,100e-6,0]`（第二段，顺序见 `code3Raw`） |
| 6 | 寄存器 | 写：`WAKE_UP=1`、`EN_ATEST0=1`、`ATEST0_MUX=23`；无 DFT 读操作 |
| 7 | 测试 | 激励 = VBAT 4→5 V；monitor = `V(ATEST0)`；公式 `V_FB=V(ATEST0)`，判据 `VBAT×2/5`；定点补证：以 4 V 还是 5 V 为测量点 |
| 8 | 下电 | ① VBAT 源释放 → ② `vbat` 归零 → ③ 释放 monitor |
| 9 | Log | `VFB_V[site]`、`VBAT_V[site]`；per-site；fail = 偏离 `VBAT×2/5`（容差定点补证） |
## 18. TM424 — `VREF_TRIM`（MNT；row 18；`M.functions[16]`；`Y L433`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | trim 基准电压；标称 1.68；单位 V（`M.functions[16]`；`Trim=Y`） |
| 2 | Golden依据 | 定点补证：Golden 未提供 |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；ATEST0 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | 定点补证：TM424 引脚绑定 |
| 5 | 上电 | ① `vbat=4.4`（ramp 100e-6）→ ② `en_tm[]` → ③ 写字段 `WAKE_UP=1,EN_ATEST0=1,ATEST0_MUX=19` → ④ `delay[2e-3]` |
| 6 | 寄存器 | 写：`WAKE_UP=1`、`EN_ATEST0=1`、`ATEST0_MUX=19`；无 DFT 读操作 |
| 7 | 测试 | 无激励；monitor = `V(ATEST0)`；公式 `V=V(ATEST0)`；限值 1.68 V；定点补证：trim 目标/步进与判定容差 |
| 8 | 下电 | ① VBAT 源释放 → ② `vbat` 归零 → ③ 释放 monitor |
| 9 | Log | `VREF_TRIM_V[site]`、`trimCode[site]`；per-site；fail = 越 1.68 V（容差定点补证） |
## 19. TM425 — `VREF_1P2V_BUF`（MNT；row 19；`M.functions[17]`；`Y L459`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | 1.2 V 基准 buffer 电压；标称 1.2；单位 V（`M.functions[17]`；`Trim=Y`） |
| 2 | Golden依据 | 定点补证：Golden 未提供 |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；ATEST1 → 定点补证：未找到已定义源表 |
| 4 | CBIT闭合 | 定点补证：TM425 引脚绑定 |
| 5 | 上电 | ① `vbat=4.4`（ramp 100e-6）→ ② `en_tm[]` → ③ 写字段 `WAKE_UP=1,EN_ATEST1=1,ATEST1_MUX=2,DIS_NTC_DETECTION_ANALOG=1` → ④ `delay[2e-3]` |
| 6 | 寄存器 | 写：`WAKE_UP=1`、`EN_ATEST1=1`、`ATEST1_MUX=2`、`DIS_NTC_DETECTION_ANALOG=1`；无 DFT 读操作 |
| 7 | 测试 | 无激励；monitor = `V(ATEST1)`；公式 `V=V(ATEST1)`；限值 1.2 V；定点补证：判定容差与位互斥 |
| 8 | 下电 | ① VBAT 源释放 → ② `vbat` 归零 → ③ 释放 monitor |
| 9 | Log | `VREF_BUF_V[site]`；per-site；fail = 越 1.2 V（容差定点补证） |
## 20. TM600 — `HS_RDSON`（BUBO；row 20；`M.functions[18]`；`Y L485`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | 目标 = `HS_RDSON`（`M.functions[18].name`），DFT 原文 `Rds,on=(PMID-SW)/ISW`（`M.functions[18].notes`）；标称 11；单位 mΩ（`M.functions[18].expectValue/unit`） |
| 2 | Golden依据 | `G/tm600-normal-highcurrent.md`（整篇）+ `G/tm600-normal-highcurrent.cpp`（整篇）+ `G/Rdson.md`（整篇） |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；BST → `SW12_U1REF_BST_ACM`（P L20 / S L69）；PMID → `PMID_HG2_FXVI`（P L8 / S L57）；VDRV → `V1P5_U34PS_FXVI`（P L13 / S L62；定点补证：VDRV 是否短接至 V1P5 未在当前证据中找到）；PMID-SW（FPVI）→ `FPVI0`（P L39 / S L88）；monitor PMID-SW/ISW → 同 `FPVI0` 的 F/S 端子 |
| 4 | CBIT闭合 | `K83`（用途：PMID BUS 接入）；`K60`+`K61`（用途：SW BUS 接入，IR `pins[SW_F_S1]=[60,61,133,134,142]`）；`K48`+`K76`（用途：BST 接入，IR `pins[BST_F_S1]` 含 48/76、`sch:672-674`）；定点补证：BST 节点多源汇聚的使能选择 |
| 5 | 上电 | ① `VBAT=3.5`（ramp 100e-6）→ ② `BST=5`（`SW12_U1REF_BST_ACM` FV 5）→ ③ `PMID=5`（100e-6）→ ④ `VDRV=5`（100e-6）→ ⑤ PMID-SW 的 `FPVI0=0 V` 短路（FV 0）→ ⑥ `BST=10`（`SW12_U1REF_BST_ACM` FV 10）；依据：`knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp:46-53`（台阶1 BST=5 V/PMID=0 V → 台阶2 BST=10 V/PMID=5 V，注释记 BST−SW 目标与 BST 领先 PMID 5 V） → ⑦ 配置寄存器 → ⑧ 测量（`delay[1e-3]` → 加流 `iset[sw,1,1e-3,0]` → `delay[2e-3]`） |
| 6 | 寄存器 | 写：`WAKE_UP=1`、`D2A_BUBO_EN_FORCE_ON=1`、`D2A_BUBO_TM_DIS_CLK=1`、`D2A_BUBO_TM_HSON=1`（`en_tm[]` 在前）；无 DFT 读操作 |
| 7 | 测试 | 激励 = `iset[sw,1,1e-3,0]`（1 A，ramp 1e-3）；monitor = PMID-SW 差压 + ISW；公式 `R=V(PMID-SW)/I_SW×1000`（mΩ）；限值 11 mΩ；定点补证：判定容差与采样参数 |
| 8 | 下电 | ① 撤流（`iset` 归零）→ ② `BST 10→5→0` → ③ `PMID` 归零 → ④ `VDRV` 归零 → ⑤ `VBAT` 归零 → ⑥ 释放 `FPVI0` 与 BST/PMID/DVRV 源；定点补证：放电机制 |
| 9 | Log | `hs_rdson[site]`、`v_meas[site]`(V, PMID-SW)、`i_meas[site]`(A, ISW)、`bst_sw_v[site]`(V)；per-site；fail = 越 11 mΩ（容差定点补证） |
## 21. TM601 — `LS_RDSON`（BUBO；row 21；`M.functions[19]`；`Y L511`）

| # | 项目 | 动作 / 资源 |
| --- | --- | --- |
| 1 | DFT目标与判据 | LS FET 导通电阻；标称 7.5；单位 mΩ（`M.functions[19].expectValue/unit`；`notes=Rds,on=(SW-PGND)/IPMID2SW`） |
| 2 | Golden依据 | 定点补证：Golden 未提供（`G/Rdson.md`、`G/LS_ZCD.md` 可作机制参考，未逐行核对） |
| 3 | 源表/通路 | VBAT → `VBAT_PD3_FXVI`（P L12 / S L61）；VDRV → `V1P5_U34PS_FXVI`（P L13 / S L62）；VBUS → `VBUS_DRVH1_ACM`（P L25 / S L74）；BST → `SW12_U1REF_BST_ACM`（P L20 / S L69）；SW-PGND（FPVI）→ `FPVI0`（P L39 / S L88）；monitor SW-PGND/I(PMID_SW) → 同 `FPVI0` 的 F/S 端子 |
| 4 | CBIT闭合 | `K60`+`K61`（用途：SW BUS 接入）；`K154`+`K155`（用途：PGND BUS 接入，IR `pins[PGND_F_S1]=[86,137,141,143,144,154,155]`）；若采纳 BST 供电：`K48`+`K76`；定点补证：BST 是否必须驱动、由哪一路源驱动 |
| 5 | 上电 | ① `VBAT=3.5`（ramp 100e-6）→ ② `VDRV=5`（100e-6）→ ③ `VBUS=5`（100e-6）→ ④ `BST=5`（100e-6；是否施加见定点补证）→ ⑤ `en_tm[]` → ⑥ 写字段 `WAKE_UP=1,D2A_BUBO_EN_FORCE_ON=1,D2A_BUBO_TM_DIS_CLK=1,D2A_BUBO_TM_LSON=1` → ⑦ `delay[5e-3]` → ⑧ 加流 `iset[pmid_sw,1,1e-3,0]` → ⑨ `delay[2e-3]` |
| 6 | 寄存器 | 写：`WAKE_UP=1`、`D2A_BUBO_EN_FORCE_ON=1`、`D2A_BUBO_TM_DIS_CLK=1`、`D2A_BUBO_TM_LSON=1`；无 DFT 读操作 |
| 7 | 测试 | 激励 = `iset[pmid_sw,1,1e-3,0]`（1 A，ramp 1e-3）；monitor = SW-PGND 差压 + I(PMID_SW)；公式 `R=V(SW-PGND)/I×1000`（mΩ）；限值 7.5 mΩ；定点补证：判定容差、采样参数、激励端点绑定 |
| 8 | 下电 | ① 撤流 → ② `BST` 归零（若已施加）→ ③ `VBUS` 归零 → ④ `VDRV` 归零 → ⑤ `VBAT` 归零 → ⑥ 释放 `FPVI0` 与各源；定点补证：放电机制 |
| 9 | Log | `ls_rdson[site]`、`v_meas[site]`(V, SW-PGND)、`i_meas[site]`(A, PMID_SW)；per-site；fail = 越 7.5 mΩ（容差定点补证） |
