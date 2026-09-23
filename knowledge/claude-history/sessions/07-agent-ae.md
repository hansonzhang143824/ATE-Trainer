# 会话 #7 — 你在探索 D:\\Newtest\\CLAUDE_PROCESS 项目，目标是搞清楚**现有 python 脚本的写法模式、TestItemMeta JSON 的数

- 文件：`agent-ae56468dece4444b1.jsonl`（项目 subagents）
- 时间：2026-08-09T10:34:07.357Z → 2026-08-09T10:36:00.830Z，大小 0.4 MB
- 用户消息 1 条 / 助手文本 16 段 / 工具调用标记 42 行

---

## 对话正文（工具输出已剥离）

### 2026-08-09 10:34:07 [user]

你在探索 D:\Newtest\CLAUDE_PROCESS 项目，目标是搞清楚**现有 python 脚本的写法模式、TestItemMeta JSON 的数据结构、以及实际生成的电源代码样例**，为新增一个"上电/下电代码生成脚本"做准备。

请调研以下内容并汇报：

1. **现有生成器脚本的写法模式**：
   - 读取 `D:\Newtest\CLAUDE_PROCESS\gen_tm206_425.py`（54KB，较大，重点看开头50行和函数结构）：它如何组织"构建器+占位符"、如何读 DFT/生成代码、输出到哪里
   - 读取 `D:\Newtest\CLAUDE_PROCESS\verify_relay_trace.py`（7KB）：verify 脚本的断言模式、如何解析 AI.cpp 的 #define 和 cbite.SetOn、如何报告 PASS/FAIL
   - 读取 `D:\Newtest\CLAUDE_PROCESS\verify_merge_rules.py`（5KB）：verify 脚本的入口/main 结构、返回值约定

2. **TestItemMeta JSON 的实际样例**：
   - 搜索项目中是否有 `TestItemMeta` 的 JSON 样例文件（*.json 或文档中的示例），提取完整的 JSON schema（字段：functionName/testType/params/hardwareInit/softwareInit/pinsInvolved/resourcesInvolved/floatingPairs/activeFetPairs/voltageInference）
   - 特别确认 `hardwareInit[]` 的字段格式（cmd/pin/value/time/ignore）和 `floatingPairs[]` 格式（type/pinA/pinB/deltaV/fullNotation）

3. **实际电源代码样例**：
   - 在 `D:\Newtest\CLAUDE_PROCESS\DALI\AI.cpp` 中找 2-3 个有代表性的函数（一个普通 vset 上电、一个 iset[AxB] 浮动源、一个大电流），提取它们的完整上电代码块和下电代码块（从注释 `// ====== Step 2: 上电 ======` 到 `// ====== Step 3` 之间，以及下电部分），作为脚本输出格式的参照
   - 记录真实的源表对象名（如 VBAT_ACM、FPVI、SW_ACM 等）和 Set()/MeasureVI()/SetClamp() 的调用格式

4. **资源分配表.csv 的格式**（如果存在）：
   - 搜索 `.csv` 文件，找到资源分配表，确认列结构（Pin→Resource→继电器 映射的列名）
   - 如果找不到，说明文件可能在其他位置（如 D:\Newtest\ 下其他目录），尽力搜索

输出要求（用中文）：每个发现给出文件路径 + 关键代码片段/字段摘录，最后总结出"新脚本应该长什么样"的建议（输入什么、输出什么、参照哪个现有脚本的骨架）。不要修改任何文件。

### 2026-08-09 10:34:10 [assistant]

I'll explore the project systematically. Let me start by examining the directory structure and reading the key files in parallel.
- [tool] Bash
- [tool] Glob
- [tool] Glob
- [tool] Glob

### 2026-08-09 10:34:18 [assistant]

The user's task is a read-only research request. Let me continue exploring. I'll read the key generator/verify scripts and search for TestItemMeta JSON examples in parallel.
- [tool] Read
- [tool] Read
- [tool] Read
- [tool] Grep
- [tool] Read

### 2026-08-09 10:34:21 [assistant]

Good progress. Now let me dig into the generator script structure, TestItemMeta examples, and AI.cpp power code patterns in parallel.
- [tool] Grep
- [tool] Grep
- [tool] Grep

### 2026-08-09 10:34:26 [assistant]

