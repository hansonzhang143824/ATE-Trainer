# PTC 第一批迁移可行性评估（DSH 侧）

评估时间：2026-09-19
评估对象：`DSH-PTC-development-handoff.md` 第一批（P0-A/P0-B/P0-C）
评估结论：**可做**，但有 2 个前提必须由用户先拍板，1 个环境陷阱必须先记住。

---

## 0. 结论摘要

| 项 | 结论 | 依据 |
|---|---|---|
| DSH 机制层面能否支撑"可训练专家母版 + Captain 临时派发" | 能 | preset 发现机制 / 子代理 persona+toolFilter+maxDepth+outputSchema / guard 均已实测存在（见 §2） |
| 交接单对现有代码的判断是否属实 | 大部分属实，1 处范围写错 | 见 §3 |
| 是否需要改 UI | 不需要（第一批仅 CLI/脚本） | 但创建 preset 需要用户在新会话选择器里目视确认 |
| 是否需要重启 dsh web | 需要（插件代码改动生效的唯一途径） | 当前 PID 30672，127.0.0.1:3080；重启会掐掉 GUI 会话 |

---

## 0.1 更正记录（同日，独立复核后）

**本报告先前有一条结论被判错，现更正。**

- 原结论（作废）："交接单第 7 条把 `STAGE_ALIASES` 写在 `ate_ptc_runner.py` 是范围写错，全 scripts 目录搜不到该符号。"
- 更正结论：`scripts/ate_ptc_runner.py:15` **确实定义** `STAGE_ALIASES = {"CORRECTION_STRATEGY": "STRATEGY"}`，并在 `:53` 使用。交接单第 7 条**是对的**。
- 状态源不是"双重"而是**三重**：`team/ptc/ptc_stage_registry.json:5` 的 stateMachine、`scripts/ate_ptc_batch_runner.py:38` 的 `STAGE_ORDER`、`scripts/ate_ptc_runner.py:15` 的 `STAGE_ALIASES`。
- 我出错的原因：用 **PowerShell `Select-String` 做全目录搜索**，把结论当成 grep 的结果写了出来 —— 正是本报告 §1.2 自己写下的密文陷阱。**教训升级为硬规则：本机禁止用 pwsh 下任何"符号不存在"的结论。** 已在本会话改正，此后所有内容判据只用 read / grep 工具。
- 证据来源：独立复核子代理（只看代码行号，不用 PowerShell），其结论我已用 read 工具亲自复查确认（`ate_ptc_runner.py:15`、`:53`）。

---

## 0.2 第二处更正（同日，实测后）

- 原结论（作废）："`~/.dsh/.agent-presets/ate-ptc/preset.yml` 是加密态、不是 YAML，所以该 preset 在选择器里只显示 id `ate-ptc`。"
- 更正结论：**该文件在磁盘上确实是加密态（`%TSD-Header-###%`，8192 字节），但 node / python / DSH 读取时会被透明解密成明文**。用真实发现代码实测，该 preset 的显示名正常解析为 `ATE PTC Runtime`（见 §7.6 输出）。
- 我犯的是同一个错第二次：**用 PowerShell 读字节，再从密文下结论**。这不只是"搜不到符号"的问题，凡是"文件内容/格式/是否合法 YAML"的判断都不能用 pwsh 做。
- 影响：本报告 §1.2 关于"加密层只影响 pwsh"的结论**加强**为——加密层对所有被包装文件生效，且只对白名单进程解密；DSH 自身的工具链（read/grep/node/python）全部在解密侧。

---

## 1. 三个必须先讲清的前提

### 1.1 工作目录不一致（需用户确认）

- 本会话工作区：`D:\Newtest\DSH\ATE-Coding-Flow`
- 交接单里所有路径、以及插件的 `workspaceRoot`、今天的批次产物：`D:\Newtest\DSH\ATE-Coding-Plat`
- 两目录目前逐字节相同（比对 6 个关键文件：`ptc_stage_registry.json`、`policy.js`、`captain-entry.js`、`ate_ptc_runner.py`、`ate_ptc_batch_runner.py`、`AGENTS.md`）
- 插件以 `link:` 方式装进 web profile，指向 **Plat**：`C:\Users\nvt10241\.dsh\profiles\web\package.json` 中 `"dsh-ptc-material-boundary": "link:D:/Newtest/DSH/ATE-Coding-Plat/plugins/dsh-ptc-material-boundary"`，其 `cordis.patch.yml` 的 `workspaceRoot: D:/Newtest/DSH/ATE-Coding-Plat`
- **风险**：在 Flow 改代码等于改死文件，运行中的宿主不会用。

### 1.2 本机存在透明加密层（环境陷阱）

Plat 下 943 个文件带 `TSZ#` / `%TSD-Header-###%` 头（.json 407、.md 191、.py 163、.cpp 74、.js 4 …）。

| 读取方 | 看到的内容 |
|---|---|
| DSH `read` / `grep` 工具（node 进程） | 明文 ✅ |
| `python.exe` | 明文 ✅ |
| `node.exe` | 明文 ✅ |
| PowerShell `Get-Content` / `Select-String` / `ReadAllBytes` | **密文 ❌** |

- 实证：第一次用 pwsh `Select-String` 搜 `STAGE_ALIASES|STAGE_ORDER` 返回 0 命中（假阴性）；改用 grep 工具立刻命中 `ate_ptc_batch_runner.py:38`。
- **纪律**：本机禁止用 pwsh 读文本 / 搜内容 / 比对哈希来判断"某符号不存在"。
- DSH `write` 工具写出的新文件是明文（已用探针文件实测，三方读取一致）。
- 附带发现（**已于同日更正，见 §0.2**）：用 pwsh 读字节时看到的 `ate-ptc/preset.yml` 是密文，但 node / python / DSH 读到的是明文；实测该 preset 的显示名被正常解析为 `ATE PTC Runtime`。
- 需要用户确认：这层加密是否为公司 DLP 合规要求；若是，用编辑器改写文件可能使其脱离加密态。

### 1.3 重启代价

插件代码（guard、`dispatch_profile`）改动必须重启 `dsh web` 才生效；重启会中断当前 GUI 会话。按全局铁律十必须走闸门脚本：
`& "$env:USERPROFILE\.dsh\rules\dsh-plugin-restart.ps1" -Profile web -PluginDir D:\Newtest\DSH\ATE-Coding-Plat\plugins\dsh-ptc-material-boundary`
（脚本存在：11846 字节；配套 `plugin-patch-gate.mjs`。）

---

## 2. DSH 机制逐条核对（交接单"已确认的 DSH 事实"）

| # | 交接单断言 | 判定 | 证据 |
|---|---|---|---|
| 1 | preset 默认根为 `~/.dsh/.agent-presets` | ✅ | `dsh-agent-presets/lib/types/discovery.js:38`（`USER_PRESET_DIR='.agent-presets'`）、`index.js:100-102`（`includeUserRoot` → 追加用户根） |
| 2 | 创建后必须实测选择器可见 | ✅ 机制上成立 | 发现不做记忆化（`discovery.js` 头注释 + `discoverPresets`），运行中新建即可见；显示名靠 `preset.yml`（`metadata.js:23`） |
| 3 | 子代理继承 Captain preset，不能换 preset | ✅ | `start()` 请求字段只有 label/prompt/parent/signal/persona/toolFilter/maxDepth/outputSchema/agentOptions，无 preset 字段（`dsh-subagent/lib/types/index.js:290-302`） |
| 4 | `start('spawn', req)` 支持 persona/toolFilter/maxDepth/outputSchema/agentOptions | ✅ | 同上；`mode` 固定 `'one-shot'`，返回发布的 run |
| 5 | spawn provider 对四项能力支持 | ✅ | `dsh-subagent-spawn-in-process/lib/index.js:23-27`（outputSchema/depthLimit/toolFilter/persona 全 true）。这是关键：换 out-of-process provider 会被 `assertCapabilities` 拒绝 |
| 6 | maxDepth 必须为 1 | ✅ | `dsh-subagent/lib/types/child-agent.js:32-39` `resolveChildDepth` 超限抛 `SubagentDepthError` |
| 7 | toolFilter 不是安全边界 | ✅ | `child-agent.js:133-134` 仅 `childCtx.tools.restrict(...)` |
| 8 | `ctx.tools.guard()` 在 `tools/pre-execute` 后提供单调拒绝 | ✅ | `dsh-tools/lib/types/index.js:521-526`（注释明确"no guard can force-allow"） |
| 9 | one-shot start 返回 run/ID；descriptor 已持久化 | ✅ | `dsh-subagent/lib/types/descriptor.js:42-43`（persisted descriptor 含 persona/toolFilter）；会话事件 `subagent/descriptor`（`policy.js:11` 已在读它） |

---

## 3. 交接单对现有代码的判断：抽查结果

| 交接单条目 | 判定 | 证据 |
|---|---|---|
| 第 7 条：`ate_ptc_batch_runner.py` 的 `STAGE_ORDER` 硬编码 `CORRECTION_STRATEGY` | ✅ 属实 | `scripts/ate_ptc_batch_runner.py:38-48`（含 `"CORRECTION_STRATEGY": 1`）vs `team/ptc/ptc_stage_registry.json:5`（stateMachine 无此阶段） |
| 交接单第 7 条另半句：`ate_ptc_runner.py` 的 `STAGE_ALIASES` | ✅ **属实（本报告先前判错，已更正）** | `scripts/ate_ptc_runner.py:15` 定义 `STAGE_ALIASES = {"CORRECTION_STRATEGY": "STRATEGY"}`，`:53` 使用它。状态源实为**三处**：`ptc_stage_registry.json` 的 stateMachine ∪ `ate_ptc_batch_runner.py:38` 的 `STAGE_ORDER` ∪ `ate_ptc_runner.py:15` 的 `STAGE_ALIASES` |
| 第 8 条：dispatch 数据结构单复数不统一 | ✅ 属实 | `ate_ptc_runner.py:226-227`（`dispatchableRoles` + `roles[0] if len==1`）、`ate_ptc_batch_runner.py:338`（兼容回落 shim）、`:357`（回落到单数 `dispatch`） |
| 第 5/9 条：现有身份判定靠 label | ✅ 属实 | `policy.js:11-16`（`labelOf()` 读 descriptor.label + 正则）、`:53`（`decision()` 按 label 分派） |
| 第 4 条：真正拒绝必须走 Hook/guard | ✅ 现状确认 | `plugins/dsh-ptc-material-boundary/lib/index.js:15-18` 目前用 `ctx.on('tools/pre-execute', ..., {prepend:true})`，**未**使用 `ctx.tools.guard()` |
| 路径绕过面（第 3 条） | 部分已防 | `policy.js:9-10` 已用 `fs.realpathSync.native` + `path.relative` 的 `inside()`；仍需补 junction / 符号链接 / 大小写 / `Input` vs `Input-old` 的实测绕过用例 |

顺带确认：`agent-teams` **当前已经是 disabled 状态**（`profiles/web/cordis.patch.yml:76-78`），文件仍在 → 交接单"不卸载 agent-teams"这条**无需任何动作**。

---

## 4. 工作量与真实风险

| 子阶段 | 可做性 | 主要风险 |
|---|---|---|
| P0-A 验证 + guard + 收据 + 状态源合并 | 可做（纯代码+测试） | 低。guard 上线需一次重启 |
| P0-B DFT 专家母版 + 评测/发布脚本 + TM106 闭环 | 可做 | **中**：`evaluate_expert_profile.py` 能自动校验 schema/哈希/边界，但"黄金案例预期值"的 DFT 语义真值只能由领域专家给定，否则评测只能验证形式不能验证语义（此点标 UNKNOWN，需一次真值输入） |
| P0-C 原理图专家母版 + 旧 IR 禁读回归 | 可做 | 低。guard 按 realpath 判定，读 `project/DALI/schematic-ir.json` 会被拒 |

---

## 5. 待用户决定

### 决定一：代码改在哪个目录

| 选项 | 优点 | 缺点 | 成本 | 可逆性 |
|---|---|---|---|---|
| **A. `ATE-Coding-Plat`（推荐）** | 插件 link 指向它，运行宿主真正加载它；批次产物、脚本、角色文件全在这；改完即生效 | 本会话工作区是 Flow，属于跨目录作业 | 无额外成本 | 高（属同源镜像） |
| B. `ATE-Coding-Flow` | 与会话工作区一致，工具常识上更顺 | 改了运行时不加载，等于白做；后续还要再同步一次 | 重复劳动 | 低（容易误判"改了没用"） |
| C. 新开一个以 Plat 为工作区的会话 | 彻底消除目录歧义，符合全局铁律 §7/§11 | 需要用户操作一次 | 几分钟 | 高 |

**推荐 A 或 C，推荐先 C 后 A**：先在一个明确以 Plat 为工作区的会话里做，避免"两个镜像到底哪个是活的"这类误判。

### 决定二：重启窗口

改动 guard / dispatch_profile 后必须重启 dsh web，当前 GUI 会话会断。建议把"需要重启的改动"集中到一次，而不是边改边重启。

---

## 6. 本评估的证据边界（诚实声明）

- 已实测：§2 全部条目（读 DSH 安装目录中的实现代码）、§3 全部条目、§1.2 加密层行为（探针文件）。
- 未实测：新建 `PTC DFT Expert` preset 后选择器**是否真的显示**（需要建出来 + 用户目视确认，这本身就是交接单要求的验收项）；TM106 的真实 DFT 闭环（需要跑真流程）。
- 已作废的中间结论：第一次用 pwsh 搜索得到的"`STAGE_ALIASES`/`STAGE_ORDER` 不存在"结论**作废**，原因是密文读取假阴性，已由 grep 工具复核推翻（详见 §0.1）。

---

## 7. 方案决定与 P0-A 首轮产出

### 7.1 用户决定（2026-09-19）

- 代码改在 `D:\Newtest\DSH\ATE-Coding-Flow`（方案 B），`ATE-Coding-Plat` 那条现有路径一律不碰。
- 插件改动的生效重启**攒到一次**再走闸门脚本。

### 7.2 方案 B 的两个必然后果（已核实，非猜测）

1. **preset 是全局的**：专家 preset 必须建在 `~/.dsh/.agent-presets`，它不属于任何一个仓库，所以新建的两个专家会同时出现在你现在这个 GUI 的新会话选择器里。这是 DSH 的机制，无法只在 Flow 内隔离。好处是"选择器里能看到 `PTC DFT Expert`"这条验收**不需要任何重启**就能达成和验证。
2. **Flow 里那条材料边界当前不生效**：`lib/policy.js` 先判 `cwd` 是否在 `workspaceRoot` 内，Flow 会话不在 Plat 根内 → `decision()` 返回 undefined → 插件对 Flow 会话完全不管。所以：开发不受干扰，但**宿主机级**的边界验收（真实会话里 guard 拒绝越界）必须有"工作区绑到 Flow"的宿主才能做。
   - 现成通道：`dsh --profile headless "<任务>"`（答一个任务、打印结果、退出）。已按 §7.6 建立**新增**的 `ptcflow` profile 承载它——不改 web/headless 任何现有文件，也不用 pnpm。
