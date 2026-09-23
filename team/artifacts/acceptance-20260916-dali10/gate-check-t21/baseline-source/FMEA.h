/*****************************************************************************
*                                                                            *
*       Source title:   FMEA.h									           *
*                       (Universal functions for all SC test projects)       *
*         Written by:   Sky Fu                                                *
*        Description:			                                             *
*                                                                            *
*   Revision History:                                                        *
*                                                                            *
*     mm/dd/yy  r.rr  - Original coding.                                     *
*                                                                            *
*****************************************************************************/

/*
REVISION BLOCK:
-Rev. -- Date --------------------------------------------------
00   6/7/21  Initial.						Sky Fu

----------------------------------------------------------------
*/

#pragma once
#include <conio.h>
#include "stdafx.h"
#define MAX_SITES 32

class eFMEA {
public:
	eFMEA();
	~eFMEA();
	int sot();
	int eot();
	void fmea_checking(short func_index_fmea);
	void fmea_onfailsite();
	void FMEA_Site_Set(DWORD siteID);
	void force_item_fail(short func, int site);

	int fmea_sites;
	int force_failed_item;
	int reinitflag;
	int curr_site;
	int flag;
	int fmea_enable;

	int fmea_2_enable;

private:
	int valid_site[MAX_SITES];
	int fmea_items_count[MAX_SITES];
	int test_item_count;
	int test_max_site;//用于第二种方式时切换site
	int test_start_site;//用于第二种方式时切换site
	int eot_site_count;
	int site_switch_flag;//用于第二种方式时切换site

	short func_index_forcefail;//记录强制fail func
	int site_forcefail;//记录强制fail site
	int flag_forcefail;//记录强制fail flag

	string int2str(DWORD n);
	int TXT_OPEN_FLAG;
	short current_func[MAX_SITES];//记录当前运行到哪个func


};

