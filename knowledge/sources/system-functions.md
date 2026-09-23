> 迁移自 auto-memory `STS8300-system-functions.md`（2026-08-16）

# STS8300 System Functions Reference (Chapter 1)

Extracted from: STS8300 Programming Manual v2.1.15, Pages 17-228
Date: 2026-07-14

---

## 1.1 Test Program Framework Functions (测试程序框架函数)

11 framework functions. All auto-generated in any test program (empty by default, user fills in).
- 4 functions in `test.cpp`: HardWareCfg, InitBeforeTestFlow, InitAfterTestFlow, SetupFailSite
- 7 functions in `xxxx.cpp` (test program name file)

### 1.1.1 HardWareCfg()
- **Signature**: `void HardWareCfg()`
- **Remarks**: Hardware site configuration function. System supports up to 32 sites. Hardware configuration uses STSSetMultiSiteBind (section 1.2.6).
- **Called**: Once during program load.
- **Example**: See 1.2.6 for binding examples.

### 1.1.2 InitBeforeTestFlow()
- **Signature**: `void InitBeforeTestFlow()`
- **Remarks**: Executed ONCE before ALL test functions, every test run.

### 1.1.3 InitAfterTestFlow()
- **Signature**: `void InitAfterTestFlow()`
- **Remarks**: Executed ONCE after ALL test functions, every test run.

### 1.1.4 UserInit()
- **Signature**: `void UserInit()`
- **Remarks**: Called ONCE the first time after loading the program for testing.

### 1.1.5 UserLoad()
- **Signature**: `void UserLoad()`
- **Remarks**: Called ONCE when user loads the program. Use for initialization that needs Load-time execution.

### 1.1.6 UserExit()
- **Signature**: `void UserExit()`
- **Remarks**: Called ONCE when user unloads the program.

### 1.1.7 OnSot()
- **Signature**: `void OnSot()`
- **Remarks**: Called every time after receiving SOT (Start of Test) signal during automatic testing.

### 1.1.8 SetupFailSite()
- **Signature**: `void SetupFailSite()`
- **Remarks**: Called after a Fail occurs in any test function when user has selected FailStop.
- **Warning**: For failed sites, set resources to a safe state in this function.

### 1.1.9 BinOutDut()
- **Signature**: `void BinOutDut()`
- **Remarks**: Called after the DUT test is complete and binning is determined. User can get binning info and/or implement code-based binning here.

### 1.1.10 OnNewLot()
- **Signature**: `void OnNewLot(const char* Lotid)`
- **Remarks**: Called when user clicks NewLot on UI, or when a new LotID is read during wafer testing.

### 1.1.11 OnWaferEnd()
- **Signature**: `void OnWaferEnd()`
- **Remarks**: Called ONCE after receiving the wafer end signal.

---

## 1.2 Global Functions (全局函数)

Main purposes: Get Site, LotID, XY coordinates, module existence, Bin info, and independently control sites.

### 1.2.1 BEGIN_SINGLE_SITE()
- **Signature**: `BEGIN_SINGLE_SITE(SiteID)`
- **Parameters**: `SiteID` - Serial site number (recommend BYTE type)
- **Remarks**: With multi-site hardware binding, uses pair BEGIN_SINGLE_SITE()/END_SINGLE_SITE() to act on a single site independently while other sites' hardware is unaffected.
- **Warning**: BEGIN_SINGLE_SITE() and END_SINGLE_SITE() MUST always be used in pairs.
- **Example**:
```cpp
double result[4] = {1,2,3,4};
fovie0.Set(FV, 5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
for (BYTE i = 0; i < 4; i++) {
    BEGIN_SINGLE_SITE(i)
    fovie0.Set(FV, result[i], FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_ms(1);
    END_SINGLE_SITE()
}
```

### 1.2.2 END_SINGLE_SITE()
- **Signature**: `END_SINGLE_SITE()`
- **Remarks**: Used in pair with BEGIN_SINGLE_SITE(). See 1.2.1.

### 1.2.3 delay_ms()
- **Signature**: `void USERRES_API delay_ms(DWORD dw_ms);`
- **Parameters**: `dw_ms` - Delay time in milliseconds
- **Remarks**: Delay function.

### 1.2.4 delay_us()
- **Signature**: `void USERRES_API delay_us(DWORD dw_us);`
- **Parameters**: `dw_us` - Delay time in microseconds
- **Remarks**: Delay function.

### 1.2.5 STSEnableCfgCheck()
- **Signature**: `int STSEnableCfgCheck();`
- **Remarks**: Sets system hardware configuration check. The check scope is based on STSSetMultiSiteBind() settings.
- **Example**:
```cpp
STSEnableCfgCheck();
STSSetMultiSiteBind(MD_FOVIe, SITE_1, "S13_0-7");
STSSetMultiSiteBind(MD_FOVIe, SITE_2, "S14_0-7");
STSSetMultiSiteBind(MD_FOVIe, SITE_3, "S19_0-7");
STSSetMultiSiteBind(MD_FOVIe, SITE_4, "S20_0-7");
// If system has fewer than 4 FOVIe boards, error will be reported
```

### 1.2.6 STSSetMultiSiteBind()
- **Signature**: `int USERRES_API STSSetMultiSiteBind(MODULE_TYPE mdtype, AT_SITE_NO sitenum, char* ChannelList);`
- **Parameters**:
  - `mdtype` - Module type: `MD_FPVIe`, `MD_FOVIe`, `MD_HVIe`, `MD_ACM`, `MD_QVMe`, `MD_QTMUe`, `MD_HPVIe`, `MD_FXVIe`
  - `sitenum` - Site number: `SITE_1` through `SITE_32`, or `NO_SITE`
  - `ChannelList` - String format: Slot+channel using S, _, comma, dash. E.g., `"S13_0-7"`, `"S13_0,S13_2,S13_5"`
