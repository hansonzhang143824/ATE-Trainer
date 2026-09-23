////////
//#include <windows.h>
#include "stdafx.h"
//#include "inireader.h"
//#include "spec.h"
//#include "Shmoo.h"
//#include <graphics.h>		// 引用 EasyX 绘图库头文件
//#include<graphics.h>//图形库文件
//#include<stdio.h>
//#include <time.h>//时间
//#include<stdlib.h>
//#include<mmsystem.h>
//#pragma comment (lib,"winmm.lib")
//#include <easyx.h>
//#include <conio.h>
//#include <iostream>
//#include <sstream>
//#include <iomanip>
//
//void SHMOO::showShmooplot()
//{
//	initgraph(1440, 1440);	// 创建绘图窗口，分辨率 640x480
//
//	initgraph(1024, 1024);//
//	setbkcolor(WHITE);
//	cleardevice();
//
//	setlinecolor(BLACK);//颜色
//	setlinestyle(PS_SOLID, 10);//这个函数用于设置当前设备画线样式，为线形为实线。宽度或者平滑度为10
//	Sleep(500);
//
//	setfillcolor(RGB(50, 130, 246));
//	fillellipse(110, 95, 970, 910);// 这个函数用于画有边框的填充椭圆。
//	Sleep(500);
//	setfillcolor(WHITE);
//	fillellipse(180, 230, 900, 910); //这个函数用于画有边框的填充椭圆。
//	Sleep(500);
//
//	fillellipse(400, 170, 530, 370);//眼睛
//	fillellipse(530, 170, 660, 370);
//	Sleep(500);
//	setfillcolor(BLACK);
//	solidcircle(480, 300, 25);//这个函数用于画无边框的填充圆。
//	solidcircle(576, 300, 25);
//	Sleep(500);
//
//	setfillcolor(WHITE);
//	solidcircle(480, 300, 10);//这个函数用于画无边框的填充圆。
//	solidcircle(576, 300, 10);
//	Sleep(500);
//
//	setfillcolor(BLACK);
//	solidcircle(530, 380, 35);//鼻子
//	Sleep(500);
//
//	setfillcolor(RED);
//	solidcircle(530, 380, 27);//鼻子里面的红色的
//	Sleep(500);
//
//	line(530, 411, 530, 710);//鼻子下面线段
//	Sleep(500);
//
//	arc(300, 430, 770, 710, PI, PI * 2);//嘴巴
//	// rectangle(300, 430, 770, 710);//矩形
//	Sleep(500);
//
//	line(70, 365, 245, 450);//胡子
//	Sleep(500);
//	line(73, 460, 245, 500);
//	Sleep(500);
//	line(73, 570, 245, 550);
//	Sleep(500);
//
//	line(1000, 355, 830, 440);
//	Sleep(500);
//	line(1010, 460, 840, 500);
//	Sleep(500);
//	line(1010, 580, 840, 550);
//	Sleep(5000);
//
//	//_getch();				// 按任意键继续
//	closegraph();			// 关闭绘图窗口
//}
//
//void SHMOO::select_shmoo_parameter(SPEC spec)
//{
//	vector<string> sts_all_func_name;
//	int total_func_cnout = 0;
//	spec.get_all_function_name(&sts_all_func_name, &total_func_cnout);
//
//	char *func_name_in_char = new char[10000];
//	string temp_str = "";
//	for (int i = 0;i< total_func_cnout; i++)
//	{
//		
//		temp_str = temp_str + sts_all_func_name[i];
//		if (i == total_func_cnout-1)
//		{
//		}
//		else
//		{
//			temp_str = temp_str+',';
//		}
//	}
//
//	std::strcpy(func_name_in_char, temp_str.c_str()); // Copy the string
//	STSSetInitSelectDialog("Parameter Select", total_func_cnout, 0, func_name_in_char);
//	delay_ms(1);
//
//
//}
//
//void SHMOO::shmoo_eot()
//{
//
//	FOR_EACH_VALID_SITE(site)
//	{
//		if (STSGetCurrentDutSwBin(site) == 1)
//		{
//			shmoo_results[site] = 1;
//		}
//		else
//		{
//			shmoo_results[site] = 2;
//		}
//	}
//
//
//	for (int site = 0; site < 8; site++)
//	{
//		shmoomap[site][loopx]=make_pair(loopy, shmoo_results[site]);
//	}
//
//	for (int site = 0; site< 8; site++)
//	{
//		for (int xin = 0; xin < 20; xin++)
//		{
//			for (int yin = 0; yin < 20; yin++)
//			{
//				if (shmoomap[site][xin].first == yin)	
//				{ 
//					if (shmoomap[site][xin].second == 1)
//					{
//						setfillcolor(GREEN);
//						fillrectangle(Base_x[site] + 1 + xin * 20, coor_transform(Base_y[site] + 19 + yin * 20), Base_x[site] + 19 + 20 * xin, coor_transform(Base_y[site] + 1 + yin * 20));
//					}
//					else if (shmoomap[site][xin].second ==2)
//					{
//						setfillcolor(RED);
//						fillrectangle(Base_x[site] + 1 + xin * 20, coor_transform(Base_y[site] + 19 + yin * 20), Base_x[site] + 19 + 20 * xin, coor_transform(Base_y[site] + 1 + yin * 20));
//					}
//					else
//					{
//
//					}
//				}
//
//			}
//		}
//	}
//}
//
//void SHMOO::shmoo_update_results(int xin, int yin, bool *results)
//{
//	for (int site = 0; site < SITE_NUM; site++)
//	{
//		shmoomap[site][xin] = make_pair(yin, results[site]);
//	}
//}
//
//void SHMOO::shmoo_plot()
//{
//
//	initgraph(1960, 1024);//
//
//	HWND hnd = GetHWnd();
//	SetWindowText(hnd, "SHMOO PLOT");
//
//	string temp;
//	string function_name_by_site = "";
//	for (int site = 0; site < 8; site++)
//	{
//		// 画坐标轴
//		line(Base_x[site] - 10, coor_transform(Base_y[site] - 10), Base_x[site] + 400, coor_transform(Base_y[site] - 10)); // x轴
//		line(Base_x[site] - 10, coor_transform(Base_y[site] - 10), Base_x[site] - 10, coor_transform(Base_y[site]+ 420));  // y轴
//		LPCTSTR Axis_Xname = shm_data[0].paraname_x.c_str();
//		settextstyle(11, 7, Axis_Xname, 0, 0, 0, false, false, false);
//		outtextxy(Base_x[site] + 400, coor_transform(Base_y[site] - 10), Axis_Xname);
//		for (int xin = 0; xin < 20; xin++)
//		{
//			temp = convertToString(shm_data[xin].x_para, 1);
//			LPCTSTR Axis_Xvalue = temp.c_str();
//			line(Base_x[site] +10+ xin * 20, coor_transform(Base_y[site] - 10), Base_x[site] +10 + 20 * xin, coor_transform(Base_y[site] - 5));
//
//			settextstyle(11, 7, Axis_Xvalue, 900, 900, 0, false, false, false);
//			outtextxy(Base_x[site] + 5 + xin * 20, coor_transform(Base_y[site] - 40), Axis_Xvalue);
//			for (int yin = 0; yin < 20; yin++)
//			{
//				setfillcolor(WHITE);
//				fillrectangle(Base_x[site] + 1 + xin * 20, coor_transform(Base_y[site] + 19 + yin * 20), Base_x[site] + 19 + 20 * xin, coor_transform(Base_y[site] + 1 + yin * 20));
//			}
//		}
//
//		LPCTSTR Axis_Yname = shm_data[0].paraname_y.c_str();
//		settextstyle(11, 7, Axis_Yname, 0, 0, 0, false, false, false);
//		outtextxy(Base_x[site]-10 , coor_transform(Base_y[site] +420), Axis_Yname);
//
//		function_name_by_site = convertToString((double)site+1,0);
//		function_name_by_site = "SHMOO PLOT ON  SITE" + function_name_by_site;
//		LPCTSTR function_name = function_name_by_site.c_str();
//		settextstyle(14,8, Axis_Yname, 0, 0, 0, false, false, false);
//		outtextxy(Base_x[site] + 100, coor_transform(Base_y[site] + 420), function_name);
//		for (int yin = 0; yin < 20; yin++)
//		{
//			temp = convertToString(shm_data[yin].y_para, 1);
//			LPCTSTR Axis_Yvalue=temp.c_str();
//			line(Base_x[site] - 10, coor_transform(Base_y[site]+10  + yin * 20), Base_x[site] -5, coor_transform(Base_y[site]  +10+ yin * 20));
//			settextstyle(11, 7, Axis_Yvalue, 0, 0, 0, false, false, false);
//			outtextxy(Base_x[site] - 40, coor_transform(Base_y[site] + yin * 20 + 15), Axis_Yvalue);
//		}
//
//
//	}
//
//
//
//	_getch();				// 按任意键继续
////	closegraph();			// 关闭绘图窗口
//
//}
//
//
//void SHMOO::DrawArrow(int startX, int startY, int endX, int endY, int arrowSize) {
//	// 画线
//	//line(startX, startY, endX, endY);
//
//	//// 计算箭头的方向向量
//	//int dx = endX - startX;
//	//int dy = endY - startY;
//
//	//// 标准化方向向量
//	//double norm = sqrt(dx * dx + dy * dy);
//	//dx /= norm;
//	//dy /= norm;
//
//	//// 计算箭头顶点坐标
//	//int arrowTopX = endX - dx * arrowSize + dy * arrowSize / 2;
//	//int arrowTopY = endY - dy * arrowSize - dx * arrowSize / 2;
//
//	//// 画箭头的两个边
//	//line(endX, endY, arrowTopX, arrowTopY);
//	//line(endX, endY, arrowTopX + 2 * dx * arrowSize / 2, arrowTopY + 2 * dy * arrowSize / 2);
//}
//
//
//int SHMOO::coor_transform(int y_axis)
//{
//	y_axis = 1024 - y_axis;
//	return y_axis;
//}
//
//LPCTSTR SHMOO::string_trans_lpctstr(string input_str)
//{
//	LPCTSTR lpctstr_data = input_str.c_str();
//	return lpctstr_data;
//}
//
//void  SHMOO::set_loop_serial(int loopx_in, int loopy_in)
//{
//	loopx = loopx_in;
//	loopy = loopy_in;
//}
//void  SHMOO::sot()
//{
//	int x_lp;
//	int y_lp;
//	
//	x_lp = loop_total_count / 20;
//	y_lp = loop_total_count % 20;
//	set_loop_serial(x_lp, y_lp);
//	loop_total_count++;
//}
//
//void SHMOO::initial_shmoomap()
//{
//	loop_total_count = 0;
//	loopx = 0;
//	loopy = 0;
//	Base_x[0] = 50;
//	Base_y[0] = 580;
//
//	Base_x[1] = 520;
//	Base_y[1] = 580;
//
//	Base_x[2] = 990;
//	Base_y[2] = 580;
//
//	Base_x[3] = 1450;
//	Base_y[3] = 580;
//
//
//	Base_x[4] = 50;
//	Base_y[4] = 100;
//
//	Base_x[5] = 520;
//	Base_y[5] = 100;
//
//	Base_x[6] = 990;
//	Base_y[6] = 100;
//
//	Base_x[7] = 1450;
//	Base_y[7] = 100;
//
//	for (int site = 0; site < SITE_NUM; site++)
//	{
//		for (int i = 0; i <20 ; i++)
//		{
//			for (int j = 0; j<20 ; j++)
//			{
//				shmoomap[site][i] = make_pair(j,3);
//			}
//		}
//	}
//
//	for (int i = 0; i < 20; i++)
//	{
//		shm_data[i].x_para = 3+0.1*i;
//		shm_data[i].y_para = 5+0.2*i;
//		shm_data[i].paraname_x = "VBAT";
//		shm_data[i].paraname_y = "VBUS";
//	}
//}
//
//string SHMOO::convertToString(double value, int precision)
//{
//	std::ostringstream streamObj;
//	streamObj << std::fixed << std::setprecision(precision) << value;
//	return streamObj.str();
//}
//
//
//
//void SHMOO::select_shmoo_x_y_param(SPEC spec)
//{
//	
//}