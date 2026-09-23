
/*============================================================================================================
*                                                                            Temperature AutoLoop Control Library                                                                                          *
*                                                                                                                                                                                                                                   *
*      This Temperaure autoloop library, which can realize one  time key kick to finish full condition (temperarure and vin point) loop operation.      *
*      It will auto measure the DUT temperature and compared with spec and acceptable variance, when temperaure hit set temp range , it will     *
*      start test automtically.                                                                                                                                                                                           *
*      This library support QT8100 Tester, MPI thermal stream and with commnucation solution of RS232                                                                 *
*      Before use this library, need to install NI 488.2/ NI MAX first                                                                                                                               *
*      Easy to add in your program, only need to set loop condition before loop operation.                                                                                          *
*                                                                                                                                                                                                                                   *
*                                                                                    Developed by Zhang Shuai                                                                                                    *
*                                                         Nuvolta Technology (Shanghai )Test Team,  Version 1.0, 2021/7/28, SH                                                         *
*                              With no permission, copy or share is forbiden.    Nuvolta Technology Corperation. All Rights Reserved.                                   *
=============================================================================================================*/

#include "stdafx.h"

#include<string>
#include<vector>
#include <atlstr.h>
#include< vector >
#include "src/visa.h"
#pragma comment(lib, "src/visa.lib")
#include<tchar.h>
#include<cmath>
#include "spec.h"

//#ifndef _MATRIX_H_
//#define _MATRIX_H_

#include <math.h>
#include <memory.h>
//#include <vector>
#include <algorithm>



using namespace std;
//#define MS_ALL -1
//#define MS_MAX_SITES 8
//#define  MAX_TRIM 256



// 使用long double 提高计算的精度
#if !defined (fraction)
typedef long double  fraction;
#endif



static int loop_ctrl_cnt = 0;
// 矩阵数据和增广列,如下所示
// |--------matrix-------|--augment--|----result----|
// |--2a + 3b + 11c + 5d =  2 -------|--1 0 0 0|-2--|
// |--1a +  b +  5c + 2d =  1 -------|--0 1 0 0| 0--|
// |--2a +  b +  3c + 2d = -3 -------|--0 0 1 0| 1--|
// |--1a +  b +  3c + 3d = -3 -------|--0 0 0 1|-1--|


extern SPEC spec;


// 设置文本颜色
void SetColorTC(int color);

// 重置文本颜色为默认值
void ResetColorTC();

class Thermal_stream
{
public:
	Thermal_stream();
	~Thermal_stream();
	void Initial();
	void tssot(int sotvalue);
	void tsinitbeforetest();
	void tseot();
	void tsfot();
	//--------------for thermal control, function definition
	void PrintCommState(DCB dcb);
	void PrintMessage(char *lpBuf, DWORD dwSize);
	BOOL WriteABuffer(char * lpBuf, DWORD dwToWrite, HANDLE hComm);
	DWORD Read(char * lpBuf, HANDLE hComm);
	BOOL SendCommand(HANDLE hCom, char * pcCmd, DWORD dwBytesToSend, BOOL bQueryCmd);
	BOOL SendCommand1(HANDLE hCom, char * pcCmd, DWORD dwBytesToSend, BOOL bQueryCmd, int *flag);
	int Thermal_Setup();
	int Thermal_End();
	double set_temp(int force_temp, int soak_time, bool fbd_stable_tmcnt_flag); // force temp and soak time setting function
	void temp_control();
	void mode_selection();
	void loop_cond_count(); // setup for default loop condition and selected loop condition
	int get_temp();
	double get_vin();

	double soak_temp_cal(int target_temp, double meas, bool enter_range_flag);
	int get_vin_seq();
	int get_temp_seq();
	int get_temp_meas_cnt();
	void temp_meas_cnt_accum();
	double get_temp_variance();
	int soak_temp_adjust_delay_time(double meas, int Ttarget, double previous_gap, int current_soak_cnt, int soak_cnt_set);
	double trim_modify_temp(double meas, int target, double previous_gap, int current_soak_cnt, int soak_cnt_set, double Tset_cal);
	int flow_flag[2];
	void set_abnormal_flag(bool value);
	void instruction();
	int rise_to_fall;
	//-----------------New temp char variables define
	void temp_loop_control();
	void temp_loop_control_study_mode();
	double soak_temp_value_calculate(int target_temp, double meas, bool enter_range_flag);
	double trim_tune_temp(double meas, int target, double previous_gap, int current_soak_cnt, int soak_cnt_set, double Tset_cal);
	bool system_oscllo_judge();