- **Return**: Returns total channel count assigned to sitenum
- **Remarks**: Sets parallel mode for a module. The program site count is determined by the maximum site count across all modules.
- **Warning**: CBITe and DCM modules do NOT use this for site binding.
- **Channel limits per module board**:
  - MD_FPVIe: max channel 1
  - MD_FOVIe: max channel 7
  - MD_HVIe: max channel 0
  - MD_ACM: max channel 23
  - MD_QVMe: max channel 3
  - MD_QTMUe: max channel 3
  - MD_HPVIe: max channel 0
  - MD_FXVIe: max channel 11
- **ChannelList rules** (strict, or system error):
  1. Only allowed chars: `S`, `_`, `,`, `-`, positive integers
  2. Channel index starts from 0
  3. Same slot+channel cannot be configured twice
  4. Same site cannot be configured twice for same module
  5. NO_SITE channels are not limited by site mask - any valid site can control them
- **Example** (4-site, 4 FOVIe):
```cpp
STSSetMultiSiteBind(MD_FOVIe, SITE_1, "S5_0-7");
STSSetMultiSiteBind(MD_FOVIe, SITE_2, "S11_0-7");
STSSetMultiSiteBind(MD_FOVIe, SITE_3, "S22_0-7");
STSSetMultiSiteBind(MD_FOVIe, SITE_4, "S28_0-7");
```

### 1.2.7 STSCBITeMultiSiteBind()
- **Signature**: `int USERRES_API STSCBITeMultiSiteBind(AT_SITE_NO siteNo, char* ChannelList);`
- **Parameters**:
  - `siteNo` - SITE_1 through SITE_32, or NO_SITE
  - `ChannelList` - CBITe channel list string. Only `,`, `-`, non-negative integers allowed. Max channel 255.
- **Return**: Total channel count assigned to siteNo
- **Remarks**: Sets CBITe channels per site. Must be called in HardWareCfg().
- **SetOn relay rules**:
  1. Only channels bound to active sites and NO_SITE are closed
  2. Inactive site channels are opened
  3. Unbound channels keep previous state
  4. All unspecified channels are opened
- **Warning**: NO_SITE ignores site validity. If CBITe is not site-bound, original channel rules apply. Debug tool is not restricted by this binding.
- **Example**:
```cpp
STSCBITeMultiSiteBind(SITE_1, "0,1,2,3");
STSCBITeMultiSiteBind(SITE_2, "4,5,6,7");
STSCBITeMultiSiteBind(NO_SITE, "10,11");
CBITe cbite;
cbite.SetOn(0, 4, 8, 10, -1);
// If SITE_1 active, SITE_2 inactive: ch0 and ch10 close; ch4 opens; ch8 unchanged; all others open
```

### 1.2.8 STSSetMultiSiteBindEx()
- **Signature**: `int USERRES_API STSSetMultiSiteBindEx(MODULE_TYPE mdtype, int sitenum, char* ChannelList);`
- **Parameters**:
  - `mdtype` - Same as STSSetMultiSiteBind
  - `sitenum` - Non-negative integer (0=Site1, 1=Site2... up to 250=Site251), or -1/NO_SITE
  - `ChannelList` - Same format rules as STSSetMultiSiteBind
- **Return**: Total channel count assigned
- **Remarks**: Extended version supporting up to 251 sites (max 251 on STS8300). Same ChannelList rules apply.
- **Warning**: CBITe and DCM modules do NOT use this for site binding.
- **Example** (40-site, 5 FOVIe boards):
```cpp
STSSetMultiSiteBindEx(MD_FOVIe, 0, "S5_0");  // Site 1
STSSetMultiSiteBindEx(MD_FOVIe, 1, "S5_1");  // Site 2
// ... through 39
```

### 1.2.9 STSCBITeMultiSiteBindEx()
- **Signature**: `int USERRES_API STSCBITeMultiSiteBindEx(int siteNo, char* ChannelList);`
- **Parameters**:
  - `siteNo` - 0=Site1...250=Site251, or -1/NO_SITE
  - `ChannelList` - Same CBITe channel rules (max channel 255)
- **Return**: Total channel count assigned
- **Remarks**: Extended CBITe binding supporting up to 251 sites. Same SetOn rules as STSCBITeMultiSiteBind.
- **Example**:
```cpp
STSCBITeMultiSiteBindEx(0, "0,1,2,3");
STSCBITeMultiSiteBindEx(1, "4,5,6,7");
STSCBITeMultiSiteBind(NO_SITE, "10,11");
```

### 1.2.10 STSSetSiteStatus()
- **Signature**: `void USERRES_API STSSetSiteStatus(DWORD siteID);`
- **Parameters**: `siteID` - Bitmask: each bit = 1 site. 0xFFFFFFFF = all 32 valid, 0x00000000 = all invalid
- **Remarks**: Sets site validity. Max 32 sites.
- **Warning**: Restore previous site status after use (use with STSGetSiteStatus).
- **Example**:
```cpp
STSSetSiteStatus(0x0001); // Only Site1 valid
STSSetSiteStatus(0x000F); // Site1-4 valid
STSSetSiteStatus(0xFFFF); // Site1-16 valid
```

### 1.2.11 STSGetSiteStatus()
- **Signature**: `int STSGetSiteStatus(BYTE* bysitestatus, int sitecnt);`
- **Parameters**:
  - `bysitestatus` - Array pointer. Member = 1 means valid, 0 means masked
  - `sitecnt` - Number of sites to query. Ensure buffer is large enough.
- **Return**: 0 = normal, -1 = bysitestatus NULL or size < 0
- **Remarks**: Gets site enable status. Max sites queried cannot exceed program site count.
- **Example**:
```cpp
BYTE sitesta[4];
STSGetSiteStatus(sitesta, 4);
```

### 1.2.12 STSGetSiteRunStatus()
- **Signature**: `int STSGetSiteRunStatus(BYTE* bysitestatus, int sitecnt);`
- **Parameters**:
  - `bysitestatus` - Array pointer. 1 = site executes test this round, 0 = does not
  - `sitecnt` - Number of sites. Ensure buffer is large enough.
- **Return**: 0 = normal, -1 = bysitestatus NULL or size < 0
- **Remarks**:
  - Between UserInit->BinOutDut: returns intersection of SOT received site status AND TestUI selected site status
  - In UserLoad: function is invalid
  - In other functions: returns TestUI user-selected site status
