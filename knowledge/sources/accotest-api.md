# AccoTEST 自动化接口 — STS8300 外部控制 API

## 概述

`Sts8200Interface.dll` 提供标准接口函数，供自动化控制程序调用，实现：
- 启动/关闭 Control 和 TestUI
- 载入测试程序 (.pgs)
- 执行测试 (批量 / 单次)
- 获取测试结果

**调用约定:** `stdcall`（所有函数）

---

## 生命周期流程

```
RunControlNoReg(user, pass)         ← 1. 启动 Control
    ↓
RunTestuiWithStationid(station)     ← 2. 启动 TestUI
    ↓
CreateNewLotFile_Acco()             ← 3. 创建 LOT
AppendStdfLotMsg3(...)              ← 4. 设置 LOT 信息
    ↓
SetPgsFileName(path)                ← 5. 指定 .pgs 文件
LoadFile(timeout)                   ← 6. 载入测试程序
    ↓
StartTest()   或  SingleTest()      ← 7. 执行测试
    ↓
StopTest()                          ← 8. 停止
ForceCloseTestui()                  ← 9. 关闭 TestUI
```

---

## 核心 API 函数

### CONTROL 启动

```cpp
// 启动 Control 并登录
int RunControlNoReg(char* username, char* password);
// 返回: 0=成功, 1=已启动, -1=句柄为0, -9=登录失败

// 切换用户
int SwitchUser(char* username, char* password);
// 返回: 0=成功, -1=未启动, -9=密码错误

// 关闭 Control
int CloseControl();
// 返回: 0=完全关闭, >0=硬件运行中

// 设置远程模式 (禁止界面操作)
int SetControlRemoteMode();
// 返回: 0=成功, -1=未启动

// 获取硬件状态
int GetHardwareStatus();
// 返回: 0=空闲, 1=TestUI使用中, 255=未启动, -9=断电
```

### TestUI 启动

```cpp
// 启动 TestUI (指定 Station)
int RunTestuiWithStationid(int stationid);
// stationid: 0=A, 1=B
// 返回: -1=未启动, -2=已启动, >0=成功(testui句柄)

// 直接启动 TestUI 并载入程序 (三合一)
int RunTestuiWithFilename(char* pgsfilename, int delaytime);
// = RunTestui() + SetPgsFileName() + LoadFile()
// delaytime: 超时 ms (如 10000)

// 判断 TestUI 是否启动
int CurTestUIExist();
// 返回: 0=已启动, 1=已启动且载入程序, 其余=未启动
```

### 测试程序管理

```cpp
// 设置 .pgs 文件路径
int SetPgsFileName(char* pgsfilename);
// 必须在 LoadFile() 前调用

// 载入测试程序
int LoadFile(int timeout_ms);
// timeout_ms: 超时 (如 10000 = 10s)
// 返回: 0=成功

// 创建新的 LOT 信息文件
int CreateNewLotFile_Acco();

// 添加 LOT 信息项
int AppendStdfLotMsg3(char* LotTitle, int stdfId, char* LotValue,
                      unsigned short curView, unsigned short curUpdate);
// stdfId 常用值:
//   0=LotId, 1=Parttype, 4=Jobname(DeviceID), 7=OperatorID,
//   10=TestCode(FT/CP), 17=TestfacilityID, 23=TestflowID
// curView: 1=显示, 0=不显示
// curUpdate: 1=可更新, 0=不可更新

// 判断测试程序是否已载入
int IsTestFileLoad();

// 获取当前 .pgs 名称
int GetCurPgsName(char* name, int strsize);

// 获取测试 site 数量
int GetTestSiteCount();
```

### 测试控制

```cpp
// 批量测试 (跑全部 test items)
int StartTest();
// 返回: 0=成功启动

// 批量测试 (指定 Station)
int StartTestWithStationid(int stationid);

// 单次测试 (跑一个 test item)
int SingleTest();
// 返回: 0=开始执行, 1=执行完毕

// 停止测试
int StopTest();
// 返回: 0=成功

// 新建 LOT
int NewLot();

// 结束当前 LOT datalog
int EndCurrentLog();
```

