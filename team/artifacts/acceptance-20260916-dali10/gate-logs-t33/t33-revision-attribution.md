# t33 修订归属（rev`15c7d2b8…` vs 待落盘 `2d0984d9…`）——红/绿归属规则

- 触发：setup-architect 提醒 **DELIVERED ≠ DEPLOYED**，并要求把我报告里的红**明确归属到部署修订**，
  而不是归属到构建过程或 t29 的 payload（这正是 t32-F3 指出的错误类型：把不属于当前修订的门禁证据当成当前证据）。
- 我方处置：**接受该要求**；本文先落**归属规则与三方状态**，`build-report.json` 的字段在**落盘后与 verdict 翻转时一次性加入**
  （避免对已交付产物做只读锚点以外的多次改写，也保证 t34 只看到一个明确的转换点）。

## 1. 三方状态（现刻实测，只读，含时刻）

| 角色 | 对象 | size / sha256 | 时刻 | 关键命中 |
| --- | --- | --- | --- | --- |
| **DEPLOYED（编译输入）** | `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` | **469,714 B / `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`** | 18:53:33 | `K109_BUSL1_PB0` = **0**、`K110_ACM18_BST` = **0**（K57 ×9、K126 ×3 在） ⇒ **缺 t29 修复（t23 版）** |
| **DELIVERED（待落盘 payload）** | `team/artifacts/.../implementation-payload-TM600-TM601.cpp` | **39,457 B / `2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9`** | **19:55:59** | `K109` ×11、`K110` ×24；SetOn 段含 `K109_BUSL1_PB0, K110_ACM18_BST` ⇒ **含修复** |
| 同上，setup-architect 通报值（**已被更晚一次覆盖**） | 同文件 | 38,147 B / `272667f3f79393b6b1365237c7ac01bed7a527d2984d53d1d5ae6804515057c0` | 19:30:55 | 含 K109/K110 |

⚠️ **payload 在我复核时已是第三个值**（38,147 → **39,457 B / `2d0984d9…` @19:55:59**）。
⇒ 引用 payload 一律**现算**（与 manifest/t35 同一条纪律）；**`272667f3…` 亦已非现盘值**。
⇒ **无论哪个 payload 版本，"未落盘"结论不变**：部署态 `test.cpp` 仍为 `15c7d2b8…`、K109/K110 命中 0。

## 2. 归属规则（写入 `build-report.json`，落盘时生效）

```
compiledRevision        = 15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a   ← 本报告一切门禁/编译证据的归属对象
compiledRevisionLabel   = t23 (pre-t29; K109/K110 absent)
expectedAfterReplace    = <落盘时现算的 payload sha256>（当前候选 2d0984d9…；落盘即以此为 expected）
attributionRule         = 红/绿归属跟随 compiledRevision：本报告中的 bst-sw = NEW-RED（K110 缺失）属于
                          **部署修订 15c7d2b8…（t23）**，既不属于构建过程，也不属于 t29 的 payload（后者尚未部署、无法被判红）
postReplaceExpectation  = 落盘 2d0984d9…（或落盘时现算值）后：bst-sw 应从 NEW-RED 转 GREEN（其余 11 门不变）
```

**要显式说清的三件事**（防后人误读，也是 t32-F3 的类型错误）：
1. `bst-sw = NEW-RED` 是**被 t30 新断言正确判出的**、且是**对部署修订 `15c7d2b8…` 的正确判定**；
2. 它**不是**构建过程/环境问题，也**不是** t29 payload 的问题（payload 尚未部署，根本未被评过）；
3. `cbit = KNOWN-RED` 是**基线豁免**（`gate_baseline.json` 未改），与本次红无关；
   `relay-trace`/`input-sync` = GREEN ⇒ t25/t28 落地断言在位且通过。

## 2.1 部署态"活危害"（Captain 独立实测，我复核确认；归属对象仍为 `compiledRevision = 15c7d2b8…`）

| 观测（部署态 `test.cpp` `15c7d2b8…`） | 值 |
| --- | --- |
| TM600 段 `SW12_U1REF_BST_ACM` 引用 | **10**（我方现算；Captain 通报 11，差 1，见下） |
| 其中 `.Set(FV,…)` 调用 | **10**（即该段内**每一处引用**都是 `.Set` 调用：9 处 `ACM200_RELAY_ON` + 1 处 `ACM200_RELAY_OFF`） |
| TM600 段 `.Set` 的 FV 序列 | `0,5,10,15,20,15,10,5,0`（`ACM200_RELAY_ON`）→ 末次 `0`（`ACM200_RELAY_OFF`） |
| TM601 段 `SW12_U1REF_BST_ACM` 引用 | 3（**全部**为 `.Set` 调用） |
| TM600 段 `K48` / `K76` / `K109` / `K110` 命中 | **0 / 0 / 0 / 0** |

