#include "StdAfx.h"
#include "Coutlier.h"

Coutlier::Coutlier(){
	double temp95_table[101] = {
		1, 1, 1, 1.153, 1.463, 1.672, 1.822, 1.938, 2.032, 2.110, 2.176,
		2.234, 2.285, 2.331, 2.371, 2.409, 2.443, 2.475, 2.501, 2.532, 2.557,
		2.580, 2.603, 2.624, 2.644, 2.663, 2.681, 2.698, 2.714, 2.730, 2.745,
		2.759, 2.773, 2.786, 2.799, 2.811, 2.823, 2.835, 2.846, 2.857, 2.866,
		2.877, 2.887, 2.896, 2.905, 2.914, 2.923, 2.931, 2.940, 2.948, 2.956,
		2.943, 2.971, 2.978, 2.986, 2.992, 3.000, 3.006, 3.013, 3.019, 3.025,
		3.032, 3.037, 3.044, 3.049, 3.055, 3.061, 3.066, 3.071, 3.076, 3.082,
		3.087, 3.092, 3.098, 3.102, 3.107, 3.111, 3.117, 3.121, 3.125, 3.130,
		3.134, 3.139, 3.143, 3.147, 3.151, 3.155, 3.160, 3.163, 3.167, 3.171,
		3.174, 3.179, 3.182, 3.186, 3.189, 3.193, 3.196, 3.201, 3.204, 3.207
	};
	double temp995_table[101] = {
		1, 1, 1, 1.155, 1.496, 1.764, 1.973, 2.139, 2.274, 2.387, 2.482,
		2.564, 2.636, 2.699, 2.755, 2.806, 2.852, 2.894, 2.932, 2.968, 3.001,
		3.031, 3.060, 3.087, 3.112, 3.135, 3.157, 3.178, 3.199, 3.218, 3.236,
		3.253, 3.270, 3.286, 3.301, 3.316, 3.330, 3.343, 3.356, 3.369, 3.381,
		3.393, 3.404, 3.415, 3.425, 3.435, 3.445, 3.455, 3.464, 3.474, 3.483,
		3.491, 3.500, 3.507, 3.516, 3.524, 3.531, 3.539, 3.546, 3.553, 3.560,
		3.566, 3.573, 3.579, 3.586, 3.592, 3.598, 3.605, 3.610, 3.617, 3.622,
		3.627, 3.633, 3.638, 3.643, 3.648, 3.654, 3.658, 3.663, 3.669, 3.673,
		3.677, 3.682, 3.687, 3.691, 3.695, 3.699, 3.704, 3.708, 3.712, 3.716,
		3.720, 3.725, 3.728, 3.732, 3.736, 3.739, 3.744, 3.747, 3.750, 3.754
	};
	for (int i = 0; i < 101; ++i){
		grubbs_table[i] = temp995_table[i];
	}

	for (vector<string>::iterator it_test = sos_config.test_vec.begin(); it_test != sos_config.test_vec.end(); ++it_test){
		for (int site = 0; site < SITE_NUM; ++site){
			sos_low_limit[*it_test][site] = 999999;
			sos_high_limit[*it_test][site] = 999999;
			sos_flag[*it_test][site] = 0;
		}
	}

	serial = 1;
	the_end = 0;
	mode = PRODUCTION;

	sigma_all.clear();
	mean_all.clear();
	cnt_all.clear();

	wafer_no = 0;
}


int Coutlier::clear(){
	serial = 1;
	the_end = 0;

	sos_database.clear();
	sos_config.clear();
	sos_low_limit.clear();
	sos_high_limit.clear();
	sos_flag.clear();
	grubbs_init_flag.clear();
	test_value.clear();
	bin_map.clear();
	acco_data.clear();

	sigma_all.clear();
	mean_all.clear();
	cnt_all.clear();

	return TRUE;
}



int Coutlier::grubbs_outlier_init(string test, vector<double>& vec){
	if ((vec.size() <= 3) || (vec.size() > 99)) return FALSE;

	vector<double> temp_vec;

	double mean = mylib.average(vec);
	double sigma = mylib.deviation(vec);

	if (sigma == 0) return FALSE;

	for (vector<double>::iterator it = vec.begin(); it != vec.end(); ++it){
		if (fabs((*it) - mean) / sigma <= grubbs_table[temp_vec.size()])
			temp_vec.push_back(*it);
	}

	vec = temp_vec;
	for (int site = 0; site < SITE_NUM; ++site){
		sos_low_limit[test][site] = mean - grubbs_table[temp_vec.size()] * sigma;
		sos_high_limit[test][site] = mean + grubbs_table[temp_vec.size()] * sigma;
	}

	return TRUE;
}


