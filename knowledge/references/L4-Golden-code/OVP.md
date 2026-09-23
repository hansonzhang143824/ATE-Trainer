# OVP 要点总结（VBAT 过压保护阈值 AWG）

> 源文件：`L4-Golden-code/OVP.cpp`（函数 VBAT_Protection，101 行）｜索引登记：VBAT OVP（一般测试项目，L1-chip/method 复用 UVLO，同原理族）

## 1. 参数类型
- **VBAT OVP 过压保护阈值 AWG**（UVLO 同原理族：比较器 + 迟滞，含 OVP/PRST/VBAT_LOW/RECHG），一般测试项目。
- 参数族命名：`VBAT_OVP_<NCELL>CELL_<CV>_<Rise|Fall|Hys>`，本案例 12 个参数（2cell/4cell × CV 4V/4.4V × Rise/Fall/Hys）。

## 2. 角色抽象（精髓）
- **被测 rail（ramp 源） = VBAT**：VAC123_VBATD_ACM 施加并 ramp（ACM200_20V/100mA）；VBUS_ACM 仅是供电轨（V_TYP_VBUS，40V 量程）。
- **比较器输出观测脚 = NTC2_FOVI**：内部 VBAT OVP 比较器输出经 DMUX（0x56=0x2B、DMUX_EN=1）mux 到 NTC2，cap 侧 FI=0 观测翻转。
- **档位角色**：N_CELL（2/4）× VBAT_CV（4V/4.4V）四档由寄存器 0x0B 单点切换；ramp 窗口 = spec × cell 倍率（8.4/8.8/16.8/17.6）。
- 下一项目映射：被测供电 rail、比较器输出监测脚、档位寄存器按角色解析。

## 3. 关键结构/特殊点
- **rampv_capv 双扫**：升扫（RL→RH，TRIG_RISING）测上阈值；降扫（FH→FL，TRIG_FALLING）测下阈值 → 每档 2 次、共 8 次 ramp。
- **Hys = rise − fall**：本例直接存 V 单位**未 ×1e3**（与 UVLO/toggle-template 用 mV 不同——写 TM 时先确认 Hys 单位约定）。
- 换档只需改 0x0B（N_CELL+VBAT_CV），其余不动 → "多档复扫"极简范式。
- 寄存器准备：entertestmode + wake_up(0x13=0x02) + CHG_MODE=0 + DMUX_EN=1 + DMUX_SEL=0x2B，把比较器输出引到 NTC2。

## 4. 上电/下电时序
- SetOn：K_VBUS_Cap, K_VCC_Cap, K_VBATD_ACM。
- 上电：VBUS=V_TYP → VBAT ramp 源预置 8V（20V 量程）→ NTC2_FOVI FI=0 → I2C 配置 → 连续 8 次 ramp（升+降交替 4 档）。
- 下电：VBAT/VBUS/NTC2 归 0 → delay 3ms → 统一 RELAY_OFF（量程降 10V/10MA）。

## 5. 测量与判定
- `rampv_capv(VAC123_VBATD_ACM, ACM200_20V, ACM200_100MA, NTC2_FOVI, FXVIe_PLUS_10V, FXVIe_PLUS_100UA, RL×N, RH×N, 400, 10, 2.5, TRIG_RISING/FALLING, …)`。
- Hys 在 FOR_EACH_VALID_SITE 内算 rise−fall 后 12 个参数 SetTestResult；spec 判定在外层。

## 6. 一句话适用场景
VBAT OVP（及 VBAT_LOW/PRST 等同类阈值）"多 cell × 多 CV 档"的阈值 + Hys 测试：双扫 + 换寄存器重扫框架可直接套用。