- **Warning**: Site status values beyond program site count are invalid.
- **Example**:
```cpp
BYTE sitesta[4];
STSGetSiteRunStatus(sitesta, 4);
```

### 1.2.13 STSSetSiteStatusEx()
- **Signature**: `int USERRES_API STSSetSiteStatusEx(BYTE* siteStatus, int size);`
- **Parameters**:
  - `siteStatus` - Array. 1 = valid, 0 = invalid
  - `size` - Array size
- **Remarks**: Extended version, max 251 sites. Restore after use (pair with STSGetSiteStatusEx).
- **Example**:
```cpp
BYTE siteStatus[64] = {0};
siteStatus[0] = 1;    // Site1 valid
siteStatus[63] = 1;   // Site64 valid
STSSetSiteStatusEx(siteStatus, 64);
```

### 1.2.14 STSGetSiteStatusEx()
- **Signature**: `int USERRES_API STSGetSiteStatusEx(BYTE* siteStatus, int size);`
- **Parameters**: `siteStatus` - Array pointer. `size` - Number of sites. Ensure enough buffer.
- **Return**: 0 = normal, -1 = siteStatus NULL or size < 0
- **Remarks**: Extended version, max 251 sites.
- **Example**:
```cpp
BYTE sitesta[64] = {0};
STSGetSiteStatusEx(sitesta, 64);
```

### 1.2.15 STSGetSingleSiteStatus()
- **Signature**: `int USERRES_API STSGetSingleSiteStatus(UINT siteNo);`
- **Parameters**: `siteNo` - Site number (0=Site1, ...). Must be less than program site count.
- **Return**: 0 = masked, 1 = valid, -1 = siteNo >= program site count
- **Remarks**: Get specified site status. Max supports siteNo=250 (Site 251).
- **Example**:
```cpp
int siteStatus = STSGetSingleSiteStatus(0); // Get Site1 status
```

### 1.2.16 STSGetOperatorID()
- **Signature**: `int STSGetOperatorID(char* operatorid, int charCnt);`
- **Parameters**:
  - `operatorid` - Buffer for operator ID string
  - `charCnt` - Requested length, must not exceed operatorid array length
- **Return**: -1 if not set (empty string), 0 = normal
- **Remarks**: Gets the UI operator's login ID.
- **Example**:
```cpp
char operatorid[10];
STSGetOperatorID(operatorid, 5);
```

### 1.2.17 STSGetWaferID()
- **Signature**: `int STSGetWaferID(char* waferid, int charCnt);`
- **Parameters**:
  - `waferid` - Buffer for wafer ID
  - `charCnt` - Requested length, must not exceed waferid array length
- **Return**: -1 if not set (empty), 0 = normal
- **Remarks**: Gets the wafer ID.
- **Example**:
```cpp
char waferid[10];
STSGetWaferID(waferid, 5);
```

### 1.2.18 STSGetLotID()
- **Signature**: `int STSGetLotID(char* lotid, int charCnt);`
- **Parameters**:
  - `lotid` - Buffer for Lot ID
  - `charCnt` - Requested length, must not exceed lotid array length
- **Return**: -1 if not set (empty), 0 = normal
- **Remarks**: Gets the Lot ID.
- **Example**:
```cpp
char lotid[10];
STSGetLotID(lotid, 5);
```

### 1.2.19 STSGetCurrentDutSwBin()
- **Signature**: `short STSGetCurrentDutSwBin(int sitecnt);`
- **Parameters**: `sitecnt` - Site number (0-based)
- **Return**: -1 if sitecnt exceeds program site count, 0 if bin not defined, otherwise SoftBin number
- **Remarks**: Gets real-time SoftBin for each site's device.
- **Example**:
```cpp
short SwBin = STSGetCurrentDutSwBin(0); // Get Site1 SoftBin
```

### 1.2.20 STSGetCurrentDutHwBin()
- **Signature**: `short STSGetCurrentDutHwBin(int sitecnt);`
- **Parameters**: `sitecnt` - Site number (0-based)
- **Return**: -1 if sitecnt exceeds program site count, 0 if bin not defined, otherwise HardBin number
- **Remarks**: Gets real-time HardBin for each site's device.
- **Example**:
```cpp
short HwBin = STSGetCurrentDutHwBin(0); // Get Site1 HardBin
```

### 1.2.21 StsGetParam()
- **Signature**: `CParam* StsGetParam(short funcIndex, LPCTSTR lpParamName);`
- **Parameters**:
  - `funcIndex` - Function index
  - `lpParamName` - Parameter name
- **Return**: Parameter pointer, or NULL if parameter is deleted
- **Remarks**: Gets function parameter pointer. If returns NULL, do NOT use for value assignment or condition operations.

### 1.2.22 StsGetBinDutTotalCount()
- **Signature**: `int StsGetBinDutTotalCount(int iBinNumber, int sitecnt);`
- **Parameters**:
  - `iBinNumber` - Bin number
  - `sitecnt` - Site number
- **Return**: Number of devices in specified bin at specified site; -1 if site/bin out of range
- **Remarks**: Gets per-site bin device count.

### 1.2.23 StsAddUserSummaryStr()
- **Signature**: `int StsAddUserSummaryStr(LPSTR strsum);`
- **Parameters**: `strsum` - Custom Summary info to add
- **Return**: -1 if same as last (not added), -2 if empty, 0 = success
- **Remarks**: Adds custom user Summary information.

### 1.2.24 StsMessageBox()
- **Signature**: `int StsMessageBox(LPCSTR lpText, LPCSTR lpCaption);`
- **Parameters**: `lpText` - Prompt text, `lpCaption` - Window title
- **Remarks**: Pops up a message dialog.

### 1.2.25 StsGetSiteCount()
- **Signature**: `int StsGetSiteCount();`
- **Return**: Site count defined in PGS
- **Remarks**: Gets PGS-configured site count.

### 1.2.26 STSGetPgsName()
- **Signature**: `int STSGetPgsName(LPTSTR pgsName, int chNum);`
- **Parameters**:
  - `pgsName` - Buffer for PGS filename
  - `chNum` - Buffer size
