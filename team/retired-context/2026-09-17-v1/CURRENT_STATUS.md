# DALI 十项验收：恢复快照

> 快照时间：2026-09-16 19:55（北京时间）。这是恢复入口，不是自动更新的实时状态。接手时先读本页，再用 `.agent-teams/ate-dali-acceptance/team.json`、目标树现盘哈希和本次 run 的证据重算；不得把旧哈希或任务 `completed` 当作当前落盘证明。

## 21:29 职责修订与用户裁定（覆盖本页较早的 TM601 推断）

- AgentTeams 的稳定分工与旧规则归属已写入 [`ROLE_ROUTING.md`](ROLE_ROUTING.md)，`team/roles/`、`team/README.md` 和项目本地插件 patch 已接入。DFT 负责测试意图；原理图/Setup 负责物理通路与全局资源事实；**test-strategy-architect 负责逐 TM 的源表选择、BST/PMID 台阶及完整测试计划**；实现者只映射机台 API。当前通用 Schema 的 PASS 不代表策略交接完整。
- 规则审查角色现已增加前置语义交接检查：计划若缺具体通道/已验证通路、阶段、寄存器依据、实测/日志或异常清理，退回策略专家，不让实现者补猜。`team/start-ate-dsh.ps1` 会以 `--patch team/dsh-agent-teams.patch.yml` 启动 DSH；本次只核对了静态入口与文档引用，未重启正在运行的 DSH，也未声称新规则已作用于旧任务。
- 用户确认 TM600 DFT 核心意图基本正确：PMID—SW 施加 1 A、实测电压/电流求 HS RDSON、BST−SW 目标 5 V。**BST/PMID 逐级交替上/下电属于测试策略专家依据黄金案例制定的实现前计划**，不要求 DFT 专家写具体台阶。策略专家必须核对 DFT 的 PMID=5 V 与旧黄金/`voltage-inference.md` 示例的 PMID=15 V，不得静默照搬。
- 用户明确提出 TM601：SW—PGND 用 FPVI、BST−SW=5 V、BST=5 V。**早期 t38/t49 的“TM601 无 BST”仅是旧输入/推断，已与用户要求冲突，不得当作已确认需求继续传给实现。**精确操作点/阶段和可行性由策略专家连同 DFT/Setup 证据复核，未收口前保留阻断。
- 本次仅更新长期团队路由与角色文档，**未修改正在验收的 `dft-ir.json`、`setup-contract.json`、`test-plan.json`、实现 payload 或 VS 工程**。21:23 读取 `team.json`：`phase=running`、t49/t50/t53 completed、t51/t52/t54 pending；这是时点快照，下一次接手须重读。现有 DSH 会话不会因文档更改而自动重载旧任务提示或修正旧产物，t51/后续新任务必须显式复读新入口并重新审查输入。

## 不变目标与边界

- 在 `D:/Newtest/DSH/ATE-Coding-Plat` 使用 **DSH 的 dsh-agent-teams** 完成 DALI 十项验收：TM000、TM001、TM102、TM103、TM108、TM109、TM135、TM600、TM601、TM1205。
- 只允许修改 `D:/PROJECT6-DALI/ForCodexDebug` 副本及本 DSH 工作区内的约定产物；`D:/PROJECT6-DALI/devel` 保持只读。
- 编译和静态门禁成功不等于机台、电性或安全签核；本轮未做硬件实测。

## 19:55 已核对事实

### 19:58 增量（覆盖下文更早的 t38 进行中口径）

- DSH `team.json`：`phase=running`，19:57:32 更新；五位成员为 `working`。`t38=completed`，实现者从 TM601 payload 删除无 BST 需求的 ACM 5 V 激励，交付 payload **39457 B / Python SHA-256 `2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9`**，并报告沙箱 `relay-trace`、`bst-sw`、`awg` 无新增红；这些是实现者自报，尚待独立复核。
- `t39`（契约 owner 路径判定）和 `t40`（rule-reviewer 独立判定/新字节复核）仍为 `pending`。`ForCodexDebug/source/test.cpp` 19:58 实测仍为 **469714 B / `15c7d2b8…`**，`t29-apply-result.json` 不存在；故不存在“已落盘/最终门禁/编译”结论。t38 输出还提醒继电器端子图的默认导通语义与普通弹簧继电器直觉不同，独立复核须确认该点。

