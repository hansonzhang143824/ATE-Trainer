/*****************************************************************************
*                                                                            *
*       Source title:   BoardCheck.h                                         *
*                       (board checker for AccoTest programs)                *
*         Written by:						                                 *
*        Description:					                                     *
*                                                                            *
*   Revision History:                                                        *
*                                                                            *
*     mm/dd/yy  r.rr  - Original coding.                                     *
*                                                                            *
*****************************************************************************/

/*
REVISION BLOCK:
-Rev. -- Date -------------------------------------------------------------------------------
1  12/24/20   upgrade to 8300
----------------------------------------------------------------------------------------------
*/


#pragma once
#include "stdafx.h"
#include <map>
#include <vector>
#include <string>
#include <Windows.h>
#include <iostream>
#include <type_traits> // 用于类型特征识别

using namespace std;

#define BTN_REDO 2000
#define BTN_EXIT 2001
#define BTN_NONE 2002
#define BTN_CANCEL 2003


struct MyData {
	bool check_status;
	double  test_data;
	double  high_limit;
	double  low_limit;
	string unit;
	string flag;
};

// 用于存储键值对的结构体
struct KeyValuePair {
	string key;
	MyData value;

	KeyValuePair(const string& k, const MyData& v) : key(k), value(v) {}
};

enum PULLUP_FLAG
{
	PULL_UP,
	PULL_DOWN
};

//class CBIT_LIB
//{
//
//public:
//	void create_data_block(string str_1, ...);
//	void updateBoardCheckResults(string  str_input, bool *chk_status, double *test_value);
//	void set_data_after_boardcheck(double *test_value, double hlimit, double llimit, bool *check_stat);
//private:
//	map<string, MyData>m_boardcheck_results[SITE_NUM];
//	double m_test_value[SITE_NUM];
//	double m_hlimit;
//	double m_llimit;
//	double m_check_stat[SITE_NUM];
//};



class DialogTemplate;

class DialogTemplate
{
public:
	DialogTemplate(LPCSTR caption, DWORD style);

	DialogTemplate(LPCSTR caption, DWORD style, int x, int y, int w, int h,
		LPCSTR font = NULL, WORD fontSize = 8);
	void AddComponent(LPCSTR type, LPCSTR caption, DWORD style, DWORD exStyle,
		int x, int y, int w, int h, WORD id);
	void AddButton(LPCSTR caption, DWORD style, DWORD exStyle, int x, int y,
		int w, int h, WORD id);
	void AddEditBox(LPCSTR caption, DWORD style, DWORD exStyle, int x, int y,
		int w, int h, WORD id);
	void AddStatic(LPCSTR caption, DWORD style, DWORD exStyle, int x, int y,
		int w, int h, WORD id);
	void AddListBox(LPCSTR caption, DWORD style, DWORD exStyle, int x, int y,
		int w, int h, WORD id);
	void AddScrollBar(LPCSTR caption, DWORD style, DWORD exStyle, int x, int y,
		int w, int h, WORD id);
	void AddComboBox(LPCSTR caption, DWORD style, DWORD exStyle, int x, int y,
		int w, int h, WORD id);
	operator const DLGTEMPLATE*() const;
	virtual ~DialogTemplate();

protected:
	// Prevent copying and assignments (by private definition)
	DialogTemplate operator=(const DialogTemplate &x) { return *this; }
	DialogTemplate(DialogTemplate &x) {}

	void AddStandardComponent(WORD type, LPCSTR caption, DWORD style,
		DWORD exStyle, int x, int y, int w, int h, WORD id);
	void AlignData(int size);
	void AppendString(LPCSTR string);
	void AppendData(void* data, int dataLength);
	void EnsureSpace(int length);

private:

	DLGTEMPLATE* dialogTemplate;
	int totalBufferLength;
	int usedBufferLength;

};


