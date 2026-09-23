> 迁移自 auto-memory `STS8300-acm.md`（2026-08-16）


# ACM -- AC Source Meter

The ACM is an AC source meter board. Each board has 24 physical channels, divided into four groups: CH0-5, CH6-11, CH12-17, CH18-23. This is the older ACM board (not ACM200).

## Enumerations

### VIMode -- ACM operating mode
- `FV` -- Constant voltage mode
- `FI` -- Constant current mode

### ACM_VRNG -- Voltage range
- `ACM_N2P18V` -- -2V to +18V range

### ACM_IRNG -- Current range
- `ACM_500MA` -- 500mA range. Note: when |I| < 215mA, board operates in DC mode; when |I| > 215mA, board operates in pulse mode (10ms duration). 215mA is approximate. If pulse exceeds 10ms, range auto-switches to 20mA (output becomes 1/25, measurement is abnormal, alarm triggers). To recover, first set to a non-500mA range, then back to 500mA.
- `ACM_200MA` -- 200mA range
- `ACM_20MA` -- 20mA range
- `ACM_2MA` -- 2mA range
- `ACM_200UA` -- 200uA range
- `ACM_20UA` -- 20uA range
- `ACM_5UA` -- 5uA range

### ACM_OUT_RELAY -- Output relay control
- `ACM_RELAY_ON` -- Close output relay
- `ACM_RELAY_OFF` -- Open output relay
- `ACM_RELAY_HOLD` -- Hold previous relay state

### ACM_MEASTYPE -- Measurement type
- `ACM_MV` -- Measure voltage
- `ACM_MI` -- Measure current

### FLOATMEASMODE -- Measurement mode
- `MEAS_NORMAL` -- Normal measurement mode (default). Measurement completes upon function call.
- `MEAS_AWG` -- AWG measurement mode. Only configures; measurement starts when AWG runs.

### TRIG_MODE -- Trigger mode
- `TRIG_FALLING` -- Falling edge trigger (default)
- `TRIG_RISING` -- Rising edge trigger

### AWG run mode
- `AWG_SINGLE` -- Run AWG waveform once (default)
- `AWG_LOOP` -- Run AWG waveform in loop, stopped by AwgStop()

### CAL_RESULT -- Calibration result
- `CAL_PASS` -- Calibration passed
- `CAL_FAIL` -- Calibration failed
- `STS_NO_RESULT_RECORD` -- Error reading calibration result (e.g., channel not calibrated or invalid site)

### CAL_METER -- Calibration meter type
- `STS_KEITHLEY2000` -- Keithley 2000
- `STS_AGILENT34401` -- Agilent 34401
- `STS_AGILENT3458A` -- Agilent 3458A
- `STS_NO_METER_RECORD` -- Error reading meter info

---

## ACM() -- Constructor
**Signature:** `ACM(char* channelList, char* chName = NULL)`
**Parameters:**
- `channelList` [char*]: ACM binding channel string, e.g. `"S6_0,S6_1"` where "S6" = Slot 6, "0,1" = intra-board index. Max intra-board index is 23 (24 channels per board).
- `chName` [char*, optional]: Custom channel name. Default `NULL`, system names it `ACM_xx`.
**Remarks:** Defines one ACM channel with its physical channel info (slot + intra-board index). Each ACM board has 24 physical channels in four groups: CH0-5, CH6-11, CH12-17, CH18-23.
**Example:**
```python
# 2 ACM boards (Slot5, Slot6), 4-site parallel
acm0 = ACM("S5_0,S5_12,S6_0,S6_12")
acm1 = ACM("S5_1,S5_13,S6_1,S6_13")
# ... up to acm11
# Site binding:
STSSetMultiSiteBind(MD_ACM, SITE_1, "S5_0-11")
STSSetMultiSiteBind(MD_ACM, SITE_2, "S5_12-23")
STSSetMultiSiteBind(MD_ACM, SITE_3, "S6_0-11")
STSSetMultiSiteBind(MD_ACM, SITE_4, "S6_12-23")
```

---

