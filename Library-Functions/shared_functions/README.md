# Shared Functions — 跨项目共享子函数库

**定位**: 跨项目复用的 STS8300 子函数(helper function)沉淀库。由 `sub-function-agent` 维护, 从每日 daylog 中的代码 diff / 重复模式提炼, 人工审核后发布。

**与 `D:\Newtest\CLAUDE_PROCESS\Library-Functions\Test_Method` 的关系**:
- `D:\Newtest\CLAUDE_PROCESS\Library-Functions\Test_Method` = **专项 ramp 捕获库**(64 具体函数 + gen_ramp64.py 生成器, Test_Method 库的主源), 各项目有独立副本
- `D:\Newtest\CLAUDE_PROCESS\Library-Functions\shared_functions` = **通用子函数库**(跨项目共享的 helper: 上电序列 / 测量模板 / 寄存器写入 / 下电序列 / 常量定义), 与 test_method 平级

两个库分工: 项目专有的 ramp/测量捕获 → test_method; 通用可复用的子函数 → shared_functions。

## 目录结构

```
D:\Newtest\CLAUDE_PROCESS\Library-Functions\shared_functions\
├── README.md            ← 本文件 (库定位)
├── registry\
│   ├── index.md         ← 子函数注册表 (唯一权威索引)
│   └── changelog.md     ← 变更日志 (版本/来源/回滚)
├── draft\               ← 待审核区 (sub-function-agent 写入, 人工确认后发布)
│   └── <函数名>.md      ← 每条一个建议, 含代码 + 用途 + 来源 + 适用范围
└── src\                 ← 已发布子函数源码 (人工确认后从 draft 迁移)
```

## 子函数注册表条目格式 (registry/index.md)

```markdown
## <函数名> (如 sfn_vcc_power_on)

| 字段 | 值 |
|------|-----|
| 状态 | active / retired |
| 版本 | v1.0 |
| 来源 | daylog/<date>.md / 项目X 代码 |
| 适用范围 | 所有 STS8300 项目 / 仅 DALI 类 |
| 首次使用 | TMxxx (日期) |
| 验证 | verify 脚本 / 编译通过 |

### 用途
一句话说明这个函数解决什么。

### 签名
```cpp
void sfn_vcc_power_on(...);
```

### 代码
```cpp
// 完整实现
```

### 回滚
出现回归时, 从 changelog.md 找到上一版本, 人工确认后恢复。
```

## 发布流程 (human-in-the-loop)

1. `sub-function-agent` 从 daylog 提炼 → 写入 `draft\<函数名>.md`
2. 工程师审核 draft → 确认
3. 代码迁入 `src\`, 索引登记 `registry/index.md`, 变更记入 `registry/changelog.md`
4. 出现回归 → 回滚(从 changelog 恢复上一版本)

> 铁律: 子函数库更新必须 human-in-the-loop。agent 只提建议, 不直接改已发布库。
