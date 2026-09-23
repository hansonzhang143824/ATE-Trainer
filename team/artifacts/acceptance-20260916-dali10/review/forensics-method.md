# t6 审查取证方法（rule-reviewer 自验版 · 已按 Captain 终裁更正）

日期：2026-09-16 · run: acceptance-20260916-dali10
状态：**我此前对“test.cpp 未加密”的更正已被我自己的实测否证，予以撤回。** Captain 终裁成立。
t6 尚未开始（依赖 t5）。

---

## 0. 我的撤回声明（诚实记录，避免后续误引用）

我上一轮曾向全组发出“test.cpp 不是 TSZ 容器 / 文件未加密”的“实证更正”。**该更正不成立，现撤回。**

两处错误：

1. **论据不成立（Captain 已指出，我接受）**：我用“python 读到明文”去证明“未加密”。透明加密的设计就是让**授权进程总是看到明文**，故该观测**恒为真**，不能作为“未加密”的证据。我的“全树 0 个 TSZ 容器”同理，是按构造必然成立，不构成反证。
2. **我的替代解释被实测否证**：我原先把 pwsh 的异常解释为“pwsh 读 UTF-8 BOM 的编码/行分割问题（机制 UNKNOWN）”。我用 `[System.IO.File]::ReadAllBytes()` 直接读**原始字节**后，该解释被推翻（见 §2）。

---

## 1. pwsh 读取异常的基础实测（grep/python 互证）

对象：`D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp`，字符串 `TM607_BUCK_LS_ZCD`

| 取证工具 | 命令 | 结果 |
|---|---|---|
| grep tool | `grep TM607_BUCK_LS_ZCD …/source/test.cpp` | **1 命中 @ 6985** |
| python | `open(p,'rb')` + utf-8 decode + `splitlines()` | **8877 行**；命中 1 处 @ **6985** |
| pwsh | `(Get-Content $p).Count` | **3316 行** |
| pwsh | `(Select-String -Path $p -Pattern 'TM607_BUCK_LS_ZCD').Count` | **0** |

grep 工具与 python 明文互证一致；pwsh 两条命令均给出错误结果。

---

## 2. 决定性实测：同一进程、同一路径、两条读取路径（我独立复现）

