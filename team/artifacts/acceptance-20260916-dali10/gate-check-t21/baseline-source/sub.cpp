#include "stdafx.h"
#include "sub.h"
#include "math.h"
#include "tempchar.h"
extern string int2str(DWORD n);
#include "Test_Method.h"
extern Test_Method test_method;
//extern bool DEBUG;
extern double ibus_factor;
extern double g_ibat_snsr_1ohm[SITE_NUM];
extern double vbat_adc_offset;
extern double g_vbus_ovp_8v[SITE_NUM];
extern double g_vbus_ovp_alm_8v[SITE_NUM];
extern double g_ibat_reg[SITE_NUM];
extern double g_vbat_reg[SITE_NUM];
extern double g_vbat_ovp_alm[SITE_NUM];
extern double g_vbat_ovp[SITE_NUM];
extern double g_vac_pdr[SITE_NUM];
extern double g_vbus_pdr[SITE_NUM];
extern double g_int_pdr[SITE_NUM];
extern double adc_vbat[SITE_NUM];

extern Thermal_stream TS;
extern double V_TYP_VBAT;
extern double V_TYP_VBUS;
extern double V_TYP_VAC;
extern int LOOP_COUNT;


//int awg_load_pattern(char* awg_name, FPVIe fpvi_list[], VIMode viMode, FPVIe_VRNG v_range, FPVIe_IRNG i_range, double start_point, double stop_point, double step){
//	if (step <= 0)	return -1;
//
//	int samples;
//	double pat[MAX_SAMPLES];
//	samples = int(fabs((stop_point - start_point) / step));
//	if ((samples <= 1) || (samples > MAX_SAMPLES)){
//		return -2;
//	}
//
//	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
//
//	for (int ch = 0; ch < FPVI_NUM_NO_SITE; ++ch){
//		fpvi_list[ch].AwgLoader(awg_name, viMode, v_range, i_range, pat, samples);
//	}
//
//	return 0;
//}
//
//
//void measure_bandgap(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double qvm_results[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value[SITE_NUM] = { 0 };
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value[site] = (DWORD)trim_reg.assy("EFUSE_REG_F0").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, working_value);
//		delay_us(500);
//		QVM_GP.MeasureLADC(215, 10, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		QVM_GP_MEASURE(qvm_results, GRP_CNT);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (qvm_results[site])*1e3;// mV
//		}
//	}
//	else
//	{
//		QVM_GP.MeasureLADC(100, 5, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		QVM_GP_MEASURE(qvm_results, GRP_CNT);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (qvm_results[site])*1e3;// mV
//		}
//	}
//}
//
//void measure_bg_res_div(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double qvm_results[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value[SITE_NUM] = { 0 };
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value[site] = (DWORD)trim_reg.assy("EFUSE_REG_F1").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, working_value);
//		delay_us(500);
//		QVM_GP.MeasureLADC(215, 10, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		QVM_GP_MEASURE(qvm_results, GRP_CNT);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (qvm_results[site])*1e3;// mV
//		}
//	}
//	else
//	{
//		QVM_GP.MeasureLADC(100, 5, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		QVM_GP_MEASURE(qvm_results, GRP_CNT);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (qvm_results[site])*1e3;// mV
//		}
//	}
//
//}
//
//void measure_mnt_v1p2_buf(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double qvm_results[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F6").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F7").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		//****************************config register for all trim code sweep*************//
//		dcm.I2CWriteData(DEV_ADDR, 0xF6, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xF7, 1, working_value2);
//		//delay_us(500);
//		//QVM_GP.MeasureLADC(215, 10, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		//QVM_GP_MEASURE(qvm_results, GRP_CNT);
//		////****************************measure test results*************//
//		//FOR_EACH_VALID_SITE(site)
//		//{
//		//	results[site] = (qvm_results[site])*1e3;// mV
//		//}
//		delay_us(1000);
//		NTC_FOVI.MeasureVI(215, 10);
//		//FOR_EACH_VALID_SITE(site)
//		//{
//		//	results[site] =NTC_FOVI.GetMeasResult(site, MVRET)*1e3;// mV
//		//}
//		bool Funstable = false;
//		bool FSunstable[SITE_NUM] = { 0 };
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = NTC_FOVI.GetMeasResult(site, MVRET)*1e3;// mV
//			if (treg_measure_flag == TREG_MEASURE_POST)
//			{
//				if (results[site] > 1202 || results[site] < 1198)
//				{
//					if (treg_measure_flag == TREG_MEASURE_POST)
//					{
//						Funstable = true;
//						FSunstable[site] = true;
//					}
//				}
//			}
//
//		}
//		if (Funstable)
//		{
//			delay_us(3000);
//			NTC_FOVI.MeasureVI(200, 10);
//			FOR_EACH_VALID_SITE(site)
//			{
//				if (FSunstable[site])
//				{
//					results[site] = NTC_FOVI.GetMeasResult(site, MVRET)*1e3;// mV
//				}
//			}
//		}
//
//	}
//	else
//	{
//		delay_us(1000);
//		QVM_GP.MeasureLADC(100, 5, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		QVM_GP_MEASURE(qvm_results, GRP_CNT);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (qvm_results[site])*1e3;// mV
//		}
//	}
//
//}
//
//void measure_mnt_dac_buf_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double qvm_results[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F7").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F8").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		//****************************config register for all trim code sweep*************//
//		dcm.I2CWriteData(DEV_ADDR, 0xF7, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xF8, 1, working_value2);
//		delay_us(3000);
//		//QVM_GP.MeasureLADC(215, 10, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		//QVM_GP_MEASURE(qvm_results, GRP_CNT);
//		////****************************measure test results*************//
//		//FOR_EACH_VALID_SITE(site)
//		//{
//		//	results[site] = (qvm_results[site])*1e3;// mV
//		//}
//		AMUX_FOVI.MeasureVI(200, 10);
//
//		bool Funstable = false;
//		bool FSunstable[SITE_NUM] = { 0 };
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = AMUX_FOVI.GetMeasResult(site, MVRET)*1e3;// mV
//			if (results[site] > 1682 || results[site] < 1678)
//			{
//				if (treg_measure_flag == TREG_MEASURE_POST)
//				{
//					Funstable = true;
//					FSunstable[site] = true;
//				}
//			}
//		}
//		if (Funstable)
//		{
//			delay_us(3000);
//			AMUX_FOVI.MeasureVI(200, 10);
//			FOR_EACH_VALID_SITE(site)
//			{
//				if (FSunstable[site])
//				{
//					results[site] = AMUX_FOVI.GetMeasResult(site, MVRET)*1e3;// mV
//				}
//			}
//		}
//
//	}
//	else
//	{
//		delay_us(1000);
//		QVM_GP.MeasureLADC(100, 5, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		QVM_GP_MEASURE(qvm_results, GRP_CNT);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (qvm_results[site]);// mV
//		}
//	}
//}
//
//void measure_intc_curr(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double qvm_results[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW == QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F0").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F1").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		//****************************config register for all trim code sweep*************//
//		dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, working_value2);
//		delay_us(1000);
//		NTC_FOVI.MeasureVI(100, 5);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = -1 * (NTC_FOVI.GetMeasResult(site, MIRET)*1e6);// nA
//		}
//	}
//	else
//	{
//		delay_us(1000);
//		NTC_FOVI.MeasureVI(100, 5);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = -1 * (NTC_FOVI.GetMeasResult(site, MIRET)*1e6);// nA
//		}
//	}
//}
//
//void measure_iztc_res(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double qvm_results[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F0").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F1").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		//****************************config register for all trim code sweep*************//
//		dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, working_value2);
//		delay_us(1000);
//		AMUX_FOVI.MeasureVI(100, 5);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] =-1* (AMUX_FOVI.GetMeasResult(site, MIRET)*1e9);// nA
//		}
//	}
//	else
//	{
//		delay_us(1000);
//		AMUX_FOVI.MeasureVI(100, 5);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = -1 * (AMUX_FOVI.GetMeasResult(site, MIRET)*1e9);// nA
//		}
//	}
//}
//
//void measure_osc_4p5m(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double qtmu_results[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F1").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F2").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		//****************************config register for all trim code sweep*************//
//		dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xF2, 1, working_value2);
//		delay_us(1000);
//		QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.5, QTMUe_FILTER_PASS);//signal input to CHB,select 10V range,trigger=2.0V,rising edge
//		QTMU_GP.Connect(QTMUe_RELAY_CHA);
//		QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS); //measure frequency,timeout=10ms,sample 20 cycles
//		QTMU_GP_MEASURE(qtmu_results, GRP_CNT);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = qtmu_results[site]*0.128;// MHz
//		}
//	}
//	else
//	{
//		delay_us(1000);
//		QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.5, QTMUe_FILTER_PASS);//signal input to CHB,select 10V range,trigger=2.0V,rising edge
//		QTMU_GP.Connect(QTMUe_RELAY_CHA);
//		QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 10, 10, QTMUe_TRANGE_MS); //measure frequency,timeout=10ms,sample 20 cycles
//		QTMU_GP_MEASURE(qtmu_results, GRP_CNT);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = qtmu_results[site]*0.128;// MHz
//		}
//	}
//}
//
//void measure_mnt_vbat_rsns_loop(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double qvm_results[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F7").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		//****************************config register for all trim code sweep*************//
//		dcm.I2CWriteData(DEV_ADDR, 0xF7, 1, working_value1);
//		delay_us(3000);
//		//QVM_GP.MeasureLADC(215, 10, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		//QVM_GP_MEASURE(qvm_results, GRP_CNT);
//		////****************************measure test results*************//
//		//FOR_EACH_VALID_SITE(site)
//		//{
//		//	results[site] = (qvm_results[site])*1e3;// mV
//		//}
//		AMUX_FOVI.MeasureVI(215, 10);
//		double aaa = spec[DEVICE_SEL]("VBAT_RSNS_Ratio");
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (AMUX_FOVI.GetMeasResult(site, MVRET) - V_TYP_VBAT*spec[DEVICE_SEL]("VBAT_RSNS_Ratio"))*1e3;// mV
//		}
//	}
//	else
//	{
//		delay_us(1000);
//		QVM_GP.MeasureLADC(100, 5, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		QVM_GP_MEASURE(qvm_results, GRP_CNT);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (qvm_results[site]-V_TYP_VBAT*0.4)*1e3;// mV
//		}
//	}
//}
//
//void measure_amux_ea_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double reg28_qvm_results[SITE_NUM] = { 0 };
//	double reg29_qvm_results[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == TempChar)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F3").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F4").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		dcm.I2CWriteData(DEV_ADDR, 0xF3, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xF4, 1, working_value2);
//		I2CWriteSameData(DEV_ADDR, 0x56, 1, 226);
//		delay_us(1000);
//		//QVM_GP.MeasureLADC(100, 5, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		//QVM_GP_MEASURE(reg28_qvm_results, GRP_CNT);
//		AMUX_FOVI.MeasureVI(215, 10);
//		FOR_EACH_VALID_SITE(site)
//		{
//			reg28_qvm_results[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
//		}
//		I2CWriteSameData(DEV_ADDR, 0x56, 1, 234);
//		delay_us(1000);
//		//QVM_GP.MeasureLADC(100, 5, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		//QVM_GP_MEASURE(reg29_qvm_results, GRP_CNT);
//		AMUX_FOVI.MeasureVI(215, 10);
//		FOR_EACH_VALID_SITE(site)
//		{
//			reg29_qvm_results[site] = AMUX_FOVI.GetMeasResult(site, MVRET);
//		}
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			//results[site] = (reg28_qvm_results[site] - reg29_qvm_results[site])*1e3-7;// mV  with 7mV
//			results[site] = (reg28_qvm_results[site] - reg29_qvm_results[site])*1e3;// mV  withno 7mV
//		}
//	}
//	else
//	{
//		I2CWriteSameData(DEV_ADDR, 0x56, 1, 226);
//		delay_us(1000);
//		QVM_GP.MeasureLADC(100, 5, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		QVM_GP_MEASURE(reg28_qvm_results, GRP_CNT);
//
//		I2CWriteSameData(DEV_ADDR, 0x56, 1, 234);
//		delay_us(1000);
//		QVM_GP.MeasureLADC(100, 5, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		QVM_GP_MEASURE(reg29_qvm_results, GRP_CNT);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (reg29_qvm_results[site] - reg28_qvm_results[site])*1e3;// mV
//		}
//	}
//}
//
//void measure_ibus_sns_gain(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Vsense2[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	double Imeas2[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F2").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F3").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xF2, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xF3, 1, working_value2);
//		FPVI.Set(FI, -2.5, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_us(1500);
//		ATEST_GRP.MeasureVI(210, 5);
//		FPVI.MeasureVI(20, 5);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//		}
//		FPVI.Set(FI, -1.5, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_us(1500);
//		ATEST_GRP.MeasureVI(215, 5);// 2150us per period
//		FPVI.MeasureVI(20, 5);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//		}
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_us(1000);
//		bool Funstable = false;
//		bool FSunstable[SITE_NUM] = { 0 };
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = abs(Vsense2[site]-Vsense1[site])/(Imeas2[site]-Imeas1[site])*1e3;// mohm
//			IBUS_SNS_Gain[site] = results[site];
//			if (treg_measure_flag == TREG_MEASURE_POST)
//			{
//				if (IBUS_SNS_Gain[site]<197 || IBUS_SNS_Gain[site]>203)
//				{
//					Funstable = true;
//					FSunstable[site] = true;
//				}
//			}
//		}
//
//		if (Funstable)
//		{
//			FPVI.Set(FI, -2.5, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_us(2000);
//			ATEST_GRP.MeasureVI(215, 10);
//			FPVI.MeasureVI(20, 5);
//			FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_ms(1);
//			FOR_EACH_VALID_SITE(site)
//			{
//				Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//				Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//			}
//			FPVI.Set(FI, -1.5, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_us(2000);
//			ATEST_GRP.MeasureVI(215, 10);
//			FPVI.MeasureVI(20, 5);
//			FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_ms(1);
//			FOR_EACH_VALID_SITE(site)
//			{
//				if (FSunstable[site])
//				{
//					Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//					Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//					results[site] = 1e3*abs(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//					IBUS_SNS_Gain[site] = results[site];
//				}
//			}
//		}
//	}
//	else
//	{
//		FPVI.Set(FI, -2.5, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_us(1000);
//		ATEST_GRP.MeasureVI(100, 5);
//		FPVI.MeasureVI(20, 5);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//		}
//		FPVI.Set(FI, -1.5, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_us(1000);
//		ATEST_GRP.MeasureVI(100, 5);
//		FPVI.MeasureVI(20, 5);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//		}
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_us(1000);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = abs(Vsense2[site]-Vsense1[site])/(Imeas2[site]-Imeas1[site])*1e3;// mohm
//			IBUS_SNS_Gain[site] = results[site];
//		}
//	}
//
//}
//
//void measure_ibus_sns_ea_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Vsense2[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F2").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xF2, 1, working_value1);
//		FPVI.Set(FI, -0.5, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
//		delay_us(1000);
//		ATEST_GRP.MeasureVI(100, 5);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = abs(FPVI.GetMeasResult(site, MIRET));
//		}
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (Vsense1[site] - Imeas1[site]*0.2)*1e3;// mV
//		}
//		delay_us(1);
//	}
//	else
//	{
//		FPVI.Set(FI, -1.5, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
//		delay_us(1000);
//		ATEST_GRP.MeasureVI(100, 5);
//		FPVI.MeasureVI(20, 5);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = abs(FPVI.GetMeasResult(site, MIRET));
//		}
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
//		delay_us(1000);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (Vsense1[site] - Imeas1[site]*IBUS_SNS_Gain[site]/1e3)*1e3;// mV
//		}
//	}
//
//}
//
//void measure_buck_rcs(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F9").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_FF").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xF9, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xFF, 1, working_value2);
//		delay_us(1000);
//		FPVI.Set(FI, -0.15, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
//		delay_us(500);
//		STSEnableAWG(&FPVI);//enable AWG pattern for ACM200_0 
//		STSEnableMeas(&FPVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
//		STSAWGRun();//Enable AWG and measurement synchronously
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		//****************************measure test results*************//
//		double Trig_Point[SITE_NUM] = { 0 };
//		double Trigger_Curr[SITE_NUM] = { 0 };
//
//		//-------BUCK RCS mode, PMID --SW as Positive, boost ZCD mode  SW-->PMID as  Positive
//
//		// I_toggle + Izcd_spec_in_boost_rcs_mode (PMID-->SW as Positive) +Izcd(SW-->PMID as Positve)
//		//Ideal-Itoggle=Ispec-Izcd= offset, Ideal =Itoggle+Ispec-Izcd, need to know PMID-->SW as posotive
//		FOR_EACH_VALID_SITE(site)
//		{
//			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
//			Trigger_Curr[site] = abs(FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]));
//			//results[site] = 1e3*(Vclamp_high_buck[site] - 1.4) / (Trigger_Curr[site] * Iscale_buck[site]);			// read the V_value of trigger point 
//			//results[site] = 1e3*(Vclamp_high_buck[site] - 1.4) / ((Trigger_Curr[site] - (Boost_hsfet_zcd[site]-0.11)) * Iscale_buck[site]);	// read the V_value of trigger point 	
//			results[site] = 1e3*(Vclamp_high_boost[site] - 1.4) / ((Trigger_Curr[site] + spec[DEVICE_SEL]("BOZCD_Target_In_BURCS") -BO_zcd_in_BU_Rcs_Mode[site])* Iscale_buck[site]);
//		}
//	}
//	else
//	{
//		delay_us(1000);
//		FPVI.Set(FI, 1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_us(500);
//		STSEnableAWG(&FPVI);//enable AWG pattern for ACM200_0 
//		STSEnableMeas(&FPVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
//		STSAWGRun();//Enable AWG and measurement synchronously
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		//****************************measure test results*************//
//		double Trig_Point[SITE_NUM] = { 0 };
//		double Trigger_Curr[SITE_NUM] = { 0 };
//		FOR_EACH_VALID_SITE(site)
//		{
//			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
//			Trigger_Curr[site] = abs(FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]));
//			results[site] = 1e3*(Vclamp_high_buck[SITE] - 1.4) / (Trigger_Curr[site] * Iscale_buck[site]);			// read the V_value of trigger point 
//		}
//	}
//}
//
//void measure_boost_rcs(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//	DWORD working_value3[SITE_NUM] = { 0 };
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F8").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F9").get_working(site);
//			working_value3[site] = (DWORD)trim_reg.assy("EFUSE_REG_FF").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xF8, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xF9, 1, working_value2);
//		dcm.I2CWriteData(DEV_ADDR, 0xFF, 1, working_value3);
//		delay_us(1000);
//		FPVI.Set(FI, 0.5, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_us(500);
//		STSEnableAWG(&FPVI);//enable AWG pattern for ACM200_0 
//		STSEnableMeas(&FPVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
//		STSAWGRun();//Enable AWG and measurement synchronously
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		//****************************measure test results*************//
//		double Trig_Point[SITE_NUM] = { 0 };
//		double Trigger_Curr[SITE_NUM] = { 0 };
//		// I_toggle + Izcd_spec (SW-->PGND as Positive) +Izcd(PGND-->SW as Positve)
//		FOR_EACH_VALID_SITE(site)
//		{
//			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
//			Trigger_Curr[site] = abs(FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]));
//			//results[site] = 1e3*(Vclamp_high_boost[site] - 1.4) / (Trigger_Curr[site] * Iscale_boost[site]);			// read the V_value of trigger point 
//			results[site] = 1e3*(Vclamp_high_boost[site] - 1.4) / ((Trigger_Curr[site] + spec[DEVICE_SEL]("BUZCD_Target_In_BORCS") - BU_zcd_in_BO_Rcs_Mode[site])* Iscale_boost[site]);
//		}
//	}
//	else
//	{
//		delay_us(1000);
//		FPVI.Set(FI, 1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_us(500);
//		STSEnableAWG(&FPVI);//enable AWG pattern for ACM200_0 
//		STSEnableMeas(&FPVI, &SDA_INT_ACM);//enable measurement for ACM200_0 
//		STSAWGRun();//Enable AWG and measurement synchronously
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		//****************************measure test results*************//
//		double Trig_Point[SITE_NUM] = { 0 };
//		double Trigger_Curr[SITE_NUM] = { 0 };
//		FOR_EACH_VALID_SITE(site)
//		{
//			Trig_Point[site] = SDA_INT_ACM.GetMeasResult(site, MVRET, TRIG_RESULT);
//			Trigger_Curr[site] = abs(FPVI.GetMeasResult(site, MIRET, (int)Trig_Point[site]));
//			results[site] = 1e3*(Vclamp_high_boost[site] - 1.4) / (Trigger_Curr[site] * Iscale_boost[site]);			// read the V_value of trigger point 
//		}
//	}
//}
//
//void measure_cs_hsfet_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_FE").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xFE, 1, working_value1);
//		delay_us(1000);
//		ATEST_GRP.MeasureVI(215, 20);
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = 1e3*(AMUX_FOVI.GetMeasResult(site, MVRET)-NTC_FOVI.GetMeasResult(site, MVRET));	//mV
//		}
//	}
//	else
//	{
//		delay_us(1000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = 1e3*(AMUX_FOVI.GetMeasResult(site, MVRET)-NTC_FOVI.GetMeasResult(site, MVRET));	//mV
//		}
//	}
//}
//
//void measure_cs_lsfet_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_FE").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_FF").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xFE, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xFF, 1, working_value2);
//		delay_us(1000);
//		ATEST_GRP.MeasureVI(215, 20);
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = 1e3*(AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET));//mV
//		}
//	}
//	else
//	{
//		delay_us(1000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = 1e3*(AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET));//mV
//		}
//	}
//}
//
//void measure_buck_hsfet_gain(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	double Vsense2[SITE_NUM] = { 0 };
//	double Imeas2[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_FA").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_FB").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xFA, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xFB, 1, working_value2);
//		FPVI.Set(FI, -2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(1900);
//		FPVI.MeasureVI(20, 5);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//		}
//		FPVI.Set(FI, -1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(1900);
//		FPVI.MeasureVI(20, 5);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//
//		bool Funstable = false;
//		bool FSunstable[SITE_NUM] = { 0 };
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//			results[site] = 1e3*abs(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//			BUCK_IBAT_HS_Gain[site] = results[site];
//			if (BUCK_IBAT_HS_Gain[site] > 103 || BUCK_IBAT_HS_Gain[site] < 97)
//			{
//				if (treg_measure_flag == TREG_MEASURE_POST)
//				{
//					Funstable = true;
//					FSunstable[site] = true;
//				}
//			}
//		}
//		if (Funstable)
//		{
//			FPVI.Set(FI, -2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//			delay_us(2000);
//			ATEST_GRP.MeasureVI(215, 10);
//			FPVI.MeasureVI(20, 5);
//			FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_ms(1);
//			FOR_EACH_VALID_SITE(site)
//			{
//				Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//				Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//			}
//			FPVI.Set(FI, -1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//			delay_us(2000);
//			ATEST_GRP.MeasureVI(215, 10);
//			FPVI.MeasureVI(20, 5);
//			FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_ms(1);
//			FOR_EACH_VALID_SITE(site)
//			{
//				if (FSunstable[site])
//				{
//					Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//					Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//					results[site] = 1e3*abs(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//					BUCK_IBAT_HS_Gain[site] = results[site];
//				}
//			}
//		}
//	}
//	else
//	{
//		FPVI.Set(FI, -2.5, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(1000);
//		ATEST_GRP.MeasureVI(50, 5);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site]=FPVI.GetMeasResult(site, MIRET);
//		}
//		FPVI.Set(FI, -1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(1000);
//		ATEST_GRP.MeasureVI(50, 5);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//			results[site] = 1e3*(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//			BUCK_IBAT_HS_Gain[site] = results[site];
//		}
//	}
//}
//
//void measure_buck_hsfet_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_FD").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xFD, 1, working_value1);
//		FPVI.Set(FI, -0.5, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);////PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = abs(FPVI.GetMeasResult(site, MIRET));
//			results[site] =1e3*(Vsense1[site]-Imeas1[site]*BUCK_IBAT_HS_Gain[site]/1e3);	//mV
//		}
//	}
//	else
//	{
//		FPVI.Set(FI, -0.5, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);////PMID--->SW
//		delay_us(1000);
//		ATEST_GRP.MeasureVI(50, 5);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = abs(FPVI.GetMeasResult(site, MIRET));
//			results[site] =1e3*(Vsense1[site]-Imeas1[site]*BUCK_IBAT_HS_Gain[site]/1e3);	//mV
//		}
//	}
//
//}
//
//void measure_boost_hsfet_gain(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	double Vsense2[SITE_NUM] = { 0 };
//	double Imeas2[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F9").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_FA").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xF9, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xFA, 1, working_value2);
//		FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//		}
//		FPVI.Set(FI, 1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		bool Funstable = false;
//		bool FSunstable[SITE_NUM] = { 0 };
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//			results[site] = 1e3*abs(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//			BOOST_IBAT_HS_Gain[site] = results[site];
//			if (BOOST_IBAT_HS_Gain[site] > 103 || BOOST_IBAT_HS_Gain[site] < 97 )
//			{
//				if (treg_measure_flag == TREG_MEASURE_POST)
//				{
//					Funstable = true;
//					FSunstable[site] = true;
//				}
//			}
//		}
//		if (Funstable)
//		{
//			FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//			delay_us(2000);
//			ATEST_GRP.MeasureVI(215, 10);
//			FPVI.MeasureVI(20, 5);
//			FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_ms(1);
//			FOR_EACH_VALID_SITE(site)
//			{
//				Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//				Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//			}
//			FPVI.Set(FI, 1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//			delay_us(2000);
//			ATEST_GRP.MeasureVI(215, 10);
//			FPVI.MeasureVI(20, 5);
//			FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_ms(1);
//			FOR_EACH_VALID_SITE(site)
//			{
//				if (FSunstable[site])
//				{
//					Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//					Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//					results[site] = 1e3*abs(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//					BOOST_IBAT_HS_Gain[site] = results[site];
//				}
//			}
//		}
//	}
//	else
//	{
//		FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//		}
//		FPVI.Set(FI, 1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//			results[site] = 1e3*(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//			BOOST_IBAT_HS_Gain[site] = results[site];
//		}
//	}
//}
//
//void measure_boost_hsfet_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_FC").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xFC, 1, working_value1);
//		FPVI.Set(FI, 0.5, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);////PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215,10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = abs(FPVI.GetMeasResult(site, MIRET));
//			results[site] =1e3*(Vsense1[site]-Imeas1[site]*BOOST_IBAT_HS_Gain[site]/1e3);	//mV
//		}
//	}
//	else
//	{
//		FPVI.Set(FI, 1.5, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_ON);////PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = abs(FPVI.GetMeasResult(site, MIRET));
//			results[site] = 1e3*(Vsense1[site] - Imeas1[site] * BOOST_IBAT_HS_Gain[site] / 1e3);	//mV
//		}
//	}
//}
//
//void measure_buck_lsfet_gain(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	double Vsense2[SITE_NUM] = { 0 };
//	double Imeas2[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_FB").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xFB, 1, working_value1);
//		FPVI.Set(FI, -2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//		}
//		FPVI.Set(FI, -1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		bool Funstable = false;
//		bool FSunstable[SITE_NUM] = { 0 };
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//			results[site] = 1e3*abs(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//			BUCK_IBAT_LS_Gain[site] = results[site];
//			if (BUCK_IBAT_LS_Gain[site] > 103 || BUCK_IBAT_LS_Gain[site] < 97)
//			{
//				if (treg_measure_flag == TREG_MEASURE_POST)
//				{
//					Funstable = true;
//					FSunstable[site] = true;
//				}
//			}
//		}
//		if (Funstable)
//		{
//			FPVI.Set(FI, -2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//			delay_us(2000);
//			ATEST_GRP.MeasureVI(215, 10);
//			FPVI.MeasureVI(20, 5);
//			FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_ms(1);
//			FOR_EACH_VALID_SITE(site)
//			{
//				Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//				Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//			}
//			FPVI.Set(FI, -1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//			delay_us(2000);
//			ATEST_GRP.MeasureVI(215, 10);
//			FPVI.MeasureVI(20, 5);
//			FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_ms(1);
//			FOR_EACH_VALID_SITE(site)
//			{
//				if (FSunstable[site])
//				{
//					Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//					Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//					results[site] = 1e3*abs(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//					BUCK_IBAT_LS_Gain[site] = results[site];
//				}
//			}
//		}
//
//
//	}
//	else
//	{
//		FPVI.Set(FI, -2.0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//		}
//		FPVI.Set(FI, -1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//			results[site] = 1e3*(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//			BUCK_IBAT_LS_Gain[site] = results[site];
//		}
//	}
//}
//
//void measure_buck_lsfet_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_FD").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xFD, 1, working_value1);
//		FPVI.Set(FI, -0.5, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);////PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = abs(FPVI.GetMeasResult(site, MIRET));
//			results[site] =1e3*(Vsense1[site]-Imeas1[site]*BUCK_IBAT_LS_Gain[site]/1e3);	//mV
//			//results[site] = trim_node->get_target(site) + sim_step[site];
//		}
//	}
//	else
//	{
//		FPVI.Set(FI, -0.5, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);////PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = abs(FPVI.GetMeasResult(site, MIRET));
//			results[site] = 1e3*(Vsense1[site] - Imeas1[site] * BUCK_IBAT_LS_Gain[site] / 1e3);	//mV
//		}
//	}
//}
//
//void measure_boost_lsfet_gain(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	double Vsense2[SITE_NUM] = { 0 };
//	double Imeas2[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_FA").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xFA, 1, working_value1);
//		FPVI.Set(FI, 2.0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//		}
//		FPVI.Set(FI, 1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		bool Funstable = false;
//		bool FSunstable[SITE_NUM] = { 0 };
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//			results[site] = 1e3*abs(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//			BOOST_IBAT_LS_Gain[site] = results[site];
//			if (BOOST_IBAT_LS_Gain[site] > 103 || BOOST_IBAT_LS_Gain[site] < 97)
//			{
//				if (treg_measure_flag == TREG_MEASURE_POST)
//				{
//					Funstable = true;
//					FSunstable[site] = true;
//				}
//			}
//		}
//		if (Funstable)
//		{
//			FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//			delay_us(2000);
//			ATEST_GRP.MeasureVI(215, 10);
//			FPVI.MeasureVI(20, 5);
//			FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_ms(1);
//			FOR_EACH_VALID_SITE(site)
//			{
//				Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//				Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//			}
//			FPVI.Set(FI, 1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//			delay_us(2000);
//			ATEST_GRP.MeasureVI(215, 10);
//			FPVI.MeasureVI(20, 5);
//			FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_ms(1);
//			FOR_EACH_VALID_SITE(site)
//			{
//				if (FSunstable[site])
//				{
//					Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//					Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//					results[site] = 1e3*abs(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//					BOOST_IBAT_LS_Gain[site] = results[site];
//				}
//			}
//		}
//
//	}
//	else
//	{
//		FPVI.Set(FI, 2.0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = FPVI.GetMeasResult(site, MIRET);
//		}
//		FPVI.Set(FI, 1, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);//PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense2[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas2[site] = FPVI.GetMeasResult(site, MIRET);
//			results[site] = 1e3*(Vsense2[site] - Vsense1[site]) / abs(Imeas2[site] - Imeas1[site]);	//mV
//			BOOST_IBAT_LS_Gain[site] = results[site];
//		}
//	}
//}
//
//void measure_boost_lsfet_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	TRIM_NODE &BOOST_LSFET_OS = trim_reg.trim("boost_lsfet_os");
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_FC").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xFC, 1, working_value1);
//		FPVI.Set(FI, 0.5, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);////PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_1A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = abs(FPVI.GetMeasResult(site, MIRET));
//			results[site] =1e3*(Vsense1[site]-Imeas1[site]*BOOST_IBAT_LS_Gain[site]/1e3);	//mV
//		}
//	}
//	else
//	{
//		FPVI.Set(FI, 0.5, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);////PMID--->SW
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			Vsense1[site] = AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET);
//			Imeas1[site] = abs(FPVI.GetMeasResult(site, MIRET));
//			results[site] = 1e3*(Vsense1[site] - Imeas1[site] * BOOST_IBAT_LS_Gain[site] / 1e3);	//mV
//		}
//	}
//}
//
//void measure_ibus_loop_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F3").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xF3, 1, working_value1);
//		FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_us(1500);
//		ATEST_GRP.MeasureVI(50, 5);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		//FOR_EACH_VALID_SITE(site)
//		//{
//		//	results[site] = (AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET))*1e3;//mV
//		//}
//		bool Funstable = false;
//		bool FSunstable[SITE_NUM] = { 0 };
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET))*1e3;//mV
//			Ibus_loop_Voffset_2A[site] = results[site] / 1e3;//V
//			if (results[site] > 5 || results[site] < -5)
//			{
//				if (treg_measure_flag == TREG_MEASURE_POST)
//				{
//					Funstable = true;
//					FSunstable[site] = true;
//				}
//			}
//		}
//		if (Funstable)
//		{
//			delay_us(3000);
//			FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//			delay_us(1500);
//			ATEST_GRP.MeasureVI(50, 5);
//			FOR_EACH_VALID_SITE(site)
//			{
//				if (FSunstable[site])
//				{
//					results[site] = (AMUX_FOVI.GetMeasResult(site, MVRET) - NTC_FOVI.GetMeasResult(site, MVRET))*1e3;//mV
//					Ibus_loop_Voffset_2A[site] = results[site]/1e3;//V
//				}
//			}
//		}
//	}
//	else
//	{
//		FPVI.Set(FI, 2, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_us(1000);
//		ATEST_GRP.MeasureVI(50, 5);
//		FPVI.MeasureVI(20, 5);
//		FPVI.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
//		delay_ms(1);
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (AMUX_FOVI.GetMeasResult(site, MVRET)- NTC_FOVI.GetMeasResult(site, MVRET))*1e3;//mV
//		}
//	}
//}
//
//void measure_mnt_vbus_ea_os_buck(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F4").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xF4, 1, working_value1);
//		delay_us(2000);
//		VBUS_FOVI.MeasureVI(215, 10);
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = VBUS_FOVI.GetMeasResult(site, MVRET) *1e3;//mV
//		}
//	}
//	else
//	{
//		//****************************config register for all trim code sweep*************//	
//		delay_us(2000);
//		VBUS_FOVI.MeasureVI(215, 10);
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = VBUS_FOVI.GetMeasResult(site, MVRET) *1e3;//mV
//		}
//	}
//
//}
//
//void measure_mnt_vbus_ea_os_boost(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F5").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xF5, 1, working_value1);
//		delay_us(2000);
//		VBUS_FOVI.MeasureVI(215, 10);
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = VBUS_FOVI.GetMeasResult(site, MVRET) *1e3;//mV
//		}
//	}
//	else
//	{
//		//****************************config register for all trim code sweep*************//	
//		delay_us(2000);
//		VBUS_FOVI.MeasureVI(215, 10);
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = VBUS_FOVI.GetMeasResult(site, MVRET) *1e3;//mV
//		}
//	}
//
//}
//
//void measure_mnt_vbat_cv_buf(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double Vsense1[SITE_NUM] = { 0 };
//	double Imeas1[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value1[SITE_NUM] = { 0 };
//	DWORD working_value2[SITE_NUM] = { 0 };
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F5").get_working(site);
//			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F6").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//	
//		dcm.I2CWriteData(DEV_ADDR, 0xF5, 1, working_value1);
//		dcm.I2CWriteData(DEV_ADDR, 0xF6, 1, working_value2);
//		delay_us(2000);
//		VBAT_ACM.MeasureVI(215, 10);
//		bool Funstable = false;
//		bool FSunstable[SITE_NUM] = { 0 };
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (VBAT_ACM.GetMeasResult(site, MVRET) - spec[DEVICE_SEL]("VBAT_CV_Point"))*1e3;//mV
//			if (results[site] > 5 || results[site] < -5)
//			{
//				if (treg_measure_flag == TREG_MEASURE_POST)
//				{
//					Funstable = true;
//					FSunstable[site] = true;
//				}
//			}
//		}
//		if (Funstable)
//		{
//			delay_us(3000);
//			AMUX_FOVI.MeasureVI(200, 10);
//			FOR_EACH_VALID_SITE(site)
//			{
//				if (FSunstable[site])
//				{
//					results[site] = (VBAT_ACM.GetMeasResult(site, MVRET) - spec[DEVICE_SEL]("VBAT_CV_Point"))*1e3;//mV
//				}
//			}
//		}
//
//	}
//	else
//	{
//		//****************************config register for all trim code sweep*************//	
//		delay_us(1000);
//		VBAT_ACM.MeasureVI(50, 5);
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = VBAT_ACM.GetMeasResult(site, MVRET) *1e3;//mV
//		}
//	}
//
//}
//
//void measure_ibat_cc_loop(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
//{
//	double qvm_results[SITE_NUM] = { 0 };
//	INT64 sim_step[SITE_NUM] = { 0 };
//	DWORD working_value[SITE_NUM] = { 0 };
//
//	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == HTOL_Burn || TEST_FLOW == QUAL || TEST_FLOW ==QA)
//	{
//		FOR_EACH_VALID_SITE(site)
//		{
//			if ((treg_measure_flag == TREG_MEASURE_PRE) || (treg_measure_flag == TREG_MEASURE_POST))
//			{
//				if (BURN_FLAG[site] == BURNNED)
//				{
//					trim_node->copy_read_to_work(site); // This Action help to guarantee the burned unit best code is the burned one
//				}
//			}
//			working_value[site] = (DWORD)trim_reg.assy("EFUSE_REG_F8").get_working(site);
//			sim_step[site] = trim_node->get_working(site);
//		}
//		//****************************config register for all trim code sweep*************//
//		dcm.I2CWriteData(DEV_ADDR, 0xF8, 1, working_value);
//		delay_us(2000);
//		ATEST_GRP.MeasureVI(215, 10);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (NTC_FOVI.GetMeasResult(site, MVRET) -AMUX_FOVI.GetMeasResult(site, MVRET))*1e3;// mV
//		}
//	}
//	else
//	{
//		delay_us(1000);
//		QVM_GP.MeasureLADC(100, 5, QVMe_LADC_2V, QVMe_LADC_10KHz, MEAS_NORMAL);
//		QVM_GP_MEASURE(qvm_results, GRP_CNT);
//		//****************************measure test results*************//
//		FOR_EACH_VALID_SITE(site)
//		{
//			results[site] = (qvm_results[site])*1e3;// mV
//		}
//	}
//}


