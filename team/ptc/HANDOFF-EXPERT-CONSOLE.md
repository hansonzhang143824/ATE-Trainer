# 交接文档：PTC 专家训练控制面板（对话式训练）

> 交接目的：新会话继续本话题。写作时间 2026-09-21。
> 当前目标（g_022）：对话式专家训练控制面板完整版——桥接服务 ✅ → 面板接真数据 ✅ → Trainer 接入 DSH ✅（最小版）。

## 1. 大背景与总目标

- 终极目标：**单 Agent（非多 Agent 编排）在 DSH 中完成 ATE 测试程序编写全流程**，PTC 模式省 token 提速。
- 已完成基础：8 个专家角色全部迁移并 published（dft v3、schematic v2、其余 v1），roster complete，测试 227 项 225 pass / 2 skip。
- 用户近期需求：**控制面板**——单个专家训练、整体发布、问题纠错、执行状态展示，在 DSH 上运行。
- 已确认采用**对话式训练**模式：用户只提供流程图/知识/吐槽（不手写规则），丢进对话让 Trainer（AI）整理分类、评估落盘位置、生成提案，用户确认后执行资产升级。
- 用户认知框架（重要）：要优化的东西分两类——①**Agent 内部内容**（instructions.md 行为规则、profile.yaml 边界、cases 金标准、output-contract.schema.json）；②**Agent 之间合约**（上下游交接 schema、expected.json、verify 脚本三源一致性）。对话式训练就是补这两类知识的工具。

## 2. 当前架构（三层）

```
浏览器面板 (team/ptc/prototype-expert-console.html, v0.3)
   │  fetch 同源相对路径
   ▼
桥接服务 (tools/expert-console.mjs, Node, 127.0.0.1:4090)
   │  ├─ spawn python → scripts/evaluate|publish|validate_expert_roster.py
   │  ├─ 读文件 → team/expert-profiles/*/status.json、team/artifacts/（批次状态/回执）
   │  ├─ HTTP → DSH web API (127.0.0.1:3080)：session.create/prompt
   │  └─ 轮询解压 → C:/Users/nvt10241/.dsh/sessions/--D-Newtest-DSH-ATE-Coding-Flow--/<trainerSessionId>/session.jsonl.zstd
   ▼
DSH web (端口 3080, preset=web, 含 PTC 插件栈 dsh-ptc-material-boundary + agent-teams)
```

启动命令：`cd D:\Newtest\DSH\ATE-Coding-Flow && node tools\expert-console.mjs` → 浏览器开 http://127.0.0.1:4090/

## 3. 交付物清单（本阶段产出）

| 文件 | 说明 |
|---|---|
| `tools/expert-console.mjs` | 桥接服务 ~230 行，全部 API 实测通过 |
| `team/ptc/prototype-expert-console.html` | 面板 v0.3（Live 版），假数据已全部换真数据 |
| `team/ptc/.trainer-session.json` | Trainer 会话 id 持久化（服务重启不丢上下文） |

| `team/ptc/TRAINING-AND-PUBLISH-GUIDE.md` | 训练/发布通俗讲义（面向不写代码的使用者） |

### 桥接服务 API（已实测）

