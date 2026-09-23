# 参考材料索引 References Index

> **参数类型索引层**（两层索引之一）：生成代码时按「具体参数类型」查本索引 → 同名联动拿到 chip(是什么)/method(怎么测)/code(长啥样)/debug(怎么排查，按需)。
> 三注册表之一：规则→`rules-registry.md` / 材料→本文件 / 函数→`functions-registry.md`。
> 参数的项目结构类型（7 类，无歧义）判据见 `../standards/test-types.md`；**功能类型索引层**（类型→判据/框架/方法）见 `func_type_index.md`。

---

## 同名联动索引（按参数）

> 四个 L 层文件夹：`L4-Golden-code/`（优秀案例）、`L1-chip/`（芯片 Block 介绍）、`L3-method/`（典型参数测试方法）、`L5-debug/`（调试/排查方法论，**按需**），文件按**参数名**命名、同名联动，**文件夹内部平铺不建子文件夹**。
> 「项目结构类型」列由 `test-types.md` 判定，决定代码框架（普通 / Toggle-AWG / Trim）。

| 参数 | 项目结构类型 | Block 介绍 `L1-chip/` | 典型测试方法 `L3-method/` | 优秀案例 `L4-Golden-code/` | 调试排查 `L5-debug/` |
|------|------------|-------------------|----------------------|-----------------|------------------|
| RDSON | 一般测试项目 | `L1-chip/RDSON.md` | `L3-method/RDSON.md` | `L4-Golden-code/Rdson.cpp` | `L5-debug/RDSON.md` |
| VBG | Trim | _待归档_ | _待归档_ | `L4-Golden-code/TM130_Trim_VBG.cpp` | — |
| BUCK HS Gain | Trim | _待归档_ | _待归档_ | `L4-Golden-code/TM623_Trim_BUCK_HS_Gain.cpp` | — |
| VAC GD present | 一般测试项目 | _待归档_ | _待归档_ | `L4-Golden-code/toggle-template.cpp` | — |
| UVLO | 一般测试项目 | `L1-chip/UVLO.md` | `L3-method/UVLO.md` | `L4-Golden-code/UVLO.cpp` | — |
| Current Threshold | 一般测试项目 | `L1-chip/Current-Threshold.md` | `L3-method/Current-Threshold.md` | `L4-Golden-code/HS_ZCD.cpp` + `L4-Golden-code/LS_ZCD.cpp` | — |
| CurrentSense | Trim | `L1-chip/CurrentSense.md` | `L3-method/CurrentSense.md` | _待归档_ | — |
| VBAT OVP | 一般测试项目 | `L1-chip/UVLO.md` | `L3-method/UVLO.md` | `L4-Golden-code/OVP.cpp` | — |
| PSM_THREHOLD | 阈值 AWG（Toggle） | `L1-chip/UVLO.md` | `L3-method/UVLO.md` | `L4-Golden-code/UVLO.cpp`（rampv_capv 双扫 + Hys） | — |
| VC_OFFSET | 阈值 AWG（Toggle） | `L1-chip/UVLO.md` | `L3-method/UVLO.md` | `L4-Golden-code/UVLO.cpp`（rampv_capv 双扫 + Hys） | — |
| VC_CLAMP_LOW | 一般测试项目（静态 FV-MV） | _待归档_ | _待归档_ | `L4-Golden-code/toggle-template.cpp`（无 ramp 参考框架） | — |
| OTP·MTP | 项目结构类型 #3 Readback / #4 Burn（**必声明 `branch`: OTP / MTP**） | `L1-chip/OTP-MTP.md` | `L3-method/OTP-MTP-Readback-Burn.md` | **三档勿全读**：Tier1=`L1-chip`+`L3-method`（通用方法，必读小件）→ Tier2=分支注解 `OTP_READ_PRE_POST_BURN-案例N.md`（OTP=1~3 / MTP=4~5，必读）→ Tier3=原文 `案例N.txt`（**按需**，只读分支匹配的 1 份；5 份合计 357KB，全读会打爆上下文）。DLP 加密 txt 须用 DSH read 工具读取 | — |
| Diff Pair | 一般测试项目（Toggle 双扫 + Hys）｜**差分电压对**，BST−SW 自举为例 | `L1-chip/UVLO.md` + `L1-chip/01-bootstrap-hs-drive.md` | `L3-method/diff-pair-spec.md` | `L4-Golden-code/TM1205_TRX_BST_UV_GD.cpp` | — |

