> 迁移自 auto-memory `STS8300-qvme.md`（2026-08-16） ｜来源 STS8300 Programming Manual, Chapter 6.8 (pages 768-800) ｜module MD_QVMe


# QVMe — Quick Voltage/Current Source Meter

QVMe is a high-speed digitizer/sampler instrument card on the STS8300 platform. Each board supports up to 4 channels (board index 0-3). It provides:
- Low-speed ADC (LS ADC): 1-1300 us sampling interval, 9 voltage ranges (100MV to 100V), 4 filter settings
- High-speed ADC (HS ADC): 0.1-1 us sampling interval, 3 voltage ranges (1V to 4V)
- FFT analysis (direct or Blackman-Harris windowed)
- AWG-synchronized measurement (up to 4 trigger points)
- Per-site measurement with alarm masking

---

## QVMe() — Constructor: define a QVMe logical channel
**Signature:** `QVMe(char* channelList, char* chName = NULL)`
**Parameters:**
- `channelList` [char*]: Binding channel string. Format: `"S<slot>_<index>,S<slot>_<index>,..."`. Example: `"S2_0,S2_1"` where S2 = Slot 2, 0/1 = board index. Maximum 4 channels per board (index 0-3).
- `chName` [char*]: Custom channel name. Default `NULL` -> system names it `QVMe_xx`.
**Remarks:** Defines a QVMe logical channel and specifies the physical channels (slot + board index) it controls. Use `STSSetMultiSiteBind(MD_QVMe, SITE_N, "Sx_y")` to bind to sites.
**Example:**
```python
# 1 QVMe board at Slot2, 4-site parallel
QVMe qvme0("S2_0-3");
STSSetMultiSiteBind(MD_QVMe, SITE_1, "S2_0");
STSSetMultiSiteBind(MD_QVMe, SITE_2, "S2_1");
STSSetMultiSiteBind(MD_QVMe, SITE_3, "S2_2");
STSSetMultiSiteBind(MD_QVMe, SITE_4, "S2_3");
```

---

## Init() — Initialize the QVMe channel
**Signature:** `int Init()`
**Return:** `int` — (implied: 0 on success)
**Remarks:** After calling Init():
1. All input/output relays are opened (disconnected)
2. Both low-speed and high-speed ADC channels are stopped and their ranges are not set
3. Low-speed channel defaults to 10 KHz filter
4. Previous measurement results cannot be read back

Recommend calling Init() at the end of a QVMe test.
**Example:**
```python
qvme0.Init();  # Initialize logical channel 0
qvme1.Init();  # Initialize logical channel 1
```

---

## Connect() — Connect input/output relays
**Signature:** `void Connect(void)`
**Remarks:** Connect the QVMe channel's input/output relays. Must be called before measurement.
**Example:**
```python
qvme0.Connect();  # Connect Logic Channel 0 Input/Output Relay
```

---

## Disconnect() — Disconnect input/output relays
**Signature:** `void Disconnect(void)`
**Remarks:** Disconnect the QVMe channel's input/output relays. Should be called after measurement is complete.
**Example:**
```python
qvme0.Disconnect();  # Disconnect Logic Channel 0 Input/Output Relay
```

---

## SetMeasTrig() — Set measurement trigger threshold and direction
**Signature:** `void SetMeasTrig(double VTrig, TRIG_MODE trigMode, double hysteresisValue = ?)`
**Parameters:**
- `VTrig` [double]: Trigger threshold voltage. Range depends on the selected measurement range.
- `trigMode` [TRIG_MODE]: Trigger direction.
  - `TRIG_FALLING`: Falling edge trigger
  - `TRIG_RISING`: Rising edge trigger
- `hysteresisValue` [double]: Hysteresis value (exact type/range not explicitly documented; parameter listed in signature)
**Remarks:** Sets the measurement trigger threshold and direction. NOTE: When `measMode` in `MeasureLADC()` or `MeasureHADC()` is `MEAS_NORMAL`, the trigger threshold set here has no effect (trigger only works in `MEAS_AWG` mode).
**Example:**
```python
# Using 10V measurement range, set falling trigger at 6.0V
qvme0.MeasureLADC(200, 5, QVMe_LADC_10V, QVMe_LADC_10KHz, MEAS_AWG, 0, 0, 0, 0);
qvme0.SetMeasTrig(6.0, TRIG_FALLING);
```

---