	void Temp_char_study_mode(std::ofstream *outfile, int target_set);

	void modifyLDF(const std::string& filePath, int newStopAfterRunValue);
	bool confirm_L_button_clicked();
private:
	//--------------for thermal control, variables definition
	DCB dcb;
	HANDLE hCom;
	BOOL fSuccess;
	TCHAR *pcCommPort; // default port is COM1, depends on which Port connected with Thermal stream
	char *pcCmd;  //PC command pointer for command address transimission

	//--------------------------------------------------loop function variables
	bool Thermal_Normal;
	bool Manual_mode;
	int TempLoopCount;
	CString *mL_tlp;        // define CString format loop temp point
	CString  *mL_vlp;      // define CString format loop vin point
	char** mc_tlp;            // define char* format loop vin point
	char**mc_vlp;            // define char* format loop vin point
	char **mc_vdd;//// define char* format loop vdd point
	int *mI_Ttarget;          // define int format loop temp target
	double *mD_Vtarget; // define double format loop vin target
	double *mD_Vddtarget;//  define double format loop vdd target
	CString Temp_sel[10];    //use selected temp loop value, CString format
	CString Vin_sel[10];        //use selected vin loop value,CString format
	int  Tsel_target[10];          // use selected temp loop value
	double Vsel1_target[10];   // user selected vin loop value
	double Vsel2_target[10];
	double Vsel3_target[10];
	double temp_variance;
	int soak_time_count;   //soak time count 
	int Tsoak_stable_time;  // first temp soak stable time count
	int Vsoak_stable_time;  // other vin point soak time count
	double temp_tolerance; // temperature tolerance 
	int Tsoak_t_1st;
	int Tsoak_t_nst;

	int sel_cnt_all;             // user selected temp * vin count 
	int set_tsize;               // user set  the loop temp count
	int set_vsize;               //  user set  the loop vin count
	int sel_tcnt;                  //  user selected  the loop temp count
	int sel_vcnt;                 // user selected the loop vin count

	int temp_seq;
	int vin_seq;
	int num_seq;

	int temp_index;
	int vin_index;
	map<int, int> temp_set_max_map;
	map<int, int> temp_set_min_map;
	bool study_mode;

	double temp_history[10];
	bool CHAR_LOOP;
	//int TempLoopCount  ;
	int char_flag;
	int t_cnt;
	int v_cnt;
	char al_flag;
	CString Temp_Reminder[20], Vin_Reminder[20];
	int temp_target[20];
	double vin_target[20];
	bool	soak_stable_flag;
	bool slow_soak;
	double Tcal_set;
	int soak_sec_cnt;
	int soak_time_all_cnt;
	int temp_meas_count;
	int enter_level1_cnt;// 累计第多少次进入第一等级温度范围
	int enter_level2_cnt;// 累计第多少次进入第二等级温度范围
	int range_status;//// 判断是否已经进入温度调节的范围
	int temp_est_gap[5];
	int force_temp;
	int single_cond_soak_time_cnt;
	bool stop_loop_flag;
	bool control_bit;
	bool abnormal_stop;// this flag show abnormal condition happens, user want to stop temp control loop, this flag will change to 1 when user click "E" button on keyboard, default value is 0;
	int init_ts_config_cnt;// use to define it is the first time enter user_init, if Yes, then assign loop voltage and current, if not, will execute nothing, default code is 0


	//-----------------New temp char variables define
	int Phase;// 定义芯片温度调控中的阶段
	int Tmax;// 定义每个target 温度对应的极限温度值，设置此温度长时间后会稳定在target值附近
	int Tmin;
	int History_Phase;
	int Tclamp;// Clamp温度值
	int time_cnt_phase3;
	int SOAK_TEMP;

	int phase_cnt1;
	int phase_cnt2;
	int phase_cnt3;

	int Tsetmax[10];//--------变量用来限定极限温度值
	int Soak_time_per_temp;//------单一温度点已经soaking的时间，如果过长需要判定原因


	bool  Soak_system_oscillo; //-----判定系统处于震荡期，温度在+1和-1 两次震荡调整