- **Return**: -1 if chNum < 1, 0 = normal
- **Remarks**: Gets currently loaded PGS filename.

### 1.2.27 STSGetPgsPath()
- **Signature**: `int STSGetPgsPath(LPTSTR pgsPath, int chNum);`
- **Parameters**:
  - `pgsPath` - Buffer for PGS file path
  - `chNum` - Buffer size
- **Return**: -1 if chNum < 1, 0 = normal
- **Remarks**: Gets currently loaded PGS file path.

### 1.2.28 STSSetTimeCheck()
- **Signature**: `int STSSetTimeCheck(int tag);`
- **Parameters**: `tag` - Time marker number. Call moment recorded as start time.
- **Return**: 0
- **Remarks**: Sets time check marker. Used with STSGetTimeElapsed. Multiple calls with same tag use the last-set time as start.

### 1.2.29 STSGetTimeElapsed()
- **Signature**: `double STSGetTimeElapsed(int tag);`
- **Parameters**: `tag` - Time marker number
- **Return**: Time elapsed from STSSetTimeCheck to this call, in milliseconds
- **Remarks**: Used in pair with STSSetTimeCheck.

### 1.2.30 STSSetSaveInterval()
- **Signature**: `int STSSetSaveInterval(int interval);`
- **Parameters**: `interval` - Save interval
- **Return**: -2 if interval < 0, 0 = success
- **Remarks**: Sets data save sampling interval (mode: save all fail data).

### 1.2.31 STSStopProgram()
- **Signature**: `int STSStopProgram();`
- **Remarks**: Stops current test program. After executing the function containing this call, skips all subsequent test functions and jumps to InitAfterTestFlow.

### 1.2.32 STSStartNewLot()
- **Signature**: `int STSStartNewLot();`
- **Remarks**: Starts next test batch. If in auto-test mode, stops current test and pops up NewLot dialog.

### 1.2.33 STSGetUserPriority()
- **Signature**: `int STSGetUserPriority();`
- **Return**: `OPERATOR = 1`, `ENGINEER = 2`, `ADMIN = 3`
- **Remarks**: Gets current logged-in user's privilege level.

### 1.2.34 STSSetEnableCalCheck()
- **Signature**: `int STSSetEnableCalCheck(BOOL bEnable = TRUE, int iCalMonthInterval = 6);`
- **Parameters**:
  - `bEnable` - Enable calibration check (default TRUE)
  - `iCalMonthInterval` - Calibration interval in months (1-12, 30 days/month). Default 6.
- **Return**: 0 = success, -1 = error
- **Remarks**: Enable/disable calibration check. Checks FPVIe, FOVIe, ACM, HVIe, QTMUe, QVMe, DCM, HPVIe, FXVIe calibration pass and time.
- **Warning**: Check is per-site based on HardwareCfg resources. Must call in UserLoad.

### 1.2.35 STSGetPartIDText()
- **Signature**: `const char* STSGetPartIDText(short siteNum);`
- **Parameters**: `siteNum` - Site number
- **Return**: PartID string for the site
- **Remarks**: Get user-defined or auto-generated PartID for a site.

### 1.2.36 STSSetEnableAlarm()
- **Signature**: `int STSSetEnableAlarm(BOOL bEnable = TRUE);`
- **Parameters**: `bEnable` - Enable alarm (default TRUE)
- **Return**: 0 = success, -1 = error
- **Remarks**: Enables parameter alarm. Takes priority over UI setting. When enabled: hardware clamp alarms and out-of-range parameter settings are recorded. If AlarmBin is set, device goes to AlarmBin.

### 1.2.37 STSSetWriteAlarmFile()
- **Signature**: `void STSSetWriteAlarmFile(BOOL alarmfile_flag);`
- **Parameters**: `alarmfile_flag` - TRUE = store, FALSE = don't store alarm info
- **Remarks**: When alarm is enabled, by default all alarm info is stored. If many alarms slow down testing, call this before test to disable alarm info storage.

### 1.2.38 STSTArming()
- **Signature**: `int STSTArming();`
- **Remarks**: Waits for Turbo-mode operations to complete.
- **Example**:
```cpp
fxvie0.TSet(FV, 4, FXVIe_5V, FXVIe_100MA, FXVIe_RELAY_ON); // Turbo Set
STSTArming(); // Turbo Arming (wait for completion)
```

---

## 1.3 Test Parameter Functions (测试参数相关函数)

Used to get PGS test parameter info (limits, condition count, etc.) and set parameter test results. Most commonly used: SetTestResult().

### 1.3.1 SetTestResult()
- **Signature**: `int SetTestResult(short sSiteID, short sSubUnitID, double dResult);`
- **Parameters**:
  - `sSiteID` - Site number (0=Site1, 1=Site2...)
  - `sSubUnitID` - Sub-unit number (0=unit1, 1=unit2...)
  - `dResult` - Test result value
- **Return**: 0 = success, non-zero = failure
- **Remarks**: Sets parameter test result.
- **Example**:
```cpp
fovie0.MeasureVI(20, 10);
for (i = 0; i < SITENUM; i++) {
    adresult[i] = fovie0.GetMeasResult(i, MIRET);
    Icc->SetTestResult(i, 0, adresult[i] * 1000);
}
```

### 1.3.2 GetTestResult()
- **Signature**: `double GetTestResult(short sSiteID, short sSubUnitID);`
- **Parameters**: `sSiteID` - Site (0=Site1...), `sSubUnitID` - Sub-unit (0=unit1...)
- **Return**: Test result value
- **Remarks**: Gets parameter test result.
- **Example**:
```cpp
double result = param->GetTestResult(0, 0);
```

### 1.3.3 SetResultRemark()
- **Signature**: `int SetResultRemark(short sSiteID, short sSubUnitID, LPCTSTR lpszremark);`
- **Parameters**:
  - `sSiteID` - Site (0=Site1...)
  - `sSubUnitID` - Sub-unit (0=unit1...)
  - `lpszremark` - Remark string pointer
- **Return**: 0 = success, non-zero = failure
- **Remarks**: Sets test result remark/comment.
- **Warning**:
  1. To display remarks, enable TestUI Options->View->ShowComment Textinresult
  2. Remarks are NOT saved in test data