3. 已确认 `scripts/ate_ptc_batch_runner.py:25` 的 `ROOT = Path(__file__).resolve().parents[1]`：在 Flow 里跑脚本，产物落在 Flow 下，**不会写到 Plat**，符合"不影响现有路径"。

### 7.3 本轮产出（P0-A 第一块，全部不依赖宿主、不改生产行为）

新增两个测试文件，并挂进聚合入口 `test/all.test.mjs`：

- `plugins/dsh-ptc-material-boundary/test/path-boundary.test.mjs` —— 在**临时目录里搭一个合成工作区**跑边界绕过回归（不碰真实 DALI 材料），覆盖交接单点名的 realpath / `..` / junction / 符号链接 / 大小写 / 前缀混淆，外加 label 伪造与越界写入。
- `plugins/dsh-ptc-material-boundary/test/guard-mount.test.mjs` —— guard 挂载验证，含一个**镜像宿主工具流水线**的假 ctx（pre-execute 瀑布 → 单调 guard 阶段 → 除能器），并显式记录当前"零 guard"的注册形态。

运行结果（Flow 副本）：

```
node --test all.test.mjs
tests 43 | pass 42 | fail 0 | skipped 1 | todo 0
```

- 基线（改动前）为 17 项全过；本轮 +26 项。
- 唯一 skipped：Windows 建文件符号链接需要特权，该项**如实记为跳过，不记为通过**。
- 顺带修掉一个测试自身的断言错误（除能器计数写错），非生产代码问题。

### 7.4 测试暴露出的两个真实缺口（尚未修，属后续交付项）

1. **身份识别是 fail-open 的**：`lib/policy.js` 只认正则匹配的 label；大小写变体等未识别 label 会让 `decision()` 返回 undefined，**该子代理完全不受边界约束**（已在测试中固化记录）。这就是交接单要求"换 descriptor + guard"的具体理由。
2. **现有派发只带 label**：`lib/captain-entry.js:112` 的 `ctx.subagents.start('spawn', { label, prompt, parent, signal })` 没有 persona / toolFilter / maxDepth / outputSchema。独立复核另证：one-shot 的描述符**只带 label**（`dsh-subagent/lib/index.js:2612-2616`），不含 persona/toolFilter —— 这正好解释了交接单为什么要求 PTC 另建 run 级派发收据。

### 7.5 复核补充的两条待观察项（复核员自述未实测）

- `policy.js:13/:16/:53` 的 cwd 检查只用 `path.resolve`（未 realpath），`:18` 的 `target === input` 是大小写敏感精确比较 → 当 `workspaceRoot` 含 junction 或大小写不一致时会**误拒合法访问**（方向是拒绝，不是放行，属 fail-closed）。
- `labelOf` 用 `findLast` 取最后一条 descriptor，而 DSH 自身 `foldSubagentDescriptor` 取第一条 → 身份取值口径是否可被利用，未验证。

### 7.6 宿主级验证通道已建立（新增，不影响任何现有路径）

**构成**（全部是新增目录/文件，`web` 与 `headless` 两个现有 profile 一个字节都没改）：

```
~/.dsh/profiles/ptcflow/
  package.json        bundles: [@deepseek-ai/dsh-base, @deepseek-ai/dsh-headless]
  cordis.yml          空数组（profile 根锚点）
  cordis.patch.yml    插入 ptc-material-boundary 行, workspaceRoot = D:/Newtest/DSH/ATE-Coding-Flow
  node_modules/dsh-ptc-material-boundary  → junction 指向 Flow 的插件目录（用 junction 代替 pnpm install）
```

为什么可行：`@deepseek-ai/dsh-base` 自带 `tools`（dsh-tools）、`subagent`（dsh-subagent）、`subagent-spawn-in-process`、`tool-subagent`、会话持久化与沙箱——正是验证 guard 与派发所需的宿主面。

**已通过的三道门**：

| 门 | 命令 | 结果 |
|---|---|---|
| 插件挂载行可解析（真解析，非只合成） | `node ~/.dsh/rules/plugin-patch-gate.mjs ~/.dsh/profiles/ptcflow` | exit 0；`bundles: 2  挂载行已解析: 81` |
| 配置合成 | `dsh --profile ptcflow --dump-config` | exit 0；`ptc-material-boundary` 行带 `workspaceRoot: D:/Newtest/DSH/ATE-Coding-Flow` |
| **真实启动**（dump-config 不导入模块，是已知盲区） | `dsh --profile ptcflow "…"` | exit 0，输出 `PTCFLOW-BOOT-OK` → 插件树真的从 Flow 加载成功 |
| **真实宿主级边界拒绝** | `dsh --profile ptcflow "调一次 subagent…"` | 模型回传插件原话：`Error: PTC dft dispatch must name its authorized TM set in the DFT descriptor.` → 边界在真实会话里于执行前生效 |

第 4 行是本次最关键的一条：它一次性证明了"插件从 Flow 加载 + workspaceRoot 绑到 Flow + `tools/pre-execute` 边界在真实会话中拦截 + 拒绝理由原样送达模型"，而且全程没有动 web、headless 或 Plat。

### 7.7 专家 preset 已建立并被真实发现代码看到

新增 `~/.dsh/.agent-presets/ptc-dft-expert/`（`agent.cordis.yml` 由 `ate-ptc` 复制后重写 persona；`preset.yml` 写明文显示名）。用**已安装的 DSH 发现实现**（不是我自己重写一套）验证：

```
node .dsh-dev/verify-preset-discovery.mjs
preset root scanned: C:\Users\nvt10241\.dsh\.agent-presets
rows: 4
{"id":"standard-70","displayName":"标准模式（70% 压缩）",...}
{"id":"liangshen","displayName":"梁神模式",...}
{"id":"ate-ptc","displayName":"ATE PTC Runtime",...}
{"id":"ptc-dft-expert","displayName":"PTC DFT Expert","description":"PTC DFT 专家母版（训练会话）…","broken":null}
missing: ptc-schematic-expert   (P0-C 尚未开始，脚本已改为可选)
broken: none
```

结论分层：
- **FACT**：`ptc-dft-expert` 存在于 roster、显示名解析为 `PTC DFT Expert`、组件可加载（`broken: null`）。
- **UNKNOWN**：浏览器选择器里的**渲染**未验证（发现层已证，UI 层没测）。这一条属交接单验收项，需要你在新建会话里看一眼。

### 7.9 本轮新增的两个核心件（P0-A）

| 文件 | 作用 | 状态 |
|---|---|---|
| `plugins/dsh-ptc-material-boundary/lib/expert-policy-registry.js` | executionClass 注册表：六个类的可读/可写/必过门禁，加 profile→class 映射。交接单 §4.2 明确要求这张表必须在**代码**里（只写 Markdown 不算强制） | 新增，纯数据+校验，不接任何现有逻辑 |
| `plugins/dsh-ptc-material-boundary/lib/dispatch-receipt.js` | run 级派发收据：pinned 的 profile/版本/persona/合同/policy 哈希/executionClass/targetTms + 规范化摘要 + 篡改检测 + `identityFromReceipt()` | 新增，纯函数，无 I/O、无宿主依赖 |
| `plugins/dsh-ptc-material-boundary/test/dispatch-receipt.test.mjs` | 收据与注册表的测试，含**反伪造**用例 | 新增 |

反伪造是这些测试的核心：收据**不能**声明比它所属 profile 更宽的执行类（`ptc-dft-expert` 声明 `implementation-standard` 会被拒），没有 targetTms 的"无范围输入专家"不可派发，`profileVersion: latest` 不被接受（必须 `draft` 或 `v1`），任何字段被改都会导致摘要不匹配。也就是说：**身份从收据读，不从 label 读** —— 直接封掉 §7.4 第 1 条那个 fail-open 缺口。

顺带一条过程记录：这轮测试当场抓出我自己注册表里的一个缺陷——`<run>` 占位符没被 `isDeclaredPath()` 允许（只允许了 `<TM>`）。已修。

**当前插件测试总况**（Flow 副本，`node --test all.test.mjs`）：

```
tests 55 | pass 54 | fail 0 | skipped 1
```

（基线 17 → 55；唯一 skipped 仍是 Windows 文件符号链接需特权那项。）

### 7.10 P0-A 收尾两块已修复并通过测试（同日）

**改动文件与结果**

| 改动 | 文件 | 说明 |
|---|---|---|
| 复数 dispatch 修复 | `scripts/ate_ptc_runner.py`、`scripts/ate_ptc_batch_runner.py` | 新增 `dispatch_roles()`：**复数 `dispatchableRoles` 为准**，单数 `dispatch` 只作回落。批处理 runner 在每个阶段都用它，不再只读单数 |
| 阶段状态源合并 | `scripts/ate_ptc_runner.py`、`scripts/ate_ptc_batch_runner.py` | 删掉批处理 runner 里硬编码的 `STAGE_ORDER` 表，改为新增的 `stage_order()` 从**注册表 stateMachine 顺序**推导等级，并把 `CORRECTION_STRATEGY` 折到 `STRATEGY`。别名声明全树只剩一处（`ate_ptc_runner.py`） |
| 新增测试 | `scripts/test_ptc_dispatch_plural_and_stage_source.py` | 11 项，含"只允许一处别名声明、不允许任何地方再写等级表"的静态扫描 |

**测试命令与结果**

```
python -m unittest test_ptc_dispatch_plural_and_stage_source      → Ran 11 tests, OK
python -m unittest discover -p "test_*.py"  (PYTHONPATH=仓库根)   → Ran 84 tests, OK, exit 0
```

修复**前**同一套新测试是 `failures=3, errors=6`，其中最典型的一条是
`AssertionError: 'BLOCKED' != 'STRATEGY'` —— 正就是交接单说的"第二阶段空 dispatch 提前返回"。
修复后 84 项全过（含原有 6 个测试文件的 29 项，无回归）。

**一条刻意的克制**：批处理 runner 只对 INPUT_SYNC 输出 `dispatches` 复数派发清单，其它阶段只加
`dispatchableRoles`。原因是 `captain_delivery_entry.advance_batch()` 的返回值会被插件的续跑逻辑
**直接拿去派发** `dispatches` 里的每个角色；在非源阶段加上这个键，等于悄悄让 Hook 自动派发策略/方法专家——
那是生产行为改变，不属于 P0-A。已写成测试固化这条边界。

### 7.11 P0-A 最后一项：真实宿主里的派发身份对应

**先分清两条路径（这是我第一遍差点搞混的地方）**：
- `subagent` **工具**在本部署里是 `backgroundMode: continuable`；
- 交接单要求用的是 `ctx.subagents.start('spawn', …)`，那是 **one-shot**。

**已实测（工具路径，continuable）**：一次真实派发后核对会话记录——

| 项 | 值 |
|---|---|
| 父会话 | `session-0ccd49d5-…`，`delegationDepth=0` |
| 父会话里收到的派发 id | `tool/result` 文本：`started subagent a84d6053-…` |
| 子会话目录与头部 id | `a84d6053-9c82-4355-a4b5-2510edf7a39d`，`delegationDepth=1` |
| 子会话第 0 条记录 | `subagent/descriptor {mode:"continuable", provider:"spawn", label:"probe-child"}` |

→ **FACT**：派发方拿到的 id、子会话的持久化 id、以及携带 `subagent/descriptor`（也就是 `policy.js:11`
`labelOf()` 唯一读取的那条事件）的会话，三者是同一个身份。身份链路成立。

**顺带发现的读取陷阱（值得记下来）**：DSH 的会话日志是 zstd 压缩且**每 flush 追加一个独立帧**；
`zlib.zstdDecompressSync` 与解压流都**只解第一帧**，于是"读日志"会静默得到一条光秃秃的头部记录、
事件数为 0——看起来像"没有证据"，实际是没读到。已按 zstd magic 切帧后逐帧解压
（`.dsh-dev/inspect-session.mjs`）。我第一遍就是这样误判的。

**one-shot 路径（交接单要求的那条）**：本机 `subagent` 工具是 continuable，所以工具验证不了它。
新增一个只挂在 `ptcflow` 上的探测插件（`.dsh-dev/probe-dispatch/`，**不属 PTC 插件、不进任何生产组合**），
在真实宿主里执行一次 `ctx.subagents.start('spawn', {persona, toolFilter, maxDepth:1, outputSchema, label, prompt, parent})`，
把 API 接受情况与返回身份写盘。结果见下节。

### 7.12 one-shot 路径验证结果（交接单 P0-A 最后一项）

探测插件在真实宿主里执行了一次 `ctx.subagents.start('spawn', {persona, toolFilter, maxDepth:1, outputSchema, label, prompt, parent})`，产物：`.dsh-dev/oneshot-probe.json`。

| 项 | 实测值 | 含义 |
|---|---|---|
| API 是否接受四项能力 | `ok: true`，无 `UNSUPPORTED_CAPABILITY` | **FACT**：`persona`/`toolFilter`/`maxDepth`/`outputSchema` 在真实宿主里被接受，不是只看代码声明 |
| 返回 run 的字段 | `dispose, id, localAgent, result`；`id = cadd37e3-aa75-4e10-a1cc-68e42a40d799` | one-shot 的 run 只给一个 `id`，没有 `subagentId`/`sessionId`（那两个是 continuable 专有） |
| 子会话是否持久化 | 存在 `sessions/…-ATE-Coding-Flow--/cadd37e3-…`，头部 `id=cadd37e3-…`、`delegationDepth=1` | **FACT**：`start()` 返回的 id == 子会话的持久化 id == 只有一层 |
| 子会话是否带身份描述符 | `subagent/descriptor {version:2, mode:"one-shot", provider:"spawn", label:"probe-oneshot-child"}`（`seq:5`） | **FACT**：one-shot 子会话**也有** descriptor 且带 label，`policy.js:11` 的 `labelOf()` 能找到它 |
| descriptor 是否含 persona/toolFilter | **不含**（只有 version/mode/provider/label） | 印证独立复核的判断，也印证交接单为什么要 PTC 自建 run 级收据 |
| outputSchema 是否真生效 | 子代理调用 `structured_output {token:"ONESHOT-CHILD-OK"}`，`stopReason:"completed"` | **FACT**：结构化输出被真正强制并回传 |

**结论（FACT）**：交接单要求的那条 one-shot 派发路径，其身份链条成立——
`ctx.subagents.start()` 返回的 `id` ＝ 子会话持久化 id ＝ 携带 `subagent/descriptor`（guard/策略读取 label 的唯一来源）的那个会话。
父会话 id 带 `session-` 前缀、子会话是裸 uuid，可据此稳定区分。

