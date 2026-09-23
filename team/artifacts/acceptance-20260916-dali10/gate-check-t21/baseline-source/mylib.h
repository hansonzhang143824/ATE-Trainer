#pragma once

#include <io.h>
#include <string>
#include <time.h>
#include <fstream>
#include "StdAfx.h"

using namespace std;
class Cmylib{
public:
	string GetSysTime(void){
		time_t raw_time;
		tm time_info;
		time(&raw_time);
		localtime_s(&time_info, &raw_time);
		char c_time[32];

		strftime(c_time, sizeof(c_time), "%Y-%m-%d %H%M%S", &time_info);
		string str_time(c_time);

		return str_time;
	}
	void separate_bits(int date1[SITE_NUM], int date2[SITE_NUM], int date3[SITE_NUM], int date4[SITE_NUM], int result[]) {
		int a1[SITE_NUM][24] = { 0 };
		int a2[SITE_NUM][24] = { 0 };
		int a3[SITE_NUM][24] = { 0 };
		int a4[SITE_NUM][24] = { 0 };
		int b1[SITE_NUM] = { 0 };
		int b2[SITE_NUM] = { 0 };
		int b3[SITE_NUM] = { 0 };
		int b4[SITE_NUM] = { 0 };
		for (int i = 0; i < 24; ++i)
		{
			SERIAL a1[SITE][i] = date1[SITE] >> i & 0x1;
			SERIAL a2[SITE][i] = date2[SITE] >> i & 0x1;
			SERIAL a3[SITE][i] = date3[SITE] >> i & 0x1;
			SERIAL a4[SITE][i] = date4[SITE] >> i & 0x1;
		}

		SERIAL b1[SITE] = a1[SITE][1] * 1 + a1[SITE][4] * 2 + a1[SITE][7] * 4 + a1[SITE][10] * 8 + a1[SITE][13] * 16 + a1[SITE][16] * 32 + a1[SITE][19] * 64 + a1[SITE][22] * 128;
		SERIAL b2[SITE] = a2[SITE][1] * 1 + a2[SITE][4] * 2 + a2[SITE][7] * 4 + a2[SITE][10] * 8 + a2[SITE][13] * 16 + a2[SITE][16] * 32 + a2[SITE][19] * 64 + a2[SITE][22] * 128;
		SERIAL b3[SITE] = a3[SITE][1] * 1 + a3[SITE][4] * 2 + a3[SITE][7] * 4 + a3[SITE][10] * 8 + a3[SITE][13] * 16 + a3[SITE][16] * 32 + a3[SITE][19] * 64 + a3[SITE][22] * 128;
		SERIAL b4[SITE] = a4[SITE][1] * 1 + a4[SITE][4] * 2 + a4[SITE][7] * 4 + a4[SITE][10] * 8 + a4[SITE][13] * 16 + a4[SITE][16] * 32 + a4[SITE][19] * 64 + a4[SITE][22] * 128;

		SERIAL result[SITE] = (b4[SITE] << 24) + (b3[SITE] << 16) + (b2[SITE] << 8) + b1[SITE];
	}
	BOOL FilePathFormat(string &path){
		string temp;
		vector<string> vec;

		split(path, "\\\\", vec);
		for (vector<string>::iterator it = vec.begin(); it != vec.end(); ++it)
			if (it != vec.end() - 1)
				temp = temp + (*it) + "\\";
			else
				temp = temp + (*it);

		path = temp;

		return TRUE;
	}

	BOOL IsFileExist(const char * file_name){
		fstream file;
		file.open(file_name, ios::in);
		if (!file){
			return FALSE;
		}
		else{
			file.close();
			return TRUE;
		}

	}

	BOOL IsFolderExist(const char * file_name)
	{
		if (_access(file_name, 0) == 0)
			return TRUE;
		else
			return FALSE;
	}

