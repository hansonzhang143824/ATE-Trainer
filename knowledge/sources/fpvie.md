> 迁移自 auto-memory `STS8300-fpvie.md`（2026-08-16） ｜来源 STS8300 编程手册-2.1.15.pdf, Chapter 6.4 (pages 565-618)


# FPVIe -- 四象限功率VI源表 (High-Current Source Meter)

FPVIe is the high-current four-quadrant power VI source meter. Max 2 channels per board. Max output: +/-100V, +/-10A.

---

## 6.4.1 FPVIe() -- Constructor

**Signature:**
```cpp
FPVIe(char* channelList, char* chName = NULL);
```

**Parameters:**
- `channelList` -- Channel binding string. Format: `"S4_0,S4_1"` where "S4" = slot 4, "0,1" = intra-board channel indices. Max 2 channels per board (indices 0-1).
- `chName` -- Custom channel name. Default NULL, system names it `FPVIe_xx`.

**Remarks:** Defines one FPVIe logical channel mapping to physical channels.

**Example:**
```cpp
FPVIe fpvie0("S4_0,S12_0,S21_0,S29_0");
FPVIe fpvie1("S4_1,S12_1,S21_1,S29_1");
STSSetMultiSiteBind(MD_FPVIe, SITE_1, "S4_0,S4_1");
STSSetMultiSiteBind(MD_FPVIe, SITE_2, "S12_0,S12_1");
STSSetMultiSiteBind(MD_FPVIe, SITE_3, "S21_0,S21_1");
STSSetMultiSiteBind(MD_FPVIe, SITE_4, "S29_0,S29_1");
```

---

## 6.4.2 Set() -- Set voltage/current

**Signature:**
```cpp
int Set(
    VIMode viMode,
    double setValue,
    FPVIe_VRNG vRange,
    FPVIe_IRNG iRange,
    FPVIe_OUT_RELAY relayStatus = FPVIe_RELAY_HOLD,
    double risingTime = 0.2);
```

**Parameters:**

- `viMode` -- Operating mode:
  - `FV` -- Constant voltage mode
  - `FI` -- Constant current mode

- `setValue` -- Setpoint value.
  - FV mode: voltage in V, range -100 to 100
  - FI mode: current in A, range -10 to 10

- `vRange` -- Voltage range (enum `FPVIe_VRNG`):
  - `FPVIe_100V`, `FPVIe_40V`, `FPVIe_20V`, `FPVIe_10V`, `FPVIe_5V`, `FPVIe_2V`, `FPVIe_1V`, `FPVIe_100MV`
  - Note: `FPVIe_100MV` can only be used for measurement, NOT for output

- `iRange` -- Current range (enum `FPVIe_IRNG`):
  - `FPVIe_10A`, `FPVIe_2A`, `FPVIe_1A`, `FPVIe_100MA`, `FPVIe_10MA`, `FPVIe_1MA`, `FPVIe_100UA`, `FPVIe_10UA`

- `relayStatus` -- Output relay action (enum `FPVIe_OUT_RELAY`):
  - `FPVIe_RELAY_ON` -- Close output relay
  - `FPVIe_RELAY_OFF` -- Open output relay
  - `FPVIe_RELAY_HOLD` -- Keep previous relay state (default)
  - `FPVIe_RELAY_SENSE_ON` -- Independent measurement mode: SENSE relay ON, FORCE relay OFF (FPVIe acts as standalone voltmeter)

- `risingTime` -- Integration/rise time in ms, resolution 0.1ms. Default 0.2ms.
  - <=0.05ms: Fast mode (0.05ms)
  - <=0.1ms: Normal mode (0.1ms)
  - <=0.2ms: Slow mode (0.2ms)
  - >0.2ms: Auto-enables Capload function for smooth rise/fall, max 65ms

**Remarks:** Sets FPVIe state: mode, setpoint, voltage/current range, output relay, and Capload time.