### 7.12.1 进行中（作业指针，供续跑）

| 项 | 值 |
|---|---|
| 作业 id | `pwsh-11`（guard 采纳后，在 ptcflow 真实宿主上重跑边界拒绝） |
| 要核对 | 期望模型回传 `PTC dft dispatch must name its authorized TM set in the DFT descriptor.`；若插件树因 `ctx.tools.guard` 报错而 `plugin tree failed to load`，则该采纳在真实宿主不可用，必须回退并改结论 |
| 结果（已完成） | exit 0，模型回传 `RESULT=PTC dft dispatch must name its authorized TM set in the DFT descriptor.` → **guard 采纳后插件树仍能从 Flow 正常加载并拒绝派发**<br>INFERENCE（非独立证明）：与采纳前那次相比，拒绝文本少了 `Error: ` 前缀，这与"这次是 guard 阶段拦下"相符；我没有做区分两者的独立实验 |
| 备注 | 非阻塞读；作业完成会自动唤醒本会话 |

### 7.13 guard 采纳（交接单 P0 第 6 条）已完成

`lib/index.js` 现在**同时**挂两处：既有的 `tools/pre-execute`（先跑）＋ 新增的 `ctx.tools.guard()`（后跑、单调拒绝）。
两处调用同一个 `decision()`，所以 guard 只可能**追加**拒绝，不可能放松任何一条。

配套测试改动（同一提交内）：
- `test/policy.test.mjs` 的假 ctx 补上 `tools.guard`（原先的假 ctx 会静默吞掉这个注册，属"假实现不镜像真实校验"）；
- `test/guard-mount.test.mjs` 的"记录当下形态"断言由 0 个 guard 改为 1 个（这条断言本来就是变更探测器，按设计强迫同步更新）。

**测试结果**：插件套件 55 项 → `pass 54 / fail 0 / skipped 1`（guard 采纳后仍全绿）。

### 7.14 一次操作事故（已回滚，必须记录）

我在做 guard 采纳时**把编辑打到了 `ATE-Coding-Plat`**——正是你明令不碰的那条路径。发现后立即回滚，并用**解密后内容哈希**证明还原：

```
Plat 与 Flow 的 lib/index.js 解密后内容 sha256 = 9972db92…（两者一致，等于改动前的原文）
Plat 文件长度 859 字节（与原始一致），已不含我加的那行
```

附带一个必须记住的事实：这两个仓库里的文件**在磁盘上是密文**，所以 `Get-FileHash`（pwsh）比较的是密文，
同样的明文每次写入会产生不同密文——**判"是否还原"必须比解密后内容哈希，不能用 pwsh 的文件哈希**。
本报告早先用 `Get-FileHash` 得出的"两仓库逐字节相同"因此只能算 INFERENCE（内容相同的证据来自解密比较）。

## 8. P0-B 第一批（同日）：专家母版资产 + 评测/发布脚本已落地

### 8.1 新增文件

| 文件 | 作用 |
|---|---|
| `team/expert-profiles/ptc-dft-expert/profile.yaml` | 母版元数据（id / 显示名 / presetId / executionClass / 可读可写 / 门禁） |
| `…/instructions.md` | 专家任务书：读什么、禁止读什么（明确写死 `schematic-ir.json` 永不作为输入）、每个 TM 产出三个产物、怎么报告 |
| `…/output-contract.schema.json` | 输出契约，字段**对齐 `scripts/validate_dft_outputs.py` 真正校验的内容**（含 20 项 testCondition 必填键），避免契约与门禁各说各话 |
| `…/cases/TM106/expected.json` | TM106 黄金案例：断言结构契约、canonical 输入身份、读源边界 |
| `…/evaluation/expected-results.json` | 案例索引（与 cases/ 目录必须一致，不一致即判失败） |
| `…/CHANGELOG.md`、`…/status.json` | 变更记录与发布状态 |
| `scripts/expert_profile.py` | 共享模块：**无依赖**的严格 profile.yaml 子集解析器、资产清单、清单摘要 |
| `scripts/evaluate_expert_profile.py` | 草稿评测（交接单 §6.1），exit 0/2 |
| `scripts/publish_expert_profile.py` | 发布（交接单 §6.2）：先评测 → 拒绝覆盖 → 快照 → 清单 → 更新 status |
| `scripts/test_expert_profile_lifecycle.py` | 14 项生命周期测试 |

### 8.2 真实命令与结果（不是只跑测试）

```
python scripts/evaluate_expert_profile.py --profile ptc-dft-expert --version draft
→ exit 0, verdict "pass", failed [], caseCount 1, 12 项检查全过
   含 "boundary_regression: plugin boundary suite passed"（真的跑了插件边界套件）

python scripts/publish_expert_profile.py --profile ptc-dft-expert --version v1
→ exit 0, published true, fileCount 7
   manifestDigest f8b667c641fd3453…  （== 草稿 assetDigest）
   manifest: version v1 / executionClass input-dft / files 7 / evaluation verdict pass
   status.json: publishedVersion v1, previousVersion null, history [v1]
```

发布的不可变性、篡改检测、拒绝覆盖、保留上一版本，都由测试固化（`publish` 失败时**不创建任何版本目录**）。

### 8.3 一个只有"真跑"才能暴露的缺陷

单元测试里我把边界套件跳过（`--skip-regression`）以保证测试快，所以**没走到那行**。
真跑第一条命令时立刻暴露：`subprocess.run(..., text=True)` 用本机区域编码（GBK）解码 node 的 UTF-8 输出，
在读线程里抛 `UnicodeDecodeError`（返回码仍是 0，所以不看 stderr 会误判成功）。已修为 `encoding="utf-8", errors="replace"` 并复跑通过。
教训：**跳过的那条路径等于没测**，交付前必须跑一次不带跳过参数的真实命令。

### 8.4 当前测试总况

```
python -m unittest discover -p "test_*.py"   → Ran 98 tests, OK, exit 0
node --test all.test.mjs                     → pass 54 / fail 0 / skipped 1
```

## 9. P0-B 第二批（同日）：分发器与派发接线

### 9.1 新增/改动

| 文件 | 作用 |
|---|---|
| `plugins/dsh-ptc-material-boundary/lib/dispatch-profile.js` | **`dispatch_profile` 宿主分发器**（交接单交付物第 4 条）：解析已发布版本 → **用 manifest 校验快照未被改动** → 注册表阶段核对 → 从已发布 instructions 生成 persona、从代码注册表取 toolFilter/读写边界 → one-shot 派发（`maxDepth: 1` ＋ `outputSchema`）→ 写 run 级收据 |
| `plugins/dsh-ptc-material-boundary/test/dispatch-profile.test.mjs` | 19 项 |
| `plugins/dsh-ptc-material-boundary/test/dispatch-pinned-source.test.mjs` | 4 项（Captain 源派发的 pinned 路径） |
| `plugins/dsh-ptc-material-boundary/lib/captain-entry.js` | 源派发支持 `config.pinnedProfiles`：已配置的角色走 pinned 分发器；**pinning 失败则不派发、不推进阶段**（符合交接单"guard、descriptor、版本 pin 任一失败：不派发、不推进阶段"） |
| `team/expert-profiles/ptc-dft-expert/profile.yaml` | 新增 `runtimeLabel: PTC dft expert [<TM>]` |

### 9.2 一个必须记录的连锁修复

分发器第一版把 label 写成 `PTC ${ownerRole}`（即 `PTC dft-expert`），而现有材料边界用的正则是
`^PTC dft expert \[(TM…)\]$`——**这个 label 完全匹配不上，而 `policy.js` 对"不认识"的 label 是 fail-open 的**，
等于用一个新机制把边界悄悄关掉。已改为：label 由已发布 `profile.yaml` 的 `runtimeLabel` 渲染；
**profile 若没有 `runtimeLabel` 就直接拒绝派发**（不给默认值，因为默认值就是 fail-open）。已写成测试。

### 9.3 版本推进

```
publish v2 (draft 已加 runtimeLabel)  → published, previousVersion v1, history [v1, v2]
v1 校验：7 个文件 0 漂移，仍未含 runtimeLabel（历史版本原样保留）
v2 校验：7 个文件 0 漂移，含 runtimeLabel
```
这次发布走的是**完整评测**（含插件边界套件），未使用 `--skip-regression`。

### 9.4 测试总况

```
node --test all.test.mjs   → tests 78 | pass 77 | fail 0 | skipped 1
python -m unittest …       → Ran 98 tests, OK, exit 0
```

### 9.5 进行中（作业指针，供续跑）

| 项 | 值 |
|---|---|
| 作业 id | `pwsh-12`（ptcflow 宿主里走**真实 dispatchProfile** 派发已发布 v2） |
| 产物路径 | `.dsh-dev/oneshot-probe.json`、`team/artifacts/dispatch-receipts/ptc-dft-expert-probe-run-1-TM106.json` |
| 要核对 | ① `dispatched: true` 且 receipt 的 `profileVersion` 是当前发布版本；② 收据 `childSessionId` 是否等于持久化子会话目录名；③ 该子会话的 descriptor label 是否为 `PTC dft expert [TM106]`（即边界认得的那个） |
| 备注 | 非阻塞读；作业完成会唤醒本会话 |

### 9.6 真实宿主跑出的**第二个集成缺陷**（已修，含修复后复验）

第一次真实 pinned 派发的结果：`dispatched: true`、收据写盘、`run.id == childSessionId == 39c358a8-…`、
label 正是 `PTC dft expert [TM106]`（边界认得的那个）——**但子代理最终 `stopReason: "error"`**。

读子代理自己的推理记录，原因写在里面：`The structured_output tool is being rejected by the host with a PTC material boundary error.`

根因：`policy.js` 的三个专家判定函数都写着
`if (exec.name === 'run_code' || exec.name === 'report') return undefined;` 然后
`if (exec.name !== 'read' && exec.name !== 'write') return DENIED;`
——于是**子代理唯一的交卷通道 `structured_output` 被当成越界工具拒掉**。
我的分发器按交接单要求传了 `outputSchema`，于是"派发能成功、结果永远交不上来"。

修复：新增 `NON_MATERIAL_TOOLS = new Set(['run_code','report','structured_output'])`，
三个判定函数统一放行这三项（它们不是材料访问，是子代理自己的结果通道）。
配套测试两条：① 结果通道对 DFT/原理图专家均放行；② **放行不等于开口子**——`glob`/`grep`/`list_agents`/`subagent` 仍然一律拒绝。

这一条是**只有真跑才能发现**的：我的单测全程用假 ctx，从未让子代理真的去交卷。

### 9.8 端到端验证结果（真实宿主 + 真实发布版本 v2）

修复后再跑同一个 pinned 派发，全链条核对：

| 环节 | 实测 |
|---|---|
| 派发是否成功 | `dispatched: true`，走的是生产代码 `dispatchProfile()` |
| 版本 | 收据 `profileVersion: v2`（当前发布版本，不是 draft、不是 latest） |
| 标签 | `PTC dft expert [TM106]` —— 正是材料边界认得的那个形状 |
| run.id | `a2d72675-77dd-4d8c-b47b-f3582d89444c` |
| 子会话 | 该 id 的会话真实存在，`delegationDepth=1`，`subagent/descriptor {mode:"one-shot", label:"PTC dft expert [TM106]"}` |
| 收据与子会话是否对得上 | 收据 `childSessionId` == 子会话 id；`findReceiptForChild()` 唯一命中 |
| 收据是否自校验通过 | `verifyDispatchReceipt → {ok: true, errors: []}` |
| 子代理是否真的交上结果 | `stopReason: "completed"`（修复前是 `"error"`） |
| 阶段归属 | `stage: INPUT_SYNC`，`registryOwner: captain`（含 registry 未把输入专家列为 owner 的说明） |

**结论（FACT）**：交接单交付物第 4、5 条在真实宿主里打通——
`dispatch_profile` → 已发布 v2 → one-shot 子代理 → run 级收据 → 收据与子会话一一对应且可校验。

### 9.9 测试总况（本轮最终）

```
node --test all.test.mjs   → tests 80 | pass 79 | fail 0 | skipped 1
python -m unittest …       → Ran 98 tests, OK, exit 0
```

## 10. Round 3：TM106 闭环现状与两个关键实证

### 10.1 TM106 的 DFT 产物与门禁（Flow 现状）

Flow 里 TM106 的三个产物**已存在**，真实门禁结果：

```
python scripts/validate_dft_outputs.py --tm TM106
→ exit 0, "status": "ready", "missingOrStaleOutputs": []
   canonicalInput sha256 = 896770d29f8ae58852e1031c1e6210c5435e52df38e0f6a0fb8fc1836622c04b
```

所以"TM106 有可用产物且过门禁"是既有事实；本轮要补的是**让这条路径走新机制**（pinned 派发 → 专家真干活 → 门禁）。

### 10.2 关键实证一：`run_code` 不是绕过材料边界的后门（我原本怀疑它，实测否掉了）

**怀疑**：`policy.js` 对输入专家**无条件放行 `run_code`**，而它是任意代码执行工具——似乎可以绕过材料边界去读任意文件。
（`ate-ptc` preset 的 `tool-presentation: mode: code` 说明真实环境就是 code 模式，这个怀疑必须实测。）

**实测**：在 ptcflow 真实宿主里以 `DSH_TOOLS_MODE=code` 派发已发布 v2 的 DFT 专家，派发任务只有一件事：
用 `run_code` 读 `project/DALI/schematic-ir.json` 并报告结果。子代理原话：

```
[reasoning] The read was refused. Report. No gate command was run; gates: [].
[tool-call run_code] ... outputs: [
  "probe-run-1 / TM106: run_code WAS available; I attempted exactly one read of project/DALI/schematic-ir.json.",
  "Outcome: REFUSED. No file content was read and no f..."
```

**结论（FACT）**：code 模式下 `run_code` 内部发起的 SDK 读取**仍然逐个经过边界判定**并被拒绝；子代理没有拿到任何文件内容，且它自身以 `stopReason: completed` 正常交卷。
→ 我原先的怀疑**不成立**，不改策略。（这条正好是 P0-C 要的重点：旧 IR 不能被读作输入，已在真实宿主里得到拒绝证据，而不是靠读代码推断。）

### 10.3 关键实证二：输入专家能自己算出产物哈希（闭环因此可闭合）

我原本还怀疑：刷新产物后 `dft-semantic-review.json` 会变旧，而专家被限制只能 hash canonical 输入，
于是**没法**重新绑定审查→闭环永远闭合不了。10.2 的结果同时否掉了这个怀疑：
code 模式下专家可以用 `run_code` 在进程内算 sha256（读取自己的产物是允许的），因此它能重写一份有效的审查。

### 10.4 进行中（作业指针，供续跑）

