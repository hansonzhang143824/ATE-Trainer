# 4090 专家控制面板 · 完整设计文档

> 一句话：一个跑在本机的网页控制台，把「专家训练 → 评估 → 发布 → 运行监控」整套 PTC 专家资产管理变成可视化操作。你只负责喂料和拍板，AI 负责拆解、落盘、验证。
> 面板地址：**http://127.0.0.1:4090/**（本机浏览器打开）

---

## 1. 设计想法（为什么长这样）

**核心工作模式：对话式训练。** 用户不手写任何规则，只把流程图、领域知识、执行问题、吐槽随手丢进对话框。Trainer（DSH 里的一个 AI 会话）把材料拆解成原子提案——每条标注「归属专家 | 落盘位置 | 写入形式 | 依据」。用户逐条确认后由面板执行写入并自动跑评估，评估过了再点发布盖章。

**两个优化对象**（用户视角的概念框架）：
- **Agent 内部内容**：专家该怎么干活——instructions.md 行为规则、profile.yaml 边界、cases 金标准案例；
- **Agent 之间合约**：交接物长什么样——output-contract.schema.json、expected.json、verify 脚本三源一致性。

**安全底线**：训练只写 draft（草稿区），不影响生产链路；发布后版本不可变；源文件只读。

## 2. 架构（三层）

```
┌─────────────────────────────────────────────┐
│ 浏览器面板 (localhost:4090)                  │  team/ptc/prototype-expert-console.html
│ 四页签：训练 | 发布 | 纠错 | DSH运行         │
└──────────────┬──────────────────────────────┘
               │ fetch
┌──────────────▼──────────────────────────────┐
│ 桥接服务 expert-console.mjs (Node, 4090)     │  tools/expert-console.mjs
│  ├─ spawn python：评估/发布/roster 脚本      │
│  ├─ 读文件：专家状态、批次状态、回执         │
│  ├─ HTTP → DSH web (3080)：Trainer 会话      │
│  └─ 轮询解压 Trainer 会话文件回收回复        │
└──────────────┬──────────────────────────────┘
               │ DSH web API
┌──────────────▼──────────────────────────────┐
│ DSH web (127.0.0.1:3080)                    │
│ profile=web：PTC 插件栈 + agent-teams       │
│ Trainer 会话 preset=ate-ptc                 │
│ 主模型 zai-coding-cn/glm-5.3-flash          │
└─────────────────────────────────────────────┘
```

启动命令（重启电脑后需手动执行）：
```
cd D:\Newtest\DSH\ATE-Coding-Flow
node tools\expert-console.mjs     → 浏览器开 http://127.0.0.1:4090/
```

## 3. 文件夹安排（全量）