## MeasureLADC() — Low-speed ADC sampling
**Signature:** `void MeasureLADC(UINT sampleTimes = 100, double sampleInterval = 10, QVMe_LADC_VRANG VRange = QVMe_LADC_10V, QVMe_LADC_FILTER Filter = QVMe_LADC_10KHz, FLOATMEASMODE measMode = MEAS_NORMAL, UINT T1 = 0, UINT T2 = 0, UINT T3 = 0, UINT T4 = 0)`
**Parameters:**
- `sampleTimes` [UINT]: Number of samples, range 1-65534, default 100. For FFT: must be 64-32768 and a power of 2.
- `sampleInterval` [double]: Sampling interval in us, range 1-1300, resolution 0.1 us, default 10 us.
- `VRange` [QVMe_LADC_VRANG]: Measurement voltage range. Default `QVMe_LADC_10V`.
  - `QVMe_LADC_100V`
  - `QVMe_LADC_50V`
  - `QVMe_LADC_20V`
  - `QVMe_LADC_10V`
  - `QVMe_LADC_5V`
  - `QVMe_LADC_2V`
  - `QVMe_LADC_1V`
  - `QVMe_LADC_500MV`
  - `QVMe_LADC_200MV`
  - `QVMe_LADC_100MV`
- `Filter` [QVMe_LADC_FILTER]: Filter setting. Default `QVMe_LADC_10KHz`.
  - `QVMe_LADC_400KHz`
  - `QVMe_LADC_100KHz`
  - `QVMe_LADC_40KHz`
  - `QVMe_LADC_10KHz`
- `measMode` [FLOATMEASMODE]: Measurement mode. Default `MEAS_NORMAL`.
  - `MEAS_NORMAL`: Normal measurement mode
  - `MEAS_AWG`: AWG-synchronized mode
- `T1, T2, T3, T4` [UINT]: Relative start times in us for AWG mode. Resolution 10 us, range 0 to (T1+T2+T3+T4) <= 600000. T2 is relative to T1, T3 relative to T2, T4 relative to T3. These 4 parameters only take effect in `MEAS_AWG` mode. Up to 4 measurement triggers can be started in one AWG burst. If all omitted, defaults to 1 trigger at time 0.
**Remarks:** Configures low-speed ADC and performs sampling, storing results in onboard memory. Must call `Connect()` before this function. In `MEAS_AWG` mode, pair with `STSEnableAWG()`, `STSEnableMeas()`, `STSAWGRun()` for synchronous measurement.
**Example:**
```python
# Low-speed: 1000 samples, 1us interval, 10V range, 40KHz filter, normal mode
qvme0.MeasureLADC(1000, 1, QVMe_LADC_10V, QVMe_LADC_40KHz, MEAS_NORMAL, 0, 0, 0, 0);
```

---

## MeasureHADC() — High-speed ADC sampling
**Signature:** `void MeasureHADC(UINT sampleTimes = 100, double sampleInterval = 1, QVMe_HADC_VRANG VRange = QVMe_HADC_4V, FLOATMEASMODE measMode = MEAS_NORMAL, UINT T1 = 0, UINT T2 = 0, UINT T3 = 0, UINT T4 = 0)`
**Parameters:**
- `sampleTimes` [UINT]: Number of samples, range 1-65534, default 100. For FFT: must be 64-32768 and a power of 2.
- `sampleInterval` [double]: Sampling interval in us, range 0.1-1, resolution 0.1 us, default 1 us.
- `VRange` [QVMe_HADC_VRANG]: Measurement voltage range. Default `QVMe_HADC_4V`.
  - `QVMe_HADC_4V`
  - `QVMe_HADC_2V`
  - `QVMe_HADC_1V`
- `measMode` [FLOATMEASMODE]: Measurement mode. Default `MEAS_NORMAL`.
  - `MEAS_NORMAL`: Normal measurement mode
  - `MEAS_AWG`: AWG-synchronized mode
- `T1, T2, T3, T4` [UINT]: Same as MeasureLADC — relative start times in us, AWG mode only.
**Remarks:** Configures high-speed ADC and performs sampling. Must call `Connect()` before this function. NOTE: `StartFFT()` and `GetFFTResult()` with `QVMe_FFT_DATA` are invalid when `measMode` is `MEAS_AWG`. `RMS_RESULT` in `GetMeasResult()` is also invalid in AWG mode.
**Example:**
```python
# High-speed: 1000 samples, 0.1us interval, 4V range, normal mode
qvme0.MeasureHADC(1000, 0.1, QVMe_HADC_4V, MEAS_NORMAL, 0, 0, 0, 0);
```

---

## GetMeasResult() — Get measurement result for a site
**Signature:** `double GetMeasResult(UINT siteNo, int sampleNumber = AVERAGE_RESULT)`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ... If the channel is defined as `NO_SITE`, `siteNo` can be any value.
- `sampleNumber` [int]: Result type identifier. Default `AVERAGE_RESULT`.
  - `AVERAGE_RESULT` (negative): Average of all samples
  - `MAX_RESULT` (negative): Maximum of all samples
  - `MIN_RESULT` (negative): Minimum of all samples
  - `TRIG_RESULT` (negative): Sample point index where trigger fired (requires `SetMeasTrig()`)
  - `RMS_RESULT` (negative): AC RMS after removing DC component
  - Non-negative integer N: Value of the (N+1)-th sample point. Range: 0 <= N <= sampleTimes-1