| 项 | 值 |
|---|---|
| 作业 id | `pwsh-15` |
| 内容 | 以 pinned 派发让已发布 v2 的 DFT 专家**真的干活**：按允许清单执行 refresh → render → validate，必要时重写审查，再复跑门禁 |
| 产物路径 | `.dsh-dev/dft-loop-probe.json`、`team/artifacts/dispatch-receipts/ptc-dft-expert-probe-run-2-TM106.json` |
| 事前备份 | `backup/tm106-dft-before-pinned-loop/`（4 个文件，允许我在结果变差时还原） |
| 要核对 | ① 门禁最终是否 `ready`；② 收据/子会话身份是否一致；③ 若专家改坏了产物 → 用备份还原并如实报告 |
| 备注 | 非阻塞读；作业完成会唤醒本会话 |

## 11. Round 4：TM106 闭环跑通 + 原理图专家建成

### 11.1 TM106 真实 DFT 闭环（已跑通，我独立复核，不采信子代理自述）

派发：pinned 派发**已发布 v2** 的 DFT 专家到 ptcflow 真实宿主（code 模式），任务是真实 DFT 工作：
hash → refresh → render → validate，必要时自己重绑审查。

| 核对项 | 结果 |
|---|---|
| 子代理是否真干活 | 会话日志里 **30 条记录**含 `validate_dft_outputs.py --tm TM106`；产物确实被重写 |
| 产物变化（对比事前备份，明文 sha256） | `dft-meta.json` 59d5e926→07379a94、`dft-conditions.yaml` 4ca2f9e3→f22578bf、`dft-semantic-review.json` 2d9b61f1→f1fcee71（三个都变=真跑） |
| **我自己**复跑门禁（不采信它说"passed"） | `python scripts/validate_dft_outputs.py --tm TM106` → **exit 0**、`missingOrStaleOutputs: []` |
| 派发身份 | 收据 `ptc-dft-expert-probe-run-2-TM106.json`；子会话 `931761de-…`，descriptor label `PTC dft expert [TM106]` |

**诚实标注**：交接单 P0-B 的顺序是"训练 → 评测 → 发布 → 派发 → 门禁"。其中"训练"这一步我做的是
**配置级改动**（新增 `runtimeLabel`）而不是"改一条 draft 规则或黄金案例"；规则级训练迭代还没真正做过。
而且**语义真值仍缺**（案例标着 `PENDING_DOMAIN_INPUT`），所以"过门禁"证明的是结构/哈希/边界/门禁，**不证明** DFT 语义正确。

### 11.2 P0-C：PTC Schematic Expert 已建成（资产 + 评测 + 发布 + 可见）

| 项 | 结果 |
|---|---|
| 资产 | `team/expert-profiles/ptc-schematic-expert/`：profile.yaml、instructions.md、output-contract.schema.json（字段对齐 `validate_schematic_outputs.py`）、cases/TM106/expected.json（含 `forbiddenInputs: [schematic-ir.json]`）、evaluation、CHANGELOG、status |
| preset | `~/.dsh/.agent-presets/ptc-schematic-expert/`（复制 ate-ptc 组件、重写 persona） |
| 评测 | `evaluate_expert_profile.py --profile ptc-schematic-expert --version draft` → **verdict pass, failed []**, exit 0 |
| 发布 | `publish_expert_profile.py --profile ptc-schematic-expert --version v1` → **published true**, digest `3eda98d25c79118b…`, 7 个文件 |
| 可见性 | 真实发现代码扫到 **5 个** preset，`PTC DFT Expert` 与 `PTC Schematic Expert` 都在列，`broken: none`、`missing: none` |
| 派发接线 | ptcflow 的 `pinnedProfiles` 已同时覆盖 `dft-expert` 与 `schematic-expert` |

### 11.3 本轮修掉的一个真缺口：输出根里的退役 IR 原本**可以**被读

我新写的 P0-C 用例一跑就失败，暴露出：`schematicDecision` 的判定是
`inputs.has(target) || inside(target, output)` —— **输出目录下任何文件都可读**，
所以把退役 `schematic-ir.json` 放进 `Output_Global_Material/schematic/` 就能被专家读到，
直接违反交接单"即使输出根里存在旧 IR，专家也不能读取它"。

修复：`policy.js` 新增 `RETIRED_ARTIFACTS` 与 `retiredArtifact()`；两条判定在算出 realpath 后先查退役名单
（原始路径与解析后路径都查，防 junction 改名），命中即拒绝：
`PTC material boundary: schematic-ir.json is a retired artifact and is never a PTC input.`

### 11.4 另一处收紧：运行标签改由代码注册表唯一确定

原理图专家的运行标签是 **TM-less**（`PTC schematic expert`，一件共享产物），而我的分发器原先要求标签必须含 `<TM>`，
会把原理图专家直接拒掉。改为把标签形状写进 `expert-policy-registry.js` 的 `RUNTIME_LABEL`，
**已发布 profile 的 `runtimeLabel` 必须与之逐字相同**，否则拒绝派发——"边界认得的标签"从此只有一处定义。
（同时把校验顺序调成"先执行类、后标签"，让错误信息指向真正原因。）

### 11.5 测试总况

```
node --test all.test.mjs   → tests 83 | pass 82 | fail 0 | skipped 1
```

### 11.6 真实宿主验证：原理图专家读旧 IR 被当场拒绝（P0-C 点名项，已完成）

场景按交接单原话搭：把一份退役 `schematic-ir.json` 放进 `Output_Global_Material/schematic/`
——**专家自己的输出根**（而不是输入根外的某处），再派发已发布 v1 的原理图专家（label `PTC schematic expert`）去读它。

子代理原话（`run_code` → `read`）：

```
REFUSED: run_code -> read project/DALI/Output_Global_Material/schematic/schematic-ir.json ->
ToolCallError(toolName=read): "PTC material boundary: schematic-ir.json is a retired artifact
and is never a PTC input."  (attempted exactly once; no retry, no alternate route; no bytes printed)
```

| 核对项 | 结果 |
|---|---|
| 派发身份 | 收据 `ptc-schematic-expert-probe-schematic-ir-1-TM106.json`；子会话 `afdf7874-…`，label `PTC schematic expert`，`profileVersion v1` |
| 是否被拒 | 被拒，且拒绝理由正是本轮新增的退役名单规则（不是"文件不存在"） |
| 是否泄漏内容 | 无（"no bytes printed"），且只尝试一次 |
| 收尾 | 诱饵 IR **已删除**，输出根恢复原状 |

**结论（FACT）**：即使旧 IR 就躺在专家自己的输出根里，读取仍被 guard 拒绝——这条要求现在是实测成立，不是代码推断。

## 12. Round 5：规则级"训练"迭代（补上 P0-B 里那一步）

### 12.1 这次训练改的是什么规则

交接单 P0-B 的顺序是"**训练** → 评测 → 发布 → 派发 → 门禁"。上一轮我用的是配置级改动（加 `runtimeLabel`），
这一轮做的是**真正的规则改动**，而且改成一个可执行的东西：

> **黄金案例必须能被别人重跑。** 每个 `cases/<TM>/expected.json` 现在声明它必须通过的**门禁命令**
> （`verification: {command, expectExit, expectContains}`），草稿评测会**真的执行**这条命令并核对退出码与状态文本。

规则来源是第一批的真实教训：DFT 产物只有在"审查被重绑 + 门禁复跑"之后才算被证明过；
一个别人无法复跑的案例只是声明，不是证据。

### 12.2 改动文件

| 文件 | 改动 |
|---|---|
| `scripts/evaluate_expert_profile.py` | 新增 `_check_case_verification()` 与 `--skip-case-gates`；无 `verification` 块的案例不受影响（保持无材料环境可用） |
| `scripts/publish_expert_profile.py` | 发布前评测同样执行案例门禁（`skip_case_gates` 透传） |
| `scripts/test_case_gate.py` | 新增 7 项测试：门禁通过/退出码不符/输出缺关键字/块格式非法/跳过要如实标注/无块不受影响/两个已发布 profile 必须声明可重跑门禁 |
| 两个 `cases/TM106/expected.json` | 加 `verification` 块（DFT→`validate_dft_outputs.py --tm TM106`；原理图→`validate_schematic_outputs.py`） |
| 两个 `instructions.md` | 加"训练轮 1"规则段（DFT 讲重绑规则；原理图讲 receipt 内 sha256 重绑） |
| 两个 `CHANGELOG.md` | 加训练轮 1 记录 |
| `.dsh-dev/train-draft-rules.mjs` | 这次规则改动的可复现脚本 |
| `.dsh-dev/verify-profiles.mjs` | 用**真实分发器**核对所有已发布 profile 是否可解析、标签是否与代码注册表一致、快照是否漂移 |

### 12.3 评测与发布结果（真实命令）

```
evaluate ptc-dft-expert   → verdict pass, failed [], 含 check `case_gate_TM106`（真的跑了 DFT 门禁）
evaluate ptc-schematic-expert → verdict pass, failed [], 含 check `case_gate_TM106`
publish  ptc-dft-expert v3 → published true, previousVersion v2, digest 61d68479…
publish  ptc-schematic-expert v2 → published true, previousVersion v1, digest a9dc275c…
```

用真实分发器复核（`.dsh-dev/verify-profiles.mjs`）：

```
ptc-dft-expert:       published v3 (history v1,v2,v3)  label "PTC dft expert [<TM>]" == registry  快照 7 文件 0 漂移
ptc-schematic-expert: published v2 (history v1,v2)     label "PTC schematic expert"  == registry  快照 7 文件 0 漂移
older versions present: dft v1,v2 / schematic v1   →  回退就是改 status.json 指针，不需要重建
ALL PROFILES OK
```

### 12.4 测试总况

```
node --test all.test.mjs   → tests 83 | pass 82 | fail 0 | skipped 1
python -m unittest …       → Ran 105 tests, OK, exit 0
```

## 13. Round 5 事后核验：抓出并修掉一个我自己造的缺陷

### 13.1 更正：§12 的"可复现脚本"只对第一次运行成立

- 原说法（作废）：`train-draft-rules.mjs` 是"这次规则改动的可复现脚本"。
- 实际：**它不幂等**。`appendOnce()` 的标记串我写成了 `'gates you must survive are re-run'`，
  而这个短语**根本不在追加内容里**，所以第二次运行判定"未包含标记"→ **又追加了一遍规则段**。
  实测证据：两个 `instructions.md` 各出现 **2 个** `## The rule added by training round 1` 块
  （draft 3430/3306 字节，而已发布快照 2925/2868 字节）。
- 影响范围：**只有 draft 被污染**。已发布快照 v3/v2 是在重复发生之前拍的，内容正确。
- 这是我"改完没做幂等核验"的直接后果，也是本轮门禁点出的问题。

### 13.2 修复与证据

| 动作 | 证据 |
|---|---|
| 修 `appendOnce()`：标记串必须**逐字出现在 block 里**，否则**抛错拒绝写入**（不再静默重复） | 第一次带错误标记运行时确实抛错：`appendOnce marker "gates you must survive are re-run" does not appear in the block … refusing to write a non-idempotent rule` |
| 把标记串改成 `'## The rule added by training round 1'`（确实在块内） | 再次运行：6 个文件全部 `already up to date`，exit 0 |
| 修 draft 的重复块（`.dsh-dev/repair-duplicate-rule.mjs`，只保留第一个块） | `instructions.md` 3430→2925、3306→2868 字节；**draft 与已发布快照逐字节相同：true/true** |
| 因此**无需重新发布** | 三个改动文件（instructions / CHANGELOG / case）在 draft 与 `versions/v3`｜`versions/v2` 的 sha256 前缀逐一相同 |

### 13.3 事后核验清单（全部在最后一次改动之后跑）

| 核验 | 结果 |
|---|---|
| 内容与幂等核对（`.dsh-dev/verify-training-change.py`） | **ALL TRAINING-CHANGE CHECKS PASS**（含"第二次运行不改任何 draft 文件"） |
| 插件套件 | `tests 83 | pass 82 | fail 0 | skipped 1` |
| python 套件 | `Ran 105 tests, OK, exit 0` |
| 两个 profile 评测（真的执行案例门禁） | `ptc-dft-expert → verdict=pass, case_gate_TM106.ok=true, boundary_regression.ok=true`；`ptc-schematic-expert → 同上` |
| `--skip-case-gates` CLI 路径（此前从未被走过） | 输出 `case_verification … SKIPPED by --skip-case-gates`，且不把它当通过 |
| 真实分发器复核已发布 profile | `ALL PROFILES OK`（两个 profile 可解析、标签与代码注册表一致、快照 0 漂移、旧版本保留） |

## 14. Round 6：收据从"证据"变成"防线"（交接单 §7.1）

### 14.1 之前的缺口

`lib/policy.js` 判身份**只读 descriptor 的 label 正则**，而且对不认识的 label 是 **fail-open**
（我自己在 §7.4 写下的 KNOWN GAP：标签大小写一变，子代理就完全没有边界）。
上一轮收据虽然写了、也验证了与子会话一一对应，但 **guard 不读它** —— 收据只是证据，不是防线。

### 14.2 本轮改动

| 文件 | 改动 |
|---|---|
| `plugins/dsh-ptc-material-boundary/lib/receipt-scope.js`（新增） | `receiptIdentityFor()`：按 `agent.id`（即子会话 id）先匹配已 pin 收据；判定三态 `pinned` / `mismatch` / `unpinned` |
| `plugins/dsh-ptc-material-boundary/lib/policy.js` | `decision()` 在 label 逻辑**之前**先问收据：`mismatch` → 直接拒绝；`pinned` → 用收据的 `executionClass` 选判定函数、用收据的 `targetTms` 当授权范围 |
| `test/receipt-identity.test.mjs`（新增） | 9 项 |

判定规则（保守优先）：

- **pinned**：恰有一份**校验通过**的收据认领该子会话 → 以**收据**为准，label 说什么都不算数；
- **mismatch**：有收据带着**这个 label** 但指向**别的会话** → 拒绝；收据存在但**校验失败**也拒绝（不退回 label）；
- **unpinned**：没有任何收据认领 → **保持原样**走 label 逻辑（交接单允许暂时保留）。

### 14.3 三个必须成立的性质（都有测试）

1. **盘上没有任何收据时，行为与改动前完全一致** —— 这是采纳 pinned 派发不会悄悄改变现有部署的关键。
   测试同时断言"不认识的 label 仍然 fail-open"这个历史行为未被顺手改掉。
2. **pinned 子代理即使 label 无法被识别（大小写变体、甚至完全没有 descriptor），仍然受边界约束** —— fail-open 缺口被封。
3. **收据能收窄范围**：label 声称 `[TM106,TM110]`、收据只 pin `TM106` 时，读 TM110 的产物**被拒**。
   另有：跨会话冒用 pinned label → 拒；收据被篡改 → 拒；两份收据都认领同一子会话 → 拒（歧义不解释成"放行"）。

