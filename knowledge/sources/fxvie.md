> 迁移自 auto-memory `STS8300-fxvie.md`（2026-08-16）


# FXVIe -- Flexible VI Source Meter

Overview: FXVIe is a 12-channel per board VI source meter (2 banks, 6 channels each). Channels 4, 5, 10, 11 support TMU and fan-out. Unique features: Gang (parallel), TMU (Time Measurement Unit), differential measurement, AWG, and Turbo mode.

---

## Common Enum Types

```python
# VIMode -- work mode
FV = 0  # constant voltage
FI = 1  # constant current

# FXVIe_VRNG -- voltage range
FXVIe_30V  = 0  # +/-30V
FXVIe_10V  = 1  # +/-10V
FXVIe_3p6V = 2  # +/-3.6V
FXVIe_5V   = 3  # +/-5V (TSet example only)
FXVIe_2V   = 4  # +/-2V (TSet example only)

# FXVIe_IRNG -- current range
FXVIe_1A     = 0
FXVIe_100MA  = 1
FXVIe_10MA   = 2
FXVIe_1MA    = 3
FXVIe_100UA  = 4
FXVIe_10UA   = 5

# FXVIe_OUT_RELAY -- output relay action
FXVIe_RELAY_HOLD            = 0  # hold previous state
FXVIe_RELAY_ON              = 1  # turn on output relay
FXVIe_RELAY_FANOUT_ON       = 2  # turn on fan-out relay
FXVIe_RELAY_ALL_ON          = 3  # turn on both output and fan-out
FXVIe_RELAY_OFF             = 4  # turn off both output and fan-out
FXVIe_RELAY_SENSE_ON        = 5  # independent voltmeter: SENSE line output relay ON, FORCE line OFF
FXVIe_RELAY_SENSE_FANOUT_ON = 6  # independent voltmeter: SENSE line fan-out relay ON, FORCE fan-out OFF

# FXVIe_MI_GAIN -- current measurement gain
FXVIe_MI_X1  = 0
FXVIe_MI_X10 = 1

# FLOATMEASMODE -- measurement mode
MEAS_NORMAL = 0  # normal: measure immediately
MEAS_AWG    = 1  # AWG mode: set only, run when AWG starts

# MeasRet -- measurement readback type
MVRET = 0  # voltage
MIRET = 1  # current

# sampleNumber constants
AVERAGE_RESULT = -1  # get average
MAX_RESULT     = -2  # get maximum
MIN_RESULT     = -3  # get minimum
TRIG_RESULT    = -4  # get trigger position (AWG mode)

# TRIG_MODE -- trigger edge
TRIG_FALLING = 0
TRIG_RISING  = 1

# FXVIe_CONTACTMODE -- contact check mode
FXVIe_HIGH_SIDE = 0
FXVIe_LOW_SIDE  = 1

# FXVIe_TMU_SLOPE -- TMU comparator trigger polarity
FXVIe_TMU_POS = 0  # rising edge
FXVIe_TMU_NEG = 1  # falling edge

# FXVIe_FILTER -- TMU input filter
FXVIe_FILTER_PASS   = 0  # bypass, no filter
FXVIe_FILTER_1MHz   = 1  # 1MHz low-pass filter
FXVIe_FILTER_100KHz = 2  # 100KHz low-pass filter

# FXVIe_TMU_MEAS -- TMU measurement type
FXVIe_MEAS_TIME      = 0  # measure time
FXVIe_MEAS_FREQ      = 1  # measure frequency
FXVIe_MEAS_HIGH_DUTY = 2  # measure high duty cycle
FXVIe_MEAS_LOW_DUTY  = 3  # measure low duty cycle
FXVIe_MEAS_EVENT     = 4  # measure events

# FXVIe_TRNG -- TMU time range
FXVIe_TRANGE_MS = 0  # ms range (30ns~5.368s)
FXVIe_TRANGE_US = 1  # us range (800ns~4ms)
FXVIe_TRANGE_NS = 2  # ns range (30ns~950ns)

# FXVIe_DIFF_FILTER -- differential measurement filter
FXVIe_DIFF_FILTER_OFF = 0
FXVIe_DIFF_FILTER_ON  = 1

# AWG run mode
AWG_SINGLE = 0  # run once
AWG_LOOP   = 1  # loop continuously (stop with AwgStop)

# CAL_RESULT -- calibration result
CAL_PASS             = 0
CAL_FAIL             = 1
STS_NO_RESULT_RECORD = 2

# CAL_METER -- calibration meter type
STS_KEITHLEY2000    = 0
STS_AGILENT34401    = 1
STS_AGILENT3458A    = 2
STS_NO_METER_RECORD = 3
```

---

## Section 1: Constructor and Basic Operation

### FXVIe() -- Constructor
**Signature:** `FXVIe(char* channelList, char* chName = NULL)`
**Parameters:**
- `channelList` [char*]: Slot binding string, e.g. `"S5_0,S5_1"`. "S5" = slot 5, "0,1" = board channel index.
- `chName` [char*]: Custom channel name. Default NULL, system names it `FXVIe_xx`.
**Remarks:**
- Max 12 channels per board, 2 banks, max 6 channels per bank.
- Board channel index max = 11.
- Channels 4, 5, 10, 11 support TMU and fan-out.
**Example:**
```python
# 4 boards at slot 5, 11, 22, 28; 4-site parallel
fxvie0  = FXVIe("S5_0,S11_0,S22_0,S28_0")
fxvie1  = FXVIe("S5_1,S11_1,S22_1,S28_1")
# ... up to fxvie11
fxvie11 = FXVIe("S5_11,S11_11,S22_11,S28_11")

# Site binding
STSSetMultiSiteBind(MD_FXVIe, SITE_1, "S5_0-11")
STSSetMultiSiteBind(MD_FXVIe, SITE_2, "S11_0-11")
STSSetMultiSiteBind(MD_FXVIe, SITE_3, "S22_0-11")
STSSetMultiSiteBind(MD_FXVIe, SITE_4, "S28_0-11")
```

### Set() -- Set VI output state
**Signature:** `int Set(VIMode viMode, double setValue, FXVIe_VRNG vRange, FXVIe_IRNG iRange, FXVIe_OUT_RELAY relayStatus = FXVIe_RELAY_HOLD, double risingTime = 0.02)`
**Parameters:**
- `viMode` [VIMode]: FV (constant voltage) or FI (constant current).
- `setValue` [double]: Set value. FV: -30V~30V. FI: -1A~1A.
- `vRange` [FXVIe_VRNG]: Voltage range. `FXVIe_30V`, `FXVIe_10V`, `FXVIe_3p6V`.
- `iRange` [FXVIe_IRNG]: Current range. `FXVIe_1A` through `FXVIe_10UA`.
- `relayStatus` [FXVIe_OUT_RELAY]: Relay action (7 values). Default: `FXVIe_RELAY_HOLD`.
- `risingTime` [double]: Rise/fall time in ms, resolution 0.01ms. Default 0.02ms.
  - <=0.02ms: Normal mode (0.02ms)
  - <=0.04ms: Slow mode (0.04ms)
  - >0.04ms: Capload mode, max 65ms.
**Remarks:** Sets FXVIe mode, value, range, relay, and capload time.
**Example:**
```python
fxvie0.Set(FV, 5, FXVIe_10V, FXVIe_100MA, FXVIe_RELAY_ON)

# risingTime = 3ms (Capload)
fxvie0.Set(FV, 0, FXVIe_10V, FXVIe_100MA, FXVIe_RELAY_ON)
delay_ms(1)
fxvie0.Set(FV, 5, FXVIe_10V, FXVIe_100MA, FXVIe_RELAY_ON, 3)
```

### SetSyn() -- Synchronized multi-site Set
**Signature:** `int SetSyn(VIMode viMode, const double* setValue, UINT siteSize, FXVIe_VRNG vRange, FXVIe_IRNG iRange, FXVIe_OUT_RELAY relayStatus = FXVIe_RELAY_HOLD, double risingTime = 0.02)`
**Parameters:**
- `viMode` [VIMode]: FV or FI.
- `setValue` [const double*]: Array of set values, one per site.
- `siteSize` [UINT]: Number of sites to sync (e.g. 4 = SITE1-4).
  - Array must be >= siteSize in length.
  - If siteSize < active sites, unset sites keep original state.
  - If siteSize > active sites, clamped to active site count.
