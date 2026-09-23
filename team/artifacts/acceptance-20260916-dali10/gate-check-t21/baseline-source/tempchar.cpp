/*============================================================================================================
*                                                                            Temperature AutoLoop Control Library                                                                                             *
*                                                                                                                                                                                                                                        *
*      This Temperaure autoloop library, which can realize one  time key kick to finish full condition (temperarure and vin point) loop operation.      *
*      It will auto measure the DUT temperature and compared with spec and acceptable variance, when temperaure hit set temp range , it will       *
*      start test automtically.                                                                                                                                                                                               *
*      This library support QT8100 Tester, MPI thermal stream and with commnucation solution of RS232                                                                     *
*      Before use this library, need to install NI 488.2/ NI MAX first                                                                                                                                    *
*      Easy to add in your program, only need to set loop condition before loop operation.                                                                                          *
*                                                                                                                                                                                                                                          *
*                                                                                    Developed by Zhang Shuai                                                                                                    *
*                                                         Nuvolta Technology (Shanghai )Test Team,  Version 1.0, 2021/7/28, SH                                                         *
*                              With no permission, copy or share is forbiden.    Nuvolta Technology Corperation. All Rights Reserved.                                   *
=============================================================================================================*/

#include"StdAfx.h"
#include "sub.h"
#include <stdio.h>
#include<conio.h>
//#include<ctype.h>;
//#include"bios.h";
#include <iostream>
#include"tempchar.h"
#include <sstream>
#include <iomanip>
#include<fstream>
#include<vector>
extern "C" int GetPgsFullPath(LPTSTR pgsPath, int chNum);

int extractNumberAfterEquals(const std::string& str) {
	// 查找"="的位置
	size_t pos = str.find('=');

	// 如果没找到"="或者"="是最后一个字符，则返回0或抛出异常
	if (pos == std::string::npos || pos == str.length() - 1) {
		std::cerr << "No number found after '=' or '=' is the last character." << std::endl;
		return 0; // 或者你可以选择抛出异常
	}

	// 提取"="后面的子字符串
	std::string numberStr = str.substr(pos + 1);

	// 尝试将子字符串转换为整数
	int number;
	std::istringstream iss(numberStr);
	if (!(iss >> number)) {
		std::cerr << "The substring after '=' is not a valid integer." << std::endl;
		return 0; // 或者你可以选择抛出异常
	}

	// 返回转换后的整数
	return number;
}


// 子函数：将字符串按照'*'分割成两个子字符串
void splitString(const std::string& string1, std::string& string2, std::string& string3) {
	std::istringstream iss(string1);
	std::getline(iss, string2, ','); // 读取*之前的部分到string2

	// 检查是否还有剩余的部分（即检查*之后是否有内容）
	if (iss.good() && !iss.eof()) {
		std::getline(iss, string3); // 如果有，读取*之后的部分到string3
	}
	else {
		// 如果没有剩余部分，清空string3
		string3.clear();
	}
}






int check_valid(int *array_in, int size_max, int input_val)
{
	int valid_flag = 1;
	for (int i = 0; i < size_max; i++)
	{
		if (abs(array_in[i] - input_val) < 0.01)
		{
			i = size_max;
			valid_flag = 0;
		}
	}
	return valid_flag;
}

int check_valid(double *array_in, int size_max, double input_val)
{
	int valid_flag = 1;
	for (int i = 0; i < size_max; i++)
	{
		if (abs(array_in[i] - input_val) < 0.01)
		{
			i = size_max;
			valid_flag = 0;
		}
	}
	return valid_flag;
}



string convertToString(double value, int precision)
{
	std::ostringstream streamObj;
	streamObj << std::fixed << std::setprecision(precision) << value;
	return streamObj.str();
}

