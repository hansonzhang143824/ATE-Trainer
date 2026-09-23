/********************************************************************/

/********************************************************************/


//#define _CRT_SECURE_NO_DEPRECATE
#include <windows.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "stdafx.h"
#include "FMEA.h"
#include <iostream>
#include <fstream>
extern "C" int GetPgsFullPath(LPTSTR pgsPath, int chNum);
int site_fmea;
BYTE sitesta_fmea[SITE_NUM];
#define SERIAL_FMEA StsGetSiteStatus(sitesta_fmea, SITE_NUM); for(site_fmea=0;site_fmea<SITE_NUM;site_fmea++)  if(sitesta_fmea[site_fmea])



ofstream ofile;

eFMEA::eFMEA(){
	for (int i = 0; i < MAX_SITES; i++)
	{


		valid_site[i] = 1;
		fmea_items_count[i] = 0;
	}
	test_item_count = 0;

	curr_site = 0;
	force_failed_item = 0;
	eot_site_count = 0;
	flag = 0;
	fmea_enable = 0;
	fmea_2_enable = 0;

	func_index_forcefail = 0;//记录强制fail func
	site_forcefail = 0;//记录强制fail site
	flag_forcefail = 0;//记录强制fail flag

	TXT_OPEN_FLAG = 0;
}
void eFMEA::FMEA_Site_Set(DWORD siteID)
{
	for (int i = 0; i < MAX_SITES; i++)
	{
		if (((DWORD)(i + 1))&siteID)
			valid_site[i] = 1;
		else
			valid_site[i] = 0;
	}
}
int eFMEA::sot(){
	if (TXT_OPEN_FLAG == 0)
	{
		if (fmea_enable) fmea_2_enable = 0;//这里使能1个就关闭另一个
		else if (fmea_2_enable) fmea_enable = 0;//这里使能1个就关闭另一个
		char pgsfullpath[300];
		GetPgsFullPath(pgsfullpath, 300);
		string fullpathpgs(pgsfullpath);
		string pathofpgs = "";

		int pos = fullpathpgs.find_last_of('\\');
		if (pos > -1)
		{
			pathofpgs = fullpathpgs.substr(0, pos + 1);
		}

		// generate_testercode_file
		string testercode_file = pathofpgs + "FMEA_info" + ".txt";
		ofile.open(testercode_file.c_str(), ios::out);
		TXT_OPEN_FLAG = 1;

	}

	if (fmea_enable)
	{
		if (flag == 0)
		{
			SERIAL_FMEA
			{
				if (valid_site[site_fmea])
				{
					curr_site = site_fmea;
					break;
				}
			}
			reinitflag = 0;
		}

		if (flag != 0)
		{
			force_failed_item++;//每测一次增加1
			SERIAL_FMEA fmea_items_count[site_fmea] = 0;//在fmea_checking中从1开始每个FUNC加1
		}
	}

	if (fmea_2_enable)
	{
		if (flag == 0)
		{
			force_failed_item++;//第一次增加1使得和fmea_items_count[site_fmea]一致
			SERIAL_FMEA
			{
				if (valid_site[site_fmea])
				{
					test_start_site = site_fmea;
					break;
				}
			}
			curr_site = test_start_site;
			reinitflag = 0;
		}

		if (flag != 0)
		{
			if (site_switch_flag)
			{
				SERIAL_FMEA// switch to next site
				{
					if (site_fmea > curr_site)
					{
						curr_site = site_fmea;
						break;
					}
				}
			}
			site_switch_flag = 1;
			SERIAL_FMEA fmea_items_count[site_fmea] = 0;//在fmea_checking中从1开始每个FUNC加1
		}
	}
	return 1;
}
int eFMEA::eot(){
	if (fmea_enable)
	{
		if (flag != 0)
		{
			if (fmea_items_count[curr_site] < force_failed_item)
				//MessageBoxA(NULL, "force fail的SITE,提前发生fail!", "FMEA", MB_OK);
				ofile << "force fail的SITE,提前发生fail! SITE" + int2str(curr_site) + "FUNC" + int2str(current_func[curr_site]) << "\n";

			if (force_failed_item == test_item_count)// switch to next site
			{
				int tempsite;
				tempsite = curr_site;
				force_failed_item = 0;
				SERIAL_FMEA
				{
					if (valid_site[site_fmea])
					{
						if (site_fmea > curr_site)
						{
							curr_site = site_fmea;
							break;
						}
					}
				}
					if (tempsite == curr_site)
					{
						MessageBoxA(NULL, "FMEA测试完成!", "FMEA", MB_OK);
						//ofile << "FMEA测试完成!" << "\n";
						ofile.close();
						fmea_enable = 0;
						flag = 0;

					}
			}
		}
		if (flag == 0)
		{
			if (reinitflag == 0) flag = 1;
		}
	}


	if (fmea_2_enable)
	{
		if (flag != 0)
		{
			if (fmea_items_count[curr_site] < force_failed_item)
				//MessageBoxA(NULL, "force fail的SITE,提前发生fail!", "FMEA", MB_OK);
				ofile << "force fail的SITE,提前发生fail! SITE" + int2str(curr_site) + "FUNC" + int2str(current_func[curr_site]) << "\n";


			if (curr_site == test_max_site)
			{
				force_failed_item++;//每遍历所有site一次增加1	
				curr_site = test_start_site;
				site_switch_flag = 0;
			}

			if (force_failed_item == (test_item_count + 1))
			{
				MessageBoxA(NULL, "FMEA测试完成!", "FMEA", MB_OK);
				//ofile << "FMEA测试完成!" << "\n";
				ofile.close();
				fmea_enable = 0;
				flag = 0;
			}
		}
		if (flag == 0)
		{
			if (reinitflag == 0) flag = 1;
		}
	}

	return 1;
}
eFMEA::~eFMEA(){

}