////////////////
//
// Base classes For Windows interface
//
////////////////
class BoardCheckElement
{
public:
	virtual ~BoardCheckElement() {};
	virtual void get(HWND hDlg) = 0;
	virtual void set(HWND hDlg) = 0;
	virtual void dlg_file(HWND hDlg, char *fname, int len) = 0;
	virtual int width() = 0;
	virtual int height() = 0;
	virtual void create_dialog(DialogTemplate *dialog, int x, int y, int *newid) = 0;
	virtual void command(HWND hDlg, int code, int target_id) {};
	int id;
	static int tagged_filename;     // Allow tags names in file name components
};
typedef BoardCheckElement *LPBoardCheckElement;


class BoardCheckButton : public BoardCheckElement
{
public:
	BoardCheckButton(char *aname, int aid, int def_style = BS_PUSHBUTTON);
	virtual ~BoardCheckButton();
	virtual int width();
	virtual int height();
	virtual void get(HWND hDlg) {};
	virtual void set(HWND hDlg) {};
	virtual void dlg_file(HWND hDlg, char *fname, int len) {};
	virtual void create_dialog(DialogTemplate *dialog, int x, int y, int *newid);
protected:
	// Prevent copying and assignments (by private definition)
	BoardCheckButton operator=(const BoardCheckButton &x) { return *this; }
	BoardCheckButton(BoardCheckButton &x) {}
	char *name;
	int style;
};


class BoardCheckListBox : public BoardCheckElement
{
public:
	BoardCheckListBox(char *aname, int aid, int def_style = LBS_NOTIFY | WS_VSCROLL | WS_BORDER);
	virtual ~BoardCheckListBox();
	virtual int width();
	virtual int height();
	virtual void get(HWND hDlg) {};
	virtual void set(HWND hDlg) {};
	virtual void dlg_file(HWND hDlg, char *fname, int len) {};
	virtual void create_dialog(DialogTemplate *dialog, int x, int y, int *newid);
	//virtual void command(HWND hDlg,int code,int target_id);
protected:
	// Prevent copying and assignments (by private definition)
	BoardCheckListBox operator=(const BoardCheckListBox &x) { return *this; }
	BoardCheckListBox(BoardCheckListBox &x) {}
	char *name;
	int style;
};

class BoardCheckGroup : public BoardCheckElement
{
public:
	BoardCheckGroup(int vertical, int aospace, int aispace);
	virtual ~BoardCheckGroup();
	void add(BoardCheckElement *el);
	virtual int width();
	virtual int height();
	virtual void get(HWND hDlg);
	virtual void set(HWND hDlg);
	virtual void dlg_file(HWND hDlg, char *fname, int len);
	virtual void create_dialog(DialogTemplate *dialog, int x, int y, int *newid);
	virtual void command(HWND hDlg, int code, int target_id);
	int count();
protected:
	// Prevent copying and assignments (by private definition)
	BoardCheckGroup operator=(const BoardCheckGroup &x) { return *this; }
	BoardCheckGroup(BoardCheckGroup &x) {}
	int is_vertical;
	int no;
	int ospace;     // outer space (space to other elements)
	int ispace;     // inner space (space between elements)
	LPBoardCheckElement *member;
};


class CBC_log
{
public:
	CBC_log(void) {}
	~CBC_log(void) {}
	void clear(void) {
		component_vec.clear();
		tnum_map.clear();
		lolim_map.clear();
		hilim_map.clear();
		unit_map.clear();
		data_map.clear();
		flag_map.clear();
	}

	vector<string> component_vec;
	map<string, DWORD> tnum_map;				// map<component, test_number>
	map<string, double> lolim_map;				// map<component, low_lim>
	map<string, double> hilim_map;				// map<component, high_lim>
	map<string, string> unit_map;				// map<component, unit>
	map<string, map<DWORD, double>> data_map;	// map<component, map<site, data>>
	map<string, map<DWORD, string>> flag_map;	// map<component, map<site, pass or fail>>
};

