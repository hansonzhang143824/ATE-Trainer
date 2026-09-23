> 迁移自 auto-memory `STS8300-cbite-qtmue.md`（2026-08-16） ｜来源 STS8300 编程手册-2.1.15.pdf, pages 240-297


# CBITe -- Relay Control (Chapter 2)

System supports up to 2 CBITe boards, 256 control bits total.
Not bound via `STSSetMultiSiteBind` -- use `STSCBITeMultiSiteBind` instead.

---

## 2.1 CBITe() -- Constructor

**Signature:**
```cpp
CBITe();
```

**Remarks:**
Defines a CBITe resource. CBITe module does NOT use `STSSetMultiSiteBind` for site binding; use `STSCBITeMultiSiteBind` instead.

**Example:**
```cpp
// 4-site test, each site uses 2 relays K1,K2:
// SITE1: K1=CBite0, K2=CBite1; SITE2: K1=CBite8, K2=CBite9;
// SITE3: K1=CBite16, K2=CBite17; SITE4: K1=CBite23, K2=CBite24;
CBITe cbite;
BYTE K1_S1 = 0;  BYTE K2_S1 = 1;
BYTE K1_S2 = 8;  BYTE K2_S2 = 9;
BYTE K1_S3 = 16; BYTE K2_S3 = 17;
BYTE K1_S4 = 23; BYTE K2_S4 = 24;
cbite.SetOn(K1_S1, K1_S2, K1_S3, K1_S4, K2_S1, K2_S2, K2_S3, K2_S4, -1);

// Or using macros:
#define K1 0,8,16,23
#define K2 1,9,17,24
cbite.SetOn(K1, K2, -1);
```

---

## 2.2 Init()

**Signature:**
```cpp
void Init();
```

**Remarks:**
Initializes CBITe control bits. After execution:
1. All CBITe control bits output HIGH (relays OPEN/OFF).
2. All user power supplies (+5V, +12V, +/-15V) are OFF.

**Example:**
```cpp
cbite.Init();
// set all cbite off status and power off all user power
```

---

## 2.3 SetOn()

**Signature:**
```cpp
BYTE SetOn(int k1, ...);
```

**Parameters:**
- `k1, ...` -- CBITe control bit numbers (variable arguments). **Last argument MUST be -1** as terminator.

**Return Values:**
- `-1` -- set failed
- `0` -- set success

**Remarks:**
- **Without site binding:** k1,... pins output LOW (relay CLOSED/ON); unspecified pins output HIGH (relay OPEN/OFF).
- **With site binding:**
  - Specified pins on valid sites or NO_SITE output LOW (relay ON).
  - Specified pins on invalid sites output HIGH (relay OFF).
  - Specified pins without site binding keep previous state.
  - All unspecified pins are set OFF.

**Example:**
```cpp
CBITe cbite;
BYTE K1=0, K2=1, K3=2, K4=3;
cbite.SetOn(K1, K2, -1);       // only K1,K2 on; K3,K4 off
cbite.SetOn(K1, K2, K3, K4, -1); // all four on
cbite.SetOn(-1);               // all off
```

**⚠ 排他陷阱（用户 2026-08-09 纠正）**：`SetOn` 是**排他（exclusive）操作**——每次调用只闭合括号内列出的继电器，**未列出的全部释放（OFF）**。
- **错误模式**：`SetOn(A, -1); SetOn(B, -1);` 两次分开调用 → 第二次把 A 释放，**最终只有 B 闭合，A 没有闭合**。
- **正确做法**：要同时闭合多个继电器，**列在同一次 SetOn 括号内**：`SetOn(A, B, -1);`。
- 需要叠加保留时用 `SetCbiteOn(nIndex)`（单 bit 非排他，不影响其它继电器）。
- **DALI 实际踩坑（2026-08-09）**：TM109/110（K65+K19/K18）、TM111/112（K21+K65）原写成两行分开 SetOn，导致第一个继电器被第二次调用释放（K21/K65 实际未闭合）；已合并为单次 `SetOn(K65, K19_ACM0_VAC2, -1)` 等。写码后必须检查：**连续两行 SetOn = 排他冲突嫌疑**。

---

## 2.4 SetCbiteOn()

**Signature:**
```cpp
BYTE SetCbiteOn(BYTE nIndex);
```

**Parameters:**
- `nIndex` -- Single CBITe control bit to turn ON.

**Return Values:**
- `-2` -- board invalid
- `0` -- set success

**Remarks:**
- **Without site binding:** Sets nIndex to LOW (relay ON). Only affects the specified bit; all others keep their state.
- **With site binding:** If nIndex is on a valid site or NO_SITE, relay closes; otherwise keeps previous state.

**Example:**
```cpp
CBITe cbite;
BYTE K1=0, K2=1, K3=2, K4=3;
cbite.SetCbiteOn(K1);  // K1 on
cbite.SetCbiteOn(K2);  // K2 on, K1 still on
cbite.SetCbiteOn(K3);  // K3 on, K1,K2 still on
cbite.SetCbiteOn(K4);  // K4 on, K1,K2,K3 still on
cbite.SetCbiteOff(K1); // K1 off, K2,K3,K4 still on
cbite.SetCbiteOff(K4); // K4 off, K2,K3 still on
```

---

## 2.5 SetCbiteOff()

**Signature:**
```cpp
BYTE SetCbiteOff(BYTE nIndex);
```

**Parameters:**
- `nIndex` -- Single CBITe control bit to turn OFF.

**Return Values:**
- `-2` -- board invalid
- `0` -- set success

**Remarks:**
- **Without site binding:** Sets nIndex to HIGH (relay OFF). Only affects the specified bit; all others keep their state.
- **With site binding:** If nIndex is on a valid site or NO_SITE, relay opens; otherwise keeps previous state.

**Example:** See SetCbiteOn() example above.

---

## 2.6 GetCbiteStatus()

**Signature:**
```cpp
WORD GetCbiteStatus(CBITe_BYTE_NO nByte);
```

**Parameters:**
- `nByte` -- One of 16 chip-select groups, each controlling 16 bits:
  `CBITE_CHIPS_1` through `CBITE_CHIPS_16`
  - CBITE_CHIPS_1: bits 0~15
  - CBITE_CHIPS_2: bits 16~31
  - ... etc through CBITE_CHIPS_16: bits 240~255

**Return Values:**
Returns a decimal WORD; convert to binary -- each bit represents one control bit status:
- `1` = relay CLOSED (ON)
- `0` = relay OPEN (OFF)

**Remarks:**
Gets the status of the 16 control bits in the specified group. The returned value is decimal; bit 0 is the lowest channel in the group, bit 15 is the highest.