int find_R(double* dataall, int starpoint, int stoppoint, double trigvalue, int site)
{
	int a = 0;
	for (int i = starpoint; i < stoppoint; i++)
	{
		if (dataall[i] >= trigvalue)
		{
			a = i;
			break;
		}
	}
	return a;
}

int find_F(double* dataall, int starpoint, int stoppoint, double trigvalue, int site)
{
	int a = 0;
	for (int i = starpoint; i < stoppoint; i++)
	{
		if (dataall[i] <= trigvalue)
		{
			a = i;
			break;
		}
	}
	return a;
}

void Retry_trim_search(TRIM_NODE *Retrim, void(*measure_func)(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results), SPEC& paraname, short funcindex, LPCTSTR funclabel, double unit_scale, int trend_p1, int trend_p2, double step_gap, bool ph1_ht_ph2, double gap_ratio)
{
	int re_bestcode[SITE_NUM] = { 0 }; 
	double re_post_val[SITE_NUM] = { 0 };
	int  current_bestcode_seq[SITE_NUM] = { 0 };
	int final_bestcode_seq[SITE_NUM] = { 0 };
	double pos[SITE_NUM] = { 0 };
	int Fail_cnt = 0;
	int Fail_site[SITE_NUM] = { 0 };
	int code_compensate[SITE_NUM] = { 0 };
	int codemax = Retrim->get_steps();
	int code_seq_arr[256] = { 0 };

	//-----------------------��trim code ���յ���˳������
	for (int i = 0; i < codemax; i++)
	{
		if (ph1_ht_ph2 == true)// ˵����һ��ֵ��ȫ�����ڵڶ��ε�
		{
			if (trend_p1>0 && trend_p2>0)//---��һ���������ڶ�������, 4-5-6-7-0-1-2-3
			{
				if (i < codemax / 2)
				{
					code_seq_arr[i] = codemax / 2 + i;
				}
				else
				{
					code_seq_arr[i] = i - codemax / 2;
				}
			}
			if (trend_p1>0 && trend_p2<0)//---��һ���������ڶ����½� 7-6-5-4-0-1-2-3
			{
				if (i < codemax / 2)
				{
					code_seq_arr[i] = codemax - i - 1;
				}
				else
				{
					code_seq_arr[i] = i - codemax / 2;;
				}
			}
			if (trend_p1<0 && trend_p2>0)//---��һ���½����ڶ�������,4-5-6-7-3-2-1-0
			{
				if (i < codemax / 2)
				{
					code_seq_arr[i] = codemax / 2 + i;
				}
				else
				{
					code_seq_arr[i] = codemax - i - 1;
				}

			}
			if (trend_p1<0 && trend_p2<0)//---��һ���½����ڶ����½�,7-6-5-4-3-2-1-0
			{
				code_seq_arr[i] = codemax - i - 1;
			}
		}
		else// ˵���ڶ���ֵ��ȫ�����ڵ�һ�ε�
		{
			//-----------------------��һ���������ڶ�������, 0-1-2-3-4-5-6-7
			if (trend_p1 > 0 && trend_p2 > 0)
			{
				code_seq_arr[i] = i;
			}
			//-----------------------��һ���������ڶ����½� 0-1-2-3-7-6-5-4,
			if (trend_p1 > 0 && trend_p2 < 0)
			{
				if (i < codemax / 2)
				{
					code_seq_arr[i] = i;
				}
				else
				{
					code_seq_arr[i] = (int)(1.5*codemax - i - 1);
				}
			}
			//------------------------��һ���½����ڶ�������,3-2-1-0-4-5-6-7
			if (trend_p1 < 0 && trend_p2>0)
			{
				if (i < codemax / 2)
				{
					code_seq_arr[i] = codemax / 2 - i - 1;
				}
				else
				{
					code_seq_arr[i] = i;
				}
			}
			//-----------------------��һ���½����ڶ����½�,3-2-1-0-7-6-5-4
			if (trend_p1 < 0 && trend_p2 < 0)
			{
				if (i < codemax / 2)
				{
					code_seq_arr[i] = codemax / 2 - i - 1;
				}
				else
				{
					code_seq_arr[i] = (int)(1.5*codemax - i - 1);
				}
			}

		}
	}




	//-------------------�ж��Ƿ������Ҫ����trim search��site
	FOR_EACH_VALID_SITE(site)
	{
		pos[site] = Retrim->get_post_reading(site);// ----------��Post Search��best Value ����ֵ��pos
		re_post_val[site] = Retrim->get_post_reading(site);// ----------��Post Search��best Value ����ֵ��re_post_val��һ������Ҫ�ز⣬re_post_val��ά�ֲ��ı䣬����͸���
		re_bestcode[site] = Retrim->get_working(site);// ---------------��Post Search�� best code ����ֵ��re_bestcode,һ������Ҫ�ز⣬re_bestcode��ά�ֲ��ı�,����͸���

		/*----------------------------����ز���Ҫ����3��������----------
		1. ����best value ����Ŀ��ֵ������1.1 ����step
		2. ������Ҫ��֤оƬ��Fresh part
		3. ���Ե������� FT ģʽ------------------------------------- */
		if (abs(pos[site] - Retrim->get_target(site)) > gap_ratio*step_gap /* && BURN_FLAG[site] == FRESH && FT_FLAG == 1*/)
		{
			Fail_cnt++;
			Fail_site[site] = 1;
		}
		//-----------------��ȡexecute�ҵ���best code �ڵ��������е����
		for (int i = 0; i < codemax; i++)
		{
			if (abs((int)Retrim->get_working(site) - code_seq_arr[i]) < 0.01)
			{
				current_bestcode_seq[site] = i;// ����execute�ҵ���best code�ڵ��������е���ŵ�bestcode_seq���飬���������Ҫ����n��code����ž�+n
			}
		}

	}

	double CODE[SITE_NUM] = { 0 };
	double CO[SITE_NUM] = { 0 };
	double Retest_Val[SITE_NUM] = { 0 };
	if (Fail_cnt > 0)//----------------�����ĳ��site��Ҫ���°���Trim search
	{
		FOR_EACH_VALID_SITE(site)
		{
			if (Fail_site[site] == 1)//------------�����site��Ҫ�ز⣬����Ҫ����bestcode
			{
				code_compensate[site] = (int)((Retrim->get_post_reading(site) - Retrim->get_target(site)) / step_gap / gap_ratio);// code compensation >0, ��Ҫ����
				final_bestcode_seq[site] = current_bestcode_seq[site] - code_compensate[site]; //������Ѱ��bestcode ��� 
				//-----------limit final seq will not out of trim code range
				if (final_bestcode_seq[site] < 0)
				{
					final_bestcode_seq[site] = 0;
				}
				if (final_bestcode_seq[site] > codemax - 1)
				{
					final_bestcode_seq[site] = codemax - 1;
				}
				re_bestcode[site] = code_seq_arr[final_bestcode_seq[site]];//������ţ���ȡ���յ�bestcode
			}
		}

		//---------------------�����µ�bestcode �ŵ�working �Ĵ�������ȥ
		FOR_EACH_VALID_SITE(site)
		{
			Retrim->set_working(re_bestcode[site], site);
		}
		//------------------ѡ��measure Preģʽ����ȡ���µ�bestcode ��Ӧ��ֵ,����site��Ҫ����
		measure_func(Retrim, TREG_MEASURE_POST, Retest_Val);

		//----------------------------------�������Ҫ�ز��site���²��ԵĽ����
		FOR_EACH_VALID_SITE(site)
		{
			if (BURN_FLAG[site] == BURNNED)
			{
				StsGetParam(funcindex, paraname.get_post_rt_str(funclabel).c_str())->SetTestResult(site, 0, re_post_val[site] * unit_scale);			// log post trimming result
				StsGetParam(funcindex, paraname.get_post_str(funclabel).c_str())->SetTestResult(site, 0, Retrim->get_target(site));			// log post trimming result
			}
			else
			{
				if (Fail_site[site] == 1)// --------------��Ҫ�ز�Ĺ�λ����Ҫ���²��Խ���������µ�������λ��ά�ֵ�һ�ε�bestcode
				{
					re_post_val[site] = Retest_Val[site];
					Retrim->set_guessed_final(re_post_val[site], site, re_bestcode[site]);
					//Retrim->set_post_reading(re_post_val[site], site);
					//Retrim->set_post_trimming(re_bestcode[site], site);
					StsGetParam(funcindex, paraname.get_post_bit_str(funclabel).c_str())->SetTestResult(site, 0, Retrim->get_working(site));					// log post trimming step  
					StsGetParam(funcindex, paraname.get_post_str(funclabel).c_str())->SetTestResult(site, 0, re_post_val[site] * unit_scale);			// log post trimming result
				}
			}

			//if (Fail_site[site] == 1)// --------------��Ҫ�ز�Ĺ�λ����Ҫ���²��Խ���������µ�������λ��ά�ֵ�һ�ε�bestcode
			//{
			//	re_post_val[site] = Retest_Val[site];
			//	Retrim->set_guessed_final(re_post_val[site], site, re_bestcode[site]);
			//	//Retrim->set_post_reading(re_post_val[site], site);
			//	//Retrim->set_post_trimming(re_bestcode[site], site);
			//	StsGetParam(funcindex, paraname.get_post_bit_str(funclabel).c_str())->SetTestResult(site, 0, Retrim->get_working(site));					// log post trimming step  
			//	if (BURN_FLAG[site] == BURNNED)
			//	{
			//		StsGetParam(funcindex, paraname.get_post_rt_str(funclabel).c_str())->SetTestResult(site, 0, re_post_val[site] * unit_scale);			// log post trimming result
			//	}
			//	else
			//	{
			//		StsGetParam(funcindex, paraname.get_post_str(funclabel).c_str())->SetTestResult(site, 0, re_post_val[site] * unit_scale);			// log post trimming result
			//	}		
			//}
		}
	}

}