**Examples:**
```cpp
// Default risingTime = 0.2ms
fpvie0.Set(FV, 5, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);

// risingTime = 3ms (Capload enabled)
fpvie0.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
delay_ms(1);
fpvie0.Set(FV, 5, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON, 3);

// High-current example (>=1A)
fpvie0.Set(FI, 2.5, FPVIe_5V, FPVIe_10A, FPVIe_RELAY_ON);
```

---

## 6.4.3 SetSyn() -- Set voltage/current synchronized across sites

**Signature:**
```cpp
int SetSyn(
    VIMode viMode,
    const double* setValue,
    UINT siteSize,
    FPVIe_VRNG vRange,
    FPVIe_IRNG iRange,
    FPVIe_OUT_RELAY relayStatus = FPVIe_RELAY_HOLD,
    double risingTime = 0.2);
```

**Parameters:**

- `viMode` -- Operating mode: `FV` or `FI`
- `setValue` -- Array of setpoint values per site.
  - FV mode: each element in V, range -100 to 100
  - FI mode: each element in A, range -10 to 10
- `siteSize` -- Number of sites for synchronized operation (SITE1 through SITE`siteSize`)
  - `setValue` array length must be >= `siteSize`
  - If `siteSize` < active site count, unset sites keep previous state
  - If `siteSize` > active site count, capped at active count
- `vRange` -- Voltage range (same enums as Set)
- `iRange` -- Current range (same enums as Set)
- `relayStatus` -- Relay action (same enums as Set)
- `risingTime` -- Rise time in ms (same behavior as Set)

**Remarks:** Sets different values for different sites with fully synchronized operation.

**Examples:**
```cpp
// SITE1=3V, SITE2=5V, synchronized
double setValue[2] = {3, 5};
int siteSize = 2;
fpvie0.SetSyn(FV, setValue, siteSize, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);

// With risingTime=3ms
fpvie0.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
delay_ms(1);
fpvie0.SetSyn(FV, setValue, siteSize, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON, 3);
```

---

