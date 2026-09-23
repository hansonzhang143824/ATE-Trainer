> 迁移自 auto-memory `STS8300-hpvie.md`（2026-08-16）


# HPVIe -- High Power VI Source Meter

## HPVIe() -- Constructor
**Signature:** `HPVIe(char* channelList, char* chName = NULL);`
**Parameters:**
- `channelList` [char*]: HPVIe bound channel string, format `"S4_0"` where `S4` is slot 4 and `0` is the board index. One board has at most 1 channel, so the board index max is 0.
- `chName` [char*, optional]: Custom channel name. Default NULL, system names it `HPVIe_xx`.
**Remarks:** Defines an HPVIe channel and specifies its physical channel info (slot number + board index).
**Example:**
```python
# System has 2 HPVIe boards (Slot4 and Slot12), two-site parallel operation
HPVIe hpvie0("S4_0,S12_0");
# Site binding:
STSSetMultiSiteBind(MD_HPVIe, SITE_1, "S4_0");  # Slot4 ch0 to SITE1
STSSetMultiSiteBind(MD_HPVIe, SITE_2, "S12_0"); # Slot12 ch0 to SITE2
```

---

## Set() -- Set HPVIe state
**Signature:** `int Set(VIMode viMode, double setValue, HPVIe_VRNG vRange, HPVIe_IRNG iRange, HPVIe_OUT_RELAY relayStatus = HPVIe_RELAY_HOLD, double risingTime = 0.2);`
**Parameters:**
- `viMode` [VIMode]: Operating mode. Values: `FV` (constant voltage), `FI` (constant current).
- `setValue` [double]: Set voltage or current value.
  - FV mode: voltage in V, range -100 to 100.
  - FI mode: current in A, range -100 to 100.
- `vRange` [HPVIe_VRNG]: Voltage range. Values: `HPVIe_100V`, `HPVIe_40V`, `HPVIe_20V`, `HPVIe_10V`, `HPVIe_5V`, `HPVIe_2V`.
- `iRange` [HPVIe_IRNG]: Current range. Values: `HPVIe_100A`, `HPVIe_50A`, `HPVIe_20A`, `HPVIe_10A`, `HPVIe_2A`, `HPVIe_1A`, `HPVIe_100MA`, `HPVIe_10MA`, `HPVIe_1MA`, `HPVIe_100UA`, `HPVIe_10UA`.
- `relayStatus` [HPVIe_OUT_RELAY, optional]: Output relay action. Values:
  - `HPVIe_RELAY_ON`: Turn on output relay.
  - `HPVIe_RELAY_FANOUT_ON`: Turn on FANOUT output relay.
  - `HPVIe_RELAY_ALL_ON`: Turn on both relay and FANOUT Force relay (for 100A test connection, reduces transmission loss).
  - `HPVIe_RELAY_OFF`: Turn off output relay.
  - `HPVIe_RELAY_SENSE_ON`: Independent measurement mode. Only SENSE line relay ON, FORCE line relay OFF. HPVIe acts as independent voltmeter.
  - `HPVIe_RELAY_SENSE_FANOUT_ON`: Independent measurement mode. Only SENSE line FANOUT relay ON, FORCE line relay OFF.
  - `HPVIe_RELAY_HOLD`: Hold previous relay state.
  Default: `HPVIe_RELAY_HOLD`.
- `risingTime` [double, optional]: Integration time in mS, resolution 0.1mS (for values >0.5mS). Default 0.2mS.
  - If <= 0.1mS: Fast mode (0.1mS).
  - If <= 0.2mS: Normal mode (0.2mS).
  - If <= 0.5mS: Slow mode (0.5mS).
  - If > 0.5mS: Capload mode enabled, risingTime is Capload rise/fall time (smoother edges, max 65mS).
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Sets HPVIe state including operating mode, constant voltage/current value, V/I ranges, output relay status, and Capload time.
**Example:**
```python
# Example 1: Set hpvie0 voltage output 5V, risingTime defaults to 0.2mS
hpvie0.Set(FV, 5, HPVIe_10V, HPVIe_100MA, HPVIe_RELAY_ON);

# Example 2: Set hpvie0 voltage output 5V, risingTime = 3mS (Capload)
hpvie0.Set(FV, 0, HPVIe_10V, HPVIe_100MA, HPVIe_RELAY_ON);
delay_ms(1);
hpvie0.Set(FV, 5, HPVIe_10V, HPVIe_100MA, HPVIe_RELAY_ON, 3);
```

---

## SetSyn() -- Synchronous set for multiple sites
**Signature:** `int SetSyn(VIMode viMode, const double* setValue, UINT siteSize, HPVIe_VRNG vRange, HPVIe_IRNG iRange, HPVIe_OUT_RELAY relayStatus = HPVIe_RELAY_HOLD, double risingTime = 0.2);`
**Parameters:**
- `viMode` [VIMode]: Operating mode. Values: `FV` (constant voltage), `FI` (constant current).
- `setValue` [const double*]: Array of set values for each site. FV mode: voltage in V (range -100 to 100). FI mode: current in A (range -100 to 100).
- `siteSize` [UINT]: Number of sites for synchronous operation. If siteSize=4, SITE1-SITE4 execute synchronously.
  - setValue array length must be greater than siteSize.
  - If siteSize < current valid site count, unspecified sites keep their previous state.
  - If siteSize > current valid site count, only valid sites are processed.
- `vRange` [HPVIe_VRNG]: Voltage range (same values as Set).
- `iRange` [HPVIe_IRNG]: Current range (same values as Set).
- `relayStatus` [HPVIe_OUT_RELAY, optional]: Output relay action (same values as Set). Default `HPVIe_RELAY_HOLD`.
- `risingTime` [double, optional]: Integration time in mS (same behavior as Set). Default 0.2mS.
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Sets different voltage/current values for different sites, fully synchronous across sites.
**Example:**
```python
# SITE1 outputs 3V, SITE2 outputs 5V, synchronous, default risingTime
double setValue[2] = {3, 5};
int siteSize = 2;
hpvie0.SetSyn(FV, setValue, siteSize, HPVIe_10V, HPVIe_100MA, HPVIe_RELAY_ON);

# With 3mS risingTime (Capload)
double setValue[2] = {3, 5};
int siteSize = 2;
hpvie0.Set(FV, 0, HPVIe_10V, HPVIe_100MA, HPVIe_RELAY_ON);
delay_ms(1);
hpvie0.SetSyn(FV, setValue, siteSize, HPVIe_10V, HPVIe_100MA, HPVIe_RELAY_ON, 3);
```

