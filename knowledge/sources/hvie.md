> 迁移自 auto-memory `STS8300-hvie.md`（2026-08-16）


# HVIe — High Voltage Source Meter

## 1. HVIe() — Define HVIe channel
**Signature:** `HVIe(char* channelList, char* chName = NULL);`
**Parameters:**
- `channelList` [char*]: HVIe binding channel string. Format: `"S3_0"` where `S3` = slot number 3 (S = Slot), `0` = intra-board index. One HVIe board has at most 1 channel, so intra-board index max is 0.
- `chName` [char*]: Custom channel name. Optional, defaults to NULL; system names the channel `HVIe_xx`.
**Return:** None (constructor).
**Remarks:** Defines one HVIe channel and specifies its actual channel info (slot number + intra-board index).
**Example:**
```cpp
// 4 HVIe boards at Slot3, Slot13, Slot20, Slot30, 4-site parallel
HVIe hvie0("S3_0,S13_0,S20_0,S30_0");
// Site binding:
STSSetMultiSiteBind(MD_HVIe, SITE_1, "S3_0");
STSSetMultiSiteBind(MD_HVIe, SITE_2, "S13_0");
STSSetMultiSiteBind(MD_HVIe, SITE_3, "S20_0");
STSSetMultiSiteBind(MD_HVIe, SITE_4, "S30_0");
```

## 2. Set() — Configure HVIe output state
**Signature:** `int Set(VIMode viMode, double setValue, HVIe_VRNG vRange, HVIe_IRNG iRange, HVIe_OUT_RELAY relayStatus = HVIe_RELAY_HOLD, double risingTime = 0.3);`
**Parameters:**
- `viMode` [VIMode]: Operating mode. Values: `FV` (constant voltage), `FI` (constant current).
- `setValue` [double]: Setpoint value. FV mode: voltage in V, range -10~1000 or -1000~10. FI mode: current in A, range -0.01~0.01.
- `vRange` [HVIe_VRNG]: Voltage range. Values:
  - `HVIe_N10P1000V` — Positive polarity, negative max -10V, positive max +1000V
  - `HVIe_P10N1000V` — Negative polarity, positive max +10V, negative max -1000V
  - `HVIe_N10P500V` — Positive polarity, negative max -10V, positive max +500V
  - `HVIe_P10N500V` — Negative polarity, positive max +10V, negative max -500V
  - `HVIe_N10P200V` — Positive polarity, negative max -10V, positive max +200V
  - `HVIe_P10N200V` — Negative polarity, positive max +10V, negative max -200V
  - `HVIe_N10P100V` — Positive polarity, negative max -10V, positive max +100V
  - `HVIe_P10N100V` — Negative polarity, positive max +10V, negative max -100V
  - `HVIe_N10P10V` — Positive polarity, negative max -10V, positive max +10V
  - `HVIe_P10N10V` — Negative polarity, positive max +10V, negative max -10V
  **Note:** `HVIe_N10P*` ranges have positive output polarity, cannot deliver full power at FV 0~-10V. `HVIe_P10N*` ranges have negative output polarity, cannot deliver full power at FV 0~10V.
- `iRange` [HVIe_IRNG]: Current range. Values:
  - `HVIe_10MA`
  - `HVIe_1MA`
  - `HVIe_100UA`
  - `HVIe_10UA` (measurement only, cannot source)
  - `HVIe_1UA` (measurement only, cannot source)
- `relayStatus` [HVIe_OUT_RELAY]: Output relay action. Values:
  - `HVIe_RELAY_ON` — Close default output relay
  - `HVIe_RELAY_FANOUT_ON` — Close FANOUT output relay
  - `HVIe_RELAY_ALL_ON` — Close all output relays
  - `HVIe_RELAY_OFF` — Open all output relays
  - `HVIe_RELAY_HOLD` — Keep previous relay state (default)
- `risingTime` [double]: Rise/fall time in ms. Resolution 0.1ms. Default 0.3ms.
  - <=0.1ms: Fastest mode (0.1ms)
  - <=0.2ms: Fast mode (0.2ms)
  - <=0.3ms: Normal mode (0.3ms, default)
  - <=0.4ms: Slow mode (0.4ms)
  - >0.4ms: Capload mode enabled, smoother edges, max 65ms
**Return:** Not documented (int return).
**Remarks:** Sets HVIe state including operating mode, voltage/current setpoint, ranges, relay state, and Capload time.
**Example:**
```cpp
// Set hvie0 to FV mode, output 650V, 1000V range, 1UA measure range, relay ON, 1ms rise
hvie0.Set(FV, 650, HVIe_N10P1000V, HVIe_1UA, HVIe_RELAY_ON, 1);
```

