# Claude 交接文档：任务 B4 验收（2026-10-02）

> 给新开的 Claude 会话：先完整读本文，再读第 2 节列出的仓库文档。用户会贴来 Codex 的「B4 做完了」回复，你的工作是按第 5 节验收。

## 1. 项目与分工

- 项目：ATE PTC Runtime / Agent Trainer。它是 DSH（DeepSeek Harness）上的专家 Agent 训练、冻结、发布、工程回放系统。
- 仓库：`D:\Newtest\DSH\ATE-Coding-Flow`（Windows，用户机器 pc-nvtsh0177）。远端为 GitHub，`master` 与 `main` 两个分支都要推，并保持一致。
- 工作台：`http://127.0.0.1:3080/agent-trainer`；DSH 宿主：`http://127.0.0.1:3080/`。
- 分工：**Codex 实现和自测**（用户在 Codex 里用 `/goal` 模式连续执行）；**Claude 写任务书、验收、诊断**。
- 用户习惯：
  - Codex 指令直接贴在聊天里的代码块中，用户自己复制。不要再用剪贴板工具。
  - 指令必须以 `/goal` 开头，写全计划文档和验收文档的完整路径，并写明停止规则。
  - 验收结论只给「通过」或「不通过 + 问题清单」，修复交回 Codex。
  - 用户要求结论经过认真核实再给；曾因 Claude 给出未经核实的结论而要求复查（见第 4 节）。

## 2. 必读仓库文档

| 文档 | 内容 |
|---|---|
| `docs/tasks/00-PLAN.md` | 迭代计划；2.4 节为 5 条硬停止条件；第 6 节为 B 验收清单 |
| `docs/tasks/A-agent-delete.md` | 任务 A（Agent 删除 + ID 台账）任务书与完成报告 |
| `docs/tasks/B-expert-fixed-session.md` | 任务 B（专家固定训练会话）任务书；第 5 节为验收 1~14；末尾 6.1、6.2 节为 B2、B3 报告，B4 报告会追加为 6.3 |
| `docs/tasks/B2-fix-plan.md` | B2 修改计划（含 A 遗留项 A-F1~F3、推送范围） |
| `docs/tasks/verify/README.md`、`verify-a.mjs`、`verify-b.mjs`、`lib.mjs` | Claude 写的验收脚本；`results/` 为运行产物（不提交） |
| Claude Project 文档 `claude/agent-trainer-plan-2026-10.md` | 00-PLAN 的较早副本 |

## 3. 进度与提交

| 阶段 | 结论 | 提交 |
|---|---|---|
| T0 轮询上限修复 | 完成 | `3d7ddf6` |
| A Agent 删除 + ID 台账 | Claude 验收通过；A-F1~F3 遗留项已在 B2 中修复 | `033a602` |
| B 第 1 轮 | 不通过：同一目标每次打开都新建 DSH 会话；宿主窗口验收未做 | `bdda5c7` |
| B2 | 服务端复用已修好；不通过：B 任务书混入 5563 个 0x00；报告缺逐条证据 | `caf6af8` |
| B3 | C-1 空字节已清除、C-2 超时保护已加、C-3 报告如实；B 整体仍差 E-1~E-3 | `d791fb2`（实现 `928b52d`） |
| **B4** | **Codex 执行中，等待结果** | — |

B3 之后 `HEAD = github/master = github/main = d791fb2`。

## 4. 重要经验与坑（务必读）

1. **Claude 内置浏览器不能用来判断宿主会话。** 内置浏览器里宿主的 `ws://127.0.0.1:3080/api/events.mux` 连不上，宿主侧栏所有工作区展开后都是空的（连 `ATE-Coding-Flow` 也是空的）。所以「会话不在列表 / 宿主卡住 / NATIVE_SESSION_NOT_LISTED」在内置浏览器里出现**不能作为代码缺陷证据**。Claude 曾据此误判「换个宿主页面就打不开」，已向用户撤回。
   - 内置浏览器仍可用于：调用 `/api/ptc-control/trainer/*` 接口（POST，body 带 `projectId:'agent-trainer'`；`target-session` 还需 `presetId:'agent-trainer'`）、读取工作台 DOM，以及看宿主标签里的网络请求顺序（`read_network_requests`）。
   - 真实宿主检查以 Codex 的实测为准；如需 Claude 亲自做，用 computer-use 操作用户电脑上的 Chrome 或 Edge（需用户批准）。