- **Example**:
```cpp
Icc->SetResultRemark(i, 0, "Icc_5V");
```

### 1.3.4 GetResultRemark()
- **Signature**: `short GetResultRemark(short sSiteID, short sSubUnitID, LPTSTR lpszResultRemark, DWORD cbBuf);`
- **Parameters**:
  - `sSiteID` - Site (0=Site1...)
  - `sSubUnitID` - Sub-unit (0=unit1...)
  - `lpszResultRemark` - Buffer for remark string
  - `cbBuf` - Buffer length
- **Return**: Test result remark
- **Example**:
```cpp
char sRemark[50];
memset(sRemark, 0, 50);
param->GetResultRemark(0, 0, sRemark, 50);
```

### 1.3.5 GetMinLimit()
- **Signature**: `double GetMinLimit();`
- **Return**: Parameter lower limit
- **Remarks**: Gets parameter lower limit.

### 1.3.6 GetMaxLimit()
- **Signature**: `double GetMaxLimit();`
- **Return**: Parameter upper limit
- **Remarks**: Gets parameter upper limit.

### 1.3.7 GetSubUnitsCount()
- **Signature**: `short GetSubUnitsCount();`
- **Return**: Sub-unit count
- **Remarks**: Gets parameter sub-unit count.
- **Example**:
```cpp
short subUnitCnt = param->GetSubUnitsCount();
```

### 1.3.8 GetDispFormat()
- **Signature**: `short GetDispFormat(LPTSTR lpszDispFormat, DWORD cbBuf);`
- **Return**: Display format string (e.g., "0.00")
- **Remarks**: Gets test result display format.

### 1.3.9 GetDescription()
- **Signature**: `short GetDescription(LPTSTR lpszDescription, DWORD cbBuf);`
- **Parameters**:
  - `lpszDescription` - Buffer for description string
  - `cbBuf` - Buffer size
- **Return**: 0 = success, positive = actual needed size (cbBuf < needed), negative = failure
- **Remarks**: Gets parameter description.
- **Example**:
```cpp
char sDescription[50];
memset(sDescription, 0, 50);
param->GetDescription(sDescription, 50);
```

### 1.3.10 GetConditionsCnt()
- **Signature**: `short GetConditionsCnt();`
- **Return**: Number of test conditions for the parameter
- **Remarks**: Gets test condition count.
- **Example**:
```cpp
short CondtionCnt = param->GetConditionsCnt();
```

### 1.3.11 GetConditionDispName()
- **Signature**: `short GetConditionDispName(const int index, LPTSTR lpszCondName, DWORD cbBuf);`
- **Parameters**:
  - `index` - Condition index (0-based)
  - `lpszCondName` - Buffer for condition display name
  - `cbBuf` - Buffer size
- **Return**: 0 = success, positive = actual needed size, negative = failure
- **Remarks**: Gets condition display name.
- **Example**:
```cpp
char sCondName[50];
memset(sCondName, 0, 50);
param->GetConditionDispName(0, sCondName, 50);
```

### 1.3.12 GetConditionSymbol()
- **Signature (overload 1)**: `short GetConditionSymbol(int index, LPTSTR lpszCondSymbol, DWORD cbBuf);`
- **Signature (overload 2)**: `short GetConditionSymbol(LPCTSTR lpszCondName, LPTSTR lpszCondSymbol, DWORD cbBuf);`
- **Parameters**: `index` (0-based) or `lpszCondName` (condition name)
- **Return**: 0 = success, positive = actual needed size, negative = failure
- **Remarks**: Gets condition alias/symbol.
- **Example**:
```cpp
param->GetConditionSymbol(0, sCondSymbol, 50);
param->GetConditionSymbol("Voltage", sCondSymbol, 50);
```

### 1.3.13 GetConditionShowKind()
- **Signature (overload 1)**: `BYTE GetConditionShowKind(int index);`
- **Signature (overload 2)**: `BYTE GetConditionShowKind(LPCTSTR lpszCondName);`
- **Parameters**: `index` (0-based) or `lpszCondName`
- **Return**: BYTE display type
- **Remarks**: Returns condition display type.
- **Example**:
```cpp
BYTE ShowKind = param->GetConditionShowKind("Voltage");
BYTE ShowKind1 = param->GetConditionShowKind(0);
```

### 1.3.14 GetConditionInputKind()
- **Signature (overload 1)**: `BYTE GetConditionInputKind(int index);`
- **Signature (overload 2)**: `BYTE GetConditionInputKind(LPCTSTR lpszCondName);`
- **Parameters**: `index` (0-based) or `lpszCondName`
- **Return**: 0 = fill-in, 1 = dropdown select, 2 = multi-select dropdown
- **Remarks**: Gets condition input format type.
- **Example**:
```cpp
BYTE InputKind = param->GetConditionInputKind("Voltage");
```

### 1.3.15 GetConditionDispValue()
- **Signature (overload 1)**: `short GetConditionDispValue(int index, LPTSTR lpszCondDispValue, DWORD cbBuf);`
- **Signature (overload 2)**: `short GetConditionDispValue(LPCTSTR lpszCondName, LPTSTR lpszCondDispValue, DWORD cbBuf);`
- **Return**: 0 = success, positive = needed size, negative = failure
- **Remarks**: Gets all selectable values, separated by ";".
- **Example**:
```cpp
param->GetConditionDispValue(0, sCondAllValue, 50);
param->GetConditionDispValue("Voltage", sCondAllValue, 50);
```

### 1.3.16 GetConditionDispUnit()
- **Signature (overload 1)**: `short GetConditionDispUnit(int index, LPTSTR lpszDispUnit, DWORD cbBuf);`
- **Signature (overload 2)**: `short GetConditionDispUnit(LPCTSTR lpszCondName, LPTSTR lpszDispUnit, DWORD cbBuf);`
- **Return**: 0 = success, positive = needed size, negative = failure
- **Remarks**: Gets all selectable units, separated by ";".
- **Example**:
```cpp
param->GetConditionDispUnit(0, sCondAllUnit, 50);
param->GetConditionDispUnit("Voltage", sCondAllUnit, 50);
```

