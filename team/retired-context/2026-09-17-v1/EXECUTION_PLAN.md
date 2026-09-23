# ATE AgentTeams 长期执行计划与状态

> **恢复前先读 [`team/CURRENT_STATUS.md`](CURRENT_STATUS.md)**：本计划的部分“当前状态/下一步”段落停留在早期里程碑，不能覆盖该带时间戳快照和 `.agent-teams/ate-dali-acceptance/team.json` 的现盘任务状态。每次阶段性结论须把快照更新到最新目标树哈希与证据；若不一致，先核实再继续。

> 这是本工程的长期计划与历史状态记录；最新恢复快照见 `team/CURRENT_STATUS.md`，实时任务状态以 `.agent-teams/ate-dali-acceptance/team.json` 为准。任何 Captain、专家 Agent 或人工接手者，在新会话、上下文压缩、服务重启或任务恢复后，须先读恢复快照和本文件，再读 `team/README.md`、`team/acceptance/acceptance-plan.json` 和自己对应的角色手册。

> **团队分工与既有规则吸收入口：[`team/ROLE_ROUTING.md`](ROLE_ROUTING.md)**。旧 `skills/AGENT_MAP.md` / `skills/nuvolta-codegen.md` 属旧单主代理流水线索引，不再决定 AgentTeams 的责任边界；当前规则正文仍保留在原 `knowledge/` 与 `skills/agents/` 文件，由新角色按路由按需读取。

## 1. 长期目标

把现有主 Agent + 临时 subagent 流程演进为基于 DSH `@nanmicoder/dsh-agent-teams` 的稳定专家团队。首要目标不是节省 token，而是形成可独立积累、可审计、可持续改进的专业角色：

- DFT 与原理图各自独立解析，产物作为全局后续输入。
- Relay、Source、Channel、TReg、上下电和 cleanup 由 Setup 专家统一建模。
- 测试策略专家从 JSON/meta、DFT、原理图和黄金案例中泛化方法、参数架构与特殊要求。
- ATE 实现专家熟练机台手册与库函数，按批准计划生成实现。
- 规则审查专家积累规则与错误示例，独立反馈给实现专家形成修复闭环。
- 编译诊断专家运行门禁和真实 VS 编译，保证语法/链接闭合，并明确“编译通过不等于电气验证通过”。

长期知识必须落入版本化的角色手册、标准、黄金案例或结构化规则库；聊天记忆只作辅助。

## 2. 固定边界

- ATE 工作区：`D:/Newtest/DSH/ATE-Coding-Plat`
- 唯一可写/可编译 VS 副本：`D:/PROJECT6-DALI/ForCodexDebug`
- 生产工程：`D:/PROJECT6-DALI/devel`，严格只读
- 路径唯一入口：`project_config.json`
- DSH 团队配置：`team/dsh-agent-teams.patch.yml`
- 验收范围：TM000、TM001、TM102、TM103、TM108、TM109、TM135、TM600、TM601、TM1205
- TM600/TM601 在 debug `test.cpp` 的基线中缺失，必须作为真实新增能力验收；其余八项为现有实现的证据化审查与必要修正。
- 受 TSZ/DLP 保护的源码只能通过已验证的 Python 明文字节链路读写；首次写入前创建可恢复备份，写入后立即复读并记录 plaintext SHA-256。
- 完整交付文件写入 `team/artifacts/<run-id>/`；Agent 消息只保留短摘要、路径、哈希、阻塞项和下一接收者。

## 3. 目标生产 DAG

```text
DFT IR ─────────────┐
                    ├─> Setup Contract ─> Test Plan ─> Implementation ─> Rule Review
Schematic IR ───────┘                                              ▲          │
                                                                    └─ Repair ┘
                                                                                │
                                                                                v
                                                                       Gates + Release Build
```

约束：DFT 与原理图必须并行且不相互覆盖事实；实现必须依赖已签收的 Setup/Test Plan；阻塞审查不得解锁编译；编译中只有行为不变的机械错误可由编译专家直接修复。

新增职责门：测试策略专家负责从已验证 Setup 通路中**选定逐 TM 的源表/通道组合**，按匹配黄金案例规划明确的上电、寄存器、测量、撤流、下电与 log；DFT 不写具体台阶，实现者不自行决定测试方法。Schema PASS 只验证结构，不替代 `ROLE_ROUTING.md` §3 的语义交接检查。

## 4. 分阶段计划

| 阶段 | 目标 | 完成条件 | 状态 |
| --- | --- | --- | --- |
| P0 隔离与基线 | 副本路径、门禁和 VS 编译可复现 | 生产路径不写；11 绿、1 个已知 cbit 红；Release 0 error/0 warning | 已完成 |
| P1 团队骨架 | 本地 patch、7 角色、Schema、验收计划可加载 | DSH `--dump-config` 退出 0；`ate-delivery` 与 7 成员可见 | 已完成 |
| P2 Staged DAG | Captain 生成可审查的任务和依赖 | 任务数大于 0；依赖满足第 3 节；未创建成员 | 已完成 |
| P3 输入与策略 | DFT IR、Schematic IR、Setup Contract、Test Plan | 四类 JSON 通过 Schema；十项覆盖；无阻塞决策 | **已完成（输入已冻结）**：`setup-contract.json` **rev22 `295d483a…`**(329115 B) 与 `test-plan.json` **v20 `1925250d…`**(166099 B) 均两次生成字节一致 + Schema exit 0；U10=QVM 并发性 / U11=SIGN-CONVENTION canonical；BST−SW 已对齐裁定 (ii)（`SW12_U1REF_BST_ACM`）；pin 全项 true；争议按"保留两侧"登记（DFT 4.2 V vs OVERVIEW 4.0/3.0 V 等）。注：原"无阻塞决策"表述按实际改为"经裁定收口 + 开放项具名登记" |
| P4 实现与复审 | 新增 TM600/TM601，审查其余八项，完成修复循环 | manifest 完整；无 open critical/high finding | **进行中**：payload **已写入 debug 副本**（`test.cpp` 434629 B `5c9cb3f9…3317` → **462848 B `3dbceb49…`**，备份+回读复核 6/6 PASS）；meta/test_conditions 已再生（落在 DSH 工作区 `project/DALI/meta/`）；**门禁 delta = 1 真红（`relay-trace` TM601 稳压电容）+ 1 假阳性（`cbit` harness 读取缺陷）**；修复链 **t22 只读规则审查 → t23 经批准代码修复 → t24 独立实现审查（替代悬空的旧 t6）** 进行中；`implementation-manifest.json` 待定稿（`afterSha256` 已可填）。**尚未编译** |
| P5 编译闭环 | 全门禁与 Release 编译 | 无新增红；Release exit 0；build-report 通过 Schema | **未开始**（须门禁 delta 归零后执行；`run_gates.ps1` 与编译需以目标树为工作区的会话执行） |
| P6 经验晋升 | 把验证过的共性经验固化到角色/规则/黄金案例 | 每条新规则有来源、反例和验证证据；不混入单次猜测 | 未开始 |

## 5. 当前状态（2026-09-16 18:34 +08:00；写入回合进行中）

### 5.0 最新状态（**本节为唯一有效的当前状态**；下方 5.1 全部为历史条目）