## Set() -- Configure ACM output state
**Signature:** `int Set(VIMode viMode, double setValue, ACM_VRNG vRange, ACM_IRNG iRange, ACM_OUT_RELAY relayStatus = ACM_RELAY_HOLD, double risingTime = 0.1)`
**Parameters:**
- `viMode` [VIMode]: Operating mode. `FV` = constant voltage, `FI` = constant current.
- `setValue` [double]: Setpoint value. For FV: voltage in V, range -2 to 18. For FI: current in A, range -0.5 to 0.5.
- `vRange` [ACM_VRNG]: Voltage range. `ACM_N2P18V`.
- `iRange` [ACM_IRNG]: Current range. One of: `ACM_500MA`, `ACM_200MA`, `ACM_20MA`, `ACM_2MA`, `ACM_200UA`, `ACM_20UA`, `ACM_5UA`.
- `relayStatus` [ACM_OUT_RELAY, optional]: Output relay action. `ACM_RELAY_ON`, `ACM_RELAY_OFF`, `ACM_RELAY_HOLD` (default).
- `risingTime` [double, optional]: Integration/slew time in ms. Resolution 0.1ms. Default 0.1ms.
**Return:** (int) Not explicitly documented; return convention likely 0=success.
**Remarks:**
- When `risingTime` <= 0.1ms: Normal mode (risingTime = 0.1ms).
- When 0.1ms < `risingTime` <= 0.2ms: Slow mode (risingTime = 0.2ms).
- When `risingTime` > 0.2ms: Capload function auto-enabled, risingTime becomes Capload rise/fall time. Capload provides smoother edges, max 65ms.
- Actual settling time depends on current range. For example, with risingTime=1ms and ACM_5UA range, actual settling time is ~1.1ms.
- See ACM_500MA notes in IRNG enum above for pulse-mode constraints.
**Example:**
```python
# Set acm0 to 5V output, default risingTime (0.1ms)
acm0.Set(FV, 5, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON)

# Set acm0 to 5V with 1ms risingTime
acm0.Set(FV, 0, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON)
delay_ms(1)
acm0.Set(FV, 5, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON, 1)
```

---

## SetSyn() -- Synchronous multi-site set
**Signature:** `int SetSyn(VIMode viMode, const double* setValue, UINT siteSize, ACM_VRNG vRange, ACM_IRNG iRange, ACM_OUT_RELAY relayStatus = ACM_RELAY_HOLD, double risingTime = 0.1)`
**Parameters:**
- `viMode` [VIMode]: Operating mode. `FV` or `FI`.
- `setValue` [const double*]: Array of per-site setpoint values. For FV: voltages in V (range -2 to 18). For FI: currents in A (range -0.5 to 0.5). Array length must be >= `siteSize`.
- `siteSize` [UINT]: Number of sites to sync. If 4, syncs SITE1-SITE4.
- `vRange` [ACM_VRNG]: Voltage range. `ACM_N2P18V`.
- `iRange` [ACM_IRNG]: Current range (see Set() for values).
- `relayStatus` [ACM_OUT_RELAY, optional]: Relay action (default `ACM_RELAY_HOLD`).
- `risingTime` [double, optional]: Integration time in ms (default 0.1ms). Same behavior as Set().
**Return:** (int) Not explicitly documented; return convention likely 0=success.
**Remarks:**
- Sets different voltage/current values across sites in a fully synchronized operation.
- `setValue` array length must exceed `siteSize`, otherwise undefined behavior.
- If `siteSize` < current effective site count, unspecified sites keep their previous state.
- If `siteSize` > current effective site count, effective site count is used.
- Same risingTime behavior as Set() (Normal/Slow/Capload modes).
- Same ACM_500MA constraints apply.
**Example:**
```python
# acm0: SITE1 output 3V, SITE2 output 5V, synchronous
setValue = [3.0, 5.0]
siteSize = 2
acm0.SetSyn(FV, setValue, siteSize, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON)

# Same with 3ms risingTime
setValue = [3.0, 5.0]
siteSize = 2
acm0.Set(FV, 0, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON)
delay_ms(1)
acm0.SetSyn(FV, setValue, siteSize, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON, 3)
```

---

## SetClamp() -- Set positive/negative clamp
**Signature:** `int SetClamp(double percent_PFS, double percent_NFS)`
**Parameters:**
- `percent_PFS` [double]: Positive clamp as % of full-scale. Range: voltage clamp 10%-105%, current clamp 10%-112%.
- `percent_NFS` [double]: Negative clamp as % of full-scale. Range: voltage clamp 10%-105%, current clamp 10%-112%.
**Return:**
- 3: Both positive and negative clamp changed
- 2: Negative clamp changed
- 1: Positive clamp changed
- 0: Neither changed
- -1: Function call failed
**Remarks:**
- Clamp settings are mode-dependent. Switching between FV and FI modes clears clamp settings back to 100% (full clamp).
- As long as FV/FI mode is not switched, clamp settings persist across Set() calls.
- If clamp value exceeds upper/lower limits, limits are enforced and an Alarm is raised.
**Example:**
```python
# Set acm1 FI=0, clamp (50,20), then switch to FV=1V, clamp (25,25)
acm1.Set(FI, 0, ACM_N2P18V, ACM_20MA, ACM_RELAY_ON)
acm1.SetClamp(50, 20)  # positive 50%, negative 20% of full range
# Switching FV/FI resets clamps to 100%
acm1.Set(FV, 0, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON)
acm1.SetClamp(25, 25)  # re-set
acm1.Set(FV, 1, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON)

# Staying in same mode preserves clamps
acm1.Set(FV, 0, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON)
acm1.SetClamp(50, 25)
acm1.Set(FV, 10, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON)  # clamp persists
delay_ms(1)
acm1.Set(FV, -2, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON)  # clamp still (50,25)
acm1.MeasureVI(ACM_MV, 100, 20)
acm1.Set(FV, 0, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON)
acm1.SetClamp(100, 100)  # restore full clamp
```

