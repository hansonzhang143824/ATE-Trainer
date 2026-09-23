#pragma once

#include "stdafx.h"	// must be front
#include "mylib.h"

class CAccoCsvData{
public:
	vector<string> test_vec;

	map<string, string> lolim_map;
	map<string, string> hilim_map;
	map<string, string> unit_map;

	map<DWORD, map<string, string>> val_map;	// map<serial, map<test, value>>
	map<DWORD, string> bin_map;					// map<serial, bin>
	map<DWORD, string> site_map;				// map<serial, site>
	map<DWORD, string> passfg_map;				// map<serial, pass_flag>

	map<string, DWORD> site_num_map;			// map<site, number>

	Cmylib mylib;

	void clear(){
		test_vec.clear();
		lolim_map.clear();
		hilim_map.clear();
		unit_map.clear();
		val_map.clear();
		bin_map.clear();
		site_map.clear();
		passfg_map.clear();
		site_num_map.clear();
	}

	BOOL get_site_numbers(map<DWORD, map<DWORD, string>>& data_map, map<string, DWORD>& res_map){
		if (data_map.empty())
			return FALSE;

		DWORD row_label = 999;
		DWORD serial = 1;

		for (DWORD row = 1; row <= data_map.size(); ++row){
			if (data_map[row][1] == "SITE_NUM"){
				row_label = row;
				if (row_label == 1)
					return FALSE;
			}
			if (row > row_label + 4){	// value region
				string site(data_map[row][1]);
				res_map[site]++;
			}
		}

		return TRUE;
	}

	// get single site value
	BOOL load_data(map<DWORD, map<DWORD, string>>& data_map, string site_num){
		if (data_map.empty())
			return FALSE;

		DWORD row_label = 999;
		DWORD serial = 1;

		for (DWORD row = 1; row <= data_map.size(); ++row){
			if (data_map[row][1] == "SITE_NUM"){
				row_label = row;
				if (row_label == 1)
					return FALSE;
				for (DWORD col = 7; col < data_map[row].size(); ++col){
					string label(data_map[row][col]);
					string unit(data_map[row + 1][col]);
					string lolim(data_map[row + 2][col]);
					string hilim(data_map[row + 3][col]);
					lolim_map[label] = lolim;
					hilim_map[label] = hilim;
					unit_map[label] = unit;

					test_vec.push_back(label);
				}
			}
			if (row > row_label + 4){	// value region
				string bin(data_map[row][4]);
				string site(data_map[row][1]);
				string passfg(data_map[row][3]);

				if (site == site_num){
					bin_map[serial] = bin;
					site_map[serial] = site;
					passfg_map[serial] = passfg;

					for (DWORD col = 7; col < data_map[row].size(); ++col){
						string label(data_map[row_label][col]);
						val_map[serial][label] = data_map[row][col];
					}
					serial++;
				}
			}
		}

		return TRUE;
	}

	BOOL load_data(map<DWORD, map<DWORD, string>>& data_map){
		if (data_map.empty())
			return FALSE;

		DWORD row_label = 999;
		DWORD serial = 1;

		for (DWORD row = 1; row <= data_map.size(); ++row){
			if (data_map[row][1] == "SITE_NUM"){
				row_label = row;
				if (row_label == 1)
					return FALSE;
				for (DWORD col = 7; col <= data_map[row].size(); ++col){
					string label(data_map[row][col]);
					string unit(data_map[row + 1][col]);
					string lolim(data_map[row + 2][col]);
					string hilim(data_map[row + 3][col]);

					if (label != ""){
						lolim_map[label] = lolim;
						hilim_map[label] = hilim;
						unit_map[label] = unit;

						test_vec.push_back(label);
					}
				}
			}
			if (row > row_label + 4){	// value region
				string bin(data_map[row][4]);
				string site(data_map[row][1]);
				string passfg(data_map[row][3]);

				bin_map[serial] = bin;
				site_map[serial] = site;
				passfg_map[serial] = passfg;
				site_num_map[site]++;

				for (DWORD col = 7; col <= data_map[row].size(); ++col){
					string label(data_map[row_label][col]);
					val_map[serial][label] = data_map[row][col];
				}
				serial++;
			}
		}

		return TRUE;
	}