## 3. SetSyn() — Synchronous multi-site set
**Signature:** `int SetSyn(VIMode viMode, const double* setValue, UINT siteSize, HVIe_VRNG vRange, HVIe_IRNG iRange, HVIe_OUT_RELAY relayStatus = HVIe_RELAY_HOLD, double risingTime = 0.3);`
**Parameters:**
- `viMode` [VIMode]: Operating mode. Values: `FV`, `FI`.
- `setValue` [const double*]: Array of setpoint values per site. FV: volts; FI: amps.
- `siteSize` [UINT]: Number of sites for sync operation. If 4, sites SITE1~SITE4.
  **Warnings:**
  - `setValue` array length must be > `siteSize` or undefined behavior.
  - If `siteSize` < active site count, unset sites keep prior state.
  - If `siteSize` > active site count, clamped to active site count.
- `vRange` [HVIe_VRNG]: Voltage range. Same enum as `Set()`.
- `iRange` [HVIe_IRNG]: Current range. Same enum as `Set()`.
- `relayStatus` [HVIe_OUT_RELAY]: Relay action. Same enum as `Set()`. Default `HVIe_RELAY_HOLD`.
- `risingTime` [double]: Rise/fall time in ms. Same behavior as `Set()`. Default 0.3ms.
**Return:** Not documented (int return).
**Remarks:** Sets different voltage/current values for each site, with fully synchronous execution across sites.
**Example:**
```cpp
// SITE1=30V, SITE2=50V, synchronous output, default risingTime
double setValue[2] = {30, 50};
int siteSize = 2;
hvie0.SetSyn(FV, setValue, siteSize, HVIe_N10P100V, HVIe_1MA, HVIe_RELAY_ON);

// With explicit risingTime in Normal mode
hvie0.Set(FV, 0, HVIe_N10P100V, HVIe_1MA, HVIe_RELAY_ON);
delay_ms(1);
hvie0.SetSyn(FV, setValue, siteSize, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON, 0.3);
```

## 4. SetClamp() — Set output clamp limits
**Signature:** `int SetClamp(double percent_PFS, double percent_NFS);`
**Parameters:**
- `percent_PFS` [double]: Positive clamp as percentage of positive full scale. Range: 10~102 (%).
- `percent_NFS` [double]: Negative clamp as percentage of negative full scale. Range: 10~102 (%).
**Return:**
- `3` — Both positive and negative clamp changed
- `2` — Negative clamp changed
- `1` — Positive clamp changed
- `0` — Neither clamp changed
- `-1` — Function call failed
**Remarks:**
- Clamp settings are mode-dependent. Switching FV/FI clears clamp to 102%.
- Switching voltage range polarity also resets clamp to 102%.
- Staying in same FV/FI mode preserves clamp settings.
- Must call `Set()` before `SetClamp()` to establish the target mode/range.
**Example:**
```cpp
// Clamp example with FI->FV mode switch
hvie0.Set(FI, 0, HVIe_P10N1000V, HVIe_1MA, HVIe_RELAY_ON);
hvie0.SetClamp(50, 20);  // positive clamp 50%, negative clamp 20% of 1000V full scale
hvie0.Set(FI, -100e-6, HVIe_P10N1000V, HVIe_1MA, HVIe_RELAY_ON);
hvie0.MeasureVI(30, 20);
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON);  // FI->FV: clamp resets to 102%
hvie0.SetClamp(80, 50);  // re-set clamps
hvie0.Set(FV, 100, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON);

// Clamp example staying in FV mode, changing current range
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_10MA, HVIe_RELAY_ON);
hvie0.SetClamp(80, 50);  // 80% of HVIe_10MA, 50% of HVIe_10MA
hvie0.Set(FV, 600, HVIe_N10P1000V, HVIe_10MA, HVIe_RELAY_ON);
delay_ms(10);
hvie0.Set(FV, 600, HVIe_N10P1000V, HVIe_1UA, HVIe_RELAY_ON);  // clamp stays (80,50) now on 1UA range
delay_ms(10);
hvie0.MeasureVI(100, 20);
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1UA, HVIe_RELAY_ON);
delay_ms(2);
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_10MA, HVIe_RELAY_ON);
hvie0.SetClamp(100, 100);  // restore clamps to 100%
delay_ms(10);
```

## 5. MeasureVI() — Configure measurement
**Signature:** `int MeasureVI(UINT sampleTimes, double samplePeriod, HVIe_MI_GAIN miGain = HVIe_MI_X1, FLOATMEASMODE measMode = MEAS_NORMAL, UINT T1 = 0, UINT T2 = 0, UINT T3 = 0, UINT T4 = 0);`
**Parameters:**
- `sampleTimes` [UINT]: Number of ADC samples. Range 1~8192. Clamped if out of range.
- `samplePeriod` [double]: Interval between samples in us. Min 5us, resolution 1us. Range 5~30000. Clamped if out of range.
- `miGain` [HVIe_MI_GAIN]: Current measurement gain. Values:
  - `HVIe_MI_X1` (default)
  - `HVIe_MI_X10`
- `measMode` [FLOATMEASMODE]: Measurement mode. Values:
  - `MEAS_NORMAL` — Execute measurement immediately (default)
  - `MEAS_AWG` — Configure only; measurement starts when AWG runs
- `T1, T2, T3, T4` [UINT]: AWG mode measurement start times in us. Resolution 10us. Range: 0~(T1+T2+T3+T4)~600000. Up to 4 measurements per AWG run.
  **Note:** These are relative times. T2 is relative to T1, T3 relative to T2, T4 relative to T3.
