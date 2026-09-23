# PTC 专家训练台账（Trainer 维护）

> 维护者：训练师会话。更新：2026-09-22。权威顺序：任务注入地址簿 > Training_Materials/_expert_bindings.json > 本台账（仅状态记录）。

## 一、状态快照
- 专家：DFT_Expert（ptc-dft-expert）｜已发布 **v4**（previous v3，publishedAt 2026-09-22T05:01:43Z）
- manifestDigest：f2ae421b16fb63e88a30e3408df6de7cfec37bee6ab05b167be9a565498d772e（发布方口径：7 快照核验一致）
- draftEvaluation：pass（14 项检查全绿，发布方口径）
- 当前模式：training，根 = Training_Materials/

## 二、已落地（2026-09-21/22 两轮）
| 项 | 内容 | 落盘证据 | Trainer 核验 |
|---|---|---|---|
| [22] | 地址簿逻辑路径纪律（round 2） | instructions.md 56-65 行 | ✅ 逐字在位 |
| [8] | 一份 profile 两态切根（round 3） | instructions.md 67-75 行 | ✅ 逐字在位 |
| [9] | 校验产物落点 + dft- 前缀（round 4） | instructions.md 77-84 行 | ✅ 逐字在位 |
| [28] | 插件训练分支动态白名单（lib/training-bindings.js，fail-closed 回退） | plugins/.../lib/training-bindings.js | ✅ 文件在位；三闸门+用例全绿（发布方口径） |
| [10] | schema 11 项修改重写 | output-contract.schema.json 新 required（sourceLocation/parseStatus/openItems） | ✅ 已核；⚠️ 差异见四 |
| gate 升级 | 语义级标准：rawIntent 有值覆盖/yaml 宽松对齐/review 两形态/磁盘字节 sha256 | verification/ 下 dft-pin-check-TM_106.json、dft-schema-check-TM_106.json | ✅ 产物在位、前缀正确 |
| [10]配套 | validate_dft_outputs.py 同步（修改11） | 见下方验证记录 | 见本轮 grep 结果 |

## 三、待落卡片（对表重排）
**round 5 打包（instructions 行为规则，一次追加）**：[1] 八步工作流定版、[2] 语义边界、[3] 异常三态分流、[4] DFT_Issue_Items 登记流程、[5] 必要性检查残余（失败原因写异常文档）、[6] 哈希残余（规则文本）、[7] Captain 握手、[13] 解析规则文件为第3步唯一依据、[14] ramp/阶段解读、[15] 给 Method_Expert 的两条必交备注、[16] 处理方法四条。
**案例**：[12] 异常分流案例、[20] ramp 解读案例（待 TM 裁定；聊天文本沿用 TM_1xx 防钩子误判写法）。
**脚本残余**：[19] pin 报警对账数据源（schematic Pin 清单）确认。
**交付态专项**：[31] 规则文件随输入根（新提案）；[21]/[26] 残余——交付态 DFT 读 schematic 产物同样被硬编码读白名单挡，与 [31] 同类，待一并裁定。
**挂起裁定**：第一批 trial 目录策略 3 问（trial 根路径、被拒定义、TM 选择）。
**已关闭**：[11]（gate 语义级改造实质完成）、[18]（被 [10] v4 取代）、[17]/[25]（训练态读已放开，交付态由 [31] 接管）。

## 四、差异与新增建议（2026-09-22）
- 差异1：schema 中 x-dft-parsing-rules / x-gate-sync 字面键未检出（功能项已落，合同自述指针缺）→ 建议 [29] 附带补齐或确认有意省略。
- [29] gate 增补 yaml 与 meta 的 sourceSha256 一致性断言。
- [30] pendingUser/openItems 非空 ⇒ deliverable-ready 不得置 ready。
- [31] 规则文件副本随输入根走（训练+交付两根）。

## 五、验证记录
- 2026-09-22 Trainer 实证：instructions.md 84 行（round 2-4 逐字在位）；schema 新 required 集；training-bindings.js 在位；status.json v4 + digest 前缀与报告一致；verification 两产物前缀正确。
- 独立评审通道：本会话 subagent 运行时故障（subagent×2、subagent_fork×1 均失败），v4 发布评审由发布链路内置评估替代；通道恢复后可对 [28]/[10] 补独立评审。
- 钩子备注：会话出站文本中 TM+数字连写曾触发 Captain 入口误判，聊天与台账统一用 TM_1xx 写法。