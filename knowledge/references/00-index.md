# references 知识库总索引（00-index）

> **L0-L5 唯一权威入口**。所有"芯片测试参考知识"按层归位，**每次变更须同步本索引，禁止留旧路径/断链**。
> 关联：`knowledge/standards/`（通用规则/门禁，非 references 层）+ `knowledge/sources|hardware|experience`（原始资料/硬件/经验，非 references 层）。

## L0-L5 分层

| 层 | 内容 | 目录/文件 |
|---|---|---|
| **L0** | ATE 通识必读（ATEST/DTEST 代称、本项目映射） | `L0-ate-primer.md` |
| **L1** | 芯片通用模块基础（参数类型族 + 电路功能模块） | `L1-chip/` |
| **L2** | 芯片测试项目（19 项清单 + 阈值/保护等测试项） | `L2-test-items/` |
| **L3** | ATE 测试方法（电压/电流阈值、差分对、继电器设计、找通路） | `L3-method/` |
| **L4** | 黄金案例（代码 .cpp + 要点总结 .md） | `L4-Golden-code/` |
| **L5** | 调试排查 | `L5-debug/` |

## 各层明细

### L0 — 通识（`L0-ate-primer.md`）
- ATEST0→VDM（模拟）/ DTEST0→nQON（数字）；两代称定义 + 纪律。

### L1 — 芯片通用模块（`L1-chip/`）
- 参数类型族：UVLO / CurrentSense / RDSON / Current-Threshold（是什么）
- 电路模块：01 自举-BST−SW / 02 BUCK-BOOST / 03 MOSFET 驱动 / 09 使能-软启动 / 10 VREF
（内容见各文件）

### L2 — 测试项目（`L2-test-items/`）
- `test-item-catalog.md`：19 项测试项目清单（骨架）
- 04 UVLO / 05 OCP / 06 OVP / 07 Current Sense / 08 nFAULT

### L3 — ATE 方法（`L3-method/`）
- `voltage-threshold-ate.md`（阈值电压：Pin+PRST/UVLO/OVP/LOW + VTRICKLE/RECHG）
- `current-threshold-ate.md`（电流阈值：内置/外置 4 方式 + 执行条件）
- `diff-pair-spec.md`（差分电压对）/ `relay-design-flow.md`（继电器设计）/ `path-principles.md`（找通路）

### L4 — 黄金案例（`L4-Golden-code/`）
- 12 个 .cpp（HS_ZCD/LS_ZCD/OVP/UVLO/toggle/RDSON/TM130/TM623/tm600/sub-measure...）+ 同名 .md 要点总结
- 用 `param_type_index.md` 索引定位（参数→案例）

### L5 — 调试排查（`L5-debug/`）
- RDSON.md（按需）

## 使用规则（重要）

1. **先读 L0**（通识），再按测试项查 L2 → 用 L1 理解结构 → L3 定方法 → L4 参照案例 → L5 排查
2. **同名联动**：`param_type_index.md` / `func_type_index.md` 是两层索引，按参数/功能类型定位四件套（L1/L3/L4/L5）
3. **变更纪律**：任何文件迁移/改名，须同步更新本索引 + param/func_type_index + 所有引用路径，**不得留旧路径断链**

## 索引文件

- `param_type_index.md`：参数类型 → L1/L3/L4/L5 四件套（参数名命名、同名联动）
- `func_type_index.md`：功能类型（7 类项目结构类型）→ 判据/框架/方法/示例