- `vRange` [FXVIe_VRNG]: Voltage range.
- `iRange` [FXVIe_IRNG]: Current range.
- `relayStatus` [FXVIe_OUT_RELAY]: Relay action.
- `risingTime` [double]: Rise/fall time in ms.
**Remarks:** Sets different values per site, fully synchronized across sites.
**Example:**
```python
setValue = [3, 5]
fxvie0.SetSyn(FV, setValue, 2, FXVIe_10V, FXVIe_100MA, FXVIe_RELAY_ON)

# with risingTime
fxvie0.Set(FV, 0, FXVIe_10V, FXVIe_100MA, FXVIe_RELAY_ON)
delay_ms(1)
fxvie0.SetSyn(FV, setValue, 2, FXVIe_10V, FXVIe_100MA, FXVIe_RELAY_ON, 3)
```

### SetClamp() -- Set clamp limits
**Signature:** `int SetClamp(double percent_PFS, double percent_NFS)`
**Parameters:**
- `percent_PFS` [double]: Positive clamp as % of full-scale range, 2~105%.
- `percent_NFS` [double]: Negative clamp as % of full-scale range, 2~105%.
**Return:**
- 3: both clamps changed
- 2: negative clamp changed
- 1: positive clamp changed
- 0: neither changed
- -1: function failed
**Remarks:** Clamp settings are mode-dependent. Switching FV/FI mode clears clamps (reset to 105%). Within same mode, clamps persist.
**Example:**
```python
fxvie1.Set(FI, 0, FXVIe_10V, FXVIe_10MA, FXVIe_RELAY_ON)
fxvie1.SetClamp(50, 20)  # positive 50%, negative 20% of full range

# Switch FI->FV: clamps auto-reset to 105%
fxvie1.Set(FV, 0, FXVIe_10V, FXVIe_100MA, FXVIe_RELAY_ON)
fxvie1.SetClamp(25, 25)  # re-clamp in FV mode
fxvie1.Set(FV, 1, FXVIe_10V, FXVIe_100MA, FXVIe_RELAY_ON)
```

---

## Section 2: Measurement

### MeasureVI() -- Configure measurement
**Signature:** `int MeasureVI(UINT sampleTimes, double samplePeriod, FXVIe_MI_GAIN miGain = FXVIe_MI_X1, FLOATMEASMODE measMode = MEAS_NORMAL, UINT T1 = 0, UINT T2 = 0, UINT T3 = 0, UINT T4 = 0)`
**Parameters:**
- `sampleTimes` [UINT]: ADC samples, 1~4096. Clamped if out of range.
- `samplePeriod` [double]: Interval between samples in us, 5~30000, resolution 1us.
- `miGain` [FXVIe_MI_GAIN]: Current measurement gain. `FXVIe_MI_X1` or `FXVIe_MI_X10`. Default: `FXVIe_MI_X1`.
- `measMode` [FLOATMEASMODE]: `MEAS_NORMAL` or `MEAS_AWG`. Default: `MEAS_NORMAL`.
- `T1,T2,T3,T4` [UINT]: AWG mode measurement start times in us, resolution 10us, range 0~(sum)~600000.
  - These are **relative** times: T2 is relative to T1, T3 relative to T2, T4 relative to T3.
  - If all 0, default one measurement at time 0.
  - AWG mode should be used with synchronous start.
**Example:**
```python
fxvie0.MeasureVI(20, 10)  # 20 samples, 10us interval, normal mode
```

### GetMeasResult() -- Get measurement result
**Signature:** `double GetMeasResult(UINT siteCount, MeasRet retType = MVRET, int sampleNumber = AVERAGE_RESULT, BYTE triggerNum = 0)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2, ...
  - If channel is NO_SITE, any value works.
- `retType` [MeasRet]: `MVRET` (voltage in V) or `MIRET` (current in A). Default: `MVRET`.
- `sampleNumber` [int]: `AVERAGE_RESULT`, `MAX_RESULT`, `MIN_RESULT`, `TRIG_RESULT`, or non-negative N (returns N+1-th sample, 0 <= N <= sam-1). Default: `AVERAGE_RESULT`.
- `triggerNum` [BYTE]: Trigger index (only for `TRIG_RESULT`). 0=first trigger, 1=second trigger. Default: 0.
**Return:** Measurement value. Returns -3 if no trigger, -5 if measurement mode mismatch.
**Remarks:** Voltage and current are measured simultaneously -- just choose readback type.
**Example:**
```python
fxvie0.MeasureVI(20, 10)
for i in range(SITENUM):
    adresult[i] = fxvie0.GetMeasResult(i, MIRET)              # average current
    adresult[i] = fxvie0.GetMeasResult(i, MVRET, 14)          # 15th voltage point

# AWG trigger mode
fxvie0.SetMeasVTrig(2, TRIG_FALLING)
fxvie1.MeasureVI(50, 20, FXVIe_MI_X1, MEAS_AWG)
fxvie0.MeasureVI(50, 20, FXVIe_MI_X1, MEAS_AWG)
STSEnableAWG(fxvie1)
STSEnableMeas(fxvie1, fxvie0)
STSAWGRun()
for i in range(SITENUM):
    Trig_Point0[i] = fxvie0.GetMeasResult(0, MVRET, TRIG_RESULT, 0)  # first trigger position
    Trig_Point1[i] = fxvie0.GetMeasResult(0, MVRET, TRIG_RESULT, 1)  # second trigger position
```

### BlockRead() -- Block read measurement data
**Signature:** `int BlockRead(UINT siteCount, UINT start, UINT size, double* buffer, MeasRet retType = MVRET)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, ...
- `start` [UINT]: Block start address, 0 <= start <= sampleTimes-1.
- `size` [UINT]: Block size, 1 <= size <= sampleTimes - start.
- `buffer` [double*]: User-defined array for results. Must be >= size. Recommend global variable.
- `retType` [MeasRet]: `MVRET` or `MIRET`. Default: `MVRET`.
**Remarks:** Reads a contiguous block of measurement results.
**Example:**
```python
result = [[0]*200 for _ in range(SITENUM)]
fxvie0.MeasureVI(200, 10)
for i in range(SITENUM):
    fxvie0.BlockRead(i, 0, 200, result[i], MVRET)
```

---

## Section 3: Pulse

### Pulse() -- Output voltage/current pulse
**Signature:** `int Pulse(double pulseValue, UINT pulseTime = 300, int measStartTime = 0, UINT sampleTimes = 10, double sampleInterval = 30)`
**Parameters:**
- `pulseValue` [double]: Pulse amplitude. FV: -30V~30V. FI: -1A~1A.
- `pulseTime` [UINT]: Pulse duration in us, 300~40000, resolution 10us. Default: 300.
- `measStartTime` [int]: Measurement start time relative to pulse start in us, -60000~60000. Default: 0.
- `sampleTimes` [UINT]: ADC samples, 1~4096. Default: 10.
- `sampleInterval` [UINT]: Sample interval in us, 5~30000, resolution 1us. Default: 30.
**Remarks:** Outputs amplitude/duration-adjustable pulse. Must call Set() first for range config. Pulse starts and ends at the Set value.
**Example:**
```python
fxvie0.Set(FV, 0, FXVIe_10V, FXVIe_10MA, FXVIe_RELAY_ON)
fxvie0.Pulse(8, 1000, -500, 200, 10)
# pulseValue=8V, duration=1000us, meas starts 500us before pulse, 200 samples, 10us interval
```

---

## Section 4: AWG (Arbitrary Waveform Generator)

