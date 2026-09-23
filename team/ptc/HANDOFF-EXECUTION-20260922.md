# 执行交接文档 —— ATE PTC 专家体系与面板建设（2026-09-22 会话）

> 交接范围：DFT 专家 v5 发布、Captain 职责配置、专家控制台面板（开批 + 专家状态表）、TM108/TM109 批次执行进展。
> 撰写时刻：2026-09-22 约 17:00（本地）/ 08:48 UTC。面板服务在线（http://127.0.0.1:4090，HTTP 200）。

---

## 一、我们做了什么

### 1. DFT 专家体系建设（v1 → v5）

- **训练文件夹体系模板**：落地到 `team/expert-profiles/ptc-dft-expert/`，含 cases/TM106 等样例（expected.json 等）。
- **训练规则提案评审与定稿**：Trainer 报告对账完成，规则写入 profile。
- **五项 DFT_Expert 提案**：全部经中介代执行完毕。
- **新合同正向验证 + 四坑裁定 + gate 改造**：全部落地（patch-policy / patch-gate 系列脚本在 scratchpad 留档）。
- **增补卡 [29][30][31]**：全部落地并验证通过。
- **v5 发布**：7 文件快照，manifestDigest `1d979ac50ab13bce92414fe19b4dd7d7ceea5905a8525cd2d8ca17f4aede7673`，previousVersion=v4。合同、gate、边界三层完全对齐，**可跑正式交付**。

### 2. Captain 职责配置（指令层 + 编排层）

- `AGENTS.md` Captain entry 节 6 条 → **8 条**：新增半导体测试项目前置预处理（四项项目事实输出 + 确认规则）、三类输入文档识别（原理图 CSV / DFT 表 / CBIT 表，规则强信号优先、冲突才会话内推理）作为 INPUT_SYNC 前置判定。
- `team/ptc/CAPTAIN_ENTRY_FLOW.md`：追加「Semiconductor preprocessing (workflow part 1)」节（注意：该文件为 TSZ 编码，追加须用 python utf-8-sig round-trip，不可 shell 重定向）。
- `team/ptc/.captain-project-cache.json`：项目地址簿初值取自已批准 `Project_Info.json`（输入 `project/DALI/Input_GlobalMaterial`、输出 `Output_Global_Material`、VS 工程 `D:/PROJECT6-DALI/ForCodexDebug/source`，三份文档 Dali-SCH.csv=原理图 / Dali_testmode.xlsx=DFT / CBIT表-DALI.xlsx=CBIT）。**发布流程与训练模式共用此文件**（用户已确认的一份地址簿方案）。
- 面板「🧭 Captain 职责」页签 + `GET/POST /api/captain/config`：可编辑层①行为规则与层②阶段编排（`ptc_stage_registry.json` 7 阶段），层③（captain-entry.js 强制层）只读展示。全部实测通过（含守卫与自动备份）。

### 3. 专家控制台（面板 + 后端桥）

**后端 `tools/expert-console.mjs`（端口 4090）：**

- 既有端点：/api/state、/api/receipts、/api/captain/config、/api/batch/advance、/api/evaluate、/api/publish、/api/roster、/api/train-rule、/api/proposal/apply、/api/bindings/mode、/api/trainer/send、/api/trainer/poll。
- **Captain 桥（本次新增）**：`ensureCaptainSession`（session.create，agentPreset=`ate-ptc`）+ `POST /api/captain/send`（TM 编号守卫：空文本 400、首条无 TM 400）+ `GET /api/captain/poll` + /api/state 返回 captain 字段（sessionId/lastReply/pending/promptAt）。
- **批次状态与专家状态表数据源**：/api/state 聚合最新批次（最新回执 mtime vs 最新批次目录定位 batchId）、阶段（advance-handoff.json）、specialists（回执 + DSH 子会话 activeMs<90s 判 RUN/IDLE）。

**前端 `team/ptc/prototype-expert-console.html`（5 页签，约 493 行）：**