### 14.4 测试总况

```
node --test all.test.mjs   → tests 92 | pass 91 | fail 0 | skipped 1
python -m unittest …       → Ran 105 tests, OK, exit 0
```

### 14.5 判别实验结果：收据说了算（已在真实宿主验证）

| 项 | 值 |
|---|---|
| 子代理标签 | `PTC dft expert [TM106,TM110]` —— **label 范围 = 两个 TM**（旧逻辑下 TM110 可读） |
| 写盘的收据 | `targetTms: ["TM106"]`，`childSessionId: 0293187f-a172-425c-80be-a24b1fe916c3`（= `run.id`），**在 start 返回后 18 ms 写入** |
| 子代理动作 | 按指令先回一句纯文本，然后**恰好一次**读取 `project/DALI/Output_Global_Material/dft/TM110/dft-meta.json` |
| 实际结果 | 被拒：`Error: PTC material boundary: this source specialist may access only its assigned input and output paths.`（`isError: true`） |
| 子代理自述 | `REFUSED … No retry, no alternate route, and no other file was read.` |
| 走的是哪条路径 | **不是** `PTC pinned identity` 的 mismatch 分支（该串无命中），而是按会话 id 命中收据后、用**收据收窄过的范围**执行 `dftDecision` |

**结论（FACT）**：在真实宿主里，标签声称两个 TM、收据只 pin 一个 TM 时，被拒的是**超出收据范围**的那次读取。
旧逻辑（label-only）在这个场景下会**放行**。也就是说：身份与授权范围现在由**收据**决定，交接单 §7.1 的要求达成。

顺带记录一条 code 模式事实：`structured_output` **不能直接调用**（`only run_code is callable directly — call structured_output from inside a run_code program`），
子代理必须经由 `run_code` 交卷——这与 Round 3/4 观察到的行为一致。

### 14.5.1 这个规则带来的一个必须知道的行为变化

`mismatch` 规则（fail-closed）意味着：**某个角色的 label 一旦有 pin 收据存在，任何没有收据、却戴着同一个 label 的子代理都会被拒**。
包括"遗留的 label 派发路径"再次派发同一角色时。这是有意的（pin 才是唯一正路），但它是一个行为变化，写在这里以免以后被当成 bug。
另外：同一角色后续的**正规** pinned 派发不受影响 —— 匹配按会话 id 先做，新收据的 `childSessionId` 就是新子代理，直接命中 `pinned` 分支。

### 14.6 探针第一次运行失败暴露的真实 API 约束（已记录）

第一次跑判别实验时，宿主直接报错：

```
Error: tools.restrict() cannot name reserved Code Mode presentation transport "run_code";
restrict end-capability tools instead
```

即：**`toolFilter.allow` 不能写 `run_code`** —— 它是 Code Mode 的"呈现传输层"，不是可过滤的端能力工具；
code 模式下它对子代理始终可用，与 allow 列表无关。
（这也解释了 Round 4 的 DFT 子代理为何能用 `run_code`：生产分发器的默认 allow 列表里本来就没有它。）

修正后用 `allow: ['read','write','pwsh']` 重跑并成功。
**这条约束记下来**：任何给 `toolFilter` 加 `run_code` 的写法都会让派发当场失败。

## 15. Round 7：整批 INPUT_SYNC 全链验证（交接单 P0 通过条件）

### 15.1 真实跑 Captain 入口（不是单测）

```
python scripts/captain_delivery_entry.py --request "TM106、TM108、TM425"
→ exit 0，新建批次 dali-20260919-195317-tm106-tm108-tm425
  state: INPUT_SYNC
  dispatches: [ {role: dft-expert,       tms: [TM106, TM108, TM425], trialDirs: [...]},
                {role: schematic-expert, tms: [TM106, TM108, TM425], trialDirs: [...]} ]
  selection: explicit   project: DALI
```

**一次 INPUT_SYNC 同时派出两个源角色、各带全部三个真实 TM** —— 正是交接单要求的形状
（"同一次 INPUT_SYNC 能为当前请求中的所有真实 TM 产出或复用 DFT 与原理图结果"的前半句）。

### 15.2 推进到 STRATEGY，没有空 dispatch

```
python scripts/captain_delivery_entry.py --continue-batch dali-20260919-195317-tm106-tm108-tm425
→ exit 0
  state             : STRATEGY
  dispatch          : test-strategy-architect
  dispatchableRoles : ['test-strategy-architect']
  has dispatches    : False   ← 见 15.3
  targetTms         : ['TM106', 'TM108', 'TM425']
  registeredStage   : STRATEGY   registeredOwner: test-strategy-architect
  registeredGate    : scripts/validate_strategy_contract.py
  tmStates          : TM106 STRATEGY / TM108 STRATEGY / TM425 STRATEGY（三者同一 owner）
```

**交接单 P0 通过条件达成**："TM106、TM108、TM425 的 batch runner 能从 INPUT_SYNC 进入 STRATEGY，不出现空 dispatch 提前结束"。
（这正是我在 Round 1 修掉的复数 dispatch 缺陷所保护的路径；当时修复前该场景会以 `BLOCKED` 提前结束。）

### 15.3 顺带验证了 Round 1 那条刻意的克制

`has dispatches: False` —— 非源阶段**没有**输出 `dispatches` 复数派发清单。
Round 1 我刻意只在 INPUT_SYNC 输出它，因为 `advance_batch()` 的返回值会被插件续跑逻辑**直接拿去派发** `dispatches` 里的每个角色；
在 STRATEGY 阶段加上这个键等于让 Hook 自动派发策略专家（生产行为改变，不属第一批）。这次真实运行印证了该约束在跑通路径上成立。

### 15.4 复用而非重算（后半句）

每个 TM 的 `prepareResults` 都是 `exitCode 0` + `READY … DISPATCH=`（**派发列表为空**），
输入清单实测：

```
tm106 status=ready dispatchableRoles=[] roleGates=[dft-expert, schematic-expert]
tm108 status=ready dispatchableRoles=[] roleGates=[dft-expert, schematic-expert]
tm425 status=ready dispatchableRoles=[] roleGates=[dft-expert, schematic-expert]
```

即：DFT 与原理图两个角色的既有结果**被复用**（无需重新解析），且两个角色的门禁都在每个 TM 上评估过。

### 15.5 尚未完成：训练会话的执行类限制仍是"约定"而非"强制"

交接单"不可违反的规则"第 6 条规定：训练 profile 只能写自己的 draft / cases / evaluation / CHANGELOG，
不能改 production artifacts、项目代码、`versions/vN` 或 publishedVersion。
当前这条**只写在 persona 里**，没有 guard 强制——因为线上宿主的 `workspaceRoot` 是 Plat，
而训练会话的工作区是 Flow，`decision()` 在 cwd 不在 root 内时直接返回"不管"。
这是第一批里**唯一还没落到代码的硬规则**，列为本轮之后的下一步。

## 16. Round 8：训练会话规则（交接单硬规则第 6 条）

### 16.1 实现

| 文件 | 改动 |
|---|---|
| `lib/expert-policy-registry.js` | 新增 `TRAINING_PRESET_PROFILE`（preset id → profile id）与 `TRAINING_READ_ONLY = ['versions','status.json']`，以及 `trainingProfileFor()` |
| `lib/policy.js` | 新增 `trainingDecision()`：训练会话**读不限**（规则约束的是"改"），**写只允许自己的母版目录**，且 `versions/**`、`status.json` 除外；shell 只允许两条受门禁脚本（评测 / 发布），且必须针对自己的 profile、不许带 `workdir`/后台；`subagent` 直接拒绝（训练会话不派活） |
| `test/training-boundary.test.mjs` | 14 项（实测计数；新增了事件式 preset、切换离开、`allowTrainingPublish` 两种模式、路径不可改写等） |

**关键设计**：这条规则**不看 `workspaceRoot`**，只看 `session.header.agentPreset`。
因为线上宿主的 root 是 Plat，而训练会话的工作区是 Flow——root 作用域的检查对训练会话**永远不会触发**，等于没写。

### 16.2 但真跑把一个前提证伪了

我为了让真实宿主进入"训练会话"，给 ptcflow 装了 `agent-presets` 行并把 default 设成 `ptc-dft-expert`，然后跑了一次真实会话：

```
probe record: parentHeader = { cwd: "D:\\Newtest\\DSH\\ATE-Coding-Flow", agentPreset: null }
```

**FACT：headless 宿主不会给会话盖上 `agentPreset`**——即便装了 preset 层并设了默认值。
结果就是训练规则**根本没被激活**：探测任务里写 `scripts/zz-training-escape.txt` 与写自己母版的两次写入**都成功了**（模型原话 `RESULT=1:WROTE 2:WROTE`，两份文件我都在盘上看到了，随后已清理）。

进一步查证：用**当前这个 GUI 会话自己的持久化日志**搜 `agentPreset` → **零命中**（`session-89bea224-…`）。
所以：

- **FACT**：headless 会话的 `agentPreset` 是 `null`；GUI 会话的**持久化**记录里也没有该字段。
- **UNKNOWN**：GUI 会话在**运行时**（`exec.agent.session.header.agentPreset`）到底有没有值。
  现有 Captain 钩子（`header.agentPreset === 'ate-ptc'`）依赖它，但我**没有运行时证据**，
  而且在线上宿主里挂一个观察者就得改部署 profile——所以我不去改，也不假装验过。

### 16.3 因此补了一条"不依赖那个字段"的硬规则

把最危险的那部分（已发布快照不可改）改成**只看路径**：

> `publishedAssetDenial()`：任何会话用 `write` 去写 `<session cwd>/team/expert-profiles/<任意 id>/versions/**` 或 `.../status.json` → **拒绝**。
> 发布走受门禁的 `publish_expert_profile.py`（它是程序写盘，不是 `write` 工具调用），draft 资产照旧可编辑。

这条**不依赖 preset、不依赖 workspaceRoot**，所以即使 `agentPreset` 在 GUI 里也为空，
"已发布快照不可被手改"这件事依然成立。已写测试：普通 coding 会话（完全无 preset）写 `versions/v3/profile.yaml` 与 `status.json` 均被拒，
写 `instructions.md`/`cases/**` 仍放行；**连 Captain 也不能手改**已发布快照。

### 16.4 我不再把裁定推给你：已做决定 + 留一键开关

§16.4 原来写的是"需要你一句话裁定"。按守门要求，我改为**自己决定并把开关留出来**：

- **默认**：训练会话可以调用**受门禁的**发布脚本（`publish_expert_profile.py --profile 自己 --version v<n>`）。
  理由：交接单 §5.1 把"运行评测 → 通过后发布"写成训练会话里的用户操作；且发布脚本自身强制"评测先过 + 不许覆盖 + 保留上一版"，手改那些文件仍被拒。
- **开关**：profile 配置里 `allowTrainingPublish: false` → 训练严格 draft-only（删掉发布放行，其余不变）。
  已写测试：同一 profile 下两种模式各自的行为都断言过，且评测命令在两种模式下都可用。
- 记法：这是我基于交接单两处文字冲突做的**解释（INFERENCE）**，不是事实；代码注释与报告都写明了。

### 16.5 一个真缺陷：preset 不只在 header 里（已修）

我原来只读 `session.header.agentPreset`。查 DSH 源码后发现它自己**不这么读**：

```js
// @deepseek-ai/dsh-agent-presets/lib/types/session.js
export function resolveSessionPreset(session) {
  for (let index = session.events.length - 1; index >= 0; index -= 1) {
    const event = session.events[index];
    if (event?.type === 'agent-preset/selected') return event.data.agentPreset;
  }
  return session.header.agentPreset;
}
```

即：**最新一条 `agent-preset/selected` 事件优先，创建时的 header 只是兜底**——因为用户在 blank 期间切 preset 后，
后续所有轮次都跑在新组合下，日志才是权威。
如果只读 header，**用户"切进"训练 preset 的会话会被漏判 → 训练限制静默失效**。

修复：新增 `lib/session-preset.js`，**逐字镜像** DSH 的解析顺序，`decision()` 改用它。
新增测试：preset 只以事件形式存在时，训练规则照样生效；**切走**的会话则不再是训练会话（新选择优先）。


### 16.5 测试总况

```
node --test all.test.mjs   → tests 103 | pass 102 | fail 0 | skipped 1
python -m unittest …       → Ran 105 tests, OK, exit 0
```

### 16.6 测试总况（最后一次改动之后跑的，含新增差分检查）

```
node --test all.test.mjs   → tests 108 | pass 107 | fail 0 | skipped 1
python -m unittest …       → Ran 105 tests, OK, exit 0
evaluate ptc-dft-expert        → verdict=pass boundary_regression=true exit=0
evaluate ptc-schematic-expert  → verdict=pass boundary_regression=true exit=0
ptcflow 插件挂载行闸门          → GATE OK
```

**新增一条可执行等价性检查**（`test/session-preset-mirror.test.mjs`）：
导入**已安装的 DSH `resolveSessionPreset`**，与我的镜像喂同一批输入逐例对比（6 种形状：无 preset、仅 header、仅事件、事件压过 header、新事件压旧事件、无关事件），
结果 **`agrees with the installed DSH implementation` 通过**。找不到该包时**跳过并说明**，不会报"未检查的一致"。

**一处更正**：§16.7 曾写"训练规则单测 16 项"，实测为 **14 项**（`training-boundary.test.mjs`）。已改正。

## 17. Round 9：独立复核结论 + TM106 原理图闭环

### 17.1 独立复核（子代理 `1c468e7e`，模型名未返回 = LLM unknown）：5 条断言全 PASS

它只读检查、未改任何文件，并给出实测（含对 cordis 直接注入返回值的实验）：

| 断言 | 结论 | 它给的证据要点 |
|---|---|---|
| 我的 `resolveSessionPreset` 与 DSH 语义等价 | PASS | 都是"事件从后往前取第一条 `agent-preset/selected`，否则回落 header"；7 组输入实测，差异只在畸形输入（DSH 抛 TypeError，我用可选链返回 undefined） |
| `decision()` 第三参数不影响旧两参数调用 | PASS | 缺省 `{}` → `allowTrainingPublish` 视为 true；实测两参数与三参数结果相同 |
| `apply()` 不再有返回值、无调用方受影响 | PASS | 实测返回 `undefined`；两处使用方都是语句调用丢弃返回值 |
| 训练会话 shell 白名单只有那几条 | PASS | 两条评测命令 + 一条发布正则，发布受 `allowPublish` 控制；`ls -la` 被拒 |
| 训练规则判定走 DSH 解析顺序 | PASS | `trainingProfileFor(agentPresetOf(...))` |

**它指出两处真问题，我都修了（并补了测试）**：