**Return:** When `sampleNumber` is negative: specific analysis result. When `sampleNumber` is non-negative: single sample point value.
**Remarks:** Gets the measurement result for a single site. To get multiple sample points, loop over the range. Must call `MeasureLADC()` or `MeasureHADC()` first. NOTE: When `measMode` is `MEAS_AWG`, `RMS_RESULT` is invalid.
**Example:**
```python
# Get average of all samples per site
int SiteID = 0;
double result[SITENUM] = {0.0};
qvme0.MeasureLADC(1000, 1, QVMe_LADC_10V, QVMe_LADC_40KHz, MEAS_NORMAL, 0, 0, 0, 0);
for (SiteID = 0; SiteID < SITENUM; SiteID++)
{
    result[SiteID] = qvme0.GetMeasResult(SiteID, AVERAGE_RESULT);
}
```

---

## StartFFT() — Start FFT computation on sampled data
**Signature:** `void StartFFT(QVMe_FFT_TYPE fftType)`
**Parameters:**
- `fftType` [QVMe_FFT_TYPE]: FFT type.
  - `QVMe_DIRECT_FFT`: Direct FFT (no window)
  - `QVMe_BLACKMAN_HARRIS_FFT`: FFT with Blackman-Harris window
**Remarks:** Starts FFT on sampled data. FFT point count range: 64-32768. The number of sample points MUST be a power of 2. Must call `MeasureLADC()` or `MeasureHADC()` first. NOTE: When `measMode` is `MEAS_AWG`, `StartFFT()` is invalid.
**Example:**
```python
# 2048-point FFT with direct method
double fft_result[2048] = {0.0};
qvme0.MeasureLADC(2048, 5, QVMe_LADC_10V, QVMe_LADC_40KHz, MEAS_NORMAL, 0, 0, 0, 0);
qvme0.StartFFT(QVMe_DIRECT_FFT);
```

---

## GetFFTResult() — Get FFT analysis result
**Signature:** `double GetFFTResult(UINT siteNo, int retResult = THD_RESULT, BYTE harmonicType = TOTAL_HARM, BYTE harmonicNum = 5, double FreqBand = -1)`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
- `retResult` [int]: Result type. Default `THD_RESULT`.
  - `THD_RESULT`: Total Harmonic Distortion
  - `SNR_RESULT`: Signal-to-Noise Ratio
  - `SINAD_RESULT`: Signal-to-Noise and Distortion
  - Non-negative integer N: Returns the voltage amplitude at frequency N * ((1/sampleInterval) / sampleTimes), where 0 <= N <= sampleTimes-1.
- `harmonicType` [BYTE]: Harmonic type used for THD calculation. Default `TOTAL_HARM`. Only meaningful when `retResult` is `THD_RESULT`.
  - `TOTAL_HARM`: All harmonics
  - `ODD_HARM`: Odd harmonics only
  - `EVEN_HARM`: Even harmonics only
- `harmonicNum` [BYTE]: Number of harmonics for THD calculation, range 2-50. Default 5. Only meaningful for `THD_RESULT`.
- `FreqBand` [double]: Frequency band in KHz for SNR/SINAD calculation (specifies the frequency range to include harmonics and noise). Range: 0 to ((1/sampleInterval)/2)*1000. Default -1 = all harmonics and noise. Only meaningful for `SNR_RESULT` or `SINAD_RESULT`.
**Return:** Requested FFT analysis value as double.
**Remarks:** Must call `StartFFT()` first. NOTE: When `measMode` is `MEAS_AWG`, this function is invalid.
**Example:**
```python
# Measure THD, SNR, SINAD of a 0.9765625 KHz 4Vpp sine wave
double THD_result[SITENUM] = {0.0};
double SNR_result[SITENUM] = {0.0};
double SINAD_result[SITENUM] = {0.0};
qvme0.Connect();
delay_ms(1);
qvme0.MeasureLADC(4096, 1, QVMe_LADC_10V, QVMe_LADC_400KHz, MEAS_NORMAL, 0, 0, 0, 0);
qvme0.StartFFT(QVMe_DIRECT_FFT);
for (int SiteID = 0; SiteID < SITENUM; SiteID++)
{
    THD_result[SiteID] = qvme0.GetFFTResult(SiteID, THD_RESULT, TOTAL_HARM, 20, -1);
    SNR_result[SiteID] = qvme0.GetFFTResult(SiteID, SNR_RESULT, TOTAL_HARM, 5, -1);
    SINAD_result[SiteID] = qvme0.GetFFTResult(SiteID, SINAD_RESULT, TOTAL_HARM, 5, -1);
}
```

---

