# B5：完成任务 B 剩余的宿主窗口验收（自动化执行）

- 仓库：`D:\Newtest\DSH\ATE-Coding-Flow`（下文路径均相对此目录）
- 编写：Claude（2026-10-02，B4 第 4 轮 `e630981` 验收后）
- 执行：Codex（`/goal` 模式）。验收：Claude
- 本文件是本轮**唯一的执行依据**。执行中如果忘了要做什么，回到本文件第 1 节（目标原文）和第 5 节（步骤）。

---

## 0. 一句话目标

用仓库里新增的验收驱动 `docs/tasks/verify/verify-b-host.mjs`，在**真实 DSH 宿主**（`http://127.0.0.1:3080/`）中自动完成 B 验收第 3、4、5（合并）、6、7（补做）、9、12 条，所有检查项 FAIL = 0，然后写 6.7 节报告，以 `[B4]` 开头提交并推送 `master`、`main`。**本轮预期不改任何产品代码。**

---

## 1. 目标回顾（原文摘录，防止长时间执行后目标走样）

### 1.1 迭代计划的目标（`docs/tasks/00-PLAN.md` 1.2、1.3 第 3 条）

> B：训练专家时，复用会话的 key 包含 `candidateRevision` 与 `selectedRunId`，保存候选或跑一次运行后就新开 DSH 原生会话；映射只存在宿主窗口 localStorage → 训练过程散落在大量会话里，换窗口/清缓存后找不回。
>
> 专家固定会话：同一 `projectId + mode + targetKind + targetId + presetId` 只对应一个长期 DSH 会话；对应关系存服务端；复用时把绑定更新到最新 revision / runId 并让会话知道上下文已变；提供「新开训练会话」按钮。

### 1.2 B 任务书的目标（`docs/tasks/B-expert-fixed-session.md` 1.3 节，原文）

- 同一 `(projectId, mode, targetKind, targetId, presetId)` 对应**一个**长期训练会话（DSH 会话不删就一直在）。
- 对应关系**存服务端**；localStorage 只作缓存。
- revision / runId 变化时**复用会话并更新绑定**，并让会话明确知道上下文已变化。
- 用户可「新开训练会话」，新会话成为该目标的默认会话；旧会话保留为历史。
- 已删除的 Agent / 工作流不再复用其会话。


### 1.3 B 验收标准 1~14（`docs/tasks/B-expert-fixed-session.md` 第 5 节，原文全文）


> **验收脚本**：DSH 重启后、执行任何会改数据的验收之前，先运行 `node docs/tasks/verify/verify-b.mjs compare`（三种模式 `context` 与改造前一致）；全部验收做完后运行 `node docs/tasks/verify/verify-b.mjs`。两次结果都须无 FAIL，输出摘要贴进完成报告。会话打开 / 复用 / 新开等需要 DSH 宿主窗口的项目仍按下列各条手工验证。

记录每个 sessionId，并在关键步骤附上 `Training_Materials/framework/control/bindings/<sessionId>.json` 与 `target-sessions/*.json` 的相关字段。以下用一个任务 A 新建的 Agent（记为 X）和工作流「新工作流 1」（记为 W）。