//------------------------------------I2C function setup utility
void Set_I2C()
{
	dcm.I2CSet(Period, SITE_NUM, DCM_REG8, "S24_1,S24_17,S24_33,S24_49,S9_1,S9_17,S9_33,S9_49", "S24_2,S24_18,S24_34,S24_50,S9_2,S9_18,S9_34,S9_50");
	dcm.I2CSetPinLevel(5.0, 0, 2.5, 0.5);
	dcm.I2CConnect();
}

void I2C_READ_BYTE(BYTE slaveaddr, DWORD regaddr, ULONG pdata[SITE_NUM])
{
	ULONG data_SITE[SITE_NUM];
	dcm.I2CReadData(slaveaddr, regaddr, 1);
	FOR_EACH_VALID_SITE(site) if (1)
	{
		pdata[site] = dcm.I2CGetReadData(site, 0);
		data_SITE[site] = dcm.I2CGetReadData(site, 0);
	}
}

void I2CWriteSameData(BYTE slaveaddr, DWORD regaddr, int length, DWORD writesamedata)
{
	DWORD sdata[SITE_NUM] = { 0 };
	for (int site = 0; site < SITE_NUM; site++)
	{
		sdata[site] = writesamedata;
	}
	dcm.I2CWriteData(slaveaddr, regaddr, 1, sdata);  //0011 0000
}