## BlockRead() — Read a block of data from onboard memory
**Signature:** `void BlockRead(UINT siteNo, long startAddr, long size, double* buffer, QVMe_MEAS_RET retType = QVMe_SAMPLE_DATA)`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
- `startAddr` [long]: Starting address of the data block (non-negative integer).
- `size` [long]: Size of the data block (positive integer).
- `buffer` [double*]: User-defined array to hold the result data. IMPORTANT: buffer length must be >= `size`, otherwise unpredictable errors may occur. Recommend defining as a global variable.
- `retType` [QVMe_MEAS_RET]: Type of data to read. Default `QVMe_SAMPLE_DATA`.
  - `QVMe_SAMPLE_DATA`: Time-domain sample data
  - `QVMe_FFT_DATA`: Frequency-domain FFT data (requires prior `StartFFT()`)
**Remarks:** Reads a data block from onboard memory. NOTE: When `measMode` is `MEAS_AWG`, `QVMe_FFT_DATA` is invalid.
**Example:**
```python
# Read FFT result
int SiteID = 0;
double fft_result[SITENUM][2048] = {0.0};
qvme0.MeasureLADC(2048, 5, QVMe_LADC_10V, QVMe_LADC_40KHz, MEAS_NORMAL, 0, 0, 0, 0);
qvme0.StartFFT(QVMe_DIRECT_FFT);
for (SiteID = 0; SiteID < SITENUM; SiteID++)
{
    qvme0.BlockRead(SiteID, 0, 2048, fft_result[SiteID], QVMe_FFT_DATA);
}

# Read raw sample data
double data_result[SITENUM][2048] = {0.0};
qvme0.MeasureLADC(2048, 5, QVMe_LADC_10V, QVMe_LADC_40KHz, MEAS_NORMAL, 0, 0, 0, 0);
for (SiteID = 0; SiteID < SITENUM; SiteID++)
{
    qvme0.BlockRead(SiteID, 0, 2048, data_result[SiteID], QVMe_SAMPLE_DATA);
}
```

---

## SetAlarmMask() — Mask/unmask alarm information for a site
**Signature:** `void SetAlarmMask(UINT siteNo, bool maskStatus = true)`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
- `maskStatus` [bool]: Default `true`.
  - `true`: Mask (suppress) the site's alarm information
  - `false`: Output the site's alarm information
**Remarks:** Sets whether to suppress alarm info (e.g. sampleInterval out-of-range warnings) for a specific site.
**Example:**
```python
qvme0.SetAlarmMask(0, true);  # Mask alarm info for SITE_1
# The alarm information about sampleInterval is not output
qvme0.MeasureHADC(1000, 10, QVMe_HADC_4V, MEAS_NORMAL, 0, 0, 0, 0);
```

---

## GetAlarmMask() — Get alarm mask status for a site
**Signature:** `bool GetAlarmMask(UINT siteNo)`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
**Return:** `true`: Alarm info is masked for this site. `false`: Alarm info is output.
**Remarks:** Reads the current alarm mask state for a specific site.
**Example:**
```python
bool status = qvme0.GetAlarmMask(0);  # Get alarm status of SITE_1
```

---

## SiteBindModify() — Reconfigure site bindings for the channel
**Signature:** `int SiteBindModify(char* modifySiteList)`
**Parameters:**
- `modifySiteList` [char*]: Site reconfiguration string. Format: `"srcSite1:dstSite1,srcSite2:dstSite2,..."`. Source and destination site numbers are separated by colon; multiple pairs separated by commas. Minimum site number 0 (SITE_1), maximum 250 (SITE_251). Example: `"0:2,1:3"` remaps SITE_1->SITE_3 and SITE_2->SITE_4.
**Return:** `0`: Reconfiguration success. Non-zero: Reconfiguration failure.
**Remarks:** Reconfigures site bindings without affecting unmodified sites. The following cause failure:
1. Multiple modifications must be comma-separated; no leading/trailing commas; no empty entries between commas
2. Source and destination must be separated by exactly one colon, both sides must be digits only
3. Site numbers must be >= 0 and < 251 (max system sites)
4. Cannot reconfigure a channel defined as `NO_SITE`
5. Same site cannot be modified twice in one call (e.g. `"0:1,0:2"` is invalid)
6. Different sites cannot be remapped to the same destination (e.g. `"0:2,1:2"` is invalid)
7. If a destination site already has a channel configuration, it MUST also be remapped in the same call

The reconfiguration is NOT affected by site validity — even if SITE_1 is invalid, its physical channel will still be remapped to the target site.
**Example:**
```python
# Channel definition and initial site binding
QVMe qvme0("S4_0,S4_1");
STSSetMultiSiteBind(MD_QVMe, SITE_1, "S4_0,S4_2");
STSSetMultiSiteBind(MD_QVMe, SITE_2, "S4_1,S4_3");

# Remap SITE_1->SITE_3, SITE_2->SITE_4
qvme0.SiteBindModify("0:2,1:3");

# Remap only SITE_1->SITE_3 (SITE_2 unchanged)
qvme0.SiteBindModify("0:2");
```

---