- **输入已冻结**：`setup-contract.json` **revision 22 / 329115 B / `295d483a6d689e04d86744a7cfe55cb7936dd9b6ecb87ab5cc66b611b57b3d5c`**（两次生成字节一致、Schema exit 0、pin 全项 true）；`test-plan.json` **v20 / 166099 B / `1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016`**（两次一致、Schema exit 0、BST−SW 对齐裁定 (ii)）；excerpt **8423 B / `9554d4d6…`**（t5 绑定输入，`delay_ms(1)`）。Captain 独立复验 **18/18 PASS**（含 6 秒稳定复读）。
- **TM600/TM601 已写入 debug 副本**：`D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` = **462848 B / `3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479`**（由具备写权限的一方=Captain 执行，用户批准本写入回合；内容作者=ate-implementer）。备份 `backups/test.cpp.before_TM600_TM601.bak` 逐字节可用；写后复核 6/6 PASS（逐字节重建、BOM/CRLF、两个 `DUT_API` 定义各 1、代码级 `delay_ms(1)=6 / delay_ms(2)=0`）。
- **meta/test_conditions 已再生**，落在 **DSH 工作区** `project/DALI/meta/`（`dali_tm_meta.json` 146180 B / `1c849664…`；`test_conditions.yaml` 11627 B / `4dd0468e…`）—— **不是 VS debug 树**。
- **门禁 delta（baseline 仅 `{"cbit": true}`）＝ 10 GREEN + 2 NEW-RED**：`relay-trace` = **真红**（`TM601_LS_RDSON` 四条电容发现，其中 **K5_VBUS_Cap 系 meta 供电模型与 BD-08 冲突所致**）；`cbit` = **假阳性**（`gate_baseline.json` 被 PowerShell 读成 TSZ 密文 ⇒ `ConvertFrom-Json` 抛错 ⇒ 基线为空 ⇒ 全部红灯判 NEW-RED；**须修读取，不得改写基线**）。
- **门禁修复中**：**t22**（rule-reviewer，只读审查 FR-001 适用边界 + 带 locator 的规则/例外建议）→ **t23**（ate-implementer，仅按 t22 裁定修 payload）→ **t24**（rule-reviewer，独立实现审查；**替代因依赖 failed t5 而永久不可认领的旧 t6**）。**职责分离**：Captain 与实现者均不得单独裁定规则适用性。
- **尚未编译**：Release 编译列在门禁 delta 归零之后；`run_gates.ps1` 与编译需以目标树为工作区的会话执行。**编译闭环 ≠ 电性签核**。
- **边界**：`D:/PROJECT6-DALI/devel` **零写入**；不授权机台/电性验证；U10/U11 仅作 bring-up limitation；目标树已有**逐字节备份** `backups/test.cpp.before_TM600_TM601.bak`（434629 B / `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`），**恢复须按校验流程执行**（先核对备份哈希与现盘哈希，再以 python 明文·字节方式写回并回读复验）—— **尚无经演练的一键恢复脚本**。

### 5.1 历史条目（保留供审计；**不得当作当前状态误读**）

#### 2026-09-16 15:36 峰时暂停时的状态