void I2CWriteSameData(BYTE slaveaddr, DWORD regaddr, DWORD writesamedata)
{
	DWORD sdata[SITE_NUM] = { 0 };
	for (int site = 0; site < SITE_NUM; site++)
	{
		sdata[site] = writesamedata;
	}
	dcm.I2CWriteData(slaveaddr, regaddr, 1, sdata);  //0011 0000
}

void entertestmode()
{
	delay_ms(5);
	I2CWriteSameData(DEV_ADDR, 0x50, 1, 0x65);
	I2CWriteSameData(DEV_ADDR, 0x50, 1, 0x37);
	I2CWriteSameData(DEV_ADDR, 0x50, 1, 0x2D);
	I2CWriteSameData(DEV_ADDR, 0x50, 1, 0xF9);
	delay_ms(1);
	I2CWriteSameData(DEV_ADDR, 0x51, 1, 0x29);
	I2CWriteSameData(DEV_ADDR, 0x51, 1, 0xCB);
	I2CWriteSameData(DEV_ADDR, 0x51, 1, 0xE2);
	I2CWriteSameData(DEV_ADDR, 0x51, 1, 0x6A);
	//I2CWriteSameData(0x60, 0x24, 1, 0x00);// overwrite OTP for temp char
}


void  Getsiteselected()
{
	BYTE SelSite[SITE_NUM] = { 0 };
	STSGetSiteStatus(SelSite, SITE_NUM);
	double siteflag = 0;
	for (int site = 0; site < SITE_NUM; site++)
	{
		if (SelSite[site]> 0)
		{
			SiteSelected[site] = 1;
		}
	}
}

