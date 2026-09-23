#include "stdafx.h"
#include "Test_Method.h"
#include "sub.h"
extern void iic_read(unsigned addr, int *rdata);
extern int rdata[SITE_NUM];
//extern BOOL fpvi_gp_valid(int gp_no = 0);
//extern void smart_FPVI_operation(int gp_no, VIMode mode = FI, double forcevalue = 0, FPVIe_VRNG vrange = FPVIe_5V, FPVIe_IRNG irange = FPVIe_10UA, int fpvichannel = -1);

// use for open short test classify to different bin
// pgs must include "OS_SHORT" "OS_SOME_OPEN" "OS_ALL_OPEN" "OS_LEAK"
BOOL Test_Method::OS_Classify(short funcindex, string pin_str_array[], unsigned int OS_NUM, string leak_str_array[], unsigned int LEAK_NUM, double os_result[][SITE_NUM], double leak_result[][SITE_NUM], vector<string>& vec_exclude)
{
	if (OS_NUM == 0) return FALSE;
	int open_count[SITE_NUM] = { 0 };
	int SHORT_FLAG[SITE_NUM] = { 0 };
	int ALAM_FLAG[SITE_NUM] = { 0 };//Bill
	int SOME_OPEN_FLAG[SITE_NUM] = { 0 };
	int ALL_OPEN_FLAG[SITE_NUM] = { 0 };
	int LEAK_FLAG[SITE_NUM] = { 0 };
	CParam *OS_Param;

	for (unsigned int os_count = 0; os_count < OS_NUM; ++os_count){
		if (find(vec_exclude.begin(), vec_exclude.end(), pin_str_array[os_count]) != vec_exclude.end()) continue;
		OS_Param = StsGetParam(funcindex, pin_str_array[os_count].c_str());
		double spec_l = OS_Param->GetMinLimit();
		double spec_h = OS_Param->GetMaxLimit();
		SERIAL{
			if (spec_l > 0){
				if (os_result[os_count][SITE] < spec_l)
					SHORT_FLAG[SITE] = 1;
				if (SHORT_FLAG[SITE] != 1 && (os_result[os_count][SITE] > spec_h))
					open_count[SITE]++;
			}
			if (spec_h < 0){
				if (os_result[os_count][SITE] >spec_h)
					SHORT_FLAG[SITE] = 1;
				if (os_result[os_count][SITE] >0.2)//Bill
					ALAM_FLAG[SITE] = 1;
				if (SHORT_FLAG[SITE] != 1 && (os_result[os_count][SITE] < spec_l))
					open_count[SITE]++;
			}
		}
	}

	for (unsigned int leak_count = 0; leak_count < LEAK_NUM; ++leak_count){
		OS_Param = StsGetParam(funcindex, leak_str_array[leak_count].c_str());
		double spec_l = OS_Param->GetMinLimit();
		double spec_h = OS_Param->GetMaxLimit();
		SERIAL{
			if (leak_result[leak_count][SITE] < spec_l || leak_result[leak_count][SITE] > spec_h)
			LEAK_FLAG[SITE] = 1;
		}
	}

	SERIAL    //judge some open or all open 
	{
		if (SHORT_FLAG[SITE] != 1 && open_count[SITE] == (OS_NUM - vec_exclude.size()))
		ALL_OPEN_FLAG[SITE] = 1;
		else if (SHORT_FLAG[SITE] != 1 && open_count[SITE] < (int)(OS_NUM - vec_exclude.size()) && open_count[SITE] > 0)
			SOME_OPEN_FLAG[SITE] = 1;
		if (ALAM_FLAG[SITE] == 1)
			SHORT_FLAG[SITE] = 0;
	}

	SERIAL	StsGetParam(funcindex, "OS_SHORT")->SetTestResult(SITE, 0, SHORT_FLAG[SITE]);
	SERIAL	StsGetParam(funcindex, "OS_SOME_OPEN")->SetTestResult(SITE, 0, SOME_OPEN_FLAG[SITE]);
	SERIAL	StsGetParam(funcindex, "OS_ALL_OPEN")->SetTestResult(SITE, 0, ALL_OPEN_FLAG[SITE]);
	SERIAL	StsGetParam(funcindex, "OS_ALAM")->SetTestResult(SITE, 0, ALAM_FLAG[SITE]);
	if (LEAK_NUM != 0)
	{
		SERIAL	StsGetParam(funcindex, "OS_LEAK")->SetTestResult(SITE, 0, LEAK_FLAG[SITE]);
	}

	return TRUE;
}