- DSH Captain 已明确裁定 **暂不执行 t29 REPLACE**：TM601 的 `SW12_U1REF_BST_ACM.Set(FV,5,…)` 与 K110 未闭合的路径存在阻断性分歧；t38 已派给 ate-implementer 修复，须契约 owner 与 rule-reviewer 独立判定、复核后才可落盘。DSH 页面显示“本轮无待你决定项”、主代理运行中。用户已点击先前的“允许”，但这不等于本次写入实际发生；以目标树哈希和写入结果为准。
- 19:55 实测 `ForCodexDebug/source/test.cpp` 仍为 **469714 B / `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`**，`t29-apply-result.json` 不存在；`devel/source/test.cpp` 仍为 **434629 B / `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`**。本次读取哈希用 Python SHA-256；PowerShell `Get-FileHash` 在当前环境返回不同值，需查明原因，不要混用作为 pin。
- 19:55 实测 payload 已继续漂移到 **38888 B / `f536c7e4896f272ca9b8dc2356cb557c622d4a4e387a61f32ed7beea08421ef0`**；`t29_apply_replace.py` 仍期望 **38147 B / `272667f3…`**。当前脚本若执行会在写入前因 payload pin 不符而中止；应由 DSH 在 t38 修复及复核后重新 pin，不能沿用旧审批或旧审查哈希。

- `t23` 实现内容、`t24` 独立审查完成；先前 TM600/TM601 版本已由 Captain 落盘。目标 `ForCodexDebug/source/test.cpp` 仍为 **469714 B / SHA-256 `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`**（18:53:33）。此哈希是 **t29 修复前** 的部署态。
- 对此旧部署态，Release Win32 编译已有 0 error / 0 warning 记录，门禁 0 NEW-RED；`cbit` 为既有 KNOWN-RED。这些结果不能复用为 t29 落盘后的最终证据。
- 独立复核确认 TM600 的 ACM→BST 激励路径缺 `K110`；旧门禁未能检出，故旧版本不得宣称最终验收通过。K109 曾有分歧；最新独立端子图复核已更正为“不属 ACM 源路线”，但 t29 payload 同闭 K109 仍被判符合 rev24 字面集合，需在最终报告区分“字面合规”和“实际必需”。
- `t29` 已标记 `completed`，但其交付后的 payload 仍在修订：19:20 的 36381 B / `73b511b7…` **已作废**；19:33 现盘为 **38147 B / SHA-256 `272667f3f79393b6b1365237c7ac01bed7a527d2984d53d1d5ae6804515057c0`**。这是易漂移产物，落盘前必须重新计算并独立复审；**Captain 对目标树 REPLACE 落盘尚需确认**。不得把 t29 completed 推导为目标树已更新。
- **历史审批注记（已被上方 19:55 快照取代）**：19:50 页面曾请求执行 `t29_apply_replace.py`，当时脚本期望 36381 B / `73b511b7…`。19:52 DSH 将脚本期望更新为 38147 B / `272667f3…`，随后 t38 修复又使 payload 继续变化。当前不能把旧审批、旧脚本或旧复核作为新字节的落盘依据。
- t29 同时主动上报三处契约不一致：`closedRelayNumbers` 与包含 K109 的路线表不一致、ACM 驱动 BST 的端子表述不清、另有未采用的 CH0 High→BST 路线。`t35` 已完成契约归口但**未改契约**；独立规则审查 `review/t35-reconciliation-review.md` 用 G6K-2G-Y 端子图更正其早期推断：**K109 不在 ACM 源路线、K110 单独把 ACM18 在 PB0/BST 间切换**，但认为 t29 同闭两者仍满足 rev24 字面集合（payload pass 不变）。审查建议方案 A 增补按路线标注，待 Captain GO；未获 GO 则按登记性限制方案 B。是否保留多闭的 K109 与后续契约语义仍须明确记录，不能把合同合规等同电学签核。
- **另有 TM601 独立审查缺口（潜在误驱动）**：`review/t29-k110-implementation-review.md` §2 指出 TM601 也执行 `SW12_U1REF_BST_ACM.Set(FV, 5, …)`，但其 `pinRouteTable` 无 BST 条目，`relaySet` 与当前 SetOn 均无 K109/K110。原理图连接图 `SCH-Connect-Map.txt:724-725` 明示该 ACM18 源在 **K110 未动作时经 NC 指向 PB0_F/PB0_S**；因此若此 5 V 设置实际到达该源，风险不只是“BST 未被驱动”，还可能是 PB0 被意外驱动。该风险是从连线与代码作出的推论，**尚非机台实测**。t35 的已完成摘要未见第四项的明确裁定；落盘前必须向契约 owner/独立规则审查核实，不能将“TM600 payload 审查 pass”外推为 TM601 电学成立。
- `t27` 已完成 test-plan v21（176875 B / SHA-256 `f0f825dd302d4105676b113f2335bc1f6fe54c8bcd46a32d621c1026c111dc04`，双次生成同哈希、Schema PASS）；`t31` 已完成审计链自保护，live meta 未改。`t28` 已交付 RS-1..RS-4 断言和回退红证，`review/t28-independent-opinion.md` 的独立审查为 **ACCEPT**；但任务此前因审查未回收而标 `failed`，需由 Captain 建可解锁的承接/收口任务，不得手改终态。`t30` 守卫实现及红证已完成，任务同样因独立审查未回收保守标 `failed`。
- `t32` 首轮独立核验已如实标 **failed**：目标树缺 K110（t29 修复尚未落盘），现有审查/门禁证据与被核验字节的对应关系不足，且 `team/schemas/verification-report.schema.json` 缺失使报告 schema 校验不能通过。修后须重做独立核验并建立可解锁的新任务，不能把 failed 任务当 pass。
- Captain 已补 `verification-report.schema.json`；`t37` 复验确认报告校验 **exit 0 / PASS**，只关闭 t32-F4，整体 `verification-report.json` 的 verdict **仍为 fail**（F1/F2/F3 未闭合）。这不构成最终验收。
- `t30` 的新 BST 守卫已给出预期阳性红证：`gate-logs-t30/bst-sw.log` 显示 TM600 契约必需 `[60,61,83,110]`、旧部署版缺 `[110]`，门禁仅 `bst-sw` 转 NEW-RED；TM601 按现契约缺失 `[]`。这证明守卫能抓 TM600 漏 K110，但**不解决上文 TM601 激励可达性的契约缺口**。任务因独立复核未回收保守标 `failed`，其下游 t33 不会自动解锁；复核后需显式替代任务。
- `t30` 扩展探针还显示 **TM1205**（十项验收之一）在现契约 `bst2sw.usedByTm` 中，扩展作用域报缺 `[61,110]`；可能是契约别名/路线登记错位，也可能是实现缺路径，**尚未裁定**。不能以默认守卫只扫 TM600/TM601 作为 TM1205 通过证据；须契约 owner + 独立规则审查单独核对并记录结论。
- `t36` 已完成 manifest 对账并通过 schema：现盘 `implementation-manifest.json` **42906 B / SHA-256 `c6f56d2fd7665a2f4d90b8fbc3044e448e2aa013bf12825b61b760ef98d1c0e0`**，状态明确写为“旧版 APPLIED + t29 PENDING LANDING”，t33 构建报告为 PENDING，t24 审查覆盖已部分撤回；不得把 manifest 的“旧版已落盘”读成 t29 已落盘。
- 旧 t7/t8/t9 因依赖失败终态 t5 无法正常解锁；替代任务已建：`t32` 独立核验、`t33` 最终树门禁及 Release 编译、`t34` 最终集成报告。其结论必须绑定 t29 实际落盘后的新哈希。