void SetTrimGroup(DWORD sitesum)
{
	BYTE SetSitestatus[SITE_NUM] = { 0 };
	STSSetSiteStatus(sitesum);// only enable site1 to site8
	STSGetSiteStatus(SetSitestatus, SITE_NUM);//-------Get which site is set in group
	double siteflag = 0;
	for (int site = 0; site < SITE_NUM; site++)
	{
		if (SetSitestatus[site] && SiteSelected[site]> 0)// --------make sure site is selected and enabled
		{
			siteflag = siteflag + (double)(pow(2, site));
		}
	}
	DWORD SiteSetting;
	SiteSetting = (DWORD)siteflag;
	STSSetSiteStatus(SiteSetting);// only enable site1 to site8
}

void SetRecoverSite()
{
	double siteflag = 0;
	for (int site = 0; site < SITE_NUM; site++)
	{
		if (SiteSelected[site] > 0)
		{
			siteflag = siteflag + pow(2, site);
		}
	}
	DWORD SITERECOVER = DWORD(siteflag);
	STSSetSiteStatus(SITERECOVER);
}

//-------------------------QVM  GROUP MEASUREMENT
void QVM_GRP_MEASURE(double *qvm_results, int grp_no)
{
	qvm_results[0] = QVM_S1.GetMeasResult(0, AVERAGE_RESULT); // site1
	qvm_results[1] = QVM_S2.GetMeasResult(0, AVERAGE_RESULT); // site3
	qvm_results[2] = QVM_S3.GetMeasResult(0, AVERAGE_RESULT); // site5
	qvm_results[3] = QVM_S4.GetMeasResult(0, AVERAGE_RESULT); // site7
	qvm_results[4] = QVM_S5.GetMeasResult(0, AVERAGE_RESULT); // site9
	qvm_results[5] = QVM_S6.GetMeasResult(0, AVERAGE_RESULT); // site11
	qvm_results[6] = QVM_S7.GetMeasResult(0, AVERAGE_RESULT); // site13
	qvm_results[7] = QVM_S8.GetMeasResult(0, AVERAGE_RESULT);  //  site15
}

//-------------------------QTMU  GROUP MEASUREMENT
void QTMU_GRP_MEASURE(double *qtmu_results, int grp_no)
{
	//------CHANNEL_A
	qtmu_results[0] = QTMU_S1.GetMeasureResult(0);// site1
	qtmu_results[1] = QTMU_S2.GetMeasureResult(0);// site3
	qtmu_results[2] = QTMU_S3.GetMeasureResult(0);// site5
	qtmu_results[3] = QTMU_S4.GetMeasureResult(0);// site7
	qtmu_results[4] = QTMU_S5.GetMeasureResult(0);// site9
	qtmu_results[5] = QTMU_S6.GetMeasureResult(0);// site11
	qtmu_results[6] = QTMU_S7.GetMeasureResult(0);// site13
	qtmu_results[7] = QTMU_S8.GetMeasureResult(0);// site15
}

void Retest_current_unstable_with_time_out(FPVIe &fpvi_res, double *results, double low_limit, double high_limit, int delay_time_ms, int time_out_ms, REMEASURE_CURR_UNIT measure_unit)
{
	bool failflag[SITE_NUM] = { 0 };
	bool loop_done = false;
	double meas_value[SITE_NUM] = { 0 };
	for (int lp = 0; lp < time_out_ms / delay_time_ms; lp++)
	{
		double unit_facotr = 1;
		if (measure_unit == MEAS_A)//A
		{
			unit_facotr = 1;
		}
		if (measure_unit == MEAS_MA)//mA
		{
			unit_facotr = 1e3;
		}
		if (measure_unit == MEAS_UA)//uA
		{
			unit_facotr = 1e6;
		}
		if (measure_unit == MEAS_NA)//nA
		{
			unit_facotr = 1e9;
		}

		loop_done = true;
		delay_ms(delay_time_ms);
		fpvi_res.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			meas_value[site] = fpvi_res.GetMeasResult(site, MIRET)*unit_facotr;//A
			if (lp == 0 || failflag[site] == true)// first time measure value or last measure cannot pass, will update test value
			{
				results[site] = meas_value[site];
			}
			if (meas_value[site] < low_limit || meas_value[site] > high_limit)
			{
				failflag[site] = true;
			}
			else
			{
				failflag[site] = false;// test value pass limit, no need to loop for this site
			}
		}

		FOR_EACH_VALID_SITE(site)
		{
			if (failflag[site])
			{
				loop_done = false;// any site not pass , need to loop, cannot stop
			}
		}
		if (loop_done)
		{
			lp = time_out_ms / delay_time_ms;
		}
	}
}