/*-----------------------------------------temp_control 函数功能介绍-----------------------------------------------------------------------------------------------------------------------------
1. temp_lp, vin_lp 均接受全局变量的值
2. 第一次loop的时候需要判定是否需要开启Temp Char测试,如果需要的选择Yes
3.第一此Loop的时候需要做一些设置,判断有多少个电压点 v_cnt , 多少个温度点 t_cnt
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/

double temp_meas( int set_tmp_val, int soak_time_left, bool soak_stable_flag, int set_loop_flag, bool fbd_stable_tmcnt_flag)
{
	DOUBLE temp_meas_val = 0;
	ULONG data_read[SITE_NUM] = { 0 };
	double adc_read_TDIE[SITE_NUM] = { 0 };

	cbite.SetOn(-1);
	delay_ms(3);
	KLV12_PGNDWL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	KLV12_PGNDWL_ACM.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	KLV12_PGNDWL_ACM.Set(FI, -0.001, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_ms(3);
	KLV12_PGNDWL_ACM.MeasureVI(50, 5);
	KLV12_PGNDWL_ACM.Set(FI, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	KLV12_PGNDWL_ACM.Set(FV, 0, ACM200_3p6V, ACM200_10MA, ACM200_RELAY_ON);
	delay_us(100);
	KLV12_PGNDWL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
	KLV12_PGNDWL_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
	FOR_EACH_VALID_SITE(site)
	{
		adc_read_TDIE[site] = KLV12_PGNDWL_ACM.GetMeasResult(site, MVRET) * 528.3446 + 383.4087;
	}

	temp_meas_val = adc_read_TDIE[0];

	if (abs(temp_meas_val) < 0.0001)
	{
		temp_meas_val = Temperature1;
	}
	if (abs(temp_meas_val) < 0.0001)
	{
		temp_meas_val = Temperature1;
	}

	int ch = 0;

	if (_kbhit()){//如果有按键按下，则_kbhit()函数返回真
		ch = _getch();//使用_getch()函数获取按下的键值
		if (ch == 101)
		{
			printf_s("  \n");
			printf_s("  You Pressed <<E>> Button to Stop Temp Loop !!!\n");
			printf_s("  \n");
		}
		else
		{
			printf_s("  \n");
			printf_s("  You Pressed  Button which cannot be recognized !!!\n");
			printf_s("  \n");
		}
	}

	if (ch == 101)// CAUTIONS!! IF USER PRESS "E" BUTTON ON KEYBOARD, WILL STOP TEMP CONTROL
	{
		TS.set_abnormal_flag(true);// Here will stop control
	}

	if (set_loop_flag == 1)
	{
		printf_s("  Soak 15s at %dC, Current temp=%.2f, set_temp=%d, target temp is %d\n", temp_meas_val, temp_meas_val, set_tmp_val, temp_meas_val);
	}
	else if (set_loop_flag == 2)
	{
		if (soak_stable_flag == true && fbd_stable_tmcnt_flag == false)
		{
			SetColorTC(10);
			printf_s("  Soak 20s at estimate temp %dC , Current temp= %.2f,  target= %d, soaking stable need %dS to go...\n", set_tmp_val, temp_meas_val, temp_meas_val, soak_time_left);
			ResetColorTC();
		}
		else
		{
			printf_s("  Soak 20s at estimate temp %dC, Current temp= %.2f,   target temp is %d\n", set_tmp_val, temp_meas_val, temp_meas_val);
		}
	}
	else if (set_loop_flag == 3)
	{
		if (soak_stable_flag == true && fbd_stable_tmcnt_flag == false)
		{
			SetColorTC(10);
			printf_s("  Current temp= %.2f, soak_temp= %d, target= %d, soaking stable need %dS to go...\n", temp_meas_val, set_tmp_val, temp_meas_val, soak_time_left);
			ResetColorTC();
		}
		else
		{
			printf_s("  Current temp= %.2f, set_temp= %d, target temp is %d, Vin target = %.2f\n", temp_meas_val, set_tmp_val, TS.get_temp(), TS.get_vin());
		}
	}
	else
	{
		if (soak_stable_flag == true && fbd_stable_tmcnt_flag == false)
		{
			SetColorTC(10);
			printf_s("  Current temp= %.2f, soak_temp= %d, target= %d, soaking stable need %dS to go...\n", temp_meas_val, set_tmp_val, TS.get_temp(), soak_time_left);
			ResetColorTC();
		}
		else
		{
			printf_s("  Current temp= %.2f, set_temp= %d, target temp is %d, Vin target = %.2f\n", temp_meas_val, set_tmp_val, TS.get_temp(), TS.get_vin());
		}
	}

	return temp_meas_val;
}

void Thermal_stream::modifyLDF(const std::string& filePath, int newStopAfterRunValue) {
	// 打开文件进行读取
	std::ifstream inputFile(filePath, std::ios::in);
	if (!inputFile.is_open()) {
		std::cerr << "Error opening file for reading: " << filePath << std::endl;
		return;
	}

	// 读取整个文件内容到字符串向量中
	std::vector<std::string> fileLines;
	std::string line;
	while (std::getline(inputFile, line)) {
		fileLines.push_back(line);
	}
	inputFile.close();

	// 修改文件内容
	for (auto& l : fileLines)
	{
		// 检查并修改StopContinuePass=0
		if (l.find("StopContinuePass=0") != std::string::npos)
		{
			l.replace(l.find("0"), 1, "1");
		}
		// 检查并修改ContinuePass=100
		if (l.find("ContinuePass=") != std::string::npos)
		{
			size_t equalPos = l.find("=");
			if (equalPos != std::string::npos)
			{
				// 将StopAfterRun后的数字替换为新值
				std::stringstream ss;
				ss << 100;
				l.replace(equalPos + 1, std::string::npos, ss.str());
			}
		}


		// 检查并修改StopAfterRun=后的数字
		if (l.find("StopAfterRun=") != std::string::npos) 
		{
			size_t equalPos = l.find("=");
			if (equalPos != std::string::npos)
			{
				// 将StopAfterRun后的数字替换为新值
				std::stringstream ss;
				ss << newStopAfterRunValue;
				l.replace(equalPos + 1, std::string::npos, ss.str());
			}
		}
	}

	// 打开文件进行写入（会清空文件内容）
	std::ofstream outputFile(filePath, std::ios::out | std::ios::trunc);
	if (!outputFile.is_open()) {
		std::cerr << "Error opening file for writing: " << filePath << std::endl;
		return;
	}

	// 将修改后的内容写回文件
	for (const auto& l : fileLines) {
		outputFile << l << std::endl;
	}
	outputFile.close();
}

void Thermal_stream::loop_cond_count()
{

	int TempsetCount = spec("TEMP_CHAR").count();
	int PSsetCount = spec("PS1_CHAR").count();


	CInputData*Temp_pInput_array[20];
	double ValueGet;

	string PSName1 = "PS1";
	string PSName2 = "PS2";
	string PSName3 = "PS3";
	string PSSel;
	string TempSel;
	string Selection_All = "Select_All";
	const char* tempsel;
	const char* pssel;
	const char* select_all;
	bool  SELALL = false;

	char  str[20] = { "Try" };
	CInputDlg* pDlg = STSGetDialog("Temp char loop  option Select Window", "Click to Select");
	if (pDlg != NULL)
	{
		for (int i = 0; i < TempsetCount + PSsetCount + 2; i++)
		{


			if (i == 0)
			{
				CInputData*pInputA = pDlg->InsertItem("Temp2", str, 10, CInputData::CONTROL_STATIC_TEXT, true);
				if (pInputA != NULL)
				{
					char pmessage[256] = { 0 };
					sprintf_s(pmessage, "请选择要测的温度点");
					pInputA->SetData(pmessage, 256);
				}
			}
			if (i == TempsetCount)
			{
				CInputData*pInputB = pDlg->InsertItem("Temp2", str, 10, CInputData::CONTROL_STATIC_TEXT, true);
				if (pInputB != NULL)
				{
					char vmessage[256] = { 0 };
					sprintf_s(vmessage, "请选择要测试的电压点");
					pInputB->SetData(vmessage, 256);
				}
			}

			if (i == TempsetCount + PSsetCount)
			{
				//CInputData*pInputC = pDlg->InsertItem("Temp2", str, 10, CInputData::CONTROL_STATIC_TEXT, true);
				//if (pInputC != NULL)
				//{
				//	char vmessage[256] = { 0 };
				//	sprintf_s(vmessage, "选择所有选项勾选下面");
				//	pInputC->SetData(vmessage, 256);
				//}

				select_all = Selection_All.c_str();
				Temp_pInput_array[TempsetCount + PSsetCount] = pDlg->InsertItem(select_all, str, 10, CInputData::CONTROL_CHECK, true);
				if (Temp_pInput_array[i] != NULL)
				{
					Temp_pInput_array[i]->SetCheck(FALSE);
				}
			}

			if (i == TempsetCount + PSsetCount + 1)
			{
				//CInputData*pInputC = pDlg->InsertItem("Temp2", str, 10, CInputData::CONTROL_STATIC_TEXT, true);
				//if (pInputC != NULL)
				//{
				//	char vmessage[256] = { 0 };
				//	sprintf_s(vmessage, "选择学习模式");
				//	pInputC->SetData(vmessage, 256);
				//}

				const char *study_select = "选择学习模式";
				Temp_pInput_array[TempsetCount + PSsetCount + 1] = pDlg->InsertItem(study_select, str, 10, CInputData::CONTROL_CHECK, true);
				if (Temp_pInput_array[i] != NULL)
				{
					Temp_pInput_array[i]->SetCheck(FALSE);
				}
			}



			if (i < TempsetCount)
			{
				ValueGet = spec("TEMP_CHAR")[i];
				TempSel = "TempSet=" + convertToString(ValueGet, 1) + "C";
				tempsel = TempSel.c_str();
				Temp_pInput_array[i] = pDlg->InsertItem(tempsel, str, 10, CInputData::CONTROL_CHECK, true);
				if (Temp_pInput_array[i] != NULL)
				{
					Temp_pInput_array[i]->SetCheck(FALSE);
				}
			}
			else if (i <TempsetCount + PSsetCount)
			{
				ValueGet = spec("PS1_CHAR")[i - TempsetCount];
				PSName1 = "PS1=" + convertToString(ValueGet, 1) + "V, ";
				ValueGet = spec("PS2_CHAR")[i - TempsetCount];
				PSName2 = "PS2=" + convertToString(ValueGet, 1) + "V, ";
				ValueGet = spec("PS3_CHAR")[i - TempsetCount];
				PSName3 = "PS3=" + convertToString(ValueGet, 1) + "V";
				PSSel = PSName1 + PSName2 + PSName3;
				PSName1 = "";
				PSName2 = "";
				PSName3 = "";
				pssel = PSSel.c_str();
				Temp_pInput_array[i] = pDlg->InsertItem(pssel, str, 10, CInputData::CONTROL_CHECK, true);
				if (Temp_pInput_array[i] != NULL)
				{
					Temp_pInput_array[i]->SetCheck(FALSE);
				}
			}
		}

		pDlg->ShowDlg();
		delay_ms(1);
		if (Temp_pInput_array[TempsetCount + PSsetCount + 1]->isCheck())// if select all option
		{
			study_mode = true;
		}
		if (Temp_pInput_array[TempsetCount + PSsetCount]->isCheck())// if select all option
		{
			SELALL = true;
		}

		for (int i = 0; i <TempsetCount + PSsetCount; i++)
		{
			if (i < TempsetCount) // ---------transfer temp loop option and temp loop count
			{
				if (SELALL == true)
				{
					Tsel_target[sel_tcnt] = (int)spec("TEMP_CHAR")[i];
					sel_tcnt++;
				}
				else
				{
					if (Temp_pInput_array[i]->isCheck())
					{
						Tsel_target[sel_tcnt] = (int)spec("TEMP_CHAR")[i];
						sel_tcnt++;
					}
				}
			}
			else if (i < TempsetCount + PSsetCount)//-------transfer power supply loop option and power supply loop count
			{
				if (SELALL == true)
				{
					Vsel1_target[sel_vcnt] = spec("PS1_CHAR")[i - TempsetCount];
					Vsel2_target[sel_vcnt] = spec("PS2_CHAR")[i - TempsetCount];
					Vsel3_target[sel_vcnt] = spec("PS3_CHAR")[i - TempsetCount];
					sel_vcnt++;
				}
				else
				{
					if (Temp_pInput_array[i]->isCheck())
					{
						Vsel1_target[sel_vcnt] = spec("PS1_CHAR")[i - TempsetCount];
						Vsel2_target[sel_vcnt] = spec("PS2_CHAR")[i - TempsetCount];
						Vsel3_target[sel_vcnt] = spec("PS3_CHAR")[i - TempsetCount];
						sel_vcnt++;
					}
				}
			}
		}
		delay_ms(1);
	}






	sel_cnt_all = sel_tcnt*sel_vcnt;

	while (sel_cnt_all<1)
	{
		StsMessageBox("Need select at least 1 Temp and 1 Power Option!!             (请至少选择一个电压和温度点) ，    Click OK to Continue!", "ERROR--没有选择任何温度和电压点!!  ");
		pDlg->ShowDlg();
		delay_ms(1);
		sel_tcnt = 0;
		sel_vcnt = 0;
		if (Temp_pInput_array[TempsetCount + PSsetCount]->isCheck())// if select all option
		{
			SELALL = true;
		}

		for (int i = 0; i < TempsetCount + PSsetCount; i++)
		{
			if (i < TempsetCount) // ---------transfer temp loop option and temp loop count
			{
				if (SELALL == true)
				{
					Tsel_target[sel_tcnt] = (int)spec("TEMP_SET")[i];
					sel_tcnt++;
				}
				else
				{
					if (Temp_pInput_array[i]->isCheck())
					{
						Tsel_target[sel_tcnt] = (int)spec("TEMP_SET")[i];
						sel_tcnt++;
					}
				}
			}
			else if (i < TempsetCount + PSsetCount)//-------transfer power supply loop option and power supply loop count
			{
				if (SELALL == true)
				{
					Vsel1_target[sel_vcnt] = spec("PS1_SET")[i - TempsetCount];
					Vsel2_target[sel_vcnt] = spec("PS2_SET")[i - TempsetCount];
					Vsel3_target[sel_vcnt] = spec("PS3_SET")[i - TempsetCount];
					sel_vcnt++;
				}
				else
				{
					if (Temp_pInput_array[i]->isCheck())
					{
						Vsel1_target[sel_vcnt] = spec("PS1_SET")[i - TempsetCount];
						Vsel2_target[sel_vcnt] = spec("PS2_SET")[i - TempsetCount];
						Vsel3_target[sel_vcnt] = spec("PS3_SET")[i - TempsetCount];
						sel_vcnt++;
					}
				}
			}
		}
		delay_ms(1);
		sel_cnt_all = sel_tcnt*sel_vcnt;
	}

	//************************************Tempchar Setup Function自动设置AutoTest的次数**********************//
	char PGSfullpath[300];
	GetPgsFullPath(PGSfullpath, 300);
	string filePGSpath(PGSfullpath);
	std::string newSuffix = ".LDF";
	size_t dotPos = filePGSpath.find_last_of('.');
	if (dotPos != std::string::npos)// 检查是否找到了点
	{
		filePGSpath.replace(dotPos, filePGSpath.size() - dotPos, newSuffix);	// 替换后缀
	}
	else 	// 如果没有点，则直接添加后缀（但这种情况对于你的例子来说不会发生）
	{
		filePGSpath += newSuffix;
	}
	string fileLDFName = filePGSpath;
	modifyLDF(fileLDFName, sel_cnt_all);	// 调用函数修改LDF文件
	//************************************Tempchar Setup Function**********************//


















	for (int i = 0; i<sel_cnt_all; i++)// 每个loop条件下的复测次数的初始值均为0
	{
		Retest_count[i] = 0;
	}

	for (int itr = 0; itr<sel_tcnt; itr++)//建立一个温度目标值和最大设定值的map
	{
		temp_set_max_map[Tsel_target[itr]] = 0;
	}
	for (int itr = 0; itr<sel_tcnt; itr++)//建立一个温度目标值和最大设定值的map
	{
		temp_set_min_map[Tsel_target[itr]] = Tsel_target[itr];
	}

	string reminder_lp_cnt = convertToString((double)sel_cnt_all, 0);
	string reminder_str = "Set Auto Test mode After  Click  Option  button to set <Stop after  Auto Test> =  " + reminder_lp_cnt;
	const char* reminder_show = reminder_str.c_str();
	StsMessageBox(reminder_show, "Reminder for loop setup ");


	//=============将Setup的值返还给tempchar 做设置
	char pgsfullpath[300];
	GetPgsFullPath(pgsfullpath, 300);
	string filepath(pgsfullpath);
	int pos = filepath.find_last_of('\\');
	string tempcharfile = filepath.substr(0, pos);
	tempcharfile = tempcharfile + "\\tempchar_setup.tc";
	std::ifstream infile(tempcharfile);
	// 检查文件是否成功打开
	if (!infile.is_open()) {
		if (MessageBoxA(NULL, "无法打开文件以读取数据!检查是否tempchar_setup.txt不存在或者路径不对.....\n是否继续使用默认值，选择-是(Y)\n如果选择参数收集学习模式，选择-否(N)", "诊断提示对话框", MB_YESNO) == IDNO)
		{
			PostQuitMessage(0);
			Thermal_Normal = false;
		}	
		else
		{
			temp_set_max_map[125] = 140;
			temp_set_max_map[100] = 115;
			temp_set_max_map[85] = 100;
			temp_set_max_map[70] = 80;
			temp_set_max_map[25] = 35;
			temp_set_max_map[0] = -15;
			temp_set_max_map[-20] = -35;
			temp_set_max_map[-40] = -60;
		}
	}
	else
	{
		Thermal_Normal = true;


	std::string line;
	string pre_str, post_str;
	string value_target, value_set;
	int map_target, map_setval;
	while (std::getline(infile, line))
	{
			//===========获取其他值， soaktime值
			if (line.find("Tsoak_stable_time=") != std::string::npos)
			{
				pos = line.find('=');
				post_str = line.substr(pos + 1, line.length());
				Tsoak_stable_time = getnumberfromstring(&post_str);
			}
			else if (line.find("Vsoak_stable_time=") != std::string::npos)
			{
				pos = line.find('=');
				post_str = line.substr(pos + 1, line.length());
				Vsoak_stable_time = getnumberfromstring(&post_str);
			}
			else
			{
				size_t commaPos = line.find(',');
				if (commaPos != std::string::npos)
				{
					pre_str = line.substr(0, commaPos);
					post_str = line.substr(commaPos + 1, line.length());
				}
				size_t pos = pre_str.find('=');

				//==============获取Target的值
				std::string numberStr = pre_str.substr(pos + 1);
				map_target = getnumberfromstring(&numberStr);

				//==============获取每个Target下对应的值
				pos = post_str.find(':');
				numberStr = post_str.substr(pos + 1);
				map_setval = getnumberfromstring(&numberStr);

				temp_set_max_map[map_target] = map_setval;

			}
		}
	}
	infile.close();


}

void Thermal_stream::tssot(int sotvalue)
{
	if (Manual_mode == false)
	{
		if (init_ts_config_cnt == 0)
		{
			if (CHAR_LOOP == false)
			{
				CHAR_LOOP = true;
			}
			init_ts_config_cnt = init_ts_config_cnt + 1;
			loop_cond_count();
			//sel_cnt_all = sel_tcnt*sel_vcnt;
			if (Thermal_Normal == true)
			{
				//====================Check communication status
				int setup_flag = 0;
				setup_flag = Thermal_Setup();
				if (setup_flag == 3)
				{
					printf_s("\n");
					printf_s("\n");
					printf_s("Congratulations!! Thermal Steam communication check success!!  Ready for temperature loop..\n");
					printf_s("\n");
					control_bit = false;
				}
				else
				{
					control_bit = true;
					printf_s("Sorry, Thermal Stream communication Failed!\n");
					printf_s("You need check Serial Port line have insert in COM1 or not?\n");
					printf_s("You can also restart the thermal stream to recover communication\n ");
				}
				//=====================================================
			}

		}
	}

}

//-------------------------normal test setup and temp control---//
void Thermal_stream::tsinitbeforetest()
{


	if (Manual_mode == false)
	{
		if (CHAR_LOOP == true && abnormal_stop == false)
		{
			if (study_mode)
			{
				temp_loop_control_study_mode();
			}
			else
			{
				temp_loop_control();
			}
		}
		else
		{
			TempLoopCount = sel_cnt_all + 1;
			stop_loop_flag = true;
		}
		if (abnormal_stop == true || control_bit == true)
		{
			STSStopProgram();
		}
	}

}