	BOOL load_data(string file_name){
		CMapMemFile raw_file;
		map<DWORD, map<DWORD, string>> raw_map;	// map<row, map<column, value>>

		if (!raw_file.create(file_name.c_str())) return FALSE;

		raw_file.CsvReader(raw_map);
		raw_file.CloseMapFile();

		load_data(raw_map);

		return TRUE;
	}

	BOOL load_data_bc(map<DWORD, map<DWORD, string>>& data_map){
		if (data_map.empty())
			return FALSE;

		// load test limit
		for (DWORD row = 2; row <= data_map.size(); ++row){
			if (data_map[row][1] == "Time")
				break;

			for (DWORD col = 2; col <= data_map[row].size(); ++col){
				if (data_map[row][col] == "Low Limit"){
					string label(data_map[row][col + 5]);
					string unit(data_map[row][col + 4]);
					string lolim(data_map[row][col + 1]);
					string hilim(data_map[row][col + 3]);
					lolim_map[label] = lolim;
					hilim_map[label] = hilim;
					unit_map[label] = unit;

					test_vec.push_back(label);
				}
			}
		}

		DWORD serial = 1;

		for (DWORD row = 1; row <= data_map.size(); ++row){
			if (data_map[row][1] != "Time"){
				DWORD col_label = (DWORD)data_map[row].size();
				string label(data_map[row][col_label]);

				for (DWORD col = 2; col <= data_map[row].size(); ++col){
					if ((data_map[row][col].find("Site") != string::npos) || (data_map[row][col].find("SITE") != string::npos)){
						val_map[serial][label] = data_map[row][col + 2];

						if (data_map[row][col + 1] == "PASS")
							passfg_map[serial] = "TRUE";
						else
							passfg_map[serial] = "FALSE";

						serial++;
					}
				}
			}
			//if(data_map[row][1] == "Time")
			//	serial++;
			//else{
			//	DWORD col_label = (DWORD)data_map[row].size() ;
			//	string label(data_map[row][col_label]);
			//	for(DWORD col = 2; col <= data_map[row].size(); ++col){
			//		if(data_map[row][col].find("Site") != string::npos)
			//			val_map[serial][label] = data_map[row][col + 2];
			//	}
			//}
		}

		return TRUE;
	}

public:
	CAccoCsvData(void) {}
	~CAccoCsvData(void) {}
};

class CTestStatisticStruct
{
public:
	vector<string> test_vec;	 // vector<test_name>
	map<string, string> std_map;  // map<test_name,std>
	map<string, string> mean_map; // map<test_name,mean>
	map<string, string> min_map;  // map<test_name,min>
	map<string, string> max_map;  // map<test_name,max>
	map<string, string> cpl_map;  // map<test_name,cpl>
	map<string, string> cpu_map;  // map<test_name,cpu>
	map<string, string> cpk_map;  // map<test_name,cpk>
	map<string, string> grr_map;  // map<test_name,grr>
	map<string, string> lolim_map;  // map<test_name,lolim>
	map<string, string> hilim_map;  // map<test_name,hilim>
	map<string, string> unit_map;  // map<test_name,unit>

	map<string, DWORD> count_map;// map<test_name,count>

	BOOL load_data(map<DWORD, map<DWORD, string>>& data_map){
		for (DWORD row = 2; row <= data_map.size(); ++row){
			if (data_map[row][2] == "") break;

			std_map[data_map[row][2]] = data_map[row][6];
			mean_map[data_map[row][2]] = data_map[row][7];
			min_map[data_map[row][2]] = data_map[row][8];
			max_map[data_map[row][2]] = data_map[row][9];
			cpl_map[data_map[row][2]] = data_map[row][10];
			cpu_map[data_map[row][2]] = data_map[row][11];
			cpk_map[data_map[row][2]] = data_map[row][12];
			grr_map[data_map[row][2]] = data_map[row][13];
			lolim_map[data_map[row][2]] = data_map[row][3];
			hilim_map[data_map[row][2]] = data_map[row][4];
			unit_map[data_map[row][2]] = data_map[row][5];
			count_map[data_map[row][2]] = atoi(data_map[row][14].c_str());
		}

		return TRUE;
	}