int Coutlier::grubbs_outlier(string test, DWORD site, vector<double>& vec, double value){
	if ((vec.size() <= 3) || (vec.size() > 99)) return FALSE;

	vector<double> temp_vec(vec);
	temp_vec.push_back(value);

	double mean = mylib.average(temp_vec);
	double sigma = mylib.deviation(temp_vec);

	sos_low_limit[test][site] = mean - grubbs_table[temp_vec.size()] * sigma;
	sos_high_limit[test][site] = mean + grubbs_table[temp_vec.size()] * sigma;

	if (sigma == 0) return FALSE;

	if (fabs(value - mean) / sigma <= grubbs_table[temp_vec.size()])
		return FALSE;
	else
		return TRUE;

	return TRUE;
}


int Coutlier::is_in_range(DWORD curr_x, DWORD curr_y, DWORD ref_x, DWORD ref_y, DWORD distance_limit){
	DWORD delta_x = curr_x - ref_x;
	DWORD delta_y = curr_y - ref_y;

	double distance = sqrt((double)(delta_x * delta_x + delta_y * delta_y));

	if (distance <= distance_limit) return TRUE;
	else return FALSE;
}


int Coutlier::pauta_outlier(string test, DWORD site, vector<double>& distri_vec, double value, DWORD sigma_n, double skip_lolim, double skip_hilim){
	if ((value > skip_lolim) && (value < skip_hilim)) return FALSE;

	double stdev = 0;
	double mean = 0;
	mylib.deviation(distri_vec, mean, stdev);

	sos_low_limit[test][site] = mean - sigma_n*stdev;
	sos_high_limit[test][site] = mean + sigma_n*stdev;

	if ((value > (mean + sigma_n*stdev)) || (value < (mean - sigma_n*stdev))) return TRUE;
	else return FALSE;
}


int Coutlier::init(string config_file, int sos_mode = PRODUCTION, string acco_file = ""){
	if (!sos_config.load(config_file)) return FALSE;
	mode = sos_mode;

	if ((acco_file != "") && (mode == SIMULATION)){
		if (!acco_data.load_data(acco_file))
			return FALSE;
	}

	return TRUE;
}


int Coutlier::log_sos_param(short funcindex, string test){
	if ((the_end) && (mode == SIMULATION)) return FALSE;
	if ((wafer_no == 0) && (mode == PRODUCTION)) return FALSE;

	//SERIAL{
	for (map<DWORD, int>::iterator it_site = bin_map.begin(); it_site != bin_map.end(); ++it_site){
		if (it_site->second != 1) continue;

		SITE = it_site->first;
		sos_flag[test][SITE] = 0;

		if (sos_database.distri_cnt[test] > 10){

			if (grubbs_init_flag[test] == 0){ // do grubbs_outlier_init one time only
				if ((wafer_no == 1) || (mode == SIMULATION)){
					grubbs_outlier_init(test, sos_database.distri_vec_map[test]);
					sos_database.distri_cnt[test] = (DWORD)sos_database.distri_vec_map[test].size();
					grubbs_init_flag[test] = 1;

					mylib.deviation(sos_database.distri_vec_map[test], mean_all[test], sigma_all[test]);
					cnt_all[test] = (DWORD)sos_database.distri_vec_map[test].size();;
				}
			}
			else{
				sos_low_limit[test][SITE] = mean_all[test] - sos_config.nsigma_map[test] * sigma_all[test];
				sos_high_limit[test][SITE] = mean_all[test] + sos_config.nsigma_map[test] * sigma_all[test];
			}
		}
		else{
			sos_database.distri_vec_map[test].push_back(test_value[test][SITE]);
			sos_database.distri_cnt[test]++;

			if (wafer_no != 1){
				sos_low_limit[test][SITE] = sos_low_limit_old[test][SITE];
				sos_high_limit[test][SITE] = sos_high_limit_old[test][SITE];
			}
		}

		// delog
		if (grubbs_init_flag[test] == 0){
			sos_flag[test][SITE] = 1;
			string param_str;
			param_str = test + "_SOS_FLAG";
			StsGetParam(funcindex, param_str.c_str())->SetTestResult(SITE, 0, 1);
			param_str = test + "_SOS_VALUE";
			StsGetParam(funcindex, param_str.c_str())->SetTestResult(SITE, 0, 999999);
			param_str = test + "_SOS_L";
			StsGetParam(funcindex, param_str.c_str())->SetTestResult(SITE, 0, 999999);
			param_str = test + "_SOS_H";
			StsGetParam(funcindex, param_str.c_str())->SetTestResult(SITE, 0, 999999);
		}
		else{
			// skip sos analysis when the tested value is safe enough
			if ((test_value[test][SITE] > sos_config.nosos_lolim_map[test]) && (test_value[test][SITE] < sos_config.nosos_hilim_map[test])){
				sos_flag[test][SITE] = 0;
				// delog
				string param_str;
				param_str = test + "_SOS_FLAG";
				StsGetParam(funcindex, param_str.c_str())->SetTestResult(SITE, 0, sos_flag[test][SITE]);
				param_str = test + "_SOS_VALUE";
				StsGetParam(funcindex, param_str.c_str())->SetTestResult(SITE, 0, test_value[test][SITE]);
				param_str = test + "_SOS_L";
				StsGetParam(funcindex, param_str.c_str())->SetTestResult(SITE, 0, sos_config.nosos_lolim_map[test]);
				param_str = test + "_SOS_H";
				StsGetParam(funcindex, param_str.c_str())->SetTestResult(SITE, 0, sos_config.nosos_hilim_map[test]);
			}
			else{
				if ((test_value[test][SITE] < sos_low_limit[test][SITE]) || (test_value[test][SITE] > sos_high_limit[test][SITE]))
					sos_flag[test][SITE] = 1;
				else
					sos_flag[test][SITE] = 0;

				string param_str;
				param_str = test + "_SOS_FLAG";
				StsGetParam(funcindex, param_str.c_str())->SetTestResult(SITE, 0, sos_flag[test][SITE]);
				param_str = test + "_SOS_VALUE";
				StsGetParam(funcindex, param_str.c_str())->SetTestResult(SITE, 0, test_value[test][SITE]);
				param_str = test + "_SOS_L";
				StsGetParam(funcindex, param_str.c_str())->SetTestResult(SITE, 0, sos_low_limit[test][SITE]);
				param_str = test + "_SOS_H";
				StsGetParam(funcindex, param_str.c_str())->SetTestResult(SITE, 0, sos_high_limit[test][SITE]);
			}
		}
	}

	return TRUE;
}


