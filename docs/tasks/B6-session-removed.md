# B6：完成 B 验收第 8 条（固定会话被删除后自动新建）

- 仓库：`D:\Newtest\DSH\ATE-Coding-Flow`（下文路径均相对此目录）
- 编写：Claude（2026-10-03）。执行：Codex（`/goal` 模式），代用户操作。验收：Claude
- 本文件是本轮**唯一的执行依据**。执行中忘了要做什么，就回到第 1 节（目标）和第 4 节（步骤）。

---

## 0. 一句话目标

部署 Claude 已写好的一处服务端修复（`lib/trainer-host.js`），然后用验收驱动 `verify-b-host.mjs --steps G` 在真实 DSH 宿主中完成 B 验收第 8 条：Z 的固定会话「被删除」后再打开 Z，必须自动新建会话、无报错、记录更新为新会话。最后写报告、提交并推送。

---

## 1. 目标回顾（原文）

**B 任务书第 5 节第 8 条**（`docs/tasks/B-expert-fixed-session.md`）：

> 8. **会话被手动删除**：在 DSH 中手动删除 S2，再打开 X → 自动新建 S3，无报错；`target-sessions` 记录更新为 S3。

**B 任务书 2.1 第 7 条**：

> **手动删除会话的识别**：客户端 `scope.sessions.binding(sessionId) === undefined`，或服务端 `sessionVerifier` 返回假，任一成立即视为失效 → 删除 target-session 记录 → 新建。旧 bindings 文件保留。

**00-PLAN 2.4 硬停止条件**（原文）：

> 1. GitHub 同步失败，或出现无法自动判断的合并冲突（尤其涉及 `agent-trainer-repair-prototype.html` 的轮询修复）。
> 2. 需要修改任务书明确禁止的范围才能继续（如 A 需要改 `trainer-schema.js` 白名单、B 需要改变 `context` 的返回内容）。
> 3. DSH 重启后启动失败且回滚脚本也无法恢复（`FAILED: dsh still not up after rollback`）。
> 4. 会造成数据丢失的操作：删除 DSH 会话、删除 bindings 文件、直接改写磁盘上的 revision / 冻结版本 / release 文件、强推或改写 Git 历史。
> 5. 同一个问题尝试 3 种不同的解决办法后仍失败。