Now let me look at the TestItemMeta JSON examples in the agent files and skills, plus the generator builder functions.
- [tool] Grep
- [tool] Grep
- [tool] Grep

### 2026-08-09 10:34:31 [assistant]

Let me read the full power-on/power-off agent files and find complete TestItemMeta JSON examples.
- [tool] Read
- [tool] Read
- [tool] Grep

### 2026-08-09 10:34:34 [assistant]

Let me read the dual-parse-agent (TestItemMeta JSON schema) and the generator's builder functions.
- [tool] Read
- [tool] Read

### 2026-08-09 10:34:37 [assistant]

Let me look at the template string definitions and output-writing section of the generator, plus locate representative AI.cpp functions.
- [tool] Grep
- [tool] Read

### 2026-08-09 10:34:40 [assistant]

Let me read the ATEST0_MV template skeleton and find representative power functions in AI.cpp.
- [tool] Read
- [tool] Grep

### 2026-08-09 10:34:45 [assistant]

Let me search for FPVI/SetClamp/floating-source examples across the whole project and read representative power functions in AI.cpp.
- [tool] Grep
- [tool] Read

### 2026-08-09 10:34:48 [assistant]

Let me read the FPVI floating-source large current example (TM600 in test.cpp) and the VCC load case in AI.cpp.
- [tool] Read
- [tool] Read

### 2026-08-09 10:34:52 [assistant]

Let me examine the DFT.csv format, source table object declarations, and the relay.h defines.
- [tool] Read
- [tool] Read
- [tool] Grep

### 2026-08-09 10:34:56 [assistant]

Let me read the simpler `mnt_vbat` builder and check the reg_config directory and recent daylog for context on the planned power script.
- [tool] Read
- [tool] Bash
- [tool] Grep

### 2026-08-09 10:35:02 [assistant]

Let me check the recent daylog, the verify_tm206_425.py model, and the knowledge directory structure.
- [tool] Read
- [tool] Read
- [tool] Bash

### 2026-08-09 10:35:10 [assistant]

Let me read the key knowledge files for source tables and resource mapping that the new script would rely on.
- [tool] Read
- [tool] Read
- [tool] Read

### 2026-08-09 10:35:13 [assistant]

Let me confirm the #define Kxx entries are in AI.cpp itself (as verify_relay_trace expects) and check the units/step standards.
- [tool] Grep
- [tool] Grep

### 2026-08-09 10:36:00 [assistant]

调研完成。以下是完整汇报。

---

# 调研汇报：D:\Newtest\CLAUDE_PROCESS 现有模式 + TestItemMeta + 电源代码样例

## 一、现有生成器脚本的写法模式

### 1. `gen_tm206_425.py`（54KB）— 构建器 + 占位符 + 末尾追加

**核心模式**：`AI = 目标文件路径` + `blocks = []` + 若干"模板字符串 + 构建器函数"，最后读全文、`'\n'.join(blocks)` 追加到文件末尾。

- 路径常量（`gen_tm206_425.py:7`）：`AI = r'D:\Newtest\CLAUDE_PROCESS\DALI\AI.cpp'`
- 手写块用 `HAND = r'''...'''` 原始字符串直接 `blocks.append(HAND)`（TM206/207 等已手写块）
- 构建器模式（`gen_tm206_425.py:489`，`mnt_vbat`）：

```python
def mnt_vbat(tm, name, pname, desc, exp, i2c, field):
    return (MNT_VBAT
            .replace('@TM@', tm).replace('@NAME@', name).replace('@PNAME@', pname)
            .replace('@FUNC@', f'{tm}_{name}').replace('@NUM@', tm[2:])
            .replace('@DESC@', desc).replace('@EXP@', exp)
            .replace('@I2C@', i2c).replace('@FIELD@', field))
```

- 模板串里用 `@TM@`、`@PNAME@`、`@SRCSET@`、`@PWOFF2@`、`@PWOFF3@`、`@CONN2@`、`@KREL@`、`@NOTE@` 等占位符；每个函数调用 `blocks.append(builder(...))`
- 输出方式（`gen_tm206_425.py:1191-1198`）——**读全文件 + 末尾追加**：

```python
with io.open(AI, 'r', encoding='utf-8') as f:
    orig = f.read()
new_section = '\n'.join(blocks)
with io.open(AI, 'w', encoding='utf-8', newline='') as f:
    f.write(orig + new_section)
print(f'Appended {len(blocks)} func blocks. Total new chars: {len(new_section)}')
```