---

## SetClamp() -- Set clamp values
**Signature:** `int SetClamp(double percent_PFS, double percent_NFS);`
**Parameters:**
- `percent_PFS` [double]: Positive clamp as percentage of positive full-scale range, in %. Range: 10 to 110.
- `percent_NFS` [double]: Negative clamp as percentage of negative full-scale range, in %. Range: 10 to 110.
**Return:**
- `3`: Both positive and negative clamps changed.
- `2`: Only negative clamp changed.
- `1`: Only positive clamp changed.
- `0`: Neither clamp changed.
- `-1`: Function call failed.
**Remarks:** Sets HPVIe positive/negative clamp values. Important: Clamp setting is mode-dependent. Switching between FV and FI modes clears the clamp setting and auto-restores to 110%. Clamp setting is preserved when staying in the same mode (FV to FV, or FI to FI).
**Example:**
```python
# Set hpvie1 FI=0 mode, clamp to (50,20), then switch to FV=1V, clamp to (25,25)
hpvie1.Set(FI, 0, HPVIe_10V, HPVIe_10MA, HPVIe_RELAY_ON);
hpvie1.SetClamp(50, 20);  # Positive clamp 50% of FS(10V), negative 20%
# Switching FI->FV restores clamps to 110% automatically
hpvie1.Set(FV, 0, HPVIe_10V, HPVIe_100MA, HPVIe_RELAY_ON);
hpvie1.SetClamp(25, 25);  # Reset clamp
hpvie1.Set(FV, 1, HPVIe_10V, HPVIe_100MA, HPVIe_RELAY_ON);

# Example 2: Same mode (FV->FV), clamp preserved, then restored to 100%
hpvie1.Set(FV, 0, HPVIe_10V, HPVIe_100MA, HPVIe_RELAY_ON);
hpvie1.SetClamp(50, 25);
hpvie1.Set(FV, 1, HPVIe_10V, HPVIe_100MA, HPVIe_RELAY_ON);
delay_ms(1);
hpvie1.Set(FV, 35, HPVIe_40V, HPVIe_100MA, HPVIe_RELAY_ON);  # Clamp unchanged (same FV mode)
hpvie1.MeasureVI(100, 20);
hpvie1.Set(FV, 0, HPVIe_40V, HPVIe_100MA, HPVIe_RELAY_ON);
hpvie1.SetClamp(100, 100);  # Restore clamps
```

---

## MeasureVI() -- Configure measurement
**Signature:** `int MeasureVI(UINT sampleTimes, double samplePeriod, HPVIe_MV_GAIN mvGain = HPVIe_MV_X1, HPVIe_MI_GAIN miGain = HPVIe_MI_X1, FLOATMEASMODE measMode = MEAS_NORMAL, UINT T1 = 0, UINT T2 = 0, UINT T3 = 0, UINT T4 = 0);`
**Parameters:**
- `sampleTimes` [UINT]: Number of AD samples. Range: 1 to 4096. Clamped if out of range.
- `samplePeriod` [double]: Time interval between samples, in uS. Min 1uS, resolution 1uS. Range: 1 to 30000. Clamped if out of range.
- `mvGain` [HPVIe_MV_GAIN, optional]: Voltage measurement gain. Values: `HPVIe_MV_X1`, `HPVIe_MV_X2`, `HPVIe_MV_X5`, `HPVIe_MV_X10`. Default `HPVIe_MV_X1`.
- `miGain` [HPVIe_MI_GAIN, optional]: Current measurement gain. Values: `HPVIe_MI_X1`, `HPVIe_MI_X2`, `HPVIe_MI_X5`, `HPVIe_MI_X10`. Default `HPVIe_MI_X1`.
- `measMode` [FLOATMEASMODE, optional]: Measurement mode.
  - `MEAS_NORMAL`: Normal measurement. Function completes measurement on call.
  - `MEAS_AWG`: AWG measurement mode. Only configures, measurement starts when AWG runs.
  Default `MEAS_NORMAL`.
- `T1, T2, T3, T4` [UINT, optional]: Measurement start times in uS for AWG mode. Resolution 10uS. Range: 0 to ~600000 (T1+T2+T3+T4 total). Up to 4 measurement starts per AWG. All default to 0 (single measurement at time 0). T2 is relative to T1, T3 relative to T2, T4 relative to T3.
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Configures measurement count, interval, voltage gain, current gain, measurement mode, and AWG-mode measurement start times. Both voltage and current are measured simultaneously; user only chooses which to read back via GetMeasResult().
**Example:**
```python
# Normal mode: 20 samples, 5uS interval
hpvie0.MeasureVI(20, 5);
```

---

## GetMeasResult() -- Get measurement result
**Signature:** `double GetMeasResult(UINT siteCount, MeasRet retType = MVRET, int sampleNumber = AVERAGE_RESULT, BYTE triggerNum = 0);`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2... If channel defined as NO_SITE, any value works.
- `retType` [MeasRet, optional]: Data type to read back. Values:
  - `MVRET`: Read back voltage measurement data (unit: V).
  - `MIRET`: Read back current measurement data (unit: A).
  Default `MVRET`.
- `sampleNumber` [int, optional]: Which result to return. Values:
  - `AVERAGE_RESULT`: Average of all samples.
  - `MAX_RESULT`: Maximum value among samples.
  - `MIN_RESULT`: Minimum value among samples.
  - `TRIG_RESULT`: Trigger position (for AWG sync). Returns which sample point transitioned. Supports up to 2 triggers.
  - Non-negative N: Returns value of the (N+1)th sample point (0 <= N <= sampleTimes-1).
  Default `AVERAGE_RESULT`.