2. **本会话没有 device_bash。** Claude 只能用 `device_list_dir`、`device_stage_files`、`device_commit_files` 读写仓库文件，不能直接跑 git、node 或重启 DSH。要跑命令，只能用 computer-use 操作 PowerShell（需用户批准）。
3. **读 git 信息的办法**：stage `.git/logs/HEAD`（提交历史，时间戳为 Unix 秒，需加 8 小时转为本地时间）和 `.git/refs/heads/master`、`.git/refs/remotes/github/main`、`.git/refs/remotes/github/master`。
4. **检查验收脚本是否被倒序或敷衍执行**：看 `docs/tasks/verify/results/*.json` 的 `at` 时间和文件 mtime。例如 B 第 1 轮的最终检查只比 compare 晚 11 秒，且显示 0 条会话记录，说明宿主实测根本没做。`context-baseline.json` 的 mtime 应保持 `1790913054180`（B 开工前），不得重新 snapshot。
5. **verify-b compare 中 training/published 的 FAIL 已核对可接受**：差异只是新增测试 Agent `agent-2abe705b` 及 revisionId 变化（数据漂移）；字段、权限、工作流、冻结版本都与基线一致。engineering 应为 PASS。
6. **文件编码**：PowerShell `Add-Content` 曾往 Markdown 里写入 0x00。验收时必须检查 B 任务书 `0x00` 数量为 0、能按 UTF-8 解码。
7. **PowerShell 读本机文件可能拿到密文**（透明加密层），判断文件内容一律用 node、python 或 stage 后在云端读。
8. **Codex 常见问题**：容易把没做的项标成「通过」；容易把属于自己的宿主验收推给「待用户执行」。要逐条看证据（sessionId、bindings / target-sessions 字段、宿主当前会话），不要只看汇总。
9. computer-use 授权 30 分钟无操作会过期；`computer_release_lock` 可能恢复剪贴板。

## 5. B4 验收清单（收到「B4 做完了」后执行）

B4 指令全文见附录。逐项核对：

1. **Git**：stage 三个 ref 文件，确认 `HEAD = github/master = github/main` 且等于 Codex 报告的 hash；reflog 中有 `[B4]` 提交。
2. **文件**：B 任务书 0x00 = 0，UTF-8 可解码；末尾有「6.3 第 4 轮（B4）」报告。
3. **E-1「新开训练会话」**：读 `plugins/dsh-ptc-control-plane/client/native-sessions.js` 的 `openTrainerNativeSession`，确认 `request.freshSession` 为 true 时不走复用，先 `forget-target-session` 再 `open-native-session`，并记录 `previousSessionId`。B3 的问题点：约第 198~215 行，`remembered = record?.sessionId || …` 在 freshSession 时仍取旧会话。确认有对应测试，且 `lib/client.js` 已重建（`verify-b.mjs` 的 B-build-1 会检查）。
4. **E-2 重启复用**：报告需给出 (a) 同一宿主页面、(b) 重新加载宿主页面、(c) 重启 DSH 之后，三个场景各自的 sessionId 和宿主当前会话。若 (b)(c) 失败，需有数据来源调查结论和证据，不得用自动新建冒充复用。`NATIVE_SESSION_NOT_LISTED` 提示应写明会话 ID，并引导用户点「新开训练会话」。
5. **E-3 宿主验收**：第 3、4、6、7、9、11、12 条必须是真实宿主执行并附证据；只有第 8 条可标「待用户执行」。抽查 1~2 条的 bindings、target-sessions 文件：
   - target-sessions 目录：`Training_Materials/framework/control/target-sessions/`（文件名为 sha256 前 32 位）；
   - binding：`Training_Materials/framework/control/bindings/<sessionId>.json`。
6. **脚本与测试**：`verify-b` 最终无 FAIL，且显示有会话记录；`verify-a --mutate --smoke` 无 FAIL；插件全量测试（B3 时为 400 passed）不减少、0 failed；重启 Gate A/B/C 通过。
7. **接口抽查（内置浏览器可做）**：对 X 调 `target-session`，sessionId 应与报告一致；`/api/ptc-control/trainer/runs` 最新 SMOKE run 为 completed。

