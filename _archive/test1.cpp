/**************************************************************************************************************************************
*   Source title:		test.CPP                                            *
*   Written by:			Shuai Zhang                                             *
*   Last Modified by:	Shuai Zhang                                            *
*   Current Rev:		V05    *
*   Description:		Davis                                               *
*   Revision History:                                                         *
*                                                                             *
*   12/22/2024  00  - Original coding.                                        *
*                                                                             *                                                                           *
**************************************************************************************************************************************/
/********************************************************************************************************************************************
------------------------------------------------------------- NU6601 TEST PROGRAM-------------------------------------------------------

NU6801 PMIC Device:

Device Name.......................................NU6801QFCN-QFNB
Program Number....................................F68011
Tester............................................STS8300 Standard
P68011  HIB Number................................DN1000007, Revision 1.0
Test Temperature..................................Final Test @ 25C
Test Flow.........................................FT,  offline QA 480ea per Lot
Test Engineer.....................................szhang@nuvoltatech.com
Other information:
............................23 Pins, Flip Chip QFN package, size 3.18*2.85*0.65mm
............................Test hardware 4set of socket, 4 set of Handler Interface Board
............................Production Site is  NINGBO ForeHope
............................Test condition: VBAT=4.2V, VBUS=VAC=9V, typical power supply, room temp for chip probe test
............................OTP Device, able to retest while cannot support re-burn for burned device

Best practice:
...........................Check program stability better use fresh sample or parts are sensitive with ball contact


*************************************************************************************************
*************************************************************************************************
Program Revision History:
==============================================================================================
Rev Level   	     Originator	              Date		                                     Auditor                             Date		                Testtime/insertion
---------------------------------------------------------------------------------------------------------------------------------------------
00  Initial	      Zhangshuai 	       2025/05/15	                             Dennis/Jensen	          2025/05/15                  8.2S  /8 site
01   Minor       Zhangshuai 	       2025/05/20	                             Dennis		                      2025/05/20                  9.4S  /15 site
02   Major        Zhangshuai 	       2025/06/30	                             Dennis		                      2025/06/30                  8S  /16 site
03   Minor        Zhangshuai 	       2025/07/16	                             Dennis		                      2025/07/17                  8S  /16 site
04   Minor        Zhangshuai 	       2025/07/31	                             Dennis		                      2025/07/31                  8S  /16 site
05   Minor        Zhangshuai 	       2025/08/21	                             Dennis		                      2025/08/21                  8S  /16 site 
06   Minor        Zhangshuai 	       2026/02/02	                             Dennis		                      2026/02/02                  8S  /16 site
*************************************************************************************************************
*************************************************************************************************************************************************************
********************************************************************PROGRAM REVISION LOG*****************************************************************
Device paranamemental Settings required from SE:
1.NU6801QDNB-AAA1/NU6802QDNB-AAA1/NU6803QDNB-AAA1 Share same program, Device Setting check NU6801.spec file


Program version History
Version-00:
1. Release date: 2025-05-13

Version-01:
1. Add VBG Trim Post measurement
2. Modify Spike in INT, VAC1/2/3
3. minimize IBAT_CC_LP_ACCUR spec after discussed with SE
4. Update V1p2_trim_post test limit, make it smaller.
5. Add Vclamp leakage screen test: measure current to screen,  HTOL have hard fail, DE find root cause is process issue cause vclamp leakage, use leakage to screen weak samples

Version-02:
1. Spec update for below item to fix low CPK issue, Test limit update based on CTR actions:
AMUX_VBUS_9V_Accur/AMUX_VBUS_5V_Accur/VBUS_ASHUT_VTH1_Fall/VRE_CHG_VTH1_Fall_DSA
AMUX_VAC1_Accur / AMUX_VAC2_Accur / AMUX_VAC3_Accur
VRE_CHG_VTH2_Fall_DSA / VBUS_OVP_VTH1_Hys /VRE_CHG_VTH1_Fall_MI
NTC_HOT_BO_T1_Fall / VBUS_REVI_VTH_Fall / VBUS_HT_VBAT_3V_Hys
OS and Leakage
2. TTR for All Test Functions
3. Modified Retest solution for IQ_Standby,OVST,and other voltage and current items.


Version-03 

1.Modify fail wait time  on VBAT/VBUS_BU/VBUS_BO_Serve Loop
2. Add 8ms for IQ_AMUX Test
3. Update NTC3_AMUX middle parameter test limit to improve yield loss
4. Update VS_PRE_MAX UVLO, rising threshold initial start value from 4.4 to 4V.
5. Add Relay off status check function to make sure relay will not burn out.


Version -04
1. BoardCheck update limit and add check point of Relay K61,K67 status
2. VBUS_BO_LOOP_ACCUR power off relay update to same as trim.
3. When relay cannot off, add delay time when CBIT Module off
4. VBG not filter best code between 0-9 for NU6801 and NU6802

Version-05
1. EQC find BOOST_ZCD on site all test values is 1mA, while limit -180~600mA, so cannot screen out if test item failed,  root cause is mosfet not open,  and add check point on this point
2. IBUS_SNS_Gain trim step15 test limit 100-300, trim target is 198mohm, need update 300mohm upper limit to fixed yield loss issue
3. Operation leakage add stable check

Version-06
1. Modify R_SDA/OTP read/HSFET_RDSON wait time to avoid cannot enter TM issue
2. Modify VBUS_EA_LOOP_BOOST unstable issue in Special HIB by reset VCC.
---------------------------------------(SHANGHAI) NUVOLTA SEMICONDUCTOR Co.Ltd , All Right Reserved-----------------------------------------
*******************************************************************************************************************************************/

#include "stdafx.h"
#include <iostream>
#include <stdlib.h>
#include <ctime>
#include <conio.h>
#include <valarray>
#include "sub.h"
#include "Test_Method.h"
#include "FMEA.h"
#include "Coutlier.h"
#include "spec.h"
#include "tempchar.h"
//#include"Shmoo.h"
#include <windows.h>
#include "UserType.h"
#include <sstream>
#include <iomanip>
#include <thread>
#include <cctype> // 包含 isdigit 所需的头文件
/*The following code was created for STS PinPlanner,don't modify*/ 
#include "Pin_Channel_define.h"
/*The following code was created for STS PinPlanner,don't modify*/ 
/****STS_PINPLANNER_CODE_BEGIN****/
#define STS_SITE_NUM 16
/****PIN GROUP DEFINITION****/
FOVIe VBUS_FOVI(_PIN_CHANNEL_DEFINE_VBUS_FOVI_, "VBUS_FOVI");
FOVIe AMUX_FOVI(_PIN_CHANNEL_DEFINE_AMUX_FOVI_, "AMUX_FOVI");
FOVIe PMID_FOVI(_PIN_CHANNEL_DEFINE_PMID_FOVI_, "PMID_FOVI");
FOVIe NTC_FOVI(_PIN_CHANNEL_DEFINE_NTC_FOVI_, "NTC_FOVI");
ACM200 KLV12_ACM(_PIN_CHANNEL_DEFINE_KLV12_ACM_, "KLV12_ACM");
ACM200 ACDRV123_ACM(_PIN_CHANNEL_DEFINE_ACDRV123_ACM_, "ACDRV123_ACM");
ACM200 SW_ACM(_PIN_CHANNEL_DEFINE_SW_ACM_, "SW_ACM");
ACM200 VCC_ACM(_PIN_CHANNEL_DEFINE_VCC_ACM_, "VCC_ACM");
ACM200 VDRV_AMP_ACM(_PIN_CHANNEL_DEFINE_VDRV_AMP_ACM_, "VDRV_AMP_ACM");
ACM200 VBAT_ACM(_PIN_CHANNEL_DEFINE_VBAT_ACM_, "VBAT_ACM");
ACM200 VAC123_ACM(_PIN_CHANNEL_DEFINE_VAC123_ACM_, "VAC123_ACM");
ACM200 PGND_ACM(_PIN_CHANNEL_DEFINE_PGND_ACM_, "PGND_ACM");
ACM200 BTST_ACM(_PIN_CHANNEL_DEFINE_BTST_ACM_, "BTST_ACM");
ACM200 VBATD_ACM(_PIN_CHANNEL_DEFINE_VBATD_ACM_, "VBATD_ACM");
ACM200 SCL_ACM(_PIN_CHANNEL_DEFINE_SCL_ACM_, "SCL_ACM");
ACM200 SDA_INT_ACM(_PIN_CHANNEL_DEFINE_SDA_INT_ACM_, "SDA_INT_ACM");
FPVIe FPVI(_PIN_CHANNEL_DEFINE_FPVI_, "FPVI");
QVMe QVM_S1_S2(_PIN_CHANNEL_DEFINE_QVM_S1_S2_, "QVM_S1_S2");
QVMe QVM_S3_S4(_PIN_CHANNEL_DEFINE_QVM_S3_S4_, "QVM_S3_S4");
QVMe QVM_S5_S6(_PIN_CHANNEL_DEFINE_QVM_S5_S6_, "QVM_S5_S6");
QVMe QVM_S7_S8(_PIN_CHANNEL_DEFINE_QVM_S7_S8_, "QVM_S7_S8");
QVMe QVM_S9_S10(_PIN_CHANNEL_DEFINE_QVM_S9_S10_, "QVM_S9_S10");
QVMe QVM_S11_S12(_PIN_CHANNEL_DEFINE_QVM_S11_S12_, "QVM_S11_S12");
QVMe QVM_S13_S14(_PIN_CHANNEL_DEFINE_QVM_S13_S14_, "QVM_S13_S14");
QVMe QVM_S15_S16(_PIN_CHANNEL_DEFINE_QVM_S15_S16_, "QVM_S15_S16");
QTMUe QTMU_S1_S2(_PIN_CHANNEL_DEFINE_QTMU_S1_S2_, "QTMU_S1_S2");
QTMUe QTMU_S3_S4(_PIN_CHANNEL_DEFINE_QTMU_S3_S4_, "QTMU_S3_S4");
QTMUe QTMU_S5_S6(_PIN_CHANNEL_DEFINE_QTMU_S5_S6_, "QTMU_S5_S6");
QTMUe QTMU_S7_S8(_PIN_CHANNEL_DEFINE_QTMU_S7_S8_, "QTMU_S7_S8");
QTMUe QTMU_S9_S10(_PIN_CHANNEL_DEFINE_QTMU_S9_S10_, "QTMU_S9_S10");
QTMUe QTMU_S11_S12(_PIN_CHANNEL_DEFINE_QTMU_S11_S12_, "QTMU_S11_S12");
QTMUe QTMU_S13_S14(_PIN_CHANNEL_DEFINE_QTMU_S13_S14_, "QTMU_S13_S14");
QTMUe QTMU_S15_S16(_PIN_CHANNEL_DEFINE_QTMU_S15_S16_, "QTMU_S15_S16");
ACM200 ACM_GRP(_GROUP_CHANNEL_DEFINE_ACM_GRP_,"ACM_GRP");
ACM200 ACM_GRP2(_GROUP_CHANNEL_DEFINE_ACM_GRP2_,"ACM_GRP2");
ACM200 ACM_GRP3(_GROUP_CHANNEL_DEFINE_ACM_GRP3_,"ACM_GRP3");
FOVIe ATEST_GRP(_GROUP_CHANNEL_DEFINE_ATEST_GRP_,"ATEST_GRP");
FOVIe FOVI_GRP(_GROUP_CHANNEL_DEFINE_FOVI_GRP_,"FOVI_GRP");
QTMUe QTMU_GP(_GROUP_CHANNEL_DEFINE_QTMU_GP_,"QTMU_GP");
QVMe QVM_GP(_GROUP_CHANNEL_DEFINE_QVM_GP_,"QVM_GP");
/****multisite settings should be included here****/
DUT_API void HardWareCfg()
{
	STSSetMultiSiteBindEx(MD_FOVIe,0,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE1_);
	STSSetMultiSiteBindEx(MD_FOVIe,1,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE2_);
	STSSetMultiSiteBindEx(MD_FOVIe,2,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE3_);
	STSSetMultiSiteBindEx(MD_FOVIe,3,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE4_);
	STSSetMultiSiteBindEx(MD_FOVIe,4,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE5_);
	STSSetMultiSiteBindEx(MD_FOVIe,5,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE6_);
	STSSetMultiSiteBindEx(MD_FOVIe,6,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE7_);
	STSSetMultiSiteBindEx(MD_FOVIe,7,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE8_);
	STSSetMultiSiteBindEx(MD_FOVIe,8,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE9_);
	STSSetMultiSiteBindEx(MD_FOVIe,9,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE10_);
	STSSetMultiSiteBindEx(MD_FOVIe,10,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE11_);
	STSSetMultiSiteBindEx(MD_FOVIe,11,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE12_);
	STSSetMultiSiteBindEx(MD_FOVIe,12,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE13_);
	STSSetMultiSiteBindEx(MD_FOVIe,13,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE14_);
	STSSetMultiSiteBindEx(MD_FOVIe,14,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE15_);
	STSSetMultiSiteBindEx(MD_FOVIe,15,_PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE16_);
	STSSetMultiSiteBindEx(MD_QVMe,NO_SITE,_PIN_SITE_BIND_DEFINE_MD_QVME_NOSITE);
	STSSetMultiSiteBindEx(MD_FPVIe,0,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE1_);
	STSSetMultiSiteBindEx(MD_FPVIe,1,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE2_);
	STSSetMultiSiteBindEx(MD_FPVIe,2,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE3_);
	STSSetMultiSiteBindEx(MD_FPVIe,3,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE4_);
	STSSetMultiSiteBindEx(MD_FPVIe,4,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE5_);
	STSSetMultiSiteBindEx(MD_FPVIe,5,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE6_);
	STSSetMultiSiteBindEx(MD_FPVIe,6,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE7_);
	STSSetMultiSiteBindEx(MD_FPVIe,7,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE8_);
	STSSetMultiSiteBindEx(MD_FPVIe,8,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE9_);
	STSSetMultiSiteBindEx(MD_FPVIe,9,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE10_);
	STSSetMultiSiteBindEx(MD_FPVIe,10,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE11_);
	STSSetMultiSiteBindEx(MD_FPVIe,11,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE12_);
	STSSetMultiSiteBindEx(MD_FPVIe,12,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE13_);
	STSSetMultiSiteBindEx(MD_FPVIe,13,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE14_);
	STSSetMultiSiteBindEx(MD_FPVIe,14,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE15_);
	STSSetMultiSiteBindEx(MD_FPVIe,15,_PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE16_);
	STSSetMultiSiteBindEx(MD_QTMUe,NO_SITE,_PIN_SITE_BIND_DEFINE_MD_QTMUE_NOSITE);
	STSSetMultiSiteBindEx(MD_ACM200,0,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE1_);
	STSSetMultiSiteBindEx(MD_ACM200,1,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE2_);
	STSSetMultiSiteBindEx(MD_ACM200,2,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE3_);
	STSSetMultiSiteBindEx(MD_ACM200,3,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE4_);
	STSSetMultiSiteBindEx(MD_ACM200,4,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE5_);
	STSSetMultiSiteBindEx(MD_ACM200,5,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE6_);
	STSSetMultiSiteBindEx(MD_ACM200,6,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE7_);
	STSSetMultiSiteBindEx(MD_ACM200,7,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE8_);
	STSSetMultiSiteBindEx(MD_ACM200,8,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE9_);
	STSSetMultiSiteBindEx(MD_ACM200,9,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE10_);
	STSSetMultiSiteBindEx(MD_ACM200,10,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE11_);
	STSSetMultiSiteBindEx(MD_ACM200,11,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE12_);
	STSSetMultiSiteBindEx(MD_ACM200,12,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE13_);
	STSSetMultiSiteBindEx(MD_ACM200,13,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE14_);
	STSSetMultiSiteBindEx(MD_ACM200,14,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE15_);
	STSSetMultiSiteBindEx(MD_ACM200,15,_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE16_);
}
/****STS_PINPLANNER_CODE_END****/
extern string int2str(DWORD n);


//*****************************************************************************//
DCM dcm;//cannot delete
CBITe cbite;//cannot delete
TREG trim_reg;//cannot delete
SPEC spec;//cannot delete
Test_Method test_method;//cannot delete
Coutlier sos;//cannot delete
//SHMOO shmoo;
int TEST_FLOW ;//cannot delete
int USER_MODE;//cannot delete
int BURN_FLAG[SITE_NUM] = { 0 };//cannot delete
int GRP_CNT = 0;// cannot delete
int SiteSelected[SITE_NUM] = { 0 };//  cannot delete
int HIB =0;
string DEVICE_SEL;
int Part_Num = 0;
bool Scan_pat_load_succeess = false;
int LOOP_COUNT = 0;
bool Relay_Off_Check = true;
/************************************************************************/
/*    Temperature Characterization Loop Set Up                                                                */
/************************************************************************/
double V_PS1_TYP, V_PS2_TYP, V_PS3_TYP;//cannot delete
int char_flag = 0;
double Temperature1 = 25;//cannot delete
Thermal_stream TS;//cannot delete
//************************************************************************//

extern "C" int GetPgsFullPath(LPTSTR pgsPath, int chNum);
string pgs_path;
bool DO_TRIM = true;
bool QC = false;

int globalsite;
BYTE sitesta[SITE_NUM];

//board check coding
bool DO_BoardCheck = true;//true;
extern BOOL run_diags();     // global funtion for HW checker
bool DO_CHAR = true;
//FMEA
bool DO_FMEA = false;
eFMEA efmea;
//SOS
int SOS_MODE = PRODUCTION;




void SetConsoleFontSize(int fontSize) {
	HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
	CONSOLE_FONT_INFOEX cfi;
	cfi.cbSize = sizeof(cfi);
	cfi.nFont = 0;
	cfi.dwFontSize.X = 0;  // 宽度设置为0，由系统决定
	cfi.dwFontSize.Y = fontSize;  // 设置高度
	cfi.FontFamily = FF_DONTCARE;
	cfi.FontWeight = FW_NORMAL;
	wcscpy(cfi.FaceName, L"Consolas");  // 可以选择其他字体

	SetCurrentConsoleFontEx(hOut, FALSE, &cfi);
}



void DCM_Channel_Connect()
{
	dcm.Connect("SCL");
	dcm.Connect("SDA");
	dcm.Connect("NTC");
	dcm.Connect("INT");

}
void DCM_Channel_Disconnect()
{
	dcm.Disconnect("SCL");
	dcm.Disconnect("SDA");
	dcm.Disconnect("NTC");
	dcm.Disconnect("INT");
}

// 设置文本颜色
void SetColor(int color) {
	SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), color);
}

// 重置文本颜色为默认值
void ResetColor() {
	SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), 7); // 7 是默认的白色文本
}

int extractIntFromString(const std::string& str) {
	std::string numStr;

	// 遍历字符串中的每个字符
	for (char ch : str) {
		// 如果字符是数字，则添加到numStr中
		if (std::isdigit(static_cast<unsigned char>(ch))) {
			numStr += ch;
		}
	}

	// 如果找到了数字部分，则将其转换为整数并返回
	if (!numStr.empty()) {
		return std::stoi(numStr);
	}
	else {
		// 如果没有找到数字部分，则返回0或抛出一个异常，根据你的需求来处理
		return 0; // 或者 throw std::runtime_error("No digits found in the string");
	}
}

void PowerSupplySelection()
{
	int volt_cnt = spec("PS1_CHAR").count();
	double Volval;
	string name_start;
	string name_stop;
	string power_name;
	for (int i = 0; i < volt_cnt; i++)
	{
		if (i == volt_cnt - 1)
		{
			Volval = spec("PS1_CHAR")[i];
			name_stop = convertToString(Volval, 1) + "V";
			power_name = power_name + name_stop;
		}
		else
		{
			Volval = spec("PS1_CHAR")[i];
			name_start = convertToString(Volval, 1) + "V,";
			power_name = power_name + name_start;
		}
	}

	size_t length = power_name.size();
	char selectVol[256] = { "" };
	std::strncpy(selectVol, power_name.c_str(), length + 1);

	char selectVoltage[256] = "";

	for (int i = 0; i < 256; i++)
	{
		selectVoltage[i] = selectVol[i];
	}
	int  cal_Voltage = STSSetInitSelectDialog("Voltage Select", volt_cnt, 0, selectVoltage);
	delay_ms(1);
	spec.set_sel_vin_index(cal_Voltage);
}

void HotKeyThread() {
	MSG msg;


	// 注册热键 Ctrl+L
	if (!RegisterHotKey(NULL, 1, MOD_CONTROL, 0x4C)) { // 0x4C 是 'L' 的虚拟键码
		std::cerr << "Failed to register hot key" << std::endl;
		return;
	}
	// 注册热键 Ctrl+K
	if (!RegisterHotKey(NULL, 2, MOD_CONTROL, 0x4B)) { // 0x4B 是 'K' 的虚拟键码
		std::cerr << "Failed to register hot key" << std::endl;
		return;
	}
	// 注册热键 Ctrl+I
	if (!RegisterHotKey(NULL, 3, MOD_CONTROL, 0x49)) { // 0x49 是 'I' 的虚拟键码
		std::cerr << "Failed to register hot key" << std::endl;
		return;
	}
	// 注册热键 Ctrl+M
	if (!RegisterHotKey(NULL, 4, MOD_CONTROL, 0x4D)) { // 0x4C 是 'M' 的虚拟键码
		std::cerr << "Failed to register hot key" << std::endl;
		return;

	}
	// 在这个线程中检查消息
	while (true) {
		if (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) 
		{
			if (msg.message == WM_HOTKEY) 
			{
				std::cout << "Hot key triggered!" << std::endl;
				// 执行相应的操作
				if (msg.wParam == 1)//----------------执行注册的第一个热键L
				{
					TS.instruction();
					TS.tssot(1);
				}
				if (msg.wParam == 2)//----------------执行注册的第2个热键K
				{
					PowerSupplySelection();
					delay_ms(1);
				}
				if (msg.wParam == 3)//----------------执行注册的第3个热键I
				{
					run_diags();
					//fclose(stdout);
					//FreeConsole();
				}
				if (msg.wParam == 4)//----------------执行注册的第4个热键M: Matrix
				{
					PowerSupplySelection();
					delay_ms(1);
				}
			}
			// 处理其他消息...
		}
		// 减少CPU使用率
		Sleep(10);
	}

	// 注销热键（?实际上这个代码可能永远不会执行，?因为线程是无限循环的）?
	 //UnregisterHotKey(NULL, 1);
}

void  TESTER_SETUP_FUNCTION()
{
	//USER_MODE = STSGetUserPriority();//   获取tester的模式是，Operator 还是别的模式
		int total_device_count = 0;
		total_device_count = spec.devicecount();
		delay_ms(1);
		std::vector<std::string> device_list(total_device_count, "DEVICE_SUMMARY");
		for (auto& str : device_list)
		{
			str = spec.getNextDevice()->devicename();
		}
		size_t totalLength = 0;
		for (const std::string& str : device_list) {
			totalLength += str.length();
			if (&str != &device_list.back()) {
				totalLength += 1; // for the comma
			}
		}
		totalLength += 1;
		char* result = new char[totalLength];
		char* currentPos = result;
		for (size_t i = 1; i < device_list.size(); ++i) {
			const std::string& str = device_list[i];
			std::strcpy(currentPos, str.c_str()); // Copy the string
			currentPos += str.length(); // Move to the next position
			if (device_list.size() == 2)
			{
				*currentPos = ',';
				++currentPos;
			}
			else
			{
				if (i < device_list.size() - 1) {
					*currentPos = ',';
					++currentPos;
				}
			}
		}


		*currentPos = '\0';
		if (USER_MODE == ENGINEER || USER_MODE == ADMIN)
		{
			DEVICE_SEL = device_list[STSSetInitSelectDialog("Partnum Select", 5, 0, result) + 1];
			string trim_setup_name = DEVICE_SEL + ".treg";
			const char* device_str_ptr = trim_setup_name.c_str();
		}
		else
		{
			char LotID_value[20];
			char LotID_name[20];
			for (int i = 0; i < 20; i++)
			{
				memset(LotID_value, 0, sizeof(LotID_value));
				memset(LotID_name, 0, sizeof(LotID_name));
				GetNewLotItemInfo(i, LotID_name, LotID_value, 20);//Get the information for lot items.
				if (strcmp("PART_TYP", LotID_name) == 0)
				{
	
					string  partname = LotID_value;
					findDevicePrefix(device_list, partname, DEVICE_SEL);
					string PRD_DEVICE_SEL = DEVICE_SEL + "-AAA1";
					string ENG_DEVICE_SEL = DEVICE_SEL + "-ABA1";
					if (PRD_DEVICE_SEL == partname)
					{
					}
					else if (ENG_DEVICE_SEL == partname)
					{
					}
					else
					{
						PostQuitMessage(0);
					}
					string trim_setup_name = DEVICE_SEL + ".treg";
					const char* device_str_ptr = trim_setup_name.c_str();
					break;
				}
			}
		}

		char P_PGS_NAME[30];
		STSGetPgsName(P_PGS_NAME, 30);
		//bool pgs_check_pass = false;
		if (containsSubstringC(P_PGS_NAME, "QA"))
		{
			TEST_FLOW = QA;
			//pgs_check_pass = true;
		}
		else if (containsSubstringC(P_PGS_NAME, "Qual"))
		{
			TEST_FLOW = QUAL;
			//pgs_check_pass = true;
		}
		else if (containsSubstringC(P_PGS_NAME, "TempChar"))
		{
			TEST_FLOW = TempChar;
			//pgs_check_pass = true;
		}
		else if (containsSubstringC(P_PGS_NAME, "HTOL_Read"))
		{
			TEST_FLOW = HTOL_Read;
			//pgs_check_pass = true;
		}
		else if (containsSubstringC(P_PGS_NAME, "HTOL_Burn"))
		{
			TEST_FLOW = HTOL_Burn;
			//pgs_check_pass = true;
		}
		else
		{
			TEST_FLOW = FT;
			//pgs_check_pass = true;
		}
		//if (!pgs_check_pass)
		//{
		//	MessageBoxA(NULL, "程序里无法找到与选择的PGS相匹配的文件 ", "诊断提示对话框", MB_YESNO);
		//	PostQuitMessage(0);
		//}
		string trim_setup_name = DEVICE_SEL + ".treg";
		const char* device_str_ptr = trim_setup_name.c_str();
		delete[] result;
		result = NULL;
		if (AllocConsole())//(AttachConsole(ATTACH_PARENT_PROCESS))//
		{
			COORD size = { 180, 180 };

			SetConsoleTitleA("AccoTEST Debug Window");
			freopen("conout$", "w+t", stdout);
			::DeleteMenu(GetSystemMenu(GetConsoleWindow(), FALSE), SC_CLOSE, MF_BYCOMMAND);
			//HANDLE hOUT = GetStdHandle(STD_OUTPUT_HANDLE);//获取标准输出句柄
			//hOUT = GetStdHandle(STD_OUTPUT_HANDLE);
			//设置控制台缓冲区大小
			//SetConsoleScreenBufferSize(hOUT, size);
			//delay_ms(2000);
		}
		Part_Num = extractIntFromString(DEVICE_SEL);
		SetColor(2);
		//--------------------Init Trim Document here
		trim_reg.init(device_str_ptr, SITE_NUM, QC, DO_TRIM);
		ResetColor();
		//cout << std::left << std::setw(20) << "I successed" << std::setw(20) << "I failed" << "paly"<< std::endl;
		//cout << std::left << std::setw(20) << "I did" << std::setw(20) << "I fghjbchubru" << "frggvdbr" << std::endl;
		//delay_ms(3000);
		fclose(stdout);
		FreeConsole();
		////------------close printf window
	LOOP_COUNT++;
}

void Inherit_register()
{
	if (TEST_FLOW == FT)
	{
		DWORD BestCode_F0[SITE_NUM] = { 0 };
		DWORD BestCode_F1[SITE_NUM] = { 0 };
		DWORD BestCode_F2[SITE_NUM] = { 0 };
		DWORD BestCode_F3[SITE_NUM] = { 0 };
		DWORD BestCode_F4[SITE_NUM] = { 0 };
		DWORD BestCode_F5[SITE_NUM] = { 0 };
		DWORD BestCode_F6[SITE_NUM] = { 0 };
		DWORD BestCode_F7[SITE_NUM] = { 0 };
		DWORD BestCode_F8[SITE_NUM] = { 0 };
		DWORD BestCode_F9[SITE_NUM] = { 0 };
		DWORD BestCode_FA[SITE_NUM] = { 0 };
		DWORD BestCode_FB[SITE_NUM] = { 0 };
		DWORD BestCode_FC[SITE_NUM] = { 0 };
		DWORD BestCode_FD[SITE_NUM] = { 0 };
		DWORD BestCode_FE[SITE_NUM] = { 0 };
		DWORD BestCode_FF[SITE_NUM] = { 0 };
		FOR_EACH_VALID_SITE(site)
		{
			if (BURN_FLAG[site] == BURNNED)
			{
				trim_reg.assy("EFUSE_REG_REGISTER").copy_read_to_work(site);
			}
		}
		FOR_EACH_VALID_SITE(site)
		{
			BestCode_F0[site] = trim_reg.assy("EFUSE_REG_F0").get_working(site);
			BestCode_F1[site] = trim_reg.assy("EFUSE_REG_F1").get_working(site);
			BestCode_F2[site] = trim_reg.assy("EFUSE_REG_F2").get_working(site);
			BestCode_F3[site] = trim_reg.assy("EFUSE_REG_F3").get_working(site);
			BestCode_F4[site] = trim_reg.assy("EFUSE_REG_F4").get_working(site);
			BestCode_F5[site] = trim_reg.assy("EFUSE_REG_F5").get_working(site);
			BestCode_F6[site] = trim_reg.assy("EFUSE_REG_F6").get_working(site);
			BestCode_F7[site] = trim_reg.assy("EFUSE_REG_F7").get_working(site);
			BestCode_F8[site] = trim_reg.assy("EFUSE_REG_F8").get_working(site);
			BestCode_F9[site] = trim_reg.assy("EFUSE_REG_F9").get_working(site);
			BestCode_FA[site] = trim_reg.assy("EFUSE_REG_FA").get_working(site);
			BestCode_FB[site] = trim_reg.assy("EFUSE_REG_FB").get_working(site);
			BestCode_FC[site] = trim_reg.assy("EFUSE_REG_FC").get_working(site);
			BestCode_FD[site] = trim_reg.assy("EFUSE_REG_FD").get_working(site);
			BestCode_FE[site] = trim_reg.assy("EFUSE_REG_FE").get_working(site);
			BestCode_FF[site] = trim_reg.assy("EFUSE_REG_FF").get_working(site);
		}
		dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, BestCode_F0);
		dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, BestCode_F1);
		dcm.I2CWriteData(DEV_ADDR, 0xF2, 1, BestCode_F2);
		dcm.I2CWriteData(DEV_ADDR, 0xF3, 1, BestCode_F3);
		dcm.I2CWriteData(DEV_ADDR, 0xF4, 1, BestCode_F4);
		dcm.I2CWriteData(DEV_ADDR, 0xF5, 1, BestCode_F5);
		dcm.I2CWriteData(DEV_ADDR, 0xF6, 1, BestCode_F6);
		dcm.I2CWriteData(DEV_ADDR, 0xF7, 1, BestCode_F7);
		dcm.I2CWriteData(DEV_ADDR, 0xF8, 1, BestCode_F8);
		dcm.I2CWriteData(DEV_ADDR, 0xF9, 1, BestCode_F9);
		dcm.I2CWriteData(DEV_ADDR, 0xFA, 1, BestCode_FA);
		dcm.I2CWriteData(DEV_ADDR, 0xFB, 1, BestCode_FB);
		dcm.I2CWriteData(DEV_ADDR, 0xFC, 1, BestCode_FC);
		dcm.I2CWriteData(DEV_ADDR, 0xFD, 1, BestCode_FD);
		dcm.I2CWriteData(DEV_ADDR, 0xFE, 1, BestCode_FE);
		dcm.I2CWriteData(DEV_ADDR, 0xFF, 1, BestCode_FF);
	}

}

void clear_resource()
{
	VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(2);
	FOVI_GRP.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	ACM_GRP.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_OFF);
}

//================NU6801 defined variables and functions======//
float Period = 4000;
double V_TYP_VBAT;
double V_TYP_VBUS;
double V_TYP_VAC;

double avss_tsbat[SITE_NUM] = { 0 };
ULONG data_read[SITE_NUM] = { 0 };

double IBUS_SNS_Gain[SITE_NUM] = { 0 };
double BUCK_IBAT_HS_Gain[SITE_NUM] = { 0 };
double BUCK_IBAT_LS_Gain[SITE_NUM] = { 0 };
double BOOST_IBAT_HS_Gain[SITE_NUM] = { 0 };
double BOOST_IBAT_LS_Gain[SITE_NUM] = { 0 };
double IBUS_EA_BASE[SITE_NUM] = { 0 };
double Iscale_buck[SITE_NUM] = { 0 };
double Iscale_boost[SITE_NUM] = { 0 };
double Vclamp_high_buck[SITE_NUM] = { 0 };
double Vclamp_high_boost[SITE_NUM] = { 0 };
double buck_ls_zcd[SITE_NUM] = { 0 };
double boost_hs_zcd[SITE_NUM] = { 0 };
double boost_hs_noc[SITE_NUM] = { 0 };
double boost_hs_ocp_off[SITE_NUM] = { 0 };
double boost_hs_ocp_11A[SITE_NUM] = { 0 };
double boost_hs_ocp_16p5A[SITE_NUM] = { 0 };
double boost_ls_pk_vos[SITE_NUM] = { 0 };
double boost_hs_ocp_vos[SITE_NUM] = { 0 };
double Gain_peak_hsfet[SITE_NUM] = { 0 };
double Gain_peak_lsfet[SITE_NUM] = { 0 };

double hs_ocp_ref_off[SITE_NUM] = { 0 };
 double iocp_ref_11A[SITE_NUM] = { 0 };
 double iocp_ref_16p5A[SITE_NUM] = { 0 };

double Ibat_cc_lp_os_buck_1a[SITE_NUM] = { 0 };
double Ibat_cc_lp_os_buck_2a[SITE_NUM] = { 0 };
double Ibat_cc_lp_os_buck_3a[SITE_NUM] = { 0 };
double Ibat_cc_lp_os_buck_4a[SITE_NUM] = { 0 };
double Ibat_cc_lp_os_buck_6a[SITE_NUM] = { 0 };

double Ibat_cc_lp_os_boost_1a[SITE_NUM] = { 0 };
double Ibat_cc_lp_os_boost_2a[SITE_NUM] = { 0 };
double Ibat_cc_lp_os_boost_3a[SITE_NUM] = { 0 };
double Ibat_cc_lp_os_boost_4a[SITE_NUM] = { 0 };
double Ibat_cc_lp_os_boost_6a[SITE_NUM] = { 0 };
double Ibat_cc_lp_os_boost_8a[SITE_NUM] = { 0 };

double Vcs_qrb_sns_buck_1A[SITE_NUM] = { 0 };
double Vcs_qrb_sns_buck_2A[SITE_NUM] = { 0 };
double Vcs_qrb_sns_buck_3A[SITE_NUM] = { 0 };
double Vcs_qrb_sns_boost_1A[SITE_NUM] = { 0 };
double Vcs_qrb_sns_boost_2A[SITE_NUM] = { 0 };
double Vcs_qrb_sns_boost_3A[SITE_NUM] = { 0 };

double Buck_lsfet_zcd[SITE_NUM] = { 0 };
double Boost_hsfet_zcd[SITE_NUM] = { 0 };
double BU_zcd_in_BO_Rcs_Mode[SITE_NUM] = { 0 };
double BO_zcd_in_BU_Rcs_Mode[SITE_NUM] = { 0 };
double Ibus_loop_Voffset_2A[SITE_NUM] = { 0 };


/************************************************************************/
/*                                                                      */
/************************************************************************/
//extern "C" int USERRES_API STSMaskTHBConfigCheck(bool maskFlag); // CLEAR EPROM
//initialize function will be called before all the test functions.
/************************************************************************/
/*                                                                      */
/************************************************************************/
DUT_API void UserLoad()
{
	//	STSMaskTHBConfigCheck(true);// CLEAR EPROM
	int a = dcm.LoadVectorFile("F68011.acvec", TRUE);

	int loadpass = -1;
	loadpass = dcm.LoadVectorFile("Davis_A1.acvec", TRUE);//20241222
	dcm.SetPinGroup("G_CLK", "SDA,SCL,NTC");
	dcm.SetPinGroup("G_OUT", "INT");
	dcm.SetPinGroup("G_ALLPIN", "INT,SDA,SCL,NTC");
	if (loadpass == 0)
	{
		Scan_pat_load_succeess = true;
	}
	STSMaskTHBConfigCheck(1);
	STSSetHardwareCheck(false);


	STSSetMultiSiteBindEx(MD_FOVIe, 0, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE1_);
	STSSetMultiSiteBindEx(MD_FOVIe, 1, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE2_);
	STSSetMultiSiteBindEx(MD_FOVIe, 2, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE3_);
	STSSetMultiSiteBindEx(MD_FOVIe, 3, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE4_);
	STSSetMultiSiteBindEx(MD_FOVIe, 4, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE5_);
	STSSetMultiSiteBindEx(MD_FOVIe, 5, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE6_);
	STSSetMultiSiteBindEx(MD_FOVIe, 6, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE7_);
	STSSetMultiSiteBindEx(MD_FOVIe, 7, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE8_);
	STSSetMultiSiteBindEx(MD_FOVIe, 8, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE9_);
	STSSetMultiSiteBindEx(MD_FOVIe, 9, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE10_);
	STSSetMultiSiteBindEx(MD_FOVIe, 10, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE11_);
	STSSetMultiSiteBindEx(MD_FOVIe, 11, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE12_);
	STSSetMultiSiteBindEx(MD_FOVIe, 12, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE13_);
	STSSetMultiSiteBindEx(MD_FOVIe, 13, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE14_);
	STSSetMultiSiteBindEx(MD_FOVIe, 14, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE15_);
	STSSetMultiSiteBindEx(MD_FOVIe, 15, _PIN_SITE_BIND_DEFINE_MD_FOVIE_SITE16_);
	STSSetMultiSiteBindEx(MD_QVMe, NO_SITE, _PIN_SITE_BIND_DEFINE_MD_QVME_NOSITE);
	STSSetMultiSiteBindEx(MD_FPVIe, 0, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE1_);
	STSSetMultiSiteBindEx(MD_FPVIe, 1, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE2_);
	STSSetMultiSiteBindEx(MD_FPVIe, 2, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE3_);
	STSSetMultiSiteBindEx(MD_FPVIe, 3, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE4_);
	STSSetMultiSiteBindEx(MD_FPVIe, 4, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE5_);
	STSSetMultiSiteBindEx(MD_FPVIe, 5, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE6_);
	STSSetMultiSiteBindEx(MD_FPVIe, 6, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE7_);
	STSSetMultiSiteBindEx(MD_FPVIe, 7, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE8_);
	STSSetMultiSiteBindEx(MD_FPVIe, 8, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE9_);
	STSSetMultiSiteBindEx(MD_FPVIe, 9, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE10_);
	STSSetMultiSiteBindEx(MD_FPVIe, 10, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE11_);
	STSSetMultiSiteBindEx(MD_FPVIe, 11, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE12_);
	STSSetMultiSiteBindEx(MD_FPVIe, 12, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE13_);
	STSSetMultiSiteBindEx(MD_FPVIe, 13, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE14_);
	STSSetMultiSiteBindEx(MD_FPVIe, 14, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE15_);
	STSSetMultiSiteBindEx(MD_FPVIe, 15, _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE16_);
	STSSetMultiSiteBindEx(MD_QTMUe, NO_SITE, _PIN_SITE_BIND_DEFINE_MD_QTMUE_NOSITE);
	STSSetMultiSiteBindEx(MD_ACM200, 0, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE1_);
	STSSetMultiSiteBindEx(MD_ACM200, 1, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE2_);
	STSSetMultiSiteBindEx(MD_ACM200, 2, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE3_);
	STSSetMultiSiteBindEx(MD_ACM200, 3, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE4_);
	STSSetMultiSiteBindEx(MD_ACM200, 4, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE5_);
	STSSetMultiSiteBindEx(MD_ACM200, 5, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE6_);
	STSSetMultiSiteBindEx(MD_ACM200, 6, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE7_);
	STSSetMultiSiteBindEx(MD_ACM200, 7, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE8_);
	STSSetMultiSiteBindEx(MD_ACM200, 8, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE9_);
	STSSetMultiSiteBindEx(MD_ACM200, 9, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE10_);
	STSSetMultiSiteBindEx(MD_ACM200, 10, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE11_);
	STSSetMultiSiteBindEx(MD_ACM200, 11, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE12_);
	STSSetMultiSiteBindEx(MD_ACM200, 12, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE13_);
	STSSetMultiSiteBindEx(MD_ACM200, 13, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE14_);
	STSSetMultiSiteBindEx(MD_ACM200, 14, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE15_);
	STSSetMultiSiteBindEx(MD_ACM200, 15, _PIN_SITE_BIND_DEFINE_MD_ACM200_SITE16_);
	AstBindingAllModule();

	//----OPERATOR Mode =1
	//----ENGINEER Mode=2
	//----ADMIN Mode=3
	USER_MODE = STSGetUserPriority();
	delay_ms(1);
	if (USER_MODE == ENGINEER || USER_MODE == ADMIN)
	{
		std::thread hotKeyThread(HotKeyThread);
		hotKeyThread.detach(); // 让线程在后台运行
	}

	//---------------------Init Spec document here
	spec.init("NU6801.spec");
	//int totl;
	//spec.get_funcname_vs_paracnt_matrix("OS_PRE", &totl);

	//DEVICE *device_sel = spec.getNextDevice();
	//string pa1=device_sel->getNextParam()->get_param_name_in_spec();
	//string pa2 = device_sel->getNextParam()->get_param_name_in_spec();
	//string pa3 = device_sel->getNextParam()->get_param_name_in_spec();

	//--------------Disable function here
//	spec.SetTestFuncDisableByFuncName("TEST_FUNC2");


	//=======Setup function : trim/test flow/board check/etc
	if (USER_MODE == ENGINEER||USER_MODE==ADMIN)
	{
		TESTER_SETUP_FUNCTION();
	}


	if (USER_MODE == OPERATOR)
	{
		//=======Operator 模式 必须要做BoardCheck
		run_diags();
	}
	else
	{

		////====================BoardCheck Setup Block=================================================
		DO_BoardCheck = MessageBoxA(NULL, "   Bypass BoardCheck!  (跳过BoardCheck)\n", "BoardCheck提示对话框", MB_YESNO) == IDNO;
		if (DO_BoardCheck)
			run_diags();
		//BoardcheckPass=run_diags();
		//     //=====================Perform FMEA BLOCK===================================================
		//	if (DO_FMEA)
		//		efmea.fmea_2_enable = 1;	
	}
}


/************************************************************************/
/*                                                                      */
/************************************************************************/
DUT_API void UserInit()
{
	if (USER_MODE == OPERATOR && IsFirstLoop())
	{
		TESTER_SETUP_FUNCTION();
	}

}
/************************************************************************/
/*                                                                      */
/************************************************************************/
DUT_API void UserExit()
{
}
/************************************************************************/
/*                                                                      */
/************************************************************************/
DUT_API void OnSot()
{

}
/************************************************************************/
DUT_API void InitBeforeTestFlow()
{
	//shmoo.sot();
	//int a=STSGetParamCount(0);
	//StsGetParam(0, spec.get_para_name("TEST_INFO", 1).c_str())->SetbVisible();
	//StsGetParam(0, spec.get_para_name("TEST_INFO", 2).c_str())->GetMaxLimit();
	//StsGetParam(0, spec.get_para_name("TEST_INFO", 3).c_str())->GetMaxLimit();
	//StsGetParam(0, spec.get_para_name("TEST_INFO", 4).c_str())->GetMaxLimit();
	//double high = spec.get_high_limit(funclabel, funcindex);
	//double low = spec.get_low_limit(funclabel, funcindex);
	string name = spec.get_para_name("TEST_INFO", 1);

	FOR_EACH_VALID_SITE(site)
	{
		BURN_FLAG[site] =FRESH;
	}



	//--------------------------------------------------------------------------------------------------//
	//=======================-Cannot Delete=====================//
	Set_I2C();
	Getsiteselected();// Cannot save , need Get selected enable site by handler or manual
	StsGetSiteStatus(sitesta, SITE_NUM);
	trim_reg.sot();
	efmea.sot();
	sos.sot();
	if (TEST_FLOW == TempChar&& TS.confirm_L_button_clicked())
	{
		TS.tsinitbeforetest();
	}
	//--------------------------------------------------------------------------------------------------//
	//=======================-Cannot Delete=====================//
	//DWORD working_value2[SITE_NUM] = { 0 };
	//FOR_EACH_VALID_SITE(site)
	//{
	//	working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_FF").get_working(site);
	//}


	//==============Power Supply Set needed in your program===============//
	spec("VBAT").set_select_index(spec.get_sel_vin_index());
	spec("VAC").set_select_index(spec.get_sel_vin_index());
	spec("VBUS").set_select_index(spec.get_sel_vin_index());

	Temperature1 = spec("TEMP_CHAR")[spec.get_sel_temp_index()];
	double aaaa = spec("TEMP_CHAR")[spec.get_sel_temp_index()];

	V_TYP_VBAT = spec("VBAT");
	V_TYP_VBUS = spec("VBUS");
	V_TYP_VAC = spec("VAC");
	//==============Power Supply Set needed in your program===============//


	VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(2);
	FOVI_GRP.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	ACM_GRP.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_OFF);
	DCM_Channel_Disconnect();
}
/************************************************************************/
//initializefunction will be called after all the test functions.
DUT_API void InitAfterTestFlow()
{
	VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(2);
	FOVI_GRP.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	ACM_GRP.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_OFF);
	sos.eot();
	if (TEST_FLOW == 2)
	{
		TS.tseot();
	}
	cbite.SetOn(-1);
}
/************************************************************************/
/*                                                                      */
/************************************************************************/
//Fail site hardware set function will be called after failed params, it can be called for serveral times.
DUT_API void SetupFailSite(const unsigned char*byFailSite)
{
	//---------------------处理fail site 的资源状态需要按site执行
	int TestStatus[SITE_NUM] = { 0 };
	//FOR_EACH_VALID_SITE(site)// 只有fail Site 才会进入到这里面来
	//{
	//	BEGIN_SINGLE_SITE(site)
			VBUS_FOVI.Set(FV,0,FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
			PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
			AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
			NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
			SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
			delay_ms(2);

			FOVI_GRP.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
			ACM_GRP.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
			FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA,FPVIe_RELAY_OFF);
		//END_SINGLE_SITE();
	//}

	//*********************Cannot Delete**********************//
	//TS.tsfot();
	//efmea.fmea_onfailsite();
	//*********************Cannot Delete**********************//
}
/************************************************************************/
/*                                                                      */
/************************************************************************/
DUT_API void BinOutDut()
{
	//*********************Cannot Delete**********************//
	trim_reg.eot(); 
	//efmea.eot();
	//shmoo.shmoo_eot();
	//*********************Cannot Delete**********************//
}
/************************************************************************/
/*                                                                      */
/************************************************************************/
DUT_API void OnNewLot(const char *Lotid)
{
	//if (STSGetUserPriority() == OPERATOR)//------------------if Operator mode will not do anything
	//{

	//}
	//else// -----------------if not do in operator mode, can use
	//{
	//	std::string target = "L";
	//	if (target.compare(Lotid) == 1) 
	//	{
	//		shmoo.initial_shmoomap();
	//		shmoo.shmoo_plot();
	//		string bb = spec("TEMP_CHAR").get_param_name_in_spec();
	//	string aaa=	spec.getNextDevice()->getNextParam()->get_param_name_in_spec();
	//		shmoo.select_shmoo_x_y_param(spec);	
	//	}
	//}
}
/************************************************************************/
/*                                                                      */
/************************************************************************/
DUT_API void OnWaferEnd(const char *Lotid)
{
}
/************************************************************************/
/*                                                                      */
/************************************************************************/

DUT_API int DEVICE_INFO(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *Part_No = StsGetParam(funcindex, "Part_No");
    CParam *QC_flag = StsGetParam(funcindex, "QC_flag");
    CParam *X_Coordinate = StsGetParam(funcindex, "X_Coordinate");
    CParam *Y_Coordinate = StsGetParam(funcindex, "Y_Coordinate");
    CParam *Wafer_ID = StsGetParam(funcindex, "Wafer_ID");
    CParam *VBAT = StsGetParam(funcindex, "VBAT");
    CParam *VBUS = StsGetParam(funcindex, "VBUS");
    CParam *VAC = StsGetParam(funcindex, "VAC");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	FOR_EACH_VALID_SITE(site)
	{
		Part_No->SetTestResult(site, 0, Part_Num);
		QC_flag->SetTestResult(site, 0, TEST_FLOW);
		if (Relay_Off_Check)
		{
			X_Coordinate->SetTestResult(site, 0, 1);
		}
		else
		{
			X_Coordinate->SetTestResult(site, 0, 999);
		}
		Y_Coordinate->SetTestResult(site, 0, 1);
		Wafer_ID->SetTestResult(site, 0, 22);
		VBAT->SetTestResult(site, 0, V_TYP_VBAT);
		VBUS->SetTestResult(site, 0, V_TYP_VBUS);
		VAC->SetTestResult(site, 0, V_TYP_VAC);
	}

	return 0;
}

DUT_API int Kelvin_Check(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_Kelvin = StsGetParam(funcindex, "VBUS_Kelvin");
    CParam *PMID_Kelvin = StsGetParam(funcindex, "PMID_Kelvin");
    CParam *SW_Kelvin = StsGetParam(funcindex, "SW_Kelvin");
    CParam *PGND_Kelvin = StsGetParam(funcindex, "PGND_Kelvin");
    CParam *VBAT_Kelvin = StsGetParam(funcindex, "VBAT_Kelvin");
    CParam *VDRV_Kelvin = StsGetParam(funcindex, "VDRV_Kelvin");
    CParam *AMUX_Kelvin = StsGetParam(funcindex, "AMUX_Kelvin");
    CParam *NTC_Kelvin = StsGetParam(funcindex, "NTC_Kelvin");
    CParam *VAC1_Kelvin = StsGetParam(funcindex, "VAC1_Kelvin");
    CParam *VAC2_Kelvin = StsGetParam(funcindex, "VAC2_Kelvin");
    CParam *VAC3_Kelvin = StsGetParam(funcindex, "VAC3_Kelvin");
    CParam *ACDRV1_Kelvin = StsGetParam(funcindex, "ACDRV1_Kelvin");
    CParam *ACDRV2_Kelvin = StsGetParam(funcindex, "ACDRV2_Kelvin");
    CParam *ACDRV3_Kelvin = StsGetParam(funcindex, "ACDRV3_Kelvin");
    CParam *KLV1_Kelvin = StsGetParam(funcindex, "KLV1_Kelvin");
    CParam *KLV2_Kelvin = StsGetParam(funcindex, "KLV2_Kelvin");
    CParam *SDA_Kelvin = StsGetParam(funcindex, "SDA_Kelvin");
    CParam *INT_Kelvin = StsGetParam(funcindex, "INT_Kelvin");
    CParam *BST_Kelvin = StsGetParam(funcindex, "BST_Kelvin");
    CParam *VCC_Kelvin = StsGetParam(funcindex, "VCC_Kelvin");
    CParam *NTC2_Kelvin = StsGetParam(funcindex, "NTC2_Kelvin");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	double kelvin_i = 0.008;//8mA
	//----------10Kohm Kelvin VBUS
	double Kelvin_r[SITE_NUM] = { 0 };
	cbite.SetOn(K8_KELVIN, K10_KELVIN, K11_KELVIN, K15_BUSH_VBUS, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		VBUS_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------10Kohm Kelvin VSW
	cbite.SetOn(K8_KELVIN, K10_KELVIN, K11_KELVIN, K17_BUSH_SW, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		SW_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//---------9Kohm Kelvin KLV1
	cbite.SetOn(K8_KELVIN, K10_KELVIN, K11_KELVIN, K19_BUSH_KLV, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		KLV1_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------10Kohm Kelvin KLV2
	cbite.SetOn(K8_KELVIN, K10_KELVIN, K11_KELVIN, K19_BUSH_KLV, K20_SHARE_KLV, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		KLV2_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------9Kohm Kelvin ACDRV1
	cbite.SetOn(K8_KELVIN, K10_KELVIN, K11_KELVIN, K21_BUSH_ACDRV, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		ACDRV1_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------10Kohm Kelvin ACDRV2
	cbite.SetOn(K8_KELVIN, K10_KELVIN, K11_KELVIN, K21_BUSH_ACDRV, K23_SHARE2_ACDRV, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		ACDRV2_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------11Kohm Kelvin ACDRV3
	cbite.SetOn(K8_KELVIN, K10_KELVIN, K11_KELVIN, K21_BUSH_ACDRV, K22_SHARE1_ACDRV, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		ACDRV3_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------10Kohm Kelvin VDRV
	cbite.SetOn(K8_KELVIN, K10_KELVIN, K11_KELVIN, K26_BUSH_VDRV, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		VDRV_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------10Kohm Kelvin PGND
	cbite.SetOn(K8_KELVIN, K10_KELVIN, K11_KELVIN, K42_BUSH_PGND, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		PGND_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------10Kohm Kelvin AMUX
	cbite.SetOn(K8_KELVIN, K10_KELVIN, K11_KELVIN, K40_BUSH_AMUX, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		AMUX_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------10Kohm Kelvin NTC
	cbite.SetOn(K8_KELVIN, K10_KELVIN, K11_KELVIN, K41_BUSH_NTC, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		NTC_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------10Kohm Kelvin VBAT
	cbite.SetOn(K8_KELVIN, K9_KELVIN, K10_KELVIN, K29_BUSL_VBAT, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		VBAT_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------10Kohm Kelvin PMID
	cbite.SetOn(K8_KELVIN, K9_KELVIN, K10_KELVIN, K31_BUSL_PMID, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		PMID_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}


	//----------9Kohm Kelvin VAC1
	cbite.SetOn(K8_KELVIN, K9_KELVIN, K10_KELVIN, K34_BUSL_VAC, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		VAC1_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------10Kohm Kelvin VAC2
	cbite.SetOn(K8_KELVIN, K9_KELVIN, K10_KELVIN, K34_BUSL_VAC, K36_SHARE2_VAC, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		VAC2_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------11Kohm Kelvin VAC3
	cbite.SetOn(K8_KELVIN, K9_KELVIN, K10_KELVIN, K34_BUSL_VAC, K35_SHARE1_VAC, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		VAC3_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------10Kohm Kelvin BTST
	cbite.SetOn(K8_KELVIN, K9_KELVIN, K10_KELVIN, K38_BUSL_BTST, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, kelvin_i, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_2V, FPVIe_10MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		Kelvin_r[site] = FPVI.GetMeasResult(site, MVRET) / FPVI.GetMeasResult(site, MIRET);
		BST_Kelvin->SetTestResult(site, 0, Kelvin_r[site]);
	}

	//----------10Kohm Kelvin VCC
	double VCC_R_high_side[SITE_NUM] = { 0 };
	double VCC_R_low_side[SITE_NUM] = { 0 };
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.ContactCheck(ACM200_HIGH_SIDE);
	FOR_EACH_VALID_SITE(site)
	{
		VCC_ACM.GetContactCheckResult(site, VCC_R_high_side[site], VCC_R_low_side[site]);
		VCC_Kelvin->SetTestResult(site, 0, VCC_R_high_side[site]);
	}
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

	//----------10Kohm Kelvin VBATD
	double VBATD_R_hs[SITE_NUM] = { 0 };
	double VBATD_R_ls[SITE_NUM] = { 0 };
	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBATD_ACM.ContactCheck(ACM200_HIGH_SIDE);
	FOR_EACH_VALID_SITE(site)
	{
		VBATD_ACM.GetContactCheckResult(site, VBATD_R_hs[site], VBATD_R_ls[site]);
		NTC2_Kelvin->SetTestResult(site, 0, VBATD_R_hs[site]);
	}
	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

	//----------10Kohm Kelvin SDA
	double SDA_R_hs[SITE_NUM] = { 0 };
	double SDA_R_ls[SITE_NUM] = { 0 };
	cbite.SetOn(K44_SDA_ACM, -1);
	delay_ms(3);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SDA_INT_ACM.ContactCheck(ACM200_HIGH_SIDE);
	FOR_EACH_VALID_SITE(site)
	{
		SDA_INT_ACM.GetContactCheckResult(site, SDA_R_hs[site], SDA_R_ls[site]);
		SDA_Kelvin->SetTestResult(site, 0, SDA_R_hs[site]/2);
	}
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

	//----------10Kohm Kelvin INT
	double INT_R_hs[SITE_NUM] = { 0 };
	double INT_R_ls[SITE_NUM] = { 0 };
	cbite.SetOn(K43_INT_ACM, -1);
	delay_ms(3);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SDA_INT_ACM.ContactCheck(ACM200_HIGH_SIDE);
	FOR_EACH_VALID_SITE(site)
	{
		SDA_INT_ACM.GetContactCheckResult(site, INT_R_hs[site], INT_R_ls[site]);
		INT_Kelvin->SetTestResult(site, 0, INT_R_hs[site]);
	}
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	
	return 0;
}

DUT_API int P2P_Leakage(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_P2P_Leak = StsGetParam(funcindex, "VBUS_P2P_Leak");
    CParam *PMID_P2P_Leak = StsGetParam(funcindex, "PMID_P2P_Leak");
    CParam *SW_P2P_Leak = StsGetParam(funcindex, "SW_P2P_Leak");
    CParam *PGND_P2P_Leak = StsGetParam(funcindex, "PGND_P2P_Leak");
    CParam *BTST_P2P_Leak = StsGetParam(funcindex, "BTST_P2P_Leak");
    CParam *VBAT_P2P_Leak = StsGetParam(funcindex, "VBAT_P2P_Leak");
    CParam *NTC2_P2P_Leak = StsGetParam(funcindex, "NTC2_P2P_Leak");
    CParam *AMUX_P2P_Leak = StsGetParam(funcindex, "AMUX_P2P_Leak");
    CParam *NTC_P2P_Leak = StsGetParam(funcindex, "NTC_P2P_Leak");
    CParam *VCC_P2P_Leak = StsGetParam(funcindex, "VCC_P2P_Leak");
    CParam *VAC1_P2P_Leak = StsGetParam(funcindex, "VAC1_P2P_Leak");
    CParam *VAC2_P2P_Leak = StsGetParam(funcindex, "VAC2_P2P_Leak");
    CParam *VAC3_P2P_Leak = StsGetParam(funcindex, "VAC3_P2P_Leak");
    CParam *KLV1_P2P_Leak = StsGetParam(funcindex, "KLV1_P2P_Leak");
    CParam *KLV2_P2P_Leak = StsGetParam(funcindex, "KLV2_P2P_Leak");
    CParam *ACDRV1_P2P_Leak = StsGetParam(funcindex, "ACDRV1_P2P_Leak");
    CParam *ACDRV2_P2P_Leak = StsGetParam(funcindex, "ACDRV2_P2P_Leak");
    CParam *ACDRV3_P2P_Leak = StsGetParam(funcindex, "ACDRV3_P2P_Leak");
    CParam *VDRV_P2P_Leak = StsGetParam(funcindex, "VDRV_P2P_Leak");
    CParam *SCL_P2P_Leak = StsGetParam(funcindex, "SCL_P2P_Leak");
    CParam *SDA_P2P_Leak = StsGetParam(funcindex, "SDA_P2P_Leak");
    CParam *INT_P2P_Leak = StsGetParam(funcindex, "INT_P2P_Leak");
    CParam *CopperTrace = StsGetParam(funcindex, "CopperTrace");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	bool have_copper_trace[SITE_NUM] = { 0 };
	double Vp2p = 0.05;
	double p2p_leakage[SITE_NUM] = { 0 };
	int wait_time = 500;
	//======KLV1,ACDRV2, ACDRV3,VAC2, VAC3 short to AGND
	//======PMID, SW, KLV2, ACDRV1, VCC, VDRV, VBAT,PGND, VAC1, BTST, VBATD, SCL, INT, SDA, AMUX, NTC force 0V
	cbite.SetOn(K20_SHARE_KLV,K68_KLV1_P2P, K48_ACDRV2_P2P, K49_ACDRV3_P2P, K51_VAC2_P2P, K52_VAC3_P2P, K43_INT_ACM, K44_SDA_ACM,K46_INT_ACM,K55_SCL_ACM, K18_BST_SW_Cap,-1);
	delay_ms(3);
	VBUS_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//VBUS
	//PMID_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//PMID
	NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//NTC
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//AMUX
	SW_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//SW
	KLV12_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//KLV2
	ACDRV123_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//ACDRV1
	VCC_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VDRV
	VDRV_AMP_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VDRV
	VBAT_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VBAT
	PGND_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//PGND
	VAC123_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VAC1
	BTST_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//BTST
	VBATD_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VBATD
	SCL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//INT,SCL
	SDA_INT_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//SDA
	delay_ms(1);
	VBUS_FOVI.Set(FV, Vp2p, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);//VBUS
	VBUS_FOVI.Set(FV, Vp2p, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//VBUS
	delay_us(wait_time);
	VBUS_FOVI.MeasureVI(50, 5);
	VBUS_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//VBUS
	VBUS_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//VBUS
   // delay_ms(1);
	copper_trace_check_after_leakage_measure(VBUS_FOVI, have_copper_trace, p2p_leakage, spec.get_low_limit("VBUS_P2P_Leak"), spec.get_high_limit("VBUS_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = VBUS_FOVI.GetMeasResult(site, MIRET)*1e9;//nA
		VBUS_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	//PMID P2P Leakage
	PMID_FOVI.Set(FV, Vp2p, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);//PMID
	PMID_FOVI.Set(FV, Vp2p, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//PMID
	delay_us(wait_time);
	PMID_FOVI.MeasureVI(50, 5);
	PMID_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//PMID
	VBUS_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//VBUS
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(PMID_FOVI, have_copper_trace, p2p_leakage, spec.get_low_limit("PMID_P2P_Leak"), spec.get_high_limit("PMID_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = PMID_FOVI.GetMeasResult(site, MIRET)*1e9;//nA
		PMID_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	//AMUX P2P Leakage
	AMUX_FOVI.Set(FV, Vp2p, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//AMUX
	delay_us(wait_time);
	AMUX_FOVI.MeasureVI(50, 5);
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//AMUX
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(AMUX_FOVI, have_copper_trace, p2p_leakage, spec.get_low_limit("AMUX_P2P_Leak"), spec.get_high_limit("AMUX_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*1e9;//nA
		AMUX_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	//NTC P2P Leakage
	NTC_FOVI.Set(FV, Vp2p, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//NTC
	delay_us(wait_time);
	NTC_FOVI.MeasureVI(50, 5);
	NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);//NTC
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(NTC_FOVI, have_copper_trace, p2p_leakage, spec.get_low_limit("NTC_P2P_Leak"), spec.get_high_limit("NTC_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = NTC_FOVI.GetMeasResult(site, MIRET)*1e9;//nA
		NTC_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	//SW P2P Leakage
	SW_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);//SW
	SW_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//SW
	//delay_ms(10);
	//SW_ACM.MeasureVI(500, 10);
	Retest_current_unstable_with_time_out(SW_ACM, p2p_leakage, spec.get_low_limit("SW_P2P_Leak") ,spec.get_high_limit("SW_P2P_Leak"), 1, 15, MEAS_NA);
	SW_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//SW
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(SW_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("SW_P2P_Leak"), spec.get_high_limit("SW_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = SW_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		SW_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	//KLV2 P2P Leakage
	KLV12_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//KLV2
	delay_us(wait_time);
	KLV12_ACM.MeasureVI(50, 5);
	KLV12_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//KLV2
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(KLV12_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("KLV2_P2P_Leak"), spec.get_high_limit("KLV2_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = KLV12_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		KLV2_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}


	//ACDRV1 P2P Leakage
	ACDRV123_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//ACDRV1
	delay_us(wait_time);
	ACDRV123_ACM.MeasureVI(50, 5);
	ACDRV123_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//ACDRV1
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(ACDRV123_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("ACDRV1_P2P_Leak"), spec.get_high_limit("ACDRV1_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = ACDRV123_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		ACDRV1_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	//VCC P2P Leakage
	VCC_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);//VCC
	VCC_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VCC
	delay_us(wait_time);
	VCC_ACM.MeasureVI(50, 5);
	VCC_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VCC
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(VCC_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("VCC_P2P_Leak"), spec.get_high_limit("VCC_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = VCC_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		VCC_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	//VDRV P2P Leakage
	VDRV_AMP_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);//VDRV
	VDRV_AMP_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VDRV
	delay_us(wait_time);
	VDRV_AMP_ACM.MeasureVI(50, 5);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VDRV
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(VDRV_AMP_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("VDRV_P2P_Leak"), spec.get_high_limit("VDRV_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = VDRV_AMP_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		VDRV_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	//VBAT P2P Leakage
	VBAT_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);//VBAT
	VBAT_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VBAT
	delay_us(wait_time);
	VBAT_ACM.MeasureVI(50, 5);
	VBAT_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VBAT
	copper_trace_check_after_leakage_measure(VBAT_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("VBAT_P2P_Leak"), spec.get_high_limit("VBAT_P2P_Leak"), MEAS_NA);
	//delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = VBAT_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		VBAT_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}



	//VAC1 P2P Leakage
	VAC123_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);//VAC1
	VAC123_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VAC1
	delay_us(wait_time);
	VAC123_ACM.MeasureVI(50, 5);
	VAC123_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VAC1
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(VAC123_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("VAC1_P2P_Leak"), spec.get_high_limit("VAC1_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		VAC1_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	//BTST P2P Leakage
	BTST_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//BTST
	delay_us(wait_time);
	BTST_ACM.MeasureVI(50, 5);
	BTST_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//BTST
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(BTST_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("BTST_P2P_Leak"), spec.get_high_limit("BTST_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = BTST_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		BTST_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	//VBATD P2P Leakage
	VBATD_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//NTC2
	delay_us(wait_time*3);
	VBATD_ACM.MeasureVI(50, 5);
	VBATD_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//NTC2
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(VBATD_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("NTC2_P2P_Leak"), spec.get_high_limit("NTC2_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = VBATD_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		NTC2_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	cbite.SetOn(K20_SHARE_KLV, K68_KLV1_P2P, K48_ACDRV2_P2P, K49_ACDRV3_P2P, K51_VAC2_P2P, K52_VAC3_P2P,  K44_SDA_ACM, K46_INT_ACM, K55_SCL_ACM, K18_BST_SW_Cap, -1);
	delay_ms(3);
	//SDA P2P Leakage
	dcm.Disconnect("SDA");
	SDA_INT_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//SDA
	delay_us(wait_time);
	SDA_INT_ACM.MeasureVI(50, 5);
	SDA_INT_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//SDA
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(SDA_INT_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("SDA_P2P_Leak"), spec.get_high_limit("SDA_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = SDA_INT_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		SDA_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	cbite.SetOn(K20_SHARE_KLV, K68_KLV1_P2P, K48_ACDRV2_P2P, K49_ACDRV3_P2P, K51_VAC2_P2P, K52_VAC3_P2P, K43_INT_ACM, K44_SDA_ACM, K55_SCL_ACM,-1);
	delay_ms(3);
	dcm.Connect("INT");
	dcm.SetPPMU("INT", DCM_PPMU_FVMV, 0, DCM_PPMUIRANGE_2MA);// EDL force 0V
	dcm.Disconnect("SCL");
	//SCL P2P Leakage
	SCL_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//SCL
	delay_us(wait_time);
	SCL_ACM.MeasureVI(50, 5);
	SCL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//SCL
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(SCL_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("SCL_P2P_Leak"), spec.get_high_limit("SCL_P2P_Leak"), MEAS_NA);
	dcm.Disconnect("INT");//INT
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = SCL_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		SCL_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	cbite.SetOn(K20_SHARE_KLV, K68_KLV1_P2P, K48_ACDRV2_P2P, K49_ACDRV3_P2P, K51_VAC2_P2P, K52_VAC3_P2P, K43_INT_ACM, K55_SCL_ACM,-1);
	delay_ms(3);
	dcm.Connect("SDA");
	dcm.SetPPMU("SDA", DCM_PPMU_FVMV, 0, DCM_PPMUIRANGE_2MA);// SDA force 0V
	//INT P2P Leakage
	SDA_INT_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//INT
	delay_us(wait_time);
	SDA_INT_ACM.MeasureVI(50, 5);
	SDA_INT_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//INT
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(SDA_INT_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("INT_P2P_Leak"), spec.get_high_limit("INT_P2P_Leak"), MEAS_NA);
	dcm.Disconnect("SDA");//SDA
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = SDA_INT_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		INT_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	cbite.SetOn(K20_SHARE_KLV, K68_KLV1_P2P, K48_ACDRV2_P2P, K49_ACDRV3_P2P, K50_VAC1_P2P, K52_VAC3_P2P,K36_SHARE2_VAC ,K43_INT_ACM, K55_SCL_ACM,K46_INT_ACM, K44_SDA_ACM, -1);
	delay_ms(3);
	//VAC2 P2P Leakage
	VAC123_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);//VAC2
	VAC123_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VAC2
	delay_us(wait_time);
	VAC123_ACM.MeasureVI(50, 5);
	VAC123_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VAC2
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(VAC123_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("VAC2_P2P_Leak"), spec.get_high_limit("VAC2_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		VAC2_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	cbite.SetOn(K20_SHARE_KLV, K68_KLV1_P2P, K48_ACDRV2_P2P, K49_ACDRV3_P2P, K50_VAC1_P2P, K51_VAC2_P2P, K35_SHARE1_VAC, K43_INT_ACM, K55_SCL_ACM, K46_INT_ACM, K44_SDA_ACM, -1);
	delay_ms(3);
	//VAC3 P2P Leakage
	VAC123_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);//VAC2
	VAC123_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VAC1
	delay_us(wait_time);
	VAC123_ACM.MeasureVI(50, 5);
	VAC123_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//VAC1
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(VAC123_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("VAC3_P2P_Leak"), spec.get_high_limit("VAC3_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		VAC3_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	cbite.SetOn(K20_SHARE_KLV, K68_KLV1_P2P, K47_ACDRV1_P2P, K49_ACDRV3_P2P, K23_SHARE2_ACDRV,K50_VAC1_P2P, K51_VAC2_P2P, K52_VAC3_P2P, K43_INT_ACM, K55_SCL_ACM, K46_INT_ACM, K44_SDA_ACM, -1);
	delay_ms(3);
	//ACDRV2 P2P Leakage
	ACDRV123_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//ACDRV2
	delay_us(wait_time);
	ACDRV123_ACM.MeasureVI(50, 5);
	ACDRV123_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//ACDRV2
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(ACDRV123_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("ACDRV2_P2P_Leak"), spec.get_high_limit("ACDRV2_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = ACDRV123_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		ACDRV2_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	cbite.SetOn(K20_SHARE_KLV, K68_KLV1_P2P, K47_ACDRV1_P2P, K48_ACDRV2_P2P ,K22_SHARE1_ACDRV, K50_VAC1_P2P, K51_VAC2_P2P, K52_VAC3_P2P, K43_INT_ACM, K55_SCL_ACM, K46_INT_ACM, K44_SDA_ACM, -1);
	delay_ms(3);
	//ACDRV3 P2P Leakage
	ACDRV123_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);//ACDRV3
	ACDRV123_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//ACDRV3
	delay_us(wait_time);
	ACDRV123_ACM.MeasureVI(50, 5);
	ACDRV123_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//ACDRV3
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(ACDRV123_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("ACDRV3_P2P_Leak"), spec.get_high_limit("ACDRV3_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = ACDRV123_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		ACDRV3_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	cbite.SetOn(K47_ACDRV1_P2P, K48_ACDRV2_P2P, K22_SHARE1_ACDRV, K50_VAC1_P2P, K51_VAC2_P2P, K52_VAC3_P2P, K43_INT_ACM, K55_SCL_ACM, K46_INT_ACM, K44_SDA_ACM, -1);
	delay_ms(3);
	//KLV1 P2P Leakage
	KLV12_ACM.Set(FV, Vp2p, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//KLV1
	delay_us(wait_time);
	KLV12_ACM.MeasureVI(50, 5);
	KLV12_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);//KLV1
	//delay_ms(1);
	copper_trace_check_after_leakage_measure(KLV12_ACM, have_copper_trace, p2p_leakage, spec.get_low_limit("KLV1_P2P_Leak"), spec.get_high_limit("KLV1_P2P_Leak"), MEAS_NA);
	FOR_EACH_VALID_SITE(site)
	{
		//p2p_leakage[site] = KLV12_ACM.GetMeasResult(site, MIRET)*1e9;//nA
		KLV1_P2P_Leak->SetTestResult(site, 0, p2p_leakage[site]);
	}

	VBUS_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);//VBUS
	PMID_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);//PMID
	NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);//NTC
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);//AMUX
	SW_ACM.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);//SW
	KLV12_ACM.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);//KLV2
	ACDRV123_ACM.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);//ACDRV1
	VCC_ACM.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);//VDRV
	VDRV_AMP_ACM.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);//VDRV
	VBAT_ACM.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);//VBAT
	PGND_ACM.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);//PGND
	VAC123_ACM.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);//VAC1
	BTST_ACM.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);//BTST
	VBATD_ACM.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);//VBATD
	SCL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);//INT,SCL
	SDA_INT_ACM.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);//SDA

	FOVI_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	ACM_GRP.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	//VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);//VBUS
	//PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);//PMID
	//NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);//NTC
	//AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);//AMUX
	//SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//SW
	//KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//KLV2
	//ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//ACDRV1
	//VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//VDRV
	//VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//VDRV
	//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//VBAT
	//PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//PGND
	//VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//VAC1
	//BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//BTST
	//VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//VBATD
	//SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//INT,SCL
	//SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//SDA
	FOR_EACH_VALID_SITE(site)
	{
		CopperTrace->SetTestResult(site, 0, have_copper_trace[site]);
	}
	return 0;
}

DUT_API int OS_PRE(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_OS_Pre = StsGetParam(funcindex, "VBUS_OS_Pre");
    CParam *PMID_OS_Pre = StsGetParam(funcindex, "PMID_OS_Pre");
    CParam *AMUX_OS_Pre = StsGetParam(funcindex, "AMUX_OS_Pre");
    CParam *NTC_OS_Pre = StsGetParam(funcindex, "NTC_OS_Pre");
    CParam *KLV1_OS_Pre = StsGetParam(funcindex, "KLV1_OS_Pre");
    CParam *KLV2_OS_Pre = StsGetParam(funcindex, "KLV2_OS_Pre");
    CParam *ACDRV1_OS_Pre = StsGetParam(funcindex, "ACDRV1_OS_Pre");
    CParam *ACDRV2_OS_Pre = StsGetParam(funcindex, "ACDRV2_OS_Pre");
    CParam *ACDRV3_OS_Pre = StsGetParam(funcindex, "ACDRV3_OS_Pre");
    CParam *SW_OS_Pre = StsGetParam(funcindex, "SW_OS_Pre");
    CParam *VCC_OS_Pre = StsGetParam(funcindex, "VCC_OS_Pre");
    CParam *VDRV_OS_Pre = StsGetParam(funcindex, "VDRV_OS_Pre");
    CParam *VBAT_OS_Pre = StsGetParam(funcindex, "VBAT_OS_Pre");
    CParam *VAC1_OS_Pre = StsGetParam(funcindex, "VAC1_OS_Pre");
    CParam *VAC2_OS_Pre = StsGetParam(funcindex, "VAC2_OS_Pre");
    CParam *VAC3_OS_Pre = StsGetParam(funcindex, "VAC3_OS_Pre");
    CParam *PGND_OS_Pre = StsGetParam(funcindex, "PGND_OS_Pre");
    CParam *BTST_OS_Pre = StsGetParam(funcindex, "BTST_OS_Pre");
    CParam *VBATDET_OS_Pre = StsGetParam(funcindex, "VBATDET_OS_Pre");
    CParam *SCL_OS_Pre = StsGetParam(funcindex, "SCL_OS_Pre");
    CParam *SDA_OS_Pre = StsGetParam(funcindex, "SDA_OS_Pre");
    CParam *INT_OS_Pre = StsGetParam(funcindex, "INT_OS_Pre");
    CParam *VCC2VBUS_OS_Pre = StsGetParam(funcindex, "VCC2VBUS_OS_Pre");
    CParam *SW2BST_OS_Pre = StsGetParam(funcindex, "SW2BST_OS_Pre");
    CParam *SW2PMID_OS_Pre = StsGetParam(funcindex, "SW2PMID_OS_Pre");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	dcm.Disconnect("SCL");
	dcm.Disconnect("SDA");
	dcm.Disconnect("INT");
	dcm.Disconnect("NTC");
	///===================Group1 Test By FOVI=============//
	cbite.SetOn(-1);
	delay_ms(3);
	FOVI_GRP.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(100);
	FOVI_GRP.Set(FI, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(100);
	FOVI_GRP.Set(FI, -0.001, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_ms(3);
	FOVI_GRP.MeasureVI(50, 5);
	FOVI_GRP.Set(FI, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(100);
	FOVI_GRP.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(100);
	FOVI_GRP.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	FOVI_GRP.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		VBUS_OS_Pre->SetTestResult(site, 0, VBUS_FOVI.GetMeasResult(site, MVRET));
		PMID_OS_Pre->SetTestResult(site, 0, PMID_FOVI.GetMeasResult(site, MVRET));
		AMUX_OS_Pre->SetTestResult(site, 0, AMUX_FOVI.GetMeasResult(site, MVRET));
		NTC_OS_Pre->SetTestResult(site, 0, NTC_FOVI.GetMeasResult(site, MVRET));
	}
	///===================Group1 Test By ACM=============//
	cbite.SetOn(K55_SCL_ACM, K44_SDA_ACM, -1);
	delay_ms(3);
	ACM_GRP.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP.Set(FI, -0.001, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(3);
	ACM_GRP.MeasureVI(50, 5);
	ACM_GRP.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	ACM_GRP.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		KLV1_OS_Pre->SetTestResult(site, 0, KLV12_ACM.GetMeasResult(site, MVRET));
		ACDRV1_OS_Pre->SetTestResult(site, 0, ACDRV123_ACM.GetMeasResult(site, MVRET));
		SW_OS_Pre->SetTestResult(site, 0, SW_ACM.GetMeasResult(site, MVRET));
		VCC_OS_Pre->SetTestResult(site, 0, VCC_ACM.GetMeasResult(site, MVRET));
		VDRV_OS_Pre->SetTestResult(site, 0, VDRV_AMP_ACM.GetMeasResult(site, MVRET));
		VBAT_OS_Pre->SetTestResult(site, 0, VBAT_ACM.GetMeasResult(site, MVRET));
		VAC1_OS_Pre->SetTestResult(site, 0, VAC123_ACM.GetMeasResult(site, MVRET));
		PGND_OS_Pre->SetTestResult(site, 0, PGND_ACM.GetMeasResult(site, MVRET));
		BTST_OS_Pre->SetTestResult(site, 0, BTST_ACM.GetMeasResult(site, MVRET));
		VBATDET_OS_Pre->SetTestResult(site, 0, VBATD_ACM.GetMeasResult(site, MVRET));
		SCL_OS_Pre->SetTestResult(site, 0, SCL_ACM.GetMeasResult(site, MVRET));
		SDA_OS_Pre->SetTestResult(site, 0, SDA_INT_ACM.GetMeasResult(site, MVRET));
	}
	///===================Group2 Test By ACM=============//
	cbite.SetOn(K20_SHARE_KLV, K22_SHARE1_ACDRV, K35_SHARE1_VAC, K43_INT_ACM, - 1);
	delay_ms(3);
	ACM_GRP2.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP2.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP2.Set(FI, -0.001, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(3);
	ACM_GRP2.MeasureVI(50, 5);
	ACM_GRP2.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP2.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP2.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	ACM_GRP2.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		KLV2_OS_Pre->SetTestResult(site, 0, KLV12_ACM.GetMeasResult(site, MVRET));
		ACDRV3_OS_Pre->SetTestResult(site, 0, ACDRV123_ACM.GetMeasResult(site, MVRET));
		VAC3_OS_Pre->SetTestResult(site, 0, VAC123_ACM.GetMeasResult(site, MVRET));
		INT_OS_Pre->SetTestResult(site, 0, SDA_INT_ACM.GetMeasResult(site, MVRET));
	}
	///===================Group3 Test By ACM=============//
	cbite.SetOn( K23_SHARE2_ACDRV, K36_SHARE2_VAC, -1);
	delay_ms(3);
	ACM_GRP3.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP3.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP3.Set(FI, -0.001, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(3);
	ACM_GRP3.MeasureVI(50, 5);
	ACM_GRP3.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP3.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP3.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	ACM_GRP3.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		ACDRV2_OS_Pre->SetTestResult(site, 0, ACDRV123_ACM.GetMeasResult(site, MVRET));
		VAC2_OS_Pre->SetTestResult(site, 0, VAC123_ACM.GetMeasResult(site, MVRET));
	}

	//----------BST-SW Diode
	cbite.SetOn(K18_BST_SW_Cap, -1);
	delay_ms(3);
	BTST_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(500);
	BTST_ACM.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FI, -0.001, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(1);
	BTST_ACM.MeasureVI(50, 5);
	BTST_ACM.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		SW2BST_OS_Pre->SetTestResult(site, 0, BTST_ACM.GetMeasResult(site, MVRET));
	}

	//----------BST-SW Diode
	cbite.SetOn(K18_BST_SW_Cap, -1);
	delay_ms(3);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(500);
	PMID_FOVI.Set(FI, -0.001, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_ms(1);
	PMID_FOVI.MeasureVI(50, 5);
	PMID_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	PMID_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		SW2PMID_OS_Pre->SetTestResult(site, 0, PMID_FOVI.GetMeasResult(site, MVRET));
	}


	//----------VCC2VBUS
	VCC_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(500);
	VBUS_FOVI.Set(FI, -0.001, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_ms(1);
	VBUS_FOVI.MeasureVI(50, 5);
	VBUS_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		VCC2VBUS_OS_Pre->SetTestResult(site, 0, VBUS_FOVI.GetMeasResult(site, MVRET));
	}

	return 0;
}

DUT_API int ABS_Leakage(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_26V_Leak = StsGetParam(funcindex, "VBUS_26V_Leak");
    CParam *VBUS_N0P3V_Leak = StsGetParam(funcindex, "VBUS_N0P3V_Leak");
    CParam *PMID_26V_Leak = StsGetParam(funcindex, "PMID_26V_Leak");
    CParam *PMID_N0P3V_Leak = StsGetParam(funcindex, "PMID_N0P3V_Leak");
    CParam *SW_24V_Leak = StsGetParam(funcindex, "SW_24V_Leak");
    CParam *SW_N0P3V_Leak = StsGetParam(funcindex, "SW_N0P3V_Leak");
    CParam *BTST_30V_Leak = StsGetParam(funcindex, "BTST_30V_Leak");
    CParam *BTST_N0P3V_Leak = StsGetParam(funcindex, "BTST_N0P3V_Leak");
    CParam *VBAT_6V_Leak = StsGetParam(funcindex, "VBAT_6V_Leak");
    CParam *VBAT_N0P3V_Leak = StsGetParam(funcindex, "VBAT_N0P3V_Leak");
    CParam *NTC2_6V_Leak = StsGetParam(funcindex, "NTC2_6V_Leak");
    CParam *NTC2_N0P3V_Leak = StsGetParam(funcindex, "NTC2_N0P3V_Leak");
    CParam *AMUX_6V_Leak = StsGetParam(funcindex, "AMUX_6V_Leak");
    CParam *AMUX_N0P3V_Leak = StsGetParam(funcindex, "AMUX_N0P3V_Leak");
    CParam *NTC_6V_Leak = StsGetParam(funcindex, "NTC_6V_Leak");
    CParam *NTC_N0P3V_Leak = StsGetParam(funcindex, "NTC_N0P3V_Leak");
    CParam *VCC_6V_Leak = StsGetParam(funcindex, "VCC_6V_Leak");
    CParam *VCC_N0P3V_Leak = StsGetParam(funcindex, "VCC_N0P3V_Leak");
    CParam *VAC1_26V_Leak = StsGetParam(funcindex, "VAC1_26V_Leak");
    CParam *VAC1_N0P3V_Leak = StsGetParam(funcindex, "VAC1_N0P3V_Leak");
    CParam *VAC2_26V_Leak = StsGetParam(funcindex, "VAC2_26V_Leak");
    CParam *VAC2_N0P3V_Leak = StsGetParam(funcindex, "VAC2_N0P3V_Leak");
    CParam *VAC3_26V_Leak = StsGetParam(funcindex, "VAC3_26V_Leak");
    CParam *VAC3_N0P3V_Leak = StsGetParam(funcindex, "VAC3_N0P3V_Leak");
    CParam *KLV1_26V_Leak = StsGetParam(funcindex, "KLV1_26V_Leak");
    CParam *KLV1_N0P3V_Leak = StsGetParam(funcindex, "KLV1_N0P3V_Leak");
    CParam *KLV2_26V_Leak = StsGetParam(funcindex, "KLV2_26V_Leak");
    CParam *KLV2_N0P3V_Leak = StsGetParam(funcindex, "KLV2_N0P3V_Leak");
    CParam *ACDRV1_29V_Leak = StsGetParam(funcindex, "ACDRV1_29V_Leak");
    CParam *ACDRV1_N0P3V_Leak = StsGetParam(funcindex, "ACDRV1_N0P3V_Leak");
    CParam *ACDRV2_29V_Leak = StsGetParam(funcindex, "ACDRV2_29V_Leak");
    CParam *ACDRV2_N0P3V_Leak = StsGetParam(funcindex, "ACDRV2_N0P3V_Leak");
    CParam *ACDRV3_29V_Leak = StsGetParam(funcindex, "ACDRV3_29V_Leak");
    CParam *ACDRV3_N0P3V_Leak = StsGetParam(funcindex, "ACDRV3_N0P3V_Leak");
    CParam *VDRV_6V_Leak = StsGetParam(funcindex, "VDRV_6V_Leak");
    CParam *VDRV_N0P3V_Leak = StsGetParam(funcindex, "VDRV_N0P3V_Leak");
    CParam *SCL_6V_Leak = StsGetParam(funcindex, "SCL_6V_Leak");
    CParam *SCL_N0P3V_Leak = StsGetParam(funcindex, "SCL_N0P3V_Leak");
    CParam *SDA_6V_Leak = StsGetParam(funcindex, "SDA_6V_Leak");
    CParam *SDA_N0P3V_Leak = StsGetParam(funcindex, "SDA_N0P3V_Leak");
    CParam *INT_6V_Leak = StsGetParam(funcindex, "INT_6V_Leak");
    CParam *INT_N0P3V_Leak = StsGetParam(funcindex, "INT_N0P3V_Leak");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn||TEST_FLOW == QA)
	{

		double testlimit = 0; 
		double abs_high_leak[SITE_NUM] = { 0 };
		double abs_low_leak[SITE_NUM] = { 0 };
		double abs_30v = 30;
		double abs_29v = 27;
		double abs_26v = 26;
		double abs_24v = 24;
		double abs_6v = 6;
		int wait_time = 500;
		dcm.Disconnect("SCL");
		dcm.Disconnect("SDA");
		QVM_GP.Disconnect();
		QTMU_GP.Disconnect(QTMUe_RELAY_CHA);
		SW_ACM.Set(FV, 0, ACM200_40V, ACM200_200MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_200MA, ACM200_RELAY_ON);
		//================ACDRV1 ABS Leakage, 29V
		ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, abs_29v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, abs_29v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		Retest_current_unstable_with_time_out(ACDRV123_ACM, abs_high_leak, spec.get_low_limit("ACDRV1_29V_Leak"), spec.get_high_limit("ACDRV1_29V_Leak"), 1, 15, MEAS_UA);
		ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			//abs_high_leak[site] = ACDRV123_ACM.GetMeasResult(site, MIRET);//uA  498uA
			ACDRV1_29V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}
		

		//================ACDRV2 ABS Leakage, 29V
		cbite.SetOn(K23_SHARE2_ACDRV, K36_SHARE2_VAC, -1);
		delay_ms(3);
		ACDRV123_ACM.Set(FV, abs_29v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, abs_29v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		Retest_current_unstable_with_time_out(ACDRV123_ACM, abs_high_leak, spec.get_low_limit("ACDRV2_29V_Leak"), spec.get_high_limit("ACDRV2_29V_Leak"), 1, 15, MEAS_UA);
		ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			//abs_high_leak[site] = ACDRV123_ACM.GetMeasResult(site, MIRET);//uA  498uA
			ACDRV2_29V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}

		//================ACDRV3 ABS Leakage, 29V
		cbite.SetOn(K22_SHARE1_ACDRV, K35_SHARE1_VAC, -1);
		delay_ms(3);
		ACDRV123_ACM.Set(FV, abs_29v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, abs_29v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		Retest_current_unstable_with_time_out(ACDRV123_ACM, abs_high_leak, spec.get_low_limit("ACDRV3_29V_Leak"), spec.get_high_limit("ACDRV3_29V_Leak"), 1, 15, MEAS_UA);
		ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			//abs_high_leak[site] = ACDRV123_ACM.GetMeasResult(site, MIRET);//uA  498uA
			ACDRV3_29V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);


		//==================VAC3  ABS Leakage, 26V
		VAC123_ACM.Set(FV, abs_26v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, abs_26v, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
		delay_us(wait_time);
		VAC123_ACM.MeasureVI(50, 5);
		VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			abs_high_leak[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e6;//uA    348uA
			VAC3_26V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}

		//==================VAC2  ABS Leakage, 26V
		cbite.SetOn(K36_SHARE2_VAC, -1);
		delay_ms(3);
		VAC123_ACM.Set(FV, abs_26v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, abs_26v, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
		delay_us(wait_time);
		VAC123_ACM.MeasureVI(50, 5);
		VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			abs_high_leak[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e3;//uA  1.48mA
			VAC2_26V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}
		//==================VAC1 ABS Leakage, 26V
		cbite.SetOn(-1);
		delay_ms(3);
		VAC123_ACM.Set(FV, abs_26v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, abs_26v, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
		delay_us(wait_time);
		VAC123_ACM.MeasureVI(50, 5);
		VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			abs_high_leak[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e3;//mA  1.475mA
			VAC1_26V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}


		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);


		//==================KLV1  ABS Leakage, 26V
		cbite.SetOn(-1);
		delay_ms(3);
		KLV12_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		delay_ms(1);
		KLV12_ACM.Set(FV, abs_26v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		KLV12_ACM.Set(FV, abs_26v, ACM200_40V, ACM200_100UA, ACM200_RELAY_ON);
		delay_us(wait_time * 4);
		KLV12_ACM.MeasureVI(50, 5);
		KLV12_ACM.Set(FV, 0, ACM200_40V, ACM200_100UA, ACM200_RELAY_ON);
		KLV12_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			abs_high_leak[site] = KLV12_ACM.GetMeasResult(site, MIRET)*1e6;//    178uA
			KLV1_26V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}

		//==================KLV2 ABS Leakage, 26V
		cbite.SetOn(K20_SHARE_KLV, -1);
		delay_ms(3);
		KLV12_ACM.Set(FV, abs_26v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		KLV12_ACM.Set(FV, abs_26v, ACM200_40V, ACM200_100UA, ACM200_RELAY_ON);
		delay_us(wait_time * 4);
		KLV12_ACM.MeasureVI(50, 5);
		KLV12_ACM.Set(FV, 0, ACM200_40V, ACM200_100UA, ACM200_RELAY_ON);
		KLV12_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			abs_high_leak[site] = KLV12_ACM.GetMeasResult(site, MIRET)*1e6;//uA   180uA
			KLV2_26V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}


		KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

		//==================VBUS ABS Leakage, 26V
		cbite.SetOn(-1);
		delay_ms(3);
		VBUS_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, abs_26v, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		VCC_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		Retest_current_unstable_with_time_out(VBUS_FOVI, abs_high_leak, spec.get_low_limit("VBUS_26V_Leak"), spec.get_high_limit("VBUS_26V_Leak"), 1, 10, MEAS_UA);
		//delay_us(wait_time);
		//VBUS_FOVI.MeasureVI(50, 5);
		VBUS_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			//abs_high_leak[site] = VBUS_FOVI.GetMeasResult(site, MIRET)*1e6;//uA   178uA
			VBUS_26V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);

		//==================PMID ABS Leakage, 26V
		PMID_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, abs_26v, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		VCC_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		Retest_current_unstable_with_time_out(PMID_FOVI, abs_high_leak, spec.get_low_limit("PMID_26V_Leak"), spec.get_high_limit("PMID_26V_Leak"), 1, 10, MEAS_UA);
		//delay_us(wait_time);
		//PMID_FOVI.MeasureVI(50, 5);
		PMID_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			//abs_high_leak[site] = PMID_FOVI.GetMeasResult(site, MIRET)*1e6;//uA   180uA
			PMID_26V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}

		PMID_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		FPVI.Set(FV, 0, FPVIe_20V, FPVIe_10MA, FPVIe_RELAY_OFF);
		SW_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);


		//==================SW ABS Leakage, 24V
		cbite.SetOn(K18_BST_SW_Cap, -1);
		delay_ms(3);
		SW_ACM.Set(FV, 0, ACM200_40V, ACM200_10UA, ACM200_RELAY_ON);
		SW_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_OFF);

		//==================BTST ABS Leakage, 30V
		double abs_high_leak_sw[SITE_NUM] = { 0 };
		double abs_high_leak_btst[SITE_NUM] = { 0 };
		SW_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		delay_ms(1);
		VBUS_FOVI.Set(FV, 5, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		SW_ACM.Set(FV, 5, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(100);
		VBUS_FOVI.Set(FV, 10, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		SW_ACM.Set(FV, 10, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(100);
		VBUS_FOVI.Set(FV, 15, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		SW_ACM.Set(FV, 15, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(100);
		VBUS_FOVI.Set(FV, 20, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 20, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		SW_ACM.Set(FV, 20, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(100);
		VBUS_FOVI.Set(FV, 25, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 25, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		SW_ACM.Set(FV, 24, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(100);
		VBUS_FOVI.Set(FV, 26, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 29, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(100);
		BTST_ACM.Set(FV, 30, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(5000);
		BTST_ACM.Set(FV, 30, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
		delay_us(1000);
		//BTST_ACM.MeasureVI(50, 5);
		Retest_current_unstable_with_time_out(BTST_ACM, abs_high_leak_btst, spec.get_low_limit("BTST_30V_Leak"), spec.get_high_limit("BTST_30V_Leak"), 1, 10, MEAS_UA);

		BTST_ACM.Set(FV, 30, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 29, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(100);
		BTST_ACM.Set(FV, 25, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 25, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		delay_us(500);
		BTST_ACM.Set(FV, 24.5, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 24.5, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		delay_us(1500);
		SW_ACM.Set(FV, 24, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
		Retest_current_unstable_with_time_out(SW_ACM, abs_high_leak_sw, spec.get_low_limit("SW_24V_Leak"), spec.get_high_limit("SW_24V_Leak"), 1, 10, MEAS_UA);
		//delay_us(1500);
	//	SW_ACM.MeasureVI(50, 5);	
		SW_ACM.Set(FV, 24, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		SW_ACM.Set(FV, 20, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 20, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 20, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		delay_us(100);
		SW_ACM.Set(FV, 15, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 15, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		delay_us(100);
		SW_ACM.Set(FV, 10, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 10, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		delay_us(100);
		SW_ACM.Set(FV, 5, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 5, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		delay_us(100);
		SW_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		delay_us(100);
		VBUS_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_OFF);
		SW_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_OFF);
		FOR_EACH_VALID_SITE(site)
		{
			//abs_high_leak[site] = SW_ACM.GetMeasResult(site, MIRET)*1e6;//uA
			SW_24V_Leak->SetTestResult(site, 0, abs_high_leak_sw[site]);// -2uA
			//abs_high_leak[site] = BTST_ACM.GetMeasResult(site, MIRET)*1e6;//uA
			BTST_30V_Leak->SetTestResult(site, 0, abs_high_leak_btst[site]);
		}
		////-------------BTST ABS Leakage, -0.3V
		BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

		//==================VBAT ABS Leakage, 6V
		cbite.SetOn(-1);
		delay_ms(3);
		VBUS_FOVI.Set(FV, 8, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(2);
		VBAT_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		Retest_current_unstable_with_time_out(VBAT_ACM, abs_high_leak, spec.get_low_limit("VBAT_6V_Leak"), spec.get_high_limit("VBAT_6V_Leak"), 1, 15, MEAS_UA);
		VBUS_FOVI.Set(FV, 8, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			//abs_high_leak[site] = VBAT_ACM.GetMeasResult(site, MIRET);//uA   29.7uA
			VBAT_6V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}
		////-------------VBAT ABS Leakage, -0.3V
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);



		//==================VDRV ABS Leakage, 6V
		cbite.SetOn(-1);
		delay_ms(3);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(wait_time);
		VDRV_AMP_ACM.MeasureVI(50, 5);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		FOR_EACH_VALID_SITE(site)
		{
			abs_high_leak[site] = VDRV_AMP_ACM.GetMeasResult(site, MIRET)*1e6;//uA
			VDRV_6V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}

		//==================VCC ABS Leakage, 6V
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 8, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
		delay_ms(2);// delay 2ms cannot save
		Retest_current_unstable_with_time_out(VCC_ACM, abs_high_leak, spec.get_low_limit("VCC_6V_Leak"), spec.get_high_limit("VCC_6V_Leak"), 1, 50, MEAS_UA);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		FOR_EACH_VALID_SITE(site)
		{
			//abs_high_leak[site] = VCC_ACM.GetMeasResult(site, MIRET);//uA     94.8uA
			VCC_6V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}

		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);


		////-------------VDRV ABS Leakage, -0.3V
		//VDRV_AMP_ACM.Set(FV, -0.3, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		//VDRV_AMP_ACM.Set(FV, -0.3, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		//delay_us(wait_time);
		//VDRV_AMP_ACM.MeasureVI(50, 5);
		//VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		//FOR_EACH_VALID_SITE(site)
		//{
		//	abs_low_leak[site] = VDRV_AMP_ACM.GetMeasResult(site, MIRET)*1e6;//uA
		//	VDRV_N0P3V_Leak->SetTestResult(site, 0, abs_low_leak[site]);
		//}
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);


		//==================AMUX , NTC, INT  ABS Leakage, 6V
		cbite.SetOn(K43_INT_ACM, -1);
		delay_ms(3);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, abs_6v, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, abs_6v, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(wait_time * 5);
		AMUX_FOVI.Set(FV, abs_6v, FOVIe_10V, FOVIe_100UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, abs_6v, FOVIe_10V, FOVIe_100UA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		delay_us(wait_time*10);
		AMUX_FOVI.MeasureVI(50, 5);
		NTC_FOVI.MeasureVI(50, 5);
		SDA_INT_ACM.MeasureVI(50, 5);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100UA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);

		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		FOR_EACH_VALID_SITE(site)
		{
			abs_high_leak[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
			AMUX_6V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
			abs_high_leak[site] = NTC_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
			NTC_6V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
			abs_high_leak[site] = SDA_INT_ACM.GetMeasResult(site, MIRET)*1e6;//uA
			INT_6V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}

		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_1MA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_1MA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
		delay_ms(1);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);


		//==================NTC2, SCL, SDA ABS Leakage, 6V
		cbite.SetOn(/*K43_INT_ACM,*/ K44_SDA_ACM, K55_SCL_ACM, -1);
		delay_ms(3);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(wait_time);
		VBATD_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		SCL_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(wait_time);
		VBATD_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		SCL_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, abs_6v, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		delay_us(wait_time);
		SCL_ACM.MeasureVI(50, 5);
		SDA_INT_ACM.MeasureVI(50, 5);
		VBATD_ACM.MeasureVI(50, 10);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);

		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		FOR_EACH_VALID_SITE(site)
		{
			abs_high_leak[site] = VBATD_ACM.GetMeasResult(site, MIRET)*1e6;//uA
			NTC2_6V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
			abs_high_leak[site] = SCL_ACM.GetMeasResult(site, MIRET)*1e6;//uA
			SCL_6V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
			abs_high_leak[site] = SDA_INT_ACM.GetMeasResult(site, MIRET)*1e6;//uA
			SDA_6V_Leak->SetTestResult(site, 0, abs_high_leak[site]);
		}

		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
		SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);

		delay_ms(1);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}

	return 0;
}
 
DUT_API int OTP_Read_Pre(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBG_PreRd = StsGetParam(funcindex, "VBG_PreRd");
    CParam *BG_RES_DIV_PreRd = StsGetParam(funcindex, "BG_RES_DIV_PreRd");
    CParam *V1P2_BUF_PreRd = StsGetParam(funcindex, "V1P2_BUF_PreRd");
    CParam *DAC_BUF_PreRd = StsGetParam(funcindex, "DAC_BUF_PreRd");
    CParam *IZTC_RES_PreRd = StsGetParam(funcindex, "IZTC_RES_PreRd");
    CParam *OSC_4P5M_PreRd = StsGetParam(funcindex, "OSC_4P5M_PreRd");
    CParam *VBAT_RSNS_LOOP_PreRd = StsGetParam(funcindex, "VBAT_RSNS_LOOP_PreRd");
    CParam *AMUX_EA_OS_PreRd = StsGetParam(funcindex, "AMUX_EA_OS_PreRd");
    CParam *IBUS_SNS_GAIN_PreRd = StsGetParam(funcindex, "IBUS_SNS_GAIN_PreRd");
    CParam *IBUS_SNS_EA_OS_PreRd = StsGetParam(funcindex, "IBUS_SNS_EA_OS_PreRd");
    CParam *BUCK_RCS_PreRd = StsGetParam(funcindex, "BUCK_RCS_PreRd");
    CParam *BOOST_RCS_PreRd = StsGetParam(funcindex, "BOOST_RCS_PreRd");
    CParam *CS_HS_OS_PreRd = StsGetParam(funcindex, "CS_HS_OS_PreRd");
    CParam *CS_LS_OS_PreRd = StsGetParam(funcindex, "CS_LS_OS_PreRd");
    CParam *BUCK_HS_GAIN_PreRd = StsGetParam(funcindex, "BUCK_HS_GAIN_PreRd");
    CParam *BUCK_HS_OS_PreRd = StsGetParam(funcindex, "BUCK_HS_OS_PreRd");
    CParam *BOOST_HS_GAIN_PreRd = StsGetParam(funcindex, "BOOST_HS_GAIN_PreRd");
    CParam *BOOST_HS_OS_PreRd = StsGetParam(funcindex, "BOOST_HS_OS_PreRd");
    CParam *BUCK_LS_GAIN_PreRd = StsGetParam(funcindex, "BUCK_LS_GAIN_PreRd");
    CParam *BUCK_LS_OS_PreRd = StsGetParam(funcindex, "BUCK_LS_OS_PreRd");
    CParam *BOOST_LS_GAIN_PreRd = StsGetParam(funcindex, "BOOST_LS_GAIN_PreRd");
    CParam *BOOST_LS_OS_PreRd = StsGetParam(funcindex, "BOOST_LS_OS_PreRd");
    CParam *IBUS_LOOP_OS_PreRd = StsGetParam(funcindex, "IBUS_LOOP_OS_PreRd");
    CParam *BUCK_VBUS_EA_OS_PreRd = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_PreRd");
    CParam *BOOST_VBUS_EA_OS_PreRd = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_PreRd");
    CParam *VBAT_CV_BUF_PreRd = StsGetParam(funcindex, "VBAT_CV_BUF_PreRd");
    CParam *IBAT_CC_LOOP_PreRd = StsGetParam(funcindex, "IBAT_CC_LOOP_PreRd");
    CParam *IBUS_OFF_TERM_FLT_PreRd = StsGetParam(funcindex, "IBUS_OFF_TERM_FLT_PreRd");
    CParam *ADDR_TRIM_PreRd = StsGetParam(funcindex, "ADDR_TRIM_PreRd");
    CParam *PART_ID_TRIM_PreRd = StsGetParam(funcindex, "PART_ID_TRIM_PreRd");
    CParam *PART_ID_TRIM_6802_PreRd = StsGetParam(funcindex, "PART_ID_TRIM_6802_PreRd");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	DOUBLE BG_PRE_CODE[SITE_NUM] = { 0 }; //1
	DOUBLE BG_RES_DIV_PRE_CODE[SITE_NUM] = { 0 };//2
	DOUBLE IZTC_PRE_CODE[SITE_NUM] = { 0 };// 3	
	DOUBLE OSC_4P5M_PRE_CODE[SITE_NUM] = { 0 };//4
	DOUBLE DAC_BUF_OS_PRE_CODE[SITE_NUM] = { 0 };// 6
	DOUBLE V1P2_BUF_OS_PRE_CODE[SITE_NUM] = { 0 };//8
	DOUBLE VBAT_SNS_LOOP_PRE_CODE[SITE_NUM] = { 0 };//18
	DOUBLE AMUX_EA_OS_PRE_CODE[SITE_NUM] = { 0 };// 7
	DOUBLE IBUS_SNS_GAIN__PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE IBUS_SNS_EA_OS__PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE BUCK_RCS_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE BOOST_RCS_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE CS_HS_OS_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE CS_LS_OS_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE BUCK_HS_GAIN_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE BUCK_HS_OS_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE BOOST_HS_GAIN_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE BOOST_HS_OS_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE BUCK_LS_GAIN_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE BUCK_LS_OS_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE BOOST_LS_GAIN_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE BOOST_LS_OS_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE IBUS_LOOP_OS_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE BUCK_VBUS_EA_OS_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE BOOST_VBUS_EA_OS_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE VBAT_CV_BUF_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE IBAT_CC_LOOP_PRE_CODE[SITE_NUM] = { 0 };
	//--------OPT_CODE
	DOUBLE IBUS_OFF_TERM_FLT_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE ADDR_TRIM_PRE_CODE[SITE_NUM] = { 0 };
	DOUBLE PART_ID_TRIM_PRE_CODE[SITE_NUM] = { 0 };


	ULONG REG_F0_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_F1_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_F2_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_F3_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_F4_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_F5_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_F6_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_F7_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_F8_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_F9_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_FA_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_FB_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_FC_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_FD_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_FE_PRE_READ[SITE_NUM] = { 0 };
	ULONG REG_FF_PRE_READ[SITE_NUM] = { 0 };

	DWORD working_value2[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_FF").get_working(site);
	}
	//-------------------------------OTP READ FUNCTION--------------------------//
	dcm.I2CConnect();
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K57_SDA_PU, K53_SCL_PU, K25_VCC_Cap,-1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//VBAT
	VCC_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//VBAT
	entertestmode();
	I2C_READ_BYTE(DEV_ADDR, 0xF0, REG_F0_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF1, REG_F1_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF2, REG_F2_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF3, REG_F3_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF4, REG_F4_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF5, REG_F5_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF6, REG_F6_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF7, REG_F7_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF8, REG_F8_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF9, REG_F9_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xFA, REG_FA_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xFB, REG_FB_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xFC, REG_FC_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xFD, REG_FD_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xFE, REG_FE_PRE_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xFF, REG_FF_PRE_READ);


	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//VBAT
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//VBAT
	delay_ms(1);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//VBAT
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//VBAT

	//-------------Read all register and set into readback
	FOR_EACH_VALID_SITE(site)
	{

		trim_reg.assy("EFUSE_REG_F0").set_read_back((INT)REG_F0_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_F1").set_read_back((INT)REG_F1_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_F2").set_read_back((INT)REG_F2_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_F3").set_read_back((INT)REG_F3_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_F4").set_read_back((INT)REG_F4_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_F5").set_read_back((INT)REG_F5_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_F6").set_read_back((INT)REG_F6_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_F7").set_read_back((INT)REG_F7_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_F8").set_read_back((INT)REG_F8_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_F9").set_read_back((INT)REG_F9_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_FA").set_read_back((INT)REG_FA_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_FB").set_read_back((INT)REG_FB_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_FC").set_read_back((INT)REG_FC_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_FD").set_read_back((INT)REG_FD_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_FE").set_read_back((INT)REG_FE_PRE_READ[site], site);
		trim_reg.assy("EFUSE_REG_FF").set_read_back((INT)REG_FF_PRE_READ[site], site);

	}

	INT64 a = 0;

	FOR_EACH_VALID_SITE(site)
	{
		
		//trim_reg.assy("EFUSE_REG_REGISTER").copy_read_to_work(site);// make sure all read value set in work
		if (trim_reg.assy("EFUSE_REG_REGISTER").comp_read(a, site))
		{
			BURN_FLAG[site] = FRESH; // Means device of this site is Fresh
		}
		else
		{
			BURN_FLAG[site] = BURNNED;// Means device of this site have been burned
			trim_reg.assy("EFUSE_REG_REGISTER").copy_read_to_work(site);// make sure all read value set in work
		}
	}


	FOR_EACH_VALID_SITE(site)
	{
		BG_PRE_CODE[site] = trim_reg.trim("bandgap").get_read_back(site);//check,1
		BG_RES_DIV_PRE_CODE[site] = trim_reg.trim("bg_res_div").get_read_back(site);//check,2
		IZTC_PRE_CODE[site] = trim_reg.trim("iztc_res").get_read_back(site);//check,3
		OSC_4P5M_PRE_CODE[site] = trim_reg.trim("osc_4p5m").get_read_back(site);//check,4
		DAC_BUF_OS_PRE_CODE[site] = trim_reg.trim("mnt_dac_buf_os").get_read_back(site);//check,6	
		V1P2_BUF_OS_PRE_CODE[site] = trim_reg.trim("mnt_v1p2_buf").get_read_back(site);//check,7
		VBAT_SNS_LOOP_PRE_CODE[site] = trim_reg.trim("mnt_vbat_rsns_loop").get_read_back(site);//check,8
		AMUX_EA_OS_PRE_CODE[site] = trim_reg.trim("amux_ea_os").get_read_back(site);//check,9
		IBUS_SNS_GAIN__PRE_CODE[site] = trim_reg.trim("ibus_sns_gain").get_read_back(site);//check,10
		IBUS_SNS_EA_OS__PRE_CODE[site] = trim_reg.trim("ibus_sns_ea_os").get_read_back(site);//check,11
		BUCK_RCS_PRE_CODE[site] = trim_reg.trim("buck_rcs").get_read_back(site);//check,12
		BOOST_RCS_PRE_CODE[site] = trim_reg.trim("boost_rcs").get_read_back(site);//check,13
		CS_HS_OS_PRE_CODE[site] = trim_reg.trim("cs_hsfet_os").get_read_back(site);//check,14	
		CS_LS_OS_PRE_CODE[site] = trim_reg.trim("cs_lsfet_os").get_read_back(site);//check,15
		BUCK_HS_GAIN_PRE_CODE[site] = trim_reg.trim("buck_hsfet_gain").get_read_back(site);//check,16
		BUCK_HS_OS_PRE_CODE[site] = trim_reg.trim("buck_hsfet_os").get_read_back(site);//check,17
		BOOST_HS_GAIN_PRE_CODE[site] = trim_reg.trim("boost_hsfet_gain").get_read_back(site);//check,18
		BOOST_HS_OS_PRE_CODE[site] = trim_reg.trim("boost_hsfet_os").get_read_back(site);//check,19
		BUCK_LS_GAIN_PRE_CODE[site] = trim_reg.trim("buck_lsfet_gain").get_read_back(site);//check,20
		BUCK_LS_OS_PRE_CODE[site] = trim_reg.trim("buck_lsfet_os").get_read_back(site);//check,21
		BOOST_LS_GAIN_PRE_CODE[site] = trim_reg.trim("boost_lsfet_gain").get_read_back(site);//check,22
		BOOST_LS_OS_PRE_CODE[site] = trim_reg.trim("boost_lsfet_os").get_read_back(site);//check,23
		IBUS_LOOP_OS_PRE_CODE[site] = trim_reg.trim("ibus_loop_os").get_read_back(site);//check,24
		BUCK_VBUS_EA_OS_PRE_CODE[site] = trim_reg.trim("mnt_vbus_ea_os_buck").get_read_back(site);//check,25
		BOOST_VBUS_EA_OS_PRE_CODE[site] = trim_reg.trim("mnt_vbus_ea_os_boost").get_read_back(site);//check,26
		VBAT_CV_BUF_PRE_CODE[site] = trim_reg.trim("mnt_vbat_cv_buf").get_read_back(site);//check,27
		IBAT_CC_LOOP_PRE_CODE[site] = trim_reg.trim("ibat_cc_loop").get_read_back(site);//check,28
		IBUS_OFF_TERM_FLT_PRE_CODE[site] = trim_reg.sel("ibus_off_term_flt").get_read_back(site);//check,29
		ADDR_TRIM_PRE_CODE[site] = trim_reg.sel("addr_trim").get_read_back(site);//check,30
		PART_ID_TRIM_PRE_CODE[site] = trim_reg.sel("part_id_trim").get_read_back(site);//check,31
	}

	FOR_EACH_VALID_SITE(site)
	{
		VBG_PreRd->SetTestResult(site, 0, BG_PRE_CODE[site]);//
		BG_RES_DIV_PreRd->SetTestResult(site, 0, BG_RES_DIV_PRE_CODE[site]);//
		V1P2_BUF_PreRd->SetTestResult(site, 0, V1P2_BUF_OS_PRE_CODE[site]);//
		DAC_BUF_PreRd->SetTestResult(site, 0, DAC_BUF_OS_PRE_CODE[site]);//
		IZTC_RES_PreRd->SetTestResult(site, 0, IZTC_PRE_CODE[site]);//
		OSC_4P5M_PreRd->SetTestResult(site, 0, OSC_4P5M_PRE_CODE[site]);//
		VBAT_RSNS_LOOP_PreRd->SetTestResult(site, 0, VBAT_SNS_LOOP_PRE_CODE[site]);//
		AMUX_EA_OS_PreRd->SetTestResult(site, 0, AMUX_EA_OS_PRE_CODE[site]);//
		IBUS_SNS_GAIN_PreRd->SetTestResult(site, 0, IBUS_SNS_GAIN__PRE_CODE[site]);//
		IBUS_SNS_EA_OS_PreRd->SetTestResult(site, 0, IBUS_SNS_EA_OS__PRE_CODE[site]);//
		BUCK_RCS_PreRd->SetTestResult(site, 0, BUCK_RCS_PRE_CODE[site]);//
		BOOST_RCS_PreRd->SetTestResult(site, 0, BOOST_RCS_PRE_CODE[site]);//
		CS_HS_OS_PreRd->SetTestResult(site, 0, CS_HS_OS_PRE_CODE[site]);//
		CS_LS_OS_PreRd->SetTestResult(site, 0, CS_LS_OS_PRE_CODE[site]);//
		BUCK_HS_GAIN_PreRd->SetTestResult(site, 0, BUCK_HS_GAIN_PRE_CODE[site]);//
		BUCK_HS_OS_PreRd->SetTestResult(site, 0, BUCK_HS_OS_PRE_CODE[site]);//
		BOOST_HS_GAIN_PreRd->SetTestResult(site, 0, BOOST_HS_GAIN_PRE_CODE[site]);//
		BOOST_HS_OS_PreRd->SetTestResult(site, 0, BOOST_HS_OS_PRE_CODE[site]);//
		BUCK_LS_GAIN_PreRd->SetTestResult(site, 0, BUCK_LS_GAIN_PRE_CODE[site]);//
		BUCK_LS_OS_PreRd->SetTestResult(site, 0, BUCK_LS_OS_PRE_CODE[site]);//
		BOOST_LS_GAIN_PreRd->SetTestResult(site, 0, BOOST_LS_GAIN_PRE_CODE[site]);//
		BOOST_LS_OS_PreRd->SetTestResult(site, 0, BOOST_LS_OS_PRE_CODE[site]);//
		IBUS_LOOP_OS_PreRd->SetTestResult(site, 0, IBUS_LOOP_OS_PRE_CODE[site]);//
		BUCK_VBUS_EA_OS_PreRd->SetTestResult(site, 0, BUCK_VBUS_EA_OS_PRE_CODE[site]);//
		BOOST_VBUS_EA_OS_PreRd->SetTestResult(site, 0, BOOST_VBUS_EA_OS_PRE_CODE[site]);//
		VBAT_CV_BUF_PreRd->SetTestResult(site, 0, VBAT_CV_BUF_PRE_CODE[site]);//
		IBAT_CC_LOOP_PreRd->SetTestResult(site, 0, IBAT_CC_LOOP_PRE_CODE[site]);//
		IBUS_OFF_TERM_FLT_PreRd->SetTestResult(site, 0, IBUS_OFF_TERM_FLT_PRE_CODE[site]);//
		ADDR_TRIM_PreRd->SetTestResult(site, 0, ADDR_TRIM_PRE_CODE[site]);////chenyang
		if (extractIntFromString(DEVICE_SEL) == 6801 || extractIntFromString(DEVICE_SEL) == 6803)
		{
			PART_ID_TRIM_PreRd->SetTestResult(site, 0, PART_ID_TRIM_PRE_CODE[site]);//
		}
		if (extractIntFromString(DEVICE_SEL) == 6802)
		{
			PART_ID_TRIM_6802_PreRd->SetTestResult(site, 0, PART_ID_TRIM_PRE_CODE[site]);//
		}
	}
	return 0;
}

DUT_API int Trim_VBG(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BG_AVSS = StsGetParam(funcindex, "BG_AVSS");
    CParam *VBG_step0 = StsGetParam(funcindex, "VBG_step0");
    CParam *VBG_step1 = StsGetParam(funcindex, "VBG_step1");
    CParam *VBG_step2 = StsGetParam(funcindex, "VBG_step2");
    CParam *VBG_step3 = StsGetParam(funcindex, "VBG_step3");
    CParam *VBG_step4 = StsGetParam(funcindex, "VBG_step4");
    CParam *VBG_step5 = StsGetParam(funcindex, "VBG_step5");
    CParam *VBG_step6 = StsGetParam(funcindex, "VBG_step6");
    CParam *VBG_step7 = StsGetParam(funcindex, "VBG_step7");
    CParam *VBG_step8 = StsGetParam(funcindex, "VBG_step8");
    CParam *VBG_step9 = StsGetParam(funcindex, "VBG_step9");
    CParam *VBG_step10 = StsGetParam(funcindex, "VBG_step10");
    CParam *VBG_step11 = StsGetParam(funcindex, "VBG_step11");
    CParam *VBG_step12 = StsGetParam(funcindex, "VBG_step12");
    CParam *VBG_step13 = StsGetParam(funcindex, "VBG_step13");
    CParam *VBG_step14 = StsGetParam(funcindex, "VBG_step14");
    CParam *VBG_step15 = StsGetParam(funcindex, "VBG_step15");
    CParam *VBG_pre_value = StsGetParam(funcindex, "VBG_pre_value");
    CParam *VBG_pre_bit = StsGetParam(funcindex, "VBG_pre_bit");
    CParam *VBG_post_bit = StsGetParam(funcindex, "VBG_post_bit");
    CParam *VBG_updated = StsGetParam(funcindex, "VBG_updated");
    CParam *VBG_guessed = StsGetParam(funcindex, "VBG_guessed");
    CParam *VBG_target = StsGetParam(funcindex, "VBG_target");
    CParam *VBG_post_value = StsGetParam(funcindex, "VBG_post_value");
    CParam *VBG_post_rt = StsGetParam(funcindex, "VBG_post_rt");
    CParam *VBG_Filter = StsGetParam(funcindex, "VBG_Filter");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double avss_bandgap[SITE_NUM] = { 0 };
	QVM_GP.Connect();
	dcm.I2CConnect();
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(2);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap,K25_VCC_Cap, -1);
	delay_ms(5);
	//AMUX_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(5);
	entertestmode();
	//------------------------AVSS Measurement-------------//
	I2CWriteSameData(DEV_ADDR, 0x56, 0x5A);
	I2CWriteSameData(DEV_ADDR, 0x67, 0x0A);
	I2CWriteSameData(DEV_ADDR, 0x68, 0x30);
	//		field[(EN_ATEST0,1),(ATEST0_MUX,11),(D2A_OVRD_SEL,10),(OVRD_VALUE,3)]
	delay_ms(5);
	AMUX_FOVI.MeasureVI(50, 5);
	SetTrimGroup(0x5555);
	GRP_CNT = 1;
	QVM_GP.MeasureLADC(100, 5, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
	QVM_GP_MEASURE(avss_bandgap, GRP_CNT);

	SetTrimGroup(0xAAAA);
	GRP_CNT = 2;
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap,K25_VCC_Cap ,K2_QVM_SITE_SEL, -1);// connect QVM group 2// QVM connect PC2
	delay_ms(3);
	QVM_GP.MeasureLADC(100, 5, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
	QVM_GP_MEASURE(avss_bandgap, GRP_CNT);
	SetRecoverSite();
	FOR_EACH_VALID_SITE(site)
	{
		BG_AVSS->SetTestResult(site, 0, avss_bandgap[site]*1e3);//mV
	}


	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap, -1);
	delay_ms(3);
	//------Bandgap
	I2CWriteSameData(DEV_ADDR, 0x56, 0x62);
	I2CWriteSameData(DEV_ADDR, 0x67, 0x0A);
	I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(EN_ATEST0,1),(ATEST0_MUX,12),(D2A_OVRD_SEL,10),(OVRD_VALUE,3)]
	delay_ms(2);
	TRIM_NODE &VBG = trim_reg.trim("bandgap");
	//================================第1组
	I2C_READ_BYTE(DEV_ADDR, 0xF0, data_read);
	SetTrimGroup(0x5555);
	I2C_READ_BYTE(DEV_ADDR, 0xF0, data_read);
	GRP_CNT = 1;
	VBG.execute(measure_bandgap, spec, funcindex, funclabel, 1, 0, 0, GRP_CNT);
	//================================第2组
	SetTrimGroup(0xAAAA);
	I2C_READ_BYTE(DEV_ADDR, 0xF0, data_read);
	GRP_CNT = 2;
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap,K25_VCC_Cap ,K2_QVM_SITE_SEL,-1);// connect QVM group 2// QVM connect PC2
	delay_ms(3);
	VBG.execute(measure_bandgap, spec, funcindex, funclabel, 1, 0, 0, GRP_CNT);
	SetRecoverSite();
	I2C_READ_BYTE(DEV_ADDR, 0xF0, data_read);
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		cbite.SetOn(K1_PGND2AGND, -1);
		delay_ms(3);
	}
	FOR_EACH_VALID_SITE(site)
	{
		if (extractIntFromString(DEVICE_SEL) == 6803 && VBG.get_working(site) < 10)
		{
			VBG_Filter->SetTestResult(site, 0, 0);// trim code between 1-9 need to be filter out
		}
		else
		{
			VBG_Filter->SetTestResult(site, 0, 1);// trim code =0 or trim code between 10-15, will treat as pass
		}
	}

    return 0;
}
 
DUT_API int Trim_BG_RES_DIV(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BG_RES_DIV_step0 = StsGetParam(funcindex, "BG_RES_DIV_step0");
    CParam *BG_RES_DIV_step1 = StsGetParam(funcindex, "BG_RES_DIV_step1");
    CParam *BG_RES_DIV_step2 = StsGetParam(funcindex, "BG_RES_DIV_step2");
    CParam *BG_RES_DIV_step3 = StsGetParam(funcindex, "BG_RES_DIV_step3");
    CParam *BG_RES_DIV_step4 = StsGetParam(funcindex, "BG_RES_DIV_step4");
    CParam *BG_RES_DIV_step5 = StsGetParam(funcindex, "BG_RES_DIV_step5");
    CParam *BG_RES_DIV_step6 = StsGetParam(funcindex, "BG_RES_DIV_step6");
    CParam *BG_RES_DIV_step7 = StsGetParam(funcindex, "BG_RES_DIV_step7");
    CParam *BG_RES_DIV_pre_value = StsGetParam(funcindex, "BG_RES_DIV_pre_value");
    CParam *BG_RES_DIV_pre_bit = StsGetParam(funcindex, "BG_RES_DIV_pre_bit");
    CParam *BG_RES_DIV_post_bit = StsGetParam(funcindex, "BG_RES_DIV_post_bit");
    CParam *BG_RES_DIV_updated = StsGetParam(funcindex, "BG_RES_DIV_updated");
    CParam *BG_RES_DIV_guessed = StsGetParam(funcindex, "BG_RES_DIV_guessed");
    CParam *BG_RES_DIV_target = StsGetParam(funcindex, "BG_RES_DIV_target");
    CParam *BG_RES_DIV_post_value = StsGetParam(funcindex, "BG_RES_DIV_post_value");
    CParam *BG_RES_DIV_post_rt = StsGetParam(funcindex, "BG_RES_DIV_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap,-1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x56, 0x52);
		I2CWriteSameData(DEV_ADDR, 0x67, 0x0A);
		I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(EN_ATEST0,1),(ATEST0_MUX,10),(D2A_OVRD_SEL,10),(OVRD_VALUE,3)]
		delay_ms(2);
		TRIM_NODE &BG_RES_DIV = trim_reg.trim("bg_res_div");
		//================================第1组
		SetTrimGroup(0x5555);
		GRP_CNT = 1;
		BG_RES_DIV.execute(measure_bg_res_div, spec, funcindex, funclabel, 1, 0, 1, GRP_CNT);
		//================================第2组
		SetTrimGroup(0xAAAA);
		GRP_CNT = 2;
		cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap, K2_QVM_SITE_SEL, -1);// connect QVM group 2// QVM connect PC2
		delay_ms(3);
		BG_RES_DIV.execute(measure_bg_res_div, spec, funcindex, funclabel, 1, 0, 1, GRP_CNT);
		SetRecoverSite();
		QVM_GP.Disconnect();
	}
	else
	{
		cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x52);
		I2CWriteSameData(DEV_ADDR, 0x67, 0x0A);
		I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(EN_ATEST0,1),(ATEST0_MUX,10),(D2A_OVRD_SEL,10),(OVRD_VALUE,3)]
		I2C_READ_BYTE(DEV_ADDR, 0xf0, data_read);
		delay_ms(2);
		TRIM_NODE &BG_RES_DIV = trim_reg.trim("bg_res_div");
		//================================第1组
		SetTrimGroup(0x5555);
		GRP_CNT = 1;
		BG_RES_DIV.execute(measure_bg_res_div, spec, funcindex, funclabel, 1, 0, 0, GRP_CNT);
		//================================第2组
		SetTrimGroup(0xAAAA);
		GRP_CNT = 2;
		cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap, K2_QVM_SITE_SEL, -1);// connect QVM group 2// QVM connect PC2
		delay_ms(3);
		BG_RES_DIV.execute(measure_bg_res_div, spec, funcindex, funclabel, 1, 0, 0, GRP_CNT);
		SetRecoverSite();
		QVM_GP.Disconnect();
	}


	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		cbite.SetOn(K1_PGND2AGND, -1);
		delay_ms(3);
	}
    return 0;
}
 
DUT_API int Trim_DAC_BUF(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *DAC_BUF_step0 = StsGetParam(funcindex, "DAC_BUF_step0");
    CParam *DAC_BUF_step1 = StsGetParam(funcindex, "DAC_BUF_step1");
    CParam *DAC_BUF_step2 = StsGetParam(funcindex, "DAC_BUF_step2");
    CParam *DAC_BUF_step3 = StsGetParam(funcindex, "DAC_BUF_step3");
    CParam *DAC_BUF_step4 = StsGetParam(funcindex, "DAC_BUF_step4");
    CParam *DAC_BUF_step5 = StsGetParam(funcindex, "DAC_BUF_step5");
    CParam *DAC_BUF_step6 = StsGetParam(funcindex, "DAC_BUF_step6");
    CParam *DAC_BUF_step7 = StsGetParam(funcindex, "DAC_BUF_step7");
    CParam *DAC_BUF_step8 = StsGetParam(funcindex, "DAC_BUF_step8");
    CParam *DAC_BUF_step9 = StsGetParam(funcindex, "DAC_BUF_step9");
    CParam *DAC_BUF_step10 = StsGetParam(funcindex, "DAC_BUF_step10");
    CParam *DAC_BUF_step11 = StsGetParam(funcindex, "DAC_BUF_step11");
    CParam *DAC_BUF_step12 = StsGetParam(funcindex, "DAC_BUF_step12");
    CParam *DAC_BUF_step13 = StsGetParam(funcindex, "DAC_BUF_step13");
    CParam *DAC_BUF_step14 = StsGetParam(funcindex, "DAC_BUF_step14");
    CParam *DAC_BUF_step15 = StsGetParam(funcindex, "DAC_BUF_step15");
    CParam *DAC_BUF_step16 = StsGetParam(funcindex, "DAC_BUF_step16");
    CParam *DAC_BUF_step17 = StsGetParam(funcindex, "DAC_BUF_step17");
    CParam *DAC_BUF_step18 = StsGetParam(funcindex, "DAC_BUF_step18");
    CParam *DAC_BUF_step19 = StsGetParam(funcindex, "DAC_BUF_step19");
    CParam *DAC_BUF_step20 = StsGetParam(funcindex, "DAC_BUF_step20");
    CParam *DAC_BUF_step21 = StsGetParam(funcindex, "DAC_BUF_step21");
    CParam *DAC_BUF_step22 = StsGetParam(funcindex, "DAC_BUF_step22");
    CParam *DAC_BUF_step23 = StsGetParam(funcindex, "DAC_BUF_step23");
    CParam *DAC_BUF_step24 = StsGetParam(funcindex, "DAC_BUF_step24");
    CParam *DAC_BUF_step25 = StsGetParam(funcindex, "DAC_BUF_step25");
    CParam *DAC_BUF_step26 = StsGetParam(funcindex, "DAC_BUF_step26");
    CParam *DAC_BUF_step27 = StsGetParam(funcindex, "DAC_BUF_step27");
    CParam *DAC_BUF_step28 = StsGetParam(funcindex, "DAC_BUF_step28");
    CParam *DAC_BUF_step29 = StsGetParam(funcindex, "DAC_BUF_step29");
    CParam *DAC_BUF_step30 = StsGetParam(funcindex, "DAC_BUF_step30");
    CParam *DAC_BUF_step31 = StsGetParam(funcindex, "DAC_BUF_step31");
    CParam *DAC_BUF_pre_value = StsGetParam(funcindex, "DAC_BUF_pre_value");
    CParam *DAC_BUF_pre_bit = StsGetParam(funcindex, "DAC_BUF_pre_bit");
    CParam *DAC_BUF_post_bit = StsGetParam(funcindex, "DAC_BUF_post_bit");
    CParam *DAC_BUF_updated = StsGetParam(funcindex, "DAC_BUF_updated");
    CParam *DAC_BUF_guessed = StsGetParam(funcindex, "DAC_BUF_guessed");
    CParam *DAC_BUF_target = StsGetParam(funcindex, "DAC_BUF_target");
    CParam *DAC_BUF_post_value = StsGetParam(funcindex, "DAC_BUF_post_value");
    CParam *DAC_BUF_post_rt = StsGetParam(funcindex, "DAC_BUF_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 1.68, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x9A);
		//		field[(WAKE_UP,1),(EN_ATEST0,1),(ATEST0_MUX,19)]
		Inherit_register();
		delay_ms(2);
	}
	else
	{	
		//QVM_GP.Connect();
		//AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		//cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap, -1);
		//delay_ms(3);
		//I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		//I2CWriteSameData(DEV_ADDR, 0x56, 0x9A);
		//delay_ms(2);
		//TRIM_NODE &MNT_DAC_BUF_OS = trim_reg.trim("mnt_dac_buf_os");
		////================================第1组
		//SetTrimGroup(0x5555);
		//GRP_CNT = 1;
		//MNT_DAC_BUF_OS.execute(measure_mnt_dac_buf_os, spec, funcindex, funclabel, 1, 0, 0, GRP_CNT);
		////================================第2组
		//SetTrimGroup(0xAAAA);
		//GRP_CNT = 2;
		//cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap, K2_QVM_SITE_SEL, -1);// connect QVM group 2// QVM connect PC2
		//delay_ms(3);
		//MNT_DAC_BUF_OS.execute(measure_mnt_dac_buf_os, spec, funcindex, funclabel, 1, 0, 0, GRP_CNT);
		//SetRecoverSite();
		//QVM_GP.Disconnect();



		cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap,-1);
		delay_ms(3);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x9A);
		delay_ms(1);
		//AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		//AMUX_FOVI.MeasureVI(50, 5);
	}
	AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(5);
	TRIM_NODE &MNT_DAC_BUF_OS = trim_reg.trim("mnt_dac_buf_os");
	MNT_DAC_BUF_OS.execute(measure_mnt_dac_buf_os, spec, funcindex, funclabel, 1, 0, 0, 0);
	//Retry_trim_search(&MNT_DAC_BUF_OS, measure_mnt_dac_buf_os, spec, funcindex, funclabel, 1.0, -1, -1, 1.0, false, 1.0);
	////================================第1组
	//SetTrimGroup(0x00FF);
	//GRP_CNT = 1;
	//MNT_DAC_BUF_OS.execute(measure_mnt_dac_buf_os, spec, funcindex, funclabel, 1, 0, 0, GRP_CNT);
	////================================第2组
	//SetTrimGroup(0xFF00);
	//GRP_CNT = 2;
	//cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K2_QVM_SITE_SEL, -1);// connect QVM group 2// QVM connect PC2
	//delay_ms(3);
	//MNT_DAC_BUF_OS.execute(measure_mnt_dac_buf_os, spec, funcindex, funclabel, 1, 0, 0, GRP_CNT);
	//SetRecoverSite();
	//QVM_GP.Disconnect();

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		cbite.SetOn(K1_PGND2AGND, -1);
		delay_ms(3);
	}
	else
	{
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}



    return 0;
}
 
DUT_API int Trim_V1P2_BUF(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *V1P2_BUF_step0 = StsGetParam(funcindex, "V1P2_BUF_step0");
    CParam *V1P2_BUF_step1 = StsGetParam(funcindex, "V1P2_BUF_step1");
    CParam *V1P2_BUF_step2 = StsGetParam(funcindex, "V1P2_BUF_step2");
    CParam *V1P2_BUF_step3 = StsGetParam(funcindex, "V1P2_BUF_step3");
    CParam *V1P2_BUF_step4 = StsGetParam(funcindex, "V1P2_BUF_step4");
    CParam *V1P2_BUF_step5 = StsGetParam(funcindex, "V1P2_BUF_step5");
    CParam *V1P2_BUF_step6 = StsGetParam(funcindex, "V1P2_BUF_step6");
    CParam *V1P2_BUF_step7 = StsGetParam(funcindex, "V1P2_BUF_step7");
    CParam *V1P2_BUF_step8 = StsGetParam(funcindex, "V1P2_BUF_step8");
    CParam *V1P2_BUF_step9 = StsGetParam(funcindex, "V1P2_BUF_step9");
    CParam *V1P2_BUF_step10 = StsGetParam(funcindex, "V1P2_BUF_step10");
    CParam *V1P2_BUF_step11 = StsGetParam(funcindex, "V1P2_BUF_step11");
    CParam *V1P2_BUF_step12 = StsGetParam(funcindex, "V1P2_BUF_step12");
    CParam *V1P2_BUF_step13 = StsGetParam(funcindex, "V1P2_BUF_step13");
    CParam *V1P2_BUF_step14 = StsGetParam(funcindex, "V1P2_BUF_step14");
    CParam *V1P2_BUF_step15 = StsGetParam(funcindex, "V1P2_BUF_step15");
    CParam *V1P2_BUF_pre_value = StsGetParam(funcindex, "V1P2_BUF_pre_value");
    CParam *V1P2_BUF_pre_bit = StsGetParam(funcindex, "V1P2_BUF_pre_bit");
    CParam *V1P2_BUF_post_bit = StsGetParam(funcindex, "V1P2_BUF_post_bit");
    CParam *V1P2_BUF_updated = StsGetParam(funcindex, "V1P2_BUF_updated");
    CParam *V1P2_BUF_guessed = StsGetParam(funcindex, "V1P2_BUF_guessed");
    CParam *V1P2_BUF_target = StsGetParam(funcindex, "V1P2_BUF_target");
    CParam *V1P2_BUF_post_value = StsGetParam(funcindex, "V1P2_BUF_post_value");
    CParam *V1P2_BUF_post_rt = StsGetParam(funcindex, "V1P2_BUF_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 1.2, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(EN_ATEST1,1),(ATEST1_MUX,2),(DIS_NTC_DETECTION_ANALOG,1)]
		Inherit_register();
		NTC_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(2);
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x68, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x02);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(EN_ATEST1,1),(ATEST1_MUX,2),(DIS_NTC_DETECTION_ANALOG,1)]
		delay_ms(2);
		NTC_FOVI.Set(FV, 1.2, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(2);
	}

	TRIM_NODE &MNT_V1P2_BUF = trim_reg.trim("mnt_v1p2_buf");
	MNT_V1P2_BUF.execute(measure_mnt_v1p2_buf, spec, funcindex, funclabel, 1, 0, 0,0);
	Retry_trim_search(&MNT_V1P2_BUF, measure_mnt_v1p2_buf, spec, funcindex, funclabel, 1.0, -1, 1, 1.3, false, 1.5);
	////================================第1组
	//SetTrimGroup(0x00FF);
	//GRP_CNT = 1;
	//MNT_V1P2_BUF.execute(measure_mnt_v1p2_buf, spec, funcindex, funclabel, 1, 0, 0, GRP_CNT);
	////================================第2组
	//SetTrimGroup(0xFF00);
	//GRP_CNT = 2;
	//cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K3_QVMH_NTC_SEL, K2_QVM_SITE_SEL, -1);// connect QVM group 2// QVM connect PC2
	//delay_ms(3);
	//MNT_V1P2_BUF.execute(measure_mnt_v1p2_buf, spec, funcindex, funclabel, 1, 0, 0, GRP_CNT);
	//SetRecoverSite();
	//QVM_GP.Disconnect();

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
		cbite.SetOn(K1_PGND2AGND, -1);
		delay_ms(3);
	}
	else
	{
		//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		//NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
		//cbite.SetOn(K1_PGND2AGND, -1);
		//delay_ms(3);
	}



	return 0;
}


DUT_API int Trim_IZTC_RES(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IZTC_RES_step0 = StsGetParam(funcindex, "IZTC_RES_step0");
    CParam *IZTC_RES_step1 = StsGetParam(funcindex, "IZTC_RES_step1");
    CParam *IZTC_RES_step2 = StsGetParam(funcindex, "IZTC_RES_step2");
    CParam *IZTC_RES_step3 = StsGetParam(funcindex, "IZTC_RES_step3");
    CParam *IZTC_RES_step4 = StsGetParam(funcindex, "IZTC_RES_step4");
    CParam *IZTC_RES_step5 = StsGetParam(funcindex, "IZTC_RES_step5");
    CParam *IZTC_RES_step6 = StsGetParam(funcindex, "IZTC_RES_step6");
    CParam *IZTC_RES_step7 = StsGetParam(funcindex, "IZTC_RES_step7");
    CParam *IZTC_RES_step8 = StsGetParam(funcindex, "IZTC_RES_step8");
    CParam *IZTC_RES_step9 = StsGetParam(funcindex, "IZTC_RES_step9");
    CParam *IZTC_RES_step10 = StsGetParam(funcindex, "IZTC_RES_step10");
    CParam *IZTC_RES_step11 = StsGetParam(funcindex, "IZTC_RES_step11");
    CParam *IZTC_RES_step12 = StsGetParam(funcindex, "IZTC_RES_step12");
    CParam *IZTC_RES_step13 = StsGetParam(funcindex, "IZTC_RES_step13");
    CParam *IZTC_RES_step14 = StsGetParam(funcindex, "IZTC_RES_step14");
    CParam *IZTC_RES_step15 = StsGetParam(funcindex, "IZTC_RES_step15");
    CParam *IZTC_RES_step16 = StsGetParam(funcindex, "IZTC_RES_step16");
    CParam *IZTC_RES_step17 = StsGetParam(funcindex, "IZTC_RES_step17");
    CParam *IZTC_RES_step18 = StsGetParam(funcindex, "IZTC_RES_step18");
    CParam *IZTC_RES_step19 = StsGetParam(funcindex, "IZTC_RES_step19");
    CParam *IZTC_RES_step20 = StsGetParam(funcindex, "IZTC_RES_step20");
    CParam *IZTC_RES_step21 = StsGetParam(funcindex, "IZTC_RES_step21");
    CParam *IZTC_RES_step22 = StsGetParam(funcindex, "IZTC_RES_step22");
    CParam *IZTC_RES_step23 = StsGetParam(funcindex, "IZTC_RES_step23");
    CParam *IZTC_RES_step24 = StsGetParam(funcindex, "IZTC_RES_step24");
    CParam *IZTC_RES_step25 = StsGetParam(funcindex, "IZTC_RES_step25");
    CParam *IZTC_RES_step26 = StsGetParam(funcindex, "IZTC_RES_step26");
    CParam *IZTC_RES_step27 = StsGetParam(funcindex, "IZTC_RES_step27");
    CParam *IZTC_RES_step28 = StsGetParam(funcindex, "IZTC_RES_step28");
    CParam *IZTC_RES_step29 = StsGetParam(funcindex, "IZTC_RES_step29");
    CParam *IZTC_RES_step30 = StsGetParam(funcindex, "IZTC_RES_step30");
    CParam *IZTC_RES_step31 = StsGetParam(funcindex, "IZTC_RES_step31");
    CParam *IZTC_RES_step32 = StsGetParam(funcindex, "IZTC_RES_step32");
    CParam *IZTC_RES_step33 = StsGetParam(funcindex, "IZTC_RES_step33");
    CParam *IZTC_RES_step34 = StsGetParam(funcindex, "IZTC_RES_step34");
    CParam *IZTC_RES_step35 = StsGetParam(funcindex, "IZTC_RES_step35");
    CParam *IZTC_RES_step36 = StsGetParam(funcindex, "IZTC_RES_step36");
    CParam *IZTC_RES_step37 = StsGetParam(funcindex, "IZTC_RES_step37");
    CParam *IZTC_RES_step38 = StsGetParam(funcindex, "IZTC_RES_step38");
    CParam *IZTC_RES_step39 = StsGetParam(funcindex, "IZTC_RES_step39");
    CParam *IZTC_RES_step40 = StsGetParam(funcindex, "IZTC_RES_step40");
    CParam *IZTC_RES_step41 = StsGetParam(funcindex, "IZTC_RES_step41");
    CParam *IZTC_RES_step42 = StsGetParam(funcindex, "IZTC_RES_step42");
    CParam *IZTC_RES_step43 = StsGetParam(funcindex, "IZTC_RES_step43");
    CParam *IZTC_RES_step44 = StsGetParam(funcindex, "IZTC_RES_step44");
    CParam *IZTC_RES_step45 = StsGetParam(funcindex, "IZTC_RES_step45");
    CParam *IZTC_RES_step46 = StsGetParam(funcindex, "IZTC_RES_step46");
    CParam *IZTC_RES_step47 = StsGetParam(funcindex, "IZTC_RES_step47");
    CParam *IZTC_RES_step48 = StsGetParam(funcindex, "IZTC_RES_step48");
    CParam *IZTC_RES_step49 = StsGetParam(funcindex, "IZTC_RES_step49");
    CParam *IZTC_RES_step50 = StsGetParam(funcindex, "IZTC_RES_step50");
    CParam *IZTC_RES_step51 = StsGetParam(funcindex, "IZTC_RES_step51");
    CParam *IZTC_RES_step52 = StsGetParam(funcindex, "IZTC_RES_step52");
    CParam *IZTC_RES_step53 = StsGetParam(funcindex, "IZTC_RES_step53");
    CParam *IZTC_RES_step54 = StsGetParam(funcindex, "IZTC_RES_step54");
    CParam *IZTC_RES_step55 = StsGetParam(funcindex, "IZTC_RES_step55");
    CParam *IZTC_RES_step56 = StsGetParam(funcindex, "IZTC_RES_step56");
    CParam *IZTC_RES_step57 = StsGetParam(funcindex, "IZTC_RES_step57");
    CParam *IZTC_RES_step58 = StsGetParam(funcindex, "IZTC_RES_step58");
    CParam *IZTC_RES_step59 = StsGetParam(funcindex, "IZTC_RES_step59");
    CParam *IZTC_RES_step60 = StsGetParam(funcindex, "IZTC_RES_step60");
    CParam *IZTC_RES_step61 = StsGetParam(funcindex, "IZTC_RES_step61");
    CParam *IZTC_RES_step62 = StsGetParam(funcindex, "IZTC_RES_step62");
    CParam *IZTC_RES_step63 = StsGetParam(funcindex, "IZTC_RES_step63");
    CParam *IZTC_RES_pre_value = StsGetParam(funcindex, "IZTC_RES_pre_value");
    CParam *IZTC_RES_pre_bit = StsGetParam(funcindex, "IZTC_RES_pre_bit");
    CParam *IZTC_RES_post_bit = StsGetParam(funcindex, "IZTC_RES_post_bit");
    CParam *IZTC_RES_updated = StsGetParam(funcindex, "IZTC_RES_updated");
    CParam *IZTC_RES_guessed = StsGetParam(funcindex, "IZTC_RES_guessed");
    CParam *IZTC_RES_target = StsGetParam(funcindex, "IZTC_RES_target");
    CParam *IZTC_RES_post_value = StsGetParam(funcindex, "IZTC_RES_post_value");
    CParam *IZTC_RES_post_rt = StsGetParam(funcindex, "IZTC_RES_post_rt");
    CParam *NTC_20uA = StsGetParam(funcindex, "NTC_20uA");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap,-1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 0.1, FOVIe_5V, FOVIe_1MA, FOVIe_RELAY_ON);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		delay_ms(5);
		Inherit_register();
		delay_ms(2);
	}
	else
	{
		NTC_FOVI.Set(FV, 0.1, FOVIe_5V, FOVIe_1MA, FOVIe_RELAY_ON);
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x00);//		field[(WAKE_UP,1),(EN_ATEST1,1),(ATEST1_MUX,2),(DIS_NTC_DETECTION_ANALOG,1)]
	}

	TRIM_NODE &IZTC_RES = trim_reg.trim("iztc_res");
	IZTC_RES.execute(measure_intc_curr, spec, funcindex, funclabel, 1, 0, 1);
	Retry_trim_search(&IZTC_RES, measure_intc_curr, spec, funcindex, funclabel, 1.0, -1, -1, 2.8, false, 1.0);

	double ntc_20uA[SITE_NUM] = { 0 };
	NTC_FOVI.Set(FV, 2, FOVIe_5V, FOVIe_1MA, FOVIe_RELAY_ON);
	delay_ms(2);
	NTC_FOVI.MeasureVI(200, 5);
	FOR_EACH_VALID_SITE(site)
	{
		ntc_20uA[site] = -1*NTC_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		cbite.SetOn(K1_PGND2AGND, -1);
		delay_ms(3);
	}
	else
	{
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	}
	FOR_EACH_VALID_SITE(site)
	{
		NTC_20uA->SetTestResult(site, 0, ntc_20uA[site]);
	}
	


	//cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, -1);
	//delay_ms(3);
	//VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	//delay_ms(5);
	//entertestmode();
	//I2CWriteSameData(DEV_ADDR, 0x56, 0x42);
	//I2CWriteSameData(DEV_ADDR, 0x67, 0x0A);
	//I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(EN_ATEST0,1),(ATEST0_MUX,8),(D2A_OVRD_SEL,10),(OVRD_VALUE,3)]
	//Inherit_register();
	//delay_ms(2);

	//TRIM_NODE &IZTC_RES = trim_reg.trim("iztc_res");
	//IZTC_RES.execute(measure_iztc_res, spec, funcindex, funclabel, 1, 0, 1);

	//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	//AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	//cbite.SetOn(K1_PGND2AGND, -1);
	//delay_ms(3);


    return 0;
}
 
DUT_API int Trim_OSC_4P5M(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *OSC_4P5M_step0 = StsGetParam(funcindex, "OSC_4P5M_step0");
    CParam *OSC_4P5M_step1 = StsGetParam(funcindex, "OSC_4P5M_step1");
    CParam *OSC_4P5M_step2 = StsGetParam(funcindex, "OSC_4P5M_step2");
    CParam *OSC_4P5M_step3 = StsGetParam(funcindex, "OSC_4P5M_step3");
    CParam *OSC_4P5M_step4 = StsGetParam(funcindex, "OSC_4P5M_step4");
    CParam *OSC_4P5M_step5 = StsGetParam(funcindex, "OSC_4P5M_step5");
    CParam *OSC_4P5M_step6 = StsGetParam(funcindex, "OSC_4P5M_step6");
    CParam *OSC_4P5M_step7 = StsGetParam(funcindex, "OSC_4P5M_step7");
    CParam *OSC_4P5M_step8 = StsGetParam(funcindex, "OSC_4P5M_step8");
    CParam *OSC_4P5M_step9 = StsGetParam(funcindex, "OSC_4P5M_step9");
    CParam *OSC_4P5M_step10 = StsGetParam(funcindex, "OSC_4P5M_step10");
    CParam *OSC_4P5M_step11 = StsGetParam(funcindex, "OSC_4P5M_step11");
    CParam *OSC_4P5M_step12 = StsGetParam(funcindex, "OSC_4P5M_step12");
    CParam *OSC_4P5M_step13 = StsGetParam(funcindex, "OSC_4P5M_step13");
    CParam *OSC_4P5M_step14 = StsGetParam(funcindex, "OSC_4P5M_step14");
    CParam *OSC_4P5M_step15 = StsGetParam(funcindex, "OSC_4P5M_step15");
    CParam *OSC_4P5M_pre_value = StsGetParam(funcindex, "OSC_4P5M_pre_value");
    CParam *OSC_4P5M_pre_bit = StsGetParam(funcindex, "OSC_4P5M_pre_bit");
    CParam *OSC_4P5M_post_bit = StsGetParam(funcindex, "OSC_4P5M_post_bit");
    CParam *OSC_4P5M_updated = StsGetParam(funcindex, "OSC_4P5M_updated");
    CParam *OSC_4P5M_guessed = StsGetParam(funcindex, "OSC_4P5M_guessed");
    CParam *OSC_4P5M_target = StsGetParam(funcindex, "OSC_4P5M_target");
    CParam *OSC_4P5M_post_value = StsGetParam(funcindex, "OSC_4P5M_post_value");
    CParam *OSC_4P5M_post_rt = StsGetParam(funcindex, "OSC_4P5M_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	QTMU_GP.Connect(QTMUe_RELAY_CHA);
	QTMU_GP.SetInSource(QTMUe_SINGLE_SOURCE_A);

	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap, K58_INT_PU, -1);
	delay_ms(3);
	if (!TTR)
	{
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		entertestmode();
		//------------------------OSC Measurement-------------//
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x55, 0x99);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x08); //		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,25),(ATEST1_MUX,8)]
		Inherit_register();
		delay_ms(2);
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x55, 0x99);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x08); //		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,25),(ATEST1_MUX,8)]
		delay_ms(2);
	}


	TRIM_NODE &OSC_4P5M = trim_reg.trim("osc_4p5m");
	//================================第1组
	SetTrimGroup(0x5555);
	GRP_CNT = 1;
	OSC_4P5M.execute(measure_osc_4p5m, spec, funcindex, funclabel, 1, 0, 1, GRP_CNT);
	//================================第2组
	SetTrimGroup(0xAAAA);
	GRP_CNT = 2;
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap,K6_QTMU_SITE_SEL, K58_INT_PU, -1);// connect QVM group 2// QVM connect PC2
	delay_ms(3);
	OSC_4P5M.execute(measure_osc_4p5m, spec, funcindex, funclabel, 1, 0, 1, GRP_CNT);
	SetRecoverSite();
	QTMU_GP.Disconnect(QTMUe_RELAY_CHA);
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		cbite.SetOn(K1_PGND2AGND, -1);
		delay_ms(3);
	}

    return 0;
}
 
DUT_API int Trim_VBAT_SNS_LOOP(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_SNS_LOOP_step0 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step0");
    CParam *VBAT_SNS_LOOP_step1 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step1");
    CParam *VBAT_SNS_LOOP_step2 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step2");
    CParam *VBAT_SNS_LOOP_step3 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step3");
    CParam *VBAT_SNS_LOOP_step4 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step4");
    CParam *VBAT_SNS_LOOP_step5 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step5");
    CParam *VBAT_SNS_LOOP_step6 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step6");
    CParam *VBAT_SNS_LOOP_step7 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step7");
    CParam *VBAT_SNS_LOOP_step8 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step8");
    CParam *VBAT_SNS_LOOP_step9 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step9");
    CParam *VBAT_SNS_LOOP_step10 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step10");
    CParam *VBAT_SNS_LOOP_step11 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step11");
    CParam *VBAT_SNS_LOOP_step12 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step12");
    CParam *VBAT_SNS_LOOP_step13 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step13");
    CParam *VBAT_SNS_LOOP_step14 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step14");
    CParam *VBAT_SNS_LOOP_step15 = StsGetParam(funcindex, "VBAT_SNS_LOOP_step15");
    CParam *VBAT_SNS_LOOP_pre_value = StsGetParam(funcindex, "VBAT_SNS_LOOP_pre_value");
    CParam *VBAT_SNS_LOOP_pre_bit = StsGetParam(funcindex, "VBAT_SNS_LOOP_pre_bit");
    CParam *VBAT_SNS_LOOP_post_bit = StsGetParam(funcindex, "VBAT_SNS_LOOP_post_bit");
    CParam *VBAT_SNS_LOOP_updated = StsGetParam(funcindex, "VBAT_SNS_LOOP_updated");
    CParam *VBAT_SNS_LOOP_guessed = StsGetParam(funcindex, "VBAT_SNS_LOOP_guessed");
    CParam *VBAT_SNS_LOOP_target = StsGetParam(funcindex, "VBAT_SNS_LOOP_target");
    CParam *VBAT_SNS_LOOP_post_value = StsGetParam(funcindex, "VBAT_SNS_LOOP_post_value");
    CParam *VBAT_SNS_LOOP_post_rt = StsGetParam(funcindex, "VBAT_SNS_LOOP_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here


	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap,-1);
	delay_ms(3);
	if (!TTR)
	{
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, V_TYP_VBAT*0.4, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x11, 0x10);
		I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,0),(EN_ATEST0,1),(ATEST0_MUX,31)]
		Inherit_register();
		delay_ms(2);
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x55, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x00); //		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,25),(ATEST1_MUX,8)]
		I2CWriteSameData(DEV_ADDR, 0x11, 0x10);
		I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,0),(EN_ATEST0,1),(ATEST0_MUX,31)]
		delay_ms(2);
	}

	AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(2);

	TRIM_NODE &MNT_VBAT_RSNS_LOOP = trim_reg.trim("mnt_vbat_rsns_loop");
	MNT_VBAT_RSNS_LOOP.execute(measure_mnt_vbat_rsns_loop, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&MNT_VBAT_RSNS_LOOP, measure_mnt_vbat_rsns_loop, spec, funcindex, funclabel, 1.0, -1, -1, 1.3, false, 1.0);
	////================================第1组
	//SetTrimGroup(0x00FF);
	//GRP_CNT = 1;
	//MNT_VBAT_RSNS_LOOP.execute(measure_mnt_vbat_rsns_loop, spec, funcindex, funclabel, 1, 0, 1, GRP_CNT);
	////================================第2组
	//SetTrimGroup(0xFF00);
	//GRP_CNT = 2;
	//cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K2_QVM_SITE_SEL, -1);// connect QVM group 2// QVM connect PC2
	//delay_ms(3);
	//MNT_VBAT_RSNS_LOOP.execute(measure_mnt_vbat_rsns_loop, spec, funcindex, funclabel, 1, 0, 1, GRP_CNT);
	//SetRecoverSite();
	//QVM_GP.Disconnect();

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		cbite.SetOn(K1_PGND2AGND, -1);
		delay_ms(3);
	}

    return 0;
}
 
DUT_API int Trim_AMUX_EA_Offset(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_EA_OS_step0 = StsGetParam(funcindex, "AMUX_EA_OS_step0");
    CParam *AMUX_EA_OS_step1 = StsGetParam(funcindex, "AMUX_EA_OS_step1");
    CParam *AMUX_EA_OS_step2 = StsGetParam(funcindex, "AMUX_EA_OS_step2");
    CParam *AMUX_EA_OS_step3 = StsGetParam(funcindex, "AMUX_EA_OS_step3");
    CParam *AMUX_EA_OS_step4 = StsGetParam(funcindex, "AMUX_EA_OS_step4");
    CParam *AMUX_EA_OS_step5 = StsGetParam(funcindex, "AMUX_EA_OS_step5");
    CParam *AMUX_EA_OS_step6 = StsGetParam(funcindex, "AMUX_EA_OS_step6");
    CParam *AMUX_EA_OS_step7 = StsGetParam(funcindex, "AMUX_EA_OS_step7");
    CParam *AMUX_EA_OS_step8 = StsGetParam(funcindex, "AMUX_EA_OS_step8");
    CParam *AMUX_EA_OS_step9 = StsGetParam(funcindex, "AMUX_EA_OS_step9");
    CParam *AMUX_EA_OS_step10 = StsGetParam(funcindex, "AMUX_EA_OS_step10");
    CParam *AMUX_EA_OS_step11 = StsGetParam(funcindex, "AMUX_EA_OS_step11");
    CParam *AMUX_EA_OS_step12 = StsGetParam(funcindex, "AMUX_EA_OS_step12");
    CParam *AMUX_EA_OS_step13 = StsGetParam(funcindex, "AMUX_EA_OS_step13");
    CParam *AMUX_EA_OS_step14 = StsGetParam(funcindex, "AMUX_EA_OS_step14");
    CParam *AMUX_EA_OS_step15 = StsGetParam(funcindex, "AMUX_EA_OS_step15");
    CParam *AMUX_EA_OS_pre_value = StsGetParam(funcindex, "AMUX_EA_OS_pre_value");
    CParam *AMUX_EA_OS_pre_bit = StsGetParam(funcindex, "AMUX_EA_OS_pre_bit");
    CParam *AMUX_EA_OS_post_bit = StsGetParam(funcindex, "AMUX_EA_OS_post_bit");
    CParam *AMUX_EA_OS_updated = StsGetParam(funcindex, "AMUX_EA_OS_updated");
    CParam *AMUX_EA_OS_guessed = StsGetParam(funcindex, "AMUX_EA_OS_guessed");
    CParam *AMUX_EA_OS_target = StsGetParam(funcindex, "AMUX_EA_OS_target");
    CParam *AMUX_EA_OS_post_value = StsGetParam(funcindex, "AMUX_EA_OS_post_value");
    CParam *AMUX_EA_OS_post_rt = StsGetParam(funcindex, "AMUX_EA_OS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap,-1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);
		I2CWriteSameData(DEV_ADDR, 0x56, 0xE2);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15),(EN_ATEST0,1),(ATEST0_MUX,28)]
		Inherit_register();
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);
		I2CWriteSameData(DEV_ADDR, 0x56, 0xE2);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15),(EN_ATEST0,1),(ATEST0_MUX,28)]
		delay_ms(1);
	}

	TRIM_NODE &AMUX_EA_OS = trim_reg.trim("amux_ea_os");
	AMUX_EA_OS.execute(measure_amux_ea_os, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&AMUX_EA_OS, measure_amux_ea_os, spec, funcindex, funclabel, 1.0, 1, -1, 1.2, true, 1.0);
	////================================第1组
	//SetTrimGroup(0x00FF);
	//GRP_CNT = 1;
	//delay_ms(5);
	//AMUX_EA_OS.execute(measure_amux_ea_os, spec, funcindex, funclabel, 1, 0, 0, GRP_CNT);
	////================================第2组
	//SetTrimGroup(0xFF00);
	//GRP_CNT = 2;
	//cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K2_QVM_SITE_SEL, -1);// connect QVM group 2// QVM connect PC2
	//delay_ms(3);
	//delay_ms(5);
	//AMUX_EA_OS.execute(measure_amux_ea_os, spec, funcindex, funclabel, 1, 0, 0, GRP_CNT);
	//SetRecoverSite();
	//QVM_GP.Disconnect();
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		cbite.SetOn(K1_PGND2AGND, -1);
		delay_ms(3);
	}
	else
	{
		//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		//AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		//AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		//cbite.SetOn(K1_PGND2AGND, -1);
		//delay_ms(3);
	}

    return 0;
}
 
DUT_API int Trim_IBUS_SNS_Gain(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IBUS_SNS_Gain_step0 = StsGetParam(funcindex, "IBUS_SNS_Gain_step0");
    CParam *IBUS_SNS_Gain_step1 = StsGetParam(funcindex, "IBUS_SNS_Gain_step1");
    CParam *IBUS_SNS_Gain_step2 = StsGetParam(funcindex, "IBUS_SNS_Gain_step2");
    CParam *IBUS_SNS_Gain_step3 = StsGetParam(funcindex, "IBUS_SNS_Gain_step3");
    CParam *IBUS_SNS_Gain_step4 = StsGetParam(funcindex, "IBUS_SNS_Gain_step4");
    CParam *IBUS_SNS_Gain_step5 = StsGetParam(funcindex, "IBUS_SNS_Gain_step5");
    CParam *IBUS_SNS_Gain_step6 = StsGetParam(funcindex, "IBUS_SNS_Gain_step6");
    CParam *IBUS_SNS_Gain_step7 = StsGetParam(funcindex, "IBUS_SNS_Gain_step7");
    CParam *IBUS_SNS_Gain_step8 = StsGetParam(funcindex, "IBUS_SNS_Gain_step8");
    CParam *IBUS_SNS_Gain_step9 = StsGetParam(funcindex, "IBUS_SNS_Gain_step9");
    CParam *IBUS_SNS_Gain_step10 = StsGetParam(funcindex, "IBUS_SNS_Gain_step10");
    CParam *IBUS_SNS_Gain_step11 = StsGetParam(funcindex, "IBUS_SNS_Gain_step11");
    CParam *IBUS_SNS_Gain_step12 = StsGetParam(funcindex, "IBUS_SNS_Gain_step12");
    CParam *IBUS_SNS_Gain_step13 = StsGetParam(funcindex, "IBUS_SNS_Gain_step13");
    CParam *IBUS_SNS_Gain_step14 = StsGetParam(funcindex, "IBUS_SNS_Gain_step14");
    CParam *IBUS_SNS_Gain_step15 = StsGetParam(funcindex, "IBUS_SNS_Gain_step15");
    CParam *IBUS_SNS_Gain_step16 = StsGetParam(funcindex, "IBUS_SNS_Gain_step16");
    CParam *IBUS_SNS_Gain_step17 = StsGetParam(funcindex, "IBUS_SNS_Gain_step17");
    CParam *IBUS_SNS_Gain_step18 = StsGetParam(funcindex, "IBUS_SNS_Gain_step18");
    CParam *IBUS_SNS_Gain_step19 = StsGetParam(funcindex, "IBUS_SNS_Gain_step19");
    CParam *IBUS_SNS_Gain_step20 = StsGetParam(funcindex, "IBUS_SNS_Gain_step20");
    CParam *IBUS_SNS_Gain_step21 = StsGetParam(funcindex, "IBUS_SNS_Gain_step21");
    CParam *IBUS_SNS_Gain_step22 = StsGetParam(funcindex, "IBUS_SNS_Gain_step22");
    CParam *IBUS_SNS_Gain_step23 = StsGetParam(funcindex, "IBUS_SNS_Gain_step23");
    CParam *IBUS_SNS_Gain_step24 = StsGetParam(funcindex, "IBUS_SNS_Gain_step24");
    CParam *IBUS_SNS_Gain_step25 = StsGetParam(funcindex, "IBUS_SNS_Gain_step25");
    CParam *IBUS_SNS_Gain_step26 = StsGetParam(funcindex, "IBUS_SNS_Gain_step26");
    CParam *IBUS_SNS_Gain_step27 = StsGetParam(funcindex, "IBUS_SNS_Gain_step27");
    CParam *IBUS_SNS_Gain_step28 = StsGetParam(funcindex, "IBUS_SNS_Gain_step28");
    CParam *IBUS_SNS_Gain_step29 = StsGetParam(funcindex, "IBUS_SNS_Gain_step29");
    CParam *IBUS_SNS_Gain_step30 = StsGetParam(funcindex, "IBUS_SNS_Gain_step30");
    CParam *IBUS_SNS_Gain_step31 = StsGetParam(funcindex, "IBUS_SNS_Gain_step31");
    CParam *IBUS_SNS_Gain_pre_value = StsGetParam(funcindex, "IBUS_SNS_Gain_pre_value");
    CParam *IBUS_SNS_Gain_pre_bit = StsGetParam(funcindex, "IBUS_SNS_Gain_pre_bit");
    CParam *IBUS_SNS_Gain_post_bit = StsGetParam(funcindex, "IBUS_SNS_Gain_post_bit");
    CParam *IBUS_SNS_Gain_updated = StsGetParam(funcindex, "IBUS_SNS_Gain_updated");
    CParam *IBUS_SNS_Gain_guessed = StsGetParam(funcindex, "IBUS_SNS_Gain_guessed");
    CParam *IBUS_SNS_Gain_target = StsGetParam(funcindex, "IBUS_SNS_Gain_target");
    CParam *IBUS_SNS_Gain_post_value = StsGetParam(funcindex, "IBUS_SNS_Gain_post_value");
    CParam *IBUS_SNS_Gain_post_rt = StsGetParam(funcindex, "IBUS_SNS_Gain_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	//--------------In boost mode trim
	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0xCE);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x07);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
		//		field[(WAKE_UP,1),(EN_ATEST0,1),(ATEST0_MUX,25),(EN_ATEST1,1),(ATEST1_MUX,7),(DIS_NTC_DETECTION_ANALOG,1),(BUBO_MODE,1)]
		Inherit_register();
		delay_ms(2);
	}
	else
	{
		cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(2);
		I2CWriteSameData(DEV_ADDR, 0x11, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0xCE);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x07);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
		//		field[(WAKE_UP,1),(EN_ATEST0,1),(ATEST0_MUX,25),(EN_ATEST1,1),(ATEST1_MUX,7),(DIS_NTC_DETECTION_ANALOG,1),(BUBO_MODE,1)]
		delay_ms(1);
	}

	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(100);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);

	TRIM_NODE &IBUS_SNS_GAIN = trim_reg.trim("ibus_sns_gain");
	IBUS_SNS_GAIN.execute(measure_ibus_sns_gain, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&IBUS_SNS_GAIN, measure_ibus_sns_gain, spec, funcindex, funclabel, 1.0, 1, 1, 5, true, 1.0);

	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(100);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
	}


    return 0;
}
 
DUT_API int Trim_IBUS_SNS_EA_Offset(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IBUS_SNS_EA_OS_step0 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step0");
    CParam *IBUS_SNS_EA_OS_step1 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step1");
    CParam *IBUS_SNS_EA_OS_step2 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step2");
    CParam *IBUS_SNS_EA_OS_step3 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step3");
    CParam *IBUS_SNS_EA_OS_step4 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step4");
    CParam *IBUS_SNS_EA_OS_step5 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step5");
    CParam *IBUS_SNS_EA_OS_step6 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step6");
    CParam *IBUS_SNS_EA_OS_step7 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step7");
    CParam *IBUS_SNS_EA_OS_step8 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step8");
    CParam *IBUS_SNS_EA_OS_step9 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step9");
    CParam *IBUS_SNS_EA_OS_step10 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step10");
    CParam *IBUS_SNS_EA_OS_step11 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step11");
    CParam *IBUS_SNS_EA_OS_step12 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step12");
    CParam *IBUS_SNS_EA_OS_step13 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step13");
    CParam *IBUS_SNS_EA_OS_step14 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step14");
    CParam *IBUS_SNS_EA_OS_step15 = StsGetParam(funcindex, "IBUS_SNS_EA_OS_step15");
    CParam *IBUS_SNS_EA_OS_pre_value = StsGetParam(funcindex, "IBUS_SNS_EA_OS_pre_value");
    CParam *IBUS_SNS_EA_OS_pre_bit = StsGetParam(funcindex, "IBUS_SNS_EA_OS_pre_bit");
    CParam *IBUS_SNS_EA_OS_post_bit = StsGetParam(funcindex, "IBUS_SNS_EA_OS_post_bit");
    CParam *IBUS_SNS_EA_OS_updated = StsGetParam(funcindex, "IBUS_SNS_EA_OS_updated");
    CParam *IBUS_SNS_EA_OS_guessed = StsGetParam(funcindex, "IBUS_SNS_EA_OS_guessed");
    CParam *IBUS_SNS_EA_OS_target = StsGetParam(funcindex, "IBUS_SNS_EA_OS_target");
    CParam *IBUS_SNS_EA_OS_post_value = StsGetParam(funcindex, "IBUS_SNS_EA_OS_post_value");
    CParam *IBUS_SNS_EA_OS_post_rt = StsGetParam(funcindex, "IBUS_SNS_EA_OS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	if (!TTR)
	{
		//--------------In boost mode trim
		cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap,K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0xCE);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x07);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x64, 0x01);
		//I2CWriteSameData(DEV_ADDR, 0x68, 0x20);
		Inherit_register();
		delay_ms(2);
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x64, 0x01);// disable chopper
	}

	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(100);
	TRIM_NODE &IBUS_SNS_EA_OS = trim_reg.trim("ibus_sns_ea_os");
	IBUS_SNS_EA_OS.execute(measure_ibus_sns_ea_os, spec, funcindex, funclabel, 1, 0, 1);
	Retry_trim_search(&IBUS_SNS_EA_OS, measure_ibus_sns_ea_os, spec, funcindex, funclabel, 1.0, -1, 1, 15, false, 1.0);

	//STSSetTimeCheck(1);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(100);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
	//double testtime2 = STSGetTimeElapsed(1);

    return 0;
}
 
DUT_API int Trim_BUBO_RCS_Base(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VC_HighCalmp_BUCK = StsGetParam(funcindex, "VC_HighCalmp_BUCK");
    CParam *Buck_I1 = StsGetParam(funcindex, "Buck_I1");
    CParam *Buck_I2 = StsGetParam(funcindex, "Buck_I2");
    CParam *Buck_Iscale = StsGetParam(funcindex, "Buck_Iscale");
    CParam *VC_HighCalmp_BOOST = StsGetParam(funcindex, "VC_HighCalmp_BOOST");
    CParam *Boost_I1 = StsGetParam(funcindex, "Boost_I1");
    CParam *Boost_I2 = StsGetParam(funcindex, "Boost_I2");
    CParam *Boost_Iscale = StsGetParam(funcindex, "Boost_Iscale");
    CParam *Buck_Iclamp = StsGetParam(funcindex, "Buck_Iclamp");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	double Iscale1_buck[SITE_NUM] = { 0 };
	double Iscale2_buck[SITE_NUM] = { 0 };
	double Iscale1_boost[SITE_NUM] = { 0 };
	double Iscale2_boost[SITE_NUM] = { 0 };
	double buckIclamp[SITE_NUM] = { 0 };
	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//VBAT need <4.2V, VBAT_OVP
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 2, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
		//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(IBAT_LIMIT,7),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(EN_ATEST0,1),(D2A_BUBO_ATEST0,1),(D2A_BUBO_TM_DIS_COMPH_SLP,1),(DIS_NTC_DETECTION_ANALOG,1)]
		I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x01);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x51);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x21);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		//-------config1
		Inherit_register();
		delay_ms(2);
	}
	else
	{
		//cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		//delay_ms(3);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//VBAT need <4.2V, VBAT_OVP
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		//BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 2, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
		//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(IBAT_LIMIT,7),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(EN_ATEST0,1),(D2A_BUBO_ATEST0,1),(D2A_BUBO_TM_DIS_COMPH_SLP,1),(DIS_NTC_DETECTION_ANALOG,1)]
		I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x01);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x51);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
		//-------config1
		I2CWriteSameData(DEV_ADDR, 0x58, 0x21);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		delay_ms(1);
		Inherit_register();
		delay_ms(2);
	}

	NTC_FOVI.MeasureVI(50, 5);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vclamp_high_buck[site] = NTC_FOVI.GetMeasResult(site, MVRET);
		Iscale1_buck[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
	}
	//-------config2
	I2CWriteSameData(DEV_ADDR, 0x58, 0x31); //		field[(D2A_BUBO_TM_ISCALE_DOWN,1)]
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Iscale2_buck[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
		Iscale_buck[site] = Iscale1_buck[site] / Iscale2_buck[site];
	}
	AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);

	I2CWriteSameData(DEV_ADDR, 0x5A, 0x61);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x5B);
	delay_ms(1);
	NTC_FOVI.Set(FV, 4, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(1);
	NTC_FOVI.MeasureVI(50, 5);
	NTC_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		buckIclamp[site] = NTC_FOVI.GetMeasResult(site, MIRET)*1e9;//nA
	}
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x51);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);


	//---------------BOOST Mode
	//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(IBAT_LIMIT,7),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(BUBO_MODE,1),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(EN_ATEST0,1),(D2A_BUBO_ATEST0,1),(D2A_BUBO_TM_DIS_COMPH_SLP,1),(DIS_NTC_DETECTION_ANALOG,1)] 
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
	delay_ms(5);// delay need keep to make sure boost mode can enter stable
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x03, 0x60);
	//-------config1
	I2CWriteSameData(DEV_ADDR, 0x58, 0x21);//		field[(D2A_BUBO_TM_DIS_CLK,1),(FSM_STAT,6)]
	AMUX_FOVI.Set(FV, 2, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
	delay_ms(2);
	//NTC_FOVI.MeasureVI(50, 5);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		//Vclamp_high_boost[site] = NTC_FOVI.GetMeasResult(site, MVRET);
		//if (Vclamp_high_boost[site] < 2.4)
		//{
		//	delay_ms(1);
		//}
		Iscale1_boost[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
	}

	//-------config2
	I2CWriteSameData(DEV_ADDR, 0x58, 0x31); //		field[(D2A_BUBO_TM_ISCALE_DOWN,1)]
	delay_ms(2);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Iscale2_boost[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
		Iscale_boost[site] = Iscale1_boost[site] / Iscale2_boost[site];
	}

	BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	NTC_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vclamp_high_boost[site] = NTC_FOVI.GetMeasResult(site, MVRET);
	}

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);


#if 1
	double boost_hs_noc[SITE_NUM] = { 0 };
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double bubo_zcd_noc[200] = { 0.0 };
	double Trig = 2.5;
	int Trig_Point[SITE_NUM] = { 0 };
	//---------------BUCK_LS_ZCD

	SW_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
	cbite.SetOn(K17_BUSH_SW, K33_BUSL_PGND, K30_VBAT_Cap, K32_PMID_Cap, K28_VDRV_Cap, K25_VCC_Cap, K18_BST_SW_Cap, K43_INT_ACM, K58_INT_PU, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	entertestmode();
	//---------------BUCK_LS_ZCD
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x01);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_LSON,1),(BUBO_MODE,0)]
	I2CWriteSameData(DEV_ADDR, 0x55, 0xB0);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);	//		field[(D2A_BUBO_TM_DIS_CLK,1),(EN_DTEST0,1),(DTEST0_MUX,48)]
	Inherit_register();
	delay_ms(1);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	STSAWGCreateRampData(&bubo_zcd_noc[0], sam, 1, 0.2, -0.5);// PGND--->SW
	FPVI.AwgClear();
	FPVI.AwgLoader("bubo_zcd_noc_pattern", FI, FPVIe_1V, FPVIe_1A, bubo_zcd_noc, sam);
	FPVI.AwgSelect("bubo_zcd_noc_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	FPVI.Set(FI, 0.21, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x58, 0xE0);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//avoid spike
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		Buck_lsfet_zcd[site] = -1 * FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]); //Read the voltage value on trigger position, A,  PGND---->SW为正，与电感店里方向一致。
		BU_zcd_in_BO_Rcs_Mode[site] = FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]);
		check_awg_trigger_point(Trig_Point, sam,Buck_lsfet_zcd, BU_zcd_in_BO_Rcs_Mode,site);// add for AWG trigger check
	}

	cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K31_BUSL_PMID, K17_BUSH_SW, K28_VDRV_Cap, K25_VCC_Cap, K43_INT_ACM,K58_INT_PU,-1);
	delay_ms(3);
	StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
	//entertestmode();
	delay_ms(3);// delay_3ms for pwoer on stable which can help enter boost mode
	//-------------------BOOST HS_ZCD
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xB1);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x02);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);	//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_HSON,1)]
	I2CWriteSameData(DEV_ADDR, 0x6D, 0x80);// minmum ZCD current
	delay_ms(3);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	STSAWGCreateRampData(&bubo_zcd_noc[0], sam, 1, -0.18, 0.68);//SW ---->PMID
	FPVI.AwgClear();
	FPVI.AwgLoader("bubo_zcd_noc_pattern", FI, FPVIe_1V, FPVIe_1A, bubo_zcd_noc, sam);
	FPVI.AwgSelect("bubo_zcd_noc_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	FPVI.Set(FI, -0.2, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		Boost_hsfet_zcd[site] = FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]);//Read the voltage value on trigger position, A
		BO_zcd_in_BU_Rcs_Mode[site] =-1* FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]);
		check_awg_trigger_point(Trig_Point, sam, Boost_hsfet_zcd, BO_zcd_in_BU_Rcs_Mode, site);// add for AWG trigger check
	}
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

#if 0
	//---------------BOOST_NOC
	I2CWriteSameData(DEV_ADDR, 0x09, 0x19);
	delay_ms(3);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	STSAWGCreateRampData(&bubo_zcd_noc[0], sam, 1, -2.0, -3.2);//PMID--->SW
	FPVI.AwgClear();
	FPVI.AwgLoader("bubo_zcd_noc_pattern", FI, FPVIe_1V, FPVIe_10A, bubo_zcd_noc, sam);
	FPVI.AwgSelect("bubo_zcd_noc_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	FPVI.Set(FI, -2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_ms(2);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		boost_hs_noc[site] = FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]); //Read the voltage value on trigger position
	}
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
#endif

	VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);

	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(1);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
#endif
	FOR_EACH_VALID_SITE(site)
	{
		VC_HighCalmp_BUCK->SetTestResult(site, 0, Vclamp_high_buck[site]);
		Buck_I1->SetTestResult(site, 0, Iscale1_buck[site]);
		Buck_I2->SetTestResult(site, 0, Iscale2_buck[site]);
		Buck_Iscale->SetTestResult(site, 0, Iscale_buck[site]);
		VC_HighCalmp_BOOST->SetTestResult(site, 0, Vclamp_high_boost[site]);
		Boost_I1->SetTestResult(site, 0, Iscale1_boost[site]);
		Boost_I2->SetTestResult(site, 0, Iscale2_boost[site]);
		Boost_Iscale->SetTestResult(site, 0, Iscale_boost[site]);
		Buck_Iclamp->SetTestResult(site, 0, buckIclamp[site]);
	}
	return 0;
}

DUT_API int Trim_BUCK_RCS(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BUCK_RCS_step0 = StsGetParam(funcindex, "BUCK_RCS_step0");
    CParam *BUCK_RCS_step1 = StsGetParam(funcindex, "BUCK_RCS_step1");
    CParam *BUCK_RCS_step2 = StsGetParam(funcindex, "BUCK_RCS_step2");
    CParam *BUCK_RCS_step3 = StsGetParam(funcindex, "BUCK_RCS_step3");
    CParam *BUCK_RCS_step4 = StsGetParam(funcindex, "BUCK_RCS_step4");
    CParam *BUCK_RCS_step5 = StsGetParam(funcindex, "BUCK_RCS_step5");
    CParam *BUCK_RCS_step6 = StsGetParam(funcindex, "BUCK_RCS_step6");
    CParam *BUCK_RCS_step7 = StsGetParam(funcindex, "BUCK_RCS_step7");
    CParam *BUCK_RCS_step8 = StsGetParam(funcindex, "BUCK_RCS_step8");
    CParam *BUCK_RCS_step9 = StsGetParam(funcindex, "BUCK_RCS_step9");
    CParam *BUCK_RCS_step10 = StsGetParam(funcindex, "BUCK_RCS_step10");
    CParam *BUCK_RCS_step11 = StsGetParam(funcindex, "BUCK_RCS_step11");
    CParam *BUCK_RCS_step12 = StsGetParam(funcindex, "BUCK_RCS_step12");
    CParam *BUCK_RCS_step13 = StsGetParam(funcindex, "BUCK_RCS_step13");
    CParam *BUCK_RCS_step14 = StsGetParam(funcindex, "BUCK_RCS_step14");
    CParam *BUCK_RCS_step15 = StsGetParam(funcindex, "BUCK_RCS_step15");
    CParam *BUCK_RCS_pre_value = StsGetParam(funcindex, "BUCK_RCS_pre_value");
    CParam *BUCK_RCS_pre_bit = StsGetParam(funcindex, "BUCK_RCS_pre_bit");
    CParam *BUCK_RCS_post_bit = StsGetParam(funcindex, "BUCK_RCS_post_bit");
    CParam *BUCK_RCS_updated = StsGetParam(funcindex, "BUCK_RCS_updated");
    CParam *BUCK_RCS_guessed = StsGetParam(funcindex, "BUCK_RCS_guessed");
    CParam *BUCK_RCS_target = StsGetParam(funcindex, "BUCK_RCS_target");
    CParam *BUCK_RCS_post_value = StsGetParam(funcindex, "BUCK_RCS_post_value");
    CParam *BUCK_RCS_post_rt = StsGetParam(funcindex, "BUCK_RCS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	//cbite.SetOn(K1_PGND2AGND, K26_BUSH_VDRV, K33_BUSL_PGND,  -1);
	//delay_ms(3);
	//VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	//FPVI.Set(FI, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
	//delay_ms(5);
	//FPVI.MeasureVI(100, 5);
	//VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	//VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

	cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K31_BUSL_PMID,K30_VBAT_Cap, K32_PMID_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap, -1);
	delay_ms(3);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//VBAT need <4.2V, VBAT_OVP
	VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
	entertestmode();
	//----config open hsfet
    //		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(IBAT_LIMIT,7),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(BUBO_MODE,0),(D2A_BUBO_TM_ISCALE_DOWN,1),(D2A_BUBO_TM_DIS_COMPH_SLP,1)]
	I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x31);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xB7);//		field[(EN_DTEST0,1),(DTEST0_MUX,55)]
	I2CWriteSameData(DEV_ADDR, 0x59, 0x02);//		field[(D2A_BUBO_TM_HSON,1)]
	Inherit_register();
	delay_ms(2);
	//BTST_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	SDA_INT_ACM.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double buck_rcs[200] = { 0.0 };
	double Trig =2.5;
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&buck_rcs[0], sam, 1,-0.15, -1.95);//  PMID-->SW
	FPVI.AwgLoader("buck_rcs_pattern", FI, FPVIe_1V, FPVIe_2A, buck_rcs, sam);
	FPVI.AwgSelect("buck_rcs_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI( sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	TRIM_NODE &BUCK_RCS = trim_reg.trim("buck_rcs");
	BUCK_RCS.force_table_char_active(true);
	BUCK_RCS.execute(measure_buck_rcs, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&BUCK_RCS, measure_buck_rcs, spec, funcindex, funclabel, 1, -1, -1, 6, false, 1);
	
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_us(100);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x00);// HS_LS OFF
	if (!TTR)
	{
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);

		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_10MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_10MA, ACM200_RELAY_OFF);//BST=SW
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_OFF);
	}
	else
	{
		BTST_ACM.Set(FV, 9, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
		PMID_FOVI.Set(FV, 5, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 5, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
		delay_us(500);
	}


    return 0;
}
 
DUT_API int Trim_BOOST_RCS(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BOOST_RCS_step0 = StsGetParam(funcindex, "BOOST_RCS_step0");
    CParam *BOOST_RCS_step1 = StsGetParam(funcindex, "BOOST_RCS_step1");
    CParam *BOOST_RCS_step2 = StsGetParam(funcindex, "BOOST_RCS_step2");
    CParam *BOOST_RCS_step3 = StsGetParam(funcindex, "BOOST_RCS_step3");
    CParam *BOOST_RCS_step4 = StsGetParam(funcindex, "BOOST_RCS_step4");
    CParam *BOOST_RCS_step5 = StsGetParam(funcindex, "BOOST_RCS_step5");
    CParam *BOOST_RCS_step6 = StsGetParam(funcindex, "BOOST_RCS_step6");
    CParam *BOOST_RCS_step7 = StsGetParam(funcindex, "BOOST_RCS_step7");
    CParam *BOOST_RCS_step8 = StsGetParam(funcindex, "BOOST_RCS_step8");
    CParam *BOOST_RCS_step9 = StsGetParam(funcindex, "BOOST_RCS_step9");
    CParam *BOOST_RCS_step10 = StsGetParam(funcindex, "BOOST_RCS_step10");
    CParam *BOOST_RCS_step11 = StsGetParam(funcindex, "BOOST_RCS_step11");
    CParam *BOOST_RCS_step12 = StsGetParam(funcindex, "BOOST_RCS_step12");
    CParam *BOOST_RCS_step13 = StsGetParam(funcindex, "BOOST_RCS_step13");
    CParam *BOOST_RCS_step14 = StsGetParam(funcindex, "BOOST_RCS_step14");
    CParam *BOOST_RCS_step15 = StsGetParam(funcindex, "BOOST_RCS_step15");
    CParam *BOOST_RCS_pre_value = StsGetParam(funcindex, "BOOST_RCS_pre_value");
    CParam *BOOST_RCS_pre_bit = StsGetParam(funcindex, "BOOST_RCS_pre_bit");
    CParam *BOOST_RCS_post_bit = StsGetParam(funcindex, "BOOST_RCS_post_bit");
    CParam *BOOST_RCS_updated = StsGetParam(funcindex, "BOOST_RCS_updated");
    CParam *BOOST_RCS_guessed = StsGetParam(funcindex, "BOOST_RCS_guessed");
    CParam *BOOST_RCS_target = StsGetParam(funcindex, "BOOST_RCS_target");
    CParam *BOOST_RCS_post_value = StsGetParam(funcindex, "BOOST_RCS_post_value");
    CParam *BOOST_RCS_post_rt = StsGetParam(funcindex, "BOOST_RCS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	DWORD working_value2[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_FF").get_working(site);
	}
	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K33_BUSL_PGND, K30_VBAT_Cap, K32_PMID_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		entertestmode();
		//----config open hsfet
		//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(IBAT_LIMIT,7),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(BUBO_MODE,1),(D2A_BUBO_TM_ISCALE_DOWN,1),(D2A_BUBO_TM_DIS_COMPH_SLP,1)]
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x11);//D2A_BUBO_TM_DIS_CLK=0
		I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);
		I2CWriteSameData(DEV_ADDR, 0x55, 0xB6);//		field[(EN_DTEST0,1),(DTEST0_MUX,54)]
		I2CWriteSameData(DEV_ADDR, 0x59, 0x01); //		field[(D2A_BUBO_TM_LSON,1)]
		Inherit_register();
		delay_ms(2);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
		delay_us(100);
	}
	else
	{
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K33_BUSL_PGND, K30_VBAT_Cap, K32_PMID_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap, -1);
		delay_ms(3);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(IBAT_LIMIT,7),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(BUBO_MODE,1),(D2A_BUBO_TM_ISCALE_DOWN,1),(D2A_BUBO_TM_DIS_COMPH_SLP,1)]
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		//I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
		//I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		//I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x11);//D2A_BUBO_TM_DIS_CLK=0
		I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);
		I2CWriteSameData(DEV_ADDR, 0x55, 0xB6);//		field[(EN_DTEST0,1),(DTEST0_MUX,54)]
		I2CWriteSameData(DEV_ADDR, 0x59, 0x01); //		field[(D2A_BUBO_TM_LSON,1)]
		I2CWriteSameData(DEV_ADDR, 0x6D, 0x80);// minmum ZCD current
		delay_ms(1);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(100);
	}


	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double boost_rcs[200] = { 0.0 };
	double Trig = 2.5;
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&boost_rcs[0], sam, 1, 0.5, 3);// SW---PGND
	FPVI.AwgLoader("boost_rcs_pattern", FI, FPVIe_1V, FPVIe_10A, boost_rcs, sam);
	FPVI.AwgSelect("boost_rcs_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);


	TRIM_NODE &BOOST_RCS = trim_reg.trim("boost_rcs");
	//BOOST_RCS.disable_trim_step(2);
	//BOOST_RCS.disable_trim_step(3);
	//BOOST_RCS.disable_trim_step(4);
	BOOST_RCS.disable_trim_step(5);
	BOOST_RCS.disable_trim_step(6);
	BOOST_RCS.disable_trim_step(7);
	BOOST_RCS.force_table_char_active(true);
	BOOST_RCS.execute(measure_boost_rcs, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&BOOST_RCS, measure_boost_rcs, spec, funcindex, funclabel, 1, -1, -1, 6.9, false, 1);

	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(100);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);

	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	}
	else
	{
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	}

    return 0;
}
 
DUT_API int Trim_BUCK_HS_Gain(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BUCK_HS_Gain_step0 = StsGetParam(funcindex, "BUCK_HS_Gain_step0");
    CParam *BUCK_HS_Gain_step1 = StsGetParam(funcindex, "BUCK_HS_Gain_step1");
    CParam *BUCK_HS_Gain_step2 = StsGetParam(funcindex, "BUCK_HS_Gain_step2");
    CParam *BUCK_HS_Gain_step3 = StsGetParam(funcindex, "BUCK_HS_Gain_step3");
    CParam *BUCK_HS_Gain_step4 = StsGetParam(funcindex, "BUCK_HS_Gain_step4");
    CParam *BUCK_HS_Gain_step5 = StsGetParam(funcindex, "BUCK_HS_Gain_step5");
    CParam *BUCK_HS_Gain_step6 = StsGetParam(funcindex, "BUCK_HS_Gain_step6");
    CParam *BUCK_HS_Gain_step7 = StsGetParam(funcindex, "BUCK_HS_Gain_step7");
    CParam *BUCK_HS_Gain_step8 = StsGetParam(funcindex, "BUCK_HS_Gain_step8");
    CParam *BUCK_HS_Gain_step9 = StsGetParam(funcindex, "BUCK_HS_Gain_step9");
    CParam *BUCK_HS_Gain_step10 = StsGetParam(funcindex, "BUCK_HS_Gain_step10");
    CParam *BUCK_HS_Gain_step11 = StsGetParam(funcindex, "BUCK_HS_Gain_step11");
    CParam *BUCK_HS_Gain_step12 = StsGetParam(funcindex, "BUCK_HS_Gain_step12");
    CParam *BUCK_HS_Gain_step13 = StsGetParam(funcindex, "BUCK_HS_Gain_step13");
    CParam *BUCK_HS_Gain_step14 = StsGetParam(funcindex, "BUCK_HS_Gain_step14");
    CParam *BUCK_HS_Gain_step15 = StsGetParam(funcindex, "BUCK_HS_Gain_step15");
    CParam *BUCK_HS_Gain_step16 = StsGetParam(funcindex, "BUCK_HS_Gain_step16");
    CParam *BUCK_HS_Gain_step17 = StsGetParam(funcindex, "BUCK_HS_Gain_step17");
    CParam *BUCK_HS_Gain_step18 = StsGetParam(funcindex, "BUCK_HS_Gain_step18");
    CParam *BUCK_HS_Gain_step19 = StsGetParam(funcindex, "BUCK_HS_Gain_step19");
    CParam *BUCK_HS_Gain_step20 = StsGetParam(funcindex, "BUCK_HS_Gain_step20");
    CParam *BUCK_HS_Gain_step21 = StsGetParam(funcindex, "BUCK_HS_Gain_step21");
    CParam *BUCK_HS_Gain_step22 = StsGetParam(funcindex, "BUCK_HS_Gain_step22");
    CParam *BUCK_HS_Gain_step23 = StsGetParam(funcindex, "BUCK_HS_Gain_step23");
    CParam *BUCK_HS_Gain_step24 = StsGetParam(funcindex, "BUCK_HS_Gain_step24");
    CParam *BUCK_HS_Gain_step25 = StsGetParam(funcindex, "BUCK_HS_Gain_step25");
    CParam *BUCK_HS_Gain_step26 = StsGetParam(funcindex, "BUCK_HS_Gain_step26");
    CParam *BUCK_HS_Gain_step27 = StsGetParam(funcindex, "BUCK_HS_Gain_step27");
    CParam *BUCK_HS_Gain_step28 = StsGetParam(funcindex, "BUCK_HS_Gain_step28");
    CParam *BUCK_HS_Gain_step29 = StsGetParam(funcindex, "BUCK_HS_Gain_step29");
    CParam *BUCK_HS_Gain_step30 = StsGetParam(funcindex, "BUCK_HS_Gain_step30");
    CParam *BUCK_HS_Gain_step31 = StsGetParam(funcindex, "BUCK_HS_Gain_step31");
    CParam *BUCK_HS_Gain_pre_value = StsGetParam(funcindex, "BUCK_HS_Gain_pre_value");
    CParam *BUCK_HS_Gain_pre_bit = StsGetParam(funcindex, "BUCK_HS_Gain_pre_bit");
    CParam *BUCK_HS_Gain_post_bit = StsGetParam(funcindex, "BUCK_HS_Gain_post_bit");
    CParam *BUCK_HS_Gain_updated = StsGetParam(funcindex, "BUCK_HS_Gain_updated");
    CParam *BUCK_HS_Gain_guessed = StsGetParam(funcindex, "BUCK_HS_Gain_guessed");
    CParam *BUCK_HS_Gain_target = StsGetParam(funcindex, "BUCK_HS_Gain_target");
    CParam *BUCK_HS_Gain_post_value = StsGetParam(funcindex, "BUCK_HS_Gain_post_value");
    CParam *BUCK_HS_Gain_post_rt = StsGetParam(funcindex, "BUCK_HS_Gain_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	//DWORD working_value2[SITE_NUM] = { 0 };
	//FOR_EACH_VALID_SITE(site)
	//{
	//	working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_FF").get_working(site);
	//}

	//--------PMID--->SW
	cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap,-1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
	ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
	entertestmode();
	//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,0),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
	Inherit_register();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_ms(2);
	TRIM_NODE &BUCK_HSFFET_GAIN = trim_reg.trim("buck_hsfet_gain");
	BUCK_HSFFET_GAIN.execute(measure_buck_hsfet_gain, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&BUCK_HSFFET_GAIN, measure_buck_hsfet_gain, spec, funcindex, funclabel, 1.0, 1, 1, 2.2, false, 0.9);

	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);

		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		ATEST_GRP.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}

    return 0;
}
 
DUT_API int Trim_CS_HS_Offset(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *CS_HS_OS_step0 = StsGetParam(funcindex, "CS_HS_OS_step0");
    CParam *CS_HS_OS_step1 = StsGetParam(funcindex, "CS_HS_OS_step1");
    CParam *CS_HS_OS_step2 = StsGetParam(funcindex, "CS_HS_OS_step2");
    CParam *CS_HS_OS_step3 = StsGetParam(funcindex, "CS_HS_OS_step3");
    CParam *CS_HS_OS_step4 = StsGetParam(funcindex, "CS_HS_OS_step4");
    CParam *CS_HS_OS_step5 = StsGetParam(funcindex, "CS_HS_OS_step5");
    CParam *CS_HS_OS_step6 = StsGetParam(funcindex, "CS_HS_OS_step6");
    CParam *CS_HS_OS_step7 = StsGetParam(funcindex, "CS_HS_OS_step7");
    CParam *CS_HS_OS_step8 = StsGetParam(funcindex, "CS_HS_OS_step8");
    CParam *CS_HS_OS_step9 = StsGetParam(funcindex, "CS_HS_OS_step9");
    CParam *CS_HS_OS_step10 = StsGetParam(funcindex, "CS_HS_OS_step10");
    CParam *CS_HS_OS_step11 = StsGetParam(funcindex, "CS_HS_OS_step11");
    CParam *CS_HS_OS_step12 = StsGetParam(funcindex, "CS_HS_OS_step12");
    CParam *CS_HS_OS_step13 = StsGetParam(funcindex, "CS_HS_OS_step13");
    CParam *CS_HS_OS_step14 = StsGetParam(funcindex, "CS_HS_OS_step14");
    CParam *CS_HS_OS_step15 = StsGetParam(funcindex, "CS_HS_OS_step15");
    CParam *CS_HS_OS_step16 = StsGetParam(funcindex, "CS_HS_OS_step16");
    CParam *CS_HS_OS_step17 = StsGetParam(funcindex, "CS_HS_OS_step17");
    CParam *CS_HS_OS_step18 = StsGetParam(funcindex, "CS_HS_OS_step18");
    CParam *CS_HS_OS_step19 = StsGetParam(funcindex, "CS_HS_OS_step19");
    CParam *CS_HS_OS_step20 = StsGetParam(funcindex, "CS_HS_OS_step20");
    CParam *CS_HS_OS_step21 = StsGetParam(funcindex, "CS_HS_OS_step21");
    CParam *CS_HS_OS_step22 = StsGetParam(funcindex, "CS_HS_OS_step22");
    CParam *CS_HS_OS_step23 = StsGetParam(funcindex, "CS_HS_OS_step23");
    CParam *CS_HS_OS_step24 = StsGetParam(funcindex, "CS_HS_OS_step24");
    CParam *CS_HS_OS_step25 = StsGetParam(funcindex, "CS_HS_OS_step25");
    CParam *CS_HS_OS_step26 = StsGetParam(funcindex, "CS_HS_OS_step26");
    CParam *CS_HS_OS_step27 = StsGetParam(funcindex, "CS_HS_OS_step27");
    CParam *CS_HS_OS_step28 = StsGetParam(funcindex, "CS_HS_OS_step28");
    CParam *CS_HS_OS_step29 = StsGetParam(funcindex, "CS_HS_OS_step29");
    CParam *CS_HS_OS_step30 = StsGetParam(funcindex, "CS_HS_OS_step30");
    CParam *CS_HS_OS_step31 = StsGetParam(funcindex, "CS_HS_OS_step31");
    CParam *CS_HS_OS_step32 = StsGetParam(funcindex, "CS_HS_OS_step32");
    CParam *CS_HS_OS_step33 = StsGetParam(funcindex, "CS_HS_OS_step33");
    CParam *CS_HS_OS_step34 = StsGetParam(funcindex, "CS_HS_OS_step34");
    CParam *CS_HS_OS_step35 = StsGetParam(funcindex, "CS_HS_OS_step35");
    CParam *CS_HS_OS_step36 = StsGetParam(funcindex, "CS_HS_OS_step36");
    CParam *CS_HS_OS_step37 = StsGetParam(funcindex, "CS_HS_OS_step37");
    CParam *CS_HS_OS_step38 = StsGetParam(funcindex, "CS_HS_OS_step38");
    CParam *CS_HS_OS_step39 = StsGetParam(funcindex, "CS_HS_OS_step39");
    CParam *CS_HS_OS_step40 = StsGetParam(funcindex, "CS_HS_OS_step40");
    CParam *CS_HS_OS_step41 = StsGetParam(funcindex, "CS_HS_OS_step41");
    CParam *CS_HS_OS_step42 = StsGetParam(funcindex, "CS_HS_OS_step42");
    CParam *CS_HS_OS_step43 = StsGetParam(funcindex, "CS_HS_OS_step43");
    CParam *CS_HS_OS_step44 = StsGetParam(funcindex, "CS_HS_OS_step44");
    CParam *CS_HS_OS_step45 = StsGetParam(funcindex, "CS_HS_OS_step45");
    CParam *CS_HS_OS_step46 = StsGetParam(funcindex, "CS_HS_OS_step46");
    CParam *CS_HS_OS_step47 = StsGetParam(funcindex, "CS_HS_OS_step47");
    CParam *CS_HS_OS_step48 = StsGetParam(funcindex, "CS_HS_OS_step48");
    CParam *CS_HS_OS_step49 = StsGetParam(funcindex, "CS_HS_OS_step49");
    CParam *CS_HS_OS_step50 = StsGetParam(funcindex, "CS_HS_OS_step50");
    CParam *CS_HS_OS_step51 = StsGetParam(funcindex, "CS_HS_OS_step51");
    CParam *CS_HS_OS_step52 = StsGetParam(funcindex, "CS_HS_OS_step52");
    CParam *CS_HS_OS_step53 = StsGetParam(funcindex, "CS_HS_OS_step53");
    CParam *CS_HS_OS_step54 = StsGetParam(funcindex, "CS_HS_OS_step54");
    CParam *CS_HS_OS_step55 = StsGetParam(funcindex, "CS_HS_OS_step55");
    CParam *CS_HS_OS_step56 = StsGetParam(funcindex, "CS_HS_OS_step56");
    CParam *CS_HS_OS_step57 = StsGetParam(funcindex, "CS_HS_OS_step57");
    CParam *CS_HS_OS_step58 = StsGetParam(funcindex, "CS_HS_OS_step58");
    CParam *CS_HS_OS_step59 = StsGetParam(funcindex, "CS_HS_OS_step59");
    CParam *CS_HS_OS_step60 = StsGetParam(funcindex, "CS_HS_OS_step60");
    CParam *CS_HS_OS_step61 = StsGetParam(funcindex, "CS_HS_OS_step61");
    CParam *CS_HS_OS_step62 = StsGetParam(funcindex, "CS_HS_OS_step62");
    CParam *CS_HS_OS_step63 = StsGetParam(funcindex, "CS_HS_OS_step63");
    CParam *CS_HS_OS_pre_value = StsGetParam(funcindex, "CS_HS_OS_pre_value");
    CParam *CS_HS_OS_pre_bit = StsGetParam(funcindex, "CS_HS_OS_pre_bit");
    CParam *CS_HS_OS_post_bit = StsGetParam(funcindex, "CS_HS_OS_post_bit");
    CParam *CS_HS_OS_updated = StsGetParam(funcindex, "CS_HS_OS_updated");
    CParam *CS_HS_OS_guessed = StsGetParam(funcindex, "CS_HS_OS_guessed");
    CParam *CS_HS_OS_target = StsGetParam(funcindex, "CS_HS_OS_target");
    CParam *CS_HS_OS_post_value = StsGetParam(funcindex, "CS_HS_OS_post_value");
    CParam *CS_HS_OS_post_rt = StsGetParam(funcindex, "CS_HS_OS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
		ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
		//field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_SLP,1),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,15),(D2A_BUBO_ATEST1,10),(DIS_NTC_DETECTION_ANALOG,1)]
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0xAF);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
		Inherit_register();
		delay_ms(1);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_ON);
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x5A, 0xAF);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
		delay_ms(1);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_ON);
	}

	TRIM_NODE &CS_HSFFET_OS = trim_reg.trim("cs_hsfet_os");
	CS_HSFFET_OS.execute(measure_cs_hsfet_os, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&CS_HSFFET_OS, measure_cs_hsfet_os, spec, funcindex, funclabel, 1.0, 1, -1, 9, true, 1.0);

	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_ON);// PMID=SW

	if (!TTR)
	{
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);

		ATEST_GRP.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}

	return 0;
}

DUT_API int Trim_BUCK_HS_Offset(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BUCK_HS_OS_step0 = StsGetParam(funcindex, "BUCK_HS_OS_step0");
    CParam *BUCK_HS_OS_step1 = StsGetParam(funcindex, "BUCK_HS_OS_step1");
    CParam *BUCK_HS_OS_step2 = StsGetParam(funcindex, "BUCK_HS_OS_step2");
    CParam *BUCK_HS_OS_step3 = StsGetParam(funcindex, "BUCK_HS_OS_step3");
    CParam *BUCK_HS_OS_step4 = StsGetParam(funcindex, "BUCK_HS_OS_step4");
    CParam *BUCK_HS_OS_step5 = StsGetParam(funcindex, "BUCK_HS_OS_step5");
    CParam *BUCK_HS_OS_step6 = StsGetParam(funcindex, "BUCK_HS_OS_step6");
    CParam *BUCK_HS_OS_step7 = StsGetParam(funcindex, "BUCK_HS_OS_step7");
    CParam *BUCK_HS_OS_step8 = StsGetParam(funcindex, "BUCK_HS_OS_step8");
    CParam *BUCK_HS_OS_step9 = StsGetParam(funcindex, "BUCK_HS_OS_step9");
    CParam *BUCK_HS_OS_step10 = StsGetParam(funcindex, "BUCK_HS_OS_step10");
    CParam *BUCK_HS_OS_step11 = StsGetParam(funcindex, "BUCK_HS_OS_step11");
    CParam *BUCK_HS_OS_step12 = StsGetParam(funcindex, "BUCK_HS_OS_step12");
    CParam *BUCK_HS_OS_step13 = StsGetParam(funcindex, "BUCK_HS_OS_step13");
    CParam *BUCK_HS_OS_step14 = StsGetParam(funcindex, "BUCK_HS_OS_step14");
    CParam *BUCK_HS_OS_step15 = StsGetParam(funcindex, "BUCK_HS_OS_step15");
    CParam *BUCK_HS_OS_pre_value = StsGetParam(funcindex, "BUCK_HS_OS_pre_value");
    CParam *BUCK_HS_OS_pre_bit = StsGetParam(funcindex, "BUCK_HS_OS_pre_bit");
    CParam *BUCK_HS_OS_post_bit = StsGetParam(funcindex, "BUCK_HS_OS_post_bit");
    CParam *BUCK_HS_OS_updated = StsGetParam(funcindex, "BUCK_HS_OS_updated");
    CParam *BUCK_HS_OS_guessed = StsGetParam(funcindex, "BUCK_HS_OS_guessed");
    CParam *BUCK_HS_OS_target = StsGetParam(funcindex, "BUCK_HS_OS_target");
    CParam *BUCK_HS_OS_post_value = StsGetParam(funcindex, "BUCK_HS_OS_post_value");
    CParam *BUCK_HS_OS_post_rt = StsGetParam(funcindex, "BUCK_HS_OS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	//--------PMID--->SW
	//--------PMID--->SW
	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		if (V_TYP_VBAT > 4)
		{
			VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		else
		{
			VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
		ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		entertestmode();
		//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,0),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
		Inherit_register();
		delay_ms(5);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(1);
	}
	//double Vsense1[SITE_NUM] = { 0 };
	//double Imeas1[SITE_NUM] = { 0 };
	//double results[SITE_NUM] = { 0 };
	//double forcecurr = -0.5;

	//FPVI.Set(FI, forcecurr, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);////PMID--->SW
	//delay_us(2000);
	//ATEST_GRP.MeasureVI(215, 10);
	//FPVI.MeasureVI(20, 5);
	//FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	//delay_ms(1);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	//	Imeas1[site] = abs(FPVI.GetMeasResult(site, MIRET));
	//	results[site] = 1e3*(Vsense1[site] - Imeas1[site] * BUCK_IBAT_HS_Gain[site] / 1e3);	//mV
	//}


	TRIM_NODE &BUCK_HSFFET_OS = trim_reg.trim("buck_hsfet_os");
	BUCK_HSFFET_OS.execute(measure_buck_hsfet_os, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&BUCK_HSFFET_OS, measure_buck_hsfet_os, spec, funcindex, funclabel, 1.0, -1, 1, 8, false, 1.0);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	if (!TTR)
	{
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);

		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		ATEST_GRP.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}



    return 0;
}
 
DUT_API int Trim_BOOST_HS_Gain(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BOOST_HS_Gain_step0 = StsGetParam(funcindex, "BOOST_HS_Gain_step0");
    CParam *BOOST_HS_Gain_step1 = StsGetParam(funcindex, "BOOST_HS_Gain_step1");
    CParam *BOOST_HS_Gain_step2 = StsGetParam(funcindex, "BOOST_HS_Gain_step2");
    CParam *BOOST_HS_Gain_step3 = StsGetParam(funcindex, "BOOST_HS_Gain_step3");
    CParam *BOOST_HS_Gain_step4 = StsGetParam(funcindex, "BOOST_HS_Gain_step4");
    CParam *BOOST_HS_Gain_step5 = StsGetParam(funcindex, "BOOST_HS_Gain_step5");
    CParam *BOOST_HS_Gain_step6 = StsGetParam(funcindex, "BOOST_HS_Gain_step6");
    CParam *BOOST_HS_Gain_step7 = StsGetParam(funcindex, "BOOST_HS_Gain_step7");
    CParam *BOOST_HS_Gain_step8 = StsGetParam(funcindex, "BOOST_HS_Gain_step8");
    CParam *BOOST_HS_Gain_step9 = StsGetParam(funcindex, "BOOST_HS_Gain_step9");
    CParam *BOOST_HS_Gain_step10 = StsGetParam(funcindex, "BOOST_HS_Gain_step10");
    CParam *BOOST_HS_Gain_step11 = StsGetParam(funcindex, "BOOST_HS_Gain_step11");
    CParam *BOOST_HS_Gain_step12 = StsGetParam(funcindex, "BOOST_HS_Gain_step12");
    CParam *BOOST_HS_Gain_step13 = StsGetParam(funcindex, "BOOST_HS_Gain_step13");
    CParam *BOOST_HS_Gain_step14 = StsGetParam(funcindex, "BOOST_HS_Gain_step14");
    CParam *BOOST_HS_Gain_step15 = StsGetParam(funcindex, "BOOST_HS_Gain_step15");
    CParam *BOOST_HS_Gain_step16 = StsGetParam(funcindex, "BOOST_HS_Gain_step16");
    CParam *BOOST_HS_Gain_step17 = StsGetParam(funcindex, "BOOST_HS_Gain_step17");
    CParam *BOOST_HS_Gain_step18 = StsGetParam(funcindex, "BOOST_HS_Gain_step18");
    CParam *BOOST_HS_Gain_step19 = StsGetParam(funcindex, "BOOST_HS_Gain_step19");
    CParam *BOOST_HS_Gain_step20 = StsGetParam(funcindex, "BOOST_HS_Gain_step20");
    CParam *BOOST_HS_Gain_step21 = StsGetParam(funcindex, "BOOST_HS_Gain_step21");
    CParam *BOOST_HS_Gain_step22 = StsGetParam(funcindex, "BOOST_HS_Gain_step22");
    CParam *BOOST_HS_Gain_step23 = StsGetParam(funcindex, "BOOST_HS_Gain_step23");
    CParam *BOOST_HS_Gain_step24 = StsGetParam(funcindex, "BOOST_HS_Gain_step24");
    CParam *BOOST_HS_Gain_step25 = StsGetParam(funcindex, "BOOST_HS_Gain_step25");
    CParam *BOOST_HS_Gain_step26 = StsGetParam(funcindex, "BOOST_HS_Gain_step26");
    CParam *BOOST_HS_Gain_step27 = StsGetParam(funcindex, "BOOST_HS_Gain_step27");
    CParam *BOOST_HS_Gain_step28 = StsGetParam(funcindex, "BOOST_HS_Gain_step28");
    CParam *BOOST_HS_Gain_step29 = StsGetParam(funcindex, "BOOST_HS_Gain_step29");
    CParam *BOOST_HS_Gain_step30 = StsGetParam(funcindex, "BOOST_HS_Gain_step30");
    CParam *BOOST_HS_Gain_step31 = StsGetParam(funcindex, "BOOST_HS_Gain_step31");
    CParam *BOOST_HS_Gain_pre_value = StsGetParam(funcindex, "BOOST_HS_Gain_pre_value");
    CParam *BOOST_HS_Gain_pre_bit = StsGetParam(funcindex, "BOOST_HS_Gain_pre_bit");
    CParam *BOOST_HS_Gain_post_bit = StsGetParam(funcindex, "BOOST_HS_Gain_post_bit");
    CParam *BOOST_HS_Gain_updated = StsGetParam(funcindex, "BOOST_HS_Gain_updated");
    CParam *BOOST_HS_Gain_guessed = StsGetParam(funcindex, "BOOST_HS_Gain_guessed");
    CParam *BOOST_HS_Gain_target = StsGetParam(funcindex, "BOOST_HS_Gain_target");
    CParam *BOOST_HS_Gain_post_value = StsGetParam(funcindex, "BOOST_HS_Gain_post_value");
    CParam *BOOST_HS_Gain_post_rt = StsGetParam(funcindex, "BOOST_HS_Gain_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	//--------SW--->PMID
	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		if (V_TYP_VBAT > 4)
		{
			VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		else
		{
			VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
		ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		entertestmode();
		//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,1),(FPWM_EN,1)(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
		I2CWriteSameData(DEV_ADDR, 0x09, 0x19);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//D2A_BUBO_DIS_CLK=0
		I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
		Inherit_register();
		delay_ms(5);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x09, 0x19);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//D2A_BUBO_DIS_CLK=0
		I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
		delay_ms(1);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	}

	TRIM_NODE &BOOST_HSFFET_GAIN = trim_reg.trim("boost_hsfet_gain");
	BOOST_HSFFET_GAIN.execute(measure_boost_hsfet_gain, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&BOOST_HSFFET_GAIN, measure_boost_hsfet_gain, spec, funcindex, funclabel, 1.0, 1, 1, 2.2, false, 0.9);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	if (!TTR)
	{
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		ATEST_GRP.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}


    return 0;
}
 
DUT_API int Trim_BOOST_HS_Offset(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BOOST_HS_OS_step0 = StsGetParam(funcindex, "BOOST_HS_OS_step0");
    CParam *BOOST_HS_OS_step1 = StsGetParam(funcindex, "BOOST_HS_OS_step1");
    CParam *BOOST_HS_OS_step2 = StsGetParam(funcindex, "BOOST_HS_OS_step2");
    CParam *BOOST_HS_OS_step3 = StsGetParam(funcindex, "BOOST_HS_OS_step3");
    CParam *BOOST_HS_OS_step4 = StsGetParam(funcindex, "BOOST_HS_OS_step4");
    CParam *BOOST_HS_OS_step5 = StsGetParam(funcindex, "BOOST_HS_OS_step5");
    CParam *BOOST_HS_OS_step6 = StsGetParam(funcindex, "BOOST_HS_OS_step6");
    CParam *BOOST_HS_OS_step7 = StsGetParam(funcindex, "BOOST_HS_OS_step7");
    CParam *BOOST_HS_OS_step8 = StsGetParam(funcindex, "BOOST_HS_OS_step8");
    CParam *BOOST_HS_OS_step9 = StsGetParam(funcindex, "BOOST_HS_OS_step9");
    CParam *BOOST_HS_OS_step10 = StsGetParam(funcindex, "BOOST_HS_OS_step10");
    CParam *BOOST_HS_OS_step11 = StsGetParam(funcindex, "BOOST_HS_OS_step11");
    CParam *BOOST_HS_OS_step12 = StsGetParam(funcindex, "BOOST_HS_OS_step12");
    CParam *BOOST_HS_OS_step13 = StsGetParam(funcindex, "BOOST_HS_OS_step13");
    CParam *BOOST_HS_OS_step14 = StsGetParam(funcindex, "BOOST_HS_OS_step14");
    CParam *BOOST_HS_OS_step15 = StsGetParam(funcindex, "BOOST_HS_OS_step15");
    CParam *BOOST_HS_OS_pre_value = StsGetParam(funcindex, "BOOST_HS_OS_pre_value");
    CParam *BOOST_HS_OS_pre_bit = StsGetParam(funcindex, "BOOST_HS_OS_pre_bit");
    CParam *BOOST_HS_OS_post_bit = StsGetParam(funcindex, "BOOST_HS_OS_post_bit");
    CParam *BOOST_HS_OS_updated = StsGetParam(funcindex, "BOOST_HS_OS_updated");
    CParam *BOOST_HS_OS_guessed = StsGetParam(funcindex, "BOOST_HS_OS_guessed");
    CParam *BOOST_HS_OS_target = StsGetParam(funcindex, "BOOST_HS_OS_target");
    CParam *BOOST_HS_OS_post_value = StsGetParam(funcindex, "BOOST_HS_OS_post_value");
    CParam *BOOST_HS_OS_post_rt = StsGetParam(funcindex, "BOOST_HS_OS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	if (!TTR)
	{
		//--------SW--->PMID
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		if (V_TYP_VBAT > 4)
		{
			VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		else
		{
			VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
		ATEST_GRP.Set(FI, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
		entertestmode();
		//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,1),(FPWM_EN,1)(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
		I2CWriteSameData(DEV_ADDR, 0x09, 0x19);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//D2A_BUBO_DIS_CLK=0
		I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
		Inherit_register();
		delay_ms(2);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(5);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	}

	delay_ms(1);
	TRIM_NODE &BOOST_HSFFET_OS = trim_reg.trim("boost_hsfet_os");
	BOOST_HSFFET_OS.execute(measure_boost_hsfet_os, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&BOOST_HSFFET_OS, measure_boost_hsfet_os, spec, funcindex, funclabel, 1.0, -1, 1, 8, false, 1.0);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	//FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);

	BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	ATEST_GRP.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW

	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
	BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
	ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);


    return 0;
}
 
DUT_API int Trim_BUCK_LS_Gain(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BUCK_LS_Gain_step0 = StsGetParam(funcindex, "BUCK_LS_Gain_step0");
    CParam *BUCK_LS_Gain_step1 = StsGetParam(funcindex, "BUCK_LS_Gain_step1");
    CParam *BUCK_LS_Gain_step2 = StsGetParam(funcindex, "BUCK_LS_Gain_step2");
    CParam *BUCK_LS_Gain_step3 = StsGetParam(funcindex, "BUCK_LS_Gain_step3");
    CParam *BUCK_LS_Gain_step4 = StsGetParam(funcindex, "BUCK_LS_Gain_step4");
    CParam *BUCK_LS_Gain_step5 = StsGetParam(funcindex, "BUCK_LS_Gain_step5");
    CParam *BUCK_LS_Gain_step6 = StsGetParam(funcindex, "BUCK_LS_Gain_step6");
    CParam *BUCK_LS_Gain_step7 = StsGetParam(funcindex, "BUCK_LS_Gain_step7");
    CParam *BUCK_LS_Gain_step8 = StsGetParam(funcindex, "BUCK_LS_Gain_step8");
    CParam *BUCK_LS_Gain_step9 = StsGetParam(funcindex, "BUCK_LS_Gain_step9");
    CParam *BUCK_LS_Gain_step10 = StsGetParam(funcindex, "BUCK_LS_Gain_step10");
    CParam *BUCK_LS_Gain_step11 = StsGetParam(funcindex, "BUCK_LS_Gain_step11");
    CParam *BUCK_LS_Gain_step12 = StsGetParam(funcindex, "BUCK_LS_Gain_step12");
    CParam *BUCK_LS_Gain_step13 = StsGetParam(funcindex, "BUCK_LS_Gain_step13");
    CParam *BUCK_LS_Gain_step14 = StsGetParam(funcindex, "BUCK_LS_Gain_step14");
    CParam *BUCK_LS_Gain_step15 = StsGetParam(funcindex, "BUCK_LS_Gain_step15");
    CParam *BUCK_LS_Gain_step16 = StsGetParam(funcindex, "BUCK_LS_Gain_step16");
    CParam *BUCK_LS_Gain_step17 = StsGetParam(funcindex, "BUCK_LS_Gain_step17");
    CParam *BUCK_LS_Gain_step18 = StsGetParam(funcindex, "BUCK_LS_Gain_step18");
    CParam *BUCK_LS_Gain_step19 = StsGetParam(funcindex, "BUCK_LS_Gain_step19");
    CParam *BUCK_LS_Gain_step20 = StsGetParam(funcindex, "BUCK_LS_Gain_step20");
    CParam *BUCK_LS_Gain_step21 = StsGetParam(funcindex, "BUCK_LS_Gain_step21");
    CParam *BUCK_LS_Gain_step22 = StsGetParam(funcindex, "BUCK_LS_Gain_step22");
    CParam *BUCK_LS_Gain_step23 = StsGetParam(funcindex, "BUCK_LS_Gain_step23");
    CParam *BUCK_LS_Gain_step24 = StsGetParam(funcindex, "BUCK_LS_Gain_step24");
    CParam *BUCK_LS_Gain_step25 = StsGetParam(funcindex, "BUCK_LS_Gain_step25");
    CParam *BUCK_LS_Gain_step26 = StsGetParam(funcindex, "BUCK_LS_Gain_step26");
    CParam *BUCK_LS_Gain_step27 = StsGetParam(funcindex, "BUCK_LS_Gain_step27");
    CParam *BUCK_LS_Gain_step28 = StsGetParam(funcindex, "BUCK_LS_Gain_step28");
    CParam *BUCK_LS_Gain_step29 = StsGetParam(funcindex, "BUCK_LS_Gain_step29");
    CParam *BUCK_LS_Gain_step30 = StsGetParam(funcindex, "BUCK_LS_Gain_step30");
    CParam *BUCK_LS_Gain_step31 = StsGetParam(funcindex, "BUCK_LS_Gain_step31");
    CParam *BUCK_LS_Gain_pre_value = StsGetParam(funcindex, "BUCK_LS_Gain_pre_value");
    CParam *BUCK_LS_Gain_pre_bit = StsGetParam(funcindex, "BUCK_LS_Gain_pre_bit");
    CParam *BUCK_LS_Gain_post_bit = StsGetParam(funcindex, "BUCK_LS_Gain_post_bit");
    CParam *BUCK_LS_Gain_updated = StsGetParam(funcindex, "BUCK_LS_Gain_updated");
    CParam *BUCK_LS_Gain_guessed = StsGetParam(funcindex, "BUCK_LS_Gain_guessed");
    CParam *BUCK_LS_Gain_target = StsGetParam(funcindex, "BUCK_LS_Gain_target");
    CParam *BUCK_LS_Gain_post_value = StsGetParam(funcindex, "BUCK_LS_Gain_post_value");
    CParam *BUCK_LS_Gain_post_rt = StsGetParam(funcindex, "BUCK_LS_Gain_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	//--------PGND--->SW
	cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K33_BUSL_PGND, K30_VBAT_Cap, K32_PMID_Cap,K25_VCC_Cap, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x81);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
	//		field[(WAKE_UP,1),(D2A_BUBO_TM_LSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,0),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
	Inherit_register();
	delay_ms(2);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);

	TRIM_NODE &BUCK_LSFFET_GAIN = trim_reg.trim("buck_lsfet_gain");
	BUCK_LSFFET_GAIN.execute(measure_buck_lsfet_gain, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&BUCK_LSFFET_GAIN, measure_buck_lsfet_gain,spec,funcindex,funclabel,1.0,1, 1, 2.2, false, 0.9);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW
		cbite.SetOn(-1);
		delay_ms(3);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
    return 0;
}
 
DUT_API int Trim_CS_LS_Offset(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *CS_LS_OS_step0 = StsGetParam(funcindex, "CS_LS_OS_step0");
    CParam *CS_LS_OS_step1 = StsGetParam(funcindex, "CS_LS_OS_step1");
    CParam *CS_LS_OS_step2 = StsGetParam(funcindex, "CS_LS_OS_step2");
    CParam *CS_LS_OS_step3 = StsGetParam(funcindex, "CS_LS_OS_step3");
    CParam *CS_LS_OS_step4 = StsGetParam(funcindex, "CS_LS_OS_step4");
    CParam *CS_LS_OS_step5 = StsGetParam(funcindex, "CS_LS_OS_step5");
    CParam *CS_LS_OS_step6 = StsGetParam(funcindex, "CS_LS_OS_step6");
    CParam *CS_LS_OS_step7 = StsGetParam(funcindex, "CS_LS_OS_step7");
    CParam *CS_LS_OS_step8 = StsGetParam(funcindex, "CS_LS_OS_step8");
    CParam *CS_LS_OS_step9 = StsGetParam(funcindex, "CS_LS_OS_step9");
    CParam *CS_LS_OS_step10 = StsGetParam(funcindex, "CS_LS_OS_step10");
    CParam *CS_LS_OS_step11 = StsGetParam(funcindex, "CS_LS_OS_step11");
    CParam *CS_LS_OS_step12 = StsGetParam(funcindex, "CS_LS_OS_step12");
    CParam *CS_LS_OS_step13 = StsGetParam(funcindex, "CS_LS_OS_step13");
    CParam *CS_LS_OS_step14 = StsGetParam(funcindex, "CS_LS_OS_step14");
    CParam *CS_LS_OS_step15 = StsGetParam(funcindex, "CS_LS_OS_step15");
    CParam *CS_LS_OS_step16 = StsGetParam(funcindex, "CS_LS_OS_step16");
    CParam *CS_LS_OS_step17 = StsGetParam(funcindex, "CS_LS_OS_step17");
    CParam *CS_LS_OS_step18 = StsGetParam(funcindex, "CS_LS_OS_step18");
    CParam *CS_LS_OS_step19 = StsGetParam(funcindex, "CS_LS_OS_step19");
    CParam *CS_LS_OS_step20 = StsGetParam(funcindex, "CS_LS_OS_step20");
    CParam *CS_LS_OS_step21 = StsGetParam(funcindex, "CS_LS_OS_step21");
    CParam *CS_LS_OS_step22 = StsGetParam(funcindex, "CS_LS_OS_step22");
    CParam *CS_LS_OS_step23 = StsGetParam(funcindex, "CS_LS_OS_step23");
    CParam *CS_LS_OS_step24 = StsGetParam(funcindex, "CS_LS_OS_step24");
    CParam *CS_LS_OS_step25 = StsGetParam(funcindex, "CS_LS_OS_step25");
    CParam *CS_LS_OS_step26 = StsGetParam(funcindex, "CS_LS_OS_step26");
    CParam *CS_LS_OS_step27 = StsGetParam(funcindex, "CS_LS_OS_step27");
    CParam *CS_LS_OS_step28 = StsGetParam(funcindex, "CS_LS_OS_step28");
    CParam *CS_LS_OS_step29 = StsGetParam(funcindex, "CS_LS_OS_step29");
    CParam *CS_LS_OS_step30 = StsGetParam(funcindex, "CS_LS_OS_step30");
    CParam *CS_LS_OS_step31 = StsGetParam(funcindex, "CS_LS_OS_step31");
    CParam *CS_LS_OS_step32 = StsGetParam(funcindex, "CS_LS_OS_step32");
    CParam *CS_LS_OS_step33 = StsGetParam(funcindex, "CS_LS_OS_step33");
    CParam *CS_LS_OS_step34 = StsGetParam(funcindex, "CS_LS_OS_step34");
    CParam *CS_LS_OS_step35 = StsGetParam(funcindex, "CS_LS_OS_step35");
    CParam *CS_LS_OS_step36 = StsGetParam(funcindex, "CS_LS_OS_step36");
    CParam *CS_LS_OS_step37 = StsGetParam(funcindex, "CS_LS_OS_step37");
    CParam *CS_LS_OS_step38 = StsGetParam(funcindex, "CS_LS_OS_step38");
    CParam *CS_LS_OS_step39 = StsGetParam(funcindex, "CS_LS_OS_step39");
    CParam *CS_LS_OS_step40 = StsGetParam(funcindex, "CS_LS_OS_step40");
    CParam *CS_LS_OS_step41 = StsGetParam(funcindex, "CS_LS_OS_step41");
    CParam *CS_LS_OS_step42 = StsGetParam(funcindex, "CS_LS_OS_step42");
    CParam *CS_LS_OS_step43 = StsGetParam(funcindex, "CS_LS_OS_step43");
    CParam *CS_LS_OS_step44 = StsGetParam(funcindex, "CS_LS_OS_step44");
    CParam *CS_LS_OS_step45 = StsGetParam(funcindex, "CS_LS_OS_step45");
    CParam *CS_LS_OS_step46 = StsGetParam(funcindex, "CS_LS_OS_step46");
    CParam *CS_LS_OS_step47 = StsGetParam(funcindex, "CS_LS_OS_step47");
    CParam *CS_LS_OS_step48 = StsGetParam(funcindex, "CS_LS_OS_step48");
    CParam *CS_LS_OS_step49 = StsGetParam(funcindex, "CS_LS_OS_step49");
    CParam *CS_LS_OS_step50 = StsGetParam(funcindex, "CS_LS_OS_step50");
    CParam *CS_LS_OS_step51 = StsGetParam(funcindex, "CS_LS_OS_step51");
    CParam *CS_LS_OS_step52 = StsGetParam(funcindex, "CS_LS_OS_step52");
    CParam *CS_LS_OS_step53 = StsGetParam(funcindex, "CS_LS_OS_step53");
    CParam *CS_LS_OS_step54 = StsGetParam(funcindex, "CS_LS_OS_step54");
    CParam *CS_LS_OS_step55 = StsGetParam(funcindex, "CS_LS_OS_step55");
    CParam *CS_LS_OS_step56 = StsGetParam(funcindex, "CS_LS_OS_step56");
    CParam *CS_LS_OS_step57 = StsGetParam(funcindex, "CS_LS_OS_step57");
    CParam *CS_LS_OS_step58 = StsGetParam(funcindex, "CS_LS_OS_step58");
    CParam *CS_LS_OS_step59 = StsGetParam(funcindex, "CS_LS_OS_step59");
    CParam *CS_LS_OS_step60 = StsGetParam(funcindex, "CS_LS_OS_step60");
    CParam *CS_LS_OS_step61 = StsGetParam(funcindex, "CS_LS_OS_step61");
    CParam *CS_LS_OS_step62 = StsGetParam(funcindex, "CS_LS_OS_step62");
    CParam *CS_LS_OS_step63 = StsGetParam(funcindex, "CS_LS_OS_step63");
    CParam *CS_LS_OS_pre_value = StsGetParam(funcindex, "CS_LS_OS_pre_value");
    CParam *CS_LS_OS_pre_bit = StsGetParam(funcindex, "CS_LS_OS_pre_bit");
    CParam *CS_LS_OS_post_bit = StsGetParam(funcindex, "CS_LS_OS_post_bit");
    CParam *CS_LS_OS_updated = StsGetParam(funcindex, "CS_LS_OS_updated");
    CParam *CS_LS_OS_guessed = StsGetParam(funcindex, "CS_LS_OS_guessed");
    CParam *CS_LS_OS_target = StsGetParam(funcindex, "CS_LS_OS_target");
    CParam *CS_LS_OS_post_value = StsGetParam(funcindex, "CS_LS_OS_post_value");
    CParam *CS_LS_OS_post_rt = StsGetParam(funcindex, "CS_LS_OS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	if (!TTR)
	{
		clear_resource();
		cbite.SetOn(K17_BUSH_SW, K33_BUSL_PGND, K30_VBAT_Cap, K32_PMID_Cap, -1);
		delay_ms(3);
		//FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);//5V
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x81);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0xAF);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
		//		field[(WAKE_UP,1),(D2A_BUBO_TM_LSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1),(D2A_BUBO_ATEST0,15),(D2A_BUBO_ATEST1,10),(DIS_NTC_DETECTION_ANALOG,1)]
		Inherit_register();
		I2CWriteSameData(DEV_ADDR, 0x5A, 0xAF);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
		delay_ms(1);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_ON);
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x81);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0xAF);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
		//		field[(WAKE_UP,1),(D2A_BUBO_TM_LSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1),(D2A_BUBO_ATEST0,15),(D2A_BUBO_ATEST1,10),(DIS_NTC_DETECTION_ANALOG,1)]
		delay_ms(1);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_ON);
	}

	TRIM_NODE &CS_LSFFET_OS = trim_reg.trim("cs_lsfet_os");
	CS_LSFFET_OS.execute(measure_cs_lsfet_os, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&CS_LSFFET_OS, measure_cs_lsfet_os, spec, funcindex, funclabel, 1.0, 1, -1, 11, true, 1.0);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_ON);
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}


	return 0;
}

DUT_API int Trim_BUCK_LS_Offset(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BUCK_LS_OS_step0 = StsGetParam(funcindex, "BUCK_LS_OS_step0");
    CParam *BUCK_LS_OS_step1 = StsGetParam(funcindex, "BUCK_LS_OS_step1");
    CParam *BUCK_LS_OS_step2 = StsGetParam(funcindex, "BUCK_LS_OS_step2");
    CParam *BUCK_LS_OS_step3 = StsGetParam(funcindex, "BUCK_LS_OS_step3");
    CParam *BUCK_LS_OS_step4 = StsGetParam(funcindex, "BUCK_LS_OS_step4");
    CParam *BUCK_LS_OS_step5 = StsGetParam(funcindex, "BUCK_LS_OS_step5");
    CParam *BUCK_LS_OS_step6 = StsGetParam(funcindex, "BUCK_LS_OS_step6");
    CParam *BUCK_LS_OS_step7 = StsGetParam(funcindex, "BUCK_LS_OS_step7");
    CParam *BUCK_LS_OS_step8 = StsGetParam(funcindex, "BUCK_LS_OS_step8");
    CParam *BUCK_LS_OS_step9 = StsGetParam(funcindex, "BUCK_LS_OS_step9");
    CParam *BUCK_LS_OS_step10 = StsGetParam(funcindex, "BUCK_LS_OS_step10");
    CParam *BUCK_LS_OS_step11 = StsGetParam(funcindex, "BUCK_LS_OS_step11");
    CParam *BUCK_LS_OS_step12 = StsGetParam(funcindex, "BUCK_LS_OS_step12");
    CParam *BUCK_LS_OS_step13 = StsGetParam(funcindex, "BUCK_LS_OS_step13");
    CParam *BUCK_LS_OS_step14 = StsGetParam(funcindex, "BUCK_LS_OS_step14");
    CParam *BUCK_LS_OS_step15 = StsGetParam(funcindex, "BUCK_LS_OS_step15");
    CParam *BUCK_LS_OS_pre_value = StsGetParam(funcindex, "BUCK_LS_OS_pre_value");
    CParam *BUCK_LS_OS_pre_bit = StsGetParam(funcindex, "BUCK_LS_OS_pre_bit");
    CParam *BUCK_LS_OS_post_bit = StsGetParam(funcindex, "BUCK_LS_OS_post_bit");
    CParam *BUCK_LS_OS_updated = StsGetParam(funcindex, "BUCK_LS_OS_updated");
    CParam *BUCK_LS_OS_guessed = StsGetParam(funcindex, "BUCK_LS_OS_guessed");
    CParam *BUCK_LS_OS_target = StsGetParam(funcindex, "BUCK_LS_OS_target");
    CParam *BUCK_LS_OS_post_value = StsGetParam(funcindex, "BUCK_LS_OS_post_value");
    CParam *BUCK_LS_OS_post_rt = StsGetParam(funcindex, "BUCK_LS_OS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	if (!TTR)
	{
		//--------PGND--->SW
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K33_BUSL_PGND, K30_VBAT_Cap, K32_PMID_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		delay_ms(1);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x81);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		//		field[(WAKE_UP,1),(D2A_BUBO_TM_LSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,0),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
		Inherit_register();
		delay_ms(2);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(5);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x81);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		//		field[(WAKE_UP,1),(D2A_BUBO_TM_LSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,0),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
		delay_ms(1);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	}


	TRIM_NODE &BUCK_LSFFET_OS = trim_reg.trim("buck_lsfet_os");
	BUCK_LSFFET_OS.execute(measure_buck_lsfet_os, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&BUCK_LSFFET_OS, measure_buck_lsfet_os, spec, funcindex, funclabel, 1.0, -1, 1, 7.5, false, 1.0);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}


    return 0;
}
 
DUT_API int Trim_BOOST_LS_Gain(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BOOST_LS_Gain_step0 = StsGetParam(funcindex, "BOOST_LS_Gain_step0");
    CParam *BOOST_LS_Gain_step1 = StsGetParam(funcindex, "BOOST_LS_Gain_step1");
    CParam *BOOST_LS_Gain_step2 = StsGetParam(funcindex, "BOOST_LS_Gain_step2");
    CParam *BOOST_LS_Gain_step3 = StsGetParam(funcindex, "BOOST_LS_Gain_step3");
    CParam *BOOST_LS_Gain_step4 = StsGetParam(funcindex, "BOOST_LS_Gain_step4");
    CParam *BOOST_LS_Gain_step5 = StsGetParam(funcindex, "BOOST_LS_Gain_step5");
    CParam *BOOST_LS_Gain_step6 = StsGetParam(funcindex, "BOOST_LS_Gain_step6");
    CParam *BOOST_LS_Gain_step7 = StsGetParam(funcindex, "BOOST_LS_Gain_step7");
    CParam *BOOST_LS_Gain_step8 = StsGetParam(funcindex, "BOOST_LS_Gain_step8");
    CParam *BOOST_LS_Gain_step9 = StsGetParam(funcindex, "BOOST_LS_Gain_step9");
    CParam *BOOST_LS_Gain_step10 = StsGetParam(funcindex, "BOOST_LS_Gain_step10");
    CParam *BOOST_LS_Gain_step11 = StsGetParam(funcindex, "BOOST_LS_Gain_step11");
    CParam *BOOST_LS_Gain_step12 = StsGetParam(funcindex, "BOOST_LS_Gain_step12");
    CParam *BOOST_LS_Gain_step13 = StsGetParam(funcindex, "BOOST_LS_Gain_step13");
    CParam *BOOST_LS_Gain_step14 = StsGetParam(funcindex, "BOOST_LS_Gain_step14");
    CParam *BOOST_LS_Gain_step15 = StsGetParam(funcindex, "BOOST_LS_Gain_step15");
    CParam *BOOST_LS_Gain_step16 = StsGetParam(funcindex, "BOOST_LS_Gain_step16");
    CParam *BOOST_LS_Gain_step17 = StsGetParam(funcindex, "BOOST_LS_Gain_step17");
    CParam *BOOST_LS_Gain_step18 = StsGetParam(funcindex, "BOOST_LS_Gain_step18");
    CParam *BOOST_LS_Gain_step19 = StsGetParam(funcindex, "BOOST_LS_Gain_step19");
    CParam *BOOST_LS_Gain_step20 = StsGetParam(funcindex, "BOOST_LS_Gain_step20");
    CParam *BOOST_LS_Gain_step21 = StsGetParam(funcindex, "BOOST_LS_Gain_step21");
    CParam *BOOST_LS_Gain_step22 = StsGetParam(funcindex, "BOOST_LS_Gain_step22");
    CParam *BOOST_LS_Gain_step23 = StsGetParam(funcindex, "BOOST_LS_Gain_step23");
    CParam *BOOST_LS_Gain_step24 = StsGetParam(funcindex, "BOOST_LS_Gain_step24");
    CParam *BOOST_LS_Gain_step25 = StsGetParam(funcindex, "BOOST_LS_Gain_step25");
    CParam *BOOST_LS_Gain_step26 = StsGetParam(funcindex, "BOOST_LS_Gain_step26");
    CParam *BOOST_LS_Gain_step27 = StsGetParam(funcindex, "BOOST_LS_Gain_step27");
    CParam *BOOST_LS_Gain_step28 = StsGetParam(funcindex, "BOOST_LS_Gain_step28");
    CParam *BOOST_LS_Gain_step29 = StsGetParam(funcindex, "BOOST_LS_Gain_step29");
    CParam *BOOST_LS_Gain_step30 = StsGetParam(funcindex, "BOOST_LS_Gain_step30");
    CParam *BOOST_LS_Gain_step31 = StsGetParam(funcindex, "BOOST_LS_Gain_step31");
    CParam *BOOST_LS_Gain_pre_value = StsGetParam(funcindex, "BOOST_LS_Gain_pre_value");
    CParam *BOOST_LS_Gain_pre_bit = StsGetParam(funcindex, "BOOST_LS_Gain_pre_bit");
    CParam *BOOST_LS_Gain_post_bit = StsGetParam(funcindex, "BOOST_LS_Gain_post_bit");
    CParam *BOOST_LS_Gain_updated = StsGetParam(funcindex, "BOOST_LS_Gain_updated");
    CParam *BOOST_LS_Gain_guessed = StsGetParam(funcindex, "BOOST_LS_Gain_guessed");
    CParam *BOOST_LS_Gain_target = StsGetParam(funcindex, "BOOST_LS_Gain_target");
    CParam *BOOST_LS_Gain_post_value = StsGetParam(funcindex, "BOOST_LS_Gain_post_value");
    CParam *BOOST_LS_Gain_post_rt = StsGetParam(funcindex, "BOOST_LS_Gain_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	if (!TTR)
	{
		//--------SW--->PGND
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K33_BUSL_PGND, K30_VBAT_Cap, K32_PMID_Cap, -1);
		delay_ms(3);
		if (V_TYP_VBAT > 4)
		{
			VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		else
		{
			VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		entertestmode();
		//		field[(WAKE_UP,1),(D2A_BUBO_TM_LSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,1),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x81);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
		Inherit_register();
		delay_ms(2);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		delay_ms(2);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		delay_ms(1);
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x09, 0x0D);
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
		delay_ms(5);// delay need keep to make sure boost mode can enter stable
		I2CWriteSameData(DEV_ADDR, 0x59, 0x81);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
		delay_ms(1);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		delay_ms(1);
	}

	TRIM_NODE &BOOST_LSFFET_GAIN = trim_reg.trim("boost_lsfet_gain");
	BOOST_LSFFET_GAIN.execute(measure_boost_lsfet_gain, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&BOOST_LSFFET_GAIN, measure_boost_lsfet_gain, spec, funcindex, funclabel, 1.0, 1, 1, 2.2, false, 0.9);

	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}

    return 0;
}
 
DUT_API int Trim_BOOST_LS_Offset(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BOOST_LS_OS_step0 = StsGetParam(funcindex, "BOOST_LS_OS_step0");
    CParam *BOOST_LS_OS_step1 = StsGetParam(funcindex, "BOOST_LS_OS_step1");
    CParam *BOOST_LS_OS_step2 = StsGetParam(funcindex, "BOOST_LS_OS_step2");
    CParam *BOOST_LS_OS_step3 = StsGetParam(funcindex, "BOOST_LS_OS_step3");
    CParam *BOOST_LS_OS_step4 = StsGetParam(funcindex, "BOOST_LS_OS_step4");
    CParam *BOOST_LS_OS_step5 = StsGetParam(funcindex, "BOOST_LS_OS_step5");
    CParam *BOOST_LS_OS_step6 = StsGetParam(funcindex, "BOOST_LS_OS_step6");
    CParam *BOOST_LS_OS_step7 = StsGetParam(funcindex, "BOOST_LS_OS_step7");
    CParam *BOOST_LS_OS_step8 = StsGetParam(funcindex, "BOOST_LS_OS_step8");
    CParam *BOOST_LS_OS_step9 = StsGetParam(funcindex, "BOOST_LS_OS_step9");
    CParam *BOOST_LS_OS_step10 = StsGetParam(funcindex, "BOOST_LS_OS_step10");
    CParam *BOOST_LS_OS_step11 = StsGetParam(funcindex, "BOOST_LS_OS_step11");
    CParam *BOOST_LS_OS_step12 = StsGetParam(funcindex, "BOOST_LS_OS_step12");
    CParam *BOOST_LS_OS_step13 = StsGetParam(funcindex, "BOOST_LS_OS_step13");
    CParam *BOOST_LS_OS_step14 = StsGetParam(funcindex, "BOOST_LS_OS_step14");
    CParam *BOOST_LS_OS_step15 = StsGetParam(funcindex, "BOOST_LS_OS_step15");
    CParam *BOOST_LS_OS_pre_value = StsGetParam(funcindex, "BOOST_LS_OS_pre_value");
    CParam *BOOST_LS_OS_pre_bit = StsGetParam(funcindex, "BOOST_LS_OS_pre_bit");
    CParam *BOOST_LS_OS_post_bit = StsGetParam(funcindex, "BOOST_LS_OS_post_bit");
    CParam *BOOST_LS_OS_updated = StsGetParam(funcindex, "BOOST_LS_OS_updated");
    CParam *BOOST_LS_OS_guessed = StsGetParam(funcindex, "BOOST_LS_OS_guessed");
    CParam *BOOST_LS_OS_target = StsGetParam(funcindex, "BOOST_LS_OS_target");
    CParam *BOOST_LS_OS_post_value = StsGetParam(funcindex, "BOOST_LS_OS_post_value");
    CParam *BOOST_LS_OS_post_rt = StsGetParam(funcindex, "BOOST_LS_OS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	if (!TTR)
	{
		//--------SW--->PGND
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K33_BUSL_PGND, K30_VBAT_Cap, K32_PMID_Cap, -1);
		delay_ms(3);
		if (V_TYP_VBAT > 4)
		{
			VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		else
		{
			VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		delay_ms(1);
		entertestmode();
		//		field[(WAKE_UP,1),(D2A_BUBO_TM_LSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,1),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x81);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
		Inherit_register();
		delay_ms(2);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(1);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	}

	TRIM_NODE &BOOST_LSFFET_OS = trim_reg.trim("boost_lsfet_os");
	BOOST_LSFFET_OS.execute(measure_boost_lsfet_os, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&BOOST_LSFFET_OS, measure_boost_lsfet_os, spec, funcindex, funclabel, 1.0, -1, 1, 7.5, false, 1.0);

	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	//FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	ATEST_GRP.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
	BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
	ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);

    return 0;
}
 
DUT_API int Trim_IBUS_LOOP_Offset(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IBUS_LOOP_OS_step0 = StsGetParam(funcindex, "IBUS_LOOP_OS_step0");
    CParam *IBUS_LOOP_OS_step1 = StsGetParam(funcindex, "IBUS_LOOP_OS_step1");
    CParam *IBUS_LOOP_OS_step2 = StsGetParam(funcindex, "IBUS_LOOP_OS_step2");
    CParam *IBUS_LOOP_OS_step3 = StsGetParam(funcindex, "IBUS_LOOP_OS_step3");
    CParam *IBUS_LOOP_OS_step4 = StsGetParam(funcindex, "IBUS_LOOP_OS_step4");
    CParam *IBUS_LOOP_OS_step5 = StsGetParam(funcindex, "IBUS_LOOP_OS_step5");
    CParam *IBUS_LOOP_OS_step6 = StsGetParam(funcindex, "IBUS_LOOP_OS_step6");
    CParam *IBUS_LOOP_OS_step7 = StsGetParam(funcindex, "IBUS_LOOP_OS_step7");
    CParam *IBUS_LOOP_OS_step8 = StsGetParam(funcindex, "IBUS_LOOP_OS_step8");
    CParam *IBUS_LOOP_OS_step9 = StsGetParam(funcindex, "IBUS_LOOP_OS_step9");
    CParam *IBUS_LOOP_OS_step10 = StsGetParam(funcindex, "IBUS_LOOP_OS_step10");
    CParam *IBUS_LOOP_OS_step11 = StsGetParam(funcindex, "IBUS_LOOP_OS_step11");
    CParam *IBUS_LOOP_OS_step12 = StsGetParam(funcindex, "IBUS_LOOP_OS_step12");
    CParam *IBUS_LOOP_OS_step13 = StsGetParam(funcindex, "IBUS_LOOP_OS_step13");
    CParam *IBUS_LOOP_OS_step14 = StsGetParam(funcindex, "IBUS_LOOP_OS_step14");
    CParam *IBUS_LOOP_OS_step15 = StsGetParam(funcindex, "IBUS_LOOP_OS_step15");
    CParam *IBUS_LOOP_OS_pre_value = StsGetParam(funcindex, "IBUS_LOOP_OS_pre_value");
    CParam *IBUS_LOOP_OS_pre_bit = StsGetParam(funcindex, "IBUS_LOOP_OS_pre_bit");
    CParam *IBUS_LOOP_OS_post_bit = StsGetParam(funcindex, "IBUS_LOOP_OS_post_bit");
    CParam *IBUS_LOOP_OS_updated = StsGetParam(funcindex, "IBUS_LOOP_OS_updated");
    CParam *IBUS_LOOP_OS_guessed = StsGetParam(funcindex, "IBUS_LOOP_OS_guessed");
    CParam *IBUS_LOOP_OS_target = StsGetParam(funcindex, "IBUS_LOOP_OS_target");
    CParam *IBUS_LOOP_OS_post_value = StsGetParam(funcindex, "IBUS_LOOP_OS_post_value");
    CParam *IBUS_LOOP_OS_post_rt = StsGetParam(funcindex, "IBUS_LOOP_OS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	//==for 2A current from VBUS to PMID and check AMUX out to 400mV
	cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K16_VBUS_Cap, K30_VBAT_Cap, K31_BUSL_PMID, K3_QVMH_NTC_SEL, K25_VCC_Cap, - 1);
	delay_ms(3);
	VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VCC_ACM.Set(FV, 4.55, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x25);//
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);//		field[(WAKE_UP,1),(BUBO_MODE,0),(IBAT_LIMIT,7),(IBUS_SET,37),(VBUS_LOOP_DISABLE,1)]
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);//		field[(EN_ATEST1,1),(D2A_BUBO_ATEST1,5)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xCE);//		field[(EN_ATEST0,1),(ATEST0_MUX,25)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0x04);//		field[(D2A_BUBO_TM_DIS_BST_UVLO_LOCAL,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xCF);//		field[(EN_I2C_CTRL,1)]
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0x24);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	Inherit_register();
	delay_ms(2);
	
	TRIM_NODE &IBUS_LOOP_OS = trim_reg.trim("ibus_loop_os");
	IBUS_LOOP_OS.execute(measure_ibus_loop_os, spec, funcindex, funclabel, 1, 0, 0);
	Retry_trim_search(&IBUS_LOOP_OS, measure_ibus_loop_os, spec, funcindex, funclabel, 1.0, -1, 1, 5, false, 0.8);

	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_1V, FOVIe_10UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_1V, FOVIe_10UA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	if (!TTR)
	{

		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);

		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
	}

    return 0;
}
 
DUT_API int Trim_BUCK_VBUS_EA_Offset(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BUCK_VBUS_EA_OS_step0 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step0");
    CParam *BUCK_VBUS_EA_OS_step1 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step1");
    CParam *BUCK_VBUS_EA_OS_step2 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step2");
    CParam *BUCK_VBUS_EA_OS_step3 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step3");
    CParam *BUCK_VBUS_EA_OS_step4 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step4");
    CParam *BUCK_VBUS_EA_OS_step5 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step5");
    CParam *BUCK_VBUS_EA_OS_step6 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step6");
    CParam *BUCK_VBUS_EA_OS_step7 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step7");
    CParam *BUCK_VBUS_EA_OS_step8 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step8");
    CParam *BUCK_VBUS_EA_OS_step9 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step9");
    CParam *BUCK_VBUS_EA_OS_step10 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step10");
    CParam *BUCK_VBUS_EA_OS_step11 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step11");
    CParam *BUCK_VBUS_EA_OS_step12 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step12");
    CParam *BUCK_VBUS_EA_OS_step13 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step13");
    CParam *BUCK_VBUS_EA_OS_step14 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step14");
    CParam *BUCK_VBUS_EA_OS_step15 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step15");
    CParam *BUCK_VBUS_EA_OS_step16 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step16");
    CParam *BUCK_VBUS_EA_OS_step17 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step17");
    CParam *BUCK_VBUS_EA_OS_step18 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step18");
    CParam *BUCK_VBUS_EA_OS_step19 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step19");
    CParam *BUCK_VBUS_EA_OS_step20 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step20");
    CParam *BUCK_VBUS_EA_OS_step21 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step21");
    CParam *BUCK_VBUS_EA_OS_step22 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step22");
    CParam *BUCK_VBUS_EA_OS_step23 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step23");
    CParam *BUCK_VBUS_EA_OS_step24 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step24");
    CParam *BUCK_VBUS_EA_OS_step25 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step25");
    CParam *BUCK_VBUS_EA_OS_step26 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step26");
    CParam *BUCK_VBUS_EA_OS_step27 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step27");
    CParam *BUCK_VBUS_EA_OS_step28 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step28");
    CParam *BUCK_VBUS_EA_OS_step29 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step29");
    CParam *BUCK_VBUS_EA_OS_step30 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step30");
    CParam *BUCK_VBUS_EA_OS_step31 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step31");
    CParam *BUCK_VBUS_EA_OS_step32 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step32");
    CParam *BUCK_VBUS_EA_OS_step33 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step33");
    CParam *BUCK_VBUS_EA_OS_step34 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step34");
    CParam *BUCK_VBUS_EA_OS_step35 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step35");
    CParam *BUCK_VBUS_EA_OS_step36 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step36");
    CParam *BUCK_VBUS_EA_OS_step37 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step37");
    CParam *BUCK_VBUS_EA_OS_step38 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step38");
    CParam *BUCK_VBUS_EA_OS_step39 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step39");
    CParam *BUCK_VBUS_EA_OS_step40 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step40");
    CParam *BUCK_VBUS_EA_OS_step41 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step41");
    CParam *BUCK_VBUS_EA_OS_step42 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step42");
    CParam *BUCK_VBUS_EA_OS_step43 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step43");
    CParam *BUCK_VBUS_EA_OS_step44 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step44");
    CParam *BUCK_VBUS_EA_OS_step45 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step45");
    CParam *BUCK_VBUS_EA_OS_step46 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step46");
    CParam *BUCK_VBUS_EA_OS_step47 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step47");
    CParam *BUCK_VBUS_EA_OS_step48 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step48");
    CParam *BUCK_VBUS_EA_OS_step49 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step49");
    CParam *BUCK_VBUS_EA_OS_step50 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step50");
    CParam *BUCK_VBUS_EA_OS_step51 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step51");
    CParam *BUCK_VBUS_EA_OS_step52 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step52");
    CParam *BUCK_VBUS_EA_OS_step53 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step53");
    CParam *BUCK_VBUS_EA_OS_step54 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step54");
    CParam *BUCK_VBUS_EA_OS_step55 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step55");
    CParam *BUCK_VBUS_EA_OS_step56 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step56");
    CParam *BUCK_VBUS_EA_OS_step57 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step57");
    CParam *BUCK_VBUS_EA_OS_step58 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step58");
    CParam *BUCK_VBUS_EA_OS_step59 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step59");
    CParam *BUCK_VBUS_EA_OS_step60 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step60");
    CParam *BUCK_VBUS_EA_OS_step61 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step61");
    CParam *BUCK_VBUS_EA_OS_step62 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step62");
    CParam *BUCK_VBUS_EA_OS_step63 = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_step63");
    CParam *BUCK_VBUS_EA_OS_pre_value = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_pre_value");
    CParam *BUCK_VBUS_EA_OS_pre_bit = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_pre_bit");
    CParam *BUCK_VBUS_EA_OS_post_bit = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_post_bit");
    CParam *BUCK_VBUS_EA_OS_updated = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_updated");
    CParam *BUCK_VBUS_EA_OS_guessed = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_guessed");
    CParam *BUCK_VBUS_EA_OS_target = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_target");
    CParam *BUCK_VBUS_EA_OS_post_value = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_post_value");
    CParam *VBUS_BU_LOOP_IND_L = StsGetParam(funcindex, "VBUS_BU_LOOP_IND_L");
    CParam *VBUS_BU_LOOP_IND_H = StsGetParam(funcindex, "VBUS_BU_LOOP_IND_H");
    CParam *BUCK_VBUS_EA_OS_post_rt = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	//------------Connect Serve loop of BUCK mode, need confirm when 

	double vbus_bu_loop_high[SITE_NUM] = { 0 };
	double vbus_bu_loop_low[SITE_NUM] = { 0 };
	double vbus_bu_serve_loop[SITE_NUM] = { 0 };
	if (!TTR)
	{
		dcm.I2CConnect();
		cbite.SetOn(-1);
		delay_ms(3);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K62_AMP3_Power, K63_AMP4_Power, K43_INT_ACM, K58_INT_PU,-1);
		delay_ms(3);
		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FI, -0.0001, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0x37);//65*0.02+4.2=5.5V
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(BUBO_MODE,0),(VBUS_VOL_SET_L,55),(IBAT_LIMIT,7),(IBUS_SET,127),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(DIS_NTC_DETECTION_ANALOG,1)]
		I2CWriteSameData(DEV_ADDR, 0x56, 0x05);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x80);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
		I2CWriteSameData(DEV_ADDR, 0x58, 0xA0);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		Inherit_register();
		delay_ms(2);
		SCL_ACM.Set(FV, 1.8, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K62_AMP3_Power, K63_AMP4_Power, K39_SVLP_VBUS, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(5);// 3ms for cbit close relay and 2ms for amp stable

		TRIM_NODE &MNT_VBUS_EA_OS_BUCK = trim_reg.trim("mnt_vbus_ea_os_buck");
		MNT_VBUS_EA_OS_BUCK.execute(measure_mnt_vbus_ea_os_buck, spec, funcindex, funclabel, 1, 0, 0);

		delay_ms(1);
		SDA_INT_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_bu_loop_high[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
		}
		I2CWriteSameData(DEV_ADDR, 0x55, 0x8A);
		delay_ms(1);
		SDA_INT_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_bu_loop_low[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
		}

		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K62_AMP3_Power, K63_AMP4_Power, K43_INT_ACM, K58_INT_PU,-1);
		delay_ms(3);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10UA, FOVIe_RELAY_ON);
		SCL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);

		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	}
	else
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K62_AMP3_Power, K63_AMP4_Power, K43_INT_ACM, K58_INT_PU,-1);
		delay_ms(3);
		VCC_ACM.Set(FV, 4.55, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FI, -0.0001, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(5);
		entertestmode();
		Inherit_register();
		I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0x37);//65*0.02+4.2=5.5V
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);//ITERM_AUTO_En=1; Wake up=0x1
		I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(BUBO_MODE,0),(VBUS_VOL_SET_L,55),(IBAT_LIMIT,7),(IBUS_SET,127),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(DIS_NTC_DETECTION_ANALOG,1)]
		I2CWriteSameData(DEV_ADDR, 0x56, 0x05);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x80);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
		I2CWriteSameData(DEV_ADDR, 0x58, 0xA0);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		delay_ms(10);//delay_ms(10)
		SCL_ACM.Set(FV, 1.8, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K62_AMP3_Power, K63_AMP4_Power, K39_SVLP_VBUS, K43_INT_ACM, K58_INT_PU,-1);
		delay_ms(3);
		TRIM_NODE& MNT_VBUS_EA_OS_BUCK = trim_reg.trim("mnt_vbus_ea_os_buck");
		MNT_VBUS_EA_OS_BUCK.execute(measure_mnt_vbus_ea_os_buck, spec, funcindex, funclabel, 1, 0, 0);

		delay_ms(1);
		SDA_INT_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_bu_loop_high[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
		}
		I2CWriteSameData(DEV_ADDR, 0x55, 0x8A);
		delay_ms(1);
		SDA_INT_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_bu_loop_low[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
		}

		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K62_AMP3_Power, K63_AMP4_Power, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(3);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(3);
		FOR_EACH_VALID_SITE(site)
		{
			VBUS_BU_LOOP_IND_L->SetTestResult(site, 0, vbus_bu_loop_low[site]);
			VBUS_BU_LOOP_IND_H->SetTestResult(site, 0, vbus_bu_loop_high[site]);
		}

	}



    return 0;
}
 
DUT_API int Trim_BOOST_VBUS_EA_Offset(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BOOST_VBUS_EA_OS_step0 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step0");
    CParam *BOOST_VBUS_EA_OS_step1 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step1");
    CParam *BOOST_VBUS_EA_OS_step2 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step2");
    CParam *BOOST_VBUS_EA_OS_step3 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step3");
    CParam *BOOST_VBUS_EA_OS_step4 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step4");
    CParam *BOOST_VBUS_EA_OS_step5 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step5");
    CParam *BOOST_VBUS_EA_OS_step6 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step6");
    CParam *BOOST_VBUS_EA_OS_step7 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step7");
    CParam *BOOST_VBUS_EA_OS_step8 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step8");
    CParam *BOOST_VBUS_EA_OS_step9 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step9");
    CParam *BOOST_VBUS_EA_OS_step10 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step10");
    CParam *BOOST_VBUS_EA_OS_step11 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step11");
    CParam *BOOST_VBUS_EA_OS_step12 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step12");
    CParam *BOOST_VBUS_EA_OS_step13 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step13");
    CParam *BOOST_VBUS_EA_OS_step14 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step14");
    CParam *BOOST_VBUS_EA_OS_step15 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step15");
    CParam *BOOST_VBUS_EA_OS_step16 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step16");
    CParam *BOOST_VBUS_EA_OS_step17 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step17");
    CParam *BOOST_VBUS_EA_OS_step18 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step18");
    CParam *BOOST_VBUS_EA_OS_step19 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step19");
    CParam *BOOST_VBUS_EA_OS_step20 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step20");
    CParam *BOOST_VBUS_EA_OS_step21 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step21");
    CParam *BOOST_VBUS_EA_OS_step22 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step22");
    CParam *BOOST_VBUS_EA_OS_step23 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step23");
    CParam *BOOST_VBUS_EA_OS_step24 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step24");
    CParam *BOOST_VBUS_EA_OS_step25 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step25");
    CParam *BOOST_VBUS_EA_OS_step26 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step26");
    CParam *BOOST_VBUS_EA_OS_step27 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step27");
    CParam *BOOST_VBUS_EA_OS_step28 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step28");
    CParam *BOOST_VBUS_EA_OS_step29 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step29");
    CParam *BOOST_VBUS_EA_OS_step30 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step30");
    CParam *BOOST_VBUS_EA_OS_step31 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step31");
    CParam *BOOST_VBUS_EA_OS_step32 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step32");
    CParam *BOOST_VBUS_EA_OS_step33 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step33");
    CParam *BOOST_VBUS_EA_OS_step34 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step34");
    CParam *BOOST_VBUS_EA_OS_step35 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step35");
    CParam *BOOST_VBUS_EA_OS_step36 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step36");
    CParam *BOOST_VBUS_EA_OS_step37 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step37");
    CParam *BOOST_VBUS_EA_OS_step38 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step38");
    CParam *BOOST_VBUS_EA_OS_step39 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step39");
    CParam *BOOST_VBUS_EA_OS_step40 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step40");
    CParam *BOOST_VBUS_EA_OS_step41 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step41");
    CParam *BOOST_VBUS_EA_OS_step42 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step42");
    CParam *BOOST_VBUS_EA_OS_step43 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step43");
    CParam *BOOST_VBUS_EA_OS_step44 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step44");
    CParam *BOOST_VBUS_EA_OS_step45 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step45");
    CParam *BOOST_VBUS_EA_OS_step46 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step46");
    CParam *BOOST_VBUS_EA_OS_step47 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step47");
    CParam *BOOST_VBUS_EA_OS_step48 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step48");
    CParam *BOOST_VBUS_EA_OS_step49 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step49");
    CParam *BOOST_VBUS_EA_OS_step50 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step50");
    CParam *BOOST_VBUS_EA_OS_step51 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step51");
    CParam *BOOST_VBUS_EA_OS_step52 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step52");
    CParam *BOOST_VBUS_EA_OS_step53 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step53");
    CParam *BOOST_VBUS_EA_OS_step54 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step54");
    CParam *BOOST_VBUS_EA_OS_step55 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step55");
    CParam *BOOST_VBUS_EA_OS_step56 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step56");
    CParam *BOOST_VBUS_EA_OS_step57 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step57");
    CParam *BOOST_VBUS_EA_OS_step58 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step58");
    CParam *BOOST_VBUS_EA_OS_step59 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step59");
    CParam *BOOST_VBUS_EA_OS_step60 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step60");
    CParam *BOOST_VBUS_EA_OS_step61 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step61");
    CParam *BOOST_VBUS_EA_OS_step62 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step62");
    CParam *BOOST_VBUS_EA_OS_step63 = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_step63");
    CParam *BOOST_VBUS_EA_OS_pre_value = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_pre_value");
    CParam *BOOST_VBUS_EA_OS_pre_bit = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_pre_bit");
    CParam *BOOST_VBUS_EA_OS_post_bit = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_post_bit");
    CParam *BOOST_VBUS_EA_OS_updated = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_updated");
    CParam *BOOST_VBUS_EA_OS_guessed = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_guessed");
    CParam *BOOST_VBUS_EA_OS_target = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_target");
    CParam *BOOST_VBUS_EA_OS_post_value = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_post_value");
    CParam *VBUS_BO_LOOP_IND_L = StsGetParam(funcindex, "VBUS_BO_LOOP_IND_L");
    CParam *VBUS_BO_LOOP_IND_H = StsGetParam(funcindex, "VBUS_BO_LOOP_IND_H");
    CParam *BOOST_VBUS_EA_OS_post_rt = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	double vbus_bo_loop_high[SITE_NUM] = { 0 };
	double vbus_bo_loop_low[SITE_NUM] = { 0 };
	double vbus_bo_serve_loop[SITE_NUM] = { 0 };
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power,/* K62_AMP3_Power,*/ K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(5);
		VCC_ACM.Set(FV, 4.55, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FI, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);// minize amp output current range
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SCL_ACM.Set(FV, 1.8, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
		I2CWriteSameData(DEV_ADDR, 0x0C, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0xE6);//230*0.02+4.4=9V
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(BUBO_MODE,1),(VBUS_VOL_SET_L,124),(VBUS_VOL_SET_H,1),(IBAT_LIMIT,7),(IBUS_SET,127),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(DIS_NTC_DETECTION_ANALOG,1)]
		I2CWriteSameData(DEV_ADDR, 0x56, 0x05);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x80);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
		I2CWriteSameData(DEV_ADDR, 0x58, 0xA0);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		Inherit_register();
		delay_ms(2);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power, /*K62_AMP3_Power,*/ K65_SVLP_VBUS, K43_INT_ACM, K58_INT_PU, -1);
		NTC_FOVI.MeasureVI(500, 10);
		VBUS_FOVI.MeasureVI(2500, 50);

		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 8, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_ON);// minize amp output current range
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SCL_ACM.Set(FV, 1.2, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
		I2CWriteSameData(DEV_ADDR, 0x0C, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0xE6);//230*0.02+4.4=9V
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(BUBO_MODE,1),(VBUS_VOL_SET_L,124),(VBUS_VOL_SET_H,1),(IBAT_LIMIT,7),(IBUS_SET,127),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(DIS_NTC_DETECTION_ANALOG,1)]
		I2CWriteSameData(DEV_ADDR, 0x56, 0x05);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x80);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
		I2CWriteSameData(DEV_ADDR, 0x58, 0xA0);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		delay_ms(2);
		Inherit_register();
		delay_ms(2);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power, K65_SVLP_VBUS, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(5);// 3ms for cbit close relay and 2ms for amp stable
		delay_ms(100);
		TRIM_NODE &MNT_VBUS_EA_OS_BOOST = trim_reg.trim("mnt_vbus_ea_os_boost");
		MNT_VBUS_EA_OS_BOOST.execute(measure_mnt_vbus_ea_os_boost, spec, funcindex, funclabel, 1, 0, 0);
		delay_ms(1);
		SDA_INT_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_bo_loop_high[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
		}
		I2CWriteSameData(DEV_ADDR, 0x55, 0x8A);
		delay_ms(1);
		SDA_INT_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_bo_loop_low[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
		}

		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(5);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(5);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10UA, FOVIe_RELAY_ON);
		SCL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);

		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	}
	else
	{
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power,/*K62_AMP3_Power,*/K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(5);
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		//I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
		I2CWriteSameData(DEV_ADDR, 0x0C, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0xE6);//230*0.02+4.4=9V
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		delay_ms(2);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power, /*K62_AMP3_Power,*/ K65_SVLP_VBUS, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(3);// 3ms for cbit close relay and 2ms for amp stable
		Retest_voltage_unstable_with_time_out(VBUS_FOVI, vbus_bo_serve_loop, 4.5, 14.5, 5, 100, MEAS_V);

		TRIM_NODE &MNT_VBUS_EA_OS_BOOST = trim_reg.trim("mnt_vbus_ea_os_boost");
		MNT_VBUS_EA_OS_BOOST.execute(measure_mnt_vbus_ea_os_boost, spec, funcindex, funclabel, 1, 0, 0);
		I2CWriteSameData(DEV_ADDR, 0x55, 0x00);// default vlaue is 5V pull up
		delay_ms(1);
		SDA_INT_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_bo_loop_high[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
		}
		I2CWriteSameData(DEV_ADDR, 0x55, 0x8A);
		delay_ms(1);
		SDA_INT_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_bo_loop_low[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
		}

		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(5);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(15);// off delay 15ms
		
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10UA, FOVIe_RELAY_ON);
		SCL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
		//SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		//NTC_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);

		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		//SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		//NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		VBUS_FOVI.Set(FI, 0, FOVIe_20V, FOVIe_10UA, FOVIe_RELAY_ON);
		VAC123_ACM.Set(FI, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}

	FOR_EACH_VALID_SITE(site)
	{
		VBUS_BO_LOOP_IND_L->SetTestResult(site, 0, vbus_bo_loop_low[site]);
		VBUS_BO_LOOP_IND_H->SetTestResult(site, 0, vbus_bo_loop_high[site]);
	}
    return 0;
}
 
DUT_API int Trim_VBAT_CV_BUF(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_CV_BUF_step0 = StsGetParam(funcindex, "VBAT_CV_BUF_step0");
    CParam *VBAT_CV_BUF_step1 = StsGetParam(funcindex, "VBAT_CV_BUF_step1");
    CParam *VBAT_CV_BUF_step2 = StsGetParam(funcindex, "VBAT_CV_BUF_step2");
    CParam *VBAT_CV_BUF_step3 = StsGetParam(funcindex, "VBAT_CV_BUF_step3");
    CParam *VBAT_CV_BUF_step4 = StsGetParam(funcindex, "VBAT_CV_BUF_step4");
    CParam *VBAT_CV_BUF_step5 = StsGetParam(funcindex, "VBAT_CV_BUF_step5");
    CParam *VBAT_CV_BUF_step6 = StsGetParam(funcindex, "VBAT_CV_BUF_step6");
    CParam *VBAT_CV_BUF_step7 = StsGetParam(funcindex, "VBAT_CV_BUF_step7");
    CParam *VBAT_CV_BUF_step8 = StsGetParam(funcindex, "VBAT_CV_BUF_step8");
    CParam *VBAT_CV_BUF_step9 = StsGetParam(funcindex, "VBAT_CV_BUF_step9");
    CParam *VBAT_CV_BUF_step10 = StsGetParam(funcindex, "VBAT_CV_BUF_step10");
    CParam *VBAT_CV_BUF_step11 = StsGetParam(funcindex, "VBAT_CV_BUF_step11");
    CParam *VBAT_CV_BUF_step12 = StsGetParam(funcindex, "VBAT_CV_BUF_step12");
    CParam *VBAT_CV_BUF_step13 = StsGetParam(funcindex, "VBAT_CV_BUF_step13");
    CParam *VBAT_CV_BUF_step14 = StsGetParam(funcindex, "VBAT_CV_BUF_step14");
    CParam *VBAT_CV_BUF_step15 = StsGetParam(funcindex, "VBAT_CV_BUF_step15");
    CParam *VBAT_CV_BUF_step16 = StsGetParam(funcindex, "VBAT_CV_BUF_step16");
    CParam *VBAT_CV_BUF_step17 = StsGetParam(funcindex, "VBAT_CV_BUF_step17");
    CParam *VBAT_CV_BUF_step18 = StsGetParam(funcindex, "VBAT_CV_BUF_step18");
    CParam *VBAT_CV_BUF_step19 = StsGetParam(funcindex, "VBAT_CV_BUF_step19");
    CParam *VBAT_CV_BUF_step20 = StsGetParam(funcindex, "VBAT_CV_BUF_step20");
    CParam *VBAT_CV_BUF_step21 = StsGetParam(funcindex, "VBAT_CV_BUF_step21");
    CParam *VBAT_CV_BUF_step22 = StsGetParam(funcindex, "VBAT_CV_BUF_step22");
    CParam *VBAT_CV_BUF_step23 = StsGetParam(funcindex, "VBAT_CV_BUF_step23");
    CParam *VBAT_CV_BUF_step24 = StsGetParam(funcindex, "VBAT_CV_BUF_step24");
    CParam *VBAT_CV_BUF_step25 = StsGetParam(funcindex, "VBAT_CV_BUF_step25");
    CParam *VBAT_CV_BUF_step26 = StsGetParam(funcindex, "VBAT_CV_BUF_step26");
    CParam *VBAT_CV_BUF_step27 = StsGetParam(funcindex, "VBAT_CV_BUF_step27");
    CParam *VBAT_CV_BUF_step28 = StsGetParam(funcindex, "VBAT_CV_BUF_step28");
    CParam *VBAT_CV_BUF_step29 = StsGetParam(funcindex, "VBAT_CV_BUF_step29");
    CParam *VBAT_CV_BUF_step30 = StsGetParam(funcindex, "VBAT_CV_BUF_step30");
    CParam *VBAT_CV_BUF_step31 = StsGetParam(funcindex, "VBAT_CV_BUF_step31");
    CParam *VBAT_CV_BUF_step32 = StsGetParam(funcindex, "VBAT_CV_BUF_step32");
    CParam *VBAT_CV_BUF_step33 = StsGetParam(funcindex, "VBAT_CV_BUF_step33");
    CParam *VBAT_CV_BUF_step34 = StsGetParam(funcindex, "VBAT_CV_BUF_step34");
    CParam *VBAT_CV_BUF_step35 = StsGetParam(funcindex, "VBAT_CV_BUF_step35");
    CParam *VBAT_CV_BUF_step36 = StsGetParam(funcindex, "VBAT_CV_BUF_step36");
    CParam *VBAT_CV_BUF_step37 = StsGetParam(funcindex, "VBAT_CV_BUF_step37");
    CParam *VBAT_CV_BUF_step38 = StsGetParam(funcindex, "VBAT_CV_BUF_step38");
    CParam *VBAT_CV_BUF_step39 = StsGetParam(funcindex, "VBAT_CV_BUF_step39");
    CParam *VBAT_CV_BUF_step40 = StsGetParam(funcindex, "VBAT_CV_BUF_step40");
    CParam *VBAT_CV_BUF_step41 = StsGetParam(funcindex, "VBAT_CV_BUF_step41");
    CParam *VBAT_CV_BUF_step42 = StsGetParam(funcindex, "VBAT_CV_BUF_step42");
    CParam *VBAT_CV_BUF_step43 = StsGetParam(funcindex, "VBAT_CV_BUF_step43");
    CParam *VBAT_CV_BUF_step44 = StsGetParam(funcindex, "VBAT_CV_BUF_step44");
    CParam *VBAT_CV_BUF_step45 = StsGetParam(funcindex, "VBAT_CV_BUF_step45");
    CParam *VBAT_CV_BUF_step46 = StsGetParam(funcindex, "VBAT_CV_BUF_step46");
    CParam *VBAT_CV_BUF_step47 = StsGetParam(funcindex, "VBAT_CV_BUF_step47");
    CParam *VBAT_CV_BUF_step48 = StsGetParam(funcindex, "VBAT_CV_BUF_step48");
    CParam *VBAT_CV_BUF_step49 = StsGetParam(funcindex, "VBAT_CV_BUF_step49");
    CParam *VBAT_CV_BUF_step50 = StsGetParam(funcindex, "VBAT_CV_BUF_step50");
    CParam *VBAT_CV_BUF_step51 = StsGetParam(funcindex, "VBAT_CV_BUF_step51");
    CParam *VBAT_CV_BUF_step52 = StsGetParam(funcindex, "VBAT_CV_BUF_step52");
    CParam *VBAT_CV_BUF_step53 = StsGetParam(funcindex, "VBAT_CV_BUF_step53");
    CParam *VBAT_CV_BUF_step54 = StsGetParam(funcindex, "VBAT_CV_BUF_step54");
    CParam *VBAT_CV_BUF_step55 = StsGetParam(funcindex, "VBAT_CV_BUF_step55");
    CParam *VBAT_CV_BUF_step56 = StsGetParam(funcindex, "VBAT_CV_BUF_step56");
    CParam *VBAT_CV_BUF_step57 = StsGetParam(funcindex, "VBAT_CV_BUF_step57");
    CParam *VBAT_CV_BUF_step58 = StsGetParam(funcindex, "VBAT_CV_BUF_step58");
    CParam *VBAT_CV_BUF_step59 = StsGetParam(funcindex, "VBAT_CV_BUF_step59");
    CParam *VBAT_CV_BUF_step60 = StsGetParam(funcindex, "VBAT_CV_BUF_step60");
    CParam *VBAT_CV_BUF_step61 = StsGetParam(funcindex, "VBAT_CV_BUF_step61");
    CParam *VBAT_CV_BUF_step62 = StsGetParam(funcindex, "VBAT_CV_BUF_step62");
    CParam *VBAT_CV_BUF_step63 = StsGetParam(funcindex, "VBAT_CV_BUF_step63");
    CParam *VBAT_CV_BUF_pre_value = StsGetParam(funcindex, "VBAT_CV_BUF_pre_value");
    CParam *VBAT_CV_BUF_pre_bit = StsGetParam(funcindex, "VBAT_CV_BUF_pre_bit");
    CParam *VBAT_CV_BUF_post_bit = StsGetParam(funcindex, "VBAT_CV_BUF_post_bit");
    CParam *VBAT_CV_BUF_updated = StsGetParam(funcindex, "VBAT_CV_BUF_updated");
    CParam *VBAT_CV_BUF_guessed = StsGetParam(funcindex, "VBAT_CV_BUF_guessed");
    CParam *VBAT_CV_BUF_target = StsGetParam(funcindex, "VBAT_CV_BUF_target");
    CParam *VBAT_CV_BUF_post_value = StsGetParam(funcindex, "VBAT_CV_BUF_post_value");
    CParam *VBAT_LOOP_IND_L = StsGetParam(funcindex, "VBAT_LOOP_IND_L");
    CParam *VBAT_LOOP_IND_H = StsGetParam(funcindex, "VBAT_LOOP_IND_H");
    CParam *VBAT_CV_BUF_post_rt = StsGetParam(funcindex, "VBAT_CV_BUF_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	////------------Connect Serve loop of BOOST mode, need confirm when 


	double vbat_loop_high[SITE_NUM] = { 0 };
	double vbat_loop_low[SITE_NUM] = { 0 };
	double vbat_serve_loop[SITE_NUM] = { 0 };
	dcm.I2CConnect();
	if (!check_relay_off(VBUS_FOVI, K54_QPoint, K65_SVLP_VBUS, &Relay_Off_Check))
	{
		FOR_EACH_VALID_SITE(site)
		{
			VBAT_LOOP_IND_L->SetTestResult(site, 0, 99979);
			VBAT_LOOP_IND_H->SetTestResult(site, 0, 99979);
		}
	}
	else
	{
		cbite.SetOn(K54_QPoint, K67_AMP2_Power,/* K62_AMP3_Power,*/K37_VAC_Cap, K25_VCC_Cap, K16_VBUS_Cap, K43_INT_ACM, K58_INT_PU, -1);//amp no connect
		delay_ms(4);
		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		double vbat_v = 3.8;
		VBUS_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_ON);
		VAC123_ACM.Set(FV, 5, ACM200_20V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, vbat_v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 4.53, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(5);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x0A, (DWORD)spec[DEVICE_SEL]("CV_CONFIG"));
		//I2CWriteSameData(DEV_ADDR, 0x0A, 0x11);
		I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x13);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(VBAT_CV,1),(IBAT_LIMIT,7),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(DIS_NTC_DETECTION_ANALOG,1)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x20);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x67, 0x03);//		
		I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		over write vbat high than trikle
		Inherit_register();
		delay_ms(2);
		SCL_ACM.Set(FV, 1.8, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, vbat_v, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
		//VBAT_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		cbite.SetOn(K54_QPoint, K67_AMP2_Power, /*K62_AMP3_Power ,*/K37_VAC_Cap, K25_VCC_Cap, K16_VBUS_Cap, K43_INT_ACM, K58_INT_PU, K24_SVLP_VBAT, -1);//amp no connect
		delay_ms(3);// 3ms for cbit connect and 2ms for serve loop stable
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FI, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		//VBAT_ACM.MeasureVI(100, 50);

		delay_ms(5);
		Retest_voltage_unstable_with_time_out(VBAT_ACM, vbat_serve_loop, 3, 5.5, 10, 30, MEAS_V);
		TRIM_NODE &MNT_VBAT_CV_BUF = trim_reg.trim("mnt_vbat_cv_buf");
		MNT_VBAT_CV_BUF.execute(measure_mnt_vbat_cv_buf, spec, funcindex, funclabel, 1, 0, 0);

		Retry_trim_search(&MNT_VBAT_CV_BUF, measure_mnt_vbat_cv_buf, spec, funcindex, funclabel, 1.0, -1, 1, 3, false, 1.3);

		delay_ms(1);
		SDA_INT_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			vbat_loop_high[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
		}
		I2CWriteSameData(DEV_ADDR, 0x55, 0x88);
		delay_ms(1);
		SDA_INT_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			vbat_loop_low[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
		}

		cbite.SetOn(K54_QPoint, K67_AMP2_Power, K37_VAC_Cap, K25_VCC_Cap, K16_VBUS_Cap, K43_INT_ACM, K58_INT_PU, -1);//amp no connect
		delay_ms(4);
		cbite.SetOn(K54_QPoint, K37_VAC_Cap, K25_VCC_Cap, K16_VBUS_Cap, K43_INT_ACM, K58_INT_PU, -1);//amp no connect
		delay_ms(15);// delay 15ms for amplifier relay off

		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		SCL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);

		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		cbite.SetOn(-1);//amp no connect
		delay_ms(3);
		FOR_EACH_VALID_SITE(site)
		{
			VBAT_LOOP_IND_L->SetTestResult(site, 0, vbat_loop_low[site]);
			VBAT_LOOP_IND_H->SetTestResult(site, 0, vbat_loop_high[site]);
		}
	}
    return 0;
}
 
DUT_API int Trim_IBAT_CC_LOOP(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IBAT_CC_LOOP_step0 = StsGetParam(funcindex, "IBAT_CC_LOOP_step0");
    CParam *IBAT_CC_LOOP_step1 = StsGetParam(funcindex, "IBAT_CC_LOOP_step1");
    CParam *IBAT_CC_LOOP_step2 = StsGetParam(funcindex, "IBAT_CC_LOOP_step2");
    CParam *IBAT_CC_LOOP_step3 = StsGetParam(funcindex, "IBAT_CC_LOOP_step3");
    CParam *IBAT_CC_LOOP_step4 = StsGetParam(funcindex, "IBAT_CC_LOOP_step4");
    CParam *IBAT_CC_LOOP_step5 = StsGetParam(funcindex, "IBAT_CC_LOOP_step5");
    CParam *IBAT_CC_LOOP_step6 = StsGetParam(funcindex, "IBAT_CC_LOOP_step6");
    CParam *IBAT_CC_LOOP_step7 = StsGetParam(funcindex, "IBAT_CC_LOOP_step7");
    CParam *IBAT_CC_LOOP_step8 = StsGetParam(funcindex, "IBAT_CC_LOOP_step8");
    CParam *IBAT_CC_LOOP_step9 = StsGetParam(funcindex, "IBAT_CC_LOOP_step9");
    CParam *IBAT_CC_LOOP_step10 = StsGetParam(funcindex, "IBAT_CC_LOOP_step10");
    CParam *IBAT_CC_LOOP_step11 = StsGetParam(funcindex, "IBAT_CC_LOOP_step11");
    CParam *IBAT_CC_LOOP_step12 = StsGetParam(funcindex, "IBAT_CC_LOOP_step12");
    CParam *IBAT_CC_LOOP_step13 = StsGetParam(funcindex, "IBAT_CC_LOOP_step13");
    CParam *IBAT_CC_LOOP_step14 = StsGetParam(funcindex, "IBAT_CC_LOOP_step14");
    CParam *IBAT_CC_LOOP_step15 = StsGetParam(funcindex, "IBAT_CC_LOOP_step15");
    CParam *IBAT_CC_LOOP_pre_value = StsGetParam(funcindex, "IBAT_CC_LOOP_pre_value");
    CParam *IBAT_CC_LOOP_pre_bit = StsGetParam(funcindex, "IBAT_CC_LOOP_pre_bit");
    CParam *IBAT_CC_LOOP_post_bit = StsGetParam(funcindex, "IBAT_CC_LOOP_post_bit");
    CParam *IBAT_CC_LOOP_updated = StsGetParam(funcindex, "IBAT_CC_LOOP_updated");
    CParam *IBAT_CC_LOOP_guessed = StsGetParam(funcindex, "IBAT_CC_LOOP_guessed");
    CParam *IBAT_CC_LOOP_target = StsGetParam(funcindex, "IBAT_CC_LOOP_target");
    CParam *IBAT_CC_LOOP_post_value = StsGetParam(funcindex, "IBAT_CC_LOOP_post_value");
    CParam *IBAT_CC_LOOP_post_rt = StsGetParam(funcindex, "IBAT_CC_LOOP_post_rt");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	//QVM_GP.Connect();

	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K32_PMID_Cap, K28_VDRV_Cap, K25_VCC_Cap,-1);
	delay_ms(3);
	BTST_ACM.Set(FV, 3, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);// avoid spike
	SW_ACM.Set(FV, 3, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);// avoid spike
	VBAT_ACM.Set(FV, 3.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	entertestmode();
	//		field[(WAKE_UP,1),(IBAT_LIMIT,0),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(D2A_BUBO_ATEST0,13),(DIS_NTC_DETECTION_ANALOG,1),(D2A_BUBO_TM_FORCE_IBAT_SNS_OFF,1),(ATEST1_MUX,15)]
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);//(BUBO_MODE,1),
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);//Ibus_limit_off
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);//		field[(WAKE_UP,1)
	I2CWriteSameData(DEV_ADDR, 0x56, 0x06);//(EN_ATEST1,1),(EN_ATEST0,1),
	I2CWriteSameData(DEV_ADDR, 0x57, 0x0F);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x40);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x0D);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x07);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x80);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0xE0);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	delay_ms(2);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0xFD);//		field[(D2A_BUBO_ATEST1,15)]

	STSSetTimeCheck(1);
	Inherit_register();
	BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);// avoid spike
	SW_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);//avoid spike
	delay_us(200);
	BTST_ACM.Set(FV, 9, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	double timemeas = STSGetTimeElapsed(1);
	delay_ms(2);
	TRIM_NODE &IBAT_CC_LOOP = trim_reg.trim("ibat_cc_loop");
	IBAT_CC_LOOP.execute(measure_ibat_cc_loop, spec, funcindex, funclabel, 1, 0, 1);

	PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	//FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV,0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_OFF);
	//FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_OFF);
	SW_ACM.Set(FV, 0, ACM200_20V, ACM200_10MA, ACM200_RELAY_OFF);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_10MA, ACM200_RELAY_OFF);
	AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10MA, FOVIe_RELAY_OFF);
	NTC_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10MA, FOVIe_RELAY_OFF);
	BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
    return 0;
}
 
DUT_API int OTP_BURN(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *Burn_Done = StsGetParam(funcindex, "Burn_Done");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	DWORD  REG_F0_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_F1_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_F2_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_F3_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_F4_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_F5_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_F6_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_F7_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_F8_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_F9_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_FA_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_FB_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_FC_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_FD_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_FE_BestCode[SITE_NUM] = { 0 };
	DWORD  REG_FF_BestCode[SITE_NUM] = { 0 };

	//=================================Get All Best Code Need to Burn into OTP
	FOR_EACH_VALID_SITE(site)
	{
		//trim_reg.sel("addr_trim").set_working(1, site);// chenyang
		REG_F0_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_F0").get_working(site);
		REG_F1_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_F1").get_working(site);
		REG_F2_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_F2").get_working(site);
		REG_F3_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_F3").get_working(site);
		REG_F4_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_F4").get_working(site);
		REG_F5_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_F5").get_working(site);
		REG_F6_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_F6").get_working(site);
		REG_F7_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_F7").get_working(site);
		REG_F8_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_F8").get_working(site);
		REG_F9_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_F9").get_working(site);
		REG_FA_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_FA").get_working(site);
		REG_FB_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_FB").get_working(site);
		REG_FC_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_FC").get_working(site);
		REG_FD_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_FD").get_working(site);
		REG_FE_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_FE").get_working(site);
		REG_FF_BestCode[site] = (DWORD)trim_reg.assy("EFUSE_REG_FF").get_working(site);
	}

	DWORD BurnKey[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		if (BURN_FLAG[site] == FRESH)
		{
			BurnKey[site] = 0x01;// field[(NVM_PROG_ALL, 1)]
		}                                 
		else
		{
			BurnKey[site] = 0x00;
		}
	}

	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn)
	{
		//-------------------------------OTP BURN FUNCTION--------------------------//
		dcm.I2CConnect();
		cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K16_VBUS_Cap, K57_SDA_PU, K53_SCL_PU, K25_VCC_Cap,-1);
		delay_ms(5);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//VBAT
		VBUS_FOVI.Set(FV, 8.5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
		dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, REG_F0_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, REG_F1_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xF2, 1, REG_F2_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xF3, 1, REG_F3_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xF4, 1, REG_F4_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xF5, 1, REG_F5_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xF6, 1, REG_F6_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xF7, 1, REG_F7_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xF8, 1, REG_F8_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xF9, 1, REG_F9_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xFA, 1, REG_FA_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xFB, 1, REG_FB_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xFC, 1, REG_FC_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xFD, 1, REG_FD_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xFE, 1, REG_FE_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0xFF, 1, REG_FF_BestCode);
		dcm.I2CWriteData(DEV_ADDR, 0x53, 1, BurnKey);
		//dcm.I2CWriteData(0xD0, 0x53, 1, BurnKey);//chenyang
		delay_ms(50);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//VBAT
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//VBAT
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		trim_reg.assy("EFUSE_REG_REGISTER").copy_work_to_prog(site);
		Burn_Done->SetTestResult(site, 0, 1);
	}


	return 0;
}

DUT_API int OTP_Read_Post(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBG_PosRd = StsGetParam(funcindex, "VBG_PosRd");
    CParam *BG_RES_DIV_PosRd = StsGetParam(funcindex, "BG_RES_DIV_PosRd");
    CParam *V1P2_BUF_PosRd = StsGetParam(funcindex, "V1P2_BUF_PosRd");
    CParam *DAC_BUF_PosRd = StsGetParam(funcindex, "DAC_BUF_PosRd");
    CParam *IZTC_RES_PosRd = StsGetParam(funcindex, "IZTC_RES_PosRd");
    CParam *OSC_4P5M_PosRd = StsGetParam(funcindex, "OSC_4P5M_PosRd");
    CParam *VBAT_RSNS_LOOP_PosRd = StsGetParam(funcindex, "VBAT_RSNS_LOOP_PosRd");
    CParam *AMUX_EA_OS_PosRd = StsGetParam(funcindex, "AMUX_EA_OS_PosRd");
    CParam *IBUS_SNS_GAIN_PosRd = StsGetParam(funcindex, "IBUS_SNS_GAIN_PosRd");
    CParam *IBUS_SNS_EA_OS_PosRd = StsGetParam(funcindex, "IBUS_SNS_EA_OS_PosRd");
    CParam *BUCK_RCS_PosRd = StsGetParam(funcindex, "BUCK_RCS_PosRd");
    CParam *BOOST_RCS_PosRd = StsGetParam(funcindex, "BOOST_RCS_PosRd");
    CParam *CS_HS_OS_PosRd = StsGetParam(funcindex, "CS_HS_OS_PosRd");
    CParam *CS_LS_OS_PosRd = StsGetParam(funcindex, "CS_LS_OS_PosRd");
    CParam *BUCK_HS_GAIN_PosRd = StsGetParam(funcindex, "BUCK_HS_GAIN_PosRd");
    CParam *BUCK_HS_OS_PosRd = StsGetParam(funcindex, "BUCK_HS_OS_PosRd");
    CParam *BOOST_HS_GAIN_PosRd = StsGetParam(funcindex, "BOOST_HS_GAIN_PosRd");
    CParam *BOOST_HS_OS_PosRd = StsGetParam(funcindex, "BOOST_HS_OS_PosRd");
    CParam *BUCK_LS_GAIN_PosRd = StsGetParam(funcindex, "BUCK_LS_GAIN_PosRd");
    CParam *BUCK_LS_OS_PosRd = StsGetParam(funcindex, "BUCK_LS_OS_PosRd");
    CParam *BOOST_LS_GAIN_PosRd = StsGetParam(funcindex, "BOOST_LS_GAIN_PosRd");
    CParam *BOOST_LS_OS_PosRd = StsGetParam(funcindex, "BOOST_LS_OS_PosRd");
    CParam *IBUS_LOOP_OS_PosRd = StsGetParam(funcindex, "IBUS_LOOP_OS_PosRd");
    CParam *BUCK_VBUS_EA_OS_PosRd = StsGetParam(funcindex, "BUCK_VBUS_EA_OS_PosRd");
    CParam *BOOST_VBUS_EA_OS_PosRd = StsGetParam(funcindex, "BOOST_VBUS_EA_OS_PosRd");
    CParam *VBAT_CV_BUF_PosRd = StsGetParam(funcindex, "VBAT_CV_BUF_PosRd");
    CParam *IBAT_CC_LOOP_PosRd = StsGetParam(funcindex, "IBAT_CC_LOOP_PosRd");
    CParam *IBUS_OFF_TERM_FLT_PosRd = StsGetParam(funcindex, "IBUS_OFF_TERM_FLT_PosRd");
    CParam *ADDR_TRIM_PosRd = StsGetParam(funcindex, "ADDR_TRIM_PosRd");
    CParam *PART_ID_TRIM_PosRd = StsGetParam(funcindex, "PART_ID_TRIM_PosRd");
    CParam *PART_ID_6802_PosRd = StsGetParam(funcindex, "PART_ID_6802_PosRd");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	DOUBLE BG_POS_CODE[SITE_NUM] = { 0 }; //1
	DOUBLE BG_RES_DIV_POS_CODE[SITE_NUM] = { 0 };//2
	DOUBLE IZTC_POS_CODE[SITE_NUM] = { 0 };// 3	
	DOUBLE OSC_4P5M_POS_CODE[SITE_NUM] = { 0 };//4
	DOUBLE DAC_BUF_OS_POS_CODE[SITE_NUM] = { 0 };// 6
	DOUBLE V1P2_BUF_OS_POS_CODE[SITE_NUM] = { 0 };//8
	DOUBLE VBAT_SNS_LOOP_POS_CODE[SITE_NUM] = { 0 };//18
	DOUBLE AMUX_EA_OS_POS_CODE[SITE_NUM] = { 0 };// 7
	DOUBLE IBUS_SNS_GAIN__POS_CODE[SITE_NUM] = { 0 };
	DOUBLE IBUS_SNS_EA_OS__POS_CODE[SITE_NUM] = { 0 };
	DOUBLE BUCK_RCS_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE BOOST_RCS_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE CS_HS_OS_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE CS_LS_OS_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE BUCK_HS_GAIN_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE BUCK_HS_OS_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE BOOST_HS_GAIN_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE BOOST_HS_OS_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE BUCK_LS_GAIN_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE BUCK_LS_OS_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE BOOST_LS_GAIN_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE BOOST_LS_OS_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE IBUS_LOOP_OS_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE BUCK_VBUS_EA_OS_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE BOOST_VBUS_EA_OS_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE VBAT_CV_BUF_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE IBAT_CC_LOOP_POS_CODE[SITE_NUM] = { 0 };
	//--------OPT_CODE
	DOUBLE IBUS_OFF_TERM_FLT_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE ADDR_TRIM_POS_CODE[SITE_NUM] = { 0 };
	DOUBLE PART_ID_TRIM_POS_CODE[SITE_NUM] = { 0 };


	ULONG REG_F0_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_F1_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_F2_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_F3_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_F4_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_F5_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_F6_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_F7_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_F8_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_F9_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_FA_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_FB_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_FC_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_FD_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_FE_POS_READ[SITE_NUM] = { 0 };
	ULONG REG_FF_POS_READ[SITE_NUM] = { 0 };

	//-------------------------------OTP READ FUNCTION--------------------------//
	dcm.I2CConnect();
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K57_SDA_PU, K53_SCL_PU, K25_VCC_Cap, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//VBAT
	VCC_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON); 
	delay_ms(10);//add for specical lot 
	entertestmode();
	I2C_READ_BYTE(DEV_ADDR, 0xF0, REG_F0_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF1, REG_F1_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF2, REG_F2_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF3, REG_F3_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF4, REG_F4_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF5, REG_F5_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF6, REG_F6_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF7, REG_F7_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF8, REG_F8_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xF9, REG_F9_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xFA, REG_FA_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xFB, REG_FB_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xFC, REG_FC_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xFD, REG_FD_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xFE, REG_FE_POS_READ);
	I2C_READ_BYTE(DEV_ADDR, 0xFF, REG_FF_POS_READ);

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//VBAT
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);//VBAT
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

	//-------------Read all register and set into readback
	FOR_EACH_VALID_SITE(site)
	{

		trim_reg.assy("EFUSE_REG_F0").set_read_back((INT)REG_F0_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_F1").set_read_back((INT)REG_F1_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_F2").set_read_back((INT)REG_F2_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_F3").set_read_back((INT)REG_F3_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_F4").set_read_back((INT)REG_F4_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_F5").set_read_back((INT)REG_F5_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_F6").set_read_back((INT)REG_F6_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_F7").set_read_back((INT)REG_F7_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_F8").set_read_back((INT)REG_F8_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_F9").set_read_back((INT)REG_F9_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_FA").set_read_back((INT)REG_FA_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_FB").set_read_back((INT)REG_FB_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_FC").set_read_back((INT)REG_FC_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_FD").set_read_back((INT)REG_FD_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_FE").set_read_back((INT)REG_FE_POS_READ[site], site);
		trim_reg.assy("EFUSE_REG_FF").set_read_back((INT)REG_FF_POS_READ[site], site);

	}

	int ReadSameAsBurn[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		if (trim_reg.assy("EFUSE_REG_REGISTER").comp_prog_to_read(site))
		{
			ReadSameAsBurn[site] = 1; // Means device OTP Read value same as Burn value
		}
		else
		{
			ReadSameAsBurn[site] = 0;// Means device OTP Read value different as Burn value
		}
	}

	FOR_EACH_VALID_SITE(site)
	{
		BG_POS_CODE[site] = trim_reg.trim("bandgap").get_read_back(site);//check,1
		BG_RES_DIV_POS_CODE[site] = trim_reg.trim("bg_res_div").get_read_back(site);//check,2
		IZTC_POS_CODE[site] = trim_reg.trim("iztc_res").get_read_back(site);//check,3
		OSC_4P5M_POS_CODE[site] = trim_reg.trim("osc_4p5m").get_read_back(site);//check,4
		DAC_BUF_OS_POS_CODE[site] = trim_reg.trim("mnt_dac_buf_os").get_read_back(site);//check,6	
		V1P2_BUF_OS_POS_CODE[site] = trim_reg.trim("mnt_v1p2_buf").get_read_back(site);//check,7
		VBAT_SNS_LOOP_POS_CODE[site] = trim_reg.trim("mnt_vbat_rsns_loop").get_read_back(site);//check,8
		AMUX_EA_OS_POS_CODE[site] = trim_reg.trim("amux_ea_os").get_read_back(site);//check,9
		IBUS_SNS_GAIN__POS_CODE[site] = trim_reg.trim("ibus_sns_gain").get_read_back(site);//check,10
		IBUS_SNS_EA_OS__POS_CODE[site] = trim_reg.trim("ibus_sns_ea_os").get_read_back(site);//check,11
		BUCK_RCS_POS_CODE[site] = trim_reg.trim("buck_rcs").get_read_back(site);//check,12
		BOOST_RCS_POS_CODE[site] = trim_reg.trim("boost_rcs").get_read_back(site);//check,13
		CS_HS_OS_POS_CODE[site] = trim_reg.trim("cs_hsfet_os").get_read_back(site);//check,14	
		CS_LS_OS_POS_CODE[site] = trim_reg.trim("cs_lsfet_os").get_read_back(site);//check,15
		BUCK_HS_GAIN_POS_CODE[site] = trim_reg.trim("buck_hsfet_gain").get_read_back(site);//check,16
		BUCK_HS_OS_POS_CODE[site] = trim_reg.trim("buck_hsfet_os").get_read_back(site);//check,17
		BOOST_HS_GAIN_POS_CODE[site] = trim_reg.trim("boost_hsfet_gain").get_read_back(site);//check,18
		BOOST_HS_OS_POS_CODE[site] = trim_reg.trim("boost_hsfet_os").get_read_back(site);//check,19
		BUCK_LS_GAIN_POS_CODE[site] = trim_reg.trim("buck_lsfet_gain").get_read_back(site);//check,20
		BUCK_LS_OS_POS_CODE[site] = trim_reg.trim("buck_lsfet_os").get_read_back(site);//check,21
		BOOST_LS_GAIN_POS_CODE[site] = trim_reg.trim("boost_lsfet_gain").get_read_back(site);//check,22
		BOOST_LS_OS_POS_CODE[site] = trim_reg.trim("boost_lsfet_os").get_read_back(site);//check,23
		IBUS_LOOP_OS_POS_CODE[site] = trim_reg.trim("ibus_loop_os").get_read_back(site);//check,24
		BUCK_VBUS_EA_OS_POS_CODE[site] = trim_reg.trim("mnt_vbus_ea_os_buck").get_read_back(site);//check,25
		BOOST_VBUS_EA_OS_POS_CODE[site] = trim_reg.trim("mnt_vbus_ea_os_boost").get_read_back(site);//check,26
		VBAT_CV_BUF_POS_CODE[site] = trim_reg.trim("mnt_vbat_cv_buf").get_read_back(site);//check,27
		IBAT_CC_LOOP_POS_CODE[site] = trim_reg.trim("ibat_cc_loop").get_read_back(site);//check,28
		IBUS_OFF_TERM_FLT_POS_CODE[site] = trim_reg.sel("ibus_off_term_flt").get_read_back(site);//check,29
		ADDR_TRIM_POS_CODE[site] = trim_reg.sel("addr_trim").get_read_back(site);//check,30
		PART_ID_TRIM_POS_CODE[site] = trim_reg.sel("part_id_trim").get_read_back(site);//check,31
	}

	FOR_EACH_VALID_SITE(site)
	{
		VBG_PosRd->SetTestResult(site, 0, BG_POS_CODE[site]);//
		BG_RES_DIV_PosRd->SetTestResult(site, 0, BG_RES_DIV_POS_CODE[site]);//
		V1P2_BUF_PosRd->SetTestResult(site, 0, V1P2_BUF_OS_POS_CODE[site]);//
		DAC_BUF_PosRd->SetTestResult(site, 0, DAC_BUF_OS_POS_CODE[site]);//
		IZTC_RES_PosRd->SetTestResult(site, 0, IZTC_POS_CODE[site]);//
		OSC_4P5M_PosRd->SetTestResult(site, 0, OSC_4P5M_POS_CODE[site]);//
		VBAT_RSNS_LOOP_PosRd->SetTestResult(site, 0, VBAT_SNS_LOOP_POS_CODE[site]);//
		AMUX_EA_OS_PosRd->SetTestResult(site, 0, AMUX_EA_OS_POS_CODE[site]);//
		IBUS_SNS_GAIN_PosRd->SetTestResult(site, 0, IBUS_SNS_GAIN__POS_CODE[site]);//
		IBUS_SNS_EA_OS_PosRd->SetTestResult(site, 0, IBUS_SNS_EA_OS__POS_CODE[site]);//
		BUCK_RCS_PosRd->SetTestResult(site, 0, BUCK_RCS_POS_CODE[site]);//
		BOOST_RCS_PosRd->SetTestResult(site, 0, BOOST_RCS_POS_CODE[site]);//
		CS_HS_OS_PosRd->SetTestResult(site, 0, CS_HS_OS_POS_CODE[site]);//
		CS_LS_OS_PosRd->SetTestResult(site, 0, CS_LS_OS_POS_CODE[site]);//
		BUCK_HS_GAIN_PosRd->SetTestResult(site, 0, BUCK_HS_GAIN_POS_CODE[site]);//
		BUCK_HS_OS_PosRd->SetTestResult(site, 0, BUCK_HS_OS_POS_CODE[site]);//
		BOOST_HS_GAIN_PosRd->SetTestResult(site, 0, BOOST_HS_GAIN_POS_CODE[site]);//
		BOOST_HS_OS_PosRd->SetTestResult(site, 0, BOOST_HS_OS_POS_CODE[site]);//
		BUCK_LS_GAIN_PosRd->SetTestResult(site, 0, BUCK_LS_GAIN_POS_CODE[site]);//
		BUCK_LS_OS_PosRd->SetTestResult(site, 0, BUCK_LS_OS_POS_CODE[site]);//
		BOOST_LS_GAIN_PosRd->SetTestResult(site, 0, BOOST_LS_GAIN_POS_CODE[site]);//
		BOOST_LS_OS_PosRd->SetTestResult(site, 0, BOOST_LS_OS_POS_CODE[site]);//
		IBUS_LOOP_OS_PosRd->SetTestResult(site, 0, IBUS_LOOP_OS_POS_CODE[site]);//
		BUCK_VBUS_EA_OS_PosRd->SetTestResult(site, 0, BUCK_VBUS_EA_OS_POS_CODE[site]);//
		BOOST_VBUS_EA_OS_PosRd->SetTestResult(site, 0, BOOST_VBUS_EA_OS_POS_CODE[site]);//
		VBAT_CV_BUF_PosRd->SetTestResult(site, 0, VBAT_CV_BUF_POS_CODE[site]);//
		IBAT_CC_LOOP_PosRd->SetTestResult(site, 0, IBAT_CC_LOOP_POS_CODE[site]);//
		IBUS_OFF_TERM_FLT_PosRd->SetTestResult(site, 0, IBUS_OFF_TERM_FLT_POS_CODE[site]);//
		ADDR_TRIM_PosRd->SetTestResult(site, 0, ADDR_TRIM_POS_CODE[site]);////chenyang
		if (extractIntFromString(DEVICE_SEL) == 6801 || extractIntFromString(DEVICE_SEL) == 6803)
		{
			PART_ID_TRIM_PosRd->SetTestResult(site, 0, PART_ID_TRIM_POS_CODE[site]);//
		}
		if (extractIntFromString(DEVICE_SEL) == 6802)
		{
			PART_ID_6802_PosRd->SetTestResult(site, 0, PART_ID_TRIM_POS_CODE[site]);//
		}
	}


	return 0;
}

DUT_API int IQ_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IQ_Standby1_DSM = StsGetParam(funcindex, "IQ_Standby1_DSM");
    CParam *IQ_Standby2_DSM = StsGetParam(funcindex, "IQ_Standby2_DSM");
    CParam *NTC_MNT_IQ = StsGetParam(funcindex, "NTC_MNT_IQ");
    CParam *AMUX_IQ_WP = StsGetParam(funcindex, "AMUX_IQ_WP");
    CParam *AMUX_IQ_EN = StsGetParam(funcindex, "AMUX_IQ_EN");
    CParam *AMUX_IQ = StsGetParam(funcindex, "AMUX_IQ");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	bool Funstable = false;
	bool FSunstable[SITE_NUM] = { 0 };
	double Iq_standby1[SITE_NUM] = { 0 };
	double Iq_standby2[SITE_NUM] = { 0 };
	dcm.I2CConnect();
	cbite.SetOn(-1);
	delay_ms(3);
	VDRV_AMP_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
	delay_ms(1);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x07, 0x00);//		field[(VAC1_APORT_DET_ENABLE,1),(VAC2_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,0)]
	delay_ms(3);
	Retest_current_unstable_with_time_out(VBAT_ACM, Iq_standby1, spec.get_low_limit("IQ_Standby1_DSM"), spec.get_high_limit("IQ_Standby1_DSM"), 2, 50, MEAS_UA);

   I2CWriteSameData(DEV_ADDR, 0x07, 0x04);	//		field[(VAC1_APORT_DET_ENABLE,0),(VAC2_APORT_DET_ENABLE,0),(VAC_SNK_DET_SEL,0)]
   delay_ms(3);
   Retest_current_unstable_with_time_out(VBAT_ACM, Iq_standby2, spec.get_low_limit("IQ_Standby2_DSM"), spec.get_high_limit("IQ_Standby2_DSM"), 2, 50, MEAS_UA);
	double mnt_ntc_iq_pre[SITE_NUM] = { 0 };
	double mnt_ntc_iq_pos[SITE_NUM] = { 0 };
	double mnt_ntc_iq[SITE_NUM] = { 0 };
	double Iq_wakeup[SITE_NUM] = { 0 };
	double Iq_amux_en[SITE_NUM] = { 0 };
	double Iq_amux[SITE_NUM] = { 0 };

	I2CWriteSameData(DEV_ADDR, 0x10, 0x43); //		field[(WAKE_UP,1)]
	//VBAT_ACM.MeasureVI(2000, 500);
	delay_ms(8);
	Retest_current_unstable_with_time_out(VBAT_ACM, Iq_wakeup, 500, 1400, 2, 50, MEAS_UA);// for some sample need over 600ms
	//---------------------
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F); //		field[(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(3);
	VBAT_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Iq_amux_en[site] =VBAT_ACM.GetMeasResult(site, MIRET)*1e6;//uA
		Iq_amux[site] = Iq_amux_en[site] - Iq_wakeup[site];
	}
	I2CWriteSameData(DEV_ADDR, 0x11, 0x00);

	NTC_FOVI.Set(FV, 0.1, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	Retest_current_unstable_with_time_out(VBAT_ACM, mnt_ntc_iq_pre, 500, 2000.2, 5, 50, MEAS_UA);

	I2CWriteSameData(DEV_ADDR, 0x67, 0x0B);//		field[(D2A_OVRD_SEL,11)]
	I2CWriteSameData(DEV_ADDR, 0x68, 0x20);//		field[(OVRD_VALUE,2)]
	delay_ms(3);
	VBAT_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		mnt_ntc_iq_pos[site] = VBAT_ACM.GetMeasResult(site, MIRET)*1e6;//uA
		mnt_ntc_iq[site] = mnt_ntc_iq_pre[site] - mnt_ntc_iq_pos[site];
	}

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(1);
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}

	FOR_EACH_VALID_SITE(site)
	{
		IQ_Standby1_DSM->SetTestResult(site, 0, Iq_standby1[site]);//mA change to uA
		IQ_Standby2_DSM->SetTestResult(site, 0, Iq_standby2[site]);//mA change to uA
		NTC_MNT_IQ->SetTestResult(site, 0, mnt_ntc_iq[site]);//mA change to uA
		AMUX_IQ_WP->SetTestResult(site, 0, Iq_wakeup[site]);//mA change to uA
		AMUX_IQ_EN->SetTestResult(site, 0, Iq_amux_en[site]);//mA change to uA
		AMUX_IQ->SetTestResult(site, 0, Iq_amux[site]);//mA change to uA
	}




    return 0;
}
 
DUT_API int ISUSPEND_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *Iin_suspend_DSM = StsGetParam(funcindex, "Iin_suspend_DSM");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	double Isuspend[SITE_NUM] = { 0 };
	cbite.SetOn(-1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(5);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x08, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);//		field[(WAKE_UP,1),(AC1_GATE_ON,1)]
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(2);
	VBAT_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Isuspend[site] = VBAT_ACM.GetMeasResult(site, MIRET)*1e3;//mA
	}
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_10MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		Iin_suspend_DSM->SetTestResult(site, 0, Isuspend[site]);
	}
    return 0;
}
 
DUT_API int IQ_Screen_Test(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IQ_Screen_Curr = StsGetParam(funcindex, "IQ_Screen_Curr");
    CParam *IQ_Abnormal_Curr = StsGetParam(funcindex, "IQ_Abnormal_Curr");
    CParam *IQ_Recover_VBAT = StsGetParam(funcindex, "IQ_Recover_VBAT");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	return 0;
}

DUT_API int OSC_Accuracy(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *OSC_64K = StsGetParam(funcindex, "OSC_64K");
    CParam *OSC_35K = StsGetParam(funcindex, "OSC_35K");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	double qtmu_64k[SITE_NUM] = { 0 };
	double qtmu_35k[SITE_NUM] = { 0 };
	QTMU_GP.Connect(QTMUe_RELAY_CHA);
	QTMU_GP.SetInSource(QTMUe_SINGLE_SOURCE_A);
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap, K58_INT_PU, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);	
	delay_ms(5);
	entertestmode();
	//------------------------OSC Measurement-------------//
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x99);
	I2CWriteSameData(DEV_ADDR, 0x57, 0x08); //		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,25),(ATEST1_MUX,8)]
	delay_ms(2);

	//================================第1组
	SetTrimGroup(0x5555);
	GRP_CNT = 1;
	QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.5, QTMUe_FILTER_PASS);//signal input to CHB,select 10V range,trigger=2.0V,rising edge
	QTMU_GP.Connect(QTMUe_RELAY_CHA);
	QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS); //measure frequency,timeout=10ms,sample 20 cycles
	QTMU_GP_MEASURE(qtmu_35k, GRP_CNT);

	I2CWriteSameData(DEV_ADDR, 0x57, 0x00); 
	I2CWriteSameData(DEV_ADDR, 0x55, 0x8D); 
	delay_ms(2);
	QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.5, QTMUe_FILTER_PASS);//signal input to CHB,select 10V range,trigger=2.0V,rising edge
	QTMU_GP.Connect(QTMUe_RELAY_CHA);
	QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS); //measure frequency,timeout=10ms,sample 20 cycles
	QTMU_GP_MEASURE(qtmu_64k, GRP_CNT);
	//================================第2组
	SetTrimGroup(0xAAAA);
	GRP_CNT = 2;
	I2CWriteSameData(DEV_ADDR, 0x55, 0x99);
	I2CWriteSameData(DEV_ADDR, 0x57, 0x08); //		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,25),(ATEST1_MUX,8)]
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K25_VCC_Cap, K6_QTMU_SITE_SEL, K58_INT_PU, -1);// connect QVM group 2// QVM connect PC2
	delay_ms(3);
	QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.5, QTMUe_FILTER_PASS);//signal input to CHB,select 10V range,trigger=2.0V,rising edge
	QTMU_GP.Connect(QTMUe_RELAY_CHA);
	QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS); //measure frequency,timeout=10ms,sample 20 cycles
	QTMU_GP_MEASURE(qtmu_35k, GRP_CNT);

	I2CWriteSameData(DEV_ADDR, 0x57, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x8D);
	delay_ms(2);
	QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.5, QTMUe_FILTER_PASS);//signal input to CHB,select 10V range,trigger=2.0V,rising edge
	QTMU_GP.Connect(QTMUe_RELAY_CHA);
	QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS); //measure frequency,timeout=10ms,sample 20 cycles
	QTMU_GP_MEASURE(qtmu_64k, GRP_CNT);
	SetRecoverSite();

	QTMU_GP.Disconnect(QTMUe_RELAY_CHA);
	VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_10V, FOVIe_100UA, FOVIe_RELAY_ON);
	delay_ms(1);

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);



	//QTMU_GP.Connect(QTMUe_RELAY_CHA);
	//QTMU_GP.SetInSource(QTMUe_SINGLE_SOURCE_A);
	//cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K58_INT_PU, K25_VCC_Cap, -1);
	//delay_ms(5);
	//VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//entertestmode();
	////------------------------OSC Measurement-------------//
	//I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	//I2CWriteSameData(DEV_ADDR, 0x55, 0x99);
	//I2CWriteSameData(DEV_ADDR, 0x57, 0x08); //		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,25),(ATEST1_MUX,8)]
	//delay_ms(2);
	//I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	//I2CWriteSameData(DEV_ADDR, 0x55, 0x99);
	//I2CWriteSameData(DEV_ADDR, 0x57, 0x08); //		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,25),(ATEST1_MUX,8)]
	//delay_ms(5);
	//SetTrimGroup(0x5555);
	//GRP_CNT = 1;
	////================================第1组
	//QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.5, QTMUe_FILTER_PASS);//signal input to CHB,select 10V range,trigger=2.0V,rising edge
	//QTMU_GP.Connect(QTMUe_RELAY_CHA);
	//QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS); //measure frequency,timeout=10ms,sample 20 cycles
	//QTMU_GP_MEASURE(qtmu_35k, GRP_CNT);


	////================================第2组
	//SetTrimGroup(0xAAAA);
	//GRP_CNT = 2;
	//QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS); //measure frequency,timeout=10ms,sample 20 cycles
	//QTMU_GP_MEASURE(qtmu_35k, GRP_CNT);
	//SetRecoverSite();

	//I2CWriteSameData(DEV_ADDR, 0x10, 0x00);
	//I2CWriteSameData(DEV_ADDR, 0x55, 0x00);
	//I2CWriteSameData(DEV_ADDR, 0x57, 0x00); //		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,25),(ATEST1_MUX,8)]
	//I2CWriteSameData(DEV_ADDR, 0x55, 0x8D);//		field[(EN_DTEST0,1),(DTEST0_MUX,13)], osc 64K
	//delay_ms(1);
	//SetTrimGroup(0x5555);
	//GRP_CNT = 1;
	////================================第1组
	//QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS); //measure frequency,timeout=10ms,sample 20 cycles
	//QTMU_GP_MEASURE(qtmu_64k, GRP_CNT);
	////================================第2组
	//SetTrimGroup(0xAAAA);
	//GRP_CNT = 2;
	//QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS); //measure frequency,timeout=10ms,sample 20 cycles
	//QTMU_GP_MEASURE(qtmu_64k, GRP_CNT);
	//SetRecoverSite();
	//QTMU_GP.Disconnect(QTMUe_RELAY_CHA);

	//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	////VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	//cbite.SetOn(K1_PGND2AGND, -1);
	//delay_ms(3);

	FOR_EACH_VALID_SITE(site)
	{
		OSC_64K->SetTestResult(site, 0, qtmu_64k[site]);
		OSC_35K->SetTestResult(site, 0, qtmu_35k[site]);
	}

	return 0;
}

DUT_API int INFRA_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VS_PRE = StsGetParam(funcindex, "VS_PRE");
    CParam *LP_BG = StsGetParam(funcindex, "LP_BG");
    CParam *LP_BG_BUF = StsGetParam(funcindex, "LP_BG_BUF");
    CParam *LP_HR_0P5UA = StsGetParam(funcindex, "LP_HR_0P5UA");
    CParam *LP_PTAT_0P5UA = StsGetParam(funcindex, "LP_PTAT_0P5UA");
    CParam *VSPRE_MAX_CMP_Rise = StsGetParam(funcindex, "VSPRE_MAX_CMP_Rise");
    CParam *VSPRE_MAX_CMP_Fall = StsGetParam(funcindex, "VSPRE_MAX_CMP_Fall");
    CParam *VSPRE_MAX_CMP_Hys = StsGetParam(funcindex, "VSPRE_MAX_CMP_Hys");
    CParam *IRPPO_EA_FB = StsGetParam(funcindex, "IRPPO_EA_FB");
    CParam *IHR_P_1UA = StsGetParam(funcindex, "IHR_P_1UA");
    CParam *IPTAT_1UA = StsGetParam(funcindex, "IPTAT_1UA");
    CParam *AVSS_BG = StsGetParam(funcindex, "AVSS_BG");
    CParam *TSD_TM_High = StsGetParam(funcindex, "TSD_TM_High");
    CParam *TSD_TM_Low = StsGetParam(funcindex, "TSD_TM_Low");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vs_pre_qvm[SITE_NUM] = { 0 };
	double lp_bg[SITE_NUM] = { 0 };
	double lp_bg_buf[SITE_NUM] = { 0 };
	double irppo_ea_fb[SITE_NUM] = { 0 };
	double avss_bg[SITE_NUM] = { 0 };
	double lp_hr_0p5uA[SITE_NUM] = { 0 };
	double lp_ptat_0p5uA[SITE_NUM] = { 0 };
	double iptat_1uA[SITE_NUM] = { 0 };
	double ihr_p_1uA[SITE_NUM] = { 0 };
	double vspre_max_cmp_rise[SITE_NUM] = { 0 };
	double vspre_max_cmp_fall[SITE_NUM] = { 0 };
	double vspre_max_cmp_hys[SITE_NUM] = { 0 };
	double tsd_tm_high[SITE_NUM] = { 0 };
	double tsd_tm_low[SITE_NUM] = { 0 };

	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap,-1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON); 
	AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x56, 0x1A);//		field[(EN_ATEST0,1),(ATEST0_MUX,3)], VS_PRE

	Retest_voltage_unstable_with_time_out(AMUX_FOVI, vs_pre_qvm, spec.get_low_limit("VS_PRE"), spec.get_high_limit("VS_PRE"), 1, 3, MEAS_V);
	//delay_ms(1);
	//AMUX_FOVI.MeasureVI(50, 5);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	vs_pre_qvm[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	//}

	I2CWriteSameData(DEV_ADDR, 0x56, 0xA);//		field[(EN_ATEST0,1),(ATEST0_MUX,1)], LP_BG

	Retest_voltage_unstable_with_time_out(AMUX_FOVI, lp_bg, spec.get_low_limit("LP_BG") , spec.get_high_limit("LP_BG"), 1, 8,MEAS_MV);
	//delay_ms(5);
	//AMUX_FOVI.MeasureVI(215, 10);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	lp_bg[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	//}

	I2CWriteSameData(DEV_ADDR, 0x56, 0x12);//		field[(EN_ATEST0,1),(ATEST0_MUX,2)], LP_BG_BUF
	Retest_voltage_unstable_with_time_out(AMUX_FOVI, lp_bg_buf, spec.get_low_limit("LP_BG_BUF"), spec.get_high_limit("LP_BG_BUF"), 1, 8, MEAS_MV);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	lp_bg_buf[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	//}

	I2CWriteSameData(DEV_ADDR, 0x56, 0x32);
	I2CWriteSameData(DEV_ADDR, 0x67, 0x0A);
	I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(EN_ATEST0,1),(ATEST0_MUX,6),(D2A_OVRD_SEL,10),(OVRD_VALUE,3)], IRPPO_EA_FB

	Retest_voltage_unstable_with_time_out(AMUX_FOVI, irppo_ea_fb, spec.get_low_limit("IRPPO_EA_FB"), spec.get_high_limit("IRPPO_EA_FB"), 1, 8, MEAS_MV);
	//delay_ms(1);
	//AMUX_FOVI.MeasureVI(215,10);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	irppo_ea_fb[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	//}

	//I2CWriteSameData(DEV_ADDR, 0x56, 0x5A);
	//I2CWriteSameData(DEV_ADDR, 0x67, 0x0A);
	//I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(EN_ATEST0,1),(ATEST0_MUX,11),(D2A_OVRD_SEL,10),(OVRD_VALUE,3)], AVSS_BG
	//delay_ms(1);
	//AMUX_FOVI.MeasureVI(215, 10);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	avss_bg[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	//}

	FOR_EACH_VALID_SITE(site)
	{
		vs_pre_qvm[site] = vs_pre_qvm[site] * 1e3;//mV
		//lp_bg[site] = lp_bg[site] * 1e3;//mV
		//lp_bg_buf[site] = lp_bg_buf[site] * 1e3;//mV
		//irppo_ea_fb[site] = irppo_ea_fb[site] * 1e3;//mV
		//avss_bg[site] = avss_bg[site] * 1e3;//mV
	}


	I2CWriteSameData(DEV_ADDR, 0x67, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x68, 0x00);
	AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_us(500);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x22);//		field[(EN_ATEST0,1),(ATEST0_MUX,4)], LP_HR_0P5U
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		lp_hr_0p5uA[site] = -1*AMUX_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
	}

	I2CWriteSameData(DEV_ADDR, 0x56, 0x2A);//		field[(EN_ATEST0,1),(ATEST0_MUX,5)].LP_PTAT_0P5U
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		lp_ptat_0p5uA[site] = -1*AMUX_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
	}


	I2CWriteSameData(DEV_ADDR, 0x56,0x3A);
	I2CWriteSameData(DEV_ADDR, 0x67,0x0A);
	I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(EN_ATEST0,1),(ATEST0_MUX,7),,(D2A_OVRD_SEL,10),(OVRD_VALUE,3)], IHR_P_1UA
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		ihr_p_1uA[site] = -1*AMUX_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
	}

	I2CWriteSameData(DEV_ADDR, 0x56, 0x42);//		field[(EN_ATEST0,1),(ATEST0_MUX,9),(D2A_OVRD_SEL,10),(OVRD_VALUE,3)], IZTC_1UA
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		iptat_1uA[site] = -1*AMUX_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);

	VAC123_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x67, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x68, 0x00);
	VBAT_ACM.Set(FV, 3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x80);//		field[(EN_DTEST0,1),(DTEST0_MUX,0)], VSPRE_MAX_CMP
	delay_ms(1);
	int sam = 200;			//AWG waveform data length
	int interval = 50;		//AWGdata interval time, unit is uS
	double vspre_max_cmp_r[400] = { 0.0 };
	double vspre_max_cmp_f[200] = { 0.0 };
	double Trig = 2.5;

	STSAWGCreateRampData(&vspre_max_cmp_r[0], sam * 2, 1, 4.51, 5.71);//  PMID-->SW
	VAC123_ACM.AwgLoader("vspre_max_cmp_r_pattern", FV, ACM200_10V, ACM200_100MA, vspre_max_cmp_r, sam * 2);
	VAC123_ACM.AwgSelect("vspre_max_cmp_r_pattern", 0, sam * 2 - 1, sam * 2 - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam * 2, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam * 2, interval, MEAS_AWG);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	double Trig_Point[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vspre_max_cmp_rise[site] = VAC123_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		check_awg_trigger_point(Trig_Point, sam*2, vspre_max_cmp_rise, site);// add for AWG trigger check
	}

	VAC123_ACM.Set(FV, 4.7, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSAWGCreateRampData(&vspre_max_cmp_f[0], sam, 1, 4.68, 4);//  PMID-->SW

	//VAC123_ACM.Set(FV, 4.65, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//delay_us(500);
	//STSAWGCreateRampData(&vspre_max_cmp_f[0], sam, 1, 4.61, 4);//  PMID-->SW
	VAC123_ACM.AwgLoader("vspre_max_cmp_f_pattern", FV, ACM200_10V, ACM200_100MA, vspre_max_cmp_f, sam);
	VAC123_ACM.AwgSelect("vspre_max_cmp_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vspre_max_cmp_fall[site] = VAC123_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vspre_max_cmp_hys[site] = (vspre_max_cmp_rise[site] - vspre_max_cmp_fall[site])*1e3;//mV
		check_awg_trigger_point(Trig_Point, sam, vspre_max_cmp_fall, site);// add for AWG trigger check
	}





	I2CWriteSameData(DEV_ADDR, 0x56, 0x5A);
	I2CWriteSameData(DEV_ADDR, 0x67, 0x0A);
	I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(EN_ATEST0,1),(ATEST0_MUX,11),(D2A_OVRD_SEL,10),(OVRD_VALUE,3)]
	I2CWriteSameData(DEV_ADDR, 0x55, 0x00);
	delay_ms(1);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
	delay_ms(1);
	SDA_INT_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		tsd_tm_high[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
	}

	I2CWriteSameData(DEV_ADDR, 0x55, 0x93);//		field[(EN_DTEST0,1),(DTEST0_MUX,19)]
	delay_ms(1);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
	delay_ms(1);
	SDA_INT_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		tsd_tm_low[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
	}
	if (!TTR)
	{
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		delay_ms(1);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		VAC123_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	}

	FOR_EACH_VALID_SITE(site)
	{
		VS_PRE->SetTestResult(site, 0, vs_pre_qvm[site]);
		LP_BG->SetTestResult(site, 0, lp_bg[site]);
		LP_BG_BUF->SetTestResult(site, 0, lp_bg_buf[site]);
		LP_HR_0P5UA->SetTestResult(site, 0, lp_hr_0p5uA[site]);
		LP_PTAT_0P5UA->SetTestResult(site, 0, lp_ptat_0p5uA[site]);
		VSPRE_MAX_CMP_Rise->SetTestResult(site, 0, vspre_max_cmp_rise[site]);
		VSPRE_MAX_CMP_Fall->SetTestResult(site, 0, vspre_max_cmp_fall[site]);
		VSPRE_MAX_CMP_Hys->SetTestResult(site, 0, vspre_max_cmp_hys[site]);
		IRPPO_EA_FB->SetTestResult(site, 0, irppo_ea_fb[site]);
		IHR_P_1UA->SetTestResult(site, 0, ihr_p_1uA[site]);
		IPTAT_1UA->SetTestResult(site, 0, iptat_1uA[site]);
		//AVSS_BG->SetTestResult(site, 0, avss_bg[site]);
		TSD_TM_High->SetTestResult(site, 0, tsd_tm_high[site]);
		TSD_TM_Low->SetTestResult(site, 0, tsd_tm_low[site]);
	}

    return 0;
}
 
DUT_API int VBUS_PRST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_PRST_Rise = StsGetParam(funcindex, "VBUS_PRST_Rise");
    CParam *VBUS_PRST_Fall = StsGetParam(funcindex, "VBUS_PRST_Fall");
    CParam *VBUS_PRST_Hys = StsGetParam(funcindex, "VBUS_PRST_Hys");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vbus_pres_rise[SITE_NUM] = { 0 };
	double vbus_pres_fall[SITE_NUM] = { 0 };
	double vbus_pres_hys[SITE_NUM] = { 0 };
	dcm.I2CConnect();
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K43_INT_ACM, K58_INT_PU, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x55, 0x94);//		field[(EN_DTEST0,1),(DTEST0_MUX,20)]
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double vbus_pres_r[200] = { 0.0 };
	double vbus_pres_f[200] = { 0.0 };
	double Trig = 2.5;

	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vbus_pres_r[0], sam, 1, 3.6, 4.1);//  PMID-->SW
	VBUS_FOVI.AwgLoader("vbus_pres_r_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_pres_r, sam);
	VBUS_FOVI.AwgSelect("vbus_pres_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	VBUS_FOVI.Set(FV, 3.5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	double Trig_Point[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_pres_rise[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		check_awg_trigger_point(Trig_Point, sam, vbus_pres_rise, site);// add for AWG trigger check
	}


	STSAWGCreateRampData(&vbus_pres_f[0], sam, 1, 3.95, 3.45);//  PMID-->SW
	VBUS_FOVI.AwgLoader("vbus_pres_f_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_pres_f, sam);
	VBUS_FOVI.AwgSelect("vbus_pres_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	VBUS_FOVI.Set(FV, 4.1, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_pres_fall[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vbus_pres_hys[site] = (vbus_pres_rise[site] - vbus_pres_fall[site])*1e3;//mV
		check_awg_trigger_point(Trig_Point, sam, vbus_pres_fall,site);// add for AWG trigger check
	}


	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBUS_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	}
	FOR_EACH_VALID_SITE(site)
	{
		VBUS_PRST_Rise->SetTestResult(site, 0, vbus_pres_rise[site]);
		VBUS_PRST_Fall->SetTestResult(site, 0, vbus_pres_fall[site]);
		VBUS_PRST_Hys->SetTestResult(site, 0, vbus_pres_hys[site]);
	}

    return 0;
}
 
DUT_API int VBUS_HT_VBAT(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_HT_VBAT_3V_Rise_DSA = StsGetParam(funcindex, "VBUS_HT_VBAT_3V_Rise_DSA");
    CParam *VBUS_HT_VBAT_3V_Fall = StsGetParam(funcindex, "VBUS_HT_VBAT_3V_Fall");
    CParam *VBUS_HT_VBAT_3V_Hys = StsGetParam(funcindex, "VBUS_HT_VBAT_3V_Hys");
    CParam *VBUS_HT_VBAT_4V_Rise_DSA = StsGetParam(funcindex, "VBUS_HT_VBAT_4V_Rise_DSA");
    CParam *VBUS_HT_VBAT_4V_Fall = StsGetParam(funcindex, "VBUS_HT_VBAT_4V_Fall");
    CParam *VBUS_HT_VBAT_4V_Hys = StsGetParam(funcindex, "VBUS_HT_VBAT_4V_Hys");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vbus_ht_vbat_3V_rise[SITE_NUM] = { 0 };
	double vbus_ht_vbat_3V_fall[SITE_NUM] = { 0 };
	double vbus_ht_vbat_3V_hys[SITE_NUM] = { 0 };
	double vbus_ht_vbat_4V_rise[SITE_NUM] = { 0 };
	double vbus_ht_vbat_4V_fall[SITE_NUM] = { 0 };
	double vbus_ht_vbat_4V_hys[SITE_NUM] = { 0 };
	double VBAT_IN = 3;

	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K43_INT_ACM, K58_INT_PU, -1);
	delay_ms(3);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, VBAT_IN, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x55, 0xBC);//		field[(EN_DTEST0,1),(DTEST0_MUX,60)]

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double vbus_ht_vbat_r[200] = { 0.0 };
	double vbus_ht_vbat_f[200] = { 0.0 };
	double Trig = 2.5;
	VBUS_FOVI.Set(FV, VBAT_IN - 0.05, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vbus_ht_vbat_r[0], sam, 1, VBAT_IN - 0.05, VBAT_IN + 0.165);//  PMID-->SW
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_ht_vbat_r_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_ht_vbat_r, sam);
	VBUS_FOVI.AwgSelect("vbus_ht_vbat_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	double Trig_Point[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_ht_vbat_3V_rise[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]) - VBAT_IN;
		check_awg_trigger_point(Trig_Point, sam, vbus_ht_vbat_3V_rise,site);// add for AWG trigger check
	}

	VBUS_FOVI.Set(FV, VBAT_IN + 0.075, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSAWGCreateRampData(&vbus_ht_vbat_f[0], sam, 1, VBAT_IN + 0.075, VBAT_IN - 0.14);//  PMID-->SW
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_ht_vbat_f_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_ht_vbat_f, sam);
	VBUS_FOVI.AwgSelect("vbus_ht_vbat_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_ht_vbat_3V_fall[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]) - VBAT_IN;
		vbus_ht_vbat_3V_hys[site] = vbus_ht_vbat_3V_rise[site] - vbus_ht_vbat_3V_fall[site];//mV
		check_awg_trigger_point(Trig_Point, sam, vbus_ht_vbat_3V_fall,site);// add for AWG trigger check
	}


	//----------------VBUS High Than VBAT 4V
	VBAT_IN = 4;
	VBAT_ACM.Set(FV, VBAT_IN, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSAWGCreateRampData(&vbus_ht_vbat_r[0], sam, 1, VBAT_IN - 0.035, VBAT_IN + 0.18);//  PMID-->SW
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_ht_vbat_r_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_ht_vbat_r, sam);
	VBUS_FOVI.AwgSelect("vbus_ht_vbat_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	VBUS_FOVI.Set(FV, VBAT_IN - 0.05, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_ht_vbat_4V_rise[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]) - VBAT_IN;
		check_awg_trigger_point(Trig_Point, sam, vbus_ht_vbat_4V_rise,site);// add for AWG trigger check
	}

	STSAWGCreateRampData(&vbus_ht_vbat_f[0], sam, 1, VBAT_IN + 0.075, VBAT_IN - 0.155);//  PMID-->SW
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_ht_vbat_f_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_ht_vbat_f, sam);
	VBUS_FOVI.AwgSelect("vbus_ht_vbat_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	VBUS_FOVI.Set(FV, VBAT_IN + 0.1, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_ht_vbat_4V_fall[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])- VBAT_IN;
		vbus_ht_vbat_4V_hys[site] = vbus_ht_vbat_4V_rise[site] - vbus_ht_vbat_4V_fall[site];//mV
		check_awg_trigger_point(Trig_Point, sam, vbus_ht_vbat_4V_fall,site);// add for AWG trigger check
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		delay_ms(1);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}

	FOR_EACH_VALID_SITE(site)
	{
		VBUS_HT_VBAT_3V_Rise_DSA->SetTestResult(site, 0, vbus_ht_vbat_3V_rise[site]*1e3);
		VBUS_HT_VBAT_3V_Fall->SetTestResult(site, 0, vbus_ht_vbat_3V_fall[site] * 1e3);
		VBUS_HT_VBAT_3V_Hys->SetTestResult(site, 0, vbus_ht_vbat_3V_hys[site] * 1e3);
		VBUS_HT_VBAT_4V_Rise_DSA->SetTestResult(site, 0, vbus_ht_vbat_4V_rise[site] * 1e3);
		VBUS_HT_VBAT_4V_Fall->SetTestResult(site, 0, vbus_ht_vbat_4V_fall[site] * 1e3);
		VBUS_HT_VBAT_4V_Hys->SetTestResult(site, 0, vbus_ht_vbat_4V_hys[site] * 1e3);
	}


    return 0;
}
 
DUT_API int VAC_PRST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_PRST_Rise = StsGetParam(funcindex, "VAC1_PRST_Rise");
    CParam *VAC1_PRST_Fall = StsGetParam(funcindex, "VAC1_PRST_Fall");
    CParam *VAC1_PRST_Hys = StsGetParam(funcindex, "VAC1_PRST_Hys");
    CParam *VAC2_PRST_Rise = StsGetParam(funcindex, "VAC2_PRST_Rise");
    CParam *VAC2_PRST_Fall = StsGetParam(funcindex, "VAC2_PRST_Fall");
    CParam *VAC2_PRST_Hys = StsGetParam(funcindex, "VAC2_PRST_Hys");
    CParam *VAC3_PRST_Rise = StsGetParam(funcindex, "VAC3_PRST_Rise");
    CParam *VAC3_PRST_Fall = StsGetParam(funcindex, "VAC3_PRST_Fall");
    CParam *VAC3_PRST_Hys = StsGetParam(funcindex, "VAC3_PRST_Hys");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vac1_pres_rise[SITE_NUM] = { 0 };
	double vac1_pres_fall[SITE_NUM] = { 0 };
	double vac1_pres_hys[SITE_NUM] = { 0 };
	double vac2_pres_rise[SITE_NUM] = { 0 };
	double vac2_pres_fall[SITE_NUM] = { 0 };
	double vac2_pres_hys[SITE_NUM] = { 0 };
	double vac3_pres_rise[SITE_NUM] = { 0 };
	double vac3_pres_fall[SITE_NUM] = { 0 };
	double vac3_pres_hys[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K43_INT_ACM, K58_INT_PU, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x55, 0x97);	//		field[(EN_DTEST0,1),(DTEST0_MUX,23)]

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double vac_pres_r[200] = { 0.0 };
	double vac_pres_f[200] = { 0.0 };
	double Trig = 2.5;
	double Trig_Point[SITE_NUM] = { 0 };
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vac_pres_r[0], sam, 1, 3.8, 4.45);//  PMID-->SW
	VAC123_ACM.AwgLoader("vac_pres_r_pattern", FV, ACM200_10V, ACM200_100MA, vac_pres_r, sam);
	VAC123_ACM.AwgSelect("vac_pres_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);

	VAC123_ACM.Set(FV, 3.8, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously

	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vac1_pres_rise[site] = VAC123_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		check_awg_trigger_point(Trig_Point, sam, vac1_pres_rise,site);// add for AWG trigger check
	}


	STSAWGCreateRampData(&vac_pres_f[0], sam, 1, 4.05, 3.5);//  PMID-->SW
	VAC123_ACM.AwgLoader("vac_pres_f_pattern", FV, ACM200_10V, ACM200_100MA, vac_pres_f, sam);
	VAC123_ACM.AwgSelect("vac_pres_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);

	VAC123_ACM.Set(FV, 4.1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vac1_pres_fall[site] = VAC123_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vac1_pres_hys[site] = (vac1_pres_rise[site] - vac1_pres_fall[site])*1e3;//mV
		check_awg_trigger_point(Trig_Point, sam, vac1_pres_fall,site);// add for AWG trigger check
	}

	//-----------------------VAC2
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K43_INT_ACM, K58_INT_PU, K36_SHARE2_VAC, -1);
	delay_ms(3);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x96);	//		field[(EN_DTEST0,1),(DTEST0_MUX,22)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vac_pres_r[0], sam, 1, 3.8, 4.45);//  PMID-->SW
	VAC123_ACM.AwgClear();
	VAC123_ACM.AwgLoader("vac_pres_r_pattern", FV, ACM200_10V, ACM200_100MA, vac_pres_r, sam);
	VAC123_ACM.AwgSelect("vac_pres_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);

	VAC123_ACM.Set(FV, 3.8, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vac2_pres_rise[site] = VAC123_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		check_awg_trigger_point(Trig_Point, sam, vac2_pres_rise,site);// add for AWG trigger check
	}


	STSAWGCreateRampData(&vac_pres_f[0], sam, 1, 4.05, 3.55);//  PMID-->SW
	VAC123_ACM.AwgClear();
	VAC123_ACM.AwgLoader("vac_pres_f_pattern", FV, ACM200_10V, ACM200_100MA, vac_pres_f, sam);
	VAC123_ACM.AwgSelect("vac_pres_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);

	VAC123_ACM.Set(FV, 4.1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vac2_pres_fall[site] = VAC123_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vac2_pres_hys[site] = (vac2_pres_rise[site] - vac2_pres_fall[site])*1e3;//mV
		check_awg_trigger_point(Trig_Point, sam, vac2_pres_fall,site);// add for AWG trigger check
	}

	//-----------------------VAC3
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K43_INT_ACM, K58_INT_PU, K35_SHARE1_VAC, -1);
	delay_ms(3);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x95);	//		field[(EN_DTEST0,1),(DTEST0_MUX,21)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vac_pres_r[0], sam, 1, 3.8, 4.45);//  PMID-->SW
	VAC123_ACM.AwgClear();
	VAC123_ACM.AwgLoader("vac_pres_r_pattern", FV, ACM200_10V, ACM200_100MA, vac_pres_r, sam);
	VAC123_ACM.AwgSelect("vac_pres_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);

	VAC123_ACM.Set(FV, 3.8, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vac3_pres_rise[site] = VAC123_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		check_awg_trigger_point(Trig_Point, sam, vac3_pres_rise,site);// add for AWG trigger check
	}


	STSAWGCreateRampData(&vac_pres_f[0], sam, 1, 4.05, 3.55);//  PMID-->SW
	VAC123_ACM.AwgClear();
	VAC123_ACM.AwgLoader("vac_pres_f_pattern", FV, ACM200_10V, ACM200_100MA, vac_pres_f, sam);
	VAC123_ACM.AwgSelect("vac_pres_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);

	VAC123_ACM.Set(FV, 4.1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vac3_pres_fall[site] = VAC123_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vac3_pres_hys[site] = (vac3_pres_rise[site] - vac3_pres_fall[site])*1e3;//mV
		check_awg_trigger_point(Trig_Point, sam, vac3_pres_fall,site);// add for AWG trigger check
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	}

	FOR_EACH_VALID_SITE(site)
	{
		VAC1_PRST_Rise->SetTestResult(site, 0, vac1_pres_rise[site]);
		VAC1_PRST_Fall->SetTestResult(site, 0, vac1_pres_fall[site]);
		VAC1_PRST_Hys->SetTestResult(site, 0, vac1_pres_hys[site]);
		VAC2_PRST_Rise->SetTestResult(site, 0, vac2_pres_rise[site]);
		VAC2_PRST_Fall->SetTestResult(site, 0, vac2_pres_fall[site]);
		VAC2_PRST_Hys->SetTestResult(site, 0, vac2_pres_hys[site]);
		VAC3_PRST_Rise->SetTestResult(site, 0, vac3_pres_rise[site]);
		VAC3_PRST_Fall->SetTestResult(site, 0, vac3_pres_fall[site]);
		VAC3_PRST_Hys->SetTestResult(site, 0, vac3_pres_hys[site]);
	}


    return 0;
}
 
DUT_API int VBAT_UVLO(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_UVLO_Rise_SCM = StsGetParam(funcindex, "VBAT_UVLO_Rise_SCM");
    CParam *VBAT_UVLO_Fall_DSN = StsGetParam(funcindex, "VBAT_UVLO_Fall_DSN");
    CParam *VBAT_UVLO_Hys_SCM = StsGetParam(funcindex, "VBAT_UVLO_Hys_SCM");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vbat_uvlo_rise[SITE_NUM] = { 0 };
	double vbat_uvlo_fall[SITE_NUM] = { 0 };
	double vbat_uvlo_hys[SITE_NUM] = { 0 };

	cbite.SetOn(K1_PGND2AGND, K37_VAC_Cap, K43_INT_ACM, K58_INT_PU, -1);
	delay_ms(3);
	VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_20V, ACM200_100UA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x55, 0x98);	//		field[(EN_DTEST0,1),(DTEST0_MUX,24)]
	delay_ms(1);

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double vbat_uvlo_r[200] = { 0.0 };
	double vbat_uvlo_f[200] = { 0.0 };
	double Trig = 2.5;
	double Trig_Point[SITE_NUM] = { 0 };



	STSAWGCreateRampData(&vbat_uvlo_f[0], sam, 1, 2.3, 1.95);
	VBAT_ACM.AwgLoader("vbat_uvlo_f_pattern", FV, ACM200_10V, ACM200_100MA, vbat_uvlo_f, sam);
	VBAT_ACM.AwgSelect("vbat_uvlo_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);

	VBAT_ACM.Set(FV, 2.3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbat_uvlo_fall[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vbat_uvlo_r[0], sam, 1, 2.05, 2.35);
	VBAT_ACM.AwgLoader("vbat_uvlo_r_pattern", FV, ACM200_10V, ACM200_100MA, vbat_uvlo_r, sam);
	VBAT_ACM.AwgSelect("vbat_uvlo_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);

	VBAT_ACM.Set(FV, 2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously

	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbat_uvlo_rise[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vbat_uvlo_hys[site] = (vbat_uvlo_rise[site] - vbat_uvlo_fall[site])*1e3;//mV
	}





	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}



	FOR_EACH_VALID_SITE(site)
	{
		VBAT_UVLO_Rise_SCM->SetTestResult(site, 0, vbat_uvlo_rise[site]);
		VBAT_UVLO_Fall_DSN->SetTestResult(site, 0, vbat_uvlo_fall[site]);
		VBAT_UVLO_Hys_SCM->SetTestResult(site, 0, vbat_uvlo_hys[site]);
	}

    return 0;
}
 
DUT_API int VBAT_HT_3P1V(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_HT_3P1V_Rise = StsGetParam(funcindex, "VBAT_HT_3P1V_Rise");
    CParam *VBAT_HT_3P1V_Fall = StsGetParam(funcindex, "VBAT_HT_3P1V_Fall");
    CParam *VBAT_HT_3P1V_Hys = StsGetParam(funcindex, "VBAT_HT_3P1V_Hys");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vbat_ht3p1_rise[SITE_NUM] = { 0 };
	double vbat_ht3p1_fall[SITE_NUM] = { 0 };
	double vbat_ht3p1_hys[SITE_NUM] = { 0 };

	if (!TTR)
	{
		dcm.I2CConnect();
		cbite.SetOn(K1_PGND2AGND, K37_VAC_Cap, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(3);
		VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 3.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FI, 0, ACM200_20V, ACM200_100UA, ACM200_RELAY_ON);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x55, 0xBB);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x20);
		//		field[(EN_DTEST0,1),(DTEST0_MUX,59),(D2A_REGN_TM_EN,1)]
		delay_ms(1);

		int sam = 200;			//AWG waveform data length
		int interval = 20;		//AWGdata interval time, unit is uS
		double vbat_ht3p1_r[200] = { 0.0 };
		double vbat_ht3p1_f[200] = { 0.0 };
		double Trig = 2.5;
		double Trig_Point[SITE_NUM] = { 0 };
		STSAWGCreateRampData(&vbat_ht3p1_f[0], sam, 1, 3.15, 2.85);
		VBAT_ACM.AwgLoader("vbat_ht3p1_f_pattern", FV, ACM200_10V, ACM200_100MA, vbat_ht3p1_f, sam);
		VBAT_ACM.AwgSelect("vbat_ht3p1_f_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);

		VBAT_ACM.Set(FV, 3.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
		STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
		STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
		STSAWGRun();//Enable AWG and measurement synchronously
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
			vbat_ht3p1_fall[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		}

		// Set a sinewave data array, the start address starts from 0, data size is 100.
		STSAWGCreateRampData(&vbat_ht3p1_r[0], sam, 1, 2.95, 3.25);//  PMID-->SW
		VBAT_ACM.AwgLoader("vbat_ht3p1_r_pattern", FV, ACM200_10V, ACM200_100MA, vbat_ht3p1_r, sam);
		VBAT_ACM.AwgSelect("vbat_ht3p1_r_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);

		VBAT_ACM.Set(FV, 2.9, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
		STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
		STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
		STSAWGRun();//Enable AWG and measurement synchronously

		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
			vbat_ht3p1_rise[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
			vbat_ht3p1_hys[site] = (vbat_ht3p1_rise[site] - vbat_ht3p1_fall[site])*1e3;//mV
		}

		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 2.95, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FI, 0, ACM200_20V, ACM200_100UA, ACM200_RELAY_ON);
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x55, 0xBB);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x20); //		field[(EN_DTEST0,1),(DTEST0_MUX,59),(D2A_REGN_TM_EN,1)]
		delay_ms(1);
		int sam = 200;			//AWG waveform data length
		int interval = 20;		//AWGdata interval time, unit is uS
		double vbat_ht3p1_r[200] = { 0.0 };
		double vbat_ht3p1_f[200] = { 0.0 };
		double Trig = 2.5;
		double Trig_Point[SITE_NUM] = { 0 };
		int samm = 200;

		// Set a sinewave data array, the start address starts from 0, data size is 100.
		STSAWGCreateRampData(&vbat_ht3p1_r[0], samm, 1, 2.91, 3.25);//  PMID-->SW
		VBAT_ACM.AwgLoader("vbat_ht3p1_r_pattern", FV, ACM200_10V, ACM200_100MA, vbat_ht3p1_r, samm);
		VBAT_ACM.AwgSelect("vbat_ht3p1_r_pattern", 0, samm - 1, samm - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(samm, interval, MEAS_AWG);
		VBAT_ACM.MeasureVI(samm, interval, MEAS_AWG);
		VBAT_ACM.Set(FV, 2.9, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
		STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
		STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
		STSAWGRun();//Enable AWG and measurement synchronously
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
			vbat_ht3p1_rise[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		}

		STSAWGCreateRampData(&vbat_ht3p1_f[0], sam, 1, 3.15, 2.85);
		VBAT_ACM.AwgLoader("vbat_ht3p1_f_pattern", FV, ACM200_10V, ACM200_100MA, vbat_ht3p1_f, sam);
		VBAT_ACM.AwgSelect("vbat_ht3p1_f_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		VBAT_ACM.Set(FV, 3.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
		STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
		STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
		STSAWGRun();//Enable AWG and measurement synchronously
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
			vbat_ht3p1_fall[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
			vbat_ht3p1_hys[site] = (vbat_ht3p1_rise[site] - vbat_ht3p1_fall[site])*1e3;//mV
		}


		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	
		delay_ms(1);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		//SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		VBAT_HT_3P1V_Rise->SetTestResult(site, 0, vbat_ht3p1_rise[site]);
		VBAT_HT_3P1V_Fall->SetTestResult(site, 0, vbat_ht3p1_fall[site]);
		VBAT_HT_3P1V_Hys->SetTestResult(site, 0, vbat_ht3p1_hys[site]);
	}

    return 0;
}
 
DUT_API int VCC_UVLO(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_UVLO_Rise_SCM = StsGetParam(funcindex, "VCC_UVLO_Rise_SCM");
    CParam *VCC_UVLO_Fall_DST = StsGetParam(funcindex, "VCC_UVLO_Fall_DST");
    CParam *VCC_UVLO_Hys_SCM = StsGetParam(funcindex, "VCC_UVLO_Hys_SCM");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here


	double vcc_uvlo_rise[SITE_NUM] = { 0 };
	double vcc_uvlo_fall[SITE_NUM] = { 0 };
	double vcc_uvlo_hys[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(3);

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double vcc_uvlo_r[200] = { 0.0 };
	double vcc_uvlo_f[200] = { 0.0 };
	double Trig = 0.04;
	double Trig_Point[SITE_NUM] = { 0 };
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vcc_uvlo_r[0], sam, 1, 1.9, 2.25);//  VBAT current from 20mA to 50mA
	VCC_ACM.AwgLoader("vcc_uvlo_r_pattern", FV, ACM200_10V, ACM200_100MA, vcc_uvlo_r, sam);
	VCC_ACM.AwgSelect("vcc_uvlo_r_pattern", 0, sam - 1, sam - 1, interval);
	VBAT_ACM.SetMeasITrig(Trig, TRIG_RISING); // trigger value is 40mA, rising edge
	VCC_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VCC_ACM.Set(FV, 1.8, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VCC_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VCC_ACM, &VBAT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously

	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = VBAT_ACM.GetMeasResult(site, MIRET, TRIG_RESULT)-2;
		vcc_uvlo_rise[site] = VCC_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}


	STSAWGCreateRampData(&vcc_uvlo_f[0], sam, 1, 2.15, 1.85);// VBAT current from 50mA to 20mA
	VCC_ACM.AwgLoader("vcc_uvlo_f_pattern", FV, ACM200_10V, ACM200_100MA, vcc_uvlo_f, sam);
	VCC_ACM.AwgSelect("vcc_uvlo_f_pattern", 0, sam - 1, sam - 1, interval);
	VBAT_ACM.SetMeasITrig(Trig, TRIG_FALLING); // trigger value is 40mA, falling edge
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VCC_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VCC_ACM.Set(FV, 2.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VCC_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VCC_ACM, &VBAT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = VBAT_ACM.GetMeasResult(site, MIRET, TRIG_RESULT)-2;
		vcc_uvlo_fall[site] = VCC_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vcc_uvlo_hys[site] = (vcc_uvlo_rise[site] - vcc_uvlo_fall[site])*1e3;//mV
	}

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	VCC_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);

	FOR_EACH_VALID_SITE(site)
	{
		VCC_UVLO_Rise_SCM->SetTestResult(site, 0, vcc_uvlo_rise[site]);
		VCC_UVLO_Fall_DST->SetTestResult(site, 0, vcc_uvlo_fall[site]);
		VCC_UVLO_Hys_SCM->SetTestResult(site, 0, vcc_uvlo_hys[site]);
	}


    return 0;
}
 
DUT_API int VCC_Function(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCC_Acc1_30mA = StsGetParam(funcindex, "VCC_Acc1_30mA");
    CParam *VCC_Acc1_0mA = StsGetParam(funcindex, "VCC_Acc1_0mA");
    CParam *VCC_Acc3_10mA = StsGetParam(funcindex, "VCC_Acc3_10mA");
    CParam *VCC_Cap1_30mA = StsGetParam(funcindex, "VCC_Cap1_30mA");
    CParam *VCC_Cap1_0mA = StsGetParam(funcindex, "VCC_Cap1_0mA");
    CParam *VCC_Cap2_20mA = StsGetParam(funcindex, "VCC_Cap2_20mA");
    CParam *VCC_Cap2_0mA = StsGetParam(funcindex, "VCC_Cap2_0mA");
    CParam *VCC_Short1 = StsGetParam(funcindex, "VCC_Short1");
    CParam *VCC_Short2 = StsGetParam(funcindex, "VCC_Short2");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vcc_acc1_0mA[SITE_NUM] = { 0 };
	double vcc_acc1_30mA[SITE_NUM] = { 0 };
	double vcc_cap1_0mA[SITE_NUM] = { 0 };
	double vcc_cap1_30mA[SITE_NUM] = { 0 };
	double vcc_acc3_10mA[SITE_NUM] = { 0 };
	double vcc_cap2_20mA[SITE_NUM] = { 0 };
	double vcc_cap2_0mA[SITE_NUM] = { 0 };
	double vcc_short1[SITE_NUM] = { 0 };
	double vcc_short2[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K16_VBUS_Cap, K30_VBAT_Cap, K37_VAC_Cap, K25_VCC_Cap, -1);
	delay_ms(3);
	//-------------------VCC_Cap1
	VBAT_ACM.Set(FV, 3.7, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VAC123_ACM.Set(FV, 5.2, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(2);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x6D, 0x40);

	VCC_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);// -30mA
	VCC_ACM.Set(FI, -0.03, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON, 0.5);// -30mA
	delay_ms(1);
	VCC_ACM.MeasureVI(100, 5);
	VCC_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);// -30mA
	FOR_EACH_VALID_SITE(site)
	{
		vcc_cap1_30mA[site] = VCC_ACM.GetMeasResult(site, MVRET);
	}
	delay_ms(2);
	VCC_ACM.MeasureVI(100, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vcc_cap1_0mA[site] = VCC_ACM.GetMeasResult(site, MVRET);
	}
	//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//-------------------VCC_ACC1
	VBAT_ACM.Set(FV, 3.7, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 5.2, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VAC123_ACM.Set(FV, 5.2, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	//entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x63, 0x01);//		field[(WAKE_UP,1),(REGN_VOL_SET,1)]
	I2CWriteSameData(DEV_ADDR, 0x6D, 0x40);
	delay_ms(2);
	VCC_ACM.Set(FI,0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);// -30mA
	VCC_ACM.Set(FI, -0.03, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);// -30mA
	delay_ms(2);
	VCC_ACM.MeasureVI(50, 5);
	VCC_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);// 0mA
	FOR_EACH_VALID_SITE(site)
	{
		vcc_acc1_30mA[site] = VCC_ACM.GetMeasResult(site, MVRET);
	}
	delay_ms(3);
	VCC_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vcc_acc1_0mA[site] = VCC_ACM.GetMeasResult(site, MVRET);
	}

	//-------------------VCC_ACC3
	VCC_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);// 0mA
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	VAC123_ACM.Set(FV, 4.5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x6D, 0x40);
	VCC_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON, 0.5);// -10mA
	VCC_ACM.Set(FI, -0.01, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON, 0.5);// -10mA
	delay_ms(2);
	VCC_ACM.MeasureVI(100, 5);
	VCC_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);// 0mA
	FOR_EACH_VALID_SITE(site)
	{
		vcc_acc3_10mA[site] = VCC_ACM.GetMeasResult(site, MVRET);
	}
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

	//-------------------VCC_Cap2	
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	VBAT_ACM.Set(FV, 2.8, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 2.8, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(2);
	VCC_ACM.Set(FI,0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FI, -0.02, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);// -20mA
	delay_ms(2);
	VCC_ACM.MeasureVI(50, 5);
	VCC_ACM.Set(FI, -0.001, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);// 0mA
	FOR_EACH_VALID_SITE(site)
	{
		vcc_cap2_20mA[site] = (2.8 - VCC_ACM.GetMeasResult(site, MVRET))*1e3;//mV
	}
	delay_ms(2);
	VCC_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vcc_cap2_0mA[site] = (2.8 - VCC_ACM.GetMeasResult(site, MVRET))*1e3;//mV
	}
	VCC_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);// 0mA
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);


	//----------------VCC SHORT1
	VBAT_ACM.Set(FV, 4.1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);// -10mA
	delay_ms(1);
	VCC_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vcc_short1[site] = -1 * VCC_ACM.GetMeasResult(site, MIRET)*1e3;//mA
	}
	//----------------VCC SHORT2
	VBAT_ACM.Set(FV, 3.1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 4.1, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(1);
	VCC_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vcc_short2[site] = -1 * VCC_ACM.GetMeasResult(site, MIRET)*1e3;//mA
	}


	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}

	FOR_EACH_VALID_SITE(site)
	{
		VCC_Acc1_30mA->SetTestResult(site, 0, vcc_acc1_30mA[site]);
		VCC_Acc1_0mA->SetTestResult(site, 0, vcc_acc1_0mA[site]);
		VCC_Acc3_10mA->SetTestResult(site, 0, vcc_acc3_10mA[site]);
		VCC_Cap1_30mA->SetTestResult(site, 0, vcc_cap1_30mA[site]);
		VCC_Cap1_0mA->SetTestResult(site, 0, vcc_cap1_0mA[site]);
		VCC_Cap2_20mA->SetTestResult(site, 0, vcc_cap2_20mA[site]);
		VCC_Cap2_0mA->SetTestResult(site, 0, vcc_cap2_0mA[site]);
		VCC_Short1->SetTestResult(site, 0, vcc_short1[site]);
		VCC_Short2->SetTestResult(site, 0, vcc_short2[site]);
	}

    return 0;
}

DUT_API int TM_SCL_SDA(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *SCL_IN_VTH_Rise = StsGetParam(funcindex, "SCL_IN_VTH_Rise");
    CParam *SCL_IN_VTH_Fall = StsGetParam(funcindex, "SCL_IN_VTH_Fall");
    CParam *SCL_IN_VTH_Hys = StsGetParam(funcindex, "SCL_IN_VTH_Hys");
    CParam *SDA_IN_VTH_Rise = StsGetParam(funcindex, "SDA_IN_VTH_Rise");
    CParam *SDA_IN_VTH_Fall = StsGetParam(funcindex, "SDA_IN_VTH_Fall");
    CParam *SDA_IN_VTH_Hys = StsGetParam(funcindex, "SDA_IN_VTH_Hys");
    CParam *R_INT = StsGetParam(funcindex, "R_INT");
    CParam *R_SDA = StsGetParam(funcindex, "R_SDA");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double scl_uvlo_rise[SITE_NUM] = { 0 };
	double scl_uvlo_fall[SITE_NUM] = { 0 };
	double scl_uvlo_hys[SITE_NUM] = { 0 };
	double sda_uvlo_rise[SITE_NUM] = { 0 };
	double sda_uvlo_fall[SITE_NUM] = { 0 };
	double sda_uvlo_hys[SITE_NUM] = { 0 };
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double scl_sda_uvlo_r[200] = { 0.0 };
	double scl_sda_uvlo_f[200] = { 0.0 };
	double Trig = 2.5;
	double Trig_Point[SITE_NUM] = { 0 };
	double Vmeas_int[SITE_NUM] = { 0 };
	double Imeas_int[SITE_NUM] = { 0 };
	double Rcal_int[SITE_NUM] = { 0 };

	cbite.SetOn(K30_VBAT_Cap, K58_INT_PU, K55_SCL_ACM, K43_INT_ACM, -1);// connect SCL
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x55, 0x85);//		field[(EN_DTEST0,1),(DTEST0_MUX,5)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&scl_sda_uvlo_r[0], sam, 1, 0.75, 1.45);//  PMID-->SW
	SDA_INT_ACM.AwgClear();
	SCL_ACM.AwgLoader("scl_sda_uvlo_r_pattern", FV, ACM200_10V, ACM200_100MA, scl_sda_uvlo_r, sam);
	SCL_ACM.AwgSelect("scl_sda_uvlo_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	SCL_ACM.MeasureVI(sam, interval, MEAS_AWG);
	SCL_ACM.Set(FV, 0.75, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&SCL_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&SCL_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		scl_uvlo_rise[site] = SCL_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}
	STSAWGCreateRampData(&scl_sda_uvlo_f[0], sam, 1, 1.25, 0.55);//  PMID-->SW
	SDA_INT_ACM.AwgClear();
	SCL_ACM.AwgLoader("scl_sda_uvlo_f_pattern", FV, ACM200_10V, ACM200_100MA, scl_sda_uvlo_f, sam);
	SCL_ACM.AwgSelect("scl_sda_uvlo_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	SCL_ACM.MeasureVI(sam, interval, MEAS_AWG);
	SCL_ACM.Set(FV, 1.25, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&SCL_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&SCL_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		scl_uvlo_fall[site] = SCL_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		scl_uvlo_hys[site] = (scl_uvlo_rise[site] - scl_uvlo_fall[site])*1e3;//mV
	}
	//--------------用 INT_ACM 上拉到5V，然后测试INT翻低的时候，流过的电流值
	SCL_ACM.Set(FV, 1.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);// INT 翻低的时候
	SDA_INT_ACM.Set(FV, 0.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	SDA_INT_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas_int[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
		Imeas_int[site] = SDA_INT_ACM.GetMeasResult(site, MIRET);
		Rcal_int[site] = Vmeas_int[site] / Imeas_int[site];
	}
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);


	SCL_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	cbite.SetOn(K30_VBAT_Cap, K44_SDA_ACM, K46_INT_ACM, K58_INT_PU, -1);// connect SDA and INT
	delay_ms(3);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x86);//		field[(EN_DTEST0,1),(DTEST0_MUX,6)]
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&scl_sda_uvlo_r[0], sam, 1, 0.75, 1.45);//  PMID-->SW
	SDA_INT_ACM.AwgClear();
	SDA_INT_ACM.AwgLoader("scl_sda_uvlo_r_pattern", FV, ACM200_10V, ACM200_100MA, scl_sda_uvlo_r, sam);
	SDA_INT_ACM.AwgSelect("scl_sda_uvlo_r_pattern", 0, sam - 1, sam - 1, interval);
	SCL_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SCL_ACM.MeasureVI(sam, interval, MEAS_AWG);
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	SDA_INT_ACM.Set(FV, 0.75, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&SDA_INT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&SDA_INT_ACM, &SCL_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SCL_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		sda_uvlo_rise[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}
	STSAWGCreateRampData(&scl_sda_uvlo_f[0], sam, 1, 1.25, 0.55);//  PMID-->SW
	SDA_INT_ACM.AwgClear();
	SDA_INT_ACM.AwgLoader("scl_sda_uvlo_f_pattern",FV, ACM200_10V, ACM200_100MA, scl_sda_uvlo_f, sam);
	SDA_INT_ACM.AwgSelect("scl_sda_uvlo_f_pattern", 0, sam - 1, sam - 1, interval);
	SCL_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SCL_ACM.MeasureVI(sam, interval, MEAS_AWG);
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	SDA_INT_ACM.Set(FV, 1.25, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&SDA_INT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&SDA_INT_ACM, &SCL_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SCL_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		sda_uvlo_fall[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		sda_uvlo_hys[site] = (sda_uvlo_rise[site] - sda_uvlo_fall[site])*1e3;//mV
	}
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

	double Vmeas_sda[SITE_NUM] = { 0 };
	double Imeas_sda[SITE_NUM] = { 0 };
	double Rcal_sda[SITE_NUM] = { 0 };
	cbite.SetOn(K30_VBAT_Cap, K44_SDA_ACM, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(5);//add for special lot 
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x67, 0x0E);
	I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(D2A_OVRD_SEL,14),(OVRD_VALUE,3)]
	dcm.Disconnect("SDA");
	dcm.Disconnect("SCL");
	delay_us(1000);
	SDA_INT_ACM.Set(FV, 0.1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	SDA_INT_ACM.MeasureVI(50, 5);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	dcm.I2CConnect();
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas_sda[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
		Imeas_sda[site] = SDA_INT_ACM.GetMeasResult(site, MIRET);
		Rcal_sda[site] = Vmeas_sda[site] / Imeas_sda[site];
	}
	if (!TTR)
	{
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
	}


	FOR_EACH_VALID_SITE(site)
	{
		SCL_IN_VTH_Rise ->SetTestResult(site, 0, scl_uvlo_rise[site]);
		SCL_IN_VTH_Fall ->SetTestResult(site, 0, scl_uvlo_fall[site]);
		SCL_IN_VTH_Hys ->SetTestResult(site, 0, scl_uvlo_hys[site]);
		SDA_IN_VTH_Rise ->SetTestResult(site, 0, scl_uvlo_rise[site]);
		SDA_IN_VTH_Fall ->SetTestResult(site, 0, scl_uvlo_fall[site]);
		SDA_IN_VTH_Hys ->SetTestResult(site, 0, scl_uvlo_hys[site]);
		R_INT->SetTestResult(site, 0, Rcal_int[site]);
		R_SDA->SetTestResult(site, 0, Rcal_sda[site]);
	}
    return 0;
}
 
DUT_API int IPD_Current(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IPD_VBUS = StsGetParam(funcindex, "IPD_VBUS");
    CParam *IPD_VAC1 = StsGetParam(funcindex, "IPD_VAC1");
    CParam *IPD_VAC2 = StsGetParam(funcindex, "IPD_VAC2");
    CParam *IPD_VAC3 = StsGetParam(funcindex, "IPD_VAC3");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vac1_pd_1v[SITE_NUM] = { 0 };
	double vac1_pd_4v[SITE_NUM] = { 0 };
	double vac2_pd_1v[SITE_NUM] = { 0 };
	double vac2_pd_4v[SITE_NUM] = { 0 };
	double vac3_pd_1v[SITE_NUM] = { 0 };
	double vac3_pd_4v[SITE_NUM] = { 0 };
	double vbus_pd[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x08, 0x40);//		field[(VAC1_PULLDOWN,1)]
	VAC123_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	VAC123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vac1_pd_1v[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e3;//mA
	}
	VAC123_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	VAC123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vac1_pd_4v[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e3;//mA
	}
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K36_SHARE2_VAC,-1);
	delay_ms(3);
	//-----------IVAC2_PD Current
	I2CWriteSameData(DEV_ADDR, 0x08, 0x20);//		field[(VAC2_PULLDOWN,1)]
	VAC123_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	VAC123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vac2_pd_1v[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e3;//mA
	}
	VAC123_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	VAC123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vac2_pd_4v[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e3;//mA
	}
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

	//-----------IVAC3_PD Current
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K35_SHARE1_VAC, -1);
	delay_ms(3);
	I2CWriteSameData(DEV_ADDR, 0x08, 0x10);//		field[(VAC3_PULLDOWN,1)]
	VAC123_ACM.Set(FV, 1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	VAC123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vac3_pd_1v[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e3;//mA
	}
	VAC123_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	VAC123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vac3_pd_4v[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e3;//mA
	}
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);

	//-----------IBUS_PD Current
	VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x08, 0x08);//		field[(VBUS_PULLDOWN,1)]
	delay_ms(1);
	VBUS_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vbus_pd[site] = VBUS_FOVI.GetMeasResult(site, MIRET)*1e3;//mA
	}



	if (!TTR)
	{
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		VBUS_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	}
	FOR_EACH_VALID_SITE(site)
	{
		IPD_VBUS ->SetTestResult(site, 0, vbus_pd[site]);
		IPD_VAC1->SetTestResult(site, 0, vac1_pd_4v[site]);
		IPD_VAC2->SetTestResult(site, 0, vac2_pd_4v[site]);
		IPD_VAC3->SetTestResult(site, 0, vac3_pd_4v[site]);
	}

    return 0;
}
 
DUT_API int VAC_Detection(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_VBIAS_VOL = StsGetParam(funcindex, "VAC1_VBIAS_VOL");
    CParam *VAC1_SNK_DET_ABS_Rise = StsGetParam(funcindex, "VAC1_SNK_DET_ABS_Rise");
    CParam *VAC1_SNK_DET_ABS_Fall = StsGetParam(funcindex, "VAC1_SNK_DET_ABS_Fall");
    CParam *VAC1_SNK_DET_ABS_Hys = StsGetParam(funcindex, "VAC1_SNK_DET_ABS_Hys");
    CParam *VAC1_SNK_DET_SR_12mV_uS = StsGetParam(funcindex, "VAC1_SNK_DET_SR_12mV_uS");
    CParam *VAC1_SNK_DET_SR_5mV_uS = StsGetParam(funcindex, "VAC1_SNK_DET_SR_5mV_uS");
    CParam *VAC2_VBIAS_VOL = StsGetParam(funcindex, "VAC2_VBIAS_VOL");
    CParam *VAC2_SNK_DET_ABS_Rise = StsGetParam(funcindex, "VAC2_SNK_DET_ABS_Rise");
    CParam *VAC2_SNK_DET_ABS_Fall = StsGetParam(funcindex, "VAC2_SNK_DET_ABS_Fall");
    CParam *VAC2_SNK_DET_ABS_Hys = StsGetParam(funcindex, "VAC2_SNK_DET_ABS_Hys");
    CParam *VAC2_SNK_DET_SR_12mV_uS = StsGetParam(funcindex, "VAC2_SNK_DET_SR_12mV_uS");
    CParam *VAC2_SNK_DET_SR_5mV_uS = StsGetParam(funcindex, "VAC2_SNK_DET_SR_5mV_uS");
    CParam *IVAC_PULLUP = StsGetParam(funcindex, "IVAC_PULLUP");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double vac_sink_det_vth_r[200] = { 0.0 };
	double vac_sink_det_vth_f[200] = { 0.0 };
	double Trig = 2.5;
	double Trig_Point[SITE_NUM] = { 0 };

	double vac1_bias_vol[SITE_NUM] = { 0 };
	double vac1_abs_rise[SITE_NUM] = { 0 };
	double vac1_abs_fall[SITE_NUM] = { 0 };
	double vac1_abs_hys[SITE_NUM] = { 0 };
	double vac1_rel_rise[SITE_NUM] = { 0 };
	double vac1_rel_fall[SITE_NUM] = { 0 };
	double vac1_rel_hys[SITE_NUM] = { 0 };

	double vac2_bias_vol[SITE_NUM] = { 0 };
	double vac2_abs_rise[SITE_NUM] = { 0 };
	double vac2_abs_fall[SITE_NUM] = { 0 };
	double vac2_abs_hys[SITE_NUM] = { 0 };
	double vac2_rel_rise[SITE_NUM] = { 0 };
	double vac2_rel_fall[SITE_NUM] = { 0 };
	double vac2_rel_hys[SITE_NUM] = { 0 };
	double vac_Ipullup[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	//-------VAC1
	I2CWriteSameData(DEV_ADDR, 0x07, 0x06); //		
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	delay_ms(1);
	VAC123_ACM.MeasureVI(50, 5);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	delay_ms(3);
	FOR_EACH_VALID_SITE(site)
	{
		vac_Ipullup[site] = -1 * VAC123_ACM.GetMeasResult(site, MIRET)*1e6;
	}
	//cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap,-1);
	//delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 3, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	entertestmode();
	//-------VAC1
	I2CWriteSameData(DEV_ADDR, 0x07,0x03); //		field[(VAC1_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,1)]	
	VAC123_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	delay_ms(3);
	VAC123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vac1_bias_vol[site] = VAC123_ACM.GetMeasResult(site, MVRET);
	}


	I2CWriteSameData(DEV_ADDR, 0x07, 0x02);//		field[(VAC1_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,0)]
	I2CWriteSameData(DEV_ADDR, 0x55, 0x82);//		field[(EN_DTEST0,1),(DTEST0_MUX,2)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vac_sink_det_vth_r[0], sam, 1, 2.05, 2.55);//  PMID-->SW
	VAC123_ACM.AwgClear();
	VAC123_ACM.AwgLoader("vac_sink_det_vth_r_pattern", FV, ACM200_10V, ACM200_100MA, vac_sink_det_vth_r, sam);
	VAC123_ACM.AwgSelect("vac_sink_det_vth_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.Set(FV, 2.0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vac1_abs_rise[site] = VAC123_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}
	STSAWGCreateRampData(&vac_sink_det_vth_f[0], sam, 1, 2.35, 1.85);//  PMID-->SW
	VAC123_ACM.AwgClear();
	VAC123_ACM.AwgLoader("vac_sink_det_vth_f_pattern", FV, ACM200_10V, ACM200_100MA, vac_sink_det_vth_f, sam);
	VAC123_ACM.AwgSelect("vac_sink_det_vth_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.Set(FV, 2.4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vac1_abs_fall[site] = VAC123_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vac1_abs_hys[site] = (vac1_abs_rise[site] - vac1_abs_fall[site])*1e3;//mV
	}


	double slewrate_12mv_us_vac1[SITE_NUM];
	double slewrate_5mv_us_vac1[SITE_NUM];
	I2CWriteSameData(DEV_ADDR, 0x07, 0x03);//		field[(VAC1_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,1)]
	I2CWriteSameData(DEV_ADDR, 0x55, 0x82);//		field[(EN_DTEST0,1),(DTEST0_MUX,2)]
	delay_ms(1);
	sam =10;
	STSAWGCreateRampData(&vac_sink_det_vth_f[0], sam, 1, 3, 0.6);//  PMID-->SW
	VAC123_ACM.AwgClear();
	VAC123_ACM.AwgLoader("vac_sink_det_vth_f_pattern", FV, ACM200_10V, ACM200_100MA, vac_sink_det_vth_f, sam);
	VAC123_ACM.AwgSelect("vac_sink_det_vth_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.Set(FV, 3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		slewrate_12mv_us_vac1[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
	}
	sam = 25;
	STSAWGCreateRampData(&vac_sink_det_vth_f[0], sam, 1, 3, 0.5);//  PMID-->SW
	VAC123_ACM.AwgClear();
	VAC123_ACM.AwgLoader("vac_sink_det_vth_f_pattern", FV, ACM200_10V, ACM200_100MA, vac_sink_det_vth_f, sam);
	VAC123_ACM.AwgSelect("vac_sink_det_vth_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.Set(FV, 3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		slewrate_5mv_us_vac1[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
	}
	sam = 200;


	//----------VAC2
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K43_INT_ACM, K58_INT_PU, K36_SHARE2_VAC, K25_VCC_Cap,-1);
	delay_ms(3);
	VAC123_ACM.Set(FV, 3, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x07, 0x05);//		field[(VAC2_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,1)]
	VAC123_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
	delay_ms(3); 
	VAC123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		vac2_bias_vol[site] = VAC123_ACM.GetMeasResult(site, MVRET);
	}
	I2CWriteSameData(DEV_ADDR, 0x07, 0x04);//		field[(VAC2_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,0)]
	I2CWriteSameData(DEV_ADDR, 0x55, 0xBF);//		field[(EN_DTEST0,1),(DTEST0_MUX,63)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vac_sink_det_vth_r[0], sam, 1, 2.05, 2.55);//  PMID-->SW
	VAC123_ACM.AwgClear();
	VAC123_ACM.AwgLoader("vac_sink_det_vth_r_pattern", FV, ACM200_10V, ACM200_100MA, vac_sink_det_vth_r, sam);
	VAC123_ACM.AwgSelect("vac_sink_det_vth_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.Set(FV, 2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vac2_abs_rise[site] = VAC123_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}
	STSAWGCreateRampData(&vac_sink_det_vth_f[0], sam, 1, 2.35, 1.85);//  PMID-->SW
	VAC123_ACM.AwgClear();
	VAC123_ACM.AwgLoader("vac_sink_det_vth_f_pattern", FV, ACM200_10V, ACM200_100MA, vac_sink_det_vth_f, sam);
	VAC123_ACM.AwgSelect("vac_sink_det_vth_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.Set(FV, 2.4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vac2_abs_fall[site] = VAC123_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vac2_abs_hys[site] = (vac2_abs_rise[site] - vac2_abs_fall[site])*1e3;//mV
	}

	
	double slewrate_12mv_us_vac2[SITE_NUM];
	double slewrate_5mv_us_vac2[SITE_NUM];
	I2CWriteSameData(DEV_ADDR, 0x07, 0x05);//		field[(VAC2_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,1)]
	I2CWriteSameData(DEV_ADDR, 0x55, 0xBF);//		field[(EN_DTEST0,1),(DTEST0_MUX,63)]
	delay_ms(1);
	sam = 10;
	STSAWGCreateRampData(&vac_sink_det_vth_f[0], sam, 1, 3, 0.6);//  PMID-->SW
	VAC123_ACM.AwgClear();
	VAC123_ACM.AwgLoader("vac_sink_det_vth_f_pattern", FV, ACM200_10V, ACM200_100MA, vac_sink_det_vth_f, sam);
	VAC123_ACM.AwgSelect("vac_sink_det_vth_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.Set(FV, 3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		slewrate_12mv_us_vac2[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
	}
	sam = 25;
	STSAWGCreateRampData(&vac_sink_det_vth_f[0], sam, 1, 3, 0.5);//  PMID-->SW
	VAC123_ACM.AwgClear();
	VAC123_ACM.AwgLoader("vac_sink_det_vth_f_pattern", FV, ACM200_10V, ACM200_100MA, vac_sink_det_vth_f, sam);
	VAC123_ACM.AwgSelect("vac_sink_det_vth_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VAC123_ACM.Set(FV, 3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VAC123_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VAC123_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		slewrate_5mv_us_vac2[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
	}
	sam = 200;
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		delay_ms(1);
		VAC123_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		VAC1_VBIAS_VOL->SetTestResult(site, 0, vac1_bias_vol[site]);
		VAC1_SNK_DET_ABS_Rise->SetTestResult(site, 0, vac1_abs_rise[site]);
		VAC1_SNK_DET_ABS_Fall->SetTestResult(site, 0, vac1_abs_fall[site]);
		VAC1_SNK_DET_ABS_Hys->SetTestResult(site, 0, vac1_abs_hys[site]);
		VAC1_SNK_DET_SR_12mV_uS->SetTestResult(site, 0, slewrate_12mv_us_vac1[site]);
		VAC1_SNK_DET_SR_5mV_uS->SetTestResult(site, 0, slewrate_5mv_us_vac1[site]);
		VAC2_VBIAS_VOL->SetTestResult(site, 0, vac2_bias_vol[site]);
		VAC2_SNK_DET_ABS_Rise->SetTestResult(site, 0, vac2_abs_rise[site]);
		VAC2_SNK_DET_ABS_Fall->SetTestResult(site, 0, vac2_abs_fall[site]);
		VAC2_SNK_DET_ABS_Hys->SetTestResult(site, 0, vac2_abs_hys[site]);
		VAC2_SNK_DET_SR_12mV_uS->SetTestResult(site, 0, slewrate_12mv_us_vac2[site]);
		VAC2_SNK_DET_SR_5mV_uS->SetTestResult(site, 0, slewrate_5mv_us_vac2[site]);
		IVAC_PULLUP->SetTestResult(site, 0, vac_Ipullup[site]);
	}

    return 0;
}
 
DUT_API int VBUS_Protection(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_OVP_VTH1_Rise = StsGetParam(funcindex, "VBUS_OVP_VTH1_Rise");
    CParam *VBUS_OVP_VTH1_Fall = StsGetParam(funcindex, "VBUS_OVP_VTH1_Fall");
    CParam *VBUS_OVP_VTH1_Hys = StsGetParam(funcindex, "VBUS_OVP_VTH1_Hys");
    CParam *VBUS_OVP_VTH2_Rise = StsGetParam(funcindex, "VBUS_OVP_VTH2_Rise");
    CParam *VBUS_OVP_VTH2_Fall = StsGetParam(funcindex, "VBUS_OVP_VTH2_Fall");
    CParam *VBUS_OVP_VTH2_Hys = StsGetParam(funcindex, "VBUS_OVP_VTH2_Hys");
    CParam *VBUS_OVP_VTH3_Rise = StsGetParam(funcindex, "VBUS_OVP_VTH3_Rise");
    CParam *VBUS_OVP_VTH3_Fall = StsGetParam(funcindex, "VBUS_OVP_VTH3_Fall");
    CParam *VBUS_OVP_VTH3_Hys = StsGetParam(funcindex, "VBUS_OVP_VTH3_Hys");
    CParam *VBUS_OVP_VTH4_Rise = StsGetParam(funcindex, "VBUS_OVP_VTH4_Rise");
    CParam *VBUS_OVP_VTH4_Fall = StsGetParam(funcindex, "VBUS_OVP_VTH4_Fall");
    CParam *VBUS_OVP_VTH4_Hys = StsGetParam(funcindex, "VBUS_OVP_VTH4_Hys");
    CParam *VBUS_REVI_VTH_Rise = StsGetParam(funcindex, "VBUS_REVI_VTH_Rise");
    CParam *VBUS_REVI_VTH_Fall = StsGetParam(funcindex, "VBUS_REVI_VTH_Fall");
    CParam *VBUS_REVI_VTH_Hys = StsGetParam(funcindex, "VBUS_REVI_VTH_Hys");
    CParam *VBUS_ASHUT_VTH1_Rise = StsGetParam(funcindex, "VBUS_ASHUT_VTH1_Rise");
    CParam *VBUS_ASHUT_VTH1_Fall = StsGetParam(funcindex, "VBUS_ASHUT_VTH1_Fall");
    CParam *VBUS_ASHUT_VTH1_Hys = StsGetParam(funcindex, "VBUS_ASHUT_VTH1_Hys");
    CParam *VBUS_HT_4P8V_Rise = StsGetParam(funcindex, "VBUS_HT_4P8V_Rise");
    CParam *VBUS_HT_4P8V_Fall = StsGetParam(funcindex, "VBUS_HT_4P8V_Fall");
    CParam *VBUS_HT_4P8V_Hys = StsGetParam(funcindex, "VBUS_HT_4P8V_Hys");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vbus_ovp1_rise[SITE_NUM] = { 0 };
	double vbus_ovp1_fall[SITE_NUM] = { 0 };
	double vbus_ovp1_hys[SITE_NUM] = { 0 };
	double vbus_ovp2_rise[SITE_NUM] = { 0 };
	double vbus_ovp2_fall[SITE_NUM] = { 0 };
	double vbus_ovp2_hys[SITE_NUM] = { 0 };
	double vbus_ovp3_rise[SITE_NUM] = { 0 };
	double vbus_ovp3_fall[SITE_NUM] = { 0 };
	double vbus_ovp3_hys[SITE_NUM] = { 0 };
	double vbus_ovp4_rise[SITE_NUM] = { 0 };
	double vbus_ovp4_fall[SITE_NUM] = { 0 };
	double vbus_ovp4_hys[SITE_NUM] = { 0 };
	double vbus_revive_rise[SITE_NUM] = { 0 };
	double vbus_revive_fall[SITE_NUM] = { 0 };
	double vbus_revive_hys[SITE_NUM] = { 0 };
	double vbus_ashut_rise[SITE_NUM] = { 0 };
	double vbus_ashut_fall[SITE_NUM] = { 0 };
	double vbus_ashut_hys[SITE_NUM] = { 0 };
	double vbus_ashut2_rise[SITE_NUM] = { 0 };
	double vbus_ashut2_fall[SITE_NUM] = { 0 };
	double vbus_ashut2_hys[SITE_NUM] = { 0 };
	double vbus_ht_4p8v_rise[SITE_NUM] = { 0 };
	double vbus_ht_4p8v_fall[SITE_NUM] = { 0 };
	double vbus_ht_4p8v_hys[SITE_NUM] = { 0 };

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double vbus_protect_r[200] = { 0.0 };
	double vbus_protect_f[200] = { 0.0 };
	double Trig = 2.5;
	double TrigR = 3.5;
	double TrigF = 3.5;
	double Trig_Point[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap,-1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 5.5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xA3);//		field[(WAKE_UP,1),(VBUS_OVP,0),(EN_DTEST0,1),(DTEST0_MUX,35)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vbus_protect_r[0], sam, 1,6.1, 6.9);//  PMID-->SW
	VBUS_FOVI.AwgLoader("vbus_protect_r_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_protect_r, sam);
	VBUS_FOVI.AwgSelect("vbus_protect_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	VBUS_FOVI.Set(FV, 6, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_ovp1_rise[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);		
	}
	STSAWGCreateRampData(&vbus_protect_f[0], sam, 1, 6.6, 5.8);
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_protect_f_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_protect_f, sam);
	VBUS_FOVI.AwgSelect("vbus_protect_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	VBUS_FOVI.Set(FV, 6.9, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_ovp1_fall[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vbus_ovp1_hys[site] = (vbus_ovp1_rise[site] - vbus_ovp1_fall[site])*1e3;//mV
	}

	//---------------------------OVP2 VTH
	I2CWriteSameData(DEV_ADDR, 0x0C, 0x08);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xA3);//		field[(WAKE_UP,1),(VBUS_OVP,2),(EN_DTEST0,1),(DTEST0_MUX,35)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vbus_protect_r[0], sam, 1, 13.1, 13.9);
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_protect_r_pattern", FV, FOVIe_20V, FOVIe_100MA, vbus_protect_r, sam);
	VBUS_FOVI.AwgSelect("vbus_protect_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	VBUS_FOVI.Set(FV, 13, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_ovp2_rise[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	STSAWGCreateRampData(&vbus_protect_f[0], sam, 1, 13.6, 12.8);
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_protect_f_pattern", FV, FOVIe_20V, FOVIe_100MA, vbus_protect_f, sam);
	VBUS_FOVI.AwgSelect("vbus_protect_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	VBUS_FOVI.Set(FV, 14, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_ovp2_fall[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vbus_ovp2_hys[site] = (vbus_ovp2_rise[site] - vbus_ovp2_fall[site])*1e3;//mV
	}


	//---------------------------OVP3 VTH
	I2CWriteSameData(DEV_ADDR, 0x0C, 0x14);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xA3);//		field[(WAKE_UP,1),(VBUS_OVP,5),(EN_DTEST0,1),(DTEST0_MUX,35)]
	delay_ms(1);
	if (extractIntFromString(DEVICE_SEL) == 6801 || extractIntFromString(DEVICE_SEL) == 6803)
	{
		// Set a sinewave data array, the start address starts from 0, data size is 100.
		STSAWGCreateRampData(&vbus_protect_r[0], sam, 1, 19.4 ,20.2);
		VBUS_FOVI.AwgClear();
		VBUS_FOVI.AwgLoader("vbus_protect_r_pattern", FV, FOVIe_40V, FOVIe_100MA, vbus_protect_r, sam);
		VBUS_FOVI.AwgSelect("vbus_protect_r_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
		VBUS_FOVI.Set(FV, 19.2, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VBUS_FOVI.Set(FV, 19.2, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_us(500);
		STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
		STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
		STSAWGRun();//Enable AWG and measurement synchronously
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
			vbus_ovp3_rise[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		}
		STSAWGCreateRampData(&vbus_protect_f[0], sam, 1, 20.0, 19.0);
		VBUS_FOVI.AwgClear();
		VBUS_FOVI.AwgLoader("vbus_protect_f_pattern", FV, FOVIe_40V, FOVIe_100MA, vbus_protect_f, sam);
		VBUS_FOVI.AwgSelect("vbus_protect_f_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
		VBUS_FOVI.Set(FV, 20.5, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_us(500);
		STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
		STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
		STSAWGRun();//Enable AWG and measurement synchronously
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
			vbus_ovp3_fall[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
			vbus_ovp3_hys[site] = (vbus_ovp3_rise[site] - vbus_ovp3_fall[site])*1e3;//mV
		}
	}
	if (extractIntFromString(DEVICE_SEL) == 6802)
	{
		// Set a sinewave data array, the start address starts from 0, data size is 100.
		STSAWGCreateRampData(&vbus_protect_r[0], sam, 1, 13.1, 13.9);
		VBUS_FOVI.AwgClear();
		VBUS_FOVI.AwgLoader("vbus_protect_r_pattern", FV, FOVIe_20V, FOVIe_100MA, vbus_protect_r, sam);
		VBUS_FOVI.AwgSelect("vbus_protect_r_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
		VBUS_FOVI.Set(FV, 13, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_us(500);
		STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
		STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
		STSAWGRun();//Enable AWG and measurement synchronously
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
			vbus_ovp4_rise[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		}

		STSAWGCreateRampData(&vbus_protect_f[0], sam, 1, 13.5, 12.9);
		VBUS_FOVI.AwgClear();
		VBUS_FOVI.AwgLoader("vbus_protect_f_pattern", FV, FOVIe_20V, FOVIe_100MA, vbus_protect_f, sam);
		VBUS_FOVI.AwgSelect("vbus_protect_f_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
		VBUS_FOVI.Set(FV, 14, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_us(500);
		STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
		STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
		STSAWGRun();//Enable AWG and measurement synchronously
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
			vbus_ovp4_fall[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
			vbus_ovp4_hys[site] = (vbus_ovp4_rise[site] - vbus_ovp4_fall[site])*1e3;//mV
		}
	}
	

	//--------------------------VBUS REVIVE
	VBUS_FOVI.Set(FV, V_TYP_VBAT - 0.3, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
	VBUS_FOVI.Set(FV, V_TYP_VBAT - 0.3, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(1500);
	I2CWriteSameData(DEV_ADDR, 0x0C, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xA1);//		field[(WAKE_UP,1),(VBUS_OVP,5),(EN_DTEST0,1),(DTEST0_MUX,35)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vbus_protect_r[0], sam, 1, V_TYP_VBAT-0.1, V_TYP_VBAT+0.1);
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_protect_r_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_protect_r, sam);
	VBUS_FOVI.AwgSelect("vbus_protect_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_revive_rise[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	VBUS_FOVI.Set(FV, V_TYP_VBAT, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(1500);
	STSAWGCreateRampData(&vbus_protect_f[0], sam, 1, V_TYP_VBAT-0.02, V_TYP_VBAT -0.22);
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_protect_f_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_protect_f, sam);
	VBUS_FOVI.AwgSelect("vbus_protect_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_revive_fall[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vbus_revive_hys[site] = (vbus_revive_rise[site] - vbus_revive_fall[site])*1e3;//mV
	}


	//--------------------------VBUS ASHUTDOWN-VTH1
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xA0);//		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,32)]
	delay_ms(1);
	VBUS_FOVI.Set(FV, V_TYP_VBAT, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vbus_protect_r[0], sam, 1, V_TYP_VBAT+0.085, V_TYP_VBAT+0.29);
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_protect_r_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_protect_r, sam);
	VBUS_FOVI.AwgSelect("vbus_protect_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_ashut_rise[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	VBUS_FOVI.Set(FV, V_TYP_VBAT + 0.15, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSAWGCreateRampData(&vbus_protect_f[0], sam, 1, V_TYP_VBAT+0.13, V_TYP_VBAT-0.01);
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_protect_f_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_protect_f, sam);
	VBUS_FOVI.AwgSelect("vbus_protect_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_ashut_fall[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vbus_ashut_hys[site] = (vbus_ashut_rise[site] - vbus_ashut_fall[site])*1e3;//mV
	}


	//--------------------------VBUS High Than 4.8V 
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xA2);	//		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,34),(BUBO_MODE,1)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vbus_protect_r[0], sam, 1, 4.55, 4.85);//
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_protect_r_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_protect_r, sam);
	VBUS_FOVI.AwgSelect("vbus_protect_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	VBUS_FOVI.Set(FV, 4.5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_ht_4p8v_rise[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	STSAWGCreateRampData(&vbus_protect_f[0], sam, 1, 4.75, 4.45);
	VBUS_FOVI.AwgClear();
	VBUS_FOVI.AwgLoader("vbus_protect_f_pattern", FV, FOVIe_10V, FOVIe_100MA, vbus_protect_f, sam);
	VBUS_FOVI.AwgSelect("vbus_protect_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	VBUS_FOVI.Set(FV, 4.9, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_ht_4p8v_fall[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vbus_ht_4p8v_hys[site] = (vbus_ht_4p8v_rise[site] - vbus_ht_4p8v_fall[site])*1e3;//mV
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		//SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	}

	FOR_EACH_VALID_SITE(site)
	{
		VBUS_OVP_VTH1_Rise->SetTestResult(site, 0, vbus_ovp1_rise[site]);
		VBUS_OVP_VTH1_Fall->SetTestResult(site, 0, vbus_ovp1_fall[site]);
		VBUS_OVP_VTH1_Hys->SetTestResult(site, 0, vbus_ovp1_hys[site]);
		VBUS_OVP_VTH2_Rise->SetTestResult(site, 0, vbus_ovp2_rise[site]);
		VBUS_OVP_VTH2_Fall->SetTestResult(site, 0, vbus_ovp2_fall[site]);
		VBUS_OVP_VTH2_Hys->SetTestResult(site, 0, vbus_ovp2_hys[site]);
		if (extractIntFromString(DEVICE_SEL) == 6801 || extractIntFromString(DEVICE_SEL) == 6803)
		{
			VBUS_OVP_VTH3_Rise->SetTestResult(site, 0, vbus_ovp3_rise[site]);
			VBUS_OVP_VTH3_Fall->SetTestResult(site, 0, vbus_ovp3_fall[site]);
			VBUS_OVP_VTH3_Hys->SetTestResult(site, 0, vbus_ovp3_hys[site]);
		}
		if (extractIntFromString(DEVICE_SEL) == 6802)
		{
			VBUS_OVP_VTH4_Rise->SetTestResult(site, 0, vbus_ovp4_rise[site]);
			VBUS_OVP_VTH4_Fall->SetTestResult(site, 0, vbus_ovp4_fall[site]);
			VBUS_OVP_VTH4_Hys->SetTestResult(site, 0, vbus_ovp4_hys[site]);
		}
		VBUS_REVI_VTH_Rise->SetTestResult(site, 0, (vbus_revive_rise[site]-V_TYP_VBAT)*1e3);
		VBUS_REVI_VTH_Fall->SetTestResult(site, 0, (vbus_revive_fall[site] - V_TYP_VBAT)*1e3);
		VBUS_REVI_VTH_Hys->SetTestResult(site, 0, vbus_revive_hys[site]);
		VBUS_ASHUT_VTH1_Rise->SetTestResult(site, 0,(vbus_ashut_rise[site] - V_TYP_VBAT)*1e3);
		VBUS_ASHUT_VTH1_Fall->SetTestResult(site, 0, (vbus_ashut_fall[site] - V_TYP_VBAT)*1e3);
		VBUS_ASHUT_VTH1_Hys->SetTestResult(site, 0, vbus_ashut_hys[site]);
		VBUS_HT_4P8V_Rise->SetTestResult(site, 0, vbus_ht_4p8v_rise[site]);
		VBUS_HT_4P8V_Fall->SetTestResult(site, 0, vbus_ht_4p8v_fall[site]);
		VBUS_HT_4P8V_Hys->SetTestResult(site, 0, vbus_ht_4p8v_hys[site]);
	}



    return 0;
}
 
DUT_API int VBAT_Protection(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_OVP_Rise = StsGetParam(funcindex, "VBAT_OVP_Rise");
    CParam *VBAT_OVP_Fall = StsGetParam(funcindex, "VBAT_OVP_Fall");
    CParam *VBAT_OVP_Hys = StsGetParam(funcindex, "VBAT_OVP_Hys");
    CParam *VBAT_OVP_RiseMI = StsGetParam(funcindex, "VBAT_OVP_RiseMI");
    CParam *VBAT_OVP_FallMI = StsGetParam(funcindex, "VBAT_OVP_FallMI");
    CParam *VBAT_OVP_HysMI = StsGetParam(funcindex, "VBAT_OVP_HysMI");
    CParam *VBAT_LOW_Rise = StsGetParam(funcindex, "VBAT_LOW_Rise");
    CParam *VBAT_LOW_Fall = StsGetParam(funcindex, "VBAT_LOW_Fall");
    CParam *VBAT_LOW_Hys = StsGetParam(funcindex, "VBAT_LOW_Hys");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vbat_low_rise[SITE_NUM] = { 0 };
	double vbat_low_fall[SITE_NUM] = { 0 };
	double vbat_low_hys[SITE_NUM] = { 0 };
	double vbat_ovp_rise[SITE_NUM] = { 0 };
	double vbat_ovp_fall[SITE_NUM] = { 0 };
	double vbat_ovp_hys[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K37_VAC_Cap, K58_INT_PU, K43_INT_ACM, K25_VCC_Cap, -1);
	delay_ms(3);
	VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 3.7, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(5);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	delay_ms(1);
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double vbat_protect_r[200] = { 0.0 };
	double vbat_protect_f[200] = { 0.0 };
	double Trig = 2.5;
	double Trig_Point[SITE_NUM] = { 0 };
	//===================VBAT OVP
	I2CWriteSameData(DEV_ADDR, 0x0A, (DWORD)spec[DEVICE_SEL]("CV_CONFIG"));
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x9E);//		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,30)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	//STSAWGCreateRampData(&vbat_protect_r[0], sam, 1, 4.15, 4.35);
	STSAWGCreateRampData(&vbat_protect_r[0], sam, 1, spec[DEVICE_SEL]("VbatOvp_Rstart"), spec[DEVICE_SEL]("VbatOvp_Rstop"));
	VBAT_ACM.AwgClear();
	VBAT_ACM.AwgLoader("vbat_protect_r_pattern", FV, ACM200_10V, ACM200_100MA, vbat_protect_r, sam);
	VBAT_ACM.AwgSelect("vbat_protect_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	//VBAT_ACM.Set(FV, 4.1, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, spec[DEVICE_SEL]("VbatOvp_Rstart")-0.05, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbat_ovp_rise[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}
	//STSAWGCreateRampData(&vbat_protect_f[0], sam, 1, 4.3, 4.1);
	STSAWGCreateRampData(&vbat_protect_f[0], sam, 1, spec[DEVICE_SEL]("VbatOvp_Fstart"), spec[DEVICE_SEL]("VbatOvp_Fstop"));
	VBAT_ACM.AwgClear();
	VBAT_ACM.AwgLoader("vbat_protect_f_pattern", FV, ACM200_10V, ACM200_100MA, vbat_protect_f, sam);
	VBAT_ACM.AwgSelect("vbat_protect_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	//VBAT_ACM.Set(FV, 4.35, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, spec[DEVICE_SEL]("VbatOvp_Fstart")+0.05, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbat_ovp_fall[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vbat_ovp_hys[site] = (vbat_ovp_rise[site] - vbat_ovp_fall[site])*1e3;//mV
	}

	VBAT_ACM.Set(FV, 2.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	I2CWriteSameData(DEV_ADDR, 0x0A, 0x10);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x9C);//		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,28),(BUBO_MODE,1)]
	delay_ms(1);

	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vbat_protect_r[0], sam, 1, 2.55, 2.85);
	VBAT_ACM.AwgClear();
	VBAT_ACM.AwgLoader("vbat_protect_r_pattern", FV, ACM200_10V, ACM200_100MA, vbat_protect_r, sam);
	VBAT_ACM.AwgSelect("vbat_protect_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(0.5, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbat_low_rise[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	VBAT_ACM.Set(FV, 2.65, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(1500);
	STSAWGCreateRampData(&vbat_protect_f[0], sam, 1, 2.65, 2.35);
	VBAT_ACM.AwgClear();
	VBAT_ACM.AwgLoader("vbat_protect_f_pattern", FV, ACM200_10V, ACM200_100MA, vbat_protect_f, sam);
	VBAT_ACM.AwgSelect("vbat_protect_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbat_low_fall[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vbat_low_hys[site] = (vbat_low_rise[site] - vbat_low_fall[site])*1e3;//mV
	}

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
	delay_ms(1);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

	//if (!TTR)
	//{
	//	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
	//	delay_ms(1);
	//	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	//	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	//	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	//}
	//else
	//{
	//	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
	//	//delay_ms(1);
	//	//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	//	//VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	//	//SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	//}


	FOR_EACH_VALID_SITE(site)
	{
		VBAT_LOW_Rise->SetTestResult(site, 0, vbat_low_rise[site]);
		VBAT_LOW_Fall->SetTestResult(site, 0, vbat_low_fall[site]);
		VBAT_LOW_Hys->SetTestResult(site, 0, vbat_low_hys[site]);
		if (spec[DEVICE_SEL]("VBAT_CV_Point") == 4.2)
		{
			VBAT_OVP_Rise->SetTestResult(site, 0, 100 * vbat_ovp_rise[site] / spec[DEVICE_SEL]("VBAT_CV_Point"));
			VBAT_OVP_Fall->SetTestResult(site, 0, 100 * vbat_ovp_fall[site] / spec[DEVICE_SEL]("VBAT_CV_Point"));
			VBAT_OVP_Hys->SetTestResult(site, 0, 0.1 * vbat_ovp_hys[site] / spec[DEVICE_SEL]("VBAT_CV_Point"));
		}
		else
		{
			VBAT_OVP_RiseMI->SetTestResult(site, 0, 100 * vbat_ovp_rise[site] / spec[DEVICE_SEL]("VBAT_CV_Point"));
			VBAT_OVP_FallMI->SetTestResult(site, 0, 100 * vbat_ovp_fall[site] / spec[DEVICE_SEL]("VBAT_CV_Point"));
			VBAT_OVP_HysMI->SetTestResult(site, 0, 0.1 * vbat_ovp_hys[site] / spec[DEVICE_SEL]("VBAT_CV_Point"));
		}
	}

    return 0;
}
 
DUT_API int VTRIKLE_VTH(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VTRIKLE_VTH1_Rise_DSA = StsGetParam(funcindex, "VTRIKLE_VTH1_Rise_DSA");
    CParam *VTRIKLE_VTH1_Fall_SCM = StsGetParam(funcindex, "VTRIKLE_VTH1_Fall_SCM");
    CParam *VTRIKLE_VTH1_Hys_SCM = StsGetParam(funcindex, "VTRIKLE_VTH1_Hys_SCM");
    CParam *VTRIKLE_VTH2_Rise_DSA = StsGetParam(funcindex, "VTRIKLE_VTH2_Rise_DSA");
    CParam *VTRIKLE_VTH2_Fall_SCM = StsGetParam(funcindex, "VTRIKLE_VTH2_Fall_SCM");
    CParam *VTRIKLE_VTH2_Hys_SCM = StsGetParam(funcindex, "VTRIKLE_VTH2_Hys_SCM");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vtrikle_vth1_rise[SITE_NUM] = { 0 };
	double vtrikle_vth1_fall[SITE_NUM] = { 0 };
	double vtrikle_vth1_hys[SITE_NUM] = { 0 };
	double vtrikle_vth2_rise[SITE_NUM] = { 0 };
	double vtrikle_vth2_fall[SITE_NUM] = { 0 };
	double vtrikle_vth2_hys[SITE_NUM] = { 0 };
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double vtrikle_r[200] = { 0.0 };
	double vtrikle_f[200] = { 0.0 };
	double Trig = 2.5;
	double Trig_Point[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K37_VAC_Cap, K58_INT_PU, K43_INT_ACM, K25_VCC_Cap,-1);
	delay_ms(3);
	VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	//===================VTRIKLE VTH2
	I2CWriteSameData(DEV_ADDR, 0x0A, 0x10);//VTRIKEL=3V
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x9F);//		field[(WAKE_UP,1),(VTRICKLE,1)(EN_DTEST0,1),(DTEST0_MUX,31),(BUBO_MODE,0)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vtrikle_r[0], sam, 1, 2.85, 3.15);
	VBAT_ACM.AwgClear();
	VBAT_ACM.AwgLoader("vtrikle_r_pattern", FV, ACM200_10V, ACM200_100MA, vtrikle_r, sam);
	VBAT_ACM.AwgSelect("vtrikle_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.Set(FV, 2.8, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vtrikle_vth2_rise[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	STSAWGCreateRampData(&vtrikle_f[0], sam, 1, 2.95, 2.55);
	VBAT_ACM.AwgClear();
	VBAT_ACM.AwgLoader("vtrikle_f_pattern", FV, ACM200_10V, ACM200_100MA, vtrikle_f, sam);
	VBAT_ACM.AwgSelect("vtrikle_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.Set(FV, 3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vtrikle_vth2_fall[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vtrikle_vth2_hys[site] = (vtrikle_vth2_rise[site] - vtrikle_vth2_fall[site])*1e3;//mV
	}

	//===================VTRIKLE VTH1
	I2CWriteSameData(DEV_ADDR, 0x0A, 0x00);//VTRIKLE=2.7V
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x9F);//		field[(WAKE_UP,1),(VTRICKLE,0)(EN_DTEST0,1),(DTEST0_MUX,31),(BUBO_MODE,0)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vtrikle_r[0], sam, 1, 2.55, 2.85);
	VBAT_ACM.AwgClear();
	VBAT_ACM.AwgLoader("vtrikle_r_pattern", FV, ACM200_10V, ACM200_100MA, vtrikle_r, sam);
	VBAT_ACM.AwgSelect("vtrikle_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.Set(FV, 2.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vtrikle_vth1_rise[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	STSAWGCreateRampData(&vtrikle_f[0], sam, 1, 2.55, 2.25);
	VBAT_ACM.AwgClear();
	VBAT_ACM.AwgLoader("vtrikle_f_pattern", FV, ACM200_10V, ACM200_100MA, vtrikle_f, sam);
	VBAT_ACM.AwgSelect("vtrikle_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.Set(FV, 2.8, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vtrikle_vth1_fall[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		vtrikle_vth1_hys[site] = (vtrikle_vth1_rise[site] - vtrikle_vth1_fall[site])*1e3;//mV
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		//SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		//delay_ms(1);
		//VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		//VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		//SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		VTRIKLE_VTH1_Rise_DSA->SetTestResult(site, 0, vtrikle_vth1_rise[site]);
		VTRIKLE_VTH1_Fall_SCM->SetTestResult(site, 0, vtrikle_vth1_fall[site]);
		VTRIKLE_VTH1_Hys_SCM->SetTestResult(site, 0, vtrikle_vth1_hys[site]);
		VTRIKLE_VTH2_Rise_DSA->SetTestResult(site, 0, vtrikle_vth2_rise[site]);
		VTRIKLE_VTH2_Fall_SCM->SetTestResult(site, 0, vtrikle_vth2_fall[site]);
		VTRIKLE_VTH2_Hys_SCM->SetTestResult(site, 0, vtrikle_vth2_hys[site]);
	}


    return 0;
}
 
DUT_API int VRE_CHG_VTH(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VRE_CHG_VTH1_Rise_SCM = StsGetParam(funcindex, "VRE_CHG_VTH1_Rise_SCM");
    CParam *VRE_CHG_VTH1_Fall_DSA = StsGetParam(funcindex, "VRE_CHG_VTH1_Fall_DSA");
    CParam *VRE_CHG_VTH1_Hys_SCM = StsGetParam(funcindex, "VRE_CHG_VTH1_Hys_SCM");
    CParam *VRE_CHG_VTH2_Rise_SCM = StsGetParam(funcindex, "VRE_CHG_VTH2_Rise_SCM");
    CParam *VRE_CHG_VTH2_Fall_DSA = StsGetParam(funcindex, "VRE_CHG_VTH2_Fall_DSA");
    CParam *VRE_CHG_VTH2_Hys_SCM = StsGetParam(funcindex, "VRE_CHG_VTH2_Hys_SCM");
    CParam *VRE_CHG_VTH1_Rise_MI = StsGetParam(funcindex, "VRE_CHG_VTH1_Rise_MI");
    CParam *VRE_CHG_VTH1_Fall_MI = StsGetParam(funcindex, "VRE_CHG_VTH1_Fall_MI");
    CParam *VRE_CHG_VTH1_Hys_MI = StsGetParam(funcindex, "VRE_CHG_VTH1_Hys_MI");
    CParam *VRE_CHG_VTH2_Rise_MI = StsGetParam(funcindex, "VRE_CHG_VTH2_Rise_MI");
    CParam *VRE_CHG_VTH2_Fall_MI = StsGetParam(funcindex, "VRE_CHG_VTH2_Fall_MI");
    CParam *VRE_CHG_VTH2_Hys_MI = StsGetParam(funcindex, "VRE_CHG_VTH2_Hys_MI");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vrechg_vth1_rise[SITE_NUM] = { 0 };
	double vrechg_vth1_fall[SITE_NUM] = { 0 };
	double vrechg_vth1_hys[SITE_NUM] = { 0 };
	double vrechg_vth2_rise[SITE_NUM] = { 0 };
	double vrechg_vth2_fall[SITE_NUM] = { 0 };
	double vrechg_vth2_hys[SITE_NUM] = { 0 };
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double vrechg_r[200] = { 0.0 };
	double vrechg_f[200] = { 0.0 };
	double Trig = 2.5;
	double Trig_Point[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K37_VAC_Cap, K58_INT_PU, K43_INT_ACM, K25_VCC_Cap,-1);
	delay_ms(3);
	VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	//===================VRE_CHG_VTH1
	I2CWriteSameData(DEV_ADDR, 0x0A, (DWORD)spec[DEVICE_SEL]("CV_CONFIG"));
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x9D);//		field[(WAKE_UP,1),(VRE_CHG,0)(EN_DTEST0,1),(DTEST0_MUX,29),(BUBO_MODE,0)]

	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vrechg_r[0], sam, 1, spec[DEVICE_SEL]("Rechg_Rstart1"), spec[DEVICE_SEL]("Rechg_Rstop1"));
	//STSAWGCreateRampData(&vrechg_r[0], sam, 1,4,5);
	VBAT_ACM.AwgClear();
	VBAT_ACM.AwgLoader("vrechg_r_pattern", FV, ACM200_10V, ACM200_100MA, vrechg_r, sam);
	VBAT_ACM.AwgSelect("vrechg_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.Set(FV, spec[DEVICE_SEL]("Rechg_Rstart1")-0.05, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//VBAT_ACM.Set(FV, 3.95, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vrechg_vth1_rise[site] = (spec[DEVICE_SEL]("VBAT_CV_Point") - VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]))*1e3;//mV
	}

	STSAWGCreateRampData(&vrechg_f[0], sam, 1, spec[DEVICE_SEL]("Rechg_Fstart1"), spec[DEVICE_SEL]("Rechg_Fstop1"));
	//STSAWGCreateRampData(&vrechg_f[0], sam, 1, 5, 4);
	VBAT_ACM.AwgClear();
	VBAT_ACM.AwgLoader("vrechg_f_pattern", FV, ACM200_10V, ACM200_100MA, vrechg_f, sam);
	VBAT_ACM.AwgSelect("vrechg_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.Set(FV, spec[DEVICE_SEL]("Rechg_Fstart1")+ 0.05, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//VBAT_ACM.Set(FV,5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vrechg_vth1_fall[site] = (spec[DEVICE_SEL]("VBAT_CV_Point") - VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]))*1e3;//mV
		vrechg_vth1_hys[site] =  vrechg_vth1_fall[site]-vrechg_vth1_rise[site];//mV
	}


	//===================VRE_CHG_VTH2
	I2CWriteSameData(DEV_ADDR, 0x0A, (DWORD)(spec[DEVICE_SEL]("CV_CONFIG")+8));
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x9D);	//		field[(WAKE_UP,1),(VRE_CHG,1)(EN_DTEST0,1),(DTEST0_MUX,29),(BUBO_MODE,0)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vrechg_r[0], sam, 1, spec[DEVICE_SEL]("Rechg_Rstart2"), spec[DEVICE_SEL]("Rechg_Rstop2"));
	VBAT_ACM.AwgClear();
	VBAT_ACM.AwgLoader("vrechg_r_pattern", FV, ACM200_10V, ACM200_100MA, vrechg_r, sam);
	VBAT_ACM.AwgSelect("vrechg_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.Set(FV, spec[DEVICE_SEL]("Rechg_Rstart2")-0.05, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{	
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vrechg_vth2_rise[site] = (spec[DEVICE_SEL]("VBAT_CV_Point") - VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]))*1e3;//mV
	}

	STSAWGCreateRampData(&vrechg_f[0], sam, 1, spec[DEVICE_SEL]("Rechg_Fstart2"), spec[DEVICE_SEL]("Rechg_Fstop2"));
	VBAT_ACM.AwgClear();
	VBAT_ACM.AwgLoader("vrechg_f_pattern", FV, ACM200_10V, ACM200_100MA, vrechg_f, sam);
	VBAT_ACM.AwgSelect("vrechg_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.Set(FV, spec[DEVICE_SEL]("Rechg_Fstart2")+0.05, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vrechg_vth2_fall[site] = (spec[DEVICE_SEL]("VBAT_CV_Point") - VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]))*1e3;//mV
		vrechg_vth2_hys[site] = vrechg_vth2_fall[site]- vrechg_vth2_rise[site];//mV
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		VAC123_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	}


	FOR_EACH_VALID_SITE(site)
	{
		if (spec[DEVICE_SEL]("VBAT_CV_Point") == 4.2)
		{
			VRE_CHG_VTH1_Rise_SCM->SetTestResult(site, 0, vrechg_vth1_rise[site]);
			VRE_CHG_VTH1_Fall_DSA->SetTestResult(site, 0, vrechg_vth1_fall[site]);
			VRE_CHG_VTH1_Hys_SCM->SetTestResult(site, 0, vrechg_vth1_hys[site]);
			VRE_CHG_VTH2_Rise_SCM->SetTestResult(site, 0, vrechg_vth2_rise[site]);
			VRE_CHG_VTH2_Fall_DSA->SetTestResult(site, 0, vrechg_vth2_fall[site]);
			VRE_CHG_VTH2_Hys_SCM->SetTestResult(site, 0, vrechg_vth2_hys[site]);
		}
		else
		{
			VRE_CHG_VTH1_Rise_MI->SetTestResult(site, 0, vrechg_vth1_rise[site]);
			VRE_CHG_VTH1_Fall_MI->SetTestResult(site, 0, vrechg_vth1_fall[site]);
			VRE_CHG_VTH1_Hys_MI-> SetTestResult(site, 0, vrechg_vth1_hys[site]);
			VRE_CHG_VTH2_Rise_MI->SetTestResult(site, 0, vrechg_vth2_rise[site]);
			VRE_CHG_VTH2_Fall_MI->SetTestResult(site, 0, vrechg_vth2_fall[site]);
			VRE_CHG_VTH2_Hys_MI->SetTestResult(site, 0, vrechg_vth2_hys[site]);
		}

	}


    return 0;
}
 
DUT_API int NTC_Function(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *NTC_COLD_BU_Rise = StsGetParam(funcindex, "NTC_COLD_BU_Rise");
    CParam *NTC_COLD_BU_Fall = StsGetParam(funcindex, "NTC_COLD_BU_Fall");
    CParam *NTC_COLD_BU_Hys = StsGetParam(funcindex, "NTC_COLD_BU_Hys");
    CParam *NTC_COLD_BO_Rise = StsGetParam(funcindex, "NTC_COLD_BO_Rise");
    CParam *NTC_COLD_BO_Fall = StsGetParam(funcindex, "NTC_COLD_BO_Fall");
    CParam *NTC_COLD_BO_Hys = StsGetParam(funcindex, "NTC_COLD_BO_Hys");
    CParam *NTC_JUDGE_Rise = StsGetParam(funcindex, "NTC_JUDGE_Rise");
    CParam *NTC_JUDGE_Fall = StsGetParam(funcindex, "NTC_JUDGE_Fall");
    CParam *NTC_JUDGE_Hys = StsGetParam(funcindex, "NTC_JUDGE_Hys");
    CParam *NTC_HOT_BU_T0_Rise = StsGetParam(funcindex, "NTC_HOT_BU_T0_Rise");
    CParam *NTC_HOT_BU_T0_Fall = StsGetParam(funcindex, "NTC_HOT_BU_T0_Fall");
    CParam *NTC_HOT_BU_T0_Hys = StsGetParam(funcindex, "NTC_HOT_BU_T0_Hys");
    CParam *NTC_HOT_BU_T1_Rise = StsGetParam(funcindex, "NTC_HOT_BU_T1_Rise");
    CParam *NTC_HOT_BU_T1_Fall = StsGetParam(funcindex, "NTC_HOT_BU_T1_Fall");
    CParam *NTC_HOT_BU_T1_Hys = StsGetParam(funcindex, "NTC_HOT_BU_T1_Hys");
    CParam *NTC_HOT_BO_T0_Rise = StsGetParam(funcindex, "NTC_HOT_BO_T0_Rise");
    CParam *NTC_HOT_BO_T0_Fall = StsGetParam(funcindex, "NTC_HOT_BO_T0_Fall");
    CParam *NTC_HOT_BO_T0_Hys = StsGetParam(funcindex, "NTC_HOT_BO_T0_Hys");
    CParam *NTC_HOT_BO_T1_Rise = StsGetParam(funcindex, "NTC_HOT_BO_T1_Rise");
    CParam *NTC_HOT_BO_T1_Fall = StsGetParam(funcindex, "NTC_HOT_BO_T1_Fall");
    CParam *NTC_HOT_BO_T1_Hys = StsGetParam(funcindex, "NTC_HOT_BO_T1_Hys");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double ntc_cold_bu_rise[SITE_NUM] = { 0 };
	double ntc_cold_bu_fall[SITE_NUM] = { 0 };
	double ntc_cold_bu_hys[SITE_NUM] = { 0 };
	double ntc_cold_bo_rise[SITE_NUM] = { 0 };
	double ntc_cold_bo_fall[SITE_NUM] = { 0 };
	double ntc_cold_bo_hys[SITE_NUM] = { 0 };
	double ntc_hot_bu_t0_rise[SITE_NUM] = { 0 };
	double ntc_hot_bu_t0_fall[SITE_NUM] = { 0 };
	double ntc_hot_bu_t0_hys[SITE_NUM] = { 0 };
	double ntc_hot_bo_t0_rise[SITE_NUM] = { 0 };
	double ntc_hot_bo_t0_fall[SITE_NUM] = { 0 };
	double ntc_hot_bo_t0_hys[SITE_NUM] = { 0 };
	double ntc_hot_bu_t1_rise[SITE_NUM] = { 0 };
	double ntc_hot_bu_t1_fall[SITE_NUM] = { 0 };
	double ntc_hot_bu_t1_hys[SITE_NUM] = { 0 };
	double ntc_hot_bo_t1_rise[SITE_NUM] = { 0 };
	double ntc_hot_bo_t1_fall[SITE_NUM] = { 0 };
	double ntc_hot_bo_t1_hys[SITE_NUM] = { 0 };
	double ntc_judge_rise[SITE_NUM] = { 0 };
	double ntc_judge_fall[SITE_NUM] = { 0 };
	double ntc_judge_hys[SITE_NUM] = { 0 };
	double mnt_ntc_iq[SITE_NUM] = { 0 };
	double mnt_ntc_iq_pre[SITE_NUM] = { 0 };
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double ntc_function_r[200] = { 0.0 };
	double ntc_function_f[200] = { 0.0 };
	double Trig = 2.5;
	double Trig_Point[SITE_NUM] = { 0 };
	cbite.SetOn(K58_INT_PU, K43_INT_ACM,K30_VBAT_Cap,K25_VCC_Cap,-1);
	delay_ms(3);
	NTC_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR,0x10, 0x43);//		field[(WAKE_UP,1)]

	//===================NTC COLD BUCK Mode
	I2CWriteSameData(DEV_ADDR, 0x10,0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x83);	//		field[(WAKE_UP,1),(BUBO_MODE,0),(EN_DTEST0,1),(DTEST0_MUX,3)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&ntc_function_f[0], sam, 1, 0.49, 0.39);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_f_pattern", FV, FOVIe_2V, FOVIe_100MA, ntc_function_f, sam);
	NTC_FOVI.AwgSelect("ntc_function_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	NTC_FOVI.Set(FV, 0.5, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_cold_bu_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV
	}

	STSAWGCreateRampData(&ntc_function_r[0], sam, 1, 0.51, 0.58);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_r_pattern", FV, FOVIe_2V, FOVIe_100MA, ntc_function_r, sam);
	NTC_FOVI.AwgSelect("ntc_function_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	NTC_FOVI.Set(FV, 0.5, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_cold_bu_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV
		ntc_cold_bu_hys[site] = ntc_cold_bu_rise[site] - ntc_cold_bu_fall[site];//mV
	}


	//===================NTC JUDGE
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xBE);//		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,62)]
	delay_ms(1);
	NTC_FOVI.Set(FV,0.2, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSAWGCreateRampData(&ntc_function_f[0], sam, 1, 0.195, 0.115);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_f_pattern", FV, FOVIe_5V, FOVIe_100MA, ntc_function_f, sam);
	NTC_FOVI.AwgSelect("ntc_function_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_judge_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV
	}

	NTC_FOVI.Set(FV, 1.9, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&ntc_function_r[0], sam, 1, 1.94, 2.01);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_r_pattern", FV, FOVIe_5V, FOVIe_100MA, ntc_function_r, sam);
	NTC_FOVI.AwgSelect("ntc_function_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_judge_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV
		ntc_judge_hys[site] = ntc_judge_rise[site] - ntc_judge_fall[site];//mV
	}


	//===================NTC HOT BUCK Mode, TEMP SET =0
	NTC_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x84);//		field[(WAKE_UP,1),(BUBO_MODE,0),(EN_DTEST0,1),(DTEST0_MUX,4),(NTC1_TEMP_SETTING,0)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&ntc_function_r[0], sam, 1, 1.19, 1.41);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_r_pattern", FV, FOVIe_5V, FOVIe_100MA, ntc_function_r, sam);
	NTC_FOVI.AwgSelect("ntc_function_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	NTC_FOVI.Set(FV, 1.15, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_hot_bu_t0_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV
	}

	NTC_FOVI.Set(FV, 1.15, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSAWGCreateRampData(&ntc_function_f[0], sam, 1, 1.13, 1.03);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_f_pattern", FV, FOVIe_5V, FOVIe_100MA, ntc_function_f, sam);
	NTC_FOVI.AwgSelect("ntc_function_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_hot_bu_t0_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV
		ntc_hot_bu_t0_hys[site] = ntc_hot_bu_t0_rise[site] - ntc_hot_bu_t0_fall[site];//mV
	}

	//===================NTC HOT BUCK Mode, TEMP SET =1
	NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x4B);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x84);//		field[(WAKE_UP,1),(BUBO_MODE,0),(EN_DTEST0,1),(DTEST0_MUX,4),(NTC1_TEMP_SETTING,1)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&ntc_function_r[0], sam, 1, 0.99, 1.18);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_r_pattern", FV, FOVIe_2V, FOVIe_100MA, ntc_function_r, sam);
	NTC_FOVI.AwgSelect("ntc_function_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	NTC_FOVI.Set(FV, 0.95, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_hot_bu_t1_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV
	}

	NTC_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSAWGCreateRampData(&ntc_function_f[0], sam, 1, 0.96, 0.86);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_f_pattern", FV, FOVIe_2V, FOVIe_100MA, ntc_function_f, sam);
	NTC_FOVI.AwgSelect("ntc_function_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_hot_bu_t1_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV	
		ntc_hot_bu_t1_hys[site] = ntc_hot_bu_t1_rise[site] - ntc_hot_bu_t1_fall[site];//mV
	}




	//===================NTC COLD BOOST Mode
	NTC_FOVI.Set(FV, 2.5, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x83);		//		field[(WAKE_UP,1),(BUBO_MODE,1),(EN_DTEST0,1),(DTEST0_MUX,3)]
	delay_ms(1);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	NTC_FOVI.Set(FV, 1.2, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSAWGCreateRampData(&ntc_function_f[0], sam, 1, 1.15, 0.99);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_f_pattern", FV, FOVIe_5V, FOVIe_100MA, ntc_function_f, sam);
	NTC_FOVI.AwgSelect("ntc_function_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_cold_bo_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV
	}

	// Set a sinewave data array, the start address starts from 0, data size is 100.
	NTC_FOVI.Set(FV, 1.25, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSAWGCreateRampData(&ntc_function_r[0], sam, 1, 1.28, 1.43);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_r_pattern", FV, FOVIe_5V, FOVIe_100MA, ntc_function_r, sam);
	NTC_FOVI.AwgSelect("ntc_function_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_cold_bo_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]) * 1e3;//mV
		ntc_cold_bo_hys[site] = ntc_cold_bo_rise[site] - ntc_cold_bo_fall[site];//mV
	}




	//===================NTC HOT BOOST Mode, TEMP_SET=0
	NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x84);	//		field[(WAKE_UP,1),(BUBO_MODE,0),(EN_DTEST0,1),(DTEST0_MUX,4),(NTC_Temp_Setting,0)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x84);	//		field[(WAKE_UP,1),(BUBO_MODE,0),(EN_DTEST0,1),(DTEST0_MUX,4),(NTC_Temp_Setting,0)]
	delay_ms(1);
	NTC_FOVI.Set(FV, 0.85, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&ntc_function_r[0], sam, 1, 0.86, 0.98);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_r_pattern", FV, FOVIe_2V, FOVIe_100MA, ntc_function_r, sam);
	NTC_FOVI.AwgSelect("ntc_function_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_hot_bo_t0_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV;
	}

	NTC_FOVI.Set(FV, 0.83, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(1000);
	STSAWGCreateRampData(&ntc_function_f[0], sam, 1, 0.81, 0.74);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_f_pattern", FV, FOVIe_2V, FOVIe_100MA, ntc_function_f, sam);
	NTC_FOVI.AwgSelect("ntc_function_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
	bool failflag = false;
	bool failsite[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_hot_bo_t0_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV;	
		if (ntc_hot_bo_t0_fall[site] > 785)
		{
			failflag = true;
			failsite[site] = 1;
		}
		ntc_hot_bo_t0_hys[site] = ntc_hot_bo_t0_rise[site] - ntc_hot_bo_t0_fall[site];//mV
	}
	if (failflag)
	{
		NTC_FOVI.Set(FV, 1.1, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_us(3000);
		NTC_FOVI.Set(FV, 0.83, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_us(1000);
		STSAWGCreateRampData(&ntc_function_f[0], sam, 1, 0.81, 0.74);
		NTC_FOVI.AwgClear();
		NTC_FOVI.AwgLoader("ntc_function_f_pattern", FV, FOVIe_2V, FOVIe_100MA, ntc_function_f, sam);
		NTC_FOVI.AwgSelect("ntc_function_f_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
		STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
		STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
		STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
			if (failsite[site] == 1)
			{
				ntc_hot_bo_t0_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV;	
				ntc_hot_bo_t0_hys[site] = ntc_hot_bo_t0_rise[site] - ntc_hot_bo_t0_fall[site];//mV
			}
		}
	}

	//===================NTC HOT BOOST Mode， TEMP_SET=1
	NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x4B);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x84);	//		field[(WAKE_UP,1),(BUBO_MODE,0),(EN_DTEST0,1),(DTEST0_MUX,4),(NTC_Temp_Setting,0)]
	delay_ms(1);
	NTC_FOVI.Set(FV, 0.7, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(1000);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&ntc_function_r[0], sam, 1, 0.73, 0.84);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_r_pattern", FV, FOVIe_2V, FOVIe_100MA, ntc_function_r, sam);
	NTC_FOVI.AwgSelect("ntc_function_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_hot_bo_t1_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV;
	}


	NTC_FOVI.Set(FV, 0.71, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(1000);
	STSAWGCreateRampData(&ntc_function_f[0], sam, 1, 0.695, 0.625);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ntc_function_f_pattern", FV, FOVIe_2V, FOVIe_100MA, ntc_function_f, sam);
	NTC_FOVI.AwgSelect("ntc_function_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ntc_hot_bo_t1_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])*1e3;//mV;
		ntc_hot_bo_t1_hys[site] = ntc_hot_bo_t1_rise[site] - ntc_hot_bo_t1_fall[site];//mV
	}





	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(1);
		NTC_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		NTC_COLD_BO_Rise->SetTestResult(site, 0, ntc_cold_bo_rise[site]);
		NTC_COLD_BO_Fall->SetTestResult(site, 0, ntc_cold_bo_fall[site]);
		NTC_COLD_BO_Hys->SetTestResult(site, 0, ntc_cold_bo_hys[site]);
		NTC_COLD_BU_Rise->SetTestResult(site, 0, ntc_cold_bu_rise[site]);
		NTC_COLD_BU_Fall->SetTestResult(site, 0, ntc_cold_bu_fall[site]);
		NTC_COLD_BU_Hys->SetTestResult(site, 0, ntc_cold_bu_hys[site]);
		NTC_JUDGE_Rise->SetTestResult(site, 0, ntc_judge_rise[site]);
		NTC_JUDGE_Fall->SetTestResult(site, 0, ntc_judge_fall[site]);
		NTC_JUDGE_Hys->SetTestResult(site, 0, ntc_judge_hys[site]);
		NTC_HOT_BO_T0_Rise->SetTestResult(site, 0, ntc_hot_bo_t0_rise[site]);
		NTC_HOT_BO_T0_Fall ->SetTestResult(site, 0, ntc_hot_bo_t0_fall[site]);
		NTC_HOT_BO_T0_Hys ->SetTestResult(site, 0, ntc_hot_bo_t0_hys[site]);
		NTC_HOT_BU_T0_Rise->SetTestResult(site, 0, ntc_hot_bu_t0_rise[site]);
		NTC_HOT_BU_T0_Fall ->SetTestResult(site, 0, ntc_hot_bu_t0_fall[site]);
		NTC_HOT_BU_T0_Hys ->SetTestResult(site, 0, ntc_hot_bu_t0_hys[site]);
		NTC_HOT_BO_T1_Rise->SetTestResult(site, 0, ntc_hot_bo_t1_rise[site]);
		NTC_HOT_BO_T1_Fall->SetTestResult(site, 0, ntc_hot_bo_t1_fall[site]);
		NTC_HOT_BO_T1_Hys->SetTestResult(site, 0, ntc_hot_bo_t1_hys[site]);
		NTC_HOT_BU_T1_Rise->SetTestResult(site, 0, ntc_hot_bu_t1_rise[site]);
		NTC_HOT_BU_T1_Fall->SetTestResult(site, 0, ntc_hot_bu_t1_fall[site]);
		NTC_HOT_BU_T1_Hys->SetTestResult(site, 0, ntc_hot_bu_t1_hys[site]);
	}


    return 0;
}
 
DUT_API int FB_Function(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VAC1_FB = StsGetParam(funcindex, "VAC1_FB");
    CParam *VAC2_FB = StsGetParam(funcindex, "VAC2_FB");
    CParam *VAC3_FB = StsGetParam(funcindex, "VAC3_FB");
    CParam *VBUS_FB = StsGetParam(funcindex, "VBUS_FB");
    CParam *VBAT_FB = StsGetParam(funcindex, "VBAT_FB");
    CParam *VBAT_FB_MI = StsGetParam(funcindex, "VBAT_FB_MI");
    CParam *V1P2_BUF_TrimPost = StsGetParam(funcindex, "V1P2_BUF_TrimPost");
    CParam *V1P2_BUF_ATEST0 = StsGetParam(funcindex, "V1P2_BUF_ATEST0");
    CParam *DAC_BUF_TrimPost = StsGetParam(funcindex, "DAC_BUF_TrimPost");
    CParam *VBG_Trim_Post = StsGetParam(funcindex, "VBG_Trim_Post");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double vac1_fb[SITE_NUM] = { 0 };
	double vac2_fb[SITE_NUM] = { 0 };
	double vac3_fb[SITE_NUM] = { 0 };
	double vbus_fb[SITE_NUM] = { 0 };
	double vbat_fb[SITE_NUM] = { 0 };
	double v1p2_buf_atest0[SITE_NUM] = { 0 };
	double v1p2_buf_trim[SITE_NUM] = { 0 };
	double dac_vref_trim[SITE_NUM] = { 0 };
	double  vbg_trim_post[SITE_NUM] = { 0 };
	NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K37_VAC_Cap, K16_VBUS_Cap,K25_VCC_Cap,-1);
	delay_ms(3);
	VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	//VAC123_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	//VBUS_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 1.68, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(2);
	entertestmode();
	//------Bandgap
	I2CWriteSameData(DEV_ADDR, 0x56, 0x62);
	I2CWriteSameData(DEV_ADDR, 0x67, 0x0A);
	I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(EN_ATEST0,1),(ATEST0_MUX,12),(D2A_OVRD_SEL,10),(OVRD_VALUE,3)]
	AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	Retest_voltage_unstable_with_time_out(AMUX_FOVI, vbg_trim_post, spec.get_low_limit("VBG_Trim_Post"), spec.get_high_limit("VBG_Trim_Post"), 1, 5, MEAS_MV);
	//delay_ms(3);
	//AMUX_FOVI.MeasureVI(215, 10);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	vbg_trim_post[site] = AMUX_FOVI.GetMeasResult(site, MVRET)*1e3;//mV
	//}
	I2CWriteSameData(DEV_ADDR, 0x67, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x68, 0x00);//		field[(EN_ATEST0,1),(ATEST0_MUX,12),(D2A_OVRD_SEL,10),(OVRD_VALUE,3)]

	//----------------------VREF_TRIM 
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x9A);
	//		field[(WAKE_UP,1),(EN_ATEST0,1),(ATEST0_MUX,19)]
	//Inherit_register();
	AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	Retest_voltage_unstable_with_time_out(AMUX_FOVI, dac_vref_trim, spec.get_low_limit("DAC_BUF_TrimPost"), spec.get_high_limit("DAC_BUF_TrimPost"), 1, 5, MEAS_MV);
	//delay_ms(3);
	//AMUX_FOVI.MeasureVI(215, 10);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	dac_vref_trim[site] = AMUX_FOVI.GetMeasResult(site, MVRET)*1e3;//mV
	//}

	//------------V1P2_BUF_ATEST0
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);
	//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15),,(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(2);//cannot save
	AMUX_FOVI.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		v1p2_buf_atest0[site] = AMUX_FOVI.GetMeasResult(site, MVRET)*1e3;//mV
	}

	NTC_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x4);
	I2CWriteSameData(DEV_ADDR, 0x57, 0x2);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x4);
	//		field[(WAKE_UP,1),(EN_ATEST1,1),(ATEST1_MUX,2),(DIS_NTC_DETECTION_ANALOG,1)]
	delay_ms(2);//cannot save
	NTC_FOVI.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		v1p2_buf_trim[site] = NTC_FOVI.GetMeasResult(site, MVRET)*1e3;//mV
	}

	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x57, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x00);
	//------------VBAT feedback
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x10);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);
	//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,0),(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(2);//cannot save
	AMUX_FOVI.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		vbat_fb[site] = AMUX_FOVI.GetMeasResult(site, MVRET)*1e3;//mV
	}

	//------------VAC1 feedback
	VAC123_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 0.5, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(2);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x11);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);
	//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,1),(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(1);
	AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(2);//cannot save
	AMUX_FOVI.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		vac1_fb[site] = AMUX_FOVI.GetMeasResult(site, MVRET)*1e3;//mV
	}

	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K37_VAC_Cap, K16_VBUS_Cap,K36_SHARE2_VAC, -1);
	delay_ms(3);
	VAC123_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	//------------VAC2 feedback
	AMUX_FOVI.Set(FV, 0.5, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x12);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);
	//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,2),(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(1);
	AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(2);//cannot save
	AMUX_FOVI.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		vac2_fb[site] = AMUX_FOVI.GetMeasResult(site, MVRET)*1e3;//mV
		//if (site == 10)
		//{
		//	vac2_fb[site] = vac2_fb[site]-2;
		//}
	}
	
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K37_VAC_Cap, K16_VBUS_Cap, K35_SHARE1_VAC,-1);
	delay_ms(3);
	VAC123_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	//------------VAC3 feedback
	AMUX_FOVI.Set(FV, 0.5, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x13);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);
	//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,3),(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(1);
	AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(2);//cannot save
	AMUX_FOVI.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		vac3_fb[site] = AMUX_FOVI.GetMeasResult(site, MVRET)*1e3;//mV
	}
	//------------VBUS feedback
	AMUX_FOVI.Set(FV, 0.5, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x14);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);
	//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,4),(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(1);
	AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(2);//cannot save
	AMUX_FOVI.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		vbus_fb[site] = AMUX_FOVI.GetMeasResult(site, MVRET)*1e3;//mV
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(1);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		VAC1_FB->SetTestResult(site, 0, vac1_fb[site]);
		VAC2_FB->SetTestResult(site, 0, vac2_fb[site]);
		VAC3_FB->SetTestResult(site, 0, vac3_fb[site]);
		VBUS_FB->SetTestResult(site, 0, vbus_fb[site]);
		if (spec[DEVICE_SEL]("VBAT_CV_Point") == 4.2)
		{
			VBAT_FB->SetTestResult(site, 0, vbat_fb[site]);
		}
		else
		{
			VBAT_FB_MI->SetTestResult(site, 0, vbat_fb[site]);
		}	
		V1P2_BUF_ATEST0->SetTestResult(site, 0, v1p2_buf_atest0[site]);
		V1P2_BUF_TrimPost->SetTestResult(site, 0, v1p2_buf_trim[site]);
		DAC_BUF_TrimPost->SetTestResult(site, 0, dac_vref_trim[site]);
		VBG_Trim_Post->SetTestResult(site, 0, vbg_trim_post[site]);
	}

    return 0;
}
 
DUT_API int IR_CHG_COMP(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IR_CHG_COMP1_DST = StsGetParam(funcindex, "IR_CHG_COMP1_DST");
    CParam *IR_CHG_COMP2_DST = StsGetParam(funcindex, "IR_CHG_COMP2_DST");
    CParam *VCLAMP_CHG1_DST = StsGetParam(funcindex, "VCLAMP_CHG1_DST");
    CParam *VCLAMP_CHG2_DST = StsGetParam(funcindex, "VCLAMP_CHG2_DST");
    CParam *IR_CHG_COMP_STOP_Rise = StsGetParam(funcindex, "IR_CHG_COMP_STOP_Rise");
    CParam *IR_CHG_COMP_STOP_Fall = StsGetParam(funcindex, "IR_CHG_COMP_STOP_Fall");
    CParam *IR_CHG_COMP_STOP_Hys = StsGetParam(funcindex, "IR_CHG_COMP_STOP_Hys");
    CParam *IR_CHG_COMP_STOP_Fall_DSA = StsGetParam(funcindex, "IR_CHG_COMP_STOP_Fall_DSA");
    CParam *IR_CHG_COMP_STOP_Hys_SCM = StsGetParam(funcindex, "IR_CHG_COMP_STOP_Hys_SCM");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	double  Vmeas1[SITE_NUM] = { 0 };
	double  Vmeas2[SITE_NUM] = { 0 };
	double  Vmeas3[SITE_NUM] = { 0 };
	double R_clamp_chg1[SITE_NUM] = { 0 };
	double R_clamp_chg2[SITE_NUM] = { 0 };
	double R_chg_comp1[SITE_NUM] = { 0 };
	double R_chg_comp2[SITE_NUM] = { 0 };
	double R_chg_stop_comp_fall[SITE_NUM] = { 0 };
	double R_chg_stop_comp_hys[SITE_NUM] = { 0 };

	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);// add V01 to avoid spike
	delay_ms(1);// add V01 to avoid spike
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);// add V01 to avoid spike
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap,-1);
	delay_ms(3);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(3);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x0F, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x9A);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x96);
	I2CWriteSameData(DEV_ADDR, 0x57, 0x11);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
	//		field[(WAKE_UP,1),(BUBO_MODE,0),(IR_COMP_TYPE,1)(IR_COMP,1),(VCLAMP,0),(D2A_MNT_TM_EN,1),(EN_ATEST0,1),(ATEST0_MUX,18),(EN_ATEST1,1),(ATEST1_MUX,1),(DIS_NTC_DETECTION_ANALOG,1),(EN_DTEST0,1),(DTEST0_MUX,26)]
   delay_ms(2);
	//============IR_CHG_COMP1 &&VCLAMP_CHG1
	NTC_FOVI.Set(FV, 2, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
    delay_ms(5);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas1[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	NTC_FOVI.Set(FV, 1.5, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas2[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	NTC_FOVI.Set(FV, 1.2, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas3[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
		R_clamp_chg1[site] = (Vmeas1[site] - Vmeas3[site]) / 0.4;
		R_chg_comp1[site] = (Vmeas2[site] - Vmeas3[site]) / 0.4/ 3;		
	}

	//============IR_CHG_COMP2 &&VCLAMP_CHG2
	I2CWriteSameData(DEV_ADDR, 0x0F, 0x0E);
	//I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	//I2CWriteSameData(DEV_ADDR, 0x55, 0x9A);
	//I2CWriteSameData(DEV_ADDR, 0x56, 0x96);
	//I2CWriteSameData(DEV_ADDR, 0x57, 0x11);
	//I2CWriteSameData(DEV_ADDR, 0x65, 0x4);
	//		field[(WAKE_UP,1),(BUBO_MODE,0),(IR_COMP_TYPE,1)(IR_COMP,2),(VCLAMP,1),(D2A_MNT_TM_EN,1),(EN_ATEST0,1),(ATEST0_MUX,18),(EN_ATEST1,1),(ATEST1_MUX,1),(DIS_NTC_DETECTION_ANALOG,1),(EN_DTEST0,1),(DTEST0_MUX,26)]
    delay_ms(1);
	NTC_FOVI.Set(FV, 2, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(5);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas1[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	NTC_FOVI.Set(FV, 1.5, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas2[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	NTC_FOVI.Set(FV, 1.2, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas3[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
		R_clamp_chg2[site] = (Vmeas1[site] - Vmeas3[site]) / 0.4;
		R_chg_comp2[site] = (Vmeas2[site] - Vmeas3[site]) / (0.4 * 3);
	}


	//----------------------IR_CHG_COMP_STOP_Fall
	I2CWriteSameData(DEV_ADDR, 0x0F, 0x0E);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x9A);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x96);
	I2CWriteSameData(DEV_ADDR, 0x57, 0x11);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
	//		field[(WAKE_UP,1),(BUBO_MODE,0),(IR_COMP_TYPE,1)(IR_COMP,2),(VCLAMP,1),(D2A_MNT_TM_EN,1),(EN_ATEST0,1),(ATEST0_MUX,18),(EN_ATEST1,1),(ATEST1_MUX,1),(DIS_NTC_DETECTION_ANALOG,1),(EN_DTEST0,1),(DTEST0_MUX,26)]
	delay_ms(1);
	double ir_comp_chg_stop_rise[SITE_NUM] = { 0 };
	double ir_comp_chg_stop_fall[SITE_NUM] = { 0 };
	double ir_comp_chg_stop_hys[SITE_NUM] = { 0 };
	double v_ir_comp_chg_stop_rise[SITE_NUM] = { 0 };
	double v_ir_comp_chg_stop_fall[SITE_NUM] = { 0 };
	double v_ir_comp_chg_stop_hys[SITE_NUM] = { 0 };
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double ir_comp_r[200] = { 0.0 };
	double ir_comp_f[200] = { 0.0 };
	double Trig = 2.5;
	double Trig_Point[SITE_NUM] = { 0 };

	SetTrimGroup(0x5555);
	NTC_FOVI.Set(FV, 1.3, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(1500);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&ir_comp_r[0], sam, 1, 1.305, 1.355);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ir_comp_r_pattern", FV, FOVIe_2V, FOVIe_100MA, ir_comp_r, sam);
	NTC_FOVI.AwgSelect("ir_comp_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		v_ir_comp_chg_stop_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	NTC_FOVI.Set(FV, 1.335, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(1500);
	STSAWGCreateRampData(&ir_comp_f[0], sam, 1, 1.330, 1.275);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ir_comp_f_pattern", FV, FOVIe_2V, FOVIe_100MA, ir_comp_f, sam);
	NTC_FOVI.AwgSelect("ir_comp_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		v_ir_comp_chg_stop_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		v_ir_comp_chg_stop_hys[site] = v_ir_comp_chg_stop_rise[site] - v_ir_comp_chg_stop_fall[site];
		R_chg_stop_comp_fall[site] = (v_ir_comp_chg_stop_fall[site] - 1.2) / 0.1;
		R_chg_stop_comp_hys[site] = (v_ir_comp_chg_stop_hys[site]) / 0.1;
	}

	SetTrimGroup(0xAAAA);
	NTC_FOVI.Set(FV, 1.3, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(1500);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&ir_comp_r[0], sam, 1, 1.305, 1.355);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ir_comp_r_pattern", FV, FOVIe_2V, FOVIe_100MA, ir_comp_r, sam);
	NTC_FOVI.AwgSelect("ir_comp_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		v_ir_comp_chg_stop_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	NTC_FOVI.Set(FV, 1.335, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(1500);
	STSAWGCreateRampData(&ir_comp_f[0], sam, 1, 1.330, 1.275);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ir_comp_f_pattern", FV, FOVIe_2V, FOVIe_100MA, ir_comp_f, sam);
	NTC_FOVI.AwgSelect("ir_comp_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		v_ir_comp_chg_stop_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		v_ir_comp_chg_stop_hys[site] = v_ir_comp_chg_stop_rise[site] - v_ir_comp_chg_stop_fall[site];
		R_chg_stop_comp_fall[site] = (v_ir_comp_chg_stop_fall[site] - 1.2) / 0.1;
		R_chg_stop_comp_hys[site] = (v_ir_comp_chg_stop_hys[site]) / 0.1;
	}

	SetRecoverSite();

#if 0
	NTC_FOVI.Set(FV, 1.335, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(1500);
	STSAWGCreateRampData(&ir_comp_f[0], sam, 1, 1.330, 1.275);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ir_comp_f_pattern", FV, FOVIe_2V, FOVIe_100MA, ir_comp_f, sam);
	NTC_FOVI.AwgSelect("ir_comp_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
	bool Funstable = false;
	bool FSunstable[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		v_ir_comp_chg_stop_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		v_ir_comp_chg_stop_hys[site] = v_ir_comp_chg_stop_rise[site] - v_ir_comp_chg_stop_fall[site];
		R_chg_stop_comp_fall[site] = (v_ir_comp_chg_stop_fall[site] - 1.2) / 0.1;
		R_chg_stop_comp_hys[site] = (v_ir_comp_chg_stop_hys[site]) / 0.1;
		if (R_chg_stop_comp_hys[site] < 0.01)
		{
			Funstable = true;
			FSunstable[site] = true;
		}
	}
	if (Funstable)
	{
		NTC_FOVI.Set(FV, 1.3, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_us(1500);
		// Set a sinewave data array, the start address starts from 0, data size is 100.
		STSAWGCreateRampData(&ir_comp_r[0], sam, 1, 1.305, 1.355);
		NTC_FOVI.AwgClear();
		NTC_FOVI.AwgLoader("ir_comp_r_pattern", FV, FOVIe_2V, FOVIe_100MA, ir_comp_r, sam);
		NTC_FOVI.AwgSelect("ir_comp_r_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
		STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
		STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
		STSAWGRun();//Enable AWG and measurement synchronously
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
			v_ir_comp_chg_stop_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		}


		NTC_FOVI.Set(FV, 1.335, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_us(1500);
		STSAWGCreateRampData(&ir_comp_f[0], sam, 1, 1.33, 1.275);
		NTC_FOVI.AwgClear();
		NTC_FOVI.AwgLoader("ir_comp_f_pattern", FV, FOVIe_2V, FOVIe_100MA, ir_comp_f, sam);
		NTC_FOVI.AwgSelect("ir_comp_f_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
		STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
		STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
		STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
		FOR_EACH_VALID_SITE(site)
		{
			if (FSunstable[site])
			{
				Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
				v_ir_comp_chg_stop_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
				v_ir_comp_chg_stop_hys[site] = v_ir_comp_chg_stop_rise[site] - v_ir_comp_chg_stop_fall[site];
				R_chg_stop_comp_fall[site] = (v_ir_comp_chg_stop_fall[site] - 1.2) / 0.1;
				R_chg_stop_comp_hys[site] = (v_ir_comp_chg_stop_hys[site]) / 0.1;
			}
		}
	}
#endif

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(1);
		AMUX_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		NTC_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		IR_CHG_COMP1_DST->SetTestResult(site, 0, R_chg_comp1[site] * 1e3);//mohm
		IR_CHG_COMP2_DST->SetTestResult(site, 0, R_chg_comp2[site] * 1e3);//mohm
		VCLAMP_CHG1_DST->SetTestResult(site, 0, R_clamp_chg1[site] * 1e3);//mV
		VCLAMP_CHG2_DST->SetTestResult(site, 0, R_clamp_chg2[site] * 1e3);//mV

		IR_CHG_COMP_STOP_Rise->SetTestResult(site, 0, v_ir_comp_chg_stop_rise[site]);
		IR_CHG_COMP_STOP_Fall->SetTestResult(site, 0, v_ir_comp_chg_stop_fall[site]);
		IR_CHG_COMP_STOP_Hys->SetTestResult(site, 0, v_ir_comp_chg_stop_hys[site]);

		IR_CHG_COMP_STOP_Fall_DSA->SetTestResult(site, 0, R_chg_stop_comp_fall[site]);
		IR_CHG_COMP_STOP_Hys_SCM->SetTestResult(site, 0, R_chg_stop_comp_hys[site]*1e3);//mA
	}

    return 0;
}
 
DUT_API int IR_DISCHG_COMP(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IR_CABLE_COMP1_DSA = StsGetParam(funcindex, "IR_CABLE_COMP1_DSA");
    CParam *IR_CABLE_COMP2_DSA = StsGetParam(funcindex, "IR_CABLE_COMP2_DSA");
    CParam *IR_CABLE_COMP3_DSA = StsGetParam(funcindex, "IR_CABLE_COMP3_DSA");
    CParam *VCLAMP_DIS_CHG1_DSA = StsGetParam(funcindex, "VCLAMP_DIS_CHG1_DSA");
    CParam *VCLAMP_DIS_CHG2_DSA = StsGetParam(funcindex, "VCLAMP_DIS_CHG2_DSA");
    CParam *VCLAMP_DIS_CHG3_DSA = StsGetParam(funcindex, "VCLAMP_DIS_CHG3_DSA");
    CParam *IR_DISCHG_COMP_STOP_Rise = StsGetParam(funcindex, "IR_DISCHG_COMP_STOP_Rise");
    CParam *IR_DISCHG_COMP_STOP_Fall = StsGetParam(funcindex, "IR_DISCHG_COMP_STOP_Fall");
    CParam *IR_DISCHG_COMP_STOP_Hys = StsGetParam(funcindex, "IR_DISCHG_COMP_STOP_Hys");
    CParam *IR_DISCHG_COMP_STOP_Fall_DSA = StsGetParam(funcindex, "IR_DISCHG_COMP_STOP_Fall_DSA");
    CParam *IR_DISCHG_COMP_STOP_Hys_SCM = StsGetParam(funcindex, "IR_DISCHG_COMP_STOP_Hys_SCM");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double  Vmeas1[SITE_NUM] = { 0 };
	double  Vmeas2[SITE_NUM] = { 0 };
	double  Vmeas3[SITE_NUM] = { 0 };
	double  Vmeas4[SITE_NUM] = { 0 };
	double R_clamp_dischg1[SITE_NUM] = { 0 };
	double R_clamp_dischg2[SITE_NUM] = { 0 };
	double R_clamp_dischg3[SITE_NUM] = { 0 };
	double R_cable_comp1[SITE_NUM] = { 0 };
	double R_cable_comp2[SITE_NUM] = { 0 };
	double R_cable_comp3[SITE_NUM] = { 0 };
	double R_dischg_stop_comp_fall[SITE_NUM] = { 0 };
	double R_dischg_stop_comp_hys[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K43_INT_ACM, K58_INT_PU,K25_VCC_Cap, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x0F, 0x01);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x9A);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xB6);
	I2CWriteSameData(DEV_ADDR, 0x57, 0x11);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
	//		field[(WAKE_UP,1),(BUBO_MODE,1),(IR_COMP_TYPE,0)(IR_COMP,1),(VCLAMP,0),(D2A_MNT_TM_EN,1),(EN_ATEST0,1),(ATEST0_MUX,22),(EN_ATEST1,1),(ATEST1_MUX,1),(DIS_NTC_DETECTION_ANALOG,1),(EN_DTEST0,1),(DTEST0_MUX,26)]
	delay_ms(1);
	//============IR_CABLE_COMP1 && VCLAMP_DIS_CHG1
	NTC_FOVI.Set(FV, 3, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(5);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas1[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	NTC_FOVI.Set(FV, 2.4, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas2[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	}
	NTC_FOVI.Set(FV, 1.2, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(215, 10);

	FOR_EACH_VALID_SITE(site)
	{
		Vmeas3[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
		R_clamp_dischg1[site] = (Vmeas1[site] - Vmeas3[site]) / 0.1;
		R_cable_comp1[site] = (Vmeas2[site] - Vmeas3[site]) / (0.1 * 3);
	}



	//============IR_CHG_COMP2
	//I2CWriteSameData(DEV_ADDR, 0x9, 0x9);
	I2CWriteSameData(DEV_ADDR, 0x0F, 0x02);
	//I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	//I2CWriteSameData(DEV_ADDR, 0x55, 0x9A);
	//I2CWriteSameData(DEV_ADDR, 0x56, 0xB6);
	//I2CWriteSameData(DEV_ADDR, 0x57, 0x11);
	//I2CWriteSameData(DEV_ADDR, 0x65, 0x4);
	////		field[(WAKE_UP,1),(BUBO_MODE,1),(IR_COMP_TYPE,0)(IR_COMP,2),(VCLAMP,0),(D2A_MNT_TM_EN,1),(EN_ATEST0,1),(ATEST0_MUX,22),(EN_ATEST1,1),(ATEST1_MUX,1),(DIS_NTC_DETECTION_ANALOG,1),(EN_DTEST0,1),(DTEST0_MUX,26)]
	delay_ms(1);
	//------------IR_CABLE_COMP2
	NTC_FOVI.Set(FV, 1.8, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(5);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas2[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	//--------------------VCLAMP_DISCHG2
	I2CWriteSameData(DEV_ADDR, 0xF, 0x6); // (VCLAMP, 1)
	delay_ms(1);
	NTC_FOVI.Set(FV, 3, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas1[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	}
	FOR_EACH_VALID_SITE(site)
	{
		R_clamp_dischg2[site] = (Vmeas1[site] - Vmeas3[site]) / 0.1;
		R_cable_comp2[site] = (Vmeas2[site] - Vmeas3[site]) / (0.1 * 1.5);
	}


	//============IR_CHG_COMP3 
	//I2CWriteSameData(DEV_ADDR, 0x9, 0x9);
	I2CWriteSameData(DEV_ADDR, 0xF, 0x7);
	//I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	//I2CWriteSameData(DEV_ADDR, 0x55, 0x9A);
	//I2CWriteSameData(DEV_ADDR, 0x56, 0xB6);
	//I2CWriteSameData(DEV_ADDR, 0x57, 0x11);
	//I2CWriteSameData(DEV_ADDR, 0x65, 0x4);
	//		field[(WAKE_UP,1),(BUBO_MODE,1),(IR_COMP_TYPE,0)(IR_COMP,3),(VCLAMP,1),(D2A_MNT_TM_EN,1),(EN_ATEST0,1),(ATEST0_MUX,22),(EN_ATEST1,1),(ATEST1_MUX,1),(DIS_NTC_DETECTION_ANALOG,1),(EN_DTEST0,1),(DTEST0_MUX,26)]
	delay_ms(1);
	NTC_FOVI.Set(FV,3, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas1[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	}
	NTC_FOVI.Set(FV, 2.4, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas2[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	}
	FOR_EACH_VALID_SITE(site)
	{
		R_clamp_dischg3[site] = (Vmeas1[site] - Vmeas3[site]) / 0.1;
		R_cable_comp3[site] = (Vmeas2[site] - Vmeas3[site]) / (0.1 * 3);
	}

	double v_ir_comp_chg_stop_rise[SITE_NUM] = { 0 };
	double v_ir_comp_chg_stop_fall[SITE_NUM] = { 0 };
	double v_ir_comp_chg_stop_hys[SITE_NUM] = { 0 };
	double ir_comp_chg_stop_rise[SITE_NUM] = { 0 };
	double ir_comp_chg_stop_fall[SITE_NUM] = { 0 };
	double ir_comp_chg_stop_hys[SITE_NUM] = { 0 };
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double ir_comp_r[200] = { 0.0 };
	double ir_comp_f[200] = { 0.0 };
	double Trig = 2.5;
	double Trig_Point[SITE_NUM] = { 0 };
	SetTrimGroup(0x5555);
	delay_ms(1);
	NTC_FOVI.Set(FV, 1.4, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&ir_comp_r[0], sam, 1, 1.41, 1.50);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ir_comp_r_pattern", FV, FOVIe_2V, FOVIe_100MA, ir_comp_r, sam);
	NTC_FOVI.AwgSelect("ir_comp_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		v_ir_comp_chg_stop_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	NTC_FOVI.Set(FV, 1.5, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSAWGCreateRampData(&ir_comp_f[0], sam, 1, 1.46, 1.37);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ir_comp_f_pattern", FV, FOVIe_2V, FOVIe_100MA, ir_comp_f, sam);
	NTC_FOVI.AwgSelect("ir_comp_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		v_ir_comp_chg_stop_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		v_ir_comp_chg_stop_hys[site] = v_ir_comp_chg_stop_rise[site] - v_ir_comp_chg_stop_fall[site];
		R_dischg_stop_comp_fall[site] = (v_ir_comp_chg_stop_fall[site] - 1.2) / 0.4;
		R_dischg_stop_comp_hys[site] = (v_ir_comp_chg_stop_hys[site]) / 0.4;
	}

	SetTrimGroup(0xAAAA);
	delay_ms(1);
	NTC_FOVI.Set(FV, 1.4, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&ir_comp_r[0], sam, 1, 1.41, 1.50);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ir_comp_r_pattern", FV, FOVIe_2V, FOVIe_100MA, ir_comp_r, sam);
	NTC_FOVI.AwgSelect("ir_comp_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		v_ir_comp_chg_stop_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	NTC_FOVI.Set(FV, 1.5, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSAWGCreateRampData(&ir_comp_f[0], sam, 1, 1.46, 1.37);
	NTC_FOVI.AwgClear();
	NTC_FOVI.AwgLoader("ir_comp_f_pattern", FV, FOVIe_2V, FOVIe_100MA, ir_comp_f, sam);
	NTC_FOVI.AwgSelect("ir_comp_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously	FOR_EACH_VALID_SITE(site)
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		v_ir_comp_chg_stop_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		v_ir_comp_chg_stop_hys[site] = v_ir_comp_chg_stop_rise[site] - v_ir_comp_chg_stop_fall[site];
		R_dischg_stop_comp_fall[site] = (v_ir_comp_chg_stop_fall[site] - 1.2) / 0.4;
		R_dischg_stop_comp_hys[site] = (v_ir_comp_chg_stop_hys[site]) / 0.4;
	}

	SetRecoverSite();

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	delay_ms(1);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

	FOR_EACH_VALID_SITE(site)
	{
		IR_CABLE_COMP1_DSA->SetTestResult(site, 0, R_cable_comp1[site]*1e3);
		IR_CABLE_COMP2_DSA->SetTestResult(site, 0, R_cable_comp2[site] * 1e3);
		IR_CABLE_COMP3_DSA->SetTestResult(site, 0, R_cable_comp3[site] * 1e3);
		VCLAMP_DIS_CHG1_DSA->SetTestResult(site, 0, R_clamp_dischg1[site] * 1e3);
		VCLAMP_DIS_CHG2_DSA->SetTestResult(site, 0, R_clamp_dischg2[site]*1e3);
		VCLAMP_DIS_CHG3_DSA->SetTestResult(site, 0, R_clamp_dischg3[site] * 1e3);

		IR_DISCHG_COMP_STOP_Rise->SetTestResult(site, 0, v_ir_comp_chg_stop_rise[site]);
		IR_DISCHG_COMP_STOP_Fall->SetTestResult(site, 0, v_ir_comp_chg_stop_fall[site]);
		IR_DISCHG_COMP_STOP_Hys->SetTestResult(site, 0, v_ir_comp_chg_stop_hys[site]);

		IR_DISCHG_COMP_STOP_Fall_DSA->SetTestResult(site, 0, R_dischg_stop_comp_fall[site] * 1e3);
		IR_DISCHG_COMP_STOP_Hys_SCM->SetTestResult(site, 0, R_dischg_stop_comp_hys[site] * 1e3);
	}



    return 0;
}
  
DUT_API int ACDRV_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *ACDRV1_ON_VOL_DSA = StsGetParam(funcindex, "ACDRV1_ON_VOL_DSA");
    CParam *ACDRV2_ON_VOL_DSA = StsGetParam(funcindex, "ACDRV2_ON_VOL_DSA");
    CParam *ACDRV3_ON_VOL_DSA = StsGetParam(funcindex, "ACDRV3_ON_VOL_DSA");
    CParam *ACDRV1_ON_HCLAMP = StsGetParam(funcindex, "ACDRV1_ON_HCLAMP");
    CParam *ACDRV2_ON_HCLAMP = StsGetParam(funcindex, "ACDRV2_ON_HCLAMP");
    CParam *ACDRV3_ON_HCLAMP = StsGetParam(funcindex, "ACDRV3_ON_HCLAMP");
    CParam *ACDRV1_ON_CLAMP_DSA = StsGetParam(funcindex, "ACDRV1_ON_CLAMP_DSA");
    CParam *ACDRV2_ON_CLAMP_DSA = StsGetParam(funcindex, "ACDRV2_ON_CLAMP_DSA");
    CParam *ACDRV3_ON_CLAMP_DSA = StsGetParam(funcindex, "ACDRV3_ON_CLAMP_DSA");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	double acdrv1_on_vol[SITE_NUM] = { 0 };
	double acdrv2_on_vol[SITE_NUM] = { 0 };
	double acdrv3_on_vol[SITE_NUM] = { 0 };
	double acdrv1_on_Hclamp[SITE_NUM] = { 0 };
	double acdrv2_on_Hclamp[SITE_NUM] = { 0 };
	double acdrv3_on_Hclamp[SITE_NUM] = { 0 };
	double acdrv1_on_Lclamp[SITE_NUM] = { 0 };
	double acdrv2_on_Lclamp[SITE_NUM] = { 0 };
	double acdrv3_on_Lclamp[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K37_VAC_Cap,K25_VCC_Cap, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 4.5, ACM200_20V, ACM200_10MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 10, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	delay_ms(3);
	entertestmode();
	//------ACDRV1
	I2CWriteSameData(DEV_ADDR, 0x08, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43); //		field[(WAKE_UP,1),(AC1_GATE_ON,1)]
	delay_ms(1);
	VAC123_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	ACDRV123_ACM.Set(FV, 10, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FI, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	delay_ms(2);
	ACDRV123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		acdrv1_on_vol[site] = ACDRV123_ACM.GetMeasResult(site, MVRET);
	}

	VAC123_ACM.Set(FV, 12, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 17.2, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	ACDRV123_ACM.Set(FV, 17.2, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FI, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	delay_ms(2);
	ACDRV123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		acdrv1_on_Hclamp[site] = ACDRV123_ACM.GetMeasResult(site, MVRET);
	}
	I2CWriteSameData(DEV_ADDR, 0x08, 0x00); //		field[(AC1_GATE_ON,0)]
	ACDRV123_ACM.Set(FV, 4, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	ACDRV123_ACM.Set(FV, 4, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FI, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	delay_ms(1);
	ACDRV123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		acdrv1_on_Lclamp[site] = ACDRV123_ACM.GetMeasResult(site, MVRET);
	}
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//need off to avoid spike

	//------ACDRV2
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K37_VAC_Cap, K36_SHARE2_VAC, K23_SHARE2_ACDRV, K25_VCC_Cap, -1);
	delay_ms(3);
	I2CWriteSameData(DEV_ADDR, 0x08, 0x02);//field[(WAKE_UP,1),(AC2_GATE_ON,1)]
	delay_ms(1);
	VAC123_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	ACDRV123_ACM.Set(FV, 10, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FI, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	delay_ms(2);
	ACDRV123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		acdrv2_on_vol[site] = ACDRV123_ACM.GetMeasResult(site, MVRET);
	}

	VAC123_ACM.Set(FV, 12, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 17.2, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	ACDRV123_ACM.Set(FV, 17.2, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FI, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	delay_ms(2);
	ACDRV123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		acdrv2_on_Hclamp[site] = ACDRV123_ACM.GetMeasResult(site, MVRET);
	}
	I2CWriteSameData(DEV_ADDR, 0x08, 0x00); //		field[(AC1_GATE_ON,0)]
	ACDRV123_ACM.Set(FV, 4, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	ACDRV123_ACM.Set(FV, 4, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FI, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	delay_ms(1);
	ACDRV123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		acdrv2_on_Lclamp[site] = ACDRV123_ACM.GetMeasResult(site, MVRET);
	}
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);                                                    
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//need off to avoid spike

	//------ACDRV3
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K37_VAC_Cap, K35_SHARE1_VAC, K22_SHARE1_ACDRV, K25_VCC_Cap, -1);
	delay_ms(3);
	VAC123_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);                                                          
	I2CWriteSameData(DEV_ADDR, 0x08, 0x01);//field[(WAKE_UP,1),(AC3_GATE_ON,1)]
	delay_ms(1);
	ACDRV123_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	ACDRV123_ACM.Set(FV, 10, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FI, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	delay_ms(2);
	ACDRV123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		acdrv3_on_vol[site] = ACDRV123_ACM.GetMeasResult(site, MVRET);
	}

	VAC123_ACM.Set(FV, 12, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 17.2, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	ACDRV123_ACM.Set(FV, 17.2, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FI, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	delay_ms(2);
	ACDRV123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		acdrv3_on_Hclamp[site] = ACDRV123_ACM.GetMeasResult(site, MVRET);
	}
	I2CWriteSameData(DEV_ADDR, 0x08, 0x00); //		field[(AC1_GATE_ON,0)]
	ACDRV123_ACM.Set(FV, 4, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	ACDRV123_ACM.Set(FV, 4, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FI, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	delay_ms(1);
	ACDRV123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		acdrv3_on_Lclamp[site] = ACDRV123_ACM.GetMeasResult(site, MVRET);
	}
	if (!TTR)
	{
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_20V, ACM200_10MA, ACM200_RELAY_ON);
		delay_ms(1);
		VAC123_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_20V, ACM200_10MA, ACM200_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		ACDRV1_ON_VOL_DSA->SetTestResult(site, 0, acdrv1_on_vol[site]);
		ACDRV2_ON_VOL_DSA->SetTestResult(site, 0, acdrv2_on_vol[site]);
		ACDRV3_ON_VOL_DSA->SetTestResult(site, 0, acdrv3_on_vol[site]);
		ACDRV1_ON_HCLAMP->SetTestResult(site, 0, acdrv1_on_Hclamp[site]);
		ACDRV2_ON_HCLAMP->SetTestResult(site, 0, acdrv2_on_Hclamp[site]);
		ACDRV3_ON_HCLAMP->SetTestResult(site, 0, acdrv3_on_Hclamp[site]);
		ACDRV1_ON_CLAMP_DSA->SetTestResult(site, 0, acdrv1_on_Lclamp[site]-12);
		ACDRV2_ON_CLAMP_DSA->SetTestResult(site, 0, acdrv2_on_Lclamp[site]-12);
		ACDRV3_ON_CLAMP_DSA->SetTestResult(site, 0, acdrv3_on_Lclamp[site]-12);
	}

    return 0;
}
 
DUT_API int ACDRV_TIME(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *ACDRV_SOFTSTART_DSA = StsGetParam(funcindex, "ACDRV_SOFTSTART_DSA");
    CParam *ACDRV_SHUTDN_DSM = StsGetParam(funcindex, "ACDRV_SHUTDN_DSM");
    CParam *ACDRV_SS_VTH_DSA = StsGetParam(funcindex, "ACDRV_SS_VTH_DSA");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double isoftstart[SITE_NUM] = { 0 };
	double tsoftstart[SITE_NUM] = { 0 };
	double tshutdown[SITE_NUM] = { 0 };
	double Iacdrv[SITE_NUM] = { 0 };

	//QTMU_GP.Connect(QTMUe_RELAY_CHB);
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K37_VAC_Cap, K22_SHARE1_ACDRV,  K36_SHARE2_VAC, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x08, 0x07); //		(AC3_GATE_ON,1)]
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43); //		field[(WAKE_UP,1),
	delay_ms(1);

	ACDRV123_ACM.Set(FV,0, ACM200_20V, ACM200_100UA, ACM200_RELAY_ON);
	delay_us(500);
	ACDRV123_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		isoftstart[site] = -1*ACDRV123_ACM.GetMeasResult(site, MIRET);//  3.6~4.4uA
		tsoftstart[site] = 4e-6 * 2.9 / isoftstart[site];//ms  约2.9ms
	}
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);


	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K37_VAC_Cap, K22_SHARE1_ACDRV, K35_SHARE1_VAC, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, V_TYP_VBUS, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, V_TYP_VBUS+2, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x08, 0x07);//
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x08, 0x00);//  close ACDRV
	delay_ms(1);
	ACDRV123_ACM.MeasureVI(50, 5);
	ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_100MA, ACM200_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Iacdrv[site] = ACDRV123_ACM.GetMeasResult(site, MIRET);
		tshutdown[site] = 1e6*10*4e-9 / Iacdrv[site];//uS    10V * 4nF = t * current
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FI, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	}




	double vbus_on_addrv_ss[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, /*K37_VAC_Cap,*/K25_VCC_Cap,-1);// canot add VAC cap to aviod ACDRV voltage climb high in the start
	delay_ms(3);
	VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 4.2, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	ACDRV123_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x8, 0x07);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x60, 0x20);
	//		field[(WAKE_UP,1),(AC1_GATE_SS_EN,1),(AC1_GATE_ON,1)]
	delay_ms(10);// cannnot save for stable consider

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double acdrv_ss_vth_r[200] = { 0.0 };
	double Trig = 0.1;// ACDRV 从0V到4.0V
	double Trig_Point[SITE_NUM] = { 0 };
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&acdrv_ss_vth_r[0], sam, 1, 4.28, 4.67);//  
	VBUS_FOVI.AwgLoader("acdrv_ss_vth_r_pattern", FV, FOVIe_10V, FOVIe_100MA, acdrv_ss_vth_r, sam);
	VBUS_FOVI.AwgSelect("acdrv_ss_vth_r_pattern", 0, sam - 1, sam - 1, interval);
	ACDRV123_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	ACDRV123_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBUS_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);

	VBUS_FOVI.Set(FV, 4.2, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	ACDRV123_ACM.Set(FI, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
	delay_us(2000);// need wait over 1ms for acdrv voltage fall to zero mv
	//ACDRV123_ACM.MeasureVI(400, 50);

	STSEnableAWG(&VBUS_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBUS_FOVI, &ACDRV123_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously

	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = ACDRV123_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbus_on_addrv_ss[site] = VBUS_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);

		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);

		VBUS_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	}


	FOR_EACH_VALID_SITE(site)
	{
		ACDRV_SOFTSTART_DSA->SetTestResult(site, 0, tsoftstart[site]);
		ACDRV_SHUTDN_DSM->SetTestResult(site, 0, tshutdown[site]);
		ACDRV_SS_VTH_DSA->SetTestResult(site, 0, vbus_on_addrv_ss[site]);
	}

    return 0;
}
 
DUT_API int ACDRV_INFRA(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VCP_TEST = StsGetParam(funcindex, "VCP_TEST");
    CParam *ACDRV_BIAS_1UA = StsGetParam(funcindex, "ACDRV_BIAS_1UA");
    CParam *ACDRV_VDD_IQ = StsGetParam(funcindex, "ACDRV_VDD_IQ");
    CParam *ACDRV_VBUS_IQ = StsGetParam(funcindex, "ACDRV_VBUS_IQ");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	double vcp_test[SITE_NUM] = {0};
	double acdrv_bias_1uA[SITE_NUM] = { 0 };
	double acdrv_vdd_iq_pre[SITE_NUM] = { 0 };
	double acdrv_vbus_iq[SITE_NUM] = { 0 };
	double acdrv_vdd_iq_pos[SITE_NUM] = { 0 };
	double acdrv_vdd_iq_delta[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x08, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 1, 130); //		field[(WAKE_UP,1),(AC1_GATE_ON,1),(EN_ATEST0,1),(ATEST0_MUX,16)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		acdrv_bias_1uA[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
	}


	AMUX_FOVI.Set(FV, 1.2, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x8, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x7A);//		field[(WAKE_UP,1),(AC1_GATE_ON,1),(EN_ATEST0,1),(ATEST0_MUX,15)]
	AMUX_FOVI.Set(FV, 1.2, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		vcp_test[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);

	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);


	cbite.SetOn(K1_PGND2AGND,-1);
	delay_ms(3);
	VBUS_FOVI.Set(FV, 9, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	//FPVI.Set(FV, 0.01, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
	VAC123_ACM.Set(FV, 9, ACM200_20V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 4.8, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x10,0x43);//		field[(WAKE_UP,1)]
	I2CWriteSameData(DEV_ADDR, 0x08, 0x07);//		field[(AC1_GATE_ON,1),(AC2_GATE_ON,1),(AC3_GATE_ON,1)]
	delay_ms(9);// cannot remove for current flow down
	Retest_current_unstable_with_time_out(VBUS_FOVI, acdrv_vbus_iq, spec.get_low_limit("ACDRV_VBUS_IQ"), spec.get_high_limit("ACDRV_VBUS_IQ"), 1, 12, MEAS_UA);
	//delay_ms(10);
	//VBUS_FOVI.MeasureVI(50, 5);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	acdrv_vbus_iq[site] = VBUS_FOVI.GetMeasResult(site, MIRET)*1e6;
	//}


	//I2CWriteSameData(DEV_ADDR, 0x08, 0x00);//		field[(AC1_GATE_ON,0),(AC2_GATE_ON,0),(AC3_GATE_ON,0)]
	//delay_ms(2);
	//VCC_ACM.MeasureVI(50, 5);
	//VBUS_FOVI.MeasureVI(500, 50);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	acdrv_vdd_iq_pre[site] = VCC_ACM.GetMeasResult(site, MIRET)*1e6;
	//	acdrv_vbus_iq_pre[site] = VBUS_FOVI.GetMeasResult(site, MIRET)*1e6;
	//	//acdrv_vdd_iq_delta[site] = acdrv_vdd_iq_pos[site] - acdrv_vdd_iq_pre[site];
	//	//acdrv_vbus_iq_delta[site] = acdrv_vbus_iq_pos[site] - acdrv_vbus_iq_pre[site];
	//	acdrv_vdd_iq_delta[site] = acdrv_vdd_iq_pos[site];
	//		acdrv_vbus_iq_delta[site] = acdrv_vbus_iq_pos[site];
	//}

	VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(1);
	VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

	FOR_EACH_VALID_SITE(site)
	{
		VCP_TEST->SetTestResult(site, 0, vcp_test[site]);
		ACDRV_BIAS_1UA->SetTestResult(site, 0, acdrv_bias_1uA[site]);
		//ACDRV_VDD_IQ->SetTestResult(site, 0, acdrv_vdd_iq_delta[site]);
		ACDRV_VBUS_IQ->SetTestResult(site, 0, acdrv_vbus_iq[site]);
	}

    return 0;
}
 
DUT_API int RDSON_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *HSFET_RDSON = StsGetParam(funcindex, "HSFET_RDSON");
    CParam *LSFET_RDSON = StsGetParam(funcindex, "LSFET_RDSON");
    CParam *BST_VOL_DROP = StsGetParam(funcindex, "BST_VOL_DROP");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
 	double Vmeas[SITE_NUM] = { 0 };
 	double Imeas[SITE_NUM] = { 0 };
 	double hsfet_rdson[SITE_NUM] = { 0 };
 	double lsfet_rdson[SITE_NUM] = { 0 };
 	double vbtst_drop[SITE_NUM] = { 0 };

	//------LSZCD 阈值点设置在电流减小到0mA 附近位置，需要关闭下管开启上管防止效率损失，一般是芯片内部SW-->PGND 电流逐步降低到0mA 附近但是大于0mA

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double bubo_zcd_noc[200] = { 0.0 };
	double Trig = 2.5;
	int Trig_Point[SITE_NUM] = { 0 };
	SW_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
	cbite.SetOn(K17_BUSH_SW, K33_BUSL_PGND, K30_VBAT_Cap, K32_PMID_Cap, K28_VDRV_Cap,K25_VCC_Cap, K18_BST_SW_Cap,K43_INT_ACM,K58_INT_PU,-1);
	delay_ms(3);
	VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x01);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_LSON,1),(BUBO_MODE,0)]
	//I2C_READ_BYTE(DEV_ADDR, 0x61, data_read);
    delay_ms(1);
	double curr = -0.035;
	//curr = 0;
	//---------------BTST  Voltage drop
	BTST_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FI, curr, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	BTST_ACM.MeasureVI(50, 5);
	VDRV_AMP_ACM.MeasureVI(50, 5);
	BTST_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		vbtst_drop[site] = (VDRV_AMP_ACM.GetMeasResult(site, MVRET) - BTST_ACM.GetMeasResult(site, MVRET))*1e3;
	}
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
 	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
 	FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
 	delay_ms(1);
 	FPVI.MeasureVI(50, 5);
 	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
 	FOR_EACH_VALID_SITE(site)
 	{
 		Vmeas[site] = FPVI.GetMeasResult(site, MVRET);
 		Imeas[site] = abs(FPVI.GetMeasResult(site, MIRET));
 		lsfet_rdson[site] = (Vmeas[site] / Imeas[site])*1e3;//mohm
 	}

#if 0
	//---------------BUCK_LS_ZCD
	//I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
   //I2CWriteSameData(DEV_ADDR, 0x59, 0x01);
	//I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_LSON,1),(BUBO_MODE,0)]
	I2CWriteSameData(DEV_ADDR, 0x55, 0xB0);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);	//		field[(D2A_BUBO_TM_DIS_CLK,1),(EN_DTEST0,1),(DTEST0_MUX,48)]
	delay_ms(1);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0.2, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&bubo_zcd_noc[0], sam, 1, 0.1, -0.5);// 电流值为正表明SW-->LSFET-->PGND, 电流为负，表明PGND-->LSFET-->SW, 目标这里的120mA
	FPVI.AwgClear();
	FPVI.AwgLoader("bubo_zcd_noc_pattern", FI, FPVIe_1V, FPVIe_1A, bubo_zcd_noc, sam);
	FPVI.AwgSelect("bubo_zcd_noc_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		if (Trig_Point[site] < 0)
		{
			delay_us(1);
		}
		buck_ls_zcd[site] = -1 * FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site])*1e3; //Read the voltage value on trigger position, mA,  PGND---->SW为正，与电感店里方向一致。
	}
#endif
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//avoid spike



	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(1);
		PMID_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	}


	cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K31_BUSL_PMID, K17_BUSH_SW, K28_VDRV_Cap, K25_VCC_Cap, K43_INT_ACM,K58_INT_PU,-1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
	delay_ms(5);//add for special lot 
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x02);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);	//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_HSON,1)]
	delay_ms(1);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, -2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vmeas[site] = FPVI.GetMeasResult(site, MVRET);
		Imeas[site] = abs(FPVI.GetMeasResult(site, MIRET));
		hsfet_rdson[site] =-1* (Vmeas[site] / Imeas[site])*1e3;//mohm
	}

#if 0
	//-------------------BOOST HS_ZCD
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x02);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xB1);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//D2A_BUBO_DIS_CLK=0
	//		field[(D2A_BUBO_TM_DIS_CLK,1),(EN_DTEST0,1),(DTEST0_MUX,49)]
	I2CWriteSameData(DEV_ADDR, 0x6D, 0x80);
	delay_ms(3);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	STSAWGCreateRampData(&bubo_zcd_noc[0], sam, 1, 0, 0.9);//SW ---->PMID
	FPVI.AwgClear();
	FPVI.AwgLoader("bubo_zcd_noc_pattern", FI, FPVIe_1V, FPVIe_1A, bubo_zcd_noc, sam);
	FPVI.AwgSelect("bubo_zcd_noc_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		boost_hs_zcd[site] = FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site])*1e3; //Read the voltage value on trigger position, mA
	}
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
#endif
	//---------------BOOST_NOC
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x02);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xB1);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//D2A_BUBO_DIS_CLK=0
	//		field[(D2A_BUBO_TM_DIS_CLK,1),(EN_DTEST0,1),(DTEST0_MUX,49)]
	I2CWriteSameData(DEV_ADDR, 0x6D, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x09, 0x19);
	delay_ms(3);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	STSAWGCreateRampData(&bubo_zcd_noc[0], sam, 1, -1.82, -3.38);//PMID--->SW
	FPVI.AwgClear();
	FPVI.AwgLoader("bubo_zcd_noc_pattern", FI, FPVIe_1V, FPVIe_10A, bubo_zcd_noc, sam);
	FPVI.AwgSelect("bubo_zcd_noc_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	FPVI.Set(FI, -1.8, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_ms(2);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		boost_hs_noc[site] = FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]); //Read the voltage value on trigger position
		check_awg_trigger_point(Trig_Point, sam, boost_hs_noc,site);// add for AWG trigger check
	}
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);

	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(1);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);

 	FOR_EACH_VALID_SITE(site)
 	{
		HSFET_RDSON->SetTestResult(site, 0, hsfet_rdson[site]);
		LSFET_RDSON->SetTestResult(site, 0, lsfet_rdson[site]);
		BST_VOL_DROP->SetTestResult(site, 0, vbtst_drop[site]);
 	}

	return 0;
}
 
DUT_API int ZCD_NOC_Test(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BUCK_LS_ZCD = StsGetParam(funcindex, "BUCK_LS_ZCD");
    CParam *BOOST_HS_ZCD = StsGetParam(funcindex, "BOOST_HS_ZCD");
    CParam *BOOST_HS_NOC = StsGetParam(funcindex, "BOOST_HS_NOC");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	if (!TTR)
	{
		//------LSZCD 阈值点设置在电流减小到0mA 附近位置，需要关闭下管开启上管防止效率损失，一般是芯片内部SW-->PGND 电流逐步降低到0mA 附近但是大于0mA
		double buck_ls_zcd[SITE_NUM] = { 0 };
		double boost_hs_zcd[SITE_NUM] = { 0 };
		double boost_hs_noc[SITE_NUM] = { 0 };

		int sam = 200;			//AWG waveform data length
		int interval = 20;		//AWGdata interval time, unit is uS
		double bubo_zcd_noc[200] = { 0.0 };
		double Trig = 2.5;
		int Trig_Point[SITE_NUM] = { 0 };

		//---------------BUCK_LS_ZCD
		cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K33_BUSL_PGND, K17_BUSH_SW, K28_VDRV_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		delay_ms(5);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x01);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_LSON,1),(BUBO_MODE,0)]
		I2CWriteSameData(DEV_ADDR, 0x55, 0xB0);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x20);	//		field[(D2A_BUBO_TM_DIS_CLK,1),(EN_DTEST0,1),(DTEST0_MUX,48)]
		delay_ms(2);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		FPVI.Set(FI, 0.26, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(2);
		STSAWGCreateRampData(&bubo_zcd_noc[0], sam, 1, 0.25, -0.5);// PGND--->SW
		FPVI.AwgClear();
		FPVI.AwgLoader("bubo_zcd_noc_pattern", FI, FPVIe_1V, FPVIe_1A, bubo_zcd_noc, sam);
		FPVI.AwgSelect("bubo_zcd_noc_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

		STSEnableAWG(&FPVI);
		STSEnableMeas(&FPVI, &SDA_INT_ACM);
		STSAWGRun();
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
			buck_ls_zcd[site] = -1 * FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site])*1e3; //Read the voltage value on trigger position, mA,  PGND---->SW为正，与电感店里方向一致。
			check_awg_trigger_point(Trig_Point, sam, buck_ls_zcd,site);// add for AWG trigger check
		}


		//---------------BOOST_HS_ZCD
		cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K31_BUSL_PMID, K17_BUSH_SW, K28_VDRV_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap, -1);
		delay_ms(3);
		//VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
		//VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(5);
		//entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		//I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x02);
		//I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_HSON,1),(BUBO_MODE,1)]
		I2CWriteSameData(DEV_ADDR, 0x55, 0xB1);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//D2A_BUBO_DIS_CLK=0
		//		field[(D2A_BUBO_TM_DIS_CLK,1),(EN_DTEST0,1),(DTEST0_MUX,49)]
		I2CWriteSameData(DEV_ADDR, 0x6D, 0x80);
		delay_ms(3);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

		STSAWGCreateRampData(&bubo_zcd_noc[0], sam, 1, -0.1, 0.65);//SW ---->PMID
		FPVI.AwgClear();
		FPVI.AwgLoader("bubo_zcd_noc_pattern", FI, FPVIe_1V, FPVIe_1A, bubo_zcd_noc, sam);
		FPVI.AwgSelect("bubo_zcd_noc_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
		FPVI.Set(FI, -0.2, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(2);
		STSEnableAWG(&FPVI);
		STSEnableMeas(&FPVI, &SDA_INT_ACM);
		STSAWGRun();
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
			boost_hs_zcd[site] = FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site])*1e3; //Read the voltage value on trigger position, mA
		}

		//---------------BOOST_NOC
		I2CWriteSameData(DEV_ADDR, 0x6D, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x09, 0x19);
		//I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		//I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//D2A_BUBO_DIS_CLK=0
		//I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,1),(FPWM_EN,1)]
		//I2CWriteSameData(DEV_ADDR, 0x55, 0xB1);//		field[(EN_DTEST0,1),(DTEST0_MUX,49)]
		//I2CWriteSameData(DEV_ADDR, 0x59, 0x02);//		field[(D2A_BUBO_TM_HSON,1)]
		delay_ms(3);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		STSAWGCreateRampData(&bubo_zcd_noc[0], sam, 1, -2.0, -3.2);//PMID--->SW
		FPVI.AwgClear();
		FPVI.AwgLoader("bubo_zcd_noc_pattern", FI, FPVIe_1V, FPVIe_10A, bubo_zcd_noc, sam);
		FPVI.AwgSelect("bubo_zcd_noc_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
		FPVI.Set(FI, -2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		delay_ms(2);
		STSEnableAWG(&FPVI);
		STSEnableMeas(&FPVI, &SDA_INT_ACM);
		STSAWGRun();
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
			boost_hs_noc[site] = FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]); //Read the voltage value on trigger position
		}
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);


		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		FOR_EACH_VALID_SITE(site)
		{
			BUCK_LS_ZCD->SetTestResult(site, 0, buck_ls_zcd[site]);
			BOOST_HS_ZCD->SetTestResult(site, 0, boost_hs_zcd[site]);
			BOOST_HS_NOC->SetTestResult(site, 0, boost_hs_noc[site]);
		}
	}
	else
	{	
		FOR_EACH_VALID_SITE(site)
		{
			BUCK_LS_ZCD->SetTestResult(site, 0, Buck_lsfet_zcd[site]*1e3);//mA
			BOOST_HS_ZCD->SetTestResult(site, 0, Boost_hsfet_zcd[site]*1e3);//mA
			BOOST_HS_NOC->SetTestResult(site, 0, boost_hs_noc[site]);
		}
	}

    return 0;
}
 
DUT_API int STRESS_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *STRESS_HS_GATE_Pre = StsGetParam(funcindex, "STRESS_HS_GATE_Pre");
    CParam *STRESS_HS_GATE_Post = StsGetParam(funcindex, "STRESS_HS_GATE_Post");
    CParam *STRESS_HS_GATE_Delta = StsGetParam(funcindex, "STRESS_HS_GATE_Delta");
    CParam *STRESS_LS_GATE_Pre = StsGetParam(funcindex, "STRESS_LS_GATE_Pre");
    CParam *STRESS_LS_GATE_Post = StsGetParam(funcindex, "STRESS_LS_GATE_Post");
    CParam *STRESS_LS_GATE_Delta = StsGetParam(funcindex, "STRESS_LS_GATE_Delta");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn )
	{
		double stress_hs_pre[SITE_NUM] = { 0 };
		double stress_hs_pos[SITE_NUM] = { 0 };
		double stress_hs_delta[SITE_NUM] = { 0 };
		double stress_ls_pre[SITE_NUM] = { 0 };
		double stress_ls_pos[SITE_NUM] = { 0 };
		double stress_ls_delta[SITE_NUM] = { 0 };
		//clear_resource();

		cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K18_BST_SW_Cap, K17_BUSH_SW, K38_BUSL_BTST, -1);
		delay_ms(3);
		FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		//BTST_ACM.Set(FV, 3, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		//SW_ACM.Set(FV, 3, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		delay_us(500);
		//BTST_ACM.Set(FV, 13, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x02);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);	//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_HSON,1)]
		delay_us(1000);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x02);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);	//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_HSON,1)]
		delay_ms(2);
		FPVI.Set(FV, -5, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
		Retest_current_unstable_with_time_out(FPVI, stress_hs_pre, spec.get_low_limit("STRESS_HS_GATE_Pre"), spec.get_high_limit("STRESS_HS_GATE_Pre"), 1, 10, MEAS_UA);

		FPVI.Set(FV, -8, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
		delay_ms(100);
		FPVI.Set(FV, -5, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
		Retest_current_unstable_with_time_out(FPVI, stress_hs_pos, spec.get_low_limit("STRESS_HS_GATE_Post"), spec.get_high_limit("STRESS_HS_GATE_Post"), 1, 10, MEAS_UA);

		FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
		//delay_ms(5);
		//FOR_EACH_VALID_SITE(site)
		//{
		//	stress_hs_pos[site] = -1*stress_hs_pos[site];
		//	stress_hs_pre[site] = -1*stress_hs_pos[site];
		//	stress_hs_delta[site] = stress_hs_pos[site] - stress_hs_pre[site];//uA
		//}

		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(3);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x00);	//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_HSON,1)]
		delay_ms(2);
		PMID_FOVI.Set(FV, 8, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x28);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x01);//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,0),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_DIS_BST_CHARGE,1),(D2A_BUBO_TM_LSON,1)]
		delay_ms(1);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		Retest_current_unstable_with_time_out(VDRV_AMP_ACM, stress_ls_pre, spec.get_low_limit("STRESS_LS_GATE_Pre"), spec.get_high_limit("STRESS_LS_GATE_Pre"), 1, 10, MEAS_UA);

		VDRV_AMP_ACM.Set(FV, 8, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);// high stress
		delay_ms(100);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON, 0.5);
		Retest_current_unstable_with_time_out(VDRV_AMP_ACM, stress_ls_pos, spec.get_low_limit("STRESS_LS_GATE_Post"), spec.get_high_limit("STRESS_LS_GATE_Post"), 1, 10, MEAS_UA);

		FOR_EACH_VALID_SITE(site)
		{
			stress_hs_pos[site] = -1 * stress_hs_pos[site];
			stress_hs_pre[site] = -1 * stress_hs_pre[site];
			stress_hs_delta[site] = stress_hs_pos[site] - stress_hs_pre[site];//uA
			stress_ls_delta[site] = stress_ls_pos[site] - stress_ls_pre[site];//uA
		}


		if (!TTR)
		{
			VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
			BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
			VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
			SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
			PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
			delay_us(1000);
			PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
			BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
			VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
			VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
			SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		}
		else
		{
			//STSSetTimeCheck(1);
			VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
			VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
			BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
			VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
			SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
			PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);

			PMID_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
			BTST_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
			VDRV_AMP_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
			SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
			//double testmiea = STSGetTimeElapsed(1);
			delay_us(1);
		}


		FOR_EACH_VALID_SITE(site)
		{
			STRESS_HS_GATE_Pre->SetTestResult(site, 0, stress_hs_pre[site]);
			STRESS_HS_GATE_Post->SetTestResult(site, 0, stress_hs_pos[site]);
			STRESS_HS_GATE_Delta->SetTestResult(site, 0, stress_hs_delta[site] * 1e3);//nA
			STRESS_LS_GATE_Pre->SetTestResult(site, 0, stress_ls_pre[site]);
			STRESS_LS_GATE_Post->SetTestResult(site, 0, stress_ls_pos[site]);
			STRESS_LS_GATE_Delta->SetTestResult(site, 0, stress_ls_delta[site] * 1e3);//nA
		}
	}
	return 0;
}
 
DUT_API int VC_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VC_CLAMP_LOW = StsGetParam(funcindex, "VC_CLAMP_LOW");
    CParam *VC_OFFSET_Rise = StsGetParam(funcindex, "VC_OFFSET_Rise");
    CParam *VC_OFFSET_Fall = StsGetParam(funcindex, "VC_OFFSET_Fall");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	double vc_clamp_low[SITE_NUM] = { 0 };
	double vc_offset_rise[SITE_NUM] = { 0 };
	double vc_offset_fall[SITE_NUM] = { 0 };

	cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
	//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(IBAT_LIMIT,7),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(DIS_NTC_DETECTION_ANALOG,1)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);//		field[(EN_ATEST1,1),(D2A_BUBO_ATEST1,5)]
	//delay_ms(1);
	//NTC_FOVI.MeasureVI(100, 5);
	Retest_voltage_unstable_with_time_out(NTC_FOVI, vc_clamp_low, spec.get_low_limit("VC_CLAMP_LOW"), spec.get_high_limit("VC_CLAMP_LOW"),1, 20, MEAS_V);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	vc_clamp_low[site]=NTC_FOVI.GetMeasResult(site, MVRET);
	//}

	NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 2, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);

	I2CWriteSameData(DEV_ADDR, 0x0B, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(DIS_NTC_DETECTION_ANALOG,1)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x61);//		field[(EN_ATEST1,1),(D2A_BUBO_ATEST1,6),(EN_ATEST0,1),(D2A_BUBO_ATEST0,1)]
	delay_ms(1);

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double vc_offset_r[200] = { 0.0 };
	double vc_offset_f[200] = { 0.0 };
	double Trig = -100e-9;
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vc_offset_r[0], sam, 1, 1.29, 1.51);//  PMID-->SW
	NTC_FOVI.AwgLoader("vc_offset_r_pattern", FV, FOVIe_2V, FOVIe_100MA, vc_offset_r, sam);
	NTC_FOVI.AwgSelect("vc_offset_r_pattern", 0, sam - 1, sam - 1, interval);
	AMUX_FOVI.SetMeasITrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	AMUX_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);

	NTC_FOVI.Set(FV, 1.25, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(1000);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &AMUX_FOVI);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	double Trig_Point[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = AMUX_FOVI.GetMeasResult(site, MIRET, TRIG_RESULT);
		vc_offset_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		check_awg_trigger_point(Trig_Point, sam, vc_offset_rise,site);// add for AWG trigger check
	}


	STSAWGCreateRampData(&vc_offset_f[0], sam, 1, 1.51, 1.29);//  PMID-->SW
	NTC_FOVI.AwgLoader("vc_offset_f_pattern", FV, FOVIe_2V, FOVIe_100MA, vc_offset_f, sam);
	NTC_FOVI.AwgSelect("vc_offset_f_pattern", 0, sam - 1, sam - 1, interval);
	AMUX_FOVI.SetMeasITrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	AMUX_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);

	NTC_FOVI.Set(FV, 1.51, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(1000);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &AMUX_FOVI);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = AMUX_FOVI.GetMeasResult(site, MIRET, TRIG_RESULT);
		vc_offset_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		check_awg_trigger_point(Trig_Point, sam, vc_offset_fall,site);// add for AWG trigger check
	}


	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		PMID_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);

	}
	FOR_EACH_VALID_SITE(site)
	{
		VC_CLAMP_LOW->SetTestResult(site, 0, vc_clamp_low[site]);
		VC_OFFSET_Rise->SetTestResult(site, 0, vc_offset_rise[site]);
		VC_OFFSET_Fall->SetTestResult(site, 0, vc_offset_fall[site]);
	}

    return 0;
}
 
DUT_API int PSM_THRESHOLD(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *PSM_VTH_Rise = StsGetParam(funcindex, "PSM_VTH_Rise");
    CParam *PSM_VTH_Fall = StsGetParam(funcindex, "PSM_VTH_Fall");
    CParam *PSM_VTH_Hys = StsGetParam(funcindex, "PSM_VTH_Hys");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double psm_vth_r[200] = { 0.0 };
	double psm_vth_f[200] = { 0.0 };
	double Trig = 2.5;
	double psm_vth_rise[SITE_NUM] = { 0 };
	double psm_vth_fall[SITE_NUM] = { 0 };
	double psm_vth_hys[SITE_NUM] = { 0 };
	cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K43_INT_ACM, K58_INT_PU,K25_VCC_Cap, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	NTC_FOVI.Set(FV, 1.25, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x60);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(EN_ATEST1,1),(D2A_BUBO_ATEST1,6),(DIS_NTC_DETECTION_ANALOG,1)]
	I2CWriteSameData(DEV_ADDR, 0x55, 0xB4);//		field[(EN_DTEST0,1),(DTEST0_MUX,52)]
	delay_ms(1);

	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&psm_vth_r[0], sam, 1, 1.35, 1.5);//  PMID-->SW
	NTC_FOVI.AwgLoader("psm_vth_r_pattern", FV, FOVIe_2V, FOVIe_100MA, psm_vth_r, sam);
	NTC_FOVI.AwgSelect("psm_vth_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);

	NTC_FOVI.Set(FV, 1.3, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	double Trig_Point[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		psm_vth_rise[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		check_awg_trigger_point(Trig_Point, sam, psm_vth_rise,site);// add for AWG trigger check
	}


	STSAWGCreateRampData(&psm_vth_f[0], sam, 1, 1.48, 1.32);//  PMID-->SW
	NTC_FOVI.AwgLoader("psm_vth_f_pattern", FV, FOVIe_2V, FOVIe_100MA, psm_vth_f, sam);
	NTC_FOVI.AwgSelect("psm_vth_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);

	NTC_FOVI.Set(FV, 1.5, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&NTC_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&NTC_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		psm_vth_fall[site] = NTC_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		psm_vth_hys[site] = (psm_vth_rise[site] - psm_vth_fall[site])*1e3;//mV
		check_awg_trigger_point(Trig_Point, sam, psm_vth_fall,site);// add for AWG trigger check
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
		PMID_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
	}

	FOR_EACH_VALID_SITE(site)
	{
		PSM_VTH_Rise->SetTestResult(site, 0, psm_vth_rise[site]);
		PSM_VTH_Fall->SetTestResult(site, 0, psm_vth_fall[site]);
		PSM_VTH_Hys->SetTestResult(site, 0, psm_vth_hys[site]);
	}
    return 0;
}
 
DUT_API int TRIKEL_CURRENT(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *ITRKL_HS_CURRENT_200mA = StsGetParam(funcindex, "ITRKL_HS_CURRENT_200mA");
    CParam *ITRKL_LS_CURRENT_200mA = StsGetParam(funcindex, "ITRKL_LS_CURRENT_200mA");
    CParam *ITRKL_CURRENT_200mA = StsGetParam(funcindex, "ITRKL_CURRENT_200mA");
    CParam *ITRKL_HS_CURRENT_400mA = StsGetParam(funcindex, "ITRKL_HS_CURRENT_400mA");
    CParam *ITRKL_LS_CURRENT_400mA = StsGetParam(funcindex, "ITRKL_LS_CURRENT_400mA");
    CParam *ITRKL_CURRENT_400mA = StsGetParam(funcindex, "ITRKL_CURRENT_400mA");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double bubo_trikle[200] = { 0.0 };
	double Trig = 2.5;
	int Trig_Point[SITE_NUM] = { 0 };

	double trikle_current1[SITE_NUM] = { 0 };
	double trikle_current2[SITE_NUM] = { 0 };
	double hs_trikle_curr1[SITE_NUM] = { 0 };
	double hs_trikle_curr2[SITE_NUM] = { 0 };
	double ls_trikle_curr1[SITE_NUM] = { 0 };
	double ls_trikle_curr2[SITE_NUM] = { 0 };
	cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K43_INT_ACM, K58_INT_PU, K31_BUSL_PMID, K17_BUSH_SW, K25_VCC_Cap, -1);// connect SW and PIMD by FPVI
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x0B, 0x00);// (ITRIKLE,0)
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_SLP,1),(BUBO_MODE,0),(D2A_BUBO_TM_FORCE_EN_CS,1),(ITRIKLE,0)]
	I2CWriteSameData(DEV_ADDR, 0x67, 0x03);//		field[(D2A_OVRD_SEL,3)] //		field[(ovrd_value,3)]
	I2CWriteSameData(DEV_ADDR, 0x68, 0x20);//		field[(OVRD_VALUE,2)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xB8);//		field[(EN_DTEST0,1),(DTEST0_MUX,56)]
	delay_ms(1);
	FPVI.Set(FI, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	//--------Trikle1, HSFET current threshold
	STSAWGCreateRampData(&bubo_trikle[0], sam, 1, -0.5, -0.1);// PMID-->SW
	FPVI.AwgClear();
	FPVI.AwgLoader("bubo_trikle_pattern", FI, FPVIe_1V, FPVIe_1A, bubo_trikle, sam);
	FPVI.AwgSelect("bubo_trikle_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	FPVI.Set(FI, -0.55, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		hs_trikle_curr1[site] = -1 * FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site])*1e3; //Read the voltage value on trigger position, mA
		check_awg_trigger_point(Trig_Point, sam, hs_trikle_curr1,site);// add for AWG trigger check
	}


	//--------Trikle2, HSFET current threshold
	I2CWriteSameData(DEV_ADDR, 0x0B, 0x10);// (ITRIKLE,1)
	delay_ms(1);
	STSAWGCreateRampData(&bubo_trikle[0], sam, 1, -0.9, -0.4);//PGND-->SW
	FPVI.AwgClear();
	FPVI.AwgLoader("bubo_trikle_pattern", FI, FPVIe_1V, FPVIe_1A, bubo_trikle, sam);
	FPVI.AwgSelect("bubo_trikle_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	FPVI.Set(FI, -0.95, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		hs_trikle_curr2[site] = -1 * FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site])*1e3;  //Read the voltage value on trigger position, mA
		check_awg_trigger_point(Trig_Point, sam, hs_trikle_curr2,site);// add for AWG trigger check
	}

	I2CWriteSameData(DEV_ADDR, 0x59, 0x00);
	BTST_ACM.Set(FV, V_TYP_VBUS, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K43_INT_ACM, K58_INT_PU, K33_BUSL_PGND, K17_BUSH_SW, K25_VCC_Cap, -1);// connect SW and PGND by FPVI
	delay_ms(3);
	I2CWriteSameData(DEV_ADDR, 0x0B, 0x00);// (ITRIKLE,0)
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x81);//		field[(D2A_BUBO_TM_HSON,0),(D2A_BUBO_TM_LSON,1)]
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_SLP,1),(BUBO_MODE,0),(D2A_BUBO_TM_FORCE_EN_CS,1),(ITRIKLE,0)]
	I2CWriteSameData(DEV_ADDR, 0x67, 0x03);//		field[(D2A_OVRD_SEL,3)] //		field[(ovrd_value,3)]
	I2CWriteSameData(DEV_ADDR, 0x68, 0x20);//		field[(OVRD_VALUE,2)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x55, 0xB2);//		field[(EN_DTEST0,1),(DTEST0_MUX,50)]
	delay_ms(1);

	//--------Trikle1, LSFET current threshold
	FPVI.Set(FI, -0.45, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	STSAWGCreateRampData(&bubo_trikle[0], sam, 1, -0.4, 0.1);//PGND--->SW
	FPVI.AwgClear();
	FPVI.AwgLoader("bubo_trikle_pattern", FI, FPVIe_1V, FPVIe_1A, bubo_trikle, sam);
	FPVI.AwgSelect("bubo_trikle_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		ls_trikle_curr1[site] = -1 * FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site])*1e3; //Read the voltage value on trigger position, mA
		check_awg_trigger_point(Trig_Point, sam, ls_trikle_curr1,site);// add for AWG trigger check
	}

	//--------Trikle2, LSFET current threshold
	FPVI.Set(FI, -0.4, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	I2CWriteSameData(DEV_ADDR, 0x0B, 0x10);// (ITRIKLE,1)
	delay_ms(1);
	STSAWGCreateRampData(&bubo_trikle[0], sam, 1, -0.3, 0.1);// SW--->PGND
	FPVI.AwgClear();
	FPVI.AwgLoader("bubo_trikle_pattern", FI, FPVIe_1V, FPVIe_1A, bubo_trikle, sam);
	FPVI.AwgSelect("bubo_trikle_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		ls_trikle_curr2[site] = -1 * FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site])*1e3; //Read the voltage value on trigger position, mA
		check_awg_trigger_point(Trig_Point, sam, ls_trikle_curr2,site);// add for AWG trigger check
	}
	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);

		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_ON);
		PMID_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FI, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	}

	FOR_EACH_VALID_SITE(site)
	{
		ITRKL_HS_CURRENT_200mA->SetTestResult(site, 0, hs_trikle_curr1[site]);
		ITRKL_LS_CURRENT_200mA->SetTestResult(site, 0, ls_trikle_curr1[site]);
		ITRKL_CURRENT_200mA->SetTestResult(site, 0, 0.5*(hs_trikle_curr1[site] + ls_trikle_curr1[site]));
		ITRKL_HS_CURRENT_400mA->SetTestResult(site, 0, hs_trikle_curr2[site]);
		ITRKL_LS_CURRENT_400mA->SetTestResult(site, 0, ls_trikle_curr2[site]);
		ITRKL_CURRENT_400mA->SetTestResult(site, 0, 0.5*(hs_trikle_curr2[site] + ls_trikle_curr2[site]));
	}


	return 0;
}

DUT_API int BUCK_IPEAK_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BUCK_HS_PK_10A = StsGetParam(funcindex, "BUCK_HS_PK_10A");
    CParam *BUCK_HS_PK_15A = StsGetParam(funcindex, "BUCK_HS_PK_15A");
    CParam *BUCK_HS_PK_2P5A = StsGetParam(funcindex, "BUCK_HS_PK_2P5A");
    CParam *BUCK_HS_Ref_Def = StsGetParam(funcindex, "BUCK_HS_Ref_Def");
    CParam *BUCK_HS_Ref_10A = StsGetParam(funcindex, "BUCK_HS_Ref_10A");
    CParam *BUCK_HS_Ref_15A = StsGetParam(funcindex, "BUCK_HS_Ref_15A");
    CParam *BUCK_HS_PK_Gain = StsGetParam(funcindex, "BUCK_HS_PK_Gain");
    CParam *BUCK_HS_PK_Vos = StsGetParam(funcindex, "BUCK_HS_PK_Vos");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double bubo_limit_ocp[200] = { 0.0 };
	double Trig = 2.5;
	int Trig_Point[SITE_NUM] = { 0 };

	double buck_hs_ilimit_off[SITE_NUM] = { 0 };
	double buck_hs_ilimit_10A[SITE_NUM] = { 0 };
	double buck_hs_ilimit_15A[SITE_NUM] = { 0 };
	double ilimit_ref_10A[SITE_NUM] = { 0 };
	double ilimit_ref_15A[SITE_NUM] = { 0 };
	double ilimit_ref_off[SITE_NUM] = { 0 };
	double ilimit_ref_off_rt[SITE_NUM] = { 0 };
	cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K43_INT_ACM, K58_INT_PU, K31_BUSL_PMID, K17_BUSH_SW, K25_VCC_Cap, -1);// connect SW and PIMD by FPVI
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x86);//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(BUBO_MODE,0),(D2A_BUBO_TM_FORCE_EN_CS,1),(D2A_BUBO_TM_LOW_ILIMT_OFF,1)]
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x67, 0x03);//		field[(DIS_NTC_DETECTION_ANALOG,1),(D2A_OVRD_SEL,3)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(OVRD_VALUE,3)]
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1),],  field[(D2A_BUB0_ATEST1,10),(D2A_BUB0_ATEST0,8)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	I2CWriteSameData(DEV_ADDR, 0x55, 0xB8);//		field[(EN_DTEST0,1),(DTEST0_MUX,56)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x06);	//		field[(EN_ATEST0,1),(EN_ATEST1,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(IPEAK_LIMIT,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x86);//		field[(D2A_BUBO_TM_LOW_ILIMT_OFF,1)]
	delay_ms(1);

	STSAWGCreateRampData(&bubo_limit_ocp[0], sam, 1, -2, -3);// PMID-->SW
	FPVI.AwgClear();
	FPVI.AwgLoader("bubo_limit_ocp_pattern", FI, FPVIe_1V, FPVIe_10A, bubo_limit_ocp, sam);
	FPVI.AwgSelect("bubo_limit_ocp_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	FPVI.Set(FI, -2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_ms(1);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		buck_hs_ilimit_off[site] = -1 * FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]); //Read the voltage value on trigger position
		check_awg_trigger_point(Trig_Point, sam, buck_hs_ilimit_off,site);// add for AWG trigger check
	}


	AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x06);//		field[(EN_ATEST0,1),(EN_ATEST1,1)]

	double Vsns1_peak[SITE_NUM] = { 0 };
	double Vsns2_peak[SITE_NUM] = { 0 };
	double buck_pk_vos[SITE_NUM] = { 0 };
	double buck_pk_vos_rt[SITE_NUM] = { 0 };
	I2CWriteSameData(DEV_ADDR, 0x5A, 0xAE);//----CSTOP_VREF_SNS2--ATEST1, CSTOP_VSNS_IBAT----ATEST0
	FPVI.Set(FI, 0.4, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	ATEST_GRP.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vsns1_peak[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}
	FPVI.Set(FI, 0.9, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	ATEST_GRP.MeasureVI(215, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	double unstableMs[SITE_NUM] = { 0 };
	int unstable = 0;
	FOR_EACH_VALID_SITE(site)
	{
		Vsns2_peak[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
		Gain_peak_hsfet[site] = abs((Vsns2_peak[site] - Vsns1_peak[site]) / 0.5);// ohm
		if (abs(Gain_peak_hsfet[site] - 0.08) > 0.0035)
		{
			unstable++;
			unstableMs[site] = 1;
		}
	}
	if (unstable)
	{
		FPVI.Set(FI, 0.9, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(2);
		ATEST_GRP.MeasureVI(215, 10);
		FOR_EACH_VALID_SITE(site)
		{
			Vsns1_peak[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
		}
		FPVI.Set(FI, 0.5, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(2);
		ATEST_GRP.MeasureVI(215, 10);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			if (unstableMs[site])
			{
				Vsns2_peak[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
				Gain_peak_hsfet[site] = abs((Vsns2_peak[site] - Vsns1_peak[site]) / 0.5);// ohm
				if (abs(Gain_peak_hsfet[site] - 0.08) > 0.0035)
				{
					Gain_peak_hsfet[site] = 0.8*BUCK_IBAT_HS_Gain[site] / 1000;
				}
			}
		}
	}
	

	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);


	I2CWriteSameData(DEV_ADDR, 0x5A, 0xA8);	//field[ (D2A_BUBO_ATEST0, 8)]: CSTOP_HS_ILIM_REF//field[ (D2A_BUBO_ATEST1, 10):CSTOP_VREF_SNS2
	delay_ms(5);
	ATEST_GRP.MeasureVI(100, 5);
	FOR_EACH_VALID_SITE(site)
	{
		ilimit_ref_off[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
		buck_pk_vos[site] = ilimit_ref_off[site] - buck_hs_ilimit_off[site] * Gain_peak_hsfet[site];
	}

	//-------------------------------Measure reference
	I2CWriteSameData(DEV_ADDR, 0x59, 0x82);//		field[(D2A_BUBO_TM_LOW_ILIMT_OFF,0)]
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//	10A,	field[(IPEAK_LIMIT,1)],0x1= BUBO FORCE ON enable (D2A_BUBO_EN=1)
	delay_ms(5);
	ATEST_GRP.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		ilimit_ref_15A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}

	I2CWriteSameData(DEV_ADDR, 0x61, 0x0D);//15A, field[(IPEAK_LIMIT,2)],0x1= BUBO FORCE ON enable (D2A_BUBO_EN=1)
	delay_ms(5);
	ATEST_GRP.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		ilimit_ref_10A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}

	I2CWriteSameData(DEV_ADDR, 0x59, 0x86);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 5);
	FOR_EACH_VALID_SITE(site)
	{
		ilimit_ref_off_rt[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
		buck_pk_vos_rt[site] = ilimit_ref_off_rt[site] - buck_hs_ilimit_off[site] * Gain_peak_hsfet[site];
	}

	if (!TTR)
	{
		StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);

		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_OFF);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
	}
	else
	{
		double vlimit_ref_11A[SITE_NUM] = { 0 };
		double vlimit_ref_16p5A[SITE_NUM] = { 0 };
		double cstop_vref_sns[SITE_NUM] = { 0 };
		//double hs_ocp_ref_off[SITE_NUM] = { 0 };
		double bubo_limit_ocp[200] = { 0.0 };
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);//(BUBO_MODE,1),
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);//field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_TM_FORCE_EN_CS,1),
		I2CWriteSameData(DEV_ADDR, 0x59, 0x86);//(D2A_BUBO_TM_LOW_ILIMT_OFF,1)]
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x67, 0x03);//		field[(DIS_NTC_DETECTION_ANALOG,1),(D2A_OVRD_SEL,3)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(OVRD_VALUE,3)]
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
		//I2CWriteSameData(DEV_ADDR, 0x5A, 0xA0);//		field[(D2A_BUBO_ATEST1,10)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		I2CWriteSameData(DEV_ADDR, 0x55, 0xC0);//		field[(EN_DTEST0,1),(DTEST0_MUX,64)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x04);	//		field[(EN_ATEST1,1)]

		FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10A, FPVIe_RELAY_ON);
		FPVI.Set(FI, 0, FPVIe_10V, FPVIe_10A, FPVIe_RELAY_ON);

		STSAWGCreateRampData(&bubo_limit_ocp[0], sam, 1, 2.1, 2.9);// PMID-->SW
		FPVI.AwgClear();
		FPVI.AwgLoader("bubo_limit_ocp_pattern", FI, FPVIe_1V, FPVIe_10A, bubo_limit_ocp, sam);
		FPVI.AwgSelect("bubo_limit_ocp_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
		FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		delay_ms(1);
		STSEnableAWG(&FPVI);
		STSEnableMeas(&FPVI, &SDA_INT_ACM);
		STSAWGRun();
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
			boost_hs_ocp_off[site] = FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]);  //Read the voltage value on trigger position, mA
			check_awg_trigger_point(Trig_Point, sam, boost_hs_ocp_off,site);// add for AWG trigger check
		}

		//double Gain_ocp[SITE_NUM] = { 0 };
		//double buck_ocp_vos[SITE_NUM] = { 0 };
		//I2CWriteSameData(DEV_ADDR, 0x5A, 0xBE);//----CSTOP_VREF_SNS2--ATEST1, CSTOP_VSNS_IBAT----ATEST0
		//FPVI.Set(FI, 0.4, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		//delay_ms(2);
		//ATEST_GRP.MeasureVI(215, 10);
		//FOR_EACH_VALID_SITE(site)
		//{
		//	Vsns1_peak[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
		//}
		//FPVI.Set(FI, 0.9, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		//delay_ms(2);
		//ATEST_GRP.MeasureVI(215, 10);
		//FOR_EACH_VALID_SITE(site)
		//{
		//	Vsns2_peak[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
		//	Gain_ocp[site] = abs((Vsns2_peak[site] - Vsns1_peak[site]) / 0.5);// ohm
		//	Gain_ocp[site] = Gain_peak[site] * 1.1;
		//}
		//FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		//FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);



		I2CWriteSameData(DEV_ADDR, 0x5A, 0xA0);//		field[(D2A_BUBO_ATEST1,10)]--CSTOP_VREF_SNS2, 2.805V,一直不变
		delay_ms(5);
		NTC_FOVI.MeasureVI(100, 5);
		FOR_EACH_VALID_SITE(site)
		{
			cstop_vref_sns[site] = NTC_FOVI.GetMeasResult(site, MVRET);
		}

		I2CWriteSameData(DEV_ADDR, 0x5A, 0xB0);//		field[(D2A_BUBO_ATEST1,11)]--CSTOP_HS_OCP_REF
		delay_ms(5);
		NTC_FOVI.MeasureVI(100, 5);
		FOR_EACH_VALID_SITE(site)
		{
			hs_ocp_ref_off[site] = abs(NTC_FOVI.GetMeasResult(site, MVRET) - cstop_vref_sns[site]);
			boost_hs_ocp_vos[site] = hs_ocp_ref_off[site] - boost_hs_ocp_off[site] * Gain_peak_hsfet[site];
		}

		//----------------10A *1.1, Get Reference
		I2CWriteSameData(DEV_ADDR, 0x59, 0x82);//		field[(D2A_BUBO_TM_LOW_ILIMT_OFF,0)]
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(IPEAK_LIMIT,1)]
		delay_ms(5);
		NTC_FOVI.MeasureVI(100, 5);
		FOR_EACH_VALID_SITE(site)
		{
			iocp_ref_16p5A[site] = abs(NTC_FOVI.GetMeasResult(site, MVRET) - cstop_vref_sns[site]);
		}

		//------------------15A* 1.1, Get Reference
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0D);//		field[(IPEAK_LIMIT,1)], 10A*1.1
		delay_ms(5);
		NTC_FOVI.MeasureVI(100, 5);
		FOR_EACH_VALID_SITE(site)
		{
			iocp_ref_11A[site] = abs(NTC_FOVI.GetMeasResult(site, MVRET) - cstop_vref_sns[site]);
		}
		FOR_EACH_VALID_SITE(site)
		{
			//boost_hs_ocp_11A[site] = iocp_ref_11A[site] * boost_hs_ocp_off[site] / hs_ocp_ref_off[site];
			//boost_hs_ocp_16p5A[site] = iocp_ref_16p5A[site] * boost_hs_ocp_off[site] / hs_ocp_ref_off[site];
			boost_hs_ocp_11A[site] = (iocp_ref_11A[site] - boost_hs_ocp_vos[site]) / Gain_peak_hsfet[site];
			boost_hs_ocp_16p5A[site] = (iocp_ref_16p5A[site] - boost_hs_ocp_vos[site]) / Gain_peak_hsfet[site];
		}

		I2CWriteSameData(DEV_ADDR, 0x59, 0x00);
		BTST_ACM.Set(FV, V_TYP_VBUS, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
	}


	FOR_EACH_VALID_SITE(site)
	{
		buck_hs_ilimit_10A[site] = (ilimit_ref_10A[site] - buck_pk_vos[site]) / Gain_peak_hsfet[site];
		buck_hs_ilimit_15A[site] = (ilimit_ref_15A[site] - buck_pk_vos[site]) / Gain_peak_hsfet[site];
		if (buck_hs_ilimit_15A[site]<13.95)
		{	
			buck_hs_ilimit_15A[site] = (ilimit_ref_15A[site] - buck_pk_vos_rt[site]) / Gain_peak_hsfet[site];
			buck_hs_ilimit_10A[site] = (ilimit_ref_10A[site] - buck_pk_vos_rt[site]) / Gain_peak_hsfet[site];
			buck_pk_vos[site] = buck_pk_vos_rt[site];
		}
		BUCK_HS_PK_10A->SetTestResult(site, 0, buck_hs_ilimit_10A[site]);
		BUCK_HS_PK_15A->SetTestResult(site, 0, buck_hs_ilimit_15A[site]);
		BUCK_HS_PK_2P5A->SetTestResult(site, 0, buck_hs_ilimit_off[site]);
		BUCK_HS_Ref_Def->SetTestResult(site, 0, ilimit_ref_off[site]);
		BUCK_HS_Ref_10A->SetTestResult(site, 0, ilimit_ref_10A[site]);
		BUCK_HS_Ref_15A->SetTestResult(site, 0, ilimit_ref_15A[site]);
		BUCK_HS_PK_Gain->SetTestResult(site, 0, Gain_peak_hsfet[site] * 1e3);//mohm
		BUCK_HS_PK_Vos->SetTestResult(site, 0, buck_pk_vos[site] * 1e3);//mV
	}

	return 0;
}

DUT_API int BOOST_IPEAK_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BOOST_LS_PK_10A = StsGetParam(funcindex, "BOOST_LS_PK_10A");
    CParam *BOOST_LS_PK_15A = StsGetParam(funcindex, "BOOST_LS_PK_15A");
    CParam *BOOST_LS_PK_2P5A = StsGetParam(funcindex, "BOOST_LS_PK_2P5A");
    CParam *BOOST_LS_Ref_Def = StsGetParam(funcindex, "BOOST_LS_Ref_Def");
    CParam *BOOST_LS_Ref_10A = StsGetParam(funcindex, "BOOST_LS_Ref_10A");
    CParam *BOOST_LS_Ref_15A = StsGetParam(funcindex, "BOOST_LS_Ref_15A");
    CParam *BOOST_LS_PK_Gain = StsGetParam(funcindex, "BOOST_LS_PK_Gain");
    CParam *BOOST_LS_PK_Vos = StsGetParam(funcindex, "BOOST_LS_PK_Vos");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double bubo_limit_ocp[200] = { 0.0 };
	double Trig = 2.5;
	int Trig_Point[SITE_NUM] = { 0 };

	double boost_ls_ilimit_off[SITE_NUM] = { 0 };
	double boost_ls_ilimit_10A[SITE_NUM] = { 0 };
	double boost_ls_ilimit_15A[SITE_NUM] = { 0 };
	double ilimit_ref_10A[SITE_NUM] = { 0 };
	double ilimit_ref_15A[SITE_NUM] = { 0 };
	double ilimit_ref_off[SITE_NUM] = { 0 };
	cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K43_INT_ACM, K58_INT_PU, K33_BUSL_PGND, K17_BUSH_SW, K25_VCC_Cap, -1);// connect SW and PIMD by FPVI
	delay_ms(3);
	if (!TTR)
	{
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);//VBAT<4.2V
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);// BUBO_mode=1
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x85);//		field[(WAKE_UP,1),(D2A_BUBO_TM_LSON,1),(BUBO_MODE,1),(D2A_BUBO_TM_FORCE_EN_CS,1),(D2A_BUBO_TM_LOW_ILIMT_OFF,1)]	
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x67, 0x03);//		field[(DIS_NTC_DETECTION_ANALOG,1),(D2A_OVRD_SEL,3)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(OVRD_VALUE,3)]
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);	//		field[(D2A_BUBO_EN_FORCE_ON,1),]
		//I2CWriteSameData(DEV_ADDR, 0x5A, 0xAC);//		field[(D2A_BUBO_ATEST1,10),(D2A_BUBO_ATEST0,12)]
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		I2CWriteSameData(DEV_ADDR, 0x55, 0xB8);//		field[(EN_DTEST0,1),(DTEST0_MUX,56)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);//		field[(EN_ATEST0,1),(EN_ATEST1,1)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x85);//		field[(D2A_BUBO_TM_LOW_ILIMT_REF,1)]
		delay_ms(1);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		//------BST LSFET PEAK current threshold
		STSAWGCreateRampData(&bubo_limit_ocp[0], sam, 1, 2, 3.1);// SW--->PGND
		FPVI.AwgClear();
		FPVI.AwgLoader("bubo_limit_ocp_pattern", FI, FPVIe_1V, FPVIe_10A, bubo_limit_ocp, sam);
		FPVI.AwgSelect("bubo_limit_ocp_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
		FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		delay_ms(1);
		STSEnableAWG(&FPVI);
		STSEnableMeas(&FPVI, &SDA_INT_ACM);
		STSAWGRun();
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
			boost_ls_ilimit_off[site] = abs(FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site])); //Read the voltage value on trigger position,
			check_awg_trigger_point(Trig_Point, sam, boost_ls_ilimit_off,site);// add for AWG trigger check
		}
	}
	else
	{
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);// BUBO_mode=1
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x85);//		field[(WAKE_UP,1),(D2A_BUBO_TM_LSON,1),(BUBO_MODE,1),(D2A_BUBO_TM_FORCE_EN_CS,1),(D2A_BUBO_TM_LOW_ILIMT_OFF,1)]	
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x67, 0x03);//		field[(DIS_NTC_DETECTION_ANALOG,1),(D2A_OVRD_SEL,3)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(OVRD_VALUE,3)]
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);	//		field[(D2A_BUBO_EN_FORCE_ON,1),]
		//I2CWriteSameData(DEV_ADDR, 0x5A, 0xAC);//		field[(D2A_BUBO_ATEST1,10),(D2A_BUBO_ATEST0,12)]
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		I2CWriteSameData(DEV_ADDR, 0x55, 0xB8);//		field[(EN_DTEST0,1),(DTEST0_MUX,56)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);//		field[(EN_ATEST0,1),(EN_ATEST1,1)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x85);//		field[(D2A_BUBO_TM_LOW_ILIMT_REF,1)]
		delay_ms(1);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		//------BST LSFET PEAK current threshold
		STSAWGCreateRampData(&bubo_limit_ocp[0], sam, 1, 2.1, 2.9);// SW--->PGND
		FPVI.AwgClear();
		FPVI.AwgLoader("bubo_limit_ocp_pattern", FI, FPVIe_1V, FPVIe_10A, bubo_limit_ocp, sam);
		FPVI.AwgSelect("bubo_limit_ocp_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
		FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		delay_ms(1);
		STSEnableAWG(&FPVI);
		STSEnableMeas(&FPVI, &SDA_INT_ACM);
		STSAWGRun();
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
			boost_ls_ilimit_off[site] = abs(FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site])); //Read the voltage value on trigger position,
			check_awg_trigger_point(Trig_Point, sam, boost_ls_ilimit_off,site);// add for AWG trigger check
		}
	}

	AMUX_FOVI.Set(FV, 2.9, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 2.9, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(1);
	AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);

	double Vsns1_peak[SITE_NUM] = { 0 };
	double Vsns2_peak[SITE_NUM] = { 0 };
	I2CWriteSameData(DEV_ADDR, 0x5A, 0xAE);//----CSTOP_VREF_SNS2--ATEST1, CSTOP_VSNS_IBAT----ATEST0
	FPVI.Set(FI, 0.4, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	ATEST_GRP.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Vsns1_peak[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}
	FPVI.Set(FI, 0.9, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	ATEST_GRP.MeasureVI(215, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	double unstableMs[SITE_NUM] = { 0 };
	int unstable = 0;
	FOR_EACH_VALID_SITE(site)
	{
		Vsns2_peak[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
		Gain_peak_lsfet[site] = abs((Vsns2_peak[site] - Vsns1_peak[site]) / 0.5);// ohm
		if (abs(Gain_peak_hsfet[site] - 0.08) > 0.0035)
		{
			unstable++;
			unstableMs[site] = 1;
		}
	}
	if (unstable)
	{
		FPVI.Set(FI, 0.9, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(2);
		ATEST_GRP.MeasureVI(215, 10);
		FOR_EACH_VALID_SITE(site)
		{
			Vsns1_peak[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
		}
		FPVI.Set(FI, 0.5, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(2);
		ATEST_GRP.MeasureVI(215, 10);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			if (unstableMs[site])
			{
				Vsns2_peak[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
				Gain_peak_hsfet[site] = abs((Vsns2_peak[site] - Vsns1_peak[site]) / 0.5);// ohm
				if (abs(Gain_peak_hsfet[site] - 0.08) > 0.0035)
				{
					Gain_peak_hsfet[site] = 0.8*BOOST_IBAT_LS_Gain[site] / 1000;
				}
			}
		}
	}
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);


	I2CWriteSameData(DEV_ADDR, 0x5A, 0xAC);	//field[ (D2A_BUBO_ATEST0, 8)]: CSTOP_LS_ILIM_REF//field[ (D2A_BUBO_ATEST1, 10):CSTOP_VREF_SNS2
	delay_ms(10);
	ATEST_GRP.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		ilimit_ref_off[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
		boost_ls_pk_vos[site] = ilimit_ref_off[site] - boost_ls_ilimit_off[site] * Gain_peak_hsfet[site];
	}

	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B); //0x1= BUBO FORCE ON enable (D2A_BUBO_EN=1)
	I2CWriteSameData(DEV_ADDR, 0x59, 0x81);//		field[(D2A_BUBO_TM_LOW_ILIMT_OFF,0)]
	delay_ms(4);
	ATEST_GRP.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		ilimit_ref_15A[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	I2CWriteSameData(DEV_ADDR, 0x61, 0x0D);//		field[(IPEAK_LIMIT,2)]
	delay_ms(4);
	ATEST_GRP.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		ilimit_ref_10A[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
		PMID_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	}


	FOR_EACH_VALID_SITE(site)
	{
		boost_ls_ilimit_10A[site] = (ilimit_ref_10A[site] - boost_ls_pk_vos[site]) / Gain_peak_hsfet[site];
		boost_ls_ilimit_15A[site] = (ilimit_ref_15A[site] - boost_ls_pk_vos[site]) / Gain_peak_hsfet[site];
		//boost_ls_ilimit_10A[site] = (ilimit_ref_10A[site] - boost_ls_pk_vos[site]) * boost_ls_ilimit_off[site] / (ilimit_ref_off[site] -boost_ls_pk_vos[site]);
		//boost_ls_ilimit_15A[site] = (ilimit_ref_15A[site]- boost_ls_pk_vos[site]) * boost_ls_ilimit_off[site] / (ilimit_ref_off[site] - boost_ls_pk_vos[site]);
		BOOST_LS_PK_10A->SetTestResult(site, 0, boost_ls_ilimit_10A[site]);
		BOOST_LS_PK_15A->SetTestResult(site, 0, boost_ls_ilimit_15A[site]);
		BOOST_LS_PK_2P5A->SetTestResult(site, 0, boost_ls_ilimit_off[site]);
		BOOST_LS_Ref_Def->SetTestResult(site, 0, ilimit_ref_off[site]);
		BOOST_LS_Ref_10A->SetTestResult(site, 0, ilimit_ref_10A[site]);
		BOOST_LS_Ref_15A->SetTestResult(site, 0, ilimit_ref_15A[site]);
		BOOST_LS_PK_Gain->SetTestResult(site, 0, Gain_peak_hsfet[site] * 1e3);//mohm
		BOOST_LS_PK_Vos->SetTestResult(site, 0, boost_ls_pk_vos[site]*1e3);//mV
	}


	return 0;
}

DUT_API int BOOST_OCP_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BOOST_HS_OCP_11A = StsGetParam(funcindex, "BOOST_HS_OCP_11A");
    CParam *BOOST_HS_OCP_16P5A = StsGetParam(funcindex, "BOOST_HS_OCP_16P5A");
    CParam *BOOST_HS_OCP_2P5A = StsGetParam(funcindex, "BOOST_HS_OCP_2P5A");
    CParam *BOOST_HSOCP_Ref_Def = StsGetParam(funcindex, "BOOST_HSOCP_Ref_Def");
    CParam *BOOST_HSOCP_Ref_11A = StsGetParam(funcindex, "BOOST_HSOCP_Ref_11A");
    CParam *BOOST_HSOCP_Ref_16P5A = StsGetParam(funcindex, "BOOST_HSOCP_Ref_16P5A");
    CParam *BOOST_HSOCP_Gain = StsGetParam(funcindex, "BOOST_HSOCP_Gain");
    CParam *BOOST_HSOCP_Vos = StsGetParam(funcindex, "BOOST_HSOCP_Vos");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double bubo_limit_ocp[200] = { 0.0 };
	double Trig = 2.5;
	int Trig_Point[SITE_NUM] = { 0 };

	if (!TTR)
	{
		double vlimit_ref_11A[SITE_NUM] = { 0 };
		double vlimit_ref_16p5A[SITE_NUM] = { 0 };
		cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K43_INT_ACM, K58_INT_PU, K31_BUSL_PMID, K17_BUSH_SW, K25_VCC_Cap, -1);// connect SW and PIMD by FPVI
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
		BTST_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);//(BUBO_MODE,1),
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);//field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_TM_FORCE_EN_CS,1),
		I2CWriteSameData(DEV_ADDR, 0x59, 0x86);//(D2A_BUBO_TM_LOW_ILIMT_OFF,1)]
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x67, 0x03);//		field[(DIS_NTC_DETECTION_ANALOG,1),(D2A_OVRD_SEL,3)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(OVRD_VALUE,3)]
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
		//I2CWriteSameData(DEV_ADDR, 0x5A, 0xA0);//		field[(D2A_BUBO_ATEST1,10)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		I2CWriteSameData(DEV_ADDR, 0x55, 0xC0);//		field[(EN_DTEST0,1),(DTEST0_MUX,64)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x04);	//		field[(EN_ATEST1,1)]

		FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10A, FPVIe_RELAY_ON);
		FPVI.Set(FI, 0, FPVIe_10V, FPVIe_10A, FPVIe_RELAY_ON);

		STSAWGCreateRampData(&bubo_limit_ocp[0], sam, 1, 2, 3);// PMID-->SW
		FPVI.AwgClear();
		FPVI.AwgLoader("bubo_limit_ocp_pattern", FI, FPVIe_1V, FPVIe_10A, bubo_limit_ocp, sam);
		FPVI.AwgSelect("bubo_limit_ocp_pattern", 0, sam - 1, sam - 1, interval);
		SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
		SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
		FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
		FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		delay_ms(1);
		STSEnableAWG(&FPVI);
		STSEnableMeas(&FPVI, &SDA_INT_ACM);
		STSAWGRun();
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		FOR_EACH_VALID_SITE(site)
		{
			Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
			boost_hs_ocp_off[site] = FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]);  //Read the voltage value on trigger position, mA
			check_awg_trigger_point(Trig_Point, sam, boost_hs_ocp_off,site);// add for AWG trigger check
		}

		double cstop_vref_sns[SITE_NUM] = { 0 };
		//double hs_ocp_ref_off[SITE_NUM] = { 0 };
		I2CWriteSameData(DEV_ADDR, 0x5A, 0xA0);//		field[(D2A_BUBO_ATEST1,10)]--CSTOP_VREF_SNS2, 2.805V,一直不变
		delay_ms(2);
		NTC_FOVI.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			cstop_vref_sns[site] = NTC_FOVI.GetMeasResult(site, MVRET);
		}

		I2CWriteSameData(DEV_ADDR, 0x5A, 0xB0);//		field[(D2A_BUBO_ATEST1,11)]--CSTOP_HS_OCP_REF
		delay_ms(2);
		NTC_FOVI.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			hs_ocp_ref_off[site] = NTC_FOVI.GetMeasResult(site, MVRET) - cstop_vref_sns[site];
		}

		//----------------10A *1.1, Get Reference
		I2CWriteSameData(DEV_ADDR, 0x59, 0x82);//		field[(D2A_BUBO_TM_LOW_ILIMT_OFF,0)]
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(IPEAK_LIMIT,1)]
		delay_ms(2);
		NTC_FOVI.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			vlimit_ref_11A[site] = NTC_FOVI.GetMeasResult(site, MVRET) - cstop_vref_sns[site];
		}

		//------------------15A* 1.1, Get Reference
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0D);//		field[(IPEAK_LIMIT,1)], 10A*1.1
		delay_ms(2);
		NTC_FOVI.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			vlimit_ref_16p5A[site] = NTC_FOVI.GetMeasResult(site, MVRET) - cstop_vref_sns[site];
		}


		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);

		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
		FOR_EACH_VALID_SITE(site)
		{
			boost_hs_ocp_11A[site] = vlimit_ref_11A[site] * boost_hs_ocp_off[site] / hs_ocp_ref_off[site];
			boost_hs_ocp_16p5A[site] = vlimit_ref_16p5A[site] * boost_hs_ocp_off[site] / hs_ocp_ref_off[site];
		}
	}

	FOR_EACH_VALID_SITE(site)
	{
		BOOST_HS_OCP_11A->SetTestResult(site, 0, boost_hs_ocp_11A[site]);
		BOOST_HS_OCP_16P5A->SetTestResult(site, 0, boost_hs_ocp_16p5A[site]);
		BOOST_HS_OCP_2P5A->SetTestResult(site, 0, boost_hs_ocp_off[site] );
		BOOST_HSOCP_Ref_Def->SetTestResult(site, 0, hs_ocp_ref_off[site]);
		BOOST_HSOCP_Ref_11A->SetTestResult(site, 0, iocp_ref_11A[site]);
		BOOST_HSOCP_Ref_16P5A->SetTestResult(site, 0, iocp_ref_16p5A[site]);
		BOOST_HSOCP_Gain->SetTestResult(site, 0, Gain_peak_hsfet[site]*1e3);//mohm
		BOOST_HSOCP_Vos->SetTestResult(site, 0, boost_hs_ocp_vos[site]*1e3);//mV
	}

	return 0;
}

DUT_API int VBAT_LOOP_ACCUR(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_LP_4P2V_Output = StsGetParam(funcindex, "VBAT_LP_4P2V_Output");
    CParam *VBAT_LP_4P2V_Accuracy_DSA = StsGetParam(funcindex, "VBAT_LP_4P2V_Accuracy_DSA");
    CParam *VBAT_LP_4P4V_Output = StsGetParam(funcindex, "VBAT_LP_4P4V_Output");
    CParam *VBAT_LP_4P4V_Accuracy_DSA = StsGetParam(funcindex, "VBAT_LP_4P4V_Accuracy_DSA");
    CParam *VBAT_LP_4P55V_Output = StsGetParam(funcindex, "VBAT_LP_4P55V_Output");
    CParam *VBAT_LP_4P55V_Accuracy_DSA = StsGetParam(funcindex, "VBAT_LP_4P55V_Accuracy_DSA");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	double vbat_loop_4p4v_out[SITE_NUM] = { 0 };
	double vbat_loop_4p2v_out[SITE_NUM] = { 0 };
	//------------Connect Serve loop of BOOST mode, need confirm when 
	cbite.SetOn(K54_QPoint, K67_AMP2_Power,/* K62_AMP3_Power,*/K37_VAC_Cap, K25_VCC_Cap, K16_VBUS_Cap, -1);//amp no connect
	delay_ms(4);
	double vbat_v = 3.8;
	VBUS_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_ON);
	VAC123_ACM.Set(FV, 5, ACM200_20V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, vbat_v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 4.54, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(5);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x0A, (DWORD)spec[DEVICE_SEL]("CV_CONFIG"));
	//I2CWriteSameData(DEV_ADDR, 0x0A, 0x11);
	I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(VBAT_CV,1),(IBAT_LIMIT,7),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(DIS_NTC_DETECTION_ANALOG,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x67, 0x03);//		
	I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		over write vbat high than trikle
	delay_ms(2);
	SCL_ACM.Set(FV, 1.8, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, vbat_v, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
	//VBAT_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	cbite.SetOn(K54_QPoint, K67_AMP2_Power, /*K62_AMP3_Power ,*/K37_VAC_Cap, K25_VCC_Cap, K16_VBUS_Cap, K24_SVLP_VBAT, -1);//amp no connect
	delay_ms(5);// 3ms for cbit connect and 2ms for serve loop stable
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FI, 0, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	Retest_voltage_unstable_with_time_out(VBAT_ACM, vbat_loop_4p2v_out, 4, 4.8,10, 30,MEAS_V);
	FOR_EACH_VALID_SITE(site)
	{
		vbat_loop_4p2v_out[site] = VBAT_ACM.GetMeasResult(site, MVRET);//mV
	}

	//=============Config for VBAT= 4.4V
	I2CWriteSameData(DEV_ADDR, 0x0A, 0x15);// 4.4V
	delay_ms(10);
	VBAT_ACM.MeasureVI(215, 50);
	FOR_EACH_VALID_SITE(site)
	{
		vbat_loop_4p4v_out[site] = VBAT_ACM.GetMeasResult(site, MVRET);//mV
	}

	cbite.SetOn(K54_QPoint, K67_AMP2_Power, K37_VAC_Cap, K53_SCL_PU, K57_SDA_PU, K25_VCC_Cap, K16_VBUS_Cap, -1);//amp no connect
	delay_ms(3);
	cbite.SetOn(K54_QPoint, K37_VAC_Cap, K53_SCL_PU, K57_SDA_PU, K25_VCC_Cap, K16_VBUS_Cap, -1);//amp no connect
	delay_ms(3);
	if (!TTR)
	{
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SCL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
		delay_ms(1);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SCL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FI, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SCL_ACM.Set(FI, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10UA, FOVIe_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10UA, FOVIe_RELAY_OFF);//PMID need power off, or serve loop will be changed
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}

	FOR_EACH_VALID_SITE(site)
	{
		if (spec[DEVICE_SEL]("VBAT_CV_Point")==4.2)
		{
			VBAT_LP_4P2V_Output->SetTestResult(site, 0, vbat_loop_4p2v_out[site]);
			VBAT_LP_4P2V_Accuracy_DSA->SetTestResult(site, 0, (vbat_loop_4p2v_out[site] - spec[DEVICE_SEL]("VBAT_CV_Point"))*1e3);
			VBAT_LP_4P4V_Output->SetTestResult(site, 0, vbat_loop_4p4v_out[site]);
			VBAT_LP_4P4V_Accuracy_DSA->SetTestResult(site, 0, (vbat_loop_4p4v_out[site] - 4.4)*1e3);
		}
		else
		{
			VBAT_LP_4P55V_Output->SetTestResult(site, 0, vbat_loop_4p2v_out[site]);
			VBAT_LP_4P55V_Accuracy_DSA->SetTestResult(site, 0, (vbat_loop_4p2v_out[site] - spec[DEVICE_SEL]("VBAT_CV_Point"))*1e3);
		}

	}
    return 0;
}
 
DUT_API int VBAT_LOOP_COMP_ACCUR(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_LP_COMP_ACC = StsGetParam(funcindex, "VBAT_LP_COMP_ACC");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	double vbat_loop_comp_4p2v_acc[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap,  -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, 4, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	NTC_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x0A, 0x11);
	I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(VBAT_CV,1),(IBAT_LIMIT,7),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(DIS_NTC_DETECTION_ANALOG,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	delay_ms(1);

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double vbat_cv_vth[200] = { 0.0 };
	double Trig = 2.5;
	double Trig_Point[SITE_NUM] = { 0 };
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&vbat_cv_vth[0], sam, 1, 4.0, 4.4);//VBAT  ramp ntc falling from 3.3V to 2.1V
	VBAT_ACM.AwgLoader("vbat_cv_vth_pattern", FV, ACM200_10V, ACM200_100MA, vbat_cv_vth, sam);
	VBAT_ACM.AwgSelect("vbat_cv_vth_pattern", 0, sam - 1, sam - 1, interval);
	NTC_FOVI.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	NTC_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	VBAT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	VBAT_ACM.Set(FV, 4.0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&VBAT_ACM);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&VBAT_ACM, &NTC_FOVI);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously

	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = NTC_FOVI.GetMeasResult(site, MVRET, TRIG_RESULT);
		vbat_loop_comp_4p2v_acc[site] = VBAT_ACM.GetMeasResult(site, MVRET, (int)Trig_Point[site]) - 0.06;// need cut off 60mV
		check_awg_trigger_point(Trig_Point, sam, vbat_loop_comp_4p2v_acc,site);// add for AWG trigger check
	}
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		VBAT_LP_COMP_ACC->SetTestResult(site, 0, vbat_loop_comp_4p2v_acc[site]);
	}

	return 0;
}

DUT_API int VBUS_LOOP_BU_ACCUR(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_LP_BU_5V_Output = StsGetParam(funcindex, "VBUS_LP_BU_5V_Output");
    CParam *VBUS_LP_BU_5V_Accuracy = StsGetParam(funcindex, "VBUS_LP_BU_5V_Accuracy");
    CParam *VBUS_LP_BU_9V_Output = StsGetParam(funcindex, "VBUS_LP_BU_9V_Output");
    CParam *VBUS_LP_BU_9V_Accuracy = StsGetParam(funcindex, "VBUS_LP_BU_9V_Accuracy");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	double unsettle_flag[SITE_NUM] = { 0 };
	double unsettle = 0;
	double vbus_loop_5v_out[SITE_NUM] = { 0 };
	double vbus_loop_9v_out[SITE_NUM] = { 0 };
	if(! check_relay_off(VBAT_ACM,K54_QPoint,K24_SVLP_VBAT, &Relay_Off_Check))
	{
		FOR_EACH_VALID_SITE(site)
		{
			VBUS_LP_BU_5V_Output->SetTestResult(site, 0, 99979);
			VBUS_LP_BU_5V_Accuracy->SetTestResult(site, 0, 99979);
			VBUS_LP_BU_9V_Output->SetTestResult(site, 0, 99979);
			VBUS_LP_BU_9V_Accuracy->SetTestResult(site, 0, 99979);
		}
	}
	else
	{
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K62_AMP3_Power, K63_AMP4_Power, -1);
		delay_ms(3);
		VCC_ACM.Set(FV, 4.55, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FI, -0.0001, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(5);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0x1F);//30*0.02+4.4=5V
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(BUBO_MODE,0),(VBUS_VOL_SET_L,55),(IBAT_LIMIT,7),(IBUS_SET,127),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(DIS_NTC_DETECTION_ANALOG,1)]
		I2CWriteSameData(DEV_ADDR, 0x56, 0x05);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x80);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
		I2CWriteSameData(DEV_ADDR, 0x58, 0xA0);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		delay_ms(2);
		SCL_ACM.Set(FV, 1.8, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K62_AMP3_Power, K63_AMP4_Power, K39_SVLP_VBUS, -1);
		delay_ms(3);
		Retest_voltage_unstable_with_time_out(VBUS_FOVI, vbus_loop_5v_out, 4.0, 14.5, 10, 100, MEAS_V);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_loop_5v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
		}
#if 0
		FOR_EACH_VALID_SITE(site)
		{
			vbus_loop_5v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
			if (vbus_loop_5v_out[site]<11)
			{
				unsettle++;
				unsettle_flag[site] = 1;
			}
		}
		if (unsettle>0)
		{
			delay_ms(75);// 3ms for cbit close relay and 2ms for amp stable
			VBUS_FOVI.MeasureVI(215, 10);
			FOR_EACH_VALID_SITE(site)
			{
				vbus_loop_5v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
			}
		}
#endif

		I2CWriteSameData(DEV_ADDR, 0x0C, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0xE6);// 4.4+230*0.02=9V
		delay_ms(4);
		VBUS_FOVI.MeasureVI(215, 10);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_loop_9v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
		}


		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K62_AMP3_Power, K63_AMP4_Power, -1);
		delay_ms(3);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, -1);
		delay_ms(3);
		if (!TTR)
		{
			VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
			VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10UA, FOVIe_RELAY_ON);
			SCL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
			delay_ms(1);
			VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
			VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
			SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		}

		FOR_EACH_VALID_SITE(site)
		{
			VBUS_LP_BU_5V_Output->SetTestResult(site, 0, vbus_loop_5v_out[site]);
			VBUS_LP_BU_5V_Accuracy->SetTestResult(site, 0, (vbus_loop_5v_out[site] - 5) * 1e3);
			VBUS_LP_BU_9V_Output->SetTestResult(site, 0, vbus_loop_9v_out[site]);
			VBUS_LP_BU_9V_Accuracy->SetTestResult(site, 0, (vbus_loop_9v_out[site] - 9) * 1e3);
		}
	}




	return 0;
}

DUT_API int VBUS_LOOP_BO_ACCUR(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_LP_BO_4P6V_Output = StsGetParam(funcindex, "VBUS_LP_BO_4P6V_Output");
    CParam *VBUS_LP_BO_4P6V_Accuracy = StsGetParam(funcindex, "VBUS_LP_BO_4P6V_Accuracy");
    CParam *VBUS_LP_BO_5V_Output = StsGetParam(funcindex, "VBUS_LP_BO_5V_Output");
    CParam *VBUS_LP_BO_5V_Accuracy = StsGetParam(funcindex, "VBUS_LP_BO_5V_Accuracy");
    CParam *VBUS_LP_BO_9V_Output = StsGetParam(funcindex, "VBUS_LP_BO_9V_Output");
    CParam *VBUS_LP_BO_9V_Accuracy = StsGetParam(funcindex, "VBUS_LP_BO_9V_Accuracy");
    CParam *VBUS_LP_BO_12V_Output = StsGetParam(funcindex, "VBUS_LP_BO_12V_Output");
    CParam *VBUS_LP_BO_12V_Accuracy = StsGetParam(funcindex, "VBUS_LP_BO_12V_Accuracy");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	double vbus_loop_12v_out[SITE_NUM] = { 0 };
	double vbus_loop_9v_out[SITE_NUM] = { 0 };
	double vbus_loop_5v_out[SITE_NUM] = { 0 };
	double vbus_loop_4p6v_out[SITE_NUM] = { 0 };

	if (!TTR)
	{
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power, -1);
		delay_ms(3);
		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FI, -0.0001, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_ON);// minize amp output current range
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SCL_ACM.Set(FV, 1.8, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		delay_ms(5);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
		I2CWriteSameData(DEV_ADDR, 0x0C, 0x01);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0x7C);//12V
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(BUBO_MODE,1),(VBUS_VOL_SET_L,124),(VBUS_VOL_SET_H,1),(IBAT_LIMIT,7),(IBUS_SET,127),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(DIS_NTC_DETECTION_ANALOG,1)]
		I2CWriteSameData(DEV_ADDR, 0x56, 0x05);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x80);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
		delay_ms(1);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
		I2CWriteSameData(DEV_ADDR, 0x58, 0xA0);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		delay_ms(2);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power, K65_SVLP_VBUS, K43_INT_ACM, K58_INT_PU, -1);
		//VBUS_FOVI.MeasureVI(500, 50);
		delay_ms(5);// 3ms for cbit close relay and 2ms for amp stable
		VBUS_FOVI.MeasureVI(215, 10);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_loop_12v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
		}

		//=============Config for VBUS= 9V
		I2CWriteSameData(DEV_ADDR, 0x0C, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0xE6);// 4.4+230*0.02=9V
		delay_ms(2);
		VBUS_FOVI.MeasureVI(215, 10);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_loop_9v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
		}

		//=============Config for VBUS= 5V
		I2CWriteSameData(DEV_ADDR, 0x0C, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0x1E);// 4.4+30*0.02=5V
		delay_ms(2);
		VBUS_FOVI.MeasureVI(215, 10);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_loop_5v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
		}

		//=============Config for VBUS= 4.6V
		I2CWriteSameData(DEV_ADDR, 0x0C, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0x0A);// 4.4+10*0.02=4.6V
		delay_ms(2);
		VBUS_FOVI.MeasureVI(215, 10);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_loop_4p6v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
		}

		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(3);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10UA, FOVIe_RELAY_ON);
		SCL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);

		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	}
	else
	{
		double unsettle_flag[SITE_NUM] = { 0 };
		double unsettle = 0;
		NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power,/* K62_AMP3_Power,*/ K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(5);
		I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
		I2CWriteSameData(DEV_ADDR, 0x0C, 0x01);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0x7C);//12V
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
		delay_ms(2);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power, /*K62_AMP3_Power,*/ K65_SVLP_VBUS, K43_INT_ACM, K58_INT_PU, -1);
		NTC_FOVI.MeasureVI(500, 10);
		delay_ms(3);// 3ms for cbit close relay and 2ms for amp stable
		Retest_voltage_unstable_with_time_out(VBUS_FOVI, vbus_loop_12v_out, 11.0, 14.5, 10, 100, MEAS_V);
#if 0
		VBUS_FOVI.MeasureVI(215, 10);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_loop_12v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
			if (vbus_loop_12v_out[site]<11)
			{
				unsettle++;
				unsettle_flag[site] = 1;
			}
		}
		if (unsettle>0)
		{
			delay_ms(75);// 3ms for cbit close relay and 2ms for amp stable
			VBUS_FOVI.MeasureVI(215, 10);
			FOR_EACH_VALID_SITE(site)
			{
				vbus_loop_12v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
			}
		}
#endif

		//=============Config for VBUS= 9V
		I2CWriteSameData(DEV_ADDR, 0x0C, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0xE6);// 4.4+230*0.02=9V
		delay_ms(2);
		VBUS_FOVI.MeasureVI(215, 10);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_loop_9v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
		}

		//=============Config for VBUS= 5V
		I2CWriteSameData(DEV_ADDR, 0x0C, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0x1E);// 4.4+30*0.02=5V
		delay_ms(2);
		VBUS_FOVI.MeasureVI(215, 10);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_loop_5v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
		}

		//=============Config for VBUS= 4.6V
		I2CWriteSameData(DEV_ADDR, 0x0C, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x0D, 0x0A);// 4.4+10*0.02=4.6V
		delay_ms(2);
		VBUS_FOVI.MeasureVI(215, 10);
		FOR_EACH_VALID_SITE(site)
		{
			vbus_loop_4p6v_out[site] = VBUS_FOVI.GetMeasResult(site, MVRET);//mV
		}


		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K61_AMP2_Power, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(5);
		cbite.SetOn(K30_VBAT_Cap, K54_QPoint, K25_VCC_Cap, K43_INT_ACM, K58_INT_PU, -1);
		delay_ms(15);// off delay 15ms
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_10UA, FOVIe_RELAY_ON);
		SCL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}


	if (!check_relay_off(VBUS_FOVI, K54_QPoint, K65_SVLP_VBUS, &Relay_Off_Check))
	{
		FOR_EACH_VALID_SITE(site)
		{
			VBUS_LP_BO_4P6V_Output->SetTestResult(site, 0, 99979);
			VBUS_LP_BO_4P6V_Accuracy->SetTestResult(site, 0, 99979);
			VBUS_LP_BO_5V_Output->SetTestResult(site, 0, 99979);
			VBUS_LP_BO_5V_Accuracy->SetTestResult(site, 0, 99979);
			VBUS_LP_BO_9V_Output->SetTestResult(site, 0, 99979);
			VBUS_LP_BO_9V_Accuracy->SetTestResult(site, 0, 99979);
			VBUS_LP_BO_12V_Output->SetTestResult(site, 0, 99979);
			VBUS_LP_BO_12V_Accuracy->SetTestResult(site, 0, 99979);
		}
	}
	else
	{
		FOR_EACH_VALID_SITE(site)
		{
			VBUS_LP_BO_4P6V_Output->SetTestResult(site, 0, vbus_loop_4p6v_out[site]);
			VBUS_LP_BO_4P6V_Accuracy->SetTestResult(site, 0, (vbus_loop_4p6v_out[site] - 4.6) * 1e3);
			VBUS_LP_BO_5V_Output->SetTestResult(site, 0, vbus_loop_5v_out[site]);
			VBUS_LP_BO_5V_Accuracy->SetTestResult(site, 0, (vbus_loop_5v_out[site] - 5) * 1e3);
			VBUS_LP_BO_9V_Output->SetTestResult(site, 0, vbus_loop_9v_out[site]);
			VBUS_LP_BO_9V_Accuracy->SetTestResult(site, 0, (vbus_loop_9v_out[site] - 9)  * 1e3);
			VBUS_LP_BO_12V_Output->SetTestResult(site, 0, vbus_loop_12v_out[site]);
			VBUS_LP_BO_12V_Accuracy->SetTestResult(site, 0, (vbus_loop_12v_out[site] - 12)  * 1e3);
		}
	}

	return 0;
}

DUT_API int IBUS_SNS_ACCUR_BU(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IBUS_SNS_ACCUR_BU_0P2A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_BU_0P2A");
    CParam *IBUS_SNS_ACCUR_BU_0P4A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_BU_0P4A");
    CParam *IBUS_SNS_ACCUR_BU_1A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_BU_1A");
    CParam *IBUS_SNS_ACCUR_BU_2A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_BU_2A");
    CParam *IBUS_SNS_ACCUR_BU_4A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_BU_4A");
    CParam *IBUS_SNS_Gain_BUCK = StsGetParam(funcindex, "IBUS_SNS_Gain_BUCK");
    CParam *IBUS_SNS_Offset_BUCK = StsGetParam(funcindex, "IBUS_SNS_Offset_BUCK");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	double Vcs_qrb_buck_0p2A[SITE_NUM] = { 0 };
	double Vcs_qrb_buck_0p4A[SITE_NUM] = { 0 };
	double Vcs_qrb_buck_1A[SITE_NUM] = { 0 };
	double Vcs_qrb_buck_2A[SITE_NUM] = { 0 };
	double Vcs_qrb_buck_3A[SITE_NUM] = { 0 };
	double Vcs_qrb_buck_gain[SITE_NUM] = { 0 };
	double Vcs_qrb_buck_offset[SITE_NUM] = { 0 };
	cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 1.6, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 1.6, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xCE);
	I2CWriteSameData(DEV_ADDR, 0x57, 0x07);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
	//		field[(WAKE_UP,1),(EN_ATEST0,1),(ATEST0_MUX,25),(EN_ATEST1,1),(ATEST1_MUX,7),(DIS_NTC_DETECTION_ANALOG,1))]
	delay_ms(1);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(100);
	//------------------0.2A Current for voltage measurement
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(100);
	FPVI.Set(FI, 0.2, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(2000);
	AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_us(3000);
	//ATEST_GRP.MeasureVI(215, 10);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_qrb_buck_0p2A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(100);

	//------------------0.4A Current for voltage measurement
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(100);
	FPVI.Set(FI, 0.4, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(2000);
	//ATEST_GRP.MeasureVI(215, 10);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(3000);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_qrb_buck_0p4A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}

	//------------------1A Current for voltage measurement
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_us(100);
	FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_us(2000);
	//ATEST_GRP.MeasureVI(215, 10);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(2000);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_qrb_buck_1A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
		Vcs_qrb_sns_buck_1A[site] = Vcs_qrb_buck_1A[site];
	}

	//------------------2A Current for voltage measurement
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(2000);
	//ATEST_GRP.MeasureVI(215, 10);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(2000);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_qrb_buck_2A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
		Vcs_qrb_sns_buck_2A[site] = Vcs_qrb_buck_2A[site];
	}

	//------------------3A Current for voltage measurement
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(2000);
	//ATEST_GRP.MeasureVI(215, 10);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_qrb_buck_3A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
		Vcs_qrb_sns_buck_3A[site] = Vcs_qrb_buck_3A[site];
		Vcs_qrb_buck_gain[site] = (Vcs_qrb_buck_3A[site] - Vcs_qrb_buck_1A[site]) / 2;
		Vcs_qrb_buck_offset[site] = Vcs_qrb_buck_3A[site] - Vcs_qrb_buck_gain[site] * 3;
	}

	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
		VBUS_FOVI.Set(FI, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
	}

	FOR_EACH_VALID_SITE(site)
	{
		IBUS_SNS_ACCUR_BU_0P2A->SetTestResult(site, 0, 100 * (Vcs_qrb_buck_0p2A[site] - 0.04) / 0.04);
		IBUS_SNS_ACCUR_BU_0P4A->SetTestResult(site, 0, 100 * (Vcs_qrb_buck_0p4A[site] - 0.08) / 0.08);
		IBUS_SNS_ACCUR_BU_1A->SetTestResult(site, 0, 100 * (Vcs_qrb_buck_1A[site] - 0.2) / 0.2);
		IBUS_SNS_ACCUR_BU_2A->SetTestResult(site, 0, 100 * (Vcs_qrb_buck_2A[site] - 0.4) / 0.4);
		IBUS_SNS_ACCUR_BU_4A->SetTestResult(site, 0, 100 * (Vcs_qrb_buck_3A[site] - 0.6) / 0.6);
		IBUS_SNS_Gain_BUCK->SetTestResult(site, 0, Vcs_qrb_buck_gain[site] * 1e3);//mohm
		IBUS_SNS_Offset_BUCK->SetTestResult(site, 0, Vcs_qrb_buck_offset[site] * 1e3);//mV
	}

	return 0;
}

DUT_API int IBUS_SNS_ACCUR_BO(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IBUS_SNS_ACCUR_BO_0P2A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_BO_0P2A");
    CParam *IBUS_SNS_ACCUR_BO_0P4A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_BO_0P4A");
    CParam *IBUS_SNS_ACCUR_BO_1A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_BO_1A");
    CParam *IBUS_SNS_ACCUR_BO_2A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_BO_2A");
    CParam *IBUS_SNS_ACCUR_BO_4A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_BO_4A");
    CParam *IBUS_SNS_ACCUR_REF_1A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_REF_1A");
    CParam *IBUS_SNS_ACCUR_REF_2A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_REF_2A");
    CParam *IBUS_SNS_ACCUR_REF_4A = StsGetParam(funcindex, "IBUS_SNS_ACCUR_REF_4A");
    CParam *IBUS_SNS_Gain_BOOST = StsGetParam(funcindex, "IBUS_SNS_Gain_BOOST");
    CParam *IBUS_SNS_Offset_BOOST = StsGetParam(funcindex, "IBUS_SNS_Offset_BOOST");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	double Vcs_qrb_boost_0p2A[SITE_NUM] = { 0 };
	double Vcs_qrb_boost_0p4A[SITE_NUM] = { 0 };
	double Vcs_qrb_boost_1A[SITE_NUM] = { 0 };
	double Vcs_qrb_boost_2A[SITE_NUM] = { 0 };
	double Vcs_qrb_boost_3A[SITE_NUM] = { 0 };
	double Vcs_qrb_boost_gain[SITE_NUM] = { 0 };
	double Vcs_qrb_boost_offset[SITE_NUM] = { 0 };

	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 1.6, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 1.6, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
	}
	else
	{
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(1);
	}
	//field[(WAKE_UP,1),(EN_ATEST0,1),(ATEST0_MUX,25),(EN_ATEST1,1),(ATEST1_MUX,7),(DIS_NTC_DETECTION_ANALOG,1),(BUBO_MODE,1)]
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xCE);
	I2CWriteSameData(DEV_ADDR, 0x57, 0x07);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
	delay_ms(1);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(100);
	//------------------0.2A Current for voltage measurement
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(100);
	FPVI.Set(FI, -0.2, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_us(3000);
	//ATEST_GRP.MeasureVI(215, 10);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	FOR_EACH_VALID_SITE(site)
	{
		Vcs_qrb_boost_0p2A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}

	//------------------0.4A Current for voltage measurement
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(100);
	FPVI.Set(FI, -0.4, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(2000);
	ATEST_GRP.MeasureVI(215, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_qrb_boost_0p4A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}

	//------------------1A Current for voltage measurement
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_us(100);
	FPVI.Set(FI, -1, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_us(2000);
	//ATEST_GRP.MeasureVI(215, 10);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_qrb_boost_1A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
		Vcs_qrb_sns_boost_1A[site] = Vcs_qrb_boost_1A[site];
	}

	//------------------2A Current for voltage measurement
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, -2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(2000);
	//ATEST_GRP.MeasureVI(215, 10);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_qrb_boost_2A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
		Vcs_qrb_sns_boost_2A[site] = Vcs_qrb_boost_2A[site];
	}

	//------------------3A Current for voltage measurement
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, -3, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(2000);
	//ATEST_GRP.MeasureVI(215, 10);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_qrb_boost_3A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
		Vcs_qrb_sns_boost_3A[site] = Vcs_qrb_boost_3A[site];
	}
	delay_us(1000);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_qrb_boost_3A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
		Vcs_qrb_boost_gain[site] = (Vcs_qrb_boost_3A[site] - Vcs_qrb_boost_1A[site]) / 2;
		Vcs_qrb_boost_offset[site] = Vcs_qrb_boost_3A[site] - Vcs_qrb_boost_gain[site] * 3;
	}

	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
#if 0
	double ibus_sns_acc_ref_1a[SITE_NUM] = { 0 };
	double ibus_sns_acc_ref_2a[SITE_NUM] = { 0 };
	double ibus_sns_acc_ref_4a[SITE_NUM] = { 0 };
	I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x0B);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);//		field[(WAKE_UP,1),(BUBO_MODE,0),(IBAT_LIMIT,7),(IBUS_SET,11),(VBUS_LOOP_DISABLE,1)]
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x57, 0x07);//		field[(EN_ATEST1,1),(ATEST1_MUX,7)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xC6);//		field[(EN_ATEST0,1),(ATEST0_MUX,24)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0x04);//		field[(D2A_BUBO_TM_DIS_BST_UVLO_LOCAL,1)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xC7);//		field[(EN_I2C_CTRL,1)]
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0x24);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x11);//-----IBUS_Set=1A: 0.15A +17*50mA
	delay_ms(5);
	ATEST_GRP.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		ibus_sns_acc_ref_1a[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}

	I2CWriteSameData(DEV_ADDR, 0x0E, 0x25);//-----IBUS_Set=2A: 0.15A +37*50mA
	delay_ms(5);
	ATEST_GRP.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		ibus_sns_acc_ref_2a[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}

	I2CWriteSameData(DEV_ADDR, 0x0E, 0x4D);//-----IBUS_Set=4A: 0.15A +77*50mA
	delay_ms(5);
	ATEST_GRP.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		ibus_sns_acc_ref_4a[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}
#endif
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		PMID_FOVI.Set(FI, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	}

	FOR_EACH_VALID_SITE(site)
	{
		IBUS_SNS_ACCUR_BO_0P2A->SetTestResult(site, 0, 100 * (Vcs_qrb_boost_0p2A[site] - 0.04) / 0.04);
		IBUS_SNS_ACCUR_BO_0P4A->SetTestResult(site, 0, 100 * (Vcs_qrb_boost_0p4A[site] - 0.08) / 0.08);
		IBUS_SNS_ACCUR_BO_1A->SetTestResult(site, 0, 100 * (Vcs_qrb_boost_1A[site] - 0.2) / 0.2);
		IBUS_SNS_ACCUR_BO_2A->SetTestResult(site, 0, 100 * (Vcs_qrb_boost_2A[site] - 0.4) / 0.4);
		IBUS_SNS_ACCUR_BO_4A->SetTestResult(site, 0, 100 * (Vcs_qrb_boost_3A[site] - 0.6) / 0.6);
		//IBUS_SNS_ACCUR_REF_1A->SetTestResult(site, 0, 100 * (ibus_sns_acc_ref_1a[site] - 0.2) / 0.2);
		//IBUS_SNS_ACCUR_REF_2A->SetTestResult(site, 0, 100 * (ibus_sns_acc_ref_2a[site] - 0.4) / 0.4);
		//IBUS_SNS_ACCUR_REF_4A->SetTestResult(site, 0, 100 * (ibus_sns_acc_ref_4a[site] - 0.8) / 0.8);
		IBUS_SNS_Gain_BOOST->SetTestResult(site, 0, Vcs_qrb_boost_gain[site] * 1e3);//mohm
		IBUS_SNS_Offset_BOOST->SetTestResult(site, 0, Vcs_qrb_boost_offset[site] * 1e3);//mV
	}


	return 0;
}

DUT_API int IBUS_LOOP_ACC(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IBUS_EA_LP_ACC_1A = StsGetParam(funcindex, "IBUS_EA_LP_ACC_1A");
    CParam *IBUS_EA_LP_ACC_2A = StsGetParam(funcindex, "IBUS_EA_LP_ACC_2A");
    CParam *IBUS_EA_LP_ACC_3A = StsGetParam(funcindex, "IBUS_EA_LP_ACC_3A");
    CParam *IBUS_LOOP_1A_ACCUR = StsGetParam(funcindex, "IBUS_LOOP_1A_ACCUR");
    CParam *IBUS_LOOP_2A_ACCUR = StsGetParam(funcindex, "IBUS_LOOP_2A_ACCUR");
    CParam *IBUS_LOOP_3A_ACCUR = StsGetParam(funcindex, "IBUS_LOOP_3A_ACCUR");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	//-------LOOP 测试时候, VCS mux -->AMUX, IBUS_Ref mux---->NTC,  config ox0E to select IBUS_ref option,  ideally AMUX-NTC=0mV
	//1A loop accuracy: force 1A current, config 1A reference, measure AMUX and NTC to get vcs_1A and IBUS_ref_1A, calculates: vcs_1A-IBUS_ref_1A, then calculate the error percent

	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);

	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	double Ibus_ea_offset_1A[SITE_NUM] = { 0 };
	double Ibus_ea_offset_2A[SITE_NUM] = { 0 };
	double Ibus_ea_offset_3A[SITE_NUM] = { 0 };

	cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K31_BUSL_PMID, K16_VBUS_Cap, K30_VBAT_Cap, K32_PMID_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap, -1);
	delay_ms(3);
	//cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K16_VBUS_Cap, K30_VBAT_Cap, K31_BUSL_PMID, K3_QVMH_NTC_SEL, K25_VCC_Cap, -1);
	//delay_ms(3);
	VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VCC_ACM.Set(FV, 4.55, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x11);//
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);//		field[(WAKE_UP,1),(BUBO_MODE,0),(IBAT_LIMIT,7),(IBUS_SET,37),(VBUS_LOOP_DISABLE,1)]
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);//		field[(EN_ATEST1,1),(D2A_BUBO_ATEST1,5)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xCE);//		field[(EN_ATEST0,1),(ATEST0_MUX,25)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0x04);//		field[(D2A_BUBO_TM_DIS_BST_UVLO_LOCAL,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xCF);//		field[(EN_I2C_CTRL,1)]
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0x24);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	delay_ms(2);

	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_ms(1);
	//------------------------1A
	FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Ibus_ea_offset_1A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}

	//-----------------------2A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x25);// 37*50+150mA=2000mA
	delay_ms(1);
	FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(5);
	FOR_EACH_VALID_SITE(site)
	{
		Ibus_ea_offset_2A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}

	//-----------------------3A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x39);//----57*50mA+150mA=3000mA
	delay_ms(1);
	FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Ibus_ea_offset_3A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}

	//FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	//FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	//FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	//AMUX_FOVI.Set(FV, 0, FOVIe_1V, FOVIe_10UA, FOVIe_RELAY_ON);
	//NTC_FOVI.Set(FV, 0, FOVIe_1V, FOVIe_10UA, FOVIe_RELAY_ON);
	//AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	//NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);



#if 0
	cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K31_BUSL_PMID, K16_VBUS_Cap,K30_VBAT_Cap, K32_PMID_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap, -1);
	delay_ms(3);
	//cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K16_VBUS_Cap, K30_VBAT_Cap, K31_BUSL_PMID, K25_VCC_Cap, -1);
	//delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x0A, 0x07);//---CV=4.5V
	I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x11);//1A
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);//		field[(WAKE_UP,1),(BUBO_MODE,0),(IBAT_LIMIT,7),(IBUS_SET,37),(VBUS_LOOP_DISABLE,1)]
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);//		field[(EN_ATEST1,1),(D2A_BUBO_ATEST1,5)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xCE);//		field[(EN_ATEST0,1),(ATEST0_MUX,25)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0x04);//		field[(D2A_BUBO_TM_DIS_BST_UVLO_LOCAL,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xCF);//		field[(EN_I2C_CTRL,1)]
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0x24);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	delay_ms(2);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_ms(1);
	//------------------------1A
	FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_ms(2);
	ATEST_GRP.MeasureVI(215, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Ibus_ea_offset_1A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}
	//-----------------------2A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x25);// 37*50+150mA=2000mA
	delay_ms(1);
	FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_ms(2);
	ATEST_GRP.MeasureVI(215, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(5);
	FOR_EACH_VALID_SITE(site)
	{
		Ibus_ea_offset_2A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}


	//-----------------------3A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x39);//----57*50mA+150mA=3000mA
	delay_ms(1);
	FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_ms(2);
	ATEST_GRP.MeasureVI(215, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Ibus_ea_offset_3A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}
#endif
	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_1V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_1V, FOVIe_10UA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_200MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VCC_ACM.Set(FV, 4.55, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		IBUS_EA_LP_ACC_1A->SetTestResult(site, 0, Ibus_ea_offset_1A[site]*1e3);//PCNT
		IBUS_EA_LP_ACC_2A->SetTestResult(site, 0, Ibus_ea_offset_2A[site] * 1e3);//PCNT
		IBUS_EA_LP_ACC_3A->SetTestResult(site, 0, Ibus_ea_offset_3A[site]*1e3);//PCNT

		IBUS_LOOP_1A_ACCUR->SetTestResult(site, 0, 1e3*(Vcs_qrb_sns_boost_1A[site] + Ibus_ea_offset_1A[site]) / 0.2);//mA
		IBUS_LOOP_2A_ACCUR->SetTestResult(site, 0, 1e3*(Vcs_qrb_sns_boost_2A[site] + Ibus_loop_Voffset_2A[site]) / 0.2);//mA
		IBUS_LOOP_3A_ACCUR->SetTestResult(site, 0, 1e3*(Vcs_qrb_sns_boost_3A[site] + Ibus_ea_offset_3A[site]) / 0.2);//mA
	}

	return 0;
}

DUT_API int IBUS_TERM(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IBUS_TERM_200mA_Rise = StsGetParam(funcindex, "IBUS_TERM_200mA_Rise");
    CParam *IBUS_TERM_200mA_Fall = StsGetParam(funcindex, "IBUS_TERM_200mA_Fall");
    CParam *IBUS_TERM_200mA_Hys = StsGetParam(funcindex, "IBUS_TERM_200mA_Hys");
    CParam *IBUS_TERM_400mA_Rise = StsGetParam(funcindex, "IBUS_TERM_400mA_Rise");
    CParam *IBUS_TERM_400mA_Fall = StsGetParam(funcindex, "IBUS_TERM_400mA_Fall");
    CParam *IBUS_TERM_400mA_Hys = StsGetParam(funcindex, "IBUS_TERM_400mA_Hys");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double ibus_term_r[200] = { 0.0 };
	double ibus_term_f[200] = { 0.0 };
	double Trig = 2.5;
	int Trig_Point[SITE_NUM] = { 0 };
	double ibus_term_200mA_rise[SITE_NUM] = { 0 };
	double ibus_term_200mA_fall[SITE_NUM] = { 0 };
	double ibus_term_200mA_hys[SITE_NUM] = { 0 };
	double ibus_term_400mA_rise[SITE_NUM] = { 0 };
	double ibus_term_400mA_fall[SITE_NUM] = { 0 };
	double ibus_term_400mA_hys[SITE_NUM] = { 0 };

	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K15_BUSH_VBUS, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x0A, 0x00);//---CV=4.5V
		I2CWriteSameData(DEV_ADDR, 0x56, 0x01);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x55, 0x99);//		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,25)]
		I2CWriteSameData(DEV_ADDR, 0xF5, 0x40);//		field[(TRIM_IBUS_OFF_TERM_FLT,1)]
		I2CWriteSameData(DEV_ADDR, 0x0B, 0x07);//		field[(ITERM,7)], 200mA
		I2CWriteSameData(DEV_ADDR, 0x58, 0x20);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
		delay_ms(1);
	}
	else
	{
		SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		I2CWriteSameData(DEV_ADDR, 0x0A, 0x00);//---CV=4.5V
		I2CWriteSameData(DEV_ADDR, 0x0B, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x00);//1A
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x0A, 0x00);//---CV=4.5V
		I2CWriteSameData(DEV_ADDR, 0x56, 0x01);
		I2CWriteSameData(DEV_ADDR, 0x57, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x55, 0x99);//		field[(WAKE_UP,1),(EN_DTEST0,1),(DTEST0_MUX,25)]
		I2CWriteSameData(DEV_ADDR, 0xF5, 0x40);//		field[(TRIM_IBUS_OFF_TERM_FLT,1)]
		I2CWriteSameData(DEV_ADDR, 0x0B, 0x07);//		field[(ITERM,7)], 200mA
		I2CWriteSameData(DEV_ADDR, 0x58, 0x20);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
		delay_ms(1);
	}

	STSAWGCreateRampData(&ibus_term_r[0], sam, 1, 0.195, 0.395);// PMID-->SW
	FPVI.AwgClear();
	FPVI.AwgLoader("ibus_term_r_pattern", FI, FPVIe_1V, FPVIe_1A, ibus_term_r, sam);
	FPVI.AwgSelect("ibus_term_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	FPVI.Set(FI, 0.19, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		ibus_term_200mA_rise[site] = abs(FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]))*1e3;  //Read the voltage value on trigger position, mA
		check_awg_trigger_point(Trig_Point, sam, ibus_term_200mA_rise,site);// add for AWG trigger check
	}

	FPVI.Set(FI, 0.35, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&ibus_term_f[0], sam, 1, 0.295, 0.105);// PMID-->SW
	FPVI.AwgClear();
	FPVI.AwgLoader("ibus_term_f_pattern", FI, FPVIe_1V, FPVIe_1A, ibus_term_f, sam);
	FPVI.AwgSelect("ibus_term_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		ibus_term_200mA_fall[site] = abs(FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]))*1e3;  //Read the voltage value on trigger position, mA
		ibus_term_200mA_hys[site] = ibus_term_200mA_rise[site] - ibus_term_200mA_fall[site];
		check_awg_trigger_point(Trig_Point, sam, ibus_term_200mA_fall,site);// add for AWG trigger check
	}


	I2CWriteSameData(DEV_ADDR, 0x0B, 1, 15);//		field[(ITERM,15)], 400mA
	delay_ms(1);
	STSAWGCreateRampData(&ibus_term_r[0], sam, 1, 0.405, 0.595);// PMID-->SW
	FPVI.AwgClear();
	FPVI.AwgLoader("ibus_term_r_pattern", FI, FPVIe_1V, FPVIe_1A, ibus_term_r, sam);
	FPVI.AwgSelect("ibus_term_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	FPVI.Set(FI, 0.4, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		ibus_term_400mA_rise[site] = abs(FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]))*1e3;  //Read the voltage value on trigger position, mA
		check_awg_trigger_point(Trig_Point, sam, ibus_term_400mA_rise,site);// add for AWG trigger check
	}

	FPVI.Set(FI, 0.55, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&ibus_term_f[0], sam, 1, 0.495, 0.305);// PMID-->SW
	FPVI.AwgClear();
	FPVI.AwgLoader("ibus_term_f_pattern", FI, FPVIe_1V, FPVIe_1A, ibus_term_f, sam);
	FPVI.AwgSelect("ibus_term_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT); //Get the position of trigger point
		ibus_term_400mA_fall[site] = abs(FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]))*1e3;  //Read the voltage value on trigger position, mA
		ibus_term_400mA_hys[site] = ibus_term_400mA_rise[site] - ibus_term_400mA_fall[site];
		check_awg_trigger_point(Trig_Point, sam, ibus_term_400mA_fall,site);// add for AWG trigger check
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FI, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	}

	FOR_EACH_VALID_SITE(site)
	{
		IBUS_TERM_200mA_Rise->SetTestResult(site, 0, ibus_term_200mA_rise[site]);
		IBUS_TERM_200mA_Fall->SetTestResult(site, 0, ibus_term_200mA_fall[site]);
		IBUS_TERM_200mA_Hys->SetTestResult(site, 0, ibus_term_200mA_hys[site]);
		IBUS_TERM_400mA_Rise->SetTestResult(site, 0, ibus_term_400mA_rise[site]);
		IBUS_TERM_400mA_Fall->SetTestResult(site, 0, ibus_term_400mA_fall[site]);
		IBUS_TERM_400mA_Hys->SetTestResult(site, 0, ibus_term_400mA_hys[site]);
	}

	return 0;
}

DUT_API int IBAT_CC_LOOP_OS_ACCUR(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IBAT_CC_LP_OS_BU_2A = StsGetParam(funcindex, "IBAT_CC_LP_OS_BU_2A");
    CParam *IBAT_CC_LP_OS_BU_3A = StsGetParam(funcindex, "IBAT_CC_LP_OS_BU_3A");
    CParam *IBAT_CC_LP_OS_BU_4A = StsGetParam(funcindex, "IBAT_CC_LP_OS_BU_4A");
    CParam *IBAT_CC_LP_OS_BU_6A = StsGetParam(funcindex, "IBAT_CC_LP_OS_BU_6A");
    CParam *IBAT_CC_LP_OS_BO_2A = StsGetParam(funcindex, "IBAT_CC_LP_OS_BO_2A");
    CParam *IBAT_CC_LP_OS_BO_3A = StsGetParam(funcindex, "IBAT_CC_LP_OS_BO_3A");
    CParam *IBAT_CC_LP_OS_BO_4A = StsGetParam(funcindex, "IBAT_CC_LP_OS_BO_4A");
    CParam *IBAT_CC_LP_OS_BO_6A = StsGetParam(funcindex, "IBAT_CC_LP_OS_BO_6A");
    CParam *IBAT_CC_LP_OS_BO_8A = StsGetParam(funcindex, "IBAT_CC_LP_OS_BO_8A");
    CParam *IBAT_CC_LP_OS_BU_2A_ACCUR = StsGetParam(funcindex, "IBAT_CC_LP_OS_BU_2A_ACCUR");
    CParam *IBAT_CC_LP_OS_BU_3A_ACCUR = StsGetParam(funcindex, "IBAT_CC_LP_OS_BU_3A_ACCUR");
    CParam *IBAT_CC_LP_OS_BU_4A_ACCUR = StsGetParam(funcindex, "IBAT_CC_LP_OS_BU_4A_ACCUR");
    CParam *IBAT_CC_LP_OS_BU_6A_ACCUR = StsGetParam(funcindex, "IBAT_CC_LP_OS_BU_6A_ACCUR");
    CParam *IBAT_CC_LP_OS_BO_2A_ACCUR = StsGetParam(funcindex, "IBAT_CC_LP_OS_BO_2A_ACCUR");
    CParam *IBAT_CC_LP_OS_BO_3A_ACCUR = StsGetParam(funcindex, "IBAT_CC_LP_OS_BO_3A_ACCUR");
    CParam *IBAT_CC_LP_OS_BO_4A_ACCUR = StsGetParam(funcindex, "IBAT_CC_LP_OS_BO_4A_ACCUR");
    CParam *IBAT_CC_LP_OS_BO_6A_ACCUR = StsGetParam(funcindex, "IBAT_CC_LP_OS_BO_6A_ACCUR");
    CParam *IBAT_CC_LP_OS_BO_8A_ACCUR = StsGetParam(funcindex, "IBAT_CC_LP_OS_BO_8A_ACCUR");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	//---------AMUX=CSTOP_VSNS_IBAT
	//---------NTC = IBATSNS_IABT_REF. offset should be NTC-AMUX, if NTC >AMUX, means loop will large than sense, 
	cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K32_PMID_Cap, K28_VDRV_Cap, K25_VCC_Cap, -1);
	delay_ms(3);
	BTST_ACM.Set(FV,3, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	SW_ACM.Set(FV, 3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 3.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);	
	delay_ms(1);
	AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);//Ibus_limit_off
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);//		field[(WAKE_UP,1)
	I2CWriteSameData(DEV_ADDR, 0x56, 0x06);//(EN_ATEST1,1),(EN_ATEST0,1),
	I2CWriteSameData(DEV_ADDR, 0x57, 0x0F);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x40);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x0D);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x07);
	I2CWriteSameData(DEV_ADDR, 0x58, 0xA0);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x58, 0xE0);//		field[(D2A_BUBO_TM_DIS_CLK,1)], enbubo but dis bubo clk
	delay_us(200);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0xFD);//		field[(D2A_BUBO_ATEST1,15)]
	delay_us(200);
	BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	SW_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_us(200);
	BTST_ACM.Set(FV, 9, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(2);
	//---------------2A
	I2CWriteSameData(DEV_ADDR, 0x0B, 1, 0x00);// IBAT_LIMIT=2A
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Ibat_cc_lp_os_buck_2a[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	//---------------3A
	I2CWriteSameData(DEV_ADDR, 0x0B, 1, 0x20);// IBAT_LIMIT=3A
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Ibat_cc_lp_os_buck_3a[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}
	//---------------4A
	I2CWriteSameData(DEV_ADDR, 0x0B, 1, 0x40);// IBAT_LIMIT=4A
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Ibat_cc_lp_os_buck_4a[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}
	//---------------6A
	I2CWriteSameData(DEV_ADDR, 0x0B, 1, 0x60);// IBAT_LIMIT=6A
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Ibat_cc_lp_os_buck_6a[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);//BUBO_MODE=1
	I2CWriteSameData(DEV_ADDR, 0x58, 0xE0);
	//---------------2A
	I2CWriteSameData(DEV_ADDR, 0x0B, 1, 0x00);// IBAT_LIMIT=2A
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Ibat_cc_lp_os_boost_2a[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	//---------------3A
	I2CWriteSameData(DEV_ADDR, 0x0B, 1, 0x20);// IBAT_LIMIT=3A
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Ibat_cc_lp_os_boost_3a[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	//---------------4A
	I2CWriteSameData(DEV_ADDR, 0x0B, 1, 0x40);// IBAT_LIMIT=4A
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Ibat_cc_lp_os_boost_4a[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}
	//---------------6A
	I2CWriteSameData(DEV_ADDR, 0x0B, 1, 0x60);// IBAT_LIMIT=6A
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Ibat_cc_lp_os_boost_6a[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}
	//---------------8A
	I2CWriteSameData(DEV_ADDR, 0x0B, 1, 0x80);// IBAT_LIMIT=8A
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Ibat_cc_lp_os_boost_8a[site] = NTC_FOVI.GetMeasResult(site, MVRET) - AMUX_FOVI.GetMeasResult(site, MVRET);
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		FPVI.Set(FV, 0, FPVIe_20V, FPVIe_100MA, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10MA, FOVIe_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10MA, FOVIe_RELAY_OFF);
	}
	else
	{
		BTST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}

	FOR_EACH_VALID_SITE(site)
	{
		IBAT_CC_LP_OS_BU_2A->SetTestResult(site, 0, Ibat_cc_lp_os_buck_2a[site] * 1e3);//mV
		IBAT_CC_LP_OS_BU_3A->SetTestResult(site, 0, Ibat_cc_lp_os_buck_3a[site] * 1e3);//mV
		IBAT_CC_LP_OS_BU_4A->SetTestResult(site, 0, Ibat_cc_lp_os_buck_4a[site] * 1e3);//mV
		IBAT_CC_LP_OS_BU_6A->SetTestResult(site, 0, Ibat_cc_lp_os_buck_6a[site] * 1e3);//mV
		IBAT_CC_LP_OS_BO_2A->SetTestResult(site, 0, Ibat_cc_lp_os_boost_2a[site] * 1e3);//mV
		IBAT_CC_LP_OS_BO_3A->SetTestResult(site, 0, Ibat_cc_lp_os_boost_3a[site] * 1e3);//mV
		IBAT_CC_LP_OS_BO_4A->SetTestResult(site, 0, Ibat_cc_lp_os_boost_4a[site] * 1e3);//mV
		IBAT_CC_LP_OS_BO_6A->SetTestResult(site, 0, Ibat_cc_lp_os_boost_6a[site] * 1e3);//mV
		IBAT_CC_LP_OS_BO_8A->SetTestResult(site, 0, Ibat_cc_lp_os_boost_8a[site] * 1e3);//mV
		IBAT_CC_LP_OS_BU_2A_ACCUR->SetTestResult(site, 0, 2 + Ibat_cc_lp_os_buck_2a[site] / 0.1);
		IBAT_CC_LP_OS_BU_3A_ACCUR->SetTestResult(site, 0, 3+ Ibat_cc_lp_os_buck_3a[site] / 0.1);
		IBAT_CC_LP_OS_BU_4A_ACCUR->SetTestResult(site, 0, 4 + Ibat_cc_lp_os_buck_4a[site] / 0.1);
		IBAT_CC_LP_OS_BU_6A_ACCUR->SetTestResult(site, 0, 6 + Ibat_cc_lp_os_buck_6a[site] / 0.1);
		IBAT_CC_LP_OS_BO_2A_ACCUR->SetTestResult(site, 0, 2 + Ibat_cc_lp_os_boost_2a[site] / 0.1);
		IBAT_CC_LP_OS_BO_3A_ACCUR->SetTestResult(site, 0, 3+ Ibat_cc_lp_os_boost_3a[site] / 0.1);
		IBAT_CC_LP_OS_BO_4A_ACCUR->SetTestResult(site, 0, 4 + Ibat_cc_lp_os_boost_4a[site] / 0.1);
		IBAT_CC_LP_OS_BO_6A_ACCUR->SetTestResult(site, 0, 6 + Ibat_cc_lp_os_boost_6a[site] / 0.1);
		IBAT_CC_LP_OS_BO_8A_ACCUR->SetTestResult(site, 0, 8 + Ibat_cc_lp_os_boost_8a[site] / 0.1);
	}


	return 0;
}

DUT_API int IBAT_CC_LOOP_ACCUR_BU(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IBAT_SNS_CC_ACCUR_BU_1A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BU_1A");
    CParam *IBAT_SNS_CC_ACCUR_BU_2A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BU_2A");
    CParam *IBAT_SNS_CC_ACCUR_BU_3A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BU_3A");
    CParam *IBAT_SNS_CC_ACCUR_BU_4A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BU_4A");
    CParam *IBAT_SNS_CC_ACCUR_BU_6A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BU_6A");
    CParam *IBAT_SNS_CC_ACCUR_BU_8A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BU_8A");
    CParam *IBAT_SNS_CC_ACCUR_BU_10A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BU_10A");
    CParam *IBAT_LOOP_CC_ACCUR_BU_2A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BU_2A");
    CParam *IBAT_LOOP_CC_ACCUR_BU_3A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BU_3A");
    CParam *IBAT_LOOP_CC_ACCUR_BU_4A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BU_4A");
    CParam *IBAT_LOOP_CC_ACCUR_BU_6A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BU_6A");
    CParam *IBAT_LOOP_CC_ACCUR_BU_8A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BU_8A");
    CParam *IBAT_LOOP_CC_ACCUR_BU_10A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BU_10A");
    CParam *IBAT_LOOP_CC_ACCUR_BU_12A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BU_12A");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	double Vcs_hsfet_1A[SITE_NUM] = { 0 };
	double Vcs_hsfet_2A[SITE_NUM] = { 0 };
	double Vcs_hsfet_3A[SITE_NUM] = { 0 };
	double Vcs_hsfet_4A[SITE_NUM] = { 0 };
	double Vcs_hsfet_6A[SITE_NUM] = { 0 };
	double Vcs_hsfet_8A[SITE_NUM] = { 0 };
	double Vcs_hsfet_10A[SITE_NUM] = { 0 };
	double Vcs_lsfet_1A[SITE_NUM] = { 0 };
	double Vcs_lsfet_2A[SITE_NUM] = { 0 };
	double Vcs_lsfet_3A[SITE_NUM] = { 0 };
	double Vcs_lsfet_4A[SITE_NUM] = { 0 };
	double Vcs_lsfet_6A[SITE_NUM] = { 0 };
	double Vcs_lsfet_8A[SITE_NUM] = { 0 };
	double Vcs_lsfet_10A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_1A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_2A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_3A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_4A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_6A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_8A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_10A[SITE_NUM] = { 0 };
	double Ibat_cc_loop_accur_2A[SITE_NUM] = { 0 };
	double Ibat_cc_loop_accur_3A[SITE_NUM] = { 0 };
	double Ibat_cc_loop_accur_4A[SITE_NUM] = { 0 };
	double Ibat_cc_loop_accur_6A[SITE_NUM] = { 0 };
	double Vcs_Gain[SITE_NUM] = { 0 };
	double Vcs_Offset[SITE_NUM] = { 0 };
	//--------PMID--->SW

	cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 4.5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 4.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
	ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
	entertestmode();
	//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,0),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
	I2CWriteSameData(DEV_ADDR, 0x0A, 0x07);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
	delay_ms(2);
	double base_0mA[SITE_NUM] = { 0 };
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	ATEST_GRP.MeasureVI(100, 5);
	FOR_EACH_VALID_SITE(site)
	{
		base_0mA[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}
	//--------------------------HSFET 1A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, -1, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);// SW-->PMID, HSFET ON
	delay_us(2000);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_hsfet_1A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET) - base_0mA[site];
	}
	//--------------------------HSFET 2A
	delay_ms(3);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, -2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);// PMID-->SW, HSFET ON
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_hsfet_2A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET) - base_0mA[site];
	}
	//--------------------------HSFET 3A
	delay_ms(3);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, -3, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);// PMID-->SW, HSFET ON
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_hsfet_3A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET) - base_0mA[site];
		Vcs_Gain[site] = (Vcs_hsfet_3A[site] - Vcs_hsfet_1A[site]) / 2;
		Vcs_Offset[site] = Vcs_hsfet_3A[site] - Vcs_Gain[site] * 3;
		Vcs_hsfet_4A[site] = Vcs_Gain[site] * 4 + Vcs_Offset[site];
		Vcs_hsfet_6A[site] = Vcs_Gain[site] * 6 + Vcs_Offset[site];
		Vcs_hsfet_8A[site] = Vcs_Gain[site] * 8 + Vcs_Offset[site];
		Vcs_hsfet_10A[site] = Vcs_Gain[site] * 10 + Vcs_Offset[site];
	}

	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);

		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K33_BUSL_PGND, K30_VBAT_Cap, K32_PMID_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 4.5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 4.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		entertestmode();
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x59, 0x00);// HS_ON=0/LS_ON=0
		BTST_ACM.Set(FV, V_TYP_VBUS, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
		cbite.SetOn(K1_PGND2AGND, K33_BUSL_PGND, K17_BUSH_SW, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		//PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	}
	I2CWriteSameData(DEV_ADDR, 0x0A, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x81);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
	//		field[(WAKE_UP,1),(D2A_BUBO_TM_LSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,0),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
	delay_ms(2);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	ATEST_GRP.MeasureVI(100, 5);
	FOR_EACH_VALID_SITE(site)
	{
		base_0mA[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}
	//--------------------------LSFET 1A
	FPVI.Set(FI, -1, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);// PGND-->SW, LSFET ON
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_lsfet_1A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET)-base_0mA[site];
	}
	//--------------------------LSFET 2A
	delay_ms(5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, -2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);// PGND-->SW, LSFET ON
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_lsfet_2A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET) - base_0mA[site];
	}
	//--------------------------LSFET 3A
	delay_ms(5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, -3, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);// PGND-->SW, LSFET ON
	delay_ms(2);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_lsfet_3A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET) - base_0mA[site];
		Vcs_Gain[site] = (Vcs_lsfet_3A[site] - Vcs_lsfet_1A[site]) / 2;
		Vcs_Offset[site] = Vcs_lsfet_3A[site] - Vcs_Gain[site] * 3;
		Vcs_lsfet_4A[site] = Vcs_Gain[site] * 4 + Vcs_Offset[site];
		Vcs_lsfet_6A[site] = Vcs_Gain[site] * 6 + Vcs_Offset[site];
		Vcs_lsfet_8A[site] = Vcs_Gain[site] * 8 + Vcs_Offset[site];
		Vcs_lsfet_10A[site] = Vcs_Gain[site] * 10 + Vcs_Offset[site];
	}
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		//VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		//ATEST_GRP.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		//BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW
		//VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	}
	double vcs_gain_buck[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		Ibat_cc_sns_1A[site] = Vcs_hsfet_1A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_1A[site] * (5 - V_TYP_VBAT) / 5;
		Ibat_cc_sns_2A[site] = Vcs_hsfet_2A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_2A[site] * (5 - V_TYP_VBAT) / 5;
		Ibat_cc_sns_3A[site] = Vcs_hsfet_3A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_3A[site] * (5 - V_TYP_VBAT) / 5;
		Ibat_cc_sns_4A[site] = Vcs_hsfet_4A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_4A[site] * (5 - V_TYP_VBAT) / 5;
		Ibat_cc_sns_6A[site] = Vcs_hsfet_6A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_6A[site] * (5 - V_TYP_VBAT) / 5;
		Ibat_cc_sns_8A[site] = Vcs_hsfet_8A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_8A[site] * (5 - V_TYP_VBAT) / 5;
		Ibat_cc_sns_10A[site] = Vcs_hsfet_10A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_10A[site] * (5 - V_TYP_VBAT) / 5;
		vcs_gain_buck[site] = (Ibat_cc_sns_3A[site] - Ibat_cc_sns_1A[site]) / 2;
		Ibat_cc_loop_accur_2A[site] = Ibat_cc_sns_2A[site] +Ibat_cc_lp_os_buck_2a[site];
		Ibat_cc_loop_accur_3A[site] = Ibat_cc_sns_3A[site] +Ibat_cc_lp_os_buck_3a[site];
		Ibat_cc_loop_accur_4A[site] = Ibat_cc_sns_4A[site] +Ibat_cc_lp_os_buck_4a[site];
		Ibat_cc_loop_accur_6A[site] = Ibat_cc_sns_6A[site] +Ibat_cc_lp_os_buck_6a[site];
		IBAT_SNS_CC_ACCUR_BU_1A->SetTestResult(site, 0, Ibat_cc_sns_1A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_SNS_CC_ACCUR_BU_2A->SetTestResult(site, 0, Ibat_cc_sns_2A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_SNS_CC_ACCUR_BU_3A->SetTestResult(site, 0, Ibat_cc_sns_3A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_SNS_CC_ACCUR_BU_4A->SetTestResult(site, 0, Ibat_cc_sns_4A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_SNS_CC_ACCUR_BU_6A->SetTestResult(site, 0, Ibat_cc_sns_6A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_SNS_CC_ACCUR_BU_8A->SetTestResult(site, 0, Ibat_cc_sns_8A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_SNS_CC_ACCUR_BU_10A->SetTestResult(site, 0, Ibat_cc_sns_10A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_LOOP_CC_ACCUR_BU_2A->SetTestResult(site, 0, Ibat_cc_loop_accur_2A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_LOOP_CC_ACCUR_BU_3A->SetTestResult(site, 0, Ibat_cc_loop_accur_3A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_LOOP_CC_ACCUR_BU_4A->SetTestResult(site, 0, Ibat_cc_loop_accur_4A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_LOOP_CC_ACCUR_BU_6A->SetTestResult(site, 0, Ibat_cc_loop_accur_6A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_LOOP_CC_ACCUR_BU_8A->SetTestResult(site, 0, 1.33*Ibat_cc_loop_accur_6A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_LOOP_CC_ACCUR_BU_10A->SetTestResult(site, 0, 1.67*Ibat_cc_loop_accur_6A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
		IBAT_LOOP_CC_ACCUR_BU_12A->SetTestResult(site, 0, 2.0*Ibat_cc_loop_accur_6A[site] / vcs_gain_buck[site]);//0,1 是理论的Gain值
	}


	return 0;
}

DUT_API int IBAT_CC_LOOP_ACCUR_BO(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IBAT_SNS_CC_ACCUR_BO_1A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BO_1A");
    CParam *IBAT_SNS_CC_ACCUR_BO_2A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BO_2A");
    CParam *IBAT_SNS_CC_ACCUR_BO_3A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BO_3A");
    CParam *IBAT_SNS_CC_ACCUR_BO_4A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BO_4A");
    CParam *IBAT_SNS_CC_ACCUR_BO_6A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BO_6A");
    CParam *IBAT_SNS_CC_ACCUR_BO_8A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BO_8A");
    CParam *IBAT_SNS_CC_ACCUR_BO_10A = StsGetParam(funcindex, "IBAT_SNS_CC_ACCUR_BO_10A");
    CParam *IBAT_LOOP_CC_ACCUR_BO_2A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BO_2A");
    CParam *IBAT_LOOP_CC_ACCUR_BO_3A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BO_3A");
    CParam *IBAT_LOOP_CC_ACCUR_BO_4A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BO_4A");
    CParam *IBAT_LOOP_CC_ACCUR_BO_6A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BO_6A");
    CParam *IBAT_LOOP_CC_ACCUR_BO_8A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BO_8A");
    CParam *IBAT_LOOP_CC_ACCUR_BO_10A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BO_10A");
    CParam *IBAT_LOOP_CC_ACCUR_BO_12A = StsGetParam(funcindex, "IBAT_LOOP_CC_ACCUR_BO_12A");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	double Vcs_hsfet_1A[SITE_NUM] = { 0 };
	double Vcs_hsfet_2A[SITE_NUM] = { 0 };
	double Vcs_hsfet_3A[SITE_NUM] = { 0 };
	double Vcs_hsfet_4A[SITE_NUM] = { 0 };
	double Vcs_hsfet_6A[SITE_NUM] = { 0 };
	double Vcs_hsfet_8A[SITE_NUM] = { 0 };
	double Vcs_hsfet_10A[SITE_NUM] = { 0 };
	double Vcs_lsfet_1A[SITE_NUM] = { 0 };
	double Vcs_lsfet_2A[SITE_NUM] = { 0 };
	double Vcs_lsfet_3A[SITE_NUM] = { 0 };
	double Vcs_lsfet_4A[SITE_NUM] = { 0 };
	double Vcs_lsfet_6A[SITE_NUM] = { 0 };
	double Vcs_lsfet_8A[SITE_NUM] = { 0 };
	double Vcs_lsfet_10A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_1A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_2A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_3A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_4A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_6A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_8A[SITE_NUM] = { 0 };
	double Ibat_cc_sns_10A[SITE_NUM] = { 0 };
	double Ibat_cc_loop_accur_1A[SITE_NUM] = { 0 };
	double Ibat_cc_loop_accur_2A[SITE_NUM] = { 0 };
	double Ibat_cc_loop_accur_3A[SITE_NUM] = { 0 };
	double Ibat_cc_loop_accur_4A[SITE_NUM] = { 0 };
	double Ibat_cc_loop_accur_6A[SITE_NUM] = { 0 };
	double Ibat_cc_loop_accur_8A[SITE_NUM] = { 0 };
	double Vcs_Gain[SITE_NUM] = { 0 };
	double Vcs_Offset[SITE_NUM] = { 0 };

	if (!TTR)
	{
		delay_ms(10);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		if (V_TYP_VBAT > 4.4)
		{
			VBAT_ACM.Set(FV, 4.4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		else
		{
			VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		VDRV_AMP_ACM.Set(FV, 4.5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 4.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
		ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
		//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,1),(FPWM_EN,1)(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
		I2CWriteSameData(DEV_ADDR, 0x0A, 0x07);
		I2CWriteSameData(DEV_ADDR, 0x09, 0x19);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//D2A_BUBO_DIS_CLK=0
		I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
		delay_ms(5);
	}
	else
	{
		cbite.SetOn( K17_BUSH_SW, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
		//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,1),(FPWM_EN,1)(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
		I2CWriteSameData(DEV_ADDR, 0x0A, 0x07);
		I2CWriteSameData(DEV_ADDR, 0x09, 0x19);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//D2A_BUBO_DIS_CLK=0
		I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
		I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
		I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
		I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
		delay_ms(1);
	}

	double base_0mA[SITE_NUM] = { 0 };
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	ATEST_GRP.MeasureVI(100, 5);
	FOR_EACH_VALID_SITE(site)
	{
		base_0mA[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}
	//--------------------------HSFET 1A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);// SW-->PMID, HSFET ON
	delay_us(2000);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(5);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_hsfet_1A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET)-base_0mA[site];
	}
	//--------------------------HSFET 2A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);// SW-->PMID, HSFET ON
	delay_us(2000);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(5);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_hsfet_2A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET) - base_0mA[site];
	}
	//--------------------------HSFET 3A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);// SW-->PMID, HSFET ON
	FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);// SW-->PMID, HSFET ON
	delay_us(2000);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_hsfet_3A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET) - base_0mA[site];
		Vcs_Gain[site] = (Vcs_hsfet_3A[site] - Vcs_hsfet_1A[site]) / 2;
		Vcs_Offset[site] = Vcs_hsfet_3A[site] - Vcs_Gain[site] * 3;
		Vcs_hsfet_4A[site] = Vcs_Gain[site] * 4 + Vcs_Offset[site];
		Vcs_hsfet_6A[site] = Vcs_Gain[site] * 6 + Vcs_Offset[site];
		Vcs_hsfet_8A[site] = Vcs_Gain[site] * 8 + Vcs_Offset[site];
		Vcs_hsfet_10A[site] = Vcs_Gain[site] * 10 + Vcs_Offset[site];
	}


	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);

		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K33_BUSL_PGND, K30_VBAT_Cap, K32_PMID_Cap, -1);
		delay_ms(3);
		if (V_TYP_VBAT > 4.4)
		{
			VBAT_ACM.Set(FV, 4.4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		else
		{
			VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		}
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 4.5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 4.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
	}
	else
	{
		BTST_ACM.Set(FV, V_TYP_VBUS, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x00);// HS_ON=0/LS_ON=0	
		delay_us(500);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
		SW_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
		cbite.SetOn(K33_BUSL_PGND, K17_BUSH_SW, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		SW_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		delay_us(500);
	}
	PMID_FOVI.Set(FV,5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(2);
	entertestmode();
	//		field[(WAKE_UP,1),(D2A_BUBO_TM_LSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,1),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x81);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x9D);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(DIS_NTC_DETECTION_ANALOG,1)]
	delay_ms(2);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	ATEST_GRP.MeasureVI(100, 5);
	FOR_EACH_VALID_SITE(site)
	{
		base_0mA[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
	}

	//--------------------------LSFET 1A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 1, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);// SW--->PGND, LSFET ON
	delay_us(2000);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_lsfet_1A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET) - base_0mA[site];
	}
	//--------------------------LSFET 2A
	delay_ms(3);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);// SW--->PGND, LSFET ON
	delay_us(2000);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_lsfet_2A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET) - base_0mA[site];
	}
	//--------------------------LSFET 3A
	delay_ms(3);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);// SW--->PGND, LSFET ON
	delay_us(2000);
	ATEST_GRP.MeasureVI(100, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vcs_lsfet_3A[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET) - base_0mA[site];
		Vcs_Gain[site] = (Vcs_lsfet_3A[site] - Vcs_lsfet_1A[site]) / 2;
		Vcs_Offset[site] = Vcs_lsfet_3A[site] - Vcs_Gain[site] * 3;
		Vcs_lsfet_4A[site] = Vcs_Gain[site] * 4 + Vcs_Offset[site];
		Vcs_lsfet_6A[site] = Vcs_Gain[site] * 6 + Vcs_Offset[site];
		Vcs_lsfet_8A[site] = Vcs_Gain[site] * 8 + Vcs_Offset[site];
		Vcs_lsfet_10A[site] = Vcs_Gain[site] * 10 + Vcs_Offset[site];
	}

	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FV, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		ATEST_GRP.Set(FV, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		ATEST_GRP.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}

	double vcs_gain_boost[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		Ibat_cc_sns_1A[site] = Vcs_hsfet_1A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_1A[site] * (5 - V_TYP_VBAT) / 5;
		Ibat_cc_sns_2A[site] = Vcs_hsfet_2A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_2A[site] * (5 - V_TYP_VBAT) / 5;
		Ibat_cc_sns_3A[site] = Vcs_hsfet_3A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_3A[site] * (5 - V_TYP_VBAT) / 5;
		Ibat_cc_sns_4A[site] = Vcs_hsfet_4A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_4A[site] * (5 - V_TYP_VBAT) / 5;
		Ibat_cc_sns_6A[site] = Vcs_hsfet_6A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_6A[site] * (5 - V_TYP_VBAT) / 5;
		Ibat_cc_sns_8A[site] = Vcs_hsfet_8A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_8A[site] * (5 - V_TYP_VBAT) / 5;
		Ibat_cc_sns_10A[site] = Vcs_hsfet_10A[site] * V_TYP_VBAT / 5 + Vcs_lsfet_10A[site] * (5 - V_TYP_VBAT) / 5;
		vcs_gain_boost[site] = (Ibat_cc_sns_3A[site] - Ibat_cc_sns_1A[site]) / 2;
		Ibat_cc_loop_accur_2A[site] = Ibat_cc_sns_2A[site] + Ibat_cc_lp_os_boost_2a[site];
		Ibat_cc_loop_accur_3A[site] = Ibat_cc_sns_3A[site] + Ibat_cc_lp_os_boost_3a[site];
		Ibat_cc_loop_accur_4A[site] = Ibat_cc_sns_4A[site] + Ibat_cc_lp_os_boost_4a[site];
		Ibat_cc_loop_accur_6A[site] = Ibat_cc_sns_6A[site] + Ibat_cc_lp_os_boost_6a[site];
		Ibat_cc_loop_accur_8A[site] = Ibat_cc_sns_8A[site] + Ibat_cc_lp_os_boost_8a[site];

		IBAT_SNS_CC_ACCUR_BO_1A->SetTestResult(site, 0, Ibat_cc_sns_1A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_SNS_CC_ACCUR_BO_2A->SetTestResult(site, 0, Ibat_cc_sns_2A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_SNS_CC_ACCUR_BO_3A->SetTestResult(site, 0, Ibat_cc_sns_3A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_SNS_CC_ACCUR_BO_4A->SetTestResult(site, 0, Ibat_cc_sns_4A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_SNS_CC_ACCUR_BO_6A->SetTestResult(site, 0, Ibat_cc_sns_6A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_SNS_CC_ACCUR_BO_8A->SetTestResult(site, 0, Ibat_cc_sns_8A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_SNS_CC_ACCUR_BO_10A->SetTestResult(site, 0, Ibat_cc_sns_10A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_LOOP_CC_ACCUR_BO_2A->SetTestResult(site, 0, Ibat_cc_loop_accur_2A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_LOOP_CC_ACCUR_BO_3A->SetTestResult(site, 0, Ibat_cc_loop_accur_3A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_LOOP_CC_ACCUR_BO_4A->SetTestResult(site, 0, Ibat_cc_loop_accur_4A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_LOOP_CC_ACCUR_BO_6A->SetTestResult(site, 0, Ibat_cc_loop_accur_6A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_LOOP_CC_ACCUR_BO_8A->SetTestResult(site, 0, Ibat_cc_loop_accur_8A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_LOOP_CC_ACCUR_BO_10A->SetTestResult(site, 0, 1.25*Ibat_cc_loop_accur_8A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
		IBAT_LOOP_CC_ACCUR_BO_12A->SetTestResult(site, 0, 2*Ibat_cc_loop_accur_6A[site] / vcs_gain_boost[site]);// 0.1 是理论gain值
	}

	return 0;
}

DUT_API int LOOP_GM_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBAT_LOOP_GM = StsGetParam(funcindex, "VBAT_LOOP_GM");
    CParam *VBAT_LOOP_Intc = StsGetParam(funcindex, "VBAT_LOOP_Intc");
    CParam *VBAT_LOOP_Vamux = StsGetParam(funcindex, "VBAT_LOOP_Vamux");
    CParam *VBUS_LOOP_BUCK_GM = StsGetParam(funcindex, "VBUS_LOOP_BUCK_GM");
    CParam *VBUS_LOOP_BUCK_Intc = StsGetParam(funcindex, "VBUS_LOOP_BUCK_Intc");
    CParam *VBUS_LOOP_BUCK_Vamux = StsGetParam(funcindex, "VBUS_LOOP_BUCK_Vamux");
    CParam *VBUS_LOOP_BOOST_GM = StsGetParam(funcindex, "VBUS_LOOP_BOOST_GM");
    CParam *VBUS_LOOP_BOOST_Intc = StsGetParam(funcindex, "VBUS_LOOP_BOOST_Intc");
    CParam *VBUS_LOOP_BOOST_Vamux = StsGetParam(funcindex, "VBUS_LOOP_BOOST_Vamux");
    CParam *IBAT_LOOP_GM = StsGetParam(funcindex, "IBAT_LOOP_GM");
    CParam *IBAT_LOOP_Intc = StsGetParam(funcindex, "IBAT_LOOP_Intc");
    CParam *IBAT_LOOP_Vamux = StsGetParam(funcindex, "IBAT_LOOP_Vamux");
    CParam *IBUS_LOOP_GM = StsGetParam(funcindex, "IBUS_LOOP_GM");
    CParam *IBUS_LOOP_Intc = StsGetParam(funcindex, "IBUS_LOOP_Intc");
    CParam *IBUS_LOOP_Vamux = StsGetParam(funcindex, "IBUS_LOOP_Vamux");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
#if 0
	double Vamux_meas[SITE_NUM] = { 0 };
	double Iamux_meas[SITE_NUM] = { 0 };
	double Intc_meas[SITE_NUM] = { 0 };
	double vbat_loop_gm[SITE_NUM] = { 0 };
	double vbus_loop_buck_gm[SITE_NUM] = { 0 };
	double vbus_loop_boost_gm[SITE_NUM] = { 0 };
	double ibat_loop_gm[SITE_NUM] = { 0 };
	double ibus_loop_gm[SITE_NUM] = { 0 };


	cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, -1);// connect SW and PIMD by FPVI
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_1MA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x0A, 0x11);
	I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x96);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(VBAT_CV,1),(IBAT_LIMIT,7),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(EN_ATEST0,1),(ATEST0_MUX,18),(DIS_NTC_DETECTION_ANALOG,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(VBAT_CV,1),(IBAT_LIMIT,7),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(EN_ATEST0,1),(ATEST0_MUX,18),(DIS_NTC_DETECTION_ANALOG,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	delay_ms(2);
	AMUX_FOVI.MeasureVI(215, 10);
	NTC_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_meas[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
		Intc_meas[site] = NTC_FOVI.GetMeasResult(site, MIRET)*1e6;
		vbat_loop_gm[site] = Intc_meas[site] / (Vamux_meas[site] - 4.0 * 0.4)/10;// uA/V

		VBAT_LOOP_Intc->SetTestResult(site, 0, Intc_meas[site]);
		VBAT_LOOP_Vamux->SetTestResult(site, 0, Vamux_meas[site]*1e3);
	}

	//==================VBUS_LOOP_GM_BUCK
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
		delay_ms(2);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		entertestmode();
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x0A, 0x00);
	}
	I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xAE);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(BUBO_MODE,0),(IBAT_LIMIT,7),(IBUS_SET,127),(EN_ATEST0,1),(ATEST0_MUX,21),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(DIS_NTC_DETECTION_ANALOG,1)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xAF);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x80);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0xA0);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	delay_ms(2);
	NTC_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_1MA, FOVIe_RELAY_ON);
	AMUX_FOVI.MeasureVI(215, 10);
	NTC_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_meas[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
		Intc_meas[site] = NTC_FOVI.GetMeasResult(site, MIRET)*1e6;
		vbus_loop_buck_gm[site] = Intc_meas[site] / (Vamux_meas[site]);// uA/V

		VBUS_LOOP_BUCK_Intc->SetTestResult(site, 0, Intc_meas[site]);
		VBUS_LOOP_BUCK_Vamux->SetTestResult(site, 0, Vamux_meas[site] * 1e3);	
	}

	//==================VBUS_LOOP_GM_BOOST
	I2CWriteSameData(DEV_ADDR, 0x09, 1, 9);//(BUBO_MODE,1)
	delay_ms(2);
	AMUX_FOVI.MeasureVI(215, 10);
	NTC_FOVI.MeasureVI(50, 5);
	NTC_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_1MA, FOVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_meas[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
		Intc_meas[site] = NTC_FOVI.GetMeasResult(site, MIRET)*1e6;
		vbus_loop_boost_gm[site] = Intc_meas[site] / (Vamux_meas[site]);// uA/V

		VBUS_LOOP_BOOST_Intc->SetTestResult(site, 0, Intc_meas[site]);
		VBUS_LOOP_BOOST_Vamux->SetTestResult(site, 0, Vamux_meas[site] * 1e3);
	}


	//================IBAT_LOOOP_GM
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
		delay_ms(5);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_1MA, FOVIe_RELAY_ON);
		entertestmode();
	}
	else
	{
		AMUX_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_1MA, FOVIe_RELAY_ON);
	}


	I2CWriteSameData(DEV_ADDR, 0x0B, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x40);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x5D);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(BUBO_MODE,1),(IBAT_LIMIT,0),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(EN_ATEST0,1),(D2A_BUBO_ATEST0,13),(DIS_NTC_DETECTION_ANALOG,1),(D2A_BUBO_TM_FORCE_IBAT_SNS_OFF,1)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0x07);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x80);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0xA0);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	delay_ms(2);
	NTC_FOVI.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Intc_meas[site] = NTC_FOVI.GetMeasResult(site, MIRET);
		ibat_loop_gm[site] = Intc_meas[site]*1e6;//uA
		IBAT_LOOP_Intc->SetTestResult(site, 0, Intc_meas[site]);
		IBAT_LOOP_Vamux->SetTestResult(site, 0, Vamux_meas[site] * 1e3);
	}

	//================IBUS_LOOOP_GM
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
		delay_ms(5);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_1MA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
	}
	else
	{
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_10V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_1MA, FOVIe_RELAY_ON);
		I2CWriteSameData(DEV_ADDR, 0x0E, 0x00);
		I2CWriteSameData(DEV_ADDR, 0x59, 0x00);
	}

	I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xC6);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);	//		field[(WAKE_UP,1),(BUBO_MODE,0),(IBAT_LIMIT,7),(EN_ATEST0,1),(ATEST0_MUX,24),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(VBUS_LOOP_DISABLE,1),(DIS_NTC_DETECTION_ANALOG,1)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xC7);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x80);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0xA0);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xCF);//		field[(ATEST0_MUX,25)]
	delay_ms(2);
	AMUX_FOVI.MeasureVI(215, 10);
   FOR_EACH_VALID_SITE(site)
   {
	   Vamux_meas[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
   }

   AMUX_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
   NTC_FOVI.Set(FV, 5, FOVIe_10V, FOVIe_1MA, FOVIe_RELAY_ON);
	delay_ms(2);
	NTC_FOVI.MeasureVI(100, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Intc_meas[site] = NTC_FOVI.GetMeasResult(site, MIRET);
		ibus_loop_gm[site] = Intc_meas[site]*1e6;

		IBUS_LOOP_Intc->SetTestResult(site, 0, Intc_meas[site]);
		IBUS_LOOP_Vamux->SetTestResult(site, 0, Vamux_meas[site] * 1e3);
	}

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(1);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
	AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_OFF);
	NTC_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		VBAT_LOOP_GM->SetTestResult(site, 0, vbat_loop_gm[site]);
		VBUS_LOOP_BUCK_GM->SetTestResult(site, 0, vbus_loop_buck_gm[site]);
		VBUS_LOOP_BOOST_GM->SetTestResult(site, 0, vbus_loop_boost_gm[site]);
		IBAT_LOOP_GM->SetTestResult(site, 0, ibat_loop_gm[site]);
		IBUS_LOOP_GM->SetTestResult(site, 0, ibus_loop_gm[site]);
	}
#endif
	return 0;
}
 
DUT_API int BST_UVLO_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *BST_UVLO_Rise = StsGetParam(funcindex, "BST_UVLO_Rise");
    CParam *BST_UVLO_Fall = StsGetParam(funcindex, "BST_UVLO_Fall");
    CParam *BST_UVLO_Hys = StsGetParam(funcindex, "BST_UVLO_Hys");
    CParam *BST_UVLO_Rise_L = StsGetParam(funcindex, "BST_UVLO_Rise_L");
    CParam *BST_UVLO_Fall_L = StsGetParam(funcindex, "BST_UVLO_Fall_L");
    CParam *BST_UVLO_Hys_L = StsGetParam(funcindex, "BST_UVLO_Hys_L");
    CParam *COUNTER_High = StsGetParam(funcindex, "COUNTER_High");
    CParam *COUNTER_Low = StsGetParam(funcindex, "COUNTER_Low");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double bst_uvlo_r[200] = { 0.0 };
	double bst_uvlo_f[200] = { 0.0 };
	double Trig = 2.5;
	int Trig_Point[SITE_NUM] = { 0 };
	double bst_uvlo_rise[SITE_NUM] = { 0 };
	double bst_uvlo_fall[SITE_NUM] = { 0 };
	double bst_uvlo_hys[SITE_NUM] = { 0 };
	double bst_uvlo_rise_10[SITE_NUM] = { 0 };
	double bst_uvlo_fall_10[SITE_NUM] = { 0 };
	double bst_uvlo_hys_10[SITE_NUM] = { 0 };
	double bst_counter_high[SITE_NUM] = { 0 };
	double bst_counter_low[SITE_NUM] = { 0 };
	cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap,K43_INT_ACM, K58_INT_PU,K53_SCL_PU,K57_SDA_PU,K17_BUSH_SW,K38_BUSL_BTST,K18_BST_SW_Cap,K25_VCC_Cap,-1);// connect SW and BTST by FPVI
	delay_ms(3);
	VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	FPVI.Set(FV, -5, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);//		field[(WAKE_UP,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_SLP,1),
	I2CWriteSameData(DEV_ADDR, 0x61,0x0B);//		field[(EN_DTEST0,1),(DTEST0_MUX,12)]
	I2CWriteSameData(DEV_ADDR, 0x55, 0x8C);
	delay_ms(1);
	STSAWGCreateRampData(&bst_uvlo_f[0], sam, 1,-3.68, -3.2);// BST-SW
	FPVI.AwgClear();
	FPVI.AwgLoader("bst_uvlo_f_pattern", FV, FPVIe_10V, FPVIe_100MA, bst_uvlo_f, sam);
	FPVI.AwgSelect("bst_uvlo_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	FPVI.Set(FV, -3.7, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FV, -2.5, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT)-2; //Get the position of trigger point
		bst_uvlo_fall[site] =-1* FPVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])-0.006; //Read the voltage value on trigger position, mA
		check_awg_trigger_point(Trig_Point, sam, bst_uvlo_fall,site);// add for AWG trigger check
	}

	STSAWGCreateRampData(&bst_uvlo_r[0], sam, 1,-3.25, -3.85);// BST-SW
	FPVI.AwgClear();
	FPVI.AwgLoader("bst_uvlo_r_pattern", FV, FPVIe_10V, FPVIe_100MA, bst_uvlo_r, sam);
	FPVI.AwgSelect("bst_uvlo_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	FPVI.Set(FV, -3.1, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FV, -5, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);

	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT)-2; //Get the position of trigger point
		bst_uvlo_rise[site] = -1*FPVI.GetMeasResult(site, MVRET, (int)Trig_Point[site])-0.006; //Read the voltage value on trigger position, mA
		bst_uvlo_hys[site] = (bst_uvlo_rise[site] - bst_uvlo_fall[site])*1e3;//mV
		check_awg_trigger_point(Trig_Point, sam, bst_uvlo_rise,site);// add for AWG trigger check
	}


	//---------------BST config2
	I2CWriteSameData(DEV_ADDR, 0x6D, 0x10);
	delay_ms(2);
	STSAWGCreateRampData(&bst_uvlo_f[0], sam, 1, -3.65, -3);// BST-SW
	FPVI.AwgClear();
	FPVI.AwgLoader("bst_uvlo_f_pattern", FV, FPVIe_10V, FPVIe_100MA, bst_uvlo_f, sam);
	FPVI.AwgSelect("bst_uvlo_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	FPVI.Set(FV, -3.7, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	delay_ms(1);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FV, -2.5, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT) - 2; //Get the position of trigger point
		bst_uvlo_fall_10[site] = -1 * FPVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]) - 0.006; //Read the voltage value on trigger position, mA
		check_awg_trigger_point(Trig_Point, sam, bst_uvlo_fall_10,site);// add for AWG trigger check
	}

	STSAWGCreateRampData(&bst_uvlo_r[0], sam, 1, -3.15, -3.75);// BST-SW
	FPVI.AwgClear();
	FPVI.AwgLoader("bst_uvlo_r_pattern", FV, FPVIe_10V, FPVIe_100MA, bst_uvlo_r, sam);
	FPVI.AwgSelect("bst_uvlo_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	FPVI.MeasureVI(sam, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	FPVI.Set(FV, -3.1, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	delay_ms(1);
	STSEnableAWG(&FPVI);
	STSEnableMeas(&FPVI, &SDA_INT_ACM);
	STSAWGRun();
	FPVI.Set(FV, -5, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);

	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = (int)SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT) - 2; //Get the position of trigger point
		bst_uvlo_rise_10[site] = -1 * FPVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]) - 0.006; //Read the voltage value on trigger position, mA
		bst_uvlo_hys_10[site] = (bst_uvlo_rise_10[site] - bst_uvlo_fall_10[site])*1e3;//mV
		check_awg_trigger_point(Trig_Point, sam, bst_uvlo_rise_10,site);// add for AWG trigger check
	}

	////===============BOOST_COUNTER
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x59, 0xA6);
	I2CWriteSameData(DEV_ADDR, 0x62, 0x80);//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(BUBO_MODE,1),(D2A_BUBO_TM_FORCE_EN_CS,1),(D2A_BUBO_TM_LOW_ILIMT_OFF,1),(HFET_OCP_PRO_DIS,1),(D2A_BUBO_TM_FORCE_ILIMT_SNS_OFF,1)]
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);
	I2CWriteSameData(DEV_ADDR, 0x67, 0x03);//		field[(DIS_NTC_DETECTION_ANALOG,1),(D2A_OVRD_SEL,3)]
	I2CWriteSameData(DEV_ADDR, 0x68, 0x30);//		field[(OVRD_VALUE,3)]
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	I2CWriteSameData(DEV_ADDR, 0x55, 0xC0);//		field[(EN_DTEST0,1),(DTEST0_MUX,64)]
	I2CWriteSameData(DEV_ADDR, 0x62, 0x00);//		field[(HFET_OCP_PRO_DIS,0)]
	I2CWriteSameData(DEV_ADDR, 0x55, 0xAF);//		field[(EN_DTEST0,1),(DTEST0_MUX,47)]
	I2CWriteSameData(DEV_ADDR, 0x59, 0xA4);//		field[(D2A_BUBO_TM_HSON,0)]
	I2CWriteSameData(DEV_ADDR, 0x59, 0xA6);//		field[(D2A_BUBO_TM_HSON,1)]  ----第一次	
	I2CWriteSameData(DEV_ADDR, 0x59, 0xA4);//		field[(D2A_BUBO_TM_HSON,0)]
	delay_us(1);
	I2CWriteSameData(DEV_ADDR, 0x59, 0xA6);//		field[(D2A_BUBO_TM_HSON,1)]-----第二次
	delay_us(1);
	I2CWriteSameData(DEV_ADDR, 0x59, 0xA4);//		field[(D2A_BUBO_TM_HSON,0)]
	delay_us(1);
	I2CWriteSameData(DEV_ADDR, 0x59, 0xA6);//		field[(D2A_BUBO_TM_HSON,1)]-----第三次
	delay_ms(1);
	SDA_INT_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		bst_counter_high[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
	}

	I2CWriteSameData(DEV_ADDR, 0x59, 0xA4);//		field[(D2A_BUBO_TM_HSON,0)]
	I2CWriteSameData(DEV_ADDR, 0x59, 0xA6);//		field[(D2A_BUBO_TM_HSON,1)]----第四次
	delay_us(1000);
	SDA_INT_ACM.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		bst_counter_low[site] = SDA_INT_ACM.GetMeasResult(site, MVRET);
	}
	I2CWriteSameData(DEV_ADDR, 0x59, 0xA4);//		field[(D2A_BUBO_TM_HSON,0)]
	I2CWriteSameData(DEV_ADDR, 0x59, 0x00);//		field[(D2A_BUBO_TM_HSON,0)],field[(D2A_BUBO_TM_LSON,0)]	
	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);

		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
	}





	FOR_EACH_VALID_SITE(site)
	{
		BST_UVLO_Rise->SetTestResult(site, 0, bst_uvlo_rise[site]);
		BST_UVLO_Fall->SetTestResult(site, 0, bst_uvlo_fall[site]);
		BST_UVLO_Hys->SetTestResult(site, 0, bst_uvlo_hys[site]);
		BST_UVLO_Rise_L->SetTestResult(site, 0, bst_uvlo_rise_10[site]);
		BST_UVLO_Fall_L->SetTestResult(site, 0, bst_uvlo_fall_10[site]);
		BST_UVLO_Hys_L->SetTestResult(site, 0, bst_uvlo_hys_10[site]);
		COUNTER_High->SetTestResult(site, 0, bst_counter_high[site]);
		COUNTER_Low->SetTestResult(site, 0, bst_counter_low[site]);
	}
    return 0;
}
 
 
DUT_API int IBAT_LOOP_INDICATOR(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *IBAT_LP_INDICATOR_Rise = StsGetParam(funcindex, "IBAT_LP_INDICATOR_Rise");
    CParam *IBAT_LP_INDICATOR_Fall = StsGetParam(funcindex, "IBAT_LP_INDICATOR_Fall");
    CParam *IBAT_LP_INDICATOR_Hys = StsGetParam(funcindex, "IBAT_LP_INDICATOR_Hys");
    CParam *IBUS_LP_INDICATOR_Rise = StsGetParam(funcindex, "IBUS_LP_INDICATOR_Rise");
    CParam *IBUS_LP_INDICATOR_Fall = StsGetParam(funcindex, "IBUS_LP_INDICATOR_Fall");
    CParam *IBUS_LP_INDICATOR_Hys = StsGetParam(funcindex, "IBUS_LP_INDICATOR_Hys");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	int sam = 200;			//AWG waveform data length
	int interval = 20;		//AWGdata interval time, unit is uS
	double ibat_lp_ind_r[200] = { 0.0 };
	double ibat_lp_ind_f[200] = { 0.0 };
	double Trig = 2.5;
	double Trig_Point[SITE_NUM] = { 0 };
	double ibat_loop_indicator_rise[SITE_NUM] = { 0 };
	double ibat_loop_indicator_fall[SITE_NUM] = { 0 };
	double ibat_loop_indicator_hys[SITE_NUM] = { 0 };
	double ibus_loop_indicator_rise[SITE_NUM] = { 0 };
	double ibus_loop_indicator_fall[SITE_NUM] = { 0 };
	double ibus_loop_indicator_hys[SITE_NUM] = { 0 };

	cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K17_BUSH_SW, K38_BUSL_BTST, K43_INT_ACM, K58_INT_PU, K25_VCC_Cap, -1);// connect SW and BTST by FPVI
	delay_ms(3);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	SW_ACM.Set(FV, 3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FI, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	entertestmode();
	//==================IBAT LOOP  INDICATOR
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);
	I2CWriteSameData(DEV_ADDR, 0x0B, 0x40);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x7F);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x87);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x06);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x40);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x5D);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x04);//		field[(WAKE_UP,1),(BUBO_MODE,1),(IBAT_LIMIT,2),(IBUS_SET,127),(VBUS_LOOP_DISABLE,1),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(EN_ATEST0,1),(D2A_BUBO_ATEST0,13),(DIS_NTC_DETECTION_ANALOG,1),(D2A_BUBO_TM_FORCE_IBAT_SNS_OFF,1),(EN_DTEST0,1),(DTEST0_MUX,7)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0x07);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x80);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0xA0);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	delay_ms(1);
	FPVI.Set(FV, -5, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&ibat_lp_ind_r[0], sam, 1, 1.05, 1.55);
	AMUX_FOVI.AwgClear();
	AMUX_FOVI.AwgLoader("ibat_lp_ind_r_pattern", FV, FOVIe_2V, FOVIe_100MA, ibat_lp_ind_r, sam);
	AMUX_FOVI.AwgSelect("ibat_lp_ind_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	AMUX_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&AMUX_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&AMUX_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ibat_loop_indicator_rise[site] = AMUX_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		check_awg_trigger_point(Trig_Point, sam, ibat_loop_indicator_rise,site);// add for AWG trigger check
	}

	STSAWGCreateRampData(&ibat_lp_ind_f[0], sam, 1, 1.45, 0.95);// 
	AMUX_FOVI.AwgClear();
	AMUX_FOVI.AwgLoader("ibat_lp_ind_f_pattern", FV, FOVIe_2V, FOVIe_100MA, ibat_lp_ind_f, sam);
	AMUX_FOVI.AwgSelect("ibat_lp_ind_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	AMUX_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	AMUX_FOVI.Set(FV, 1.5, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&AMUX_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&AMUX_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ibat_loop_indicator_fall[site] = AMUX_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		ibat_loop_indicator_hys[site] = (ibat_loop_indicator_rise[site] - ibat_loop_indicator_fall[site])*1e3;//mV
		check_awg_trigger_point(Trig_Point, sam, ibat_loop_indicator_fall,site);// add for AWG trigger check
	}

	//===============IBUS_LOOP_INDICATOR
	I2CWriteSameData(DEV_ADDR, 0x0B, 0xE0);
	I2CWriteSameData(DEV_ADDR, 0x0E, 0x7E);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x55, 0x89);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xC6);
	I2CWriteSameData(DEV_ADDR, 0x5A, 0x50);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x13);
	I2CWriteSameData(DEV_ADDR, 0x65, 0x4);//		field[(WAKE_UP,1),(BUBO_MODE,0),(IBAT_LIMIT,7),(IBUS_SET,126),(EN_ATEST0,1),(ATEST0_MUX,24),(EN_ATEST1,1),(D2A_BUBO_ATEST1,5),(VBUS_LOOP_DISABLE,1),(DIS_NTC_DETECTION_ANALOG,1),(EN_DTEST0,1),(DTEST0_MUX,9)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xC7);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x80);//		field[(EN_I2C_CTRL,1),(D2A_BUBO_TM_DIS_VBATLOOP,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x1B);//		field[(D2A_BUBO_EN_FORCE_ON,1)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0xA0);//		field[(D2A_BUBO_TM_DIS_CLK,1)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xCF);//		field[(ATEST0_MUX,25)]
	delay_ms(1);
	// Set a sinewave data array, the start address starts from 0, data size is 100.
	STSAWGCreateRampData(&ibat_lp_ind_r[0], sam, 1, 1.75, 2.65);
	AMUX_FOVI.AwgClear();
	AMUX_FOVI.AwgLoader("ibat_lp_ind_r_pattern", FV, FOVIe_5V, FOVIe_100MA, ibat_lp_ind_r, sam);
	AMUX_FOVI.AwgSelect("ibat_lp_ind_r_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_FALLING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	AMUX_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	AMUX_FOVI.Set(FV, 1.7, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&AMUX_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&AMUX_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ibus_loop_indicator_rise[site] = AMUX_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		check_awg_trigger_point(Trig_Point, sam, ibus_loop_indicator_rise,site);// add for AWG trigger check
	}

	STSAWGCreateRampData(&ibat_lp_ind_f[0], sam, 1, 2.55, 1.65);// 
	AMUX_FOVI.AwgClear();
	AMUX_FOVI.AwgLoader("ibat_lp_ind_f_pattern", FV, FOVIe_5V, FOVIe_100MA, ibat_lp_ind_f, sam);
	AMUX_FOVI.AwgSelect("ibat_lp_ind_f_pattern", 0, sam - 1, sam - 1, interval);
	SDA_INT_ACM.SetMeasVTrig(Trig, TRIG_RISING); // trigger value is 2.5, falling edge
	SDA_INT_ACM.MeasureVI(sam, interval, MEAS_AWG);
	AMUX_FOVI.MeasureVI(sam, interval, FOVIe_MI_X1, MEAS_AWG);
	AMUX_FOVI.Set(FV, 2.6, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_us(500);
	STSEnableAWG(&AMUX_FOVI);//enable AWG pattern for ACM200_0 
	STSEnableMeas(&AMUX_FOVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
	STSAWGRun();//Enable AWG and measurement synchronously
	FOR_EACH_VALID_SITE(site)
	{
		Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
		ibus_loop_indicator_fall[site] = AMUX_FOVI.GetMeasResult(site, MVRET, (int)Trig_Point[site]);
		ibus_loop_indicator_hys[site] = (ibus_loop_indicator_rise[site] - ibus_loop_indicator_fall[site])*1e3;//mV
		check_awg_trigger_point(Trig_Point, sam, ibus_loop_indicator_fall,site);// add for AWG trigger check
	}

    SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(1);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

	FOR_EACH_VALID_SITE(site)
	{
		IBAT_LP_INDICATOR_Rise->SetTestResult(site, 0, ibat_loop_indicator_rise[site]);
		IBAT_LP_INDICATOR_Fall->SetTestResult(site, 0, ibat_loop_indicator_fall[site]);
		IBAT_LP_INDICATOR_Hys->SetTestResult(site, 0, ibat_loop_indicator_hys[site]);
		IBUS_LP_INDICATOR_Rise->SetTestResult(site, 0, ibus_loop_indicator_rise[site]);
		IBUS_LP_INDICATOR_Fall->SetTestResult(site, 0, ibus_loop_indicator_fall[site]);
		IBUS_LP_INDICATOR_Hys->SetTestResult(site, 0, ibus_loop_indicator_hys[site]);
	}
    return 0;
}
 
DUT_API int AMUX_VBAT_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_VBAT_Gain = StsGetParam(funcindex, "AMUX_VBAT_Gain");
    CParam *AMUX_VBAT_Vin = StsGetParam(funcindex, "AMUX_VBAT_Vin");
    CParam *AMUX_VBAT_Vout = StsGetParam(funcindex, "AMUX_VBAT_Vout");
    CParam *AMUX_VBAT_Self_Accur = StsGetParam(funcindex, "AMUX_VBAT_Self_Accur");
    CParam *AMUX_VBAT_3P0V_Accur = StsGetParam(funcindex, "AMUX_VBAT_3P0V_Accur");
    CParam *AMUX_VBAT_4P2V_Accur = StsGetParam(funcindex, "AMUX_VBAT_4P2V_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double Vamux_in[SITE_NUM] = { 0 };
	double Vamux_out_4p2v[SITE_NUM] = { 0 };
	double Vamux_out_3v[SITE_NUM] = { 0 };
	double Gain_vbat[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Self_accuacy[SITE_NUM] = { 0 };
	double Loop_accuracy_4p2v[SITE_NUM] = { 0 };
	double Loop_accuracy_3v[SITE_NUM] = { 0 };
	double R_amux = 200000;
	cbite.SetOn(K1_PGND2AGND,K30_VBAT_Cap, K25_VCC_Cap,-1);
	delay_ms(3);
	VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);

	//==============VBUS =4.2V
	AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x10);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_in[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	}
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_vbat[site] = 1.2/(Ireference[site] * R_amux);
	}
	I2CWriteSameData(DEV_ADDR, 0x11, 0x10);//		field[(CHANNEL_MUX,0)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_4p2v[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vbat[site];//V
	}

	//==============VBUS =3V
	VBAT_ACM.Set(FV, 3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_3v[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vbat[site];//V
		Self_accuacy[site] = 100 * (Vamux_out_4p2v[site] - Vamux_in[site]) / Vamux_in[site];
		Loop_accuracy_4p2v[site] = 1000 * (Vamux_out_4p2v[site] - 4.2*spec[DEVICE_SEL]("VBAT_RSNS_Ratio"));
		Loop_accuracy_3v[site] = 1000 * (Vamux_out_3v[site] - 3.0*spec[DEVICE_SEL]("VBAT_RSNS_Ratio"));
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	}


	FOR_EACH_VALID_SITE(site)
	{
		AMUX_VBAT_Gain->SetTestResult(site, 0, abs(Gain_vbat[site]));
		AMUX_VBAT_Vin->SetTestResult(site, 0, Vamux_in[site]);
		AMUX_VBAT_Vout->SetTestResult(site, 0, Vamux_out_4p2v[site]);
		AMUX_VBAT_Self_Accur->SetTestResult(site, 0, Self_accuacy[site]);
		AMUX_VBAT_4P2V_Accur->SetTestResult(site, 0, Loop_accuracy_4p2v[site]);
		AMUX_VBAT_3P0V_Accur->SetTestResult(site, 0, Loop_accuracy_3v[site]);
	}

    return 0;
}
 
DUT_API int AMUX_NTC_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_NTC_Gain = StsGetParam(funcindex, "AMUX_NTC_Gain");
    CParam *AMUX_NTC_Vin = StsGetParam(funcindex, "AMUX_NTC_Vin");
    CParam *AMUX_NTC_Vout = StsGetParam(funcindex, "AMUX_NTC_Vout");
    CParam *AMUX_NTC_Accur = StsGetParam(funcindex, "AMUX_NTC_Accur");
    CParam *AMUX_NTC_Self_Accur = StsGetParam(funcindex, "AMUX_NTC_Self_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	double Vamux_in[SITE_NUM] = { 0 };
	double Vamux_out[SITE_NUM] = { 0 };
	double Gain_vntc[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Self_accuacy[SITE_NUM] = { 0 };
	double Loop_accuracy[SITE_NUM] = { 0 };
	double R_amux = 200000;
	if (!TTR)
	{
		cbite.SetOn(K30_VBAT_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		//==============VBUS =4.2V
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		NTC_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
		entertestmode();
	}
	else
	{
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
		delay_ms(1);
	}
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1D);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_in[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	}
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_vntc[site] = 1.2 / (Ireference[site] * R_amux);
	}

	I2CWriteSameData(DEV_ADDR, 0x11, 0x1D);//		field[(CHANNEL_MUX,13)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vntc[site];//V
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_1MA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_in[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
		Self_accuacy[site] = 100 * (Vamux_out[site] - Vamux_in[site]) / Vamux_in[site];
		Loop_accuracy[site] = 100 * (Vamux_out[site] - 1) / 1;
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		AMUX_NTC_Gain->SetTestResult(site, 0, abs(Gain_vntc[site]));
		AMUX_NTC_Vin->SetTestResult(site, 0, Vamux_in[site]);
		AMUX_NTC_Vout->SetTestResult(site, 0, Vamux_out[site]);
		AMUX_NTC_Accur->SetTestResult(site, 0, Loop_accuracy[site]);
		AMUX_NTC_Self_Accur->SetTestResult(site, 0, Self_accuacy[site]);
	}
	return 0;
}

DUT_API int AMUX_NTC2_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_NTC2_Gain = StsGetParam(funcindex, "AMUX_NTC2_Gain");
    CParam *AMUX_NTC2_Vin = StsGetParam(funcindex, "AMUX_NTC2_Vin");
    CParam *AMUX_NTC2_Vout = StsGetParam(funcindex, "AMUX_NTC2_Vout");
    CParam *AMUX_NTC2_Accur = StsGetParam(funcindex, "AMUX_NTC2_Accur");
    CParam *AMUX_NTC2_Self_Accur = StsGetParam(funcindex, "AMUX_NTC2_Self_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here
	double Vamux_in[SITE_NUM] = { 0 };
	double Vamux_out[SITE_NUM] = { 0 };
	double Gain_vntc2[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Self_accuacy[SITE_NUM] = { 0 };
	double Loop_accuracy[SITE_NUM] = { 0 };
	double R_amux = 200000;
	if (!TTR)
	{
		cbite.SetOn(K30_VBAT_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		//==============VBUS =4.2V
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBATD_ACM.Set(FV, 1.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(5);
		entertestmode();
	}
	else
	{
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_100UA, FOVIe_RELAY_ON);
		VBATD_ACM.Set(FV, 1.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
	}
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1A);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_in[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	}
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_vntc2[site] = 1.2 / (Ireference[site] * R_amux);
	}

	I2CWriteSameData(DEV_ADDR, 0x11, 0x1A);//		field[(CHANNEL_MUX,13)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vntc2[site];//V
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_1MA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_in[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
		Self_accuacy[site] = 100 * (Vamux_out[site] - Vamux_in[site]) / Vamux_in[site];
		Loop_accuracy[site] = 100 * (Vamux_out[site] - 1.5) / 1.5;
	}
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		NTC_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}
	else
	{
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	}

	FOR_EACH_VALID_SITE(site)
	{
		AMUX_NTC2_Gain->SetTestResult(site, 0, abs(Gain_vntc2[site]));
		AMUX_NTC2_Vin->SetTestResult(site, 0, Vamux_in[site]);
		AMUX_NTC2_Vout->SetTestResult(site, 0, Vamux_out[site]);
		AMUX_NTC2_Accur->SetTestResult(site, 0, Loop_accuracy[site]);
		AMUX_NTC2_Self_Accur->SetTestResult(site, 0, Self_accuacy[site]);
	}

	return 0;
}


DUT_API int AMUX_VAC1_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_VAC1_Gain = StsGetParam(funcindex, "AMUX_VAC1_Gain");
    CParam *AMUX_VAC1_Vin = StsGetParam(funcindex, "AMUX_VAC1_Vin");
    CParam *AMUX_VAC1_Vout = StsGetParam(funcindex, "AMUX_VAC1_Vout");
    CParam *AMUX_VAC1_Accur = StsGetParam(funcindex, "AMUX_VAC1_Accur");
    CParam *AMUX_VAC1_Self_Accur = StsGetParam(funcindex, "AMUX_VAC1_Self_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	double Vamux_in[SITE_NUM] = { 0 };
	double Vamux_out[SITE_NUM] = { 0 };
	double Gain_vac1[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Self_accuacy[SITE_NUM] = { 0 };
	double Loop_accuracy[SITE_NUM] = { 0 };
	double R_amux = 200000;
	if (!TTR)
	{
		cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x11, 0x11);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
		I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,31)]
	}
	else
	{
		cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
		I2CWriteSameData(DEV_ADDR, 0x11, 0x11);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
		I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,31)]
	}
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_in[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	}
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	delay_ms(2);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_vac1[site] = 1.2 / (Ireference[site] * R_amux);
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x11);//		field[(CHANNEL_MUX,1)]
	delay_ms(1);
	double Vamux_base[SITE_NUM] = { 0 };
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vac1[site];//V
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vac1[site];//V
	}

	VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vac1[site] - Vamux_base[site];//V
		Self_accuacy[site] = 100 * (Vamux_out[site] - Vamux_in[site]) / Vamux_in[site];
		Loop_accuracy[site] = 100 * (Vamux_out[site] - V_TYP_VAC*0.1) / (V_TYP_VAC*0.1);
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	}


	FOR_EACH_VALID_SITE(site)
	{
		AMUX_VAC1_Gain->SetTestResult(site, 0, abs(Gain_vac1[site]));
		AMUX_VAC1_Vin->SetTestResult(site, 0, Vamux_in[site]);
		AMUX_VAC1_Vout->SetTestResult(site, 0, Vamux_out[site]);
		AMUX_VAC1_Accur->SetTestResult(site, 0, Loop_accuracy[site]);
		AMUX_VAC1_Self_Accur->SetTestResult(site, 0, Self_accuacy[site]);
	}

    return 0;
}
 
DUT_API int AMUX_VAC2_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_VAC2_Gain = StsGetParam(funcindex, "AMUX_VAC2_Gain");
    CParam *AMUX_VAC2_Vin = StsGetParam(funcindex, "AMUX_VAC2_Vin");
    CParam *AMUX_VAC2_Vout = StsGetParam(funcindex, "AMUX_VAC2_Vout");
    CParam *AMUX_VAC2_Accur = StsGetParam(funcindex, "AMUX_VAC2_Accur");
    CParam *AMUX_VAC2_Self_Accur = StsGetParam(funcindex, "AMUX_VAC2_Self_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double Vamux_in[SITE_NUM] = { 0 };
	double Vamux_out[SITE_NUM] = { 0 };
	double Gain_vac2[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Self_accuacy[SITE_NUM] = { 0 };
	double Loop_accuracy[SITE_NUM] = { 0 };
	double R_amux = 200000;
	if (!TTR)
	{
		cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K36_SHARE2_VAC, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
	}
	else
	{
		cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K36_SHARE2_VAC, K25_VCC_Cap, -1);
		delay_ms(3);
		VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
	}
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x12);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,2)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_in[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	}
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(2);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_vac2[site] = 1.2 / (Ireference[site] * R_amux);
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x12);//		field[(CHANNEL_MUX,2)]
	delay_ms(1);
	double Vamux_base[SITE_NUM] = { 0 };
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vac2[site];//V
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vac2[site];//V
	}
	VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vac2[site] - Vamux_base[site];//V
		Self_accuacy[site] = 100 * (Vamux_out[site] - Vamux_in[site]) / Vamux_in[site];
		Loop_accuracy[site] = 100 * (Vamux_out[site] - V_TYP_VAC*0.1) / (V_TYP_VAC*0.1);
	}
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	}



	FOR_EACH_VALID_SITE(site)
	{
		AMUX_VAC2_Gain->SetTestResult(site, 0, abs(Gain_vac2[site]));
		AMUX_VAC2_Vin->SetTestResult(site, 0, Vamux_in[site]);
		AMUX_VAC2_Vout->SetTestResult(site, 0, Vamux_out[site]);
		AMUX_VAC2_Accur->SetTestResult(site, 0, Loop_accuracy[site]);
		AMUX_VAC2_Self_Accur->SetTestResult(site, 0, Self_accuacy[site]);
	}

    return 0;
}
 
DUT_API int AMUX_VAC3_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_VAC3_Gain = StsGetParam(funcindex, "AMUX_VAC3_Gain");
    CParam *AMUX_VAC3_Vin = StsGetParam(funcindex, "AMUX_VAC3_Vin");
    CParam *AMUX_VAC3_Vout = StsGetParam(funcindex, "AMUX_VAC3_Vout");
    CParam *AMUX_VAC3_Accur = StsGetParam(funcindex, "AMUX_VAC3_Accur");
    CParam *AMUX_VAC3_Self_Accur = StsGetParam(funcindex, "AMUX_VAC3_Self_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double Vamux_in[SITE_NUM] = { 0 };
	double Vamux_out[SITE_NUM] = { 0 };
	double Gain_vac3[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Self_accuacy[SITE_NUM] = { 0 };
	double Loop_accuracy[SITE_NUM] = { 0 };
	double R_amux = 200000;
	if (!TTR)
	{
		cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K35_SHARE1_VAC, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
	}
	else
	{
		cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K35_SHARE1_VAC, K25_VCC_Cap, -1);
		delay_ms(3);
		VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
	}
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x13);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,2)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_in[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	}
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	//AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_vac3[site] = 1.2 / (Ireference[site] * R_amux);
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x13);//		field[(CHANNEL_MUX,1)]
	delay_ms(1);
	double Vamux_base[SITE_NUM] = { 0 };
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vac3[site];//V
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vac3[site];//V
	}
	VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vac3[site] - Vamux_base[site];//V
		Self_accuacy[site] = 100 * (Vamux_out[site] - Vamux_in[site]) / Vamux_in[site];
		Loop_accuracy[site] = 100 * (Vamux_out[site] - V_TYP_VAC*0.1) / (V_TYP_VAC*0.1);
	}

	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VAC123_ACM.Set(FV, V_TYP_VAC, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FI, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	}


	FOR_EACH_VALID_SITE(site)
	{
		AMUX_VAC3_Gain->SetTestResult(site, 0, abs(Gain_vac3[site]));
		AMUX_VAC3_Vin->SetTestResult(site, 0, Vamux_in[site]);
		AMUX_VAC3_Vout->SetTestResult(site, 0, Vamux_out[site]);
		AMUX_VAC3_Accur->SetTestResult(site, 0, Loop_accuracy[site]);
		AMUX_VAC3_Self_Accur->SetTestResult(site, 0, Self_accuacy[site]);
	}


    return 0;
}
 
DUT_API int AMUX_VBUS_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_VBUS_Gain = StsGetParam(funcindex, "AMUX_VBUS_Gain");
    CParam *AMUX_VBUS_Vin = StsGetParam(funcindex, "AMUX_VBUS_Vin");
    CParam *AMUX_VBUS_Vout = StsGetParam(funcindex, "AMUX_VBUS_Vout");
    CParam *AMUX_VBUS_Self_Accur = StsGetParam(funcindex, "AMUX_VBUS_Self_Accur");
    CParam *AMUX_VBUS_5V_Accur = StsGetParam(funcindex, "AMUX_VBUS_5V_Accur");
    CParam *AMUX_VBUS_9V_Accur = StsGetParam(funcindex, "AMUX_VBUS_9V_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here
	double Vamux_in[SITE_NUM] = { 0 };
	double Vamux_out_5v[SITE_NUM] = { 0 };
	double Vamux_out_9v[SITE_NUM] = { 0 };
	double Gain_vbus[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Self_accuacy[SITE_NUM] = { 0 };
	double Loop_accuracy_5v[SITE_NUM] = { 0 };
	double Loop_accuracy_9v[SITE_NUM] = { 0 };
	double R_amux = 200000;
	if (!TTR)
	{
		cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K16_VBUS_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
	}
	else
	{
		cbite.SetOn(K1_PGND2AGND, K30_VBAT_Cap, K16_VBUS_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		VBUS_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
	}
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x14);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,4)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,31)]
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_in[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(2);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_vbus[site] = 1.2 / (Ireference[site] * R_amux);
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x14);//		field[(CHANNEL_MUX,1)]
	delay_ms(1);
	double Vamux_base[SITE_NUM] = { 0 };
	VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vbus[site];//V
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(3);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vbus[site];//V
	}


	VBUS_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(5);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_5v[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vbus[site] - Vamux_base[site];//V
		Self_accuacy[site] = 100 * (Vamux_out_5v[site] - Vamux_in[site]) / Vamux_in[site];
		Loop_accuracy_5v[site] = 100 * (Vamux_out_5v[site] - 5 * 0.1) / (5 * 0.1);
	}

	VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	delay_ms(5);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_9v[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_vbus[site] - Vamux_base[site];//V
		Loop_accuracy_9v[site] = 100 * (Vamux_out_9v[site] - 9 * 0.1) / (9 * 0.1);
	}
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
	}


	FOR_EACH_VALID_SITE(site)
	{
		AMUX_VBUS_Gain->SetTestResult(site, 0, abs(Gain_vbus[site]));
		AMUX_VBUS_Vin->SetTestResult(site, 0, Vamux_in[site]);
		AMUX_VBUS_Vout->SetTestResult(site, 0, Vamux_out_5v[site]);
		AMUX_VBUS_Self_Accur->SetTestResult(site, 0, Self_accuacy[site]);
		AMUX_VBUS_5V_Accur->SetTestResult(site, 0, Loop_accuracy_5v[site]);
		AMUX_VBUS_9V_Accur->SetTestResult(site, 0, Loop_accuracy_9v[site]);
	}

    return 0;
}
 
DUT_API int AMUX_IBUS_BU_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_IBUS_Gain = StsGetParam(funcindex, "AMUX_IBUS_Gain");
    CParam *AMUX_IBUS_VinP = StsGetParam(funcindex, "AMUX_IBUS_VinP");
    CParam *AMUX_IBUS_VinN = StsGetParam(funcindex, "AMUX_IBUS_VinN");
    CParam *AMUX_IBUS_Vin = StsGetParam(funcindex, "AMUX_IBUS_Vin");
    CParam *AMUX_IBUS_Vout = StsGetParam(funcindex, "AMUX_IBUS_Vout");
    CParam *AMUX_IBUS_Self_Accur = StsGetParam(funcindex, "AMUX_IBUS_Self_Accur");
    CParam *AMUX_IBUS_BU_0P2A_Accur = StsGetParam(funcindex, "AMUX_IBUS_BU_0P2A_Accur");
    CParam *AMUX_IBUS_BU_0P4A_Accur = StsGetParam(funcindex, "AMUX_IBUS_BU_0P4A_Accur");
    CParam *AMUX_IBUS_BU_1P5A_Accur = StsGetParam(funcindex, "AMUX_IBUS_BU_1P5A_Accur");
    CParam *AMUX_IBUS_BU_3P0A_Accur = StsGetParam(funcindex, "AMUX_IBUS_BU_3P0A_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
     // TODO: Add your function code here

	double Vamux_in[SITE_NUM] = { 0 };
	double Vamux_out_0p2A_buck[SITE_NUM] = { 0 };
	double Vamux_out_0p4A_buck[SITE_NUM] = { 0 };
	double Vamux_out_1p5A_buck[SITE_NUM] = { 0 };
	double Vamux_out_3p0A_buck[SITE_NUM] = { 0 };
	double Vamux_out_0p2A_boost[SITE_NUM] = { 0 };
	double Vamux_out_0p4A_boost[SITE_NUM] = { 0 };
	double Vamux_out_1p5A_boost[SITE_NUM] = { 0 };
	double Vamux_out_3p0A_boost[SITE_NUM] = { 0 };
	double Vamux_inP[SITE_NUM] = { 0 };
	double Vamux_inN[SITE_NUM] = { 0 };
	double Gain_Ibus[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Self_accuacy[SITE_NUM] = { 0 };
	double Loop_accuracy_0p2A_buck[SITE_NUM] = { 0 };
	double Loop_accuracy_0p4A_buck[SITE_NUM] = { 0 };
	double Loop_accuracy_1p5A_buck[SITE_NUM] = { 0 };
	double Loop_accuracy_3p0A_buck[SITE_NUM] = { 0 };
	double Loop_accuracy_0p2A_boost[SITE_NUM] = { 0 };
	double Loop_accuracy_0p4A_boost[SITE_NUM] = { 0 };
	double Loop_accuracy_1p5A_boost[SITE_NUM] = { 0 };
	double Loop_accuracy_3p0A_boost[SITE_NUM] = { 0 };

	double R_amux = 200000;
	if (!TTR)
	{
		cbite.SetOn(K30_VBAT_Cap, K16_VBUS_Cap, K15_BUSH_VBUS, K31_BUSL_PMID, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		entertestmode();
	}
	else
	{
		cbite.SetOn(K30_VBAT_Cap, K16_VBUS_Cap, K15_BUSH_VBUS, K31_BUSL_PMID, K25_VCC_Cap, -1);
		delay_ms(3);
		VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
	}
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x15);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,5)]
	I2CWriteSameData(DEV_ADDR, 0x56, 0xF2);//(ATEST0_MUX,31)]
	FPVI.Set(FI, 0.4, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	delay_ms(10);// AMUX value is small
	AMUX_FOVI.MeasureVI(215, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_inN[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	}

	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,30)]
	FPVI.Set(FI, 0.4, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(10);
	AMUX_FOVI.MeasureVI(215, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_inP[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	}


	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(500);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_Ibus[site] = 1.2 / (Ireference[site] * R_amux);
	}


	double Amux_Ibus_base[SITE_NUM] = { 0 };
	//----------------Buck Mode 0.2A
	I2CWriteSameData(DEV_ADDR, 0x11, 0x15);//(ATEST0_MUX, 5)]
	//FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	//delay_ms(1);
	//AMUX_FOVI.MeasureVI(100, 5);

	//FOR_EACH_VALID_SITE(site)
	//{
	//	Amux_Ibus_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibus[site];//V
	//}
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_us(3000);// cannot save for stable
	AMUX_FOVI.MeasureVI(50, 5);
	//AMUX_FOVI.MeasureVI(2500, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Amux_Ibus_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibus[site];//V
	}

	FPVI.Set(FI, 0.2, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_0p2A_buck[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibus[site] - Amux_Ibus_base[site];//V
	}


	//----------------Buck Mode 0.4A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(500);
	FPVI.Set(FI, 0.4, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_0p4A_buck[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibus[site] - Amux_Ibus_base[site];//V
	}


	//----------------Buck Mode 1.5A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_us(500);
	FPVI.Set(FI, 1.5, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_us(1500);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_1p5A_buck[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibus[site] - Amux_Ibus_base[site];//V
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	//----------------Buck Mode 3A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(500);
	FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(1500);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_3p0A_buck[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibus[site] - Amux_Ibus_base[site];//V
	}

	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	if (!TTR)
	{
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(1);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VBUS_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		Vamux_in[site] = Vamux_inP[site] - Vamux_inN[site];//V
		Self_accuacy[site] = 100 * (Vamux_out_0p4A_buck[site] - Vamux_in[site]) / Vamux_in[site];

		Loop_accuracy_0p2A_buck[site] = 100 * (Vamux_out_0p2A_buck[site] - 0.2*0.4) / (0.2*0.4);
		Loop_accuracy_0p4A_buck[site] = 100 * (Vamux_out_0p4A_buck[site] - 0.4*0.4) / (0.4*0.4);
		Loop_accuracy_1p5A_buck[site] = 100 * (Vamux_out_1p5A_buck[site] - 1.5*0.4) / (1.5*0.4);
		Loop_accuracy_3p0A_buck[site] = 100 * (Vamux_out_3p0A_buck[site] - 3 * 0.4) / (3 * 0.4);

		Loop_accuracy_0p2A_boost[site] = 100 * (Vamux_out_0p2A_boost[site] - 0.2*0.4) / (0.2*0.4);
		Loop_accuracy_0p4A_boost[site] = 100 * (Vamux_out_0p4A_boost[site] - 0.4*0.4) / (0.4*0.4);
		Loop_accuracy_1p5A_boost[site] = 100 * (Vamux_out_1p5A_boost[site] - 1.5*0.4) / (1.5*0.4);
		Loop_accuracy_3p0A_boost[site] = 100 * (Vamux_out_3p0A_boost[site] - 3 * 0.4) / (3 * 0.4);
	}

	FOR_EACH_VALID_SITE(site)
	{
		AMUX_IBUS_Gain->SetTestResult(site, 0, abs(Gain_Ibus[site]));
		AMUX_IBUS_VinP->SetTestResult(site, 0, Vamux_inP[site]);
		AMUX_IBUS_VinN->SetTestResult(site, 0, Vamux_inN[site]);
		AMUX_IBUS_Vin->SetTestResult(site, 0, Vamux_in[site]);
		AMUX_IBUS_Vout->SetTestResult(site, 0, Vamux_out_0p4A_buck[site]);
		AMUX_IBUS_Self_Accur->SetTestResult(site, 0, Self_accuacy[site]);

		AMUX_IBUS_BU_0P2A_Accur->SetTestResult(site, 0, Loop_accuracy_0p2A_buck[site]);
		AMUX_IBUS_BU_0P4A_Accur->SetTestResult(site, 0, Loop_accuracy_0p4A_buck[site]);
		AMUX_IBUS_BU_1P5A_Accur->SetTestResult(site, 0, Loop_accuracy_1p5A_buck[site]);
		AMUX_IBUS_BU_3P0A_Accur->SetTestResult(site, 0, Loop_accuracy_3p0A_buck[site]);
	}


     return 0;
 }
  
DUT_API int AMUX_IBUS_BO_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_IBUS_BO_0P2A_Accur = StsGetParam(funcindex, "AMUX_IBUS_BO_0P2A_Accur");
    CParam *AMUX_IBUS_BO_0P4A_Accur = StsGetParam(funcindex, "AMUX_IBUS_BO_0P4A_Accur");
    CParam *AMUX_IBUS_BO_1P5A_Accur = StsGetParam(funcindex, "AMUX_IBUS_BO_1P5A_Accur");
    CParam *AMUX_IBUS_BO_3P0A_Accur = StsGetParam(funcindex, "AMUX_IBUS_BO_3P0A_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
	 // TODO: Add your function code here

	double Vamux_in[SITE_NUM] = { 0 };
	double Vamux_out_0p2A_boost[SITE_NUM] = { 0 };
	double Vamux_out_0p4A_boost[SITE_NUM] = { 0 };
	double Vamux_out_1p5A_boost[SITE_NUM] = { 0 };
	double Vamux_out_3p0A_boost[SITE_NUM] = { 0 };
	double Gain_Ibus[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Loop_accuracy_0p2A_boost[SITE_NUM] = { 0 };
	double Loop_accuracy_0p4A_boost[SITE_NUM] = { 0 };
	double Loop_accuracy_1p5A_boost[SITE_NUM] = { 0 };
	double Loop_accuracy_3p0A_boost[SITE_NUM] = { 0 };

	double R_amux = 200000;
	if (!TTR)
	{
		cbite.SetOn(K30_VBAT_Cap, K32_PMID_Cap, K15_BUSH_VBUS, K31_BUSL_PMID, K25_VCC_Cap, -1);
		delay_ms(3);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		if (V_TYP_VBUS > 10)
		{
			PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_40V, FOVIe_100MA, FOVIe_RELAY_ON);
		}
		else
		{
			PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		}
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
	}
	else
	{
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
		delay_ms(1);
	}

	// I2CWriteSameData(DEV_ADDR, 0x64, 0x01);
	//===========================================BOOST MODE=======================================//
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);// BUBO_mode=1
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(2);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_Ibus[site] = 1.2 / (Ireference[site] * R_amux);
	}

	double Amux_Ibus_base[SITE_NUM] = { 0 };
	//----------------Boost Mode 0.2A
	I2CWriteSameData(DEV_ADDR, 0x11, 0x15);//
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	//delay_ms(1);
	//AMUX_FOVI.MeasureVI(50, 5);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	Amux_Ibus_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibus[site];//V
	//}
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_us(5500);// cannot remove for stable need
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Amux_Ibus_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibus[site];//V
	}

	FPVI.Set(FI, -0.2, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_0p2A_boost[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibus[site] - Amux_Ibus_base[site];//V
	}


	//----------------Boost Mode 0.4A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(500);
	FPVI.Set(FI, -0.4, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_0p4A_boost[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibus[site] - Amux_Ibus_base[site];//V
	}


	//----------------Boost Mode 1.5A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_ms(1);
	FPVI.Set(FI, -1.5, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_us(1500);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_1p5A_boost[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibus[site] - Amux_Ibus_base[site];//V
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	//----------------Boost Mode 3A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(500);
	FPVI.Set(FI, -3, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(1500);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_3p0A_boost[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibus[site] - Amux_Ibus_base[site];//V
	}

	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(1);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
		PMID_FOVI.Set(FI, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	}


	FOR_EACH_VALID_SITE(site)
	{
		Loop_accuracy_0p2A_boost[site] = 100 * (Vamux_out_0p2A_boost[site] - 0.2*0.4) / (0.2*0.4);
		Loop_accuracy_0p4A_boost[site] = 100 * (Vamux_out_0p4A_boost[site] - 0.4*0.4) / (0.4*0.4);
		Loop_accuracy_1p5A_boost[site] = 100 * (Vamux_out_1p5A_boost[site] - 1.5*0.4) / (1.5*0.4);
		Loop_accuracy_3p0A_boost[site] = 100 * (Vamux_out_3p0A_boost[site] - 3 * 0.4) / (3 * 0.4);
	}

	FOR_EACH_VALID_SITE(site)
	{
		AMUX_IBUS_BO_0P2A_Accur->SetTestResult(site, 0, Loop_accuracy_0p2A_boost[site]);
		AMUX_IBUS_BO_0P4A_Accur->SetTestResult(site, 0, Loop_accuracy_0p4A_boost[site]);
		AMUX_IBUS_BO_1P5A_Accur->SetTestResult(site, 0, Loop_accuracy_1p5A_boost[site]);
		AMUX_IBUS_BO_3P0A_Accur->SetTestResult(site, 0, Loop_accuracy_3p0A_boost[site]);
	}



	 return 0;
 }

DUT_API int AMUX_IBAT_BU_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_IBAT_Gain = StsGetParam(funcindex, "AMUX_IBAT_Gain");
    CParam *AMUX_IBAT_VinP = StsGetParam(funcindex, "AMUX_IBAT_VinP");
    CParam *AMUX_IBAT_VinN = StsGetParam(funcindex, "AMUX_IBAT_VinN");
    CParam *AMUX_IBAT_Vin = StsGetParam(funcindex, "AMUX_IBAT_Vin");
    CParam *AMUX_IBAT_Vout = StsGetParam(funcindex, "AMUX_IBAT_Vout");
    CParam *AMUX_IBAT_Self_Accur = StsGetParam(funcindex, "AMUX_IBAT_Self_Accur");
    CParam *AMUX_IBAT_BU_0P5A_Accur = StsGetParam(funcindex, "AMUX_IBAT_BU_0P5A_Accur");
    CParam *AMUX_IBAT_BU_1P5A_Accur = StsGetParam(funcindex, "AMUX_IBAT_BU_1P5A_Accur");
    CParam *AMUX_IBAT_BU_3P0A_Accur = StsGetParam(funcindex, "AMUX_IBAT_BU_3P0A_Accur");
    CParam *AMUX_IBAT_BU_5P0A_Cal_Accur = StsGetParam(funcindex, "AMUX_IBAT_BU_5P0A_Cal_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here

	double Vamux_in[SITE_NUM] = { 0 };
	double Vamux_out_0p5A_buck[SITE_NUM] = { 0 };
	double Vamux_out_1p5A_buck[SITE_NUM] = { 0 };
	double Vamux_out_3p0A_buck[SITE_NUM] = { 0 };
	double Vamux_outP[SITE_NUM] = { 0 };
	double Vamux_outN[SITE_NUM] = { 0 };
	double Gain_Ibat[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Self_accuacy[SITE_NUM] = { 0 };
	double Loop_accuracy_0p5A_buck[SITE_NUM] = { 0 };
	double Loop_accuracy_1p5A_buck[SITE_NUM] = { 0 };
	double Loop_accuracy_3p0A_buck[SITE_NUM] = { 0 };
	double R_amux = 200000;
	//double amux_offset = 0.009;//20mV, Bench with add compensation in application condition
	double amux_offset = 0;
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, K57_SDA_PU, -1);
		delay_ms(3);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);

		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
	}
	else
	{
		AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(5);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);	
		VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
		BTST_ACM.Set(FV, V_TYP_VBUS, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, V_TYP_VBUS, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_us(500);
		BTST_ACM.Set(FV, V_TYP_VBUS+5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		delay_us(500);
	}
	entertestmode();
	//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,0),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x20);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x17);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(1);

	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x56, 0xF2);//		field[(EN_ATEST0,1),(ATEST0_MUX,30)]
	FPVI.Set(FI, -1.5, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_ms(5);// 3ms atleast
	AMUX_FOVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_outN[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	}

	I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//(ATEST0_MUX,31)]
	FPVI.Set(FI, -1.5, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_ms(10);// 12ms at least
	AMUX_FOVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_outP[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);//(ATEST0_MUX,31)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_Ibat[site] = 1.2 / (Ireference[site] * R_amux);
	}



	double Amux_Ibus_base[SITE_NUM] = { 0 };
	//----------------Buck Mode 0.2A
	I2CWriteSameData(DEV_ADDR, 0x11, 0x17);//(ATEST0_MUX, 7)]
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(10);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Amux_Ibus_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibat[site];//V
	}
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(10);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Amux_Ibus_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibat[site];//V
	}

	//-------------Buck Mode 0.5A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FI, -0.5, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.MeasureVI(50, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_0p5A_buck[site] = AMUX_FOVI.GetMeasResult(site, MIRET)* R_amux*Gain_Ibat[site] - Amux_Ibus_base[site] + amux_offset;//V
	}


	//-------------Buck Mode 1.5A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, -1.5, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_us(1500);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_1p5A_buck[site] = AMUX_FOVI.GetMeasResult(site, MIRET) *R_amux*Gain_Ibat[site] - Amux_Ibus_base[site] + amux_offset;//V
	}

	//-------------Buck Mode 3A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, -3, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(2000);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_3p0A_buck[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibat[site] - Amux_Ibus_base[site] + amux_offset;//V
	}
	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);

		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW

		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_OFF);//BST=SW
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
		delay_ms(2);
	}


	FOR_EACH_VALID_SITE(site)
	{
		Vamux_in[site] = Vamux_outP[site] - Vamux_outN[site];//V
		Self_accuacy[site] = 100 * (Vamux_out_1p5A_buck[site] - Vamux_in[site]) / Vamux_in[site];
		Loop_accuracy_1p5A_buck[site] = 100 * (Vamux_out_1p5A_buck[site] - 1.5*0.1) / (1.5*0.1);
		Loop_accuracy_0p5A_buck[site] = 100 * (Vamux_out_0p5A_buck[site] - 0.5*0.1) / (0.5*0.1);
		Loop_accuracy_3p0A_buck[site] = 100 * (Vamux_out_3p0A_buck[site] - 3.0*0.1) / (3.0*0.1);
	}

	FOR_EACH_VALID_SITE(site)
	{
		AMUX_IBAT_Gain->SetTestResult(site, 0, abs(Gain_Ibat[site]));
		AMUX_IBAT_VinP->SetTestResult(site, 0, Vamux_outP[site]);
		AMUX_IBAT_VinN->SetTestResult(site, 0, Vamux_outN[site]);
		AMUX_IBAT_Vin->SetTestResult(site, 0, Vamux_in[site]);
		AMUX_IBAT_Vout->SetTestResult(site, 0, Vamux_out_1p5A_buck[site]);
		AMUX_IBAT_Self_Accur->SetTestResult(site, 0, Self_accuacy[site]);
		AMUX_IBAT_BU_0P5A_Accur->SetTestResult(site, 0, Loop_accuracy_0p5A_buck[site]);
		AMUX_IBAT_BU_1P5A_Accur->SetTestResult(site, 0, Loop_accuracy_1p5A_buck[site]);
		AMUX_IBAT_BU_3P0A_Accur->SetTestResult(site, 0, Loop_accuracy_3p0A_buck[site]);
		AMUX_IBAT_BU_5P0A_Cal_Accur->SetTestResult(site, 0, Loop_accuracy_3p0A_buck[site]*0.6);
	}

	return 0;
 }
 
DUT_API int AMUX_IBAT_BO_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_IBAT_BO_0P5A_Accur = StsGetParam(funcindex, "AMUX_IBAT_BO_0P5A_Accur");
    CParam *AMUX_IBAT_BO_1P5A_Accur = StsGetParam(funcindex, "AMUX_IBAT_BO_1P5A_Accur");
    CParam *AMUX_IBAT_BO_3P0A_Accur = StsGetParam(funcindex, "AMUX_IBAT_BO_3P0A_Accur");
    CParam *AMUX_IBAT_BO_5P0A_Cal_Accur = StsGetParam(funcindex, "AMUX_IBAT_BO_5P0A_Cal_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
	 // TODO: Add your function code here

	double Vamux_in[SITE_NUM] = { 0 };
	double Vamux_out_0p5A_boost[SITE_NUM] = { 0 };
	double Vamux_out_1p5A_boost[SITE_NUM] = { 0 };
	double Vamux_out_3p0A_boost[SITE_NUM] = { 0 };
	double Vamux_outP[SITE_NUM] = { 0 };
	double Vamux_outN[SITE_NUM] = { 0 };
	double Gain_Ibat[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Self_accuacy[SITE_NUM] = { 0 };
	double Loop_accuracy_0p5A_boost[SITE_NUM] = { 0 };
	double Loop_accuracy_1p5A_boost[SITE_NUM] = { 0 };
	double Loop_accuracy_3p0A_boost[SITE_NUM] = { 0 };
	double R_amux = 200000;
	//double amux_offset = 0.009;//20mV, Bench with add compensation in application condition
	double amux_offset = 0;
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_1V, FOVIe_100UA, FOVIe_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);//BST=SW
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		cbite.SetOn(K1_PGND2AGND, K17_BUSH_SW, K31_BUSL_PMID, K30_VBAT_Cap, K32_PMID_Cap, K25_VCC_Cap, -1);
		delay_ms(3);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		StepUp_PowerOnByPMID_Hsfet(V_TYP_VBUS);
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
	}

	//		field[(WAKE_UP,1),(D2A_BUBO_TM_HSON,1),(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(BUBO_MODE,0),(D2A_BUBO_TM_FORCE_EN_CS,1),(EN_ATEST0,1),(EN_ATEST1,1)(D2A_BUBO_ATEST0,13),(D2A_BUBO_ATEST1,9)]
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);// BUBO_MODE=1
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x09, 0x09);// BUBO_MODE=1
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x58, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x82);
	I2CWriteSameData(DEV_ADDR, 0x61, 0x0B);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(1);
	AMUX_FOVI.MeasureVI(215, 10);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_Ibat[site] = 1.2 / (Ireference[site] * R_amux);
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	double Amux_Ibus_base[SITE_NUM] = { 0 };
	I2CWriteSameData(DEV_ADDR, 0x11, 0x17);//(ATEST0_MUX, 7)]
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);// need >750us
	AMUX_FOVI.MeasureVI(215, 10);// need measure full cylcye
	FOR_EACH_VALID_SITE(site)
	{
		Amux_Ibus_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibat[site];//V
	}
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	//delay_ms(10);
	//AMUX_FOVI.MeasureVI(500, 50);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	Amux_Ibus_base[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibat[site];//V
	//}

	//-------------Boost Mode 0.5A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0.5, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_us(1000);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_0p5A_boost[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibat[site] - Amux_Ibus_base[site] + amux_offset;//V
	}

	//-------------Boost Mode 1.5A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 1.5, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	delay_us(1500);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_1p5A_boost[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibat[site] - Amux_Ibus_base[site] + amux_offset;//V
	}

	//-------------Boost Mode 3A
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 3, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	delay_us(2000);
	AMUX_FOVI.MeasureVI(100, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x59, 0x00);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_3p0A_boost[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Ibat[site] - Amux_Ibus_base[site] + amux_offset;//V
	}

	if (!TTR)
	{
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		StepDown_PowerOffByPMID_Hsfet(V_TYP_VBUS);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		delay_ms(1);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	}
	else
	{
		I2CWriteSameData(DEV_ADDR, 0x59, 0x00);//HS_IN=0,LS_ON=0
		delay_ms(1);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, V_TYP_VBUS, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 5, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_us(500);
		BTST_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 5, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_us(500);
		BTST_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);

		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		PMID_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}


	FOR_EACH_VALID_SITE(site)
	{
		Loop_accuracy_1p5A_boost[site] = 100 * (Vamux_out_1p5A_boost[site] - 1.5*0.1) / (1.5*0.1);
		Loop_accuracy_0p5A_boost[site] = 100 * (Vamux_out_0p5A_boost[site] - 0.5*0.1) / (0.5*0.1);
		Loop_accuracy_3p0A_boost[site] = 100 * (Vamux_out_3p0A_boost[site] - 3.0*0.1) / (3.0*0.1);
	}

	FOR_EACH_VALID_SITE(site)
	{
		AMUX_IBAT_BO_0P5A_Accur->SetTestResult(site, 0, Loop_accuracy_0p5A_boost[site]);
		AMUX_IBAT_BO_1P5A_Accur->SetTestResult(site, 0, Loop_accuracy_1p5A_boost[site]);
		AMUX_IBAT_BO_3P0A_Accur->SetTestResult(site, 0, Loop_accuracy_3p0A_boost[site]);
		AMUX_IBAT_BO_5P0A_Cal_Accur->SetTestResult(site, 0, Loop_accuracy_3p0A_boost[site] * 0.6);
	}

	 return 0;
 }

DUT_API int AMUX_IAC1_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_IAC1_Gain = StsGetParam(funcindex, "AMUX_IAC1_Gain");
    CParam *AMUX_IAC1_Vin = StsGetParam(funcindex, "AMUX_IAC1_Vin");
    CParam *AMUX_IAC1_Vout = StsGetParam(funcindex, "AMUX_IAC1_Vout");
    CParam *AMUX_IAC1_Vamp = StsGetParam(funcindex, "AMUX_IAC1_Vamp");
    CParam *AMUX_IAC1_Self_Accur = StsGetParam(funcindex, "AMUX_IAC1_Self_Accur");
    CParam *AMUX_IAC1_50mA_Accur = StsGetParam(funcindex, "AMUX_IAC1_50mA_Accur");
    CParam *AMUX_IAC1_100mA_Accur = StsGetParam(funcindex, "AMUX_IAC1_100mA_Accur");
    CParam *AMUX_IAC1_200mA_Accur = StsGetParam(funcindex, "AMUX_IAC1_200mA_Accur");
    CParam *AMUX_IAC1_400mA_Accur = StsGetParam(funcindex, "AMUX_IAC1_400mA_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	double Vamux_amp_50ma[SITE_NUM] = { 0 };
	double Vamux_amp_100ma[SITE_NUM] = { 0 };
	double Vamux_amp_200ma[SITE_NUM] = { 0 };
	double Vamux_amp_400ma[SITE_NUM] = { 0 };
	double Vamux_out_50ma[SITE_NUM] = { 0 };
	double Vamux_out_100ma[SITE_NUM] = { 0 };
	double Vamux_out_200ma[SITE_NUM] = { 0 };
	double Vamux_out_400ma[SITE_NUM] = { 0 };

	double Vamux_in[SITE_NUM] = { 0 };
	double Gain_Iac1[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Self_accuacy[SITE_NUM] = { 0 };
	double Loop_accuracy_50ma[SITE_NUM] = { 0 };
	double Loop_accuracy_100ma[SITE_NUM] = { 0 };
	double Loop_accuracy_200ma[SITE_NUM] = { 0 };
	double Loop_accuracy_400ma[SITE_NUM] = { 0 };
	double R_amux = 200000;

	if (!TTR)
	{
		cbite.SetOn(-1);
		delay_ms(3);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		delay_ms(10);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		delay_ms(10);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		double VAC_Base = 8;
		double vcc_v = 4.5;
		cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K9_KELVIN, K10_KELVIN, K11_KELVIN, K12_SHARE, K13_PC, K27_VDRV_AMP, K14_AMP_Force, K45_AMP_Sense, K60_AMP1_Power, -1);
		delay_ms(5);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 4.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, vcc_v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, VAC_Base, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FI, -0.0005, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);//500uA load
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	}
	else
	{
		double VAC_Base = 8;
		double vcc_v = 4.5;
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);


		cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K9_KELVIN, K10_KELVIN, K11_KELVIN, K12_SHARE, K13_PC, K27_VDRV_AMP, K14_AMP_Force, K45_AMP_Sense, K60_AMP1_Power, -1);
		delay_ms(5);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VAC123_ACM.Set(FV, VAC_Base, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 4.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 4.0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FI, -0.0005, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);//500uA load
		//AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	}
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x0A, 0x07);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x18);//(ATEST0_MUX, 8)]
	//I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,31)]
	//delay_ms(1);
	//FPVI.Set(FI, 0.2, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	//delay_ms(10);
	//AMUX_FOVI.MeasureVI(100, 10);
	//FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	//delay_ms(1);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	Vamux_in[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	//}

	AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	//I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(2);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_Iac1[site] = 1.2 / (Ireference[site] * R_amux);
	}

	int failflag = 0;
	double Vamux_amp_0ma[SITE_NUM] = { 0 };
	double Vamux_out_0ma[SITE_NUM] = { 0 };
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1MA, FPVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x18);//(ATEST0_MUX, 8)]
	delay_ms(1);
	//---------------------0mA
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1MA, FPVIe_RELAY_ON);
	delay_ms(20);
	AMUX_FOVI.MeasureVI(215, 10);
	VDRV_AMP_ACM.MeasureVI(200, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_0ma[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Iac1[site];//V
		Vamux_amp_0ma[site] = VDRV_AMP_ACM.GetMeasResult(site, MVRET);// Measure AMP result
	}
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	delay_ms(10);
	bool close_f = false;
	bool failsite[SITE_NUM] = { 0 };
	//-------------------------400mA

	double forcei = 0.4;
	double accur[SITE_NUM] = { 0 };
	FPVI.Set(FI, forcei, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON,1);
	delay_ms(4);
	AMUX_FOVI.MeasureVI(200, 5);
	VDRV_AMP_ACM.MeasureVI(200, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_400ma[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Iac1[site] - Vamux_out_0ma[site]; //V
		Vamux_amp_400ma[site] = VDRV_AMP_ACM.GetMeasResult(site, MVRET) - Vamux_amp_0ma[site];// Measure AMP result
		if (abs(Vamux_out_400ma[site] -Vamux_amp_400ma[site]) / Vamux_amp_400ma[site] > 0.1)
		{
			close_f = true;
			failsite[site] = true;
		}
	}

	if (!close_f)
	{
		delay_ms(100);
		FPVI.Set(FI, forcei, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON, 1);
		delay_ms(4);
		AMUX_FOVI.MeasureVI(200, 5);
		VDRV_AMP_ACM.MeasureVI(200, 10);
		FPVI.MeasureVI(50, 5);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(1);
		FOR_EACH_VALID_SITE(site)
		{
			if (failsite[site])
			{
				Vamux_out_400ma[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Iac1[site] - Vamux_out_0ma[site]; //V
				Vamux_amp_400ma[site] = VDRV_AMP_ACM.GetMeasResult(site, MVRET) - Vamux_amp_0ma[site];// Measure AMP result
			}
		}
	}

	//-------------------------200mA
	FPVI.Set(FI, 0.2, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(5);
	AMUX_FOVI.MeasureVI(200, 5);
	VDRV_AMP_ACM.MeasureVI(200, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_200ma[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Iac1[site] - Vamux_out_0ma[site];//V
		Vamux_amp_200ma[site] = VDRV_AMP_ACM.GetMeasResult(site, MVRET) - Vamux_amp_0ma[site];// Measure AMP result
	}

	//------------------------100mA
	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(1);
	FPVI.Set(FI, 0.1, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(5);
	AMUX_FOVI.MeasureVI(200, 5);
	VDRV_AMP_ACM.MeasureVI(200, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_100ma[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Iac1[site] - Vamux_out_0ma[site];//V
		Vamux_amp_100ma[site] = VDRV_AMP_ACM.GetMeasResult(site, MVRET) - Vamux_amp_0ma[site];// Measure AMP result
	}

	//-------------------------50mA
	FPVI.Set(FI, 0.05, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(5);
	AMUX_FOVI.MeasureVI(200, 5);
	VDRV_AMP_ACM.MeasureVI(200, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_50ma[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Iac1[site] - Vamux_out_0ma[site];//V
		Vamux_amp_50ma[site] = VDRV_AMP_ACM.GetMeasResult(site, MVRET) - Vamux_amp_0ma[site];// Measure AMP result
	}
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);

	if (!TTR)
	{
		AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
		delay_ms(10);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
		AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
		VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);
	}
	else
	{
		VAC123_ACM.Set(FV, 8, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FI, 0, ACM200_20V, ACM200_1MA, ACM200_RELAY_ON);
	}


	FOR_EACH_VALID_SITE(site)
	{
		//Self_accuacy[site] = 10 * (Vamux_out_200ma[site] - Vamux_in[site]) / Vamux_in[site];
		Loop_accuracy_50ma[site] = 100 * (Vamux_out_50ma[site] - Vamux_amp_50ma[site] * 4) / (Vamux_amp_50ma[site] * 4);
		Loop_accuracy_100ma[site] = 100 * (Vamux_out_100ma[site] - Vamux_amp_100ma[site] * 4) / (Vamux_amp_100ma[site] * 4);
		Loop_accuracy_200ma[site] = 100 * (Vamux_out_200ma[site] - Vamux_amp_200ma[site] * 4) / (Vamux_amp_200ma[site] * 4);
		Loop_accuracy_400ma[site] = 100 * (Vamux_out_400ma[site] - Vamux_amp_400ma[site] * 4) / (Vamux_amp_400ma[site] * 4);
	}

	FOR_EACH_VALID_SITE(site)
	{
		AMUX_IAC1_Gain->SetTestResult(site, 0, abs(Gain_Iac1[site]));
		//AMUX_IAC1_Vin->SetTestResult(site, 0, Vamux_in[site]);
		AMUX_IAC1_Vout->SetTestResult(site, 0, Vamux_out_200ma[site]);
		AMUX_IAC1_Vamp->SetTestResult(site, 0, Vamux_amp_200ma[site]);
		//AMUX_IAC1_Self_Accur->SetTestResult(site, 0, Self_accuacy[site]);

		AMUX_IAC1_50mA_Accur->SetTestResult(site, 0, Loop_accuracy_50ma[site]);
		AMUX_IAC1_100mA_Accur->SetTestResult(site, 0, Loop_accuracy_100ma[site]);
		AMUX_IAC1_200mA_Accur->SetTestResult(site, 0, Loop_accuracy_200ma[site]);
		AMUX_IAC1_400mA_Accur->SetTestResult(site, 0, Loop_accuracy_400ma[site]);

	}



    return 0;
}
 
DUT_API int AMUX_IAC2_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *AMUX_IAC2_Gain = StsGetParam(funcindex, "AMUX_IAC2_Gain");
    CParam *AMUX_IAC2_Vin = StsGetParam(funcindex, "AMUX_IAC2_Vin");
    CParam *AMUX_IAC2_Vout = StsGetParam(funcindex, "AMUX_IAC2_Vout");
    CParam *AMUX_IAC2_Vamp = StsGetParam(funcindex, "AMUX_IAC2_Vamp");
    CParam *AMUX_IAC2_Self_Accur = StsGetParam(funcindex, "AMUX_IAC2_Self_Accur");
    CParam *AMUX_IAC2_50mA_Accur = StsGetParam(funcindex, "AMUX_IAC2_50mA_Accur");
    CParam *AMUX_IAC2_100mA_Accur = StsGetParam(funcindex, "AMUX_IAC2_100mA_Accur");
    CParam *AMUX_IAC2_200mA_Accur = StsGetParam(funcindex, "AMUX_IAC2_200mA_Accur");
    CParam *AMUX_IAC2_400mA_Accur = StsGetParam(funcindex, "AMUX_IAC2_400mA_Accur");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here


	double Vamux_amp_50ma[SITE_NUM] = { 0 };
	double Vamux_amp_100ma[SITE_NUM] = { 0 };
	double Vamux_amp_200ma[SITE_NUM] = { 0 };
	double Vamux_amp_400ma[SITE_NUM] = { 0 };
	double Vamux_out_50ma[SITE_NUM] = { 0 };
	double Vamux_out_100ma[SITE_NUM] = { 0 };
	double Vamux_out_200ma[SITE_NUM] = { 0 };
	double Vamux_out_400ma[SITE_NUM] = { 0 };

	double Vamux_in[SITE_NUM] = { 0 };
	double Gain_Iac2[SITE_NUM] = { 0 };
	double Ireference[SITE_NUM] = { 0 };
	double Self_accuacy[SITE_NUM] = { 0 };
	double Loop_accuracy_50ma[SITE_NUM] = { 0 };
	double Loop_accuracy_100ma[SITE_NUM] = { 0 };
	double Loop_accuracy_200ma[SITE_NUM] = { 0 };
	double Loop_accuracy_400ma[SITE_NUM] = { 0 };
	double R_amux = 200000;
	double VAC_Base = 8;
	double vcc_v = 4.5;
	if (!TTR)
	{
		cbite.SetOn(-1);
		delay_ms(3);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		delay_ms(10);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		delay_ms(10);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

		cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K9_KELVIN, K10_KELVIN, K11_KELVIN, K12_SHARE, K13_PC, K27_VDRV_AMP, K14_AMP_Force, K45_AMP_Sense, K60_AMP1_Power, K20_SHARE_KLV, K36_SHARE2_VAC, -1);
		delay_ms(5);
		SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		BTST_ACM.Set(FV, 4.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
		VBAT_ACM.Set(FV, 4.2, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VCC_ACM.Set(FV, vcc_v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		VAC123_ACM.Set(FV, VAC_Base, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		VDRV_AMP_ACM.Set(FI, -0.0005, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);//500uA load
		AMUX_FOVI.Set(FI, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(5);
		entertestmode();
	}
	else
	{
		cbite.SetOn(K30_VBAT_Cap, K37_VAC_Cap, K9_KELVIN, K10_KELVIN, K11_KELVIN, K12_SHARE, K13_PC, K27_VDRV_AMP, K14_AMP_Force, K45_AMP_Sense, K60_AMP1_Power, K20_SHARE_KLV, K36_SHARE2_VAC, -1);
		delay_ms(5);
		VAC123_ACM.Set(FV, VAC_Base, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
		//AMUX_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
		delay_ms(1);
	}
	I2CWriteSameData(DEV_ADDR, 0x0A, 0x07);
	I2CWriteSameData(DEV_ADDR, 0x10, 0x43);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x19);//(ATEST0_MUX, 9)]
	//I2CWriteSameData(DEV_ADDR, 0x56, 0xFA);//		field[(EN_ATEST0,1),(ATEST0_MUX,31)]
	//delay_ms(1);
	//FPVI.Set(FI, 0.2, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	//delay_ms(10);
	//AMUX_FOVI.MeasureVI(100, 5);
	//FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	//delay_ms(1);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	Vamux_in[site] = AMUX_FOVI.GetMeasResult(site, MVRET);//V
	//}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	//I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F);//		field[(WAKE_UP,1),(AMUX_EN,1),(CHANNEL_MUX,15)]
	delay_ms(2);
	AMUX_FOVI.MeasureVI(50, 5);
	FOR_EACH_VALID_SITE(site)
	{
		Ireference[site] = AMUX_FOVI.GetMeasResult(site, MIRET);//uA
		Gain_Iac2[site] = 1.2 / (Ireference[site] * R_amux);
	}

	bool close_f = false;
	bool failsite[SITE_NUM] = { 0 };
	double Vamux_amp_0ma[SITE_NUM] = { 0 };
	double Vamux_out_0ma[SITE_NUM] = { 0 };
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1MA, FPVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	I2CWriteSameData(DEV_ADDR, 0x56, 0x00);
	I2CWriteSameData(DEV_ADDR, 0x11, 0x19);//(ATEST0_MUX, 8)]
	delay_ms(1);
	//---------------------0mA
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1MA, FPVIe_RELAY_ON);
	delay_ms(10);
	AMUX_FOVI.MeasureVI(215, 10);
	VDRV_AMP_ACM.MeasureVI(200, 10);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_0ma[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Iac2[site];//V
		Vamux_amp_0ma[site] = VDRV_AMP_ACM.GetMeasResult(site, MVRET);// Measure AMP result
	}

	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_100UA, FOVIe_RELAY_ON);
	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(10);
	//-------------------------400mA
	double forcei = 0.4;
	FPVI.Set(FI, forcei, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(200, 5);
	VDRV_AMP_ACM.MeasureVI(200, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_400ma[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Iac2[site] - Vamux_out_0ma[site]; //V
		Vamux_amp_400ma[site] = VDRV_AMP_ACM.GetMeasResult(site, MVRET) - Vamux_amp_0ma[site];// Measure AMP result
		if (abs(Vamux_out_400ma[site] - Vamux_amp_400ma[site]) / Vamux_amp_400ma[site] > 0.1)
		{
			close_f = true;
			failsite[site] = true;
		}
	}
	if (!close_f)
	{
		delay_ms(100);
		FPVI.Set(FI, forcei, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON, 1);
		delay_ms(4);
		AMUX_FOVI.MeasureVI(200, 5);
		VDRV_AMP_ACM.MeasureVI(200, 10);
		FPVI.MeasureVI(50, 5);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
		delay_ms(1);
		FOR_EACH_VALID_SITE(site)
		{
			if (failsite[site])
			{
				Vamux_out_400ma[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Iac2[site] - Vamux_out_0ma[site]; //V
				Vamux_amp_400ma[site] = VDRV_AMP_ACM.GetMeasResult(site, MVRET) - Vamux_amp_0ma[site];// Measure AMP result
			}
		}
	}

	//-------------------------200mA
	FPVI.Set(FI, 0.2, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(200, 5);
	VDRV_AMP_ACM.MeasureVI(200, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_200ma[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Iac2[site] - Vamux_out_0ma[site];//V
		Vamux_amp_200ma[site] = VDRV_AMP_ACM.GetMeasResult(site, MVRET) - Vamux_amp_0ma[site];// Measure AMP result
	}

	//------------------------100mA
	AMUX_FOVI.Set(FV, 1, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	delay_ms(1);
	FPVI.Set(FI, 0.1, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(200, 5);
	VDRV_AMP_ACM.MeasureVI(200, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_100ma[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Iac2[site] - Vamux_out_0ma[site];//V
		Vamux_amp_100ma[site] = VDRV_AMP_ACM.GetMeasResult(site, MVRET) - Vamux_amp_0ma[site];// Measure AMP result
	}

	//-------------------------50mA
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_ON);
	FPVI.Set(FI, 0.05, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_ON);
	delay_ms(2);
	AMUX_FOVI.MeasureVI(200, 5);
	VDRV_AMP_ACM.MeasureVI(200, 5);
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_ON);
	delay_ms(1);
	FOR_EACH_VALID_SITE(site)
	{
		Vamux_out_50ma[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*R_amux*Gain_Iac2[site] - Vamux_out_0ma[site];//V
		Vamux_amp_50ma[site] = VDRV_AMP_ACM.GetMeasResult(site, MVRET) - Vamux_amp_0ma[site];// Measure AMP result
	}
	FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);


	AMUX_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_5V, FOVIe_10UA, FOVIe_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_ON);
	
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	if (!TTR)
	{
		VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
		FPVI.Set(FV, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_OFF);
	}
	else
	{
		VAC123_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_100MA, FPVIe_RELAY_ON);
	}	
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_100MA, FOVIe_RELAY_OFF);

	FOR_EACH_VALID_SITE(site)
	{
		//Self_accuacy[site] = 100 * (Vamux_out_200ma[site] - Vamux_in[site]) / Vamux_in[site];
		Loop_accuracy_50ma[site] = 100 * (Vamux_out_50ma[site] - Vamux_amp_50ma[site] * 4) / (Vamux_amp_50ma[site] * 4);
		Loop_accuracy_100ma[site] = 100 * (Vamux_out_100ma[site] - Vamux_amp_100ma[site] * 4) / (Vamux_amp_100ma[site] * 4);
		Loop_accuracy_200ma[site] = 100 * (Vamux_out_200ma[site] - Vamux_amp_200ma[site] * 4) / (Vamux_amp_200ma[site] * 4);
		Loop_accuracy_400ma[site] = 100 * (Vamux_out_400ma[site] - Vamux_amp_400ma[site] * 4) / (Vamux_amp_400ma[site] * 4);
	}


	FOR_EACH_VALID_SITE(site)
	{
		AMUX_IAC2_Gain->SetTestResult(site, 0, abs(Gain_Iac2[site]));
		//AMUX_IAC2_Vin->SetTestResult(site, 0, Vamux_in[site]);
		AMUX_IAC2_Vout->SetTestResult(site, 0, Vamux_out_200ma[site]);
		AMUX_IAC2_Vamp->SetTestResult(site, 0, Vamux_amp_200ma[site]);
		//AMUX_IAC2_Self_Accur->SetTestResult(site, 0, Self_accuacy[site]);

		AMUX_IAC2_50mA_Accur->SetTestResult(site, 0, Loop_accuracy_50ma[site]);
		AMUX_IAC2_100mA_Accur->SetTestResult(site, 0, Loop_accuracy_100ma[site]);
		AMUX_IAC2_200mA_Accur->SetTestResult(site, 0, Loop_accuracy_200ma[site]);
		AMUX_IAC2_400mA_Accur->SetTestResult(site, 0, Loop_accuracy_400ma[site]);

	}
	
    return 0;
}
 
//DEL DUT_API int AMUX_IQ_TEST(short funcindex, LPCTSTR funclabel)
//DEL {
//DEL //{{AFX_STS_PARAM_PROTOTYPES
//DEL     CParam *AMUX_Iwakeup = StsGetParam(funcindex, "AMUX_Iwakeup");
//DEL     CParam *AMUX_Iamux_en = StsGetParam(funcindex, "AMUX_Iamux_en");
//DEL     CParam *AMUX_IQ = StsGetParam(funcindex, "AMUX_IQ");
//DEL //}}AFX_STS_PARAM_PROTOTYPES
//DEL     // TODO: Add your function code here
//DEL 	double Iq_wakeup[SITE_NUM] = { 0 };
//DEL 	double Iq_amux_en[SITE_NUM] = { 0 };
//DEL 	double Iq_amux[SITE_NUM] = { 0 };
//DEL 	dcm.I2CConnect();
//DEL 	cbite.SetOn(K1_PGND2AGND, -1);
//DEL 	delay_ms(3);
//DEL 	VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
//DEL 	VCC_ACM.Set(FI, -0.002, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
//DEL 	delay_ms(5);
//DEL 	entertestmode();
//DEL 	I2CWriteSameData(DEV_ADDR, 0x10, 0x43); //		field[(WAKE_UP,1)]
//DEL 	//VBAT_ACM.Set(FV, V_TYP_VBAT, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
//DEL 	delay_ms(5);
//DEL 	VBAT_ACM.MeasureVI(50, 5);
//DEL 	VCC_ACM.MeasureVI(50, 5);
//DEL 	FOR_EACH_VALID_SITE(site)
//DEL 	{
//DEL 		Iq_wakeup[site] = (VBAT_ACM.GetMeasResult(site, MIRET) + VCC_ACM.GetMeasResult(site, MIRET))*1e6;//uA
//DEL 	}

//DEL 	//---------------------
//DEL 	I2CWriteSameData(DEV_ADDR, 0x11, 0x1F); //		field[(AMUX_EN,1),(CHANNEL_MUX,15)]
//DEL 	delay_ms(3);
//DEL 	VBAT_ACM.MeasureVI(50, 5);
//DEL 	FOR_EACH_VALID_SITE(site)
//DEL 	{
//DEL 		Iq_amux_en[site] = (VBAT_ACM.GetMeasResult(site, MIRET) + VCC_ACM.GetMeasResult(site, MIRET))*1e6;//uA
//DEL 		Iq_amux[site] = Iq_amux_en[site] - Iq_wakeup[site];
//DEL 	}
//DEL 	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
//DEL 	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
//DEL 	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
//DEL 	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

//DEL 	FOR_EACH_VALID_SITE(site)
//DEL 	{
//DEL 		AMUX_Iwakeup->SetTestResult(site, 0, Iq_wakeup[site]);
//DEL 		AMUX_Iamux_en->SetTestResult(site, 0, Iq_amux_en[site]);
//DEL 		AMUX_IQ->SetTestResult(site, 0, Iq_amux[site]);
//DEL 	}

//DEL     return 0;
//DEL }

DUT_API int DIGITAL_TEST(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *SCAN_Check = StsGetParam(funcindex, "SCAN_Check");
    CParam *IDDQ_P1_Check = StsGetParam(funcindex, "IDDQ_P1_Check");
    CParam *IDDQ_P1_Curr = StsGetParam(funcindex, "IDDQ_P1_Curr");
    CParam *IDDQ_P2_Check = StsGetParam(funcindex, "IDDQ_P2_Check");
    CParam *IDDQ_P2_Curr = StsGetParam(funcindex, "IDDQ_P2_Curr");
    CParam *IDDQ_P3_Check = StsGetParam(funcindex, "IDDQ_P3_Check");
    CParam *IDDQ_P3_Curr = StsGetParam(funcindex, "IDDQ_P3_Curr");
    CParam *IDDQ_P4_Check = StsGetParam(funcindex, "IDDQ_P4_Check");
    CParam *IDDQ_P4_Curr = StsGetParam(funcindex, "IDDQ_P4_Curr");
    CParam *IDDQ_P5_Check = StsGetParam(funcindex, "IDDQ_P5_Check");
    CParam *IDDQ_P5_Curr = StsGetParam(funcindex, "IDDQ_P5_Curr");
    CParam *IDDQ_P6_Check = StsGetParam(funcindex, "IDDQ_P6_Check");
    CParam *IDDQ_P6_Curr = StsGetParam(funcindex, "IDDQ_P6_Curr");
    CParam *IDDQ_P7_Check = StsGetParam(funcindex, "IDDQ_P7_Check");
    CParam *IDDQ_P7_Curr = StsGetParam(funcindex, "IDDQ_P7_Curr");
    CParam *IDDQ_P8_Check = StsGetParam(funcindex, "IDDQ_P8_Check");
    CParam *IDDQ_P8_Curr = StsGetParam(funcindex, "IDDQ_P8_Curr");
    CParam *IDDQ_P9_Check = StsGetParam(funcindex, "IDDQ_P9_Check");
    CParam *IDDQ_P9_Curr = StsGetParam(funcindex, "IDDQ_P9_Curr");
    CParam *IDDQ_P10_Check = StsGetParam(funcindex, "IDDQ_P10_Check");
    CParam *IDDQ_P10_Curr = StsGetParam(funcindex, "IDDQ_P10_Curr");
    CParam *IDDQ_P11_Check = StsGetParam(funcindex, "IDDQ_P11_Check");
    CParam *IDDQ_P11_Curr = StsGetParam(funcindex, "IDDQ_P11_Curr");
//}}AFX_STS_PARAM_PROTOTYPES
	// TODO: Add your function code here


	dcm.Connect("INT");
	dcm.Connect("NTC");
	dcm.Connect("SCL");
	dcm.Connect("SDA");

	int nPinResult = 0;
	//ULONG scan_enable[SITE_NUM];
	double scan_pre_enter[SITE_NUM] = { 0 };
	double scan_pos_enter[SITE_NUM] = { 0 };
	dcm.I2CConnect();//Connect all relay of each site.
	cbite.SetOn(K1_PGND2AGND, K58_INT_PU, K30_VBAT_Cap,-1);
	delay_ms(3);
	VBAT_ACM.Set(FV, 4, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x52, 0x8C);
	I2CWriteSameData(DEV_ADDR, 0x52, 0xB1);
	I2CWriteSameData(DEV_ADDR, 0x52, 0x37);
	I2CWriteSameData(DEV_ADDR, 0x52, 0x82);
	delay_ms(1);
	dcm.Connect("G_ALLPIN");//connect channel relay
	dcm.InitMCU("G_ALLPIN");//Initialize the MCU
	dcm.SetPinLevel("G_CLK", 5, -0.5, 0, 0);
	dcm.SetPinLevel("G_OUT", 0, 0, 2.5, 0.5);
	dcm.RunVectorWithGroup("G_ALLPIN", "scan_start", "scan_stop");
	dcm.SaveFailMap(0);

	int Scan_pass[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		if (Scan_pat_load_succeess)
		{
			Scan_pass[site] = dcm.GetMCUPinResult("INT", site);
			SCAN_Check->SetTestResult(site, 0, Scan_pass[site]);
		}
		else
		{
			SCAN_Check->SetTestResult(site, 0, -1);
		}

	}
	dcm.Disconnect("G_ALLPIN");// disconnect channel relay	

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_OFF);


	double vbat_curr[SITE_NUM] = { 0 };
	dcm.I2CConnect();//Connect all relay of each site.
	cbite.SetOn(K29_BUSL_VBAT, K17_BUSH_SW,K43_INT_ACM, -1);
	//cbite.SetOn(K29_BUSL_VBAT, K17_BUSH_SW, K58_INT_PU, -1);
	delay_ms(5);
	SDA_INT_ACM.Set(FV, 4.0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 4.5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 6, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 6, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	entertestmode();
	I2CWriteSameData(DEV_ADDR, 0x52, 0x8C);
	I2CWriteSameData(DEV_ADDR, 0x52, 0xB1);
	I2CWriteSameData(DEV_ADDR, 0x52, 0x37);
	I2CWriteSameData(DEV_ADDR, 0x52, 0x82);
	//delay_ms(250);
	//VBAT_ACM.MeasureVI(500, 500);
	//FOR_EACH_VALID_SITE(site)
	//{
	//	vbat_curr[site] = VBAT_ACM.GetMeasResult(site, MIRET);
	//}
	//VBAT_ACM.Set(FV, 4.5, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
	//VBAT_ACM.MeasureVI(4000, 50);
	dcm.Connect("G_ALLPIN");//connect channel relay
	dcm.InitMCU("G_ALLPIN");//Initialize the MCU
	dcm.SetPinLevel("G_CLK", 5, -0.5, 0, 0);
	dcm.SetPinLevel("G_OUT", 0, 0, 2.0, 0.75);
	dcm.RunVectorWithGroup("G_ALLPIN", "iddq_start1", "iddq_stop1");
	dcm.SaveFailMap(0);
	//----------------IDDQ Test, Config =1
	double curr[SITE_NUM] = { 0 };
	FOR_EACH_VALID_SITE(site)
	{
		nPinResult = dcm.GetMCUPinResult("INT", site);
		IDDQ_P1_Check->SetTestResult(site, 0, nPinResult);
	}

	VBAT_ACM.Set(FV, 4.5, ACM200_10V, ACM200_1MA, ACM200_RELAY_ON);
	delay_ms(2);
	VBAT_ACM.MeasureVI(50, 10);
	SDA_INT_ACM.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		curr[site] = VBAT_ACM.GetMeasResult(site, MIRET);
		IDDQ_P1_Curr->SetTestResult(site, 0, curr[site] * 1e6);
	}

	//----------------IDDQ Test, Config =2
	dcm.RunVectorWithGroup("G_ALLPIN", "iddq_start2", "iddq_stop2");
	dcm.SaveFailMap(0);
	FOR_EACH_VALID_SITE(site)
	{
		nPinResult = dcm.GetMCUPinResult("INT", site);
		IDDQ_P2_Check->SetTestResult(site, 0, nPinResult);
	}
	delay_us(500);
	VBAT_ACM.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		curr[site] = VBAT_ACM.GetMeasResult(site, MIRET);
		IDDQ_P2_Curr->SetTestResult(site, 0, curr[site] * 1e6);
	}

	//----------------IDDQ Test, Config =3
	dcm.RunVectorWithGroup("G_ALLPIN", "iddq_start3", "iddq_stop3");
	dcm.SaveFailMap(0);
	FOR_EACH_VALID_SITE(site)
	{
		nPinResult = dcm.GetMCUPinResult("INT", site);
		IDDQ_P3_Check->SetTestResult(site, 0, nPinResult);
	}
	delay_us(500);
	VBAT_ACM.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		curr[site] = VBAT_ACM.GetMeasResult(site, MIRET);
		IDDQ_P3_Curr->SetTestResult(site, 0, curr[site] * 1e6);
	}

	//----------------IDDQ Test, Config =4
	dcm.RunVectorWithGroup("G_ALLPIN", "iddq_start4", "iddq_stop4");
	dcm.SaveFailMap(0);
	FOR_EACH_VALID_SITE(site)
	{
		nPinResult = dcm.GetMCUPinResult("INT", site);
		IDDQ_P4_Check->SetTestResult(site, 0, nPinResult);
	}
	delay_us(500);
	VBAT_ACM.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		curr[site] = VBAT_ACM.GetMeasResult(site, MIRET);
		IDDQ_P4_Curr->SetTestResult(site, 0, curr[site] * 1e6);
	}

	//----------------IDDQ Test, Config =5
	dcm.RunVectorWithGroup("G_ALLPIN", "iddq_start5", "iddq_stop5");
	dcm.SaveFailMap(0);
	FOR_EACH_VALID_SITE(site)
	{
		nPinResult = dcm.GetMCUPinResult("INT", site);
		IDDQ_P5_Check->SetTestResult(site, 0, nPinResult);
	}
	delay_us(500);
	VBAT_ACM.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		curr[site] = VBAT_ACM.GetMeasResult(site, MIRET);
		IDDQ_P5_Curr->SetTestResult(site, 0, curr[site] * 1e6);
	}

	//----------------IDDQ Test, Config =6
	dcm.RunVectorWithGroup("G_ALLPIN", "iddq_start6", "iddq_stop6");
	dcm.SaveFailMap(0);
	FOR_EACH_VALID_SITE(site)
	{
		nPinResult = dcm.GetMCUPinResult("INT", site);
		IDDQ_P6_Check->SetTestResult(site, 0, nPinResult);
	}
	delay_us(500);
	VBAT_ACM.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		curr[site] = VBAT_ACM.GetMeasResult(site, MIRET);
		IDDQ_P6_Curr->SetTestResult(site, 0, curr[site] * 1e6);
	}


	//----------------IDDQ Test, Config =7
	dcm.RunVectorWithGroup("G_ALLPIN", "iddq_start7", "iddq_stop7");
	dcm.SaveFailMap(0);
	FOR_EACH_VALID_SITE(site)
	{
		nPinResult = dcm.GetMCUPinResult("INT", site);
		IDDQ_P7_Check->SetTestResult(site, 0, nPinResult);
	}
	delay_us(500);
	VBAT_ACM.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		curr[site] = VBAT_ACM.GetMeasResult(site, MIRET);
		IDDQ_P7_Curr->SetTestResult(site, 0, curr[site] * 1e6);
	}

	//----------------IDDQ Test, Config =8
	dcm.RunVectorWithGroup("G_ALLPIN", "iddq_start8", "iddq_stop8");
	dcm.SaveFailMap(0);
	FOR_EACH_VALID_SITE(site)
	{
		nPinResult = dcm.GetMCUPinResult("INT", site);
		IDDQ_P8_Check->SetTestResult(site, 0, nPinResult);
	}
	delay_us(500);
	VBAT_ACM.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		curr[site] = VBAT_ACM.GetMeasResult(site, MIRET);
		IDDQ_P8_Curr->SetTestResult(site, 0, curr[site] * 1e6);
	}

	//----------------IDDQ Test, Config =9
	dcm.RunVectorWithGroup("G_ALLPIN", "iddq_start9", "iddq_stop9");
	dcm.SaveFailMap(0);
	FOR_EACH_VALID_SITE(site)
	{
		nPinResult = dcm.GetMCUPinResult("INT", site);
		IDDQ_P9_Check->SetTestResult(site, 0, nPinResult);
	}
	delay_us(500);
	VBAT_ACM.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		curr[site] = VBAT_ACM.GetMeasResult(site, MIRET);
		IDDQ_P9_Curr->SetTestResult(site, 0, curr[site] * 1e6);
	}

	//----------------IDDQ Test, Config =10
	dcm.RunVectorWithGroup("G_ALLPIN", "iddq_start10", "iddq_stop10");
	dcm.SaveFailMap(0);
	FOR_EACH_VALID_SITE(site)
	{
		nPinResult = dcm.GetMCUPinResult("INT", site);
		IDDQ_P10_Check->SetTestResult(site, 0, nPinResult);
	}
	delay_us(500);
	VBAT_ACM.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		curr[site] = VBAT_ACM.GetMeasResult(site, MIRET);
		IDDQ_P10_Curr->SetTestResult(site, 0, curr[site] * 1e6);
	}

	//----------------IDDQ Test, Config =11
	dcm.RunVectorWithGroup("G_ALLPIN", "iddq_start11", "iddq_stop11");
	dcm.SaveFailMap(0);
	FOR_EACH_VALID_SITE(site)
	{
		nPinResult = dcm.GetMCUPinResult("INT", site);
		IDDQ_P11_Check->SetTestResult(site, 0, nPinResult);
	}
	delay_us(500);
	VBAT_ACM.MeasureVI(50, 10);
	FOR_EACH_VALID_SITE(site)
	{
		curr[site] = VBAT_ACM.GetMeasResult(site, MIRET);
		IDDQ_P11_Curr->SetTestResult(site, 0, curr[site] * 1e6);
	}

	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	cbite.SetOn(-1);
	delay_ms(3);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_OFF);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	dcm.Disconnect("G_ALLPIN");// disconnect channel relay	
	delay_us(200);
	dcm.I2CConnect();//Connect all relay of each site.

	return 0;
}

DUT_API int Operation_Leakage(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_19V_Leak = StsGetParam(funcindex, "VBUS_19V_Leak");
    CParam *PMID_19V_Leak = StsGetParam(funcindex, "PMID_19V_Leak");
    CParam *SW_19V_Leak = StsGetParam(funcindex, "SW_19V_Leak");
    CParam *BTST_25V_Leak = StsGetParam(funcindex, "BTST_25V_Leak");
    CParam *VBAT_5V_Leak = StsGetParam(funcindex, "VBAT_5V_Leak");
    CParam *NTC2_5V_Leak = StsGetParam(funcindex, "NTC2_5V_Leak");
    CParam *AMUX_5V_Leak = StsGetParam(funcindex, "AMUX_5V_Leak");
    CParam *NTC_5V_Leak = StsGetParam(funcindex, "NTC_5V_Leak");
    CParam *VCC_5V_Leak = StsGetParam(funcindex, "VCC_5V_Leak");
    CParam *VAC1_20V_Leak = StsGetParam(funcindex, "VAC1_20V_Leak");
    CParam *VAC2_20V_Leak = StsGetParam(funcindex, "VAC2_20V_Leak");
    CParam *VAC3_20V_Leak = StsGetParam(funcindex, "VAC3_20V_Leak");
    CParam *KLV1_20V_Leak = StsGetParam(funcindex, "KLV1_20V_Leak");
    CParam *KLV2_20V_Leak = StsGetParam(funcindex, "KLV2_20V_Leak");
    CParam *ACDRV1_24V_Leak = StsGetParam(funcindex, "ACDRV1_24V_Leak");
    CParam *ACDRV2_24V_Leak = StsGetParam(funcindex, "ACDRV2_24V_Leak");
    CParam *ACDRV3_24V_Leak = StsGetParam(funcindex, "ACDRV3_24V_Leak");
    CParam *VDRV_5V_Leak = StsGetParam(funcindex, "VDRV_5V_Leak");
    CParam *SCL_5V_Leak = StsGetParam(funcindex, "SCL_5V_Leak");
    CParam *SDA_5V_Leak = StsGetParam(funcindex, "SDA_5V_Leak");
    CParam *INT_5V_Leak = StsGetParam(funcindex, "INT_5V_Leak");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here


	double oper_high_leak[SITE_NUM] = { 0 };
	double oper_low_leak[SITE_NUM] = { 0 };
	double oper_25v = 25;
	double oper_24v = 24;
	double oper_20v = 20;
	double oper_19v = 19;
	double oper_5v = 5;
	int wait_time = 500;
	dcm.Disconnect("SCL");
	dcm.Disconnect("SDA");
	QVM_GP.Disconnect();
	QTMU_GP.Disconnect(QTMUe_RELAY_CHA);

	cbite.SetOn(-1);
	delay_ms(3);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_100MA, FPVIe_RELAY_OFF);
	SW_ACM.Set(FV, 0, ACM200_40V, ACM200_200MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_200MA, ACM200_RELAY_ON);
	//================ACDRV1 ABS Leakage, 29V
	ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, oper_24v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, oper_24v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	Retest_current_unstable_with_time_out(ACDRV123_ACM, oper_high_leak, spec.get_low_limit("ACDRV1_24V_Leak"), spec.get_high_limit("ACDRV1_24V_Leak"), 1, 100, MEAS_UA);
	//delay_us(wait_time);
	//delay_ms(10);
	//ACDRV123_ACM.MeasureVI(50, 5);
	ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		//oper_high_leak[site] = ACDRV123_ACM.GetMeasResult(site, MIRET)*1e6;//uA  498uA
		ACDRV1_24V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}

	//================ACDRV2 ABS Leakage, 29V
	cbite.SetOn(K23_SHARE2_ACDRV, K36_SHARE2_VAC, -1);
	delay_ms(3);
	ACDRV123_ACM.Set(FV, oper_24v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, oper_24v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	Retest_current_unstable_with_time_out(ACDRV123_ACM, oper_high_leak, spec.get_low_limit("ACDRV2_24V_Leak"), spec.get_high_limit("ACDRV2_24V_Leak"), 1, 100, MEAS_UA);
	//delay_us(wait_time);
	//delay_ms(10);
	//ACDRV123_ACM.MeasureVI(50, 5);
	ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		//oper_high_leak[site] = ACDRV123_ACM.GetMeasResult(site, MIRET)*1e6;//uA  498uA
		ACDRV2_24V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}

	//================ACDRV3 ABS Leakage, 29V
	cbite.SetOn(K22_SHARE1_ACDRV, K35_SHARE1_VAC, -1);
	delay_ms(3);
	ACDRV123_ACM.Set(FV,oper_24v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, oper_24v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	Retest_current_unstable_with_time_out(ACDRV123_ACM, oper_high_leak, spec.get_low_limit("ACDRV3_24V_Leak"), spec.get_high_limit("ACDRV3_24V_Leak"), 1, 100, MEAS_UA);
	//delay_us(wait_time);
	//delay_ms(10);
	//ACDRV123_ACM.MeasureVI(50, 5);
	ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		//oper_high_leak[site] = ACDRV123_ACM.GetMeasResult(site, MIRET)*1e6;//uA  498uA
		ACDRV3_24V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}
	ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);


	//==================VAC3  ABS Leakage, 26V
	VAC123_ACM.Set(FV, oper_20v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, oper_20v, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
	Retest_current_unstable_with_time_out(VAC123_ACM, oper_high_leak, spec.get_low_limit("VAC3_20V_Leak"), spec.get_high_limit("VAC3_20V_Leak"), 1, 5, MEAS_UA);
	//delay_us(wait_time);
	//VAC123_ACM.MeasureVI(50, 5);
	VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		//oper_high_leak[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e6;//uA    348uA
		VAC3_20V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}

	//==================VAC2  ABS Leakage, 26V
	cbite.SetOn(K36_SHARE2_VAC, -1);
	delay_ms(3);
	VAC123_ACM.Set(FV, oper_20v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, oper_20v, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
	Retest_current_unstable_with_time_out(VAC123_ACM, oper_high_leak, spec.get_low_limit("VAC2_20V_Leak"), spec.get_high_limit("VAC2_20V_Leak"), 1, 5, MEAS_MA);
	VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		//oper_high_leak[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e3;//uA  1.48mA
		VAC2_20V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}

	//==================VAC1 ABS Leakage, 26V
	cbite.SetOn(-1);
	delay_ms(3);
	VAC123_ACM.Set(FV, oper_20v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, oper_20v, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
	Retest_current_unstable_with_time_out(VAC123_ACM, oper_high_leak, spec.get_low_limit("VAC1_20V_Leak"), spec.get_high_limit("VAC1_20V_Leak"), 1, 5, MEAS_MA);
	//delay_us(wait_time);
	//VAC123_ACM.MeasureVI(50, 5);
	VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_1MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		//oper_high_leak[site] = VAC123_ACM.GetMeasResult(site, MIRET)*1e3;//mA  1.475mA
		VAC1_20V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);


	//==================KLV1  ABS Leakage, 26V
	cbite.SetOn(-1);
	delay_ms(3);
	KLV12_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(1);
	KLV12_ACM.Set(FV, oper_20v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	KLV12_ACM.Set(FV, oper_20v, ACM200_40V, ACM200_100UA, ACM200_RELAY_ON);
	delay_us(wait_time * 4);
	KLV12_ACM.MeasureVI(50, 5);
	KLV12_ACM.Set(FV, 0, ACM200_40V, ACM200_100UA, ACM200_RELAY_ON);
	KLV12_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		oper_high_leak[site] = KLV12_ACM.GetMeasResult(site, MIRET)*1e6;//    178uA
		KLV1_20V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}

	//==================KLV2 ABS Leakage, 26V
	cbite.SetOn(K20_SHARE_KLV, -1);
	delay_ms(3);
	KLV12_ACM.Set(FV, oper_20v, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	KLV12_ACM.Set(FV, oper_20v, ACM200_40V, ACM200_100UA, ACM200_RELAY_ON);
	delay_us(wait_time * 4);
	KLV12_ACM.MeasureVI(50, 5);
	KLV12_ACM.Set(FV, 0, ACM200_40V, ACM200_100UA, ACM200_RELAY_ON);
	KLV12_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		oper_high_leak[site] = KLV12_ACM.GetMeasResult(site, MIRET)*1e6;//uA   180uA
		KLV2_20V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}

	KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

	//==================VBUS ABS Leakage, 26V
	cbite.SetOn(-1);
	delay_ms(3);
	VBUS_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, oper_19v, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	VCC_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(wait_time);
	//VBUS_FOVI.MeasureVI(50, 5);
	Retest_current_unstable_with_time_out(VBUS_FOVI, oper_high_leak, spec.get_low_limit("VBUS_19V_Leak"), spec.get_high_limit("VBUS_19V_Leak"), 1, 5, MEAS_UA);
	VBUS_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		//oper_high_leak[site] = VBUS_FOVI.GetMeasResult(site, MIRET)*1e6;//uA   178uA
		VBUS_19V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}


	//==================PMID ABS Leakage, 26V
	PMID_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	PMID_FOVI.Set(FV, oper_19v, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	VCC_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(wait_time);
	//PMID_FOVI.MeasureVI(50, 5);
	Retest_current_unstable_with_time_out(PMID_FOVI, oper_high_leak, spec.get_low_limit("PMID_19V_Leak"), spec.get_high_limit("PMID_19V_Leak"), 1, 5, MEAS_UA);
	PMID_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		//oper_high_leak[site] = PMID_FOVI.GetMeasResult(site, MIRET)*1e6;//uA   180uA
		PMID_19V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	//==================SW ABS Leakage, 24V
	cbite.SetOn(K18_BST_SW_Cap, -1);
	delay_ms(3);
	//==================BTST ABS Leakage, 30V
	SW_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(1);
	VBUS_FOVI.Set(FV, 5, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	SW_ACM.Set(FV, 5, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	VBUS_FOVI.Set(FV, 10, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	SW_ACM.Set(FV, 10, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	VBUS_FOVI.Set(FV, 15, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	SW_ACM.Set(FV, 15, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	VBUS_FOVI.Set(FV, 20, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	BTST_ACM.Set(FV, 20, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	SW_ACM.Set(FV, 20, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	BTST_ACM.Set(FV, 25, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(200);
	delay_us(wait_time);
	BTST_ACM.MeasureVI(50, 5);
	BTST_ACM.Set(FV, 20, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	SW_ACM.Set(FV, 19, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 19, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(500);
	SW_ACM.MeasureVI(50, 5);
	SW_ACM.Set(FV, 15, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 15, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 15, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(100);
	SW_ACM.Set(FV, 10, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 10, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 10, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(100);
	SW_ACM.Set(FV, 5, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 5, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 5, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(100);
	SW_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(100);
	VBUS_FOVI.Set(FV, 0, FOVIe_40V, FOVIe_10MA, FOVIe_RELAY_OFF);
	SW_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_OFF);
	BTST_ACM.Set(FV, 0, ACM200_40V, ACM200_10MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		oper_high_leak[site] = SW_ACM.GetMeasResult(site, MIRET)*1e6;//uA
		SW_19V_Leak->SetTestResult(site, 0, oper_high_leak[site]);// -2uA
		oper_high_leak[site] = BTST_ACM.GetMeasResult(site, MIRET)*1e6;//uA
		BTST_25V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}

	//==================VBAT ABS Leakage, 5V
	cbite.SetOn(-1);
	delay_ms(3);
	VBUS_FOVI.Set(FV, 8, FOVIe_20V, FOVIe_10MA, FOVIe_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
	delay_ms(2);
	VBAT_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(2);
	VBAT_ACM.MeasureVI(100, 5);
	VBUS_FOVI.Set(FV, 8, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_20V, FOVIe_1MA, FOVIe_RELAY_OFF);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	FOR_EACH_VALID_SITE(site)
	{
		oper_high_leak[site] = VBAT_ACM.GetMeasResult(site, MIRET)*1e6;//uA   29.7uA
		VBAT_5V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}

	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);


	//==================VDRV ABS Leakage, 6V
	cbite.SetOn(-1);
	delay_ms(3);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(wait_time);
	VDRV_AMP_ACM.MeasureVI(50, 5);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		oper_high_leak[site] = VDRV_AMP_ACM.GetMeasResult(site, MIRET)*1e6;//uA
		VDRV_5V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

	//==================VCC ABS Leakage, 5V
	int unstable = 0;
	int unstablems[SITE_NUM] = { 0 };
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 8, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(2);
	VDRV_AMP_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(5);// delay 5ms cannot save
	Retest_current_unstable_with_time_out(VCC_ACM, oper_high_leak, spec.get_low_limit("VCC_5V_Leak"), spec.get_high_limit("VCC_5V_Leak"), 1, 150, MEAS_UA);

	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

	FOR_EACH_VALID_SITE(site)
	{
		//oper_high_leak[site] = VCC_ACM.GetMeasResult(site, MIRET)*1e6;//uA     94.8uA
		VCC_5V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);






	//==================AMUX , NTC, INT  ABS Leakage, 6V
	cbite.SetOn(K43_INT_ACM, -1);
	delay_ms(3);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	AMUX_FOVI.Set(FV, oper_5v, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, oper_5v, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	SDA_INT_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(wait_time);
	AMUX_FOVI.Set(FV, oper_5v, FOVIe_10V, FOVIe_100UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, oper_5v, FOVIe_10V, FOVIe_100UA, FOVIe_RELAY_ON);
	SDA_INT_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	delay_us(wait_time*10);
	AMUX_FOVI.MeasureVI(50, 5);
	NTC_FOVI.MeasureVI(50, 5);
	SDA_INT_ACM.MeasureVI(50, 5);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100UA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100UA, FOVIe_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);

	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		oper_high_leak[site] = AMUX_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
		AMUX_5V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
		oper_high_leak[site] = NTC_FOVI.GetMeasResult(site, MIRET)*1e6;//uA
		NTC_5V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
		oper_high_leak[site] = SDA_INT_ACM.GetMeasResult(site, MIRET)*1e6;//uA
		INT_5V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(1);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_100MA, FOVIe_RELAY_OFF);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);

	//==================NTC2, SCL, SDA ABS Leakage, 6V
	cbite.SetOn(K44_SDA_ACM, K55_SCL_ACM, -1);
	delay_ms(3);
	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);

	VBATD_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SCL_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(wait_time*1);
	VBATD_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	SCL_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, oper_5v, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	delay_us(wait_time*4);
	VBATD_ACM.MeasureVI(50, 5);
	SCL_ACM.MeasureVI(50, 5);
	SDA_INT_ACM.MeasureVI(50, 5);
	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100UA, ACM200_RELAY_ON);

	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		oper_high_leak[site] = VBATD_ACM.GetMeasResult(site, MIRET)*1e6;//uA
		NTC2_5V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
		oper_high_leak[site] = SCL_ACM.GetMeasResult(site, MIRET)*1e6;//uA
		SCL_5V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
		oper_high_leak[site] = SDA_INT_ACM.GetMeasResult(site, MIRET)*1e6;//uA
		SDA_5V_Leak->SetTestResult(site, 0, oper_high_leak[site]);
	}

	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);

	delay_ms(1);
	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);


    return 0;
}
 
DUT_API int OS_FINAL(short funcindex, LPCTSTR funclabel)
{
//{{AFX_STS_PARAM_PROTOTYPES
    CParam *VBUS_OS_Final = StsGetParam(funcindex, "VBUS_OS_Final");
    CParam *PMID_OS_Final = StsGetParam(funcindex, "PMID_OS_Final");
    CParam *AMUX_OS_Final = StsGetParam(funcindex, "AMUX_OS_Final");
    CParam *NTC_OS_Final = StsGetParam(funcindex, "NTC_OS_Final");
    CParam *KLV1_OS_Final = StsGetParam(funcindex, "KLV1_OS_Final");
    CParam *KLV2_OS_Final = StsGetParam(funcindex, "KLV2_OS_Final");
    CParam *ACDRV1_OS_Final = StsGetParam(funcindex, "ACDRV1_OS_Final");
    CParam *ACDRV2_OS_Final = StsGetParam(funcindex, "ACDRV2_OS_Final");
    CParam *ACDRV3_OS_Final = StsGetParam(funcindex, "ACDRV3_OS_Final");
    CParam *SW_OS_Final = StsGetParam(funcindex, "SW_OS_Final");
    CParam *VCC_OS_Final = StsGetParam(funcindex, "VCC_OS_Final");
    CParam *VDRV_OS_Final = StsGetParam(funcindex, "VDRV_OS_Final");
    CParam *VBAT_OS_Final = StsGetParam(funcindex, "VBAT_OS_Final");
    CParam *VAC1_OS_Final = StsGetParam(funcindex, "VAC1_OS_Final");
    CParam *VAC2_OS_Final = StsGetParam(funcindex, "VAC2_OS_Final");
    CParam *VAC3_OS_Final = StsGetParam(funcindex, "VAC3_OS_Final");
    CParam *PGND_OS_Final = StsGetParam(funcindex, "PGND_OS_Final");
    CParam *BTST_OS_Final = StsGetParam(funcindex, "BTST_OS_Final");
    CParam *VBATDET_OS_Final = StsGetParam(funcindex, "VBATDET_OS_Final");
    CParam *SCL_OS_Final = StsGetParam(funcindex, "SCL_OS_Final");
    CParam *SDA_OS_Final = StsGetParam(funcindex, "SDA_OS_Final");
    CParam *INT_OS_Final = StsGetParam(funcindex, "INT_OS_Final");
    CParam *VCC2VBUS_OS_Final = StsGetParam(funcindex, "VCC2VBUS_OS_Final");
    CParam *SW2BST_OS_Final = StsGetParam(funcindex, "SW2BST_OS_Final");
    CParam *SW2PMID_OS_Final = StsGetParam(funcindex, "SW2PMID_OS_Final");
//}}AFX_STS_PARAM_PROTOTYPES
    // TODO: Add your function code here

	dcm.Disconnect("SCL");
	dcm.Disconnect("SDA");
	dcm.Disconnect("INT");
	dcm.Disconnect("NTC");
	VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_ON);
	delay_ms(2);
	VBUS_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	PMID_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	AMUX_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	NTC_FOVI.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	KLV12_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	ACDRV123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VDRV_AMP_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VBAT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	PGND_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VAC123_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	VBATD_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	SCL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	SDA_INT_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FPVI.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_OFF);

	///===================Group1 Test By FOVI=============//
	cbite.SetOn(-1);
	delay_ms(3);
	FOVI_GRP.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(100);
	FOVI_GRP.Set(FI, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(100);
	FOVI_GRP.Set(FI, -0.001, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_ms(1);
	FOVI_GRP.MeasureVI(50, 5);
	FOVI_GRP.Set(FI, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(100);
	FOVI_GRP.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(100);
	FOVI_GRP.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_ON);
	FOVI_GRP.Set(FV, 0, FOVIe_10V, FOVIe_10MA, FOVIe_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		VBUS_OS_Final->SetTestResult(site, 0, VBUS_FOVI.GetMeasResult(site, MVRET));
		PMID_OS_Final->SetTestResult(site, 0, PMID_FOVI.GetMeasResult(site, MVRET));
		AMUX_OS_Final->SetTestResult(site, 0, AMUX_FOVI.GetMeasResult(site, MVRET));
		NTC_OS_Final->SetTestResult(site, 0, NTC_FOVI.GetMeasResult(site, MVRET));
	}
	///===================Group1 Test By ACM=============//
	cbite.SetOn(K55_SCL_ACM, K44_SDA_ACM, -1);
	delay_ms(3);
	ACM_GRP.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP.Set(FI, -0.001, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(1);
	ACM_GRP.MeasureVI(50, 5);
	ACM_GRP.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	ACM_GRP.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		KLV1_OS_Final->SetTestResult(site, 0, KLV12_ACM.GetMeasResult(site, MVRET));
		ACDRV1_OS_Final->SetTestResult(site, 0, ACDRV123_ACM.GetMeasResult(site, MVRET));
		SW_OS_Final->SetTestResult(site, 0, SW_ACM.GetMeasResult(site, MVRET));
		VCC_OS_Final->SetTestResult(site, 0, VCC_ACM.GetMeasResult(site, MVRET));
		VDRV_OS_Final->SetTestResult(site, 0, VDRV_AMP_ACM.GetMeasResult(site, MVRET));
		VBAT_OS_Final->SetTestResult(site, 0, VBAT_ACM.GetMeasResult(site, MVRET));
		VAC1_OS_Final->SetTestResult(site, 0, VAC123_ACM.GetMeasResult(site, MVRET));
		PGND_OS_Final->SetTestResult(site, 0, PGND_ACM.GetMeasResult(site, MVRET));
		BTST_OS_Final->SetTestResult(site, 0, BTST_ACM.GetMeasResult(site, MVRET));
		VBATDET_OS_Final->SetTestResult(site, 0, VBATD_ACM.GetMeasResult(site, MVRET));
		SCL_OS_Final->SetTestResult(site, 0, SCL_ACM.GetMeasResult(site, MVRET));
		SDA_OS_Final->SetTestResult(site, 0, SDA_INT_ACM.GetMeasResult(site, MVRET));
	}
	///===================Group2 Test By ACM=============//
	cbite.SetOn(K20_SHARE_KLV, K22_SHARE1_ACDRV, K35_SHARE1_VAC, K43_INT_ACM, -1);
	delay_ms(3);
	ACM_GRP2.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP2.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP2.Set(FI, -0.001, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(1);
	ACM_GRP2.MeasureVI(50, 5);
	ACM_GRP2.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP2.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP2.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	ACM_GRP2.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		KLV2_OS_Final->SetTestResult(site, 0, KLV12_ACM.GetMeasResult(site, MVRET));
		ACDRV3_OS_Final->SetTestResult(site, 0, ACDRV123_ACM.GetMeasResult(site, MVRET));
		VAC3_OS_Final->SetTestResult(site, 0, VAC123_ACM.GetMeasResult(site, MVRET));
		INT_OS_Final->SetTestResult(site, 0, SDA_INT_ACM.GetMeasResult(site, MVRET));
	}
	///===================Group3 Test By ACM=============//
	cbite.SetOn(K23_SHARE2_ACDRV, K36_SHARE2_VAC, -1);
	delay_ms(3);
	ACM_GRP3.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP3.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP3.Set(FI, -0.001, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(1);
	ACM_GRP3.MeasureVI(50, 5);
	ACM_GRP3.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP3.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	ACM_GRP3.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	ACM_GRP3.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		ACDRV2_OS_Final->SetTestResult(site, 0, ACDRV123_ACM.GetMeasResult(site, MVRET));
		VAC2_OS_Final->SetTestResult(site, 0, VAC123_ACM.GetMeasResult(site, MVRET));
	}

	//----------BST-SW Diode
	cbite.SetOn(K18_BST_SW_Cap, -1);
	delay_ms(3);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(500);
	BTST_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FI, -0.001, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(1);
	BTST_ACM.MeasureVI(50, 5);
	BTST_ACM.Set(FI, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	BTST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		SW2BST_OS_Final->SetTestResult(site, 0, BTST_ACM.GetMeasResult(site, MVRET));
	}

	//----------BST-SW Diode
	cbite.SetOn(K18_BST_SW_Cap, -1);
	delay_ms(3);
	PMID_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(500);
	PMID_FOVI.Set(FI, -0.001, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_ms(1);
	PMID_FOVI.MeasureVI(50, 5);
	PMID_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	PMID_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	SW_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	PMID_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		SW2PMID_OS_Final->SetTestResult(site, 0, PMID_FOVI.GetMeasResult(site, MVRET));
	}


	//----------VCC2VBUS
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_us(500);
	VBUS_FOVI.Set(FI, -0.001, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	delay_ms(1);
	VBUS_FOVI.MeasureVI(50, 5);
	VBUS_FOVI.Set(FI, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_ON);
	VBUS_FOVI.Set(FV, 0, FOVIe_2V, FOVIe_10MA, FOVIe_RELAY_OFF);
	VCC_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		VCC2VBUS_OS_Final->SetTestResult(site, 0, VBUS_FOVI.GetMeasResult(site, MVRET));
	}

    return 0;
}
