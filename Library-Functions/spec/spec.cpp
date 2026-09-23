#include "stdafx.h"
#include "inireader.h"
#include "spec.h"
#include<string>

//#include <graphics.h>		// 引用 EasyX 绘图库头文件
//#include<stdio.h>
//#include <time.h>//时间
//#include<stdlib.h>
//#include<mmsystem.h>
//#pragma comment (lib,"winmm.lib")


extern "C" int GetPgsFullPath(LPTSTR pgsPath, int chNum);



const char *temp_states[] = { "amb", "hot", "cold" };

int(*SPEC::temp_state_func)(void) = NULL;
void(*SPEC::error_func)(const char *) = NULL;
bool SPEC::isprotected = true;

//#ifdef WIN32
//static void etsfatalerror_wrapper(const char *msg){ etsfatalerror((char *)msg); }
//#endif

static void clean(char **source){
	if ((*source != NULL) && strlen(*source)){
		char *destination = new char[strlen(*source) + 1];
		char *d = destination;
		int cnt = 0;
		for (const char *p = *source; p < *source + strlen(*source) + 1; p++){
			switch (*p){
			case '\\':  // \"
				if (*(p + 1) == '"') {
					*d = *(p + 1);
					p++;
				}
				else {
					*d = *p;
				}
				d++;
				break;
			case '"':
				cnt++;
				if (cnt >= 2) {
					*d = '\0';
					p = *source + strlen(*source); // set p to end of string
				}
				break;
			default:
				*d = *p;
				d++;
				break;
			}
		}
		strcpy(*source, destination);
		DEL(destination);
	}
}

///////////////////////////////////////////////////////////////////////////////
// class INDEX
///////////////////////////////////////////////////////////////////////////////
INDEX::INDEX(unsigned index, double index_value, const char *index_str){
	name = index;
	value = index_value;
	str_value = new char[strlen(index_str) + 1];
	strcpy(str_value, index_str);
	this->next_node = NULL;
	SPEC::isprotected ? isprotected = true : isprotected = false;
}

INDEX::~INDEX(){
	DEL(str_value);
}

// This function sets the value of index
INDEX &INDEX::operator= (double index_value){
	if (!isprotected){
		if (int(name) >= 0)
			value = index_value;
	}
	else
		SPEC::error("SPEC: index \"%d\" is protected. Assignment not allowed\n", (int)name);
	return *this;
}

INDEX &INDEX::operator= (int index_value){
	return this->operator = ((double)index_value);
}

INDEX &INDEX::operator= (unsigned index_value){
	return this->operator = ((double)index_value);
}

INDEX &INDEX::operator= (INT64 index_value){
	return this->operator = ((double)index_value);
}

INDEX &INDEX::operator= (bool index_value){
	return this->operator = ((double)(index_value ? 1 : 0));
}

INDEX &INDEX::operator= (INDEX &i){
	return this->operator = ((double)i.value);
}

// This function returns the value of index 
INDEX::operator const double(){
	if (int(name) >= 0)
		return value;
	else
		return 0.0;
}

// This function returns the string of index
const char *INDEX::get_str() {
	return str_value;
}

void INDEX::protect(){
	isprotected = true;
}

INDEX &INDEX::unprotect(){
	isprotected = false;
	return *this;
}

///////////////////////////////////////////////////////////////////////////////
// class PARAMETER
///////////////////////////////////////////////////////////////////////////////
PARAMETER::PARAMETER(const char *param_name, double param_value, const char *param_str){
	name = new char[strlen(param_name) + 1];
	strcpy(name, param_name);
	next_node = NULL;
	index_root = NULL;
	current_index = NULL;
	value = param_value;
	str_value = new char[strlen(param_str) + 1];// char type
	string_value = param_str;//string type
	strcpy(str_value, param_str);
	add_index(_INTERNAL_INDEX, 0.0, "");
	num_index = 0;
	para_temp_value = 0;// add by hanson
	user_set_index = 0;// add by hanson
	user_set_index_check = true;// add by hanson

	SPEC::isprotected ? isprotected = true : isprotected = false;
}

PARAMETER::~PARAMETER(){
	INDEX *i = index_root;
	if (index_root){
		while (i->next_node)
			i = i->next_node;
		while (i != index_root){
			i = i->pre_node;
			DEL_OBJ(i->next_node);
		}
		DEL_OBJ(index_root);
		num_index = 0;
		para_temp_value = 0;// add by hanson
		user_set_index=0;// add by hanson
		 user_set_index_check=false;// add by hanson

	}
	DEL(name);
	DEL(str_value);
}

// This function sets the value of parameter
PARAMETER &PARAMETER::operator= (double param_value){
	if (!isprotected){
		if (!(strcmp(name, _INTERNAL_PARAMETER) == 0)){
			if (num_index == 0)
				value = param_value;
			else
				SPEC::error("SPEC: parameter \"%s\" has index defined\n", name);
		}
	}
	else
		SPEC::error("SPEC: parameter \"%s\" is protected. Assignment not allowed\n", name);
	return *this;
}

void PARAMETER::set_select_value(double temp_value)// add by  hanson
{
	para_temp_value = temp_value;
}

void PARAMETER::set_select_index(int temp_index) // add by hanson
{
	user_set_index= temp_index;
	user_set_index_check=true;
}

PARAMETER &PARAMETER::operator= (int param_value){
	return this->operator = ((double)param_value);
}

PARAMETER &PARAMETER::operator= (unsigned param_value){
	return this->operator = ((double)param_value);
}

PARAMETER &PARAMETER::operator= (INT64 param_value){
	return this->operator = ((double)param_value);
}

//PARAMETER &PARAMETER::operator= (string param_value){
//	string_value = param_value;
//	return this->operator = ((string)string_value);
//}


PARAMETER &PARAMETER::operator= (bool param_value){
	return this->operator = ((double)(param_value ? 1 : 0));
}

PARAMETER &PARAMETER::operator= (PARAMETER &p){
	return this->operator = ((double)p.value);
}




