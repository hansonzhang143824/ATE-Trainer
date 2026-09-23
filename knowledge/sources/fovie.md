> 迁移自 auto-memory `STS8300-fovie.md`（2026-08-16） ｜来源 STS8300 编程手册-2.1.15.pdf, Chapter 6.5 (pages 619-668)


# FOVIe -- 四象限电压电流源表 (Standard Source Meter)

FOVIe is the standard four-quadrant voltage/current source meter. Max 8 channels per board. Max output: +/-40V, +/-1A.

---

## 6.5.1 FOVIe() -- Constructor

**Signature:**
```cpp
FOVIe(char* channelList, char* chName = NULL);
```

**Parameters:**
- `channelList` -- Channel binding string. Format: `"S5_0,S5_1"` where "S5" = slot 5, "0,1" = intra-board channel indices. Max 8 channels per board (indices 0-7).
- `chName` -- Custom channel name. Default NULL, system names it `FOVIe_xx`.

**Remarks:** Defines one FOVIe logical channel mapping to physical channels.

**Example:**
```cpp
FOVIe fovie0("S5_0,S11_0,S22_0,S28_0");
FOVIe fovie1("S5_1,S11_1,S22_1,S28_1");
// ... fovie2 through fovie7
STSSetMultiSiteBind(MD_FOVIe, SITE_1, "S5_0-7");
STSSetMultiSiteBind(MD_FOVIe, SITE_2, "S11_0-7");
STSSetMultiSiteBind(MD_FOVIe, SITE_3, "S22_0-7");
STSSetMultiSiteBind(MD_FOVIe, SITE_4, "S28_0-7");
```

---

## 6.5.2 Set() -- Set voltage/current

**Signature:**
```cpp
int Set(
    VIMode viMode,
    double setValue,
    FOVIe_VRNG vRange,
    FOVIe_IRNG iRange,
    FOVIe_OUT_RELAY relayStatus = FOVIe_RELAY_HOLD,
    double risingTime = 0.1);
```

**Parameters:**

- `viMode` -- Operating mode:
  - `FV` -- Constant voltage mode
  - `FI` -- Constant current mode

- `setValue` -- Setpoint value.
  - FV mode: voltage in V, range -40 to 40
  - FI mode: current in A, range -1 to 1

- `vRange` -- Voltage range (enum `FOVIe_VRNG`):
  - `FOVIe_40V`, `FOVIe_20V`, `FOVIe_10V`, `FOVIe_5V`, `FOVIe_2V`, `FOVIe_1V`

- `iRange` -- Current range (enum `FOVIe_IRNG`):
  - `FOVIe_1A`, `FOVIe_100MA`, `FOVIe_10MA`, `FOVIe_1MA`, `FOVIe_100UA`, `FOVIe_10UA`
  - Note: `FOVIe_10UA` can only be used for measurement, NOT for output

- `relayStatus` -- Output relay action (enum `FOVIe_OUT_RELAY`):
  - `FOVIe_RELAY_ON` -- Close output relay
  - `FOVIe_RELAY_OFF` -- Open output relay
  - `FOVIe_RELAY_HOLD` -- Keep previous relay state (default)
  - `FOVIe_RELAY_SENSE_ON` -- Independent measurement mode: SENSE relay ON, FORCE relay OFF (FOVIe acts as standalone voltmeter)

- `risingTime` -- Change time in ms, resolution 0.1ms. Default 0.1ms.
  - <=0.1ms: Normal mode (0.1ms)
  - <=0.2ms: Slow mode (0.2ms)
  - >0.2ms: Auto-enables Capload function for smooth rise/fall, max 65ms

**Remarks:** Sets FOVIe state: mode, setpoint, voltage/current range, output relay, and Capload time.

**Examples:**
```cpp
// Default risingTime = 0.1ms
fovie0.Set(FV, 5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);

// risingTime = 3ms (Capload enabled)
fovie0.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
delay_ms(1);
fovie0.Set(FV, 5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON, 3);
```

---