## 下一个可执行闭环

1. 先按独立端子图复核收敛 t35 三项契约不一致，**并补判 TM601 设置 BST ACM 5 V、K110 未闭可能误驱动 PB0 的第四项**；对现盘 t29 payload 的新哈希重新独立审查。Captain 只把获批增量在允许的目标副本执行精确 REPLACE，保留写前备份、重读、逐字节/哈希验证。需要跨工作区权限时仅对确切动作走 DSH 一次性审批；不得以本页代替审批。
2. 独立复核 t28/t30 守卫及回退阳性对照，并以可解锁的替代任务承接其 failed 状态；在目标树 **新哈希** 上运行 t30 修后转绿对照，同时单独裁定 TM1205 的 `[61,110]` 扩展探针；更新 test-plan v21 的引用 pin 并核对 t31 审计链。
3. 为 t32 首轮 fail 建修后独立复验任务；报告 schema 缺口已由 t37 关闭，复验须在最终目标字节上处理其余 F1/F2/F3 与证据一致性。由 t33 或其可解锁替代任务重跑全部门禁和 Release 编译，再由最终集成任务汇总十项逐项证据、保留所有未实测项和残余风险。旧 t34 若仍依赖 failed t32，须显式改用替代任务，不能等待自动解锁。任何代码/规则/元数据后改，都须重跑受影响门禁与构建。
4. 把最终事实写回 `team/EXECUTION_PLAN.md` 与 `team/artifacts/acceptance-20260916-dali10/RUN-LEDGER.md`；本页应更新为最新单一恢复入口。每次更新写明时间、目标树哈希、任务状态、门禁/编译对应哈希、未决项与下一动作。

## 20:2x 更新（Captain，本页为最新单一恢复入口）

