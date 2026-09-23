# t41 复核回填收口：`t28` 与 `t30` 的 ACCEPT 以正式产物固化

- 出具人：rule-reviewer（独立复核方）· 日期：2026-09-16 · 任务：`t41`
- 目的：把 `t28`/`t30` 的独立复核结论**以正式产物固化**（任务 `t25`/`t28`/`t30` 均因"复核未回收"标记 `failed`，本文件为其收口依据）。
- **只读**：未重跑门禁、未改任何被审文件。已复算 payload / 契约 / 计划 / 目标树 / `devel` 五者**均未变**。

## 0. 收口结论
| 任务 | 被审对象 | **verdict** | 意见文件 |
|---|---|---|---|
| `t28` | `scripts/check_input_sync.py`（RS-1..RS-4 + 回退红证 + manifest 登记） | **ACCEPT (pass)** | `review/t28-independent-opinion.md` |
| `t30` | `scripts/verify_bst_sw_sequence.py`（SetOn vs 契约 needsClosed 断言 + 阳性对照） | **ACCEPT (pass)** | `review/t30-independent-opinion.md` |

## 1. 判据哈希（**全部由我现算**，非引用任何消息文本）

| 对象 | size | sha256 |
|---|---|---|
| `scripts/check_input_sync.py` | 17,455 B | `e804c459b2d3088e72d455eb9e1b7893119cea47ad0a640735b6f5db42d784d1` |
| `scripts/verify_bst_sw_sequence.py` | 24,964 B | `17092feac034902e463fc5f14c79dc48cb1195436eda14f26d25691e11d54c78` |
| `scripts/gate_baseline.json`（未改） | 28 B | `021015da84e6fd4c54a595796e1bad73e18c57db94f856871d5667044302cb1d` |
| `scripts/run_gates.ps1` | 9,763 B | `dd2a4337f22d339a4a0f866c43d1843413db8f1d9e726c07bf8fbcaa5ab310b9` |
| `gate-logs-t28/t28-red-proof.json` | 5,351 B | `b97441a457119ca0ca11dca2b55a69e302c06cc6cb0b378f663bc77d4d78c529` |
| `gate-logs-t28/redproof-before-fix.log` | 1,317 B | `c0bfc972d34b44915165f7d893f19d8a6f9fe9c8ce641d8c20ed168d17327786` |
| `gate-logs-t28/redproof-after-fix.log` | 6,377 B | `6a17726003afaa6e6470c20e7e94ea18477e96c6590d76ad906e1970c3aae7e2` |
| `gate-logs-t28/input-sync-green.log` | 1,933 B | `538a00a425faca00bed76b8f01150e2c9df8d2504a87f83939b3fad562ea692f` |
| `gate-logs-t30/bst-sw-positive-control.log` | 1,262 B | `6333fd67bae609d3e16f90ceb267b28f1d50eb6182bd89ca439f83031d890537` |
| `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp`（部署态） | 469,714 B | `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a` |

**一处须以哈希为准的观察**：`gate_baseline.json` 的 mtime 显示 **22:45:34**（晚于本会话其它产物时刻），但其 **字节与哈希仍为 28 B / `021015da…`** ⇒ **未改**；mtime 异常不影响判定，但**引用时以哈希为准**。

**本文件另附**（我的四份复核产物现行值，**均已因收录更正而变动，此前引用一律失效**）：
| 文件 | size | sha256 |
|---|---|---|
| `review/t28-independent-opinion.md` | 12,117 B | `ea6b2c9e75fac98c154bcdce961ceb475259a3a52a11d1789a6e5fb3e9d5f79a` |
| `review/t30-independent-opinion.md` | 11,154 B | `fc8e3131e84ef93eb63384678e35e3f0942e29c1b31a1cfd54e975f4107c57d7` |
| `review/gate-capability-boundaries.md`（含 B-6） | 12,922 B | `2337c9450d6b2587161f0c81e44371f3f3c8b42ad85dacca6b0818b70e01a251` |
| `review/t40-tm601-bst-determination.md` | 27,250 B | `67fb79e1acd9adb69368ab81c391318da61eee88040a5dfdb2a436e0db85aea1` |