FOVIe_VRNG Test_Method::get_fovi_v_range(double v){
	if (v < 0)
		v = -v;
	if (v <= 1)
		return FOVIe_1V;
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

FXVIe_PLUS_VRNG Test_Method::get_fxvi_v_range(double v){
	if (v < 0)
		v = -v;
	if (v <= 1)
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


// Ramp acm current, capture acm voltage, trig stop
// Can set acm_ramp i_range 
// Good for IBAT_SNS
// fovi_cap no current loading
BOOL Test_Method::ramp(ACM acm_ramp, ACM_IRNG i_range, ACM acm_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result){
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = int(fabs((stop_point - start_point) / step));
	if ((samples <= 1) || (samples > MAX_SAMPLES)){
		samples = MAX_SAMPLES;
	}

	acm_ramp.Set(FI, start_point, ACM_N2P18V, i_range, ACM_RELAY_ON, 1);
	acm_cap.Set(FI, 0, ACM_N2P18V, ACM_5UA, ACM_RELAY_ON);

	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	acm_ramp.AwgClear();
	acm_ramp.AwgLoader("awg", FI, ACM_N2P18V, i_range, pat, samples);
	acm_ramp.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	acm_cap.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	acm_ramp.MeasureVI(ACM_MI, samples, interval, MEAS_AWG);
	acm_cap.MeasureVI(ACM_MV, samples, interval, MEAS_AWG);

	STSEnableAWG(&acm_ramp);
	STSEnableMeas(&acm_ramp, &acm_cap);
	STSAWGRunTriggerStop(&acm_cap, &acm_ramp, &acm_cap);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)acm_cap.GetMeasResult(SITE, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			//result[SITE] = start_point + (Trig_Point[SITE] - 1) * step;
			result[SITE] = acm_ramp.GetMeasResult(SITE, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}
	acm_cap.Set(FI, 0, ACM_N2P18V, ACM_5UA, ACM_RELAY_OFF);
	return TRUE;
}
// Ramp acm voltage, capture acm voltage, trig stop
// Can set acm_ramp i_range 
// Good for DPDM VTH




BOOL Test_Method::rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result, int delay_2p)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	//samples = int(fabs((stop_point - start_point) / step));
	//if ((samples <= 1) || (samples > MAX_SAMPLES)){
	//	samples = MAX_SAMPLES;
	//}
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);


	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1 - delay_2p) + delay_2p*(stop_point - start_point) / samples;
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result, int delay_2p)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	//samples = int(fabs((stop_point - start_point) / step));
	//if ((samples <= 1) || (samples > MAX_SAMPLES)){
	//	samples = MAX_SAMPLES;
	//}
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);


	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1 - delay_2p) + delay_2p*(stop_point - start_point) / samples;
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}



BOOL Test_Method::rampi_fv_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, ACM200 capret_res, ACM200_VRNG capret_vrange, ACM200_IRNG capret_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	//samples = int(fabs((stop_point - start_point) / step));
	//if ((samples <= 1) || (samples > MAX_SAMPLES)){
	//	samples = MAX_SAMPLES;
	//}
	samples = (int)step;
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	cap_res.Set(FV, 3.5, cap_vrange, cap_irange, ACM200_RELAY_ON);
	capret_res.Set(FI, 0, capret_vrange, capret_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);
	capret_res.MeasureVI(samples, interval, MEAS_AWG);
	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res, &capret_res);
	STSAWGRun();

	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = capret_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}