## GetBoardSN() — Get board serial number
**Signature:** `int GetBoardSN(UINT siteNo, char* boardSN, UINT snSize)`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
- `boardSN` [char*]: User-defined buffer to hold the serial number. Returns `"N/A"` if not stored.
- `snSize` [UINT]: Size of the `boardSN` buffer (positive integer).
**Return:** `0`: Read success. `-1`: Invalid site, read failure.
**Remarks:** Gets the main module serial number for the board associated with the given site and channel.
**Example:**
```python
char boardSn[255] = {0};
qvme0.GetBoardSN(0, boardSn, 255);
```

---

## GetBoardHDRev() — Get board hardware revision
**Signature:** `int GetBoardHDRev(UINT siteNo, char* hardRev, UINT revSize)`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
- `hardRev` [char*]: User-defined buffer to hold the hardware revision string. Returns `"N/A"` if not stored.
- `revSize` [UINT]: Size of the `hardRev` buffer (positive integer).
**Return:** `0`: Read success. `-1`: Invalid site, read failure.
**Remarks:** Gets the hardware revision of the main module for the board associated with the given site and channel.
**Example:**
```python
char hardRev[255] = {0};
qvme0.GetBoardHDRev(0, hardRev, 255);
```

---

## GetCalibrationTime() — Get calibration date/time
**Signature:** `SYSTEMTIME GetCalibrationTime(UINT siteNo) const`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
**Return:** `SYSTEMTIME` struct with the calibration date. Returns `1970-1-1 8:0:0` if calibration not stored or site invalid.
**Remarks:** Gets the date when calibration was performed for the specified channel.
**Example:**
```python
SYSTEMTIME calDate;
calDate = qvme0.GetCalibrationTime(0);  # Get calibration date of SITE_1
```

---

## GetCalibrationTemperature() — Get calibration temperature
**Signature:** `double GetCalibrationTemperature(UINT siteNo) const`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
**Return:** Temperature (double) at time of calibration. Returns `0` on error. Error causes: (1) channel not calibrated; (2) invalid site.
**Remarks:** Gets the temperature recorded when calibration was performed for the specified channel.
**Example:**
```python
double calTemperature = 0.0;
calTemperature = qvme0.GetCalibrationTemperature(0);
```

---

## GetCalibrationHumidity() — Get calibration humidity
**Signature:** `double GetCalibrationHumidity(UINT siteNo) const`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
**Return:** Humidity (double) at time of calibration. Returns `0` on error. Error causes: (1) channel not calibrated; (2) invalid site.
**Remarks:** Gets the humidity recorded when calibration was performed for the specified channel.
**Example:**
```python
double calHumidity = 0.0;
calHumidity = qvme0.GetCalibrationHumidity(0);
```

---

## GetCalibrationResult() — Get calibration result
**Signature:** `CAL_RESULT GetCalibrationResult(UINT siteNo) const`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
**Return:** Calibration result enum:
- `CAL_PASS`: Calibration passed
- `CAL_FAIL`: Calibration failed
- `STS_NO_RESULT_RECORD`: Not stored or site invalid
**Remarks:** Gets the calibration result for the specified channel.
**Example:**
```python
CAL_RESULT calResult;
calResult = qvme0.GetCalibrationResult(0);
```

---

## GetCalibrationLogicRev() — Get calibration logic revision
**Signature:** `int GetCalibrationLogicRev(UINT siteNo) const`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
**Return:** Logic revision number (int) at time of calibration. Returns `255` on error. Error causes: (1) channel not calibrated; (2) invalid site.
**Remarks:** Gets the logic/firmware version used during calibration for the specified channel.
**Example:**
```python
int calLogicRev = 0;
calLogicRev = qvme0.GetCalibrationLogicRev(0);
```

---

## GetCalibrationMeter() — Get calibration meter info
**Signature:** `CAL_METER GetCalibrationMeter(UINT siteNo, char* meterSN = NULL, UINT snSize = 0)`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
- `meterSN` [char*]: User-defined buffer to hold the calibration meter serial number. Returns `"N/A"` if not stored. Default `NULL` (do not retrieve SN).
- `snSize` [UINT]: Size of the `meterSN` buffer (positive integer). Default `0` (do not retrieve SN).
**Return:** Calibration meter type enum:
- `STS_KEITHLEY2000`: Keithley 2000
- `STS_AGILENT34401`: Agilent 34401
- `STS_AGILENT3458A`: Agilent 3458A
- `STS_NO_METER_RECORD`: Not stored or site invalid
**Remarks:** Reads the type and serial number of the meter used during calibration.
**Example:**
```python
char meterSN[255] = {0};
CAL_METER calMeter;
calMeter = qvme0.GetCalibrationMeter(0, meterSN, 255);
```

---