- `triggerNum` [BYTE, optional]: Trigger number (only valid when sampleNumber=TRIG_RESULT). 0=first trigger position, 1=second trigger position. Default 0.
**Return:** Measured value (voltage in V for MVRET, current in A for MIRET). Returns -3 if no trigger occurred. Returns -5 if measurement mode doesn't match readback mode.
**Remarks:** Gets measurement result from MeasureVI(). Voltage and current are measured simultaneously; select MVRET or MIRET to read back the desired type.
**Example:**
```python
# Example 1: Read back current average
hpvie0.MeasureVI(20, 5);
for (i = 0; i < SITENUM; i++) {
    adresult[i] = hpvie0.GetMeasResult(i, MIRET);
}

# Example 2: Read back 15th voltage sample point
hpvie0.MeasureVI(20, 5);
for (i = 0; i < SITENUM; i++) {
    adresult[i] = hpvie0.GetMeasResult(i, MVRET, 14);
}

# Example 3: AWG sync measurement, read trigger positions
hpvie1.MeasureVI(50, 20, HPVIe_MV_X1, HPVIe_MI_X1, MEAS_AWG);
hpvie0.MeasureVI(50, 20, HPVIe_MV_X1, HPVIe_MI_X1, MEAS_AWG);
hpvie0.SetMeasVTrig(2, TRIG_FALLING);
STSEnableAWG(&hpvie1);
STSEnableMeas(&hpvie1, &hpvie0);
STSAWGRun();
for (i = 0; i < SITENUM; i++) {
    Trig_Point0[i] = hpvie1.GetMeasResult(0, MVRET, TRIG_RESULT, 0);  # First trigger
    Trig_Point1[i] = hpvie1.GetMeasResult(0, MVRET, TRIG_RESULT, 1);  # Second trigger
}
```

---

## BlockRead() -- Block read measurement results
**Signature:** `int BlockRead(UINT siteCount, UINT start, UINT size, double* buffer, MeasRet retType = MVRET);`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
- `start` [UINT]: Start address of data block, non-negative. Range: 0 to (sampleTimes-1) from MeasureVI.
- `size` [UINT]: Data block size, positive. Range: 1 to (sampleTimes - start).
- `buffer` [double*]: User-defined array to store results, e.g. `double result[1000] = {0.0};`. Buffer length must be >= size. Recommend defining as global variable.
- `retType` [MeasRet, optional]: Data type. `MVRET` (voltage) or `MIRET` (current). Default `MVRET`.
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Reads a block of measurement results. Start address and size are user-defined.
**Example:**
```python
double result[SITENUM][200] = {0.0};
hpvie0.MeasureVI(200, 10);
for (i = 0; i < SITENUM; i++) {
    hpvie0.BlockRead(i, 0, 200, result[i], MVRET);
}
```

---

## Pulse() -- Output a voltage/current pulse
**Signature:** `int Pulse(double pulseValue, UINT pulseTime = 300, int measStartTime = 0, UINT sampleTimes = 10, double sampleInterval = 30, HPVIe_MV_GAIN mvGain = HPVIe_MV_X1, HPVIe_MI_GAIN miGain = HPVIe_MI_X1);`
**Parameters:**
- `pulseValue` [double]: Pulse amplitude. FV mode: V (-100 to 100). FI mode: A (-100 to 100).
- `pulseTime` [UINT, optional]: Pulse duration, in uS. Resolution 10uS. Range: 300 to 40000. Default 300uS.
  - Pulse setup speed depends on integration time and voltage range. At 0.2mS integration, 10V range full-scale setup is 200uS, 100V range is 500uS.
  - Current range max time limited by HPVIe output power curve.
- `measStartTime` [int, optional]: Measurement start time relative to pulse start, in uS. Range: -60000 to 60000. Default 0.
- `sampleTimes` [UINT, optional]: Number of samples. Range 1 to 4096. Default 10.
- `sampleInterval` [double, optional]: Sample interval, in uS. Min 1uS, resolution 1uS. Default 30uS.
- `mvGain` [HPVIe_MV_GAIN, optional]: Voltage measurement gain. Default `HPVIe_MV_X1`.
- `miGain` [HPVIe_MI_GAIN, optional]: Current measurement gain. Default `HPVIe_MI_X1`.
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Outputs a voltage or current pulse with adjustable amplitude and width. Must call Set() before Pulse() to configure range and relay. Pulse start and end values are both the Set() value.
**Example:**
```python
# hpvie0 start state FV=0. Output 8V pulse for 1mS. 200 samples, 10uS interval.
# Start measurement 500uS before pulse.
hpvie0.Set(FV, 0, HPVIe_10V, HPVIe_10MA, HPVIe_RELAY_ON);
hpvie0.Pulse(8, 1000, -500, 200, 10);
```

---

## AwgLoader() -- Load AWG waveform data
**Signature:** `int AwgLoader(char* awgName, VIMode viMode, HPVIe_VRNG vRange, HPVIe_IRNG iRange, double* awgData, UINT awgSize);`
**Parameters:**
- `awgName` [char*]: AWG waveform name. Case-insensitive.
- `viMode` [VIMode]: Operating mode. Values: `FV` (constant voltage), `FI` (constant current).
- `vRange` [HPVIe_VRNG]: Voltage range (used for data conversion only, no range switching).
- `iRange` [HPVIe_IRNG]: Current range (used for data conversion only, no range switching).
- `awgData` [double*]: Array storing AWG waveform data.
- `awgSize` [UINT]: AWG waveform data size. Range: 1 to 4096.
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Imports AWG waveform data. Notes:
- Range info is for data conversion only, does not switch ranges.
- One HPVIe channel can import multiple AWG waveforms, but each must have a unique name. Same-name waveforms only write the first call.
- Executing AwgLoader writes AWG data to RAM (takes ~5mS for 4096 points, time proportional to point count).
- Single test program: total AWG waveform length per channel must be <= 4096 (excess data not written to RAM).
- Recommend total length per channel < 4096 so data is cached (first-call-only time cost).
- If total > 4096, each call rewrites to RAM, increasing test time.
**Example:**
```python
# Ramp waveform: hpvie0 from 16.5V to 21.5V, step 0.1V
int sam = 50;
int interval = 200;
double awg_pattern[100] = {0.0};
STSAWGCreateRampData(&awg_pattern[0], sam, 1, 16.5, 21.5);
hpvie0.AwgLoader("Vst", FV, HPVIe_40V, HPVIe_100MA, awg_pattern, sam);

# Sine wave: 100Hz, amplitude 2V, DC offset 10V
sam = 1000;
interval = 10;
double awg_pattern[2000] = {0.0};
STSAWGCreateSineData(&awg_pattern[0], sam, 1, 4, 10, 0);  # Vpp=4, DC=10
hpvie0.AwgLoader("Sine", FV, HPVIe_10V, HPVIe_1MA, awg_pattern, sam);
```