- 已把 `project_config.json` 的 channel map、relay definitions、VS source 和 TReg 全部切到 `ForCodexDebug`。
- 已消除 `scripts/run_gates.ps1` 中对生产工程的硬编码，并增加可覆盖的 `-BuildPath`。
- 已为 `fast_rebuild.ps1` 增加 `-LogFile`，真实保存 MSBuild 路径、toolset、输出 DLL 和 0 error/0 warning 证据。
- 基线门禁：11 项 GREEN；`cbit` 为已登记 KNOWN-RED；NEW-RED 为 0。
- 基线 Release 编译：exit 0，0 errors，0 warnings；目标为 `D:/PROJECT6-DALI/ForCodexDebug/source/F12011.sln`。
- 已建立 7 个角色手册、7 个 JSON Schema、零依赖 artifact validator 和十项 acceptance plan。
- `team/dsh-agent-teams.patch.yml` 已经真实 DSH compose 验证，`ate-delivery` 和七个成员被识别。
- DSH 工作区 `ATE-Coding-Plat` 已注册并选中。
- DSH 会话“DALI 十项真实验收运行”已创建 staged 团队 `ate-dali-acceptance`；七名成员已列出但尚未创建。
- staged DAG 已完成并从 `.agent-teams/ate-dali-acceptance/team.json` 复核：7 成员、9 任务、10 依赖，run-id 为 `acceptance-20260916-dali10`。
- DAG：t1 DFT 与 t2 Schematic 并行；t3 Setup 依赖 t1+t2；t4 Strategy 依赖 t3；t5 Implementation 依赖 t4；t6 Rule Review 与 t7 Capability Verification 均依赖 t5 并行；t8 Gates+Release Build 依赖通过的 t6；t9 Integration 依赖 t6+t7+t8。
- 修复回路采用运行时 review 机制：t6 若返回 `needs_revision`，生成 repair + 下一轮 review；若未自动触发，由 Captain 在同一轮显式创建 repair 任务，禁止让下游依赖失败审查。
- 已在任何成员写入前生成隔离起点：`team/artifacts/acceptance-20260916-dali10/isolation-baseline.json`，最终 t9 将重算生产树与 debug 副本哈希。
- 已识别并完成本次运行的限值裁定：OVERVIEW 中 TM600/TM601 是 11/7.5 mΩ，而 `project/DALI/input/DFT.csv` 是 10/8 mΩ；`acceptance-20260916-dali10` 采用 OVERVIEW 的 11/7.5 mΩ，理由是 `project_config.json` 将 DFT xlsx 设为权威输入且 OVERVIEW 有明确 sheet/row 意图定位。CSV 的 10/8 mohm 必须作为冲突的派生/旧值保留，禁止改写、平均或删除；若后续出现更新版本或正式批准记录，必须重开此决策。
- staged plan 已批准并启动。七名专家子会话已创建；当前 t1 `dft-expert` 与 t2 `schematic-expert` 运行中。
- t3/t4/t5 的成员已经加入，但任务仍受依赖保护；t5 实现者只进行只读预研，不得在 t4 完成前写源码。t6/t8 对应成员空闲等待依赖。
- 当前进度：t1-t4、t10-t12 已完成；t5 attempt 1 因 DSH `Workspace Write` 无权写外部 VS 副本而失败，但生成了完整 implementation payload 与明文备份，目标源码仍为基线哈希；Captain 已创建 t13 处理 Setup 的最小范围/编号/措辞修复，t6-t9 仍受依赖保护。
- t11 已由 Captain 在 freeze 指令下终态完成：`test-plan.json` v12 = 148150 B / Python 明文字节 sha256 `b3ea171484c2ecc2ae2e941bab95aceceb2899c703e938141c56fee35bf18ddb`，Schema PASS；U11 SIGN-CONVENTION 和 2 ms forced-current 整窗硬上限已落地。
- t12 已正式完成：`setup-contract.json` = 321779 B / Python 明文字节 sha256 `93e417f60b7ff043ed515cf12a72d1708807f7fd7c9caa1b6b7c91d865a201d6`，Schema PASS；BD-08、`simulationDomainReference` 与 SIGN-CONVENTION 已落地。其输出自报把 BD-08 归属扩展到 TM102/103/108/109，Captain 已按实测 DFT 行创建 t13：数值由各 TM 自身 DFT 证据决定，BD-08 归属只允许 TM600/TM601；同时统一 U10/U11 和降级 DV-01 争议措辞。
- t13 虽已被平台标记 completed，但其后 Setup 生成器又并发重写了产物：现盘 `setup-contract.json` = 326363 B / Python 明文字节 sha256 `30b96931fe77f31e0a5ea5fbd163f7a1154e1d94bc85c3d35af257215bc97d9b`，与 t13 报告的 `b98cd824...` 不同。现盘文件还把 openItems 写成 U11=QVM concurrency、U10=SIGN-CONVENTION，而同一文件 `polarityDecision.signConventionFinding.captainRuling`/`assumptionToVerify` 又明确 SIGN-CONVENTION=U11；这既内部矛盾，也与 test-plan v12 的 U11=SIGN-CONVENTION 冲突。故 t13 不能作为冻结输入，t15 的固定哈希已经失效。
- 15:13 已向 Captain 下达强制冻结指令；Captain 已取消 t15 并创建 t16 Setup 冻结修复，统一 U10=QVM channel-0 concurrency、U11=FI SIGN-CONVENTION，修正 `setup-contract-build.py`，连续生成两次获得完全相同的 Python 明文字节 SHA-256，Schema PASS，更新 `setup-contract-pin.json`。Captain 同时从证据中发现 test-plan 的 BST-SW 资源裁定仍有反向表述，新增 t17 计划冻结修复；后续新的实现任务必须显式依赖 t16+t17 并固定两份新哈希。两项冻结完成前继续保持 `Workspace Write`，禁止外部写入。
- Captain 又创建 t18（依赖 t16），为撤回 t12 错误扩展到 TM102/103/108/109 的 BD-08 激励并登记 DFT/OVERVIEW 数值冲突。由于 t18 再次修改 Setup 生成器和产物，t16 哈希只是中间态；已立即下达 DAG 修正：最终 Setup 冻结以 t18 后连续两次同哈希、Schema PASS、最终 pin 为准；实现须显式依赖 t17+t18。三项任务未完成前不开放外部写权限。
- t16 已由 `setup-architect` 正式 completed：`setup-contract.json` 中间态 revision 16 / 330754 B / Python 明文 sha256 `9f6d6e075c1f3dfa13767afcb061d1562e229faa38304f582129494264a1fe3d`，连续两次生成字节相同、Schema PASS；U10/U11 全局引用统一，并把 BST-SW 资源裁定改为 `SW12_U1REF_BST_ACM`。该哈希仍将被 t18 覆盖，不可作为实现最终 pin。t17/t18 尚待认领。
- **用户要求等到北京时间 18:00 后继续，以避开 DeepSeek 峰时费用。**15:3x 已向 Captain 发送暂停/恢复指令，停止可见的 DSH 运行回合；由于排队消息会自动再次拉起旧回合，又以 Ctrl+C 停止本次本地 DSH Web 服务（原 `http://127.0.0.1:7799/`，端口已无监听）。15:35:47 `team.json` 状态 t16 completed、t17 claimed、t18 claimed（其 claim 并不等于完成），team mtime 停在 15:33:37；`Full access` 未启用，外部 debug `test.cpp` 仍为 434629 B / Python 明文 sha256 `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`。已在当前 Codex 任务设置 18:00 北京时间的恢复 heartbeat（id `18-00-dsh`），恢复后应取消每日重复触发。
- 暂停前最后一次现盘快照（**未冻结，禁止实现引用**）：15:34:31 `setup-contract.json` 331223 B / `0fed1c181c6d584a9be6e3efbccb354c4e2f05d7437bc737f052b6cb4653a58a`；`test-plan.json` 157175 B / `33a0a4e46a209f036bfd5c0fc0316ae51cc67ce64277d2be78173c0615498e6d`。t16 完成后的产物曾继续漂移（revision 16→19），所以恢复时须先重算和重验 pin；不能把这些快照当最终哈希。
- t3 `setup-architect` 已正式交付 `artifacts/acceptance-20260916-dali10/setup-contract.json`：十项 scope、65 个资源、12 个 alias 解析、10 项 TM delta、13 条冲突记录，Schema PASS；寄存器采用 per-TM `.sv` 映射，CSV 的 HS/LS 注释交换保留为冲突证据，模拟域 source 不移植到 ATE。
- BD-05 已作本次 debug 生成/编译验收的临时工程裁定：`FPVIe.SetClamp(50,50)`，在每次 FV/FI 模式切换后重发；1 A force 使用 FPVIe 1 V / 2 A 量程，对应 ±0.5 V compliance。此裁定不授权真实机台上电；U1（1 A 继电器额定值）必须保留为上机前硬件签核项。
- t4 `test-strategy-architect` 已交付 `artifacts/acceptance-20260916-dali10/test-plan.json` 并通过 Schema。交付后发现 BD-04 状态尚未按裁定关闭，以及新增 BD-08（ATE 激励与仿真域 `.sv` 数值冲突）；Captain 已创建 t10 修订任务，禁止 t5 在终态计划修订前认领。
- BD-04/BD-08 已终裁：TM108/TM109 采用 OVERVIEW 4.4 V；TM600/TM601 ATE 激励采用 DFT/OVERVIEW（TM600 PMID 15 V、TM601 PMID 9 V、standby/supply 4.2 V）。CSV 的 4.15 V/行内矛盾与 `.sv` 的 5 V/3.5 V 仿真值均保留为冲突/参考，不得混合。
- t5 attempt 1 权限阻塞：DSH 工作区是 `D:/Newtest/DSH/ATE-Coding-Plat`，而唯一写目标 `D:/PROJECT6-DALI/ForCodexDebug` 在工作区外；`Workspace Write` 拒绝写入。实现专家没有绕过权限，`test.cpp` 仍为 434629 B / Python 明文 sha256 `5c9cb3f9…3317`，并交付 `implementation-payload-TM600-TM601.cpp` 与 `backups/test.cpp.before_TM600_TM601.bak`。用户已在动作发生前明确回复“大胆干，没问题，100% 授权”；2026-09-16 14:46 已通过 DSH Web 风险确认并复核主按钮明确显示 `访问模式，当前：Full access`，但 Captain 新一轮处理开始后该模式自动回退到 `Workspace Write`，证明访问模式按回合生效而非会话永久保持。因此必须在 t13 即将开始外部写入时再次启用，并在同一回合完成 `ForCodexDebug` 副本写入/编译；完成后确认保持或恢复 `Workspace Write`。
- t1 `dft-expert` 已正式交付 `artifacts/acceptance-20260916-dali10/dft-ir.json`：runId 和十项 scope 正确，Schema PASS；补充版同时保留 OVERVIEW 11/7.5 mΩ 与 DFT.csv 10/8 mohm 两套原始证据、locator、Python 明文哈希和 `pending-user-adjudication`，禁止平均或静默覆盖；函数名采用 `TM600_HS_RDSON` / `TM601_LS_RDSON`，并记录 MV&MI + Kelvin 差分要求。
- t2 `schematic-expert` 已正式交付 `artifacts/acceptance-20260916-dali10/schematic-ir.json` 且 Schema PASS：十项 scope、72 个继电器、41 个网络、182 条路径；上游并行输入阶段已闭合，t3 已由调度器自动认领。
- 已实测纠正角色路径缺陷（Captain，13:45）：角色手册与 README 引用的 `golden-code/` 在工作区不存在（`project/DALI/golden-code` 与根级 `golden-code` 均 Test-Path=False）；真实黄金案例库为 `knowledge/references/L4-Golden-code/`（36 项 / 18 .md），与本次十项直接相关的有 tm600-normal-highcurrent、Rdson、toggle-template、TM1205_TRX_BST_UV_GD、TM130_Trim_VBG、sub-measure-template。已就地修正 `roles/test-strategy-architect.md`、`roles/ate-implementer.md`、`README.md`。
- 已实测确认 TSZ 双哈希陷阱（Captain，13:45）：同一文件 Python（授权进程）读到**明文**、PowerShell/`Get-FileHash` 与 .NET 读到**密文**，字节数完全相同但 SHA-256 不同 —— `dali_tm_meta.json` 明文 `1F5EEB5E…F7F1` vs 密文 `48B06343…2E77`（均 143019 B）；`test_conditions.yaml` 明文 `0F4354ED…5C48` vs 密文 `D501253A…A115`（均 11363 B）。故**所有 before/after 哈希必须用 Python 计算并标注 plaintext**，否则跨阶段比对会把"未改动"误判为"被改动"（或反之掩盖真实改动）。该规则已写入 `roles/ate-implementer.md` 与 `artifacts/acceptance-20260916-dali10/RUN-LEDGER.md`。
- 已裁定 TM600/TM601 符号名（Captain，13:50）：函数名必须满足 `DUT_API int TM<digits>_*(short funcindex ...)`（`gen_testitems_meta.py:86-94`），故采用 `TM600_HS_RDSON` / `TM601_LS_RDSON`；`acceptance-plan.json` 的 `symbolHint`（RDSON_TEST_HS/LS）**不可**用作函数名，仅作提示。已通过 send_message 下达 t4（必须显式固定精确名）与 t5（照抄签收值）。
- 已裁定 meta 覆盖不再阻塞（Captain，13:50）：函数名取自 test.cpp、意图取自 OVERVIEW（两行均存在）→ 重跑 `gen_testitems_meta.py` 即自动纳入，`--require-all` 可通过；meta 两文件已在 t5 inScope，无需新增任务。
- 已解答 t5 的 compliance 未知（Captain，14:05，**15:3x 更正表述**）：~~本代无 `SetClamp`（全文件命中 0）~~ → **正确表述：`SetClamp` 在 tester SDK 中存在**（`C:/AccoTEST/AccoTEST System/INCLude/FPVIe.h:101 int SetClamp(double percent_PFS, double percent_NFS);`、`FXVIe.h:117/458`），**本项目自有源码 0 次使用**。前次"不存在"是**扫描范围受限**（只扫项目树）导致的错误外推，由 setup-architect 发现并要求更正；权威版本见 `RUN-LEDGER.md`。补充机制：clamp 参数为**满量程百分比**，且**切换 FV/FI 模式会清除箝位**（`knowledge/sources/fpvie.md:141-168`）→ 每次模式切换后须重新下发；数值仍缺（BD-05 未决）。同时 `Set(...)` 的**量程实参**仍是 clamp/compliance 的常规承载方式；取回用 `MeasureVI` + `GetMeasResult(site, MVRET|MIRET)`。TM600/TM601 force = 1 A → 电流量程须 ≥1 A（取 `FPVIe_2A`），不得沿用示例 `FXVIe_PLUS_10MA`。
- 已裁定拓扑以 DFT 意图为准（Captain，14:05）：外部强制电流 + `Check=PMID-SW`/`PGND-SW` 差分 Kelvin 感测（RDSON=V/I）；归档黄金的 FPVI 自身 MVRET/MIRET 反推属不同拓扑，不得覆盖 DFT 意图，黄金只提供本代 API 机制。
- 已确认 RDSON 黄金案例属另一 API 代际、不可照抄（t5 侦察 + Captain 复核）：`SetClamp`/`K31_VBUSL_PMID`/`BTST_ACM`/`PMID_FOVI` 在 test.cpp+StdAfx.h 命中 0；精化：`FOVIe_*`/`VBAT_ACM` 存在于方法库层（sub.cpp/Test_Method），不在 TM 级 test.cpp。
- Captain 自我更正已撤回一例：先前怀疑 t5 的"0 命中"为假零，逐文件归因后证明**成员正确**（错误源于我按 7 文件 blob 统计）。