## GetCalibrationCalBoardInfo() — Get calibration board info
**Signature:** `int GetCalibrationCalBoardInfo(UINT siteNo, char* boardSN = NULL, UINT snSize = 0, char* HardRev = NULL, UINT revSize = 0)`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
- `boardSN` [char*]: User-defined buffer for the calibration board serial number. Returns `"N/A"` on error. Default `NULL` (do not retrieve).
- `snSize` [UINT]: Size of `boardSN` buffer. Default `0`.
- `HardRev` [char*]: User-defined buffer for the calibration board hardware version. Returns `"N/A"` on error. Default `NULL` (do not retrieve).
- `revSize` [UINT]: Size of `HardRev` buffer. Default `0`.
**Return:** Logic revision of the calibration board used (int). Returns `255` on error. Error causes: (1) channel not calibrated; (2) invalid site.
**Remarks:** Gets information about the calibration board used when calibrating this channel.
**Example:**
```python
BYTE logicRev = 0;
char boardSN[255] = {0};
char boardHdRev[255] = {0};
logicRev = qvme0.GetCalibrationCalBoardInfo(0, boardSN, 255, boardHdRev, 255);
```

---

## GetCalibrationSoftRev() — Get calibration software revision
**Signature:** `int GetCalibrationSoftRev(UINT siteNo, char* softRev, UINT revSize)`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
- `softRev` [char*]: User-defined buffer for software revision string. Returns `"N/A"` if not stored.
- `revSize` [UINT]: Size of `softRev` buffer (positive integer).
**Return:** `0`: Read success. `-1`: Invalid site, read failure.
**Remarks:** Gets the software version used during calibration for the specified channel.
**Example:**
```python
char softRev[255] = {0};
qvme0.GetCalibrationSoftRev(0, softRev, 255);
```

---

## GetCalibrationSlotID() — Get calibration slot ID
**Signature:** `int GetCalibrationSlotID(UINT siteNo) const`
**Parameters:**
- `siteNo` [UINT]: Site number. 0 = Site1, 1 = Site2, ...
**Return:** Slot ID (int) where the board was installed during calibration. Returns `0` on error. Error causes: (1) channel not calibrated; (2) invalid site.
**Remarks:** Gets the slot position the board occupied when calibration was performed.
**Example:**
```python
int slotID = qvme0.GetCalibrationSlotID(0);
```

---

# Programming Examples from Manual (Section 6.8.17)

## DC Precision Voltage Measurement
```python
double avg_result[SITENUM] = {0.0};
qvme0.Connect();
delay_ms(1);
qvme0.MeasureLADC(200, 5, QVMe_LADC_5V, QVMe_LADC_40KHz, MEAS_NORMAL, 0, 0, 0, 0);
// sample=200; interval=5us
for (int SiteID = 0; SiteID < SITENUM; SiteID++)
{
    avg_result[SiteID] = qvme0.GetMeasResult(SiteID, AVERAGE_RESULT);
    // Average->SetTestResult(SiteID, 0, avg_result[SiteID]);
}
```

## RMS Measurement
```python
// Measure RMS of a 1KHz 4Vpp sine wave
int SiteID = 0;
double rms_result[SITENUM] = {0.0};
qvme0.Connect();
delay_ms(1);
qvme0.MeasureLADC(200, 5, QVMe_LADC_5V, QVMe_LADC_40KHz, MEAS_NORMAL, 0, 0, 0, 0);
// Ensure sample number covers a whole period
for (SiteID = 0; SiteID < SITENUM; SiteID++)
{
    rms_result[SiteID] = qvme0.GetMeasResult(SiteID, RMS_RESULT);
}
```

## FFT Analysis (THD/SNR/SINAD via GetFFTResult)
```python
// Measure 0.9765625KHz 4Vpp sine: THD, SNR, SINAD directly
int SiteID = 0;
double THD_result[SITENUM] = {0.0};
double SNR_result[SITENUM] = {0.0};
double SINAD_result[SITENUM] = {0.0};
qvme0.Connect();
delay_ms(1);
qvme0.MeasureLADC(4096, 1, QVMe_LADC_10V, QVMe_LADC_400KHz, MEAS_NORMAL, 0, 0, 0, 0);
// sample=4096, interval=1us (sample rate=1M), 400KHz filter
qvme0.StartFFT(QVMe_DIRECT_FFT);
for (SiteID = 0; SiteID < SITENUM; SiteID++)
{
    THD_result[SiteID] = qvme0.GetFFTResult(SiteID, THD_RESULT, TOTAL_HARM, 20, -1);
    SNR_result[SiteID] = qvme0.GetFFTResult(SiteID, SNR_RESULT, TOTAL_HARM, 5, -1);
    SINAD_result[SiteID] = qvme0.GetFFTResult(SiteID, SINAD_RESULT, TOTAL_HARM, 5, -1);
}
```