//----------------End of Test function when pass
void Thermal_stream::tseot()
{

	if (Manual_mode == false)
	{
		if (control_bit == true)
		{
			CHAR_LOOP = false;
		}
		if (CHAR_LOOP == true)
		{
			//--TEST_OUTPUT.Printf ("TempLoopCount = %d\n", TempLoopCount);
			TempLoopCount++;

			if (TempLoopCount >= sel_cnt_all + 1)
			{
				STSCBSetContinuePassStopSetting(1, 1);
				STSCBSetContinueFailStopSetting(1, 1);

				if (Tsel_target[temp_seq] > 40)
				{
					Tsoak_stable_time = 30;
					for (int i = 0; i < Tsoak_stable_time; i++)
					{
						set_temp(-40, 1, true);
					}

				}
				else if (Tsel_target[temp_seq] > 10 && Tsel_target[temp_seq] < 40)
				{
					Tsoak_stable_time = 10;
					for (int i = 0; i < Tsoak_stable_time; i++)
					{
						set_temp(25, 1, true);
					}
				}
				else
				{
					Tsoak_stable_time = 30;
					for (int i = 0; i <18; i++)
					{
						set_temp(125, 1, true);
					}
				}

				for (int i = 0; i < 20; i++)
				{
					set_temp(25, 1, true);
				}

				Thermal_End();
				TempLoopCount = 1;
				CHAR_LOOP = false;
				//--TEST_OUTPUT.Printf("Execute TSEOF function");
				fclose(stdout);
				FreeConsole();
				//LogarithmTest();
				if (stop_loop_flag == true)
				{
					//--AbortApp("User have stop the loop sequence, need reload to start! ");
				}
			}
		}
	}



}












//-------------End of Test function when fail
void Thermal_stream::tsfot()
{
	if (Manual_mode == false)
	{
		//char* options[2] = { "YES", "NO" };
		//int fail_flag = 1;
		//--int fail_flag =TEST_OUTPUT.PopupSelectDialog("Test failed, would you want to retest ?", options, ARRAY_LEN(options), "Note: Select Retest or not");

		for (std::map<int, int>::iterator itr = Retest_count.begin(); itr != Retest_count.end(); ++itr)// 每个条件下只要复测次数达到设定的数字，这个条件就停止复测
		{
			if (itr->first == TempLoopCount)
			{
				itr->second++;
			}
			if (itr->second>1)
			{
				TempLoopCount++; //不再复测
			}
			else
			{
				TempLoopCount = TempLoopCount; //复测

			}
		}

		//if (MessageBoxA(NULL, "出现测试Fail，请确认: 如果继续，选择-是否复测(Y)\n    如果不复测，选择-否(N)", "失效处理提示对话框", MB_YESNO) == IDNO) // Yes, retest
		//{
		//	TempLoopCount++; //点击复测
		//}
		//else // no, do not retest
		//{
		//	TempLoopCount = TempLoopCount;
		//}
	}

}



int Thermal_stream::get_temp()
{
	return Tsel_target[temp_seq];
}


double Thermal_stream::get_vin()
{
	return Vsel1_target[vin_seq];
}

int Thermal_stream::get_vin_seq()
{
	return vin_seq;
}

int Thermal_stream::get_temp_seq()
{
	return temp_seq;
}

int Thermal_stream::get_temp_meas_cnt()
{
	return temp_meas_count;
}

void Thermal_stream::temp_meas_cnt_accum()
{
	temp_meas_count++;
}

double Thermal_stream::get_temp_variance()
{
	return temp_variance;
}

void Thermal_stream::set_abnormal_flag(bool value)
{
	abnormal_stop = value;
}
///*----------------------------------------------Temp_measure 函数功能介绍------------------------------------------------------------------------------







/*
*------------------------------------------------------------------------- Print serial port configuration.----------------------------------------
*/
void Thermal_stream::PrintCommState(DCB dcb)
{
	//  Print some of the DCB structure values
	//--TEST_OUTPUT.Printf( TEXT("\nBaudRate = %d, ByteSize = %d, Parity = %d, StopBits = %d\n"), 
	//--dcb.BaudRate, 
	//--dcb.ByteSize, 
	//--dcb.Parity,
	//--dcb.StopBits );
}

//*
//* Print response data string.
//*/
void Thermal_stream::PrintMessage(char *lpBuf, DWORD dwSize)
{
	char pcMsg[100];
	int i = 0;

	// Copy buffer data to new buffer, avoid error.
	for (i = 0; i < (int)dwSize; i++)
	{
		pcMsg[i] = lpBuf[i];
	}

	// Put string end character.
	pcMsg[dwSize] = '\0';
	printf_s(TEXT("Receive Message count:%d, string:%s.\n"), dwSize, pcMsg);
}

//*
//* Write command out to serial port.
//*/
BOOL Thermal_stream::WriteABuffer(char * lpBuf, DWORD dwToWrite, HANDLE hComm)
{
	OVERLAPPED osWrite = { 0 };
	DWORD dwWritten;
	BOOL fRes;

	// Create this writes OVERLAPPED structure hEvent.
	osWrite.hEvent = CreateEvent(NULL, TRUE, FALSE, NULL);
	if (osWrite.hEvent == NULL)
		// Error creating overlapped event handle.
		return FALSE;

	// Issue write.
	if (!WriteFile(hComm, lpBuf, dwToWrite, &dwWritten, &osWrite)) {
		if (GetLastError() != ERROR_IO_PENDING) {
			// WriteFile failed, but it isn't delayed. Report error and abort.
			fRes = FALSE;
		}
		else {
			// Write is pending.
			if (!GetOverlappedResult(hComm, &osWrite, &dwWritten, TRUE))
				fRes = FALSE;
			else
				// Write operation completed successfully.
				fRes = TRUE;
		}
	}
	else
		// WriteFile completed immediately.
		fRes = TRUE;

	CloseHandle(osWrite.hEvent);
	return fRes;
}

//*
//* Read response data from serial port.
//*/
DWORD Thermal_stream::Read(char * lpBuf, HANDLE hComm)
{
	DWORD dwRead = 100;
	BOOL fWaitingOnRead = FALSE;
	OVERLAPPED osReader = { 0 };
	DWORD dwRes;
	DWORD dwErr;

	// Create the overlapped event. Must be closed before exiting
	// to avoid a handle leak.
	osReader.hEvent = CreateEvent(NULL, TRUE, FALSE, NULL);

	if (osReader.hEvent == NULL)
	{
		// Error creating overlapped event; abort.
	}

	if (!fWaitingOnRead)
	{
		// Issue read operation.
		BOOL flag_test;
		flag_test = ReadFile(hComm, lpBuf, READ_BUF_SIZE, &dwRead, &osReader);

		if (!ReadFile(hComm, lpBuf, READ_BUF_SIZE, &dwRead, &osReader))
		{
			dwErr = GetLastError();
			if (dwErr != ERROR_IO_PENDING)
				// Error in communications; report it.
			{
				//--TEST_OUTPUT.Printf(TEXT("Read Error:%d.\n"), dwErr );
				dwRead = -1;
			}
			else
			{
				fWaitingOnRead = TRUE;
				dwRead = -2;
			}
		}
		else
		{
			// Read completed immediately.  
		}
	}

	if (fWaitingOnRead) {
		dwRes = WaitForSingleObject(osReader.hEvent, READ_TIMEOUT);
		switch (dwRes)
		{
			// Read completed.
		case WAIT_OBJECT_0:
			if (!GetOverlappedResult(hComm, &osReader, &dwRead, FALSE))
			{
				// Error in communications; report it.
				dwRead = -1;
			}
			else
			{
				// Read completed successfully.				  			 
			}
			//  Reset flag so that another opertion can be issued.
			fWaitingOnRead = FALSE;
			break;

		case WAIT_TIMEOUT:
			// Operation isn't complete yet. fWaitingOnRead flag isn't
			// changed since I'll loop back around, and I don't want
			// to issue another read until the first one finishes.
			//
			// This is a good time to do some background work.
			break;

		default:
			// Error in the WaitForSingleObject; abort.
			// This indicates a problem with the OVERLAPPED structure's
			// event handle.
			break;
		}
	}

	return dwRead;
}

//*
//* Basic function to send command out and includes read response data back.
//*/
BOOL Thermal_stream::SendCommand(HANDLE hCom, char * pcCmd, DWORD dwBytesToSend, BOOL bQueryCmd)
{
	BOOL bResult;
	char pcMsg[READ_BUF_SIZE];
	DWORD dwMsgCnt;
	DWORD Fix_val = 56;
	bResult = WriteABuffer(pcCmd, dwBytesToSend, hCom);

	// Read response data.
	if (bQueryCmd)
	{
		// Wait for response data is ready.
		Sleep(1000);

		dwMsgCnt = Read(&pcMsg[0], hCom);
		PrintMessage(&pcMsg[0], dwMsgCnt);

		if (Fix_val == dwMsgCnt)
		{

		}
	}

	// Wait for command complete.
	Sleep(1000);

	return bResult;
}


BOOL Thermal_stream::SendCommand1(HANDLE hCom, char * pcCmd, DWORD dwBytesToSend, BOOL bQueryCmd, int *flag)
{
	BOOL bResult;
	char pcMsg[READ_BUF_SIZE];
	DWORD dwMsgCnt;
	char * cmmd = TEXT("*IDN?\n");
	bResult = WriteABuffer(pcCmd, dwBytesToSend, hCom);

	// Read response data.
	char a1 = 'F';
	char a2 = 'F';
	char a3 = 'F';
	if (bQueryCmd)
	{
		// Wait for response data is ready.
		Sleep(1000);

		dwMsgCnt = Read(&pcMsg[0], hCom);

		PrintMessage(&pcMsg[0], dwMsgCnt);
		a1 = pcMsg[0];
		a2 = pcMsg[1];
		a3 = pcMsg[2];
	}

	if (a1 == 'M' && a2 == 'P' && a3 == 'I')// communication is good
	{
		*flag = 10;
	}
	else
	{
		*flag = 1010;
	}
	// Wait for command complete.
	Sleep(1000);

	return bResult;
}