### AwgLoader() -- Import AWG waveform data
**Signature:** `int AwgLoader(char* awgName, VIMode viMode, FXVIe_VRNG vRange, FXVIe_IRNG iRange, double* awgData, UINT awgSize)`
**Parameters:**
- `awgName` [char*]: Waveform name (case-insensitive). Must be unique if multiple waveforms.
- `viMode` [VIMode]: FV or FI.
- `vRange` [FXVIe_VRNG]: Voltage range (for data conversion only, does not switch range).
- `iRange` [FXVIe_IRNG]: Current range (for data conversion only).
- `awgData` [double*]: AWG waveform data array.
- `awgSize` [UINT]: Data size, 1~4096.
**Remarks:**
- Range info is for data scaling only -- no range switching occurs.
- Same-name waveforms only write on first call -- subsequent calls ignored.
- Writes data to RAM; 4096 points takes ~5ms.
- Total AWG data per channel per test program must be <= 4096 (recommended). If exceeded, re-writes cost extra time.
**Example:**
```python
sam = 50
interval = 200
awg_pattern = [0]*100
STSAWGCreateRampData(awg_pattern, sam, 1, 16.5, 21.5)
fxvie0.AwgLoader("Vst", FV, FXVIe_30V, FXVIe_100MA, awg_pattern, sam)

# sine wave: 100Hz, Vpp=4V, DC offset=10V
sam = 1000
awg_pattern = [0]*2000
STSAWGCreateSineData(awg_pattern, sam, 1, 4, 10, 0)
fxvie0.AwgLoader("Sine", FV, FXVIe_30V, FXVIe_100MA, awg_pattern, sam)
```

### AwgSelect() -- Select AWG waveform to run (synchronous)
**Signature:** `int AwgSelect(char* awgName, UINT startAddr, UINT stopAddr, int loopBackAddr, double awgInterval = 10.0)`
**Parameters:**
- `awgName` [char*]: Waveform name matching AwgLoader.
- `startAddr` [UINT]: Start point, 0~sam-1.
- `stopAddr` [UINT]: Stop point, 0~sam-1.
- `loopBackAddr` [int]: Return address after run. <0: stay at end; 0~sam-1: hold at that point.
- `awgInterval` [double]: Data interval in us, 10~60000, resolution 1us. Default: 10.
**Remarks:**
- Must call Set() before AwgSelect with matching mode/ranges from AwgLoader.
- AwgSelect alone does NOT output -- use STSAWGRun() for synchronous start.
- Each channel can have multiple waveforms; select the one to run.
**Example:**
```python
# Load two waveforms, run only one
sam1, sam2 = 1000, 500
interval = 200
awg_pattern1 = [0]*1000
awg_pattern2 = [0]*500
STSAWGCreateRampData(awg_pattern1, sam1, 1, 16.5, 21.5)
STSAWGCreateRampData(awg_pattern2, sam2, 1, 16.5, 10.5)
fxvie0.AwgLoader("AWG_Vst",   FV, FXVIe_30V, FXVIe_100MA, awg_pattern1, sam1)
fxvie0.AwgLoader("AWG_Vuvlo", FV, FXVIe_10V, FXVIe_100MA, awg_pattern2, sam2)
fxvie0.Set(FV, 16.5, FXVIe_30V, FXVIe_100MA, FXVIe_RELAY_ON)
fxvie0.AwgSelect("AWG_Vst", 0, sam1-1, 0, interval)
STSAWGRun()
```

### AwgRun() -- Single-channel AWG start (non-synchronous)
**Signature:** `int AwgRun(char* awgName, UINT startAddr, UINT stopAddr, int loopBackAddr, double awgInterval = 10.0, BOOL runMode = AWG_SINGLE, UINT delayTime_ms = 0)`
**Parameters:**
- `awgName` [char*]: Waveform name matching AwgLoader.
- `startAddr` [UINT]: Start point, 0~sam-1.
- `stopAddr` [UINT]: Stop point, 0~sam-1.
- `loopBackAddr` [UINT]: <0 stay at end; 0~sam-1 hold at that point.
- `awgInterval` [double]: Data interval in us, 10~60000. Default: 10.
- `runMode` [BOOL]: `AWG_SINGLE` (run once) or `AWG_LOOP` (continuous, stop with AwgStop). Default: `AWG_SINGLE`.
- `delayTime_ms` [UINT]: Delay in ms, 0~60000. Operations after AwgRun allowed after this delay. Default = AWG scan time. **Recommend not setting this.**
**Remarks:**
- Standalone AWG start -- does not synchronize with other sources.
- For synchronous measurement, use AwgSelect + STSAWGRun instead.
- Set() with matching ranges must be called before.
**Example:**
```python
sam = 830
interval = 10
awg_pattern = [0]*1000
STSAWGCreateSineData(awg_pattern, sam, 1, 0.66, 3.3, 0)  # 120Hz, Vpp=0.66V, DC=3.3V
fxvie0.AwgLoader("Sin_AWG", FV, FXVIe_10V, FXVIe_1A, awg_pattern, sam)
fxvie0.Set(FV, 0, FXVIe_10V, FXVIe_1A, FXVIe_RELAY_ON)
fxvie0.AwgRun("Sin_AWG", 0, sam-1, 0, interval, AWG_LOOP)
```

### AwgStop() -- Stop AWG loop
**Signature:** `int AwgStop(void)`
**Remarks:** Stops looping AWG on the channel.
**Example:**
```python
fxvie0.AwgRun("Sin_AWG", 0, sam-1, 0, interval, AWG_LOOP)
delay_ms(6)
fxvie0.AwgStop()
```

### AwgClear() -- Clear AWG data
**Signature:** `int AwgClear(void)`
**Remarks:** Clears AWG data on the channel. Usually called before AwgLoader.
**Example:**
```python
fxvie0.AwgClear()
fxvie0.AwgLoader("P1", FV, FXVIe_30V, FXVIe_100MA, awg_pattern1, sam)
```

---

## Section 5: Measurement Triggers

### SetMeasVTrig() -- Set voltage measurement trigger
**Signature:** `int SetMeasVTrig(double vTrig, TRIG_MODE trigMode = TRIG_FALLING, double hysteresisValue = 0.0)`
**Parameters:**
- `vTrig` [double]: Trigger voltage in V. Must match the Set() voltage range.
- `trigMode` [TRIG_MODE]: `TRIG_FALLING` or `TRIG_RISING`. Default: `TRIG_FALLING`.
- `hysteresisValue` [double]: Hysteresis in V, >= 0 only. Default: 0.
  - Rising edge: triggers when result drops below (vTrig-hysteresis) then rises above vTrig.
  - Falling edge: triggers when result rises above (vTrig+hysteresis) then drops below vTrig.
**Remarks:** Must NOT insert any range-changing function between SetMeasVTrig and MeasureVI. Range/state must be identical.
**Example:**
```python
# Correct:
fxvie1.Set(FI, 0, FXVIe_10V, FXVIe_10MA, FXVIe_RELAY_ON)
fxvie1.SetMeasVTrig(2, TRIG_FALLING)
fxvie1.MeasureVI(sam, interval, FXVIe_MI_X1, MEAS_AWG)

# Wrong (range changed between trigger set and measure):
fxvie1.SetMeasVTrig(2, TRIG_FALLING)
fxvie1.Set(FI, 0, FXVIe_30V, FXVIe_10MA, FXVIe_RELAY_ON)  # ERROR: range mismatch!
fxvie1.MeasureVI(sam, interval, FXVIe_MI_X1, MEAS_AWG)
```

### SetMeasITrig() -- Set current measurement trigger
**Signature:** `int SetMeasITrig(double iTrig, TRIG_MODE trigMode = TRIG_FALLING, double hysteresisValue = 0.0)`
**Parameters:**
- `iTrig` [double]: Trigger current in A. Must match the Set() current range.
- `trigMode` [TRIG_MODE]: `TRIG_FALLING` or `TRIG_RISING`. Default: `TRIG_FALLING`.
- `hysteresisValue` [double]: Hysteresis in A, >= 0 only. Default: 0.
**Remarks:** Same as SetMeasVTrig but for current. Must NOT insert range/gain-changing function between SetMeasITrig and MeasureVI.
**Example:**
```python
# Correct:
fxvie0.MeasureVI(sam, interval, FXVIe_MI_X1, MEAS_AWG)
fxvie0.SetMeasITrig(200e-6, TRIG_RISING)
STSEnableAWG(fxvie0)
STSEnableMeas(fxvie0)
STSAWGRun()

# Wrong:
fxvie0.MeasureVI(sam, interval, FXVIe_MI_X1, MEAS_AWG)
fxvie0.Set(FV, 16.5, FXVIe_30V, FXVIe_10MA, FXVIe_RELAY_ON)  # ERROR: range change!
fxvie0.SetMeasITrig(200e-6, TRIG_RISING)
```

---

## Section 6: Contact Check