---

## MeasureVI() -- Configure measurement
**Signature:** `int MeasureVI(ACM_MEASTYPE measType, UINT sampleTimes, double samplePeriod, FLOATMEASMODE measMode = MEAS_NORMAL, UINT T1 = 0, UINT T2 = 0, UINT T3 = 0, UINT T4 = 0)`
**Parameters:**
- `measType` [ACM_MEASTYPE]: Measurement type. `ACM_MV` = voltage, `ACM_MI` = current.
- `sampleTimes` [UINT]: Number of ADC samples. Range 1-4096. If <1, forced to 1; if >4096, forced to 4096.
- `samplePeriod` [double]: Inter-sample interval in us. Min 5us, resolution 1us, range 5-30000. If <5, forced to 5; if >30000, forced to 30000.
- `measMode` [FLOATMEASMODE, optional]: Measurement mode. `MEAS_NORMAL` (default) = complete on call. `MEAS_AWG` = configure only, launches with AWG.
- `T1` [UINT, optional]: AWG mode 1st measurement start time in us. Resolution 10us. Default 0.
- `T2` [UINT, optional]: AWG mode 2nd measurement start time (relative to T1). Resolution 10us. Default 0.
- `T3` [UINT, optional]: AWG mode 3rd measurement start time (relative to T2). Resolution 10us. Default 0.
- `T4` [UINT, optional]: AWG mode 4th measurement start time (relative to T3). Resolution 10us. Default 0.
**Return:** (int) Not explicitly documented.
**Remarks:**
- In AWG mode, up to 4 measurement windows can be triggered within one AWG run. T1-T4 are relative times (T2 relative to T1, T3 relative to T2, T4 relative to T3). Total (T1+T2+T3+T4) range: 0 to 600000us.
- If T1-T4 are all omitted, defaults to one measurement at time 0.
- For AWG mode, recommend using synchronous measurement start.
**Example:**
```python
# Normal mode: measure current, 20 samples, 10us interval
acm0.MeasureVI(ACM_MI, 20, 10)

# AWG mode with trigger
acm1.MeasureVI(ACM_MV, 50, 20, MEAS_AWG)
acm0.MeasureVI(ACM_MV, 50, 20, MEAS_AWG)
```

---

## GetMeasResult() -- Read measurement result
**Signature:** `double GetMeasResult(UINT siteCount, int sampleNumber = AVERAGE_RESULT, BYTE triggerNum = 0)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc. Can be any value for NO_SITE channels.
- `sampleNumber` [int, optional]: Result selection:
  - `AVERAGE_RESULT` -- Average value (default)
  - `MAX_RESULT` -- Maximum value
  - `MIN_RESULT` -- Minimum value
  - `TRIG_RESULT` -- Trigger position. In AWG sync measurement, returns the sample index where trigger transition occurred. Supports up to 2 triggers.
  - Non-negative integer N -- Returns the (N+1)th sample value. `0 <= N <= sampleTimes-1`.
- `triggerNum` [BYTE, optional]: Trigger number selector. Only valid when `sampleNumber = TRIG_RESULT`. 0 = first trigger (default), 1 = second trigger. Max 2 triggers.
**Return:** (double) Measurement result. Returns -3 when `sampleNumber = TRIG_RESULT` and no trigger occurred.
**Remarks:**
- Result type (voltage or current) depends on `measType` set in MeasureVI().
**Example:**
```python
# Average current
acm0.MeasureVI(ACM_MI, 20, 10)
for i in range(SITENUM):
    result[i] = acm0.GetMeasResult(i)  # AVERAGE_RESULT

# 15th sample voltage value
acm0.MeasureVI(ACM_MV, 20, 10)
for i in range(SITENUM):
    result[i] = acm0.GetMeasResult(i, 14)  # 0-based index