**本轮对第 4 条的特别授权（用户在对话中明确要求 Codex 代为完成第 8 条）**：只允许验收驱动把 **Z 当前固定会话** 的持久化目录**临时移动**到 `C:\Users\nvt10241\.dsh\b8-removed-sessions\<时间>\`，并在同一次运行结束时自动移回。**不得删除**任何会话目录或 bindings 文件；不得移动其他会话。

---

## 2. 为什么之前没完成、以及 Claude 已经做了什么

1. **DSH 没有「删除会话」功能**。DSH 的说明（`@deepseek-ai/dsh-workspace` README「已知限制」）写明会话删除尚未提供；侧栏只有「归档」和「移除工作区」，两者都保留会话。所以第 8 条只能用「让会话的持久化记录消失」来模拟，这正是驱动步骤 G 做的事（移出目录 → 验证 → 移回）。用户之前删除的是 Agent `custom-agent-8`（任务 A 的功能），与第 8 条无关。
2. **Claude 读代码发现一个会让第 8 条失败的缺陷**：会话记录消失后，DSH 的 `SessionPersistence.inspect()` 会抛出 `session "<id>" not found`（`dsh-session-persistence/lib/index.js` 的 `inspect` / `prepareCore`）。`lib/trainer-host.js` 的 `sessionVerifier` 与 `resumePersistedTrainerAgent` 没有接住这个异常，于是 `target-session`、`bind-session`、`open-native-session` 都返回 `trainer_operation_failed`，页面卡片显示「未能打开原生会话 session "…" not found」，不会自动新建。
3. **Claude 已写好修复与回归测试，并放进仓库工作区（未提交）**：
   - `plugins/dsh-ptc-control-plane/lib/trainer-host.js`：新增导出函数 `isMissingPersistedSession` 与 `inspectPersistedSession`（只把「该会话 not found」当作「会话不存在」，其他错误照常抛出）；`resumePersistedTrainerAgent` 和 `sessionVerifier` 改用它。改动只有这 3 处，完整 diff 见附录 A。
   - `plugins/dsh-ptc-control-plane/test/trainer-missing-session.test.mjs`（新增，2 个测试）与 `test/all.test.mjs`（末尾加一行 import）。
   - `docs/tasks/verify/verify-b-host.mjs`：新增步骤 G（检查 G-1 ~ G-7）。
   - `docs/tasks/B-expert-fixed-session.md`：Claude 上一轮的整理（第二个 6.7 改为 6.8、修正路径、新增 6.9 验收结论）也还没提交，本轮一并提交。
4. **Claude 的验证**：
   - 新测试在云端用你仓库里的真实 `trainer-service.js`、`trainer-project.js` 等运行：修复后 2/2 通过；把验证逻辑换回旧写法时，第 2 个测试准确失败（`trainer_operation_failed: session "session-1" not found`），说明测试能抓住这个缺陷。
   - 步骤 G 在模拟宿主上跑了两遍：模拟修复后的服务端 PASS 9 / FAIL 0；模拟未修复的服务端，G-2、G-3、G-4、G-6 准确报 FAIL，且两种情况下旧会话目录都被移回原处。

---

## 3. 预期结果（判定标准）

| 检查 | 含义 | 期望 |
|---|---|---|
| G-1 | Z 的会话目录已移出 `~/.dsh/sessions` | PASS |
| G-2 | 移除后查询 `target-session(Z)` | 接口正常返回 `null`，不报错 |
| G-3 | 再打开 Z | 卡片成功、显示「新建会话」、新 sessionId ≠ 旧会话 |
| G-4 | `target-sessions` 中 Z 的记录 | 更新为新 sessionId |
| G-5 | 旧会话的 bindings 文件 | 仍在且内容未变 |
| G-6 | 再次打开 Z | 复用新会话 |
| G-7 | 旧会话目录 | 已移回原处（不丢数据） |

当前 Z = `agent-70e75253`（新 Agent 20），固定会话预计为 `session-2b0476aa-038e-4ce1-8c68-5ba61525b744`；以脚本预检读到的为准。

---

## 4. 执行步骤

所有命令在仓库根目录执行。默认沙箱启动浏览器或写 `.git` 报 `EPERM` 时，用提升权限的环境重跑同一命令。

### 步骤 0：准备
1. `git fetch github --prune`；`HEAD`、`github/master`、`github/main` 三者相同（应为 `fcb08f1` 或之后）。不一致 → 硬停止条件 1。
2. `git status --porcelain > .tmp-b6-baseline-status.txt`（不提交）。确认以下路径处于「已修改或新增」状态：`docs/tasks/B6-session-removed.md`、`docs/tasks/B-expert-fixed-session.md`、`docs/tasks/verify/verify-b-host.mjs`、`plugins/dsh-ptc-control-plane/lib/trainer-host.js`、`plugins/dsh-ptc-control-plane/test/trainer-missing-session.test.mjs`、`plugins/dsh-ptc-control-plane/test/all.test.mjs`。
3. `git diff -- plugins/dsh-ptc-control-plane/lib/trainer-host.js` 与附录 A 一致（只有 3 处改动）。不一致 → 停止并报告（说明工作区被别人改过）。
4. `node --check docs/tasks/verify/verify-b-host.mjs`、`node --check plugins/dsh-ptc-control-plane/lib/trainer-host.js` 无输出。

### 步骤 1：测试
在 `plugins/dsh-ptc-control-plane` 下执行：
```
node --test test/trainer-missing-session.test.mjs
node test/all.test.mjs
```
**通过标准**：第一条 2 pass / 0 fail；全量 ≥ 406 pass、0 fail（原 404 + 新增 2）。
**失败处理**：见 5.1。

### 步骤 2：部署
1. 用 `/api/ptc-control/trainer/runs`（POST，body `{"projectId":"agent-trainer"}`）确认没有进行中的 framework run；有则等待（最多 15 分钟）。
2. `& "C:\Users\nvt10241\.dsh\rules\dsh-plugin-restart.ps1" -Profile web -PluginDir .\plugins\dsh-ptc-control-plane`
**通过标准**：Gate A/B/C 全部 exit 0；端口 3080 返回 200；启动日志无 `plugin tree failed to load`、`ERR_MODULE_NOT_FOUND`、`ERR_PACKAGE_PATH_NOT_EXPORTED`、`input hint must not be empty`。
**注意**：重启后到步骤 3 之间，**不要在任何浏览器里打开 Z**（否则 Z 的旧会话会被加载进 DSH 内存，G-3 会误判为复用）。本轮不改客户端代码，不需要重建 `lib/client.js`，也不运行 `verify-b.mjs compare`。

### 步骤 3：第 8 条验收
```
node docs/tasks/verify/verify-b-host.mjs --steps G
```
**通过标准**：输出末行 `FAIL 0`，G-1 ~ G-7 全部 PASS。证据在 `docs/tasks/verify/results/verify-b-host.json` 的 `byStep.G`（`G.move`、`G.targetSessionAfterMove`、`G.ids`、`G.restore`）。
**失败处理**：见 5.2 ~ 5.5。

### 步骤 4：只读复核
```
node docs/tasks/verify/verify-b.mjs
```
**通过标准**：PASS 10 / FAIL 0。

### 步骤 5：写报告
用 Node 按 UTF-8 在 `docs/tasks/B-expert-fixed-session.md` 末尾追加「6.10」节（模板见第 6 节），不要用 PowerShell 的 `Add-Content` / `Out-File`。写完执行：
```
node -e "const b=require('fs').readFileSync('docs/tasks/B-expert-fixed-session.md');new TextDecoder('utf-8',{fatal:true}).decode(b);console.log('NUL',b.filter(x=>x===0).length)"
```
**通过标准**：`NUL 0`，无解码错误。

### 步骤 6：提交与推送
1. 只 `git add`：`docs/tasks/B6-session-removed.md`、`docs/tasks/B-expert-fixed-session.md`、`docs/tasks/verify/verify-b-host.mjs`、`plugins/dsh-ptc-control-plane/lib/trainer-host.js`、`plugins/dsh-ptc-control-plane/test/trainer-missing-session.test.mjs`、`plugins/dsh-ptc-control-plane/test/all.test.mjs`。不要 add `docs/tasks/verify/results/`。
2. `git diff --cached --stat` 只含以上 6 个路径。
3. 提交信息：`[B4] 第 8 条：固定会话被删除后自动新建（修复 DSH 会话缺失时报错）`
4. `git push github HEAD:master`、`git push github HEAD:main`（不加 `--force`）；`git fetch github` 后三个 ref 一致，`git rev-list --left-right --count HEAD...github/main` 为 `0	0`。

---

## 5. 异常处理

总原则：同一问题最多换 3 种办法；不得修改测试或驱动里的判定条件；不得删除任何会话目录或 bindings 文件。

| 编号 | 现象 | 处理 |
|---|---|---|
| 5.1 | 步骤 1 测试失败 | 新测试失败：先核对 `trainer-host.js` 是否与附录 A 一致，不一致就按附录 A 改正；一致仍失败 → 停止并报告完整输出。其他测试失败：确认是否本轮之前就失败（与 B5 时的 404 passed 对比）；若是本轮引入的，按 B5 计划书第 7 节修复 |
| 5.2 | G-2 失败且错误含 `not found` 或 `trainer_operation_failed` | 说明运行中的 DSH 没有加载修复后的代码。核对重启脚本的 `-PluginDir` 指向本仓库插件目录、Gate 输出与启动日志时间；重新部署一次后重跑 G（G 会自动先移回目录，可放心重跑） |
| 5.3 | G-3 显示「仍复用了旧会话」 | 旧会话仍在 DSH 内存中（重启后被打开过）。重启 DSH，**立即**重跑 G，期间不要打开 Z |
| 5.4 | G-3 卡片报其他错误 | 收集证据：`byStep.G` 中该次打开的 `body`、`console.host`、截图，以及 `C:\Users\nvt10241\.dsh\dsh-web-restart.log`。属于代码缺陷 → 按 B5 计划书第 7 节修复（只改 `lib/trainer-host.js`、`lib/trainer-service.js`、`client/native-sessions.js` 中相关逻辑，补测试，客户端改动要重建 `lib/client.js`，全量测试 0 失败，重启 Gate 通过），然后重跑 G |
| 5.5 | G-7 失败，或脚本中途被强行终止 | 打开 `C:\Users\nvt10241\.dsh\b8-removed-sessions\<时间>\manifest.json`，按其中 `from`/`to` 把目录手工移回（如果 `from` 已被重新创建，不要覆盖，停止并报告两边路径）。这是硬停止条件 4 的边界，处理完立即报告 |
| 5.6 | 预检：`target-session(Z)` 为 null，或找不到 Z 的会话目录 | 不要新建来替代。报告 Z 的 `target-sessions/30be50373bf83495422b5eba466265ea.json` 内容与 `C:\Users\nvt10241\.dsh\sessions` 中的搜索结果，停止 |
| 5.7 | 浏览器启动或宿主入口问题 | 按 B5 计划书 6.1、6.2 处理 |

---

## 6. 6.10 节报告模板

```
## 6.10 第 8 条：固定会话被删除后自动新建（Codex，按 docs/tasks/B6-session-removed.md 执行）