## 6. 当前证据

- `team/artifacts/baseline-20260916/acceptance-inventory.json`
- `team/artifacts/baseline-20260916/build-report.json`
- `team/artifacts/baseline-20260916/gates/*.log`
- `team/artifacts/baseline-20260916/build-verified/build.log`
- `team/acceptance/acceptance-plan.json`
- `team/dsh-agent-teams.patch.yml`

## 7. 下一步

以下是 2026-09-16 19:20 起的执行顺序；执行前先刷新 `team/CURRENT_STATUS.md` 的时间戳、任务状态与目标树哈希。此前“18:00 恢复、t17/t18 冻结、等待旧 t5/t7/t8/t9”的文字已作废，保留于历史日志而非执行指令。

1. t35 已归口 t29 的三处不一致；DSH Captain 于 19:55 将**第四项 TM601 BST 5 V 激励路径缺口裁定为落盘阻断项**，已派 t38 给 ate-implementer 修复，并要求契约 owner 与 rule-reviewer 独立判定、复核（见 `review/t29-k110-implementation-review.md` §2）。t38 复核通过前**不执行 REPLACE**。19:50 旧审批对应的脚本 pin 曾为 36381 B / `73b511b7…`；19:52 脚本改为 38147 B / `272667f3…`，而 19:55 payload 又变为 38888 B / `f536c7e4…`，因此任何旧审批、旧脚本 pin 与旧审查都不能覆盖新字节。Captain 只将获批的精确增量落盘到 `ForCodexDebug`，写前备份、写后复读和哈希验证，不碰 `devel`。`t29 completed` 只表示旧 payload 交付，不代表目标树已更新；现盘目标仍为 469714 B / `15c7d2b8…`。
2. t27 计划 v21 与 t31 审计链自保护已完成，后续须同步 pin。t28 RS 守卫、t30 BST 守卫均已有实现和缺陷阳性红证，但因独立复核未回收保守标 failed，需显式复核并以可解锁任务承接；修后在最终树转绿。t30 扩展探针还对十项范围内 TM1205 报缺 `[61,110]`，须契约 owner 与独立规则审查判断是登记/路线错位还是实现缺失，不得因默认守卫只扫 TM600/TM601 而略过。
3. t32 首轮独立核验已判 fail（目标缺 K110、证据版本对应性不足、verification-report schema 缺失）；修后需补 schema 并建立新的独立复验任务。t33 或其替代任务在**最终目标树哈希**上重跑门禁与 Release 编译，最终集成任务形成十项逐项验收报告。旧 t34 若依赖 failed t32 不会自动解锁，不得把它当作已完成闭环。
4. 任一代码、规则、meta 或计划后改均记录新哈希和受影响的复验结果；每个里程碑更新 `CURRENT_STATUS.md`、本文件及 `RUN-LEDGER.md`。不得把静态门禁/编译通过写成硬件或电性签核。

## 8. 恢复协议

如果上下文被压缩或会话中断：

1. 先读 `team/CURRENT_STATUS.md`，再读本文件第 1、2、4、5、7 节；核对快照时间，勿将旧哈希视作现值。
2. 检查 `.agent-teams/` 的当前团队状态和 `team/artifacts/` 最新 run 目录。
3. 对比 `project_config.json`，确认写入目标仍为 `ForCodexDebug`。
4. 不重复已标记“已完成”且有证据路径的工作。
5. 从第 7 节第一个未完成项继续，并在产生新证据后更新本文件。

## 8.1 实现已落盘 + 独立审查项（2026-09-16 18:4x，本轮新增；须与 `RUN-LEDGER.md` 同读）