	BOOL export_SCA(map<DWORD, map<DWORD, string>>& sca_map, map<DWORD, map<DWORD, string>>& out_map){
		DWORD row_testname = 0;
		DWORD col_testname = 0;

		for (DWORD row = 1; row <= sca_map.size(); ++row){
			for (DWORD col = 1; col <= sca_map[row].size(); ++col){
				if (sca_map[row][col] == "Testname"){
					row_testname = row;
					col_testname = col;
					break;
				}
			}
			if ((row_testname != 0) && (col_testname != 0)) break;
		}

		out_map[1][1] = "Testname";
		out_map[1][2] = "(mean - 6sigma)";
		out_map[1][3] = "min. reading";
		out_map[1][4] = "mean";
		out_map[1][5] = "stdev";
		out_map[1][6] = "max. reading";
		out_map[1][7] = "(mean + 6sigma)";
		out_map[1][8] = "LTL";
		out_map[1][9] = "UTL";
		out_map[1][10] = "Unit ATE";

		for (DWORD row = row_testname + 3; row <= sca_map.size(); ++row){
			if (sca_map[row][col_testname] != ""){
				string testname_str(sca_map[row][col_testname]);

				if (std_map.find(testname_str) != std_map.end()){
					double mean = atof(mean_map[testname_str].c_str());
					double std = atof(std_map[testname_str].c_str());
					double neg6sigma = mean - 6 * std;
					double pos6sigma = mean + 6 * std;
					string str_neg6sigma = mylib.float2str(neg6sigma);
					string str_pos6sigma = mylib.float2str(pos6sigma);

					out_map[row][1] = testname_str;
					out_map[row][2] = str_neg6sigma;
					out_map[row][3] = min_map[testname_str];
					out_map[row][4] = mean_map[testname_str];
					out_map[row][5] = std_map[testname_str];
					out_map[row][6] = max_map[testname_str];
					out_map[row][7] = str_pos6sigma;
					out_map[row][8] = lolim_map[testname_str];
					out_map[row][9] = hilim_map[testname_str];
					out_map[row][10] = unit_map[testname_str];
				}
			}
		}

		return TRUE;
	}

	BOOL export_CPK(map<DWORD, map<DWORD, string>>& out_map){
		out_map[1][1] = "Test Number";
		out_map[1][2] = "Test Name";
		out_map[1][3] = "Low Limit";
		out_map[1][4] = "High Limit";
		out_map[1][5] = "Unit";
		out_map[1][6] = "Stdev";
		out_map[1][7] = "Average";
		out_map[1][8] = "Min";
		out_map[1][9] = "Max";
		out_map[1][10] = "Cpl";
		out_map[1][11] = "Cpu";
		out_map[1][12] = "Cpk";
		out_map[1][13] = "Count";
		out_map[1][14] = "Comment";

		DWORD row = 2;
		DWORD num = 1;
		for (vector<string>::iterator it = test_vec.begin(); it != test_vec.end(); ++it){
			string testname_str = *it;
			if ((std_map.find(*it) != std_map.end()) && (cpk_map[testname_str] != "999999") && (unit_map[testname_str] != "DB")){
				out_map[row][1] = mylib.int2str(num++);
				out_map[row][2] = testname_str;
				out_map[row][3] = lolim_map[testname_str];
				out_map[row][4] = hilim_map[testname_str];
				out_map[row][5] = unit_map[testname_str];
				out_map[row][6] = std_map[testname_str];
				out_map[row][7] = mean_map[testname_str];
				out_map[row][8] = min_map[testname_str];
				out_map[row][9] = max_map[testname_str];
				out_map[row][10] = cpl_map[testname_str];
				out_map[row][11] = cpu_map[testname_str];
				out_map[row][12] = cpk_map[testname_str];
				out_map[row][13] = mylib.int2str(count_map[testname_str]);

				row++;
			}
		}

		return TRUE;
	}

