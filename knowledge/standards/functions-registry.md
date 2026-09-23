# 函数注册表 Functions Registry

> 唯一权威索引：STS8300 测试代码生成时「生成前先查，命中复用」的函数清单。
> 三注册表之一：规则→`rules-registry.md` / 材料→`references/param_type_index.md` / 函数→本文件。
> 维护：sub-function-agent 提 draft + 人工审核发布；生成代码前先查本表，命中→调函数（带正确参数语义），未命中→写裸代码（收尾 ≥2 处重复标记给 sub-function-agent 提炼）。

## 函数库定位

| 库 | 路径 | 定位 | 读写注意 |
|----|------|------|---------|
| test_method | `D:\Newtest\CLAUDE_PROCESS\Library-Functions\Test_Method\Test_Method.h` / `.cpp` | 专项 ramp / OS / 量程捕获库（NU 通用，各项目有副本） | **DLP 加密，读写走 python 字节模式，禁文本模式** |
| shared_functions | `D:\Newtest\CLAUDE_PROCESS\Library-Functions\shared_functions\` | 跨项目通用子函数（上电/测量/寄存器/下电/常量） | 普通，draft→人工→src |

> 说明：`shared_functions` 当前**无已发布子函数**（src/ 空），仅 registry 有分类占位。本表实际登记主体是 test_method。

---

## 已登记函数（test_method · Test_Method 类）

> 签名来自 `Test_Method.h`（2026-08-03 版）。ramp 家族共用一套调用语义（见下）。
> 完整 64 函数矩阵由 `gen_ramp64.py` 生成（4 类型 × 4 ramp 源 × 4 cap 源）。

### ramp 家族共用调用语义

| 项 | 约定 |
|----|------|
| `step` | **采样点数**（samples = (int)step），不是电压步进 |
| `interval` | 采样间隔，**≥ 10** |
| `trig_level` | 触发阈值（电压/电流） |
| `trig_mode` | `TRIG_RISING` / `TRIG_FALLING`（定义于 FloatingVI.h） |
| `result` | **触发点处的 ramp 电压/电流**（输出） |

### 函数清单

| 函数 | 签名要点 | 触发场景 | 调用语义/坑 | 调用点 |
|------|---------|---------|------------|--------|
| `OS_Classify` | `(funcindex, pin_str[], OS_NUM, leak_str[], LEAK_NUM, os_result[][SITE_NUM], leak_result[][SITE_NUM], vec_exclude)` | OS 接触测试分类 | 一次性分出 OS/漏电，结果写数组 | 待补 |
| `get_fovi_v_range` | `(double v) → FOVIe_VRNG` | 电压量程决策 | 按目标电压返回量程枚举 | 待补 |
| `ramp`（5 重载） | ACM / FOVIe(带 ACM cap) / FOVIe 双源 / FOVIe / FPVIe 双源 | ramp 捕获 | 见共用语义 | 待补 |
| `ramp_v` | `(ACM acm_ramp, ...)` | ACM 电压 ramp | 同上 | 待补 |
| `ramp_I` | `(FOVIe fovi_ramp, ..., FOVIe fovi_cap, ...)` | FOVIe 电流 ramp | 同上 | 待补 |
| `ramp_ucp` | `(FPVIe fpvi_ramp1, fpvi_ramp2, fpvi_gp_bysite[][SITE_NUM], ...)` | FPVIe ramp | 同上 | 待补 |
| `rampv_capv`（5 重载） | ramp源∈{ACM200, FOVIe, FPVIe} × cap源∈{FOVIe, ACM200}，签名 `(ramp_res, ramp_vrange, ramp_irange, cap_res, cap_vrange, cap_irange, start, stop, step, interval, trig_level, TRIG_MODE, result)` | 电压扫 + 电容源捕获 | 电压 ramp，result=触发点电压 | `toggle-template.cpp`（VAC 迟滞） |
| `rampi_capv`（4 重载） | FPVIe ramp × cap∈{FOVIe, ACM200}（含 capreturn 变体） | 电流扫 + 电容源捕获 | 电流 ramp，result=触发点电流 | 待补 |
| `rampi_fv_capv` | `(FPVIe ramp, ACM200 cap, ACM200 capret, ...)` | 电流扫 | 同上 | 待补 |

---

## 登记/更新协议

给我新增或改动函数时，贴此模板（我登记进本表 + 影响面检查）：

```
【类型】新增函数 / 改签名 / 改语义 / 弃用
【函数名】rampi_capv
【库】test_method / shared_functions
【签名】double rampi_capv(...)
【触发场景】ramp 捕获 / 上电 / 测量
【调用语义】step=采样点数, interval≥10, TRIG_RISING/FALLING, result=触发点电压
【调用点】TMxxx
【影响面】改语义 → 哪些已生成 TM 受影响
```

## 状态

- [ ] 待补：`OS_Classify` / `get_fovi_v_range` / `ramp*` 的调用点与具体语义（从实际 TM 案例回填）
- [ ] 待确认：64 函数矩阵是否逐条登记（当前按 9 个家族 + 共用语义收编，不逐条 64）
