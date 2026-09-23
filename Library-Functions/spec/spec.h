/*****************************************************************************
*                                                                            *
*       Source title:   SPEC.h                                               *
*                       (Help treg execute feature in AccoTest)              *
*         Modify by:   SC TE                                                 *
*        Description:  Thx All Contributors                                  *
*                                                                            *
*   Revision History:                                                        *
*                                                                            *
*     mm/dd/yy  r.rr  - Original coding.                                     *
*                                                                            *
*****************************************************************************/

/*
REVISION BLOCK:
-Rev. -- Date --------------------------------------------------
00		ready for upgraded treg for execute
01		update get_step_str for not full steps delog need.		Alan	2018/12/18
----------------------------------------------------------------
*/



#pragma once
#include <map>
#include <vector>
#include <string>
#include <Windows.h>
#include <iostream>
using namespace std;


#define	BAD_POS 0xFFFFFFFF 
#define	SUCCESS 0


//sanfeng start

//#if !defined(__SPEC)
#define __SPEC

//#define  WIN32_LEAN_AND_MEAN             // Exclude rarely-used stuff from Windows headers

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <float.h>
#include <math.h>
#include <assert.h>
#include <ctype.h>
#include <limits.h>     // for PATH_MAX

#ifdef _WIN32
#include <direct.h>
#define getcwd _getcwd
#else
#include <unistd.h>
#endif

//#ifndef SITE_NUM    // windows operating systems
//#define SITE_NUM 12
//#endif

//#include "inireader.h"

//#ifdef WIN32
//#  include <windows.h>
//#  include <direct.h>
//#  include "cdef500d.h"
//#  include "util.h"
//#  include "testmain.h"
////#  include "TiShell.h"
//#else // linux / solaris
//#  include <unistd.h>   // for getcwd

#  define INT64 long
//#  define _stricmp strcasecmp
//#  define _getcwd getcwd
//#  define _MAX_PATH PATH_MAX
//#endif

#define DEL(p)     if(p){delete [] p; p=NULL;}
#define DEL_OBJ(p) if(p){delete    p; p=NULL;}

#define _INTERNAL_PARAMETER  "__int_param"
#define _INTERNAL_INDEX      ((unsigned)-1)
#define _DEFAULT             "DEFAULT"

///////////////////////////////////////////////////////////////////////////////
class INDEX{
	friend      class SPEC;
	friend      class PARAMETER;
public:
	INDEX       &operator= (double index_value);
	INDEX       &operator= (int index_value);
	INDEX       &operator= (unsigned index_value);
	INDEX       &operator= (INT64 index_value);
	INDEX       &operator= (bool index_value);
	INDEX       &operator= (INDEX &i);
	operator const double();
	const char  *get_str();
	void        protect();
	INDEX       &unprotect();
private:
	INDEX(unsigned index, double index_value, const char *index_str);
	~INDEX();
	INDEX       *pre_node;
	INDEX       *next_node;
	unsigned    name;
	double      value;
	char        *str_value;
	bool        isprotected;
};

///////////////////////////////////////////////////////////////////////////////
class PARAMETER{
	friend      class SPEC;
	friend      class DEVICE;
public:
	unsigned    count() { return num_index; };
	INDEX       *add_index(unsigned index, double index_value, const char *index_str);
	INDEX       &operator[] (unsigned index);
	PARAMETER   &operator= (double param_value);
	PARAMETER   &operator= (int param_value);
	PARAMETER   &operator= (unsigned param_value);
	PARAMETER   &operator= (INT64 param_value);
	PARAMETER   &operator= (bool param_value);
	PARAMETER   &operator= (PARAMETER &p);

	operator const double();
	operator string();
	const char  *get_str();
	void        protect();
	PARAMETER   &unprotect();
	INDEX       *getNextIndex();
	void set_select_value(double temp_value);// add by hanson
	void set_select_index(int temp_index);// add by hanson
	//void set_vin_value(double temp_value);// add by hanson
	//void set_vin_index(int temp_index);// add by hanson
	string  get_param_name_in_spec();// add by hanson
private:
	PARAMETER(const char *param_name, double param_value, const char *param_str);
	~PARAMETER();
	INDEX       *find_index(unsigned index);
	PARAMETER   *pre_node;
	PARAMETER   *next_node;
	INDEX       *index_root;    // used for adding INDEX objects
	INDEX       *current_index;
	char        *name;
	unsigned    num_index;
	double      value;
	char        *str_value;
	bool        isprotected;
	double para_temp_value;// add by hanson
	int user_set_index;// add by hanson
	bool user_set_index_check;// add by hanson
	string string_value;
};