- **落盘仍被阻断（用户裁定的第四项）**：TM601 的 `SW12_U1REF_BST_ACM` 5 V **可达性**须两方独立判定。`t39`（契约 owner）**已完成**、`t40`（rule-reviewer）**在跑**；**新增 `t42`（schematic-expert）**判定 **ACM200 引脚归属**：契约通道宏 `Pin_Channel_define.h:20` 指向 pin `_5` ⇒ 通路 `S5_ACM200_FH5/SH5`（`SCH:673`）需 **`[48,76]`**；若为 `FH18/SH18` ⇒ 需 **`[110,61]`**。**`t39` 与复核方的结论都建立在 pin-18 前提上 ⇒ `t42` 是决定性前提。** `t40`+`t42` 闭环前**不落盘、不改 payload/契约**（不得折中、不得单方裁定）。
- **`t39` 结论（四方证据）**：TM601 的 5 V **到不了 BST**，落在 **DUT 引脚** `PB0_F_S1`/`PB0_S_S1`（同网 `PWM1_*`/`K147_PB0_OSC`/`S24_P10`）⇒ 悬空激励 + **对 DUT 引脚的非预期 5 V 偏置风险**；契约四处（`aliasesUsed`/`relaySet`/`scopePins`/`pinRouteTable`）独立排除 BST；**推荐移除**（`t38` 已执行）。交付件 `t41-tm601-bst-path-determination.md` = 11,032 B / `24ba7b9060dc80477f15ec0ab63127ba846b13fd47435b9fe6abd3a7fc49d1d1`。**FACT/INFERENCE/UNKNOWN 已分离；UNKNOWN 未写"已排除"。**
- **payload 现值（易漂移）**：**39,457 B / `2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9` @19:55:59** ＝ `t38` 后交付件；**38,147 / `272667f3…`（复核方 verdict 的对象）与 36,381 / `73b511b7…`、35,014 / `444810dd…` 均为过渡态、盘上无副本**。19:55:59 那次 +1,310 B 的**归属＝`t38`（作者 ate-implementer）**，非无主编辑。
- **引用纪律（四条，已生效）**：① 单一真源 `gate-logs-t28/t28-anchors.json`；消息只给「路径 + size」，值一律 python(rb) 现算（实测：pwsh 与 python 对同一文件 **size 相同而哈希不同** ⇒ **只有 python 明文哈希可作锚**）；② **内容键**（`PER-FUNCTION JUSTIFICATION` ×1 + **去注释后**可执行 `K109_BUSL1_PB0` ×1、`K110_ACM18_BST` ×1 + `TM601 ACM Sets=0 / TM600=10`）+ 现算哈希 + mtime；③ **"可执行计数"必须写明剥离方法**（`//` 行首剥离会漏掉**行尾注释** ⇒ 实测 `ERROR_RES` 会被算成 4 而非 2；正确做法＝按行 `re.sub(r"//.*$","")` 再计）；④ **给出哈希即冻结**，若再写须交回新哈希并由复核方**对新字节重出 verdict**。
- **已收口**：`t28` + `t30` 独立复核均 **ACCEPT**（`t41`＝复核回填任务已建）；`t27` 计划 v21 已签收；`t31` 平台闭合；`t35` 契约归口闭合（文档 37,112 B / `d8455cee…`）；`R1`（`run_gates.ps1:119` 正则）**本轮不派**（避免作废 t25 已复核产物），登记为残余改进；`t35` E.3 的"禁止单独引用 (a)"一行**改由 `t34` 承载**（不再改冻结中的 t35）。
- **待执行（判定一到即动）**：(甲) 需修 ⇒ **先契约 rev 25**（按路线分组 + 三条登记待办：`TM600.aliasesUsed += bst2sw`；TM1205 移出 `bst2sw.usedByTm` 并建 BST1-SW1/BST2-SW2 独立别名；补 `TM1205.aliasesUsed`）→ 改 payload → 三门禁 → 独立复核 → **Captain REPLACE**；(乙) 不需修 ⇒ **一次 REPLACE `2d0984d9…`** → **Captain 代跑 Release 编译**（交回 `build.log` + 0/0 逐字 + `F12011.dll` 哈希；成员会话对目标树只读、`MSBuild MSB3491`）→ `t33` 转 pass → `t34` 终稿（blocked/fail 项如实登记：`T32-F1/F2/F3`、`DELIVERED≠DEPLOYED`、门禁盲区 + **B-6**、meta 重生成风险、`K109↔FPVIe1` 耦合三条并列、编译≠电性、无机台验证）。
- **边界不变**：`devel` 零写入；**未做任何机台/电性验证**；**编译闭环 ≠ 电性签核**。

## 20:8x 更新（Captain，最新单一恢复入口）—— **ch5 定案**，**唯一门 = `t43`**

**① 落盘门**：`t39` ✅／`t40` ✅（终稿 `review/t40-tm601-bst-determination.md` = 23,399 B / `374300057a2174c136033451f29d7f5bf50220f2aa26ce015c6d6f6ea5928a8c`，另交叉意见 `review/t40-crosscheck-t39-opinion.md`）／`t42` ✅ pass／`t44` ✅ 补遗 ⇒ **现唯一门 = `t43`**（Captain 另派的独立复核 + 裁定：① **ch5 vs ch18** ② **TM600 的 `K109/K110` 去留** ③ 是否允许改用 ch18+`[110]` ④ `rev 25` 先于 payload 的顺序确认；含**循环禁令**：不得以契约 `channelsInScope`/`relayChain` 标签为权威）。`t43` 须输出 **(甲)** 采纳 ch5 + 逐条 accept/reject `t42` 四层证据，或 **(乙)** 坚持 ch18 并给**新的独立依据**（不得再用已被其作者撤回的映射）＋并列分歧与 locator ⇒ **(乙) 即上报用户裁定**。

