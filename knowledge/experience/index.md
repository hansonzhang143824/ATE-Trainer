# 经验库索引 — index

> 项目级实现经验沉淀。由 experience-agent 维护 + 人工审核发布。状态: `active`(可用) / `draft`(待审核) / `retired`(推翻)。

## 条目速查

| 主题 | 文件 | 适用项目 | 状态 |
|------|------|---------|------|
| check E 已落地: TestItemMeta capAuthority 为权威 (OVERVIEW 派生四集), 对象名反推仅降级 | relay-check.md | DALI 类 | active |
| 供电 PIN 判定: 权威来源是 DFT 意图 + SCH-Connect-Map 继电器链→PIN, 对象名反推是兜底 (根因, 已由 meta 权威落地) | relay-check.md | DALI 类 | draft |
| 测试垫偏置: 名字含供电 token ≠ 供电轨 (对象名反推固有歧义) | relay-check.md | DALI 类 | draft |
| 豁免粒度反模式: 函数级/集合级豁免 | relay-check.md | DALI 类 | draft |
| Cap 修复后快速验证工具链用法 | project-notes.md | DALI 类 | draft |
| 源表规格三层权威 + 实卡宏交叉验证 (编程手册无精度→硬件手册补齐; 5处转写纠错) | project-notes.md | DALI 类 | draft |

## 分类说明

| 主题 | 收录什么 |
|------|---------|
| power-sequence.md | 上电/下电绕法、台阶经验、RELAY_OFF 量程教训 |
| measurement.md | 量程选择、时序、测量报错含义 |
| debug-patterns.md | 常见报错 → 根因速查 (资源名错/调用顺序/未初始化) |
| relay-check.md | 继电器/Cap 检查脚本 (verify_relay_trace.py) 实现陷阱: token 消歧/测试垫判定/豁免粒度 |
| project-notes.md | 项目专属决策记录 (不做规则, 只留参考) |