	BOOL IsFileExist(string path, string type){
		string dir = path + "\\" + type;
		WIN32_FIND_DATA FindFileData;
		HANDLE hFind;
		LPCTSTR bufDir;
		bufDir = (LPCTSTR)(dir.c_str());
		hFind = FindFirstFile(bufDir, &FindFileData);
		if (hFind == INVALID_HANDLE_VALUE)
			return FALSE;
		else
			return TRUE;
	}

	BOOL myDeleteFile(string path, string name){

		if (IsFileExist(path, name)){
			string cmd = "del /s /q " + path + "\\" + name;
			system(cmd.c_str());
		}

		return TRUE;
	}

	BOOL myDeleteFile(string file){

		if (IsFileExist(file.c_str())){
			string cmd = "del /s /q " + file;
			system(cmd.c_str());
		}

		return TRUE;
	}

	BOOL IsFileOpen(string file){
		//FILE *fp = NULL;
		//fopen_s(&fp, file.c_str(), "r");
		//HANDLE hFile;

		HANDLE hFile = CreateFile(file.c_str(),		 // file to open
			GENERIC_READ,		 // open for reading
			0,					 // share for reading
			NULL,				 // default security
			OPEN_EXISTING,		 // existing file only
			FILE_ATTRIBUTE_NORMAL,// normal file
			NULL);				 // no attr. template
		//fp = NULL;


		if (hFile == INVALID_HANDLE_VALUE){	// file is open
			CloseHandle(hFile);
			return TRUE;
		}
		else{
			CloseHandle(hFile);
			return FALSE;
		}
	}

	BOOL EagleUnitConversion(map<string, string>& unit_map){
		map<string, string> conversion_map;
		conversion_map["KV"] = "kV";
		conversion_map["MV"] = "mV";
		conversion_map["UV"] = "uV";
		conversion_map["NV"] = "nV";
		conversion_map["MA"] = "mA";
		conversion_map["UA"] = "uA";
		conversion_map["NA"] = "nA";
		conversion_map["PA"] = "pA";
		conversion_map["MH"] = "mH";
		conversion_map["UF"] = "uF";
		conversion_map["NF"] = "uF";
		conversion_map["PF"] = "pF";
		conversion_map["MW"] = "mW";
		conversion_map["UW"] = "uW";
		conversion_map["MS"] = "ms";

		conversion_map["US"] = "us";
		conversion_map["NS"] = "ns";
		conversion_map["MDGR"] = "mDGR";
		conversion_map["MRAD"] = "mRAD";
		conversion_map["MM"] = "mm";
		conversion_map["UM"] = "um";
		conversion_map["OHM"] = "ohm";
		conversion_map["KOHM"] = "kohm";
		conversion_map["MOHM"] = "Mohm";
		conversion_map["HZ"] = "Hz";
		conversion_map["KHZ"] = "KHz";
		conversion_map["MHZ"] = "MHz";
		conversion_map["GHZ"] = "GHz";
		conversion_map["PCNT"] = "%";
		conversion_map["PPM"] = "ppm";

		for (map<string, string>::iterator it = unit_map.begin(); it != unit_map.end(); ++it){
			if (conversion_map.find((*it).second) != conversion_map.end())
				(*it).second = conversion_map[(*it).second];
		}

		return TRUE;
	}

	void align_to_max(map<string, string>& imap){
		size_t max = 0;
		for (map<string, string>::iterator it = imap.begin(); it != imap.end(); ++it){
			if ((*it).second.length() > max)
				max = (*it).second.length();
		}
		for (map<string, string>::iterator it = imap.begin(); it != imap.end(); ++it){
			if (max > (*it).second.length()){
				string temp(max - (*it).second.length(), ' ');
				(*it).second = (*it).second + temp;
			}
		}
	}