### TestUI 关闭

```cpp
// 关闭 TestUI (正常)
int CloseTestui();
// 返回: 0=成功

// 强制关闭 TestUI
int ForceCloseTestui();

// 禁止 Shell 关闭 TestUI
int EnableShellClose(int enable);
```

### 测试状态与结果

```cpp
// 获取测试状态
int GetTestuiTestingStatus();
// 返回: 0=空闲, 1=运行中

// 获取测试过的结果数
int GetTestedResult();

// 获取参数总数
int GetParamCount();

// 获取指定参数的 SubUnit 数
int GetSubUnitCountWithParamIndex(int paramIndex);

// 获取测试值
double GetTestValue(int paramIndex, int site, int subunit);
// paramIndex: 参数序号
// site: 0=Site1, 1=Site2 ...
// subunit: SubUnit 序号

// 获取 Site 测试结果
int GetSiteTestResult(int site);
// 返回: 0=Pass, 1=Fail, -1=未测试

// 获取参数测试结果
int GetParamTestResult(int paramIndex, int site, int subunit);

// 获取 Bin 信息
int GetBinCount();
int GetBinInfo(int binIndex, char* binName, int strsize, int* binType, int* siteResult);
```

### 测试模式设置

```cpp
// 自动载入模式: 1=OP权限下载入按钮无效
int SetAutoLoadMode(int mode);

// 界面模式: 1=自动化模式 (不等待用户操作)
int SetInterFaceMode(int mode);

// 禁止 LOT 信息框弹出
int DisAutoShowLotInfo();

// 启用 QA 测试模式
int EnableQATest(int enable);

// 设置最大自动运行次数
int SetMaxAutoRunCount(int count);
```

### 导出设置

```cpp
// 自动导出: 0=无, 1=Excel, 2=CSV, 4=STDF
int AutoExportSet(int exportMode);  // 可组合: 7=全导出

// 设置 DataLog 文件名规则
int SetDatalogFileName(char* filename);

// 设置保存文件路径
int SetSaveFileName(char* path);

// Summary 输出选项: CSV(1/0), TXT(1/0), SUM(1/0)
int SetSummaryLogSaveOption(int csv, int txt, int sum);

// 设置 DataLog 路径
int SetDatalogPath(char* path);

// 设置 Summary 路径
int SetSumPath(char* path);
```

---

## 推荐启动脚本流程

```python
# 1. 启动 Control
RunControlNoReg("oper", "oper")
sleep(2)

# 2. 启动 TestUI (Station A)
RunTestuiWithStationid(0)
sleep(1)

# 3. 创建 LOT + 设置信息
CreateNewLotFile_Acco()
AppendStdfLotMsg3("LotID", 0, "TEST_LOT", 1, 0)
AppendStdfLotMsg3("DeviceID", 4, "NU6801", 1, 0)
AppendStdfLotMsg3("TestCode", 10, "FT", 1, 0)

# 4. 自动化模式设置
SetAutoLoadMode(1)
SetInterFaceMode(1)
DisAutoShowLotInfo()

# 5. 载入测试程序
SetPgsFileName("<PGS_PATH>")
LoadFile(10000)

# 6. 设置导出
AutoExportSet(7)
SetSummaryLogSaveOption(1, 1, 1)

# 7. 执行单次测试
SingleTest()

# 8. 获取结果
n = GetParamCount()
for i in range(n):
    val = GetTestValue(i, 0, 0)
    print(f"Param[{i}] = {val}")

# 9. 清理
StopTest()
ForceCloseTestui()
```

---

## 配置

| 项 | 值 | 说明 |
|------|------|------|
| PROJECT_PATH | `D:\PROJECT5-BOSTON\P68101\F68101-V0P2` | test.cpp/sub.cpp 所在目录 |
| PGS_PATH | `D:\PROJECT5-BOSTON\P68101\F68101-V0P2\F68101-FT.pgs` | .pgs 文件完整路径 |
| USERNAME | `admin` | Control 登录用户名 |
| PASSWORD | `admin` | Control 登录密码 |
| STATION | `0` | 0=StationA |