**② ch5 定案（六条独立证据同向 + 少数派唯一权威被作者撤回）**：`SW12_U1REF_BST_ACM` = ACM200 **channel 5**（`Pin_Channel_define.h:20 = "S5_5,…"`）⇒ 到 BST 需 **`K48`+`K76`**；`K110_ACM18_BST` 属**另一台仪器 `PB0_BST_ACM`（`:33 = "S5_18,…"`）**。证据：宏表原文／**TM600 段只调 `SW12_U1REF_BST_ACM`（10 次 `.Set`，非零 **7**）不调 `PB0_BST_ACM`**（Captain 实测）／行为层 `test.cpp:7000/7087/7170/7513` 闭 `K48_ACM5_AMP_REF`+`K76_ACM_BST` 且 `:6997/:7598/:7621` 注释写 `(FH5→BST)`／复合宏穷举（唯一 `ACM200[] -> BST` = `K_BST_ACM=48,76`）／控制组 5/5 ＋ ch5·ch18 网决定性分离／**契约 owner `setup-architect` 撤回自身映射错误**。**BST–SW 闭集 = `[48,61,76]`**。

**③ 定案批（`t43` 结案后一次性执行）**：**rev 25 先于 payload，同批落盘，只重跑一次门禁 ⇒ 期望 `bst-sw` = GREEN**（不存在"落盘后仍红"的例外路径）。**rev 25 范围**：路线按通道分组（ch5 `[48,61,76]`／**ch18 单列**／FPVIe 组）＋ `bst2sw` 映射更正（保留原文）＋ **ACM200 行按通道分列**＋ **`t30` 期望依据改 `[48,61,76]`**＋**三条登记待办**（`TM600.aliasesUsed += bst2sw`；**TM1205 移出 `bst2sw.usedByTm` 落 `bst1_sw1`/`bst2_sw2` 变体条目**；补 `TM1205.aliasesUsed`）＋ `acmDriveFrame`／`unrealisableRoutes`／`terminalAssignment` legacy ＋ **TM601 显式登记"无 BST 轨道、不采用 ACM 驱动"**。**payload 改动**：TM600 **补 `K48_ACM5_AMP_REF`+`K76_ACM_BST`**，**移除 `K109/K110`**（rev 25 更正映射后"依约保守"基础消失；保留会把 `FPVIe1_FL/SL_BUS_S1` 低域总线与 ch18 源脚耦合到 BST）；**`L416-420` 改为只陈述操作事实**（不引 `relays.md` L31 口诀）。

**④ 两条新实质结论**：**(a) 先例一致性**：部署态**六个函数**（`TM607/608/609/616/640/641`）把源送 BST **一律经 `K48+K76`、无一处用 K110**；`K_BST_ACM` **0 处调用点** ⇒ TM600 缺 `[48,76]` 是**与既有实现不一致**，非新要求（措辞用"已实现/已部署"，不说"已在跑"）。**(b) BST 节点汇聚不变式**：`K110` pin4/5 与 `K76` pin4/5 **同网**；BST 有**七源** ⇒ 闭 `K48/K76` **不是选源而是多源汇聚**，**须与"显式 `RELAY_OFF` 共驱仪器"成对**（`TM641` 先例）。

**⑤ 危险项（须写入 `t34`）**：**部署态 TM600 的活危害** —— 驱动 ch5 源（10 次 `.Set`、阶梯 `0→5→10→15→20→15→10→5→0`、量程最高 `ACM200_40V`）而函数体内 **`K46/K48/K49/K76/K109/K110` 全 0 命中** ⇒ 源被送到 **`SW1_F/SW1_S`**，而 **`SW1` 不在 `scopePins` 内** ⇒ **越界驱动相节点**（`SW1` 是另一开关相节点，非 `SW` 的 Kelvin 抽头）；**电性后果 = UNKNOWN（owner/机台判）**。**跨项约束**：ch5 **三目的地互斥**（`SCH:673` BST／`:775` SW1／`:778` SW2）⇒ **TM600 的修法不能描述为"补两个继电器"**（`t47` 判定中）。

**⑥ 在跑任务**：`t43`（门）／`t34`（setup-architect 已 claim，**先出 blocked/fail 如实版**）／`t45`+`t46`+`t48`（三个补遗）／`t47`（ch5 端点共享与跨项冲突）。