class Cvi_config
{
public:
	Cvi_config(){
		mode = FV;
		v = 3;
		i = 0;
		fxv_range = FXVIe_PLUS_10V;
		fxi_range = FXVIe_PLUS_10MA;
		v_range = FOVIe_10V;
		i_range = FOVIe_10MA;
		miGain = FOVIe_MI_X1;
		acm_v_range = ACM_N2P18V;
		acm_i_range = ACM_2MA;
		acm200_v_range = ACM200_10V;
		acm200_i_range = ACM200_10MA;
		fpvi_v_range = FPVIe_5V;
		fpvi_i_range = FPVIe_10MA;
		i_range = FOVIe_10MA;
		delay = 10; // ms
		sample_times = 100;
		sample_period = 10;	// us
	}

	void init(void){
		mode = FV;
		v = 3;
		i = 0;
		fxv_range = FXVIe_PLUS_10V;
		fxi_range = FXVIe_PLUS_10MA;
		v_range = FOVIe_10V;
		i_range = FOVIe_10MA;
		miGain = FOVIe_MI_X1;
		acm_v_range = ACM_N2P18V;
		acm_i_range = ACM_200UA;
		delay = 10; // ms
		sample_times = 100;
		sample_period = 10;	// us	
	}
	void fovi_set(int mode_val = FV, double v_val = 3, double i_val = 0, FOVIe_VRNG v_range_val = FOVIe_10V, FOVIe_IRNG i_range_val = FOVIe_10MA, int delay_val = 10, int sample_times_val = 100, int sample_period_val = 10){
		mode = mode_val;
		v = v_val;
		i = i_val;
		v_range = v_range_val;
		i_range = i_range_val;
		delay = delay_val;
		sample_times = sample_times_val;
		sample_period = sample_period_val;
	}

	void fxvi_plus_set(int mode_val = FV, double v_val = 3, double i_val = 0, FXVIe_PLUS_VRNG v_range_val = FXVIe_PLUS_10V, FXVIe_PLUS_IRNG i_range_val = FXVIe_PLUS_10MA, int delay_val = 10, int sample_times_val = 100, int sample_period_val = 10){
		mode = mode_val;
		v = v_val;
		i = i_val;
		fxv_range = v_range_val;
		fxi_range = i_range_val;
		delay = delay_val;
		sample_times = sample_times_val;
		sample_period = sample_period_val;
	}
	void acm_set(int mode_val = FV, double v_val = 3, double i_val = 0, ACM_VRNG v_range_val = ACM_N2P18V, ACM_IRNG i_range_val = ACM_200UA, int delay_val = 10, int sample_times_val = 100, int sample_period_val = 10){
		mode = mode_val;
		v = v_val;
		i = i_val;
		acm_v_range = v_range_val;
		acm_i_range = i_range_val;
		delay = delay_val;
		sample_times = sample_times_val;
		sample_period = sample_period_val;
	}

	void acm200_set(int mode_val = FV, double v_val = 3, double i_val = 0, ACM200_VRNG v_range_val = ACM200_10V, ACM200_IRNG i_range_val = ACM200_10MA, int delay_val = 10, int sample_times_val = 100, int sample_period_val = 10){
		mode = mode_val;
		v = v_val;
		i = i_val;
		acm200_v_range = v_range_val;
		acm200_i_range = i_range_val;
		delay = delay_val;
		sample_times = sample_times_val;
		sample_period = sample_period_val;
	}
	~Cvi_config() {}

	int mode;
	double v;
	double i;
	FXVIe_PLUS_VRNG fxv_range;
	FXVIe_PLUS_IRNG fxi_range;
	FXVIe_PLUS_MI_GAIN fxmiGain;

