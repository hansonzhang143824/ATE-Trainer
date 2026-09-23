// stdafx.cpp : source file that includes just the standard includes
//	DUT.pch will be the pre-compiled header
//	stdafx.obj will contain the pre-compiled type information

#include "stdafx.h"
GLOBAL int g_x_coords[SITE_NUM] = { -9999 }, g_y_coords[SITE_NUM] = { -9999 };
GLOBAL char waferid[64];
/*
Site mapping "+" => skip die
y -------------->
x	1 ++  2 ++  3 ++ 4
|	+
|	+
|	5 ++  6 ++  7 ++ 8
|	+
|	+
|	9 ++  10 ++ 11++ 12
|	+
|	+
|	13 ++ 14 ++ 15 ++ 16
V

*/

GLOBAL void G_GetXYCoordinate()
{
	StsGetSingleDieCorXY(0, g_x_coords[0], g_y_coords[0]);
	StsGetWaferID(waferid, 63);

	g_x_coords[0] = g_x_coords[0];		//site1
	g_y_coords[0] = g_y_coords[0];
	g_x_coords[1] = g_x_coords[0] + 2;	//site2
	g_y_coords[1] = g_y_coords[0];
	g_x_coords[2] = g_x_coords[0] + 4;
	g_y_coords[2] = g_y_coords[0];
	g_x_coords[3] = g_x_coords[0] + 6;
	g_y_coords[3] = g_y_coords[0];

	g_x_coords[4] = g_x_coords[0];
	g_y_coords[4] = g_y_coords[0] + 2;
	g_x_coords[5] = g_x_coords[0] + 2;
	g_y_coords[5] = g_y_coords[0] + 2;
	g_x_coords[6] = g_x_coords[0] + 4;
	g_y_coords[6] = g_y_coords[0] + 2;
	g_x_coords[7] = g_x_coords[0] + 6;
	g_y_coords[7] = g_y_coords[0] + 2;

	g_x_coords[8] = g_x_coords[0];
	g_y_coords[8] = g_y_coords[0] + 4;
	g_x_coords[9] = g_x_coords[0] + 2;
	g_y_coords[9] = g_y_coords[0] + 4;
	g_x_coords[10] = g_x_coords[0] + 4;
	g_y_coords[10] = g_y_coords[0] + 4;
	g_x_coords[11] = g_x_coords[0] + 6;
	g_y_coords[11] = g_y_coords[0] + 4;

	g_x_coords[12] = g_x_coords[0];
	g_y_coords[12] = g_y_coords[0] + 6;
	g_x_coords[13] = g_x_coords[0] + 2;
	g_y_coords[13] = g_y_coords[0] + 6;
	g_x_coords[14] = g_x_coords[0] + 4;
	g_y_coords[14] = g_y_coords[0] + 6;
	g_x_coords[15] = g_x_coords[0] + 6;
	g_y_coords[15] = g_y_coords[0] + 6;

	//for (int site = 0; site<SITE_NUM; site++)
	//{
	//	StsSetDieCorXY(site, g_x_coords[site], g_y_coords[site]);
	//}
}
// TODO: reference any additional headers you need in STDAFX.H
// and not in this file
//智能GROUP对应关系如下
//|   7  |  6  |   5  |   4  |   3  |  2  |   1  |   0  |
//| 16-0 |17-0 | 15-0 | 18-0 | 2-0  | 31-0| 1-0  | 32-0 |--fpvi0
//| 16-1 |17-1 | 15-1 | 18-1 | 2-1  | 31-1| 1-1  | 32-1 |--fpvi1

int offfpvi = 0;
int onfpvi = 0;
int keepon_fpvi = 0;
DWORD g_last_valid_fpvi = 0;