**⑦ 引用纪律（四条，全部生效）**：① 单一真源 `gate-logs-t28/t28-anchors.json`（**稳定锚点 = 剔除 `anchorsObservedAt` 行后的主体哈希**；消息只给「路径 + size」；值一律 python(rb) 现算）；② 内容键须**去注释后可执行计数**＋**写明剥离方法**（`re.sub(r"//.*$","")`；行首剥离会把 `ERROR_RES` 算成 4）；**`ACM Sets(<fn>)` 唯一合法定义 = "经剥离后仍非空且含 `.Set` 的行数"**（**不是**"仪器名出现次数"——二者现盘巧合相等，属**潜伏假通过**）；③ **冻结声明只写「文件名 + 现算哈希 + 现算时刻」**，尺寸与哈希同一命令取得，**转述记忆值一律视为未验证**；④ **给出哈希即冻结**，再写须交新哈希并由复核方对**新字节**重出 verdict。

**边界**：契约仍 **rev 24 / `fd00a508…`**；`devel` 零写入；**未落盘**；**未做任何机台/电性验证**；**编译闭环 ≠ 电性签核**。

## 状态语义

- `payload authored` ≠ `target deployed` ≠ `independently reviewed` ≠ `gates/build on final tree` ≠ `hardware signed off`。
- 不以“12 门绿”替代电路路径核验：旧门禁漏检 TM600 的 K110 是已经证实的反例。
- `team.json` 是任务状态源；本页是人工恢复说明。两者不一致时先查证据再更新本页，不得静默覆盖历史。

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

## 2026-09-16 22:0x +0800（CURRENT_STATUS 条目） TM601 DFT 修改后的裁定与新 DAG（Captain，最新单一恢复入口）

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


## 2026-09-16 22:0x +0800 冻结隔离的必要性（实测证据）

- 本次核对期间，**旧 run 的活跃写入被实测到**：	eam/artifacts/acceptance-20260916-dali10/setup-contract.json 从 21:49:39 的 **376,308 B / d9ecffb0…** 变为 **377,128 B**（同一分钟内的两次现算），说明旧团队仍在改写旧目录产物。因此新 DAG 的输入一律改为 	eam/artifacts/tm601r3-20260916/snapshot/ 的冻结副本（setup_contract.json 376,308 B / d9ecffb0…、test_plan.json 185,689 B / 707ce845…），并以 pin/snapshot-manifest.json 4014 B / 3de6c6d85ed8cd6c389f63e9cea705a6044d12cc6418e33b4aae5748cd9ac13e 固定；任何成员读旧目录的现值都将被视为不可复现输入。
- 目标树与 devel 本次前后未变：ForCodexDebug/source/test.cpp = 469,714 B / 15c7d2b8…36c01a；devel/source/test.cpp = 434,629 B / 5c9cb3f9…ac3317（只读）。


## 2026-09-16 23:2x +0800 两处自我更正 + 门禁实跑判据（覆盖本页此前的门禁口径）

**① 撤回「bst-sw 门靠 meta `capAuthority.powered_pins` 指纹」**：那是 `scripts/verify_bst_sw_sequence.py` docstring L5-L7/L81-L85 里**已被作者于 2026-09-13 重写掉的旧实现**。实际选靶判据在 `derive_targets()` L100-L101（函数体含 `rampi_capv(`），拓扑由 `SetOn` 内 `K_FPVIH_TO_PGND`→LS / `K_FPVIH_TO_PMID`→HS 判定，判不出则 WARN 跳过（L106-L112）。

**② 撤回「TM600/TM601 不在 bst-sw 门作用域」**（我 23:0x 的推断，已被实跑推翻）：门内另有一条**独立的契约闭集通道**，且**默认作用域就写着这两个函数**——`DEFAULT_TM_SCOPE = ["TM600_HS_RDSON", "TM601_LS_RDSON"]`（L259）；`check_contract_closures()` L429-L467 对 scope 内每个函数做「契约期望集 − payload `cbite.SetOn` 集」的致命断言；判据 = `aliasResolution[*].resolution.closedRelayNumbers`（L261-L263）；`pinRouteTable`/`relaySet` 仅作 locator；读不到契约 = 红（L505-L507）。

**③ 实跑判据（只读，本轮执行）**
```
python scripts\verify_bst_sw_sequence.py --src D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp \
  --contract team\artifacts\tm601r3-20260916\snapshot\setup_contract.json
→ [t30] TM600_HS_RDSON: 期望 [48,60,61,76,83] 缺失 [48,76]
→ [t30] TM601_LS_RDSON: 期望 [60,61,154,155] 缺失 []
→ [scan] targets=4 FAIL=2 ; exit=1
```
其中 `targets=4` = `TM607_BUCK_LS_ZCD / TM608_BOOST_HS_ZCD / TM609_BOOST_HS_NEG / TM640_BOOST_HS_OCP`（**不含** TM600/TM601，因它们无 `rampi_capv`）。附带确立：**部署态 TM600 的实际闭合集里连 `K109/K110` 都没有**，只有 `{13,57,60,61,83,85,126}` ⇒ 属**仅漏腿**（与 t48 记载一致）。