## 6.5.3 SetSyn() -- Set voltage/current synchronized across sites

**Signature:**
```cpp
int SetSyn(
    VIMode viMode,
    const double* setValue,
    UINT siteSize,
    FOVIe_VRNG vRange,
    FOVIe_IRNG iRange,
    FOVIe_OUT_RELAY relayStatus = FOVIe_RELAY_HOLD,
    double risingTime = 0.1);
```

**Parameters:**

- `viMode` -- Operating mode: `FV` or `FI`
- `setValue` -- Array of setpoint values per site.
  - FV mode: each element in V, range -40 to 40
  - FI mode: each element in A, range -1 to 1
- `siteSize` -- Number of sites for synchronized operation (SITE1 through SITE`siteSize`)
  - `setValue` array length must be >= `siteSize`
  - If `siteSize` < active site count, unset sites keep previous state
  - If `siteSize` > active site count, capped at active count
- `vRange` -- Voltage range (same enums as Set)
- `iRange` -- Current range (same enums as Set)
- `relayStatus` -- Relay action (same enums as Set). NB: parameter name is `enableRelay` in docs but type is `FOVIe_OUT_RELAY`
- `risingTime` -- Change time in ms (same behavior as Set). Default 0.1ms.

**Remarks:** Sets different values for different sites with fully synchronized operation.

**Examples:**
```cpp
// SITE1=3V, SITE2=5V, synchronized, default risingTime
double setValue[2] = {3, 5};
int siteSize = 2;
fovie0.SetSyn(FV, setValue, siteSize, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);

// With risingTime=3ms
fovie0.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
delay_ms(1);
fovie0.SetSyn(FV, setValue, siteSize, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON, 3);
```

---

## 6.5.4 SetClamp() -- Set positive/negative clamp

**Signature:**
```cpp
int SetClamp(
    double percent_PFS,
    double percent_NFS);
```

**Parameters:**
- `percent_PFS` -- Positive clamp as percentage of full-scale, range 10-102%
- `percent_NFS` -- Negative clamp as percentage of full-scale, range 10-102%

**Return Values:**
- `3` -- Both positive and negative clamp changed
- `2` -- Negative clamp changed
- `1` -- Positive clamp changed
- `0` -- Neither changed
- `-1` -- Function call failed

**Remarks:** Clamp settings are mode-dependent. Switching between FV/FI modes clears clamp settings back to 102%. Within the same mode, clamp settings persist.

**Example:**
```cpp
fovie1.Set(FI, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
fovie1.SetClamp(50, 20);  // positive=50%, negative=20%
fovie1.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);  // clamp resets to 102%
fovie1.SetClamp(25, 25);  // re-set
fovie1.Set(FV, 1, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
```

---

## 6.5.5 MeasureVI() -- Configure measurement

**Signature:**
```cpp
int MeasureVI(
    UINT sampleTimes,
    double samplePeriod,
    FOVIe_MI_GAIN miGain = FOVIe_MI_X1,
    FLOATMEASMODE measMode = MEAS_NORMAL,
    UINT T1 = 0,
    UINT T2 = 0,
    UINT T3 = 0,
    UINT T4 = 0);
```

**Parameters:**

- `sampleTimes` -- ADC sample count, range 1-4096. Clamped if out of range.
- `samplePeriod` -- Sampling interval in us. **Min 5us** (not 1us like FPVIe), resolution 1us, range 5-30000. Clamped if out of range.
- `miGain` -- Current measurement gain (enum `FOVIe_MI_GAIN`):
  - `FOVIe_MI_X1` (default), `FOVIe_MI_X10`
  - Note: FOVIe has only X1 and X10 (no X2/X5 like FPVIe)
  - Note: FOVIe has NO mvGain parameter (unlike FPVIe which has both mvGain and miGain)
- `measMode` -- Measurement mode:
  - `MEAS_NORMAL` (default) -- Normal mode, measurement completes after call
  - `MEAS_AWG` -- AWG mode, only sets up config; measurement starts with AWG sync
