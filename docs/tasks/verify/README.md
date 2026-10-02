# 验收脚本与清单（任务 A / B）

编写：Claude（2026-10-02）。目的：把可以自动化的验收项写成脚本，Codex 自测和 Claude 验收共用同一套检查；脚本覆盖不了的界面交互，列在本文「手工清单」中，由 Claude 在浏览器中完成。

- 运行环境：Node ≥ 18（使用内置 `fetch`），**在仓库根目录** `D:\Newtest\DSH\ATE-Coding-Flow` 运行。
- 环境变量（可选）：`TRAINER_BASE`（默认 `http://127.0.0.1:3080`）、`TRAINER_ROOT`（默认当前目录）、`SMOKE_WORKFLOW`（默认 `新工作流 1`）。
- 每次运行的结果写入 `docs/tasks/verify/results/*.json`。**`results/` 不提交到 Git**，运行结果的摘要贴到对应任务书的「完成报告」中作为证据。
- 退出码：有任一 FAIL 时为 1。

| 文件 | 用途 |
|---|---|
| `lib.mjs` | 公共函数：调用 Trainer API、台账结构校验、目录遍历、结果记录 |
| `verify-a.mjs` | 任务 A 验收 |
| `verify-b.mjs` | 任务 B 验收（含 context 改造前后对比） |

---

## 任务 A

```
node docs/tasks/verify/verify-a.mjs                    # 只读检查（安全，可随时运行）
node docs/tasks/verify/verify-a.mjs --mutate --smoke   # 完整验收
```

| 编号 | 检查内容 | 对应任务书 |
|---|---|---|
| A-page-1~5 | 页面脚本语法；T0 轮询修复仍在；无 `confirm/alert/prompt`；已去除 `agent-T1~T3` / `custom-agent-N` 分配逻辑；存在 `agentDeletionPlan` | 2.1、2.4、2.5、验收 12 |
| A-reg-1~4 | 台账存在且结构合法；当前全部 Agent 已登记；`agentId` 与目录一致、`name` 非空 | 2.1、验收 1、2 |
| A-scan-1 | **独立复扫**仓库根目录下 4 个来源，台账必须覆盖全部历史 Agent ID（与 Codex 的初始化脚本交叉核对，两边实现互相独立） | 2.1、验收 2a |
| A-srv-1~7（`--mutate`） | 绕过页面直接调用 `apply-changes`：复用 ID → `REUSED`；不登记 → `UNREGISTERED`；两个只登记一个 → `UNREGISTERED`；缩小 / 删除台账 → `LEDGER_SHRINK`；损坏台账 → `LEDGER_INVALID`。每项都核对 revision 未变化 | 2.7、验收 2c |
| A-smoke-1（`--smoke`） | 跑一次 SMOKE_ONLY，4 步全部 completed（约 1~2 分钟） | 验收 11 |

关于 `--mutate`：服务端实现正确时，所有请求都会被拒绝，**不会写入任何数据**。如果某项意外提交成功，脚本会记为 FAIL 并立即回滚它写入的测试数据；`A-srv-1` 需要台账中存在「已登记但当前不存在」的 ID，没有时会 SKIP（先在页面新建并删除一个 Agent 后再运行）。

---

## 任务 B

```
node docs/tasks/verify/verify-b.mjs snapshot   # ① B 开工前、改任何代码之前
node docs/tasks/verify/verify-b.mjs compare    # ② B 部署重启后、执行任何会改数据的测试之前
node docs/tasks/verify/verify-b.mjs            # ③ B 完成、全部验收操作做完之后
```

**① 与 ② 的时机很重要**：对比的是 training / engineering / published 三种模式下 `context` 的完整返回。中间如果保存过候选、发布过版本，返回内容本来就会变，对比就失去意义。所以 ① 必须在改代码前做，② 必须在重启后、动数据之前做。

| 编号 | 检查内容 | 对应任务书 |
|---|---|---|
| B-ctx（compare） | 三种模式的 `context` 返回与改造前完全一致 | 2.0、验收 10 |
| B-build-1~4 | `lib/client.js` 比源文件新且含新逻辑；会话键与 `matchesTarget` 不含 revision / runId；路由白名单有两个新 operation；`resolveTarget` 存在并至少被 4 处调用 | 2.0、2.2、2.6、验收 14 |
| B-api-1~3 | `target-session` 接口可用；training 下每个目标的记录字段正确、`lastResolved.source === 'candidate'`；只在候选中的 Agent 在 engineering 下返回 `null` | 2.0、2.1、验收 10 |
| B-file-1 | `target-sessions/*.json`：文件名等于键的哈希、必需字段齐全、绑定文件存在、同一个 sessionId 不被两个目标共用 | 2.1、验收 1、7、8 |
| B-file-2 | 所有绑定中的 `pendingContextChange`：结构正确；**不存在「来源和 runId 都相同却未删除」的情况**（删除硬规则） | 2.3 |
| B-file-3 | 页面无 `confirm/alert/prompt` | 验收 14 |

