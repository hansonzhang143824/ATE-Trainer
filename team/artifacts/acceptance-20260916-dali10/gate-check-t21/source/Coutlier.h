/*****************************************************************************
*                                                                            *
*       Source title:   Coutlier.h                                           *
*                       (Filter Outlier in CP test )                         *
*         Create by:   Alan Luo                                              *
*                                                                            *
*        Description:                                                        *
*                                                                            *
*          1. source\\SOS_Config.csv is required for any mode				 *
*          2. source\\MP_DATA.csv is required for SIMULATION mode            *
*          3. Need updte mylib.h/LogDataStruct.h                             *
*                                                                            *
*   Revision History:                                                        *
*                                                                            *
*     2/20/22  r.rr  - Original coding.                                      *
*                                                                            *
*****************************************************************************/

/*
REVISION BLOCK:
-Rev. -- Date --------------------------------------------------
x		 --------  Long history with no record
00     03/10/22  Init release in JCAP for SC8547 8200;
01     03/18/22  Add log_sos_param_all function to make the code less in test.cpp
----------------------------------------------------------------
*/

#pragma once

#include "StdAfx.h"
#include "mylib.h"
#include "LogDataStruct.h"
#include "spec.h"

#define SIMULATION 0
#define PRODUCTION 1


class Coutlier{
private:
	int grubbs_outlier_init(string test, vector<double>& vec);  // scan all value, delete outlier, size of vec can't be <3 or >99
	int grubbs_outlier(string test, DWORD site, vector<double>& vec, double value); // outlier return TRUE, not outlier return FALSE and add value to vec, size of vec can't be <3 or >99
	int is_in_range(DWORD curr_x, DWORD curr_y, DWORD ref_x, DWORD ref_y, DWORD distance_limit); // return TRUE if the distance from curr_x/y to ref_x/y < distance_limit, else return FALSE
	int pauta_outlier(string test, DWORD site, vector<double>& distri_vec, double value, DWORD sigma_n, double skip_lolim, double skip_hilim); // ¿≠“¿¥Ôoutlier return TRUE, not outlier return FALSE

public:
	Coutlier();
	~Coutlier(){}

	int clear();
	// in UserInit
	int init(string config_file, int sos_mode, string acco_file); // load config file, mode = SIMULATION if acco_file == ""
	// in test function
	int input_test_value(string param_str, double *result);
	// in SOS function
	int log_sos_param(short funcindex, string test); // unify format: test_SOS_FLAG(0,0), test_SOS_VALUE(raw_lolim,raw_hilim), test_SOS_L(raw_lolim,raw_hilim), test_SOS_H(raw_lolim,raw_hilim)
	int log_sos_param_all(short funcindex); // unify format: test_SOS_FLAG(0,0), test_SOS_VALUE(raw_lolim,raw_hilim), test_SOS_L(raw_lolim,raw_hilim), test_SOS_H(raw_lolim,raw_hilim)
	void update_test_result_flag();
	// in eot 
	int eot();
	// in sot 
	int sot();

	// for debug only
	int print(){}

private:
	double grubbs_table[101];

	Cmylib mylib;
	CSOS_output sos_database;
	CSOS_config sos_config;

	int x_corr[SITE_NUM];
	int y_corr[SITE_NUM];

	map<string, map<DWORD, double>> sos_low_limit;  // map<test,map<site,value>>
	map<string, map<DWORD, double>> sos_high_limit; // map<test,map<site,value>>
	map<string, map<DWORD, double>> sos_low_limit_old;  // map<test,map<site,value>>
	map<string, map<DWORD, double>> sos_high_limit_old; // map<test,map<site,value>>

	//DWORD sos_flag;
	map<string, map<DWORD, double>> sos_flag; //map<test,map<site,flag>>

	map<string, int> grubbs_init_flag; // map<test,flag>
	map<string, map<DWORD, double>> test_value; //map<test,map<site,value>>
	map<DWORD, int> bin_map; //map<site,bin>

	DWORD the_end;

	DWORD serial;

	CAccoCsvData acco_data; // for simulate from acco raw data
	int mode;

	map<string, double> sigma_all; // map<test, sigam>
	map<string, double> mean_all; // map<test, mean>
	map<string, DWORD> cnt_all; // map<test, cnt>

	string wafer_id;
	string wafer_id_old;
	DWORD wafer_no;
};