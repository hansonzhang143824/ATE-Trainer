# t33 转 pass 的**有序执行清单**（含 t42 三种结局分支）

- 目的：把"落盘 → 构建 → 报告"的每一步固定成可核对的顺序，避免各方再就"谁在等谁"往复。
- 现状（现刻实测，只读；**引用一律现算**）：

| 角色 | 对象 | 现刻值 |
| --- | --- | --- |
| DEPLOYED | `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` | 469,714 B / `15c7d2b8…236c01a`，mtime 18:53:33；`K109_BUSL1_PB0`=**0**、`K110_ACM18_BST`=**0** ⇒ **仍 t23 版，未落盘** |
| DELIVERED | `implementation-payload-TM600-TM601.cpp` | 39,457 B / `2d0984d9…48997f9`，mtime 19:55:59；TM600 SetOn 含 `K109_BUSL1_PB0, K110_ACM18_BST`；**TM601 SetOn 不含两者**（与"TM601 悬空 ACM 驱动已移除"一致） |
| 门禁基线 | `scripts/gate_baseline.json` | 28 B / `021015da…02cb1d`（未改） |
| 契约 | `setup-contract.json` | 328,805 B / `fd00a508…15a18`（rev 24，待 rev 25） |
| 本会话能力 | — | **对目标树只读** ⇒ MSBuild `error MSB3491`（写 `source\Release\F12011.tlog\F12011.lastbuildstate` 被拒）⇒ **Release 编译须由可写会话（Captain）执行** |

## 裁定：**单一合并批**（Captain 2026-09-16）（裁定 (i) 合并批）

Captain 裁定选 **(i) 合并为同一批落盘**：**`rev 25`（契约消歧 + 结构化别名归属）与 payload 改动同一批**，
**在 `t43`（`K109/K110` 去留裁定）之前不落盘**；批处理完成后**只重跑一次门禁**。

**闭集更正（Captain 2026-09-16）**：BST–SW 闭集 = **`[48,60,61,76]`**
（BST 侧 ∈ ACM200 族 `[48,76]`；SW 侧 ∈ FPVIe[L] 族 `[60,61]`）。
**三情形**：rev24+t29 ⇒ GREEN；rev25 未同批 ⇒ 仍 NEW-RED 且**红因是"缺 [48,76]"**；rev25+payload 同批 ⇒ 期望 GREEN（本分支）。

**据此更新的落盘后期望**：批处理完成后 **`bst-sw` 期望为 GREEN**
（修正后期望集 `[48,60,61,76]`；TM600 已闭 `{60,61}`，**批处理需补的是 `K48`+`K76`**）⇒
**不再存在"落盘后仍红"的例外路径**；其余 11 门不变；`cbit` 仍为基线豁免。
⇒ 本节下方的**分支 B/C 仅作为历史备选保留**，不再是预计路径。

---

## 分支 A：t42 判**pin 18**（`[110,61]` 成立，契约 rev 24 无需改）
1. Captain REPLACE：以 payload 现盘值落盘 `test.cpp`；**通报落盘后 `test.cpp` 的 size / sha256 / mtime + 两个 define 命中数**（setup-architect 承诺通报）。
2. 我（只读）复算落盘后哈希，作为 **`compiledRevision`**（**不再用 `15c7d2b8…`**），并核对 K109/K110 命中数 > 0。
3. 我重跑 `pwsh -NoProfile -File scripts/run_gates.ps1 -LogDir .../gate-logs-t33`（不带 `-Build`），期望：**12 门 = 11 GREEN + `cbit` KNOWN-RED，`bst-sw` 由 NEW-RED 转 GREEN**；记录 `FULL_EXIT` 与逐门 exit。
4. Captain 以可写会话执行 Release|Win32 构建，交回：`build.log` + **0 error / 0 warning 逐字输出** + `F12011.dll` 的 size/sha256/mtime。
5. 我只改 `build-report.json`（我的 inScope）：`verdict` → `pass`；写 `compiledRevision`（步骤 2 现算值）、`builds[]`（步骤 4 证据，**证据来源标注＝Captain 会话**）、`gateTable`/`gateSummary`（步骤 3）、`sourceAnchors`（落盘后 before/after）、delta 归因 `bst-sw: NEW-RED → GREEN`、其余 11 门不变。
6. 复跑 `python scripts/validate_team_artifact.py build-report ...` 至 exit 0；把报告现算哈希通报 Captain 与 setup-architect（t34 引用）。