	int  Soak_temp_limit_too_high;//-------只用于低温，设置温度限制导致芯片达不到目标温度的情况下， 需要降低限值
	int Soak_temp_limit_too_low; //-------只用于高温，设置温度限制导致芯片达不到目标温度的情况下，需要提升限值

	double measure_10_temp_histroy[10];
	
	struct
	{
		bool enter_phase1;
		bool enter_phase2;
		bool enter_phase3;
		bool enter_phase4;
		bool enter_phase5;
		int phase_change_count;
		bool exit_phase1;
		bool exit_phase2;
		bool exit_phase3;
	}PRecord;


	struct PhaseRecord
	{
		int enter_phase_cnt;
		int  soak_time_count;
		int soak_clamp_cnt;
		double temp_his[6];
	};

	map <int, int> Retest_count;
	map<int, PhaseRecord> Phasemap;

	bool L_button_clicked;
};



extern double V_PS1_TYP;
extern double V_PS2_TYP;
extern double V_PS3_TYP;
extern double Temperature;

extern int TestTypeNumber;
extern CString Loop_temp[10];
extern CString Loop_vin[10];
extern char* LoopTemp[10];
extern char* LoopVin[10];
extern char* LoopVdd[10];
extern int  Temp_INT[10];
extern double Vin_DUB[10];
extern double Vdd_DUB[10];
extern double Temperature1;


extern int char_flag;
extern int t_cnt;
extern int v_cnt;
extern CString Temp_Reminder[20], Vin_Reminder[20];
extern int temp_target[20];
extern double vin_target[20];

static ViSession defaultRM;
static ViSession instr;
static ViStatus status;
static ViUInt32 retCount;
static ViUInt32 writeCount;
static unsigned char buffer[100];
static char stringinput[512];
static char resourcename[50];

#define READ_BUF_SIZE		60
#define WRITE_BUF_SIZE		60
#define READ_TIMEOUT		500      // milliseconds

extern Thermal_stream TS;

void temp_loop_setup(CString temp_lp[], CString  vin_lp[], char* templp[], char* vinlp[], int *Temp_target, double *Vin_target, int lpcnt);
void temp_control(CString temp_lp[], CString  vin_lp[], char* templp[], char* vinlp[], int Temp_target[], double Vin_target[], int lpcnt);
//void temp_control (CString temp_lp[], CString  vin_lp[], char* templp[], char* vinlp[], int Temp_target[], double Vin_target[], int lpcnt);
void Temp_selection(CString temp[], CString vin[], int tmp_max, int vin_max, int num, int *TEMP, double *VIN, bool en_tmp);
void Temp_measure(CString temp[], CString vin[], int *tmp_target, double *vin_target, int tmp_seq, int vin_seq, int ctrl_mod);
void SendCommandAndRead(ViBuf cmd);
void SendCommand(ViBuf cmd);
void WriteCommandAndRead(ViBuf cmd, BOOL isQuery);
void Thermal_setup();
void data_converter(char*tmp, int data);
double best_soak(int target_temp, double meas, double meas_pre);
//double soak_temp_cal(int target_temp);
void LogarithmTest();
int check_valid(int *array_in, int size_max, int input_val);
int check_valid(double *array_in, int size_max, double input_val);
void LogarithmTest(double temp[], double *a_ptr, double *b_ptr, double *c_ptr);
double temp_meas(/*ACM200 acm_res, */int set_tmp_val, int soak_time_left, bool soak_stable_flag, int set_loop_flag, bool fbd_stable_tmcnt_flag);
//double temp_meas(FOVIe fovi_res, int set_tmp_val, int soak_time_left, bool soak_stable_flag, int set_loop_flag, bool fbd_stable_tmcnt_flag);
//double temp_meas(FXVIe_PLUS fxvi_plus, int set_tmp_val, int soak_time_left, bool soak_stable_flag, int set_loop_flag, bool fbd_stable_tmcnt_flag);
//double temp_meas(FPVIe fpvi, int set_tmp_val, int soak_time_left, bool soak_stable_flag, int set_loop_flag, bool fbd_stable_tmcnt_flag);
//double temp_meas(ACM acm_res, int set_tmp_val, int soak_time_left, bool soak_stable_flag, int set_loop_flag, bool fbd_stable_tmcnt_flag);

string convertToString(double value, int precision);
int extractNumberAfterEquals(const std::string& str);
void splitString(const std::string& string1, std::string& string2, std::string& string3);
int getnumberfromstring(string *input_str);