	void align_to_21(map<string, string>& imap){
		for (map<string, string>::iterator it = imap.begin(); it != imap.end(); ++it){
			if ((*it).second.find(' ') != string::npos){	// delete one ' '
				size_t pos = (*it).second.find(' ');
				string part1 = (*it).second.substr(0, pos);
				string part2 = (*it).second.substr(pos + 1, (*it).second.length() - pos - 1);
				(*it).second = part1 + part2;
			}
			if (21 > (*it).second.length()){
				string temp(21 - (*it).second.length(), ' ');
				(*it).second = (*it).second + temp;
			}
			else if (21 < (*it).second.length()){
				string temp((*it).second, 0, 21);
				(*it).second = temp;
			}
		}
	}

	void convert_test_format(const map<string, string>& in_map, map<string, string>& out_map){
		for (map<string, string>::const_iterator it = in_map.begin(); it != in_map.end(); ++it){
			if ((*it).first.find('.') != string::npos){
				size_t pos = (*it).first.find('.');
				string test((*it).first);
				test = test.replace(pos, 1, "0000");
				out_map[(*it).first] = test;
			}
		}
	}

	// cell(1,2) to B1
	string convert_cell_format(DWORD row, DWORD column){
		string result;

		if ((row <= 1048576) && (column <= 16384)){
			while (column--){
				result = result + char((column % 26) + 'A');
				column /= 26;
			}
			result = result.assign(result.rbegin(), result.rend());
			result = result + int2str(row);
		}

		return result;
	}

	string int2str(DWORD n) {

		char t[64];
		int i = 0;

		if (n == 0)
			return "0";

		while (n) {
			t[i++] = char((n % 10) + '0');
			n /= 10;
		}
		t[i] = 0;

		string result(t);
		result = result.assign(result.rbegin(), result.rend());

		return result;
	}

	string float2str(double f){
		char buf[64];
		_gcvt_s(buf, 64, f, 8);
		string result(buf);
		if (result.length() > 1)
			if (result.find(".") == result.length() - 1){
				string temp(result, 0, result.length() - 1);
				result = temp;
			}

		return result;
	}

	string GetFileName(string path){
		size_t start = 0;
		size_t end = 0;
		start = path.find_last_of("\\");
		end = path.find('.');

		string name(path, start + 1, end - start - 1);

		return name;
	}

	string GetFilePostfix(string path){
		size_t start = 0;
		size_t end = 0;
		start = path.find('.');
		end = path.length();

		string postfix(path, start + 1, end - start - 1);

		return postfix;
	}

	string GetFileFolderPath(string path){
		size_t pos = 0;
		pos = path.find_last_of("\\");

		string name(path, 0, pos + 1);

		return name;
	}

	double average(vector<double> & vec){
		if (vec.empty()) return 0;

		double avg = 0;

		for (vector<double>::iterator it = vec.begin(); it != vec.end(); ++it)	avg += (*it);

		avg /= vec.size();

		return avg;
	}

	double deviation(vector<double> & vec){
		double avg = 0;
		double s = 0;

		for (vector<double>::iterator it = vec.begin(); it != vec.end(); ++it)	avg += (*it);

		avg /= vec.size();

		for (vector<double>::iterator it = vec.begin(); it != vec.end(); ++it)	s += pow((*it) - avg, 2);

		if (vec.size() > 1)
			s /= (vec.size() - 1);

		s = sqrt(s);

		return s;
	}

	void deviation(vector<double> & vec, double& mean, double& sigma){
		if (vec.size() > 1){
			mean = 0;
			sigma = 0;
			for (vector<double>::iterator it = vec.begin(); it != vec.end(); ++it){
				mean += (*it);
			}
			mean /= vec.size();
			for (vector<double>::iterator it = vec.begin(); it != vec.end(); ++it){
				sigma += pow((*it) - mean, 2);
			}
			sigma /= (vec.size() - 1);
			sigma = sqrt(sigma);
		}
	}

	void deviation(DWORD cnt_old, double mean_old, double sigma_old, double value_new, double& mean_new, double& sigma_new){
		mean_new = (cnt_old * mean_old + value_new) / (cnt_old + 1);
		sigma_new = pow((cnt_old * pow(sigma_old, 2) + cnt_old * pow(mean_old - mean_new, 2) + pow(value_new - mean_new, 2)) / (cnt_old + 1), 0.5);
	}

