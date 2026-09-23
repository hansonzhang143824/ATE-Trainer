/*****************************************************************************
*                                                                            *
*       Source title:   Test_Method.h                                        *
*                       (Universal functions for all SC test projects)       *
*         Written by:   SC TE                                                *
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
00   08/24/18  Initial.						Alan Luo
01   09/04/18  Reset ERROR_RES to 9999		Alan Luo
Remove fpvi current ramp 1ms capload at start for EOS damage risk
02   10/31/18  Fix "Enable log" alarm issue  Alan
Change "fovi_cap.Set" from RELAY_SENSE_ON to RELAY_ON
03   3/27/19   Add ramp with I2C flag trig, ramp with QVM measure
Add ADC_Statistic Parameters Calculation function (Includes FSR/LSB/INL/DNL...)
04   07/23/19  Return measure current not calculated result, when use fpvi ramp current
----------------------------------------------------------------
*/

#pragma once
#include "stdafx.h"

#define MAX_SAMPLES 4096
#define ERROR_RES	9999
#define START_DELAY	0
#define TRIG_DELAY	250

class Test_Method {
public:
	Test_Method() {}
	~Test_Method() {}

	BOOL OS_Classify(short funcindex, string pin_str_array[], unsigned int OS_NUM, string leak_str_array[], unsigned int LEAK_NUM, double os_result[][SITE_NUM], double leak_result[][SITE_NUM], vector<string>& vec_exclude);
	FOVIe_VRNG get_fovi_v_range(double v);
	FXVIe_PLUS_VRNG get_fxvi_v_range(double v);
	BOOL ramp(ACM acm_ramp, ACM_IRNG i_range, ACM acm_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL ramp_v(ACM acm_ramp, ACM_IRNG i_range, ACM acm_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL ramp(FOVIe fovi_ramp, FOVIe_VRNG v_range, FOVIe_IRNG i_range, ACM acm_cap, ACM_IRNG acm_i_range, double loading, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL ramp(FOVIe fovi_ramp, FOVIe fovi_ramp1, FOVIe_VRNG v_range, FOVIe_IRNG i_range, ACM acm_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL ramp(FOVIe fovi_ramp, FOVIe_VRNG v_range, FOVIe_IRNG i_range, ACM acm_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL ramp(FPVIe fpvi_ramp1, FPVIe fpvi_ramp2, FPVIe fpvi_gp_bysite[][SITE_NUM], FPVIe_VRNG v_range, FPVIe_IRNG i_range, ACM acm_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL ramp_I(FOVIe fovi_ramp, FOVIe_VRNG v_range, FOVIe_IRNG i_range, FOVIe fovi_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double* result);
	BOOL ramp_ucp(FPVIe fpvi_ramp1, FPVIe fpvi_ramp2, FPVIe fpvi_gp_bysite[][SITE_NUM], FPVIe_VRNG v_range, FPVIe_IRNG i_range, ACM acm_cap, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result, int delay_2p);
	BOOL rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result, int delay_2p);
	BOOL rampi_fv_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, ACM200 capret_res, ACM200_VRNG capret_vrange, ACM200_IRNG capret_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);

	BOOL rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capv(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(FOVIe ramp_res, FOVIe_VRNG ramp_vrange, FOVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(FXVIe_PLUS ramp_res, FXVIe_PLUS_VRNG ramp_vrange, FXVIe_PLUS_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampi_capi(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FPVIe cap_res, FPVIe_VRNG cap_vrange, FPVIe_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
	BOOL rampv_capv_sim(FPVIe ramp_res, FPVIe_VRNG ramp_vrange, FPVIe_IRNG ramp_irange, FXVIe_PLUS cap_res, FXVIe_PLUS_VRNG cap_vrange, FXVIe_PLUS_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
};