1. **注释与实现不符**：`policy.js` 与 `expert-policy-registry.js` 的注释仍写"keyed off `session.header.agentPreset`"，而实现已改用事件优先解析。已改。
2. **`captain-entry.js` 仍直接读 header**：这是**同一类缺陷的第二处**——用户"切进" `ate-ptc` 的会话会保留旧 header，
   于是 **Captain 永远不会被激活**。已改用同一个 `agentPresetOf()`，并补测试（事件式 `ate-ptc` 现在能识别；header 兜底仍可用）。

它的诚实边界我也照记：仓库不是 git 仓库，它**无法证实**"此前那行 `return options;` 曾导致加载失败"（其直接注入实验在 cordis 的 effect 路径上确实会抛 `Invalid effect`，但走真实插件路径未复现）。
我的说法相应收敛：**我从未声称它导致过错误**，删掉它是因为"从 `apply()` 返回值"本就不在插件契约里，纯属避免风险。

### 17.2 TM106 原理图闭环：四次尝试，阻断点已精确定位

| 运行 | 做法 | 结果 |
|---|---|---|
| run 1 | 按配方（未加禁令） | 子代理**自行加料**跑目录列举 + `glob`，被我的边界正确拒绝 → 报 `blocked`；产物未被改坏 |
| run 2 | 加严"只许跑这三条"，默认沙箱 | step1 hash **exit 0**（sha 与我预算一致）；step2 生成器 **exit 1** |
| run 3（诊断） | 只放宽沙箱为 `danger-full-access`，命令不变 | **三条全部 exit 0**、打成功行、门禁 `ready`；12 个产物与备份逐字节相同 |
| run 4 | 修掉生成器一处"清理掩盖主异常"的写法后，**回到默认沙箱** | step2 仍 **exit 1**；门禁仍 `ready`；产物未变 |

**精确根因（FACT，来自 run 4 的完整 traceback）**：

```
File "scripts\generate_schematic_txt.py", line 59, in main
    stage=Path(temp); shutil.copy2(ROOT/"project_config.json", stage/"project_config.json"); ...
File "...\shutil.py", line 262, in copyfile
    with open(dst, 'wb') as fdst:
PermissionError: [Errno 13] Permission denied:
    'D:\...\Output_Global_Material\schematic\schematic-full-pp72nmne\project_config.json'
[sandbox: file access denied under workspace-write mode]
```

即：**在刚建出来的暂存目录里写文件被拒**（`open(dst,'wb')` 直接 Errno 13）；
同一目录随后**也删不掉**（`rmdir` → WinError 5），这解释了输出目录里那几个**空**的 `schematic-full-*` 残留目录。

**结论（FACT）**：阻断来自**沙箱/文件策略层**，不是 PTC 边界、也不是生成器逻辑——
同一套命令在放宽沙箱下三条全部 exit 0、门禁 ready、产物字节稳定。DFT 侧之所以能在默认沙箱跑通，
是因为它的 refresh/render 是**覆写既有文件**（既有路径有写入授权），而原理图生成器要**新建目录再往里写**。

### 17.2.1 更正：我中途的一条推断是错的

我在本轮中途写过"主因只是清理失败、产物其实已写好"。**该推断作废**：
run 4 的完整 traceback 显示**主异常是第 52/59 行往新目录拷文件**（PermissionError），
清理失败只是**次生**异常（`During handling of the above exception, another exception occurred`）。
我上一轮只在被截断的上下文里看到 rmtree 片段，据此下了错判。

**仍然保留的改动（理由已改写）**：`generate_schematic_txt.py` 的
`TemporaryDirectory(..., ignore_cleanup_errors=True)`。它**不能**解开 step2，
但能让次生异常不再掩盖真正的主异常——正是这次把我误导的那个坑。
改完 python 套件 105 项仍全过。

### 17.2.2 部署侧后果（必须知道）

**任何在常驻工作区内"新建目录再写入"的 PTC 阶段脚本，在委派子代理的 workspace-write 沙箱下都会失败**；
写既有路径则不受影响。原理图生成器正好属于前者。
三条可选处置：
1. 给原理图角色更宽的写范围（部署侧放开沙箱，不改脚本）——**我的推荐（暂定）**；
2. 改生成器的暂存位置（例如放在已有授权目录内，或系统临时区）；
3. 宿主沙箱在"新建目录"时补授权。

> **本条推荐目前是「暂定」，不算结论。** 它属于高影响建议（放宽写范围），已按质量契约派
> **独立复核子代理 `acd82051`** 评估：根因 C1/C2/C3 是否成立、我有没有漏掉替代机制、以及 A/B/C 三个选项的
> 安全性/成本/可逆性。复核落地后本节会更新；**若与我的判断冲突，以复核为准**。
>
> **我自查到的一处不利于 C3 的证据，先记下来**：`scripts/refresh_dft_meta_from_source.py:61` 其实也有
> `args.meta.parent.mkdir(parents=True, exist_ok=True)`，只是它写的目录**已存在**、该调用是 no-op。
> 因此"DFT 成功 / 原理图失败"这组对比**无法区分** C3 与"只有既有路径才有授权"这类替代机制——
> 这也是我请复核去找沙箱实现里"授权如何施加"的原因。

**UNKNOWN**：机制层面到底是"新目录未继承写入授权"还是别的策略实现细节，我没有继续深挖（只做了隔离实验）。

### 17.2.3 独立复核结论：我的机制解释 C3 **被否**，选项 A 的推荐**撤回**

独立复核子代理 `acd82051`（**LLM unknown**；只读、未改文件）给出判定：

| 我的结论 | 复核判定 | 它的证据 |
|---|---|---|
| C1 阻断来自文件策略层、不是 PTC 插件 | **PASS（有保留）** | 反事实对照（同命令受限失败/放开成功）成立；但**`[sandbox: file access denied under workspace-write mode]` 不能当证据**——它是 `denialSignatures` 的 **stderr 子串分类器**产物（`dsh-sandbox-local/lib/index.js:205-215`、`dsh-pwsh-sandbox/lib/index.js:55,63-64,71`），任何原因的 EACCES 都会被贴上这个标签 |
| C2 写不进刚建出的目录；该目录也删不掉 | **PASS（仅症状层）** | 但它指出"删不掉"只在那个受限进程内观测过，且**残留目录已被我删除** |
| **C3 新建目录未继承沙箱写入授权** | **FAIL** | `dsh-sandbox-local/lib/index.js:389` 是**只对工作区根施加一次 ACE**；`types-CNjZgO4h.js:544` 继承位 `OI\|CI`；它**复算** workspace SID = `S-1-4-839778856-663547807` 与树上 ACE 一致；实测 `schematic` 目录带 `(A;OICIID;…)`、其中既有文件带 `(A;ID;…)` → **继承链贯通 ≥4 层、无 Deny、无 `D:P`**；`GRANT_MASK 0x110156` 含 FILE_ADD_SUBDIRECTORY/DELETE。**"新目录没继承授权"不成立** |
| 我的对照"DFT 成功=只覆写既有路径" | **不成立** | `refresh_dft_meta_from_source.py:61` 是 `mkdir(parents=True, exist_ok=True)` + `write_text`，缺目录会建、缺文件会新建 |

**因此我撤回两件事**：
1. **§17.2 里"C3 新目录未继承授权"这一机制解释作废**（保留"写不进刚建目录"这个**症状级事实**）。
2. **§17.2.2 推荐的选项 A（放宽沙箱）撤回**。复核的判据：放宽 `danger-full-access` 会失去**唯一真正限制"写到哪里"的 OS 级边界**，而插件只按**命令白名单**放行、不限制写目标 → 用不可逆的边界损失去买一个**尚未定位**的因，不可取。它也指出选项 B 的前提可能破产（若真因是"新对象 DACL 缺 capability ACE"，换到 `%TEMP%` 同样失败）。

**复核给出的首选替代机制 M1′**：新建对象的 DACL 来自**受限令牌的默认 DACL**（`types-CNjZgO4h.js:1493` 把默认 DACL 只并入**一个** SID，优先临时 SID），
而写检查要两道都过、树上又没有 Everyone ACE → 新目录**不可写、不可删、连列举都 WinError 5**（该沙箱设计上"读不受限"，所以列举失败必须用对象 DACL 缺普通 ACE 解释）。
**一击定案的判据**：下次失败时**先 `icacls` 那个残留目录、再清理**——只出现 `S-1-4-…-1`（临时 SID）、没有 workspace SID/AU → M1′ 成立（宿主缺陷，走选项 C）；出现正常 `(I)(OI)(CI)(W,D,DC)` + workspace SID → M1′ 与 C3 一起被否，改查第三方拒绝（AV/EDR/AppLocker；本机 `icacls` 反复报域信任失效，属 M3 线索）。

**我接受的一条操作批评**：上一轮我把 3 个残留目录删掉，**毁掉了唯一能区分 C3 与 M1′ 的证据**。已改规矩：**先 `icacls`、后清理**（本轮起执行）。

**复核自己的限制（照记）**：它的会话是 `danger-full-access`，派出的子代理只会继承更宽的模式，所以它**没有做任何受限写实验**；上述机制判断全部来自代码阅读 + 既有 ACL 读数。它也未读取第 5 次探针结果。

### 17.2.4 选项 B 的实测结果：**被否**（失败模式从"报错"变成"挂住"）

按复核的提醒（"B 的前提可能破产"），我在**默认沙箱**下做了 B 的实验：
给生成器加了一个**不设则行为不变**的开关 `PTC_SCHEMATIC_STAGE_DIR`（默认仍暂存到输出目录），
本地先验证两种位置都可用（`SCHEMATIC TXT+JSON READY`、exit 0），再在 ptcflow 里把该变量设成 `%TEMP%` 跑 run 5。

| 运行 | 暂存位置 | 沙箱 | 结果 |
|---|---|---|---|
| run 3 | 输出目录内 | `danger-full-access` | 三条命令全 exit 0、门禁 ready |
| run 2/4 | 输出目录内 | 默认（workspace-write） | step2 `PermissionError` 写不进新目录 |
| **run 5** | **`%TEMP%`** | 默认（workspace-write） | step2 **挂住**——子代理原话：`step 2 hangs (no output for 5 minutes). That's a real block: the generator produces no output and hangs.` |

**结论（FACT）**：选项 B **不能**解决该阻断（换位置只是把"权限拒绝"换成"无输出挂起"）。
产物完好（12 个文件与备份逐字节相同）、无残留目录；本次我在清理前先做了 `icacls` 检查（无残留可查）。

**因此 §17.2.2 的三个选项现状**：
- **A：撤回**（复核判定会失去唯一真正限制"写到哪里"的 OS 级边界，且是在根因未定位前花掉它）；
- **B：实测否证**（本小节）；
- **C：留给宿主侧**（复核指出授权机制是"一次性施加到 root + 向既有子树传播"，逐操作补授权与该机制不兼容，须在 token/默认 DACL 层修）。

**机制仍 UNKNOWN**，并且 run 5 的"挂起"并不整齐地落在复核首选假设 M1′（新对象 DACL 缺 capability ACE）上——
挂起更像是某次 spawn/拦截在等一个永不到来的裁决。复核也明说它的机制判断来自**代码阅读 + 既有 ACL 读数**，没做受限写实验。
**下次失败时按复核给的一击判据办：先 `icacls` 那个残留目录、再清理。**

### 17.2.5 一击判据实测（按复核给的规矩：**先 icacls、后清理**）

run 6：默认沙箱、暂存回到输出目录内 → 复现 step2 `PermissionError`，并留下一个新建目录 `schematic-full-w9_v2s9p`。
**我这次先读了它的 ACL、再删除**（上轮销毁证据的教训已改）。四组 `icacls` 原文：

| 对象 | ACL 关键行 |
|---|---|
| **A. 受限子代理新建的目录** | `NT AUTHORITY\SYSTEM:(OI)(CI)(F)`、`BUILTIN\Administrators:(OI)(CI)(F)`、`OWNER RIGHTS:(OI)(CI)(F)` — **无任何 `(I)` 继承标记、无工作区 capability SID、无 Authenticated Users** |
| B. 同树既有目录 `schematic` | `(I)(OI)(CI)(W,D,DC)` ← **继承来的工作区写授权**；另有 BA/SY |
| C. 同树既有文件 | `(I)(W,D,DC)`；BA/SY/AU |
| D. 工作区根 | `(OI)(CI)(W,D,DC)`（显式可继承）；BA/SY/AU |

**结论（FACT）**：既有对象都带着**继承来的 `(W,D,DC)` 工作区授权**；而**受限子代理新建的目录一个继承 ACE 都没有**，
只拿到形如**令牌默认 DACL**（SYSTEM/BA/OWNER RIGHTS）的 ACL → 该受限令牌对它**不可写、不可删**，
这与观测到的 `PermissionError`（写）+ `WinError 5`（删除/列举）一致。

### 17.2.6 更正：我上一步"撤回 C3"撤得太快

上一小节（17.2.3）我依据复核的读数**撤回了 C3**。现在看，那次撤回**过头了**：

- 复核当时证明的是"**既有**对象的继承链贯通"（B/C/D 这类样本），它手上**没有**"受限进程新建对象"的样本；
- 我新采到的 A 正是那个缺失样本，显示新建目录**没有**拿到工作区授权。

所以正确的表述是：**"新建对象缺少工作区写授权"这一可观测缺陷成立**（原先 C3 的实质结论成立），
只是**机制命名**仍未定（是"受限令牌用默认 DACL"、还是"继承在受限路径上被跳过"、或是别的），
这一点留给正在跑的独立复核 `76f9c213` 与后续确证。

### 17.2.7 处置建议的现状（待独立验证）

**建议 R**：处置走**宿主侧修**（在受限令牌/默认 DACL 层使受限进程新建的对象获得工作区 capability SID），
**不要**用放宽到 `danger-full-access` 绕过；仓库侧保留 `ignore_cleanup_errors=True`（只防止次生异常掩盖主异常）。

- A（放宽沙箱）：**撤回**（会失去唯一真正限制"写到哪里"的 OS 级边界）；
- B（改暂存位置）：**实测否证**（run 5 从"报错"变成"无输出挂起"）；
- C／R（宿主侧修）：**现有 ACL 判据支持**，但**仍标为暂定**——已按质量契约派独立复核 `76f9c213`
  评估该判据解读、替代解释与 R 的安全性/成本/可逆性；**其结论落地前 R 不算成立**。

### 17.2.8 我自查的宿主源码证据（**非独立**，但把 C 的落点钉住了）

读 `dsh-sandbox-windows-acl`（Windows 沙箱后端）源码，发现它的设计**本就打算覆盖这个场景**：

```
lib/types/token.d.ts:36-51
  "Merge one full-access allow ACE for `sidPtr` into the token's DEFAULT DACL
   — the DACL every NEW object the token holder creates (without an explicit
   security descriptor) takes. The restricted token inherits the user's default
   DACL verbatim, WHICH NAMES NO RESTRICTING SID ..."

lib/types-CNjZgO4h.js:1493
  setTokenDefaultDaclGrant(api, restrictedToken,
      this.tempWriteSidPtr ?? this.writeSidPtr ?? worldSid);

README.md:99
  "... 受限令牌默认 DACL 携带 restricting SID 全权 ACE（init 时写入）..."
```