**已发生（不可回退的事实）**：TM600/TM601 payload 已由 **Captain（具备写权限的一方；用户在写入回合批准 `danger-full-access`）** 落盘到 `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp`：
`434629 B / 5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317` → **`462848 B / 3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479`**。备份逐字节校验通过；复核 **6/6 PASS**（逐字节重建、BOM/CRLF、两个 `DUT_API` 定义各 1、代码级 `delay_ms(1)=6 / delay_ms(2)=0`、真实新增能力）。meta/test_conditions 已再生，落在 **DSH 工作区** `project/DALI/meta/`，**不是 VS debug 树**。署名：**内容作者=ate-implementer、执行者=Captain**。

**门禁 delta（baseline 仅 `{"cbit": true}`）＝ 10 GREEN + 2 NEW-RED**
- `relay-trace` = **真红**：`TM601_LS_RDSON` 缺 `K57_CAP_BST_SW`（与 TM600 不对称）及 `K44_Cap_SW2_BST2` / `K45_Cap_SW1_BST1` / `K5_VBUS_Cap`（FR-001：静态供电⇒闭稳压电容）。
- `cbit` = **假阳性**：`scripts/gate_baseline.json` 被 PowerShell 读成 **8192 B TSZ 密文**（`%TSD-Header-###%`）⇒ `ConvertFrom-Json` 抛错 ⇒ `$baseline` 为空 ⇒ 全部红灯被判 NEW-RED。**须修 `run_gates.ps1` 的读取方式（改用 python 授权读者），严禁改写基线掩盖。**

**独立规则审查项（用户提供证据 + Captain 只读实测；t21 必做、t6 明确项）**：F1 门禁读取缺陷；F2 TM601 稳压电容；F3 裸 `126` → `K126_V1P5_CAP`；**F4 量程 ≥2× 且最小合规档**（15 V→`FXVIe_PLUS_30V`、9 V→`FXVIe_PLUS_20V`、ACM 10 V→`ACM200_20V`、ACM 20 V→`ACM200_40V`，并检查回落台阶与关断态；SDK 档位已由 Captain 直读 `C:\AccoTEST\AccoTEST System\INCLude\FXVIe.h|ACM200.h|FPVIe.h` 核实）；F5 TM601 派生 `−1 A` 的负 RDSON/除零保护；F6 2 ms 为**理论零余量**、不得表述为实测脉冲合规；F7 meta 落点如实标注。

**放行顺序**：`t20` **failed 保留**；**`t21` 完成后**才放行 t6/t7；Release 编译在门禁归零后执行；**编译闭环 ≠ 电性签核**；`devel` 零写入、不授权机台验证。

## 9. 变更日志

| 时间 | 变更 | 证据/结果 |
| 2026-09-16 21:29 | 将用户对 TM600 案例的职责裁定固化为团队路由 | 新建 `team/ROLE_ROUTING.md`；更新 DFT/Setup/Strategy/Implementer 角色、README 与 `dsh-agent-teams.patch.yml`；未改运行产物与 VS 代码。TM601“无 BST”旧推断被用户要求覆盖，留待 DSH 新任务重审。 |
| --- | --- | --- |
| 2026-09-16 13:26 | 完成复制工程 Release 基线编译 | `baseline-20260916/build-report.json`，exit 0 |
| 2026-09-16 13:28 | 修复构建日志为空的问题并复编 | `build-verified/build.log`，0 error/0 warning |
| 2026-09-16 13:34 | 在 DSH 中提交十项 `/agent-teams --profile ate-delivery` 目标 | 会话“DALI 十项真实验收运行” |
| 2026-09-16 13:35 | 创建 staged 团队，七角色正确，Captain 继续生成 DAG | 团队 `ate-dali-acceptance`；0 task，尚未批准 |
| 2026-09-16 13:41 | 完成并复核 staged DAG | 7 成员 / 9 任务 / 10 依赖；`.agent-teams/ate-dali-acceptance/team.json` |
| 2026-09-16 13:41 | 冻结写入前隔离快照 | `artifacts/acceptance-20260916-dali10/isolation-baseline.json` |
| 2026-09-16 13:42 | 将最终 DAG、冲突与恢复入口写回本计划 | 等待 Approve & Run，尚未写源码 |
| 2026-09-16 13:43 | 批准并启动团队 | 七名专家已创建；t1/t2 运行；0/9 完成 |
| 2026-09-16 13:45 | 修正 golden 路径缺陷 + 登记 TSZ 双哈希陷阱 | 手册/README 就地修正；实测哈希对照见本节与 `RUN-LEDGER.md` |
| 2026-09-16 13:45 | 基线哈希交叉复核通过 | debug 副本 test.cpp/sub.cpp/StdAfx.h 的 Python 明文 sha256 与 `baseline-20260916/acceptance-inventory.json` 三项 MATCH |
| 2026-09-16 13:50 | 裁定 TM600/TM601 符号名与 meta 覆盖（源码证据） | `gen_testitems_meta.py:86-94/359-360`：函数名取自 test.cpp 且必须 `TM\d+_` 前缀 → 采用 `TM600_HS_RDSON` / `TM601_LS_RDSON`，acceptance-plan 的 symbolHint 不可作函数名；meta 自动纳入，无需新增任务。推导见 `artifacts/acceptance-20260916-dali10/RUN-LEDGER.md` 与 `probe_meta_naming.py` |
| 2026-09-16 13:50 | 复核 t5 成员侦察事实：隔离起点成立 | `devel/source/test.cpp` 与 `ForCodexDebug/source/test.cpp` 字节完全相同（434629 B，`5c9cb3f9…`，python `b1 == b2`） |
| 2026-09-16 14:05 | 解答 t5 的 compliance 未知 + 裁定 RDSON 拓扑 | **15:3x 更正**：`SetClamp` **在 SDK 中存在**（`FPVIe.h:101`、`FXVIe.h:117/458`），本项目自有源码 0 次使用；前版"全文件 0 命中 ⇒ 不存在"系扫描范围受限所致的错误外推，已撤回。拓扑仍以 DFT 意图为准（差分 Kelvin）。证据：`probe_api_generation.py`、`probe_compliance.py`、SDK 头实测 |
| 2026-09-16 14:05 | 撤回 Captain 自身一次误判 | 曾疑 t5 "0 命中"为假零；逐文件归因证明成员正确（我误用 7 文件 blob 统计），归因表见 `RUN-LEDGER.md` |
| 2026-09-16 13:56 | t1 DFT IR 正式完成并校验；t2 原理图 IR 已落盘待正式提交 | `dft-ir.json`、`schematic-ir.json` 均 Schema PASS；team state 为 t1 completed / t2 in_progress；源码仍未写入 |
| 2026-09-16 13:58 | 裁定本次 TM600/TM601 验收限值 | 采用 OVERVIEW 11/7.5 mΩ；CSV 10/8 mohm 保留为冲突旧值；仅作用于 debug 验收，后续新证据触发重审 |
| 2026-09-16 14:00 | t2 原理图 IR 正式完成，t3 自动解锁 | `dft-ir.json` 与 `schematic-ir.json` 均覆盖十项且 Schema PASS；最终原理图 IR 含 182 条路径、41 个网络；t3 attempt 1 in_progress |
| 2026-09-16 14:08 | t3 Setup 契约正式完成，t4 自动认领 | `setup-contract.json` Schema PASS；65 资源 / 12 alias / 10 TM delta；BD-05 采用仅限 debug 生成/编译的 `SetClamp(50,50)` 临时裁定，U1 保留为上机前硬件签核 |
| 2026-09-16 14:15 | t4 测试计划完成；创建 t10 可审计修订任务 | 初版 `test-plan.json` Schema PASS，但 BD-04/BD-08 状态晚于交付裁定；t10 在 t5 开工前修订，源码仍为基线哈希 |
| 2026-09-16 14:28 | t5 attempt 1 因跨工作区写权限失败，未改源码 | payload + 明文备份已落 run 目录；`test.cpp` 仍为基线 `5c9cb3f9…3317`；DSH Full access 风险确认停在动作前，等待用户明确授权 |
| 2026-09-16 14:46 | 用户明确授权并成功启用 DSH Full access | DSH 主会话按钮已复核为 `访问模式，当前：Full access`；权限仅限本轮 `ForCodexDebug` 副本写入/编译。已下达状态对账纪律：t11/t12 必须正式闭合，随后新建 t13（sourceTaskId=t5），不得覆盖失败尝试；完成后恢复 Workspace Write |
| 2026-09-16 14:49 | 发现 Full access 按回合生效 | Captain 新一轮处理开始后按钮自动回退 `Workspace Write`；故不能把一次启用当成持久授权状态。t13 写入前必须再次启用，并在同一回合完成外部写入/编译 |
| 2026-09-16 14:59 | t11/t12 正式闭合；创建 t13 Setup 修复 | test-plan v12 `b3ea1714…`、setup-contract `93e417f6…` 均 Schema PASS；t13 只修 BD-08 归属范围、U10/U11 编号和 DV-01 disputed 措辞。实现重试编号顺延，继续禁止写副本 |
| 2026-09-16 15:13 | 拒绝使用已漂移的 t13 Setup 产物并要求可重复冻结 | t13 报告 `b98cd824…` 后现盘变为 `30b96931…`；同一 JSON 的 U10/U11 定义互相矛盾，且 t15 固定旧哈希。Captain 已取消 t15、创建 t16 Setup 冻结修复；另发现 test-plan 的 BST-SW 裁定反向表述并创建 t17 计划冻结修复。两者均要求生成器幂等、连续两次同哈希、Schema PASS；访问模式保持 Workspace Write |
| 2026-09-16 15:2x | t16 完成，继续等待 t17/t18 最终冻结 | Setup 中间态 revision 16 / `9f6d6e07…` 两次生成一致、schema PASS、U10/U11 统一；t18 将再次修改同一生成器，故该哈希不供实现引用 |
| 2026-09-16 15:36 | 用户要求等 18:00 避开峰时费用，暂停 DSH | 已停止可见回合并停止本地 7799 服务；t17/t18 claimed 非 completed，debug test.cpp 基线哈希未变，访问模式未提升；计划 18:00 heartbeat 恢复前先对账，自动提醒完成后取消 |
| 2026-09-16 15:2x | 用户正式下达限值裁定（含理由/作用域/重开条件） | OVERVIEW 11/7.5 mΩ 为代码与计划验收限值；CSV 10/8 mohm 保留、禁改写/平均/删除；仅适用本次 debug 验收，发现更新版本须重开。已下发 t3/t4/t5 并记入 `RUN-LEDGER.md` |
| 2026-09-16 15:3x | Captain 第三次自我更正：撤回"感测端用 FPVI 自身 MVRET" | 能力存在（`FPVIe.h:104-117` 默认 `MVRET` + `FPVIe_MV_GAIN`）但 live 代码从不如此用（`test.cpp:8065-8071` 只读 `MIRET`，ΔV 来自两台 ACM 单端相减）。错误性质：把"API 有能力"当成"计量正确" |
| 2026-09-16 15:3x | 发现 FPVIe 具备真四线 Kelvin 能力（但项目 0 次使用） | `FPVIe.h:29-35`（`FPVIe_RELAY_SENSE_ON`）、`:53-58`（`CONTACTMODE`）、`:60-66`（`HIGH_MV/LOW_MV`）；`StdAfx.h:249-255` 有 `K86/K87/K88_Sense_FLOAT/K89/K90_PC_Force/K91_PC_Sense`（FPVI1 同构 `:303-309`）；`Test_Method.h:21` 注释显示项目曾**有意**从 `RELAY_SENSE_ON` 改回 `RELAY_ON` |
| 2026-09-16 15:4x | t2 交付物 Captain 复验 + 感测争议收敛 | `schematic-ir.json` **450689 B / sha256 `ed77ccae15f45853…`** / schema PASS（早先 447580 B / `3ed7a4d7…` 为交付前中间版，已作废）；t2 关键发现（PC 网络含 100 mΩ/5 mΩ 串联感测电阻 → 10 mΩ 项必须走 BUS Kelvin 路由 K87/K88/K89、K131/K132/K133；每 BUS 侧只闭一个 pin；K141/K142 必须打开；极性相反；旧代际 K 号；**继电器无电流额定值 ⇒ 1 A 未硬件签核**）已下发 t3；"感测形式之争"收敛为 3 条可判定问项（a: FPVI0 sense 是否经 K88/K91 落到 PMID/SW 引脚；b: PMID/SW 各自的单端伏特表通路；c: 各 `FPVIe_RELAY_*` 取值下内部继电器动作） |

