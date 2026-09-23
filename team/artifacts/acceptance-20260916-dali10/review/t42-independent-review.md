# t43 正面裁定：`SW12_U1REF_BST_ACM` 的 ACM200 引脚归属 = **ch5**（并据此更正 t40 v2）

- 出具人：rule-reviewer · 日期：2026-09-16 · 任务：`t43`
- 裁定对象（canonical 字节）：`implementation-payload-TM600-TM601.cpp` = **39,457 B / `2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9`**（Captain ⑤ 定性）
- **只读**：未改任何被审文件（payload/契约/计划/门禁/两棵树）；仅写 `review/`。
- **边界**：本文全为**文献/网表/在役代码**证据，**非电性结论**；**无机台实测**；**编译闭环 ≠ 电性签核**。

---

## 0. 第一问的裁定（正面回答，不回避）

> **`SW12_U1REF_BST_ACM` 这一台仪器实例，在站点 S5..S28 上驱动 ACM200 的 —— `ch5`。**

**⇒ `t42` 的 ch5 归属正确；我 `t40` v2 中"出发自 `S5_ACM200_FH18`(ch18)"的前提**错误**，其"不闭 `K110` ⇒ 源落 `PB0`"的推论**随之**失效（该落点是 **ch18 仪器** `PB0_BST_ACM` 的行为）。**

### 0.1 判据（按证据等级递进；已回避循环）
| # | 等级 | 证据（我独立实测） | 指向 |
|---|---|---|---|
| ① | **在役代码（最强）** | `test.cpp:7595` ``//   ACM200_FH8(VCP_SW_ACM) … K61 … SW``；**`:7598` / `:7621` ``// 用 K48/K76 把 ACM200_FH5(SW12_U1REF_BST_ACM) 接入 BST``** —— **注释把引脚名与被驱仪器名写在了一起** | **ch5** |
**`[更正·见 review/t56-owner-attribution-correction.md]` 本处把 `L7000/7087/7170/7513` 当作部署树 TM600 的行为——**归属错误**：该四处属 `TM607/608/609/640`；部署树 TM600 的唯一调用点是 `L9081`（未闭 `48/76`）。**
| ② | 在役行为 | `test.cpp:7000/7087/7170/7513` 4 处 `SetOn(… K48_ACM5_AMP_REF, K76_ACM_BST …)`；全文件 `K48_ACM5_AMP_REF`=8、`K76_ACM_BST`=8、**`K110_ACM18_BST`=0、`K109_BUSL1_PB0`=0** | **ch5** |
| ③ | 别名自带通道号 | `StdAfx.h:211 K48_ACM5_AMP_REF`、`:224 K61_ACM8_SW`、`:279 K110_ACM18_BST`（后缀＝通道号，且与 `Pin_Channel_define.h:19/23/33` 的分组对齐） | **ch5** |
| ④ | 权威网表 | `NetK46_BUS_FH_SW1_S1_2 ∋ {K46.2, K48.6, S5_ACM200_FH5}`；`NetK109_BUSL_PB0_S1_4 ∋ {K109.4, K110.6, S5_ACM200_FH18}` | 两条腿分属 ch5/ch18 |
| ⑤ | 宏语义实读 | `Pin_Channel_define.h:20` `_PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_ = "S5_5,…"`；`:62` 站点绑定恰 **24 token（`S5_0..S5_23`）**；`:57` 分组宏第二 token 集合 = `{0..23}`；`:15-:38` 24 宏严格通道序；配 `hardware-specs.md` ACM200=24 通道 | `_5` = **通道索引** |
| ⑥ | IR 记录级 | `S5_ACM200_FH5 -> BST_F_S1 required_on=[48,76]`（`K48(ON,6→5)→K76(ON,6→5)`）；`S5_ACM200_FH18 -> BST_F_S1 required_on=[110]` | 两族并存 |

**循环禁令已遵守**：本裁定**未**使用 `channelsInScope.BST = "S5_ACM200_FH18/SH18 (K110_BST)"` 或 `aliasResolution[3].relayChain` 作为"仪器在 ch18"的依据 —— 二者**正是 `t42` 指认的错项**，而 ①–⑤ 均为**独立于该结论**的证据。**Cap 的观察我确认**：同一 `channelsInScope` 对 SW=FH8/INT=FH15/VDM=FH7 **都符合"宏指定通道"规则，唯 BST 破例**（按字面串 `BST` 匹配到 `K110_ACM18_BST`）⇒ 该字段是**派生时的字符串误配**，不是权威。