### 1.3.17 GetTestConditionValue()
- **Signature (overload 1)**: `short GetTestConditionValue(int index, LPTSTR lpszCondValue, DWORD cbBuf);`
- **Signature (overload 2)**: `short GetTestConditionValue(LPCTSTR lpszCondName, LPTSTR lpszCondValue, DWORD cbBuf);`
- **Return**: 0 = success, positive = needed size, negative = failure
- **Remarks**: Gets condition current value.
- **Example**:
```cpp
param->GetTestConditionValue(0, sCondValue, 50);
param->GetTestConditionValue("Voltage", sCondValue, 50);
```

### 1.3.18 GetConditionCurSelDouble()
- **Signature (overload 1)**: `double GetConditionCurSelDouble(short index);`
- **Signature (overload 2)**: `double GetConditionCurSelDouble(LPCTSTR lpszCondName);`
- **Return**: Current selected value as double
- **Remarks**: Gets condition current value as double.
- **Example**:
```cpp
double value = param->GetConditionCurSelDouble(0);
double value = param->GetConditionCurSelDouble("Voltage");
```

### 1.3.19 GetConditionValueSelOrder()
- **Signature (overload 1)**: `int GetConditionValueSelOrder(short index);`
- **Signature (overload 2)**: `int GetConditionValueSelOrder(LPCTSTR lpszCondName);`
- **Return**: For dropdown type, returns the ordinal position of current selection among all options (0-based)
- **Remarks**: Get selection ordinal among all options.
- **Example**:
```cpp
// Options: "50;40;20;10;5.2;1", current=20 => returns 2
double valueOrder = param->GetConditionValueSelOrder(0);
```

### 1.3.20 GetConditionSelectUnit()
- **Signature (overload 1)**: `short GetConditionSelectUnit(int index, LPTSTR lpszCondSelUnit, DWORD cbBuf);`
- **Signature (overload 2)**: `short GetConditionSelectUnit(LPCTSTR lpszCondName, LPTSTR lpszCondSelUnit, DWORD cbBuf);`
- **Return**: 0 = success, positive = needed size, negative = failure
- **Remarks**: Gets condition currently selected unit.
- **Example**:
```cpp
param->GetConditionSelectUnit(0, sCondUnit, 50);
param->GetConditionSelectUnit("Voltage", sCondUnit, 50);
```

### 1.3.21 GetConditionUnitSelOrder()
- **Signature (overload 1)**: `int GetConditionUnitSelOrder(short index);`
- **Signature (overload 2)**: `int GetConditionUnitSelOrder(LPCTSTR lpszCondName);`
- **Return**: For dropdown, ordinal position of current unit selection (0-based)
- **Remarks**: Gets unit selection ordinal.
- **Example**:
```cpp
// Units: "V;mV;uV", current="V" => returns 0
double valueOrder = param->GetConditionUnitSelOrder("Voltage");
```

### 1.3.22 GetParamStationNo()
- **Signature**: `short GetParamStationNo();`
- **Return**: Station number where the parameter resides (excluding empty stations)
- **Remarks**: For multi-station mode, gets parameter's test station.
- **Example**:
```cpp
short nStationNum = Icc->GetParamStationNo();
```

### 1.3.23 GetConditionDispTip()
- **Signature (overload 1)**: `short GetConditionDispTip(int index, LPTSTR lpszCondDispTip, DWORD cbBuf);`
- **Signature (overload 2)**: `short GetConditionDispTip(LPCTSTR lpszCondName, LPTSTR lpszCondDispTip, DWORD cbBuf);`
- **Return**: 0 = success, positive = needed size, negative = failure
- **Remarks**: Gets condition current tooltip.
- **Example**:
```cpp
param->GetConditionDispTip(0, sCondUnit, 50);
param->GetConditionDispTip("Voltage", sCondUnit, 50);
```

---

## 1.16 Advanced Function Application (进阶功能应用函数)

### 1.16.1 STSUpdateFunTest()
- **Signature**: `int STSUpdateFunTest(int nFun, BOOL bTest);`
- **Parameters**:
  - `nFun` - Function number
  - `bTest` - Whether to execute test (TRUE/FALSE)
- **Return**: 0 = success, -1 = called outside UserLoad, -2 = function does not exist
- **Remarks**: Set whether function executes test. **Must be called in UserLoad.**
- **Example**:
```cpp
int nRet = STSUpdateFunTest(0, TRUE);
```

### 1.16.2 STSShowLimitDlg()
- **Signature**: `int STSShowLimitDlg();`
- **Return**: 0 = limit set successfully, 1 = user didn't click OK, 2 = called outside UserLoad, -1 = limit does not exist
- **Remarks**: Displays limit selection dialog. **Must be called in UserLoad.**

### 1.16.3 STSSetUseLimitbyID()
- **Signature**: `int STSSetUseLimitbyID(unsigned int nID);`
- **Parameters**: `nID` - Limit group ID
- **Return**: 0 = success, 2 = called outside UserLoad, -1 = failure
- **Remarks**: Set test limits by limit ID. **Must be called in UserLoad.**
- **Example**:
```cpp
int nRet = STSSetUseLimitbyID(0);
```

### 1.16.4 STSSetUseLimitbyName()
- **Signature**: `int STSSetUseLimitbyName(const char* pcName);`
- **Parameters**: `pcName` - Limit name
- **Return**: 0 = success, 2 = called outside UserLoad, -1 = failure
- **Remarks**: Set test limits by limit name. **Must be called in UserLoad.**
- **Example**:
```cpp
int nRet = STSSetUseLimitbyName("FT");
```

### 1.16.5 STSGetLimitCount()
- **Signature**: `unsigned int STSGetLimitCount();`
- **Return**: Number of limit groups in the system
- **Remarks**: Gets total limit group count.
- **Example**:
```cpp
unsigned int nRet = STSGetLimitCount();
```

### 1.16.6 STSGetLimitName()
- **Signature**: `const char* STSGetLimitName(unsigned int nID);`
- **Parameters**: `nID` - Limit group ID
- **Return**: Limit name string
- **Remarks**: Get limit group name by ID.
- **Example**:
```cpp
const char* pcData = STSGetLimitName(nID);
```

