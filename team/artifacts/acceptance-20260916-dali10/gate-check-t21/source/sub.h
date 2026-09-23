//#ifndef __MAX_SAMPLES
#define __MAX_SAMPLES 4096
//#endif
#include "StdAfx.h"
#include"treg.h"

extern int SiteSelected[SITE_NUM];
extern float Period;
extern int GRP_CNT;
extern int TEST_FLOW;

extern int BURN_FLAG[SITE_NUM];

extern double avss_tsbat[SITE_NUM];
extern double IBUS_SNS_Gain[SITE_NUM];
extern double BUCK_IBAT_HS_Gain[SITE_NUM];
extern double BUCK_IBAT_LS_Gain[SITE_NUM];
extern double BOOST_IBAT_HS_Gain[SITE_NUM];
extern double BOOST_IBAT_LS_Gain[SITE_NUM];
extern double Iscale_buck[SITE_NUM];
extern double Iscale_boost[SITE_NUM];
extern double Vclamp_high_buck[SITE_NUM];
extern double Vclamp_high_boost[SITE_NUM];
extern double Buck_lsfet_zcd[SITE_NUM];
extern double Boost_hsfet_zcd[SITE_NUM];
extern double BU_zcd_in_BO_Rcs_Mode[SITE_NUM];
extern double BO_zcd_in_BU_Rcs_Mode[SITE_NUM];
extern double Ibus_loop_Voffset_2A[SITE_NUM];

extern double IBUS_EA_BASE[SITE_NUM];
extern string DEVICE_SEL;
extern bool Relay_Off_Check;
enum REMEASURE_CURR_UNIT {
	MEAS_A,  // 0 = measure unit is A
	MEAS_MA, // 1 = measure unit is mA 
	MEAS_UA,     // 2 =measure unit is uA
	MEAS_NA, // 3 =  measure unit is nA
};

enum REMEASURE_VOL_UNIT {
	MEAS_V,  // 0 = measure unit is V
	MEAS_MV, // 1 = measure unit is mV 
};

//-------------------------QVM  GROUP MEASUREMENT
void QVM_GRP_MEASURE(double *qvm_results, int grp_no);

//-------------------------QTMU  GROUP MEASUREMENT
void QTMU_GRP_MEASURE(double *qtmu_results, int grp_no);
//inline int MsSiteStat(int treg_site)
//{
//	BYTE treg_stat[SITE_NUM] = { 0 };
//	int a;
//	a = STSGetSiteStatus(treg_stat, SITE_NUM);
//	return (int)treg_stat[treg_site];
//}
//#define FOR_EACH_VALID_SITE(site) for (int site = 0; site < SITE_NUM; site++) if (MsSiteStat(site))
//#include "awg.h"
BOOL set_mos_relay_on(int mos_no, int gp_no);
//BOOL set_mos_relay_on_rdson(int mos_no, int gp_no);
//BOOL set_mos_relay_on_rdson_sw(int mos_no, int gp_no);
BOOL EEPROM_Read(int bank, int* EE_READ, double* EE_IQ);
void power_down(bool debug = true);
void iic_read_adc(int adrr1, int adrr2, int* data);
void power_off(bool debug = true);
void I2CSetup(bool debug = true);
void I2CWriteData(unsigned int dev_addr, unsigned int reg_addr, int data = 0);
void iic_read(unsigned addr, int *rdata);
bool WRITE_AMBA(unsigned long address, int data4, int data3, int data2, int data1);//Different site write same data
BOOL iic_read(int addr_dev, int addr_reg, int *data);
BOOL iic_read_adc(int addr, int *data);
int awg_load_pattern(char* awg_name, FPVIe fpvi_list[], VIMode viMode, FPVIe_VRNG v_range, FPVIe_IRNG i_range, double start_point, double stop_point, double step);
BOOL fpvi_gp_valid(int gp_no = 0);
void iic_read_adc(int adrr1, int adrr2, int *data);
void power_cool(bool debug);


BOOL TRIMBANK_Burn(bool burn_flag[SITE_NUM]);