- `T1, T2, T3, T4` -- AWG measurement start times in us. Resolution 10us. Range: 0 to 600000 (cumulative).
  - **Relative times:** T2 is relative to T1, T3 relative to T2, T4 relative to T3.
  - All default to 0 (single measurement at time 0).

**Remarks:** Configures FOVIe measurement: sample count, interval, current gain, measurement mode, and up to 4 AWG measurement start times.

**Key differences from FPVIe MeasureVI:**
- No `mvGain` parameter (FOVIe has no voltage measurement gain setting)
- Min samplePeriod is 5us (FPVIe is 1us)
- Only `FOVIe_MI_X1` and `FOVIe_MI_X10` for miGain

**Example:**
```cpp
fovie0.MeasureVI(20, 10);  // 20 samples, 10us interval
```

---

## 6.5.6 GetMeasResult() -- Read measurement result

**Signature:**
```cpp
double GetMeasResult(
    UINT siteCount,
    MeasRet retType = MVRET,
    int sampleNumber = AVERAGE_RESULT,
    BYTE triggerNum = 0);
```

**Parameters:**

- `siteCount` -- Site index: 0=Site1, 1=Site2, ...
  - For `NO_SITE` channels, any value works

- `retType` -- Data type to read:
  - `MVRET` (default) -- Read voltage measurement (unit: V)
  - `MIRET` -- Read current measurement (unit: A)

- `sampleNumber` -- Which sample to return:
  - `AVERAGE_RESULT` (default) -- Average value
  - `MAX_RESULT` -- Maximum value
  - `MIN_RESULT` -- Minimum value
  - `TRIG_RESULT` -- Trigger position (which sample point triggered, max 2 triggers)
  - Non-negative N -- Returns the (N+1)th sample value (0 <= N <= sampleTimes-1)

- `triggerNum` -- Trigger count selection (only when `sampleNumber=TRIG_RESULT`):
  - `0` (default) -- First trigger position
  - `1` -- Second trigger position

**Return Values:** Measured voltage (V) or current (A). Returns -3 if no trigger occurred. Returns -5 if measurement mode mismatch.

**Remarks:** Both voltage and current are measured simultaneously on each call. You only need to pick which to read back.

**Examples:**
```cpp
// Average current
fovie0.MeasureVI(20, 10);
for (i = 0; i < SITENUM; i++) {
    adresult[i] = fovie0.GetMeasResult(i, MIRET);
}

// 15th sample voltage (index 14)
adresult[i] = fovie0.GetMeasResult(i, MVRET, 14);

// AWG trigger positions
Trig_Point0[i] = fovie0.GetMeasResult(0, MVRET, TRIG_RESULT, 0);  // first trigger
Trig_Point1[i] = fovie0.GetMeasResult(0, MVRET, TRIG_RESULT, 1);  // second trigger
```

---

## 6.5.7 BlockRead() -- Read measurement data block

**Signature:**
```cpp
int BlockRead(
    UINT siteCount,
    UINT start,
    UINT size,
    double* buffer,
    MeasRet retType = MVRET);
```

**Parameters:**

- `siteCount` -- Site index: 0=Site1, 1=Site2, ...
- `start` -- Starting address of data block, range: 0 to (MeasureVI sampleTimes - 1)
- `size` -- Block size, range: 1 to (MeasureVI sampleTimes - start)
- `buffer` -- User-defined result array. Must have length >= `size`. Recommended: global variable.
- `retType` -- `MVRET` (default) or `MIRET`

**Remarks:** Reads a contiguous block of measurement results.

**Example:**
```cpp
double result[SITENUM][200] = {0.0};
fovie0.MeasureVI(200, 10);
for (i = 0; i < SITENUM; i++) {
    fovie0.BlockRead(i, 0, 200, result[i], MVRET);
}
```

---

## 6.5.8 Pulse() -- Output pulse

**Signature:**
```cpp
int Pulse(
    double pulseValue,
    UINT pulseTime = 300,
    int measStartTime = 0,
    UINT sampleTimes = 10,
    double sampleInterval = 30);
```

**Parameters:**