### 1.16.7 STSGetUseLimitID()
- **Signature**: `unsigned int STSGetUseLimitID();`
- **Return**: Currently active limit group ID
- **Remarks**: Get the ID of the limit group currently in use.

### 1.16.8 STSGetUseLimitName()
- **Signature**: `const char* STSGetUseLimitName();`
- **Return**: Currently active limit group name
- **Remarks**: Get the name of the limit group currently in use.

### 1.16.9 STSGetMustResult()
- **Signature**: `CSTSMustResult* STSGetMustResult();`
- **Return**: CSTSMustResult operation class pointer
- **Remarks**: Get MustResult (required assignment) function operation class. See CSTSMustResult section (1.16.21) for methods.
- **Example**:
```cpp
CSTSMustResult* pMustResult = STSGetMustResult();
```

### 1.16.10 STSGetFunction()
- **Signature**: `CFunctionTest* STSGetFunction(unsigned int nID);`
- **Parameters**: `nID` - Function number
- **Return**: Function pointer (CFunctionTest*)
- **Remarks**: Get function pointer. See CFunctionTest section (1.16.20) for methods.
- **Example**:
```cpp
CFunctionTest* pFun = STSGetFunction(0);
```

### 1.16.11 STSShowBinDlg()
- **Signature**: `int STSShowBinDlg();`
- **Return**: 0 = bin set successfully, 1 = user didn't click OK, 2 = called outside UserLoad, 3 = no options, -1 = bin combination does not exist
- **Remarks**: Displays bin selection dialog. **Must be called in UserLoad.**

### 1.16.12 STSSetUseBinbyID()
- **Signature**: `int STSSetUseBinbyID(unsigned int nID);`
- **Parameters**: `nID` - Bin group ID
- **Return**: 0 = success, 2 = called outside UserLoad, -1 = failure
- **Remarks**: Set test bin by ID. **Must be called in UserLoad.**
- **Example**:
```cpp
int nRet = STSSetUseBinbyID(0);
```

### 1.16.13 STSSetUseBinbyName()
- **Signature**: `int STSSetUseBinbyName(const char* pcName);`
- **Parameters**: `pcName` - Bin combination name
- **Return**: 0 = success, 2 = called outside UserLoad, -1 = failure
- **Remarks**: Set test bin by name. **Must be called in UserLoad.**
- **Example**:
```cpp
int nRet = STSSetUseBinbyName("FT");
```

### 1.16.14 STSGetBinCount()
- **Signature**: `unsigned int STSGetBinCount();`
- **Return**: Number of bin combinations in the system
- **Remarks**: Gets total bin combination count.
- **Example**:
```cpp
unsigned int nRet = STSGetBinCount();
```

### 1.16.15 STSGetBinName()
- **Signature**: `const char* STSGetBinName(unsigned int nID);`
- **Parameters**: `nID` - Bin ID
- **Return**: Bin combination name
- **Remarks**: Get bin combination name by ID.
- **Example**:
```cpp
const char* pcData = STSGetBinName(nID);
```

### 1.16.16 STSGetUseBinID()
- **Signature**: `unsigned int STSGetUseBinID();`
- **Return**: Currently active bin combination ID
- **Remarks**: Get the ID of the bin combination currently in use.

### 1.16.17 STSGetUseBinName()
- **Signature**: `const char* STSGetUseBinName();`
- **Return**: Currently active bin combination name
- **Remarks**: Get the name of the bin combination currently in use.

### 1.16.18 STSSetHardwareCheck()
- **Signature**: `int STSSetHardwareCheck(BOOL bEnable);`
- **Parameters**: `bEnable` - TRUE = enable, FALSE = disable
- **Return**: 0
- **Remarks**: Enable/disable hardware check. Priority higher than UI setting. **Must be called in UserLoad** (otherwise UI may not sync). If PGS version >= 1004, hardware check is forced ON by default; only this API can disable it (UI setting is disabled).

### 1.16.19 STSSetEnableLog()
- **Signature**: `int STSSetEnableLog(BOOL bEnable);`
- **Parameters**: `bEnable` - TRUE = enable, FALSE = disable
- **Return**: 0
- **Remarks**: Enable/disable log. Priority higher than UI setting. **Must be called in UserLoad** (otherwise UI may not sync). If PGS version >= 1004, log is forced ON by default; only this API can disable it (UI setting is disabled).

### 1.16.20 CFunctionTest Class Methods

Methods accessible via `STSGetFunction(nID)->...`:

#### 1.16.20.1 STSGetParamCount() [CFunctionTest]
- **Signature**: `unsigned int STSGetParamCount();`
- **Return**: Number of parameters in the function
- **Example**:
```cpp
CFunctionTest* pFun = STSGetFunction(0);
if (pFun != NULL) {
    unsigned int nCount = pFun->STSGetParamCount();
}
```

#### 1.16.20.2 STSGetParam() [CFunctionTest]
- **Signature**: `CParam* STSGetParam(unsigned int nID);`
- **Parameters**: `nID` - Parameter number within the function
- **Return**: Parameter pointer
- **Remarks**: Get parameter pointer by ID within the function.

#### 1.16.20.3 STSGetParamByName() [CFunctionTest]
- **Signature**: `CParam* STSGetParamByName(const char* pcName);`
- **Parameters**: `pcName` - Parameter name
- **Return**: Parameter pointer
- **Remarks**: Get parameter pointer by name.

#### 1.16.20.4 STSGetParambySymbol() [CFunctionTest]
- **Signature**: `CParam* STSGetParambySymbol(const char* pcSymbol);`
- **Parameters**: `pcSymbol` - Parameter Symbol
- **Return**: Parameter pointer
- **Remarks**: Get parameter pointer by Symbol identifier.
- **Example**:
```cpp
CParam* pParam = pFun->STSGetParambySymbol("ICC");
```