⇒ **这不是"少一个闭合"，而是部署态**活危害**（Captain 实测、我复核确认）**：TM600 段**正在驱动 ch5 源**（`.Set(FV,…)` 且 `ACM200_RELAY_ON`）**而 `K48` 未闭**；
按 `t44`/`t45` 的改道机制，源被送往 `SW1_F/SW2_F`（**既非 BST，也非 PB0**）。
**计数差异说明（我方实测 vs Captain 通报）**：Captain 通报"引用 11 / `.Set` 10"，我方现算为"引用 **10** / `.Set` **10**" ——
第 11 处引用我在 `TM600_HS_RDSON` 块内**未找到**（块内每一处 `SW12_U1REF_BST_ACM` 都是 `.Set(...)` 形式；
全文另有 37 处属其它函数）。**计数差 1 不改变实质结论**：该段**正在驱动 ch5 源而 `K48` 未闭** ⇒ 活危害。

⇒ **本行归属仍为 `compiledRevision = 15c7d2b8…`**（既非构建过程、也非未部署的 payload）；
**批处理落盘后该危害应随之消除**（payload 的 TM600 将闭 `K48`+`K76`）。
（复核脚本+日志：`gate-logs-t33/t45_verify_captain_deployed.py` / `t45-captain-deployed-verify.log`）

---

## 3. 待落盘后一次性加入 `build-report.json` 的字段（清单）

- `compiledRevision` / `compiledRevisionLabel` / `attributionRule` / `postReplaceExpectation`
- `expectedAfterReplace`（落盘时现算 payload sha256）
- `payloadDelivered`：`{path, size, sha256, mtime, note:"DELIVERED ≠ DEPLOYED"}`
- `verdict`：`blocked` → **`pass`**（仅当 ① 落盘完成且 bst-sw 转 GREEN，② 由可写会话提供 Release 0 error/0 warning 的 `build.log` + `F12011.dll` 哈希）
- 附 delta 归因：`bst-sw: NEW-RED → GREEN`（引用落盘后同一次 `run_gates.ps1` 输出）

## 4. 与其余纪律的一致性

- **不复用 t29 落盘前的日志当最终证据**（t33 non-goal）——本文件即为"落盘前证据只作状态记录、不作最终结论"的留痕。
- **不得把 payload 尺寸当作"已落盘"**（setup-architect 明确要求）：本文件三处均标注 DELIVERED/DEPLOYED 区分。
- 边界：本文件无电性结论；**编译成功 ≠ 电性/硬件正确**；未做任何机台验证。

### 1.1 payload 版本前进（2026-09-16 晚）

| 角色 | 对象 | 现刻现算 | 状态 |
| --- | --- | --- | --- |
| DEPLOYED | `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` | 469,714 B / `15c7d2b8…` | **未落盘**（TM600 = `{13,57,60,61,83,85,126}` ⇒ 缺 `[48,76]`） |
| DELIVERED（**现盘**） | `implementation-payload-TM600-TM601.cpp` | **43,806 B / `66abc088…`** | **已合规**（TM600 SetOn `L264` = `{13,48,57,60,61,76,83,85,126}` ⊇ 期望） |
| ~~旧交付件~~ | 同文件的历史版本 | ~~39,457 B / `2d0984d9…`~~、~~38,147 B / `272667f3…`~~ | **已被取代**，仅供溯源 |

⚠️ 本文 §1 与 §2 里以 **`39,457 / 2d0984d9…` 为"现盘/DELIVERED"** 的表述，一律改读为"**旧版、已被取代**"；
**现盘交付件是 `43,806 B / `66abc088…``**（引用前请现算）。

### 1.2 `postReplaceExpectation` 更正为**单口径 GREEN**（rule-reviewer 指出，我现算确认）

**原因**：我原先写的两口径表是拿**旧 payload（39,457）**算的 —— 那版**只闭 `[110,61]`、不含 `[48,76]`**，
故在 ch5 口径下必然仍红。**现盘 payload 已闭 `[48,60,61,76]`** ⇒ 两口径下都不缺：

| 契约口径 | 部署态（缺） | 旧 payload 39,457 | **现盘 payload 43,806** |
| --- | --- | --- | --- |
| rev 24（`[110,61]`） | 缺 `110` | 不缺 → 换版 GREEN | 不缺 → **GREEN** |
| rev 25/30+（`[48,76]`+`[60,61]`） | 缺 `48/76` | **缺 `48/76` → 仍红** | 不缺 → **GREEN** |

⇒ **`postReplaceExpectation` = "换版到现盘 payload ⇒ `bst-sw` 转 GREEN（单口径，其余 11 门不变）"**。

### 1.3 三口径归因（保留"真缺陷"但不合并）

| 对象 | 判定 | 性质 |
| --- | --- | --- |
| **部署态（现役 t23）** | `[13,57,60,61,83,85,126]` ⇒ **缺 `48/76`** | **真缺陷 + 活危害**：TM600 在驱动 ch5 仪器而 `K48` 未闭 ⇒ 源被改道至 `SW1_F`/`SW2_F` |
| ~~旧 payload 39,457~~ | 闭 `109/110`、缺 `48/76` | **闭错 + 缺闭**（历史） |
| **现盘 payload 43,806** | `{13,48,57,60,61,76,83,85,126}` ⊇ 期望 | **已合规**（落盘后预期 GREEN） |

⇒ **三口径不得合并记账**；"第二处真缺陷"只存在于**部署态**，**不属现盘 payload**。