## 2026-09-16 21:45:12 +0800 冷启动现盘核对（覆盖以上旧快照的执行口径）

- **任务源**：`D:\Newtest\DSH\ATE-Coding-Plat\.agent-teams\ate-dali-acceptance\team.json`，team.json phase=`running`，t43=`pending`、t49=`completed`、t50=`completed`、t51=`pending`、t52=`pending`、t53=`completed`、t54=`failed`。`t43`、`t52` 虽有 `review/` 文件，任务本身仍为 `pending`；不得把产物存在等同任务闭合。`t54` 为 `failed`，本轮门禁的 `bst-sw` 红灯针对旧部署树。
- **目标树**：`ForCodexDebug/source/test.cpp` = 469714 B / Python 明文 SHA-256 `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`；`devel/source/test.cpp` = 434629 B / Python 明文 SHA-256 `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`。后者本次仅读。候选 `implementation-payload-TM600-TM601.cpp` = 43806 B / Python 明文 SHA-256 `66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4`，**尚未落盘**。
- **输入现盘**：`setup-contract.json` rev `34` = 374992 B / Python 明文 SHA-256 `aff6992d6ad5742e68ae64cd0f4ce5552815ffe831ab96c7038827ee3a503303`；`test-plan.json` = 180977 B / Python 明文 SHA-256 `9591e21703e2991594bf35ab388a1e27d2168419cbc40c0128735f30e3e3bd62`；`dft-ir.json` = 130724 B / Python 明文 SHA-256 `d8f900a41e6a30f2c7022a881f5636a652c0fe0a6189e0d42aeb43fe1388a31b`。哈希均由同一 Python 进程按 `read_bytes()` 现算，不能套用上文的旧 rev/哈希。
- **TM600**：候选 payload 已有 ch5 的 K48/K76，且 t52 审查文档对当时字节给出 pass；目标树仍缺 K48/K76，`t54` 门禁 10 GREEN、`bst-sw` NEW-RED、`cbit` KNOWN-RED，suite exit 1。ch5 到 BST 的物理路径和多源互斥须随新策略完整复核；旧 t52 verdict 只覆盖其对象字节及旧计划，不是本轮最终放行。
- **TM601 用户要求优先**：SW—PGND 用 FPVI、BST−SW=5 V、BST=5 V。现有 DFT/Setup/计划及 t38/t52 payload 仍沿用“TM601 无 BST、移除 ACM 激励”的旧推断，与用户要求冲突。**暂停 TM600/TM601 候选落盘、最终门禁/编译放行**，由 DSH 路由给 DFT 记录意图冲突、schematic/Setup 核实可达通路及全局互斥、test-strategy-architect 制定逐 TM 资源和阶段，rule-reviewer 独立验收后实现者才映射 API。不能直接恢复旧 ACM ch5 5 V 调用；须先证明 BST 与 SW 的操作点、BST=5 V 同时成立并确认源可达与下电动作。
- **下一动作**：恢复 DSH `ate-dali-acceptance` 会话时显式复读 `team/ROLE_ROUTING.md`、各角色手册与本条；建立可解锁的新修订/复核任务承接旧 `pending`/`failed` 状态，重新固定输入/实现哈希。任何 REPLACE 只针对 `ForCodexDebug`，经独立审查后备份、写入、回读；随后在新目标哈希上重跑门禁与 Release 编译并更新十项报告。无机台/电性签核。

