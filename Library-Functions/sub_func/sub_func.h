/*****************************************************************************
*                                                                            *
*       Source title:   sub_func.h                                           *
*                       (Reusable sub-functions for all NU test projects)    *
*         Written by:   NU TE                                                *
*        Description:   Generic helpers (power on/off / measure / register   *
*                       config / constants). Copy sub_func.h / sub_func.cpp  *
*                       into each project's VS project, alongside            *
*                       Test_Method.h/.cpp and treg.h/.cpp.                  *
*                                                                            *
*****************************************************************************/

#pragma once
#include "stdafx.h"

// =====================================================================
// 通用子函数库 (Sub_Func)
// 与 test_method / treg 平级的第 3 个Library-Functions源，存「我们自己的其他子函数」。
// 使用方式：把 sub_func.h / sub_func.cpp 复制到每个项目的 VS 工程文件。
// =====================================================================
class Sub_Func {
public:
	Sub_Func() {}
	~Sub_Func() {}

	// ---- 上电 / 下电 ----
	BOOL power_on(short site_num);     // 上电：继电器/源表初始化 + 按 PIN 类型两段式 ramp
	BOOL power_off(short site_num);    // 下电：三步下电 + RELAY_OFF 统一量程

	// ---- 测量 ----
	// 单点 V/I 实测（电阻 = 实测 V / 实测 I，禁用理论设定值）
	BOOL measure_vi(ACM200 res, ACM200_VRNG v_range, ACM200_IRNG i_range,
	                double *meas_v, double *meas_i);

	// ---- 寄存器配置 ----
	// 写 trim/test 寄存器（重新上电后配置前须先 entertestmode()）
	BOOL config_register(short site_num, const char *label, int value);

	// ---- 常量 / 量程决策 ----
	double pick_vrange(double set_v);  // 量程 >= 2 x 设定值
	double pick_irange(double set_i);
};