BOOL Test_Method::ramp_v(ACM acm_ramp, ACM_IRNG i_range, ACM acm_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result){
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = int(fabs((stop_point - start_point) / step));
	if ((samples <= 1) || (samples > MAX_SAMPLES)){
		samples = MAX_SAMPLES;
	}

	acm_ramp.Set(FV, start_point, ACM_N2P18V, i_range, ACM_RELAY_ON);
	acm_cap.Set(FI, 0, ACM_N2P18V, ACM_5UA, ACM_RELAY_ON);

	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	acm_ramp.AwgClear();
	acm_ramp.AwgLoader("awg", FV, ACM_N2P18V, i_range, pat, samples);
	acm_ramp.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	acm_cap.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	acm_ramp.MeasureVI(ACM_MV, samples, interval, MEAS_AWG);
	acm_cap.MeasureVI(ACM_MV, samples, interval, MEAS_AWG);

	STSEnableAWG(&acm_ramp);
	STSEnableMeas(&acm_ramp, &acm_cap);
	STSAWGRunTriggerStop(&acm_cap, &acm_ramp, &acm_cap);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)acm_cap.GetMeasResult(SITE, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			//result[SITE] = start_point + (Trig_Point[SITE] - 1) * step;
			result[SITE] = acm_ramp.GetMeasResult(SITE, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}


// Ramp fovie voltage, capture acm voltage, trig stop
// Can set fovi_ramp v_range and i_range 
// Good for UVLO, threshold, power good measurement
// fovi_cap no current loading
BOOL Test_Method::ramp(FOVIe fovi_ramp, FOVIe_VRNG v_range, FOVIe_IRNG i_range, ACM acm_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result){
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = int(fabs((stop_point - start_point) / step));
	if ((samples <= 1) || (samples > MAX_SAMPLES)){
		samples = MAX_SAMPLES;
	}

	fovi_ramp.Set(FV, start_point, v_range, i_range, FOVIe_RELAY_ON, 1);
	acm_cap.Set(FI, 0, ACM_N2P18V, ACM_5UA, ACM_RELAY_ON);

	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	fovi_ramp.AwgClear();
	fovi_ramp.AwgLoader("awg", FV, v_range, i_range, pat, samples);
	fovi_ramp.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	acm_cap.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	fovi_ramp.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	acm_cap.MeasureVI(ACM_MV, samples, interval, MEAS_AWG);

	STSEnableAWG(&fovi_ramp);
	STSEnableMeas(&fovi_ramp, &acm_cap);
	STSAWGRunTriggerStop(&acm_cap, &acm_cap, &fovi_ramp);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)acm_cap.GetMeasResult(SITE, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			//result[SITE] = start_point + (Trig_Point[SITE] - 1) * step;
			result[SITE] = fovi_ramp.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}
	acm_cap.Set(FI, 0, ACM_N2P18V, ACM_5UA, ACM_RELAY_OFF);
	return TRUE;
}