	FOVIe_VRNG v_range;
	FOVIe_IRNG i_range;
	FOVIe_MI_GAIN miGain;
	ACM_VRNG acm_v_range;
	ACM_IRNG acm_i_range;
	ACM200_VRNG acm200_v_range;
	ACM200_IRNG acm200_i_range;
	FPVIe_VRNG fpvi_v_range;
	FPVIe_IRNG fpvi_i_range;

	int delay;
	int sample_times;
	int sample_period;
};


class BoardCheck
{
public:
	BoardCheck();
	~BoardCheck();
	void Sot();
	friend BOOL CALLBACK  BoardCheckDialogProc(HWND hDlg, UINT iMsg, WPARAM wParam, LPARAM lParam);

	FOVIe_VRNG get_fovi_v_range(double v){
		if (v < 0)
			v = -v;
		if (v <= 1)
			return FOVIe_1V;
		if (v <= 2)
			return FOVIe_2V;
		else if (v <= 5)
			return FOVIe_10V;
		else if (v <= 10)
			return FOVIe_10V;
		else if (v <= 20)
			return FOVIe_20V;
		else if (v <= 40)
			return FOVIe_40V;
		else
			return FOVIe_10V;
	}

	FXVIe_PLUS_VRNG get_fxvi_plus_v_range(double v){
		if (v < 0)
			v = -v;
		if (v <= 2)
			return FXVIe_PLUS_3p6V;
		else if (v <= 10)
			return FXVIe_PLUS_10V;
		else if (v <= 20)
			return FXVIe_PLUS_20V;
		else if (v <= 40)
			return FXVIe_PLUS_40V;
		else
			return FXVIe_PLUS_10V;
	}


	ACM200_VRNG get_acm200_v_range(double v){
		if (v < 0)
			v = -v;
		if (v <= 2)
			return ACM200_3p6V;
		if (v <= 10)
			return ACM200_10V;
		else if (v <= 20)
			return ACM200_20V;
		else if (v <= 40)
			return ACM200_40V;
		else
			return ACM200_10V;
	}

	FPVIe_VRNG get_fpvi_v_range(double v){
		if (v < 0)
			v = -v;
		if (v <= 0.1)
			return FPVIe_100MV;
		if (v <= 1)
			return FPVIe_1V;
		else if (v <= 2)
			return FPVIe_2V;
		else if (v <= 5)
			return FPVIe_5V;
		else if (v <= 10)
			return FPVIe_10V;
		else if (v <= 20)
			return FPVIe_20V;
		else if (v <= 40)
			return FPVIe_40V;
		else if (v <= 100)
			return FPVIe_100V;
		else
			return FPVIe_1V;
	}
	FOVIe_IRNG get_fovi_i_range(double i){
		if (i < 0)
			i = -i;
		if (i <= 10e-6)
			return FOVIe_10UA;
		else if (i <= 100e-6)
			return FOVIe_100UA;
		else if (i <= 1e-3)
			return FOVIe_1MA;
		else if (i <= 10e-3)
			return FOVIe_10MA;
		else if (i <= 100e-3)
			return FOVIe_100MA;
		else if (i <= 1)
			return FOVIe_1A;
		else
			return FOVIe_1MA;
	}

	FXVIe_PLUS_IRNG get_fxvi_plus_i_range(double i){
		if (i < 0)
			i = -i;
		if (i <= 10e-6)
			return FXVIe_PLUS_10UA;
		else if (i <= 100e-6)
			return FXVIe_PLUS_100UA;
		else if (i <= 1e-3)
			return FXVIe_PLUS_1MA;
		else if (i <= 10e-3)
			return FXVIe_PLUS_10MA;
		else if (i <= 100e-3)
			return FXVIe_PLUS_100MA;
		else if (i <= 1)
			return FXVIe_PLUS_1A;
		else
			return FXVIe_PLUS_1MA;
	}