- `pulseValue` -- Pulse amplitude.
  - FV mode: V, range -40 to 40
  - FI mode: A, range -1 to 1
- `pulseTime` -- Pulse duration in us. Resolution 10us, range 300-40000. Default 300us.
- `measStartTime` -- Measurement start time relative to pulse start in us. Range -60000 to 60000. Default 0.
- `sampleTimes` -- Sample count, range 1-4096. Default 10.
- `sampleInterval` -- Sampling interval in us. Min 5us, resolution 1us. Default 30us.

**Remarks:** Outputs an adjustable-amplitude, adjustable-width voltage or current pulse. Must call `Set()` first. Pulse start and end values equal the Set() setpoint.

**Example:**
```cpp
fovie0.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
fovie0.Pulse(8, 1000, -500, 200, 10);
// 8V pulse, 1000us width, measurement starts 500us before pulse, 200 samples at 10us
```

---

## 6.5.9 AwgLoader() -- Import AWG waveform data

**Signature:**
```cpp
int AwgLoader(
    char* awgName,
    VIMode viMode,
    FOVIe_VRNG vRange,
    FOVIe_IRNG iRange,
    double* awgData,
    UINT awgSize);
```

**Parameters:**

- `awgName` -- AWG waveform name (case-insensitive)
- `viMode` -- `FV` or `FI`
- `vRange` -- Voltage range (same enums as Set)
- `iRange` -- Current range (same enums as Set)
- `awgData` -- Pointer to waveform data array (double)
- `awgSize` -- Waveform data size, range 1-4096

**Remarks:**
- Range info is for data conversion only, does NOT switch hardware range
- Multiple AWG waveforms per channel OK, each must have unique name
- Same-named waveforms: only first `AwgLoader` call is used
- Writing 4096 points takes ~5ms, proportional to size
- Total AWG data per channel per test program must be <= 4096; excess ignored
- Recommended: keep total < 4096 to avoid re-write overhead

**Example:**
```cpp
int sam = 50;
double awg_pattern[100] = {0.0};
STSAWGCreateRampData(&awg_pattern[0], sam, 1, 16.5, 21.5);
fovie0.AwgLoader("Vst", FV, FOVIe_40V, FOVIe_100MA, awg_pattern, sam);
```

---

## 6.5.10 AwgSelect() -- Select AWG waveform for sync operation

**Signature:**
```cpp
int AwgSelect(
    char* awgName,
    UINT startAddr,
    UINT stopAddr,
    int loopBackAddr,
    double awgInterval = 10.0);
```

**Parameters:**

- `awgName` -- AWG waveform name (must match `AwgLoader`)
- `startAddr` -- Waveform start point, range 0 to sam-1
- `stopAddr` -- Waveform end point, range 0 to sam-1
- `loopBackAddr` -- Return point after execution:
  - `< 0`: hold at end position
  - `0 to sam-1`: return to this point after completion
- `awgInterval` -- Data interval time in us. Resolution 1us, range 10-60000. Default 10us.

**Remarks:**
- Selects which AWG waveform to run with start/stop/loop/intervals
- Must call `Set()` before `AwgSelect` with ranges matching `AwgLoader`
- `AwgSelect` alone does NOT produce output -- must use `STSAWGRun()` for sync operation

**Example:**
```cpp
fovie0.AwgLoader("AWG_Vst", FV, FOVIe_40V, FOVIe_100MA, awg_pattern1, sam1);
fovie0.AwgLoader("AWG_Vuvlo", FV, FOVIe_20V, FOVIe_100MA, awg_pattern2, sam2);
fovie0.Set(FV, 16.5, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
fovie0.AwgSelect("AWG_Vst", 0, sam1-1, 0, interval);
STSAWGRun();  // Only AWG_Vst runs
```

---

## 6.5.11 AwgRun() -- Standalone AWG start

**Signature:**
```cpp
int AwgRun(
    char* awgName,
    UINT startAddr,
    UINT stopAddr,
    int loopBackAddr,
    double awgInterval = 10.0,
    BOOL runMode = AWG_SINGLE,
    UINT delayTime_ms = 0);
```