	//
	//string SelectFolderPath(HWND hWnd){
	//	char szPath[MAX_PATH];
	//
	//	ZeroMemory(szPath, sizeof(szPath));
	//
	//	BROWSEINFO bi;
	//	bi.hwndOwner = hWnd;
	//	bi.pidlRoot = NULL;
	//	bi.pszDisplayName = szPath;
	//	bi.lpszTitle = "Please select the folder path: ";
	//	bi.ulFlags = 0;
	//	bi.lpfn = NULL;
	//	bi.lParam = 0;
	//	bi.iImage = 0;
	//
	//	LPITEMIDLIST lp = SHBrowseForFolder(&bi);
	//
	//	if(lp && SHGetPathFromIDList(lp, szPath)){
	//		string path(szPath);
	//		return path;
	//	} else {
	//		return "NULL";
	//	}
	//}

	//static int CALLBACK SHBrowserForFolderCallbackProc(HWND hwnd, UINT uMsg, LPARAM lParam, LPARAM lpData){
	//	switch(uMsg){
	//	case BFFM_INITIALIZED:
	//		::SendMessage(hwnd, BFFM_SETSELECTION, TRUE, (LPARAM)(LPTSTR)(LPCTSTR)m_filePath);
	//		break;
	//	case BFFM_SELCHANGED:
	//		TCHAR curr[MAX_PATH];
	//		SHGetPathFromIDList((LPCITEMIDLIST)lParam, curr);
	//		::SendMessage(hwnd, BFFM_SETSTATUSTEXT, 0, (LPARAM)curr);
	//		break;
	//	default:
	//		break;
	//	}
	//	return 0;
	//}

	//static string SelectFolderPath(HWND hWnd){
	//	char szPath[MAX_PATH];
	//
	//	ZeroMemory(szPath, sizeof(szPath));
	//
	//	BROWSEINFO bi;
	//	bi.hwndOwner = hWnd;
	//	bi.pidlRoot = NULL;
	//	bi.pszDisplayName = szPath;
	//	bi.lpszTitle = "Please select the folder path: \nIf the path is C:\\, Output file will be put in input file folder";
	//	bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_EDITBOX; // With folder path text edit, and only valid path showed.
	//	bi.lpfn = SHBrowserForFolderCallbackProc;
	//	bi.lParam = 0;
	//	bi.iImage = 0;
	//
	//	LPITEMIDLIST lp = SHBrowseForFolder(&bi);
	//
	//	if(lp && SHGetPathFromIDList(lp, szPath)){
	//		string path(szPath);
	//		return path;
	//	} else {
	//		return "NULL";
	//	}
	//}

	void split(const string &s, const string &seperator, vector<string> &result){
		size_t i = 0;

		while (i != s.size()){
			int flag = 0;
			while ((i != s.size()) && (flag == 0)){
				flag = 1;
				for (size_t x = 0; x < seperator.size(); ++x)
					if (s[i] == seperator[x]){
						++i;
						flag = 0;
						break;
					}
			}

			flag = 0;
			size_t j = i;
			while ((j != s.size()) && (flag == 0)){
				for (size_t x = 0; x < seperator.size(); ++x)
					if (s[j] == seperator[x]){
						flag = 1;
						break;
					}
				if (flag == 0)
					++j;
			}
			if (i != j){
				result.push_back(s.substr(i, j - i));
				i = j;
			}
		}
	}

	// 3.5_85 to vin=3.5 temp=85
	void split_level(string level, string &vin, string &temp){
		size_t pos = level.find('_');
		if (pos != string::npos){
			string vin_str(level, 0, pos);
			string temp_str(level, pos + 1, level.length() - pos);
			vin = vin_str;
			temp = temp_str;
		}
	}