**Return:** Not documented (int return).
**Remarks:** Configures measurement count, interval, current gain, mode, and up to 4 AWG measurement start times. Voltage and current are measured simultaneously; user chooses which to read back.
**Example:**
```cpp
// Normal mode: 20 samples at 10us interval
hvie0.MeasureVI(20, 10);
```

## 6. GetMeasResult() — Get single measurement result
**Signature:** `double GetMeasResult(UINT siteCount, MeasRet retType = MVRET, int sampleNumber = AVERAGE_RESULT, BYTE triggerNum = 0);`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc. If channel is `NO_SITE`, any value is acceptable.
- `retType` [MeasRet]: Data type to read back. Values:
  - `MVRET` — Voltage measurement data (V) (default)
  - `MIRET` — Current measurement data (A)
- `sampleNumber` [int]: Sample selection. Values:
  - `AVERAGE_RESULT` — Average value (default)
  - `MAX_RESULT` — Maximum value
  - `MIN_RESULT` — Minimum value
  - `TRIG_RESULT` — Trigger position (sample index where transition occurred, up to 2 triggers)
  - Non-negative `N` — Returns the (N+1)th sample value (0 <= N <= sampleTimes-1)
- `triggerNum` [BYTE]: Trigger index. Only valid when `sampleNumber = TRIG_RESULT`. 0 = first trigger (default), 1 = second trigger.
**Return:**
- Normal: voltage (V) for `MVRET`, current (A) for `MIRET`
- `-3` — No trigger occurred (when `sampleNumber = TRIG_RESULT`)
- `-5` — Measurement mode mismatch with readback mode
**Remarks:** Voltage and current are measured simultaneously per sample; user selects which to read. When `TRIG_RESULT` with no trigger, returns -3.
**Example:**
```cpp
// Output -500uA, measure voltage, average of 100 samples
hvie0.SetClamp(90, 90);
hvie0.Set(FI, -500e-6, HVIe_P10N1000V, HVIe_1MA, HVIe_RELAY_ON);
hvie0.MeasureVI(100, 30);
for (int siteID = 0; siteID < 4; siteID++) {
    adresult[siteID] = hvie0.GetMeasResult(siteID);  // defaults to MVRET, average
    param->SetTestResult(siteID, 0, adresult[siteID]);
}
hvie0.Set(FI, 0, HVIe_P10N1000V, HVIe_1MA, HVIe_RELAY_OFF);

// Output 600V, read all 100 individual current samples
double adresult[100][SITENUM] = {0};
hvie0.Set(FV, 600, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON);
delay_ms(10);
hvie0.MeasureVI(100, 20);
for (int siteID = 0; siteID < SITENUM; siteID++) {
    for (int i = 0; i < 100; i++) {
        adresult[i][siteID] = hvie0.GetMeasResult(siteID, i);  // returns MVRET by default
    }
}
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_OFF);
delay_ms(1);
```

## 7. BlockRead() — Read block of measurement results
**Signature:** `int BlockRead(UINT siteCount, UINT start, UINT size, double* buffer, MeasRet retType = MVRET);`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
- `start` [UINT]: Block start address (0-based). Range: 0 to (sampleTimes - 1) from `MeasureVI`.
- `size` [UINT]: Block size. Range: 1 to (sampleTimes - start).
- `buffer` [double*]: User-defined result array. Must have length >= size. Recommended as global variable.
- `retType` [MeasRet]: Data type. `MVRET` (voltage, default) or `MIRET` (current).
**Return:** Not documented explicitly (int return).
**Remarks:** Reads a contiguous block of measurement results. Block start and size are user-defined.
**Example:**
```cpp
double result[SITENUM][200] = {0.0};
hvie0.MeasureVI(200, 10);
for (i = 0; i < SITENUM; i++) {
    hvie0.BlockRead(i, 0, 200, result[i]);
}
```

## 8. Pulse() — Output a voltage/current pulse
**Signature:** `int Pulse(double pulseValue, UINT pulseTime = 300, int measStartTime = 0, UINT sampleTimes = 10, double sampleInterval = 30);`
**Parameters:**
- `pulseValue` [double]: Pulse amplitude. FV: volts; FI: amps. Same range as `Set()`.
- `pulseTime` [UINT]: Pulse width in us. Resolution 10us. Range: 300~40000. Default 300us.
- `measStartTime` [int]: Measurement start time in us (relative to pulse start). Range: -60000~60000. Default 0.
- `sampleTimes` [UINT]: Number of samples. Range 1~8192. Default 10.
- `sampleInterval` [UINT]: Sample interval in us. Min 5us, resolution 1us. Default 30us.
**Return:** Not documented (int return).
**Remarks:** Outputs a voltage or current pulse with adjustable amplitude and width. Must call `Set()` before `Pulse()` to configure range, etc. Pulse starts and ends at the `Set()` value.
**Example:**
```cpp
// Start at FV=0, 8V pulse for 1ms, 200 samples at 10us, measurement starts 500us before pulse
hvie0.Set(FV, 0, HVIe_N10P10V, HVIe_1MA, HVIe_RELAY_ON);
hvie0.Pulse(8, 1000, -500, 200, 10);
```