// pass index in []
INDEX &PARAMETER::operator[] (unsigned index){
	INDEX *i = NULL;
	if (index_root){
		i = find_index(index);
		if (!i)
		{
			SPEC::error("SPEC: index \"%d\" not existing\n", index);
			i = find_index(_INTERNAL_INDEX);
		}
	}
	else
	{
		assert(index_root != NULL);
	}
	return *i;
}

// This function returns the value of parameter
PARAMETER::operator const double(){
	if ((strcmp(name, _INTERNAL_PARAMETER) == 0))
		return 0.0;
	if (num_index == 0)
		return value;
	else {
		SPEC::error("SPEC: parameter \"%s\" has index defined\n", name);
		//return 0.0;
		if (user_set_index_check)// add by hanson
		{
			para_temp_value = operator[](user_set_index);// add by hanson
		}
		return para_temp_value; // add by hanson
	}
}


// This function returns the value of parameter
PARAMETER::operator string(){
	if ((strcmp(name, _INTERNAL_PARAMETER) == 0))
		return "";
	if (num_index == 0)
		return string_value;
	else {
		SPEC::error("SPEC: parameter \"%s\" has index defined\n", name);
		//return 0.0;
		if (user_set_index_check)// add by hanson
		{
			para_temp_value = operator[](user_set_index);// add by hanson
		}
		//return para_temp_value; // add by hanson
		return "";
	}
}




// This function returns the string of parameter
const char *PARAMETER::get_str() {
	return str_value;
}


string PARAMETER::get_param_name_in_spec()
{
	string aa = name;
	return  aa;
}

void PARAMETER::protect(){
	isprotected = true;
}

PARAMETER &PARAMETER::unprotect(){
	isprotected = false;
	return *this;
}

INDEX *PARAMETER::add_index(unsigned index, double index_value, const char* index_str){
	INDEX *i = index_root;
	INDEX *ii = NULL;
	if (index_root){
		if ((ii = find_index(index))){
			SPEC::error("SPEC: index \"%d\" already exists\n", index);
			return ii;
		}
		while (i->next_node)
			i = i->next_node;
		i->next_node = new INDEX(index, index_value, index_str);
		i->next_node->pre_node = i;
		i = i->next_node;
	}
	else {
		index_root = new INDEX(index, index_value, index_str);
		index_root->pre_node = NULL;
		i = index_root;
	}
	num_index++;
	return i;
}

INDEX *PARAMETER::find_index(unsigned index){
	INDEX *i = index_root;
	if (index >= 0){
		do{
			if (i->name == index){
				return i;
			}
			else {
				if (i->next_node)
					i = i->next_node;
			}
		} while (i->next_node);

		if (i->name == index){
			return i;
		}
		else {
			return (INDEX *)NULL;
		}
	}
	else
		return (INDEX *)NULL;
}

INDEX *PARAMETER::getNextIndex(){
	if (!current_index)
		index_root ? current_index = index_root->next_node : current_index = NULL; // start with root
	else {
		do {
			current_index = current_index->next_node;
			if (!current_index)
				break;
		} while (current_index->name == _INTERNAL_INDEX);
	}
	return current_index;
}

///////////////////////////////////////////////////////////////////////////////
// class DEVICE 
///////////////////////////////////////////////////////////////////////////////
DEVICE::DEVICE(const char *device_name){
	name = new char[strlen(device_name) + 1];
	strcpy(name, device_name);
	next_node = NULL;
	current_param = NULL;
	param_root = NULL;
	add_param(_INTERNAL_PARAMETER, 0.0, "");
	num_params = 0;
}

DEVICE::~DEVICE(){
	PARAMETER *p = param_root;
	if (param_root){
		while (p->next_node)
			p = p->next_node;
		while (p != param_root){
			p = p->pre_node;
			DEL_OBJ(p->next_node);
		}
		DEL_OBJ(param_root);
		num_params = 0;
	}
	DEL(name);
}

// pass parameter name in ()
PARAMETER &DEVICE::operator() (const char *param_name){
	PARAMETER *p = NULL;
	if (param_root){
		p = find_param(param_name);
		if (!p){
			SPEC::error("SPEC: parameter \"%s\" not existing\n", param_name);
			p = find_param(_INTERNAL_PARAMETER);
		}
	}
	else
		assert(param_root != NULL);
	return *p;
}

// This function adds and additonal parameter named 'param_name' to the device's
// parameter list at run time.
PARAMETER *DEVICE::add_param(const char *param_name, double param_value, const char *param_str){
	PARAMETER   *p = param_root;
	PARAMETER   *pp = NULL;
	if (param_root){
		if ((pp = find_param(param_name))){
			SPEC::error("SPEC: parameter \"%s\" already exists\n", param_name);
			return pp;
		}
		while (p->next_node)
			p = p->next_node;
		p->next_node = new PARAMETER(param_name, param_value, param_str);
		p->next_node->pre_node = p;
		p = p->next_node;
	}
	else {
		param_root = new PARAMETER(param_name, param_value, param_str);
		param_root->pre_node = NULL;
		p = param_root;
	}
	num_params++;
	return p;
}

PARAMETER *DEVICE::find_param(const char *param_name){
	PARAMETER *p = param_root;
	if (strcmp(param_name, "") != 0){
		do{
			if (strcmp(p->name, param_name) == 0){
				return p;
			}
			else {
				if (p->next_node)
					p = p->next_node;
			}
		} while (p->next_node);

		if (strcmp(p->name, param_name) == 0){
			return p;
		}
		else {
			return (PARAMETER *)NULL;
		}
	}
	else
		return (PARAMETER *)NULL;
}

PARAMETER *DEVICE::getNextParam(){
	if (!current_param)
		param_root ? current_param = param_root->next_node : current_param = NULL; // start with root
	else {
		do {
			current_param = current_param->next_node;
			if (!current_param)
				break;
		} while (strcmp(current_param->name, _INTERNAL_PARAMETER) == 0);
	}
	return current_param;
}