# AWG trigger positions
acm0.SetMeasVTrig(2.0, TRIG_FALLING)
acm1.MeasureVI(ACM_MV, 50, 20, MEAS_AWG)
acm0.MeasureVI(ACM_MV, 50, 20, MEAS_AWG)
STSEnableAWG(&acm1)
STSEnableMeas(&acm1, &acm0)
STSAWGRun()
for i in range(SITENUM):
    Trig_Point0[i] = acm0.GetMeasResult(i, TRIG_RESULT, 0)  # first trigger
    Trig_Point1[i] = acm0.GetMeasResult(i, TRIG_RESULT, 1)  # second trigger
```

---

## BlockRead() -- Read block of measurement data
**Signature:** `int BlockRead(UINT siteCount, UINT start, UINT size, double* buffer)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
- `start` [UINT]: Block start address (non-negative). Range: 0 to (sampleTimes - 1) from MeasureVI.
- `size` [UINT]: Block size (positive). Range: 1 to (sampleTimes - start) from MeasureVI.
- `buffer` [double*]: User-defined result array, e.g. `double result[1000] = {0.0}`. Buffer length must be >= `size`, otherwise undefined behavior. Recommend global variable.
**Return:** (int) Not explicitly documented.
**Remarks:** Reads a contiguous block of measurement results. Result type depends on `measType` in MeasureVI (ACM_MV returns voltage, ACM_MI returns current).
**Example:**
```python
result = [[0.0] * 200 for _ in range(SITENUM)]
acm0.MeasureVI(ACM_MV, 200, 10)  # measure voltage
for i in range(SITENUM):
    acm0.BlockRead(i, 0, 200, result[i])  # start=0, size=200
```

---

## Pulse() -- Output a pulse
**Signature:** `int Pulse(double pulseValue, UINT pulseTime = 300, int measStartTime = 0, ACM_MEASTYPE measType = ACM_MV, UINT sampleTimes = 10, double samplePeriod = 30)`
**Parameters:**
- `pulseValue` [double]: Pulse amplitude. In FV mode: volts (range -2 to 18). In FI mode: amps (range -0.5 to 0.5).
- `pulseTime` [UINT, optional]: Pulse width in us. Resolution 10us. Range: 300-40000 (when |I| < 215mA); 300-10000 (when |I| > 215mA). Default 300us.
- `measStartTime` [int, optional]: Measurement start time relative to pulse start in us. Range -60000 to 60000. Negative = before pulse. Default 0.
- `measType` [ACM_MEASTYPE, optional]: Measurement type. `ACM_MV` (default) or `ACM_MI`.
- `sampleTimes` [UINT, optional]: Number of ADC samples. Range 1-4096. Default 10.
- `samplePeriod` [UINT, optional]: Inter-sample interval in us. Range 5-30000, resolution 1us. Default 30us.
**Return:** (int) Not explicitly documented.
**Remarks:**
- Must call Set() before Pulse() to configure range and other info. The pulse starts from and returns to the Set() value.
- This function outputs a single voltage or current pulse with configurable amplitude, width, and measurement.
**Example:**
```python
# Start FV=0, output 8V pulse for 1ms, measure voltage,
# 200 samples, 10us interval, start measuring 500us before pulse
acm0.Set(FV, 0, ACM_N2P18V, ACM_20MA, ACM_RELAY_ON)
acm0.Pulse(8, 1000, -500, ACM_MV, 200, 10)
```

---

## AwgLoader() -- Load AWG waveform data
**Signature:** `int AwgLoader(char* awgName, VIMode viMode, ACM_VRNG vRange, ACM_IRNG iRange, double* awgData, UINT awgSize)`
**Parameters:**
- `awgName` [char*]: AWG waveform name. Case-insensitive.
- `viMode` [VIMode]: Operating mode. `FV` or `FI`.
- `vRange` [ACM_VRNG]: Voltage range. `ACM_N2P18V`.
- `iRange` [ACM_IRNG]: Current range (see Set() for values).
- `awgData` [double*]: Array of AWG waveform data points.
- `awgSize` [UINT]: Waveform data size. Range 1-4096.
**Return:** (int) Not explicitly documented.
**Remarks:**
- Range info is for data conversion only; it does NOT switch ranges.
- One ACM channel can load multiple AWG waveforms; each must have a unique name. Duplicate names only write data from the first AwgLoader call.
- Writing 4096 points takes ~5ms; time is proportional to point count.
- Total AWG data per channel per test program must be <= 4096. Data beyond 4096 is silently discarded.
- Best practice: keep total per-channel AWG data < 4096 so repeated calls reuse data (no re-write time).
- If total exceeds 4096, data is re-written to RAM each time, increasing test time.
**Example:**
```python
# Ramp from -1.5V to 3.5V, step 0.1V
sam = 50
interval = 200  # us
awg_pattern = [0.0] * 100
STSAWGCreateRampData(awg_pattern, sam, 1, -1.5, 3.5)
acm0.AwgLoader("Vst", FV, ACM_N2P18V, ACM_20MA, awg_pattern, sam)

# 100Hz sine, Vpp=4, DC offset=5
sam = 1000
interval = 10
awg_pattern = [0.0] * 2000
STSAWGCreateSineData(awg_pattern, sam, 1, 4, 5, 0)
acm0.AwgLoader("Sine", FV, ACM_N2P18V, ACM_2MA, awg_pattern, sam)
```