- 页签：①总览 ②🏃 DSH 运行 ③训练 ④发布 ⑤🧭 Captain 职责。
- 「🏃 DSH 运行」页签：最新批次流水线卡片 = 8 段流水线图 + **专家状态表**（专家/版本/目标 TM/状态/派发时间，5 秒自动刷新，🏃 跑动中=子会话 90s 内有写入，💤 已静默 N 分钟）+ 回执表 + 唤醒 Captain 按钮。
- 「🧭 Captain 职责」页签顶部：**开批卡片**（📋 填入模板 + 🚀 开批 + ⟳ 刷新回复 + 日志区；capKick/capPoll/capKickPreset/capPollOnce，5s 轮询，turn/end 停轮询）。
- 同步文档：`team/ptc/HANDOFF-EXPERT-CONSOLE.md` 已含全部功能描述。

### 4. 批次实际执行

- **`dali-20260922-152339-tm108`（旧批，已完成）**：Schematic_Expert v2 + DFT_Expert v5 双双交活，PTC 门禁全过。用户要求只跑到 DFT 解析（INPUT_SYNC），未推进策略阶段——符合预期终态。
- **`dali-20260922-155636-tm108`（新批，进行中）**：用户经面板再次开批（会话 session-0f0f832c）。文档识别验证通过（三份材料与确认映射一致）；DFT 派工第一次被 PTC 门禁拦下（派工描述须显式声明授权 TM 集合），Captain 自查格式后重派。
- **`dali-20260922-160106-tm109`（排队中）**：TM109 批已建、输入清单已备好，排在 TM108 的 DFT 之后执行。

---

## 二、完成了什么（✅）

| # | 事项 | 验证 |
|---|------|------|
| 1 | DFT_Expert v5 发布 | manifestDigest 核对，三层（合同+gate+边界）对齐 |
| 2 | 训练规则定稿 + 五项提案执行 + 增补卡 [29][30][31] | 全部实测通过 |
| 3 | AGENTS.md Captain entry 8 条 + CAPTAIN_ENTRY_FLOW 预处理节 + .captain-project-cache.json | 面板 GET /api/captain/config 读到新 8 条 |
| 4 | 面板「Captain 职责」配置功能 | GET/POST 全实测（守卫/备份/回写一致） |
| 5 | 后端 Captain 桥（send/poll/状态） | 空文本 400、无 TM 首条 400、poll 正常 |
| 6 | 面板开批按钮 + 输入区 + 5s 轮询 | 服务重启验证（新 pid、4090 监听、HTTP 200） |
| 7 | 面板专家状态表（流水线下方） | 实测显示 SCH v2 / DFT v5 行，RUN/IDLE 正确 |
| 8 | 旧批 152339-tm108 INPUT_SYNC | 双专家交活，门禁全过 |
| 9 | TM108 文档识别环（新批） | Captain 确认三份材料映射一致 |

---

## 三、还没做的（❌/⏳）

1. **⏳ TM108（新批 155636）DFT 解析产物核对**：Captain 最终回复（turn 已结束，pending=false）称 DFT 专家正在后台运行（`PTC dft expert [TM108]`，作业标识 `bbdac8c7-…`），**产物尚未核对**。注意：截至今日 17:00，155636 批次目录下尚无新回执落盘——接手后先 `ls team/artifacts/dispatch-receipts | grep 155636` 确认派发是否真正落盘，再核对解析产物。
2. **⏳ TM109（批 160106）DFT 派发**：输入清单已备好，排队中，尚未执行。
3. **❌ 策略及后续阶段（STRATEGY → … → COMPLETE）**：用户明确要求冻结在 DFT 解析（INPUT_SYNC），**不要主动推进**。
4. **❌ 批次监控 watcher 已停止**：dispatch 监控代理在检测到批次切换（152339→155636）后失败/超时退出，当前无活跃监控。如需继续盯，重启面板轮询或重派 watcher。
5. **❌ 悬置假设 F045**：「预处理落盘 AGENTS.md + 同步 CAPTAIN_ENTRY_FLOW.md + 缓存推导默认值」已实际落地，但当时标记为未经交叉验证的 hypothesis——现已通过面板 /api/captain/config 实读验证，可视为已确认（接手人如需严谨可再走一次新会话确认流程）。
6. **❌ 独立审计（FAST_DELIVERY_PENDING_AUDIT 终态）**：本会话未涉及，按 AGENTS.md 规则 Captain 不会自行恢复。