///////////////////////////////////////////////////////////////////////////////
// class SPEC
///////////////////////////////////////////////////////////////////////////////
SPEC::SPEC(bool unprotect_all){
	current_device = NULL;
	selected_device = NULL;
	strcpy_dynamic(&selected_device, _DEFAULT); // set default name
	device_root = NULL;
	num_devices = 0;
	SPEC::isprotected = !unprotect_all;
	//#ifdef WIN32
	//	//SPEC::temp_state_func=TI_ShellGetTempState;
	//	SPEC::error_func = etsfatalerror_wrapper;
	//#endif
	minimum_device_digits = 1;
}

void SPEC::initial_device_position()
{
	current_device = NULL;
	//selected_device = NULL;
	//strcpy_dynamic(&selected_device, _DEFAULT); // set default name
	//device_root = NULL;
}

SPEC::~SPEC(){
	if (device_root){
		DEVICE *d = device_root;
		while (d->next_node)
			d = d->next_node;
		while (d != device_root){
			d = d->pre_node;
			DEL_OBJ(d->next_node);
		}
		DEL_OBJ(device_root);
		num_devices = 0;
	}
	DEL(selected_device);
}

// pass parameter name in ()
PARAMETER &SPEC::operator() (const char *param_name){
	DEVICE    *d;
	PARAMETER *p;
	if (device_root)
	{
		d = find_device(selected_device); // look for selected device first
		if (!d)
		{                           // check if device exists
			d = find_device(_DEFAULT);    // fall back to DEFAULT
			if (!d){                       // add DEFAULT device to avoid program crash
				error("SPEC: device \"%s\" not existing\n", selected_device);
				d = add_device(_DEFAULT);
			}
		}
		p = d->find_param(param_name);    // look for parameter
		if (!p)
		{                           // check if parameter exists
			d = find_device(_DEFAULT);    // fall back to DEFAULT
			if (!d){                       // add DEFAULT device to avoid program crash
				error("SPEC: parameter \"%s\" not existing\n", param_name);
				d = add_device(_DEFAULT);
				p = d->find_param(_INTERNAL_PARAMETER);
			}
			else
			{
				p = d->find_param(param_name);
				if (!p){
					error("SPEC: parameter \"%s\" not existing\n", param_name);
					p = d->find_param(_INTERNAL_PARAMETER);
				}
			}
		}
	}
	else
	{
		d = add_device(_DEFAULT); // add object to avoid crash
		p = d->find_param(_INTERNAL_PARAMETER);
	}
	return *p;
}

// pass device name in []
DEVICE &SPEC::operator[] (const char *device_name){
	DEVICE *d;
	if (device_root){
		d = find_device(device_name);
		if (!d){
			error("SPEC: device \"%s\" not existing\n", device_name);
			d = find_device(_DEFAULT);
			if (!d)
				d = add_device(_DEFAULT);  // add DEFAULT to avoid program crash
		}
	}
	else
		d = add_device(_DEFAULT); // add object to avoid crash
	return *d;
}

DEVICE &SPEC::operator[] (string device_name_string){
	DEVICE *d;
	const char*device_name = device_name_string.c_str();
	if (device_root){
		d = find_device(device_name);
		if (!d){
			error("SPEC: device \"%s\" not existing\n", device_name);
			d = find_device(_DEFAULT);
			if (!d)
				d = add_device(_DEFAULT);  // add DEFAULT to avoid program crash
		}
	}
	else
		d = add_device(_DEFAULT); // add object to avoid crash
	return *d;
}



// This function initializes the SPEC class and loads the spec definition from
// the file passed by 'file_name'. Returns true if read was sucessful, false if
// 'file_name' is not existing.
bool SPEC::init(const char *file_name)
{
	init();
	manual_select_vin_index = 0;
	manual_select_temp_index = 0;
	DEVICE      *new_device = NULL;
	KEY         *key = NULL;
	SECTION     *section = NULL;
	READER      *reader = new READER("MULTILINE,CASE_SENSITIVE");
	PARSER      *parser = new PARSER;
	bool        default_set = false;
	char        *temp = NULL;
	const char  *str = NULL;
	int         temp_state = 0;

	//this->~SPEC(); // first clean up memory

	if (!reader->open(file_name)){

		string Pre_info = "查找不到";
		string Post_info = ", 确认文件名或者路径是否正确！";
		string filename_info = file_name;
		filename_info = Pre_info + filename_info + Post_info;
		file_name = filename_info.c_str();
		MessageBoxA(NULL, file_name, "诊断提示对话框", MB_YESNO);

		//error("SPEC: file \"%s\" not existing\n", file_name);
		DEL_OBJ(reader);
		return false;  // exit and return false 
	}

	// reader->dump("debug.reader");

	if (temp_state_func){
		temp_state = temp_state_func();
		if (temp_state < 0 || temp_state > 2){ // check if temp_state is in allowed range
			temp_state_func = NULL; // disable temperature state support
			temp_state = 0;
			SPEC::error("SPEC: Error: temperature state function must return 0 for \"amb\", 1 for \"hot\", 2 for \"cold\"\n");
		}
	}

	// loop through all sections
	while ((section = reader->getNextSection())){
		if (num_devices > 0 && find_device(section->getName())){
			error("SPEC: device [%s] already exists in %s\n", section->getName(), file_name);
		}
		else {
			new_device = add_device(section->getName());
			if (!default_set){
				strcpy_dynamic(&selected_device, new_device->name); // set default name
				default_set = true;
			}
			while ((key = section->getNextKey())){                 // loop through all keys
				PARAMETER* parameter = NULL;
				const char *err = NULL; bool temp_found = false;
				double value = 0;

				str = key->getString();
				strcpy_dynamic(&temp, str);

				if (temp && temp[0] == '"'){                     // check for strings
					clean(&temp); // strip off "
					new_device->add_param(key->getName(), 0.0, temp);
				}
				else if (strchr(temp, ':')){                    // check for lookup tables and temp state
					int index = -1; bool first = true;
					char *cindex = NULL; char *cvalue = NULL;
					parameter = new_device->add_param(key->getName(), 0.0, "");
					while (1){
						cindex = first ? strtok(temp, ",:") : strtok(NULL, ",:"); first = false;
						cvalue = strtok(NULL, ",:");
						if (cindex != NULL && cvalue != NULL){
							if (sscanf(cindex, "%d", &index) > 0){   // check if index is numeric
								if (cvalue[0] == '"'){           // check for strings
									clean(&cvalue); // strip off "
									parameter->add_index(index, 0.0, cvalue);
								}
								else {
									err = parser->parse(cvalue, &value, reader, section->getName(), _DEFAULT);
									if ((strcmp(err, "") == 0))
										parameter->add_index(index, value, "");
									else
										SPEC::error("SPEC: parameter \"%s\": index \"%d\": %s\n", key->getName(), index, err);
								}
							}
							else {                            // check for temperature state
								if (temp_state_func){
									if (_stricmp(cindex, temp_states[temp_state]) == 0){
										err = parser->parse(cvalue, &value, reader, section->getName(), _DEFAULT);
										if ((strcmp(err, "") == 0)){
											temp_found = true;
											parameter->value = value;
											// update string in reader with value for the selected temperature state. This
											// enables the parser to find the parameter as variable in another expression.
											key->setString(cvalue);
										}
										else
											SPEC::error("SPEC: parameter \"%s\": %s\n", key->getName(), err);
									}
								}
							}
						}
						else
							break;
					}
					if (!temp_state_func && parameter->num_index == 0)
						SPEC::error("SPEC: parameter \"%s\": temperature state unknown\n", parameter->name);
					else if (!temp_found && parameter->num_index == 0)
						SPEC::error("SPEC: parameter \"%s\": temperature state \"%s\" not found\n", \
						parameter->name, temp_states[temp_state]);
				}
				else { // ask parser
					err = parser->parse(temp, &value, reader, section->getName(), _DEFAULT);
					if ((strcmp(err, "") == 0))
						new_device->add_param(key->getName(), value, "");
					else
						SPEC::error("SPEC: parameter \"%s\": %s\n", key->getName(), err);
				}
				DEL(temp);
			}
		}
	}
	DEL_OBJ(parser);
	DEL_OBJ(reader);
	return true;
}