	ACM_IRNG get_acm_i_range(double i){
		if (i < 0)
			i = -i;
		if (i <= 5e-6)
			return ACM_5UA;
		else if (i <= 20e-6)
			return ACM_20UA;
		else if (i <= 200e-6)
			return ACM_200UA;
		else if (i <= 2e-3)
			return ACM_2MA;
		else if (i <= 20e-3)
			return ACM_20MA;
		else if (i <= 200e-3)
			return ACM_200MA;
		else if (i <= 0.5)
			return ACM_500MA;
		else
			return ACM_2MA;
	}
	ACM200_IRNG get_acm200_i_range(double i){
		if (i < 0)
			i = -i;
		if (i <= 10e-6)
			return ACM200_10UA;
		else if (i <= 100e-6)
			return ACM200_100UA;
		else if (i <= 1e-3)
			return ACM200_1MA;
		else if (i <= 10e-3)
			return ACM200_10MA;
		else if (i <= 100e-3)
			return ACM200_100MA;
		else if (i <= 200e-3)
			return ACM200_200MA;
		else
			return ACM200_1MA;
	}

	PPMUIRange get_dcm_i_range(double i){
		if (i < 0)
			i = -i;
		if (i <= 2e-6)
			return DCM_PPMUIRANGE_2UA;
		else if (i <= 20e-6)
			return DCM_PPMUIRANGE_20UA;
		else if (i <= 200e-6)
			return DCM_PPMUIRANGE_200UA;
		else if (i <= 2e-3)
			return DCM_PPMUIRANGE_2MA;
		else if (i <= 32e-3)
			return DCM_PPMUIRANGE_32MA;
		else
			return DCM_PPMUIRANGE_2MA;
	}
	FPVIe_IRNG get_fpvi_i_range(double i){
		if (i < 0)
			i = -i;
		if (i <= 10e-6)
			return FPVIe_10UA;
		else if (i <= 100e-6)
			return FPVIe_100UA;
		else if (i <= 1e-3)
			return FPVIe_1MA;
		else if (i <= 10e-3)
			return FPVIe_10MA;
		else if (i <= 100e-3)
			return FPVIe_100MA;
		else if (i <= 1)
			return FPVIe_1A;
		else if (i <= 2)
			return FPVIe_2A;
		else if (i <= 10)
			return FPVIe_10A;
		else
			return FPVIe_1MA;
	}


	void SetSiteConnected(int site, BOOL value) { site_connected[site] = value; }
	BOOL GetSiteConnected(int site) { return site_connected[site]; }
	BOOL IsNoSiteConnected(void) { for (int site = 0; site<SITE_NUM; ++site) if (site_connected[site]) return FALSE; return TRUE; }
	void ClearSiteConnected(void) { for (int site = 0; site<SITE_NUM; ++site) site_connected[site] = 0; }
	BOOL IsCheckPass(void);
	int get_nBtn(void) { return nBtn; }
	void Display(void);
	BOOL output_format(void);
	BOOL report(void);
	BOOL Board_ID_Check(const char* boardName, const char* rev, const char* SCLChannel, const char* SDAChannel);
	BOOL Board_ID_Write(const char* boardName, const char* rev, const char* number, const char* SCLChannel, const char* SDAChannel);
	BOOL Board_ID_Read(string* boardName, string* rev, string* number, const char* SCLChannel, const char* SDAChannel);


	//****************************************define component测试方法*****************************************//

	//**********************************1.CAP *************************//
	// use awg method to test cap with fovi/fpvi/acm
	//BOOL test_cap(FOVIe &fovi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//BOOL test_cap(ACM &acm_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//BOOL test_cap(FPVIe &fpvi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	// not use awg to test cap with fovi/fpvi/acm