///////////////////////////////////////////////////////////////////////////////
class DEVICE{
	friend      class SPEC;
public:
	unsigned    count() { return num_params; };
	char		*devicename() { return name; };
	PARAMETER   *add_param(const char *param_name, double param_value, const char *param_str);
	PARAMETER   &operator() (const char *param_name);
	PARAMETER   *getNextParam();
private:
	DEVICE(const char *device_name);
	~DEVICE();
	PARAMETER   *find_param(const char *param_name);
	DEVICE      *pre_node;
	DEVICE      *next_node;
	PARAMETER   *param_root;
	PARAMETER   *current_param;
	char        *name;
	unsigned    num_params;
};

///////////////////////////////////////////////////////////////////////////////


class CMapMemFile
{
private:
	HANDLE hFile;
	HANDLE hMapFile;
	DWORD size_low, size_high;	// no bigger than 4G
	DWORD error_code;
	const char* fileName;

	BOOL bMapOK;

	void* pvFile;
	unsigned char* p;

	//for load_data_to_db
	DWORD tab_ent_cnt;	// include '/t' and '/n'
	DWORD columns_of_one_row;
	DWORD column_no;
	DWORD row_no;

public:
	string error_str;

public:
	CMapMemFile(void){
		hFile = NULL;
		hMapFile = NULL;
		pvFile = NULL;
		p = NULL;
		size_low = 0;
		size_high = 0;
		error_code = 0;
		bMapOK = FALSE;
		tab_ent_cnt = 0;
		columns_of_one_row = 0;
		column_no = 0;
		row_no = 0;
	}

	// create for read only
	BOOL create(const char* file){
		fileName = file;
		hFile = CreateFile(
			fileName,
			GENERIC_READ,
			FILE_SHARE_READ,
			NULL,
			OPEN_EXISTING,
			FILE_ATTRIBUTE_NORMAL,
			0);

		if (hFile == INVALID_HANDLE_VALUE) {
			bMapOK = false;
			error_code = GetLastError();
			error_str = "Fail CreateFile, hFile == INVALID_HANDLE_VALUE";
			//cout<<"create map file failure:"<<error_code<<endl;
			return FALSE;
		}
		else{
			size_low = GetFileSize(hFile, &size_high);
			if (size_low == BAD_POS && (error_code = GetLastError()) != SUCCESS) {
				bMapOK = false;
				CloseHandle(hFile);
				error_str = "Fail GetFileSize";
				//cout<<"error :"<<error_code<<endl;
				return FALSE;
			}
			else{
				bMapOK = true;
				//cout<<"Create map file suceess"<<endl;
			}
		}

		hMapFile = CreateFileMapping(
			hFile,
			NULL,
			PAGE_READONLY,
			size_high,
			size_low,
			NULL
			);
		if (size_high > 0){
			bMapOK = FALSE;
			error_str = "Can't create file bigger than 4G.";
			//cout << "Can't create file bigger than 4G." << endl;
			CloseHandle(hFile);
			return FALSE;
		}
		if (hMapFile == INVALID_HANDLE_VALUE){
			bMapOK = FALSE;
			error_str = "Fail CreateFileMapping, hMapFile == INVALID_HANDLE_VALUE";
			//cout << "Can't create file mapping. Error: " << GetLastError() << endl;
			CloseHandle(hFile);
			return FALSE;
		}
		else {
			bMapOK = TRUE;
			//cout << "Create file mapping suceess!" << endl;
		}

		if (bMapOK){
			pvFile = MapViewOfFile(
				hMapFile,
				FILE_MAP_READ,
				0,
				0,
				0);
			if ((error_code = GetLastError()) != SUCCESS) {
				bMapOK = false;
				error_str = "Fail MapViewOfFile";
				//cout<<"error :"<<error_code<<endl;
				return FALSE;
			}
			p = (unsigned char*)pvFile;
		}

		return TRUE;
	}