	// [-40,0,25,85,125] ---->
	// -40
	// 0
	// 25
	// 85
	// 125
	BOOL split_a_bracket(vector<string> & vec, string multi_no){
		if (multi_no == "")
			return FALSE;

		vec.clear();

		if (multi_no.find('[') == string::npos)
			vec.push_back(multi_no);

		size_t begin_of_word = 1;
		for (size_t i = 1; i < multi_no.length(); ++i){
			if ((multi_no[i] == ',') || (multi_no[i] == ']')){
				if (i == begin_of_word){
					cout << "Error multi number format, like [-40,,25,85] ..." << endl;
					return FALSE;
					break;
				}
				else {
					string word(multi_no, begin_of_word, i - begin_of_word);
					vec.push_back(word);
				}

				begin_of_word = i + 1;
			}
		}

		return TRUE;
	}

	//[3,4][0,1]0[8,9].1 ---->
	//[3,4]
	//[0,1]
	//0
	//[8,9]
	//.1
	BOOL split_multi_seg(vector<string> & seg_vec, string multi_testno_str){
		if (multi_testno_str == "")
			return FALSE;

		size_t begin_of_seg = 0;

		for (size_t i = 0; i < multi_testno_str.length(); ++i){
			if ((multi_testno_str[i] == '[') && (i != 0) && (i != begin_of_seg)){
				string seg(multi_testno_str, begin_of_seg, i - begin_of_seg);
				seg_vec.push_back(seg);
				begin_of_seg = i;
			}
			if ((multi_testno_str[i] == ']') || ((multi_testno_str[i] != ']') && (i == multi_testno_str.length() - 1))){
				string seg(multi_testno_str, begin_of_seg, i - begin_of_seg + 1);
				seg_vec.push_back(seg);
				begin_of_seg = i + 1;
			}
		}

		return TRUE;
	}

	//[3,4][0,1]0[8,9].1 ---->
	//3008.1
	//3009.1
	//3108.1
	//3109.1
	//4008.1
	//4009.1
	//4108.1
	//4109.1
	BOOL get_items_from_multi_bracket_string(vector<string> & item_vec, string multi_bracket_string){
		vector<string> seg_vec;
		split_multi_seg(seg_vec, multi_bracket_string);

		//list<string> testno_list;
		item_vec.clear();
		for (vector<string>::iterator it = seg_vec.begin(); it != seg_vec.end(); it++){
			if ((*it).find('[') == string::npos){
				if (item_vec.empty())
					item_vec.push_back(*it);
				else
					for (vector<string>::iterator it_item_vec = item_vec.begin(); it_item_vec != item_vec.end(); ++it_item_vec)
						(*it_item_vec) = (*it_item_vec) + (*it);
			}
			else{
				vector<string> multi_no_vec; // record [0,1]
				vector<string> temp_vec(item_vec);

				item_vec.clear();
				if (temp_vec.empty()){
					if (!split_a_bracket(multi_no_vec, *it))
						return FALSE;

					for (vector<string>::iterator it_multi_no_vec = multi_no_vec.begin(); it_multi_no_vec != multi_no_vec.end(); ++it_multi_no_vec){
						item_vec.push_back(*it_multi_no_vec);
					}

					multi_no_vec.clear();
				}
				else{
					for (vector<string>::iterator it_item_vec = temp_vec.begin(); it_item_vec != temp_vec.end(); ++it_item_vec){
						split_a_bracket(multi_no_vec, *it);

						for (vector<string>::iterator it_multi_no_vec = multi_no_vec.begin(); it_multi_no_vec != multi_no_vec.end(); ++it_multi_no_vec){
							item_vec.push_back(*it_item_vec + *it_multi_no_vec);
						}

						multi_no_vec.clear();
					}
				}
			}
		}
		return TRUE;
	}