void Retest_current_unstable_with_time_out(ACM200 &acm_res, double *results, double low_limit, double high_limit, int delay_time_ms, int time_out_ms, REMEASURE_CURR_UNIT measure_unit)
{
	bool failflag[SITE_NUM] = { 0 };
	bool loop_done = false;
	double meas_value[SITE_NUM] = { 0 };
	for (int lp = 0; lp < time_out_ms / delay_time_ms; lp++)
	{
		double unit_facotr = 1;
		if (measure_unit == MEAS_A)//A
		{
			unit_facotr = 1;
		}
		if (measure_unit == MEAS_MA)//mA
		{
			unit_facotr = 1e3;
		}
		if (measure_unit == MEAS_UA)//uA
		{
			unit_facotr = 1e6;
		}
		if (measure_unit == MEAS_NA)//nA
		{
			unit_facotr = 1e9;
		}

		loop_done = true;
		delay_ms(delay_time_ms);
		acm_res.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			meas_value[site] = acm_res.GetMeasResult(site, MIRET)*unit_facotr;//A
			if (lp == 0 || failflag[site] == true)// first time measure value or last measure cannot pass, will update test value
			{
				results[site] = meas_value[site];
			}
			if (meas_value[site] < low_limit || meas_value[site] > high_limit)
			{
				failflag[site] = true;
			}
			else
			{
				failflag[site] = false;// test value pass limit, no need to loop for this site
			}
		}

		FOR_EACH_VALID_SITE(site)
		{
			if (failflag[site])
			{
				loop_done = false;// any site not pass , need to loop, cannot stop
			}
		}
		if (loop_done)
		{
			lp = time_out_ms / delay_time_ms;
		}
	}
}

void Retest_current_unstable_with_time_out(FOVIe &fovi_res, double *results, double low_limit, double high_limit, int delay_time_ms, int time_out_ms, REMEASURE_CURR_UNIT measure_unit)
{
	bool failflag[SITE_NUM] = { 0 };
	bool loop_done = false;
	double meas_value[SITE_NUM] = { 0 };
	for (int lp = 0; lp < time_out_ms / delay_time_ms; lp++)
	{
		double unit_facotr = 1;
		if (measure_unit == MEAS_A)//A
		{
			unit_facotr = 1;
		}
		if (measure_unit == MEAS_MA)//mA
		{
			unit_facotr = 1e3;
		}
		if (measure_unit == MEAS_UA)//uA
		{
			unit_facotr = 1e6;
		}
		if (measure_unit == MEAS_NA)//nA
		{
			unit_facotr = 1e9;
		}

		loop_done = true;
		delay_ms(delay_time_ms);
		fovi_res.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			meas_value[site] = fovi_res.GetMeasResult(site, MIRET)*unit_facotr;//A
			if (lp == 0 || failflag[site] == true)// first time measure value or last measure cannot pass, will update test value
			{
				results[site] = meas_value[site];
			}
			if (meas_value[site] < low_limit || meas_value[site] > high_limit)
			{
				failflag[site] = true;
			}
			else
			{
				failflag[site] = false;// test value pass limit, no need to loop for this site
			}
		}

		FOR_EACH_VALID_SITE(site)
		{
			if (failflag[site])
			{
				loop_done = false;// any site not pass , need to loop, cannot stop
			}
		}
		if (loop_done)
		{
			lp = time_out_ms / delay_time_ms;
		}
	}
}

void Retest_current_unstable_with_time_out(FXVIe_PLUS& fxvi_res, double* results, double low_limit, double high_limit, int delay_time_ms, int time_out_ms, REMEASURE_CURR_UNIT measure_unit)
{
	bool failflag[SITE_NUM] = { 0 };
	bool loop_done = false;
	double meas_value[SITE_NUM] = { 0 };
	for (int lp = 0; lp < time_out_ms / delay_time_ms; lp++)
	{
		double unit_facotr = 1;
		if (measure_unit == MEAS_A)//A
		{
			unit_facotr = 1;
		}
		if (measure_unit == MEAS_MA)//mA
		{
			unit_facotr = 1e3;
		}
		if (measure_unit == MEAS_UA)//uA
		{
			unit_facotr = 1e6;
		}
		if (measure_unit == MEAS_NA)//nA
		{
			unit_facotr = 1e9;
		}

		loop_done = true;
		delay_ms(delay_time_ms);
		fxvi_res.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			meas_value[site] = fxvi_res.GetMeasResult(site, MIRET) * unit_facotr;//A
			if (lp == 0 || failflag[site] == true)// first time measure value or last measure cannot pass, will update test value
			{
				results[site] = meas_value[site];
			}
			if (meas_value[site] < low_limit || meas_value[site] > high_limit)
			{
				failflag[site] = true;
			}
			else
			{
				failflag[site] = false;// test value pass limit, no need to loop for this site
			}
		}

		FOR_EACH_VALID_SITE(site)
		{
			if (failflag[site])
			{
				loop_done = false;// any site not pass , need to loop, cannot stop
			}
		}
		if (loop_done)
		{
			lp = time_out_ms / delay_time_ms;
		}
	}
}

void Retest_voltage_unstable_with_time_out(ACM200 &acm_res, double *results, double low_limit_V, double high_limit_V, int delay_time_ms, int time_out_ms, REMEASURE_VOL_UNIT measure_unit)
{
	bool failflag[SITE_NUM] = { 0 };
	bool loop_done = false;
	double measV[SITE_NUM] = { 0 };

	double unit_facotr = 1;
	if (measure_unit == MEAS_V)//A
	{
		unit_facotr = 1;
	}
	if (measure_unit == MEAS_MV)//mA
	{
		unit_facotr = 1e3;
	}

	for (int lp = 0; lp < time_out_ms / delay_time_ms; lp++)
	{
		loop_done = true;
		delay_ms(delay_time_ms);
		acm_res.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			measV[site] = acm_res.GetMeasResult(site, MVRET)*unit_facotr;//V
			results[site] = measV[site];
			if (measV[site] < low_limit_V || measV[site] > high_limit_V)
			{
				failflag[site] = true;
			}
			else
			{
				failflag[site] = false;
			}
		}

		FOR_EACH_VALID_SITE(site)
		{
			if (failflag[site])
			{
				loop_done = false;
			}
		}
		if (loop_done)
		{
			lp = time_out_ms / delay_time_ms;
		}
	}
}

void Retest_voltage_unstable_with_time_out(FOVIe &fovi_res, double *results, double low_limit_V, double high_limit_V, int delay_time_ms, int time_out_ms, REMEASURE_VOL_UNIT measure_unit)
{
	bool failflag[SITE_NUM] = { 0 };
	bool loop_done = false;
	double measV[SITE_NUM] = { 0 };
	double unit_facotr = 1;
	if (measure_unit == MEAS_V)//A
	{
		unit_facotr = 1;
	}
	if (measure_unit == MEAS_MV)//mA
	{
		unit_facotr = 1e3;
	}
	for (int lp = 0; lp < time_out_ms / delay_time_ms; lp++)
	{
		loop_done = true;
		delay_ms(delay_time_ms);
		fovi_res.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			measV[site] = fovi_res.GetMeasResult(site, MVRET)*unit_facotr;//V
			results[site]=measV[site];
			if (measV[site] < low_limit_V || measV[site] > high_limit_V)
			{
				failflag[site] = true;
			}
			else
			{
				failflag[site] = false;
			}
		}

		FOR_EACH_VALID_SITE(site)
		{
			if (failflag[site])
			{
				loop_done = false;
			}
		}
		if (loop_done)
		{
			lp = time_out_ms / delay_time_ms;
		}
	}
}

void Retest_voltage_unstable_with_time_out(FXVIe_PLUS& fxvi_res, double* results, double low_limit_V, double high_limit_V, int delay_time_ms, int time_out_ms, REMEASURE_VOL_UNIT measure_unit)
{
	bool failflag[SITE_NUM] = { 0 };
	bool loop_done = false;
	double measV[SITE_NUM] = { 0 };
	double unit_facotr = 1;
	if (measure_unit == MEAS_V)//A
	{
		unit_facotr = 1;
	}
	if (measure_unit == MEAS_MV)//mA
	{
		unit_facotr = 1e3;
	}
	for (int lp = 0; lp < time_out_ms / delay_time_ms; lp++)
	{
		loop_done = true;
		delay_ms(delay_time_ms);
		fxvi_res.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			measV[site] = fxvi_res.GetMeasResult(site, MVRET) * unit_facotr;//V
			results[site] = measV[site];
			if (measV[site] < low_limit_V || measV[site] > high_limit_V)
			{
				failflag[site] = true;
			}
			else
			{
				failflag[site] = false;
			}
		}

		FOR_EACH_VALID_SITE(site)
		{
			if (failflag[site])
			{
				loop_done = false;
			}
		}
		if (loop_done)
		{
			lp = time_out_ms / delay_time_ms;
		}
	}
}

void copper_trace_check_after_leakage_measure(ACM200 &acm_res, bool *fail_flag, double *results, double low_limit, double high_limit, REMEASURE_CURR_UNIT measure_unit)
{
	double p2p_measure[SITE_NUM] = { 0 };
	double p2p_leak_post[SITE_NUM] = { 0 };
	bool copper_trace_flag[SITE_NUM] = { 0 };
	double unit_factor = 1;
	if (measure_unit == MEAS_A)
	{
		unit_factor = 1;
	}
	if (measure_unit == MEAS_MA)
	{
		unit_factor = 1e3;
	}
	if (measure_unit == MEAS_UA)
	{
		unit_factor = 1e6;
	}
	if (measure_unit == MEAS_NA)
	{
		unit_factor = 1e9;
	}
	FOR_EACH_VALID_SITE(site)
	{
		results[site] = acm_res.GetMeasResult(site, MIRET)*unit_factor;
		copper_trace_flag[site] = fail_flag[site];
		if (!copper_trace_flag[site])
		{
			BEGIN_SINGLE_SITE(site)
				p2p_measure[site] = acm_res.GetMeasResult(site, MIRET)*unit_factor;
				if (p2p_measure[site]<low_limit || p2p_measure[site]>high_limit)
				{
					acm_res.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);
					acm_res.Set(FI, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);
					acm_res.Set(FI, -0.01, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);
					delay_ms(5);
					acm_res.Set(FI, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);
					acm_res.Set(FV, 0, ACM200_3p6V, ACM200_100MA, ACM200_RELAY_ON);
					acm_res.Set(FV, 0, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);
					acm_res.Set(FV, 0.05, ACM200_3p6V, ACM200_10UA, ACM200_RELAY_ON);
					delay_ms(1);
					acm_res.MeasureVI(50, 5);
					p2p_leak_post[site] = acm_res.GetMeasResult(site, MIRET)*unit_factor;
					results[site] = p2p_leak_post[site];
					if (p2p_leak_post[site] > low_limit && p2p_leak_post[site] < high_limit)
					{
						fail_flag[site] = true;
					}
					else
					{
						fail_flag[site] = false;
					}
				}
			END_SINGLE_SITE();
		}
	}
}

