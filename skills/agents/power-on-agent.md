---
name: power-on-agent
description: 上电配置 — 已脚本化 → gen_power_sequence.py（推理→agent, 固定→脚本）。本文档为脚本规格文档，保留 R-PON 规则清单供脚本覆盖验证，不直接运行推理
model: sonnet
tools: Read, Grep, Bash
---

# 上电 Agent — 电源配置 + 上电序列

> ⚠️ **已脚本化 (2026-08-09)**：上电逻辑为固定模板，已由 `gen_power_sequence.py` 取代。本文档保留为**脚本规格文档**：列出 R-PON 铁律清单 + 脚本输入接口 + agent 残余职责。主 Skill 调用脚本生成 Step 2 上电代码 + PowerState JSON，不再派发本 agent 推理。

## 脚本调用方式（主 Skill 用）

```bash
python gen_power_sequence.py \
  --meta <TestItemMeta.json> \
  --pin-map <pinmap.json> \
  --define Pin_Channel_define.h \
  --mode power-on
```

stdout 输出 `###SECTION:POWER_ON###` 代码块 + `###SECTION:POWER_STATE###` PowerState JSON。主 Skill 将 POWER_ON 块填入 `<%POWER_ON_CODE%>`，将 POWER_STATE 保存传给下电段。

- 完整 CLI 见脚本 `--help`（含 `--current-limit` / `--ramp-profile` 覆盖、`--verify` 对拍、`--audit-rules` 自检）
- 规则→函数覆盖映射表内置在脚本 `RULE_COVERAGE`，用 `--audit-rules` 机器自检

## 输入

- `TestItemMeta.hardwareInit[]`（--meta）
- `TestItemMeta.floatingPairs[]`（--meta）
- `TestItemMeta.mvNoFipins[]`（--meta）
- `--pin-map` pin→object 映射（由 relay-agent 从 SCH-Connect-Map 补齐）
- `--define Pin_Channel_define.h`（extern 类型权威，脚本解析量程前缀）

## 输出

### 1. 上电代码块（POWER_ON SECTION）
```cpp
// ====== Step 2: 上电 ======
// vset[vbat,4.2,100e-6,0] → VBAT=4.2V FV
VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
delay_ms(1);
```

### 2. PowerState JSON（POWER_STATE SECTION）
```json
{
  "sources": [
    { "name": "VBAT_ACM", "mode": "FV", "finalValue": 4.2, "vRange": "ACM200_10V", "iRange": "ACM200_100MA" }
  ],
  "floatingPairs": [],
  "upSequence": [
    { "step": 1, "source": "VBAT_ACM", "mode": "FV", "value": 4.2, "note": "VBAT上电", "delay": 0 }
  ],
  "finalVoltages": { "VBAT": 4.2 }
}
```

## R-PON 规则清单（脚本必须覆盖，agent 曾推理的决策点）

| 规则ID | 内容 | 脚本函数 | 状态 |
|--------|------|---------|:---:|
| R-PON-01 | `vset`→FV / `iset`→FI 模式判定 | mode_for_cmd() | 已覆盖 |
| R-PON-02 | MV 无 FI 配置 → FI=0 + 最小量程 10UA | apply_mv_no_fi() | 已覆盖 |
| R-PON-03 | 浮动源识别（pinA→pinB 成对） | parse_floating_pairs() | 已覆盖 |
| R-PON-04 | 量程 ≥ 2× 设定值，取最小满足档 | select_range() | 已覆盖 |
| R-PON-05 | 量程 ≤ 90% 满量程（防御断言） | select_range() | 已覆盖 |
| R-PON-06 | 普通上电逐条 Set + delay_ms(1) | gen_simple_power_on() | 已覆盖 |
| R-PON-07 | 浮动源三阶段 ≤5V 台阶 | gen_floating_ramp() | 已覆盖 |
| R-PON-08 | 大电流三段式（FV=0→FI=0→Clamp→FI） | gen_high_current_init() | 已覆盖 |
| R-PON-09 | 小电流两段式上电 (按 PIN 类型分类): FV 测量电流<100uA(小量程) → **power PIN**(VAC/ACDRV/VIN/PMID/VBUS/VBAT/VSYS/VCC/VDRV/BST/SW/CFH/CFL/LED)→先 100MA 大量程上电稳定 500us 后切测量量程; **digital PIN**(GPx/KLV/SNSP/SNSN)→先 10MA 上电稳定 500us 后切; **ATEST 类模拟 PIN**(VDM/NTC/AMON)→直接设测量量程, 无两段式; 未知按 power 保守 | pin_category() + gen_two_stage_power_on() + gen_simple_power_on() | 已覆盖 |
| R-FLT | 等电位 / ΔV≤5V / 每步 delay_us(200) | gen_floating_ramp() | 已覆盖 |
| R-RNG | ≥2×、≤90% | select_range() | 已覆盖 |
| R-SRC | extern 类型声明权威（FXVIe_PLUS 双词前缀） | parse_extern_types() | 已覆盖 |
| R-ST | 台阶每步延迟 | gen_floating_ramp() | 已覆盖 |

