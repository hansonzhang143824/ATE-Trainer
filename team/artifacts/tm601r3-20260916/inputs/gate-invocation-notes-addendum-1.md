# 门禁调用方式核实 · 补遗 1（更正 A1.1：撤回「meta 指纹」口径）

> 时间：2026-09-16 23:0x +0800。本文件**更正**同目录 `gate-invocation-notes.md`（3,111 B / `1ab24ec665388a8c6762abc6c6b428bf7fd3ebb401d53c4e0f9297d8a8094ec9`）中的 A1.1 与「指纹」表述；**原始文件不改写**（避免哈希漂移），以本补遗为准。

**被核实的源文件（现算 pin）**
- `scripts/verify_bst_sw_sequence.py` = 24,964 B / `17092feac034902e463fc5f14c79dc48cb1195436eda14f26d25691e11d54c78` @2026-09-16 19:39:53
- `scripts/run_gates.ps1` = 9,763 B / `dd2a4337f22d339a4a0f866c43d1843413db8f1d9e726c07bf8fbcaa5ab310b9` @2026-09-16 18:43:41

## 1. 撤回（RETRACTED）

| 我此前的说法 | 状态 | 更正为 |
| --- | --- | --- |
| 「`bst-sw` 门把 LS 项归类靠 **meta `capAuthority.powered_pins` 指纹**（`powered_pins 含 IPMID2SW/PMID-SW`）」 | **撤回** | 那是**已被作者废弃的旧实现**，只存在于脚本 **docstring L5-L7/L81-L85** 的历史说明里。**实际代码**见 `derive_targets()`（L78-L114） |
| 「meta 指纹未命中 ⇒ TM601 的 BST 约束落进空 PASS 而不报警」 | **撤回（原因不同）** | 真实机制见 §2：**目标集合根本不包含 TM600/TM601**，与 meta 指纹无关；空 PASS 另有其触发条件 |

## 2. 实际代码事实（FACT，逐行引用）

`derive_targets(functions)`（L96-L114）的选靶判据是**行为自证、不依赖 meta 字段名**（docstring L87）：

| 步 | 代码 | 含义 |
| --- | --- | --- |
| ① 入口 | `if not name or not re.search(r'\brampi_capv\s*\(', block): continue`（L100-L101） | **只有函数体内含 `rampi_capv(` 的电流斜坡项才入选**（docstring L88：含 `rampi_capv(` → 电流斜坡 → 本家族；L89-L90 实测 TM607/608/609/640 rampi=1，TM641/643/1205 rampi=0/rampv≥2 被排除） |
| ② 量程 | `re.search(r'\brampi_capv\s*\([^;]*?FPVIe_(2A\|10A)', block)`（L102-L103） | 取 `FPVIe_2A`/`FPVIe_10A` |
| ③ 拓扑 | `SetOn` 内含 `K_FPVIH_TO_PGND` → `'LS'`；含 `K_FPVIH_TO_PMID` → `'HS'`；**都判不出则跳过并 WARN**（L106-L112） | 「不猜」 |
| ④ HS 协议 | `check_hs` 要求 `PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V` 各恰 1 次（L201/L208），下电 `Set(FV, 0, FXVIe_PLUS_10V`（L223/L230） | HS 类目标必须用 **FXVIe + PMID=5 V** 的既定序列 |
| ⑤ 空 PASS 条件 | `if not targets: print('…非 ZCD/OCP 家族, 空 PASS'); return 0`（L497-L499） | **targets 为空即空 PASS**（此时 L502 之后的契约闭合断言尚未执行） |
| ⑥ 契约闭集断言 | L503-L523：`resolve_contract_path` → 读不到契约则**追加 error（红）**；`--skip-contract-closures` 可跳过（仅调试） | 契约闭集断言**只在 targets 非空时参与** |

## 3. 对 TM600/TM601 的可执行后果（INFERENCE，已标注不确定性）

- TM600/TM601 是 **RDSON（iset 直流强制）**，其 DFT 计划中并无 `rampi_capv(` 电流斜坡 ⇒ **按现行代码，它们不会被 `derive_targets` 选为 targets**；⇒ `bst-sw` 门**不会**对这两项执行 HS/LS 序列检查，**也不会**对其执行契约闭集断言（闭集断言与 targets 同域）。
- ⇒ 推论：**现行 `bst-sw` 门对 TM600/TM601 既不报红也不构成通过证据**；它真正覆盖的是 rampv/rampi 家族（TM607-609/640 等）。这解释了 t54 所报「部署态 TM600 缺 `[48,76]` ⇒ bst-sw NEW-RED」为何在**改契约期望集**后仍报红、以及为何该门的历史红/绿都不能直接当 TM600/TM601 的签署证据。
- **UNKNOWN（不得当作已验证）**：`check_contract_closures` 的 `resolve_scope()` 是否会在 targets 之外额外纳入 TM600/TM601 行（我只按 L497-L523 的主流程阅读，**未逐行读完 L248-L470 的 scope 解析与 `check_extra` 语义**）。⇒ **归口 `t11`**：在跑门禁时必须打印/核对 `[t30]` 行给出的**生效作用范围**（`--list-scope`）与 `[scan] targets=N`，确认 TM600/TM601 是否在域内；**不得以 targets=0 的空 PASS 记为绿**。

## 4. 边界

未修改任何脚本；**本轮未运行门禁**（避免产出与最终树不对应的证据）；`devel` 零写入；目标树未落盘（469,714 B / `15c7d2b8…`）；无机台/电性验证。