void copper_trace_check_after_leakage_measure(FOVIe &fovi_res, bool *fail_flag, double *results, double low_limit, double high_limit, REMEASURE_CURR_UNIT measure_unit)
{
	double p2p_measure[SITE_NUM] = { 0 };
	double p2p_leak_post[SITE_NUM] = { 0 };
	bool copper_trace_flag[SITE_NUM] = { 0 };
	double unit_factor = 1;
	if (measure_unit == MEAS_A)
	{
		unit_factor = 1;
	}
	if (measure_unit == MEAS_MA)
	{
		unit_factor = 1e3;
	}
	if (measure_unit == MEAS_UA)
	{
		unit_factor = 1e6;
	}
	if (measure_unit == MEAS_NA)
	{
		unit_factor = 1e9;
	}
	FOR_EACH_VALID_SITE(site)
	{
		results[site] = fovi_res.GetMeasResult(site, MIRET)*unit_factor;
		copper_trace_flag[site] = fail_flag[site];
		if (!copper_trace_flag[site])
		{
			BEGIN_SINGLE_SITE(site)
				p2p_measure[site] = fovi_res.GetMeasResult(site, MIRET)*unit_factor;
			if (p2p_measure[site]<low_limit || p2p_measure[site]>high_limit)
			{
				fovi_res.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
				fovi_res.Set(FI, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
				fovi_res.Set(FI, -0.01, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
				delay_ms(5);
				fovi_res.Set(FI, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
				fovi_res.Set(FV, 0, FOVIe_2V, FOVIe_100MA, FOVIe_RELAY_ON);
				fovi_res.Set(FV, 0, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
				fovi_res.Set(FV, 0.05, FOVIe_2V, FOVIe_10UA, FOVIe_RELAY_ON);
				delay_ms(1);
				fovi_res.MeasureVI(50, 5);
				p2p_leak_post[site] = fovi_res.GetMeasResult(site, MIRET)*unit_factor;
				results[site] = p2p_leak_post[site];
				if (p2p_leak_post[site] > low_limit && p2p_leak_post[site] < high_limit)
				{
					fail_flag[site] = true;
				}
				else
				{
					fail_flag[site] = false;
				}
			}
			END_SINGLE_SITE();
		}
	}
}

void copper_trace_check_after_leakage_measure(FXVIe_PLUS& fxvi_res, bool* fail_flag, double* results, double low_limit, double high_limit, REMEASURE_CURR_UNIT measure_unit)
{
	double p2p_measure[SITE_NUM] = { 0 };
	double p2p_leak_post[SITE_NUM] = { 0 };
	bool copper_trace_flag[SITE_NUM] = { 0 };
	double unit_factor = 1;
	if (measure_unit == MEAS_A)
	{
		unit_factor = 1;
	}
	if (measure_unit == MEAS_MA)
	{
		unit_factor = 1e3;
	}
	if (measure_unit == MEAS_UA)
	{
		unit_factor = 1e6;
	}
	if (measure_unit == MEAS_NA)
	{
		unit_factor = 1e9;
	}
	FOR_EACH_VALID_SITE(site)
	{
		results[site] = fxvi_res.GetMeasResult(site, MIRET) * unit_factor;
		copper_trace_flag[site] = fail_flag[site];
		if (!copper_trace_flag[site])
		{
			BEGIN_SINGLE_SITE(site)
				p2p_measure[site] = fxvi_res.GetMeasResult(site, MIRET) * unit_factor;
			if (p2p_measure[site]<low_limit || p2p_measure[site]>high_limit)
			{
				fxvi_res.Set(FV, 0, FXVIe_PLUS_3p6V, FXVIe_PLUS_10UA, FXVIe_PLUS_RELAY_ON);
				fxvi_res.Set(FI, 0, FXVIe_PLUS_3p6V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
				fxvi_res.Set(FI, -0.01, FXVIe_PLUS_3p6V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
				delay_ms(5);
				fxvi_res.Set(FI, 0, FXVIe_PLUS_3p6V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
				fxvi_res.Set(FV, 0, FXVIe_PLUS_3p6V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);
				fxvi_res.Set(FV, 0, FXVIe_PLUS_3p6V, FXVIe_PLUS_10UA, FXVIe_PLUS_RELAY_ON);
				fxvi_res.Set(FV, 0.05, FXVIe_PLUS_3p6V, FXVIe_PLUS_10UA, FXVIe_PLUS_RELAY_ON);
				delay_ms(1);
				fxvi_res.MeasureVI(50, 5);
				p2p_leak_post[site] = fxvi_res.GetMeasResult(site, MIRET) * unit_factor;
				results[site] = p2p_leak_post[site];
				if (p2p_leak_post[site] > low_limit && p2p_leak_post[site] < high_limit)
				{
					fail_flag[site] = true;
				}
				else
				{
					fail_flag[site] = false;
				}
			}
			END_SINGLE_SITE();
		}
	}
}

std::string extractBeforeDelimiter(const std::string& input, char delimiter) {
	size_t pos = input.find(delimiter);
	if (pos != std::string::npos) {
		return input.substr(0, pos);
	}
	return input; // ���û���ҵ��ָ���������ԭ�ַ���
}

bool containsSubstringC(const char* mainStr, const char* subStr) 
{
	return strstr(mainStr, subStr) != nullptr;
}

bool findDevicePrefix(const std::vector<std::string>& device_list, const std::string& target, std::string& result) 
{
	// ��ȡĿ���ַ�����"-"ǰ����
	size_t dash_pos = target.find('-');
	if (dash_pos == std::string::npos) {
		return false;
	}
	std::string prefix = target.substr(0, dash_pos);

	// ��vector�в���ƥ����
	auto it = std::find(device_list.begin(), device_list.end(), prefix);
	if (it != device_list.end()) {
		result = prefix;
		return true;
	}
	return false;
}

bool IsFirstLoop()
{
	bool flag = false;
	if (!LOOP_COUNT)
	{
		flag= true;
	}
	return flag;
}

void check_awg_trigger_point(double * trig_pnt, int sam_pnt, double *ramp_trig_value1, double *ramp_trig_value2, int site)
{
		if (trig_pnt[site]<1 || trig_pnt[site]>sam_pnt - 2)
		{
			ramp_trig_value1[site] = 99999;
			ramp_trig_value2[site] = 99999;
		}
}
void check_awg_trigger_point(int * trig_pnt, int sam_pnt, double *ramp_trig_value1, double *ramp_trig_value2, int site)
{
		if (trig_pnt[site]<1 || trig_pnt[site]>sam_pnt - 2)
		{
			ramp_trig_value1[site] = 99999;
			ramp_trig_value2[site] = 99999;
		}
}
void check_awg_trigger_point(double * trig_pnt, int sam_pnt, double *ramp_trig_value1, int site )
{
		if (trig_pnt[site]<1 || trig_pnt[site]>sam_pnt - 2)
		{
			ramp_trig_value1[site] = 99999;
		}
}
void check_awg_trigger_point(int * trig_pnt, int sam_pnt, double *ramp_trig_value1, int site)
{
		if (trig_pnt[site]<1 || trig_pnt[site]>sam_pnt - 2)
		{
			ramp_trig_value1[site] = 99999;
		}
}

// ===================================================================
// DALI: measure_bandgap �� TM139 Trim_VBG ���� (VDM MV, ���� mV)
// treg: bandgap, 16��(Table 0-15, ASSY F0 bits 0-3)
// ����: VDM_SDA_ACM MV (���÷����� FI=0 ����), MVRET �� 1e3 �� mV
// �Ĵ����� test.cpp ������: 0x10=0x43, 0x57=0x02, 0x5E=0x0C (ATEST0_MUX=12 �� VBG)
// ===================================================================
void measure_bandgap(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
	DWORD working_value1[SITE_NUM] = { 0 };

	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
	{
		FOR_EACH_SITE(site)
		{
			if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
				if (BURN_FLAG[site] == BURNNED)
					trim_node->copy_read_to_work(site);
			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F0").get_working(site);
		}

		// д�� EFUSE trim ֵ (bandgap 16�� �� F0 bits 0-3)
		dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, working_value1);
		delay_ms(2);

		// VDM_SDA_ACM MV���� (FI=0 ����, ����10UA)
		VDM_SDA_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			results[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET) * 1e3;  // V �� mV
		}
	}
}

// ===================================================================
// DALI: measure_bg_res_div �� TM135 Trim_BG_RES_DIV ���� (VDM MV, ���� mV)
// treg: bg_res_div, 8��(Table 0-7, ASSY F1 bits 2-4)
// ����: VDM_SDA_ACM MV (���÷����� FI=0 ����), MVRET �� 1e3 �� mV
// �Ĵ����� test.cpp ������: 0x10=0x43, 0x57=0x02, 0x5E=0x0A (ATEST0_MUX=10 �� BG_RES_DIV)
// ===================================================================
void measure_bg_res_div(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
	DWORD working_value1[SITE_NUM] = { 0 };

	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
	{
		FOR_EACH_SITE(site)
		{
			if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
				if (BURN_FLAG[site] == BURNNED)
					trim_node->copy_read_to_work(site);
			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F1").get_working(site);
		}

		// д�� EFUSE trim ֵ (bg_res_div 8�� �� F1 bits 2-4)
		dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, working_value1);
		delay_ms(2);

		// VDM_SDA_ACM MV���� (FI=0 ����, ����10UA)
		VDM_SDA_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			results[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET) * 1e3;  // V �� mV
		}
	}
}

// ===================================================================
// DALI: measure_iztc_res �� TM133 Trim_IZTC_RES ���� (VDM MI, ���� uA ������)
// treg: iztc_res, 64��(Table 0-63, ASSY F0 bits 4-7 + F1 bits 0-1)
// ����: VDM_SDA_ACM MI (���÷����� FV=1V), MIRET �� 1e6 �� uA (IZTC ������ �� -1)
// �Ĵ����� test.cpp ������: 0x10=0x43, 0x57=0x02, 0x5E=0x08 (ATEST0_MUX=8 �� IZTC_RES)
// ===================================================================
void measure_iztc_res(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
	DWORD working_value1[SITE_NUM] = { 0 };
	DWORD working_value2[SITE_NUM] = { 0 };

	if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
	{
		FOR_EACH_SITE(site)
		{
			if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
				if (BURN_FLAG[site] == BURNNED)
					trim_node->copy_read_to_work(site);
			working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F0").get_working(site);
			working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F1").get_working(site);
		}

		// д�� EFUSE trim ֵ (iztc_res 64�� �� F0 bits 4-7 + F1 bits 0-1)
		dcm.I2CWriteData(DEV_ADDR, 0xF0, 1, working_value1);
		dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, working_value2);
		delay_ms(2);

		// VDM_SDA_ACM MI���� (FV=1V, ����10UA), ���� uA
		VDM_SDA_ACM.MeasureVI(50, 5);
		FOR_EACH_VALID_SITE(site)
		{
			results[site] = -1 * VDM_SDA_ACM.GetMeasResult(site, MIRET) * 1e6;  // A �� uA (IZTC ��������ȡ��)
		}
	}
}


// ===================================================================
// DALI: measure_osc_4p5m - TM301 Trim_OSC_4P5M (QTMU ��Ƶ, �ع� MHz)
// treg: osc_4p5m, 16��(Table 0-15, 0xF1 bits 7-5 + 0xF2 bit0), Target=4.5MHz
// ����: д EFUSE trim ֵ (0xF1/0xF2) -> QTMU �� foldback ~35KHz -> x0.128 �ع� 4.5MHz
// �Ĵ��������� test.cpp: 0x10=0x43, 0x56=0x33, 0x57=0x08 (DMUX_SEL=51)
// ===================================================================
void measure_osc_4p5m(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
    DWORD working_value1[SITE_NUM] = { 0 };
    DWORD working_value2[SITE_NUM] = { 0 };
    double qtmu_results[SITE_NUM] = { 0 };

    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
    {
        FOR_EACH_SITE(site)
        {
            if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F1").get_working(site);
            working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F2").get_working(site);
        }

        // д EFUSE trim ֵ (osc_4p5m 16��: 0xF1 bits 7-5 + 0xF2 bit0)
        dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, working_value1);
        dcm.I2CWriteData(DEV_ADDR, 0xF2, 1, working_value2);
        delay_us(1000);

        // QTMU ��Ƶ (nQON -> CHA), �ĵ��� API ��� QTMU_GP_MEASURE ��
        QTMU_GP.Connect(QTMUe_RELAY_CHA, 500);
        QTMU_GP.SetInSource(QTMUe_SINGLE_SOURCE_A);
        QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.0, QTMUe_FILTER_PASS);
        QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 20, 10, QTMUe_TRANGE_US);
        FOR_EACH_VALID_SITE(site)
        {
            qtmu_results[site] = QTMU_GP.GetMeasureResult(site, AVERAGE_RESULT, QTMUe_MU1);  // KHz
            results[site] = qtmu_results[site] * 0.128;  // KHz->MHz �ع� (foldback /128)
        }
        QTMU_GP.Disconnect(QTMUe_RELAY_CHA, 100);
    }
}