> 覆盖验证方式：`python gen_power_sequence.py --audit-rules`（PASS 要求 19 规则全部可达）+ `--verify AI.cpp` 真实函数对拍。

## 决策流程（脚本内部实现，本文档仅存档原理）

### Step 1: 确定每个 Pin 的 Resource → 见 `knowledge/hardware/pin-resource-map.md`
查 SCH-Connect-Map / Pin_Channel_define.h，找到 Pin 对应的 Resource Name 和 Type。（**现由 --pin-map 显式传入**，脚本不做 pin→源表查找）

### Step 2: 确定 FV/FI 模式
| DFT指令 | 模式 |
|---------|:---:|
| `vset` | FV |
| `iset` | FI |
| MV测量无FI配置 | FI=0, 量程选最小(10UA) |

### Step 3: 选择量程（≥2×设定值）→ 见 `knowledge/sources/`
按 Resource Type 查对应源表知识库的量程表（table_max = 满量程 50% = 文档"设定值范围"上限）:
- ACM200 → `knowledge/sources/acm200.md`
- FXVIe_PLUS/FOVIe → `knowledge/sources/fovie.md`
- FPVI → `knowledge/sources/fpvie.md`

### Step 4: 生成上电代码
#### 4a. 普通上电（无浮动源）
逐条 hardwareInit 生成 `.Set(FV, value, vRange, iRange, RELAY_ON)`
#### 4b. 浮动电压源上电（有 floatingPairs type=vset）
**核心约束: PinA = PinB + ΔV, |ΔV| ≤ 5V, 每步 200μs**
```
阶段1: PinB 先设基准电压
阶段2: FPVI FV=0 强制等电位 (PinA=PinB)
阶段3: PinA 升至最终值 (PinA-PinB ≤ 5V)
```
#### 4c. 大电流上电（iset[AxB] ≥ 1A）
```cpp
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
FPVI.Set(FI, target, FPVIe_1V, FPVIe_10A, FPVI_RELAY_ON);
FPVI.SetClamp(25, 25);
```

### Step 5: 输出 PowerState JSON
必须包含: `sources[]`, `floatingPairs[]`, `upSequence[]`, `finalVoltages{}`

## 知识库引用
- Pin→Resource: `knowledge/hardware/pin-resource-map.md`
- 源表量程/Set签名: `knowledge/sources/acm200.md`, `fovie.md`, `fpvie.md`
- 台阶规则: `knowledge/standards/units.md`
- 大电流: `knowledge/sources/fpvie.md`

## 铁律
- 浮动源必须台阶上电，不可一步到位
- 每步 PinA-PinB ≤ 5V
- FPVI FV=0 等电位不可省略
- 量程 ≥ 2× 设定值
- PowerState 必须包含所有 4 个字段

## 脚本输入边界（仍需 agent 推理，脚本不做）

| 输入 | 谁生成 | 依据 |
|------|--------|------|
| `--pin-map` pin→object | relay-agent 补 SCH-Connect-Map | SCH-Connect-Map |
| `currentLimit` | dft-parse / params[].check | FV 源 iRange 判断输入 |
| `rampProfile` | voltageInference / activeFetPairs | 浮动 ramp 终点 |
| `mvNoFipins` | dft-parse | MV 无 FI 意图 |
| ≥200mA→FPVIe / ≥1A→三段式 选型 | relay-agent | 资源选型 |
| Step 3~6 框架 | 主 Skill 模板 | — |