> **索引优先查找铁律（2026-08-26 用户拍板）**: 生成代码时**先经本索引判定参数类型**（阈值 AWG→UVLO/toggle-template；电流阈值→HS_ZCD/LS_ZCD；静态→无 ramp 普通框架），**只读取匹配的独立 golden 文件**（references/L4-Golden-code/*.cpp，1.3~6.9KB），**禁止从 test.cpp 现翻旧函数当模板**（test.cpp 348KB，全读 ≈ 116K token 常驻上下文）。索引未登记的参数 → 归类到现有类型补一行即可，不新建大文件。

> ⚠ 案例文件**位置/名字/内容不允许变动**（工程源文件），靠本索引建立「参数 → 文件路径」连接，**不物理迁移/重命名**；新案例 copy 进 `L4-Golden-code/` 保持原名；**根目录手交的案例直接剪切(move)进 `L4-Golden-code/`，根目录不留残留**，由索引记录。

## 代码案例（L4-Golden-code/）

> 现有案例按类型归档，`一句话用途` + 关联规则如下；后续并入上方「同名联动索引」。

| 类型 | 案例 | 位置 | 一句话用途 | 关联规则/函数 |
|------|------|------|-----------|--------------|
| RDSON（按参数） | `Rdson.cpp` | `L4-Golden-code/` | **RDSON 官方案例**：台阶上电(BST 领先 PMID 5V) + FPVI 大电流(SetClamp 50,50) + RON=MVRET/MIRET×1e3 | R-VIR、R-PON/R-POFF、FPVIe |
| Current Threshold / ZCD（按参数） | `HS_ZCD` + `LS_ZCD` | `L4-Golden-code/` | **ZCD 过零电流阈值 AWG**：rampi_capv 电流 ramp + SDA_INT toggle 观测，单阈值无迟滞；HS=BOOST / LS=BUCK，均电流>200mA 用 FPVIe 浮动源 + BST 台阶上电。**关键特殊结构（2026-08-26 用户明确）**：① **MOSFET 结构**=被测上管，两端分别连着 **PMID↔SW**，大电流 → **FPVI 短接两端**；② **台阶配对结构 BST−SW**，压差必须始终满足台阶上下电（BST≥SW 且 BST−SW≤5V），自举电容 Cap_SW_BST(K57) 是配对结构一部分 → BOOST 测试闭 K57、不闭 SW1/BST1 对的 K45；③ **测试方法本质=电流阈值**：rampi_capv 电流 ramp + 抓其他 PIN 翻转，**翻转点对应电流值 = ZCD 值**（单阈值无迟滞、无 Hys）；**PIN 是角色实例非名称（2026-08-26 用户再深化）**：PMID↔SW=被测 MOSFET 两端、BST−SW=台阶电压对两端，下一项目可映射 SW1↔VBUS / BST2−CFH2，按角色从本项目权威源解析 | R-PON、rampi_capv、浮动源规则、R-SETON、[[nuvolta-golden-case-usage]] |
| UVLO/PRST（按参数） | `UVLO.cpp` | `L4-Golden-code/` | **PRST 阈值 AWG**：rampv_capv 双扫(TRIG_RISING/FALLING) + VAC1/2/3 三通道 + Hys=(rise−fall)×1e3 | R-HYS、rampv_capv、R-SETON |
| **差分电压对（Diff Pair）** | `TM1205_TRX_BST_UV_GD.cpp` | `L4-Golden-code/` | **两端压差阈值 AWG**（2026-09-13 用户拍板新增）：**浮动源单通道跨两点**（H→一端、L→另一端）→ 捕获值 **直接=压差**；**极性**决定输出正/负域（本案例负域 ⇒ `fabs()` 还原）；自举电容 K_SWx_BSTx 在压差两端 ⇒ **ramp 源 Cap 豁免不闭**；**多对共用同一浮动源 ⇒ 分时复用**（每路独立 `cbite.SetOn`，合并会让两路并联）。角色：两端=被测差分对 / 观测=指示脚(Open-Drain 需上拉) / DMUX_SEL 选路 | `diff-pair-spec.md`、`relay-design-flow.md §五`、FR-001 反向、R-SETON |
| VBAT OVP（按参数） | `OVP.cpp` | `L4-Golden-code/` | **VBAT 过压保护阈值 AWG**：rampv_capv 双扫(TRIG_RISING/FALLING) 测 VBAT OVP 阈值 + Hys=rise−fall，2cell/4cell × CV 4V/4.4V 四档（ramp 源 VAC123_VBATD_ACM、cap 源 NTC2_FOVI） | R-HYS、rampv_capv、R-SETON |
| Toggle/AWG（迟滞） | `toggle-template.cpp` | `L4-Golden-code/` | VAC1/2/3 GD present 检测：rampv_capv 双扫 TRIG_RISING/FALLING + Hys=(rise−fall)×1e3 + entertestmode + I2C 配置 + 三步下电 | R-HYS、rampv_capv、R-PON/R-POFF |
| 大电流 + 浮动源（RDSON） | `tm600-normal-highcurrent.cpp` | `L4-Golden-code/` | **TM600 黄金案例（唯一正确版，已确认）**：Normal + 大电流 + 浮动源最复杂案例 | R-PON、FPVIe、大电流规则 |
| Trim sub 模板 | `sub-measure-template.cpp` | `L4-Golden-code/` | Trim 的 sub.cpp measure 函数模板 | Trim 规则、R-VIR |
| Trim（VBG · 简单） | `TM130_Trim_VBG.cpp` + `TM130_sub_measure.cpp` | `L4-Golden-code/` | **已确认**：电压基准 VBG trim，16 steps，无 FPVI/无浮动源/无 BST = 简单 Trim 标准模板 | Trim 规则 |
| Trim（BUCK 高边增益 · 复杂） | `TM623_Trim_BUCK_HS_Gain.cpp` + `TM623_sub_measure.cpp` | `L4-Golden-code/` | **已确认**：BUCK HS 增益 trim，32 steps，FPVI 3A + 浮动源 + BST 台阶上电 = 复杂 Trim 标准模板 | Trim 规则、FPVIe、大电流规则 |
| OTP Readback/Burn（项目A·三件套全） | `OTP_READ_PRE_POST_BURN-案例1.txt` + `.md` | `L4-Golden-code/` | **OTP 完整三件套**：直读 0xC0-EF；SN 随机生成（`device_sn_assign_random`）；解锁Key/假密钥复烧保护；POST 双检（comp_prog_to_read + 版本校验） | L3 OTP-MTP |
| OTP Readback/Burn（项目B·最小完整） | `OTP_READ_PRE_POST_BURN-案例2.txt` + `.md` | `L4-Golden-code/` | 0xF0-FF 单窗最小参照；BurnKey→0x53（NVM_PROG_ALL）；NU6801/02/03 器件分支；POST comp_prog_to_read | L3 OTP-MTP |
| OTP Readback/Burn（项目C·地址特判） | `OTP_READ_PRE_POST_BURN-案例3.txt` + `.md` | `L4-Golden-code/` | ADDR_CHANGE 特判（0xCE→归零）；`EFUSE_REG_REGISTER_BURN` 专用验证节点；Burn_Check_Pass 参数化；QA/QUAL/TempChar 门控 copy_read_to_prog | L3 OTP-MTP |
| MTP Readback/Burn（无线充项目） | `OTP_READ_PRE_POST_BURN-案例4.txt` + `.md` | `L4-Golden-code/` | **MTP 双函数**：控制器读/写端口（读0x13-16/写0x1C-1F，键 0xA5/0x5A）；CRC-16/XMODEM 闭环（烧前算+读后验）；双 READBACK 经比对功能等价（重复收录） | L3 OTP-MTP |
| MTP PRE（同无线充项目） | `OTP_READ_PRE_POST_BURN-案例5.txt` + `.md` | `L4-Golden-code/` | MTP PRE + **QC 码值变换层**（16bit 补码→Gain=1±code/1e4→全局数组供下游）；无 fresh 判定 | L3 OTP-MTP |
> 过程稿 `TM600_*.cpp`（4 文件）+ `TM601_LS_RDSON.cpp` 已移至 `_archive/` 隔离，**非黄金案例**；正确版 = `L4-Golden-code/tm600-normal-highcurrent.cpp`（TM600 黄金案例）与 `L4-Golden-code/Rdson.cpp`（同函数按参数命名快照）。

## 芯片 Block 介绍（L1-chip/）

| 参数 | 位置 | 一句话用途 |
|------|------|-----------|
| UVLO | `L1-chip/UVLO.md` | 欠压锁定阈值：上下阈值 + HYS，指示 PIN(PG/DTEST) Open-Drain/Push-pull，OVP/PRST/VBAT_LOW 同原理 |
| Current Threshold | `L1-chip/Current-Threshold.md` | 过零电流 ZCD：Vcs=I×Rdson 比 Vref_zcd，BUCK(SW-PGND)/BOOST(PMID-SW)，无迟滞单阈值 |
| CurrentSense | `L1-chip/CurrentSense.md` | 电流检测核心：Gain + Offset/Vos 两参数，Vcs=Rsns×Imirror+Vos，电流镜/电阻分压两结构，下游 ZCD/OCP/Peak/环路/AMUX/Trickle = Vcs+EA |
| RDSON | `L1-chip/RDSON.md` | 导通电阻：RON=VON/ION，功耗 P=I²×RON，毫欧级必须 Kelvin 四线法(Force/Sense 分离)，易受接触/路径/时序/自热干扰 |
| _（待归档）_ | `L1-chip/<参数>.md` | ADC / Freq Related / AMUX / close-loop 等 Block 介绍待你提供，按参数名归档并登记 |

## 典型参数测试方法（L3-method/）

| 参数 | 位置 | 一句话用途 |
|------|------|-----------|
| UVLO | `L3-method/UVLO.md` | 供电 PIN ramp 电压低→高测上阈值、高→低测下阈值，差值 HYS(mV)，rampv_capv |
| Current Threshold | `L3-method/Current-Threshold.md` | PGND-SW / PMID-SW ramp 电流，monitor 翻转点=ZCD 电流，rampi_capv，无迟滞 |
| CurrentSense | `L3-method/CurrentSense.md` | 先 Trim Offset 再 Trim Gain（Offset 0 电流 / Gain 大电流两点做差）；差分电压运放测 Sense 端；闭环(5mV@1A) vs 开环(AWG ramp Comp 翻转) |
| RDSON | `L3-method/RDSON.md` | 15 步稳健流程(先试探后加压) + 测量工具箱(I-V/脉宽/温度扫描) + 短脉冲防自热；RON=V_meas/I_meas(呼应 R-VIR) |
| _（待归档）_ | `L3-method/<参数>.md` | 各参数「一般怎么测」待你提供，按参数名归档并登记 |

## 调试/排查方法论（L5-debug/）

| 参数 | 位置 | 一句话用途 |
|------|------|-----------|
| RDSON | `L5-debug/RDSON.md` | 三类问题 + 7 步排查法(80/15/5) + 六大偏差根源 + 速查判断表 + 短路校验法 + 10 条经验 |
| _（待归档）_ | `L5-debug/<参数>.md` | 各参数「出问题怎么排查」**按需**归档并登记（非必须） |

## 电路设计（circuit/）

| 主题 | 位置 | 一句话用途 |
|------|------|-----------|
| _（待归档）_ | `knowledge/hardware/` 已有 closed-loop-model / bus-topology / test-strategy | 电流检测、闭环、大电流/差分电压选型原理已沉淀在 hardware/，待按电路主题建独立案例 |

---

## 给资料协议（材料模板）

```
【类型】代码案例 / 芯片 Block 介绍 / 典型参数测试方法 / 电路设计 / 手册
【名称】台阶上电
【文件】D:\...\xxx.cpp（或直接贴内容）
【对应】TMxxx / Rdson / UVLO ...
【一句话用途】两段式上电标准写法
【提炼要求】要抽规则 / 只要存档 / 两者
```

## 待确认

- [x] TM600：唯一正确版 = `L4-Golden-code/tm600-normal-highcurrent.cpp`（过程稿已移 `_archive/`）
- [x] TM130 / TM623：已确认为干净的标准 Trim 案例（简单/复杂两档，已入 `L4-Golden-code/`）
- [ ] circuit / chip / method 三类目前为空，等你提供资料后填充
- [x] 案例不物理迁移：靠 index 建立连接，文件位置/名字/内容不变；新案例 copy 进 `L4-Golden-code/` 保持原名（2026-08-16 用户确认）
- [x] OVP.cpp（VBAT_Protection，VBAT 过压保护阈值 AWG）已归档 `L4-Golden-code/` + 登记索引，L1-chip/method 复用 UVLO（同原理）（2026-08-16 用户提供）
- [x] ZCD（Current Threshold）code 案例 `HS_ZCD`(BOOST/PMID-SW) + `LS_ZCD`(BUCK/SW-PGND) 已从根目录剪切进 `L4-Golden-code/` + 登记索引（2026-08-20 用户提供）
- [x] OTP/MTP Readback/Burn 家族：5 案例（3 OTP 项目三件套 + MTP 项目）归档 `L4-Golden-code/OTP_READ_PRE_POST_BURN-案例1~5`（txt 原样 + 同名 md 注解），L1-chip/L3-method 文档建立，func_type_index #3/#4 判据升级为代码级（2026-09-07 用户提供；txt 为 DLP 加密格式，agent 必须用 DSH read 工具读取，Bash/grep 只见密文）

<!-- GOLDEN-LEDGER:BEGIN (由 gen_material_status.py --write-md 生成, 勿手改) -->
### 黄金案例台账（L4-Golden-code 全量 · 总结文档全部登记于此）

> 机读版：`material_status.json` 的 `goldenCases` 段（含哈希，`--check` 判漂移）；**三档定位见 `../standards/context-management.md §6`**；**全部总结文档尚待用户 review**（清单见 `docs/黄金案例-要点总结-review清单.md`）。

| 案例 | 要点总结 | 总结类型 | 归属参数类型 | 同源别名 |
|---|---|---|---|---|
| `HS_ZCD.cpp` | `HS_ZCD.md` | 标准要点总结 | Current Threshold | — |
| `LS_ZCD.cpp` | `LS_ZCD.md` | 标准要点总结 | Current Threshold | — |
| `OTP_READ_PRE_POST_BURN-案例1.txt` | `OTP_READ_PRE_POST_BURN-案例1.md` | 分支注解 | OTP·MTP | — |
| `OTP_READ_PRE_POST_BURN-案例2.txt` | `OTP_READ_PRE_POST_BURN-案例2.md` | 分支注解 | OTP·MTP | — |
| `OTP_READ_PRE_POST_BURN-案例3.txt` | `OTP_READ_PRE_POST_BURN-案例3.md` | 分支注解 | OTP·MTP | — |
| `OTP_READ_PRE_POST_BURN-案例4.txt` | `OTP_READ_PRE_POST_BURN-案例4.md` | 分支注解 | OTP·MTP | — |
| `OTP_READ_PRE_POST_BURN-案例5.txt` | `OTP_READ_PRE_POST_BURN-案例5.md` | 分支注解 | OTP·MTP | — |
| `OVP.cpp` | `OVP.md` | 标准要点总结 | VBAT OVP | — |
| `Rdson.cpp` | `Rdson.md` | 标准要点总结 | RDSON | tm600-normal-highcurrent.cpp |
| `TM1205_TRX_BST_UV_GD.cpp` | `TM1205_TRX_BST_UV_GD.md` | 标准要点总结 | Diff Pair | — |
| `TM130_Trim_VBG.cpp` | `TM130_Trim_VBG.md` | 标准要点总结 | VBG | — |
| `TM130_sub_measure.cpp` | `TM130_sub_measure.md` | 标准要点总结 | VBG | — |
| `TM623_Trim_BUCK_HS_Gain.cpp` | `TM623_Trim_BUCK_HS_Gain.md` | 标准要点总结 | BUCK HS Gain | — |
| `TM623_sub_measure.cpp` | `TM623_sub_measure.md` | 标准要点总结 | BUCK HS Gain | — |
| `UVLO.cpp` | `UVLO.md` | 标准要点总结 | PSM_THREHOLD, UVLO, VC_OFFSET | toggle-template.cpp |
| `sub-measure-template.cpp` | `sub-measure-template.md` | 标准要点总结 | BUCK HS Gain, VBG | — |
| `tm600-normal-highcurrent.cpp` | `tm600-normal-highcurrent.md` | 标准要点总结 | — | Rdson.cpp |
| `toggle-template.cpp` | `toggle-template.md` | 标准要点总结 | VAC GD present, VC_CLAMP_LOW | UVLO.cpp |
<!-- GOLDEN-LEDGER:END -->