- `GET /api/state`——8 专家真实版本/草稿状态（draftClean=digest 对比）、最新批次 state（来自 advance-handoff.json，剥 BOM）、DSH 在线探测、trainer 状态。
- `POST /api/evaluate {profile}` → evaluate_expert_profile.py --version draft
- `POST /api/publish {profile}` → publish_expert_profile.py --version 自动算 next（v+1）
- `POST /api/roster` → validate_expert_roster.py（实测 exit 0 complete）
- `POST /api/train-rule {profile, rule, source}`——幂等写入 instructions.md（`<!-- ptc-console:rule id=<sha8> -->` marker）+ CHANGELOG.md，然后自动跑评估
- `POST /api/trainer/send {text}`——转发到 DSH Trainer 会话（session.prompt mode:queue）
- `GET /api/trainer/poll`——轮询解压 Trainer 会话文件，回收 `assistant/message` 文本（需 `turn/end` 且 time > promptAt 才置 pending=false）
- `POST /api/proposal/apply {profile, location, text, source}`——提案卡片后端：instructions.md → trainRule 写入+评估；其他落盘位置 → 幂等暂存到 `team/artifacts/training-proposals.md`（marker `proposal id=<sha8>`）；未知 profile 返回 400
- `POST /api/batch/advance {batchId?}`——跑 `captain_delivery_entry.py --continue-batch <batchId>`（缺省取最新批次），即「唤醒 Captain」；不存在的批次被脚本 BLOCKED（exit 2）
- `GET /api/captain/config` / `POST /api/captain/config {agmd?, registry?}`——Captain 职责配置：读取/回写 AGENTS.md「Captain entry」节（禁止二级标题、长度≤8000）和 ptc_stage_registry.json（stateMachine 顺序锁定不可改；全空且原本不存在的 stages 键不写入，防 COMPLETE 空白行污染）；每次写入前自动备份到 `team/ptc/.captain-config-backups/`；POST 路由必须先判 method（曾有 GET 路由吞掉 POST 的 bug，已修）

### 面板 v0.3 功能

- 顶栏：DSH 在线状态、批次状态、Trainer 状态（5s 轮询刷新）
- 左侧：8 专家列表（版本/draft 是否干净/案例数）；**点击专家 = 设为训练目标**（不切页签），训练页显示目标横幅可清除
- 页签 0 对话式训练：聊天框（Ctrl+Enter 发送）+ 右侧「提案卡片」（Trainer 回复自动按 `[编号] (专家 | 位置 | 形式)` 解析成可勾选卡片，勾选→ `/api/proposal/apply`；全选/全不选切换）+「快捷写入」表单。发送时若选了目标专家，prompt 自动加前缀【训练目标：xxx，材料优先拆解为该专家提案】
- 页签 1 发布：专家下拉 + 版本时间线 + 评估/发布按钮 + 全队状态表
- 页签 2 纠错：A1/A3/B2/B5 问题清单，「转训练提案」按钮把问题文本塞进训练输入框
- 页签 3 DSH 运行：批次流水线（STAGES 数组高亮当前 stage）+ 真实回执列表 +「唤醒 Captain（推进当前批次）」按钮（confirm 后调 `/api/batch/advance`，与 autopilot 兑底同机制，会触发真实派发）
- 页签 4 Captain 职责：① AGENTS.md Captain entry 节文本编辑；② registry 各阶段 owner/gate/families/outputs 表格编辑；③ 只读说明（入口/自动派发在 captain-entry.js，改它需重启 DSH web）。保存即备份
- 已知 UI 状态：聊天记录不持久化（刷新清空，但重新发消息会接上原 DSH 会话，上下文不丢）

## 4. Trainer（核心验证已通过）

- Trainer = DSH 里一个真实会话（preset ate-ptc，cwd=ATE-Coding-Flow），系统提示词内嵌在 expert-console.mjs 的 `TRAINER_SYSTEM` 常量：拆解材料为原子知识点 × 归属专家 × 落盘位置 × 形式，回复格式 `[编号] (专家 | 落盘位置 | 形式) 内容 —— 依据`，不确定标"待确认"，不编造。
- **端到端实测通过**：喂入 A3 问题（dft 产物目录策略：首选 trial，被拒降级 Output_Global_Material/dft/<TM>/，回执留痕）→ 返回 1644 字 6 条提案，含 schema 修复方向、金标准断言、脚本伪代码（标"建议"）、落地顺序 [2]→[1]→[3]→[5]→[4]→[6]、待确认点（"被拒"定义）。
- 当前 trainer 会话 id 存在 `.trainer-session.json`（历史测试会话若干可弃）。

## 5. 关键技术契约（踩过的坑，务必遵守）