**Parameters:**

- `awgName` -- AWG waveform name (must match `AwgLoader`)
- `startAddr` -- Waveform start point, range 0 to sam-1
- `stopAddr` -- Waveform end point, range 0 to sam-1
- `loopBackAddr` -- Return point after execution:
  - `< 0`: hold at end position
  - `0 to sam-1`: return to this point
- `awgInterval` -- Data interval in us. Resolution 1us, range 10-60000. Default 10us.
- `runMode` -- Run mode:
  - `AWG_SINGLE` (default) -- Run once
  - `AWG_LOOP` -- Loop continuously, stop with `AwgStop()`
- `delayTime_ms` -- Delay in ms after AWG start before subsequent code runs. Range 0-60000.
  - Default (unset): blocks until AWG scan completes
  - **Recommendation: do NOT set this parameter**

**Remarks:**
- Standalone AWG start for one FOVIe channel
- Must call `Set()` before with ranges matching `AwgLoader`
- Does NOT need `AwgSelect` (start/stop/loop/interval set here)
- Cannot sync with other sources -- for sync, use `AwgSelect` + `STSAWGRun`

**Example:**
```cpp
int sam = 830;
double interval = 10;
double awg_pattern[1000] = {0.0};
STSAWGCreateSineData(&awg_pattern[0], sam, 1, 0.66, 3.3, 0);
fovie0.AwgLoader("Sin_AWG", FV, FOVIe_5V, FOVIe_1A, awg_pattern, sam);
fovie0.Set(FV, 0, FOVIe_5V, FOVIe_1A, FOVIe_RELAY_ON);
fovie0.AwgRun("Sin_AWG", 0, sam-1, 0, interval, AWG_LOOP);
```

---

## 6.5.12 AwgStop() -- Stop AWG loop

**Signature:**
```cpp
int AwgStop(void);
```

**Remarks:** Stops cyclic AWG execution for one FOVIe channel.

**Example:**
```cpp
fovie0.AwgRun("Sin_AWG", 0, sam-1, 0, interval, AWG_LOOP);
delay_ms(5);
fovie0.AwgStop();
```

---

## 6.5.13 AwgClear() -- Clear AWG data

**Signature:**
```cpp
int AwgClear(void);
```

**Remarks:** Clears AWG data for this FOVIe channel. Typically called before `AwgLoader`.

**Example:**
```cpp
fovie0.AwgClear();
fovie0.AwgLoader("P1", FV, FOVIe_40V, FOVIe_100MA, awg_pattern1, sam);
```

---

## 6.5.14 SetMeasVTrig() -- Set voltage measurement trigger

**Signature:**
```cpp
int SetMeasVTrig(
    double vTrig,
    TRIG_MODE trigMode = TRIG_FALLING,
    double hysteresisValue = 0.0);
```

**Parameters:**

- `vTrig` -- Trigger voltage in V. Must be within the Set() voltage range of the channel.
- `trigMode` -- Trigger mode:
  - `TRIG_FALLING` (default) -- Falling edge trigger
  - `TRIG_RISING` -- Rising edge trigger
- `hysteresisValue` -- Hysteresis value in V. Must be non-negative. Default 0.
  - Rising edge: triggers when measurement goes below `(vTrig - hysteresisValue)` then above `vTrig`
  - Falling edge: triggers when measurement goes above `(vTrig + hysteresisValue)` then below `vTrig`

**Remarks:**
- The voltage/current range state must be IDENTICAL between `SetMeasVTrig` and `MeasureVI`.
- Do NOT insert any range-changing function calls between them.

**Example:**
```cpp
fovie0.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
fovie1.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
fovie1.SetMeasVTrig(Trig, TRIG_FALLING);
STSEnableAWG(&fovie0);
STSEnableMeas(&fovie0, &fovie1);
STSAWGRun();
```

---

## 6.5.15 SetMeasITrig() -- Set current measurement trigger