## 1. 我 v2 的正确部分（保留）
IR 确实枚举 **两条** `ACM200 → BST` 家族：`FH18/SH18 → [110]`、`FH5/SH5 → [48,76]`；而契约 `pinRouteTable["BST"][".6: ACM200…"] needsClosed=[48,76]`（line 672）**只反映 ch5**、**未按引脚分列** ⇒ 与 `bst2sw.usedByTm`（TM1205 误纳）、`TM600.aliasesUsed`（漏 `bst2sw`）**同根因**（门禁边界 **B-6**）；修法＝**按引脚/路线分列**（`acm_5 → [48,76]`、`acm_18 → [110]`）或至少在 `detail` 写引脚。**该条已并入 rev 25 清单。**

## 2. 更正 `t40` v2（Q1 分级重写；**处置结论不变**）
| 分级 | v2（ch18 前提，**撤回**） | **修订后（ch5）** |
|---|---|---|
| FACT | 现盘 TM601 段不驱动 ACM 源、不闭 `K109/K110` ⇒ 本项不产生 PB0 误驱动 | **保留并加强**：TM601 段 ACM 驱动 = **0** ⇒ **不产生任何误驱动**（与落点归属无关） |
| INFERENCE | 若恢复驱动且不闭 `K110` ⇒ 5 V 落 `PB0_F_S1` | **改为**：若恢复驱动，未动作时经 `K48(NC,6→7) → K49(NC,6→7)` 落 **`SW1_F_S1`（`required_on=[]`，默认导通）**；`K49` 动作则落 **`SW2_F_S1`（`required_on=[49]`）**。**`PB0_F_S1`/`PWM1_F_S1` 属 ch18 仪器，与本项无关** |
| UNKNOWN | PB0 占用 / 仪器内部继电器 / K110 磁保持语义 | **保留**，并补 **`SW1_F/SW2_F` 在本工况的占用状态**（导出不可判定） |
locator（改道）：IR 记录级（上）+ `SCH-Connect-Map.txt:774-779`（`SW1 [Kelvin] 需闭合: 无(默认导通)`、`F: S5_ACM200_FH5 -> K48(Relay-NC) -> K49(Relay-NC) -> SW1_F`、`SW2 需闭合: K49`）—— 与 `ate-implementer` 实测一致，**我独立复现** ✅
**⇒ `t40` 的处置结论（TM601 无 BST 授权 ⇒ 移除正确）不依赖落点归属**，其**核心论据**为：① `TM601.ateStimulus` 无 `bst2sw`；② `relaySet`/`scopePins`/`pinRouteTable` 三处均无 BST；③ 本项测 `Rds,on=(SW−PGND)/IPMID2SW`；④ `SW12_U1REF_BST_ACM.Set` 计数 = 0。**⇒ `t40` 的 `verdict=pass` 维持**，仅 Q1 分级按本表重写。

## 3. 顺位其后的三问
### (a) TM600 是否**必须**由 ch5 驱动 BST？⇒ **是。**
四源同向：在役代码 4 处（含 `:7598/:7621` 注释）＋ IR `required_on=[48,76]` ＋ `SCH:672-674` ＋ 契约 `pinRouteTable…列6 = [48,76]`。⇒ **现盘"本项两腿皆未闭"构成真缺陷**（在役 `K48/K76` 的 8 次闭合都在**其它条目**里）。
### (b) t29 对 TM600 的 `K109/K110`：**移除**（不再标"依约保守"）。
① 在役代码 **0 次**使用它们；② `K109` pins 3/6 = `FPVIe1_FL_BUS_S1`/`FPVIe1_SL_BUS_S1`（我实测网表）⇒ 保留会把 **FPVIe 低域总线拉到 BST 节点**，引入非本仪器耦合；③ 保留与在役行为不一致，且需**永久禁用 `--check-extra`**。
**`[更正·见 review/t55-closure-set-correction.md]` 本处闭集写作漏 `K60`；权威值 = `[48,60,61,76]`（BST `[48,76]` + SW `[60,61]`）。**
⇒ **rev 25 落批口径**：**补 `K48_ACM5_AMP_REF` + `K76_ACM_BST`、移除 `K109/K110`** ⇒ BST–SW 闭集 = **`[48,61,76]`**。
### (c) 是否允许改用 ch18 + `[110]`？⇒ **物理可达，但不建议。**
IR 确有 `S5_ACM200_FH18 -> BST_F_S1 = [110]`；但改用 ch18 会**改变声明的驱动仪器**（`SW12_U1REF_BST_ACM` → `PB0_BST_ACM`），使**契约/计划/在役实现三者同时失一致**，且与 `Pin_Channel_define.h:20` 的宏绑定冲突。**判据＝可逆性与一致性**：ch5 是"跟随在役实现"，ch18 是"另立新路线（需改宏、契约、计划、payload 四处）"。