1. **首次打开新建**：选中 X，点「打开 Trainer 原生会话」→ 得到 S1，卡片显示「新建会话」；`target-sessions/` 下出现 X 对应记录，`sessionId === S1`。
2. **直接再开复用**：再次点打开 → 仍为 S1，卡片显示「已复用会话」；DSH 会话列表中名为 `Agent Trainer · <X 的 name>` 的会话只有 1 个。
3. **运行后复用**：运行一次包含 X 的工作流或 SMOKE（使 `selectedRunId` 变化）后再打开 X → 仍为 S1；`bindings/S1.json` 的 `selectedRunId` 为新 runId，`bindingRevision` 比第 2 步大。
4. **保存候选后复用**：修改 X 的 instructions 并保存候选（revision 变化）后再打开 → 仍为 S1；`bindings/S1.json` 的 `candidateRevision` 等于 `current.json` 的 `revisionId`；卡片显示 `revision <旧> → <新>`。
5. **上下文更新**：第 4 步中，`contextUpdated` 为 `'message'` 时 S1 会话中可见 `[Trainer 上下文更新]` 消息且**没有**触发模型回复；为 `'binding-only'` 时：`bindings/S1.json` 中出现 `pendingContextChange`；在 S1 中调用 `trainer_context` 返回的 `bindingChanged` 与之相同，随后文件中该字段消失、`bindingRevision` 不变；再调用一次 `bindingChanged` 为 `null`。另验证合并：连续两次「运行 + 重新打开」后再调用 `trainer_context`，`fromRunId` 为第一次之前的值、`toRunId` 为最新值。
6. **清缓存仍复用**：清空 DSH 宿主窗口 localStorage 中所有 `ptc-native-session:` 开头的项，刷新宿主与工作台后再打开 X → 仍为 S1。
7. **新开训练会话**：点「新开训练会话」并确认 → 得到 S2；`target-sessions` 中 X 的记录 `sessionId === S2`；S1 仍在 DSH 会话列表中且可打开查看历史；再次点打开 → S2。
8. **会话被手动删除**：在 DSH 中手动删除 S2，再打开 X → 自动新建 S3，无报错；`target-sessions` 记录更新为 S3。
9. **目标隔离**：打开 W（「在 Trainer 中训练当前工作流」）→ 得到 SW，SW ≠ S3；再打开 X → S3；再打开 W → SW。另选一个 Agent Y → 得到不同于 S3、SW 的会话。
10. **模式隔离与目标解析**：
    - **engineering**：选一个存在于当前激活 release 中的目标，工程模式下打开 → 得到与训练模式不同的会话 SE；再次打开 → 仍为 SE；回到训练模式 → 仍为训练模式原会话。
    - **engineering 间接包含**：选一个未被 release 直接列出、但被 release 中某工作流步骤包含的 Agent，`resolveTarget` 返回 `via:'workflow'`，`target-session` 不为 `null`（新建后）。
    - **只在候选**：本任务新建、未发布的 Agent，在 engineering 下 `resolveTarget` 与 `target-session` 均返回 `null`，且不会复用其训练模式会话。
    - **published**：`context` 在 published 下的返回内容与改造前一致（附改造前后同一请求的返回对比）；published 下打开的会话与 training、engineering 的会话互不复用。
    - 若某模式在页面上不允许打开会话，记录实际提示，并改用直接调用 `target-session` 接口验证。
    - **engineering 新 release**：激活一个新 release 后再打开 SE → 仍为 SE，`pendingContextChange.to.releaseId` 为新 release。
11. **删除后不复用**：把 X 从所有工作流移除后用任务 A 的功能删除 X；`target-session` 查询 X 返回 `null`；新建 Agent Z（新 ID）→ 打开得到全新会话，≠ S3。
12. **旧数据兼容**：在服务端无记录、仅 localStorage 有旧格式 key 的情况下（可用备份的旧 localStorage 值或手工构造），打开对应目标：符合复用条件则复用并补写服务端记录；不符合则新建，无报错。
13. **测试**：插件全部测试通过（与第 0 步基线对比，失败数不增加），新增测试覆盖 2.5 节 5 类场景，并补充：
    - 同一 target 并发两次 `open-native-session`，`sessionFactory` 只被调用 1 次；
    - `pendingContextChange` 的设置、合并、消费清除、并发两次读取（一次有值一次 `null`）、会话自身 `apply-changes` 不设置；
    - 删除条件硬规则：①来源相同、runId 不同 → 保留；②release 相同、runId 不同 → 保留；③来源与 runId 都相同 → 删除；④来源先变后变回、runId 未变 → 删除；
    - 按会话键加锁：同一目标并发打开只调用一次 `sessionFactory`；不同目标并发打开互不等待（用可控延迟的 stub 验证）；锁内抛错后 Map 中的条目被清除，下一次可重试；
    - 死锁防护：在 `serial()` 任务内执行 bind + upsert + 设置 `pendingContextChange` 能正常完成（带超时断言）；
    - `resolveTarget`：training 存在/不存在；engineering 直接列出、经工作流间接包含、只在候选、无激活 release；published 与改造前 `context` 一致；
    - `target-session` 在 `published` / `engineering` 模式下按激活 release 判断存在性。
14. **部署与质量**：
    - DSH 重启后启动日志无第 4 节列出的致命签名；
    - 页面 `<script>` 内容 `node --check` 通过；
    - 工作台与 DSH 宿主控制台无新增 error；
    - 页面中无 `window.confirm`、`alert(`、`prompt(`；
    - `lib/client.js` 已按 2.6 重新构建且包含新逻辑标识；
    - **限定路径检查**：对比开工前的 `git status --porcelain`，本任务新增/修改的路径只能是第 2 节涉及的文件、`lib/client.js`、新增测试与本任务书（完成报告）；提交时只 `git add` 这些路径，不提交开工前已存在的无关改动。

### 1.4 硬停止条件（`docs/tasks/00-PLAN.md` 2.4 节，原文）