**Example:**
```cpp
BYTE result = 0;
cbite.SetOn(2,3,4,5,6,7,-1);
delay_ms(1);
result = cbite.GetCbiteStatus(CBITE_CHIPS_1);
// result=252 (0000000011111100 binary), highest=ch15, lowest=ch0

result = cbite.GetCbiteStatus(CBITE_CHIPS_8); // bits 112~127
// e.g. result=63829 (1111100101010101)
```

---

## 2.7 SetDutPower()

**Signature:**
```cpp
int SetDutPower(
    CBITe_POWER power_sel,
    CBITe_POWER_STATUS status,
    CBITe_BOARD_SEL boardno);
```

**Parameters:**
- `power_sel` -- Power supply selection:
  - `CBITE_15V_POSITIVE` -- +15V
  - `CBITE_15V_NEGATIVE` -- -15V
  - `CBITE_12V_POSITIVE` -- +12V
  - `CBITE_5V_POSITIVE` -- +5V
  - `CBITE_ALL_USERPOWER` -- all four supplies
- `status` -- Power state:
  - `CBITE_POWERON` -- power ON
  - `CBITE_POWEROFF` -- power OFF
- `boardno` -- Board selection:
  - `CBITE_BOARD1` -- first board
  - `CBITE_BOARD2` -- second board

**Return Values:**
- `0` -- selected board valid
- `-2` -- selected board invalid

**Remarks:**
Controls the four user power supplies on the selected CBITe board.

**Example:**
```cpp
cbite.SetDutPower(CBITE_ALL_USERPOWER, CBITE_POWERON, CBITE_BOARD2);
// set all user power of CBITE_BOARD2 on
```

---

## 2.8 GetDutPowerStatus()

**Signature:**
```cpp
int GetDutPowerStatus(    // NOTE: PDF shows "DutPowerStatus" not "GetDutPowerStatus"
    CBITe_POWER power_sel,
    CBITe_BOARD_SEL boardno);
```

**Parameters:**
- `power_sel` -- Power supply to query (same enum as SetDutPower):
  - `CBITE_15V_POSITIVE`, `CBITE_15V_NEGATIVE`, `CBITE_12V_POSITIVE`, `CBITE_5V_POSITIVE`, `CBITE_ALL_USERPOWER`
- `boardno` -- Board selection: `CBITE_BOARD1` or `CBITE_BOARD2`

**Return Values:**
- `1` -- power is ON and operating normally
- `0` -- power is OFF
- `-1` -- power should be ON but operating abnormally (e.g. 5V outputting only 3V)
- `-2` -- selected board invalid
- `-3` -- board supports programmable control but does not support power status query
- `-4` -- board does not support programmable power control
- For `CBITE_ALL_USERPOWER`: returns an 8-bit value -- upper 4 bits = ON/OFF status, lower 4 bits = operating status

**Remarks:**
Gets the power status of a board's supply.

**Example:**
```cpp
int result = 0;
result = cbite.GetDutPowerStatus(CBITE_15V_POSITIVE, CBITE_BOARD1);
```

---

## 2.9.1 GetBoardSN()

**Signature:**
```cpp
int GetBoardSN(
    CBITe_BOARD_SEL boardno,
    char* boardSN,
    UINT snSize);
```

**Parameters:**
- `boardno` -- Board: `CBITE_BOARD1` or `CBITE_BOARD2`
- `boardSN` -- User-defined char buffer (e.g. `char boardSN[255]={0}`). Returns "N/A" if not stored.
- `snSize` -- Size of boardSN buffer (UINT, positive integer)

**Return Values:**
- `0` -- read success
- `-1` -- site invalid, read failed

**Remarks:**
Gets the board serial number.

**Example:**
```cpp
char boardSN[255] = {0};
cbite.GetBoardSN(CBITE_BOARD1, boardSN, 255);
```

---

## 2.9.2 GetBoardHDRev()

**Signature:**
```cpp
int GetBoardHDRev(
    CBITe_BOARD_SEL boardno,
    char* hardRev,
    UINT revSize);
```

**Parameters:**
- `boardno` -- Board: `CBITE_BOARD1` or `CBITE_BOARD2`
- `hardRev` -- User-defined char buffer (e.g. `char hardRev[255]={0}`). Returns "N/A" if not stored.
- `revSize` -- Size of hardRev buffer (UINT, positive integer)

**Return Values:**
- `0` -- read success
- `-1` -- site invalid, read failed

**Remarks:**
Gets the board hardware revision.

**Example:**
```cpp
char hardRev[255] = {0};
cbite.GetBoardHDRev(CBITE_BOARD1, hardRev, 255);
```

---

# QTMUe -- Time Measurement Unit (Chapter 3)

One QTMUe board has max 4 channels (板内序号 max 3).
Channel list format: `"S23_0,S23_1"` where S=Slot, numbers=board-internal channel index.

---

## 3.1 QTMUe() -- Constructor

**Signature:**
```cpp
QTMUe(char* channelList, char* chName = NULL);
```

**Parameters:**
- `channelList` -- Channel binding string, e.g. `"S23_0,S23_1"`. "S23" = slot 23, "0,1" = board-internal channel indices (max 3 per board).
- `chName` -- Custom channel name (optional). Default NULL, system names it `QTMUe_xx`.

**Remarks:**
Defines a QTMUe channel, specifying the physical channel(s) it contains (slot + board-internal index).

**Example:**
```cpp
// 1 QTMUe board at Slot23, 4-site parallel:
QTMUe qtmue0("S23_0-3");
// Site binding:
STSSetMultiSiteBind(MD_QTMUe, SITE_1, "S23_0");
STSSetMultiSiteBind(MD_QTMUe, SITE_2, "S23_1");
STSSetMultiSiteBind(MD_QTMUe, SITE_3, "S23_2");
STSSetMultiSiteBind(MD_QTMUe, SITE_4, "S23_3");
```

---

## 3.2 Connect()

**Signature:**
```cpp
int Connect(
    QTMUe_RELAY_CHANNEL RelayChabSel,
    UINT InoutDelay = 500);
```

**Parameters:**
- `RelayChabSel` -- Relay channel selection:
  - `QTMUe_RELAY_CHA` -- connect CHA only
  - `QTMUe_RELAY_CHB` -- connect CHB only
  - `QTMUe_RELAY_CHAB` -- connect both CHA and CHB
- `InoutDelay` -- Delay after relay connection, unit uS, range 0~10000, default 500.
  - Default 500uS is the minimum relay settling time.
  - Delay can be shared for efficiency: `qtmue0.Connect(..., 0); qtmue1.Connect(..., 500);`
  - Can reduce delay if other operations/delays occur between Connect() and Measure().

**Remarks:**
Connects the input relay of the current QTMUe logical channel.

**Example:**
```cpp
qtmue0.Connect(QTMUe_RELAY_CHA, 500); // connect CHA, delay 500uS
```

---

## 3.3 Disconnect()

**Signature:**
```cpp
int Disconnect(
    QTMUE_RELAY_CHANNEL RelayChabSel,
    UINT InoutDelay = 100);
```