结论：全部满足则「B 通过」，按 00-PLAN 第 1.4 节，B 验收完成即本轮迭代结束，告诉用户并建议下一步（见第 7 节）。不满足则出「不通过 + 问题清单」和新的 `/goal` 指令。

## 6. 如果 B4 仍不通过：由 Claude 亲自操作（用户已同意）

- 先请用户批准 computer-use：终端（PowerShell 或 Windows Terminal）+ 浏览器（Chrome 或 Edge）。
- 在终端中：`cd D:\Newtest\DSH\ATE-Coding-Flow` → `git fetch github --prune` → 修改代码 → `node plugins/dsh-ptc-control-plane/scripts/build-client.mjs` → 运行插件测试（在 `plugins/dsh-ptc-control-plane` 下执行 `node test/all.test.mjs`）→ 重启前确认没有进行中的 framework run → `& "C:\Users\nvt10241\.dsh\rules\dsh-plugin-restart.ps1" -Profile web -PluginDir .\plugins\dsh-ptc-control-plane`（Gate A/B/C 必须通过；失败会自动回滚）。
- 在真实浏览器中：一个标签开宿主 `http://127.0.0.1:3080/`，从「打开 ATE Trainer」链接取 `nativeHost`，另一个标签开 `/agent-trainer?nativeHost=<id>`，逐条执行验收。
- 写文件用 node 或 python 按 UTF-8 写，不用 PowerShell 的 `Add-Content` / `Out-File`。
- 提交只 add 本轮相关路径，信息以 `[B4]` 开头；推送 `github master` 与 `github main`；不强推。
- **不得删除任何 DSH 会话或 bindings 文件**；第 8 条（删会话）动手前单独问用户。

## 7. 测试数据与遗留

- 测试 Agent X = `agent-2abe705b`（名「新 Agent 12」）。历史会话：`session-34c931f4…`、`session-39443adf…`、`session-b9c2c46f…`（B 第 1 轮 bug 造成的重复会话）、`session-c2044dd0…`（B2 新开）、`session-e9dbff85-4e3d-43bc-90d7-be5752fd88ed`（B3 起的当前会话）。workflow-T1 会话：`session-8c000ae3…`。都不要删除。
- 台账 `contracts/agent-ids.json` 只增不减，验收产生的 ID（如 `agent-74be5219`、`agent-b874b4a8`、`agent-2f86883e`、`agent-2abe705b`）按设计保留。
- 00-PLAN 第 9 节的延期项：发布模式待审核指针、冻结版本排序、撤销删除、删除时连带移除步骤、BUSINESS 运行刷新后接回、业务运行明确终态。
- B 完成后可建议：更新 Claude 之前发布的「ATE PTC Runtime 现状报告」页面（Artifact，标题「ATE PTC Runtime 现状报告」），补上 A、B 完成情况。

## 附录：用户已发给 Codex 的 B4 指令全文