---

## AwgSelect() -- Select AWG waveform for synchronous run
**Signature:** `int AwgSelect(char* awgName, UINT startAddr, UINT stopAddr, int loopBackAddr, double awgInterval = 10.0);`
**Parameters:**
- `awgName` [char*]: AWG waveform name. Must match the name used in AwgLoader.
- `startAddr` [UINT]: AWG waveform start point. Range: 0 to sam-1 (sam = AWG point count).
- `stopAddr` [UINT]: AWG waveform end point. Range: 0 to sam-1.
- `loopBackAddr` [int]: AWG waveform loop-back point (position after AWG finishes).
  - < 0: Stays at the position where AWG ended.
  - 0 to sam-1: Returns to the specified position after completion.
- `awgInterval` [double, optional]: AWG data interval time, in uS. Resolution 1uS. Range: 10 to 60000. Default 10uS.
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Selects the AWG waveform to run, sets start/stop/loop-back points and interval. Notes:
- One HPVIe channel can import multiple AWG waveforms; use AwgSelect to choose which to run.
- Must call Set() before AwgSelect; Set's ranges must exactly match AwgLoader's ranges.
- AwgSelect does NOT output AWG; only configures. Actual output requires STSAWGRun() (synchronous start function).
**Example:**
```python
# Two waveforms, only run AWG_Vst
double interval = 200;
int sam1 = 1000;
int sam2 = 500;
double awg_pattern1[1000] = {0.0};
double awg_pattern2[500] = {0.0};
STSAWGCreateRampData(&awg_pattern1[0], sam1, 1, 16.5, 21.5);
STSAWGCreateRampData(&awg_pattern2[0], sam2, 1, 16.5, 10.5);
hpvie0.AwgLoader("AWG_Vst", FV, HPVIe_40V, HPVIe_100MA, awg_pattern1, sam1);
hpvie0.AwgLoader("AWG_Vuvlo", FV, HPVIe_20V, HPVIe_100MA, awg_pattern2, sam2);
# Set range must match AWG_Vst's AwgLoader range
hpvie0.Set(FV, 16.5, HPVIe_40V, HPVIe_100MA, HPVIe_RELAY_ON);
hpvie0.AwgSelect("AWG_Vst", 0, sam1 - 1, 0, interval);
# ... setup measurement, enable ...
STSAWGRun();  # AWG synchronous start
```

---

## AwgRun() -- Run AWG standalone (single channel)
**Signature:** `int AwgRun(char* awgName, UINT startAddr, UINT stopAddr, int loopBackAddr, double awgInterval = 10.0, BOOL runMode = AWG_SINGLE, UINT delayTime_ms = 0);`
**Parameters:**
- `awgName` [char*]: AWG waveform name. Must match AwgLoader name.
- `startAddr` [UINT]: AWG waveform start point. Range: 0 to sam-1.
- `stopAddr` [UINT]: AWG waveform end point. Range: 0 to sam-1.
- `loopBackAddr` [int]: Loop-back point. < 0 stays at end position; 0 to sam-1 returns to specified point.
- `awgInterval` [double, optional]: AWG data interval time, in uS. Resolution 1uS. Range: 10 to 60000. Default 10uS.
- `runMode` [BOOL, optional]: Run mode. Values:
  - `AWG_SINGLE`: Run AWG waveform once (default).
  - `AWG_LOOP`: Loop AWG waveform continuously (stop with AwgStop()).
- `delayTime_ms` [UINT, optional]: Delay time in mS. Range: 0 to 60000. After this delay, system allows subsequent operations. If omitted, defaults to AWG scan time (blocks until AWG completes). **Recommendation: do not set this parameter.**
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Standalone AWG start for a single HPVIe channel. Notes:
- Must call Set() before AwgRun; Set's ranges must match AwgLoader's ranges.
- This function sets start/stop/loop-back and interval; no need for AwgSelect.
- Cannot synchronize measurement with other sources. For sync measurement, use AwgSelect + STSAWGRun.
**Example:**
```python
# hpvie0 continuously outputs 120Hz sine wave, amplitude 0.33V, DC offset 3.3V
int sam = 830;
double interval = 10;
double awg_pattern[1000] = {0.0};
STSAWGCreateSineData(&awg_pattern[0], sam, 1, 0.66, 3.3, 0);
hpvie0.AwgLoader("Sin_AWG", FV, HPVIe_5V, HPVIe_1A, awg_pattern, sam);
hpvie0.Set(FV, 0, HPVIe_5V, HPVIe_1A, HPVIe_RELAY_ON);
hpvie0.AwgRun("Sin_AWG", 0, sam - 1, 0, interval, AWG_LOOP);
```

---

## AwgStop() -- Stop AWG loop
**Signature:** `int AwgStop(void);`
**Parameters:** None
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Stops the AWG loop operation of an HPVIe channel.
**Example:**
```python
hpvie0.AwgStop();
```

---

## AwgClear() -- Clear AWG data
**Signature:** `int AwgClear(void);`
**Parameters:** None
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Typically called before AwgLoader to clear the HPVIe channel's AWG data.
**Example:**
```python
hpvie0.AwgClear();  # Clear AWG data of hpvie0
hpvie0.AwgLoader("P1", FV, HPVIe_40V, HPVIe_100MA, awg_pattern1, sam);
```

---