## 9. AwgLoader() — Load AWG waveform data
**Signature:** `int AwgLoader(char* awgName, VIMode viMode, HVIe_VRNG vRange, HVIe_IRNG iRange, double* awgData, UINT awgSize);`
**Parameters:**
- `awgName` [char*]: AWG waveform name. Case-insensitive.
- `viMode` [VIMode]: Operating mode. `FV` or `FI`.
- `vRange` [HVIe_VRNG]: Voltage range. Same enum as `Set()`.
- `iRange` [HVIe_IRNG]: Current range. Same enum as `Set()`.
- `awgData` [double*]: Pointer to AWG waveform data array.
- `awgSize` [UINT]: Waveform data size. Range: 1~8192.
**Return:** Not documented (int return).
**Remarks:**
- Range info is used only for data conversion, not range switching.
- Multiple AWG waveforms can be loaded per channel; each must have a unique name. Duplicate names keep only the first.
- Data is written to RAM; writing 8192 points takes ~10ms, proportional to size.
- Total AWG data per channel per test program must be <= 8192 points. Excess data is discarded.
- If total <= 8192, duplicate waveforms are not re-loaded (only first `AwgLoader` call consumes time).
- If total > 8192, data is re-written each time, increasing test time.
**Example:**
```cpp
// Ramp from 16.5V to 21.5V, step 0.1V
int sam = 50;
int interval = 200;  // us
double awg_pattern[100] = {0.0};
STSAWGCreateRampData(&awg_pattern[0], sam, 1, 16.5, 21.5);
hvie0.AwgLoader("Vst", FV, HVIe_N10P100V, HVIe_1MA, awg_pattern, sam);

// 100Hz sine, 2V amplitude (4Vpp), 10V DC offset
int sam = 1000;
int interval = 10;  // us
double awg_pattern[2000] = {0.0};
STSAWGCreateSineData(&awg_pattern[0], sam, 1, 4, 10, 0);
hvie0.AwgLoader("Sine", FV, HVIe_N10P100V, HVIe_1MA, awg_pattern, sam);
```

## 10. AwgSelect() — Select AWG waveform for synchronized run
**Signature:** `int AwgSelect(char* awgName, UINT startAddr, UINT stopAddr, int loopBackAddr, double awgInterval = 10.0);`
**Parameters:**
- `awgName` [char*]: AWG waveform name (must match `AwgLoader` name).
- `startAddr` [UINT]: Start point. Range: 0 to sam-1.
- `stopAddr` [UINT]: Stop point. Range: 0 to sam-1.
- `loopBackAddr` [int]: Loop-back point. If < 0, stays at end position. If 0 to sam-1, returns to that point after execution.
- `awgInterval` [double]: Data interval time in us. Resolution 1us. Range: 10~60000. Default 10us.
**Return:** Not documented (int return).
**Remarks:**
- Must call `Set()` before `AwgSelect()` with matching range and mode.
- `AwgSelect()` does NOT output waveforms; only `STSAWGRun()` triggers AWG output.
- Used with synchronized functions (`STSAWGRun`, `STSEnableAWG`, `STSEnableMeas`).
**Example:**
```cpp
// Load two waveforms, select and run only "AWG_Vst"
double interval = 200;
int sam1 = 1000, sam2 = 500;
double awg_pattern1[1000] = {0.0}, awg_pattern2[500] = {0.0};
STSAWGCreateRampData(&awg_pattern1[0], sam1, 1, 16.5, 21.5);
STSAWGCreateRampData(&awg_pattern2[0], sam2, 1, 16.5, 10.5);
hvie0.AwgLoader("AWG_Vst", FV, HVIe_N10P100V, HVIe_1MA, awg_pattern1, sam1);
hvie0.AwgLoader("AWG_Vuvlo", FV, HVIe_N10P100V, HVIe_1MA, awg_pattern2, sam2);
// Set() must match the AwgLoader range/mode
hvie0.Set(FV, 16.5, HVIe_N10P100V, HVIe_1MA, HVIe_RELAY_ON);
hvie0.AwgSelect("AWG_Vst", 0, sam1 - 1, 0, interval);
// ...
STSAWGRun();  // AWG synchronous start
```

## 11. AwgRun() — Start AWG on a single channel (standalone)
**Signature:** `int AwgRun(char* awgName, UINT startAddr, UINT stopAddr, int loopBackAddr, double awgInterval = 10.0, BOOL runMode = AWG_SINGLE, UINT delayTime_ms = 0);`
**Parameters:**
- `awgName` [char*]: AWG waveform name (must match `AwgLoader` name).
- `startAddr` [UINT]: Start point. Range: 0 to sam-1.
- `stopAddr` [UINT]: Stop point. Range: 0 to sam-1.
- `loopBackAddr` [int]: Loop-back point. If < 0, stays at end; if 0 to sam-1, returns to that point.
- `awgInterval` [double]: Data interval in us. Resolution 1us. Range: 10~60000. Default 10us.
- `runMode` [BOOL]: Run mode. Values:
  - `AWG_SINGLE` — Run once (default)
  - `AWG_LOOP` — Loop continuously (stop with `AwgStop()`)