int Thermal_stream::Thermal_Setup()
{

	int flag = 1;
	int communication_success_falg = 0;
	printf_s("Execute Thermal_Setup()!");

	if (hCom == INVALID_HANDLE_VALUE)
	{
		//  Handle the error.
		printf_s("CreateFile failed with error %d.\n", GetLastError());
		return (1);
	}

	//  Setup and Verify Serial Port Configuration.
	//  Initialize the DCB structure.
	SecureZeroMemory(&dcb, sizeof(DCB));
	dcb.DCBlength = sizeof(DCB);

	//  Build on the current configuration by first retrieving all current
	//  settings.
	fSuccess = GetCommState(hCom, &dcb);

	if (!fSuccess)
	{
		//  Handle the error.
		printf_s("GetCommState failed with error %d.\n", GetLastError());
		return (2);
	}

	PrintCommState(dcb);       //  Output to console

	//  Fill in some DCB values and set the com state: 
	//  57,600 bps, 8 data bits, no parity, and 1 stop bit.
	dcb.BaudRate = CBR_115200;     //  baud rate
	dcb.ByteSize = 8;             //  data size, xmit and rcv
	dcb.Parity = NOPARITY;      //  parity bit
	dcb.StopBits = ONESTOPBIT;    //  stop bit

	fSuccess = SetCommState(hCom, &dcb);

	if (!fSuccess)
	{
		//  Handle the error.
		printf_s("SetCommState failed with error %d.\n", GetLastError());
		return (3);
	}

	//  Get the comm config again.
	fSuccess = GetCommState(hCom, &dcb);

	if (!fSuccess)
	{
		//  Handle the error.
		printf_s("GetCommState failed with error %d.\n", GetLastError());
		return (2);
	}

	PrintCommState(dcb);       //  Output to console

	// _tprintf (TEXT("Serial port %s successfully reconfigured.\n"), pcCommPort);
	printf_s(TEXT("Serial port %s successfully reconfigured.\n"), pcCommPort);
	printf_s("\n");
	printf_s("\n");
	printf_s("Thermal Stream need check communication, please wait.................\n");

	// Enter remote mode first, only in serial port.
	pcCmd = TEXT("%RM\n");
	SendCommand(hCom, pcCmd, 4, FALSE);


	bool comm_valid_flag = false;
	// Query indentification to make sure system is ready.
	pcCmd = TEXT("*IDN?\n");
	SendCommand1(hCom, pcCmd, 6, TRUE, &flag);


	// Setup configuration.
	pcCmd = TEXT("DUTM 0\n"); // set to Air Mode
	SendCommand(hCom, pcCmd, 7, FALSE);

	pcCmd = TEXT("DSNS 0\n"); // switch DUT sensor to None for Air Mode
	SendCommand(hCom, pcCmd, 7, FALSE);

	// Operation start.
	pcCmd = TEXT("HEAD 1\n"); // Head Down and Start Flow
	SendCommand(hCom, pcCmd, 7, FALSE);




	if (flag == 1010)// 通信不正常
	{
		//  Setup and Verify Serial Port Configuration.
		//  Initialize the DCB structure.
		SecureZeroMemory(&dcb, sizeof(DCB));
		dcb.DCBlength = sizeof(DCB);
		//  Build on the current configuration by first retrieving all current
		//  settings.
		fSuccess = GetCommState(hCom, &dcb);
		if (!fSuccess)
		{
			//  Handle the error.
			printf_s("GetCommState failed with error %d.\n", GetLastError());
			return (2);
		}
		PrintCommState(dcb);       //  Output to console
		//  Fill in some DCB values and set the com state: 
		//  57,600 bps, 8 data bits, no parity, and 1 stop bit.
		dcb.BaudRate = CBR_115200;     //  baud rate
		dcb.ByteSize = 8;             //  data size, xmit and rcv
		dcb.Parity = NOPARITY;      //  parity bit
		dcb.StopBits = ONESTOPBIT;    //  stop bit
		fSuccess = SetCommState(hCom, &dcb);
		if (!fSuccess)
		{
			//  Handle the error.
			printf_s("SetCommState failed with error %d.\n", GetLastError());
			return (3);
		}
		//  Get the comm config again.
		fSuccess = GetCommState(hCom, &dcb);
		if (!fSuccess)
		{
			//  Handle the error.
			printf_s("GetCommState failed with error %d.\n", GetLastError());
			return (2);
		}
		PrintCommState(dcb);       //  Output to console
		// _tprintf (TEXT("Serial port %s successfully reconfigured.\n"), pcCommPort);
		printf_s(TEXT("Serial port %s successfully reconfigured.\n"), pcCommPort);
		printf_s("\n");
		printf_s("\n");
		printf_s("Thermal Stream need check communication, please wait.................\n");
		// Enter remote mode first, only in serial port.
		pcCmd = TEXT("%RM\n");
		SendCommand(hCom, pcCmd, 4, FALSE);
		comm_valid_flag = false;
		// Query indentification to make sure system is ready.
		pcCmd = TEXT("*IDN?\n");
		SendCommand1(hCom, pcCmd, 6, TRUE, &flag);
		// Setup configuration.
		pcCmd = TEXT("DUTM 0\n"); // set to Air Mode
		SendCommand(hCom, pcCmd, 7, FALSE);
		pcCmd = TEXT("DSNS 0\n"); // switch DUT sensor to None for Air Mode
		SendCommand(hCom, pcCmd, 7, FALSE);
		// Operation start.
		pcCmd = TEXT("HEAD 1\n"); // Head Down and Start Flow
		SendCommand(hCom, pcCmd, 7, FALSE);
	}











	if (flag == 1010)// 通信不正常
	{
		for (int i = 0; i<4; i++)
		{
			int try_cnt = 0;
			pcCmd = TEXT("%RM\n");
			SendCommand(hCom, pcCmd, 4, FALSE);
			pcCmd = TEXT("*IDN?\n");
			SendCommand1(hCom, pcCmd, 6, TRUE, &try_cnt);
			if (try_cnt == 1010)
			{
				i = i;
			}
			else
			{
				i = 4;
			}
		}

		pcCmd = TEXT("%RM\n");
		SendCommand(hCom, pcCmd, 4, FALSE);
		pcCmd = TEXT("*IDN?\n");
		SendCommand1(hCom, pcCmd, 6, TRUE, &flag);
		if (flag == 1010)
		{
			control_bit = true;//stop_loop_flag = true; will not do loop
			//--TEST_OUTPUT.MsgBox(MB_OKCANCEL,"Please restart the Thermal , communication failed");
			StsMessageBox("Warning!!! Please restart the Thermal, communication failed!!", "Click OK to EXIT");
			communication_success_falg = 0;// communication failed!!
		}

	}
	else
	{
		control_bit = false;
		communication_success_falg = 3;// communication successes!!
	}

	return communication_success_falg;
}



int Thermal_stream::Thermal_End()
{
	// Operation start.
	pcCmd = TEXT("HEAD 0\n"); // Head Down and Start Flow
	SendCommand(hCom, pcCmd, 7, FALSE);
	//--TEST_OUTPUT.Printf("Thermal_End have been execute !");
	return (0);
}

Thermal_stream::Thermal_stream()
{
	//if (AllocConsole())//(AttachConsole(ATTACH_PARENT_PROCESS))//
	//{
	//	COORD size = { 180, 180 };

	//	SetConsoleTitleA("AccoTEST Debug Window");
	//	freopen("conout$", "w+t", stdout);
	//	::DeleteMenu(GetSystemMenu(GetConsoleWindow(), FALSE), SC_CLOSE, MF_BYCOMMAND);
	//	//HANDLE hOUT = GetStdHandle(STD_OUTPUT_HANDLE);//获取标准输出句柄
	//	//hOUT = GetStdHandle(STD_OUTPUT_HANDLE);
	//	//设置控制台缓冲区大小
	//	//SetConsoleScreenBufferSize(hOUT, size);
	//	delay_ms(2000);
	//}



	Initial();

	pcCommPort = TEXT("COM1"); // default port is COM3
	//  Open a handle to the specified com port.
	hCom = CreateFile(pcCommPort,
		GENERIC_READ | GENERIC_WRITE,
		0,      //  must be opened with exclusive-access
		NULL,   //  default security attributes
		OPEN_EXISTING, //  must use OPEN_EXISTING
		0,      //  not overlapped I/O
		NULL); //  hTemplate must be NULL for comm devices

	printf_s("Execute Thermal_stream()!");
}

Thermal_stream::~Thermal_stream()
{
	// Port close
	CloseHandle(hCom);
	//--TEST_OUTPUT.Printf("Execute ~Thermal_stream()!");
	printf_s("Execute ~Thermal_stream()!");
	fclose(stdout);
	FreeConsole();
}

void Thermal_stream::Initial()
{
	L_button_clicked = false;
	sel_cnt_all = 0;  //selected loop count all

	set_tsize = 0;
	set_vsize = 0;
	sel_tcnt = 0;
	sel_vcnt = 0;
	soak_time_count = 1;
	//Tsoak_stable_time = 0;
	//Vsoak_stable_time = 0;
	temp_tolerance = 1.0;

	temp_seq = 0;
	vin_seq = 0;
	num_seq = 0;

	CHAR_LOOP = false;
	Manual_mode = true;
	TempLoopCount = 1;
	char_flag = 0;
	t_cnt = 0;
	v_cnt = 0;
	for (int i = 0; i<10; i++)
	{
		temp_history[i] = 0;
	}
	soak_stable_flag = false;// flag 用来判定是否进入 variation区间
	slow_soak = false;
	Tcal_set = 0.0;
	soak_sec_cnt = 0;
	temp_meas_count = 0;
	int Tsoak_t_1st = 10;
	int Tsoak_t_nst = 5;
	temp_variance = 1.0;
	al_flag = 'O';

	enter_level1_cnt = 0;
	enter_level2_cnt = 0;
	range_status = 0;
	soak_time_all_cnt = 1;
	for (int i = 0; i<5; i++)
	{
		temp_est_gap[i] = 0;
	}
	flow_flag[0] = 0;
	flow_flag[1] = 0;
	if (control_bit == false)
	{
		stop_loop_flag = false;
	}
	else
	{
		stop_loop_flag = true;
	}
	rise_to_fall = 1;
	abnormal_stop = false;// no user input, default value is false
	init_ts_config_cnt = 0;// first enter TS config will be 0 as default

	single_cond_soak_time_cnt = 0;
	//printf_s("Please Set Auto Test mode when you see this reminder!");

	//-----------------New temp char variables define

	time_cnt_phase3 = 0;


	phase_cnt1 = 0;
	phase_cnt2 = 0;
	phase_cnt3 = 0;
}
//void temp_loop_setup(CString temp_lp[], CString  vin_lp[], char* templp[], char* vinlp[], int *Temp_target, double *Vin_target, int lpcnt)



void Thermal_stream::mode_selection()
{
	if (MessageBoxA(NULL, "是否采用手动模式，选择-是(Y)\n   如果选择自动模式，选择-否(N)", "诊断提示对话框", MB_YESNO) == IDNO)
	{
		Manual_mode = false;
	}
	else
	{
		Manual_mode = true;
	}
}









bool Thermal_stream::confirm_L_button_clicked()
{
	return L_button_clicked;
}


void Thermal_stream::instruction()
{
	L_button_clicked = true;
#if 0

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
		delay_ms(2000);
	}

	char pgsfullpath[300];
	GetPgsFullPath(pgsfullpath, 300);
	string fullpathpgs(pgsfullpath);
	string pathofpgs = "";

	int pos = fullpathpgs.find_last_of('\\');
	if (pos > -1)
	{
		pathofpgs = fullpathpgs.substr(0, pos + 1);
	}

	std::string filePath = pathofpgs + "example.txt";

	// 创建输入文件流对象并打开文件
	std::ifstream inputFile(filePath);

	// 检查文件是否成功打开
	if (!inputFile) {
		std::cerr << "无法打开文件: " << filePath << std::endl;
		//return 1;
	}

	// 读取文件内容
	std::string line;
	std::vector<std::string> lines;
	while (std::getline(inputFile, line)) {
		lines.push_back(line);
	}

	// 关闭文件
	inputFile.close();

	string data[10];
	double Target_temp_get[10] = { 0 };
	double Target_temp_Tmax[10] = { 0 };

	string target_str, tmax_str;
	// 输出文件内容
	for (size_t i = 0; i < lines.size(); i++)
	{
		data[i] = lines[i];
		splitString(data[i], target_str, tmax_str);
		Target_temp_get[i] = extractNumberAfterEquals(target_str);
		Target_temp_Tmax[i] = extractNumberAfterEquals(tmax_str);
		std::cout << data[i] << std::endl;
	}

#endif 

	delay_ms(1);
	if (MessageBoxA(NULL, "是否采用手动模式，选择-是(Y)\n如果选择自动模式，选择-否(N)", "诊断提示对话框", MB_YESNO) == IDNO)
	{
		Manual_mode = false;
	}
	else
	{
		Manual_mode = true;
	}

	if (Manual_mode == false)
	{
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
			delay_ms(2000);
		}
		printf_s("Please Set Auto Test mode when you see this reminder!\n");
	}
	else
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



}