```
/goal 修复「新开训练会话」失效，验证重启后复用，并在真实宿主中补完 B 验收。仓库：D:\Newtest\DSH\ATE-Coding-Flow
当前基线：本地 HEAD = github/master = github/main = d791fb2。

【先读文档】
- B 任务书（验收 1~14；末尾 6.1、6.2 节是前两轮报告）：D:\Newtest\DSH\ATE-Coding-Flow\docs\tasks\B-expert-fixed-session.md
- 修改计划：D:\Newtest\DSH\ATE-Coding-Flow\docs\tasks\B2-fix-plan.md
- 迭代计划（2.4 节硬停止条件）：D:\Newtest\DSH\ATE-Coding-Flow\docs\tasks\00-PLAN.md
- 验收脚本：D:\Newtest\DSH\ATE-Coding-Flow\docs\tasks\verify\README.md、verify-b.mjs

【Claude 验收 B3 结论：C-1、C-2 超时保护、C-3 报告通过；B 整体还差以下 3 项】

E-1（阻断，代码问题）「新开训练会话」不会新开
- 位置：client/native-sessions.js 的 openTrainerNativeSession（约第 198~215 行）。freshSession:true 只清掉了本地缓存，但 remembered = record?.sessionId || … 仍然取到服务端记录的旧 sessionId，随后按服务端权威复用分支返回原会话。B2 里拿到 c2044dd0 只是因为当时复用总是失败、被动走了 forget + 新建；B3 修好复用后，这个按钮实际不再新建。
- 修改要求：request.freshSession 为 true 时不走复用。先 forget-target-session，再 open-native-session 新建，并在 binding 或 target-session 记录中保留 previousSessionId；旧会话和旧 binding 文件不删除。卡片显示「新建会话（替换 <旧ID>）」。
- 补测试：服务端记录有效时 freshSession 仍然新建（sessionFactory 调用 1 次、forget 调用 1 次、返回的新 ID ≠ 旧 ID、previousSessionId = 旧 ID）；没有 freshSession 时仍然复用（以上两个调用都是 0 次）。

E-2（需验证）DSH 重启后能否复用
- 你在 6.2 节写到：重启后旧会话 c2044dd0 不在新宿主进程的 sessions.list 里。目前只有这一次观察，原因没查清。
- 本轮验证：对 X=agent-2abe705b，在 (a) 同一宿主页面、(b) 重新加载宿主页面、(c) 用 dsh-plugin-restart.ps1 重启 DSH 之后，分别打开一次，记录 sessionId，以及宿主是否真的切换到该会话（写明宿主当前会话 ID 或标题）。
- 如果 (b) 或 (c) 失败：调查宿主 sessions.list 的数据来源，以及空会话（从未发过消息）和有消息的会话有没有区别；对比测试时给一个会话先发一条消息再重启。把结论和证据（代码位置或持久化文件路径）写进报告，能修就修。不允许靠自动 forget + 新建来充当“复用成功”。
- 不论结果如何，都要修改 NATIVE_SESSION_NOT_LISTED 的提示：写明会话 ID，并告诉用户可以点「新开训练会话」继续（依赖 E-1 修好）。不要只写「刷新 DSH 页面后重试」。

E-3（阻断）宿主窗口验收未完成：6.2 节第 3、4、6、7、9、11、12 条为「待用户执行」。你的浏览器自动化环境能正常加载宿主会话列表（B3 中 3 次复用成功），这些条目必须本轮在真实宿主中完成。只有第 8 条（在 DSH 中删除会话，属于硬停止条件 4）继续标注「待用户执行」。
- 第 6 条按原文执行：清掉宿主 localStorage 中 ptc-native-session: 开头的项，重新加载宿主和工作台，再打开 X，应为同一 sessionId。
- 第 7 条在 E-1 修好后通过页面按钮执行。
- 第 11 条另建测试 Agent Y 执行：打开 Y 的会话 → 从工作流移除 Y → 用 A 的功能删除 Y → target-session 查询 Y 返回 null → 新建 Z，Z 得到全新会话。删除的是候选里的 Agent，不是 DSH 会话，不违反硬停止条件。
- 每条记录 sessionId、bindings 和 target-sessions 的关键字段，以及宿主是否真的切换到该会话。

【执行顺序】
git fetch github --prune → 修 E-1 并补测试 → 修改 E-2 的提示文字 → 用 scripts/build-client.mjs 重建 lib/client.js → 用 C:\Users\nvt10241\.dsh\rules\dsh-plugin-restart.ps1 重启 DSH（已授权；重启前确认没有进行中的 framework run）→ 在真实宿主中做 E-2 的 (a)(b)，再执行 B 验收 1~14（第 8 条除外）→ 再重启一次 DSH，做 E-2 的 (c) → 运行 node docs/tasks/verify/verify-b.mjs、node docs/tasks/verify/verify-a.mjs --mutate --smoke、插件全量测试 → 在 B 任务书末尾追加「6.3 第 4 轮（B4）」报告（用 Node/Python 按 UTF-8 写入，写完确认 0x00 数量为 0）→ 只提交本轮相关路径，提交信息以「[B4] 」开头，推送到 github 的 master 和 main，确认本地 HEAD、github/master、github/main 三者一致且 0/0。

【停止规则】
只有命中 00-PLAN.md 2.4 节的 5 条硬停止条件才停下，其余问题自行决策并在报告中记录。不得删除 DSH 会话或 bindings 文件，不得直接改写 revision / 冻结版本 / release 文件，不得改变 context 的返回内容，不得强推或改写 Git 历史。宿主窗口没有实际完成的条目不得写「通过」。

完成后回复「B4 做完了」，附：提交 hash、E-1 新增测试名称、E-2 三个场景各自的 sessionId 与宿主当前会话、B 验收 1~14 结果一览、验收脚本和插件测试结果、github/main 与 github/master 的 hash。
```