---

## AwgSelect() -- Select AWG waveform for synchronous run
**Signature:** `int AwgSelect(char* awgName, UINT startAddr, UINT stopAddr, int loopBackAddr, double awgInterval = 10.0)`
**Parameters:**
- `awgName` [char*]: AWG waveform name (must match a name from AwgLoader).
- `startAddr` [UINT]: Start address. Range 0 to sam-1 (sam = waveform point count).
- `stopAddr` [UINT]: Stop address. Range 0 to sam-1.
- `loopBackAddr` [int]: Return/loop-back address. -1 = stay at stop position. 0 to sam-1 = return to that address after completion.
- `awgInterval` [double, optional]: AWG data interval time in us. Resolution 1us. Range 10-60000. Default 10us.
**Return:** (int) Not explicitly documented.
**Remarks:**
- Must call Set() before AwgSelect; the Set() range configuration must match the AwgLoader range exactly.
- AwgSelect only configures; the waveform does NOT output until STSAWGRun() is called.
- Used for synchronous multi-source AWG operation. For single-source AWG, consider AwgRun() instead.
**Example:**
```python
interval = 200  # us
sam1 = 1000
sam2 = 500
awg_pattern1 = [0.0] * 1000
awg_pattern2 = [0.0] * 500
STSAWGCreateRampData(awg_pattern1, sam1, 1, -1.5, 3.5)
STSAWGCreateRampData(awg_pattern2, sam2, 1, -0.5, -1.5)
acm0.AwgLoader("AWG_Vst", FV, ACM_N2P18V, ACM_200MA, awg_pattern1, sam1)
acm0.AwgLoader("AWG_Vuvlo", FV, ACM_N2P18V, ACM_200MA, awg_pattern2, sam2)
# Set() must match AwgLoader range
acm0.Set(FV, -1.5, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON)
acm0.AwgSelect("AWG_Vst", 0, sam1 - 1, 0, interval)
STSAWGRun()  # only now does AWG output
```

---

## AwgRun() -- Single-channel AWG standalone start
**Signature:** `int AwgRun(char* awgName, UINT startAddr, UINT stopAddr, int loopBackAddr, double awgInterval = 10.0, BOOL runMode = AWG_SINGLE, UINT delayTime_ms = 0)`
**Parameters:**
- `awgName` [char*]: AWG waveform name (must match AwgLoader name).
- `startAddr` [UINT]: Start address. Range 0 to sam-1.
- `stopAddr` [UINT]: Stop address. Range 0 to sam-1.
- `loopBackAddr` [int]: Return address. -1 = stay at stop. 0 to sam-1 = return to that address.
- `awgInterval` [double, optional]: Data interval time in us. Resolution 1us. Range 10-60000. Default 10us.
- `runMode` [BOOL, optional]: Run mode. `AWG_SINGLE` (default, run once) or `AWG_LOOP` (loop, stopped by AwgStop()).
- `delayTime_ms` [UINT, optional]: Delay in ms before subsequent operations can start. Range 0-60000. Default (omitted) = AWG scan time (blocks until AWG completes). Recommendation: do NOT fill this parameter.
**Return:** (int) Not explicitly documented.
**Remarks:**
- Set() must be called first; range config must match AwgLoader exactly.
- This is a standalone start (includes waveform selection); does NOT use AwgSelect.
- Cannot be used for synchronous measurement with other sources. For sync measurement, use AwgSelect + STSAWGRun().
**Example:**
```python
# acm0 continuously outputs 120Hz sine, Vpp=0.66, DC=3.3
sam = 830
interval = 10  # us
awg_pattern = [0.0] * 1000
STSAWGCreateSineData(awg_pattern, sam, 1, 0.66, 3.3, 0)
acm0.AwgLoader("Sin_AWG", FV, ACM_N2P18V, ACM_500MA, awg_pattern, sam)
acm0.Set(FV, 0, ACM_N2P18V, ACM_500MA, ACM_RELAY_ON)
acm0.AwgRun("Sin_AWG", 0, sam - 1, 0, interval, AWG_LOOP)
```