// Ramp 2 fovie voltage, capture acm voltage, trig stop
// Can set fovi_ramp v_range and i_range 
// Good for UVLO, threshold, power good measurement
// fovi_cap no current loading
BOOL Test_Method::ramp(FOVIe fovi_ramp, FOVIe fovi_ramp1, FOVIe_VRNG v_range, FOVIe_IRNG i_range, ACM acm_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result){
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = int(fabs((stop_point - start_point) / step));
	if ((samples <= 1) || (samples > MAX_SAMPLES)){
		samples = MAX_SAMPLES;
	}

	fovi_ramp.Set(FV, start_point, v_range, i_range, FOVIe_RELAY_ON, 1);
	fovi_ramp1.Set(FV, start_point, v_range, i_range, FOVIe_RELAY_ON, 1);
	acm_cap.Set(FI, 0, ACM_N2P18V, ACM_5UA, ACM_RELAY_ON);

	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	fovi_ramp.AwgClear();
	fovi_ramp1.AwgClear();
	fovi_ramp.AwgLoader("awg", FV, v_range, i_range, pat, samples);
	fovi_ramp1.AwgLoader("awg", FV, v_range, i_range, pat, samples);
	fovi_ramp.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	fovi_ramp1.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	acm_cap.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	fovi_ramp.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	fovi_ramp1.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	acm_cap.MeasureVI(ACM_MV, samples, interval, MEAS_AWG);

	STSEnableAWG(&fovi_ramp, &fovi_ramp1);
	STSEnableMeas(&fovi_ramp, &fovi_ramp1, &acm_cap);
	STSAWGRunTriggerStop(&acm_cap, &fovi_ramp, &fovi_ramp1, &acm_cap);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)acm_cap.GetMeasResult(SITE, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			//result[SITE] = start_point + (Trig_Point[SITE] - 1) * step;
			result[SITE] = fovi_ramp.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}



// Ramp fovie voltage, capture acm voltage, trig stop
// Can set fovi_ramp v_range and i_range 
// Good for UVLO, threshold, power good measurement
// capture acm has current loading
BOOL Test_Method::ramp(FOVIe fovi_ramp, FOVIe_VRNG v_range, FOVIe_IRNG i_range, ACM acm_cap, ACM_IRNG acm_i_range, double loading, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result){
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = int(fabs((stop_point - start_point) / step));
	if ((samples <= 1) || (samples > MAX_SAMPLES)){
		samples = MAX_SAMPLES;
	}

	fovi_ramp.Set(FV, start_point, v_range, i_range, FOVIe_RELAY_ON, 1);
	acm_cap.Set(FI, loading, ACM_N2P18V, acm_i_range, ACM_RELAY_ON);

	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	fovi_ramp.AwgClear();
	fovi_ramp.AwgLoader("awg", FV, v_range, i_range, pat, samples);
	fovi_ramp.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	acm_cap.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	fovi_ramp.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	acm_cap.MeasureVI(ACM_MV, samples, interval, MEAS_AWG);

	STSEnableAWG(&fovi_ramp);
	STSEnableMeas(&fovi_ramp, &acm_cap);
	STSAWGRunTriggerStop(&acm_cap, &fovi_ramp, &acm_cap);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)acm_cap.GetMeasResult(SITE, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			//result[SITE] = start_point + (Trig_Point[SITE] - 1) * step;
			result[SITE] = fovi_ramp.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}
	acm_cap.Set(FI, 0, ACM_N2P18V, acm_i_range, ACM_RELAY_ON);

	return TRUE;
}