---

## 四、最新进展（截至 2026-09-22 16:48 本地）

- **Captain 会话** `session-0f0f832c-1ff2-4ed6-8b49-9c35d0047feb`（DSH 会话，agentPreset=ate-ptc）：turn 已结束（pending=false），最终回复要点：
  1. 第一环文档识别**验证通过**：`Dali-SCH.csv`=原理图、`Dali_testmode.xlsx`=DFT（含 TM108 行）、`CBIT表-DALI.xlsx`=CBIT 表，与确认映射完全一致；
  2. 第二环 TM108 的 DFT 解析专家**正在后台运行**（作业 `bbdac8c7-…`）；
  3. TM109 已备好输入清单排在下一个发；
  4. 两单冻结在 DFT 解析，策略及之后未动；专家完成通知到后 Captain 会核对产物给最终结论。
- **面板**：服务在线（4090，HTTP 200），当前定位批次 `dali-20260922-160106-tm109`（阶段 `?`：该批尚无 advance-handoff/回执，属正常等待态）。
- **旧批 152339**：终态 INPUT_SYNC 完成，不会再有动静。

---

## 五、接手人快速上手

**入口与操作：**

- 面板：`http://127.0.0.1:4090`（服务由 `node tools/expert-console.mjs` 提供；若掉线，在仓库根重启）。浏览器如显示旧画面，**Ctrl+F5 强刷**。
- 开批：「🧭 Captain 职责」页签顶部开批卡片 → 📋 填入模板（默认 TM108 文案，可改 TM 编号）→ 🚀 开批 → 等「⏳ Captain 处理中…」变为回复文本（或点 ⟳ 刷新回复）。
- 看专家实时状态：「🏃 DSH 运行」页签 → 最新批次流水线卡片 → 流水线图下方专家状态表（🏃=90 秒内在写子会话，💤=已交活/停摆）。

**关键路径速查：**

| 用途 | 路径 |
|------|------|
| 面板后端 | `tools/expert-console.mjs` |
| 面板前端 | `team/ptc/prototype-expert-console.html` |
| Captain 会话状态 | DSH `session-0f0f832c-1ff2-4ed6-8b49-9c35d0047feb`（zstd 会话文件，读法见 expert-console.mjs readCaptainReply） |
| 派发回执 | `team/artifacts/dispatch-receipts/` |
| 批次产物 | `team/artifacts/<batchId>/<tm>/` |
| 项目地址簿 | `team/ptc/.captain-project-cache.json` |
| 阶段编排 | `team/ptc/ptc_stage_registry.json`（唯一权威） |
| Captain 强制层 | `plugins/dsh-ptc-material-boundary/lib/captain-entry.js`（只读，不可面板编辑） |
| 面板功能文档 | `team/ptc/HANDOFF-EXPERT-CONSOLE.md` |

**注意事项：**

- CAPTAIN_ENTRY_FLOW.md 是 TSZ 编码：编辑须 `python -c "open(p,encoding='utf-8-sig').read()"` round-trip，**不可用 shell 重定向**。
- DSH 的 promptAt 机制：新发消息会重置可读窗口，旧回复可能被甩出轮询范围（F097）。
- 面板提案卡片不持久化（F096）：刷新即丢，代发消息不经过面板渲染。
- 派工被门禁拦的已知原因：派工描述里必须**显式声明授权 TM 集合**（Captain 已知悉此格式要求）。

**建议的下一步（按优先级）：**

1. 核对 TM108（155636 批）DFT 解析产物：确认回执落盘 + `team/artifacts/dali-20260922-155636-tm108/tm108/` 下 INPUT_SYNC 产物内容。
2. 跟进 TM109 DFT 派发与执行。
3. 产物核对通过后，向用户汇报两单最终结论；是否推进 STRATEGY 由用户决定（默认不推进）。
