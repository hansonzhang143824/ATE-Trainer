# 吸收记录 #28 — codex 迁移接缝调查①：proj_config/check-agent/AGENT_MAP 结构（subagent 只读）

- 源文件：`sessions/28-agent-a5.md`（237 行，全文）← `~/.claude/projects/subagents/agent-a5b868ea2c254bf63.jsonl`
- 时间：2026-08-23 15:14 → 15:15（0.1MB）；用户 1 条（调查任务）/ 助手 2 段 / 工具 3 次
- 主题：为吸收 codex 迁移的「输入哈希冻结」+「材料门硬门禁」方法论，精确调查现行体系三个文件的内部结构（接缝设计前置）

## 关键结论（结构化调查结果）

1. **proj_config.py（92 行）**：纯读取器零哈希——load() 返回 9 key（project/project_dir/inputs/optional_inputs/intermediates/outputs/derived/_root/_config）；`_read`（rb+utf-8-sig→utf-8→gbk 回退）、`_resolve`（isabs→normpath 否则 join root）、`_resolve_section` 整段路径化；派生逻辑 = vs_src_dir → test_cpp/sub_cpp/stdafx_h（derived 段可覆盖）；config_from_argv 支持 --config。**全文无 hash/sha/md5/checksum**——哈希冻结并入净区：load() 返回 dict 加 _hash key，或在 _read() 拿原始 bytes 时做 SHA-256（DLP 解码前最稳定）。
2. **check-agent.md（248 行，agent 规格非代码）**：检查项实测 **92 主 ID**（front-matter "60+" 过期）：P 6 / E 27 / T 5 / R 35 / V 7(+3 子) / M 4 / H 8。新增检查项 = 组表加行续号 + 定义判定 + 同步输入表/轻量模式 + 脚本强制引用。**无任何"材料/黄金代码/参考案例是否被读取"检查、无材料存在性门禁**——材料门是空白区；现有门禁 keyed 到代码内容正确性，证据机制 = JSON verdict/checks[] + merge_log.md。
3. **AGENT_MAP.md（97 行，2026-08-09 版）**：19 agent 文件（08-10 删 2 个 A0 遗留）；pipeline 中 **relay-agent（#3）与 measure-agent（#6）仍活跃执行未脚本化**（对比 power-on/off→gen_power_sequence.py、cbit P1/P2/P4 已脚本化）；架构原则"推理→agent，固定→脚本"。
4. **接缝建议**：材料门若要拦在生成前 → 接缝在主 Skill 生成循环之前（cbit 公共前置后、relay-agent #3 前），非挂在 check-agent 收尾；哈希冻结接缝在 proj_config.load()/read()。

## 涉及文件

- 只读：proj_config.py、.claude/agents/check-agent.md、.claude/AGENT_MAP.md。零修改。

## 交叉引用

- 三 subagent（#28/#29/#30）同批并行（08-23 15:14-15:16），为 #34（b55b4f8d codex 迁移评审主会话）供料；材料门/哈希冻结在 #31 已见落地（verify_material_receipt.py、project_manifest.py）→ 吸收确实发生了。

## 未决问题

- 无（调查结论直接供 #34 设计）。