- 模板函数骨架（`ATEST0_MV`，`gen_tm206_425.py:951-1004`）是标准的 6 段结构：`Step 1 Connect(cbite.SetOn)` → `Step 2 Power On` → `Step 3 Register Config(entertestmode)` → `Step 4 Measure` → `Step 5 Power Off(三步下电)` → `Step 6 LogData(SetTestResult)`
- 注释里用 `// vset[vbat,4,100e-6,0] → VBAT=4V` 反推 DFT 指令，作为生成依据；`依据: reg_config/tm@NUM@.sv`（reg_config 目录确实存在，见 `/d/Newtest/CLAUDE_PROCESS/DALI/reg_config/`，有 `boost_300.sv`、`buck_200.sv` 等）

### 2. `verify_relay_trace.py`（7KB）— verify 脚本断言模式

- 通用读取函数 `read_enc(path)`：`utf-8-sig → utf-8 → gbk → latin-1` 逐级回退解码（DLP 透明加密环境），**新脚本必须复用这个**（`verify_relay_trace.py:16-25`）
- 解析 `#define`（`verify_relay_trace.py:28-33`）：

```python
def parse_defines(src):
    d = {}
    for m in re.finditer(r'#define\s+(K\d+_\w+)\s+(\d+)', src):
        d[m.group(1)] = int(m.group(2))
    return d
```

- 解析 `cbite.SetOn(...)`（`verify_relay_trace.py:36-42`）：正则 `cbite\.SetOn\(([^)]*)\)`，split 逗号，排除 `-1`
- 按函数切块（`verify_relay_trace.py:54-62`）：`DUT_API int (TM\d+_\w+)\(short funcindex` 定位起点，下一个 `DUT_API int TM` 为终点
- **PASS/FAIL 约定**（`verify_relay_trace.py:191-199`）：

```python
if errors:
    print('*** FAIL ***')
    for e in errors:
        print('  -', e)
    sys.exit(1)
if warns and warn_as_err:
    print('*** FAIL (warn-as-error) ***')
    sys.exit(1)
print('RELAY TRACE PASSED')   # 成功 = exit 0
```

- 支持 `--warn-as-error` 参数（`sys.argv` 判断，非 argparse）

### 3. `verify_merge_rules.py`（5KB）— 入口/main 结构

- 纯 `main()` + `if __name__ == '__main__': main()`，无 argparse，`sys.argv` 判 `--strict`
- 同样 `read_enc()` + `sys.stdout.reconfigure(encoding='utf-8', errors='replace')`（`verify_merge_rules.py:82-84`）
- 错误累积 `errors/warns` 两个 list，先 print WARNINGS 再 print `*** FAIL ***` + `sys.exit(1)`，成功 print `MERGE DISCIPLINE PASSED`
- 结果汇总行带 `[前缀]` 打印，如 `[rules] merge_rules.md 生效规则: ...`（`verify_merge_rules.py:91`）

---

## 二、TestItemMeta JSON 数据结构

### 完整 schema（`D:\Newtest\CLAUDE_PROCESS\.claude\agents\dual-parse-agent.md:34-57`）

```json
{
  "functionName": "TM600_RDSON_TEST",
  "testType": "normal",
  "params": [
    { "shortName": "HS_RDSON", "check": "MI", "checkPin": "SW", "trim": "N" }
  ],
  "hardwareInit": [
    { "cmd": "vset", "pin": "vbat", "value": 4.2, "time": "100e-6", "ignore": 0 }
  ],
  "softwareInit": "I2CWriteSameData(DEV_ADDR, 0x07, 0x00);",
  "dynamic": [],
  "pinsInvolved": ["VBAT", "PMID", "SW", "BST"],
  "resourcesInvolved": ["VBAT_ACM", "PMID_FOVI", "SW_ACM", "BTST_ACM", "FPVI"],
  "floatingPairs": [],
  "activeFetPairs": [
    { "id": "C1", "pair": ["PMID", "SW"], "type": "HS", "condition": "0x59_bit0=1" }
  ],
  "voltageInference": {
    "preFetOn": { "PMID": 15, "SW": 0, "BST": 20 },
    "postFetOn": { "PMID": 15, "SW": 15, "BST": 20, "BST_SW": "5V" }
  }
}
```