**Parameters:**
- `RelayChabSel` -- Relay channel to disconnect:
  - `QTMUe_RELAY_CHA` -- disconnect CHA only
  - `QTMUe_RELAY_CHB` -- disconnect CHB only
  - `QTMUe_RELAY_CHAB` -- disconnect both CHA and CHB
- `InoutDelay` -- Delay after disconnection, unit uS, range 0~10000, default 100.
  - Default 100uS is the minimum relay release time.
  - Same delay-sharing principles as Connect().

**Remarks:**
Disconnects the input relay of the current logical channel.

**Example:**
```cpp
qtmue0.Disconnect(QTMUe_RELAY_CHB, 100); // disconnect CHB, delay 100uS
```

---

## 3.4 SetInSource()

**Signature:**
```cpp
int SetInSource(
    QTMUe_SOURCE_AB sourceSel = QTMUe_SINGLE_SOURCE_A);
```

**Parameters:**
- `sourceSel` -- Measurement signal source:
  - `QTMUe_SINGLE_SOURCE_A` -- single-source, Start and Stop both from SOURCE_A
  - `QTMUe_SINGLE_SOURCE_B` -- single-source, Start and Stop both from SOURCE_B
  - `QTMUe_DUAL_SOURCE_START_A` -- dual-source, Start=SOURCE_A, Stop=SOURCE_B
  - `QTMUe_DUAL_SOURCE_START_B` -- dual-source, Start=SOURCE_B, Stop=SOURCE_A
  - Default: `QTMUe_SINGLE_SOURCE_A`

**Remarks:**
Sets whether measurement uses single or dual signal source, and which sources for Start/Stop. Also sets the matrix relationship between user-side channel unit and board-internal measurement unit (1-to-1).

**Important notes:**
1. Using this function defaults TMU to MU1.
2. MUST be called before Start() and Stop() to ensure the TMU matches.
3. If SetInSource is after Start/Stop, TMU mismatch occurs; Measure() returns error.
4. System calls `SetInSource(QTMUe_SINGLE_SOURCE_A)` after each test (`InitAfterTestFlow`) to restore single-source default.
5. For complex matrix relationships, use SetMatrix() instead.

**Example:**
```cpp
// Single source, both Start and Stop from SOURCE_A:
qtmue0.SetInSource(QTMUe_SINGLE_SOURCE_A);

// Dual source, Start=SOURCE_A, Stop=SOURCE_B:
qtmue0.SetInSource(QTMUe_DUAL_SOURCE_START_A);
```

---

## 3.5 SetMatrix()

**Signature:**
```cpp
int SetMatrix(
    QTMUe_TMU TmuSel,
    QTMUe_CHANNEL StartChSel,
    QTMUe_CHANNEL StopChSel,
    int siteNo = QTMUe_ALLSITE);
```

**Parameters:**
- `TmuSel` -- Time measurement unit selection:
  - `QTMUe_MU1` -- TMU 1
  - `QTMUe_MU2` -- TMU 2
- `StartChSel` -- Start signal source channel:
  - `QTMUe_CHANNEL_A` -- CHA of all physical channels in logical channel
  - `QTMUe_CHANNEL_B` -- CHB of all physical channels in logical channel
  - `QTMUe_CHANNEL_0A` -- physical channel 0 CHA
  - `QTMUe_CHANNEL_1A` -- physical channel 1 CHA
  - `QTMUe_CHANNEL_2A` -- physical channel 2 CHA
  - `QTMUe_CHANNEL_3A` -- physical channel 3 CHA
  - `QTMUe_CHANNEL_0B` -- physical channel 0 CHB
  - `QTMUe_CHANNEL_1B` -- physical channel 1 CHB
  - `QTMUe_CHANNEL_2B` -- physical channel 2 CHB
  - `QTMUe_CHANNEL_3B` -- physical channel 3 CHB
- `StopChSel` -- Stop signal source channel (same enum values as StartChSel)
- `siteNo` -- Site selection, range [-1, 250]. Default `QTMUe_ALLSITE` (-1).
  - `QTMUe_ALLSITE` (-1) -- all sites
  - Non-negative N -- specific site N

**Return Values:**
- Returns -1 if siteNo is out of range (no matrix set).

**Important constraints:**
1. When StartChSel/StopChSel = `QTMUe_CHANNEL_A` or `QTMUe_CHANNEL_B`, siteNo MUST be `QTMUe_ALLSITE` (can be omitted).
2. When StartChSel = `QTMUe_CHANNEL_A/B`, StopChSel must also be `QTMUe_CHANNEL_A/B`.
3. When StartChSel = `QTMUe_CHANNEL_0A~3B`, StopChSel must also be `QTMUe_CHANNEL_0A~3B`, and siteNo must be a specific site (non-negative), NOT `QTMUe_ALLSITE`.

**Remarks:**
Sets the matrix relationship between user-side channel unit and board-internal measurement unit.

**Notes:**
1. Both SetMatrix and SetInSource set the matrix -- the last call wins on hardware.
2. SetMatrix setting persists until SetInSource is called.
3. MUST be called before Start/Stop to keep TMU consistent.
4. If SetMatrix comes after Start/Stop, TMU mismatch in Measure() returns error.
5. If SetMatrix sets different MUs for different sites, Start/Stop/Measure MUST use serial-site macros for per-site MU setup, or Measure() will skip.
6. Group setting only supported when siteNo = `QTMUe_ALLSITE`.

**Example:**
```cpp
// All sites: MU1 with CHA as both Start and Stop:
qtmue0.SetMatrix(QTMUe_MU1, QTMUe_CHANNEL_A, QTMUe_CHANNEL_A, QTMUe_ALLSITE);

// Per-site configuration (SITE_1=site 0, SITE_2=site 1):
qtmue0.SetMatrix(QTMUe_MU1, QTMUe_CHANNEL_0A, QTMUe_CHANNEL_1A, 0);
qtmue0.SetMatrix(QTMUe_MU2, QTMUe_CHANNEL_0A, QTMUe_CHANNEL_1B, 0);
qtmue0.SetMatrix(QTMUe_MU1, QTMUe_CHANNEL_2A, QTMUe_CHANNEL_3A, 1);
qtmue0.SetMatrix(QTMUe_MU2, QTMUe_CHANNEL_2A, QTMUe_CHANNEL_3B, 1);
```

---

## 3.6 Start()

**Signature:**
```cpp
void Start(
    QTMUe_TMU TmuSel = QTMUe_MU1,
    QTMUe_VRANGE Vrange = QTMUe_50V,
    QTMUe_SLOPE Slope = QTMUe_POS,
    double TriggerLevel = 0.0,
    QTMUe_FILTER Filter = QTMUe_FILTER_PASS,
    UINT TriggerWidth = 200,
    UINT HoldoffTime = 0,
    UINT HoldoffNum = 0);
```