### ContactCheck() -- Set contact check mode
**Signature:** `int ContactCheck(FXVIe_CONTACTMODE checkMode)`
**Parameters:**
- `checkMode` [FXVIe_CONTACTMODE]: `FXVIe_HIGH_SIDE` or `FXVIe_LOW_SIDE`.
**Remarks:**
- VI source returns to pre-check state after completion.
- Supports Group operation.
- Same bank channels cannot perform LOW-side check simultaneously.
**Example:**
```python
fxvie0.ContactCheck(FXVIe_HIGH_SIDE)
```

### GetContactCheckResult() -- Get contact check result
**Signature:** `int GetContactCheckResult(UINT siteCount, double& highRes, double& lowRes)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, ...
- `highRes` [double&]: Output high-side resistance value.
- `lowRes` [double&]: Output low-side resistance value.
**Return:**
- -1: invalid site
- 0: contact check pass
- 1: high-side fail
- 2: low-side fail
**Example:**
```python
highRes = 0.0
lowRes = 0.0
result = fxvie0.GetContactCheckResult(0, highRes, lowRes)
```

---

## Section 7: Relay Control

### SetFLOff() -- Disconnect Force Low relay
**Signature:** `int SetFLOff()`
**Remarks:** Disconnects the ForceLow relay of the current channel's bank.
**Example:**
```python
fxvie0.SetFLOff()
```

---

## Section 8: TMU (Time Measurement Unit)

TMU channels: 4, 5, 10, 11 per board.

### TMUConnect() -- Connect TMU input relay
**Signature:** `int TMUConnect(UINT usDelay = 500)`
**Parameters:**
- `usDelay` [UINT]: Delay after relay connection in us, 0~10000. Default: 500.
**Example:**
```python
fxvie0.TMUConnect()
```

### TMUDisconnect() -- Disconnect TMU input relay
**Signature:** `int TMUDisconnect(UINT usDelay = 100)`
**Parameters:**
- `usDelay` [UINT]: Delay after relay disconnection in us, 0~10000. Default: 100.
**Example:**
```python
fxvie0.TMUDisconnect()
```

### TMUSetInSource() -- Set single signal source mode
**Signature:** `int TMUSetInSource()`
**Remarks:**
- User channel unit and board internal measurement unit are 1:1 mapped.
- Must be called before TMUStart/TMUStop so hardware channels match.
- If set after Start/Stop, signal channels may mismatch -- Measure returns abnormal value.
- System calls this in InitAfterTestFlow to restore default single-signal state.
- For complex matrix, use TMUSetMatrix.
**Example:**
```python
fxvie0.TMUSetInSource()  # Single source mode
```

### TMUSetMatrix() -- Set TMU signal matrix
**Signature:** `int TMUSetMatrix(FXVIe* startChSel, FXVIe* stopChSel)`
**Parameters:**
- `startChSel` [FXVIe*]: Pointer to FXVIe channel for START signal.
- `stopChSel` [FXVIe*]: Pointer to FXVIe channel for STOP signal.
**Remarks:**
- Last call between TMUSetInSource and TMUSetMatrix takes effect; persists until reset.
- For dual-signal measurement, both TMU channels in same bank must be on same Site.
- Constraints (none met = no matrix set):
  a) startChSel and stopChSel must have same number of channels.
  b) Corresponding channels form signal group, must be in same bank and be TMU channels.
  c) Physical channels of the logical channel calling this must match those in startChSel or stopChSel.
  d) All-or-nothing: either all dual-signal or all single-signal, no mixing.
**Example:**
```python
# 2-site: fxvie0 has ch4,10; fxvie1 has ch5,11
fxvie0 = FXVIe("S5_4,S5_10")
fxvie1 = FXVIe("S5_5,S5_11")

# Dual-signal: fxvie0's MU as measurement unit, fxvie0=start, fxvie1=stop
fxvie0.TMUSetMatrix(fxvie0, fxvie1)

# Single-signal: same as TMUSetInSource
fxvie0.TMUSetMatrix(fxvie0, fxvie0)
```

### TMUStart() -- Set START signal parameters
**Signature:** `int TMUStart(FXVIe_VRNG vRange = FXVIe_30V, FXVIe_TMU_SLOPE slope = FXVIe_TMU_POS, double triggerLevel = 0.0, FXVIe_FILTER filter = FXVIe_FILTER_PASS, UINT triggerWidth = 200, UINT holdoffTime = 0, UINT holdoffNum = 0)`
**Parameters:**
- `vRange` [FXVIe_VRNG]: Signal voltage range. `FXVIe_30V`, `FXVIe_10V`, `FXVIe_3p6V`. Default: `FXVIe_30V`.
- `slope` [FXVIe_TMU_SLOPE]: Trigger polarity. `FXVIe_TMU_POS` (rising) or `FXVIe_TMU_NEG` (falling). Default: `FXVIe_TMU_POS`.
- `triggerLevel` [double]: Trigger level in V. Range matches vRange. Default: 0.0V.
- `filter` [FXVIe_FILTER]: Input filter. `FXVIe_FILTER_PASS`, `FXVIe_FILTER_1MHz`, `FXVIe_FILTER_100KHz`. Default: `FXVIe_FILTER_PASS`.
  - Use filter to remove high-frequency noise on signal.
  - Not recommended for square wave signals.
- `triggerWidth` [UINT]: Trigger pulse width in ns, 0~80000, step 5ns (auto-rounded to nearest 5). Default: 200.
  - Signal must remain above (rising) or below (falling) triggerLevel for triggerWidth.
- `holdoffTime` [UINT]: Delayed trigger time in ns, 0 or 20~1e9, step 5ns. Input <20 becomes 0. Default: 0.
- `holdoffNum` [UINT]: Ignored START event count, 0~65535. Default: 0.
**Remarks:** For single-signal measurement, TMUStart and TMUStop must have same vRange and filter.
**Example:**
```python
fxvie0.TMUStart(FXVIe_10V, FXVIe_TMU_POS, 3.5, FXVIe_FILTER_1MHz)
fxvie0.TMUStart(FXVIe_3p6V, FXVIe_TMU_POS, 1.5, FXVIe_FILTER_PASS, 10, 0, 1)
```

### TMUStop() -- Set STOP signal parameters
**Signature:** `int TMUStop(FXVIe_VRNG vRange = FXVIe_30V, FXVIe_TMU_SLOPE slope = FXVIe_TMU_POS, double triggerLevel = 0.0, FXVIe_FILTER filter = FXVIe_FILTER_PASS, UINT triggerWidth = 200, UINT holdoffTime = 0, UINT holdoffNum = 0)`
**Parameters:** Same as TMUStart.
**Remarks:**
- For frequency measurement, TMUStop can be omitted.
- For single-signal mode, vRange and filter must match TMUStart.
**Example:**
```python
fxvie0.TMUStop(FXVIe_10V, FXVIe_TMU_NEG, 3.5, FXVIe_FILTER_1MHz)
fxvie0.TMUStop(FXVIe_3p6V, FXVIe_TMU_POS, 1.5, FXVIe_FILTER_PASS, 10, 0, 2)
```

### TMUMeasure() -- Start TMU measurement
**Signature:** `int TMUMeasure(FXVIe_TMU_MEAS measType = FXVIe_MEAS_TIME, UINT sampleNum = 1, double msTimeout = 1.0, FXVIe_TRNG tRange = FXVIe_TRANGE_MS)`
**Parameters:**
- `measType` [FXVIe_TMU_MEAS]: Measurement type:
  - `FXVIe_MEAS_TIME`: measure time, sampleNum = sample count
  - `FXVIe_MEAS_FREQ`: measure frequency, sampleNum = period count
  - `FXVIe_MEAS_HIGH_DUTY`: high duty cycle, sampleNum = edge count (min 3 for full period)
  - `FXVIe_MEAS_LOW_DUTY`: low duty cycle, sampleNum = edge count (min 3 for full period)
  - `FXVIe_MEAS_EVENT`: events, sampleNum = event count (includes Start+Stop)
  - Default: `FXVIe_MEAS_TIME`.
- `sampleNum` [UINT]: Sample count, 1~2048. Default: 1.
- `msTimeout` [double]: Measurement timeout in ms, 0.001~21000. Default: 1.0. Out of range = 1.
- `tRange` [FXVIe_TRNG]: Time range. `FXVIe_TRANGE_MS`, `FXVIe_TRANGE_US`, `FXVIe_TRANGE_NS`. Default: `FXVIe_TRANGE_MS`.
  - For DUTY and EVENT types, must be `FXVIe_TRANGE_MS`.
**Remarks:**
- For DUTY type: Start and Stop must use different slopes (one rising, one falling), holdoffNum must be 0.
- If TMUStart/TMUStop signal channels don't match TMUSetMatrix/TMUSetInSource, returns abnormal value.
**Example:**
```python
fxvie0.TMUMeasure(FXVIe_MEAS_TIME, 1, 2)
# Duty cycle measurement
fxvie0.TMUMeasure(FXVIe_MEAS_HIGH_DUTY, 20, 10, FXVIe_TRANGE_MS)
```

### TMUGetMeasResult() -- Get TMU measurement result
**Signature:** `double TMUGetMeasResult(UINT siteCount, int retType = AVERAGE_RESULT)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, ...
- `retType` [int]: Result type:
  - `AVERAGE_RESULT`: average value (default)
  - Non-negative N: return N+1-th sample (0 <= N <= sampleNum-1)
  - For TIME type: retType=AVERAGE -> avg time in us; retType=N -> N+1-th sample time in us.
  - For FREQ type: retType ignored, returns frequency in KHz.
  - For DUTY type: retType ignored, returns duty cycle in %.
  - For EVENT type: retType=AVERAGE -> event count meeting trigger; retType=N -> N+1-th event moment in us.