## 4. `t42` 三处错项指认：**成立**（契约仍 rev 24 / `fd00a508…`，我实测）
| 契约字段 | 我实测值 | 判定 |
|---|---|---|
| `$.resources[2].channelsInScope.BST` | `S5_ACM200_FH18/SH18 (K110_BST)` | **✘** 把 **ch18 引脚**挂到 **ch5 仪器名**下（同字段对 SW/INT/VDM 均合格，唯 BST 破例 ⇒ 字符串误配） |
| `$.aliasResolution[3].resolution.relayChain[0]` | `K110_ACM18_BST … (ACM200 S5_FH18 -> BST)` | **✘** 同上 |
| `$.aliasFlatTable[3].relayPath` | `K110_ACM18_BST -> K61_ACM8_SW` | **✘** 同上 |
| `$.tmDeltas.TM600.pinRouteTable.BST 列6` | `[48,76]` | **✔ 正确**（与 IR/在役一致） |
**⇒ `alternatives[0]` 是契约里唯一正确的 `[110,61]` 处**（它以 `PB0_BST_ACM`/ch18 为仪器）；**但须在 rev 25 明确标注其 ch18 归属**，与 ch5 的 `[48,61,76]` **并列**而非混用。

## 4bis. 追加加固证据（**不依赖 `S5_5 ↔ FH5` 编号读法**）—— 我独立复现，逐条成立
**(1) 复合宏层面：全文件没有任何 `ACM200 -> BST` 复合宏使用 `K110`**（我穷举 `#define K_*BST*`）：
```
L620  #define K_BST_ACM   48,76   // ACM200[] -> BST:    K48_ACM5_AMP_REF + K76_ACM_BST     ← 唯一一条 ACM200→BST
L619  #define K_BST2_ACM  43      // ACM200[] -> BST2:   K43_ACM4_BST2
L377  #define K_FPVIH_TO_BST_A  46,48,76  // FPVIe[H] -> BST
L451/452 #define K_FPVIL_TO_BST_A/B  109,110,138,139,145,146 / 109,110   // FPVIe[L] -> BST
L514/556 #define K_BST_QTMU / K_BST_QVMH  141,46,48,76 / 137,46,48,76   // QTMU/QVM -> BST
L557  #define K_BST_QVML  109,110,139  // QVM[L] -> BST
```
⇒ **`K110_ACM18_BST` 只出现在 `FPVIe[L]` 与 `QVM[L]` 的宏里，从不出现在任何 `ACM200 -> BST` 宏**。**唯一**那条 `ACM200[] -> BST` 是 `K_BST_ACM = 48,76`，且**点名 `K48_ACM5_AMP_REF`（通道 5）**。⇒ **链路"复合宏 → 别名 `ACM5` → 网表网 `∋ S5_ACM200_FH5`"在头文件与网表内部闭合**，**不依赖 `_5` 的编号解读**。
**(2) 控制组 5/5（我实测 `StdAfx.h` 的 `K<n>_ACM<c>_<fn>`）**：`ch4 K42_ACM4`↔`FH4`、**`ch5 K48_ACM5`↔`FH5`**、`ch7 K59_ACM7`↔`FH7`、`ch8 K61_ACM8`↔`FH8`、`ch18 K110_ACM18`↔`FH18`；**全表 `ACMn` 后缀＝1..23 与 `Pin_Channel_define.h:15-38` 的顺序一一对应**（我逐条核过）。
**(3) 决定性分离（网表）**：ch5 网 `{K46.2, K48.6, S5_ACM200_FH5}` **不含 K110**；ch18 网 `{K109.4, K110.6, S5_ACM200_FH18}` **不含 K48/K76**。