---

## 手工清单（Claude 在浏览器中验收）

脚本无法驱动 DSH 宿主窗口和页面交互，以下项目由 Claude 在内置浏览器中检查，结果记入验收结论。

### 验收 A

1. 训练模式下 Agent 列表有删除按钮；切到发布 / 工程模式后没有。
2. 新建 Agent：ID 形如 `agent-xxxxxxxx`，列表显示「新 Agent N」，悬停可见 ID。
3. 删除未被引用的 Agent：确认层列出 4 个文件；删除后列表消失；toast 文案正确。
4. 删除 `agent-T3`（被「新工作流 1」第 3 步使用）：被阻止，提示含工作流名与步骤序号；网络请求中没有 `apply-changes`。
5. 确认层：Esc、点遮罩、取消都不提交；快速连点两次「确认删除」只发出 1 次请求。
6. 运行 SMOKE 期间点删除：被阻止。
7. 运行 `verify-a.mjs --mutate --smoke`，结果无 FAIL。

### 验收 B

1. 确认 Codex 已提供 ① snapshot 与 ② compare 的结果，且 compare 无 FAIL。
2. 同一 Agent：打开会话 → 跑一次 SMOKE → 保存一次候选 → 再打开，三次是同一个 sessionId；卡片显示「已复用会话」与 revision 变化。
3. 「新开训练会话」得到新 sessionId；旧会话仍在 DSH 会话列表中。
4. 删除一个有过会话的 Agent，再新建一个 Agent：新 Agent 得到全新会话。
5. 运行 `verify-b.mjs`，结果无 FAIL。

---

## 任务 B 宿主窗口验收（`verify-b-host.mjs`，2026-10-02 新增）

脚本 `verify-b.mjs` 不能驱动 DSH 宿主窗口；宿主条目由 `verify-b-host.mjs` 自动完成。它用 `cdp.mjs`（零依赖的 Chrome DevTools 协议客户端）启动一个**独立的 Chrome / Edge**（临时 profile，调试端口只监听 127.0.0.1，结束时关闭），打开真实宿主 `http://127.0.0.1:3080/` 与工作台 `/agent-trainer?nativeHost=<宿主ID>`，像用户一样点击按钮，再对照 `bindings/*.json`、`target-sessions/*.json`、`current.json` 逐项判定。执行计划见 `docs/tasks/B5-host-acceptance.md`。

```
node docs/tasks/verify/verify-b-host.mjs --steps A   # 依次执行 A、B、C、D、E、F，每次一个步骤
```

| 步骤 | 对应 B 验收条目 | 检查编号 |
|---|---|---|
| A | 7（新开后再次打开仍为 S2、S1 未被删除）、E-2 | A-1 ~ A-8 |
| B | 9（W → X → W 交替；另一 Agent 得到不同会话） | B-1 ~ B-8 |
| C | 3（运行后复用、selectedRunId 更新）、5（合并规则） | C-1 ~ C-6 |
| D | 4（保存候选后复用、candidateRevision 更新、卡片显示 revision 旧 → 新） | D-1 ~ D-4 |
| E | 6（清空 `ptc-native-session:` 缓存并刷新后仍复用） | E-1 ~ E-4 |
| F | 12（旧格式 localStorage key 的两种情况） | F-1 ~ F-9 |

- 参数：`--chrome <浏览器路径>`、`--port <调试端口，默认 9333>`、`--headless`、`--keep-open`、`--x`、`--workflow`、`--z`、`--foreign-session`；环境变量 `CHROME_PATH`、`DSH_HOME`（默认 `~/.dsh`）。
- 结果：`results/verify-b-host.json`（每次打开的卡片文字、sessionId、binding 与 target-session 关键字段、宿主 console 错误）、`results/verify-b-host-<步骤>.json`、截图 `results/host-shots/<时间>/`。均不提交。
- 不删除任何 DSH 会话或 bindings 文件；唯一的删除动作是步骤 F 对 Z 调用 `forget-target-session`（只删除映射文件）。