	// Judge is it "*[n-m]*" type string ?
	BOOL is_range_bracket_string(string str){
		BOOL comma_flag = FALSE;
		BOOL sub_flag = FALSE;
		BOOL bracket_flag = FALSE;

		if (str == "")
			return FALSE;

		for (size_t i = 0; i < str.length(); ++i){
			if (str[i] == '[')
				bracket_flag = TRUE;
			if (str[i] == ']'){
				if (bracket_flag && sub_flag && !comma_flag)
					return TRUE;

				bracket_flag = FALSE;
				comma_flag = FALSE;
				sub_flag = FALSE;
			}
			if (str[i] == ',')
				comma_flag = TRUE;
			if (str[i] == '-')
				sub_flag = TRUE;

		}

		return FALSE;
	}

	//[0-3] ----> 
	//[0,1,2,3] 
	//or
	//[10-13] ----> 
	//[10,11,12,13] 
	BOOL range_to_list_bracket_string(string & str){
		size_t sub_pos = str.find('-');
		string start_str(str, 1, sub_pos - 1);
		string stop_str(str, sub_pos + 1, str.length() - sub_pos - 2);
		int start_int = atoi(start_str.c_str());
		int stop_int = atoi(stop_str.c_str());

		string result = "[";
		for (int i = start_int; i <= stop_int; ++i){
			result = result + int2str(i);
			if (i != stop_int)
				result = result + ',';
		}

		result = result + ']';
		str = result;

		return TRUE;
	}

	//200[0-3].1 ----> 
	//200[0,1,2,3].1 
	BOOL range_to_list_multi_bracket_string(string & str){
		string result;
		BOOL bracket_flag = FALSE;
		string bracket_str;

		if (!is_range_bracket_string(str)){
			return TRUE;
		}

		for (size_t i = 0; i < str.length(); ++i){

			if (str[i] == '[')
				bracket_flag = TRUE;

			if (str[i] == ']'){
				bracket_str = bracket_str + str[i];
				if (is_range_bracket_string(bracket_str)){
					range_to_list_bracket_string(bracket_str);
					result = result + bracket_str;
				}

				bracket_str = "";
				bracket_flag = FALSE;
			}
			else {
				if (!bracket_flag)
					result = result + str[i];
				else
					bracket_str = bracket_str + str[i];
			}

		}

		str = result;

		return TRUE;
	}