void SPEC::set_sel_vin_index(int set_val)
{
	manual_select_vin_index = set_val;
}

int SPEC::get_sel_vin_index()
{
	return manual_select_vin_index;
}

void SPEC::set_sel_temp_index(int set_val)
{
	manual_select_temp_index = set_val;
}

int SPEC::get_sel_temp_index()
{
	return manual_select_temp_index;
}
// This function adds and additonal device to the SPEC list at run time.
DEVICE *SPEC::add_device(const char *device_name){
	DEVICE    *d = device_root;
	DEVICE    *dd = NULL;
	if (device_root){
		if ((dd = find_device(device_name))){
			SPEC::error("SPEC: device \"%s\" already exists\n", device_name);
			return dd;
		}
		while (d->next_node)
			d = d->next_node;
		d->next_node = new DEVICE(device_name);
		d->next_node->pre_node = d;
		d = d->next_node;
	}
	else {
		device_root = new DEVICE(device_name);
		device_root->pre_node = NULL;
		d = device_root;
	}
	num_devices++;
	return d;
}

DEVICE *SPEC::find_device(const char *device_name){
	DEVICE *d = device_root;
	if (strcmp(device_name, "") != 0){
		do{
			if (strcmp(d->name, device_name) == 0){
				return d;
			}
			else {
				if (d->next_node)
					d = d->next_node;
			}
		} while (d->next_node);

		if (strcmp(d->name, device_name) == 0){
			return d;
		}
		else {
			return (DEVICE *)NULL;
		}
	}
	else
		return (DEVICE *)NULL;
}

DEVICE *SPEC::getNextDevice(){
	if (!current_device)
		device_root ? current_device = device_root : current_device = NULL; // start with root
	else {
		do {
			current_device = current_device->next_node;
			if (!current_device)
				break;
		} while (strcmp(current_device->name, _DEFAULT) == 0);
	}
	return current_device;
}

// This function selects the device name for which the specification values are
// valid. Returns true if device exists or false if device is not existing.
bool SPEC::select_device(const char *device_name){
	DEVICE *d;
	if (device_root){
		d = find_device(device_name);
		if (d){
			strcpy_dynamic(&selected_device, device_name);
			return true;
		}
	}
	error("SPEC: device \"%s\" not existing\n", device_name);
	return false;
}

// This function returns the currently selected device as STRING
const char *SPEC::get_device_str(){
	return selected_device;
}

// This function returns the currently selected device # as INTEGER.
// Optionally it can search for numbers with specified minimal count of digits
// Searches from the last character if min_digits is negative
// First call with min_digits specified sets this as default for next call without parameter
const int SPEC::get_device_num(int min_digits){
	int digit_count = 0;
	int len = strlen(selected_device);
	int shift;

	if (min_digits != 0)
		minimum_device_digits = min_digits;

	for (shift = (minimum_device_digits < 0 ? len - 1 : 0); shift >= 0 && shift < len; shift += (minimum_device_digits < 0 ? -1 : 1)){
		if (isdigit(*(selected_device + shift))){
			digit_count++;
		}
		else {
			if (digit_count >= abs(minimum_device_digits))
				break;
			digit_count = 0;
		}
	}

	if (digit_count >= abs(minimum_device_digits))
		return atoi(selected_device + shift + (minimum_device_digits < 0 ? 1 : -digit_count));

	error("SPEC::get_device_num(): selected device \"%s\" doesn't contain required %d digit(s)\n",
		selected_device, minimum_device_digits);
	return 0;
}

void SPEC::error(const char *msg, ...){
	char buff[4096];
	va_list marker;
	va_start(marker, msg);
	vsprintf(buff, msg, marker);
	va_end(marker);

	if (error_func)
		error_func(buff);
}