### 4bis.1 ⚠️ 关于"两条腿并存 ≠ 证据冲突"（Captain ② 的纠正，我确认并采纳）
**网表并不反证 ch5。** `S5_ACM200_FH18/SH18` 与 `K110` 的 COM 同网，是因为 **`K110` 本身就是 ch18 的继电器**（别名 `K110_ACM18_BST`）⇒ 它支持的是"**ch18 有一条经 K110 到 BST 的腿**"，**不是**"`SW12_U1REF_BST_ACM` 走 K110"。**两条腿都真实存在，但属不同源仪器**（`ACM200-ch5` vs `FPVIe[L]`/`ACM200-ch18`）。
⇒ **对 t30/t39 的对齐含义**：分叉**不是**"宏说 ch5 vs 网表说 FH18"，而是"**派生字段把 ch18 的引脚挂到了 ch5 的仪器名下**"（§4 三处错项）。**以此为准**，避免把并存误读为冲突。

## 4ter. `t29` 的 `K109/K110`：我独立复核 captain 的"实质耦合"论证 —— **成立**
- **FACT（网表）**：`K109` pins 3/6 = `FPVIe1_FL_BUS_S1` / `FPVIe1_SL_BUS_S1`（我实测 net 成员）。
- **INFERENCE（成立）**：`K109` 通电 ⇒ 其 COM 离开该低域总线、接到 NC 侧，而 **NC 侧与 `K110` 的 COM 同在 BST 源节点**（`NetK109_BUSL_PB0_S1_4/5 ∋ K110.6/.3`）⇒ **闭合 `K109` 即把 `FPVIe1` 低域总线接到 BST 节点**。
- **FACT**：`K110` 的 COM 即 `S5_ACM200_FH18/SH18`（ch18 仪器源脚）⇒ 闭合 `K110` 即把 **ch18 的源腿接到 BST**。
- **INFERENCE（成立，即 captain 所述"多出未声明/悬空源"）**：若 ch18 仪器（`PB0_BST_ACM`）**在本项未被驱动**，则该接点成为 BST 上的**未声明/悬空源**；且**未动作时它按 NC 路径通向 `PB0_F_S1`/`PWM1_F_S1`** ⇒ 使 BST 节点与 DUT 的 PB0/PWM1 引脚产生**未声明的耦合**。
- **⇒ 结论**：保留 `K109/K110` **不是无害冗余，而是实质耦合**（把另一台仪器的源腿 + FPVIe 低域总线都挂到 BST 节点）。**故我支持：t29 的 `K109/K110` 应移除（而非"依约保守保留"）。** 与 §3(b) 一致。
- **UNKNOWN（不声称）**：耦合在机台上的实际电气后果（是否产生可测偏置/冲突）——**无机台实测**。

## 5. 交付与遗留
- **本裁定即 `t43` 的第一问答复：ch5**；`t40` v2 的 ch5/ch18 前提已更正、其 Q1 分级已重写，**处置结论与 verdict 不变**。
- **rev 25 清单（我支持附录 L.3）**：`closedRelayNumbersByRoute`（`ch5:[48,76]` / `fpvieCh0Low:[109,110,138,139,145,146]` / `s10Ch0B:[109,110]`）+ 三处 ch18 错项改归属 + `pinRouteTable` ACM200 行**按引脚分列** + `acmDriveFraming` + `unrealisableRoutes` + F.8 的 TM1205 登记更正。
- **t30 期望集**须随 rev 25 更新为 `[48,76]` 口径（改脚本另派任务、**不得动 `gate_baseline.json`**）。
- **⚠️ 连带风险（转 t34 必录）**：`K48/K76` 在**其它条目**也被闭，而本 run `SetOn` 为**排他**语义（payload `L219-229` + `cbite-qtmue.md:80-81/:92-93`）⇒ **跨条目共享继电器可能互相释放**。
- **UNKNOWN（不声称）**：机台层电气行为、`SW1_F/SW2_F` 本工况占用状态、K110 机械保持语义（`IM06DJR` 手册未核）。