	//overload for map<string, map<DWORD, DWORD>> type 
	//map<single_test_no_string, map<bracket_number, element_number>>
	//as below example
	//map["3008.1"][0] = 0 ; pos of '3' is 0 at [3,4]
	//map["3008.1"][1] = 0 ; pos of '0' is 0 at [0,1]
	//map["3008.1"][2] = 0 ; pos of '8' is 0 at [8,9]
	//map["3009.1"][0] = 0 ; pos of '3' is 0 at [3,4]
	//map["3009.1"][1] = 0 ; pos of '0' is 0 at [0,1]
	//map["3009.1"][2] = 1 ; pos of '9' is 1 at [8,9]
	//map["4108.1"][0] = 1 ; pos of '4' is 1 at [3,4]
	//map["4108.1"][1] = 1 ; pos of '1' is 1 at [0,1]
	//map["4108.1"][2] = 0 ; pos of '8' is 0 at [8,9]
	//[3,4][0,1]0[8,9].1 ---->
	//3008.1
	//3009.1
	//3108.1
	//3109.1
	//4008.1
	//4009.1
	//4108.1
	//4109.1
	BOOL get_items_from_multi_bracket_string(map<string, map<DWORD, DWORD>> & element_map, string multi_bracket_string){
		//vector<string> item_vec;
		vector<string> seg_vec;
		DWORD bracket_number = 0;
		DWORD element_number = 0;

		range_to_list_multi_bracket_string(multi_bracket_string);
		split_multi_seg(seg_vec, multi_bracket_string);

		//list<string> testno_list;
		//item_vec.clear();
		element_map.clear();
		for (vector<string>::iterator it = seg_vec.begin(); it != seg_vec.end(); it++){
			if ((*it).find('[') == string::npos){ // not bracket type
				//if(item_vec.empty()){
				if (element_map.empty()){
					//item_vec.push_back(*it);
					element_map[*it][0] = 0;
				}
				else{
					//for(vector<string>::iterator it_item_vec = item_vec.begin(); it_item_vec != item_vec.end(); ++it_item_vec)
					//	(*it_item_vec) = (*it_item_vec) + (*it);

					map<string, map<DWORD, DWORD>> temp_map1(element_map); //backup old element_map
					element_map.clear();
					for (map<string, map<DWORD, DWORD>>::iterator it_map1 = temp_map1.begin(); it_map1 != temp_map1.end(); ++it_map1){
						for (map<DWORD, DWORD>::iterator it_map2 = (*it_map1).second.begin(); it_map2 != (*it_map1).second.end(); ++it_map2)
							element_map[(*it_map1).first + (*it)][(*it_map2).first] = (*it_map2).second;
					}
				}
			}
			else{ // bracket type "[0,1]"
				vector<string> multi_no_vec; // record [0,1]
				//vector<string> temp_vec(item_vec); // backup old item_vec
				//map<string, map<DWORD, DWORD>> temp_map2(element_map); //backup old element_map

				//item_vec.clear();
				//if(temp_vec.empty()){
				//temp_map2.clear();
				if (element_map.empty()){
					if (!split_a_bracket(multi_no_vec, *it)) // split bracket [0,1] --> {0,1} to multi_no_vec
						return FALSE;

					// copy multi_no_vec to item_vec
					for (vector<string>::iterator it_multi_no_vec = multi_no_vec.begin(); it_multi_no_vec != multi_no_vec.end(); ++it_multi_no_vec){
						//item_vec.push_back(*it_multi_no_vec);
						element_map[*it_multi_no_vec][bracket_number] = element_number++;
					}
					element_number = 0;
					bracket_number++;

					multi_no_vec.clear();
				}
				else{
					map<string, map<DWORD, DWORD>> temp_map2(element_map); //backup old element_map
					element_map.clear();

					for (map<string, map<DWORD, DWORD>>::iterator it_old_1 = temp_map2.begin(); it_old_1 != temp_map2.end(); ++it_old_1){
						// restore old element_map with old bracket_number
						for (map<DWORD, DWORD>::iterator it_old_2 = (*it_old_1).second.begin(); it_old_2 != (*it_old_1).second.end(); ++it_old_2){
							split_a_bracket(multi_no_vec, *it);

							for (vector<string>::iterator it_multi_no_vec = multi_no_vec.begin(); it_multi_no_vec != multi_no_vec.end(); ++it_multi_no_vec){
								element_map[(*it_old_1).first + *it_multi_no_vec][(*it_old_2).first] = (*it_old_2).second;
							}

							multi_no_vec.clear();
						}

						// add new to element_map
						split_a_bracket(multi_no_vec, *it);

						for (vector<string>::iterator it_multi_no_vec = multi_no_vec.begin(); it_multi_no_vec != multi_no_vec.end(); ++it_multi_no_vec){
							element_map[(*it_old_1).first + *it_multi_no_vec][bracket_number] = element_number++;
						}
						element_number = 0;

						multi_no_vec.clear();
					}

					//for(vector<string>::iterator it_item_vec = temp_vec.begin(); it_item_vec != temp_vec.end(); ++it_item_vec){
					//	split_a_bracket(multi_no_vec, *it);

					//	for(vector<string>::iterator it_multi_no_vec = multi_no_vec.begin(); it_multi_no_vec != multi_no_vec.end(); ++it_multi_no_vec){
					//		item_vec.push_back(*it_item_vec + *it_multi_no_vec);
					//	}

					//	multi_no_vec.clear();
					//}
					bracket_number++;
				} // end of !temp_vec.empty()
			}
		}
		return TRUE;
	}






	static string m_filePath;

	Cmylib(){}
	~Cmylib(){}
};

