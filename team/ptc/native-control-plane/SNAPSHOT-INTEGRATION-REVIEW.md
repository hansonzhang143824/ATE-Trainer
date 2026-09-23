# Training snapshot integration review

审查日期：2026-09-22。范围：training-materials / guard / dispatch / execution，以及 lifecycle、实际调用的 Python DFT 生产器和门禁。本报告为代码只读审查结论；不把静态风险当作已发生的线上故障，不执行真实交付。下面记录审查时版本，后续修复应另记验证结果。

## 已确认问题

### 1. 输入与草稿已冻结，实际执行策略尚未完整冻结（高）

`training-materials.js:130` 的 sources 只包含 workbook、special information、解析规则、instructions、profile.yaml、output-contract.schema.json；`:146` 的 cacheKey 只覆盖这些文件。`training-paths.js` 和 `training-execution.js:74` 仍调用工作区实时 `scripts/*.py`。这些脚本进一步导入 `dft_source`、`dft_test_condition`、`material_plaintext_hash`、`ptc_contract_schema`、`ptc_trim_validation` 等实时依赖。

因此修改实际解析代码或门禁代码不会改变现有 cacheKey，运行中也未验证其与创建时版本一致。输出 schema 文件虽然被复制，实际门禁使用的是 Python `ptc_contract_schema.validate_test_condition`，不是已复制的 JSON schema。`profile.yaml` 被复制，但模型选择仍来自 `agentDefaultModel.currentSelection()`（dispatch:83）；该文件本身尚不是实际模型配置的执行来源。

建议记录所有实际策略脚本及本地依赖的明文 SHA-256，将其纳入 cacheKey；每次生产器/门禁调用前及宿主门禁后复核，变化立即 BLOCKED，后续用新 run。无需为此把脚本复制到伪造仓库。

### 2. 已完成候选没有绑定原完成时的三文件集合（高）

materials:158 选择候选的条件是 `state.status === completed`、旧 manifest.cacheKey 相同和 runId 匹配；`:173` 随后复制该目录中当前的三份产物。没有读取旧终端证据，也没有比对原完成时每份产物的字节 SHA-256。

当前门禁确实重新校验 workbook hash、原始行覆盖、条件字段以及 review 对 meta/yaml 的当前字节绑定（validate_dft_outputs.py:183–200、215–250）。这可捕获普通过期产物，但不能证明当前三份文件仍是那个已完成、指定草稿的运行所验收的集合。例如已完成后替换了 review，或外部编辑同时重绑了 meta/yaml/review，completed 和 cacheKey 不会自行失效。

建议宿主完成和 UNCHANGED 证据都记录 `finalProducts[TM][filename] = exactByteSha256`，包含 review 文件本身。这个宿主验收摘要不属于 review 自我引用。候选复制前后比对上一完成证据的三文件摘要，不一致时禁止快复用。

### 3. 宿主执行入口的路径检查发生在首次写入之后（高）

executeTrainingRun 在调用 prepareTrainingMaterials 之前读取 run/state 并写 execution.lock、checking state（execution:173–192）。该入口只核对 context.mode/runId，没有调用已加固的 assertSafeRunPath。reconcileInterruptedTrainingRuns 同样直接枚举目录并写 state/receipt。

新建运行入口已拒绝 junction，但如果既有目录之后被外部替换，上述两个入口仍可能先沿 junction 写入，再由材料准备检测到异常。训练 child 无权自行实施该替换；这是宿主既有状态验证缺口。建议在任何读取/写入之前验证运行目录、run/state/receipt/lock 及其祖先路径。

### 4. 全运行取消范围尚未覆盖材料准备和最终宿主门禁（中）

dispatcher 生命周期覆盖 agents.create、whenIdle、subagents.start 和 child.result；这是已正确实现的范围。材料准备及前置门禁先于 dispatcher 创建；最终宿主门禁在 child.result 的 finish 关闭生命周期之后执行（execution:116，dispatch:153）。stop API 仅查询 dispatcher.active，因而这两段没有可取消的 active dispatcher，返回 409。每次显式宿主 Python 命令已有 30 秒超时，但缺少这两段共享的整轮取消/deadline。

建议整个 executeTrainingRun 拥有运行级生命周期，或明确将准备与复核也纳入控制句柄。未在本审查中证明单条 DSH pwsh 工具实际超过 30 秒；宿主工具层是否另有超时需单独核实。

### 5. 回执关闭持久化失败时缺少独立的内存撤权判断（中，条件风险）