## SetMeasVTrig() -- Set voltage measurement trigger
**Signature:** `int SetMeasVTrig(double vTrig, TRIG_MODE trigMode = TRIG_FALLING, double hysteresisValue = 0.0);`
**Parameters:**
- `vTrig` [double]: Trigger voltage threshold, in V. Related to the voltage range set by Set().
- `trigMode` [TRIG_MODE, optional]: Trigger mode. Values:
  - `TRIG_FALLING`: Falling edge trigger (default).
  - `TRIG_RISING`: Rising edge trigger.
- `hysteresisValue` [double, optional]: Hysteresis value for trigger voltage, in V. Must be non-negative. Default 0.0.
  - Rising edge: trigger fires when measurement goes below (vTrig-hysteresisValue) then above vTrig.
  - Falling edge: trigger fires when measurement goes above (vTrig+hysteresisValue) then below vTrig.
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Voltage measurement trigger configuration. Critical constraint: between SetMeasVTrig and MeasureVI calls, the voltage/current ranges and measurement gain settings must remain consistent. Do not insert any function that changes range or gain between them.
**Example:**
```python
# Correct approach:
hpvie0.MeasureVI(sam, interval, HPVIe_MV_X1, HPVIe_MI_X1, MEAS_AWG);
hpvie1.MeasureVI(sam, interval, HPVIe_MV_X1, HPVIe_MI_X1, MEAS_AWG);
hpvie1.SetMeasVTrig(Trig, TRIG_FALLING);  # Trigger at 2V, falling edge
STSEnableAWG(&hpvie0);
STSEnableMeas(&hpvie0, &hpvie1);
STSAWGRun();

# WRONG approach (inserting Set between MeasureVI and SetMeasVTrig):
hpvie0.MeasureVI(sam, interval, HPVIe_MV_X1, HPVIe_MI_X1, MEAS_AWG);
hpvie1.MeasureVI(sam, interval, HPVIe_MV_X1, HPVIe_MI_X1, MEAS_AWG);
hpvie1.Set(FI, 0, HPVIe_5V, HPVIe_10MA, HPVIe_RELAY_ON);  # ERROR: changes range!
hpvie1.SetMeasVTrig(Trig, TRIG_FALLING);  # Will cause utility error
```

---

## SetMeasITrig() -- Set current measurement trigger
**Signature:** `int SetMeasITrig(double iTrig, TRIG_MODE trigMode = TRIG_FALLING, double hysteresisValue = 0.0);`
**Parameters:**
- `iTrig` [double]: Trigger current threshold, in A. Related to the current range set by Set().
- `trigMode` [TRIG_MODE, optional]: Trigger mode. Values:
  - `TRIG_FALLING`: Falling edge trigger (default).
  - `TRIG_RISING`: Rising edge trigger.
- `hysteresisValue` [double, optional]: Hysteresis value for trigger current, in A. Must be non-negative. Default 0.0.
  - Rising edge: trigger fires when measurement goes below (iTrig-hysteresisValue) then above iTrig.
  - Falling edge: trigger fires when measurement goes above (iTrig+hysteresisValue) then below iTrig.
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Current measurement trigger configuration. Critical constraint: between SetMeasITrig and MeasureVI calls, the voltage/current ranges and measurement gain settings must remain consistent. Do not insert any function that changes range or gain between them.
**Example:**
```python
# hpvie0 ramp from 16.5V to 21.5V. Trigger on hpvie0 current rising above 200uA.
double Trig = 200e-6;
int sam = 50;
int interval = 200;
double awg_pattern[100] = {0.0};
STSAWGCreateRampData(&awg_pattern[0], sam, 1, 16.5, 21.5);
hpvie0.AwgLoader("Vst", FV, HPVIe_40V, HPVIe_100MA, awg_pattern, sam);
hpvie0.Set(FV, 16.5, HPVIe_40V, HPVIe_100MA, HPVIe_RELAY_ON);
hpvie0.AwgSelect("Vst", 0, sam - 1, sam - 1, interval);

# Correct:
hpvie0.MeasureVI(sam, interval, HPVIe_MV_X1, HPVIe_MI_X1, MEAS_AWG);
hpvie0.SetMeasITrig(Trig, TRIG_RISING);  # Trigger at 200uA, rising edge
STSEnableAWG(&hpvie0);
STSEnableMeas(&hpvie0);
STSAWGRun();

# WRONG (inserting Set between MeasureVI and SetMeasITrig):
hpvie0.MeasureVI(sam, interval, HPVIe_MV_X1, HPVIe_MI_X1, MEAS_AWG);
hpvie0.Set(FV, 16.5, HPVIe_40V, HPVIe_10MA, HPVIe_RELAY_ON);  # ERROR: current range changed!
hpvie0.SetMeasITrig(Trig, TRIG_RISING);  # Will cause utility error
```

---

## KelvinCheck() -- Perform Kelvin connection check
**Signature:** `int KelvinCheck(HPVIe_KELVINMODE checkMode, HPVIe_KELVINCH checkCh, UINT sampleTimes = 200);`
**Parameters:**
- `checkMode` [HPVIe_KELVINMODE]: Kelvin test mode. Values:
  - `HPVIe_HIGH_SIDE`: Check high-side circuit connection.
  - `HPVIe_LOW_SIDE`: Check low-side circuit connection.
  - `HPVIe_HIGH_LOW_SIDE_QUICK`: Serial check of both high and low side connections.
- `checkCh` [HPVIe_KELVINCH]: Kelvin test channel. Values:
  - `HPVIe_CHA`: Only HPVIe_RELAY_ON connection for kelvin check.
  - `HPVIe_CHB`: Only HPVIe_RELAY_FANOUT_ON connection for kelvin check.
  - `HPVIe_CHAB`: HPVIe_RELAY_ALL_ON connection for kelvin check.
- `sampleTimes` [UINT, optional]: AD sample count for kelvin check. Range: 50 to 500. Clamped if out of range. Default 200.
**Return:** (not explicitly documented, presumably 0 for success)
**Remarks:** Configures and performs HPVIe Kelvin connection check. Notes:
- After check completes, VI source DA value is 0; everything else restored to pre-check state.
- This function does not support Group operation.
**Example:**
```python
# High-side Kelvin check on hpvie0 CHA, 200 samples
hpvie0.Set(FV, 1, HPVIe_10V, HPVIe_1MA, HPVIe_RELAY_OFF);
hpvie0.KelvinCheck(HPVIe_HIGH_SIDE, HPVIe_CHA);
```