// ===================================================================
// DALI: measure_osc_64k - TM300 Trim_OSC_64K (QTMU ��Ƶ, KHz)
// [����ȱ��] treg �� [osc_64k] �� (�ѱ���); D2A_OSC_64K_TRIM 3bit -> 8��
//   �ݰ� reg_config 0xF2 д�� (�� TRIM_REG 0xF2 �ֶζ���ì��, ���û�ȷ��)
// ����: д 0xF2 -> QTMU �� 64KHz ֱ��Ƶ�� (�� foldback, Test=Direct)
// �Ĵ��������� test.cpp: 0x56=0x0C, 0x57=0x08 (DMUX_SEL=12)
// ===================================================================
void measure_osc_64k(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
    DWORD working_value1[SITE_NUM] = { 0 };

    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
    {
        FOR_EACH_SITE(site)
        {
            if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F2").get_working(site);
        }

        // д EFUSE trim ֵ (osc_64k 8��: 0xF2, ��ȷ��)
        dcm.I2CWriteData(DEV_ADDR, 0xF2, 1, working_value1);
        delay_us(1000);

        // QTMU ��Ƶ (nQON -> CHA), �ĵ��� API ��� QTMU_GP_MEASURE ��
        QTMU_GP.Connect(QTMUe_RELAY_CHA, 500);
        QTMU_GP.SetInSource(QTMUe_SINGLE_SOURCE_A);
        QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.0, QTMUe_FILTER_PASS);
        QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 20, 10, QTMUe_TRANGE_US);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = QTMU_GP.GetMeasureResult(site, AVERAGE_RESULT, QTMUe_MU1);  // KHz
        }
        QTMU_GP.Disconnect(QTMUe_RELAY_CHA, 100);
    }
}
// ===================================================================
// DALI: measure_mnt_vbat_rsns_loop �� TM422 VBAT_FB ���� (VDM MV, ���� mV)
// treg: mnt_vbat_rsns_loop, 16��(Table 0-15)
// ����: VDM_SDA_ACM MV (���÷����� FI=0 ����), (V(FB_VBAT)-2.0)*1e3 mV ƫ�� (VBAT=5V, FB=VBAT*2/5=2V, target=0)
// �Ĵ����� test.cpp ������: 0x10=0x43, 0x57=0x02, 0x5E=0x17 (ATEST0_MUX=23=FB_VBAT)
// ===================================================================
void measure_mnt_vbat_rsns_loop(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
    DWORD working_value1[SITE_NUM] = { 0 };
    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
    {
        FOR_EACH_SITE(site)
        {
            if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F7").get_working(site);
        }

        // д�� EFUSE trim ֵ
        dcm.I2CWriteData(DEV_ADDR, 0xF7, 1, working_value1);
        delay_ms(2);

        // VDM_SDA_ACM MV���� (FI=0 ����, ����10UA)
        VDM_SDA_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = (VDM_SDA_ACM.GetMeasResult(site, MVRET) - 2.0) * 1e3;  // V �� mV (FB_VBAT ƫ��);
        }
    }
}

// ===================================================================
// DALI: measure_mnt_dac_buf_os �� TM424 VREF_TRIM ���� (VDM MV, ���� mV)
// treg: mnt_dac_buf_os, 32��(Table 0-31)
// ����: VDM_SDA_ACM MV (���÷����� FI=0 ����), MVRET*1e3 mV (target=1680mV)
// �Ĵ����� test.cpp ������: 0x10=0x43, 0x57=0x02, 0x5E=0x13 (ATEST0_MUX=19=VREF_1P68V)
// ===================================================================
void measure_mnt_dac_buf_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
    DWORD working_value1[SITE_NUM] = { 0 };
    DWORD working_value2[SITE_NUM] = { 0 };
    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
    {
        FOR_EACH_SITE(site)
        {
            if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F7").get_working(site);
            working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F8").get_working(site);
        }

        // д�� EFUSE trim ֵ
        dcm.I2CWriteData(DEV_ADDR, 0xF7, 1, working_value1);
        dcm.I2CWriteData(DEV_ADDR, 0xF8, 1, working_value2);
        delay_ms(2);

        // VDM_SDA_ACM MV���� (FI=0 ����, ����10UA)
        VDM_SDA_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET) * 1e3;  // V �� mV;
        }
    }
}

// ===================================================================
// DALI: measure_mnt_v1p2_buf �� TM425 VREF_1P2V_BUF ���� (VDM MV, ���� mV)
// treg: mnt_v1p2_buf, 16��(Table 0-15)
// ����: VDM_SDA_ACM MV (���÷����� FI=0 ����), MVRET*1e3 mV (target=1200mV)
// �Ĵ����� test.cpp ������: 0x10=0x43, 0x57=0x04, 0x58=0x02 (ATEST1_MUX=2=VREF_1P2V_BUF)
// ===================================================================
void measure_mnt_v1p2_buf(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
    DWORD working_value1[SITE_NUM] = { 0 };
    DWORD working_value2[SITE_NUM] = { 0 };
    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
    {
        FOR_EACH_SITE(site)
        {
            if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F6").get_working(site);
            working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F7").get_working(site);
        }

        // д�� EFUSE trim ֵ
        dcm.I2CWriteData(DEV_ADDR, 0xF6, 1, working_value1);
        dcm.I2CWriteData(DEV_ADDR, 0xF7, 1, working_value2);
        delay_ms(2);

        // VDM_SDA_ACM MV���� (FI=0 ����, ����10UA)
        VDM_SDA_ACM.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET) * 1e3;  // V �� mV;
        }
    }
}
// ===================================================================
// measure_ibus_sns_gain — IBUS sense Gain trim measure (Boost, 两点做差)
// treg [ibus_sns_gain] Target=198mohm, 6bit=64step (0xF3[7:5] + 0xF4[2:0])
// 方法: force 1A/3A (Boost +, PMID→VBUS), VCS=V(VDM)-V(AMUX), I=|FPVI0 MIRET|
//   Gain = |ΔVCS|/|ΔI| × 1e3 (mohm), target 198
// 调用: TM702_IBUS_SNS_GAIN_TRIM execute (sub.h 已声明, 本定义与原注释 NU6801 算法对齐)
// ===================================================================
void measure_ibus_sns_gain(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
{
    double Vsense1[SITE_NUM] = { 0 };
    double Vsense2[SITE_NUM] = { 0 };
    double Imeas1[SITE_NUM] = { 0 };
    double Imeas2[SITE_NUM] = { 0 };
    DWORD working_value1[SITE_NUM] = { 0 };
    DWORD working_value2[SITE_NUM] = { 0 };
    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
    {
        FOR_EACH_SITE(site)
        {
            if (treg_measure_flag == TREG_MEASURE_PRE || treg_measure_flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F3").get_working(site);
            working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F4").get_working(site);
        }
        // 写 trim code: ibus_sns_gain = 0xF3[7:5] + 0xF4[2:0]
        dcm.I2CWriteData(DEV_ADDR, 0xF3, 1, working_value1);
        dcm.I2CWriteData(DEV_ADDR, 0xF4, 1, working_value2);
        delay_ms(2);

        // 1A 点 (Boost +, FPVIe_2A)
        FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);
        delay_ms(2);
        VDM_SDA_ACM.MeasureVI(50, 5);
        VAC123_AMUX_ACM.MeasureVI(50, 5);
        FPVI0.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            Vsense1[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET) - VAC123_AMUX_ACM.GetMeasResult(site, MVRET);  // VCS = V(VDM)-V(AMUX)
            Imeas1[site] = fabs(FPVI0.GetMeasResult(site, MIRET));
        }

        // 3A 点 (Boost +, FPVIe_10A)
        FPVI0.Set(FI, 3.0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
        delay_ms(2);
        VDM_SDA_ACM.MeasureVI(50, 5);
        VAC123_AMUX_ACM.MeasureVI(50, 5);
        FPVI0.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            Vsense2[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET) - VAC123_AMUX_ACM.GetMeasResult(site, MVRET);
            Imeas2[site] = fabs(FPVI0.GetMeasResult(site, MIRET));
        }
        FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
        delay_ms(1);

        // 两点做差法: Gain = |ΔVCS|/|ΔI| × 1e3 (mohm)
        FOR_EACH_VALID_SITE(site)
        {
            if (fabs(Imeas2[site] - Imeas1[site]) > 1e-6)
                results[site] = fabs(Vsense2[site] - Vsense1[site]) / fabs(Imeas2[site] - Imeas1[site]) * 1e3;  // mohm
            else
                results[site] = 0;
        }
    }
}

// ===================================================================
// measure_ibus_sns_ea_os — IBUS sense offset trim measure (Boost, 单点 2A)
// treg [ibus_sns_ea_os] Target=0mV, 4bit=16step (0xF3[4:1])
// 方法: force 2A (Boost +, PMID→VBUS), VCS=V(VDM)-V(AMUX), I=|FPVI0 MIRET|
//   Vos = (VCS - I×0.2) × 1e3 (mV), target 0 (即 VCS trim 到最接近 2A×0.2=0.4V)
// 调用: TM703_IBUS_SNS_VOS_TRIM execute (sub.h 已声明)
// ===================================================================
void measure_ibus_sns_ea_os(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results)
{
    double Vsense1[SITE_NUM] = { 0 };
    double Imeas1[SITE_NUM] = { 0 };
    DWORD working_value1[SITE_NUM] = { 0 };
    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
    {
        FOR_EACH_SITE(site)
        {
            if (treg_measure_flag == TREG_MEASURE_PRE || treg_measure_flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F3").get_working(site);
        }
        // 写 trim code: ibus_sns_ea_os = 0xF3[4:1]
        dcm.I2CWriteData(DEV_ADDR, 0xF3, 1, working_value1);
        delay_ms(2);

        // 2A 点 (Boost +, FPVIe_10A)
        FPVI0.Set(FI, 2.0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
        delay_ms(2);
        VDM_SDA_ACM.MeasureVI(50, 5);
        VAC123_AMUX_ACM.MeasureVI(50, 5);
        FPVI0.MeasureVI(50, 5);
        FOR_EACH_VALID_SITE(site)
        {
            Vsense1[site] = VDM_SDA_ACM.GetMeasResult(site, MVRET) - VAC123_AMUX_ACM.GetMeasResult(site, MVRET);  // VCS = V(VDM)-V(AMUX)
            Imeas1[site] = fabs(FPVI0.GetMeasResult(site, MIRET));
            results[site] = (Vsense1[site] - Imeas1[site] * 0.2) * 1e3;  // mV, target 0
        }
        FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);
        delay_ms(1);
    }
}

