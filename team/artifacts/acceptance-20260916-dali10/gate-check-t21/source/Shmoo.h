//#pragma once
//#include <map>
//#include <vector>
//#include <string>
//#include <Windows.h>
//#include <iostream>
//using namespace std;
//
//#define     PI 3.1415926
//
//struct shmoo_data
//{
//	double x_para;
//	double y_para;
//	string paraname_x;
//	string paraname_y;
//};
//
//class SHMOO
//{
//public:
//		void showShmooplot();
//		void select_shmoo_parameter(SPEC spec);
//		void shmoo_plot(CParam *parameter_sel, double x_asix, double y_axis);
//		bool get_shmoo_results();
//		void shmoo_eot();
//		void shmoo_update_results(int xin, int yin, bool *results);
//		void initial_shmoomap();
//		void shmoo_plot();
//		void DrawArrow(int startX, int startY, int endX, int endY, int arrowSize);
//		int coor_transform(int y_axis);
//		LPCTSTR string_trans_lpctstr(string input_str);
//		void set_loop_serial(int loopx, int loopy);
//		void sot();
//		void select_shmoo_x_y_param(SPEC spec);
//		string convertToString(double value, int precision);
//	private:
//	
//		short shmoo_results[SITE_NUM];
//		map<int, pair<int, short>> shmoomap[SITE_NUM];
//		int Base_x[SITE_NUM];
//		int Base_y[SITE_NUM];
//		int loopx;
//		int loopy;
//		int loop_total_count;
//		shmoo_data shm_data[20];
//};