**硬停止条件（只有这些情况才停下）**：
1. GitHub 同步失败，或出现无法自动判断的合并冲突（尤其涉及 `agent-trainer-repair-prototype.html` 的轮询修复）。
2. 需要修改任务书明确禁止的范围才能继续（如 A 需要改 `trainer-schema.js` 白名单、B 需要改变 `context` 的返回内容）。
3. DSH 重启后启动失败且回滚脚本也无法恢复（`FAILED: dsh still not up after rollback`）。
4. 会造成数据丢失的操作：删除 DSH 会话、删除 bindings 文件、直接改写磁盘上的 revision / 冻结版本 / release 文件、强推或改写 Git 历史。
5. 同一个问题尝试 3 种不同的解决办法后仍失败。

---

## 2. 当前状态（Claude 已逐项核实，基线 `e630981`）

| 条目 | 状态 | 依据（Claude 核对的磁盘文件或代码） |
|---|---|---|
| 1 首次打开新建 | 已通过 | B3/B4 记录与 target-sessions 文件一致 |
| 2 直接再开复用 | 已通过 | B3 连续 3 次复用，bindingRevision 3/4/5 |
| **3 运行后复用** | **本轮做** | X 的 `bindings/session-ad0b3230…`、`session-e4ab77e8…` 中 `selectedRunId` 均为 `null`，说明 6.6 节写的「通过」没有做 |
| **4 保存候选后复用** | **本轮做** | X 的两个 binding 中 `candidateRevision` 一直是 `revision-36ba7f47…`，同上 |
| 5 上下文更新 | 消费部分已通过；**合并部分本轮做** | 6.2 节已有 `trainer_context` 消费证据；合并规则（两次运行后 fromRunId/toRunId）随第 3 条一起做 |
| **6 清缓存仍复用** | **本轮做** | B4 未执行（Codex 的浏览器工具不能写 localStorage） |
| **7 新开训练会话** | 新开已通过；**再次打开与 S1 保留本轮补** | `e4ab77e8` 的 bindingRevision=1，说明新开后没再打开过 |
| 8 手动删除会话 | 继续标「待用户执行」 | 硬停止条件 4 |
| **9 目标隔离** | **本轮做** | 「新工作流 1」在本轮之前从未在训练模式下打开过（见 4.2 第 4 点） |
| 10 模式隔离 | 已通过（API/静态） | 前轮 verify-b 与 resolver 检查 |
| 11 删除后不复用 | 已通过 | Y=`agent-0e624d84` 删除后 target-session 为 null，Z 得到新会话 |
| **12 旧数据兼容** | **本轮做** | B4 未执行，原因同第 6 条 |
| 13 测试 | 已通过 | 404 passed / 0 failed |
| 14 部署与质量 | 已通过 | Gate A/B/C、verify-b PASS 10 |
| E-1 previousSessionId | 已通过 | `e630981` 中服务端 `bindUnlocked` 已保存该字段；`e4ab77e8` 的 binding 与 X 的 target-session 中都有 `previousSessionId = session-ad0b3230…` |
| E-2 重启后复用 | 已通过 | (a)(b)(c) 均为 `ad0b3230`，binding revision 7/8/10 与文件一致 |

当前关键 ID（执行时以脚本预检读到的为准，下表只作对照）：

| 名称 | 值 |
|---|---|
| X | `agent-2abe705b`（新 Agent 12） |
| S2（X 当前固定会话） | `session-e4ab77e8-f88d-40a3-8a20-f7da6d4e88d1` |
| S1（被替换的旧会话） | `session-ad0b3230-3c3f-450d-a1dd-7de3d30fb04a` |
| W | 工作流「新工作流 1」，workflowId 为 `custom-workflow-1`（**不是** `workflow-T1`） |
| Z | `agent-70e75253`（新 Agent 20），会话 `session-adaca03d-d4b2-44d7-8d32-838cd93f4c70` |
| Y（已删除） | `agent-0e624d84`，会话 `session-42b70531-18a9-4af9-ac32-88043f940daf`（第 12 条用作「别人的会话」） |

---

## 3. 前几轮为什么一直没完成（根因与本轮对策）