---

## GetKelvinCheckResult() -- Get Kelvin check result
**Signature:** `int GetKelvinCheckResult(UINT siteCount, HPVIe_KELVINCH checkCh, double& highRes, double& lowRes);`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
- `checkCh` [HPVIe_KELVINCH]: Channel to read kelvin check result. Values: `HPVIe_CHA`, `HPVIe_CHB`, `HPVIe_CHAB`.
- `highRes` [double&]: Output -- high-side measured resistance value (Ohm).
- `lowRes` [double&]: Output -- low-side measured resistance value (Ohm).
**Return:**
- `< 0`: Invalid site.
- `32-bit value`: Lower 16 bits = low-side abnormality, Upper 16 bits = high-side abnormality. Each bit=1 indicates abnormality, 0=normal.

| Bit | Side | Description |
|-----|------|-------------|
| 0 | LOW | Resistance out of [0, 8 Ohm] range |
| 1 | LOW | SLS connection abnormal |
| 2 | LOW | FLS connection abnormal |
| 3 | LOW | SLS or FLS connection abnormal |
| 4 | LOW | SL connection abnormal |
| 5 | LOW | Constant current 1 abnormal |
| 6 | LOW | FL or SL connection abnormal |
| 7 | LOW | Constant current 2 abnormal |
| 8 | LOW | FLB connection abnormal |
| 9 | LOW | Constant current 3 abnormal |
| 10-15 | - | Always 0 |
| 16 | HIGH | Resistance out of [0, 8 Ohm] range |
| 17 | HIGH | SHS connection abnormal |
| 18 | HIGH | FHS connection abnormal |
| 19 | HIGH | SHS or FHS connection abnormal |
| 20 | HIGH | SL connection abnormal |
| 21 | HIGH | Constant current 1 abnormal |
| 22 | HIGH | FH or SH connection abnormal |
| 23 | HIGH | Constant current 2 abnormal |
| 24 | HIGH | FHB connection abnormal |
| 25 | HIGH | Constant current 3 abnormal |
| 26-31 | - | Always 0 |

**Remarks:** Reads kelvin check result for the specified site and check channel.
**Example:**
```python
hpvie0.Set(FV, 0, HPVIe_10V, HPVIe_1MA, HPVIe_RELAY_OFF);
hpvie0.KelvinCheck(HPVIe_HIGH_SIDE, HPVIe_CHA);
int result[STS_SITE_NUM] = {0};
double highRes = 0;
double lowRes = 0;
for (iSite = 0; iSite < STS_SITE_NUM; iSite++) {
    result[iSite] = hpvie0.GetKelvinCheckResult(iSite, HPVIe_CHA, highRes, lowRes);
}
```

---

## SetAlarmMask() -- Set alarm mask
**Signature:** `void SetAlarmMask(UINT siteCount, bool status = true);`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
- `status` [bool, optional]: `true` = mask alarm info for this site, `false` = output alarm info for this site. Default `true`.
**Return:** void
**Remarks:** Masks alarm information for a specific site. Note: Alarm mask set by this function is re-initialized in `InitBeforeTestFlow()`.
**Example:**
```python
hpvie0.SetAlarmMask(0);  # Mask alarm info for SITE_1
# Over-range alarm will NOT be output
hpvie0.Set(FV, 5, HPVIe_2V, HPVIe_10MA, HPVIe_RELAY_ON);
```

---

## GetAlarmMask() -- Get alarm mask status
**Signature:** `bool GetAlarmMask(UINT siteCount);`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
**Return:**
- `true`: Site alarm is masked.
- `false`: Site alarm is output.
**Remarks:** Reads the alarm status for a site.
**Example:**
```python
bool status = hpvie0.GetAlarmMask(0);  # Get alarm status of SITE_1
```

---

## SiteBindModify() -- Modify site binding
**Signature:** `int SiteBindModify(char* modifySiteList);`
**Parameters:**
- `modifySiteList` [char*]: Site reconfiguration string. Format: `"srcSite1:dstSite1,srcSite2:dstSite2,..."`. Source and target sites separated by colon, multiple pairs separated by comma. Site numbers: 0 (SITE_1) to 250 (SITE_251). Example: `"0:2,1:3"` remaps SITE_1 to SITE_3, SITE_2 to SITE_4.
**Return:**
- `0`: Site reconfiguration successful.
- Non-zero: Site reconfiguration failed.
**Failure conditions:**
- Multiple pairs must be comma-separated; first/last char cannot be comma; no empty entries between commas.
- Source and target must be separated by exactly one colon; both sides must be numeric only.
- Site numbers must be >= 0 and < 251 (max system sites).
- Cannot reconfigure NO_SITE channels.
- Same source site cannot appear twice in one call (e.g., `"0:1,0:2"` is invalid).
- Different source sites cannot map to the same target site (e.g., `"0:2,1:2"` is invalid).
- If a target site already has a channel configured, it must also be remapped in the same call. Example: if SITE_1 and SITE_2 are configured, modifying only SITE_1 to SITE_2 (`"0:1"`) is invalid without also remapping SITE_2.
**Remarks:** Reconfigures channel site binding. Unmodified sites keep their original binding. The reconfiguration is NOT affected by site validity -- e.g., remapping SITE_1 to SITE_2 always moves the physical channel regardless of SITE_1 validity.
**Example:**
```python
# Setup:
HPVIe hpvie0("S4_0,S12_0");
HPVIe hpvie1("S5_0,S13_0");
HPVIe gphpvie0("S4_0,S12_0,S5_0,S13_0");
STSSetMultiSiteBind(MD_HPVIe, SITE_1, "S4_0,S5_0");
STSSetMultiSiteBind(MD_HPVIe, SITE_2, "S12_0,S13_0");

# Example 1: Remap SITE_1->SITE_3, SITE_2->SITE_4
hpvie0.SiteBindModify("0:2,1:3");
# Note: gphpvie0 changes from GroupPin to MultiSitePin

# Example 2: Remap SITE_1->SITE_2, SITE_2->SITE_3
hpvie0.SiteBindModify("0:1,1:2");

# Example 3: Remap SITE_1->SITE_3, SITE_2 unchanged
hpvie0.SiteBindModify("0:2");

# Example 4: Remap group SITE_1->SITE_3, SITE_2->SITE_4
gphpvie0.SiteBindModify("0:2,1:3");
# Note: hpvie0 and hpvie1 both get remapped since gphpvie0 contains them
```