#### 1.16.20.5 STSISQAFunction() [CFunctionTest]
- **Signature**: `BOOL STSISQAFunction();`
- **Return**: TRUE = InLine QA function, FALSE = not InLine QA function
- **Remarks**: Check if function is an InLine QA function.

#### 1.16.20.6 STSISDPATFunction() [CFunctionTest]
- **Signature**: `BOOL STSISDPATFunction();`
- **Return**: TRUE = DPAT test function, FALSE = other
- **Remarks**: Check if function is a DPAT test function.

#### 1.16.20.7 STSSetTest() [CFunctionTest]
- **Signature**: `void STSSetTest(BOOL bData);`
- **Parameters**: `bData` - Whether to test
- **Remarks**: Set whether function executes test. **Only effective in UserLoad.**

#### 1.16.20.8 STSGetTest() [CFunctionTest]
- **Signature**: `BOOL STSGetTest();`
- **Return**: TRUE = function executes test, FALSE = does not
- **Remarks**: Get whether function tests.

#### 1.16.20.9 STSGetStation() [CFunctionTest]
- **Signature**: `int STSGetStation();`
- **Return**: Station number in multi-station test
- **Remarks**: Get the station number where the function resides.

#### 1.16.20.10 STSIsAlwaysRun() [CFunctionTest]
- **Signature**: `BOOL STSIsAlwaysRun();`
- **Return**: TRUE = must execute if selected, FALSE = will not execute after FailStop triggers
- **Remarks**: Check if function is always-run.

#### 1.16.20.11 STSSetAlwaysRun() [CFunctionTest]
- **Signature**: `int STSSetAlwaysRun(BOOL bData);`
- **Parameters**: `bData` - Whether must execute
- **Remarks**: Set function as must-execute.
- **Example**:
```cpp
CFunctionTest* pFun = STSGetFunction(0);
if (pFun != NULL) {
    pFun->STSSetAlwaysRun(TRUE);
}
```

### 1.16.21 CSTSMustResult Class Methods

Methods accessible via `STSGetMustResult()->...`:

#### 1.16.21.1 GetEnable() [CSTSMustResult]
- **Signature**: `BOOL GetEnable();`
- **Return**: TRUE = MustResult feature enabled, FALSE = disabled
- **Remarks**: Check if MustResult (required assignment) is enabled.

#### 1.16.21.2 SetEnable() [CSTSMustResult]
- **Signature**: `void SetEnable(BOOL bData);`
- **Parameters**: `bData` - Enable/disable MustResult
- **Remarks**: Set MustResult feature on/off.
- **Example**:
```cpp
CSTSMustResult* pMustResult = STSGetMustResult();
if (pMustResult != NULL) {
    pMustResult->SetEnable(TRUE);
}
```

#### 1.16.21.3 GetMustResult() [CSTSMustResult]
- **Signature (overload 1)**: `BOOL GetMustResult(const char* pcSymbol);`
- **Signature (overload 2)**: `BOOL GetMustResult(int nFun, int nParam);`
- **Parameters**:
  - Overload 1: `pcSymbol` - Parameter Symbol
  - Overload 2: `nFun` - Function number, `nParam` - Parameter number within function
- **Return**: TRUE = parameter must be assigned, FALSE = optional
- **Remarks**: Check if parameter requires mandatory assignment.

#### 1.16.21.4 SetMustResult() [CSTSMustResult]
- **Signature (overload 1)**: `void SetMustResult(const char* pcSymbol, BOOL bData);`
- **Signature (overload 2)**: `void SetMustResult(int nFun, int nParam, BOOL bData);`
- **Parameters**: `pcSymbol` or `nFun/nParam`, `bData` - Whether must assign
- **Remarks**: Set parameter as must-assign or optional.
- **Example**:
```cpp
pMustResult->SetMustResult("ICC", TRUE);
pMustResult->SetMustResult(0, 0, TRUE);
```

#### 1.16.21.5 GetMustResultParamCount() [CSTSMustResult]
- **Signature**: `int GetMustResultParamCount();`
- **Return**: Number of must-assign parameters
- **Remarks**: Get count of parameters requiring mandatory assignment.

#### 1.16.21.6 GetMustResulteParam() [CSTSMustResult]
- **Signature**: `CParam* GetMustResulteParam(unsigned int nItem);`
- **Parameters**: `nItem` - Parameter index (0-based)
- **Return**: Parameter pointer
- **Remarks**: Get the n-th must-assign parameter.

#### 1.16.21.7 SetAllParamMustValue() [CSTSMustResult]
- **Signature**: `void SetAllParamMustValue(BOOL bData);`
- **Parameters**: `bData` - Whether all parameters must be assigned
- **Remarks**: Set ALL parameters as must-assign or optional.
- **Example**:
```cpp
pMustResult->SetAllParamMustValue(TRUE);
```

---

## Summary: Key Patterns and Rules

### Framework Execution Order
```
UserLoad -> UserInit -> [OnNewLot] -> [For each test run:]
  OnSot -> InitBeforeTestFlow -> [Test Functions] -> BinOutDut -> InitAfterTestFlow
  -> [OnWaferEnd]
UserExit
```

### Critical Rules
1. **BEGIN_SINGLE_SITE/END_SINGLE_SITE MUST be paired** - unpredictable errors otherwise
2. **STSSetMultiSiteBind for non-CBITe modules** vs **STSCBITeMultiSiteBind for CBITe** - do not mix
3. **UserLoad-only functions**: STSUpdateFunTest, STSShowLimitDlg, STSSetUseLimitbyID/Name, STSShowBinDlg, STSSetUseBinbyID/Name, STSSetHardwareCheck, STSSetEnableLog, STSSetEnableCalCheck, STSSetRelayActTimes, STSSetTest (CFunctionTest), SetTestNum, SetAllTestNum, SetEnable (TestNum)
4. **NO_SITE channels**: Not restricted by site mask; any valid site can control them
5. **STSSetSiteStatus**: Always restore original status after use (pair with STSGetSiteStatus)
6. **PGS version >= 1004**: HardwareCheck and EnableLog forced ON; only program API can disable
7. **Site binding rules for CBITe SetOn**: Active site + NO_SITE channels close; inactive site channels open; unbound channels keep state; unspecified channels open