// FOR IBUS
BOOL Test_Method::ramp(FPVIe fpvi_ramp1, FPVIe fpvi_ramp2, FPVIe fpvi_gp_bysite_qb[][SITE_NUM], FPVIe_VRNG v_range, FPVIe_IRNG i_range, ACM acm_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result){
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples = 0;
	int start_sample = 0;
	int stop_sample = 0;

	samples = int(fabs((stop_point - start_point) / 2 / step + 1));
	start_sample = int(fabs((start_point / 2 - 0) / step + 1));
	stop_sample = int(fabs((stop_point / 2 - 0) / step + 1));
	if ((samples <= 1) || (samples > MAX_SAMPLES)){
		samples = MAX_SAMPLES;
		return FALSE;
	}

	acm_cap.Set(FI, 0, ACM_N2P18V, ACM_20UA, ACM_RELAY_ON);
	for (int gp_no = 0; gp_no<FPVI_GP_NUM; ++gp_no)
	{
		if (!fpvi_gp_valid(gp_no)){
			SERIAL_GP_FPVI{
				result[SITE] = ERROR_RES;
			}
			continue;
		}
		if (gp_no == 0)
		{
			////cbite.SetOn(K_QB_GP_odd, K1_CVAC1, K3_CVBUS, K2_CVAC2, K5_CPMID, K7_CVOUT, K16_CREGN, K19_INT_ACM, K17_FOVI_SVAC1, K47_FOVI_SVAC2, K18_INT_V5V ,-1);
			delay_ms(5);
		}
		if (gp_no == 1)
		{
			////cbite.SetOn(K_QB_GP_even, K1_CVAC1, K3_CVBUS, K2_CVAC2, K5_CPMID, K7_CVOUT, K16_CREGN, K19_INT_ACM, K17_FOVI_SVAC1, K47_FOVI_SVAC2, K18_INT_V5V, -1);
			delay_ms(5);
		}
		SERIAL_GP_FPVI{
			for (int i = 0; i < 2; ++i)
			{
				fpvi_gp_bysite_qb[i][SITE].AwgSelect("fpvi_10A_ramp_up", start_sample, stop_sample - 1, stop_sample - 1, interval);
				fpvi_gp_bysite_qb[i][SITE].MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
			}
		}
			//smartfpvi01->Set(FI, start_point / 2.0, v_range, i_range, FPVIe_RELAY_ON);
		delay_ms(3);
		acm_cap.SetMeasVTrig(trig_level, trig_mode);
		acm_cap.MeasureVI(ACM_MV, samples, interval, MEAS_AWG);

		SERIAL_GP_FPVI{
			STSEnableAWG(&fpvi_gp_bysite_qb[0][SITE], &fpvi_gp_bysite_qb[1][SITE]);
			STSEnableMeas(&fpvi_gp_bysite_qb[0][SITE], &fpvi_gp_bysite_qb[1][SITE]);
		}
		STSEnableMeas(&acm_cap);
		STSAWGRunTriggerStop(&acm_cap, &acm_cap);
		for (int i = 0; i < 2; ++i){
			SERIAL_GP_FPVI fpvi_gp_bysite_qb[i][SITE].AwgStop();
		}
		delay_us(TRIG_DELAY);
		int Trig_Point[SITE_NUM];
		SERIAL_GP_FPVI{
			Trig_Point[SITE] = (int)acm_cap.GetMeasResult(SITE, TRIG_RESULT);
			if ((Trig_Point[SITE] > 1) && (Trig_Point[SITE] < samples - 1)){
				result[SITE] = fpvi_gp_bysite_qb[0][SITE].GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1) + fpvi_gp_bysite_qb[1][SITE].GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
			}
			else
				result[SITE] = ERROR_RES;
		}

			//smartfpvi01->Set(FI, 0, v_range, i_range, FPVIe_RELAY_ON);
		delay_ms(2);
		// smartfpvi01->Set(FI, 0, FPVIe_1V, FPVIe_1MA, FPVIe_RELAY_OFF);
		////cbite.SetOn( K1_CVAC1, K3_CVBUS, K2_CVAC2, K5_CPMID, K7_CVOUT, K16_CREGN, K19_INT_ACM, K17_FOVI_SVAC1, K47_FOVI_SVAC2, K18_INT_V5V, -1);
		delay_ms(2);

		//	smart_FPVI_operation_init();

	}
	acm_cap.Set(FI, 0, ACM_N2P18V, ACM_20UA, ACM_RELAY_OFF);
	/*   for (int i = 0; i < FOVI_NUM; i++)
	fovie_list[i].Set(FV, 0, FOVIe_1V, FOVIe_1MA, FXVIe_PLUS_RELAY_OFF);	*/
	return TRUE;
}