| 根因 | 表现 | 本轮对策 |
|---|---|---|
| 宿主条目靠 Codex 的浏览器工具手工点，而该工具只能只读执行页面脚本，且在 compare 有 FAIL 时会被自动审查拦下 | 第 6、12 条连续几轮都「未执行」；B4 中途无法打开宿主标签 | 新增 `verify-b-host.mjs`：由 Node 启动**独立的 Chrome**（临时 profile、仅 127.0.0.1 调试端口），通过 DevTools 协议点按钮、读卡片、读写宿主 localStorage。不再依赖 Codex 的浏览器工具；本轮也**不运行 compare**（不改代码就不需要） |
| 证据由执行方自己汇总，没有机器判定 | 第 3、4、9 条写了「通过」，但磁盘文件显示根本没做 | 每个条目由脚本对照 `bindings/*.json`、`target-sessions/*.json`、`current.json` 自动判 PASS/FAIL，结果写入 `results/verify-b-host.json`，Claude 会逐项复核同一批文件 |
| 长时间执行后目标走样 | 报告 6.3~6.6 互相矛盾；会话被替换却没写进报告 | 本文件第 1 节附目标原文；第 5 节每一步都写明命令、通过标准、失败处理 |
| 部分验收口径在真实 DSH 里做不到或有歧义 | 「S1 在会话列表中可见」：DSH 列表界面本来就隐藏空白会话；「宿主当前会话」只能看到标题「新会话」 | 第 4.2 节由 Claude（验收方）给出明确口径与理由 |
| 测试桩掩盖真实行为（B4 的 previousSessionId） | 单测通过，真实服务端不保存 | 已在 `e630981` 修复；本轮脚本直接读真实文件判定 |

---

## 4. 本轮方案

### 4.1 工具（Claude 已写好并放进仓库工作区，本轮由 Codex 一并提交）

| 文件 | 作用 |
|---|---|
| `docs/tasks/verify/cdp.mjs` | 零依赖的 Chrome DevTools 协议客户端与浏览器启动器（Node ≥ 18 即可，不需要 npm 包） |
| `docs/tasks/verify/verify-b-host.mjs` | 宿主验收驱动：预检 → 启动独立 Chrome → 打开宿主与工作台 → 按步骤 A~F 点击页面并逐项判定 |
| `docs/tasks/verify/README.md` | 已补充新脚本的用法 |

**Claude 的可行性验证**：在云端用真实的 `agent-trainer-repair-prototype.html` 页面、真实的 `client/native-sessions.js`，加上一个按 `trainer-service.js` 语义编写的模拟服务端与模拟宿主，完整跑通 A~F 共 41 项检查（PASS 41 / FAIL 0），并故意制造一次服务端缺陷，确认脚本会准确报 FAIL 和原因。真实环境与模拟环境的差别只在 DSH 宿主本身，相关的不确定点都写进了第 6 节的异常处理。

脚本的边界（写死在脚本里）：
- 不删除任何 DSH 会话或 bindings 文件；唯一的删除动作是步骤 F 对 Z 调用 `forget-target-session`，只删除 `target-sessions/` 下的映射文件，这是任务书 2.1 第 5 条允许的操作，不属于硬停止条件 4。
- 只使用临时浏览器 profile，不碰用户平时的 Chrome；调试端口只监听 127.0.0.1；脚本结束时关闭这个浏览器。
- 会产生的数据变化：X、W、Z 的 binding 更新；两次 SMOKE 运行；X 的 instructions 末尾增加一行「# Candidate saved from white Agent Trainer」（即页面「保存候选」按钮的固定行为）；Z 可能换成新会话（第 12(i) 条的一种合法结果）；新建一个测试 Agent V。都是测试数据，按 A/B 的设计保留。

### 4.2 验收口径（Claude 作为验收方的决定）

1. **第 7 条「S1 仍在 DSH 会话列表中且可打开查看历史」**：DSH 列表界面本来就隐藏空白会话（`@deepseek-ai/dsh-client-runtime` README：「列表界面隐藏 blank 行；store 保留全部行」）。S1 从未发过消息，界面上看不到是正常的。改为判定 S1 **没有被删除**：`bindings/S1.json` 存在且内容未变（A-5）、DSH 会话持久化目录存在（A-6）、`~/.dsh/storages/workspace.json` 仍登记 S1（A-7，查不到只记 WARN）。
2. **E-2「宿主当前会话 ID」**：宿主侧 `openPtcSessionView()` 在 `scope.sessions.list.current !== sessionId` 时会抛出 `OPEN_FAILED`，卡片显示「已请求 DSH 宿主打开原生会话」就证明宿主当前选中的正是该 sessionId。标题显示「新会话」只是空白会话的默认标题，不代表宿主停在别的会话上。Claude 撤回 B4 验收时的第 6 个问题。
3. **第 6 条**：脚本在真实宿主页面里执行删除 `ptc-native-session:` 开头的 localStorage 项，与在 DevTools 里手工删除等价；删除前后的 key 列表都写进证据。
4. **第 9 条**：W 按任务书就是「新工作流 1」，它的 workflowId 是 `custom-workflow-1`（Claude 之前的交接文档误写为 `workflow-T1`，已更正）。它此前没有固定会话，所以第一次打开会**新建** SW，这是正常的（B-3 记 WARN，不阻断）；第二次打开必须复用 SW。
5. **第 12 条**分两部分：
   - (i) Z 的服务端记录被 forget、宿主刷新后只剩旧格式 key 指向 Z 自己的旧会话：按任务书 2.2 第 3 条，会话必须已被宿主加载（`scope.sessions.binding(id) !== undefined`）才复用。刷新后的宿主通常还没加载它，所以**「复用旧会话」和「新建会话」两种结果都合格**，前提是无报错、服务端补写的记录与结果一致、旧 binding 文件仍在；脚本会记录走的是哪个分支。
   - (ii) 新 Agent V、服务端无记录、旧格式 key 指向别人的会话（Y 的 `session-42b70531…`）：**必须新建**，且 Y 的 binding 文件 sha256 与修改时间都不变。