- `delayTime_ms` [UINT]: Delay in ms before allowing subsequent operations. Range: 0~60000. Default = AWG scan time (blocks until AWG completes). Recommendation: do NOT set this parameter.
**Return:** Not documented (int return).
**Remarks:**
- Standalone AWG start for a single channel.
- Must call `Set()` before with matching range/mode as `AwgLoader`.
- Does NOT need `AwgSelect()`; start/stop/loop-back are set directly.
- Cannot sync with other sources; use `AwgSelect()` + `STSAWGRun()` for synchronized measurement.
**Example:**
```cpp
// 200Hz sine, 100Vpp, 150V DC offset, run for 20ms in loop mode
double sam = 500;
double interval = 10;
double awg_pattern[1000] = {0.0};
STSAWGCreateSineData(&awg_pattern[0], sam, 1, 100, 150, 0);
hvie0.AwgLoader("Sin_AWG", FV, HVIe_N10P1000V, HVIe_1MA, awg_pattern, sam);
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON, 0.305);
delay_ms(1);
hvie0.Set(FV, 150, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON, 0.305);
delay_ms(10);
hvie0.AwgRun("Sin_AWG", 0, (sam - 1), (sam - 1), interval, AWG_LOOP);
delay_ms(20);  // waveform runs for 20ms
hvie0.AwgStop();
delay_ms(1);
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON, 0.305);
delay_ms(1);
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_OFF, 0.305);
```

## 12. AwgStop() — Stop AWG loop
**Signature:** `int AwgStop(void);`
**Parameters:** None.
**Return:** Not documented (int return).
**Remarks:** Stops the AWG loop mode on a specific HVIe channel.
**Example:**
```cpp
// Generate a 5ms-period sine, loop for 15ms, then stop
double sam = 500;
double interval = 10;
double awg_pattern[1000] = {0.0};
STSAWGCreateSineData(&awg_pattern[0], sam, 1, 120, 180, 0);
hvie0.AwgLoader("Sin_AWG", FV, HVIe_N10P1000V, HVIe_1MA, awg_pattern, sam);
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON, 0.35);
delay_ms(20);
hvie0.Set(FV, 180, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON, 0.35);
delay_ms(10);
hvie0.AwgRun("Sin_AWG", 0, (sam - 1), 0, interval, AWG_LOOP);
delay_ms(15);  // run for 15ms
hvie0.AwgStop();
delay_ms(1);
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON, 0.35);
delay_ms(1);
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_OFF, 0.35);
```

## 13. AwgClear() — Clear AWG data
**Signature:** `int AwgClear(void);`
**Parameters:** None.
**Return:** Not documented (int return).
**Remarks:** Typically called before `AwgLoader()` to clear the HVIe channel's AWG data.
**Example:**
```cpp
hvie0.AwgClear();
hvie0.AwgLoader("P1", FV, HVIe_N10P100V, HVIe_1MA, awg_pattern1, sam);
```

## 14. SetMeasVTrig() — Set voltage measurement trigger
**Signature:** `int SetMeasVTrig(double vTrig, TRIG_MODE trigMode = TRIG_FALLING, double hysteresisValue = 0.0);`
**Parameters:**
- `vTrig` [double]: Trigger voltage threshold in V. Must be compatible with the voltage range set by `Set()`.
- `trigMode` [TRIG_MODE]: Trigger mode. Values:
  - `TRIG_FALLING` — Falling edge trigger (default)
  - `TRIG_RISING` — Rising edge trigger
- `hysteresisValue` [double]: Hysteresis voltage in V. Must be >= 0. Default 0.
  - Rising edge: triggers when value goes below (vTrig - hysteresisValue) then above vTrig.
  - Falling edge: triggers when value goes above (vTrig + hysteresisValue) then below vTrig.
**Return:** Not documented (int return).
**Remarks:**
- The voltage/current range state at `SetMeasVTrig()` and `MeasureVI()` must be identical.
- Do NOT insert any range-changing `Set()` calls between them.
**Example:**
```cpp
// Correct: SetMeasVTrig before MeasureVI, same range state
hvie1.Set(FI, 0, HVIe_N10P100V, HVIe_1MA, HVIe_RELAY_ON);
double Trig = 2;  // 2V trigger
// ... load AWG, AwgSelect ...
hvie1.SetMeasVTrig(Trig, TRIG_FALLING);
hvie0.MeasureVI(sam, interval, HVIe_MI_X1, MEAS_AWG);
hvie1.MeasureVI(sam, interval, MEAS_AWG);
STSEnableAWG(&hvie0);
STSEnableMeas(&hvie0, &hvie1);
STSAWGRun();

// WRONG: Set() between SetMeasVTrig and MeasureVI changes range
hvie1.SetMeasVTrig(Trig, TRIG_FALLING);
hvie1.Set(FI, 0, HVIe_N10P10V, HVIe_1MA, HVIe_RELAY_ON);  // range changed! will cause error
hvie0.MeasureVI(sam, interval, HVIe_MI_X1, MEAS_AWG);
hvie1.MeasureVI(sam, interval, MEAS_AWG);
```

