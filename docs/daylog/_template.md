# 每日档案 — YYYY-MM-DD

> 三个自进化 Agent (rules/experience/sub-function) 的共享数据源。主 skill 收尾时写入, 或 debug/修改后追加。
> 每个事件记一条, 用下面的 6 类标记。temporary debug note 和 not useful 类明确标注, 提炼时排除在长期库外。

## 事件记录

### <时间> | <事件类型: codegen/debug/报错修复/规则修正/人工反馈>
- **TM**: TMxxx (或 N/A)
- **内容**: 一句话描述发生了什么(修改了什么/报了什么错/工程师怎么纠正的)
- **代码 diff** (如有): 变更前后的关键差异
- **来源**: 哪个 skill / 哪个 agent / 工程师口述
- **初步分类**: (提炼前可留空, 由 agent 分类)

---

## 六类提炼结果 (agent 分类用)

| 类 | 含义 | 进长期库? |
|----|------|:---:|
| global rule | 可泛化到大多数 STS8300 项目 | ✅ 规则库 |
| specialized rule | 只适用特定项目/测试类型/资源 | ✅ 规则库 (带适用范围) |
| project-specific experience | 对类似项目有参考价值, 不强制为规则 | ✅ 经验库 |
| sub_function usage | 可复用 helper/封装模板 | ✅ 子函数库 |
| temporary debug note | 只对当前 debug 有用 | ❌ 排除 |
| not useful for rules | 价值不足 / 已有知识覆盖 | ❌ 排除 |