## 6.4.4 SetClamp() -- Set positive/negative clamp

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
fpvie1.Set(FI, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
fpvie1.SetClamp(50, 20);  // positive clamp=50%, negative clamp=20% of full range
fpvie1.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);  // clamp resets to 102%
fpvie1.SetClamp(25, 25);  // re-set after mode switch
fpvie1.Set(FV, 1, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
```

---

## 6.4.5 MeasureVI() -- Configure measurement

**Signature:**
```cpp
int MeasureVI(
    UINT sampleTimes,
    double samplePeriod,
    FPVIe_MV_GAIN mvGain = FPVIe_MV_X1,
    FPVIe_MI_GAIN miGain = FPVIe_MI_X1,
    FLOATMEASMODE measMode = MEAS_NORMAL,
    UINT T1 = 0,
    UINT T2 = 0,
    UINT T3 = 0,
    UINT T4 = 0);
```

**Parameters:**

- `sampleTimes` -- ADC sample count, range 1-4096. Clamped if out of range.
- `samplePeriod` -- Sampling interval in us. Range 1-30000, resolution 1us. Clamped if out of range.
- `mvGain` -- Voltage measurement gain (enum `FPVIe_MV_GAIN`):
  - `FPVIe_MV_X1` (default), `FPVIe_MV_X2`, `FPVIe_MV_X5`, `FPVIe_MV_X10`
- `miGain` -- Current measurement gain (enum `FPVIe_MI_GAIN`):
  - `FPVIe_MI_X1` (default), `FPVIe_MI_X2`, `FPVIe_MI_X5`, `FPVIe_MI_X10`
- `measMode` -- Measurement mode:
  - `MEAS_NORMAL` (default) -- Normal mode, measurement completes after call
  - `MEAS_AWG` -- AWG mode, only sets up config; measurement starts with AWG sync
- `T1, T2, T3, T4` -- AWG measurement start times in us. Resolution 10us. Range: 0 to 600000 (cumulative).
  - **Relative times:** T2 is relative to T1, T3 relative to T2, T4 relative to T3.
  - All default to 0 (single measurement at time 0).

**Remarks:** Configures FPVIe measurement: sample count, interval, voltage gain, current gain, measurement mode, and up to 4 AWG measurement start times.

**Example:**
```cpp
fpvie0.MeasureVI(20, 5);  // 20 samples, 5us interval, default MEAS_NORMAL
```

---

## 6.4.6 GetMeasResult() -- Read measurement result

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

**Remarks:** Both voltage and current are measured simultaneously on each call. You only need to pick which to read back (`MVRET` or `MIRET`).

**Examples:**
```cpp
// Average current
fpvie0.MeasureVI(20, 5);
for (i = 0; i < SITENUM; i++) {
    adresult[i] = fpvie0.GetMeasResult(i, MIRET);
}

// 15th sample voltage (index 14)
adresult[i] = fpvie0.GetMeasResult(i, MVRET, 14);

// AWG trigger positions
Trig_Point0[i] = fpvie0.GetMeasResult(0, MVRET, TRIG_RESULT, 0);  // first trigger
Trig_Point1[i] = fpvie0.GetMeasResult(0, MVRET, TRIG_RESULT, 1);  // second trigger
```

---

## 6.4.7 BlockRead() -- Read measurement data block

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
fpvie0.MeasureVI(200, 10);
for (i = 0; i < SITENUM; i++) {
    fpvie0.BlockRead(i, 0, 200, result[i], MVRET);
}
```

---

## 6.4.8 Pulse() -- Output pulse

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
  - FV mode: V, range -100 to 100
  - FI mode: A, range -10 to 10
- `pulseTime` -- Pulse duration in us. Resolution 10us, range 300-40000. Default 300us.
- `measStartTime` -- Measurement start time relative to pulse start in us. Range -60000 to 60000. Default 0.
- `sampleTimes` -- Sample count, range 1-4096. Default 10.
- `sampleInterval` -- Sampling interval in us. Min 1us, resolution 1us. Default 30us.

**Remarks:** Outputs an adjustable-amplitude, adjustable-width voltage or current pulse. Must call `Set()` first to configure range, etc. Pulse start and end values equal the Set() setpoint.

**Example:**
```cpp
fpvie0.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
fpvie0.Pulse(8, 1000, -500, 200, 10);
// 8V pulse, 1000us width, measurement starts 500us before pulse, 200 samples at 10us
```

---

## 6.4.9 AwgLoader() -- Import AWG waveform data

**Signature:**
```cpp
int AwgLoader(
    char* awgName,
    VIMode viMode,
    FPVIe_VRNG vRange,
    FPVIe_IRNG iRange,
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
fpvie0.AwgLoader("Vst", FV, FPVIe_40V, FPVIe_100MA, awg_pattern, sam);
// 16.5V to 21.5V ramp

// Sine wave: 100Hz, Vpp=4V, DC=10V
int sam2 = 1000;
double awg_pattern2[2000] = {0.0};
STSAWGCreateSineData(&awg_pattern2[0], sam2, 1, 4, 10, 0);
fpvie0.AwgLoader("Sine", FV, FPVIe_10V, FPVIe_1MA, awg_pattern2, sam2);
```

---

## 6.4.10 AwgSelect() -- Select AWG waveform for sync operation

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
- For standalone (non-sync) AWG, use `AwgRun()` instead

**Example:**
```cpp
fpvie0.AwgLoader("AWG_Vst", FV, FPVIe_40V, FPVIe_100MA, awg_pattern1, sam1);
fpvie0.AwgLoader("AWG_Vuvlo", FV, FPVIe_20V, FPVIe_100MA, awg_pattern2, sam2);
fpvie0.Set(FV, 16.5, FPVIe_40V, FPVIe_100MA, FPVIe_RELAY_ON);
fpvie0.AwgSelect("AWG_Vst", 0, sam1-1, 0, interval);
STSAWGRun();  // Only AWG_Vst runs
```

---

## 6.4.11 AwgRun() -- Standalone AWG start

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
- Standalone AWG start for one FPVIe channel
- Must call `Set()` before with ranges matching `AwgLoader`
- Does NOT need `AwgSelect` (start/stop/loop/interval are set here)
- Cannot sync with other sources -- for sync, use `AwgSelect` + `STSAWGRun`

**Example:**
```cpp
// 120Hz sine wave, 0.33V amplitude, 3.3V DC offset, loop mode
int sam = 830;
double interval = 10;
double awg_pattern[1000] = {0.0};
STSAWGCreateSineData(&awg_pattern[0], sam, 1, 0.66, 3.3, 0);
fpvie0.AwgLoader("Sin_AWG", FV, FPVIe_5V, FPVIe_1A, awg_pattern, sam);
fpvie0.Set(FV, 0, FPVIe_5V, FPVIe_1A, FPVIe_RELAY_ON);
fpvie0.AwgRun("Sin_AWG", 0, sam-1, 0, interval, AWG_LOOP);
```

---

## 6.4.12 AwgStop() -- Stop AWG loop

**Signature:**
```cpp
int AwgStop(void);
```

**Remarks:** Stops cyclic AWG execution for one FPVIe channel.

**Example:**
```cpp
fpvie0.AwgRun("Sin_AWG", 0, sam-1, 0, interval, AWG_LOOP);
delay_ms(5);  // Run for 5ms
fpvie0.AwgStop();
```

---

## 6.4.13 AwgClear() -- Clear AWG data

**Signature:**
```cpp
int AwgClear(void);
```

**Remarks:** Clears AWG data for this FPVIe channel. Typically called before `AwgLoader`.

**Example:**
```cpp
fpvie0.AwgClear();
fpvie0.AwgLoader("P1", FV, FPVIe_40V, FPVIe_100MA, awg_pattern1, sam);
```

---

## 6.4.14 SetMeasVTrig() -- Set voltage measurement trigger

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
- The voltage/current range and measurement gain state must be IDENTICAL between `SetMeasVTrig` and `MeasureVI`.
- Do NOT insert any range/gain-changing function calls between them.

**Example:**
```cpp
fpvie0.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
fpvie1.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
fpvie1.SetMeasVTrig(Trig, TRIG_FALLING);  // 2V falling edge trigger
STSEnableAWG(&fpvie0);
STSEnableMeas(&fpvie0, &fpvie1);
STSAWGRun();
```

---

## 6.4.15 SetMeasITrig() -- Set current measurement trigger

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
  - Same rising/falling logic as `SetMeasVTrig` but for current

**Remarks:**
- The voltage/current range and measurement gain state must be IDENTICAL between `SetMeasITrig` and `MeasureVI`.
- Do NOT insert any range/gain-changing function calls between them.

**Example:**
```cpp
fpvie0.AwgLoader("Vst", FV, FPVIe_40V, FPVIe_100MA, awg_pattern, sam);
fpvie0.Set(FV, 16.5, FPVIe_40V, FPVIe_100MA, FPVIe_RELAY_ON);
fpvie0.AwgSelect("Vst", 0, sam-1, sam-1, interval);
fpvie0.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
fpvie0.SetMeasITrig(Trig, TRIG_RISING);  // 200uA rising edge
STSEnableAWG(&fpvie0);
STSEnableMeas(&fpvie0);
STSAWGRun();
// WRONG: inserting Set() between MeasureVI and SetMeasITrig
// fpvie0.Set(FV, 16.5, FPVIe_40V, FPVIe_10MA, FPVIe_RELAY_ON);  // WILL CAUSE ERROR
```

---

## 6.4.16 ContactCheck() -- Contact detection

**Signature:**
```cpp
int ContactCheck(FPVIe_CONTACTMODE checkMode);
```

**Parameters:**

- `checkMode` -- Contact check mode (enum `FPVIe_CONTACTMODE`):
  - `FPVIe_HIGH_SIDE` -- Check high-side circuit connection
  - `FPVIe_LOW_SIDE` -- Check low-side circuit connection
  - `FPVIe_ALL_SIDE` -- Check both high and low side

**Remarks:**
- After detection, VI source restores to pre-detection state
- Supports Group operations

**Example:**
```cpp
fpvie0.Set(FV, 15, FPVIe_20V, FPVIe_10MA, FPVIe_RELAY_ON);
fpvie0.ContactCheck(FPVIe_HIGH_SIDE);
```

---

## 6.4.17 GetContactCheckResult() -- Read contact check result

**Signature:**
```cpp
int GetContactCheckResult(UINT siteCount);
```

**Parameters:**
- `siteCount` -- Site index: 0=Site1, 1=Site2, ...

**Return Values:**
- `< 0`: Site invalid
- `0`: Contact check PASS
- For `FPVIe_HIGH_SIDE` / `FPVIe_LOW_SIDE`: >0 means FAIL
- For `FPVIe_ALL_SIDE`:
  - `1`: High-side FAIL, low-side PASS
  - `2`: High-side PASS, low-side FAIL
  - `3`: Both FAIL

**Pass criterion:** Contact resistance < 100 ohm = PASS. Error approx +/-20 ohm.

**Example:**
```cpp
fpvie0.Set(FV, 0, FPVIe_10V, FPVIe_1MA, FPVIe_RELAY_ON);
fpvie0.ContactCheck(FPVIe_HIGH_SIDE);
int result[SITENUM] = {0};
for (iSite = 0; iSite < SITENUM; iSite++) {
    result[iSite] = fpvie0.GetContactCheckResult(iSite);
}
```

---

## 6.4.18 SetAlarmMask() -- Set alarm mask

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
fpvie0.SetAlarmMask(0);  // Mask SITE_1 alarms
fpvie0.Set(FV, 5, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);  // Over-range alarm suppressed
```

---

## 6.4.19 GetAlarmMask() -- Read alarm mask state

**Signature:**
```cpp
bool GetAlarmMask(UINT siteCount);
```

**Parameters:**
- `siteCount` -- Site index: 0=Site1, 1=Site2, ...

**Return Values:** `true` = masked, `false` = not masked.

**Example:**
```cpp
bool status = fpvie0.GetAlarmMask(0);
```

---

## 6.4.20 SiteBindModify() -- Reconfigure site binding

**Signature:**
```cpp
int SiteBindModify(char* modifySiteList);
```

**Parameters:**
- `modifySiteList` -- Reconfiguration string, format: `"origSite1:targetSite1,origSite2:targetSite2,..."`
  - Orig and target separated by `:`, multiple groups separated by `,`
  - Site numbers: 0=SITE_1 to 250=SITE_251
  - Example: `"0:2,1:3"` = SITE_1 to SITE_3, SITE_2 to SITE_4

**Return Values:** 0 = success, non-zero = failure.

**Remarks:**
- Unaffected channels keep original site binding
- Reconfiguration is NOT affected by site validity -- even if SITE_1 is invalid, physical channels still get moved to target site
- Cannot reconfigure NO_SITE channels
- Same site cannot be modified twice in one call
- Different sites cannot be modified to the same target

**Example:**
```cpp
FPVIe fpvie0("S4_0,S12_0");
STSSetMultiSiteBind(MD_FPVIe, SITE_1, "S4_0,S4_1");
STSSetMultiSiteBind(MD_FPVIe, SITE_2, "S12_0,S12_1");
fpvie0.SiteBindModify("0:2,1:3");  // SITE_1->SITE_3, SITE_2->SITE_4
```

---

## 6.4.21 Board Information Functions

### 6.4.21.1 GetBoardSN()

**Signature:**
```cpp
int GetBoardSN(UINT siteCount, char* boardSN, UINT snSize);
```
- `boardSN` -- User buffer (e.g., `char boardSN[255]={0}`), returns empty on invalid
- `snSize` -- Buffer size
- Returns: 0 = success, non-zero = failure

### 6.4.21.2 GetBoardHDRev()

**Signature:**
```cpp
int GetBoardHDRev(UINT siteCount, char* hardRev, UINT revSize);
```
- `hardRev` -- User buffer, returns "N/A" if not stored
- Returns: 0 = success, non-zero = failure

---

## 6.4.22 Calibration Information Functions

### 6.4.22.1 GetCalibrationTime()

**Signature:**
```cpp
SYSTEMTIME GetCalibrationTime(UINT siteCount) const;
```
- Returns: Calibration date, or 1970-1-18 0:0:0 on error

### 6.4.22.2 GetCalibrationTemperature()

**Signature:**
```cpp
double GetCalibrationTemperature(UINT siteCount) const;
```
- Returns: Temperature at calibration, or 0 on error

### 6.4.22.3 GetCalibrationHumidity()

**Signature:**
```cpp
double GetCalibrationHumidity(UINT siteCount) const;
```
- Returns: Humidity at calibration, or 0 on error

### 6.4.22.4 GetCalibrationResult()

**Signature:**
```cpp
CAL_RESULT GetCalibrationResult(UINT siteCount) const;
```
- Return values: `CAL_PASS`, `CAL_FAIL`, `STS_NO_RESULT_RECORD`

### 6.4.22.5 GetCalibrationLogicRev()

**Signature:**
```cpp
int GetCalibrationLogicRev(UINT siteCount) const;
```
- Returns: Logic version number, or 255 on error

### 6.4.22.6 GetCalibrationMeter()

**Signature:**
```cpp
CAL_METER GetCalibrationMeter(
    UINT siteCount,
    char* meterSN = NULL,
    UINT snSize = 0);
```
- Return meter types: `STS_KEITHLEY2000`, `STS_AGILENT34401`, `STS_AGILENT3458A`, `STS_NO_METER_RECORD`
- `meterSN` -- Buffer for meter serial number (default NULL = don't read)

### 6.4.22.7 GetCalibrationCalBoardInfo()

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
- `boardSN` -- Buffer for board serial number (default NULL = don't read)
- `boardHdRev` -- Buffer for board hardware revision (default NULL = don't read)

### 6.4.22.8 GetCalibrationSoftRev()

**Signature:**
```cpp
int GetCalibrationSoftRev(
    UINT siteCount,
    char* softRev,
    UINT revSize);
```
- Returns: 0 = success, non-zero = failure

### 6.4.22.9 GetCalibrationSlotID()

**Signature:**
```cpp
int GetCalibrationSlotID(UINT siteCount) const;
```
- Returns: Slot ID at calibration, or 0 on error

---

## Summary: Key FPVIe Enums and Ranges

| Category | Enums |
|---|---|
| **V Range** | `FPVIe_100V`, `FPVIe_40V`, `FPVIe_20V`, `FPVIe_10V`, `FPVIe_5V`, `FPVIe_2V`, `FPVIe_1V`, `FPVIe_100MV` (measure only) |
| **I Range** | `FPVIe_10A`, `FPVIe_2A`, `FPVIe_1A`, `FPVIe_100MA`, `FPVIe_10MA`, `FPVIe_1MA`, `FPVIe_100UA`, `FPVIe_10UA` |
| **Relay** | `FPVIe_RELAY_ON`, `FPVIe_RELAY_OFF`, `FPVIe_RELAY_HOLD`, `FPVIe_RELAY_SENSE_ON` |
| **MV Gain** | `FPVIe_MV_X1`, `FPVIe_MV_X2`, `FPVIe_MV_X5`, `FPVIe_MV_X10` |
| **MI Gain** | `FPVIe_MI_X1`, `FPVIe_MI_X2`, `FPVIe_MI_X5`, `FPVIe_MI_X10` |
| **Contact** | `FPVIe_HIGH_SIDE`, `FPVIe_LOW_SIDE`, `FPVIe_ALL_SIDE` |
| **Max V** | +/-100V |
| **Max I** | +/-10A |
| **Channels/board** | 2 |