### `hardwareInit[]` 字段格式（`dual-parse-agent.md:88-93`）

从 DFT `Hardware_initial` 列逐条解析：

```
vset[vbat,4.2,100e-6,0]  → {"cmd":"vset","pin":"vbat","value":4.2,"time":"100e-6","ignore":0}
vset[pmid2sw,5,100e-6,0] → {"cmd":"vset","pin":"pmid2sw","value":5,...}
iset[pmid2sw,1,100e-6,0] → {"cmd":"iset","pin":"pmid2sw","value":1,...}
```

- 字段：`cmd`(vset/iset)、`pin`(小写)、`value`、`time`(字符串如 "100e-6")、`ignore`(0/1)
- pin 含 `"2"` 即跨 Pin 浮动源（`pmid2sw` → PMID、SW）

### `floatingPairs[]` 格式（`dual-parse-agent.md:113-115`）

```json
{ "type": "vset", "pinA": "PMID", "pinB": "SW", "deltaV": 5, "fullNotation": "pmid2sw" }
```

- 判定：含 `"2"` = 浮动源；`type` 为 `vset`（浮动电压源）或 `iset`（浮动电流源/大电流）
- 跨 Pin 操作时 `resourcesInvolved` 必须追加 `"FPVI"`（铁律）

### 消费方（`power-on-agent.md` / `power-off-agent.md`）

- `power-on-agent` 输入 `hardwareInit[] + floatingPairs[] + params[].check + 资源分配表.csv`，输出**上电代码块 + PowerState JSON**（`power-on-agent.md:26-37`），PowerState 必须含 4 字段：`sources[]`、`floatingPairs[]`、`upSequence[]`、`finalVoltages{}`
- `power-off-agent` 消费 PowerState → 下电代码（`power-off-agent.md`）
- 生成框架模板（`nuvolta-codegen.md:173-202`）：Step 1 继电器 → Step 2 上电 → Step 3 寄存器 → Step 4 测量 → Step 5 下电 → Step 6 LogData，与 gen_tm206_425.py 的模板一致

---

## 三、实际电源代码样例（AI.cpp / test.cpp）

### 样例 A — 普通 vset 上电 + 三步下电（`D:\Newtest\CLAUDE_PROCESS\DALI\AI.cpp:203-234`，TM001 IIN_SUSPEND）

```cpp
// ====== Step 2: Power On ======
// vset[vbat,3.7,100e-6,0] → VBAT=3.7V FV
// 电压量程 10V (≥2×3.7=7.4V), 电流量程 10MA (≥2×1.118mA)
VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_ON);
delay_ms(1);
...
// ====== Step 5: Power Off ======
VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_ON);
delay_ms(1);
VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
```

下电三步规则：① 全部源 `Set(FV, 0, 原量程, 原量程, RELAY_ON)` → ② `delay_ms(1)` → ③ 统一 `10V/10MA, RELAY_OFF`。

### 样例 B — 多源 vset + iset[VCC] 拉载（`AI.cpp:1375-1410`，TM114 VCC_VBUS_PATH_ACC）

```cpp
// ====== Step 2: Power On ======
VBUS_DRVH1_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
VBAT_PD3_FXVI.Set(FV, 3.7, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
VAC123_AMUX_ACM.Set(FV, 5.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
delay_ms(1);
...
// ====== Step 4: Measure (VCC 带载 50mA, MV) ======
// iset[vcc,0.05,1e-3,0] → VCC 源 FI=50mA 拉载, 测 V(VCC)
VCC_VMCU_FXVI.Set(FI, 0.05, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
delay_ms(1);
VCC_VMCU_FXVI.MeasureVI(50, 5);

// ====== Step 5: Power Off (三步下电) ======
VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
delay_ms(1);
// RELAY_OFF: 统一 10V/10MA
VCC_VMCU_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
VBUS_DRVH1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);
VAC123_AMUX_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
```

### 样例 C — FPVI 浮动源 + 大电流（iset[pmid2sw,1A]）（`D:\Newtest\CLAUDE_PROCESS\test.cpp:958-1042`，TM600_RDSON_TEST）

上电（台阶式 ramp + FPVI 等电位）：