## 2026-09-16 21:52:01 +0800 DSH 恢复分发受自动审批阻断

- 已在 `DALI 十项真实验收运行` 原会话准备恢复指令，明确要求暂停旧 `t55 REPLACE`，重审用户指定的 TM601 `SW—PGND FPVI / BST−SW=5 V / BST=5 V`，由 DFT→schematic/Setup→test-strategy-architect→独立规则审查→实现的职责链处理，并复核 TM600 ch5、闭集及多源互斥。
- 点击 DSH 页面“发送消息”时，**自动审批拒绝分发**；给出的理由是该长指令可能启动后续代理任务与文件修改，认为当前没有对这次消息及下游效果的明确授权。未绕过拒绝，**该指令未发送**，未创建新 DSH 任务、未落盘候选 payload、未重跑最终门禁或编译。
- 等待用户明确批准向现有 DSH 会话发送这条恢复指令；批准后先核对 team.json 与目标树新鲜状态，再发送并确认 DSH 回执。先前现盘核对与 TM601 需求冲突见上一节。`devel` 保持只读，机台/电性未验证。

## 2026-09-16 21:52:58 +0800 异步任务完成后的补充核对

- 在恢复分发被拒之后，现盘 `team.json` 又显示 `t51=completed`（此前为 pending）；其交付的 `test-plan.json` 现为 183339 B / Python 明文 SHA-256 `0b0a44ab7d02cb3857bd63bf95163d2d9def9c0e198e0a1bfbb2d931e1b3fe6c`，修订 v24。t43=`pending`、t52=`pending`、t54=`failed`。这是旧任务的异步完成，**没有吸收本次 TM601 用户要求**；v24 仍把 `[110,61]` 作为 contested 历史路线保留，不能视作新的实现前策略签收。
- 为避免旧会话沿过期 TM601 前提继续推进，已停止本次启动的 DSH 51821 服务。自动审批拒绝的恢复指令仍未发送；旧候选仍不得落盘。再次恢复时先重读任务源与三份核心产物的现盘哈希，阻断旧 t55 REPLACE，按职责链完成新策略与独立审查。
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

## 2026-09-16 22:0x +0800（EXECUTION_PLAN 条目） TM601 DFT 修改后的裁定与新 DAG（Captain，最新单一恢复入口）

**用户裁定（本次权威输入）**：用户已修改 `project/DALI/Dali_testmode.xlsx`，**修改后的 TM601 DFT 为唯一权威**；先前 TM601 DFT 有错误，忽略其引起的所有 TM601 报错，不作为阻断、修复或验收失败依据。旧 DFT 派生的 TM601 推断、计划、payload、审查**仅保留审计用途**。

**现盘事实（python read_bytes 现算）**
- 新版 DFT：`project/DALI/Dali_testmode.xlsx` = 12,210,680 B / SHA-256 `f4bbb8569763784c500974121fca0d18dc3018061c50875e49c8da1fa0569564` @ 2026-09-16 21:46:39（旧版 pin 为 `d9d721a3…`，已失效）。
- TM601（OVERVIEW row 133）：`vset[vbat,3.5,100e-6,0]` / `vset[vdrv,5,100e-6,0]` / `vset[vbus,5,100e-6,0]` / **`vset[bst,5,100e-6,0]`（BST=5 V，旧版没有）**；`field[WAKE_UP,1]` + `field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_LSON,1)]`；`delay[5e-3]` / **`iset[pmid_sw,1,1e-3,0]`** / `delay[2e-3]`；Power=VBAT,SW；`I(PMID_SW)`；SW-PGND；ExpectValue=7.5 mΩ。
- TM600（OVERVIEW row 132）未变：`vset[pmid,5,100e-6,0]`（**PMID=5 V**）、`vset[bst_sw,5,1e-3,0]`（**BST−SW=5 V**）、`iset[sw,1,1e-3,0]`、ExpectValue=11 mΩ、Special=`Y / 2 FLOAT`。
- 目标树 `ForCodexDebug/source/test.cpp` = 469714 B / `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`（未落盘）；`devel/source/test.cpp` = 434629 B / `5c9cb3f9…`（只读）。
- 旧 run 现盘：`setup-contract.json` 376308 B / `d9ecffb0…`（rev 36）、`test-plan.json` 185689 B / `707ce845…`（v25）、旧候选 payload 43806 B / `66abc088…`；`t55_replace.py` 5573 B / `cc8711f9…`（**未执行**）。
- 旧 run `team.json` phase=`running`：t43/t52 pending、t54 failed；`schematic-expert`/`setup-architect`/`test-strategy-architect`/`rule-reviewer`/`compile-diagnostician` 仍为 working，可能继续改写**旧目录**产物。

**裁定**
1. **停止旧 `t55` REPLACE**：未经新策略与独立审查，**不得落盘任何旧候选 payload**。旧 `66abc088…` 与旧 `2d0984d9…` 一律视为 audit-only。
2. **忽略旧 DFT 引起的 TM601 报错**：旧 `bst-sw`/`relay-trace` 针对 TM601 的红灯、旧 `[110,61]`/`[48,60,61,76]` 之争、t38/t39/t40/t41/t42/t43/t44~t48/t52 的 TM601 结论**均不作为本轮阻断、修复或验收失败依据**（保留审计）。
3. **新职责链**：`dft-expert` 重提取新 DFT → `schematic`/`Setup` 核实物理通路/通道/共享与互斥 → `test-strategy-architect` 制定逐 TM 资源、阶段、寄存器、测量、下电、日志 → `rule-reviewer` 独立审查 → **之后** `ate-implementer` 才映射 API。**Captain 只协调依赖，不落盘、不裁定电气意图**。
4. **TM600 单独复审**（不予豁免）：ACM200 channel 5 → BST 的 `K48/K76`、BST-SW 闭集、多源互斥、以及 **PMID=5 V 与新证据对照旧黄金/`voltage-inference.md` 的 15 V**（并列登记，待裁定，不得静默采用）。
5. **输入冻结**：新 DAG 全部走 `team/artifacts/tm601r3-20260916/snapshot/` 冻结副本 + `pin/snapshot-manifest.json`，以免旧 run 的活跃写入污染新输入 pin。