**④ 新事实（对契约修订重要）**：冻结契约下 **TM601 的期望集只有 `[60,61,154,155]`，无任何 BST 要求** ⇒「TM601 BST=5 V」在门禁层面**当前无约束**，必须由新 DAG 的 `t6` 登记，否则永远不被检查。

**⑤ 新陷阱（实测，必须写进 t9/t11 口径）**：把**只含增量的候选 payload 文件**当 `--src` 会得到 `targets=[]`，脚本在契约闭集断言**之前** `return 0` 并打印「空 PASS」（**实测 exit=0**）⇒ **假绿**。硬要求：`--src` 必须指向**等价全量源文件**，且必须同时在场 `[scan] targets=N (N>0)` 与两行 `[t30]`；**空 PASS 一律记为「未执行」，不得记为通过**。

**⑥ 另一 run 的活跃写入（本会话第三次实测）**：`acceptance-20260916-dali10/setup-contract.json` 377,128 B → **377,276 B**；其 `team.json` 亦反复漂移。⇒ 新 DAG 的输入只认冻结副本（`snapshot/setup_contract.json` = 376,308 B / `d9ecffb0…`）。

**⑦ 未做**：未运行完整 `run_gates.ps1`（无已落盘新树，产物会与最终树不对应）；未改任何门禁脚本；未落盘任何 payload；`devel` 零写入。裁 A1（TM600 PMID=5 V）因独立复核未回收，仍标 **provisional**。


## 2026-09-16 23:4x +0800 BST 节点源表与 B 项降级修正（新增）

- 新增证据件 `team/artifacts/tm601r3-20260916/bst-node-source-table.md` = 7538 B / `0b17bc652745802d77f806e21ea4169b20e0ac65b69405b599cea0c2f19e2a26`：BST 节点**8 条来路**逐行 locator（ACM200 ch5 `K48,K76`；FPVIe CH0-High `K46,K48,K76`；CH0-Low `K109,K110,K138,K139,K145,K146`；S10_CH0_A `K141,K46,K48,K76`；QVM 高/低端；FPVIe CH1-High `K131,K132,K134,K135`；CH1-Low `K109,K110`），以及 ACM200 **ch5/ch18 两路可达 ⇒ 多源互斥**、漏闭 K48 ⇒ **改道 SW1/SW2 而非开路**。
- **归类张力（待 t2 定案）**：`knowledge/hardware/relays.md:99` 把 `K46~K59` 列为 **MOS P2P 默认断开**，而 `K48/K49` 在别处按 Share/BUS 使用（`:95/:96/:105-108`）。
- **B 项修正**：TM601「BST=5 V」与「BST−SW=5 V」在 LS 导通（`V(SW)≈7.5 mV`）下数值几乎等价（≈4.99 V）⇒ 不再当作互相矛盾；真正待定 = 由哪一路源驱动 BST、是否需要 `bst_sw` 差分行。工作簿 `AH133` 的 `SW-PGND=0.3`（无单位）不足以定标。
- 裁 A1（TM600 PMID）仍 **provisional**（独立复核未回收）。


## 2026-09-16 23:5x +0800 A 项（TM600 PMID）代码级证据 + TM601 叙事更正

- 新增 `team/artifacts/tm601r3-20260916/pmid-operating-point-evidence.md` = 6454 B / `632ea15462e232cfaaf4455d7ffd03ae161d7c4846ca8ddb39621de0ead66844`。
- **部署态 TM600 是 15 V 台阶**：`test.cpp:9097-9115` 把 `BST`（0→5→10→15→20 V）与 `PMID`（0→5→10→15 V）**交替**递进以维持 BST−SW=5 V；`:9114` 终态 PMID 15 V / BST 20 V；`:9086` 注释自述 `PMID 15 V, VBAT 4.2 V`。⇒ `voltage-inference.md` 的 15 V 台阶 = **部署态那条台阶**。
- **部署态 TM640 是 5 V 工况先例**：`test.cpp:7492` 的 DFT 行 `vset[vbat,3.5] vset[pmid,5] vset[bst_sw,5] vset[vdrv,5]` **与新版 TM600 DFT 逐字相同**；`:7521/:7526` 用 ACM200 10 V/100 MA 两步实现 BST−SW=5 V；`:7513` 闭集含 `K48/K76`。
- **裁 A 建议（强证据、未独立复核）**：采用新版 DFT 的 `PMID=5 V` + `BST−SW=5 V`；把 15 V 台阶标注为已部署的另一种工况并保留；**禁止把两者拼用**（会产生 20 V BST 台阶且与台阶自身注释矛盾）。
- **TM601 叙事更正**：部署态 `test.cpp:9269` 就有 `SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, RELAY_ON)` ⇒ 旧 run「TM601 无 BST / 移除 ACM 激励」的表述与部署态代码不符（其 SetOn 仅未闭 K48/K76）。