**Signature:**
```cpp
int SetMeasITrig(
    double iTrig,
    TRIG_MODE trigMode = TRIG_FALLING,
    double hysteresisValue = 0.0);
```

**Parameters:**

- `iTrig` -- Trigger current in A. Must be within the Set() current range of the channel.
- `trigMode` -- `TRIG_FALLING` (default) or `TRIG_RISING`
- `hysteresisValue` -- Hysteresis value in A. Must be non-negative. Default 0.

**Remarks:**
- The voltage/current range and measurement gain state must be IDENTICAL between `SetMeasITrig` and `MeasureVI`.
- Do NOT insert any range/gain-changing function calls between them.

---

## 6.5.16 ContactCheck() -- Contact detection

**Signature:**
```cpp
int ContactCheck(FOVIe_CONTACTMODE checkMode);
```

**Parameters:**

- `checkMode` -- Contact check mode (enum `FOVIe_CONTACTMODE`):
  - `FOVIe_HIGH_SIDE` -- Check high-side circuit connection
  - Note: FOVIe only supports HIGH_SIDE (unlike FPVIe which also has LOW_SIDE and ALL_SIDE)

**Remarks:**
- After detection, VI source restores to pre-detection state
- Supports Group operations

**Example:**
```cpp
fovie0.ContactCheck(FOVIe_HIGH_SIDE);
```

---

## 6.5.17 GetContactCheckResult() -- Read contact check result

**Signature:**
```cpp
int GetContactCheckResult(UINT siteCount);
```

**Parameters:**
- `siteCount` -- Site index: 0=Site1, 1=Site2, ...

**Return Values:**
- `< 0`: Site invalid
- `0`: Contact check PASS
- `1`: Contact check FAIL

**Example:**
```cpp
int result = fovie0.GetContactCheckResult(0);
```

---

## 6.5.18 SetAlarmMask() -- Set alarm mask

**Signature:**
```cpp
void SetAlarmMask(
    UINT siteCount,
    bool status = true);
```

**Parameters:**
- `siteCount` -- Site index: 0=Site1, 1=Site2, ...
- `status` -- `true` (default) to mask alarms, `false` to output alarms

**Remarks:** Alarm mask is re-initialized in `InitBeforeTestFlow()`.

**Example:**
```cpp
fovie0.SetAlarmMask(0);  // Mask SITE_1 alarms
fovie0.Set(FV, 5, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);  // Over-range alarm suppressed
```

---

## 6.5.19 GetAlarmMask() -- Read alarm mask state

**Signature:**
```cpp
bool GetAlarmMask(UINT siteCount);
```

**Parameters:**
- `siteCount` -- Site index: 0=Site1, 1=Site2, ...

**Return Values:** `true` = masked, `false` = not masked.

**Example:**
```cpp
bool status = fovie0.GetAlarmMask(0);
```

---

## 6.5.20 Board Information Functions

### 6.5.20.1 GetBoardSN()

**Signature:**
```cpp
int GetBoardSN(UINT siteCount, char* boardSN, UINT snSize);
```
- `boardSN` -- User buffer (e.g., `char boardSN[255]={0}`), returns empty on invalid
- `snSize` -- Buffer size
- Returns: 0 = success, non-zero = failure

### 6.5.20.2 GetBoardHDRev()

**Signature:**
```cpp
int GetBoardHDRev(UINT siteCount, char* hardRev, UINT revSize);
```
- `hardRev` -- User buffer, returns "N/A" if not stored
- Returns: 0 = success, non-zero = failure

---

## 6.5.21 Calibration Information Functions

### 6.5.21.1 GetCalibrationTime()

**Signature:**
```cpp
SYSTEMTIME GetCalibrationTime(UINT siteCount) const;
```
- Returns: Calibration date, or 1970-1-18 0:0:0 on error

### 6.5.21.2 GetCalibrationTemperature()

**Signature:**
```cpp
double GetCalibrationTemperature(UINT siteCount) const;
```
- Returns: Temperature at calibration, or 0 on error

### 6.5.21.3 GetCalibrationHumidity()