**Parameters:**
- `TmuSel` -- Time measurement unit:
  - `QTMUe_MU1`, `QTMUe_MU2`. Default `QTMUe_MU1`.
- `Vrange` -- Voltage range:
  - `QTMUe_50V`, `QTMUe_25V`, `QTMUe_10V`, `QTMUe_5V`, `QTMUe_N2P6V`. Default `QTMUe_50V`.
- `Slope` -- Comparator trigger polarity:
  - `QTMUe_POS` -- rising edge trigger
  - `QTMUe_NEG` -- falling edge trigger
  - Default `QTMUe_POS`.
- `TriggerLevel` -- Comparator trigger level in Volts, range must match Vrange. Default 0.0V.
- `Filter` -- Input filter (invalid in `QTMUe_N2P6V` range):
  - `QTMUe_FILTER_PASS` -- direct path, no filter
  - `QTMUe_FILTER_10MHz` -- 10MHz low-pass
  - `QTMUe_FILTER_1MHz` -- 1MHz low-pass
  - `QTMUe_FILTER_100KHz` -- 100KHz low-pass
  - Default `QTMUe_FILTER_PASS`.
  - **Warning:** Use filter if signal has high-frequency noise. Do NOT use filter for square-wave signals.
- `TriggerWidth` -- Trigger pulse width, range 0~80000, step 5, unit nS. Default 200. Non-multiples of 5 are rounded to nearest.
  - After signal reaches TriggerLevel, it must stay above (rising) or below (falling) for TriggerWidth to qualify as a trigger event.
- `HoldoffTime` -- Delayed trigger time, range 0~1e9, step 5, unit nS. Default 0. Non-multiples of 5 rounded.
- `HoldoffNum` -- Number of START events to ignore, range 0~65535. Default 0.

**Remarks:**
Sets the START signal configuration.

**Note:** For single-source measurement, Start and Stop must have matching Vrange and Filter.

**Example:**
```cpp
// 10V range, rising edge at 3.5V, 1MHz filter, MU1:
qtmue0.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 3.5, QTMUe_FILTER_1MHz);

// 5V range, rising edge 1.5V, no filter, pulse width 10nS, MU2, ignore 1 event:
qtmue0.Start(QTMUe_MU2, QTMUe_5V, QTMUe_POS, 1.5, QTMUe_FILTER_PASS, 10, 0, 1);
```

---

## 3.7 Stop()

**Signature:**
```cpp
void Stop(
    QTMUe_TMU TmuSel = QTMUe_MU1,
    QTMUe_VRANGE Vrange = QTMUe_50V,
    QTMUe_SLOPE Slope = QTMUe_POS,
    double TriggerLevel = 0.0,
    QTMUe_FILTER Filter = QTMUe_FILTER_PASS,
    UINT TriggerWidth = 200,
    UINT HoldoffTime = 0,
    UINT HoldoffNum = 0);
```

**Parameters:**
All parameters identical to Start() (see section 3.6).

**Remarks:**
Sets the STOP signal configuration.

**Notes:**
1. For single-source measurement, Start and Stop must have matching Vrange and Filter.
2. When measuring frequency, this function does not need to be called.

**Example:**
```cpp
// 10V range, falling edge 3.5V, 1MHz filter, MU1:
qtmue0.Stop(QTMUe_MU1, QTMUe_10V, QTMUe_NEG, 3.5, QTMUe_FILTER_1MHz);

// 5V range, rising edge 1.5V, no filter, MU2, ignore 2 STOP events:
qtmue0.Stop(QTMUe_MU2, QTMUe_5V, QTMUe_POS, 1.5, QTMUe_FILTER_PASS, 10, 0, 2);
```

---

## 3.8 SetArm()

**Signature:**
```cpp
int SetArm(
    QTMUe_TMU TmuSel = QTMUe_MU1,
    QTMUe_TRIGGER_SOURCE Source = QTMUe_ARM_SOURCE,
    QTMUe_ARM_MODE TriggerMode = QTMUe_EDGE,
    QTMUe_SLOPE Slope = QTMUe_POS,
    UINT Holdoff = 0,
    UINT ArmNum = 1);
```

**Parameters:**
- `TmuSel` -- Time measurement unit: `QTMUe_MU1`, `QTMUe_MU2`. Default `QTMUe_MU1`.
- `Source` -- External trigger source:
  - `QTMUe_ARM_SOURCE` -- trigger inputs of all physical channels in logical channel
  - `QTMUe_ARM_SOURCE_0` -- physical channel 0 trigger input
  - `QTMUe_ARM_SOURCE_1` -- physical channel 1 trigger input
  - `QTMUe_ARM_SOURCE_2` -- physical channel 2 trigger input
  - `QTMUe_ARM_SOURCE_3` -- physical channel 3 trigger input
  - Default `QTMUe_ARM_SOURCE`.
- `TriggerMode` -- Trigger mode:
  - `QTMUe_EDGE` -- edge trigger
  - `QTMUe_LEVEL` -- level trigger
  - Default `QTMUe_EDGE`.
- `Slope` -- Trigger polarity/level:
  - `QTMUe_POS` -- rising edge (high level) trigger
  - `QTMUe_NEG` -- falling edge (low level) trigger
  - Default `QTMUe_POS`.
- `Holdoff` -- Edge count / level time. Default 0.
  - Edge trigger mode: range 0~65535 (edge count).
  - Level trigger mode: range 0~327675, step 5nS. Non-multiples of 5 rounded.
- `ArmNum` -- Trigger count. Range = 1 (only 1 external trigger currently supported). Default 1.

**Remarks:**
Sets external trigger (Arm) conditions.

**Notes:**
1. External trigger input requirements: 2V <= high level <= 5.5V, 0 <= low level <= 0.8V.
2. If using external trigger, SetArm's TmuSel MUST match Start and Stop.
3. Default (when not called) = auto-trigger mode.

**Example:**
```cpp
// External trigger, edge trigger, rising edge, MU1:
qtmue0.SetArm(QTMUe_MU1, QTMUe_ARM_SOURCE, QTMUe_EDGE, QTMUe_POS);
```

---

## 3.9 StopArm()

**Signature:**
```cpp
int StopArm(
    QTMUe_TMU TmuSel = QTMUe_MU1);
```

**Parameters:**
- `TmuSel` -- Time measurement unit: `QTMUe_MU1`, `QTMUe_MU2`. Default `QTMUe_MU1`.

**Remarks:**
Restores auto-trigger mode. Also resets SetArm parameters (TriggerMode, Slope, Holdoff, ArmNum) to defaults.

---

## 3.10 Measure()

**Signature:**
```cpp
void Measure(
    QTMUe_TMU TmuSel = QTMUe_MU1,
    QTMUe_MEAS_TYPE MeasType = QTMUe_MEAS_TIME,
    UINT SampleNum = 1,
    Double msTimeout = 1,
    QTMUe_TRANGE Trange = QTMUe_TRANGE_MS);
```