1. **DSH web API**（F165）：`POST http://127.0.0.1:3080/api/<method>`，body=`{type:"client-request",rpcId,method,payload}`，Content-Type: application/json。`session.create` payload=`{cwd}` → 返回 `{result:{value:{sessionId,agentPreset}}}`（**sessionId 在 result.value 里，不是顶层**）。`session.prompt` payload=`{sessionId,mode:"queue",content:[{type:"text",text}]}` → `{result:{value:{accepted:true}}}`。注意 create 后立即 prompt 偶发竞态失败，重试即成。
2. **events.mux 不是 SSE**：GET /api/events.mux 返回 426 upgrade required（实为 WebSocket）。回收 Trainer 回复走**轮询会话文件**：`C:/Users/nvt10241/.dsh/sessions/--D-Newtest-DSH-ATE-Coding-Flow--/<sessionId>/session.jsonl.zstd`，多帧 zstd（magic `28 B5 2F FD`），Node `zlib.zstdDecompressSync` 逐帧解压。事件结构：`assistant/message` 的 `data.message.content[].text` 为回复文本，`turn/end` 表示完成（`data.reason.kind==="completed"`）。
3. **TSZ 加密**：项目里 scripts/*.py、status.json 等 DSH 进程写的文件 read_files 读不了（binary rejected），**git-bash 的 python 可透读**（`open(p,encoding='utf-8-sig')`）；lib/*.js、HTML、mjs 为明文可直接编辑。**写文件用编辑工具或 node，别用 PowerShell 重定向**（会密文化）。
4. **本机 PowerShell/curl 的 TLS(schannel) 有问题**，网络调用一律用 Node 的 fetch（外网也要 node -e）。
5. **dsh web 不接受 --profile 参数**：PTC 插件栈必须编在 profiles/web 的 cordis.patch.yml 里（已配置）。
6. **后台进程会被环境清理/换 PID**：会话间后台 node 进程经常消失或 PID 变化，重要状态必须落盘（如 .trainer-session.json）。重启桥接服务：先 `netstat -ano | grep :4090.*LISTENING` 找 PID → `powershell Stop-Process -Id <pid> -Force` → 重启。
7. run_bash 有断路器：同一命令连续失败 5 次会被拒，需换写法或 `LINCO_RETRY_OVERRIDE=1` 前缀。

## 6. 环境与进程现状（交接时点）

- DSH web：3080 在线，加载 web profile（PTC 栈 + agent-teams），主模型 zai-coding-cn/glm-5.3-flash（settings.yaml），ZAI_API_KEY 环境变量已注入进程。QWEN_TOKEN_PLAN_API_KEY 亦已注入（qwen3.8-flash 可用，但未用）。
- 桥接服务：4090 运行中（**重启电脑后需手动启动**，见第 2 节命令）。
- autopilot（PID 12540）：盯批次 dali-20260921-080849-tm106-tm108-tm425 的空壳回归，IDLE 60s 唤醒 Captain；交接时批次卡在 INPUT_SYNC（A4 状态滞后问题再次实证：receipts 已到 METHOD 但 handoff 仍显示 INPUT_SYNC），到 COMPILE 自动退出。**此批次是空壳链路回归验证，非真实交付**。
- Key 管理约定（用户已放宽）：API Key 只要不写进代码文件即可，进程内存注入已满足。

## 7. 未完成 / 下一步（优先级序）

1. ~~提案卡片化~~ ✅ 已完成并实测（解析、勾选执行、instructions 自动写入+评估、其他位置暂存 training-proposals.md、幂等去重）。
1b. Captain 前置预处理职责（2026-09-21，工作流第 1 部分）：AGENTS.md Captain entry 节新增第 2/3 条（四项项目信息+确认规则、三类文档识别+强信号规则+传 INPUT_SYNC 专家作前置判定），CAPTAIN_ENTRY_FLOW.md 追加「Semiconductor preprocessing」节，缓存 `team/ptc/.captain-project-cache.json`（初值取自已批准的 Project_Info.json）。判定策略=规则优先+会话内 LLM 兜底+用户确认把关（不接外部模型，实测不准再议 DeepSeek）。后续第 2/3 部分由用户补充后在同一入口追加。
1c. 训练文件夹体系（2026-09-21，g_005）：`Training_Materials/` 已建成——Input_GlobalMaterial 与 Output_Global_Material **复制**自 project/DALI（训练快照，交付链路原位不动），另有 Setup/Strategic/Method/Implement/Review/Compile_Expert_Output（各含与产物平级的 verification/ 子目录，Setup 用途待定、至少放未来哈希校验结果）、Captain_Check_Output、ErrorLog。绑定关系在 `Training_Materials/_expert_bindings.json`（专家→读/写/校验目录，训练平铺、交付按 TM 分子目录、新项目整包复制为 project/<Project_Name>/）。
1d. 专家改名（2026-09-21）：显示名全面弃用中文，统一为 *_Expert 风格——DFT_Expert、Schematic_Expert、Strategic_Expert、Method_Expert、Review_Expert、Implement_Expert、Compile_Expert、Evolution_Expert。已同步：面板 NAMES 映射（ID_BY_NAME 随之反转）、A3 快捷按钮、Trainer 角色清单（显示名=角色ID，提案用显示名）、TRAINING-AND-PUBLISH-GUIDE.md、_expert_bindings.json（displayName+profileId 双字段）。profileId（ptc-dft-expert 等）仍是派发路由的真实 ID，未改动。桥接服务已重启生效。
1e. 单 profile + 地址簿切根（2026-09-21，[8]定案）：`_expert_bindings.json` 新增 modes（training=Training_Materials / delivery=project/DALI）+ activeMode（持久化，切换即写回）；`expert-console.mjs` 新增 GET/POST `/api/bindings/mode`，且 `/api/trainer/send` 自动在消息头注入当前模式地址簿（各专家读/写/校验目录；可传 noAddressBook 关闭），返回带 injected/mode 字段；面板训练页签 targetBanner 下新增「⇄ 切换训练态/交付态」按钮（loadMode/toggleMode）。全链路实测通过：模式双向切换+落盘、地址簿按根渲染（DFT/Schematic 校验指向 Output_Global_Material/verification/）。DFT/原理图解析校验结果统一写 Output_Global_Material/verification/（dft-*/schematic-* 前缀），不再暂借 Setup_Expert_Output；解析规则文件=User_input/DFT解析规则.txt（已代发 Trainer 纳入规则）。待办：交付侧 captain-entry.js roleTask 拼同款地址簿。
2. ~~训练/发布通俗讲义~~ ✅ 已落盘为 `team/ptc/TRAINING-AND-PUBLISH-GUIDE.md`。
3. ~~DSH 运行页接通驱动操作~~ ✅ 已接通（唤醒 Captain 按钮 + `/api/batch/advance`，带 confirm 防误触）。
4. 空壳回归批次：autopilot 进程已死（交接后未存活）；2026-09-21 通过 `/api/batch/advance` 手动对 dali-20260921-080849-tm106-tm108-tm425 执行 --continue-batch——**生效**，状态从 INPUT_SYNC 修正为 IMPLEMENTATION（A4 状态滞后实锤：脚本按 receipts 重算）。注意：该脚本返回的是**派发计划**（TM108→ate-implementer、TM106→rule-reviewer），真正派发仍需 DSH 内 Captain 会话执行；面板按钮目前只到"刷新状态+出计划"这一层。
5. LINK-REGRESSION-ISSUES.md A 类 8 条（agent 执行流程）+ B 类 8 条（产物合同/schema）——**A 类恰是用户接下来要用面板梳理的内容**（用户原话："有了面板马上开始梳理 agent 执行流程"）。A1 唤醒缺陷未修（autopilot 是兜底非根治）。
6. P5 移除 agent-teams：条件 1 满足，条件 2 简化不深推，条件 3/4 待定。
7. GUI 运行时激活未验证（F051 遗留）：8 角色训练评估只覆盖 TM106 一个案例。

## 8. 用户工作偏好（重要）

- 用户=提需求+判断结果+偶尔授权动作；CodeM=安装/写代码/跑流程/读日志/改错自闭环（F017）。
- 用户不手写规则，一切训练走「喂料 → AI 出提案 → 用户确认」。
- 生成的 HTML 必须自动用浏览器打开（已写入全局规范 .codem/memory/html_auto_open_rule.md）；分析报告输出到 D:\赛美科工程导入\（FT 数据类）。
- 回复风格：简短、直接给答案、关键节点各报一句；用户会挑战估算，估算要把「纯编码时间」和「实验/等待时间」分开讲。
