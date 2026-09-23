# 寄存器配置（Register Config）

> 规则层：所有测试函数（普通 / Toggle-AWG / Trim）配置寄存器的通用步骤规则。
> 关联：`framework.md` Step 3（模板已含 `entertestmode()`）、`rules-registry.md`、`Library-Functions/treg/`（Trim Library-Functions）、`error-checklist.md`（H011/R034）。
> **区分**：寄存器配置 = 通用步骤（所有函数都做）；treg = Trim 专属Library-Functions（只 Trim 用）。Trim 函数里既要配寄存器、又要调 treg，两者并行。

## 铁律（已有，指向）

- **entertestmode()**：重新上电后、配置寄存器前必须先调（写密钥解锁测试寄存器）。见 `framework.md` Step 3。
- **REGISTER_CODE 来源**：DFT `Software_initial` 原样复制（见 `framework.md` 占位符说明）。

## 寄存器配置铁律（重新上电必须先进测试模式）

**只要该测试项配置寄存器（任何 I2C/寄存器写），配置之前一律先执行 `entertestmode()`** —— **不设条件**：不看是否 Power Cycle、**不看 DFT 有没有 `en_tm[]`**（2026-09-13 用户拍板） —— 芯片上电后寄存器写入受**密钥（Key）保护**，必须先写密钥解锁测试寄存器，才能用 `I2CWriteSameData` 配置寄存器：
```cpp
entertestmode();   // 写密钥解锁测试寄存器（密钥写入序列在此函数内实现）
<%REGISTER_CODE%>
```
- **原理**: 重新上电 = 芯片回到受保护初态，测试寄存器被密钥锁住；`entertestmode()` 内含**密钥写入序列**；DFT 的 `en_tm[]` 只是**提示**，**不作为是否调用它的判据**（DFT 可能漏写）。漏解锁 = 寄存器**静默写不进去**、测试结果失真 —— 比多写一次解锁危险得多，故一律加 → **每次重新上电后都必须重新进一次测试模式，不能省略**
- **适用**: 每个"上电 → 寄存器配置"流程（Step 2 → Step 3）；含多参数/多次测量的函数中，每次重新上电后再次配寄存器之前都必须先调用一次
- **例外**: 仅当 DFT 明确无 en_tm[]（如纯睡眠 Iq 测量）才不调用，但须在注释说明原因；DFT 用 key1_open 等替代命令进入测试路径时按其原始设计
- 检查项: check-agent **R034**（强化: 上电后、配寄存器前必须有 entertestmode()）

## 配置位置

_待填_：哪些寄存器写 test.cpp 主函数、哪些下沉 sub_func（判定规则）

## registermap 读取

_待填_：从 DFT 的「配置含义」→ 查 registermap 拿实际寄存器地址/值 的方法

## 待确认

- [ ] 配置位置判定（test.cpp vs sub.cpp）
- [ ] registermap 文件位置 + 读取方法
- [ ] 是否脚本化（registermap 解析）