	//对地电容
	//【FOVI源】
	BOOL test_cap_to_gnd(FOVIe &fovi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FXVIe_PLUS源】
	BOOL test_cap_to_gnd(FXVIe_PLUS &fovi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FPVI源】
	BOOL test_cap_to_gnd(FPVIe &fpvi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM源】
	BOOL test_cap_to_gnd(ACM &acm_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM200源】
	BOOL test_cap_to_gnd(ACM200 &acm_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);


	//源-源之间的电容
	//【ACM-ACM】
	BOOL test_cap_between_pin(ACM &acm_res1, ACM &acm_res2, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM-FOVI】
	BOOL test_cap_between_pin(ACM &acm_res, FOVIe &fovi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM-FXVIe_PLUS】
	BOOL test_cap_between_pin(ACM &acm_res, FXVIe_PLUS &fovi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM200-ACM200】
	BOOL test_cap_between_pin(ACM200 &acm_res1, ACM200 &acm_res2, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM200-FOVI】
	BOOL test_cap_between_pin(ACM200 &acm_res, FOVIe &fovi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM200-FXVIe_PLUS】
	BOOL test_cap_between_pin(ACM200 &acm_res, FXVIe_PLUS &fovi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//**********************************1.CAP *************************//

	//**********************************2.RES *************************//
	//对地电阻：pull_flag=0,上拉电阻pull_flag=1;
	//【ACM源】
	BOOL test_r(PULLUP_FLAG flag, ACM &acm_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM200源】
	BOOL test_r(PULLUP_FLAG flag, ACM200 &acm_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FOVI源】
	BOOL test_r(PULLUP_FLAG flag, FOVIe &fovi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FXVI_PLUS源】
	BOOL test_r(PULLUP_FLAG flag, FXVIe_PLUS &fovi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FPVI源】
	BOOL test_r(PULLUP_FLAG flag, FPVIe &fpvi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【DCM源】
	BOOL test_r(PULLUP_FLAG flag, const char* lpszGroupPinName, const char* lpszPinName, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//源-源电阻
	//【ACM源-ACM源】(res2给0,变成对地电阻)
	BOOL test_r(ACM &acm_res1, ACM &acm_res2, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	//【ACM200源-ACM200源】(res2给0,变成对地电阻)
	BOOL test_r(ACM200 &acm_res1, ACM200 &acm_res2, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//**********************************2.RES *************************//

	//**********************************3.Relay:Check 电压*************************//
	//***************单个源对地/固定源(VI源)
	//【ACM源】
	BOOL test_relay(ACM &acm_res, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM200源】
	BOOL test_relay(ACM200 &acm_res, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FOVI源】
	BOOL test_relay(FOVIe &fovi_res, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FXVI_PLUS源】
	BOOL test_relay(FXVIe_PLUS &fovi_res, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FPVI源】
	BOOL test_relay(FPVIe &fpvi_res, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	//***************两个源之间check(VI源）
	//【ACM-ACM源 ACM force, ACM measure】
	BOOL test_relay(ACM &acm_force, ACM &acm_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM200-ACM200源 ACM force, ACM measure】
	BOOL test_relay(ACM200 &acm_force, ACM200 &acm_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	//【ACM-FOVI源 ACM force, FOVI measure】
	BOOL test_relay(ACM &acm_force, FOVIe &fovi_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM-FXVIe_PLUS源 ACM force, FXVIe_PLUS measure】
	BOOL test_relay(ACM &acm_force, FXVIe_PLUS &fovi_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);


	//【ACM200-FOVI源 ACM200 force, FOVI measure】
	BOOL test_relay(ACM200 &acm_force, FOVIe &fovi_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM200-FXVIe_PLUS源 ACM200 force, FXVIe_PLUS measure】
	BOOL test_relay(ACM200 &acm_force, FXVIe_PLUS &fovi_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);


	//【ACM-FPVI源 ACM force, FPVI measure】
	BOOL test_relay(ACM &acm_force, FPVIe &fpvi_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM200-FPVI源 ACM force, FPVI measure】
	BOOL test_relay(ACM200 &acm_force, FPVIe &fpvi_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	//【FOVI-FOVI源 FOVI force,FOVI measure】
	BOOL test_relay(FOVIe &fovi_force, FOVIe &fovi_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FXVIe_PLUS-FXVIe_PLUS源 FXVIe_PLUS force,FXVIe_PLUS measure】
	BOOL test_relay(FXVIe_PLUS &fovi_force, FXVIe_PLUS &fovi_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);


	//【FOVI-FPVI源 FOVI force,FPVI measure】
	BOOL test_relay(FOVIe &fovi_force, FPVIe &fpvi_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FXVIe_PLUS-FPVI源 FOVI force,FPVI measure】
	BOOL test_relay(FXVIe_PLUS &fovi_force, FPVIe &fpvi_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	//【FPVI-FPVI源 FPVI force,FPVI measure】
	BOOL test_relay(FPVIe &fpvi_force, FPVIe &fpvi_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	 
	//***************两个源之间check(VI-DCM源）
	//【ACM-DCM源 DCM force，ACM measure】
	BOOL test_relay(ACM &acm_measure, const char* lpszGroupPinName, const char* lpszPinName, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM200-DCM源 DCM force，ACM measure】
	BOOL test_relay(ACM200 &acm_measure, const char* lpszGroupPinName, const char* lpszPinName, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FOVI-DCM源 DCM force，FOVI measure】
	BOOL test_relay(FOVIe &fovi_measure, const char* lpszGroupPinName, const char* lpszPinName, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FXVIe_PLUS-DCM源 DCM force，FOVI measure】
	BOOL test_relay(FXVIe_PLUS &fovi_measure, const char* lpszGroupPinName, const char* lpszPinName, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	
	//【FPVI-DCM源 DCM force，FPVI measure】
	BOOL test_relay(FPVIe &fpvi_measure, const char* lpszGroupPinName, const char* lpszPinName, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	//***************两个源之间check(VI-QVM源）
	//【ACM-QVM源 ACM force，QVM measure】
	BOOL test_relay(ACM &acm_force, QVMe &qvm_res, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1, int grp_no);
	//【ACM200-QVM源 ACM force，QVM measure】
	BOOL test_relay(ACM200 &acm_force, QVMe &qvm_res, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1, int grp_no);
	//【FOVI-QVM源 FOVI force QVM measure】
	BOOL test_relay(FOVIe &fovi_force, QVMe &qvm_res, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1, int grp_no);
	//【FXVIe_PLUS-QVM源 FOVI force QVM measure】
	BOOL test_relay(FXVIe_PLUS &fovi_force, QVMe &qvm_res, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1, int grp_no);

	
	//【FPVI-QVM源 FPVI force，QVM measure】
	BOOL test_relay(FPVIe &fpvi_force, QVMe &qvm_res, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1, int grp_no);

	//***************两个源之间check(VI-QTMU源）
	//【ACM-QTMU源 ACM force，QTMU measure】
	BOOL test_qtmu(ACM &acm_res, QTMUe &qtmu, QTMUe_SOURCE_AB source, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1, int grp_no);
	//【ACM200-QTMU源 ACM force，QTMU measure】
	BOOL test_qtmu(ACM200 &acm_res, QTMUe &qtmu, QTMUe_SOURCE_AB source, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1, int grp_no);
	//【FOVI-QTMU源 FOVI force QTMU measure】
	BOOL test_qtmu(FOVIe &fovi_res, QTMUe &qtmu, QTMUe_SOURCE_AB source, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1, int grp_no);

	//【FXVIe_PLUS-QTMU源 FOVI force QTMU measure】
	BOOL test_qtmu(FXVIe_PLUS &fovi_res, QTMUe &qtmu, QTMUe_SOURCE_AB source, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1, int grp_no);


	//【FPVI-QTMU源 FPVI force，QTMU measure】
	BOOL test_qtmu(FPVIe &fpvi_res, QTMUe &qtmu, QTMUe_SOURCE_AB source, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1, int grp_no);

	//***************三个源之间check
	//【ACM-ACM-FPVI源】
	BOOL test_relay(ACM &acm_res1, ACM &acm_res2, FPVIe &fpvi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【ACM200-ACM200-FPVI源】
	BOOL test_relay(ACM200 &acm_res1, ACM200 &acm_res2, FPVIe &fpvi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FOVI-FOVI-FPVI源】
	BOOL test_relay(FOVIe &fovi_res1, FOVIe &fovi_res2, FPVIe &fpvi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【FXVIe_PLUS-FOVIeI源】
	BOOL BoardCheck::test_relay(FXVIe_PLUS &fovi_force, FOVIe &fovi_measure, Cvi_config &vi, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1);

	//【FXVIe_PLUS-FXVIe_PLUS-FPVI源】
	BOOL test_relay(FXVIe_PLUS &fovi_res1, FXVIe_PLUS &fovi_res2, FPVIe &fpvi_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	//【ACM-ACM-QVM源】1大电压
	BOOL test_relay(ACM &acm_res1, ACM &acm_res2, QVMe &qvm_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1, int grp_no);
	//【ACM-ACM-QVM源】2小电压
	BOOL test_relay_qvm2(ACM &acm_res1, ACM &acm_res2, QVMe &qvm_res, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1, int grp_no);

	//**********************************3.Relay:Check 电压*************************//

	// only measure
	//【量电压】fovi量电压
	BOOL test_v(FOVIe &fovie_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	//【量电压】FXVIe_PLUS量电压
	BOOL test_v(FXVIe_PLUS &fovie_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	//【量电压】fpvi量电压
	BOOL test_v(FPVIe &fpvie_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【量电压】ACM量电压
	BOOL test_v(ACM &acm_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【量电压】ACM量电压
	BOOL test_v(ACM200 &acm_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	BOOL test_r_small(FPVIe &fpvie_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	BOOL test_r_middle(FPVIe &fpvie_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1=NULL);

	BOOL test_r_kelvin(FPVIe &fpvie_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);
	//【量电压】ACM量电压
	BOOL test_v_p2p(ACM200 &acm_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	BOOL test_v_p2p(FOVIe &fovie_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	BOOL test_v_p2p(FXVIe_PLUS &fovie_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	BOOL test_kelvin(ACM200 &acm_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	BOOL test_kelvin_ohm(FPVIe &fpvie_meas, DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	BOOL log(DWORD tnum, const char* component, double* result, double lolim, double hilim, const char* unit);
	BOOL test_log(DWORD tnum, const char* component, double lolim, double hilim, const char* unit, double *result1 = NULL);

	void create_data_block(string str_1, ...);
	void updateBoardCheckResults(string  str_input, string unit_input);
	void set_data_after_boardcheck(double *test_value, double hlimit, double llimit);
	bool check_results_summary();
	void SetConsoleTextSize(int fontSize);
private:
	// Prevent copying and assignments (by private definition)
	BoardCheck operator=(const BoardCheck &x) { return *this; }
	BoardCheck(BoardCheck &x) {}
	void create_input(void);
	void delete_input(void);
	BoardCheckGroup *input;
	BoardCheckGroup *buttons;    // deleted with input
	BoardCheckGroup *listbox;    // deleted with input

	DialogTemplate *dialog;
	CBC_log bc_log;
	vector<string> display_vec;
	//int nMaxExtent;
	BOOL CheckPass;				// result of all site
	BOOL check_result[SITE_NUM];// result of each site
	int nBtn;
	BOOL site_connected[SITE_NUM];


	// 成员变量定义（已修改为 vector 模式）
	vector<vector<KeyValuePair>> M_boardcheck_results;

	map<string, MyData>m_boardcheck_results[SITE_NUM];
	double m_test_value[SITE_NUM];
	double m_hlimit;
	double m_llimit;
	bool m_check_stat[SITE_NUM];

};