---

## GetBoardSN() -- Get board serial number
**Signature:** `int GetBoardSN(UINT siteCount, char* boardSN, UINT snSize);`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
- `boardSN` [char*]: User-defined buffer for board serial number, e.g. `char boardSN[255] = {0}`. Returns empty if not stored or site invalid.
- `snSize` [UINT]: Size of boardSN buffer.
**Return:** `0` = success. Non-zero = failure.
**Remarks:** Gets the board's serial number.
**Example:**
```python
char boardSN[255] = {0};
hpvie0.GetBoardSN(0, boardSN, 255);
```

---

## GetBoardHDRev() -- Get board hardware revision
**Signature:** `int GetBoardHDRev(UINT siteCount, char* hardRev, UINT revSize);`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
- `hardRev` [char*]: User-defined buffer for hardware revision, e.g. `char hardRev[255] = {0}`. Returns "N/A" if not stored.
- `revSize` [UINT]: Size of hardRev buffer.
**Return:** `0` = success. Non-zero = failure.
**Remarks:** Gets the board's hardware revision.
**Example:**
```python
char hardRev[255] = {0};
hpvie0.GetBoardHDRev(0, hardRev, 255);
```

---

## GetCalibrationTime() -- Get calibration time
**Signature:** `SYSTEMTIME GetCalibrationTime(UINT siteCount) const;`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
**Return:** SYSTEMTIME of calibration date. Returns 1970-1-1 8:0:0 on error (channel not calibrated or site invalid).
**Remarks:** Gets the calibration date of the channel.
**Example:**
```python
SYSTEMTIME calDate;
calDate = hpvie0.GetCalibrationTime(0);
```

---

## GetCalibrationTemperature() -- Get calibration temperature
**Signature:** `double GetCalibrationTemperature(UINT siteCount) const;`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
**Return:** Temperature at calibration time. Returns 0 on error (channel not calibrated or site invalid).
**Remarks:** Gets the calibration temperature of the channel.
**Example:**
```python
double calTemperature = 0.0;
calTemperature = hpvie0.GetCalibrationTemperature(0);
```

---

## GetCalibrationHumidity() -- Get calibration humidity
**Signature:** `double GetCalibrationHumidity(UINT siteCount) const;`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
**Return:** Humidity at calibration time. Returns 0 on error (channel not calibrated or site invalid).
**Remarks:** Gets the calibration humidity of the channel.
**Example:**
```python
double calHumidity = 0.0;
calHumidity = hpvie0.GetCalibrationHumidity(0);
```

---

## GetCalibrationResult() -- Get calibration result
**Signature:** `CAL_RESULT GetCalibrationResult(UINT siteCount) const;`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
**Return:** Calibration result enum:
- `CAL_PASS`: Calibration passed.
- `CAL_FAIL`: Calibration failed.
- `STS_NO_RESULT_RECORD`: Abnormal (channel not calibrated or site invalid).
**Remarks:** Gets the calibration result of the channel.
**Example:**
```python
CAL_RESULT calResult;
calResult = hpvie0.GetCalibrationResult(0);
```

---

## GetCalibrationLogicRev() -- Get calibration logic revision
**Signature:** `int GetCalibrationLogicRev(UINT siteCount) const;`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
**Return:** Logic revision number. Returns 255 on error (channel not calibrated or site invalid).
**Remarks:** Gets the calibration logic revision number.
**Example:**
```python
int calLogicRev = 0;
calLogicRev = hpvie0.GetCalibrationLogicRev(0);
```

---

## GetCalibrationMeter() -- Get calibration meter info
**Signature:** `CAL_METER GetCalibrationMeter(UINT siteCount, char* meterSN = NULL, UINT snSize = 0);`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
- `meterSN` [char*, optional]: User-defined buffer for calibration meter serial number, e.g. `char meterSN[255] = {0}`. Returns "N/A" on error. Default NULL (do not read serial).
- `snSize` [UINT, optional]: Size of meterSN buffer. Default 0.
**Return:** Calibration meter type enum:
- `STS_KEITHLEY2000`: Keithley 2000.
- `STS_AGILENT34401`: Agilent 34401.
- `STS_AGILENT3458A`: Agilent 3458A.
- `STS_NO_METER_RECORD`: Abnormal (channel not calibrated or site invalid).
**Remarks:** Gets the calibration meter type and serial number.
**Example:**
```python
CAL_METER calMeterType;
char calMeterSN[255] = {0};
calMeterType = hpvie0.GetCalibrationMeter(0, calMeterSN, 255);
```

---

## GetCalibrationCalBoardInfo() -- Get calibration board info
**Signature:** `int GetCalibrationCalBoardInfo(UINT siteCount, char* boardSN = NULL, UINT snSize = 0, char* boardHdRev = NULL, UINT revSize = 0);`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
- `boardSN` [char*, optional]: User-defined buffer for calibration board serial number. Returns "N/A" on error. Default NULL (do not read serial).
- `snSize` [UINT, optional]: Size of boardSN buffer. Default 0.
- `boardHdRev` [char*, optional]: User-defined buffer for calibration board hardware revision. Returns "N/A" on error. Default NULL (do not read revision).
- `revSize` [UINT, optional]: Size of boardHdRev buffer. Default 0.
**Return:** Calibration board logic revision number (normal). Returns 255 on error (channel not calibrated or site invalid).
**Remarks:** Gets calibration board related information used when the channel was calibrated.
**Example:**
```python
int logicRev = 0;
char boardSN[255] = {0};
char boardHdRev[255] = {0};
logicRev = hpvie0.GetCalibrationCalBoardInfo(0, boardSN, 255, boardHdRev, 255);
```