## FFT Analysis (THD/SNR/SINAD via BlockRead Manual Calculation)
```python
// Manual THD/SNR/SINAD via BlockRead + Blackman-Harris FFT
int i = 0, j = 0, k = 0;
int sample = 2048;
double P1[SITENUM] = {0}, P2[SITENUM] = {0};
double P3[SITENUM] = {0}, P4[SITENUM] = {0};
double thd[SITENUM] = {0}, snr[SITENUM] = {0}, sinad[SITENUM] = {0};
qvme0.Connect();
delay_ms(1);
double fft_result[2048] = {0.0};
qvme0.MeasureLADC(sample, 5, QVMe_LADC_10V, QVMe_LADC_40KHz, MEAS_NORMAL, 0, 0, 0, 0);
qvme0.StartFFT(QVMe_BLACKMAN_HARRIS_FFT);
for (i = 0; i < SITENUM; i++)
{
    qvme0.BlockRead(i, 0, sample, fft_result, QVMe_FFT_DATA);
    // Effective signal power
    for (j = -3; j <= 3; j++)
        P1[i] = P1[i] + fft_result[10 + j] * fft_result[10 + j];
    // Noise + harmonic signal power
    for (j = 4; j < 7; j++)
        P2[i] = P2[i] + fft_result[j] * fft_result[j];
    for (j = 14; j < 191; j++)
        P2[i] = P2[i] + fft_result[j] * fft_result[j];
    // Harmonic signal power
    for (j = 20; j < 201; j = j + 10)
        for (k = -3; k <= 3; k++)
            P3[i] = P3[i] + fft_result[j + k] * fft_result[j + k];
    // Noise signal power
    P4[i] = P2[i] - P3[i];
    thd[i] = 20 * log10(sqrt(P3[i] / (P1[i] + 1e-100)) + 1e-100);
    snr[i] = 20 * log10(sqrt(P1[i] / (P4[i] + 1e-100)) + 1e-100);
    sinad[i] = 20 * log10(sqrt(P1[i] / (P2[i] + 1e-100)) + 1e-100);
}
```

## QVMe + FPVIe Synchronous AWG Measurement
```python
// AWG: FPVIe ramps 8V->3V, QVMe captures synchronously with 5V falling trigger
int sample = 100;
double Trig = 5;  // trigger level
double Trig_Point_qvme[SITENUM] = {0.0};
double Trig_Point_fpvie[SITENUM] = {0.0};
double result_qvme[SITENUM] = {0.0};
double result_fpvie[SITENUM] = {0.0};
int sam = 50;       // data size
int interval = 20;   // interval = 20us
double awg_pattern[1000] = {0.0};
qvme0.Connect();
delay_ms(1);
STSAWGCreateRampData(&awg_pattern[0], sam, 1, 8, 3);
// Ramp data: size=50, cycles=1, start=8V, stop=3V
fpvie0.AwgLoader("Vst", FV, FPVIe_10V, FPVIe_10MA, awg_pattern, sam);
fpvie0.Set(FV, 8, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
fpvie0.AwgSelect("Vst", 0, sam - 1, sam - 1, interval);
fpvie0.SetMeasVTrig(Trig, TRIG_FALLING);
fpvie0.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
qvme0.MeasureLADC(sample, 10, QVMe_LADC_10V, QVMe_LADC_10KHz, MEAS_AWG, 0, 0, 0, 0);
qvme0.SetMeasTrig(Trig, TRIG_FALLING);
STSEnableAWG(&fpvie0);
STSEnableMeas(&fpvie0, &qvme0);
STSAWGRun();  // Enable AWG and measurement synchronously
for (int SiteID = 0; SiteID < SITENUM; SiteID++)
{
    Trig_Point_qvme[SiteID] = qvme0.GetMeasResult(SiteID, TRIG_RESULT);
    result_qvme[SiteID] = qvme0.GetMeasResult(SiteID, Trig_Point_qvme[SiteID]);
    Trig_Point_fpvie[SiteID] = fpvie0.GetMeasResult(SiteID, MVRET, TRIG_RESULT);
    result_fpvie[SiteID] = fpvie0.GetMeasResult(SiteID, MVRET, Trig_Point_fpvie[SiteID]);
}
```

---

# Enum Type Summary