6. **第 5 条**：消费与清除前轮已通过，本轮只验合并规则：两次「运行 + 重新打开」后，`pendingContextChange.fromRunId` 保留最早值、`toRunId` 为最新 runId（C-6）。

### 4.3 步骤总览

| 步骤 | 覆盖条目 | 主要动作 | 预计耗时 |
|---|---|---|---|
| A | 7 补做、E-2 | 全新浏览器中打开 X → 应为 S2；核对 S1 未被删除 | 1~2 分钟 |
| B | 9 | 打开 W → X → W，再打开 Z | 2~3 分钟 |
| C | 3、5 合并 | 跑 SMOKE → 打开 X；再跑 SMOKE → 打开 X | 3~5 分钟（每次运行约 1 分钟） |
| D | 4 | 打开 X → 页面「保存候选」→ 打开 X | 1~2 分钟 |
| E | 6 | 打开 X → 清缓存 → 刷新宿主与工作台 → 打开 X | 1~2 分钟 |
| F | 12 | Z 的旧格式 key；新建 V 并测「别人的会话」 | 2~3 分钟 |

**顺序固定为 A → B → C → D → E → F**，每一步单独执行一条命令（避免单条命令超时）。F 必须最后做，因为它会改变 Z 的映射。

---

## 5. 执行步骤

每一步都写明：命令 → 通过标准 → 失败时怎么办（对应第 6 节的编号）。**所有命令在仓库根目录 `D:\Newtest\DSH\ATE-Coding-Flow` 下执行。**如果默认沙箱启动浏览器报 `spawn EPERM`，改用提升权限的环境执行同一条命令（B4 中 `node --check` 也遇到过同样情况）。

### 步骤 0：准备（不改任何数据）

1. `git fetch github --prune`；确认 `git rev-parse HEAD`、`git rev-parse github/master`、`git rev-parse github/main` 三者相同（应为 `e630981` 或之后由用户推送的提交）。不一致 → 硬停止条件 1。
2. `git status --porcelain > .tmp-b5-baseline-status.txt`（记录开工前的无关改动，不提交、不还原）。
3. 确认以下文件存在（Claude 已放好，属于未跟踪文件）：`docs/tasks/B5-host-acceptance.md`（本文件）、`docs/tasks/verify/cdp.mjs`、`docs/tasks/verify/verify-b-host.mjs`。
4. `node --check docs/tasks/verify/cdp.mjs`、`node --check docs/tasks/verify/verify-b-host.mjs` 均无输出。
5. 浏览器 `http://127.0.0.1:3080/` 返回 200（脚本预检也会查）。DSH 没有运行 → 按 B 任务书第 4 节重启（已授权），Gate A/B/C 必须通过。

**通过标准**：以上 5 项全部满足。**本轮不需要重启 DSH，也不运行 `verify-b.mjs compare`**（不改代码就不需要；compare 已知的 2 个 FAIL 是前轮候选数据漂移，Claude 已核对可接受）。

### 步骤 1：A（第 7 条补做 + E-2）

```
node docs/tasks/verify/verify-b-host.mjs --steps A
```

**通过标准**：输出末行 `FAIL 0`。必须看到：`P-0`、`P-1`、`A-1`~`A-6`、`A-8` 为 PASS（`A-7` 允许 WARN）。`A-2` 的 sessionId 必须等于预检打印的 S2。
**失败处理**：`P-*` 失败 → 6.1 / 6.2 / 6.3；`A-1`/`A-2` 失败 → 6.4；`A-5`/`A-6` 失败 → 硬停止（S1 被删除或改写属于数据丢失，立即停止并报告，不要修复）。

### 步骤 2：B（第 9 条）