## 2026-09-17 00:4x +0800 独立复核 DISAGREE + 三项撤回（覆盖本页 A 项口径）

- 复核件 `team/artifacts/tm601r3-20260916/review/independent-review-pmid-ruling.md` = 28221 B / `533e71b99f74a7249c3d193b1a1eca7232861b3fd2cfee3ec3007671035978c8`；回执 `review/captain-recovery-r8-independent-review.md` = 6223 B / `b2e6507547d91427faa6b2ea78c5b23f11c04145f00eba190771468079c1bd45`。
- **裁定：DISAGREE with Ruling A1 as written**（方向 5 V 大概对，但论证 non-sequitur、权威面不全、字面执行最危险）。
- **撤回**：「15 V 台阶在 5 V 工况会得 BST−SW=15 V ⇒ 支持 A1」——前提不成立：部署态 TM600 `:9081` **从未闭 K48/K76**，20 V 台阶**未被证明到达 BST**。
- **四方矛盾（决定性）**：`test.cpp:9027-9028` 声称「ACM200 reaches SW only and cannot reach BST」，而 `SCH-Connect-Map.txt:672-674` 是 `S5_ACM200_FH5 -> K48 -> K76 -> BST_F`，TM640 `:7513` 又确实闭了 K48/K76 ⇒ **契约/门禁/已部署代码/注释四方不一致**，须先由用户裁定哪份权威。
- **修正后的建议**：议题应改为**四字段耦合工况对账**（PMID 5/15、VBAT 3.5/4.2、iset[sw] vs iset[pmid2sw]、11/10 mΩ），并优先回答「BST 是否可达」；A1 仅作**工作假设**，等第二个复核 `e1aec5f2-…` 回收后定。
- 已知事实：`voltage-inference.md:142-143` 逐字转录 `DFT.csv`（契约引用的权威输入）；21:46 那次改动**只有 TM601 行新增 `vset[bst,5,…]`**（见证件 `d9d721a3…` 已在改动前含 `vset[pmid,5]`）。


## 2026-09-17 01:0x +0800 ch5→BST 四方矛盾消解（R9）

- 新增 `team/artifacts/tm601r3-20260916/bst-path-resolution-r9.md` = 6053 B / `4f29d428a1226ce0cef822615f0d04ec855c4e5766a08595acb4b4172b6b3971`。
- **普查（我实测）**：闭 K48/K76 且驱动 ch5 的函数 = TM607/TM608/TM609/TM640（**4/4 全 True**）；TM600 与 TM601 驱动 ch5 却**都不闭 K48/K76** ⇒ 「本板 ACM200 到不了 BST」不成立，TM600/TM601 属**漏闭**。
- **更正 R8**：`test.cpp:9024-9033` 的「ACM200 reaches SW only and cannot reach BST」是其**黄金案例双地参考源安排**的局部论证，**不是硬件限制**，与 `SCH:672-674` 并不矛盾；我 R8 回执的「注释与端子图矛盾」说法**撤回**。
- **更正 R8 之二**：`test.cpp:9035-9037` 部署态已写明「11/7.5 mΩ 配 pmid 5 V；DFT.csv 的 10/8 配 15/9 V」⇒ A 项不是四个零散字段冲突，而是**两套来源二选一**；工作簿那套自洽且与门禁取向一致。
- **修法**：TM600 补 `K48+K76`（同一次 SetOn）；TM601 补 BST 腿登记（否则其 ch5 5 V 到不了 BST）；TM600 需 `BST_abs=10 V` 才有 BST−SW=5 V。
- 未证实：K48/K76 物理贯通、vset 语义、PMID 上 FV+FI 共存、部署态台阶是否真到过 BST；第二个复核未回收。


## 2026-09-17 01:2x +0800 沙箱实证：TM600 补 K48/K76 ⇒ 门禁契约断言转绿（R10）

- 新增 `team/artifacts/tm601r3-20260916/sandbox-fix-verification.md` = 3418 B / `af16a10bcaa00ba40cc26c637d3daddaf668a8dad91fb72230dc76c303ef808c`；沙箱副本 `sandbox/test.cpp.k48k76` = 469745 B / `fab6262b32013154ad84dbf381b62936706c7c6804dd11fd5bedf8c9b5d703dd`。
- **实证**：未编辑副本 → `TM600 缺失 [48,76]`、exit 1；**仅追加 K48+K76** → `TM600 缺失 []`、exit 0（`BST-SW SEQUENCE PASSED`）**。
- **关键限制**：本门**只校验继电器闭集、不校验 BST 阶梯电压** ⇒ **门禁绿不等于操作点正确**；且它不证明继电器实际物理贯通。
- **未动**：目标树 `15c7d2b8…`、devel `5c9cb3f9…`（前后哈希一致，实测）；未改脚本/契约/计划；无机台验证。