---

## AwgStop() -- Stop looping AWG
**Signature:** `int AwgStop(void)`
**Return:** (int) Not explicitly documented.
**Remarks:** Stops the AWG loop execution on this ACM channel (for waveforms started with `AWG_LOOP` mode).
**Example:**
```python
# Run a 1.5ms period sine for 5ms then stop
sam = 150
interval = 10
awg_pattern = [0.0] * 1000
STSAWGCreateSineData(awg_pattern, sam, 1, 2, 3, 0)
acm0.AwgLoader("Sin_AWG", FV, ACM_N2P18V, ACM_500MA, awg_pattern, sam)
acm0.Set(FV, 0, ACM_N2P18V, ACM_500MA, ACM_RELAY_ON)
acm0.AwgRun("Sin_AWG", 0, sam - 1, 0, interval, AWG_LOOP)
delay_ms(5)
acm0.AwgStop()
```

---

## AwgClear() -- Clear AWG data
**Signature:** `int AwgClear(void)`
**Return:** (int) Not explicitly documented.
**Remarks:** Typically called before AwgLoader to clear existing AWG data for this channel.
**Example:**
```python
acm0.AwgClear()
acm0.AwgLoader("P1", FV, ACM_N2P18V, ACM_200MA, awg_pattern1, sam)
```

---

## SetMeasVTrig() -- Set voltage measurement trigger
**Signature:** `int SetMeasVTrig(double vTrig, TRIG_MODE trigMode = TRIG_FALLING, double hysteresisValue = 0.0)`
**Parameters:**
- `vTrig` [double]: Trigger voltage in V. Value depends on the voltage range set by Set().
- `trigMode` [TRIG_MODE, optional]: Trigger mode. `TRIG_FALLING` (default) = falling edge, `TRIG_RISING` = rising edge.
- `hysteresisValue` [double, optional]: Hysteresis value in V. Must be non-negative. Default 0.0.
**Return:** (int) Not explicitly documented.
**Remarks:**
- For rising edge (TRIG_RISING): trigger fires when measurement first goes below (vTrig - hysteresisValue), then goes above vTrig.
- For falling edge (TRIG_FALLING): trigger fires when measurement first goes above (vTrig + hysteresisValue), then goes below vTrig.
- **Critical:** The voltage/current range state must be identical between SetMeasVTrig and MeasureVI. No range-changing functions may be inserted between them, or a utility error occurs.
**Example:**
```python
# acm0 outputs ramp from 10.5V to 8V. acm1 triggers on falling edge at 2V.
acm1.Set(FI, 0, ACM_N2P18V, ACM_20MA, ACM_RELAY_ON)
Trig = 2.0  # trigger voltage
sam = 25
interval = 200
awg_pattern = [0.0] * 100
STSAWGCreateRampData(awg_pattern, sam, 1, 10.5, 8)
acm0.AwgLoader("Uvlo", FV, ACM_N2P18V, ACM_200MA, awg_pattern, sam)
acm0.Set(FV, 10.5, ACM_N2P18V, ACM_200MA, ACM_RELAY_ON)
acm0.AwgSelect("Uvlo", 0, sam - 1, sam - 1, interval)
acm1.SetMeasVTrig(Trig, TRIG_FALLING)  # trigger at 2V falling edge
acm0.MeasureVI(ACM_MV, sam, interval, MEAS_AWG)
acm1.MeasureVI(ACM_MV, sam, interval, MEAS_AWG)
STSEnableAWG(&acm0)
STSEnableMeas(&acm0, &acm1)
STSAWGRun()
```

---