```
node docs/tasks/verify/verify-b-host.mjs --steps B
```

**通过标准**：`FAIL 0`；`B-1`、`B-2`、`B-4`~`B-7` 为 PASS；`B-3` 为 WARN（W 首次打开新建）或 PASS 均可；`B-8` 只在 W 预检已有会话时出现，出现就必须 PASS。
**失败处理**：6.4；`B-6` 失败（Z 与 S2/SW 相同）→ 代码缺陷，进入第 7 节修复流程。

### 步骤 3：C（第 3 条 + 第 5 条合并）

```
node docs/tasks/verify/verify-b-host.mjs --steps C
```

**通过标准**：`FAIL 0`；`C-1`~`C-6` 为 PASS；证据中 `run.C-run-1` 与 `run.C-run-2` 的 `apiStatus` 都是 `completed`。
**失败处理**：运行未完成 → 6.5；`C-2`/`C-5` 失败（selectedRunId 未更新）或 `C-6` 失败（合并规则不对）→ 代码缺陷，进入第 7 节。

### 步骤 4：D（第 4 条）

```
node docs/tasks/verify/verify-b-host.mjs --steps D
```

**通过标准**：`FAIL 0`；`D-1`~`D-4` 为 PASS；证据 `D.ids` 中 `revB === currentJson`。
**失败处理**：「保存候选后 30 秒内 revision 没有变化」→ 6.7；`D-3`/`D-4` 失败 → 代码缺陷，进入第 7 节。

### 步骤 5：E（第 6 条）

```
node docs/tasks/verify/verify-b-host.mjs --steps E
```

**通过标准**：`FAIL 0`；`E-1`~`E-4` 为 PASS；证据 `E.storage` 中 `before` 至少 1 项，`cleared` 与 `afterReload` 为空数组，`after` 中有 X 的新格式 key，值为 S2。
**失败处理**：`E-1` 失败 → 6.8；`E-3` 失败（清缓存后没有复用 S2）→ 代码缺陷，进入第 7 节。

### 步骤 6：F（第 12 条）

```
node docs/tasks/verify/verify-b-host.mjs --steps F
```

**通过标准**：`FAIL 0`；`F-1`~`F-4`、`F-6`~`F-9` 为 PASS；`F-5` 只在 (i) 走「新建」分支时出现，出现就必须 PASS。在报告中写明 (i) 走的是哪个分支（证据 `F.i.branch`）。
**失败处理**：`F-2` 出现 `inconsistent`，或 `F-7` 复用了别人的会话 → 代码缺陷，进入第 7 节；`F-9` 失败（别人的 binding 被改写）→ 硬停止条件 4，立即停止并报告。

### 步骤 7：只读复核

```
node docs/tasks/verify/verify-b.mjs
```

**通过标准**：`PASS 10 / FAIL 0`（`B-file-1` 的记录数会比 B4 多，`B-file-2` 显示有未消费的 pendingContextChange 是正常的，只要不是 FAIL）。
**失败处理**：`B-file-1` 失败（sessionId 被两个目标共用、绑定缺失）→ 代码缺陷，进入第 7 节。

### 步骤 8：写 6.7 节报告

用 Node 按 UTF-8 追加到 `docs/tasks/B-expert-fixed-session.md` 末尾（**不要用 PowerShell 的 `Add-Content` / `Out-File`**），模板见第 8 节。写完执行：

```
node -e "const b=require('fs').readFileSync('docs/tasks/B-expert-fixed-session.md');const n=b.filter(x=>x===0).length;new TextDecoder('utf-8',{fatal:true}).decode(b);console.log('NUL',n)"
```

**通过标准**：输出 `NUL 0`，且没有抛出解码错误。

### 步骤 9：提交与推送

1. 只 `git add` 以下路径：`docs/tasks/B5-host-acceptance.md`、`docs/tasks/verify/cdp.mjs`、`docs/tasks/verify/verify-b-host.mjs`、`docs/tasks/verify/README.md`、`docs/tasks/B-expert-fixed-session.md`。如果走过第 7 节修复流程，再加上实际修改的代码、测试和重建后的 `plugins/dsh-ptc-control-plane/lib/client.js`。**不要 add `docs/tasks/verify/results/`**（运行产物）。
2. `git diff --cached --stat`，确认没有其他路径。
3. 提交信息：`[B4] 自动化完成宿主验收第 3/4/6/7/9/12 条`（走过修复流程就在后面加上修复内容）。
4. `git push github HEAD:master` 与 `git push github HEAD:main`（不加 `--force`）。
5. `git fetch github` 后确认 `HEAD`、`github/master`、`github/main` 三者相同，`git rev-list --left-right --count HEAD...github/main` 为 `0	0`。