	BOOL export_CYCLE(CTestStatisticStruct& cycle2, CTestStatisticStruct& cycle3, map<DWORD, map<DWORD, string>>& out_map){
		out_map[1][1] = "Test Name";
		out_map[1][2] = "Low Limit";
		out_map[1][3] = "High Limit";
		out_map[1][4] = "Unit";
		out_map[1][5] = "Average";
		out_map[1][6] = "";
		out_map[1][7] = "";
		out_map[1][8] = "";
		out_map[1][9] = "";
		out_map[1][10] = "6*Stdev";
		out_map[1][11] = "";
		out_map[1][12] = "";
		out_map[1][13] = "";
		out_map[1][14] = "";
		out_map[1][15] = "Comment";
		out_map[2][1] = "";
		out_map[2][2] = "";
		out_map[2][3] = "";
		out_map[2][4] = "";
		out_map[2][5] = "1st";
		out_map[2][6] = "2nd";
		out_map[2][7] = "2nd_delta%";
		out_map[2][8] = "3rd";
		out_map[2][9] = "3rd_delta%";
		out_map[2][10] = "1st";
		out_map[2][11] = "2nd";
		out_map[2][12] = "2nd_delta%";
		out_map[2][13] = "3rd";
		out_map[2][14] = "3rd_delta%";
		out_map[2][15] = "";

		DWORD row = 3;
		for (vector<string>::iterator it = test_vec.begin(); it != test_vec.end(); ++it){
			string testname_str = *it;
			if ((std_map.find(*it) != std_map.end()) && (unit_map[testname_str] != "DB") && (mean_map[testname_str] != "999999") && (cycle2.mean_map[testname_str] != "999999") && (cycle3.mean_map[testname_str] != "999999")){
				out_map[row][1] = testname_str;
				out_map[row][2] = lolim_map[testname_str];
				out_map[row][3] = hilim_map[testname_str];
				out_map[row][4] = unit_map[testname_str];

				out_map[row][5] = mean_map[testname_str];
				out_map[row][6] = cycle2.mean_map[testname_str];
				out_map[row][8] = cycle3.mean_map[testname_str];

				double lolim = atof(lolim_map[testname_str].c_str());
				double hilim = atof(hilim_map[testname_str].c_str());
				double mean1 = atof(mean_map[testname_str].c_str());
				double mean2 = atof(cycle2.mean_map[testname_str].c_str());
				double mean3 = atof(cycle3.mean_map[testname_str].c_str());
				double sigma1 = atof(std_map[testname_str].c_str());
				double sigma2 = atof(cycle2.std_map[testname_str].c_str());
				double sigma3 = atof(cycle3.std_map[testname_str].c_str());

				if (hilim != lolim){
					out_map[row][7] = mylib.float2str((mean2 - mean1) / (hilim - lolim) * 100);
					out_map[row][9] = mylib.float2str((mean3 - mean1) / (hilim - lolim) * 100);
					out_map[row][12] = mylib.float2str(6 * (sigma2 - sigma1) / (hilim - lolim) * 100);
					out_map[row][14] = mylib.float2str(6 * (sigma3 - sigma1) / (hilim - lolim) * 100);
				}
				else {
					out_map[row][7] = "0";
					out_map[row][9] = "0";
					out_map[row][12] = "0";
					out_map[row][14] = "0";
				}

				out_map[row][10] = mylib.float2str(6 * sigma1);
				out_map[row][11] = mylib.float2str(6 * sigma2);
				out_map[row][13] = mylib.float2str(6 * sigma3);

				row++;
			}
		}

		return TRUE;
	}

	CTestStatisticStruct(void) {}
	~CTestStatisticStruct(void) {}

private:
	Cmylib mylib;

};

class CTcsResultStruct
{
public:
	vector<string> test_vec;

	map<string, double> lolim_map;
	map<string, double> hilim_map;
	map<string, string> unit_map;

	DWORD samples_cnt;
	DWORD setups_cnt;

	map<string, DWORD> setup_map;							// map<setup, cnt>
	map<string, double> mgb_map;								// map<test_name, mgb>
	map<string, double> grr_map;								// map<test_name, grr>
	map<string, string> str_mgb_map;							// map<test_name, mgb>
	map<string, string> str_grr_map;							// map<test_name, grr>
	map<string, map<string, double>> std_map;					// map<test_name, map<part id, std>>
	map<string, double> avg_std_map;							// map<test_name, avg_std>
	//map<string,map<string,map<string,string>>> data_map;	// map<test_name, map<part id, map<setup, value>>>
	map<string, map<DWORD, map<string, string>>> data_map;	// map<test_name, map<part id, map<setup, value>>>
	map<string, map<string, double>> sigma_bysetup_map;		// map<test_name, map<partid,sigma>>
	//map<string,map<DWORD,double>> partid_map;				// map<test_name, map<partid,sigma>>