void SPEC::strcpy_dynamic(char **destination, const char *source){
	DEL(*destination);
	*destination = new char[strlen(source) + 1];
	strcpy(*destination, source);
}

bool SPEC::dump(const char *file_name){
	FILE *fp = NULL;
	char filepath[_MAX_PATH];   // defined in <stdlib.h>
	_getcwd(filepath, _MAX_PATH);
	strcat(filepath, "/");       // using '/' as directory separator for windows/unix portability
	strcat(filepath, file_name);
	if ((fp = fopen(filepath, "w")) == NULL)
		return false;

	INDEX *i = NULL;
	PARAMETER *p = NULL;
	DEVICE *d = NULL;

	while ((d = getNextDevice())){
		fprintf(fp, "[%s]\n", d->name);
		while ((p = d->getNextParam())){
			if (p->num_index > 0){
				fprintf(fp, "%s=\n", p->name);
				while ((i = p->getNextIndex())){
					if (strcmp(i->str_value, "") != 0)
						fprintf(fp, "    %d:\"%s\"\n", i->name, i->str_value);
					else
						fprintf(fp, "    %d:%.4f\n", i->name, i->value);
				}
			}
			else {
				if (strcmp(p->str_value, "") != 0)
					fprintf(fp, "%s=\"%s\"\n", p->name, p->str_value);
				else
					fprintf(fp, "%s=%.4f\n", p->name, p->value);
			}
		}
		fprintf(fp, "\n");
	}

	fclose(fp);
	return true;
}

void SPEC::register_temp_state_func(int(*func)(void)){
	temp_state_func = func;
}

void SPEC::register_error_func(void(*func)(const char *)){
	error_func = func;
}



/////////////////goto CMapMemFile///////////////////////
// read csv file, and put the cell data to map[row][column]
BOOL CMapMemFile::CsvReader(map<DWORD, map<DWORD, string>> &res_map){
	int flag = 0; // record the number of '"', if it is 2, it will changed to 0 automatically
	unsigned char* ptr_begin_of_word = p;

	DWORD row = 1;
	DWORD column = 0;

	//for(DWORD i = 0; i < 1024; ++i){	// for debug
	for (DWORD i = 0; i < GetSize(); ++i)
	{
		if (p[i] == '"')
		{
			++flag;
			if (flag == 1)
				ptr_begin_of_word = p + i + 1;
		}

		if (((flag == 0) || (flag == 2)) && ((p[i] == ',') || (p[i] == '\n'))) 
		{

			++column;

			if (i == 0)
			{
				res_map[row][column] = "";
			}
			else
			{
				// it seems before '\n', there is a special char, which like "Home" key, 
				// make the cursor jump to the first char of the row. 
				// so the end of the word turn to be p + i - 1
				if ((flag == 2) || (p[i] == '\n'))
				{
					string word(ptr_begin_of_word, p + i - 1);	// copy word from p to as string
					res_map[row][column] = word;
				}
				else{
					string word(ptr_begin_of_word, p + i);	// copy word from p to as string
					res_map[row][column] = word;
				}

			}

			ptr_begin_of_word = p + i + 1;

			if (p[i] == '\n')
			{
				++row;
				column = 0;
			}

			if (flag == 2)
				flag = 0;

		}
	}	// end of for

	ptr_begin_of_word = NULL;
	CloseMapFile();


	return TRUE;

}