---

## 6. 异常处理

总原则：**同一个问题最多换 3 种办法**（第 3 种仍失败就是硬停止条件 5）；不得为了让脚本通过而修改脚本中的判定条件（`expect(...)` 里的比较），也不得手工改写 bindings、target-sessions、revision 文件。

| 编号 | 现象 | 处理 |
|---|---|---|
| 6.1 | `P-X`：找不到浏览器 / `spawn EPERM` / 30 秒连不上调试端口 / 端口已被占用 | ① 提升权限的环境重跑；② 加 `--chrome "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"` 换 Edge；③ 加 `--port 9444` 换端口。三种都失败 → 停止，报告完整输出 |
| 6.2 | `P-X`：「DSH 宿主页面出现「打开 ATE Trainer」入口」等待超时 | 看 `results/host-shots/<时间>/` 下的宿主截图和 `results/verify-b-host.json` 中 `latest.console.host`。① 确认 DSH 正在运行（`http://127.0.0.1:3080/` 能打开）后重跑；② 换 Edge 重跑；③ 按 B 任务书第 4 节重启 DSH（Gate A/B/C 通过）后重跑。仍失败 → 停止，附截图与 console |
| 6.3 | `P-X`：「target-session(X) 为 null」或预检找不到 X / 「新工作流 1」 | **不要新建来替代。**检查 `Training_Materials/framework/control/target-sessions/96e45c352d33fbbd693605f58d2881d6.json` 与 `bindings/session-e4ab77e8-….json` 是否存在，用 `/api/ptc-control/trainer/context` 看 X 与工作流是否还在候选中。文件或候选被意外删除属于数据丢失 → 停止并报告 |
| 6.4 | 某个 `*-open-*` 卡片显示打开失败（`NATIVE_SESSION_NOT_LISTED`、`HOST_UNAVAILABLE`、`TARGET_MISMATCH`、`OPEN_FAILED` 等） | ① 原样重跑该步骤一次（脚本可以重复执行，每次重新预检）；② 若仍失败，查看证据中该次打开的 `body`、`latest.console.host`、截图，以及 DSH 日志 `C:\Users\nvt10241\.dsh\dsh-web-restart.log`，判断是环境问题还是代码问题；③ 代码问题 → 第 7 节修复流程。只出现在 W 或 Z 上、X 正常时，也按代码问题处理（同一套复用逻辑） |
| 6.5 | 步骤 C：SMOKE 运行失败 / 停止 / 15 分钟未结束 | ① 用 `/api/ptc-control/trainer/runs`（body `{"projectId":"agent-trainer","runId":"<runId>"}`）看失败原因；② 运行 `node docs/tasks/verify/verify-a.mjs --smoke` 判断 SMOKE 本身是否正常；③ 环境或模型问题（与本任务代码无关）→ 停止并报告；SMOKE 本身正常则重跑步骤 C |
| 6.6 | `B-3` 为 WARN | 不阻断。报告中写明 W 预检时的会话 ID（若有）与证据 `B.oldSW.dshSessionDir`，由 Claude 判断 |
| 6.7 | 步骤 D：「保存候选后 30 秒内 revision 没有变化」或「候选中没有 agents/<X>/instructions.md」 | 看 D 步骤的工作台截图里的 toast 文字。① 用 `/api/ptc-control/trainer/assets`（training 模式、当前 revision）确认 X 的 instructions 路径；② 若 X 的 `agent.json` 的 `instructionsRef` 不是 `agents/<X>/instructions.md`，属于测试数据问题，换一个由页面新建的 Agent 作为 X：`--x <agentId>`，并在报告中说明；③ apply-changes 报错 → 记录错误码，按代码问题进入第 7 节 |
| 6.8 | 步骤 E：`E-1` 清理前就没有 `ptc-native-session:` 缓存项 | 说明宿主没有写缓存（`rememberSessionId`）。先确认 E 步骤开头那次打开 X 是成功的；成功却没写缓存 → 代码问题，进入第 7 节 |
| 6.9 | 脚本自身问题（不是产品问题），例如页面元素选择器变了、等待时间不够、路径不同 | 允许做**机械性修正**（选择器、超时、路径、参数），禁止修改判定条件。修改的 diff 原样写进 6.7 节报告的「偏离」中 |
| 6.10 | Codex 的自动审查拦截启动浏览器 | 用户已授权：本轮可以用 `verify-b-host.mjs` 启动独立的 Chrome/Edge（临时 profile、仅 127.0.0.1 调试端口）。仍被拦截 → 停止，报告被拦截的提示原文，由用户处理 |