double Thermal_stream::set_temp(int force_temp, int soak_time, bool fbd_stable_tmcnt_flag = false)  // forbid_stable_time_count_flag, will not decrease soak stable time left when flag is true
{
	// Setup point.
	char SetTemp[10] = { "SETP 8" };
	char SetSoak[10] = { "SOAK 10\n" };


	////*****************************
	data_converter(SetTemp, force_temp);
	pcCmd = TEXT(SetTemp);
	SendCommand(hCom, pcCmd, 9, FALSE);// Set force temperature value 
	pcCmd = TEXT("SOAK 1\n");
	SendCommand(hCom, pcCmd, 7, FALSE);
	////********************************

	delay_ms(1000);

	if (soak_time == 1)
	{
		// no need to take action
	}
	else
	{
		if (soak_time == 2)
		{
			pcCmd = TEXT("SOAK 1\n");
		}
		else if (soak_time == 5)
		{
			pcCmd = TEXT("SOAK 4\n");
		}
		else if (soak_time == 10)
		{
			pcCmd = TEXT("SOAK 9\n");
		}
		else if (soak_time == 15)
		{
			pcCmd = TEXT("SOAK 14\n");
		}
		else if (soak_time == 20)
		{
			pcCmd = TEXT("SOAK 19\n");
		}
		else if (soak_time == 40)
		{
			pcCmd = TEXT("SOAK 39\n");
		}
		else if (soak_time == 60)
		{
			pcCmd = TEXT("SOAK 59\n");
		}
		else if (soak_time == 80)
		{
			pcCmd = TEXT("SOAK 79\n");
		}
		else if (soak_time == 100)
		{
			pcCmd = TEXT("SOAK 99\n");
		}
		else
		{
			pcCmd = TEXT("SOAK 2\n");
		}

		SendCommand(hCom, pcCmd, 7, FALSE);
	}

	// Set Soak time value 
	int gflag = 0;
	if (soak_time == 8)
		gflag = 1;
	else if (soak_time == 20)
		gflag = 2;
	else if (soak_time == 12)
		gflag = 3;
	else
		gflag = 0;
	double meas_val = 0.0;



	while (soak_time>0 && Tsoak_stable_time>0)
	{
		single_cond_soak_time_cnt++;

		//--TIME.wait_us(1e6);
		//meas_val= temp_meas(force_temp,Tsoak_stable_time, soak_stable_flag, gflag, fbd_stable_tmcnt_flag);
		meas_val = temp_meas(force_temp, Tsoak_stable_time, soak_stable_flag, gflag, fbd_stable_tmcnt_flag);
		if (soak_time>1)
		{
			if (abs(meas_val - get_temp())  <get_temp_variance())
			{
				if (fbd_stable_tmcnt_flag == false)
				{
					//Tsoak_stable_time--;
				}
				soak_stable_flag = true;
			}
			else
			{
				Tsoak_stable_time = Tsoak_t_nst;
				soak_stable_flag = false;
			}
		}
		soak_time--;
	}

	return meas_val;
}




void data_converter(char*tmp, int data)
{

	char tchar;
	int a1, a2, a3, flag;
	a1 = a2 = a3 = flag = 0;
	if (data >= 100)
	{
		a1 = 1;
		tchar = a1 + '0';
		tmp[5] = tchar;
		a2 = data % 100 / 10;
		tchar = a2 + '0';
		tmp[6] = tchar;
		a3 = data % 100 % 10;
		tchar = a3 + '0';
		tmp[7] = tchar;

	}
	else if (data >= 10 && data <99)
	{
		a2 = data / 10;
		tchar = a2 + '0';
		tmp[5] = tchar;
		a3 = data % 10;
		tchar = a3 + '0';
		tmp[6] = tchar;
		//tmp[7]=' ';
	}
	else if (data >= 0 && data <9)
	{
		a3 = data;
		tchar = a3 + '0';
		tmp[5] = tchar;
		//tmp[6]=' ';
		//tmp[7]=' ';
	}
	else if (data >= -9 && data<0)
	{
		tmp[5] = '-';
		a3 = abs(data);
		tchar = a3 + '0';
		tmp[6] = tchar;
		//tmp[7]=' ';
	}
	else
	{
		tmp[5] = '-';
		a2 = abs(data) / 10;
		tchar = a2 + '0';
		tmp[6] = tchar;
		a3 = abs(data) % 10;
		tchar = a3 + '0';
		tmp[7] = tchar;
	}
	//cout<<"temp =  "<<tmp<<endl;
}


int Thermal_stream::soak_temp_adjust_delay_time(double meas, int Ttarget, double previous_gap, int current_soak_cnt, int soak_cnt_set)
{
	if (current_soak_cnt >= soak_cnt_set)
	{
		if (meas - Ttarget < 0) //首先判断当前温度和目标温度的关系, 当前温度低于目标值***************************************************************
		{
			if (previous_gap>0)// 判定当前温度时升温还是降温, -------------------温度上升中-----------------------------------------------------------------------------------------------------
			{
				if (abs(meas - Ttarget) >3)// 判断当前温度和目标值差距, 温度差超过3C
				{
					if (previous_gap <0.3) //判断升温速度快慢, 温度上升慢,超过10s也达不到目标温度
					{
						soak_cnt_set = 2;
					}
					else if (previous_gap <0.6 && previous_gap >0.3) //判断升温速度快慢, 温度上升中速度,3秒需要重新调教温度
					{
						soak_cnt_set = 3;
					}
					else
					{
						soak_cnt_set = 1;
					}
				}
				else if (abs(meas - Ttarget) >2 && abs(meas - Ttarget) <3)// 温度差在2~3C之间
				{
					if (previous_gap <0.25) //判断升温速度快慢, 温度上升慢,超过10s也达不到目标温度
					{
						soak_cnt_set = 4;
					}
					else if (previous_gap <0.45 && previous_gap >0.25) //判断升温速度快慢, 温度上升中速度,3秒需要重新调教温度
					{
						soak_cnt_set = 2;
					}
					else
					{
						soak_cnt_set = 1;
					}
				}
				else if (abs(meas - Ttarget) >1 && abs(meas - Ttarget) <2) // 温度差在1~2C之间
				{
					if (previous_gap <0.2) //判断升温速度快慢, 温度上升慢,超过10s也达不到目标温度
					{
						soak_cnt_set = 4;
					}
					else if (previous_gap <0.3 && previous_gap >0.2) //判断升温速度快慢, 温度上升中速度,3秒需要重新调教温度
					{
						soak_cnt_set = 2;
					}
					else
					{
						soak_cnt_set = 1;
					}
				}
				else // 温度差小于1C
				{
					if (previous_gap <0.1) //判断升温速度快慢, 温度上升慢,超过10s也达不到目标温度
					{
						soak_cnt_set = 8;
					}
					else if (previous_gap <0.2 && previous_gap >0.1) //判断升温速度快慢, 温度上升中速度,3秒需要重新调教温度
					{
						soak_cnt_set = 5;
					}
					else
					{
						soak_cnt_set = 3;
					}
				}
			}
			else //温度低于目标值,降温中,需要让芯片尽快回到升温区间--------------------------------------------------------------------------------------------------------
			{
				if (abs(meas - Ttarget) >3)// 判断当前温度和目标值差距, 温度差超过3C
				{
					if (previous_gap <0.1) //判断降低温速度快慢, 温度上升慢,超过10s也达不到目标温度
					{
						soak_cnt_set = 5;
					}
					else if (previous_gap <0.3 && previous_gap >0.1) //判断升温速度快慢, 温度上升中速度,3秒需要重新调教温度
					{
						soak_cnt_set = 2;
					}
					else
					{
						soak_cnt_set = 1;
					}
				}
			}  //---------------降温中----------------------------------------------------------------------------------------------------------------------------------------------------------------


		}//----------------温度低于目标值***************************************************************************
		else  //-----------------------温度高于目标值*******************************************************************
		{
			if (previous_gap<0)// 判定当前温度时升温还是降温,----------------- 降温中------------------------------------------------------------------------------
			{
				if (abs(meas - Ttarget) >3)// 判断当前温度和目标值差距, 温度差超过3C
				{
					if (abs(previous_gap) <0.3) //判断升温速度快慢, 温度下降慢,超过10s也达不到目标温度
					{
						soak_cnt_set = 6;
					}
					else if (abs(previous_gap)  <0.6 && abs(previous_gap)  >0.3) //判断升温速度快慢, 温度上升中速度,3秒需要重新调教温度
					{
						soak_cnt_set = 3;
					}
					else
					{
						soak_cnt_set = 1;
					}
				}
				else if (abs(meas - Ttarget) >2 && abs(meas - Ttarget) <3)// 温度差在2~3C之间
				{
					if (abs(previous_gap)  <0.25) //判断升温速度快慢, 温度上升慢,超过10s也达不到目标温度
					{
						soak_cnt_set = 4;
					}
					else if (abs(previous_gap)  <0.45 &&abs(previous_gap)  >0.25) //判断升温速度快慢, 温度上升中速度,3秒需要重新调教温度
					{
						soak_cnt_set = 2;
					}
					else
					{
						soak_cnt_set = 1;
					}
				}
				else if (abs(meas - Ttarget) >1 && abs(meas - Ttarget) <2) // 温度差在1~2C之间
				{
					if (abs(previous_gap) <0.2) //判断升温速度快慢, 温度上升慢,超过10s也达不到目标温度
					{
						soak_cnt_set = 4;
					}
					else if (abs(previous_gap) <0.3 &&abs(previous_gap) >0.2) //判断升温速度快慢, 温度上升中速度,3秒需要重新调教温度
					{
						soak_cnt_set = 2;
					}
					else
					{
						soak_cnt_set = 1;
					}
				}
				else // 温度差小于1C
				{
					if (abs(previous_gap) <0.1) //判断升温速度快慢, 温度上升慢,超过10s也达不到目标温度
					{
						soak_cnt_set = 8;
					}
					else if (abs(previous_gap)  <0.2 &&abs(previous_gap)  >0.1) //判断升温速度快慢, 温度上升中速度,3秒需要重新调教温度
					{
						soak_cnt_set = 5;
					}
					else
					{
						soak_cnt_set = 3;
					}
				}
			}
			else //// 判定当前温度时升温还是降温,----------------- 升温中,需要让芯片尽快回到降温区间-------------------------------------------------------------------------
			{
				if (abs(meas - Ttarget) >3)// 判断当前温度和目标值差距, 温度差超过3C
				{
					if (abs(previous_gap) <0.1) //判断降低温速度快慢, 温度上升慢,超过10s也达不到目标温度
					{
						soak_cnt_set = 5;
					}
					else if (abs(previous_gap) <0.3 && abs(previous_gap) >0.1) //判断升温速度快慢, 温度上升中速度,3秒需要重新调教温度
					{
						soak_cnt_set = 2;
					}
					else
					{
						soak_cnt_set = 1;
					}
				}
			}//------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

		}//**********************************************************************************************************************************

	}//------------------need to update soak_cnt_set


	return soak_cnt_set;

}