---

## GetCalibrationSoftRev() -- Get calibration software revision
**Signature:** `int GetCalibrationSoftRev(UINT siteCount, char* softRev, UINT revSize);`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
- `softRev` [char*]: User-defined buffer for calibration software revision, e.g. `char softRev[255] = {0}`. Returns "N/A" on error.
- `revSize` [UINT]: Size of softRev buffer.
**Return:** `0` = success. Non-zero = failure (channel not calibrated or site invalid).
**Remarks:** Gets the software revision used at calibration time.
**Example:**
```python
char softRev[255] = {0};
hpvie0.GetCalibrationSoftRev(0, softRev, 255);
```

---

## GetCalibrationSlotID() -- Get calibration slot ID
**Signature:** `int GetCalibrationSlotID(UINT siteCount) const;`
**Parameters:**
- `siteCount` [UINT]: Site index. 0=SITE1, 1=SITE2...
**Return:** Slot ID where board was located during calibration. Returns 0 on error (channel not calibrated or site invalid).
**Remarks:** Gets the slot ID where the channel was located during calibration.
**Example:**
```python
int slotID = hpvie0.GetCalibrationSlotID(0);
```

---

# Enumeration Reference

## VIMode
| Value | Description |
|-------|-------------|
| `FV` | Constant voltage mode |
| `FI` | Constant current mode |

## HPVIe_VRNG (Voltage Range)
| Value | Max Range |
|-------|-----------|
| `HPVIe_100V` | 100V |
| `HPVIe_40V` | 40V |
| `HPVIe_20V` | 20V |
| `HPVIe_10V` | 10V |
| `HPVIe_5V` | 5V |
| `HPVIe_2V` | 2V |

## HPVIe_IRNG (Current Range)
| Value | Max Range |
|-------|-----------|
| `HPVIe_100A` | 100A |
| `HPVIe_50A` | 50A |
| `HPVIe_20A` | 20A |
| `HPVIe_10A` | 10A |
| `HPVIe_2A` | 2A |
| `HPVIe_1A` | 1A |
| `HPVIe_100MA` | 100mA |
| `HPVIe_10MA` | 10mA |
| `HPVIe_1MA` | 1mA |
| `HPVIe_100UA` | 100uA |
| `HPVIe_10UA` | 10uA |

## HPVIe_OUT_RELAY (Output Relay)
| Value | Description |
|-------|-------------|
| `HPVIe_RELAY_ON` | Turn on output relay |
| `HPVIe_RELAY_FANOUT_ON` | Turn on FANOUT output relay |
| `HPVIe_RELAY_ALL_ON` | Both relay + FANOUT Force relay (for 100A tests) |
| `HPVIe_RELAY_OFF` | Turn off output relay |
| `HPVIe_RELAY_SENSE_ON` | Independent voltmeter mode: SENSE relay ON, FORCE OFF |
| `HPVIe_RELAY_SENSE_FANOUT_ON` | Independent voltmeter mode: SENSE FANOUT ON, FORCE OFF |
| `HPVIe_RELAY_HOLD` | Hold previous relay state |

## HPVIe_MV_GAIN (Voltage Measurement Gain)
| Value |
|-------|
| `HPVIe_MV_X1` |
| `HPVIe_MV_X2` |
| `HPVIe_MV_X5` |
| `HPVIe_MV_X10` |

## HPVIe_MI_GAIN (Current Measurement Gain)
| Value |
|-------|
| `HPVIe_MI_X1` |
| `HPVIe_MI_X2` |
| `HPVIe_MI_X5` |
| `HPVIe_MI_X10` |

## FLOATMEASMODE (Measurement Mode)
| Value | Description |
|-------|-------------|
| `MEAS_NORMAL` | Normal measurement (completes on function call) |
| `MEAS_AWG` | AWG measurement (starts when AWG runs) |

## MeasRet (Measurement Readback Type)
| Value | Description |
|-------|-------------|
| `MVRET` | Read back voltage data (unit: V) |
| `MIRET` | Read back current data (unit: A) |

## TRIG_MODE (Trigger Mode)
| Value | Description |
|-------|-------------|
| `TRIG_FALLING` | Falling edge trigger |
| `TRIG_RISING` | Rising edge trigger |

## HPVIe_KELVINMODE (Kelvin Check Mode)
| Value | Description |
|-------|-------------|
| `HPVIe_HIGH_SIDE` | Check high-side circuit connection |
| `HPVIe_LOW_SIDE` | Check low-side circuit connection |
| `HPVIe_HIGH_LOW_SIDE_QUICK` | Serial check of both high and low sides |

## HPVIe_KELVINCH (Kelvin Check Channel)
| Value | Description |
|-------|-------------|
| `HPVIe_CHA` | HPVIe_RELAY_ON connection kelvin check |
| `HPVIe_CHB` | HPVIe_RELAY_FANOUT_ON connection kelvin check |
| `HPVIe_CHAB` | HPVIe_RELAY_ALL_ON connection kelvin check |

## AWG Run Mode
| Value | Description |
|-------|-------------|
| `AWG_SINGLE` | Run AWG waveform once |
| `AWG_LOOP` | Loop AWG waveform continuously (stop with AwgStop()) |

## CAL_RESULT (Calibration Result)
| Value | Description |
|-------|-------------|
| `CAL_PASS` | Calibration passed |
| `CAL_FAIL` | Calibration failed |
| `STS_NO_RESULT_RECORD` | No calibration record (abnormal) |

## CAL_METER (Calibration Meter Type)
| Value | Description |
|-------|-------------|
| `STS_KEITHLEY2000` | Keithley 2000 |
| `STS_AGILENT34401` | Agilent 34401 |
| `STS_AGILENT3458A` | Agilent 3458A |
| `STS_NO_METER_RECORD` | No meter record (abnormal) |

---

# Measurement Result Constants
| Constant | Description |
|----------|-------------|
| `AVERAGE_RESULT` | Average of all measured samples |
| `MAX_RESULT` | Maximum value among samples |
| `MIN_RESULT` | Minimum value among samples |
| `TRIG_RESULT` | Trigger transition position (AWG sync) |