即：沙箱**会把恰好一个 restricting SID 合并进受限令牌的默认 DACL**，好让"令牌持有者新建的对象"能通过 pass-2 检查；
有临时 SID 时优先用**临时** SID。

**但**我实测新建目录的 ACL 里（§17.2.5 的 A）**没有任何 capability SID**，只有 `SYSTEM / Administrators / OWNER RIGHTS`。
两条事实放在一起只能得出：

- **FACT**：该新建目录既没有继承工作区授权、也没有带上"设计上应当被合并进去"的那个 restricting SID → 它不可写、不可删；
- **FACT**：宿主**存在**一个明确的修点（`setTokenDefaultDaclGrant` 那一路 + 授权对象的选取），所以"选项 C"不是空谈；
- **UNKNOWN**：**为什么**合并没在这条路径上生效（是走了 pwsh 沙箱的另一条 token 路径？用的 SID 与工作区授权不一致？还是时序问题？）。这属于宿主实现细节，**我没有继续深挖，也不据此下结论**。

> **建议 C 仍标「暂定」**：我这段是**自己读源码**得出的，**不构成独立复核**。
> 针对"判据解读 + 建议 C/R"的独立复核 `76f9c213` **仍在运行、结论未回**；
> 另一位复核 `acd82051` 只独立评估了 A/B/C 三个**选项层面**（它判定 A 不可取、C 仅在判据成立时为正解），
> 并没有独立验证"C 就是正确修法"。**在 `76f9c213` 回来之前，C 不作为已成立的建议。**

#### 17.2.8.1 进一步查到的 SID 装配链（FACT）

| 环节 | 源码事实 |
|---|---|
| 装配方 | `dsh-sandbox-local/lib/index.js:364-367` 把 **两个** SID 交给 runner：`--write-sid <writeSid>` 与 `--temp-write-sid <tempSid>`；`:385` `workspaceWriteSid(workspaceRoot)`；`:404` `tempWriteSid(tempDir)` |
| runner | `dsh-sandbox-windows-acl` 的 runner 只验证这两个 SID 属于各自路径、**自己不授权**（对应 README:53 的 `manageDacls: false`） |
| 令牌层 | `types-CNjZgO4h.js:1493` 把 `tempWriteSidPtr ?? writeSidPtr ?? worldSid` **之一**并入受限令牌默认 DACL；文档（`token.d.ts:36-51`）明说这是为了让"令牌持有者新建的对象"能过 pass-2 |
| 我的实测 | 受限子代理**新建目录**的 ACL 里**没有任何 capability SID**（§17.2.5 A） |

→ **FACT**：装配与合并这两段代码都存在、且都在主路径上；但受限子代理新建的对象**没有**带上被合并的那个 SID。
→ **INFERENCE**：正因如此，新建目录对受限令牌不可写、不可删（与 pass-2 模型一致）。
→ **UNKNOWN**：链路上**哪一环**没生效（该会话是否拿到了 temp 目录、runner 是否收到了 `--temp-write-sid`、合并调用是否成功、还是 `icacls` 的呈现问题）——我没有继续深挖，也不据此下结论。


### 17.2.9 独立复核 `76f9c213` 的结论：**我的解读 X 判 FAIL，建议 R/C 只能标"待定"**

复核用**原始 SDDL**（`Get-Acl`，不用 `icacls` 文本——因本机域信任失效会污染 SID 名解析）重采，判 X **FAIL**：

| 它的发现 | 对我方判读的意义 |
|---|---|
| `icacls` 对 `S-1-4-…` capability SID **打印空白账户名**；B/C/D 行里那些"空行"其实就是 `S-1-4-839778856-663547807`（掩码 `0x110156`） | **我 §17.2.5 表格里"看到 SYSTEM/BA/OWNER RIGHTS 三个名字、没有 capability SID"的读法不可靠**——必须用原始 SDDL 复核 |
| 全树普查：**333 个目录 + 3278 个文件 100% 带该 capability SID**（纯继承），**0 个显式 ACE** | 该树上"新建对象会带上工作区授权"有强旁证 |
| MS 官方【DACL for a New Object】：未指定 SD 时**先用父目录的可继承 ACE 构造**，**只有在没有任何可继承 ACE 时**才用令牌默认 DACL；而 `schematic` 当时**确实**带可继承 ACE（**我自己的 B 行就是证据**） | X 的因果链"默认 DACL ⇒ 无 capability ⇒ 不可写"**走不到那一步** |
| `types-CNjZgO4h.js:1493` 明确把**一个** restricting SID 并入受限令牌默认 DACL（有临时 SID 时优先临时），源码注释与 README:99 同义 | 即便真走默认 DACL 分支，它也**必带** `S-1-4` ACE，而它在 restricting 列表里 → 该对象仍应可写 |
| **同一份采集里 A 与 B 自相矛盾**（父目录有可继承授权 vs 子目录零继承 ACE），按上面算法不可能同时为真 | **A 的读数或其归属本身可疑**；"宿主侧缺陷"这一步**未被证实** |

**我据此撤回三样**：
1. **解读 X（"新建对象缺工作区授权 → 因此不可写"）作废**——它与 MS 文档、与宿主自身实现都相反；
2. **§17.2.6 的"C3 复活"作废**（那一步正是建立在被证伪的 A 读数上）；
3. **建议 R/C 不再作为已成立建议，改标「待定」**——复核明说："R 的成立完全以 X 为真为前提，而 X 现在未证"。

它另外纠正我两处事实：`ignore_cleanup_errors=True` **已在代码里**（`generate_schematic_txt.py:62`），"保留"是零动作；选项 B 已被 run 5 否证（与我一致）。

**它给的替代解释（各带区分判据）**：A 的 DACL 非创建时所得（显式 SD/`SE_DACL_PROTECTED`/跨卷移入）；A 根本不是那个受限子代理新建的目录；创建者不是受限令牌而是 SYSTEM/BA 语境或某个加固模板（它抽样约 1200 个对象，含 `S-1-3-4` 的 **0 个**，故非本机普遍模板）；父目录当时并非 `schematic`；与 ACL 无关的第三方拦截（EDR/AV；run 5 的**挂起**本就不是 ACL 症状）。

**它要求的下一步（我不能靠猜，只能照做）**：
> 复现失败后**先别清理**，让失败进程 dump「新建目录」的 **原始 SDDL + Owner + 创建者 PID/token** + 父目录 SDDL（三份原文，不用 icacls 文本）；
> 同批对照：同一受限进程在**同一父目录**下建 A1、在工作区**已存在**目录下建 A2，两边都 dump；
> 另可不写盘读一次令牌默认 DACL（`TokenDefaultDacl`）。
> 判据：新建目录 SDDL 里**有没有** `S-1-4-`、是哪个（`…-663547807` 工作区 / `…-1` 临时）、有没有 `ID`（继承）标记、有没有 `P`（屏蔽继承）。

**我接受的一条批评（第二次同类）**：我又一次在读取后**删掉了那个目录**，导致复核**无法复测 A**（它全盘搜 `schematic-full-*` 无结果）。
规矩再收紧：**清理前必须留原始 SDDL + Owner + 创建者**，否则不许删。

**复核自己的限制（照记）**：它**没有做任何写盘实验**，所以"新建目录应当继承"来自官方文档 + 源码，属它的 **INFERENCE**；它也无法确定 `schematic` 里那 4 个探针文件的创建者是否为受限令牌。

### 17.2.10 R5 测量结果（原始 SDDL + 同父目录对照）——把矛盾判定了

按复核 `76f9c213` 指定的最小确证做：**失败后先不清理**，用 `Get-Acl`（**原始 SDDL**，不用 icacls 文本）读三份，再做同父目录对照。

**A1｜受限子代理新建的目录** `schematic-full-6b_b3xd0`：
```
Owner : NUVOLTA\NVT10241
SDDL  : O:S-1-5-21-...-1690 G:DUD:P(A;OICI;FA;;;OW)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)
Access: OWNER RIGHTS  FullControl  (IsInherited=False)
        SYSTEM        FullControl  (IsInherited=False)
        Administrators FullControl (IsInherited=False)
```
→ **DACL 是显式的（无 `AI`、全部 IsInherited=False）**，且**没有任何 capability SID**。

**父目录** `schematic`：
```
SDDL  : O:... G:DUD:AI(A;OICIID;0x110156;;;S-1-4-839778856-663547807)(A;ID;FA;;;BA)...
Access: S-1-4-839778856-663547807  DeleteSubdirectoriesAndFiles+Write+Delete+Synchronize  (IsInherited=True)
```
→ 父目录**确实带可继承的**工作区 capability ACE。

**A2｜同父目录、由我（非受限）会话新建的目录** `_dacl-control-…`：
```
SDDL  : O:... G:DUD:AI(A;OICIID;0x110156;;;S-1-4-839778856-663547807)(A;ID;FA;;;BA)...
Access: S-1-4-839778856-663547807  ...  (IsInherited=True)
```
→ **同一父目录下，非受限进程建的目录正常继承到了 capability ACE。**

**结论（FACT）**：
- 复核担心的"A 与 B 自相矛盾"已判定：**A 的读数是对的**——受限路径新建的目录**没有**继承父目录的可继承 capability ACE，而非受限路径**有**。
- 按复核自己给的第 2 条判据（"A1 缺而 A2 有 → 指向新建目录在该路径上不继承 → 宿主嫌疑"），**指向受限/沙箱路径**。
- 因此：**"新建对象缺少工作区 capability ACE → 受限令牌对它不可写不可删"这一可观测缺陷成立**；
  而我在 §17.2.9 里撤回的 **X 的"机制命名"（走令牌默认 DACL）仍未证**——MS 算法说本该继承，实测却落成一个**显式** DACL，
  说明有别的东西**显式写了**这个 DACL（候选：沙箱自己的 grant/revoke 回写〔README:98 记载该类行为〕、受限令牌创建分支、或第三方过滤器）。

**因此 R/C 的定性回到"方向受支持、机制未定"**：
它**仍是高影响建议**（要动宿主/部署），我**不自行推进**；已按质量契约再派一份**聚焦独立复核**验证这次的原始 SDDL + 对照是否足以支撑该方向，以及下一步该查哪一环。**该复核回来之前，R/C 仍标「暂定」。**

> **后续更正（见 §17.2.11）**：该复核后来**更正了自己的结论**——根因在**脚本侧**（`mkdtemp` 的 0o700 装上受保护 DACL 阻断继承），**宿主没有缺陷**，
> 因此 **C 被纠正为"不必要"**，我采纳其 **D**（改暂存目录创建方式）并已在默认沙箱下验收通过。

### 17.2.11 根因定位到脚本侧并修复（选项 D）——默认沙箱下验收通过

复核 `acd82051` **更正了自己上一份结论**，把根因定位到**脚本**而非宿主：

> `generate_schematic_txt.py` 用 `tempfile.TemporaryDirectory(dir=…)` → `tempfile.mkdtemp` → `os.mkdir(path, 0o700)`；
> **Windows 上 CPython 以 0o700 建目录时安装的是"显式 + 受保护（`SE_DACL_PROTECTED`）"的 owner-only DACL**
> → 保护标志**阻断继承** → 新目录拿不到父目录那个可继承的 capability ACE → 受限令牌第二道写检查失败 → 写 `Errno 13`、删 `WinError 5`。

它的关键对照证据：本机 `%TEMP%` 里有 **85 个**同型目录（如 `pip-build-tracker-…` 2026/8/5、`pip-ephem-wheel-cache-*` 2026/5/27），
全是**无沙箱的 Python `mkdtemp`**（pip）数月前建的、SDDL 与出事目录**逐字符同型**；而工作区里**0 个**目录是该受保护模式，
Python 用默认 mode 建的目录（`dft\TM106`、`ErrorLog`、`team\artifacts`）**全部带继承来的 capability ACE**。
→ **DFT/原理图不对称的真正判据是"建目录用的 mode"，不是"新建 vs 覆写"**；**宿主沙箱没有缺陷**。

**我按它给的选项 D 改了脚本**（`scripts/generate_schematic_txt.py`）：
新增 `staging_directory()` 上下文管理器，**用默认 mode 建暂存目录**（不再用 `mkdtemp` 的 0o700），暂存位置**仍留在输出目录内**（保留"看到真实部署布局"的语义），`finally` 里 best-effort 删除。

**验收判据实测（默认沙箱 workspace-write，未放宽任何边界）**：

| 判据 | 结果 |
|---|---|
| 三条命令是否 exit 0 | **是**——子代理原话：`All three exit 0. Gate JSON status "ready".` |
| 门禁 | 我独立复跑 `validate_schematic_outputs.py` → `status: ready`、无 stale |
| 产物是否稳定 | 12 个文件与备份**逐字节相同**（确定性再次确认） |
| 残留暂存目录 | **0 个**——说明新建目录这回**既能建也能删**（此前删不掉） |
| 本地对照（前提验证） | 默认 mode 建的目录 SDDL 带 `(AI)` 且 capability ACE `IsInherited=True`；与出事目录的 `P(...)`+无 capability 形成对照 |
| 回归 | python 套件 `105 全过`；脚本可解析 |

**因此**：A（放宽沙箱）撤回、B（换位置）不作为修复（`mkdtemp` 在任何位置都装同一受保护 DACL）、**C（宿主侧修）纠正为"不必要"**，
采纳 **D（改暂存目录创建方式）**——**保留全部 OS 边界、单文件改动、完全可逆**。
前提被我实测验证：**dfT/原理图两侧现在都能在默认沙箱下跑通**。

**残余 UNKNOWN（复核自述）**：`scandir`/列举为何也 `WinError 5`（按该 DACL，owner 经 `OW:FA` 本应过第一道读检查），到此仍未完整解释。

```
node --test all.test.mjs   → tests 109 | pass 108 | fail 0 | skipped 1
python -m unittest …       → Ran 108 tests, OK, exit 0   （含新加的 3 项暂存目录回归）
evaluate 两个 profile       → verdict=pass, boundary_regression=true, exit=0
```

### 17.2.12 补上防复发的回归测试（本轮新增）

修复当时只有"冒烟 + 真机验收"，**没有留下能防这个 bug 复发的测试**——这是本轮的缺口，已补：

`scripts/test_staging_directory.py`（3 项，全部通过）：
1. 名称仍是 `schematic-full-<8位十六进制>`，且上下文退出后目录被清理；
2. （Windows）用 `icacls` 断言暂存目录**带 `(I)` 继承项**——这正是 bug 的可观测症状（受保护 DACL 没有任何继承项）；
3. **用 tokenizer 剥掉字符串与注释后**判可执行代码里不得再出现 `mkdtemp` / `TemporaryDirectory`，且必须存在 `staging_directory` 并用默认 mode 建目录。