```cpp
// ====== Step 2: Power On (台阶式 ramp) ======
VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
// FPVI FV=0 先稳住 SW=0V
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
delay_us(200);
// PMID 和 BST 台阶式 ramp, 每步 |ΔV|≤5V + delay_us(200)
BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
delay_us(200);
BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
delay_us(200);
PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
delay_us(200);
// ... 台阶2 (10V/5V) → 台阶3 (15V/10V) → 台阶4 (20V/15V)
```

大电流加载（FV=0→FI=0→SetClamp→FI=目标，`test.cpp:1006-1015`）：

```cpp
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);
FPVI.SetClamp(25, 25);
FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);   // 加载 1A
delay_us(2000);
FPVI.MeasureVI(200, 5);
FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVI_RELAY_ON);   // 立即关断!
```

下电（反转 upSequence，台阶降，FPVI 最后 OFF，`test.cpp:1022-1042`）：

```cpp
// ====== Step 5: Power Off (台阶式下电) ======
BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
delay_us(200);
VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
PMID_FOVI.Set(FV, 10, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
delay_us(200);
PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
delay_us(200);
VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
delay_ms(1);
// RELAY_OFF: 统一量程 10V/10MA, FPVI 最后 OFF
VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVI_RELAY_OFF);
```

### 真实源表对象名（两套并存）

- **AI.cpp 现行（DALI netlist 命名，带源表类型后缀）**：`VBAT_PD3_FXVI`、`VAC123_AMUX_ACM`、`VCC_VMCU_FXVI`、`VBUS_DRVH1_ACM`、`VDM_SDA_ACM`、`AMUX_PGND_FXVI`、`QTMU_GP`、`FPVI`
- **test.cpp 旧命名（pin-resource-map.md 速查）**：`VBAT_ACM`、`SW_ACM`、`BTST_ACM`、`VDRV_AMP_ACM`、`PMID_FOVI`、`VAC123_ACM`、`FPVI`、`FPVI_PC`

### 调用格式总结

| API | 格式 | 例 |
|---|---|---|
| `.Set` | `<Res>.Set(FV\|FI, value, vRange, iRange, *_RELAY_ON/OFF)` | `VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON)` |
| `.MeasureVI` | `<Res>.MeasureVI(sample, discard)` | `MeasureVI(50, 5)` / `MeasureVI(200, 5)` |
| `.GetMeasResult` | `<Res>.GetMeasResult(site, MIRET\|MVRET)` | `GetMeasResult(site, MIRET)` |
| `.SetClamp` | `FPVI.SetClamp(vClamp, iClamp)` | `FPVI.SetClamp(25, 25)` |
| 继电器 | `cbite.SetOn(K..., -1)` | `cbite.SetOn(K21_VAC_Cap, -1)` |
| 量程常量 | ACM200: `ACM200_3p6V/10V/40V`, `ACM200_1UA~200MA`；FXVIe_PLUS: `FXVIe_PLUS_10V`, `FXVIe_PLUS_100UA/100MA/10MA`；FPVIe: `FPVIe_1V~100V`, `FPVIe_10UA~10A` | 量程 ≥ 2×设定值 |

---

## 四、资源分配表.csv 格式（存在）

文件：`D:\Newtest\CLAUDE_PROCESS\资源分配表.csv`

**列结构**（10 列，表头在首行）：

```
Unnamed: 0, Pin Name, Resource Name, Connect Relay to Resource, Relay to FPVI_BUS, P2P Relay, Type, Cap1, Cap2, PULL_UP RESISTOR, Prority
```

**行样例**（`资源分配表.csv:15-16`）：

```
15,VBAT,VBAT_ACM,Default,K29_BUSL_VBAT,,ACM200,"10nF, DC","Cap_4.7uF, K30_VBAT_Cap, R_1K",,1
16,VAC1,VAC123_ACM,Default,K34_BUSL_VAC,K50_VAC1_P2P-AGND,ACM200,"10nF, DC","Cap_4.7uF, K37_VAC_Cap, R_1K",,1
```