//double Thermal_stream::trim_modify_temp(double meas, int target, double previous_gap, int current_soak_cnt, int soak_cnt_set, double Tset_cal)
//{
//	if (current_soak_cnt >= soak_cnt_set)
//	{
//
//		if (meas - target <0) // //*************************************************温度低于目标值
//		{
//			rise_to_fall = 1;
//			printf_s("需要升温\n");
//
//
//
//			if (previous_gap>0) // 升温中---------------------------------------------------------------------------
//			{
//				if (target - meas <1) // 温差小于1C
//				{
//					if (previous_gap <0.3)//0.15
//					{
//						Tset_cal = Tset_cal;
//					}
//					else if (previous_gap > 0.3 && previous_gap<0.5)//0.15,0.2
//					{
//						Tset_cal = Tset_cal - 1;
//					}
//					else
//					{
//						Tset_cal = Tset_cal - 2;
//					}
//				}
//				else if (target - meas <1.5 && target - meas >1)// 温差在1C~1.5C
//				{
//					if (previous_gap >0.15 && previous_gap <0.25)
//					{
//						Tset_cal = Tset_cal;
//					}
//					else
//					{
//						Tset_cal = Tset_cal + abs(meas - target);
//					}
//				}
//				else if (target - meas <3 && target - meas >1.5) // 温差大于1.5C
//				{
//					if (previous_gap >0.6)
//					{
//						Tset_cal = Tset_cal;
//					}
//					else
//					{
//						Tset_cal = Tset_cal + abs(meas - target);
//					}
//				}
//				else
//				{
//					if (previous_gap >1)
//					{
//						Tset_cal = Tset_cal;
//					}
//					else
//					{
//						Tset_cal = Tset_cal + abs(meas - target);
//					}
//
//
//				}
//			}//-----------------------升温中---------------------------------------------------------------------------
//			else //----------------------------------------降温中------------------------------------------------
//			{
//				Tset_cal = Tset_cal + abs(meas - target);
//			}//--------------------------------------------
//
//		}//---------------------------------------------------//温度低于目标值
//		else //*************************************************温度高于目标值
//		{
//			rise_to_fall = 0;
//			printf_s("需要降温\n");
//			if ((temp_history[9] - temp_history[8]) > 0 && rise_to_fall == 0)
//			{
//				return Tset_cal - 1;
//			}
//
//			if (previous_gap>0) // 升温中---------------------------------------------------------------------------
//			{
//				Tset_cal = Tset_cal - abs(meas - target);
//			}
//			else // 降温中-----------------------------------------------------------------------------------------
//			{
//
//				if (meas - target  <1) // 温差小于1C
//				{
//					if (abs(previous_gap) <0.3)
//					{
//						Tset_cal = Tset_cal;
//					}
//					else if (abs(previous_gap) > 0.3 && abs(previous_gap)<0.5)
//					{
//						Tset_cal = Tset_cal + 1;
//					}
//					else
//					{
//						Tset_cal = Tset_cal + 2;
//					}
//				}
//				else if (meas - target<1.5 && meas - target>1)// 温差在1C~1.5C
//				{
//					if (abs(previous_gap) >0.15 && abs(previous_gap) <0.25)
//					{
//						Tset_cal = Tset_cal;
//					}
//					else
//					{
//						Tset_cal = Tset_cal - abs(meas - target);
//					}
//				}
//				else  // 温差大于1.5C
//				{
//					Tset_cal = Tset_cal - abs(meas - target);
//				}
//			}//---------------------降温中
//		} //*************************************************温度高于目标值
//
//		soak_sec_cnt = 0;
//	}
//
//	int GAP1 = 32;
//	int GAP2 = 25;
//	int coe_temp = 0;
//
//
//	if (target >120 && target <130)
//	{
//		coe_temp = 15;
//	}
//	else if (target > 95 && target < 105)
//	{
//		coe_temp = 20;
//	}
//	else if (target >65 && target < 90)
//	{
//		coe_temp = 5;
//	}
//	else if (target >20 && target <30)
//	{
//		coe_temp = -5;
//	}
//	else if (target >-5 && target <5)
//	{
//		coe_temp = 0;
//	}
//	else if (target >-45 && target <-35)
//	{
//		coe_temp = 15;
//	}
//	else
//	{
//		coe_temp = 20;
//	}
//
//	if (target > 0.1)// temp target >0
//	{
//		if (meas<target)//防止施加的温度值和目标直差距过大，微调阶段 上升时候不超过30度,温度处于上升阶段
//		{
//			if (abs(Tset_cal - target) >GAP1)
//			{
//				Tset_cal = target + GAP1;//设置温度不能很高
//			}
//			else
//			{
//				Tset_cal = Tset_cal;
//			}
//		}
//		if (meas>target) //如果当前温度高于目标温度值，此时需要降温，设置温度 不得低于温度值+ 系数 
//		{
//			if (Tset_cal + coe_temp - target < 0)// 设置温度值不能很低
//			{
//				Tset_cal = target + coe_temp;
//			}
//			else
//			{
//				Tset_cal = Tset_cal;
//			}
//		}
//
//
//	}
//	else//-------------------temp target <0
//	{
//		if (meas>target)//防止施加的温度值和目标直差距过大，微调阶段 上升时候不超过30度,温度处于上升阶段
//		{
//			if (abs(Tset_cal - target) >GAP1)
//			{
//				Tset_cal = target - GAP1;// 即使温度高于-40C， 设置的soak温度不得低于-70C
//			}
//			else
//			{
//				Tset_cal = Tset_cal;
//			}
//		}
//		if (meas < target) //如果当前温度低于目标温度值，此时需要降温，设置温度 不得低于温度值+ 系数 
//		{
//			if (Tset_cal + coe_temp - target < 0)// 设置温度值不能很低
//			{
//				Tset_cal = target - coe_temp;// 即使温度已经超过 -40C,最高soak温度不得高于-50C
//			}
//			else
//			{
//				Tset_cal = Tset_cal;
//			}
//		}
//	}
//
//
//
//	return Tset_cal;
//
//}



//-----------------New temp char variables define

double Thermal_stream::trim_tune_temp(double meas, int target, double previous_gap, int current_soak_cnt, int soak_cnt_set, double Tset_cal)
{

	Phasemap[4].soak_time_count++;
	Phasemap[5].soak_time_count++;
	if (1/*current_soak_cnt >= soak_cnt_set*/)
	{

		if (meas - target <0) // //********温度低于目标值**************温度低于目标值**********************温度低于目标值**************温度低于目标值*******
		{
			rise_to_fall = 1;
			printf_s("trim_tune_temp-需要升温\n");
			if (previous_gap>0)  //===================升温中==================升温中===================升温中====================升温中=====================升温中=============升温中=========
			{

				if (target - meas <1) // --------------------------------------------------------------------------------------------------------温差小于1C
				{
					if (previous_gap <0.2)//0.15
					{
						Tset_cal = Tset_cal;
						printf_s("目标值高于当前温度小于1度，1秒内温度升高值小于0.2C， 保持Soak温度不变\n");
					}
					else if (previous_gap > 0.2&& previous_gap<0.35)//0.15,0.2
					{
						Tset_cal = Tset_cal - 1;
						printf_s("目标值高于当前温度小于1度，1秒内温度升高值在0.2C~0.35C之间， 升温过快，需要降1C \n");
					}
					else
					{
						Tset_cal = Tset_cal - 2;
						printf_s("目标值高于当前温度小于1度，1秒内温度升高值>0.35C， 升温过快，需要降2C \n");
					}
				}
				else if (target - meas <1.5 && target - meas >1)// ----------------------------------------------------------------------------温差在1C~1.5C
				{
					if (previous_gap >0.2)
					{
						Tset_cal = Tset_cal;
						printf_s("目标值高于当前温度在1C~1.5C，1秒内温度升高值>0.2C， 可以，保持Soak温度不变\n");
					}
					else
					{
						Tset_cal = Tset_cal + abs(meas - target);
						printf_s("目标值高于当前温度在1C~1.5C，1秒内温度升高值<0.2C， 太慢，Soak温度升高差值\n");
					}
				}
				else if (target - meas <3 && target - meas >1.5) // --------------------------------------------------------------------------温差1.5C~3C之间
				{
					if (previous_gap >0.6)
					{
						Tset_cal = Tset_cal;
						printf_s("目标值高于当前温度在1.5C~3C，1秒内温度升高值0.6C， 可以，Soak温度保持不变\n");
					}
					else
					{
						Tset_cal = Tset_cal + abs(meas - target);
						printf_s("目标值高于当前温度在1.5C~3C，1秒内温度升高值小于0.6C，太慢， Soak温度升高差值\n");
					}
				}
				else//------------------------------------------------------------------------------------------------------------------------温度差大于3C
				{
					if (previous_gap >1)
					{
						Tset_cal = Tset_cal;
						printf_s("目标值高于当前温度>3C，1秒内温度升高值1C， Soak温度保持不变\n");
					}
					else
					{
						Tset_cal = Tset_cal + abs(meas - target);
						printf_s("目标值高于当前温度>3C，1秒内温度升高值小于0.6C， Soak温度升高差值\n");
					}

				}


			}
			else //=============================降温中===============================降温中===============================降温中==========================降温中=====================降温中===========
			{
				Tset_cal = Tset_cal + abs(meas - target);
				printf_s("目标值高于当前温度，已经在降温， Soak温度升高差值\n");
			}//--------------------------------------------

		}

		else //*********温度高于目标值***************************温度高于目标值********************温度高于目标值********************温度高于目标值**********
		{
			rise_to_fall = 0;
			printf_s("trim_tune_temp-需要降温\n");
			if ((temp_history[9] - temp_history[8]) > 0 && rise_to_fall == 0)
			{
				printf_s("目标值低于当前温度，需要降温，芯片还在升温， 保持Soak温度降低一度\n");
				Tset_cal = Tset_cal - 1;
				return Tset_cal;	
			}

			if (previous_gap>0) // 升温中---------------------------------------------------------------------------
			{
				Tset_cal = Tset_cal - abs(meas - target);
				printf_s("目标值低于当前温度，需要降温，芯片还在升温， 保持Soak温度降低温差\n");
			}
			else // 降温中-----------------------------------------------------------------------------------------
			{
				printf_s("降温中。。。。\n");
				if (meas - target  <1) // 温差小于1C
				{
					printf_s("温度差小于1C 。。。。\n");
					if (abs(previous_gap) <0.2)
					{
						Tset_cal = Tset_cal;
						printf_s("目标值低于当前温度1C以内，芯片降温速度小于0.2C， 保持Soak温度不变\n");
					}
					else if (abs(previous_gap) > 0.2 && abs(previous_gap)<0.4)
					{
						Tset_cal = Tset_cal + 1;
						printf_s("目标值低于当前温度1C以内，芯片降温速度在0.2C~0.4C， 保持Soak温度+1C\n");
					}
					else
					{
						Tset_cal = Tset_cal + 2;
						printf_s("目标值低于当前温度1C以内，芯片降温速度大于0.4C， 保持Soak温度+2C\n");
					}
				}
				else if (meas - target<1.5 && meas - target>1)// 温差在1C~1.5C
				{
					printf_s("温度差在1C~1.5C范围内 。。。。\n");
					if (abs(previous_gap) >0.25)
					{
						Tset_cal = Tset_cal;
						printf_s("目标值低于当前温度1~1.5C以内，芯片降温速度大于0.25， 可以，保持Soak温度不变\n");
					}
					else
					{
						printf_s("abs(previous_gap) <=0.25,Tset_cal=%.2f\n", Tset_cal);
						Tset_cal = Tset_cal - abs(meas - target);
						printf_s("目标值低于当前温度1~1.5C以内，芯片降温速度小于0.25C， 太慢，保持Soak温度降低差值\n");
						printf_s("Tset_cal=%.2f，abs(meas - target)=%.2f,  保持Soak温度降低差值\n", Tset_cal, abs(meas - target));
					}
				}
				else  // 温差大于1.5C
				{
					printf_s("温度差大于1.5C 。。。。Tset_cal=%.2f,  abs(meas - target)=%.2f\n", Tset_cal, abs(meas - target));
					Tset_cal = Tset_cal - abs(meas - target);
					printf_s("目标值低于当前温度>1.5C，芯片降温，保持Soak温度降低差值, Tset_cal=%.2f\n", Tset_cal);
				}
			}//---------------------降温中
		} //*************************************************温度高于目标值

		soak_sec_cnt = 0;
	}

	return Tset_cal;
}