```
D:\Newtest\DSH\ATE-Coding-Flow\
├─ tools\
│  └─ expert-console.mjs            ★ 桥接服务（面板后端，~230 行）
│
├─ team\
│  ├─ ptc\                          ★ 面板层
│  │  ├─ prototype-expert-console.html   面板 v0.3（由桥接服务托管）
│  │  ├─ .trainer-session.json            Trainer 会话 id 持久化（重启不丢上下文）
│  │  ├─ HANDOFF-EXPERT-CONSOLE.md        开发交接文档（面向续开发者）
│  │  ├─ LINK-REGRESSION-ISSUES.md        A类(流程)8条 + B类(合约)8条 问题清单
│  │  ├─ ptc_stage_registry.json          PTC 阶段注册表（TSZ 加密，python 透读）
│  │  └─ （ATE_PTC_RUNTIME.md / OUTPUT_CONTRACTS.md / PTC_EXECUTION_AUTHORITY.md 等运行时文档）
│  │
│  ├─ expert-profiles\              ★ 专家资产（训练写入的目标，一目录一专家）
│  │  └─ <专家名>\                   8个：ptc-dft-expert、ptc-schematic-expert、
│  │     ├─ instructions.md           strategy-expert、method-expert、rule-reviewer、
│  │     ├─ profile.yaml              ate-implementer、compile-diagnostician、evolution-expert
│  │     ├─ output-contract.schema.json
│  │     ├─ cases\<TM>\               金标准案例（当前覆盖 TM106）
│  │     ├─ evaluation\               期望评估结果
│  │     ├─ status.json               当前版本/草稿评估verdict/digest/history
│  │     ├─ CHANGELOG.md              训练与发布历史
│  │     └─ versions\v1 v2 v3…        ★ 已发布版本（快照，不可变；draft 改动只在上面几项）
│  │
│  └─ artifacts\                     ★ 运行产物
│     ├─ <批次名>\advance-handoff.json    批次状态机当前 stage（带 BOM）
│     └─ dispatch-receipts\               子代理派发回执
│
├─ scripts\                         ★ 核心脚本（桥接服务 spawn python 调用）
│  ├─ evaluate_expert_profile.py      评估草稿：--profile X --version draft
│  ├─ publish_expert_profile.py       发布：--profile X --version vN（评估不过拒发；版本已存在拒发）
│  └─ validate_expert_roster.py       全队校验：owner 全部指向 published 版本
│
└─ plugins\dsh-ptc-material-boundary\ PTC 插件（材料边界/派发回执，编入 DSH web profile）
```

**训练写入的幂等机制**：面板写入规则时在 instructions.md 末尾追加 `<!-- ptc-console:rule id=<sha256前8位> -->` 注释行 + 规则文本，同内容重复写入自动跳过；同时 CHANGELOG.md 记录训练轮次与出处。

## 4. Preset / 模型配置

| 项 | 值 | 说明 |
|---|---|---|
| DSH web 启动 profile | `web` | 唯一入口；PTC 插件栈编在 `profiles/web/cordis.patch.yml`（dsh web 子命令不接受 --profile 参数） |
| web profile 包含 | dsh-ptc-material-boundary + agent-teams | 材料边界/回执插件 + 专家团队派发 |
| Trainer 会话 preset | `ate-ptc` | session.create 时 DSH 返回的 agentPreset，工作目录=Ate-Coding-Flow |
| 主模型 | `zai-coding-cn/glm-5.3-flash` | settings.yaml agent-default-model；ZAI_API_KEY 环境变量注入进程（不落盘代码） |
| 备用模型 | `qwen-token-plan/qwen3.8-flash` | 已配置可用（QWEN_TOKEN_PLAN_API_KEY 注入），当前未用 |

## 5. 训练流程（对话式 5 步）

```
①喂料 ──→ ②Trainer拆解出提案 ──→ ③用户逐条确认 ──→ ④写入draft+自动评估 ──→ ⑤发布盖章
```

1. **喂料**：面板训练页输入框粘贴文字/流程图（可选左侧点专家=指定训练目标，发送自动带前缀）；纠错页问题可一键「转训练提案」
2. **拆解**：Trainer 系统提示词（内嵌于 expert-console.mjs 的 `TRAINER_SYSTEM`）约束输出格式 `[编号] (专家 | 落盘位置 | 形式) 内容 —— 依据`，不确定标「待确认」，涉及交接的注明影响两个专家
3. **确认**：用户看提案，认可的条目通过右侧「快捷写入」表单执行（选专家+粘规则+出处）
4. **执行+评估**：写入 instructions.md（幂等 marker）→ 自动跑 evaluate_expert_profile.py → verdict pass/fail 实时显示
5. **发布**：发布页选专家 → 评估 → 发布下一版（v+1 自动算）→ versions/ 生成不可变快照

**实测样例**：喂入「dft 产物目录策略：首选 trial 目录，被拒降级 Output_Global_Material/dft/<TM>/，回执留痕」→ Trainer 返回 6 条提案（instructions 行为规则 ×2、schema 修复、金标准断言、verify 脚本伪代码建议），含落地顺序与待确认点（"被拒"的定义）。

## 6. 发布流程与状态判定