**Parameters:**
- `TmuSel` -- Time measurement unit: `QTMUe_MU1`, `QTMUe_MU2`. Default `QTMUe_MU1`.
- `MeasType` -- Measurement type:
  - `QTMUe_MEAS_TIME` -- measure time
  - `QTMUe_MEAS_FREQ` -- measure frequency
  - `QTMUe_MEAS_HIGH_DUTY` -- high duty cycle (ratio of high time in one period)
  - `QTMUe_MEAS_LOW_DUTY` -- low duty cycle (ratio of low time in one period)
  - `QTMUe_MEAS_EVENT` -- measure events
  - Default `QTMUe_MEAS_TIME`.
- `SampleNum` -- Number of samples, range 1~65535, default 1.
  - For TIME: number of sampling times
  - For FREQ: number of cycles
  - For HIGH_DUTY/LOW_DUTY: number of edges (must be >= 3 for at least one full period)
  - For EVENT: number of events (includes both start and stop)
- `msTimeout` -- Measurement wait timeout, range 0.001~2e5, unit mS, default 1mS. Values out of range default to 1.
- `Trange` -- Time measurement range:
  - `QTMUe_TRANGE_MS` -- mS range (5nS ~ 40S)
  - `QTMUe_TRANGE_US` -- uS range (800nS ~ 4mS)
  - `QTMUe_TRANGE_NS` -- nS range (5nS ~ 950nS)
  - Default `QTMUe_TRANGE_MS`.

**Important constraints:**
- For HIGH_DUTY/LOW_DUTY/EVENT: Trange MUST be `QTMUe_TRANGE_MS`.
- For FREQ: total time of SampleNum cycles must fit within the selected Trange.
- For HIGH_DUTY/LOW_DUTY: SampleNum >= 3 required, Start slope and Stop slope must be opposite (one POS, one NEG), and HoldoffNum in both Start() and Stop() must be 0.

**Remarks:**
Starts measurement.

**Notes:**
1. If Measure's MU was not set in SetMatrix/SetInSource, no measurement occurs, returns error value.
2. If Measure's MU was set in SetMatrix/SetInSource but not in Start/Stop, no measurement occurs, returns error value.

**Example:**
```cpp
// Measure time with MU1, 1 sample, 2mS timeout:
qtmue0.Measure(QTMUe_MU1, QTMUe_MEAS_TIME, 1, 2);
```

---

## 3.11 GetMeasureResult()

**Signature:**
```cpp
double GetMeasureResult(
    UINT siteNo,
    int retType = AVERAGE_RESULT,
    QTMUe_TMU TmuSel = QTMUe_MU1,
    UINT ArmNo = 0);
```

**Parameters:**
- `siteNo` -- Site number to read result from. 0=SITE_1, 1=SITE_2, ...
- `retType` -- Result type:
  - `AVERAGE_RESULT` -- return average
  - Non-negative N (0 <= N <= SampleNum-1) -- return the (N+1)th sample value
  - Default `AVERAGE_RESULT`.

  **Behavior by MeasType:**
  - `QTMUe_MEAS_TIME` + AVERAGE_RESULT: returns time average, unit **uS**.
  - `QTMUe_MEAS_TIME` + N: returns (N+1)th sample value, unit **uS**.
  - `QTMUe_MEAS_FREQ`: retType ignored, returns frequency in **KHz**.
  - `QTMUe_MEAS_HIGH_DUTY` / `QTMUe_MEAS_LOW_DUTY`: retType ignored, returns duty cycle in **%**.
  - `QTMUe_MEAS_EVENT` + AVERAGE_RESULT: returns number of qualifying events (count).
  - `QTMUe_MEAS_EVENT` + N: returns time of (N+1)th event, unit **uS**.

- `TmuSel` -- Time measurement unit: `QTMUe_MU1`, `QTMUe_MU2`. Default `QTMUe_MU1`. MUST match the TmuSel used in Start()/Stop().
- `ArmNo` -- Get result from (N+1)th external trigger, range 0. Currently only supports 0 (= 1st trigger). Default 0.

**Remarks:**
Gets measurement result based on MeasType from Measure().

**Example:**
```cpp
qtmue0.SetInSource(QTMUe_SINGLE_SOURCE_A);
qtmue0.Start(QTMUe_MU1, QTMUe_50V, QTMUe_POS, 1.5, QTMUe_FILTER_PASS);
qtmue0.Stop(QTMUe_MU1, QTMUe_50V, QTMUe_POS, 13.5, QTMUe_FILTER_PASS);
qtmue0.Connect(QTMUe_RELAY_CHA, 500);
qtmue0.Measure(QTMUe_MU1, QTMUe_MEAS_TIME, 10, 20, QTMUe_TRANGE_MS);
// sampleNum=10, timeout=20mS

qtmue0.GetMeasureResult(0, AVERAGE_RESULT, QTMUe_MU1); // avg time of site 1
qtmue0.GetMeasureResult(0, 5, QTMUe_MU1);              // 6th point time of site 1

// High duty cycle:
qtmue0.SetInSource(QTMUe_SINGLE_SOURCE_A);
qtmue0.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.0, QTMUe_FILTER_PASS);
qtmue0.Stop(QTMUe_MU1, QTMUe_10V, QTMUe_NEG, 2.0, QTMUe_FILTER_PASS);
qtmue0.Connect(QTMUe_RELAY_CHA, 500);
qtmue0.Measure(QTMUe_MU1, QTMUe_MEAS_HIGH_DUTY, 20, 10, QTMUe_TRANGE_MS);
qtmue0.GetMeasureResult(0, AVERAGE_RESULT, QTMUe_MU1); // high duty % of site 1
```

---

## 3.12 SetAlarmMask()

**Signature:**
```cpp
void SetAlarmMask(
    UINT siteNo,
    bool maskStatus = true);
```

**Parameters:**
- `siteNo` -- Site to set alarm mask for. 0=SITE_1, 1=SITE_2, ...
- `maskStatus` -- bool:
  - `true` -- mask (suppress) alarm info for this site
  - `false` -- output alarm info for this site
  - Default `true`.

**Remarks:**
Sets whether to mask alarm info for the specified site.

**Example:**
```cpp
qtmue0.SetAlarmMask(0, true); // mask SITE_1 alarm info
// Over-range voltage alarm will not be output
qtmue0.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 15, QTMUe_FILTER_1MHz);
```

---

## 3.13 GetAlarmMask()

**Signature:**
```cpp
bool GetAlarmMask(UINT siteNo);
```

**Parameters:**
- `siteNo` -- Site to read alarm status from. 0=SITE_1, 1=SITE_2, ...

**Return Values:**
- `true` -- alarm info masked for this site
- `false` -- alarm info output enabled

**Remarks:**
Reads the alarm masking status of the specified site.