## SetMeasITrig() -- Set current measurement trigger
**Signature:** `int SetMeasITrig(double iTrig, TRIG_MODE trigMode = TRIG_FALLING, double hysteresisValue = 0.0)`
**Parameters:**
- `iTrig` [double]: Trigger current in A. Value depends on the current range set by Set().
- `trigMode` [TRIG_MODE, optional]: Trigger mode. `TRIG_FALLING` (default) or `TRIG_RISING`.
- `hysteresisValue` [double, optional]: Hysteresis value in A. Must be non-negative. Default 0.0.
**Return:** (int) Not explicitly documented.
**Remarks:**
- Hysteresis behavior mirrors SetMeasVTrig: rising edge triggers when signal crosses below (iTrig - hysteresis) then above iTrig; falling edge triggers when above (iTrig + hysteresis) then below iTrig.
- **Critical:** Same range-consistency requirement as SetMeasVTrig. Do NOT insert range-changing Set() calls between SetMeasITrig and MeasureVI.
**Example:**
```python
# acm0 ramp from -1.5V to 3.5V. Trigger on rising edge at 100uA.
Trig = 100e-6  # 100uA
sam = 50
interval = 200
awg_pattern = [0.0] * 100
STSAWGCreateRampData(awg_pattern, sam, 1, -1.5, 3.5)
acm0.AwgLoader("Vst", FV, ACM_N2P18V, ACM_20MA, awg_pattern, sam)
acm0.Set(FV, -1.5, ACM_N2P18V, ACM_20MA, ACM_RELAY_ON)
acm0.AwgSelect("Vst", 0, sam - 1, sam - 1, interval)
# Correct:
acm0.SetMeasITrig(Trig, TRIG_RISING)
acm0.MeasureVI(ACM_MI, sam, interval, MEAS_AWG)  # no Set() in between!
STSEnableAWG(&acm0)
STSEnableMeas(&acm0)
STSAWGRun()

# WRONG (will cause utility error):
# acm0.SetMeasITrig(Trig, TRIG_RISING)
# acm0.Set(FV, -1.5, ACM_N2P18V, ACM_2MA, ACM_RELAY_ON)  # range changed!
# acm0.MeasureVI(ACM_MI, sam, interval, MEAS_AWG)
```

---

## SetAlarmMask() -- Mask alarm for a site
**Signature:** `void SetAlarmMask(UINT siteCount, bool status = true)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
- `status` [bool, optional]: `true` = mask alarms on this site (default); `false` = output alarms on this site.
**Remarks:** Alarm mask set by this function is re-initialized (cleared) in `InitBeforeTestFlow()`.
**Example:**
```python
acm0.SetAlarmMask(0)  # mask Site1 alarms
# Over-range alarm is suppressed
acm0.Set(FV, 19, ACM_N2P18V, ACM_20MA, ACM_RELAY_ON)
```

---

## GetAlarmMask() -- Read alarm mask state
**Signature:** `bool GetAlarmMask(UINT siteCount)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
**Return:** (bool) `true` = alarms masked; `false` = alarms output.
**Example:**
```python
status = acm0.GetAlarmMask(0)  # read Site1 alarm status
```

---

## GetBoardSN() -- Get board serial number
**Signature:** `int GetBoardSN(UINT siteCount, char* boardSN, UINT snSize)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
- `boardSN` [char*]: User-defined buffer for serial number, e.g. `char boardSN[255] = {0}`. Returns empty for invalid site or no stored data.
- `snSize` [UINT]: Size of `boardSN` buffer.
**Return:** (int) 0 = success; non-zero = failure.
**Example:**
```python
boardSN = ["\0"] * 255
acm0.GetBoardSN(0, boardSN, 255)
```

---

## GetBoardHDRev() -- Get board hardware revision
**Signature:** `int GetBoardHDRev(UINT siteCount, char* hardRev, UINT revSize)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
- `hardRev` [char*]: User-defined buffer for hardware revision, e.g. `char hardRev[255] = {0}`. Returns "N/A" if not stored.
- `revSize` [UINT]: Size of `hardRev` buffer.
**Return:** (int) 0 = success; non-zero = failure.
**Example:**
```python
hardRev = ["\0"] * 255
acm0.GetBoardHDRev(0, hardRev, 255)
```

---

## GetCalibrationTime() -- Get calibration date
**Signature:** `SYSTEMTIME GetCalibrationTime(UINT siteCount) const`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
**Return:** (SYSTEMTIME) Calibration date. Returns 1970-1-1 8:00:00 on error (channel not calibrated or invalid site).
**Example:**
```python
calDate = acm0.GetCalibrationTime(0)
```

---

## GetCalibrationTemperature() -- Get calibration temperature
**Signature:** `double GetCalibrationTemperature(UINT siteCount) const`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
**Return:** (double) Calibration temperature in degrees. Returns 0 on error (channel not calibrated or invalid site).
**Example:**
```python
calTemperature = acm0.GetCalibrationTemperature(0)
```

---

## GetCalibrationHumidity() -- Get calibration humidity
**Signature:** `double GetCalibrationHumidity(UINT siteCount) const`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
**Return:** (double) Calibration humidity. Returns 0 on error (channel not calibrated or invalid site).
**Example:**
```python
calHumidity = acm0.GetCalibrationHumidity(0)
```

---

## GetCalibrationResult() -- Get calibration result
**Signature:** `CAL_RESULT GetCalibrationResult(UINT siteCount) const`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
**Return:** (CAL_RESULT) Enum: `CAL_PASS`, `CAL_FAIL`, or `STS_NO_RESULT_RECORD` (error -- channel not calibrated or invalid site).
**Example:**
```python
calResult = acm0.GetCalibrationResult(0)
```

