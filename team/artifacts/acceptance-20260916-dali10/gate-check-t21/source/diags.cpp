#include "stdafx.h"
#include "BoardCheck.h"
#include "sub.h"
#include <windows.h>
#include <iostream>
using namespace std;

#define		YES 	6
#define		NO	7
extern string int2str(DWORD n);






/* No repeat: board_check_repeat = -1 */
int board_check_repeat = -1; // set repeat count

void connected_site_check(BoardCheck& bc)
{
	//update for 8300
	double site_check_specl = 0;
	double site_check_spech = 0;
	double result[SITE_NUM] = { 0 };
	BYTE site_sta[SITE_NUM];
	STSGetSiteStatus(site_sta,SITE_NUM);

		for (int site = 0; site < 16; ++site)
		{
			if (USER_MODE == OPERATOR)
			{
				bc.SetSiteConnected(site, 1);
			}
			else
			{
				if (site_sta[site] == 1)
					bc.SetSiteConnected(site, 1);
				else  bc.SetSiteConnected(site, 0);
			}
		}
}


BOOL board_check_function(int &nBtn, BOOL &flag_pass)
{
	//	//////////////////////////////////////////////////////////////////
	//	/* Common usage format, don't change this if no specific need   */

	if (AllocConsole())//(AttachConsole(ATTACH_PARENT_PROCESS))//
	{
		COORD size = { 180, 180 };

		SetConsoleTitleA("BoardCheck Status Window");
		freopen("conout$", "w+t", stdout);
		::DeleteMenu(GetSystemMenu(GetConsoleWindow(), FALSE), SC_CLOSE, MF_BYCOMMAND);
		//HANDLE hOUT = GetStdHandle(STD_OUTPUT_HANDLE);//获取标准输出句柄
		//hOUT = GetStdHandle(STD_OUTPUT_HANDLE);
		////设置控制台缓冲区大小
		//SetConsoleScreenBufferSize(hOUT, size);
		//delay_ms(2000);
	}

	printf_s("\n");
	SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), 10);
	printf_s(" Performing Board Check, You Can Triggered By Hot Key: <CTRL+I > , \n");
	printf_s("\n");
	printf_s(" Please Wait For A Few Seconds Until Board Check Has Done...........\n");
	printf_s("\n");

	//std::cout << "" << endl;
	//SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), 10);
	//std::cout << " Performing Board Check, You Can Triggered By Hot Key: <CTRL+I > , " << endl<<std::flush;
	//std::cout << "" << endl;
	//std::cout << " Please Wait For A Few Seconds Until Board Check Has Done...........\n" << std::flush;
	//std::cout << "" << endl;



	BoardCheck bc;
	double result[SITE_NUM];
	string board_name;
	string board_rev;
	string board_number;
	for (int site = 0; site<SITE_NUM; ++site) result[site] = 9999;
	DWORD tnum = 1;

	bool stoponfail = 1;
	char Site_enable_flag[SITE_NUM];
	if (USER_MODE == OPERATOR)// operator mode need full site board check pass
	{
		Site_enable_flag[0] = 1;// ----------Site1 Enable
		Site_enable_flag[1] = 1;// ----------Site2 Enable
		Site_enable_flag[2] = 1;// ----------Site3 Enable
		Site_enable_flag[3] = 1;// ----------Site4 Enable
		Site_enable_flag[4] = 1;// ----------Site5 Enable
		Site_enable_flag[5] = 1;// ----------Site6 Enable
		Site_enable_flag[6] = 1;// ----------Site7 Enable
		Site_enable_flag[7] = 1;// ----------Site8 Enable
	}
	else// engineer mode, can select which site can be keep not check
	{
		Site_enable_flag[0] = 1;// ----------Site1 Enable
		Site_enable_flag[1] = 1;// ----------Site2 Enable
		Site_enable_flag[2] = 1;// ----------Site3 Enable
		Site_enable_flag[3] = 1;// ----------Site4 Enable
		Site_enable_flag[4] = 1;// ----------Site5 Enable
		Site_enable_flag[5] = 1;// ----------Site6 Enable
		Site_enable_flag[6] = 1;// ----------Site7 Enable
		Site_enable_flag[7] = 1;// ----------Site8 Enable
	}
	DWORD site_config = 0x0000;
	for (int i = 0; i < SITE_NUM; i++)
	{
		site_config = (DWORD)(site_config + Site_enable_flag[i] * pow(2, i));
	}
	STSSetSiteStatus(site_config);


	bc.Board_ID_Write("SC8561", "A", "1", "S24_31", "S24_15");
	//	//------------Board ID Check---------------
	if (0)
	{
		if (bc.Board_ID_Check("SC8561", "A", "S24_31", "S24_15"))
		{
			bc.Board_ID_Read(&board_name, &board_rev, &board_number, "S24_31", "S24_15");
		}
		else
		{

			nBtn = BTN_EXIT;
			return FALSE;
		}
	}

	BOOL Board_ID_Check(const char* boardName, const char* rev, const char* SCLChannel, const char* SDAChannel);
	BOOL Board_ID_Write(const char* boardName, const char* rev, const char* number, const char* SCLChannel, const char* SDAChannel);
	BOOL Board_ID_Read(const char* boardName, const char* rev, const char* number, const char* SCLChannel, const char* SDAChannel);


	int sel_flag = NO;
	bc.ClearSiteConnected();
	while ((bc.IsNoSiteConnected() || (sel_flag == NO)) && (board_check_repeat == -1))
	{
		connected_site_check(bc);
		if (bc.IsNoSiteConnected() && DEBUG_MODE)
		{
			if (MessageBoxA(NULL, "没有使能任何工位! \n请确认: 如果继续，选择-是(Y)\n如果退出，选择-否(N)", "诊断提示对话框", MB_YESNO) == IDNO){
				nBtn = BTN_EXIT;
				return FALSE;
			}
			continue;
		}
		sel_flag = YES;
	}

	if ((board_check_repeat != -1)) connected_site_check(bc);
	/* Common usage format, don't change this if no specific need   */
	//////////////////////////////////////////////////////////////////
	//
	//
	//	//////////////////////////////////////////////////////////////////
	//	/********************** User Define Begin ***********************/



	Cvi_config vi; // default FV,3V,0A,FOVIe_5V,FOVI_10MA,FPVIe_5V,FPVI_10MA,10ms,100 sample times,10 us interval
	//===========================================================================Cap Check===================================================//
	//----------------VBUS 10nF Cap
	//cbite.SetOn(K59_AGND_FS, -1);
	delay_ms(10);
	bc.test_cap_to_gnd(SW1_SW2_FXVI, tnum++, "VBUS_10nF_Cap, K59_AGND_FS", 5, 15, "nF");

	//----------------VBUS 4.7uF Cap
	//cbite.SetOn(K16_VBUS_Cap,K59_AGND_FS, -1);
	delay_ms(10);
	bc.test_cap_to_gnd(SW1_SW2_FXVI, tnum++, "K16_VBUS_Cap, K59_AGND_FS", 2.5, 7, "uF");


	return TRUE;
}