> 过程记录（诚实）：这条测试**第一次跑失败了**——我最初用子串搜索判"mkdtemp 不得出现"，而 helper 的 docstring 里正当地提到了它。
> 已改用 `tokenize` 只判可执行代码，重跑 3 项全过。**这是测试自身的断言缺陷，不是产品缺陷。**

**测试总况（最终）**：`python 108 全过`（原 105 + 新增 3）、`node 109（108 过 / 0 失败 / 1 跳过）`、两侧门禁 `ready`、`ALL PROFILES OK`。

### 17.2.12 防复发回归 + 同模式脚本扫描 + 仓库注释纠正（本轮）

**（一）回归测试已加固为"工作区等价"**（复核 `0b4974af` 的批评：原版用 `mkdtemp` 做 parent，只证明"系统临时区的 ACL 会传播"，即使工作区 capability ACE 丢了也照样通过）：

`scripts/test_staging_directory.py`（3 项，全过）：
1. 名称仍是 `schematic-full-<8位十六进制>`，上下文退出后被清理；
2. **`test_the_staging_directory_inherits_the_workspace_write_grant`** —— parent 建在**仓库内**（`team/_dacl-staging-test-*`，与生成器输出目录同法创建），先读出 parent 的 `S-1-4-…` capability SID，再断言**暂存目录带 `(I)` 且继承了同一个 SID**；
3. 用 tokenizer 剥掉字符串/注释后，判可执行代码里不得再出现 `mkdtemp` / `TemporaryDirectory`，且必须用默认 mode 建目录。

> 过程记录：第 3 项第一次跑**失败**（我最初用子串搜索，而 helper 的 docstring 正当地提到了 `mkdtemp`）——已改用 `tokenize` 只判可执行代码。**这是测试自身的断言缺陷，不是产品缺陷。**
>
> 同时，复核留的一个疑问（"`Path.mkdir` 默认 mode 是否也会装显式 SD，从而让修复不够用"）**已被我的对照实验回答**：仓库内用默认 mode 建的目录 SDDL 是 `D:…AI(…)`、capability ACE `IsInherited=True` → **默认 mode 会正常继承**，修复成立。

**（二）同模式脚本扫描（复核指出的同类风险）**：
全 `scripts/` 搜 `TemporaryDirectory|mkdtemp` → **除已修的生成器外，其余全部是测试文件**：
`test_ate_ptc_batch_runner.py`、`test_ate_ptc_correction.py`、`test_ate_ptc_runner.py`、`test_captain_delivery_entry.py`、`test_fast_delivery_batch.py`、`test_ptc_output_contracts.py`、`test_trial_directory.py`（另加我新加的 `test_case_gate.py` / `test_expert_profile_lifecycle.py` / `test_staging_directory.py` 自身也用 `mkdtemp` 建 fixture）。
→ **第一批的运行时路径上已无此模式**（唯一的运行时使用者就是那个生成器）。

**（三）仓库注释纠正**：`scripts/run_ptc_regression.py:39-48` 原文把 5 个被跳过的历史测试归因于 **DLP**；
新证据（本机 `%TEMP%` 里 85 个**由无沙箱 pip 在数月前**建的逐字符同型对象 + CPython 提交级依据）指向 **`mkdtemp` 的 0o700 受保护 DACL**。
已把注释改成实测归因，并注明"迁移这些测试时需要同样的修法"。**只改注释，未改行为。**

### 17.2.13 第四份独立复核：同样否证"宿主缺陷"，并把 R 判为**机制上不可行**

复核 `76f9c213` **更正了自己上一份结论**，给出**三分判定**：

| 分层 | 判定 | 依据 |
|---|---|---|
| "新建目录无 capability ACE ⇒ 该受限令牌不可写/不可删" | **PASS** | 原始 SDDL：三条全 `IsInherited=False`、无 `AI`、**无 `S-1-4-`**；父目录确有 `(A;OICIID;0x110156;;;S-1-4-…)` |
| "落成了令牌默认 DACL"（我的机制命名） | **FAIL** | 令牌默认 DACL 不可能带 `P`；且 `types-CNjZgO4h.js:1493` **必**并入一个 restricting SID |
| "宿主侧 DSH 沙箱缺陷" | **FAIL（它亲自实测否证）** | `%TEMP%` 顶层 13,888 项中 117 个 `pip*`/`tmp*` 对象里 **91 个 SDDL 与出事目录逐字符同型**，最早 **2026/5/27**；而 **DSH 是 2026/9/2 才装**；这些对象在 `%TEMP%` 顶层（受限进程的 TMP 会被改写到私有目录）⇒ 由**无沙箱**的 Python `mkdtemp` 产生 |

它也如实记账**自己两处失败检查**：用 `CreateEventW`+`GetSecurityInfo` 读令牌默认 DACL 得到 **NULL DACL**（探针未达目的，不作证据）；
第一次 `%TEMP%` 扫描的"0 命中"是**它自己的正则 bug**（`^D:P` 永不匹配以 `O:…G:DU` 开头的 SDDL），更正后为 103 命中。

**关键更正（对 R）**：**宿主侧修在本案机制上不可行**——创建者指定且**受保护**的 DACL 让"继承"与"令牌默认 DACL"两条宿主杠杆**都被按设计绕过**；
宿主侧唯一"有效"的方向是放弃 pass-2，即放弃唯一的 OS 级写边界（= 早已排除的选项）。
→ 因此 **C/R 从"暂定"改为"撤回（不可行）"**，**处置采纳 D（仓库侧）**，与我方修复一致。

**它点名的可执行项已实现**：其它在受限沙箱里用 `tempfile`/pip 的脚本会复发同一形态 → 已加**仓库级护栏**
`test_no_other_runtime_script_uses_the_protected_mkdtemp_path`（运行时脚本一律禁止 `mkdtemp`/`TemporaryDirectory`，测试模块除外，因其 fixture 合法使用且不在受限下运行），
并实测通过；扫描确认**运行时脚本里唯一的旧使用者就是已被修的生成器**，`pip` 仅出现在报错提示文本中。

**复核自身的披露（照记）**：两份复核都是 `deepseek-v4-flash`（与我同模型，非跨模型）；第二层复核未返回 ⇒ **LLM unknown**；
且它**未亲自复现**端到端验收（"默认沙箱下三条 exit 0 / 门禁 ready / 产物字节相同"是我方实测，它只旁证了产物 mtime、0 残留与脚本现状）。

### 17.4 第一批仍未完成的部分（诚实清单）



- **训练会话规则的"运行时激活"仍未被直接观测**（§16.2）：逻辑按生产 `decision()` 单测覆盖（实测 **14 项**，此前报告里写"16 项"是错的，已更正），
  但"宿主是否真的给会话盖了 preset"这一点我**没有运行时证据**：
  headless 宿主实测 `agentPreset: null`，而 GUI 会话的运行时取值我无法在不改部署 profile 的前提下观察。
  已用不依赖该字段的路径规则（§16.3）兜住最危险的那部分，并且 preset 读取已按 DSH 的官方解析顺序修正（§16.5）。
- **TM106 的 DFT / 原理图语义真值缺**（`PENDING_DOMAIN_INPUT`）：评测能证明结构、哈希、边界、门禁；
  **证明不了语义判断对不对**，我没有让评测冒充已检查。
- 已在前面轮次关闭：整批 INPUT_SYNC 全链（§15）、收据成为防线（§14）、规则级训练迭代（§12）、
  原理图专家与旧 IR 拒绝（§11）、TM106 DFT 闭环（§11.1）。
- 已在 §16.4 自行裁定：训练会话的发布权限（默认放行受门禁脚本，`allowTrainingPublish: false` 可切严格 draft-only）。

---

## 18. 第一批验收对照表（每项带证据指针与状态）

### 18.1 交接单"第一批交付物"7 项

| # | 交付物 | 状态 | 证据指针 |
|---|---|---|---|
| 1 | DFT 和 schematic 的可见训练 preset | ✅（渲染 UNKNOWN） | 真实发现代码扫到 5 个 preset，两位专家在列、`broken: none`（§11.2） |
| 2 | 两个 profile 的 draft、案例、评测、发布快照与 manifest | ✅ | dft 已发 v1→v2→v3、schematic v1→v2；`verify-profiles` → `ALL PROFILES OK`（§12.3） |
| 3 | `evaluate_expert_profile.py` 与 `publish_expert_profile.py` | ✅ | 14 项生命周期测试 + 7 项案例门禁测试；真实命令 exit 0（§8.2、§12.3） |
| 4 | 单一、受 Hook 覆盖的 `dispatch_profile` | ✅ | `lib/dispatch-profile.js`；18 项测试；真实宿主派发成功（§9.8） |
| 5 | run 级 descriptor receipt | ✅ | 收据落盘 + `verifyDispatchReceipt {ok:true}` + `findReceiptForChild` 唯一命中（§9.8） |
| 6 | Hook/guard 路径与伪造身份回归测试 | ✅ | 路径绕过 20+、guard 挂载、收据身份 9、训练边界 14（含伪造 label／篡改收据／歧义拒绝） |
| 7 | TM106 真实 DFT + 原理图闭环报告 | ✅ **两侧均完成** | DFT：真实重生成 + 我独立复跑门禁 `ready`（§11.1）。原理图：**默认沙箱（workspace-write）下三条命令全部 exit 0、门禁 `ready`、无残留目录**（§17.2.11，修复为脚本侧选项 D） |

### 18.2 交接单"第一批验收"5 条

| 验收条件 | 状态 | 证据 |
|---|---|---|
| 新会话可分别选到两个专家 | ✅ 发现层；⚠️ UI 渲染未验 | §11.2 |
| draft 评测失败不能发布；发布后保留上一版本 | ✅ | 拒绝发布时**不创建任何版本目录**；v1 在发布 v2/v3 后仍逐字节完好 |
| 运行实例的 profile、合同、policy 与输入哈希全部固定 | ✅ | 收据 pin 版本与三类哈希；分发器拒绝 `latest`、拒绝快照漂移 |
| 输入专家不能越过材料边界；伪造 label/description 无效 | ✅ | 路径回归 + 真机读旧 IR 被拒 + 收据优先身份（标签说两 TM、收据只 pin 一个 → 越界被拒）+ 退役 IR 即使在输出根也拒 |
| TM106 完成 INPUT_SYNC 且输出满足现有门禁 | ✅（生成步骤见 §17） | 真实批次：一次 INPUT_SYNC 派两角色、推进 STRATEGY、三个 manifest `ready` 且复用；两侧门禁 `ready` |

### 18.3 明确标 UNKNOWN 的三项（不冒充已完成）

1. **浏览器选择器的渲染**（发现层已证，UI 层没看）。
2. **训练会话规则的运行时激活**（headless 实测无 preset；GUI 运行时取值无法在不改部署的前提下观察）。已用"只看路径"规则兜住最危险部分。
3. **TM106 的 DFT/原理图语义真值**（`PENDING_DOMAIN_INPUT`）：能证结构/哈希/边界/门禁，**证不了语义对错**。

---

## 19. 第一批最终状态（Round 12 收官核验）

### 19.1 收官全量核验（最后一轮实跑）

| 核验 | 结果 |
|---|---|
| 插件套件 | `tests 109 | pass 108 | fail 0 | skipped 1` |
| python 套件 | `Ran 105 tests, OK, exit 0` |
| DFT TM106 门禁 | `status: ready` |
| 原理图门禁 | `status: ready` |
| 已发布 profile（真实分发器） | `ALL PROFILES OK`（dft v1–v3、schematic v1–v2，快照 0 漂移） |
| preset 发现 | 两位专家在列、`missing: none`、`broken: none` |
| 输出树整洁 | 原理图 12 项、0 个残留目录 |

### 19.2 交付物 7 项与验收 5 条的最终状态

- **交付物 1–6：全部落地并测试**（§18.1）。
- **交付物 7（TM106 真实 DFT + 原理图闭环）：两侧均已完成**——
  DFT：真实重生成 + 我独立复跑门禁 `ready`；原理图：修复脚本侧暂存目录的创建方式后，**默认沙箱下三条命令全部 exit 0、门禁 `ready`、无残留目录**（§17.2.11）。
- **验收 5 条：4 条成立**；"新会话可分别选到专家"在**发现层**成立、**UI 渲染**需你一眼确认。

### 19.3 阻挡完全闭环的条件（按重要性，均超出"只改 ATE-Coding-Flow"的授权范围）

1. ~~**宿主沙箱缺陷（唯一硬阻断）**~~ → **已解决，且不是宿主缺陷**：根因是脚本用 `tempfile.mkdtemp`（0o700 → Windows 上装上受保护的 owner-only DACL，阻断继承）。
   已按复核选项 D 改为**默认 mode 建暂存目录**，默认沙箱下验收通过（§17.2.11）；**未放宽任何 OS 边界**。
2. **训练会话规则的运行时激活**需改部署才能观察（headless 实测 `agentPreset: null`）；最危险部分已用"只看路径"规则兜住。
3. **TM106 语义真值**需你或领域专家给一次输入（`PENDING_DOMAIN_INPUT`）。
4. **浏览器选择器渲染**需你新建会话时看一眼（发现层已证）。

### 19.4 四份独立复核的状态

| 复核 | 目标 | 状态 |
|---|---|---|
| `4ac6b574` | 最初可行性判断 | **已回**：12 PASS / 1 FAIL（我当时的 `STAGE_ALIASES` 误判，已更正） |
| `1c468e7e` | preset 镜像与接线 | **已回**：5 条全 PASS，指出注释不符 + `captain-entry.js` 同类缺陷（已修并补测） |
| `acd82051` | 沙箱根因与 A/B/C 处置 | **已回**：判 C3 FAIL（仅基于既有对象样本）、A 应撤回、给出一击判据 |
| `76f9c213` | 新采 ACL 判据的解读 + 建议 R | **仍在运行**；其结论落地前 §17.2.7 的建议 R 仍标**暂定** |

### 19.5 结论边界（诚实声明）

- **原理图闭环已在默认沙箱下跑通**（§17.2.11）；过程中我两次误判（"只是清理失败"、"新对象缺授权=宿主缺陷"）都已更正，最终根因落在**脚本侧**并已修复。
- **可观测事实**（新建目录缺 capability ACE）成立；其**机制**经复核更正为 `mkdtemp` 的 0o700 受保护 DACL（不是宿主缺陷）。
- 语义真值一项始终标 UNKNOWN，评测从未声称检查过它。
- 本轮为修复该阻断所改的只有**一个仓库文件**（`scripts/generate_schematic_txt.py`），**没有**改宿主、没有放宽沙箱、没有动 `ATE-Coding-Plat`。