| Enum Type | Values |
|---|---|
| **TRIG_MODE** | `TRIG_FALLING`, `TRIG_RISING` |
| **QVMe_LADC_VRANG** | `QVMe_LADC_100V`, `QVMe_LADC_50V`, `QVMe_LADC_20V`, `QVMe_LADC_10V`, `QVMe_LADC_5V`, `QVMe_LADC_2V`, `QVMe_LADC_1V`, `QVMe_LADC_500MV`, `QVMe_LADC_200MV`, `QVMe_LADC_100MV` |
| **QVMe_LADC_FILTER** | `QVMe_LADC_400KHz`, `QVMe_LADC_100KHz`, `QVMe_LADC_40KHz`, `QVMe_LADC_10KHz` |
| **QVMe_HADC_VRANG** | `QVMe_HADC_4V`, `QVMe_HADC_2V`, `QVMe_HADC_1V` |
| **FLOATMEASMODE** | `MEAS_NORMAL`, `MEAS_AWG` |
| **MeasResult (sampleNumber)** | `AVERAGE_RESULT`, `MAX_RESULT`, `MIN_RESULT`, `TRIG_RESULT`, `RMS_RESULT` (negative ints); or non-negative N for specific sample |
| **QVMe_FFT_TYPE** | `QVMe_DIRECT_FFT`, `QVMe_BLACKMAN_HARRIS_FFT` |
| **FFT Result (retResult)** | `THD_RESULT`, `SNR_RESULT`, `SINAD_RESULT` (negative ints); or non-negative N for specific frequency bin amplitude |
| **HarmonicType** | `TOTAL_HARM`, `ODD_HARM`, `EVEN_HARM` |
| **QVMe_MEAS_RET** | `QVMe_SAMPLE_DATA`, `QVMe_FFT_DATA` |
| **CAL_RESULT** | `CAL_PASS`, `CAL_FAIL`, `STS_NO_RESULT_RECORD` |
| **CAL_METER** | `STS_KEITHLEY2000`, `STS_AGILENT34401`, `STS_AGILENT3458A`, `STS_NO_METER_RECORD` |

# Function Quick Reference

| # | Function | Signature Summary |
|---|---|---|
| 1 | `QVMe()` | Constructor: `QVMe(char* channelList, char* chName = NULL)` |
| 2 | `Init()` | Initialize: `int Init()` |
| 3 | `Connect()` | Connect relays: `void Connect()` |
| 4 | `Disconnect()` | Disconnect relays: `void Disconnect()` |
| 5 | `SetMeasTrig()` | Set trigger: `void SetMeasTrig(double VTrig, TRIG_MODE trigMode, double hysteresisValue)` |
| 6 | `MeasureLADC()` | LS ADC sample: `void MeasureLADC(UINT sampleTimes, double sampleInterval, QVMe_LADC_VRANG, QVMe_LADC_FILTER, FLOATMEASMODE, UINT T1-T4)` |
| 7 | `MeasureHADC()` | HS ADC sample: `void MeasureHADC(UINT sampleTimes, double sampleInterval, QVMe_HADC_VRANG, FLOATMEASMODE, UINT T1-T4)` |
| 8 | `GetMeasResult()` | Get result: `double GetMeasResult(UINT siteNo, int sampleNumber)` |
| 9 | `StartFFT()` | Start FFT: `void StartFFT(QVMe_FFT_TYPE fftType)` |
| 10 | `GetFFTResult()` | Get FFT result: `double GetFFTResult(UINT siteNo, int retResult, BYTE harmonicType, BYTE harmonicNum, double FreqBand)` |
| 11 | `BlockRead()` | Read data block: `void BlockRead(UINT siteNo, long startAddr, long size, double* buffer, QVMe_MEAS_RET retType)` |
| 12 | `SetAlarmMask()` | Set alarm mask: `void SetAlarmMask(UINT siteNo, bool maskStatus)` |
| 13 | `GetAlarmMask()` | Get alarm mask: `bool GetAlarmMask(UINT siteNo)` |
| 14 | `SiteBindModify()` | Reconfigure sites: `int SiteBindModify(char* modifySiteList)` |
| 15 | `GetBoardSN()` | Board SN: `int GetBoardSN(UINT siteNo, char* boardSN, UINT snSize)` |
| 16 | `GetBoardHDRev()` | Board HW rev: `int GetBoardHDRev(UINT siteNo, char* hardRev, UINT revSize)` |
| 17 | `GetCalibrationTime()` | Cal time: `SYSTEMTIME GetCalibrationTime(UINT siteNo) const` |
| 18 | `GetCalibrationTemperature()` | Cal temp: `double GetCalibrationTemperature(UINT siteNo) const` |
| 19 | `GetCalibrationHumidity()` | Cal humidity: `double GetCalibrationHumidity(UINT siteNo) const` |
| 20 | `GetCalibrationResult()` | Cal result: `CAL_RESULT GetCalibrationResult(UINT siteNo) const` |
| 21 | `GetCalibrationLogicRev()` | Cal logic rev: `int GetCalibrationLogicRev(UINT siteNo) const` |
| 22 | `GetCalibrationMeter()` | Cal meter: `CAL_METER GetCalibrationMeter(UINT siteNo, char* meterSN, UINT snSize)` |
| 23 | `GetCalibrationCalBoardInfo()` | Cal board info: `int GetCalibrationCalBoardInfo(UINT siteNo, char* boardSN, UINT snSize, char* HardRev, UINT revSize)` |
| 24 | `GetCalibrationSoftRev()` | Cal soft rev: `int GetCalibrationSoftRev(UINT siteNo, char* softRev, UINT revSize)` |
| 25 | `GetCalibrationSlotID()` | Cal slot ID: `int GetCalibrationSlotID(UINT siteNo) const` |