**Example:**
```python
# Time measurement
fxvie0.TMUSetInSource()
fxvie0.TMUStart(FXVIe_30V, FXVIe_TMU_POS, 1.5, FXVIe_FILTER_PASS)
fxvie0.TMUStop(FXVIe_30V, FXVIe_TMU_POS, 13.5, FXVIe_FILTER_PASS)
fxvie0.TMUConnect()
fxvie0.TMUMeasure(FXVIe_MEAS_TIME, 10, 20, FXVIe_TRANGE_MS)
val = fxvie0.TMUGetMeasResult(0, AVERAGE_RESULT)  # average time of SITE1
val = fxvie0.TMUGetMeasResult(0, 5)                # 6th point time of SITE1

# Duty cycle measurement
fxvie0.TMUSetInSource()
fxvie0.TMUStart(FXVIe_10V, FXVIe_TMU_POS, 2.0, FXVIe_FILTER_PASS)
fxvie0.TMUStop(FXVIe_10V, FXVIe_TMU_NEG, 2.0, FXVIe_FILTER_PASS)
fxvie0.TMUConnect()
fxvie0.TMUMeasure(FXVIe_MEAS_HIGH_DUTY, 20, 10, FXVIe_TRANGE_MS)
val = fxvie0.TMUGetMeasResult(0, AVERAGE_RESULT)  # high duty cycle %
```

---

## Section 9: Differential Measurement

These are **global functions** (not member functions).

### FXVIeDiffMeasure() -- Start differential measurement
**Signature:** `int FXVIeDiffMeasure(FXVIe* baseFXVIe, FXVIe* measFXVIe, UINT sampleTimes, double samplePeriod, FXVIe_DIFF_FILTER filter = FXVIe_DIFF_FILTER_OFF)`
**Parameters:**
- `baseFXVIe` [FXVIe*]: Reference/base channel.
- `measFXVIe` [FXVIe*]: Channel under test.
- `sampleTimes` [UINT]: Samples, 1~2048.
- `samplePeriod` [double]: Sample interval in us, 5~30000, resolution 1us.
- `filter` [FXVIe_DIFF_FILTER]: `FXVIe_DIFF_FILTER_OFF` or `FXVIe_DIFF_FILTER_ON`. Default: OFF.
**Remarks:**
- Global function.
- Two channels must be in **same bank**.
- Cannot use same channel for both.
- Does NOT support Group.
- baseFXVIe and measFXVIe must have same number of physical channels.
**Example:**
```python
fxvie0 = FXVIe("S5_0,S5_6")
fxvie1 = FXVIe("S5_1,S5_7")
FXVIeDiffMeasure(fxvie0, fxvie1, 100, 10)
```

### FXVIeDiffGetMeasResult() -- Get differential result
**Signature:** `double FXVIeDiffGetMeasResult(UINT siteCount, int sampleNumber = AVERAGE_RESULT)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, ...
- `sampleNumber` [int]: `AVERAGE_RESULT`, `MAX_RESULT`, `MIN_RESULT`, or non-negative N (0 <= N <= sam-1). Default: `AVERAGE_RESULT`.
**Return:** Differential measurement result in V.
**Remarks:** Global function. Read result promptly -- next differential measurement overwrites.
**Example:**
```python
FXVIeDiffMeasure(fxvie0, fxvie1, 100, 10)
for i in range(SITENUM):
    adresult[i] = FXVIeDiffGetMeasResult(i)
```

### FXVIeDiffBlockRead() -- Block read differential data
**Signature:** `int FXVIeDiffBlockRead(UINT siteCount, UINT start, UINT size, double* buffer)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, ...
- `start` [UINT]: Block start address.
- `size` [UINT]: Block size.
- `buffer` [double*]: User-defined array, recommend global. Must be >= size.
**Remarks:** Global function. Reads a contiguous block of differential measurement results.
**Example:**
```python
result = [[0]*200 for _ in range(SITENUM)]
FXVIeDiffMeasure(fxvie0, fxvie1, 100, 10)
for i in range(SITENUM):
    FXVIeDiffBlockRead(i, 0, 200, result[i])
```

---

## Section 10: Gang (Parallel) Functions

Gang connects channels in parallel for high-current output. Must be used between GangRelay and GangReset.

### GangRelay() -- Set parallel channel relay
**Signature:** (overloaded)
```
int GangRelay(FXVIeParallel_CH0)
int GangRelay(FXVIeParallel_CH0, FXVIeParallel_CH1)
int GangRelay(FXVIeParallel_CH0, FXVIeParallel_CH1, FXVIeParallel_CH2)
int GangRelay(FXVIeParallel_CH0, FXVIeParallel_CH1, FXVIeParallel_CH2, FXVIeParallel_CH3)
int GangRelay(FXVIeParallel_CH0, FXVIeParallel_CH1, FXVIeParallel_CH2, FXVIeParallel_CH3, FXVIeParallel_CH4)
```
**Parameters:**
- `Parallel_CHx` [FXVIe]: Channel to parallel with the main channel (up to 5 aux channels).
**Remarks:**
- Does NOT support Group.
- All parallel channels must have same site attribute (all multi-site or all NO_SITE).
- Same site: all channels must be in same bank.
- Different sites: all channels must be in different banks.
- After GangRelay (before GangReset): TMUChannel is invalid for all same-bank channels.
- After GangRelay (before GangReset): Set function is invalid for parallel channels.
- After GangRelay: all parallel channels default to FI=0, VRNG=30V, IRNG=100UA.
**Example:**
```python
# Correct:
fxvie0.GangRelay(fxvie1, fxvie2)
fxvie0.GangReset()

# Wrong: mixed site attribute
# fxvie0, fxvie1 = multi-site; fxvie2 = NO_SITE => ERROR

# Wrong: different banks same site
# SITE_1: S18_2,S18_3; SITE_2: S18_8,S18_9 -> S18_8 (bank1) and S18_1 (bank0) mismatch => ERROR
```

### GangSet() -- Set Gang current value
**Signature:** `int GangSet(double setValue, double risingTime = 0.02)`
**Parameters:**
- `setValue` [double]: Current value in A, -1.2A~1.2A.
- `risingTime` [double]: Rise/fall time in ms, 0.02~65. Default: 0.02.
  - After dividing by parallel channel count: <=0.02 = Normal, <=0.04 = Slow, >0.04 = Capload.
**Remarks:**
- Does NOT support Group.
- Must be called between GangRelay and GangReset.
- After GangSet: all parallel channels set to VRNG=30V, IRNG=1A.
**Example:**
```python
fxvie0.GangRelay(fxvie1, fxvie2)
fxvie0.GangSet(1)
fxvie0.GangReset()
```