closeReceipt 先把内存 receipt 标记 closed，再写磁盘；onCancel 的写入异常被 lifecycle 记录后继续发 abort。guard 权限判断读取磁盘 executionStatus，未查询内存 lifecycle。若撤权写盘失败而子会话未及时结束，旧磁盘回执仍可能授权后续调用；后续 closeReceipt 又因内存 closed 而提前返回。这是可从控制流确认的失败分支，未证明真实运行发生过此写盘故障。

建议 guard 额外查询宿主内存 revoked 集合，并保证失败撤权不可重新授权；磁盘关闭仍用于重启恢复。

## 源路径迁移的确切影响

复制候选保留其旧 canonicalInput/sourcePath/readSources/reviewedArtifacts.path 文本，但字节不变。当前门禁不会因这些路径仍指向上一运行而失败：它使用传入 workbook 的明文 hash，review.readSources 检查 hash 与 withinInputRoot=true，reviewedArtifacts 仅按 basename 匹配当前文件 hash。新 run 的 output_dir 在 workbook.parent.parent 内，符合当前范围校验；refresh 的 runRoot 也能递归找到唯一 workbook。

这意味着快复用的内容门禁可保持 ready，原始路径文本仍表示原生成来源。不能向用户宣称这些内嵌路径已重写为新运行，也不应只为迁移路径改写候选而破坏原 review 绑定。建议宿主候选来源及 finalProducts 证据明确记录原 run 与新 run 的复制关系；如果将来要求产品内路径必须属于当前 run，应作为新契约整体再生成。

## 已确认有效的保护

- 输入使用 Python 明文视图复制，并调用批准的 hash_ate_plaintext.py 检查复制前、源复制后、目标三个 SHA-256。
- 每 run 的输入/profile 与产物目录独立；child 只能写指定 TM 的三产物及带指定 TM 的 verification。
- 回执要求正确 runId、label、childSessionId 和 SHA-256 摘要；未绑定 child、错 session、重复回执、closed 回执均拒绝。
- guard 拒绝 workspace 祖先 junction、目标链接和硬链接，阻止跨 TM、跨 run、共享目录和生产目录写入。
- 取消后不执行最终成功门禁，状态不冒充 completed；迟到 handle 会被处置，raw settlement 与 disposal 证据分开保留，不把 abort 等同于进程已终止。
- 已完成复用只有 cacheCompatible 与当前 gate ready 同时满足才成立；旧共享目录因无草稿 provenance，首次迁移不会直接 UNCHANGED。

## 验证边界

本报告来自对应 JS 源码与 Python 明文源码阅读，没有修改执行代码，没有调用生产流水线，也没有将条件风险描述为线上复现。优先补齐策略指纹与完成产物封存证据，再扩大整轮生命周期和异常撤权覆盖。

## 本次审查后的落实记录

后续收到根代理明确实施授权，已在原审查基础上修复第 1、2 项的本模块职责部分：材料 manifest 升级为 v2，记录十个实际 DFT 脚本及本地依赖的批准 Python 明文 SHA-256 并纳入 cacheKey；同时记录 policy 文件磁盘字节摘要，仅作同步 guard 的变化信号，不作为规范输入 hash。`verifyTrainingMaterials` 在宿主门禁前后可检查冻结 input/profile 和实时策略，`verifyTrainingPolicySync` 已接入 material tool guard。发生变化时拒绝当前 run，不原地重绑。

候选复用现在必须读取上一已完成运行的终端或 preflight 证据，核对 runId、cacheKey、此 TM 的 ready/exit 0 报告，以及 `finalProducts[TM][filename]` 的三份最终字节摘要；复制后再次比对。只写 completed 状态或修改已封存 review 不再允许快复用。根代理负责 execution 的证据输出和门禁前后调用。

验证：guard 专属测试 8/8 通过；materials 专属测试 6/6 通过。批量策略哈希仍在单个 Python 解释器里逐次运行原批准命令，未另写哈希算法；材料测试总耗时由逐进程版约 73.4 秒降至 23.7 秒。该耗时覆盖多个独立运行的创建、复入、篡改和候选检查，不是一轮用户运行耗时。

仍需分别核实报告中的其他入口安全、整轮取消和撤权持久化失败分支。外部 Python/openpyxl 安装版本和 DSH 全局默认模型尚未纳入这里的十个仓库策略脚本快照；当前修复不宣称冻结了整个宿主运行时。