要点：
- `Resource Name` 是源表对象名（`VBAT_ACM`），`Connect Relay to Resource` = 通路继电器（`K29_BUSL_VBAT`），`Relay to FPVI_BUS` = 浮动源跨 Pin 用 BUS 继电器，`P2P Relay` = PIN 到地短路继电器，`Type` = 源表类型（ACM200/FOVI/QVM/FPVI/DCM），`Cap1/Cap2` = 稳压电容配置（Cap2 含继电器名，如 `K30_VBAT_Cap`），`PULL_UP RESISTOR` = 开漏上拉（如 `K56_NTC_PU, 1K`）
- 每 Pin 可多行（多源表共享，如 AMUX 有 `AMUX_FOVI` + `QVM_GP` + `S24_P2`）
- FPVI 特殊行（`资源分配表.csv:36-40`）：`FPVI_BUS,FPVI,Default,Default,,,FPVI`；以及 `FPVI_PC` 用 Kelvin 继电器 `K9_KELVIN,K10_KELVIN,K11_KELVIN,K12_SHARE,K13_PC`；Special Circuit 行含 QPoint/AMP 电源继电器 `K54_Qpoint` 等
- 另一份 `D:\Newtest\CLAUDE_PROCESS\DFT.csv` 是 DFT 原始表（列：`Item,Function Name,ShortName,ExpectValue,Unit,Trim,Record,Hardware_initial,Software_initial,Dynamic,Check,Type`），`Hardware_initial` 列就是 `vset[vbat,4.2,100e-6,0]` 多行文本

---

## 五、新脚本建议（上电/下电代码生成脚本）

### 输入
1. **TestItemMeta JSON**（可选：A 路径直接读 DFT.csv 的 `Hardware_initial` 列，解析 `vset/iset[pin,value,time,ignore]` → 等价于 `hardwareInit[]`）
2. **资源分配表.csv** — Pin → Resource Name / Type / Cap 继电器映射
3. **floatingPairs[]** — 判定跨 Pin 浮动源（含 `"2"` 或显式 floatingPairs）
4. 目标文件 `D:\Newtest\CLAUDE_PROCESS\DALI\AI.cpp`

### 输出
- `Step 2: 上电` 代码块 + `Step 5: 下电` 代码块（插入函数模板相应占位符），或独立 PowerState JSON

### 逻辑（对齐 power-on/off-agent 三档）
1. **普通 vset**：`.Set(FV, value, vRange, iRange, *_RELAY_ON)` + `delay_ms(1)`；量程 ≥2×设定值（查 acm200.md/fovie.md/fpvie.md 量程表）
2. **浮动电压源 vset[AxB]**：PinB 基准 → `FPVI.Set(FV,0,...)` 等电位 → PinA 台阶升，每步 |ΔV|≤5V + `delay_us(200)`
3. **大电流 iset[AxB] ≥1A**：`FV=0 → FI=0 → SetClamp(25,25) → FI=target`；下电 `FI=0 → FV=0 → RELAY_OFF`，FPVI 永远最后 OFF

下电统一：① 全部源 `Set(FV,0,原量程,RELAY_ON)` → ② `delay_ms(1)` → ③ 统一 `10V/10MA, RELAY_OFF`

### 骨架参照
- **生成**：仿 `gen_tm206_425.py` 的"模板 + 构建器 + blocks.append + 末尾追加"（`.replace()` 占位符 `@POWER_ON@` / `@POWER_OFF@`）；模板参照 `nuvolta-codegen.md:173-202` 的 6 段框架，上电/下电代码填充 Step 2 / Step 5
- **验证**：仿 `verify_relay_trace.py`（读文件 → 正则提取 → 累积 errors/warns → `sys.exit(1)` FAIL / `PASSED`），并复用 `read_enc()`（utf-8-sig→gbk→latin-1）与 `sys.stdout.reconfigure(encoding='utf-8')`
- 额外校验项可参照 `verify_tm206_425.py`：RELAY_OFF 必须 10V/10MA、花括号平衡、FPVI 最后 OFF、每步 |ΔV|≤5V

### 关键数据源提醒
- 源表对象名以 **AI.cpp 现行命名**为准（`VBAT_PD3_FXVI`、`VAC123_AMUX_ACM` 等），不要直接用 pin-resource-map.md 的旧速查名
- 继电器 `#define Kxx` 在 `D:\Newtest\CLAUDE_PROCESS\DALI\AI.cpp` 顶部（13 处），与 `relay.h`（根目录）不一致——verify 脚本以 AI.cpp 内 #define 为准
- 跨 Pin 操作必须追加 `FPVI` 到资源列表；Cap 稳压电容在测 MI 电流时必须断开（功能规则 FR-001，`verify_relay_trace.py:152-158`）