## 15. SetMeasITrig() — Set current measurement trigger
**Signature:** `int SetMeasITrig(double iTrig, TRIG_MODE trigMode = TRIG_FALLING, double hysteresisValue = 0.0);`
**Parameters:**
- `iTrig` [double]: Trigger current threshold in A. Must be compatible with the current range set by `Set()`.
- `trigMode` [TRIG_MODE]: Trigger mode. Values:
  - `TRIG_FALLING` — Falling edge trigger (default)
  - `TRIG_RISING` — Rising edge trigger
- `hysteresisValue` [double]: Hysteresis current in A. Must be >= 0. Default 0.
  - Rising edge: triggers when value goes below (iTrig - hysteresisValue) then above iTrig.
  - Falling edge: triggers when value goes above (iTrig + hysteresisValue) then below iTrig.
**Return:** Not documented (int return).
**Remarks:**
- The voltage/current range AND measurement gain state at `SetMeasITrig()` and `MeasureVI()` must be identical.
- Do NOT insert any range-changing or gain-changing calls between them.
**Example:**
```cpp
// Correct
double Trig = 200e-6;  // 200uA trigger
hvie0.Set(FV, 16.5, HVIe_N10P100V, HVIe_1MA, HVIe_RELAY_ON);
hvie0.AwgSelect("Vst", 0, sam - 1, sam - 1, interval);
hvie0.MeasureVI(sam, interval, HVIe_MI_X1, MEAS_AWG);
hvie0.SetMeasITrig(Trig, TRIG_RISING);
STSEnableAWG(&hvie0);
STSEnableMeas(&hvie0);
STSAWGRun();

// WRONG: Set() inserted between MeasureVI and SetMeasITrig changes range
hvie0.MeasureVI(sam, interval, HVIe_MI_X1, MEAS_AWG);
hvie0.Set(FV, 16.5, HVIe_N10P100V, HVIe_1MA, HVIe_RELAY_ON);  // range change causes error!
hvie0.SetMeasITrig(Trig, TRIG_RISING);
```

## 16. SetAlarmMask() — Mask alarm output for a site
**Signature:** `void SetAlarmMask(UINT siteCount, bool status = true);`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
- `status` [bool]: `true` = mask (suppress) alarm info for this site (default). `false` = output alarm info.
**Return:** None (void).
**Remarks:** Alarm mask set by this function is re-initialized in `InitBeforeTestFlow()`.
**Example:**
```cpp
hvie0.SetAlarmMask(0);  // suppress SITE_1 alarm info
// No over-range alarm even though 105V exceeds 100V range
hvie0.Set(FV, 105, HVIe_N10P100V, HVIe_1MA, HVIe_RELAY_ON);
```

## 17. GetAlarmMask() — Get alarm mask status for a site
**Signature:** `bool GetAlarmMask(UINT siteCount);`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
**Return:** `true` = alarm masked for this site; `false` = alarm output enabled.
**Example:**
```cpp
bool status = hvie0.GetAlarmMask(0);  // get alarm status of SITE_1
```

## 18. GetBoardSN() — Get board serial number
**Signature:** `int GetBoardSN(UINT siteCount, char* boardSN, UINT snSize);`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
- `boardSN` [char*]: User-defined buffer for serial number. Returns empty string if not stored or invalid site.
- `snSize` [UINT]: Size of `boardSN` buffer.
**Return:** `0` = success; non-zero = failure.
**Example:**
```cpp
char boardSN[255] = {0};
hvie0.GetBoardSN(0, boardSN, 255);
```

## 19. GetBoardHDRev() — Get board hardware revision
**Signature:** `int GetBoardHDRev(UINT siteCount, char* hardRev, UINT revSize);`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
- `hardRev` [char*]: User-defined buffer for hardware revision. Returns "N/A" if not stored.
- `revSize` [UINT]: Size of `hardRev` buffer.
**Return:** `0` = success; non-zero = failure.
**Example:**
```cpp
char hardRev[255] = {0};
hvie0.GetBoardHDRev(0, hardRev, 255);
```

## 20. GetCalibrationTime() — Get calibration date/time
**Signature:** `SYSTEMTIME GetCalibrationTime(UINT siteCount) const;`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
**Return:** `SYSTEMTIME` struct with calibration date. Returns 1970-1-1 8:0:0 if abnormal (uncalibrated or invalid site).
**Example:**
```cpp
SYSTEMTIME calDate;
calDate = hvie0.GetCalibrationTime(0);
```

## 21. GetCalibrationTemperature() — Get calibration temperature
**Signature:** `double GetCalibrationTemperature(UINT siteCount) const;`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
**Return:** Calibration temperature. Returns 0 if abnormal (uncalibrated or invalid site).
**Example:**
```cpp
double calTemperature = 0.0;
calTemperature = hvie0.GetCalibrationTemperature(0);
```