- **draft 干净判定**：status.json 中 `draftEvaluation.assetDigest === manifestDigest`（草稿与已发布一致）→ 面板显示「draft 干净」，否则「有变更待评估/发布」
- **发布规则**：评估 fail 拒发（不产生版本目录）；版本已存在拒发（不可变）；发布成功后 status.json 更新 publishedVersion + history
- **全队就绪判定**：validate_expert_roster.py 检查每个 stage owner 派发都指向 published 版本 → "roster complete"
- **当前版本**：dft v3、schematic v2、其余 6 个 v1，roster complete

## 7. 面板四页签（v0.3 现状）

| 页签 | 数据来源 | 能做 |
|---|---|---|
| 💬 对话式训练 | DSH Trainer 会话（真 AI） | 喂料、看提案、快捷写入+自动评估、指定训练目标 |
| 📦 发布 | status.json（真实） | 专家版本时间线、评估草稿、发布下一版、全队状态表、roster 校验 |
| 🩺 纠错 | LINK-REGRESSION-ISSUES 摘要 | 问题清单 → 一键转训练提案 |
| 🏃 DSH 运行 | artifacts（真实） | 批次流水线 stage 高亮（INPUT_SYNC→…→COMPLETE）、派发回执列表。**驱动类操作（唤醒 Captain/派发）故意未接通**，待确认后接 |

## 8. 桥接服务 API 一览（供扩展开发）

| 端点 | 作用 |
|---|---|
| GET /api/state | 8专家状态+批次+DSH在线+trainer状态（面板 5s 轮询） |
| POST /api/evaluate {profile} | 评估 draft |
| POST /api/publish {profile} | 发布下一版（版本自动算） |
| POST /api/roster | 全队校验 |
| POST /api/train-rule {profile,rule,source} | 幂等写入规则 + 自动评估 |
| POST /api/trainer/send {text} | 喂料到 DSH Trainer 会话 |
| GET /api/trainer/poll | 轮询回收 Trainer 回复（解压 zstd 会话文件） |

## 9. 已知坑（开发/运维必读）

1. **events.mux 是 WebSocket 不是 SSE**（426 upgrade required）→ Trainer 回复走轮询解压 `C:/Users/nvt10241/.dsh/sessions/--D-Newtest-DSH-ATE-Coding-Flow--/<sessionId>/session.jsonl.zstd`（多帧 zstd，zlib.zstdDecompressSync 逐帧）
2. **DSH API 的 sessionId 在 `result.value` 里**，不在顶层；create 后立即 prompt 偶发竞态，重试即可
3. **TSZ 加密**：scripts/*.py、status.json 等须 git-bash python 透读（`encoding='utf-8-sig'`）；HTML/mjs/md 为明文
4. **本机 PowerShell/curl TLS 有问题**，网络调用一律 Node fetch
5. **后台进程会被环境清理**（PID 常变），重要状态必须落盘（.trainer-session.json 即为此设计）；重启桥接服务先 `netstat -ano | grep :4090.*LISTENING` 杀旧再启
6. 聊天记录面板不持久化（刷新清空），但重新发消息会接上原 DSH 会话，训练上下文不丢——**面板是遥控器，DSH 是录像机**

## 10. 下一步（优先级）

1. **提案卡片化**：Trainer 回复解析成可勾选卡片，勾选自动按落盘位置执行（替代手动粘规则）
2. 训练/发布通俗讲义落盘 TRAINING-AND-PUBLISH-GUIDE.md
3. DSH 运行页接通驱动操作（唤醒/派发，需用户确认防误触发）
4. 用面板梳理 A 类 8 条 agent 执行流程问题（A1 Captain 唤醒缺陷等）
5. GUI 运行时激活验证、P5 移除 agent-teams 评估

---
*配套文档：HANDOFF-EXPERT-CONSOLE.md（开发交接，含全部踩坑细节）· LINK-REGRESSION-ISSUES.md（问题清单）*