### GangSetSyn() -- Synchronized multi-site Gang Set
**Signature:** `int GangSetSyn(const double* setValue, UINT siteSize, double risingTime = 0.02)`
**Parameters:**
- `setValue` [const double*]: Array of current values in A, -1.2~1.2 per site.
- `siteSize` [UINT]: Number of sites to sync.
- `risingTime` [double]: Rise/fall time in ms, 0.02~65. Default: 0.02.
**Remarks:**
- Does NOT support Group.
- Must be between GangRelay and GangReset.
- After call: VRNG=30V, IRNG=1A on all parallel channels.
**Example:**
```python
fxvie0.GangRelay(fxvie1, fxvie2)
setValue = [1, 1.2]
fxvie0.GangSetSyn(setValue, 2)
fxvie0.GangReset()
```

### GangMeasure() -- Gang measurement setup
**Signature:** `int GangMeasure(UINT sampleTimes, double samplePeriod)`
**Parameters:**
- `sampleTimes` [UINT]: ADC samples, 1~4096. Clamped if out of range.
- `samplePeriod` [double]: Sample interval in us, 5~30000, resolution 1us.
**Remarks:**
- Does NOT support Group.
- Must be between GangRelay and GangReset.
**Example:**
```python
fxvie0.GangRelay(fxvie1, fxvie2)
fxvie0.GangSet(1)
fxvie0.GangMeasure(20, 10)
fxvie0.GangReset()
```

### GangGetMeasResult() -- Get Gang measurement result
**Signature:** `double GangGetMeasResult(UINT siteCount, MeasRet retType = MVRET, int sampleNumber = AVERAGE_RESULT)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, ...
- `retType` [MeasRet]: `MVRET` (V) or `MIRET` (A). Default: `MVRET`.
- `sampleNumber` [int]: `AVERAGE_RESULT`, `MAX_RESULT`, `MIN_RESULT`, or non-negative N. Default: `AVERAGE_RESULT`.
**Return:** Measurement value in V (MVRET) or A (MIRET).
**Remarks:** Must be between GangRelay and GangReset. Voltage and current measured simultaneously.
**Example:**
```python
fxvie0.GangRelay(fxvie1, fxvie2)
fxvie0.GangSet(1)
delay_ms(1)
fxvie0.GangMeasure(20, 10)
for i in range(SITENUM):
    adresult[i] = fxvie0.GangGetMeasResult(i, MIRET)       # average current
    adresult[i] = fxvie0.GangGetMeasResult(i, MVRET, 14)   # 15th voltage point
fxvie0.GangReset()
```

### GangBlockRead() -- Block read Gang data
**Signature:** `int GangBlockRead(UINT siteCount, UINT start, UINT size, double* buffer, MeasRet retType = MVRET)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, ...
- `start` [UINT]: Block start address.
- `size` [UINT]: Block size.
- `buffer` [double*]: User array, recommend global. Must be >= size.
- `retType` [MeasRet]: `MVRET` or `MIRET`. Default: `MVRET`.
**Remarks:** Must be between GangRelay and GangReset.
**Example:**
```python
result = [[0]*200 for _ in range(SITENUM)]
fxvie0.GangRelay(fxvie1, fxvie2)
fxvie0.GangSet(1)
delay_ms(1)
fxvie0.GangMeasure(200, 10)
for i in range(SITENUM):
    fxvie0.GangBlockRead(i, 0, 200, result[i], MVRET)
fxvie0.GangReset()
```

### GangReset() -- Reset Gang mode
**Signature:** `int GangReset()`
**Remarks:** Resets parallel mode. Restores to FV=0, VRNG=30V, IRNG=1MA, RelayOff. Must call before any non-Gang operation.
**Example:**
```python
fxvie0.GangRelay(fxvie1, fxvie2)
fxvie0.GangSet(1)
fxvie0.GangMeasure(20, 10)
fxvie0.GangReset()
```

---

## Section 11: TMU Channel Routing

### TMUChannel() -- Route channel to TMU
**Signature:** `int TMUChannel(FXVIe FXVIeChannel)`
**Parameters:**
- `FXVIeChannel` [FXVIe]: Channel to give TMU capability via internal bus.
**Remarks:**
- Does NOT support Group.
- TMU channel and bridged channel must have same site attribute (both multi-site or both NO_SITE).
- Same site: both must be in same bank.
- Different sites: both must be in different banks.
- After TMUChannel (before TMUChannelReset): GangRelay invalid for all same-bank channels.
- After TMUChannel (before TMUChannelReset): Set function invalid for TMU and bridged channels.
- Each bank has one internal bus; only one channel can connect to TMU at a time.
**Example:**
```python
fxvie0 = FXVIe("S18_0,S18_6",  "fxvie0")
fxvie4 = FXVIe("S18_4,S18_10", "fxvie4")
fxvie4.TMUChannel(fxvie0)
fxvie4.TMUConnect()
fxvie4.TMUStart(FXVIe_10V, FXVIe_TMU_POS, 3, FXVIe_FILTER_PASS, 100)
fxvie4.TMUStop(FXVIe_10V, FXVIe_TMU_NEG, 3, FXVIe_FILTER_PASS, 100)
fxvie4.TMUMeasure(FXVIe_MEAS_TIME, 1, 1.0, FXVIe_TRANGE_MS)
for i in range(STS_SITE_NUM):
    Time_Result[i] = fxvie4.TMUGetMeasResult(i)
fxvie4.TMUDisconnect()
fxvie4.TMUChannelReset()
```

### TMUChannelReset() -- Reset TMU channel routing
**Signature:** `int TMUChannelReset()`
**Remarks:** Resets TMU channel bridging. Relay returns to RelayOff. Must call before non-TMU operations.
**Example:**
```python
fxvie4.TMUChannel(fxvie0)
fxvie4.TMUChannelReset()
```

---

## Section 12: Turbo Mode

### TSet() -- Turbo Set
**Signature:** `int TSet(VIMode viMode, double setValue, FXVIe_VRNG vRange, FXVIe_IRNG iRange, FXVIe_OUT_RELAY relayStatus = FXVIe_RELAY_HOLD, double risingTime = 0.02)`
**Parameters:** Same as Set().
**Remarks:**
- Differences from Set():
  - a. Set() returns when target state is reached; TSet() only sets target state, use STSTArming() to wait for completion.
  - b. Set() Group requires all channels have same VI mode, range, relay; TSet() Group has NO such requirement.
- Multiple channels can chain TSet() calls, then one STSTArming() waits for all -- saves test time.
- Requires: AccoTestSystem Version 2100 build200814_rp2.0+ and FXVIe B-module logic >= 0x12.
**Example:**
```python
fxvie0.TSet(FV, 4, FXVIe_5V, FXVIe_100MA, FXVIe_RELAY_ON)
fxvie1.TSet(FV, 1.5, FXVIe_2V, FXVIe_10MA, FXVIe_RELAY_ON)
STSTArming()  # Wait for all to complete

# Group with TSet (no range consistency requirement)
gpfxvie.TSet(FV, 0, FXVIe_10V, FXVIe_1MA, FXVIe_RELAY_OFF)
STSTArming()
```

---

## Section 13: Alarm Control

### SetAlarmMask() -- Mask/suppress alarm
**Signature:** `void SetAlarmMask(UINT siteCount, bool status = true)`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, ...
- `status` [bool]: `true` = mask alarm, `false` = output alarm. Default: `true`.
**Remarks:** Alarm mask is reinitialized by InitBeforeTestFlow().
**Example:**
```python
fxvie0.SetAlarmMask(0)  # mask SITE1 alarm (e.g., over-range alarm suppressed)
fxvie0.Set(FV, 5, FXVIe_10V, FXVIe_10MA, FXVIe_RELAY_ON)
```

### GetAlarmMask() -- Get alarm mask status
**Signature:** `bool GetAlarmMask(UINT siteCount)`
**Parameters:**
- `siteCount` [UINT]: Site index.
**Return:** `true` = masked, `false` = outputting.
**Example:**
```python
status = fxvie0.GetAlarmMask(0)
```

---

## Section 14: Board Info

### GetBoardSN() -- Get board serial number
**Signature:** `int GetBoardSN(UINT siteCount, char* boardSN, UINT snSize)`
**Parameters:**
- `siteCount` [UINT]: Site index.
- `boardSN` [char*]: Buffer for serial number. Returns empty string if not stored or invalid site.
- `snSize` [UINT]: Size of boardSN buffer.
**Example:**
```python
boardSN = [0]*255
fxvie0.GetBoardSN(0, boardSN, 255)
```

---

## Section 15: Calibration Functions

