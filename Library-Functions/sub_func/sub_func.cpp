/*****************************************************************************
*                                                                            *
*       Source title:   sub_func.cpp                                         *
*                       (Reusable sub-functions for all NU test projects)    *
*         Written by:   NU TE                                                *
*        Description:   Implementation of Sub_Func. Copy alongside           *
*                       sub_func.h into each project's VS project.           *
*                                                                            *
*****************************************************************************/

#include "stdafx.h"
#include "sub_func.h"

// ==================== 上电 / 下电 ====================

BOOL Sub_Func::power_on(short site_num)
{
	// TODO: 继电器/源表初始化 + 按 PIN 类型两段式上电
	//   power PIN -> 100MA -> 500us -> 测量量程
	//   digital PIN -> 10MA -> 500us -> 测量量程
	//   ATEST(VDM/NTC/AMON) -> 直接测量量程，无两段式
	return TRUE;
}

BOOL Sub_Func::power_off(short site_num)
{
	// TODO: 三步下电 + RELAY_OFF 统一量程
	return TRUE;
}

// ==================== 测量 ====================

BOOL Sub_Func::measure_vi(ACM200 res, ACM200_VRNG v_range, ACM200_IRNG i_range,
                          double *meas_v, double *meas_i)
{
	// TODO: 单点 V/I 实测（MVRET + MIRET 双实测，电阻 = 实测 V / 实测 I）
	return TRUE;
}

// ==================== 寄存器配置 ====================

BOOL Sub_Func::config_register(short site_num, const char *label, int value)
{
	// TODO: 写寄存器（重新上电后配置前须先 entertestmode()）
	return TRUE;
}

// ==================== 常量 / 量程决策 ====================

double Sub_Func::pick_vrange(double set_v)
{
	// TODO: 量程 >= 2 x 设定值
	return set_v;
}

double Sub_Func::pick_irange(double set_i)
{
	// TODO: 量程 >= 2 x 设定值
	return set_i;
}
