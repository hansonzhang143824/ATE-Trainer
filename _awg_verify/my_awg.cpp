// my_awg.cpp — 重写的 AWG 测试函数（电压斜坡 → 电流捕获）单文件版
// 场景：VIN 输入引脚电压斜坡，捕获 VDD 供电电流（cap 源保持 3.3V），
//       触发电流 1mA，得输入电压阈值 rise/fall，算迟滞（mV）。
// 用 rampv_capi(ACM200 ramp, ACM200 cap) 重载 —— 与黄金案例的
// rampv_capv(ACM200, FOVIe) 不同，验证库的另一个 ramp 捕获路径。
//
// 说明：下方 mock 声明里的 rampv_capi / rampv_capv 签名是程序化从真实
//       Library-Functions\Test_Method\Test_Method.h 抽取的（非手抄）。
//       因 .h 在磁盘上是 DLP 密文、g++ 读不到明文，故内联到此 .cpp 里
//       做 -fsyntax-only 语义校验（调用解析 + 参数类型/个数/返回类型）。

typedef int BOOL;
#define TRUE 1
#define FALSE 0
#define SITE_NUM 12

#define DUT_API
#define LPCTSTR const char*
#define FV 0
#define FI 1

enum ACM200_VRNG { ACM200_10V = 0, ACM200_20V = 1 };
enum ACM200_IRNG { ACM200_10MA = 0, ACM200_100MA = 1 };
enum FOVIe_VRNG { FOVIe_10V = 0 };
enum FOVIe_IRNG { FOVIe_100UA = 0, FOVIe_10MA = 1 };
enum TRIG_MODE { TRIG_RISING = 0, TRIG_FALLING = 1 };
enum RELAY { ACM200_RELAY_OFF = 0, ACM200_RELAY_ON = 1, FOVIe_RELAY_OFF = 0 };

#define K_VDD_Cap 1001
#define K_VIN_ACM 1002

class ACM200 {
public:
    void Set(int mode, double value, int vrange, int irange, int relay);
};
class FOVIe {
public:
    void Set(int mode, double value, int vrange, int irange, int relay);
};
ACM200 VDD_ACM;
ACM200 VIN_ACM;

class CParam {
public:
    void SetTestResult(int site, int index, double value);
};
CParam* StsGetParam(int funcindex, const char* name);

class Cbite {
public:
    void SetOn(int first, ...);
};
Cbite cbite;

// ===== 测试方法库（真实签名，程序化抽取自 Test_Method.h） =====
class Test_Method {
public:
    BOOL rampv_capi(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, ACM200 cap_res, ACM200_VRNG cap_vrange, ACM200_IRNG cap_irange, double cap_fv_value, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
    BOOL rampv_capv(ACM200 ramp_res, ACM200_VRNG ramp_vrange, ACM200_IRNG ramp_irange, FOVIe cap_res, FOVIe_VRNG cap_vrange, FOVIe_IRNG cap_irange, double start_point, double stop_point, double step, int interval, double trig_level, TRIG_MODE trig_mode, double *result);
};
Test_Method test_method;

void delay_ms(int);
void entertestmode();

#define FOR_EACH_VALID_SITE(site) for (int site = 0; site < SITE_NUM; site++)

// ===================== 重写的 AWG 函数 =====================
DUT_API int VIN_VTH_ILEAK(short funcindex, LPCTSTR funclabel)
{
    CParam *VIN_VTH_Rise = StsGetParam(funcindex, "VIN_VTH_Rise");
    CParam *VIN_VTH_Fall = StsGetParam(funcindex, "VIN_VTH_Fall");
    CParam *VIN_VTH_Hys  = StsGetParam(funcindex, "VIN_VTH_Hys");

    double vin_vth_rise[SITE_NUM] = { 0 };
    double vin_vth_fall[SITE_NUM] = { 0 };
    double vin_vth_hys[SITE_NUM]  = { 0 };

    // 上电：VDD 供 DUT（cap 源），VIN 斜坡（ramp 源）
    cbite.SetOn(K_VDD_Cap, K_VIN_ACM, -1);
    delay_ms(3);
    VDD_ACM.Set(FV, 3.3, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);
    VIN_ACM.Set(FV, 0.0, ACM200_10V, ACM200_10MA, ACM200_RELAY_ON);
    entertestmode();
    delay_ms(1);

    // 电压斜坡 VIN 1.0V→3.6V（升），捕获 VDD 电流 1mA 触发点电压
    test_method.rampv_capi(VIN_ACM, ACM200_10V, ACM200_10MA,
                           VDD_ACM, ACM200_10V, ACM200_100MA,
                           3.3, 1.0, 3.6, 200, 10, 1e-3, TRIG_RISING, vin_vth_rise);
    // 电压斜坡 VIN 3.4V→0.8V（降），捕获 VDD 电流 1mA 触发点电压
    test_method.rampv_capi(VIN_ACM, ACM200_10V, ACM200_10MA,
                           VDD_ACM, ACM200_10V, ACM200_100MA,
                           3.3, 3.4, 0.8, 200, 10, 1e-3, TRIG_FALLING, vin_vth_fall);

    // 下电
    VIN_ACM.Set(FV, 0.0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);
    VDD_ACM.Set(FV, 0.0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);

    FOR_EACH_VALID_SITE(site)
    {
        vin_vth_hys[site] = (vin_vth_rise[site] - vin_vth_fall[site]) * 1e3; // mV
        VIN_VTH_Rise->SetTestResult(site, 0, vin_vth_rise[site]);
        VIN_VTH_Fall->SetTestResult(site, 0, vin_vth_fall[site]);
        VIN_VTH_Hys ->SetTestResult(site, 0, vin_vth_hys[site]);
    }

    return 0;
}