**Example:**
```cpp
bool status = qtmue0.GetAlarmMask(0); // get alarm status of SITE_1
```

---

## 3.14 SiteBindModify()

**Signature:**
```cpp
int SiteBindModify(char* modifySiteList);
```

**Parameters:**
- `modifySiteList` -- Site reconfiguration string. Format: `"origSite1:destSite1,origSite2:destSite2,..."`
  - Orig and dest separated by colon (:), multiple modifications separated by comma (,).
  - Site numbers: 0 (SITE_1) to 250 (SITE_251).
  - Example: `"0:2,1:3"` = SITE_1 -> SITE_3, SITE_2 -> SITE_4.

**Return Values:**
- `0` -- success
- Non-zero -- failure

**Failure conditions:**
1. Multiple modifications must be comma-separated; first/last char cannot be comma; no empty between commas.
2. Each pair must have exactly one colon, digits on both sides, no other chars.
3. Both orig and dest must be in [0, 251).
4. Cannot reconfigure NO_SITE channels.
5. Same call cannot modify same site twice (e.g. `"0:1,0:2"`).
6. Same call cannot map different sites to same dest (e.g. `"0:2,1:2"`).
7. If dest site already has channels configured, it must also be remapped in same call.

**Remarks:**
Reconfigures site binding for channels. Channels not mentioned keep their original site info. This is NOT affected by site validity -- e.g. remapping SITE_1 to SITE_2 works even if SITE_1 is currently invalid.

**Example:**
```cpp
QTMUe qtmue0("S4_0,S4_1");
QTMUe qtmue1("S4_2,S4_3");
// Initial binding:
STSSetMultiSiteBind(MD_QTMUe, SITE_1, "S4_0,S4_2");
STSSetMultiSiteBind(MD_QTMUe, SITE_2, "S4_1,S4_3");

// Remap SITE_1 to SITE_3, SITE_2 to SITE_4:
qtmue0.SiteBindModify("0:2,1:3");

// Remap only SITE_1 to SITE_3, SITE_2 unchanged:
qtmue0.SiteBindModify("0:2");
```

---

## 3.15 Board Information Functions

### 3.15.1 GetBoardSN()

**Signature:**
```cpp
int GetBoardSN(
    UINT siteNo,
    char* boardSN,
    UINT snSize);
```

**Parameters:**
- `siteNo` -- Site to read from. 0=SITE_1, 1=SITE_2, ...
- `boardSN` -- User char buffer (e.g. `char boardSN[255]={0}`). Returns "N/A" if not stored.
- `snSize` -- Buffer size (UINT, positive).

**Return Values:**
- `0` -- success
- `-1` -- site invalid, read failed

**Example:**
```cpp
char boardSN[255] = {0};
qtmue0.GetBoardSN(0, boardSN, 255);
```

### 3.15.2 GetBoardHDRev()

**Signature:**
```cpp
int GetBoardHDRev(
    UINT siteNo,
    char* hardRev,
    UINT revSize);
```

**Parameters:**
- `siteNo` -- Site to read from. 0=SITE_1, 1=SITE_2, ...
- `hardRev` -- User char buffer (e.g. `char hardRev[255]={0}`). Returns "N/A" if not stored.
- `revSize` -- Buffer size (UINT, positive).

**Return Values:**
- `0` -- success
- `-1` -- site invalid, read failed

**Example:**
```cpp
char hardRev[255] = {0};
qtmue0.GetBoardHDRev(0, hardRev, 255);
```

---

## 3.16 Calibration Information Functions

### 3.16.1 GetCalibrationTime()

**Signature:**
```cpp
SYSTEMTIME GetCalibrationTime(UINT siteNo) const;
```

**Parameters:**
- `siteNo` -- Site. 0=SITE_1, 1=SITE_2, ...

**Return Values:**
- Normal: calibration date/time
- Error: 1970-1-1 8:0:0 (causes: channel not calibrated, or site invalid)

**Example:**
```cpp
SYSTEMTIME calDate;
calDate = qtmue0.GetCalibrationTime(0);
```

### 3.16.2 GetCalibrationTemperature()

**Signature:**
```cpp
double GetCalibrationTemperature(UINT siteNo) const;
```

**Parameters:**
- `siteNo` -- Site. 0=SITE_1, 1=SITE_2, ...

**Return Values:**
- Normal: calibration temperature (double)
- Error: 0 (causes: channel not calibrated, or site invalid)

**Example:**
```cpp
double calTemperature = 0.0;
calTemperature = qtmue0.GetCalibrationTemperature(0);
```

### 3.16.3 GetCalibrationHumidity()

**Signature:**
```cpp
double GetCalibrationHumidity(UINT siteNo) const;
```

**Parameters:**
- `siteNo` -- Site. 0=SITE_1, 1=SITE_2, ...

**Return Values:**
- Normal: calibration humidity (double)
- Error: 0 (causes: channel not calibrated, or site invalid)

**Example:**
```cpp
double calHumidity = 0.0;
calHumidity = qtmue0.GetCalibrationHumidity(0);
```

### 3.16.4 GetCalibrationResult()

**Signature:**
```cpp
CAL_RESULT GetCalibrationResult(UINT siteNo) const;
```

**Parameters:**
- `siteNo` -- Site. 0=SITE_1, 1=SITE_2, ...

**Return Values (enum):**
- `CAL_PASS` -- calibration passed
- `CAL_FAIL` -- calibration failed
- `STS_NO_RESULT_RECORD` -- not stored or site invalid

**Example:**
```cpp
CAL_RESULT calResult;
calResult = qtmue0.GetCalibrationResult(0);
```

### 3.16.5 GetCalibrationLogicRev()

**Signature:**
```cpp
int GetCalibrationLogicRev(UINT siteNo) const;
```

**Parameters:**
- `siteNo` -- Site. 0=SITE_1, 1=SITE_2, ...

**Return Values:**
- Normal: logic revision number (int)
- Error: 255 (causes: channel not calibrated, or site invalid)

**Example:**
```cpp
int calLogicRev = 0;
calLogicRev = qtmue0.GetCalibrationLogicRev(0);
```

### 3.16.6 GetCalibrationMeter()

**Signature:**
```cpp
CAL_METER GetCalibrationMeter(
    UINT siteNo,
    char* meterSN = NULL,
    UINT snSize = 0);
```