## 分支 B：t42 判**pin 5**（`[48,76]` 生效）
1. 先由契约 owner 出 **rev 25**（并把"别名→TM 归属"结构化，见 `t30-summary.md` §9.1 附加风险）。
2. **契约变更后**，我的 t30 断言**期望集合随契约自动更新**（无需改脚本：`expected_for_tm()` 全读契约）；
   但**转绿条件随之改变**：TM600 需闭 `[48,76]`。⇒ 需 Captain 另派任务做(或不做)：
   - 期望集合改 `[48,76]`，或**按路线拆分**（ACM 侧 pin 5 口径 / FPVIe 侧保持）；
   - **重跑阳性/阴性对照 + 全树 A/B**（证明无新增误报）；
   - **不得改动 `gate_baseline.json`**。
3. `payload`（TM600 的 `K109/K110`）是否保留由 Captain 裁定；建议**保留并标注"依约保守"**（rev 24 字面仍要求），待 rev 25 生效后再评。
4. 之后回到**分支 A 的步骤 1–6**（落盘与构建顺序不变）。

## 分支 C：t42 判"两条路线并存"（各按其源生效）
按路线拆分期望集合：**ACM 侧**按该实例实际落脚的 pin 口径，**FPVIe 侧**维持 `[109,110]`；
其余同分支 B 的步骤 2–4 + 分支 A 的步骤 1–6。

## 不变量（三种分支共同）
- 我的所有改动**只在** `build-report.json` 与 `team/artifacts/<run>/gate-logs-t33/`（t33 inScope）；
- **不改** `gate_baseline.json`、`test.cpp`、payload、契约、`devel`；
- 报告内 `compiledRevision` **必须是落盘后现算值**；
- 一切引用**现算 + 标时刻**；**不手抄哈希**（写文档脚本须证幂等）。

## 边界
本清单是流程与证据约定；**不含任何电性结论**。**无机台/硬件实测**；**编译闭环 ≠ 电性签核**。

---

### 门禁期望集的**实际构成**（读源码取得，非推断）

`verify_bst_sw_sequence.py::expected_for_tm()` 的**实际代码路径**（直读源码，非推断）：
1. 遍历 `tmDeltas.<base>.aliasesUsed` 里每个别名的 `resolution.closedRelayNumbers`；
2. 遍历**所有**别名，凡 `usedByTm` 文案中经 `\b(TM\d+)\b` 命中 `<base>` 者，取其 `closedRelayNumbers`。
⇒ **期望集只由这两源构成**；`pinRouteTable` 仅供**定位说明**（locator），`relaySet` 仅供**预算池**（不作为要求）。

**现盘实测（契约 revision 28）**：TM600 期望集 = **`[60, 61, 83, 110]`**
（逐项来源：K60←aliasesUsed:pmid2sw; K61←aliasesUsed:pmid2sw; K83←aliasesUsed:pmid2sw; K110←usedByTm:bst2sw）

⇒ **落盘后必须现算且并列记录三项**，不得凭记忆解释红/绿：
1. `setup-contract.json` 的 **revision** 与 `aliasResolution[bst2sw].resolution.closedRelayNumbers`；
2. 上式**现算**出的 TM600 期望集（以及 TM601 的对应集合）；
3. 落盘后 `test.cpp` 的 `compiledRevision`（现算）与其 TM600/TM601 SetOn。
**判据**：期望集 ⊆ SetOn ⇒ `bst-sw` 应 GREEN；若期望集仍含 `110` 而 payload 不含 ⇒ 红因是"**契约权威值未消歧**"，
须按此归因（**不得**记为缺陷、**不得**为迎合门禁补 `110`）。**阳性对照重建后**应为"缺 `48/76` ⇒ 红"。