double Thermal_stream::soak_temp_value_calculate(int target_temp, double meas, bool enter_range_flag)// 目标温度，当前温度，第几次进入当前的温度范围
{
	//------首先接受函数传值
	double Cal_target_temp = target_temp;
	double Cal_meas_temp = meas;
	double Cal_enter_range_cnt = enter_range_flag;
	double Cal_gap = Cal_target_temp - Cal_meas_temp;
	double Tset_cal = 0;


	//-----判断需要升温还是需要降温
	int CAL_TEMP_RISE = 0;
	if (Cal_target_temp>Cal_meas_temp)
	{
		CAL_TEMP_RISE = 1;//需要升温
		printf_s("soak_temp_calculate--需要升温\n");
	}
	else
	{
		CAL_TEMP_RISE = 0;//需要降温
		printf_s("soak_temp_calculate--需要降温\n");
	}


	if (abs(Cal_gap)>4 && Phase <= 1)// --------第一阶段，首次温度差在4C以内
	{
		Phase = 1;
		printf_s("第1阶段,,说明 未进入4C范围\n");
	}

	//================这个阶段如果10s内进入不到阶段4，就需要改变abs Tmax 值
	if (abs(Cal_gap)<4 && abs(Cal_gap)>1.5&&  Phase <= 3)//---------第二阶段，首次温度差在1.5-4C之间,  
	{
		Phase = 2;
		printf_s("第2阶段,,说明 进入1.5C~4C范围了\n");
	}

	//=============== 这个阶段5s 内进入不到阶段2，就需要改变Tmax 值
	if (abs(Cal_gap)>4 && Phase>1)//---------第三阶段，温度进入4C范围后又超出4C范围
	{
		Phase = 3;
		printf_s("第3阶段,,说明 进入4C范围又出去了\n");
	}

	//==================第四阶段,温度差小于1.5C
	if (abs(Cal_gap)<1.5&& Phase <= 5)
	{
		Phase = 4;
		Phasemap[4].enter_phase_cnt++;
		if (Phasemap[4].enter_phase_cnt == 1)
		{
			Phasemap[4].temp_his[5] = 0;
			Phasemap[4].temp_his[4] = 0;
			Phasemap[4].temp_his[3] = 0;
			Phasemap[4].temp_his[2] = 0;
			Phasemap[4].temp_his[1] = 0;
			Phasemap[4].temp_his[0] = 0;
		}
		Phasemap[4].temp_his[5] = meas;
		Phasemap[4].temp_his[4] = Phasemap[4].temp_his[5];
		Phasemap[4].temp_his[3] = Phasemap[4].temp_his[4];
		Phasemap[4].temp_his[2] = Phasemap[4].temp_his[3];
		Phasemap[4].temp_his[1] = Phasemap[4].temp_his[2];
		Phasemap[4].temp_his[0] = Phasemap[4].temp_his[1];
		printf_s("第4阶段,,说明 进入1.5C范围了\n");
	}
	//==================
	if (abs(Cal_gap)>1.5&&  Phase >3&&Phase <= 5)//--------第五阶段,温度差大于1.5C
	{
		Phase = 5;
		printf_s("第5阶段,,说明 进入1.5C范围又出去了\n");
	}


	//----------------------定义微调的方法
	soak_time_count = 1;
	temp_history[6] = temp_history[7];
	temp_history[7] = temp_history[8];
	temp_history[8] = temp_history[9];
	temp_history[9] = meas;
	double step_gap1 = temp_history[9] - temp_history[8];
	double step_gap2 = temp_history[9] - temp_history[7];
	double step_gap3 = temp_history[9] - temp_history[6];


	if (Phase == 1)// 第一阶段：当前温度和目标温度差值>4C
	{
		if (CAL_TEMP_RISE == 1)
		{
			if (Cal_target_temp > 20 && Cal_target_temp < 30 && abs(Cal_gap) < 5)// 目标值是25C，同时当前温度和25C相差小于4C
			{
				Tcal_set = 35;
			}
			else
			{
				Tcal_set = 170;
			}
		}
		else
		{
			if (Cal_target_temp > 20 && Cal_target_temp < 30 && abs(Cal_gap) < 5)// 目标值是25C，同时当前温度和25C相差小于4C
			{
				Tcal_set = 15;
			}
			else
			{
				Tcal_set = -85;
			}
		}
		Phasemap[2].soak_time_count = 0;
		Phasemap[3].soak_time_count = 0;
		Phasemap[4].soak_time_count = 0;
		Phasemap[5].soak_time_count = 0;
	}
	//=========第二个阶段，本阶段处理由于温度上下限限制长时间无法到达指定温度，在此调整温度限值==============================
	if (Phase == 2)//-------第二阶段：温度差在1.5C到4C之间
	{
		if (CAL_TEMP_RISE == 1 && Phasemap[2].soak_time_count > 8)//------需要升温，如果在第二阶段持续时间过长，大于12s，需要调整clamp的值，保证温度可以被soak到
		{
			//Tmax = Tmax + 5;
			Tmax = Tmax + (int)Cal_gap;
			Tcal_set = Tmax;
			Phasemap[2].soak_time_count = 0;
		}
		else if (CAL_TEMP_RISE == 0 && Phasemap[2].soak_time_count > 8)//------需要降温，如果在第二阶段持续时间过长，大于12s，需要调整clamp的值，保证温度可以被soak到
		{
			Tmax = Tmax + (int)Cal_gap;
			//Tmax = Tmax - 5;
			Tcal_set = Tmax;
			Phasemap[2].soak_time_count = 0;
		}
		else
		{
			if (target_temp > 50 && abs(Tsel_target[0] - target_temp) > 0.1 && meas>target_temp)//---- 如果当前目标温度大于50C而且不是第一个温度点（表示从第一温度到本温度是降温阶段）
			{
				if (CAL_TEMP_RISE == 1)
				{
					Tcal_set = Tmax;
				}
				else
				{
					Tcal_set = target_temp + 10 + (target_temp-meas) * 2;
				}
			}
			else
			{
				Tcal_set = Tmax;
			}
			
		}

		Phasemap[2].soak_time_count++;
		Phasemap[3].soak_time_count = 0;
		Phasemap[4].soak_time_count = 0;
		Phasemap[5].soak_time_count = 0;
	}
	//===============================================================================================================

	//=========第3个阶段，本阶段处理由于温度上下限限制长时间无法到达指定温度，在此调整温度限值==============================
	if (Phase == 3)//-------第3阶段：温度差在1.5C到4C之间
	{
		if (CAL_TEMP_RISE == 1 && Phasemap[3].soak_time_count > 8)//------如果在第二阶段持续时间过长，大于12s，需要调整clamp的值，保证温度可以被soak到
		{
			//Tmax = Tmax + 5;
			if (Cal_gap > 0)
			{
				if (Cal_gap < 5)
					Cal_gap = 5;
			}
			else
			{
				if (Cal_gap > -5)
					Cal_gap = -5;
			}
			printf_s("第3阶段,升温中,第二阶段持续时间超过8s, Tcal_set=%d", Tcal_set);
			Tmax = Tmax + (int)Cal_gap;
			Tcal_set = Tmax;
			Phasemap[3].soak_time_count = 0;
			printf_s("  ,  Tmax=%d \n", Tmax);
		}
		else if (CAL_TEMP_RISE == 0 && Phasemap[3].soak_time_count > 8)//------如果在第二阶段持续时间过长，大于12s，需要调整clamp的值，保证温度可以被soak到
		{
			//Tmax = Tmax - 5;
			if (Cal_gap >0)
			{
				if (Cal_gap < 5)
					Cal_gap = 5;
			}
			else
			{
				if (Cal_gap >-5)
					Cal_gap = -5;
			}
			printf_s("第3阶段,降温中第二阶段持续时间超过8s, Tcal_set=%d", Tcal_set);
			Tmax = Tmax + (int)Cal_gap;
			Tcal_set = Tmax;
			Phasemap[3].soak_time_count = 0;
			printf_s("   ,Tmax=%d\n", Tmax);
		}
		else
		{
			printf_s("第3阶段,持续时间低于8s， Tmax=%d, Tcal_set=%d\n", Tmax, Tcal_set);
			Tcal_set = Tmax;
			
		}

		Phasemap[3].soak_time_count++;
		Phasemap[2].soak_time_count = 0;
		Phasemap[4].soak_time_count = 0;
		Phasemap[5].soak_time_count = 0;
	}

	//====================第4 和第5只有微调阶段才会用 trim_modify_temp 这个函数====================================================
	if (Phase > 3)
	{
		phase_cnt2 = 0;
		int comp_range = 8;
		int soak_cnt_cnt = 3;
		if (abs(Tcal_set) < 0.001)
		{
			Tcal_set = SOAK_TEMP;
		}
		soak_sec_cnt++;
		soak_cnt_cnt = (int)soak_temp_adjust_delay_time(meas, (int)Cal_target_temp, step_gap2, soak_sec_cnt, soak_cnt_cnt);//gap2
		Tcal_set = trim_tune_temp(meas, (int)Cal_target_temp, step_gap3, soak_sec_cnt, soak_cnt_cnt, Tcal_set);
	}
	//===============================================================================================================




	//=============针对第4-5阶段， 如果计算的设置温度超过限定值， 极限就设置为限定值，后续可以更改限定值======================

	std::vector<double>temp_meas_array;
	temp_meas_array.resize(6);
	for (int i = 0; i<5; i++)
		temp_meas_array.push_back(Phasemap[4].temp_his[i]);
	std::sort(temp_meas_array.begin(), temp_meas_array.end());


	bool stable_flag = true;
	if (Phasemap[4].soak_time_count>6)
	{
		if (temp_meas_array[1] - temp_meas_array[6]>1)
		{
			stable_flag = false;
		}
		else
		{
			stable_flag = true;
		}
	}

	//==============1. 如果频繁跳跃，说明温度的调节范围过大了，引起了震荡
	if (stable_flag == false)
	{
		Tmax = target_temp + (int)((Tmax - target_temp)*0.8);
	}

	//==============2. 如果长时间达不到目标值，那就是温度范围过窄了

	if (Phase >= 4 && stable_flag == true)// 如果位于第4-5阶段
	{
		Tclamp = Tmax;
		if (Tcal_set>Tclamp + 5)
		{	
			Tcal_set = Tclamp + 5;
		}
		if (Tcal_set<Tclamp - 5)
		{
			Tcal_set = Tclamp - 5;
		}
		Phasemap[4].soak_clamp_cnt++;
	}
	//-----如果在第四阶段及以上阶段，长时间达不到目标温度，需要调整Clamp 值
	if (Phasemap[4].soak_clamp_cnt > 10 && Phase >= 4 && stable_flag == true)
	{
		if (Cal_gap > 0)
		{
			if (Cal_gap < 5)
				Cal_gap = 5;
		}
		else
		{
			if (Cal_gap > -5)
				Cal_gap = -5;
		}

	   Tmax = Tmax + (int)Cal_gap;

		time_cnt_phase3 = 0;
		Phasemap[4].soak_clamp_cnt = 0;
	}

	SOAK_TEMP = (int)Tcal_set;
	return Tcal_set;
}















void Thermal_stream::Temp_char_study_mode(std::ofstream *outfile, int target_set)
{
	int Temp_Set_study_fixed = 0;
	if (abs(target_set - 120)<10)
	{
		Temp_Set_study_fixed = 140;
	}
	if (abs(target_set - 100)<10)
	{
		Temp_Set_study_fixed = 115;
	}
	if (abs(target_set - 85)<10)
	{
		Temp_Set_study_fixed = 100;
	}
	if (abs(target_set - 70)<10)
	{
		Temp_Set_study_fixed = 85;
	}
	if (abs(target_set - 25)<10)
	{
		Temp_Set_study_fixed = 25;
	}
	if (abs(target_set)<10)
	{
		Temp_Set_study_fixed = -10;
	}
	if (abs(target_set + 20)<10)
	{
		Temp_Set_study_fixed = -35;
	}
	if (abs(target_set + 40)<10)
	{
		Temp_Set_study_fixed = -55;
	}

	double temp_measure_study = 0;
	temp_measure_study = temp_meas(target_set, Tsoak_stable_time, soak_stable_flag, 0, false);
	double Temp_set_study = 0;
	int Guess_conut_phase1 = 0;
	int phase1_flag = 0;
	int phase3_flag = 0;
	double Gap_cal = 0;
	int Guess_conut_phase3 = 0;
	while (Guess_conut_phase3 + Guess_conut_phase1<90)// 测试时间超过5分钟 或者温度差值小于1C
	{
		temp_measure_study = temp_meas(target_set, 1, true, 0, false);
		//====当温度范围大于10C，全力加速
		if (abs(temp_measure_study - target_set)>10 && phase1_flag == 0)
		{
			if (temp_measure_study<target_set)
			{
				Temp_set_study = 170;
			}
			if (temp_measure_study>target_set)
			{
				Temp_set_study = -85;
			}
		}
		else
		{
			phase1_flag = 1;
		}
		if (abs(temp_measure_study - target_set)<20 && phase1_flag == 1 && Guess_conut_phase1<70) //====当温度小于10C，按照设定值soak 150  cycle
		{
			Temp_set_study = Temp_Set_study_fixed;
			Guess_conut_phase1++;
		}
		else   //====计算差值，更新测试值，再做100 soak cycle
		{
			if (phase3_flag == 0)
			{
				Gap_cal = target_set - temp_measure_study;
				Temp_set_study = Temp_set_study + Gap_cal;
			}
			phase3_flag = 1;
			Guess_conut_phase3++;
		}

		set_temp((int)Temp_set_study, 1, false);

	}

	for (std::map<int, int>::iterator itr = temp_set_max_map.begin(); itr != temp_set_max_map.end(); ++itr)
	{
		if (itr->first == target_set)
		{
			itr->second = (int)Temp_set_study;
		}
	}

	for (std::map<int, int>::iterator itr = temp_set_min_map.begin(); itr != temp_set_min_map.end(); ++itr)
	{
		if (itr->first == target_set)
		{
			itr->second = (int)target_set;
		}
	}




	// 遍历map，并将每个键值对写入文件
	for (std::map<int, int>::iterator itr = temp_set_max_map.begin(); itr != temp_set_max_map.end(); ++itr)
	{
		if (itr->first == target_set)
		{
			*outfile << "Target =" << itr->first << ", Tmax_set as:  " << itr->second << std::endl;
		}
	}
}