**Signature:**
```cpp
double GetCalibrationHumidity(UINT siteCount) const;
```
- Returns: Humidity at calibration, or 0 on error

### 6.5.21.4 GetCalibrationResult()

**Signature:**
```cpp
CAL_RESULT GetCalibrationResult(UINT siteCount) const;
```
- Return values: `CAL_PASS`, `CAL_FAIL`, `STS_NO_RESULT_RECORD`

### 6.5.21.5 GetCalibrationLogicRev()

**Signature:**
```cpp
int GetCalibrationLogicRev(UINT siteCount) const;
```
- Returns: Logic version number, or 255 on error

### 6.5.21.6 GetCalibrationMeter()

**Signature:**
```cpp
CAL_METER GetCalibrationMeter(
    UINT siteCount,
    char* meterSN = NULL,
    UINT snSize = 0);
```
- Return meter types: `STS_KEITHLEY2000`, `STS_AGILENT34401`, `STS_AGILENT3458A`, `STS_NO_METER_RECORD`
- `meterSN` -- Buffer for meter serial number (default NULL = don't read)

### 6.5.21.7 GetCalibrationCalBoardInfo()

**Signature:**
```cpp
int GetCalibrationCalBoardInfo(
    UINT siteCount,
    char* boardSN = NULL,
    UINT snSize = 0,
    char* boardHdRev = NULL,
    UINT revSize = 0);
```
- Returns: Calibration board logic version, or 255 on error
- `boardSN` -- Buffer for board serial number (default NULL)
- `boardHdRev` -- Buffer for board hardware revision (default NULL)

### 6.5.21.8 GetCalibrationSoftRev()

**Signature:**
```cpp
int GetCalibrationSoftRev(
    UINT siteCount,
    char* softRev,
    UINT revSize);
```
- Returns: 0 = success, non-zero = failure

### 6.5.21.9 GetCalibrationSlotID()

**Signature:**
```cpp
int GetCalibrationSlotID(UINT siteCount) const;
```
- Returns: Slot ID at calibration, or 0 on error

---

## Summary: Key FOVIe Enums and Ranges

| Category | Enums |
|---|---|
| **V Range** | `FOVIe_40V`, `FOVIe_20V`, `FOVIe_10V`, `FOVIe_5V`, `FOVIe_2V`, `FOVIe_1V` |
| **I Range** | `FOVIe_1A`, `FOVIe_100MA`, `FOVIe_10MA`, `FOVIe_1MA`, `FOVIe_100UA`, `FOVIe_10UA` (measure only) |
| **Relay** | `FOVIe_RELAY_ON`, `FOVIe_RELAY_OFF`, `FOVIe_RELAY_HOLD`, `FOVIe_RELAY_SENSE_ON` |
| **MI Gain** | `FOVIe_MI_X1`, `FOVIe_MI_X10` |
| **Contact** | `FOVIe_HIGH_SIDE` (only; no LOW_SIDE or ALL_SIDE) |
| **Max V** | +/-40V |
| **Max I** | +/-1A |
| **Channels/board** | 8 |

---

## Key Differences: FPVIe vs FOVIe

| Feature | FPVIe | FOVIe |
|---|---|---|
| Max Voltage | +/-100V | +/-40V |
| Max Current | +/-10A | +/-1A |
| Channels/board | 2 | 8 |
| MeasureVI min interval | 1us | 5us |
| MV Gain | MV_X1, X2, X5, X10 | N/A (no mvGain param) |
| MI Gain | MI_X1, X2, X5, X10 | MI_X1, X10 only |
| Contact modes | HIGH_SIDE, LOW_SIDE, ALL_SIDE | HIGH_SIDE only |
| SiteBindModify | Yes | Not in FOVIe (use STSSetMultiSiteBind) |
| Set() default risingTime | 0.2ms | 0.1ms |
| SetClamp clearing trigger | FV/FI mode switch only | FV/FI mode switch only |
| Capload max | 65ms | 65ms |
| AWG max size | 4096 | 4096 |