// Ramp fovi voltage, capture fovi current, trig stop
// Can set fovi_ramp i_range 
// Good for VALWAYS
BOOL Test_Method::ramp_I(FOVIe fovi_ramp, FOVIe_VRNG v_range, FOVIe_IRNG i_range, FOVIe fovi_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double* result) {
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = int(fabs((stop_point - start_point) / step));
	if ((samples <= 1) || (samples > MAX_SAMPLES)) {
		samples = MAX_SAMPLES;
	}

	fovi_ramp.Set(FV, start_point, v_range, i_range, FOVIe_RELAY_ON);
	fovi_cap.Set(FV, 4, FOVIe_10V, FOVIe_1MA, FOVIe_RELAY_ON);

	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	fovi_ramp.AwgClear();
	fovi_ramp.AwgLoader("awg", FV, v_range, i_range, pat, samples);
	fovi_ramp.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	fovi_cap.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	fovi_ramp.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	fovi_cap.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&fovi_ramp);
	STSEnableMeas(&fovi_ramp, &fovi_cap);
	STSAWGRunTriggerStop(&fovi_cap, &fovi_ramp, &fovi_cap);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)fovi_cap.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)) {
			//result[SITE] = start_point + (Trig_Point[SITE] - 1) * step;
			result[SITE] = fovi_ramp.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}
// FOR IBUS_UCP
BOOL Test_Method::ramp_ucp(FPVIe fpvi_ramp1, FPVIe fpvi_ramp2, FPVIe fpvi_gp_bysite_qb[][SITE_NUM], FPVIe_VRNG v_range, FPVIe_IRNG i_range, ACM acm_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result){
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples = 0;
	int start_sample = 0;
	int stop_sample = 0;
	samples = int(fabs((stop_point - start_point) / 2 / step + 1));
	if (stop_point > start_point){  // ramp up
		start_sample = int(fabs((start_point / 2 - (-1)) / step + 1));
		stop_sample = int(fabs((stop_point / 2 - (-1)) / step + 1));
	}
	else { // down
		start_sample = int(fabs((start_point / 2 - 1) / step + 1));
		stop_sample = int(fabs((stop_point / 2 - 1) / step + 1));
	}
	if ((samples <= 1) || (samples > MAX_SAMPLES)){
		samples = MAX_SAMPLES;
		return FALSE;
	}


	acm_cap.Set(FI, 0, ACM_N2P18V, ACM_20UA, ACM_RELAY_ON);
	for (int gp_no = 0; gp_no<FPVI_GP_NUM; ++gp_no){
		if (!fpvi_gp_valid(gp_no)){
			SERIAL_GP_FPVI{
				result[SITE] = ERROR_RES;
			}
			continue;
		}
		if (gp_no == 0)
		{
			////cbite.SetOn(K_QB_GP_odd, K1_CVAC1, K3_CVBUS, K2_CVAC2, K5_CPMID, K7_CVOUT, K16_CREGN, K19_INT_ACM, K17_FOVI_SVAC1, K18_INT_V5V, -1);
			delay_ms(2);
		}
		if (gp_no == 1)
		{

			////cbite.SetOn(K_QB_GP_even, K1_CVAC1, K3_CVBUS, K2_CVAC2, K5_CPMID, K7_CVOUT, K16_CREGN, K19_INT_ACM, K17_FOVI_SVAC1, K18_INT_V5V, -1);
			delay_ms(2);

		}

		SERIAL_GP_FPVI{
			for (int i = 0; i < 2; ++i){
				if (stop_point > start_point){  // ramp up
					fpvi_gp_bysite_qb[i][SITE].AwgSelect("fpvi_1A_ramp_up", start_sample, stop_sample - 1, stop_sample - 1, interval);
				}
				else { // ramp down
					fpvi_gp_bysite_qb[i][SITE].AwgSelect("fpvi_1A_ramp_down", start_sample, stop_sample - 1, stop_sample - 1, interval);
				}
				fpvi_gp_bysite_qb[i][SITE].MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
			}
		}
			//smartfpvi01->Set(FI, start_point / 2.0, v_range, i_range, FPVIe_RELAY_ON);
		delay_ms(1);
		acm_cap.SetMeasVTrig(trig_level, trig_mode);
		acm_cap.MeasureVI(ACM_MV, samples, interval, MEAS_AWG);

		SERIAL_GP_FPVI{
			STSEnableAWG(&fpvi_gp_bysite_qb[0][SITE], &fpvi_gp_bysite_qb[1][SITE]);
			STSEnableMeas(&fpvi_gp_bysite_qb[0][SITE], &fpvi_gp_bysite_qb[1][SITE]);
		}
		STSEnableMeas(&acm_cap);
		STSAWGRunTriggerStop(&acm_cap, &acm_cap);
		for (int i = 0; i < 2; ++i){
			SERIAL_GP_FPVI fpvi_gp_bysite_qb[i][SITE].AwgStop();
		}
		delay_us(TRIG_DELAY);
		int Trig_Point[SITE_NUM];
		SERIAL_GP_FPVI{
			Trig_Point[SITE] = (int)acm_cap.GetMeasResult(SITE, TRIG_RESULT);
			if ((Trig_Point[SITE] > 1) && (Trig_Point[SITE] < samples - 1)){
				result[SITE] = fpvi_gp_bysite_qb[0][SITE].GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1) + fpvi_gp_bysite_qb[1][SITE].GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
			}
			else
				result[SITE] = ERROR_RES;
		}

			//smartfpvi01->Set(FI, 0, v_range, i_range, FPVIe_RELAY_ON);
			//smartfpvi01->Set(FI, 0, FPVIe_1V, FPVIe_1MA, FPVIe_RELAY_OFF);
			////cbite.SetOn(K1_CVAC1, K3_CVBUS, K2_CVAC2, K5_CPMID, K7_CVOUT, K16_CREGN, K19_INT_ACM, K17_FOVI_SVAC1, K18_INT_V5V, -1);
		delay_ms(1);


	}
	//for (int i = 0; i < FPVI_NUM_NO_SITE; ++i) {
	//	fpvi_list[i].Set(FI, 0, FPVIe_1V, FPVIe_1MA, FPVIe_RELAY_OFF);
	//}
	acm_cap.Set(FI, 0, ACM_N2P18V, ACM_20UA, ACM_RELAY_OFF);
	return TRUE;
}