### GetCalibrationTime() -- Get calibration date
**Signature:** `SYSTEMTIME GetCalibrationTime(UINT siteCount) const`
**Parameters:**
- `siteCount` [UINT]: Site index.
**Return:** Calibration date (SYSTEMTIME struct). Abnormal: 1970-1-18:0:0 (uncalibrated or invalid site).
**Example:**
```python
calDate = fxvie0.GetCalibrationTime(0)
```

### GetCalibrationTemperature() -- Get calibration temperature
**Signature:** `double GetCalibrationTemperature(UINT siteCount) const`
**Parameters:**
- `siteCount` [UINT]: Site index.
**Return:** Calibration temperature, or 0 if abnormal (uncalibrated or invalid site).
**Example:**
```python
calTemperature = fxvie0.GetCalibrationTemperature(0)
```

### GetCalibrationHumidity() -- Get calibration humidity
**Signature:** `double GetCalibrationHumidity(UINT siteCount) const`
**Parameters:**
- `siteCount` [UINT]: Site index.
**Return:** Calibration humidity, or 0 if abnormal.
**Example:**
```python
calHumidity = fxvie0.GetCalibrationHumidity(0)
```

### GetCalibrationResult() -- Get calibration result
**Signature:** `CAL_RESULT GetCalibrationResult(UINT siteCount) const`
**Parameters:**
- `siteCount` [UINT]: Site index.
**Return:** `CAL_PASS`, `CAL_FAIL`, or `STS_NO_RESULT_RECORD` (uncalibrated or invalid site).
**Example:**
```python
calResult = fxvie0.GetCalibrationResult(0)
```

### GetCalibrationLogicRev() -- Get calibration logic version
**Signature:** `int GetCalibrationLogicRev(UINT siteCount) const`
**Parameters:**
- `siteCount` [UINT]: Site index.
**Return:** Logic version number, or 255 if abnormal.
**Example:**
```python
calLogicRev = fxvie0.GetCalibrationLogicRev(0)
```