- 基线：HEAD / github/master / github/main = <hash>。
- 缺陷与修复：DSH SessionPersistence.inspect() 对已不存在的会话抛出 `session "<id>" not found`，trainer-host 的 sessionVerifier / resumePersistedTrainerAgent 未处理，导致 target-session、open-native-session 返回 trainer_operation_failed。修复：lib/trainer-host.js 新增 inspectPersistedSession，只把该会话的 not found 视为「会话不存在」。测试：trainer-missing-session.test.mjs 2/2；全量 <n> passed / 0 failed。
- 部署：重启产物 <路径>；Gate A/B/C = 0；3080 = 200；无致命签名。
- 第 8 条（脚本输出原样粘贴 G-1 ~ G-7）：
  - …
- 关键值：旧会话 SZ=<…>（目录临时移至 <to>，已移回 <from>）；新会话=<…>；target-session(Z)=<…>；旧 binding 未改写。
- verify-b.mjs：PASS <n> / FAIL <n>。
- 偏离：<无 / 具体内容>。
- 数据：未删除任何会话目录或 bindings 文件；唯一的移动操作已在同次运行中复原。
- 提交 / 推送：<hash>；github/master=<hash>；github/main=<hash>；0/0。
```

---

## 附录 A：`lib/trainer-host.js` 的完整改动（Claude 已写入工作区）

```diff
@@ 在 export function mountTrainerHost(ctx, config) { 之前新增 @@
+// DSH SessionPersistence.inspect() rejects with `session "<id>" not found` once a
+// session log no longer exists (for example after the user removed it). For the
+// Trainer that means "this fixed session is gone" (B acceptance 8): verification
+// must answer false so the target is re-created, instead of failing the request.
+export function isMissingPersistedSession(error, sessionId) {
+  const message = String(error?.message ?? '');
+  return /\bnot found\b/i.test(message) && (!sessionId || message.includes(sessionId));
+}
+
+export async function inspectPersistedSession(ctx, sessionId) {
+  if (typeof ctx?.sessionPersistence?.inspect !== 'function') return null;
+  try { return await ctx.sessionPersistence.inspect(sessionId); }
+  catch (error) {
+    if (isMissingPersistedSession(error, sessionId)) return null;
+    throw error;
+  }
+}
+
@@ resumePersistedTrainerAgent 内 @@
-        const inspected = await ctx.sessionPersistence.inspect(sessionId);
+        const inspected = await inspectPersistedSession(ctx, sessionId);
+        if (!inspected) return null;
@@ sessionVerifier 末尾 @@
-      const persisted = await ctx.sessionPersistence?.inspect(sessionId);
+      const persisted = await inspectPersistedSession(ctx, sessionId);
```