	CTcsResultStruct(void) {}
	~CTcsResultStruct(void) {}
};


class CSOS_config
{
public:
	vector<string> test_vec;			 // the test items which need to do sos
	map<string, DWORD> scope_map;		 // the distance from samples to current tested sample will do sos
	map<string, DWORD> min_count_map;	 // the minimize samples to do sos, else do dpat
	map<string, double> nsigma_map;		 // the times of sigma for new sos limit
	map<string, double> nosos_lolim_map;  // the low limit for nosos skip
	map<string, double> nosos_hilim_map;  // the high limit for nosos skip

	CSOS_config(void) {
		test_vec.clear();
		scope_map.clear();
		min_count_map.clear();
		nsigma_map.clear();
		nosos_lolim_map.clear();
		nosos_hilim_map.clear();
	}
	~CSOS_config(void) {}

	void clear(){
		test_vec.clear();
		scope_map.clear();
		min_count_map.clear();
		nsigma_map.clear();
		nosos_lolim_map.clear();
		nosos_hilim_map.clear();
	}

	BOOL load(map<DWORD, map<DWORD, string>>& config_map){
		if (config_map.empty()) return FALSE;

		for (map<DWORD, map<DWORD, string>>::iterator it_row = config_map.begin(); it_row != config_map.end(); ++it_row){
			if (it_row->first == 1) continue;

			string test = it_row->second[1];
			string scope = it_row->second[2];
			string min_count = it_row->second[3];
			string nsigma = it_row->second[4];
			string nosos_lolim = it_row->second[5];
			string nosos_hilim = it_row->second[6];

			if (test == "") break;
			else{
				if (scope == "") scope_map[test] = 20;
				else scope_map[test] = atoi(scope.c_str());

				if (min_count == "") min_count_map[test] = 50;
				else min_count_map[test] = atoi(min_count.c_str());

				if (nsigma == "") nsigma_map[test] = 6;
				else nsigma_map[test] = atof(nsigma.c_str());

				if (nosos_lolim == "") nosos_lolim_map[test] = 999999;
				else nosos_lolim_map[test] = atof(nosos_lolim.c_str());

				if (nosos_hilim == "") nosos_hilim_map[test] = 999999;
				else nosos_hilim_map[test] = atof(nosos_hilim.c_str());

				test_vec.push_back(test);
			}
		}

		return TRUE;
	}

	BOOL load(string file){
		CMapMemFile map_file;
		map<DWORD, map<DWORD, string>> data_map;	// map<row, map<column, value>>

		if (!map_file.create(file.c_str())) return FALSE;

		map_file.CsvReader(data_map);
		map_file.CloseMapFile();

		load(data_map);

		return TRUE;
	}


};


class CSOS_output
{
public:
	map<DWORD, map<DWORD, map<string, double>>> all_tested_bin1_map;	 // map<x,map<y,map<test,value>>>
	DWORD all_tested_bin1_cnt;

	map<DWORD, map<DWORD, map<string, double>>> outlier_data_map;		 // map<x,map<y,map<test,value>>>
	map<DWORD, map<DWORD, map<string, string>>> outlier_type_map;		 // map<x,map<y,map<test,sos_type>>>
	map<string, vector<double>> distri_vec_map;						 // map<test,vector<distri value>>
	map<string, DWORD> distri_cnt;									 // map<test,distri_cnt>
	map<string, DWORD> sos_cnt;										 // map<test,sos_cnt>
	map<string, DWORD> outlier_cnt;									 // map<test,outlier_cnt>

	void clear(){
		all_tested_bin1_cnt = 0;
		all_tested_bin1_map.clear();
		outlier_data_map.clear();
		outlier_type_map.clear();
		distri_vec_map.clear();
		distri_cnt.clear();
		sos_cnt.clear();
		outlier_cnt.clear();
	}

	CSOS_output(void) {
		all_tested_bin1_cnt = 0;
		all_tested_bin1_map.clear();
		outlier_data_map.clear();
		outlier_type_map.clear();
		distri_vec_map.clear();
		distri_cnt.clear();
		sos_cnt.clear();
		outlier_cnt.clear();
	}
	~CSOS_output(void) {}
};