## 2. `t28` ACCEPT 的判据（逐条）
1. **规格忠实**：RS-1..RS-4 与 `meta-excitation-override.json:recommendedGateAssertions` 逐条对应（`check_input_sync.py:265-328`）；**RS-3 的"轨道集合＋数值"属收紧、非越界**（规格要求 vset **等于**冻结 ATE 且不含 `vbus`，"相等"在集合语义下本就含"多一条即不符"）。
2. **RS-FAIL 必计入 NEW-RED**：判定仅 `L344 bad=[i for i in items if i['status']!='MATCH']`、`L349`/`L400` 双模式 `return 1`；**穷举无豁免**（`status'=='MATCH'`/`in ('DRIFT'`/`exempt`/`ignore` 命中均为 0）。
3. **回退红证**：我**独立重放** —— BEFORE `IN SYNC`/exit 0（检不出）→ AFTER `OUT OF SYNC`/exit 1（RS-1/2/3 红）；harness 只读性由 `project` meta / yaml / `project_config.json` / `gate_baseline.json` **四方前后哈希一致**证实。
4. **未改基线/未放宽既有判据**：`_cmp`/`_read_json`/`_read_yaml_sync`/`_sha`/`check_dft_group` 函数体 **identical**；`check_sch_group` 初测报 CHANGED，**逐 diff 后确认其函数体一字未改**（差异仅为紧随其后的新增注释块）；全文件 +172/−2 行，2 行删除均为必须的整合点。
5. **B-3 边界（已登记为门禁能力边界）**：`input-sync` 只比对戳，**重生成会逐字节抹除修正而戳同步刷新 ⇒ 仍报 IN SYNC**；RS-1..RS-4 即为该缺陷的检测器。

## 3. `t30` ACCEPT 的判据（逐条）
1. **阳性对照真实且走致命通道**：我亲自运行默认参数 ⇒ `TM600: 缺失=[110] / FAIL=1 / exit 1`、`TM601: 缺失=[]`；该断言**只追加 `errors`** ⇒ 既有 `if errors: sys.exit(1)`，而 `run_gates.ps1:121-123` **只看 exit code** ⇒ **不可能被 warn 吞掉**。
2. **只增不改**：`--skip-contract-closures` ⇒ `FAIL=0 / PASSED / exit 0`（回到修复前行为）；`--list` 仍为 `TM607/608/609/640`。
3. **无静默旁路**：`run_gates.ps1:82` 调用**未携带** `--skip-contract-closures`；`--check-extra` **默认关闭**；源码 `L514` 已打印本次作用范围。
4. **未误伤负列表**：两函数负列表命中均为 0。
5. **B-6 边界（新增，已并入 `gate-capability-boundaries.md`）**：**由契约派生的断言，其覆盖上限＝契约登记的完整性**；缺项→静默盲区（`TM600.aliasesUsed` 漏 `bst2sw`）、错项→误报（`bst2sw.usedByTm` 含 TM1205）、**K109 多闭无法由契约派生断言消除**（契约自身把 109 写进 `relaySet` 与 `CH0 Route` 需求）。

## 4. 哈希来源纪律（本回填附带固化；本 run 已多次因此出错）
1. **一律用 python `rb` 现算** —— 本工作区受 DLP 保护，pwsh 的 .NET/文本路径读到**密文**（`TSZ#` 头、NULs>0、同长度），会产生**假哈希/假 0 命中**；
2. **消息内不手抄长哈希**，只给**路径 + size + 现算命令**；
3. **核对他人哈希必须现算并逐字符 diff**；**不得因为自己的探针报 False 就改认他方值** —— 本 run 已有一次把正确的 `…cc0b…`（pos42='c'）误抄成 `…cb0b…`（pos42='b'）并由我照录；
4. **单一真源文件**（`gate-logs-t28/t28-anchors.json`，我复核 9/10 正确、且其自身也须现算）**也必须由工具生成，不得手写**。

## 5. 边界
- **无电性结论**；**未做机台/硬件验证**；**编译成功 ≠ 电性正确**；
- 三条非阻塞待办归属：R1（`run_gates.ps1:119` 正则放宽为 `^\s*[-*]{1,3}\s+\S`）须 Captain 另开任务（不在 t33 inScope）；R2（死导入 `import re`）与其它实质修订合并清理；R3（manifest 引用现算）已由冻结指纹方式缓解。
- **本产物为收口依据**；`t28`/`t30` 的实现侧无须再改任何被审文件。