/////////////////goto SPEC///////////////////////
string SPEC::int2str(DWORD n){
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


string SPEC::get_step_str(LPCTSTR funclabel, unsigned int step)
{
	if (trim_map.find(funclabel) != trim_map.end())
	{
		if (trim_map[funclabel].step_vec.size() > 0)
		{
			int pos = trim_map[funclabel].step_vec[0].find_last_of("_");
			if (pos > 1)
			{
				string param_str(trim_map[funclabel].step_vec[0], 0, pos);
				if (trim_map[funclabel].step_vec[0].find("Step") != string::npos)
				{
					param_str = param_str + "_Step" + int2str(step);
					if (find(trim_map[funclabel].step_vec.begin(), trim_map[funclabel].step_vec.end(), param_str) != trim_map[funclabel].step_vec.end())
						return param_str;
					else
						return "error";
				}
				else if (trim_map[funclabel].step_vec[0].find("step") != string::npos)
				{
					param_str = param_str + "_step" + int2str(step);
					if (find(trim_map[funclabel].step_vec.begin(), trim_map[funclabel].step_vec.end(), param_str) != trim_map[funclabel].step_vec.end())
						return param_str;
					else
						return "error";
				}
				else if (trim_map[funclabel].step_vec[0].find("STEP") != string::npos)
				{
					param_str = param_str + "_STEP" + int2str(step);
					if (find(trim_map[funclabel].step_vec.begin(), trim_map[funclabel].step_vec.end(), param_str) != trim_map[funclabel].step_vec.end())
						return param_str;
					else
						return "error";
				}
				else
					return "error";
				//if(step < trim_map[funclabel].step_vec.size())
				//	return trim_map[funclabel].step_vec[step];
				//else
				//	return "error";
			}
			else
				return "error";
		}
		else
			return "error";
	}
	else
		return "error";

}

string SPEC::get_pre_str(LPCTSTR funclabel){
	if (trim_map.find(funclabel) != trim_map.end()){
		if (trim_map[funclabel].str_pre != "")
			return trim_map[funclabel].str_pre;
		else
			return "error";
	}
	else
		return "error";
}

string SPEC::get_pre_bit_str(LPCTSTR funclabel){
	if (trim_map.find(funclabel) != trim_map.end()){
		if (trim_map[funclabel].str_pre_bit != "")
			return trim_map[funclabel].str_pre_bit;
		else
			return "error";
	}
	else
		return "error";
}

string SPEC::get_post_str(LPCTSTR funclabel){
	if (trim_map.find(funclabel) != trim_map.end()){
		if (trim_map[funclabel].str_post != "")
			return trim_map[funclabel].str_post;
		else
			return "error";
	}
	else
		return "error";
}

string SPEC::get_post_bit_str(LPCTSTR funclabel){
	if (trim_map.find(funclabel) != trim_map.end()){
		if (trim_map[funclabel].str_post_bit != "")
			return trim_map[funclabel].str_post_bit;
		else
			return "error";
	}
	else
		return "error";
}

string SPEC::get_post_rt_str(LPCTSTR funclabel){
	if (trim_map.find(funclabel) != trim_map.end()){
		if (trim_map[funclabel].str_post_rt != "")
			return trim_map[funclabel].str_post_rt;
		else
			return "error";
	}
	else
		return "error";
}


string SPEC::get_target_str(LPCTSTR funclabel){
	if (trim_map.find(funclabel) != trim_map.end()){
		if (trim_map[funclabel].str_target != "")
			return trim_map[funclabel].str_target;
		else
			return "error";
	}
	else
		return "error";
}

string SPEC::get_guessed_str(LPCTSTR funclabel){
	if (trim_map.find(funclabel) != trim_map.end()){
		if (trim_map[funclabel].str_guessed != "")
			return trim_map[funclabel].str_guessed;
		else
			return "error";
	}
	else
		return "error";
}

string SPEC::get_updated_str(LPCTSTR funclabel){
	if (trim_map.find(funclabel) != trim_map.end()){
		if (trim_map[funclabel].str_updated != "")
			return trim_map[funclabel].str_updated;
		else
			return "error";
	}
	else
		return "error";
}

double SPEC::get_low_limit(string param){
	string str;
	double result;

	if (lolim_map.find(param) != lolim_map.end()){
		str = lolim_map[param];
		result = atof(str.c_str());
	}
	else
		result = 999999;

	return result;
}

double SPEC::get_high_limit(string param){
	string str;
	double result;

	if (hilim_map.find(param) != hilim_map.end()){
		str = hilim_map[param];
		result = atof(str.c_str());
	}
	else
		result = 999999;

	return result;
}


string SPEC::get_unit(string param){

	if (unit_map.find(param) != unit_map.end()){
		return unit_map[param];
	}
	else
		return "none";
}

bool SPEC::init(){
	//map<DWORD, map<DWORD, string>> pgs_map;
	CMapMemFile imap_file;

	char pgsfullpath[300];
	GetPgsFullPath(pgsfullpath, 300);
	string file(pgsfullpath);

	if (!imap_file.create(file.c_str())){
		return false;
	}

	path = file;

	imap_file.CsvReader(pgs_map);
	imap_file.CloseMapFile();

	int func_flag = 0;
	string func_str;

	//DWORD start = 1;
	//DWORD stop = 1;

	for (DWORD row = 1; row < pgs_map.size(); ++row){
		if ((pgs_map[row][1].find("FUNCTION") != string::npos) && (func_flag == 0)){
			start = row;
			func_flag = 1;
		}
		if (pgs_map[row][1] == "[Station Setting Block]"){
			stop = row;
			break;
		}
	}

	if (stop <= start)
		return false;

	string temp_for_trim;
	for (DWORD row = start; row < stop; ++row)
	{
		if (pgs_map[row][1].find("FUNCTION") != string::npos)
		{
			string temp_str(pgs_map[row][1], 11, pgs_map[row][1].length() - 10);
			func_str = temp_str;
			func_index_map[row] = func_str;
		}
		else
		{
			string param_str(pgs_map[row][1], 4, pgs_map[row][1].length() - 4);
			param_vec.push_back(param_str);
			func_map[func_str] = param_str;
			lolim_map[param_str] = pgs_map[row][5];
			hilim_map[param_str] = pgs_map[row][6];
			unit_map[param_str] = pgs_map[row][8];

			temp_for_trim = func_str;
			transform(temp_for_trim.begin(), temp_for_trim.end(), temp_for_trim.begin(), ::tolower);
			if (temp_for_trim.find("trim") != string::npos)
			{
				temp_for_trim = pgs_map[row][1];
				transform(temp_for_trim.begin(), temp_for_trim.end(), temp_for_trim.begin(), ::tolower);
				if (temp_for_trim.find("step") != string::npos)
					trim_map[func_str].step_vec.push_back(param_str);
				if ((temp_for_trim.find("pre") != string::npos) && (temp_for_trim.find("value") != string::npos))
					trim_map[func_str].str_pre = param_str;
				if ((temp_for_trim.find("pre") != string::npos) && (temp_for_trim.find("bit") != string::npos))
					trim_map[func_str].str_pre_bit = param_str;
				if ((temp_for_trim.find("post") != string::npos) && (temp_for_trim.find("value") != string::npos))
					trim_map[func_str].str_post = param_str;
				if (temp_for_trim.find("post_rt") != string::npos) 
					trim_map[func_str].str_post_rt = param_str;
				if ((temp_for_trim.find("post") != string::npos) && (temp_for_trim.find("bit") != string::npos))
					trim_map[func_str].str_post_bit = param_str;
				if (temp_for_trim.find("target") != string::npos)
					trim_map[func_str].str_target = param_str;
				if (temp_for_trim.find("guessed") != string::npos)
					trim_map[func_str].str_guessed = param_str;
				if (temp_for_trim.find("updated") != string::npos)
					trim_map[func_str].str_updated = param_str;
			}
		}
	}


	return true;
}

void SPEC::get_all_function_name(vector<string>*func_name_sum, int *func_sum)
{
	size_t start_pos = 0;
	string a_func = "FUNCTION = ";
	string funcname;
	*func_sum = 0;
	int bb = 0;
	for (auto itr = func_index_map.begin(); itr != func_index_map.end(); itr++)
	{
		funcname = itr->second;
		func_name_sum->push_back(funcname);
		(*func_sum)++;
	}
}
void SPEC::get_funcname_vs_paracnt_matrix(string  funcname_in, int *total_para_cnt)
{
	string 	funcname;
	int start_no = -1;
	int  stop_no = -1;
	for (auto itr = func_index_map.begin(); itr != func_index_map.end(); itr++)
	{
		funcname = itr->second;

		if (start_no > -1 && stop_no == -1)
		{
			stop_no = itr->first;
		}
		if (funcname == funcname_in &&	start_no == -1 && stop_no == -1)
		{
			start_no = itr->first;
		}
	}
	 *total_para_cnt = stop_no - start_no - 1;
}

bool SPEC::clarify_os_fail_type(string  funcname_in)
{
	string 	funcname;
	int start_no = -1;
	int  stop_no = -1;
	int total_para_cnt = 0;
	for (auto itr = func_index_map.begin(); itr != func_index_map.end(); itr++)
	{
		funcname = itr->second;

		if (start_no > -1 && stop_no == -1)
		{
			stop_no = itr->first;
		}
		if (funcname == funcname_in &&	start_no == -1 && stop_no == -1)
		{
			start_no = itr->first;
		}
	}
	total_para_cnt = stop_no - start_no - 1;

	LPCTSTR fname = funcname_in.c_str();
	for (int i = 0; i < total_para_cnt; i++)
	{

		//get_high_limit(fname, i);
		//get_low_limit(fname, i);
	}




	return false;
}


double SPEC::get_high_limit(LPCTSTR funclabel, int fun_index)
{
	//if (AllocConsole())//(AttachConsole(ATTACH_PARENT_PROCESS))//
	//{
	//	COORD size = { 180, 180 };

	//	SetConsoleTitleA("AccoTEST Debug Window");
	//	freopen("conout$", "w+t", stdout);
	//	::DeleteMenu(GetSystemMenu(GetConsoleWindow(), FALSE), SC_CLOSE, MF_BYCOMMAND);
	//	delay_ms(2000);
	//}
	string function_name = funclabel;
	double Para_high_limit = 0;

	int bb = 0;
	//for (auto itr = func_index_map.find(function_name); itr != func_index_map.end(); itr++)
	//{
	//	cout << itr->first << '\t' << itr->second << '\n';
	//	bb = itr->second;
	//}
	for (auto itr = func_index_map.begin(); itr != func_index_map.end(); itr++)
	{
		//cout << itr->first << '\t' << itr->second << '\n';
		if (itr->second == function_name)
		{
			bb = itr->first;
		}
	}
	for (vector<string>::iterator it = param_vec.begin(); it != param_vec.end(); ++it)
	{
		string paraname = *it;
		string search_paraname = pgs_map[bb + fun_index][1];

		search_paraname.erase(std::remove(search_paraname.begin(), search_paraname.end(), ' '), search_paraname.end());// clear blank in array
		if (paraname == search_paraname)
		{
			try {
				Para_high_limit = std::stod(hilim_map[*it]);
				return std::stod(hilim_map[*it]);
			}
			catch (const std::invalid_argument& e) {
				std::cerr << "无效的输入字符串: " << e.what() << std::endl;
				return 0.0;
			}
			catch (const std::out_of_range& e) {
				std::cerr << "转换后的值超出范围: " << e.what() << std::endl;
				return 0.0;
			}
		}
	}

	return 0;
}

double SPEC::get_low_limit(LPCTSTR funclabel, int fun_index)
{
	//if (AllocConsole())//(AttachConsole(ATTACH_PARENT_PROCESS))//
	//{
	//	COORD size = { 180, 180 };

	//	SetConsoleTitleA("AccoTEST Debug Window");
	//	freopen("conout$", "w+t", stdout);
	//	::DeleteMenu(GetSystemMenu(GetConsoleWindow(), FALSE), SC_CLOSE, MF_BYCOMMAND);
	//	delay_ms(2000);
	//}
	string function_name = funclabel;
	double Para_low_limit = 0;

	int bb = 0;
	for (auto itr = func_index_map.begin(); itr != func_index_map.end(); itr++)
	{
		if (itr->second == function_name)
		{
			bb = itr->first;
		}
	}

	for (vector<string>::iterator it = param_vec.begin(); it != param_vec.end(); ++it)
	{
		string paraname = *it;
		string search_paraname = pgs_map[bb + fun_index][1];

		search_paraname.erase(std::remove(search_paraname.begin(), search_paraname.end(), ' '), search_paraname.end());// clear blank in array
		if (paraname == search_paraname)
		{
			try {
				Para_low_limit = std::stod(lolim_map[*it]);
				return std::stod(lolim_map[*it]);
			}
			catch (const std::invalid_argument& e) {
				std::cerr << "无效的输入字符串: " << e.what() << std::endl;
				return 0.0;
			}
			catch (const std::out_of_range& e) {
				std::cerr << "转换后的值超出范围: " << e.what() << std::endl;
				return 0.0;
			}
		}
	}

	return 0;
}

string SPEC::get_para_name(LPCTSTR funclabel, int fun_index)
{
	//if (AllocConsole())//(AttachConsole(ATTACH_PARENT_PROCESS))//
	//{
	//	COORD size = { 180, 180 };

	//	SetConsoleTitleA("AccoTEST Debug Window");
	//	freopen("conout$", "w+t", stdout);
	//	::DeleteMenu(GetSystemMenu(GetConsoleWindow(), FALSE), SC_CLOSE, MF_BYCOMMAND);
	//	delay_ms(2000);
	//}
	string function_name = funclabel;
	double Para_low_limit = 0;

	int bb = 0;
	for (auto itr = func_index_map.begin(); itr != func_index_map.end(); itr++)
	{
		//cout << itr->first << '\t' << itr->second << '\n';
		if (itr->second==function_name)
		{
			bb = itr->first;
		}	
	}

	string search_paraname = pgs_map[bb + fun_index][1];
	
	size_t start_pos = 0;
	string a_func = "FUNCTION = ";
	while ((start_pos = search_paraname.find(a_func, start_pos)) != std::string::npos) {
		search_paraname.erase(start_pos, a_func.length());
	}

	return search_paraname;
}

void SPEC::SetTestFuncDisableByFuncName(string func_name)
{
	int func_index = 0;
	int loop = 0;
	for (auto itr = func_index_map.begin(); itr != func_index_map.end(); itr++)
	{
		if (itr->second == func_name)
		{
			func_index=loop;
		}
		loop++;
	}

	STSUpdateFunTest(func_index, false);

}
void SPEC::SetTestFuncDisableByFuncIndex(int func_index)
{
	STSUpdateFunTest(func_index, false);
}
bool SPEC::print(void)
{

	//if (AllocConsole())//(AttachConsole(ATTACH_PARENT_PROCESS))//
	//{
	//	COORD size = { 180, 180 };

	//	SetConsoleTitleA("AccoTEST Debug Window");
	//	freopen("conout$", "w+t", stdout);
	//	::DeleteMenu(GetSystemMenu(GetConsoleWindow(), FALSE), SC_CLOSE, MF_BYCOMMAND);
	//	delay_ms(2000);
	//}

	for (vector<string>::iterator it = param_vec.begin(); it != param_vec.end(); ++it){
		cout << *it << "\t" << lolim_map[*it] << "\t" << hilim_map[*it] << "\t" << unit_map[*it] << endl;
	}

	return true;
}

/////////////////goto CFUNC///////////////////////
int CFunc::bstr2int(string str){
	// if not binary data 
	for (size_t i = 0; i < str.length(); ++i)
		if ((str[i] != '1') && (str[i] != '0'))
			return 0;

	int result = 0;
	int add = 1;
	for (int i = (int)str.length() - 1; i >= 0; --i){
		if (str[i] == '1'){
			result += add;
		}
		add *= 2;
	}

	return result;
}


/////////////////goto CBIT///////////////////////

bool CBIT::init(string file){
	map<DWORD, map<DWORD, string>> raw_map;
	CMapMemFile imap_file;

	if (!imap_file.create(file.c_str())){
		return false;
	}

	path = file;

	imap_file.CsvReader(raw_map);
	imap_file.CloseMapFile();

	DWORD start = 1;

	// access bank table
	for (DWORD row = 1; row < raw_map.size(); ++row){
		string bank_str(raw_map[row][1]);
		string param_name;
		if (((bank_str.find("Bank") != string::npos) || (bank_str.find("bank") != string::npos)) && (bank_str[bank_str.length() - 1] >= '0') && (bank_str[bank_str.length() - 1] <= '9')){
			for (DWORD col = 2; col <= 9; ++col){
				if (raw_map[row + 1][col] != "")
					param_name = raw_map[row + 1][col];

				string reg_addr(raw_map[row][col]);
				size_t pos1 = 0;
				size_t pos2 = 0;
				if ((reg_addr.find("<") != string::npos) && (reg_addr.find(">") != string::npos)){
					pos1 = reg_addr.find("<");
					pos2 = reg_addr.find(">");
					if (pos2 - pos1 > 1){
						string reg_no(reg_addr, pos1 + 1, pos2 - pos1 - 1);
						reg_addr = reg_no;
					}
					else
						return false;
				}
				else
					return false;

				string param_bit(raw_map[row + 2][col]);

				addr_map[param_name][atoi(param_bit.c_str())] = atoi(reg_addr.c_str());
			}

			start = row + 2;
		}
	}

	// access trim step table
	CFunc func;
	for (DWORD row = start; row < raw_map.size(); ++row){
		for (DWORD col = 1; col < raw_map[row].size(); ++col){
			if ((raw_map[row][col].find("EE") != string::npos) && (raw_map[row][col].find("<") != string::npos)){
				string param_str;
				string default_str;
				string target_str;
				string unit_str;
				string step_str;
				string pcnt_str;
				string val_str;

				param_str = raw_map[row - 2][col];
				default_str = raw_map[row - 2][col + 1];
				target_str = raw_map[row - 2][col + 2];
				unit_str = raw_map[row][col + 2];

				target_map[param_str] = target_str.c_str();

				for (DWORD i = row + 1; i < raw_map.size(); ++i){
					if (raw_map[i][col] == "")
						break;
					step_str = raw_map[i][col];
					pcnt_str = raw_map[i][col + 1];
					val_str = raw_map[i][col + 2];
					int step = func.bstr2int(step_str);
					double pcnt = atof(pcnt_str.c_str());
					double val = atof(val_str.c_str());
					step_map[param_str][step] = val;
					step_pcnt_map[param_str][step] = pcnt;
					default_map[param_str] = func.bstr2int(default_str);
				}
			}
		}
	}


	return true;
}

bool CBIT::print(void){
	//// monitor addr map
	//for(map<string, map<int, int>>::iterator it = addr_map.begin(); it != addr_map.end(); ++it){
	//	for(map<int, int>::iterator it_addr = it->second.begin(); it_addr != it->second.end(); ++it_addr){
	//		cout << it->first << "\t" << it_addr->first << "\t" << it_addr->second << endl;
	//	}
	//}

	//// monitor target map
	//for(map<string, string>::iterator it = target_map.begin(); it != target_map.end(); ++it)
	//	cout << it->first << "\t" << it->second << endl;

	//// monitor default map
	//for(map<string, int>::iterator it = default_map.begin(); it != default_map.end(); ++it)
	//	cout << it->first << "\t" << it->second << endl;

	// monitor step map
	for (map<string, map<int, double>>::iterator it = step_map.begin(); it != step_map.end(); ++it){
		for (map<int, double>::iterator it_step = it->second.begin(); it_step != it->second.end(); ++it_step)
			cout << it->first << "\t" << it_step->first << "\t" << it_step->second << endl;
	}

	// monitor step percnet map
	//for(map<string, map<int, double>>::iterator it = step_pcnt_map.begin(); it != step_pcnt_map.end(); ++it){
	//	for(map<int, double>::iterator it_step = it->second.begin(); it_step != it->second.end(); ++it_step)
	//		cout << it->first << "\t" << it_step->first << "\t" << it_step->second << endl;
	//}

	return true;
}