PowerShell 7.6.5 / PSEdition=Core / ConsoleHost。路径 `D:\PROJECT6-DALI\ForCodexDebug\source\`

| 文件 | python 读（**授权**视图） | pwsh `[System.IO.File]::ReadAllBytes`（**未授权**视图） |
|---|---|---|
| `test.cpp` | size 434629，**NULs=0**，first16=`ef bb bf 2f 2a 2a …`（UTF-8 BOM + `/**`），utf-8 解码 OK，**8877 行**，sha256(plaintext)=`5c9cb3f9…ac3317` | size **434629（同一字节数）**，**NULs=2055**，first16=`54 53 5a 23 05 90 07 0e 7a 01 00 00 d1 a3 de 89`（`TSZ#`），sha256(密文视图)=`6efc38e6…2156bfa` |
| `sub.cpp` | size 121909，**NULs=0**，first16=`ef bb bf 23 69 6e 63 …`（BOM + `#include "std`），utf-8 解码 OK，**3335 行**，sha256(plaintext)=`e86d49be…c391470` | size **121909**，**NULs=731**，first16=`54 53 5a 23 05 54 07 0e 29 01 00 00 4b 7e de e8`（`TSZ#`） |
| `source/StdAfx.h` | sha256(plaintext)=`ba8ab3de…aab6aee6`（与 Captain 一致） | （未单测，同族文件按同机制处理） |

**关键点**：同一进程内，`python open()` 得明文，`[System.IO.File]::ReadAllBytes()` 得 `TSZ#` 密文 —— 两者**字节数完全相同**（434629 / 121909）。这不是编码问题：若为转码/解码差异，可用字节与行结构会改变；且我已排除“pwsh 用 UTF-16 解码该文件”的可能（python `decode('utf-16-le')` 直接抛异常；GBK 解码得 8877/3335 行，与 pwsh 的 3316 行不符）。**两视图的差异只可能来自“谁在请求文件内容”。**

### 机制：已定位，不是 UNKNOWN

原先的“编码/行分割异常，机制 UNKNOWN”**更正为**：
**DLP 透明加密。** 受保护源对**授权读取路径**（python / grep 工具）透明解密为明文；对**未授权读取路径**（.NET `System.IO.File` / `Get-Content` / `Select-String`）返回原始 `TSZ#` 密文，字节数不变。这解释了全部观测：
- pwsh `Get-Content` 3316 行、`Select-String` 0 命中 —— 它读的是密文；
- **0 命中 ≠ 不存在**（这是纪律的根因，不是巧合）。

### 对照组

Captain 的对照 `scripts/run_gates.ps1`：两侧一致（NULs=0、字节一致）→ 证明差异**不由 pwsh 本身**引起，而由**文件是否受保护**引起。该对照的关键在于“非保护文件两侧一致”这一事实本身。**标注**：我复现时该路径不存在（`D:\PROJECT6-DALI\ForCodexDebug\scripts\run_gates.ps1` 缺失），故此项为**引用 Captain 实测、未由我复现**。

---

## 3. 对全组的操作性推论（重要）

1. **受保护源只经 python / grep 工具取证**。凡断言“某 API/继电器/常量不存在”，必须写明工具与限定范围；**pwsh 的 0 命中一律无效**（它读密文，必然 0）。
2. **哈希只用 python 明文 sha256**；`Get-FileHash` / .NET 哈希得到的是**密文哈希**（如 test.cpp `6efc38e6…`），若与 python 明文哈希比较，会产生**假“文件被改动”结论** —— 这正是必须禁止 pwsh 哈希的原因。
3. 实测锚点（python 明文 sha256，2026-09-16，t5 前）：
   - `source/test.cpp` = `5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317`（434629 B, 8877 行）
   - `source/sub.cpp` = `e86d49bef7ae725106311d8205df6dbc11184c7a0920eeaed416a515ac391470`（121909 B, 3335 行）
   - `source/StdAfx.h` = `ba8ab3de1b0c35cb7e9a477bd0b385f80671dc51011a08c9a5220518aab6aee6`（56968 B）
4. **改动前隔离基线（我实测，可直接用于 t9）**：python 逐文件哈希比对 `ForCodexDebug/source` 与 `devel/source`（各 111 文件），**全部源码与头文件逐字节相同**；唯一差异是 `source/Release/` 下的编译产物与 tlog/pdb/obj/lib/exp。
   → t9 隔离审计判据：实现后源码哈希 = devel 基线 **且** debug 副本新增/修改项为预期 → 证明“只改 debug 副本”。（Release 产物本就会因编译而不同，不应作为“源码被污染”的证据。）

---

## 4. 层次区分（沿用）

`FOVIe_*` / `VBAT_ACM` 等可能位于**方法库层**（`sub.cpp` / `Test_Method.*`），不在 TM 级 `test.cpp`。断言“不存在”必须写明**搜索范围（哪个文件、哪一层）**。

## 5. 我承诺执行的 t6 纪律

1. 存在性/内容断言只用 **grep 工具** 或 **python 明文**；禁用 pwsh 对源码做断言或哈希。
2. 每条 finding 的 evidence 必须含：**取证工具 + 文件 + 行号**。
3. “不存在”类 finding 必须附**工具 + 限定范围**，否则视为无效证据。
4. 评审方无改动权：全程只读；评审前后用 **python 明文 sha256** 自证被评产物未被改动。
5. **继续抽查实现者（t5）证据的取证工具**：凡用 pwsh `Select-String`/`Get-Content`/`Get-FileHash`/`.NET` 读源码得出的结论，一律**判为无效证据并要求用 grep/python 复取**。