**新 DAG（staged，等待用户 Approve & Run）**：团队 `ate-dali-tm601r3` / profile `ate-delivery` / 7 成员 / 9 任务 / 依赖 8。
```text
t1  requirements  dft-expert             重提取新 DFT（唯一权威）
 ├─ t2  verification  schematic-expert   JM601 SW—PGND + BST=5 V 可实施性；TM600 ch5→BST/K48/K76/多源互斥
 ├─ t6  implementation setup-architect   契约合并修订（ch5 分组 + 三目的地互斥 + TM601 BST 登记 + 旧条目 superseded）[deps t1,t2]
 │   └─ t7  requirements  test-strategy-architect  逐 TM 资源/阶段/寄存器/测量/下电/日志
 │        └─ t8  review  rule-reviewer   独立审查（verdict=pass 才放行）[deps t2,t6,t7]
 │             ├─ t9  implementation ate-implementer  payload 映射（不落盘）[dep t8]
 │             │   └─ t10 verification rule-reviewer  落盘前检查点 GO/NOGO [deps t8,t9]
 │             │        └─ t11 verification compile-diagnostician 门禁 + Release 编译 [dep t10]
 │             └─ t12 integration setup-architect 十项终稿与残余项 [deps t8,t9,t10,t11]
```

**阻断项（须用户裁定或前置条件满足才能继续）**
- **B1 t55 REPLACE 已停**：执行条件 = t8 `verdict=pass` + t10 检查点 GO + 用户对目标树写入的一次性授权。
- **B2 DFT 现盘已变**：旧 dft-ir 的 `d9d721a3…` pin 失效，21:46 后任何依赖旧读数的结论均须重算（新 DAG 已含此项）。
- **B3 待裁定（不阻断提取，但阻断任何依赖该值的实现）**：新 DFT `vset[pmid,5,…]` 与历史黄金/`knowledge/hardware/voltage-inference.md` 的 PMID=15 V 的差异（TM600）；需用户或授权 owner 给出作用域与重开条件。
- **B4 待核实**：TM601 `vset[bst,5,…]` 的物理含义（BST 单端轨相对 GND，还是 BST−SW 差分=5 V；新 DFT 未给 `bst_sw` 行）——由 schematic/Setup 给事实、strategy 给操作点，不得由实现者猜。
- **B5 旧 run 仍在跑**：旧团队可能继续改写旧目录产物；新 DAG 已用冻结副本隔离，但**旧 run 的 pending/failed 不会自动闭合**，需在终稿或用户裁定中正式登记。
- **B6 边界**：`devel` 零写入；**未做任何机台/电性验证**；**编译闭环 ≠ 电性签核**。


## 附录：待用户批准的两件事（文案草案，2026-09-16 22:1x）

**A. 批准新 DAG**（页面 Approve & Run，或在对话中明确写「批准 ate-dali-tm601r3 计划」）：
团队 te-dali-tm601r3 / profile te-delivery / 7 成员 / 9 任务（t1,t2,t6,t7,t8,t9,t10,t11,t12；号非连续，因中途原子重建）。批准前不会创建任何成员子会话、不会开始任何任务、不会写任何文件。

**B. 对目标树一次性写入授权（仅在 t8 通过且 t10 检查点 GO 之后才可能被用到）**：
> 授权将经独立审查通过的 TM600/TM601 候选 payload 一次性写入 D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp（写前逐字节备份、写后回读并复核 sha256），随后在同一会话重跑门禁与 Release 编译；D:/PROJECT6-DALI/devel 始终只读。

该授权**不覆盖**：旧候选 payload（66abc088… / 2d0984d9…）、任何未经 t8 审查的字节、任何对 devel 的写入、机台/电性签核。

**现盘 pin（用于判断授权是否仍然有效）**：目标树 ForCodexDebug/source/test.cpp = 469,714 B / 15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a；若在落盘前该字节发生变化，授权与检查点一并失效，须重新走 t8/t10。

**三条待裁定（可与 A 同时给出，不阻断提取）**：
1. TM600 操作点：新 DFT PMID=5 V（配 BST−SW=5 V）vs knowledge/hardware/voltage-inference.md L18/L142 的 PMID=15 V —— 以哪一侧为准？另一侧如何标注适用域？
2. TM601 的 set[bst,5,…]：按「BST 单端轨相对 GND」还是「BST−SW=5 V」理解？（新 DFT 未给 st_sw 行）
3. 旧 run te-dali-acceptance：是否停掉并单方终态（推荐停），或保留继续跑？

RUN-LEDGER（本 run）现盘 = 6610 B / 5be045b25440fd4fa24478bc57a1b680eb9c6990c8d27c4d07f06c0939f660ed。


### 补充（2026-09-16 23:5x）：A 项已有代码级证据

`pmid-operating-point-evidence.md`（team/artifacts/tm601r3-20260916/）= 6454 B / `632ea15462e232cfaaf4455d7ffd03ae161d7c4846ca8ddb39621de0ead66844`：部署态 TM600 是 **PMID 15 V 台阶**（`test.cpp:9097-9115`），而 **TM640 的 DFT 行与新版 TM600 DFT 逐字相同**且以 ACM200 10 V/100 MA 实现 PMID=5 V + BST−SW=5 V（`:7492/:7521/:7526`）。⇒ 建议采用 5 V 工况，15 V 台阶标为已部署的另一工况；**不得拼用**。


## 2026-09-17 01:0x +0800 执行口径更新（R9，**本节覆盖本文中更早的门禁/PMID 口径**）

`team/artifacts/tm601r3-20260916/bst-path-resolution-r9.md` = 6053 B / `4f29d428a1226ce0cef822615f0d04ec855c4e5766a08595acb4b4172b6b3971`：

1. **四方矛盾已消解**：`test.cpp:9024-9033` 的「ACM200 到不了 BST」是其**黄金案例双地参考源安排**的局部论证，非硬件限制；本板实测 **TM607/608/609/640 四个函数全部「闭 K48/K76 且驱动 ch5」** ⇒ ch5→BST 可达。
2. **TM600 修法**：`:9081` 同一次 `SetOn` 内补 `K48_ACM5_AMP_REF`+`K76_ACM_BST`（= TM640 `:7513` 形状；正好补齐门禁 `missing=[48,76]`）。
3. **TM601 修法**：`:9255` 的 SetOn 无 BST 腿 ⇒ 必须给 TM601 登记 `K48/K76`，否则 `:9269` 的 `Set(FV,5)` 到不了 BST。
4. **操作点**：部署态 `:9035-9037` 自述「11/7.5 mΩ 配 pmid 5 V；DFT.csv 的 10/8 配 15/9 V」⇒ 采纳工作簿那套时，TM600 需 `BST_abs=10 V`（SW 跟随到 5 V）；TM601（SW≈0）单值 5 V ⇒ BST−SW≈4.99 V。
5. **仍未证实**：K48/K76 物理贯通、`vset` 权威语义、PMID 上 FV+FI 共存、部署态 20 V 台阶是否真到过 BST；`t8` 独立审查与第二个复核 `e1aec5f2-…` 未回收。


## 2026-09-17 01:2x +0800 沙箱实证补记（R10）

`team/artifacts/tm601r3-20260916/sandbox-fix-verification.md` = 3418 B / `af16a10bcaa00ba40cc26c637d3daddaf668a8dad91fb72230dc76c303ef808c`

- 在**沙箱副本**（非目标树）内仅追加 `K48_ACM5_AMP_REF, K76_ACM_BST` 到 TM600 的 SetOn：门禁契约断言由 `缺失=[48,76] exit 1` 变为 `缺失=[] exit 0`。
- **该门只校验闭集、不校验阶梯**：BST 设 5/10/20 V 都不影响它的红绿 ⇒ `t11` 不得以「门禁绿」替代操作点正确性；阶梯/寄存器/下电仍须 `t7`+`t8`+台架。
- 沙箱副本 `sandbox/test.cpp.k48k76` = 469745 B / `fab6262b32013154ad84dbf381b62936706c7c6804dd11fd5bedf8c9b5d703dd`（可作 `t9` 的实现对照，**但不得当作已审查候选**）。