	// over load create function for new file
	BOOL create(const char* file, DWORD size){
		fileName = file;
		hFile = CreateFile(
			fileName,
			GENERIC_READ | GENERIC_WRITE,
			FILE_SHARE_READ | FILE_SHARE_WRITE,
			NULL,
			//CREATE_NEW,
			OPEN_ALWAYS,	// if no exist, create new
			FILE_ATTRIBUTE_NORMAL,
			0);

		if (hFile == INVALID_HANDLE_VALUE) {
			bMapOK = false;
			error_code = GetLastError();
			error_str = "Fail CreateFile, hFile == INVALID_HANDLE_VALUE";
			//cout << "create file fail: " << error_code << endl;
			//cout << "file name is: " << fileName << endl;
			return FALSE;
		}

		size_high = 0;
		size_low = size;
		hMapFile = CreateFileMapping(
			hFile,
			NULL,
			PAGE_READWRITE,
			size_high,
			size_low,
			NULL
			);
		if (size_high > 0){
			bMapOK = FALSE;
			error_str = "Can't create file bigger than 4G.";
			//cout << "Can't create file bigger than 4G." << endl;
			CloseHandle(hFile);
			return FALSE;
		}
		if (hMapFile == INVALID_HANDLE_VALUE){
			bMapOK = FALSE;
			error_str = "Fail CreateFileMapping, hMapFile == INVALID_HANDLE_VALUE";
			//cout << "can't create file mapping. Error: " << GetLastError() << endl;
			CloseHandle(hFile);
			return FALSE;
		}
		else {
			bMapOK = TRUE;
			//cout << "create file mapping suceess!" << endl;
		}

		if (bMapOK){
			pvFile = MapViewOfFile(
				hMapFile,
				FILE_MAP_READ | FILE_MAP_WRITE,
				0,
				0,
				0);
			if ((error_code = GetLastError()) != SUCCESS) {
				bMapOK = false;
				error_str = "Fail MapViewOfFile";
				return FALSE;
			}
			p = (unsigned char*)pvFile;
		}

		return TRUE;
	}

	DWORD find_a_word(string name, const unsigned char separator, const DWORD size){
		if (!bMapOK){
			cout << "Map fail, When find index name in file head." << endl;
			return BAD_POS;
		}

		if (p == NULL){
			cout << "Map point error, When find index name in file head." << endl;
			return BAD_POS;
		}

		if (size >= size_low){
			cout << "Size is over map file range, When find index name in file head." << endl;
			return BAD_POS;
		}

		if (name == ""){
			cout << "Name can't be blank, When find index name in file head." << endl;
		}

		// ignore '!' before name
		if (name[0] == '!'){
			string temp(name, 1, name.length() - 1);
			name = temp;
		}

		DWORD column = 0;
		DWORD first_pos_of_word = 0;
		//size_t size_name = 0; 

		DWORD start = 0;
		if ((p[0] < 33) || (p[0] > 126)){
			start = 3;
			first_pos_of_word = 3;
		}

		for (DWORD i = start; i < size; ++i){
			if ((p[i] == separator) || (p[i] == '\n') || (p[i] == 13)){	// the last column, it maybe return key
				column++;
				//size_name = strlen(name);

				if ((i - first_pos_of_word) == name.length()){	// compare only if the length is same
					for (DWORD j = 0; j < name.length(); ++j){
						if (p[first_pos_of_word + j] != name[j])
							break;
						else{
							if (j == name.length() - 1)
								return column;
						}
					}
				}

				first_pos_of_word = i + 1;
			}
		}


		//stringstream ss(p);
		//while(getline(ss,word,'\t')){
		//	if(word.compare(name) == 0){
		//		column++;
		//		return column;
		//	}
		//	else
		//		column++;
		//}

		return BAD_POS;
	}

	void CloseMapFile(void){
		if (pvFile != NULL){
			UnmapViewOfFile(pvFile);
			pvFile = NULL;
			p = NULL;
		}
		if (hMapFile != NULL){
			CloseHandle(hMapFile);
			hMapFile = NULL;
		}
		if (hFile != NULL){
			CloseHandle(hFile);
			hFile = NULL;
		}
	}

	BOOL IsMapOK(){
		return bMapOK;
	}

	DWORD GetSize(){
		return size_low;
	}

	unsigned char * GetPtr(){
		return p;
	}

	BOOL write(const char * words, DWORD len){
		if (!IsMapOK()){
			cout << "Map fail, When write words." << endl;
			return FALSE;
		}
		if (len > size_low){
			cout << "The size of the words is over range of mapped file, write fail." << endl;
			return FALSE;
		}

		try{
			for (DWORD i = 0; i<len; ++i){
				p[i] = words[i];
			}
		}
		catch (exception & e){
			cout << "write file fail: " << endl;
			cout << e.what() << endl;
			return FALSE;
		}

		return TRUE;
	}

	////////// add by developer //////////////
	BOOL CsvReader(map<DWORD, map<DWORD, string>> &res_map);



public:
	~CMapMemFile(void){}
};