## 22. GetCalibrationHumidity() — Get calibration humidity
**Signature:** `double GetCalibrationHumidity(UINT siteCount) const;`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
**Return:** Calibration humidity. Returns 0 if abnormal (uncalibrated or invalid site).
**Example:**
```cpp
double calHumidity = 0.0;
calHumidity = hvie0.GetCalibrationHumidity(0);
```

## 23. GetCalibrationResult() — Get calibration result
**Signature:** `CAL_RESULT GetCalibrationResult(UINT siteCount) const;`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
**Return:** Enum values:
- `CAL_PASS` — Calibration passed
- `CAL_FAIL` — Calibration failed
- `STS_NO_RESULT_RECORD` — Abnormal (uncalibrated or invalid site)
**Example:**
```cpp
CAL_RESULT calResult;
calResult = hvie0.GetCalibrationResult(0);
```

## 24. GetCalibrationLogicRev() — Get calibration logic revision
**Signature:** `int GetCalibrationLogicRev(UINT siteCount) const;`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
**Return:** Logic revision number. Returns 255 if abnormal (uncalibrated or invalid site).
**Example:**
```cpp
int calLogicRev = 0;
calLogicRev = hvie0.GetCalibrationLogicRev(0);
```

## 25. GetCalibrationMeter() — Get calibration meter info
**Signature:** `CAL_METER GetCalibrationMeter(UINT siteCount, char* meterSN = NULL, UINT snSize = 0);`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
- `meterSN` [char*]: User-defined buffer for meter serial number. Returns "N/A" if abnormal. Default NULL (don't read SN).
- `snSize` [UINT]: Size of `meterSN` buffer. Default 0.
**Return:** Meter type enum:
- `STS_KEITHLEY2000` — Keithley 2000
- `STS_AGILENT34401` — Agilent 34401
- `STS_AGILENT3458A` — Agilent 3458A
- `STS_NO_METER_RECORD` — Abnormal (uncalibrated or invalid site)
**Example:**
```cpp
CAL_METER calMeterType;
char calMeterSN[255] = {0};
calMeterType = hvie0.GetCalibrationMeter(0, calMeterSN, 255);
```

## 26. GetCalibrationCalBoardInfo() — Get calibration board info
**Signature:** `int GetCalibrationCalBoardInfo(UINT siteCount, char* boardSN = NULL, UINT snSize = 0, char* boardHdRev = NULL, UINT revSize = 0);`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
- `boardSN` [char*]: Buffer for calibration board serial number. Returns "N/A" if abnormal. Default NULL.
- `snSize` [UINT]: Size of `boardSN` buffer. Default 0.
- `boardHdRev` [char*]: Buffer for calibration board hardware revision. Returns "N/A" if abnormal. Default NULL.
- `revSize` [UINT]: Size of `boardHdRev` buffer. Default 0.
**Return:** Logic revision of calibration board. Returns 255 if abnormal (uncalibrated or invalid site).
**Example:**
```cpp
int logicRev = 0;
char boardSN[255] = {0};
char boardHdRev[255] = {0};
logicRev = hvie0.GetCalibrationCalBoardInfo(0, boardSN, 255, boardHdRev, 255);
```

## 27. GetCalibrationSoftRev() — Get calibration software revision
**Signature:** `int GetCalibrationSoftRev(UINT siteCount, char* softRev, UINT revSize);`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
- `softRev` [char*]: User-defined buffer for software version. Returns "N/A" if abnormal.
- `revSize` [UINT]: Size of `softRev` buffer.
**Return:** `0` = success; non-zero = failure (uncalibrated or invalid site).
**Example:**
```cpp
char softRev[255] = {0};
hvie0.GetCalibrationSoftRev(0, softRev, 255);
```

## 28. GetCalibrationSlotID() — Get calibration slot ID
**Signature:** `int GetCalibrationSlotID(UINT siteCount) const;`
**Parameters:**
- `siteCount` [UINT]: Site selector. 0 = Site1, 1 = Site2, etc.
**Return:** Slot ID where the board was during calibration. Returns 0 if abnormal (uncalibrated or invalid site).
**Example:**
```cpp
int slotID = hvie0.GetCalibrationSlotID(0);
```

---

## Enum Reference Summary

### VIMode — Operating mode
| Value | Description |
|-------|-------------|
| `FV` | Constant voltage mode |
| `FI` | Constant current mode |

### HVIe_VRNG — Voltage range
| Value | Polarity | Negative max | Positive max |
|-------|----------|-------------|-------------|
| `HVIe_N10P1000V` | Positive | -10V | +1000V |
| `HVIe_P10N1000V` | Negative | -1000V | +10V |
| `HVIe_N10P500V` | Positive | -10V | +500V |
| `HVIe_P10N500V` | Negative | -500V | +10V |
| `HVIe_N10P200V` | Positive | -10V | +200V |
| `HVIe_P10N200V` | Negative | -200V | +10V |
| `HVIe_N10P100V` | Positive | -10V | +100V |
| `HVIe_P10N100V` | Negative | -100V | +10V |
| `HVIe_N10P10V` | Positive | -10V | +10V |
| `HVIe_P10N10V` | Negative | -10V | +10V |

**Note:** `HVIe_N10P*` cannot deliver full power at FV 0~-10V. `HVIe_P10N*` cannot deliver full power at FV 0~10V.

### HVIe_IRNG — Current range
| Value | Can Source | Can Measure |
|-------|-----------|-------------|
| `HVIe_10MA` | Yes | Yes |
| `HVIe_1MA` | Yes | Yes |
| `HVIe_100UA` | Yes | Yes |
| `HVIe_10UA` | No | Yes |
| `HVIe_1UA` | No | Yes |

### HVIe_OUT_RELAY — Output relay action
| Value | Description |
|-------|-------------|
| `HVIe_RELAY_ON` | Close default output relay |
| `HVIe_RELAY_FANOUT_ON` | Close FANOUT output relay |
| `HVIe_RELAY_ALL_ON` | Close all output relays |
| `HVIe_RELAY_OFF` | Open all output relays |
| `HVIe_RELAY_HOLD` | Keep previous relay state |

### HVIe_MI_GAIN — Current measurement gain
| Value | Description |
|-------|-------------|
| `HVIe_MI_X1` | 1x gain (default) |
| `HVIe_MI_X10` | 10x gain |

### MeasRet — Measurement return data type
| Value | Description |
|-------|-------------|
| `MVRET` | Voltage measurement data (V) |
| `MIRET` | Current measurement data (A) |

### FLOATMEASMODE — Measurement mode
| Value | Description |
|-------|-------------|
| `MEAS_NORMAL` | Normal mode: measure immediately |
| `MEAS_AWG` | AWG mode: configure only, run with AWG |

### TRIG_MODE — Trigger mode
| Value | Description |
|-------|-------------|
| `TRIG_FALLING` | Falling edge trigger (default) |
| `TRIG_RISING` | Rising edge trigger |

### CAL_RESULT — Calibration result
| Value | Description |
|-------|-------------|
| `CAL_PASS` | Calibration passed |
| `CAL_FAIL` | Calibration failed |
| `STS_NO_RESULT_RECORD` | No calibration record (abnormal) |

### CAL_METER — Calibration meter type
| Value | Description |
|-------|-------------|
| `STS_KEITHLEY2000` | Keithley 2000 |
| `STS_AGILENT34401` | Agilent 34401 |
| `STS_AGILENT3458A` | Agilent 3458A |
| `STS_NO_METER_RECORD` | No meter record (abnormal) |

### GetMeasResult sampleNumber types
| Value | Description |
|-------|-------------|
| `AVERAGE_RESULT` | Average of all samples (default) |
| `MAX_RESULT` | Maximum sample value |
| `MIN_RESULT` | Minimum sample value |
| `TRIG_RESULT` | Sample index where trigger occurred |
| Non-negative N | The (N+1)th individual sample |

### AwgRun runMode
| Value | Description |
|-------|-------------|
| `AWG_SINGLE` | Run waveform once (default) |
| `AWG_LOOP` | Loop waveform continuously |

---

## Programming Examples (from manual)

### IDSS Test (6.6.20.1)
```cpp
double adresult[4] = {0.0};
int SITEID = 0;
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON);
delay_ms(1);
hvie0.Set(FV, 800, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON);
delay_ms(10);  // wait for 800V to settle
hvie0.Set(FV, 800, HVIe_N10P1000V, HVIe_1UA, HVIe_RELAY_ON);  // switch to 1UA for small current measurement
delay_ms(10);
hvie0.MeasureVI(100, 20);  // 100 samples, 20us interval
for (SITEID = 0; SITEID < SITENUM; SITEID++) {
    adresult[SITEID] = hvie0.GetMeasResult(SITEID, MIRET);  // read current average
    IDSS_POS->SetTestResult(SITEID, 0, adresult[SITEID] * 1e9);  // convert A to nA
}
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1UA, HVIe_RELAY_ON);
delay_ms(2);
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON);  // restore to 1MA range
delay_ms(10);  // wait for voltage to drop to 0
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_OFF);
delay_ms(1);
```

### BVDSS Test (6.6.20.2)
```cpp
double adresult[4] = {0.0};
int SITEID = 0;
hvie0.Set(FI, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON);
delay_ms(1);
hvie0.Set(FI, 250e-6, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON);
delay_ms(30);
hvie0.MeasureVI(10, 20);  // 10 samples, 20us interval
for (SITEID = 0; SITEID < SITENUM; SITEID++) {
    adresult[SITEID] = hvie0.GetMeasResult(SITEID);  // read voltage average (default MVRET)
    BVDSS_POS->SetTestResult(SITEID, 0, adresult[SITEID]);  // V
}
hvie0.Set(FI, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON);
delay_ms(5);
hvie0.Set(FV, 0, HVIe_N10P1000V, HVIe_1MA, HVIe_RELAY_ON);
delay_ms(10);  // wait for voltage to drop to 0
```