BOOL Test_Method::rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MVRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
    STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, ACM200_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FOVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FXVIe_PLUS_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, ACM200_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FOVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampi_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// set start ramp point
	cap_res.Set(FV, cap_fv_value, cap_vrange, cap_irange, FPVIe_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FI, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasITrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRun();
	//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);
	ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);// current recover to 0A

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MIRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = ramp_res.GetMeasResult(SITE, MIRET, Trig_Point[SITE] - 1);
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}

BOOL Test_Method::rampv_capv_sim(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result)
{
	if (interval < 10)	return FALSE;
	if (step == 0)	return FALSE;

	int samples;
	double pat[MAX_SAMPLES];
	samples = (int)step;
	ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, FPVIe_RELAY_ON);
	cap_res.Set(FI, 0, cap_vrange, cap_irange, FXVIe_PLUS_RELAY_ON);
	delay_ms(1);
	STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);
	ramp_res.AwgClear();
	ramp_res.AwgLoader("awg", FV, ramp_vrange, ramp_irange, pat, samples);
	ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);
	cap_res.SetMeasVTrig(trig_level, trig_mode);

	if (!START_DELAY)
		delay_ms(START_DELAY);

	ramp_res.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG);
	cap_res.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG);

	STSEnableAWG(&ramp_res);
	STSEnableMeas(&ramp_res, &cap_res);
	STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);
	delay_us(TRIG_DELAY);

	int Trig_Point[SITE_NUM];
	SERIAL{
		Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, MVRET, TRIG_RESULT);
		if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){
			result[SITE] = Trig_Point[SITE]*(stop_point - start_point) / samples+start_point;
		}
		else {
			result[SITE] = ERROR_RES;
		}
	}

	return TRUE;
}