//*************trim
void EEPROM_Preview();
BOOL EEPROM_Enter_Test_Mode(int mux, int tm_data0, int tm_data1);
void measure_BG(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
int find_R(double* dataall, int starpoint, int stoppoint, double trigvalue, int site);
int find_F(double* dataall, int starpoint, int stoppoint, double trigvalue, int site);

void I2CWriteSameData(BYTE slaveaddr, DWORD regaddr,DWORD writesamedata);
void I2CWriteSameData(BYTE slaveaddr, DWORD regaddr, int length, DWORD writesamedata);
void I2C_READ_BYTE(BYTE slaveaddr, DWORD regaddr, ULONG pdata[SITE_NUM]);
void entertestmode();
void Set_I2C();

//void QTMU_GP_MEASURE(double *qvm_results, int grp_no);
//void QVM_GP_MEASURE(double *qvm_results, int grp_no);
void  Getsiteselected();
void SetTrimGroup(DWORD sitesum);
void SetRecoverSite();
void StepUp_PowerOnByPMID_Hsfet(double vbus_voltage);
void StepDown_PowerOffByPMID_Hsfet(double vbus_voltage);
//--------Trim Measure function define in program
void measure_bandgap(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_bg_res_div(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_mnt_v1p2_buf(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_mnt_dac_buf_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_iztc_res(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_osc_4p5m(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_osc_64k(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_mnt_vbat_rsns_loop(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_amux_ea_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_ibus_sns_gain(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_ibus_sns_ea_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_buck_rcs(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_boost_rcs(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_cs_hsfet_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_cs_lsfet_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_buck_hsfet_gain(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_buck_hsfet_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_boost_hsfet_gain(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_boost_hsfet_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_buck_lsfet_gain(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_buck_lsfet_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_boost_lsfet_gain(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_boost_lsfet_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_ibus_loop_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_mnt_vbus_ea_os_buck(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_mnt_vbus_ea_os_boost(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_mnt_vbat_cv_buf(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_ibat_cc_loop(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);
void measure_intc_curr(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);





void Retry_trim_search(TRIM_NODE *Retrim, void(*measure_func)(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results), SPEC& paraname, short funcindex, LPCTSTR funclabel, double unit_scale, int trend_p1, int trend_p2, double step_gap, bool ph1_ht_ph2, double gap_ratio = 1.1);
void Retest_current_unstable_with_time_out(ACM200 &acm_res, double *results, double low_limit, double high_limit, int delay_time_ms, int time_out_ms, REMEASURE_CURR_UNIT measure_unit);
void Retest_current_unstable_with_time_out(FPVIe &fpvi_res, double *results, double low_limit, double high_limit, int delay_time_ms, int time_out_ms, REMEASURE_CURR_UNIT measure_unit);
void Retest_current_unstable_with_time_out(FOVIe &fovi_res, double *results, double low_limit, double high_limit, int delay_time_ms, int time_out_ms, REMEASURE_CURR_UNIT measure_unit);
void Retest_voltage_unstable_with_time_out(ACM200 &acm_res, double *results, double low_limit_V, double high_limit_V, int delay_time_ms, int time_out_ms, REMEASURE_VOL_UNIT measure_unit);
void Retest_voltage_unstable_with_time_out(FOVIe &fovi_res, double *results, double low_limit_V, double high_limit_V, int delay_time_ms, int time_out_ms, REMEASURE_VOL_UNIT measure_unit);
void copper_trace_check_after_leakage_measure(ACM200 &acm_res, bool *fail_flag, double *results, double low_limit, double high_limit, REMEASURE_CURR_UNIT measure_unit);
void copper_trace_check_after_leakage_measure(FOVIe &fovi_res, bool *fail_flag, double *results, double low_limit, double high_limit, REMEASURE_CURR_UNIT measure_unit);

std::string extractBeforeDelimiter(const std::string& input, char delimiter);
bool containsSubstringC(const char* mainStr, const char* subStr);
bool findDevicePrefix(const std::vector<std::string>& device_list, const std::string& target, std::string& result);
bool IsFirstLoop();
bool check_relay_off(ACM200 &acm_res, int relay1_name, int relay2_name, int relay3_name, bool *relay_off_check);
bool check_relay_off(FOVIe &fovi_res, int relay1_name,int relay2_name, int relay3_name, bool *relay_off_check);
void check_awg_trigger_point(double * trig_pnt, int sam_pnt, double *ramp_trig_value1, double *ramp_trig_value2, int site);
void check_awg_trigger_point(int * trig_pnt, int sam_pnt, double *ramp_trig_value1, double *ramp_trig_value2, int site);
void check_awg_trigger_point(double * trig_pnt, int sam_pnt, double *ramp_trig_value1, int site);
void check_awg_trigger_point(int * trig_pnt, int sam_pnt, double *ramp_trig_value1, int site);