---

## GetCalibrationLogicRev() -- Get calibration logic revision
**Signature:** `int GetCalibrationLogicRev(UINT siteCount) const`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
**Return:** (int) Logic revision number. Returns 255 on error (channel not calibrated or invalid site).
**Example:**
```python
calLogicRev = acm0.GetCalibrationLogicRev(0)
```

---

## GetCalibrationMeter() -- Get calibration meter info
**Signature:** `CAL_METER GetCalibrationMeter(UINT siteCount, char* meterSN = NULL, UINT snSize = 0)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
- `meterSN` [char*, optional]: Buffer for meter serial number, e.g. `char meterSN[255] = {0}`. Returns "N/A" on error. Default NULL (don't read SN).
- `snSize` [UINT, optional]: Size of `meterSN` buffer. Default 0.
**Return:** (CAL_METER) Enum: `STS_KEITHLEY2000`, `STS_AGILENT34401`, `STS_AGILENT3458A`, or `STS_NO_METER_RECORD` (error -- channel not calibrated or invalid site).
**Example:**
```python
calMeterSN = ["\0"] * 255
calMeterType = acm0.GetCalibrationMeter(0, calMeterSN, 255)
```

---

## GetCalibrationCalBoardInfo() -- Get calibration board info
**Signature:** `int GetCalibrationCalBoardInfo(UINT siteCount, char* boardSN = NULL, UINT snSize = 0, char* boardHdRev = NULL, UINT revSize = 0)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
- `boardSN` [char*, optional]: Buffer for calibration board serial number. Returns "N/A" on error. Default NULL.
- `snSize` [UINT, optional]: Size of `boardSN` buffer. Default 0.
- `boardHdRev` [char*, optional]: Buffer for calibration board hardware revision. Returns "N/A" on error. Default NULL.
- `revSize` [UINT, optional]: Size of `boardHdRev` buffer. Default 0.
**Return:** (int) Logic revision of the calibration board. Returns 255 on error (channel not calibrated or invalid site).
**Example:**
```python
boardSN = ["\0"] * 255
boardHdRev = ["\0"] * 255
logicRev = acm0.GetCalibrationCalBoardInfo(0, boardSN, 255, boardHdRev, 255)
```

---

## GetCalibrationSoftRev() -- Get calibration software revision
**Signature:** `int GetCalibrationSoftRev(UINT siteCount, char* softRev, UINT revSize)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
- `softRev` [char*]: User-defined buffer for software revision, e.g. `char softRev[255] = {0}`. Returns "N/A" on error.
- `revSize` [UINT]: Size of `softRev` buffer.
**Return:** (int) 0 = success; non-zero = error (channel not calibrated or invalid site).
**Example:**
```python
softRev = ["\0"] * 255
acm0.GetCalibrationSoftRev(0, softRev, 255)
```

---

## GetCalibrationSlotID() -- Get calibration slot ID
**Signature:** `int GetCalibrationSlotID(UINT siteCount) const`
**Parameters:**
- `siteCount` [UINT]: Site index. 0 = Site1, 1 = Site2, etc.
**Return:** (int) Slot ID at time of calibration. Returns 0 on error (channel not calibrated or invalid site).
**Example:**
```python
slotID = acm0.GetCalibrationSlotID(0)
```

---

## External STS functions used with ACM

These are not ACM member functions but are essential to ACM AWG workflows:

- `STSEnableAWG(&acm)` -- Enable AWG pattern output on the given ACM channel(s)
- `STSEnableMeas(&acm0, &acm1, ...)` -- Enable measurement on the given ACM channel(s)
- `STSAWGRun()` -- Synchronously start all enabled AWG outputs and measurements
- `STSAWGRunTriggerStop(&triggerCh, &stopCh1, &stopCh2)` -- When triggerCh is triggered, stopCh1 and stopCh2 stop synchronously
- `STSAWGCreateRampData(buffer, size, period, startVal, stopVal)` -- Create ramp waveform data
- `STSAWGCreateSineData(buffer, size, period, vpp, dcOffset, phase)` -- Create sine waveform data
- `STSAWGCreateTriangleData(buffer, size, period, vpp, dcOffset, phase)` -- Create triangle waveform data
- `STSAWGCreateSquareData(buffer, size, period, vpp, dcOffset, duty)` -- Create square waveform data
- `STSSetMultiSiteBind(MD_ACM, site, "Sn_m-k")` -- Bind ACM channels to sites