void eFMEA::fmea_checking(short func_index_fmea)
{
	SERIAL_FMEA current_func[site_fmea] = func_index_fmea;
	if (fmea_enable)
	{
		if (flag == 0)
		{
			SERIAL_FMEA
			{
				if (curr_site == site_fmea)
				test_item_count++;//第一次测PASS用于计数总共多少个FMEA项目	
			}
		}
		if (flag != 0)
		{
			SERIAL_FMEA fmea_items_count[site_fmea]++;

			SERIAL_FMEA
			{
				if (force_failed_item == fmea_items_count[site_fmea])
				{
					if (curr_site == site_fmea)
						AstGetParam(func_index_fmea, 0x00)->SetTestResult(site_fmea, 0, AstGetParam(func_index_fmea, 0x00)->GetMinLimit() - 1.0);

				}
			}
		}
	}
	else if (fmea_2_enable)
	{
		if ((flag == 0) && (test_item_count == 0))
		{
			SERIAL_FMEA
			{
				test_max_site = site_fmea;//用于判断是否遍历到了最大site
			}
		}
		if (flag == 0)
		{
			test_item_count++;//第一次测PASS用于计数总共多少个FMEA项目
		}
		if (flag != 0)
		{
			SERIAL_FMEA fmea_items_count[site_fmea]++;

			SERIAL_FMEA
			{
				if (force_failed_item == fmea_items_count[site_fmea])
				{
					if (site_fmea <= curr_site)
						AstGetParam(func_index_fmea, 0x00)->SetTestResult(site_fmea, 0, AstGetParam(func_index_fmea, 0x00)->GetMinLimit() - 1.0);

				}
			}
		}
	}
	else
	{
		if (flag_forcefail && (func_index_fmea == func_index_forcefail))
		{
			AstGetParam(func_index_forcefail, 0x00)->SetTestResult(site_forcefail, 0, AstGetParam(func_index_forcefail, 0x00)->GetMinLimit() - 1.0);
		}
	}


}
void eFMEA::fmea_onfailsite()
{
	int failsite = -1;

	if (fmea_enable)
	{
		if (flag == 0)
		{
			MessageBoxA(NULL, "请确认第一次测试PASS,确保测试稳定性", "FMEA", MB_OK);
			//ofile << "请确认第一次测试PASS,确保测试稳定性" << "\n";
			reinitflag = 1;
		}
		else
		{
			SERIAL_FMEA
			{
				failsite = site_fmea;
				if (curr_site != failsite)
					//MessageBoxA(NULL, "非期望的SITE发生fail!", "FMEA", MB_OK);
					ofile << "非期望的SITE发生fail! SITE" + int2str(failsite) + "FUNC" + int2str(current_func[failsite]) << "\n";
			}
		}
	}

	if (fmea_2_enable)
	{
		if (flag == 0)
		{
			MessageBoxA(NULL, "请确认第一次测试PASS,确保测试稳定性", "FMEA", MB_OK);
			//ofile << "请确认第一次测试PASS,确保测试稳定性" << "\n";
			reinitflag = 1;
		}
		else
		{
			SERIAL_FMEA
			{
				failsite = site_fmea;
				if (failsite > curr_site)
					//MessageBoxA(NULL, "非期望的SITE发生fail!", "FMEA", MB_OK);
					ofile << "非期望的SITE发生fail! SITE" + int2str(failsite) + "FUNC" + int2str(current_func[failsite]) << "\n";
			}
		}
	}
}

void eFMEA::force_item_fail(short func, int site)
{
	fmea_enable = 0;
	flag_forcefail = 1;
	func_index_forcefail = func;
	site_forcefail = site;
}

string eFMEA::int2str(DWORD n) {

	char t[64];
	int i = 0;

	if (n == 0)
		return "0";

	while (n) {
		t[i++] = char((n % 10) + '0');
		n /= 10;
	}
	t[i] = 0;

	string result(t);
	result = result.assign(result.rbegin(), result.rend());

	return result;
}