### GetCalibrationMeter() -- Get calibration meter info
**Signature:** `CAL_METER GetCalibrationMeter(UINT siteCount, char* meterSN = NULL, UINT snSize = 0)`
**Parameters:**
- `siteCount` [UINT]: Site index.
- `meterSN` [char*]: Buffer for meter serial number. Returns "N/A" if abnormal. Default NULL (don't read SN).
- `snSize` [UINT]: Size of meterSN buffer. Default 0.
**Return:** Meter type enum: `STS_KEITHLEY2000`, `STS_AGILENT34401`, `STS_AGILENT3458A`, or `STS_NO_METER_RECORD` (abnormal).
**Example:**
```python
calMeterSN = [0]*255
calMeterType = fxvie0.GetCalibrationMeter(0, calMeterSN, 255)
```

### GetCalibrationCalBoardInfo() -- Get calibration board info
**Signature:** `int GetCalibrationCalBoardInfo(UINT siteCount, char* boardSN = NULL, UINT snSize = 0, char* boardHdRev = NULL, UINT revSize = 0)`
**Parameters:**
- `siteCount` [UINT]: Site index.
- `boardSN` [char*]: Buffer for calibration board serial number. Returns "N/A" if abnormal. Default NULL.
- `snSize` [UINT]: Size of boardSN buffer. Default 0.
- `boardHdRev` [char*]: Buffer for hardware revision. Returns "N/A" if abnormal. Default NULL.
- `revSize` [UINT]: Size of boardHdRev buffer. Default 0.
**Return:** Calibration board logic version, or 255 if abnormal.
**Example:**
```python
boardSN = [0]*255
boardHdRev = [0]*255
logicRev = fxvie0.GetCalibrationCalBoardInfo(0, boardSN, 255, boardHdRev, 255)
```

### GetCalibrationSoftRev() -- Get calibration software version
**Signature:** `int GetCalibrationSoftRev(UINT siteCount, char* softRev, UINT revSize)`
**Parameters:**
- `siteCount` [UINT]: Site index.
- `softRev` [char*]: Buffer for software version string. Returns "N/A" if abnormal.
- `revSize` [UINT]: Size of softRev buffer.
**Return:** 0 = normal, non-zero = abnormal (uncalibrated or invalid site).
**Example:**
```python
softRev = [0]*255
fxvie0.GetCalibrationSoftRev(0, softRev, 255)
```

### GetCalibrationSlotID() -- Get calibration slot ID
**Signature:** `int GetCalibrationSlotID(UINT siteCount) const`
**Parameters:**
- `siteCount` [UINT]: Site index.
**Return:** Slot ID at calibration time, or 0 if abnormal.
**Example:**
```python
slotID = fxvie0.GetCalibrationSlotID(0)
```

---

## Section 16: Programming Examples

### Example 1: Concatenated AWG waveforms
```python
sam = 400
interval = 200
awg_pattern = [0]*1000
STSAWGCreateSineData(awg_pattern[0:100],   100, 1, -5, 0, 180)   # sine at addr 0
STSAWGCreateTriangleData(awg_pattern[100:], 100, 4, -5, 0, 0)    # triangle at addr 100
STSAWGCreateSquareData(awg_pattern[200:],   100, 4, -5, 0, 50)   # square at addr 200
STSAWGCreateRampData(awg_pattern[300:],     100, 1, 1, 5)        # ramp at addr 300
fxvie0.AwgLoader("Vcc_awg", FV, FXVIe_10V, FXVIe_10MA, awg_pattern, sam)
fxvie0.Set(FV, 0, FXVIe_10V, FXVIe_10MA, FXVIe_RELAY_ON)
fxvie0.AwgSelect("Vcc_awg", 0, sam-1, sam-1, interval)
fxvie0.MeasureVI(sam, interval, FXVIe_MI_X1, MEAS_AWG)
STSEnableAWG(fxvie0)
STSEnableMeas(fxvie0)
STSAWGRun()
```

### Example 2: PSRR test with AWG sine wave
```python
# fxvie0 outputs 120Hz sine (Vpp=0.66V, DC=3.3V), fxvie1 measures PSRR
sam = 830
interval = 10
awg_pattern = [0]*1000
STSAWGCreateSineData(awg_pattern, sam, 1, 0.66, 3.3, 0)
fxvie0.AwgLoader("Sin_AWG", FV, FXVIe_10V, FXVIe_1A, awg_pattern, sam)
fxvie0.Set(FV, 0, FXVIe_10V, FXVIe_1A, FXVIe_RELAY_ON)
fxvie0.AwgRun("Sin_AWG", 0, sam-1, 0, interval, AWG_LOOP)
delay_ms(1)
fxvie1.Set(FI, -100e-3, FXVIe_10V, FXVIe_100MA, FXVIe_RELAY_ON)
delay_ms(2)
fxvie1.MeasureVI(AD_SAMPLE, 20)
# ... compute PSRR from samples
fxvie0.AwgStop()
```

### Example 3: Same-source AWG trigger
```python
# fxvie0 ramps from 16.5V to 21.5V, triggers on current >200uA
awg_pattern = [0]*100
STSAWGCreateRampData(awg_pattern, sam, 1, 16.5, 21.5)
fxvie0.AwgLoader("Vst", FV, FXVIe_30V, FXVIe_100MA, awg_pattern, sam)
fxvie0.Set(FV, 16.5, FXVIe_30V, FXVIe_100MA, FXVIe_RELAY_ON)
fxvie0.AwgSelect("Vst", 0, sam-1, sam-1, interval)
fxvie0.MeasureVI(sam, interval, FXVIe_MI_X1, MEAS_AWG)
fxvie0.SetMeasITrig(200e-6, TRIG_RISING)
STSEnableAWG(fxvie0)
STSEnableMeas(fxvie0)
STSAWGRun()
for i in range(SITENUM):
    Trig_Point[i] = fxvie0.GetMeasResult(i, MIRET, TRIG_RESULT)
    result[i] = fxvie0.GetMeasResult(i, MVRET, Trig_Point[i])
```

### Example 4: Separate AWG source and trigger
```python
# fxvie0 ramps 0.35V-0.45V, fxvie1 triggers on V<2V, read fxvie0 voltage at trigger
fxvie1.Set(FI, 0, FXVIe_10V, FXVIe_1MA, FXVIe_RELAY_ON)
delay_ms(1)
awg_pattern = [0]*100
STSAWGCreateRampData(awg_pattern, sam, 1, 0.35, 0.45)
fxvie0.AwgLoader("Vcspre_AWG", FV, FXVIe_3p6V, FXVIe_100MA, awg_pattern, sam)
fxvie0.Set(FV, 0.30, FXVIe_3p6V, FXVIe_100MA, FXVIe_RELAY_ON)
fxvie0.AwgSelect("Vcspre_AWG", 0, sam-1, sam-1, interval)
fxvie1.SetMeasVTrig(2, TRIG_FALLING)
fxvie0.MeasureVI(sam, interval, FXVIe_MI_X1, MEAS_AWG)
fxvie1.MeasureVI(sam, interval, FXVIe_MI_X1, MEAS_AWG)
STSEnableAWG(fxvie0)
STSEnableMeas(fxvie0, fxvie1)
STSAWGRun()
for i in range(SITENUM):
    Trig_Point[i] = fxvie1.GetMeasResult(i, MVRET, TRIG_RESULT)
    result[i] = fxvie0.GetMeasResult(i, MVRET, Trig_Point[i])
```

### Example 5: Propagation delay test (MAX809)
```python
# VCC (fxvie0) rises 0->5V, measure delay to Reset (fxvie1) trigger >2V
Trig = 2
awg_pattern = [0]*100
awg_pattern[0] = 0
awg_pattern[sam-1] = 5
fxvie1.Set(FI, 0, FXVIe_10V, FXVIe_1MA, FXVIe_RELAY_ON)
delay_ms(1)
fxvie0.AwgLoader("VCC_AWG", FV, FXVIe_10V, FXVIe_100MA, awg_pattern, sam)
fxvie0.Set(FV, 0, FXVIe_10V, FXVIe_100MA, FXVIe_RELAY_ON)
fxvie0.AwgSelect("VCC_AWG", 0, sam-1, sam-1, interval)
fxvie1.SetMeasVTrig(Trig, TRIG_RISING)
fxvie0.MeasureVI(2000, interval, FXVIe_MI_X1, MEAS_AWG)
fxvie1.MeasureVI(2000, interval, FXVIe_MI_X1, MEAS_AWG)
STSEnableAWG(fxvie0)
STSEnableMeas(fxvie0, fxvie1)
STSAWGRun()
for i in range(SITENUM):
    Trig_Point[i] = fxvie1.GetMeasResult(i, MVRET, TRIG_RESULT)
    T_delay = (Trig_Point[i]-1) * interval_Meas / 1000  # ms
```

### Example 6: Gang parallel high current
```python
# 6 channels in parallel, 1.2A output
fxvie0.Set(FV, 5, FXVIe_10V, FXVIe_1MA, FXVIe_RELAY_ON)
fxvie1.Set(FV, 2, FXVIe_10V, FXVIe_1MA, FXVIe_RELAY_ON)
delay_ms(1)
fxvie0.Set(FV, 0, FXVIe_10V, FXVIe_1MA, FXVIe_RELAY_ON)
fxvie1.Set(FV, 0, FXVIe_10V, FXVIe_1MA, FXVIe_RELAY_ON)
delay_ms(1)
fxvie0.GangRelay(fxvie1, fxvie2, fxvie3, fxvie4, fxvie5)
delay_ms(1)
fxvie0.GangSet(1.2, 0.02)
delay_ms(1)
fxvie0.GangMeasure(100, 10)
for i in range(STS_SITE_NUM):
    Gang_V_Result[i] = fxvie0.GangGetMeasResult(i, MVRET)
    Gang_I_Result[i] = fxvie0.GangGetMeasResult(i, MIRET)
fxvie0.GangSet(0, 0.02)
delay_ms(1)
fxvie0.GangReset()
# ... restore normal operation
```

### Example 7: TMU -- rise time
```python
# Measure rise time Tr (1.5V to 13.5V)
fxvie0.TMUConnect()
fxvie0.TMUSetInSource()
fxvie0.TMUStart(FXVIe_30V, FXVIe_TMU_POS, 1.5, FXVIe_FILTER_PASS)
fxvie0.TMUStop(FXVIe_30V, FXVIe_TMU_POS, 13.5, FXVIe_FILTER_PASS)
fxvie0.TMUMeasure(FXVIe_MEAS_TIME, 1, 3, FXVIe_TRANGE_MS)
for i in range(SITENUM):
    val[i] = fxvie0.TMUGetMeasResult(i, AVERAGE_RESULT)  # us
fxvie0.TMUDisconnect()
```

### Example 8: TMU -- TPLH (dual-signal)
```python
# Two signals: signalA on fxvie0, signalB on fxvie1
fxvie0.TMUConnect()
fxvie1.TMUConnect()
fxvie0.TMUSetMatrix(fxvie0, fxvie1)
fxvie0.TMUStart(FXVIe_30V, FXVIe_TMU_NEG, 2.5, FXVIe_FILTER_PASS)
fxvie0.TMUStop(FXVIe_30V, FXVIe_TMU_POS, 7.7, FXVIe_FILTER_PASS)
fxvie0.TMUMeasure(FXVIe_MEAS_TIME, 1, 10, FXVIe_TRANGE_US)
for i in range(SITENUM):
    val[i] = fxvie0.TMUGetMeasResult(i, AVERAGE_RESULT)  # us
fxvie0.TMUDisconnect()
fxvie1.TMUDisconnect()
```

### Example 9: TMU -- event skip (P2 to N3)
```python
# Skip 1 Start event, capture 2nd rising edge; skip 2 Stop events, capture 3rd falling edge
fxvie0.TMUConnect()
fxvie0.TMUSetInSource()
fxvie0.TMUStart(FXVIe_10V, FXVIe_TMU_POS, 2.5, FXVIe_FILTER_PASS, 10, 0, 1)   # skip 1
fxvie0.TMUStop(FXVIe_10V, FXVIe_TMU_NEG, 2.4, FXVIe_FILTER_PASS, 10, 0, 2)    # skip 2
fxvie0.TMUMeasure(FXVIe_MEAS_TIME, 1, 10, FXVIe_TRANGE_US)
for i in range(SITENUM):
    val[i] = fxvie0.TMUGetMeasResult(i, AVERAGE_RESULT)
fxvie0.TMUDisconnect()
```

### Example 10: TMU -- frequency
```python
fxvie0.TMUConnect()
fxvie0.TMUSetInSource()
fxvie0.TMUStart(FXVIe_10V, FXVIe_TMU_POS, 2.0, FXVIe_FILTER_PASS, 10)
fxvie0.TMUMeasure(FXVIe_MEAS_FREQ, 1, 10, FXVIe_TRANGE_US)
for i in range(SITENUM):
    val[i] = fxvie0.TMUGetMeasResult(i, AVERAGE_RESULT)  # KHz
fxvie0.TMUDisconnect()
```

### Example 11: TMU -- high duty cycle
```python
fxvie0.TMUConnect()
fxvie0.TMUSetInSource()
fxvie0.TMUStart(FXVIe_10V, FXVIe_TMU_POS, 2.1, FXVIe_FILTER_PASS, 10)
fxvie0.TMUStop(FXVIe_10V, FXVIe_TMU_NEG, 2.0, FXVIe_FILTER_PASS, 10)
fxvie0.TMUMeasure(FXVIe_MEAS_HIGH_DUTY, 20, 10, FXVIe_TRANGE_MS)
for i in range(SITENUM):
    val[i] = fxvie0.TMUGetMeasResult(i, AVERAGE_RESULT)  # %
fxvie0.TMUDisconnect()
```

### Example 12: TMU -- event counting
```python
# Capture 5 transition moments (T0-T4)
Tevent = [[0]*SITENUM for _ in range(5)]
fxvie0.TMUConnect()
fxvie0.TMUSetInSource()
fxvie0.TMUStart(FXVIe_10V, FXVIe_TMU_POS, 2.5, FXVIe_FILTER_PASS, 10)
fxvie0.TMUStop(FXVIe_10V, FXVIe_TMU_NEG, 2.4, FXVIe_FILTER_PASS, 10)
fxvie0.TMUMeasure(FXVIe_MEAS_EVENT, 5, 10, FXVIe_TRANGE_MS)
for i in range(SITENUM):
    for j in range(5):
        Tevent[j][i] = fxvie0.TMUGetMeasResult(i, j)  # j-th event moment
fxvie0.TMUDisconnect()
```