int Coutlier::eot(){
	for (map<DWORD, int>::iterator it_site = bin_map.begin(); it_site != bin_map.end(); ++it_site){
		if (it_site->second != 1) continue;
		SITE = it_site->first;

		for (vector<string>::iterator it_test = sos_config.test_vec.begin(); it_test != sos_config.test_vec.end(); ++it_test){
			//sos_database.all_tested_bin1_map[x_corr[SITE]][y_corr[SITE]][*it_test] = test_value[*it_test][SITE];

			mylib.deviation(cnt_all[*it_test], mean_all[*it_test], sigma_all[*it_test], test_value[*it_test][SITE], mean_all[*it_test], sigma_all[*it_test]);
			cnt_all[*it_test]++;
		}
		sos_database.all_tested_bin1_cnt++;
	}

	return TRUE;
}


int Coutlier::sot(){
	test_value.clear();
	bin_map.clear();

	// get wafer id
	char str[64];
	STSGetWaferID(str, 20);

	if (mode == PRODUCTION)
		wafer_id = str;
	else
		wafer_id = "DNR561-21-C1";   // change wafer id to simulator new wafer loading in produciton

	//wafer_no = 1;

	if (wafer_id_old != wafer_id){
		sos_database.clear();
		sigma_all.clear();
		mean_all.clear();
		cnt_all.clear();

		wafer_id_old = wafer_id;
		wafer_no++;

		sos_low_limit_old = sos_low_limit;
		sos_high_limit_old = sos_high_limit;
	}

	if (mode == PRODUCTION){
		// get xy corrdinator
		G_GetXYCoordinate();

		// if mode is produciton, x/y corrdinater is setted in InitBeforeTestFlow function, 
		// bin_map is getted from SERIAL, test_value is getted from test function
		for (int site = 0; site < SITE_NUM; ++site){
			x_corr[site] = g_x_coords[site];
			y_corr[site] = g_y_coords[site];
		}
	}
	else{
		//SERIAL{
		for (int i = 0; i < SITE_NUM; ++i){
			if (acco_data.bin_map[serial] == ""){
				the_end = 1;
				break;
			}
			if (acco_data.bin_map[serial] != "1"){
				serial++;
				continue;
			}

			int site = atoi(acco_data.site_map[serial].c_str());

			for (vector<string>::iterator it_test = sos_config.test_vec.begin(); it_test != sos_config.test_vec.end(); ++it_test){
				test_value[*it_test][site - 1] = atof(acco_data.val_map[serial][*it_test].c_str());
			}
			x_corr[site - 1] = atoi(acco_data.val_map[serial]["X_Coordinate"].c_str());
			y_corr[site - 1] = atoi(acco_data.val_map[serial]["Y_Coordinate"].c_str());
			bin_map[site - 1] = atoi(acco_data.bin_map[serial].c_str());
			serial++;

			if (atoi(acco_data.site_map[serial].c_str()) <= site) break;
		}
	}


	return TRUE;
}



int Coutlier::input_test_value(string param_str, double *result){
	if (mode == SIMULATION) return FALSE;

	StsGetSiteStatus(sitesta, SITE_NUM);
	SERIAL test_value[param_str][SITE] = result[SITE];

	return TRUE;
}


void Coutlier::update_test_result_flag() {
	if (mode == PRODUCTION){
		StsGetSiteStatus(sitesta, SITE_NUM);
		SERIAL bin_map[SITE] = 1;
	}
}


int Coutlier::log_sos_param_all(short funcindex) {
	update_test_result_flag();

	for (vector<string>::iterator it_test = sos_config.test_vec.begin(); it_test != sos_config.test_vec.end(); ++it_test){
		log_sos_param(funcindex, (*it_test).c_str());
	}

	update_test_result_flag();

	return 0;
}