---

## 7. 修复流程（只有第 5、6 节判定为「代码缺陷」时才进入）

1. **定位**：根据失败条目找到对应逻辑——复用与新开：`plugins/dsh-ptc-control-plane/client/native-sessions.js` 的 `openTrainerNativeSession`；绑定、pendingContextChange 与 target-session：`plugins/dsh-ptc-control-plane/lib/trainer-service.js` 的 `bindUnlocked`、`upsertTargetSessionUnlocked`、`openNativeSession`；冷宿主恢复会话：`lib/trainer-host.js` 的 `resumePersistedTrainerAgent`。在报告中写清根因（代码位置 + 触发条件）。
2. **修改**：只改上述文件，遵守 B 任务书第 3 节「不要做」。先备份为同目录 `.bak-20261002-taskB5`（不提交）。
3. **补测试**：在 `plugins/dsh-ptc-control-plane/test/` 中补能复现该缺陷的测试。测试桩必须模拟真实服务端行为，**不能把请求参数原样回传当结果**（B4 的 previousSessionId 问题就是这样被掩盖的）。
4. **构建与测试**：`node plugins/dsh-ptc-control-plane/scripts/build-client.mjs`；在 `plugins/dsh-ptc-control-plane` 下执行 `node test/all.test.mjs`，要求通过数 ≥ 404、失败 0。
5. **部署**：用 `/api/ptc-control/trainer/runs` 确认没有进行中的 framework run → `& "C:\Users\nvt10241\.dsh\rules\dsh-plugin-restart.ps1" -Profile web -PluginDir .\plugins\dsh-ptc-control-plane`，Gate A/B/C 必须 exit 0，启动日志无 `plugin tree failed to load`、`ERR_MODULE_NOT_FOUND`、`ERR_PACKAGE_PATH_NOT_EXPORTED`、`input hint must not be empty`。
6. **重新验收**：先重跑失败的步骤，再按 A → F 顺序把所有步骤重跑一遍（改了代码，前面的结果就不能沿用），最后执行步骤 7。
7. 同一缺陷修了 3 次仍失败 → 硬停止条件 5，停止并报告。

---

## 8. 6.7 节报告模板（照此填写，每一项都填脚本输出的实际值）

```
## 6.7 第 4 轮（B4）宿主补验（Codex，按 docs/tasks/B5-host-acceptance.md 执行）

> 6.6 节中第 3、4、9 条的「通过」证据不足，以本节为准。

- 基线：HEAD / github/master / github/main = <hash>；开工前 git status 已保存到 .tmp-b5-baseline-status.txt。
- 工具：docs/tasks/verify/verify-b-host.mjs（独立 Chrome/Edge：<浏览器版本>，nativeHost=<ID>）；证据 docs/tasks/verify/results/verify-b-host.json，截图 docs/tasks/verify/results/host-shots/<时间>/。
- 各步骤结果（逐行粘贴脚本的 PASS/FAIL/WARN 行）：
  - A：…
  - B：…
  - C：…
  - D：…
  - E：…
  - F：…
- 关键值：S2=<…>；S1=<…>（bindings 未改写、持久化目录 <路径>）；SW=<…>；SZ=<…>；R1=<…>；R2=<…>；revA=<…> → revB=<…>（current.json=<…>）；第 12(i) 条分支=<reuse/new>，结果会话=<…>；V=<…>，V 的会话=<…>，F=<…>（binding 未变）。
- 第 5 条合并：pendingContextChange.fromRunId=<…>，toRunId=<…>。
- 第 8 条：待用户手工执行（硬停止条件 4）。
- verify-b.mjs：PASS <n> / FAIL <n> / WARN <n> / SKIP <n>。
- 偏离：<没有就写「无」；6.9 的脚本机械性修改要贴 diff；走过第 7 节修复流程要写根因、修改、测试名、测试结果、Gate 结果>。
- 数据：未删除任何 DSH 会话或 bindings 文件；forget-target-session 只删除了 Z 的映射文件；新增测试 Agent V=<…> 保留。
- 提交 / 推送：<hash>；github/master=<hash>；github/main=<hash>；0/0。
```

---

## 9. Claude 如何复核（供 Codex 了解，不需要执行）

Claude 收到「B5 做完了」后，会读取 `results/verify-b-host.json`、截图，以及报告中每个 sessionId 对应的 `bindings/*.json`、`target-sessions/*.json`、`current.json`，逐项核对字段值与修改时间是否和脚本输出一致；核对 S1、Y 的 binding 文件 sha256 未变；核对 Git 三个 ref 与提交范围。任何一处不一致都判「不通过」。