**Parameters:**
- `siteNo` -- Site. 0=SITE_1, 1=SITE_2, ...
- `meterSN` -- User char buffer for meter SN. Returns "N/A" if not stored. Default NULL (don't read SN).
- `snSize` -- Buffer size. Default 0.

**Return Values (enum):**
- `STS_KEITHLEY2000` -- Keithley 2000
- `STS_AGILENT34401` -- Agilent 34401
- `STS_AGILENT3458A` -- Agilent 3458A
- `STS_NO_METER_RECORD` -- not stored or site invalid

**Example:**
```cpp
char meterSN[255] = {0};
CAL_METER calMeter;
calMeter = qtmue0.GetCalibrationMeter(0, meterSN, 255);
```

### 3.16.7 GetCalibrationCalBoardInfo()

**Signature:**
```cpp
int GetCalibrationCalBoardInfo(
    UINT siteNo,
    char* boardSN = NULL,
    UINT snSize = 0,
    char* hardRev = NULL,
    UINT revSize = 0);
```

**Parameters:**
- `siteNo` -- Site. 0=SITE_1, 1=SITE_2, ...
- `boardSN` -- User char buffer for calibration board serial number. Returns "N/A" on error. Default NULL.
- `snSize` -- Buffer size for boardSN. Default 0.
- `hardRev` -- User char buffer for calibration board hardware revision. Returns "N/A" on error. Default NULL.
- `revSize` -- Buffer size for hardRev. Default 0.

**Return Values:**
- Normal: calibration board hardware version info (int)
- Error: 255 (causes: channel not calibrated, or site invalid)

**Example:**
```cpp
int logicRev = 0;
char boardSN[255] = {0};
char boardHdRev[255] = {0};
logicRev = qtmue0.GetCalibrationCalBoardInfo(0, boardSN, 255, boardHdRev, 255);
```

### 3.16.8 GetCalibrationSoftRev()

**Signature:**
```cpp
int GetCalibrationSoftRev(
    UINT siteNo,
    char* softRev,
    UINT revSize);
```

**Parameters:**
- `siteNo` -- Site. 0=SITE_1, 1=SITE_2, ...
- `softRev` -- User char buffer for calibration software version. Returns "N/A" if not stored. E.g. `char softRev[255]={0}`.
- `revSize` -- Buffer size (UINT, positive).

**Return Values:**
- `0` -- success
- `-1` -- site invalid, read failed

**Example:**
```cpp
char softRev[20] = {0};
qtmue0.GetCalibrationSoftRev(0, softRev, 20);
```

### 3.16.9 GetCalibrationSlotID()

**Signature:**
```cpp
int GetCalibrationSlotID(UINT siteNo) const;
```

**Parameters:**
- `siteNo` -- Site. 0=SITE_1, 1=SITE_2, ...

**Return Values:**
- Normal: slot ID where board was during calibration (int)
- Error: 0 (causes: channel not calibrated, or site invalid)

**Example:**
```cpp
int slotID = qtmue0.GetCalibrationSlotID(0);
```

---

# Programming Examples (Section 3.17)

## 3.17.1 Measure Time -- Rise Time (Tr)

```cpp
double val[4] = {0.0};
qtmue0.Connect(QTMUe_RELAY_CHA, 500);
qtmue0.SetInSource(QTMUe_SINGLE_SOURCE_A);
qtmue0.Start(QTMUe_MU1, QTMUe_25V, QTMUe_POS, 1.5, QTMUe_FILTER_PASS, 10);
qtmue0.Stop(QTMUe_MU1, QTMUe_25V, QTMUe_POS, 13.5, QTMUe_FILTER_PASS, 10);
qtmue0.Measure(QTMUe_MU1, QTMUe_MEAS_TIME, 1, 3, QTMUe_TRANGE_MS);
for (int i = 0; i < SITENUM; i++) {
    val[i] = qtmue0.GetMeasureResult(i, AVERAGE_RESULT, QTMUe_MU1); // uS
}
qtmue0.Disconnect(QTMUe_RELAY_CHA, 100);
```

## 3.17.2 Measure Time Interval -- TPLH (Dual Source)

```cpp
double val[4] = {0.0};
qtmue0.Connect(QTMUe_RELAY_CHAB, 500);
qtmue0.SetInSource(QTMUe_DUAL_SOURCE_START_A);
qtmue0.Start(QTMUe_MU1, QTMUe_25V, QTMUe_NEG, 2.5, QTMUe_FILTER_PASS, 10);
qtmue0.Stop(QTMUe_MU1, QTMUe_25V, QTMUe_POS, 7.7, QTMUe_FILTER_PASS, 10);
qtmue0.Measure(QTMUe_MU1, QTMUe_MEAS_TIME, 10, 1, QTMUe_TRANGE_US);
for (int i = 0; i < SITENUM; i++) {
    val[i] = qtmue0.GetMeasureResult(i, AVERAGE_RESULT, QTMUe_MU1); // uS
}
qtmue0.Disconnect(QTMUe_RELAY_CHAB, 100);
```

## 3.17.3 Measure Time -- P2 to N3 with Holdoff

```cpp
double val[4] = {0.0};
qtmue0.Connect(QTMUe_RELAY_CHA, 500);
qtmue0.SetInSource(QTMUe_SINGLE_SOURCE_A);
qtmue0.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.5, QTMUe_FILTER_PASS, 10, 0, 1); // HoldoffNum=1
qtmue0.Stop(QTMUe_MU1, QTMUe_10V, QTMUe_NEG, 2.5, QTMUe_FILTER_PASS, 10, 0, 2);  // HoldoffNum=2
qtmue0.Measure(QTMUe_MU1, QTMUe_MEAS_TIME, 10, 1, QTMUe_TRANGE_US);
for (int i = 0; i < SITENUM; i++) {
    val[i] = qtmue0.GetMeasureResult(i, AVERAGE_RESULT, QTMUe_MU1); // uS
}
qtmue0.Disconnect(QTMUe_RELAY_CHA, 100);
```

## 3.17.4 Measure Frequency

```cpp
double val[4] = {0.0};
qtmue0.Connect(QTMUe_RELAY_CHA, 500);
qtmue0.SetInSource(QTMUe_SINGLE_SOURCE_A);
qtmue0.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.0, QTMUe_FILTER_PASS, 10);
qtmue0.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 20, 10, QTMUe_TRANGE_US); // sample 20 cycles
for (int i = 0; i < SITENUM; i++) {
    val[i] = qtmue0.GetMeasureResult(i, AVERAGE_RESULT, QTMUe_MU1); // KHz
}
qtmue0.Disconnect(QTMUe_RELAY_CHA, 100);
```

## 3.17.5 Measure High Duty Cycle

```cpp
double val[4] = {0.0};
qtmue0.Connect(QTMUe_RELAY_CHA, 500);
qtmue0.SetInSource(QTMUe_SINGLE_SOURCE_A);
qtmue0.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.0, QTMUe_FILTER_PASS, 10);
qtmue0.Stop(QTMUe_MU1, QTMUe_10V, QTMUe_NEG, 2.0, QTMUe_FILTER_PASS, 10);
qtmue0.Measure(QTMUe_MU1, QTMUe_MEAS_HIGH_DUTY, 20, 10, QTMUe_TRANGE_MS);
// SampleNum=20 edges; Start=POS, Stop=NEG required; HoldoffNum=0 required
for (int i = 0; i < SITENUM; i++) {
    val[i] = qtmue0.GetMeasureResult(i, AVERAGE_RESULT, QTMUe_MU1); // %
}
qtmue0.Disconnect(QTMUe_RELAY_CHA, 100);
```

## 3.17.6 Event Counting

```cpp
double Tevent[5][SITENUM] = {0.0};
qtmue0.Connect(QTMUe_RELAY_CHA, 500);
qtmue0.SetInSource(QTMUe_SINGLE_SOURCE_A);
qtmue0.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.0, QTMUe_FILTER_PASS, 10);
qtmue0.Stop(QTMUe_MU1, QTMUe_10V, QTMUe_NEG, 2.0, QTMUe_FILTER_PASS, 10);
qtmue0.Measure(QTMUe_MU1, QTMUe_MEAS_EVENT, 5, 10, QTMUe_TRANGE_MS); // 5 events
for (int SITEID = 0; SITEID < SITENUM; SITEID++) {
    for (int i = 0; i < 5; i++) {
        Tevent[i][SITEID] = qtmue0.GetMeasureResult(SITEID, i, QTMUe_MU1);
    }
    // Calculate intervals: t1 = Tevent[1]-Tevent[0], t2 = Tevent[2]-Tevent[1], etc.
}
qtmue0.Disconnect(QTMUe_RELAY_CHA);
```

## 3.17.7 External Trigger (Arm) + Time Measurement

```cpp
double val[4] = {0.0};
qtmue0.Connect(QTMUe_RELAY_CHA, 500);
qtmue0.SetInSource(QTMUe_SINGLE_SOURCE_A);
qtmue0.Start(QTMUe_MU1, QTMUe_25V, QTMUe_POS, 1.5, QTMUe_FILTER_PASS, 10);
qtmue0.Stop(QTMUe_MU1, QTMUe_25V, QTMUe_POS, 7.5, QTMUe_FILTER_PASS, 10);
qtmue0.SetArm(QTMUe_MU1, QTMUe_ARM_SOURCE, QTMUe_EDGE, QTMUe_POS);
qtmue0.Measure(QTMUe_MU1, QTMUe_MEAS_TIME, 1, 100, QTMUe_TRANGE_US); // timeout=100mS
// Apply external Arm signal...
for (int i = 0; i < SITENUM; i++) {
    val[i] = qtmue0.GetMeasureResult(i, AVERAGE_RESULT, QTMUe_MU1); // uS
}
qtmue0.Disconnect(QTMUe_RELAY_CHA, 100);
```

## 3.17.8 Complex Matrix -- 4 Channels, 8 TMUs

```cpp
QTMUe qtmue0("S23_0"); QTMUe qtmue1("S23_1");
QTMUe qtmue2("S23_2"); QTMUe qtmue3("S23_3");

// Connect all CHAB
qtmue0.Connect(QTMUe_RELAY_CHAB); qtmue1.Connect(QTMUe_RELAY_CHAB);
qtmue2.Connect(QTMUe_RELAY_CHAB); qtmue3.Connect(QTMUe_RELAY_CHAB);

// All single source A
qtmue0.SetInSource(QTMUe_SINGLE_SOURCE_A);
qtmue1.SetInSource(QTMUe_SINGLE_SOURCE_A);
qtmue2.SetInSource(QTMUe_SINGLE_SOURCE_A);
qtmue3.SetInSource(QTMUe_SINGLE_SOURCE_A);

// Route CHB to MU2 for all 4 channels
qtmue0.SetMatrix(QTMUe_MU2, QTMUe_CHANNEL_B, QTMUe_CHANNEL_B, QTMUe_ALLSITE);
qtmue1.SetMatrix(QTMUe_MU2, QTMUe_CHANNEL_B, QTMUe_CHANNEL_B, QTMUe_ALLSITE);
qtmue2.SetMatrix(QTMUe_MU2, QTMUe_CHANNEL_B, QTMUe_CHANNEL_B, QTMUe_ALLSITE);
qtmue3.SetMatrix(QTMUe_MU2, QTMUe_CHANNEL_B, QTMUe_CHANNEL_B, QTMUe_ALLSITE);

// Set Start/Stop for MU1 (CHA) and MU2 (CHB) for all 4 channels
// ... (8 pairs of Start/Stop calls)
// Measure all 8 TMUs
// ... (8 Measure calls)
// Read all 8 results
```

## 3.17.9 Per-Site Matrix -- 2 Sites, Different MUs

```cpp
// qtmue0 contains channels 0,2; qtmue1 contains channels 1,3
QTMUe qtmue0("S23_0,S23_2");
QTMUe qtmue1("S23_1,S23_3");

qtmue0.Connect(QTMUe_RELAY_CHA);
qtmue1.Connect(QTMUe_RELAY_CHAB);

// SITE_1 (site 0): 0A->1A on MU1, 0A->1B on MU2
// SITE_2 (site 1): 2A->3A on MU1, 2A->3B on MU2
qtmue0.SetMatrix(QTMUe_MU1, QTMUe_CHANNEL_0A, QTMUe_CHANNEL_1A, 0);
qtmue0.SetMatrix(QTMUe_MU1, QTMUe_CHANNEL_2A, QTMUe_CHANNEL_3A, 1);
qtmue0.SetMatrix(QTMUe_MU2, QTMUe_CHANNEL_0A, QTMUe_CHANNEL_1B, 0);
qtmue0.SetMatrix(QTMUe_MU2, QTMUe_CHANNEL_2A, QTMUe_CHANNEL_3B, 1);

// Start/Stop for both MUs (both use rising edge, 2V, 10V range)
qtmue0.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2, QTMUe_FILTER_PASS, 200);
qtmue0.Stop(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2, QTMUe_FILTER_PASS, 200);
qtmue0.Start(QTMUe_MU2, QTMUe_10V, QTMUe_POS, 2, QTMUe_FILTER_PASS, 200);
qtmue0.Stop(QTMUe_MU2, QTMUe_10V, QTMUe_POS, 2, QTMUe_FILTER_PASS, 200);

qtmue0.Measure(QTMUe_MU1, QTMUe_MEAS_TIME, 1, 3, QTMUe_TRANGE_MS);
qtmue0.Measure(QTMUe_MU2, QTMUe_MEAS_TIME, 1, 3, QTMUe_TRANGE_MS);

double delayTime1 = qtmue0.GetMeasureResult(0, AVERAGE_RESULT, QTMUe_MU1); // SITE_1 MU1
double delayTime2 = qtmue0.GetMeasureResult(0, AVERAGE_RESULT, QTMUe_MU2); // SITE_1 MU2
double delayTime3 = qtmue0.GetMeasureResult(1, AVERAGE_RESULT, QTMUe_MU1); // SITE_2 MU1
double delayTime4 = qtmue0.GetMeasureResult(1, AVERAGE_RESULT, QTMUe_MU2); // SITE_2 MU2
```