void Thermal_stream::temp_loop_control_study_mode()
{
	char pgsfullpath[300];
	GetPgsFullPath(pgsfullpath, 300);
	string filepath(pgsfullpath);

	int pos = filepath.find_last_of('\\');
	string tempcharfile = filepath.substr(0, pos);
	tempcharfile = tempcharfile + "\\tempchar_setup.txt";
	std::ifstream infile(tempcharfile);

	// 打开文件以写入数据
	std::ofstream outfile(tempcharfile);
	// 检查文件是否成功打开
	if (!outfile.is_open()) {
		std::cerr << "Unable to open file for writing: " << tempcharfile << std::endl;
	}


	string line;
	string Tsoak_stable_time_Str, Vsoak_stable_time_Str;
	while (std::getline(infile, line))
	{

		size_t pos = pos = line.find('=');
		if (pos != std::string::npos)
		{
			//===========获取其他值， soaktime值
			if (line.find("Tsoak_stable_time=") != std::string::npos)
			{
				Tsoak_stable_time_Str = line;
			}
			else if (line.find("Vsoak_stable_time=") != std::string::npos)
			{
				Vsoak_stable_time_Str = line;
			}
		}
	}

	outfile << Tsoak_stable_time_Str << std::endl;
	outfile << Vsoak_stable_time_Str << std::endl;


	for (int i = 0; i < sel_tcnt; i++)
	{
		Temp_char_study_mode(&outfile, Tsel_target[i]);
	}
	// 关闭文件
	outfile.close();
}


void Thermal_stream::temp_loop_control()
{
	num_seq = (TempLoopCount - 1) % (sel_tcnt*sel_vcnt) + 1;
	temp_seq = (num_seq - 1) / sel_vcnt; // calculate which temp point need to be looped
	vin_seq = (num_seq - 1) % sel_vcnt;  // calculate which vin point need to be looped
	int Temp_spec = Tsel_target[temp_seq];
	V_PS1_TYP = Vsel1_target[vin_seq];
	V_PS2_TYP = Vsel2_target[vin_seq];
	V_PS3_TYP = Vsel3_target[vin_seq];

	for (int i = 0; i < (int)spec("PS1_CHAR").count(); i++)
	{
		if (abs(spec("PS1_CHAR")[i] - V_PS1_TYP) < 0.01)
		{
			vin_index = i;
		}
	}

	spec.set_sel_vin_index(vin_index);


	for (int i = 0; i < (int)spec("TEMP_CHAR").count(); i++)
	{
		if (abs(spec("TEMP_CHAR")[i] - Temp_spec) < 0.01)
		{
			temp_index = i;
		}
	}
	spec.set_sel_temp_index(temp_index);
	Temperature1 = (double)Temp_spec;



	for (std::map<int, int>::iterator itr = temp_set_max_map.begin(); itr != temp_set_max_map.end(); ++itr)
	{
		if (abs(itr->first - Temperature1)<0.1)
		{
			Tmax = itr->second;
		}
	}
	for (std::map<int, int>::iterator itr = temp_set_min_map.begin(); itr != temp_set_min_map.end(); ++itr)
	{
		if (abs(itr->first - Temperature1)<0.1)
		{
			Tmin = itr->second;
		}
	}




	//if (Temperature1 > 20 && Temperature1 < 30)
	//{
	//	Tmax = 25;
	//	Tmin = 10;
	//}
	//if (Temperature1 > 80 && Temperature1 < 90)
	//{
	//	Tmax = 105;
	//	Tmin = 90;
	//}
	//if (Temperature1 > 95 && Temperature1 < 100)
	//{
	//	Tmax = 128;
	//	Tmin = 110;
	//}
	//if (Temperature1 > 120 && Temperature1 < 130)
	//{
	//	Tmax = 155;
	//	Tmin = 130;
	//}
	//if (Temperature1 > -5 && Temperature1 < 5)
	//{
	//	Tmax = -20;
	//	Tmin = 10;
	//}
	//if (Temperature1 > -25 && Temperature1 < -15)
	//{
	//	Tmax = -45;
	//	Tmin = -15;
	//}
	//if (Temperature1 > -45 && Temperature1 < -35)
	//{
	//	Tmax = -65;
	//	Tmin = -35;
	//}

	double meas_temp[SITE_NUM] = { 0.0 };
	double test_temp[SITE_NUM] = { 0.0 };
	int  count = 100;
	int temp_first_loop = 0;
	single_cond_soak_time_cnt = 0;

	/************************This function will loop until arrived the target temperature*************************************************/
	int loop_temp;
	double temp_meas_lp;





	//=============将Setup的值返还给tempchar 做设置
	char pgsfullpath[300];
	GetPgsFullPath(pgsfullpath, 300);
	string filepath(pgsfullpath);
	int pos = filepath.find_last_of('\\');
	string tempcharfile = filepath.substr(0, pos);
	tempcharfile = tempcharfile + "\\tempchar_setup.tc";
	std::ifstream infile(tempcharfile);
	// 检查文件是否成功打开
	if (!infile.is_open()) {
		std::cerr << "无法打开文件以读取数据！" << std::endl;
	}
	std::string line;
	string pre_str, post_str;
	string value_target, value_set;
	//int map_target, map_setval;
	while (std::getline(infile, line))
	{
		//===========获取其他值， soaktime值
		if (line.find("Tsoak_stable_time=") != std::string::npos)
		{
			pos = line.find('=');
			post_str = line.substr(pos + 1, line.length());
			Tsoak_stable_time = getnumberfromstring(&post_str);
		}
		else if (line.find("Vsoak_stable_time=") != std::string::npos)
		{
			pos = line.find('=');
			post_str = line.substr(pos + 1, line.length());
			Vsoak_stable_time = getnumberfromstring(&post_str);
		}
	}




	if (vin_seq == 0)
	{
		//Tsoak_t_nst = 10;//定义每个温度第一次进入1C温度区间，需要维持多少秒在+/-1C的温度范围，才会允许开始测试	
		Tsoak_t_nst = Tsoak_stable_time;
	}
	else
	{
		//Tsoak_t_nst = 5;// //定义每个温度，非第一次进入1C温度区间，需要维持多少秒在+/-1C的温度范围，才会允许开始测试
		Tsoak_t_nst = Vsoak_stable_time;
	}
	enter_level1_cnt = 0;


	//----------------定义开始loop之前需要先测试一下芯片的温度，方便后续判断
	Tsoak_stable_time = Tsoak_t_nst; //10
	soak_stable_flag = false;
	bool enter_range_flag = false;

	if (vin_seq == 0)
	{
		temp_meas_lp = temp_meas(Temp_spec, Tsoak_stable_time, soak_stable_flag, 0, false);
	}
	else
	{
		temp_meas_lp = temp_meas(force_temp, Tsoak_stable_time, soak_stable_flag, 0, false);
	}

	loop_temp = Temp_spec;
	slow_soak = false;

	//-------定义是否有异常情况发生，比如通信不上，会在循环Loop之前终止掉整个程序
	if (control_bit == false)
	{
		stop_loop_flag = false;
	}
	else
	{
		stop_loop_flag = true;
	}

	for (int i = 0; i < 6; i++)
	{
		//set_temp(Temp_spec, 1, false);
		temp_meas_lp = temp_meas(Temp_spec, Tsoak_stable_time, soak_stable_flag, 0, false);
		temp_history[i] = temp_meas_lp;
		soak_sec_cnt++;
	}
	PRecord.phase_change_count = 0;
	PRecord.enter_phase1 = false;
	PRecord.enter_phase2 = false;
	PRecord.enter_phase3 = false;
	PRecord.enter_phase4 = false;
	PRecord.enter_phase5 = false;
	PRecord.exit_phase1 = false;
	PRecord.exit_phase2 = false;
	PRecord.exit_phase3 = false;
	History_Phase = 0;
	SOAK_TEMP = Temp_spec;
	if (vin_seq == 0)
	{
		Phase = 1;
	}
	//----------------在每个soak的温度点，需要保证的是在此时对于TClamp 进行赋值。
	if (vin_seq == 0)
	{
		Tclamp = Tmax;
	}


	for (int i = 0; i<5; i++)
	{
		Phasemap[i + 1].enter_phase_cnt = 0;
		Phasemap[i + 1].soak_clamp_cnt = 0;
		Phasemap[i + 1].soak_time_count = 0;
	}



	//---------------------------这里是整个循环的控制关键，判断条件在此处更新
	time_cnt_phase3 = 0;
	while (Tsoak_stable_time > 0 && stop_loop_flag == false)
	{
		//----------------------首先判断在单一温度点soak的时间是否超过10分钟，一旦超过，认为是异常的，需要终止loop，避免浪费时间
		if (single_cond_soak_time_cnt > 300)
		{
			stop_loop_flag = true;
		}
		//-------这里是等待时间的关键，每次loop一旦满足正负1C的要求，就会将soak 持续时间减一秒， 一旦超出1C范围，立即重新计数
		if (abs(temp_meas_lp - (double)Temp_spec) < get_temp_variance())
		{
			Tsoak_stable_time--;
			soak_stable_flag = true;
			enter_range_flag = true;
		}
		else
		{
			Tsoak_stable_time = Tsoak_t_nst;
			soak_stable_flag = false;
			enter_range_flag = false;
		}

		//---------此处是为了获取接下来需要soak 什么温度来使芯片靠近目标温度值
		loop_temp = (int)soak_temp_value_calculate(Temp_spec, temp_meas_lp, enter_range_flag);
		//--------此处是针对Thermal的异常处理，一旦soak 温度结尾是9， thermal会误判
		if (loop_temp % 10 == 9)
			loop_temp = loop_temp + 1;
		force_temp = loop_temp;
		//------此处是向thermal 发送soak的指令， 包括需要soak的温度和soak的时间，两个信息 
		temp_meas_lp = set_temp(loop_temp, soak_time_count, false);
		//---------------此处是为了传值，为了计算温度的历史差值，方便预测温度变化速度
		temp_history[0] = temp_history[1];
		temp_history[1] = temp_history[2];
		temp_history[2] = temp_history[3];
		temp_history[3] = temp_history[4];
		temp_history[5] = temp_meas_lp;
		double gap = temp_history[5] - temp_history[4];
		//---------------用户敲击了终止按钮，会立刻停止!!!!!!!!!!!!!!!!!!!!!!!!
		if (abnormal_stop == true)// User click E button on keyboard
		{
			stop_loop_flag = true;// stop temp control
		}


		//-----判断是否会不稳定，频繁在不同阶段之间跳跃
		if (History_Phase == Phase)
		{
			PRecord.phase_change_count = PRecord.phase_change_count;
		}
		else
		{
			PRecord.phase_change_count++;
		}
		History_Phase = Phase;
		if (PRecord.phase_change_count > 8 && Phase > 1 && abs(gap)>0.5)// 阶段改变次数大于8， 而且是在2345阶段之间跳跃，同时温度差变化超过2C。
		{
			Tmax = Temp_spec + (int)((Tmax - Temp_spec)*0.8);
			PRecord.phase_change_count = 0;
		}
	}

}




int getnumberfromstring(string *input_str)
{
	int  Number_transfer;
	//==============获取Target的值
	std::string numberStr = *input_str;
	std::string extractNum;
	bool NegativeFound = false;
	char c;
	for (std::string::iterator itr = numberStr.begin(); itr != numberStr.end(); ++itr)
	{
		c = *itr;
		if ((c >= '0'&&c <= '9') || (c == '-' &&NegativeFound == false))
		{
			extractNum += c;
			if (c == '-')
			{
				NegativeFound = true;
			}
		}
	}
	Number_transfer = std::stoi(extractNum);

	return Number_transfer;
}


// 设置文本颜色
void SetColorTC(int color) {
	SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), color);
}

// 重置文本颜色为默认值
void ResetColorTC() {
	SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), 7); // 7 是默认的白色文本
}