///////////////////////////////////////////////////////////////////////////
/* run_diags() define the boardcheck flow, as a part of boardcheck library
don't change this function if no specific need       				 */
///////////////////////////////////////////////////////////////////////////
BOOL run_diags(void)
{
	int nBtn = BTN_REDO;
	BOOL flag_pass = FALSE;

	if (USER_MODE == ADMIN)
	{
		if (MessageBoxA(NULL, "诊断即将开始! \n\n如果继续，请确认测试座里没有样品，选择-是(Y)\n如果退出，选择-否(N)", "诊断提示对话框", MB_YESNO) == IDNO)
		{
			PostQuitMessage(0);
			return FALSE;
		}
	}


	if (board_check_repeat < 0)
	{
		while ((nBtn == BTN_REDO) && (flag_pass == FALSE))
		{
			board_check_function(nBtn, flag_pass);
		}
		if ((nBtn == BTN_EXIT) || (nBtn == BTN_CANCEL))
		{
			PostQuitMessage(0);
		}	
		if (flag_pass == TRUE)
		{
			//MessageBoxA(NULL, "诊断成功！\n请点击确认，开始测试", "诊断提示对话框", MB_OK);
		}
			
	}

	string message_str;
	message_str = "重复测试" + int2str(board_check_repeat) + "次\n请点击确定按钮开始\n结束后程序自动退出\n数据请查看 bc.csv";
	if (board_check_repeat > 0)
	{
		MessageBoxA(NULL, message_str.c_str(), "诊断提示对话框", MB_OK);
	}
		
	while (board_check_repeat-- > 0)
	{
		board_check_function(nBtn, flag_pass);
		delay_ms(100);

		if (board_check_repeat == 1)
		{
			PostQuitMessage(0);
		}		
	}


	return TRUE;
}
