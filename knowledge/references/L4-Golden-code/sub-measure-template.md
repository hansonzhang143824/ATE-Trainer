# sub-measure-template 要点总结（Trim sub.cpp measure 函数模板）

> 源文件：`L4-Golden-code/sub-measure-template.cpp`（90 行）｜索引登记：Trim sub 模板 —— Trim 的 sub.cpp measure 函数模板；**铁律：所有 Trim 测量函数放 sub.cpp，不在 test.cpp 直接写 MeasureVI**

## 1. 参数类型
- Trim 项目专用 sub 层模板（非独立测试项）：measure 函数独立成 sub.cpp，供 PARAM_NODE.execute() 每步回调。

## 2. 角色抽象（精髓）
- **Trim 值角色**：`TRIM_NODE *trim_node` + `trim_reg.assy("EFUSE_REG_Fx")` 持有每 site 的 trim 工作值；`working_value[site]` = 逐 site 写入值，`sim_step[site]` = 当前 trim 步记录。
- **烧录回读角色**：flag 为 TREG_MEASURE_PRE/POST 且 BURN_FLAG=BURNNED 时先 `copy_read_to_work`（烧录态必须先回读再改）。
- **测量源表角色**：`<ResourceName>`（FOVI/ACM/FPVI）执行 MeasureVI；MV 取 MVRET、MI 取 MIRET。
- **封装数角色**：= 参数涉及的 EFUSE 寄存器个数（treg 里查 [_EFUSE_REG_Fx]）：1 个 → working_value1；2 个 → working_value1+working_value2。

## 3. 关键结构/特殊点
- 两种 measure 模式，签名统一为 `(TRIM_NODE*, TREG_MEASURE_FLAG, double *results)`：
  - **模式 A 普通 MV/MI**：单源表直测，`MeasureVI(50,5)` 后取 MVRET（或 MIRET）。
  - **模式 B 大电流 + AMUX−NTC 差分**：FPVI `FI=3A`（FPVIe_10A 量程 ≥ 2×3A）→ delay 2ms → MeasureVI → **立即 FI=0 关断**；再 AMUX/NTC 两路 MeasureVI，`results = amux − ntc`（差分，抵消 Sense 端共模）。
- 每步固定节奏：读 working → `dcm.I2CWriteData` 写 EFUSE → delay 2ms → 寄存器配置（从 DFT Software_initial 原样复制）→ 测量。
- 只做"写入 + 测量"，**不含上下电**（上下电归 test.cpp Trim 主函数）。
- 模式选择判据：单点电压/电流量测（VBG/基准）→ 模式 A；需大电流激励或差分回读（CS Gain/大电流 Trim）→ 模式 B。

## 4. 上电/下电时序
- 模板不含继电器组与电源时序（由 Trim 主函数在 execute 前后负责）；sub 函数仅在 execute 每步被调用。

## 5. 测量与判定
- 测量：`MeasureVI` + `GetMeasResult(site, MVRET/MIRET)` 填 results[site]。
- 判定不在 sub 层：步进扫描、spec 比较、target 计算由 execute 框架完成（pre/post/updated/guessed 参数由框架产出）。

## 6. 一句话适用场景
任何新 Trim 参数写 measure 函数的骨架：简单测量抄模式 A，大电流/差分（CS Gain 类）抄模式 B。