class LOG_TRIM{
public:
	vector<string> step_vec;
	string str_pre;
	string str_pre_bit;
	string str_post;
	string str_post_rt;
	string str_post_bit;
	string str_target;
	string str_guessed;
	string str_updated;

public:
	LOG_TRIM(void){}
	~LOG_TRIM(void){}
};






class SPEC{

	friend      class DEVICE;
	friend      class PARAMETER;
	friend      class INDEX;

public:
	SPEC(bool unprotect_all = false);
	~SPEC();

	bool init();
	bool print(void);

	double get_low_limit(string param);
	double get_high_limit(string param);
	string get_unit(string param);
	double  get_high_limit(LPCTSTR funclabel, int fun_index);
	double get_low_limit(LPCTSTR funclabel, int fun_index);
	string get_para_name(LPCTSTR funclabel, int fun_index);

	string get_step_str(LPCTSTR funclabel, unsigned int step);
	string get_pre_str(LPCTSTR funclabel);
	string get_pre_bit_str(LPCTSTR funclabel);
	string get_post_str(LPCTSTR funclabel);
	string get_post_rt_str(LPCTSTR funclabel);
	string get_post_bit_str(LPCTSTR funclabel);
	string get_target_str(LPCTSTR funclabel);
	string get_guessed_str(LPCTSTR funclabel);
	string get_updated_str(LPCTSTR funclabel);

	string int2str(DWORD n);

	void SetTestFuncDisableByFuncName(string func_name);
	void SetTestFuncDisableByFuncIndex(int func_index);

	unsigned    devicecount() { return num_devices; };
	bool        init(const char *file_name);
	//bool        initial(string file);
	bool        dump(const char *file_name);
	bool        select_device(const char *device_name);
	const char  *get_device_str();
	const int   get_device_num(const int min_digits = 0);
	DEVICE      *add_device(const char *device_name);
	PARAMETER   &operator() (const char *param_name);
	DEVICE      &operator[] (const char *device_name);
	DEVICE      &operator[] (string device_name);
	DEVICE      *getNextDevice();
	void        register_temp_state_func(int(*func)(void)); // user function must return 0 for "amb", 1 for "hot", 2 for "cold"
	void        register_error_func(void(*func)(const char *));
	int get_sel_vin_index();
	void set_sel_vin_index(int set_val);
	int get_sel_temp_index();
	void set_sel_temp_index(int set_val);
	DWORD start = 1;
	DWORD stop = 1;

	void get_parameter_name_in_spec_doc();

	void get_all_function_name(vector<string> *func_name_sum, int *func_sum);
	void get_funcname_vs_paracnt_matrix(string  funcname, int *total_para_cnt);
	void initial_device_position();
	bool clarify_os_fail_type(string  funcname);
private:
	unsigned int site_num;
	string path;
	map<DWORD, map<DWORD, string>> pgs_map;
	vector<string> param_vec;
	map<string, string> func_map;	//map<func, param>
	map<string, string> lolim_map;	//map<param, lolim>
	map<string, string> hilim_map;	//map<param, hilim>
	map<string, string> unit_map;	//map<param, unit>

	map<string, LOG_TRIM> trim_map;	//map<func, trim_param>
	map<int, string>func_index_map; //map<func, function_start_index>

	static void error(const char *msg, ...);
	void        strcpy_dynamic(char **destination, const char *source);
	DEVICE      *find_device(const char *device_name);
	DEVICE      *device_root;
	DEVICE      *current_device;
	char        *selected_device;
	unsigned    num_devices;
	static bool isprotected;
	static int(*temp_state_func)(void);
	static void(*error_func)(const char *);
	int         minimum_device_digits;

	int manual_select_vin_index;

	int manual_select_temp_index;

	//PARAMETER param_array[1024];
};

class CFunc{
public:
	int bstr2int(string str);

public:
	CFunc(void){}
	~CFunc(void){}
};



class CBIT{
public:
	//map<param_name, param_bit_addr, absolute_bit_addr>
	//as map<"CSNS2_slope", map<0, 8>>
	//as map<"CSNS2_slope", map<1, 10>>
	//as map<"CSNS2_slope", map<2, 9>>
	//as map<"CSNS2_slope", map<3, 11>>
	map<string, map<int, int>> addr_map;

	//map<param_name, target> 
	//for option bit, target is "SEL"
	map<string, string> target_map;
	//map<param_name, default step>
	map<string, int> default_map;

	//map<param_name, map<step, value>>
	map<string, map<int, double>> step_map;
	map<string, map<int, double>> step_pcnt_map;


	string path;

public:
	bool init(string file);
	bool print(void);

public:
	CBIT(void){}
	~CBIT(void){}
};

