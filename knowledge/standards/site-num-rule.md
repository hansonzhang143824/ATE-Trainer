# SITE_NUM 铁律（STS_SITE_NUM → SITE_NUM）

> 2026-08-29 用户拍板；08-30 权威迁移完成（fast_rebuild PASS）。
> 使用方：任何生成代码（写参数数组、Trim 等）。
> 关联：memory [[nuvolta-site-num-rule]]。

- **入口解析时**，材料/参考代码中一旦出现 `STS_SITE_NUM`，**全部改写成 `SITE_NUM`**（生成代码只用 `SITE_NUM`，如 `double param[SITE_NUM] = { 0 };`）。
- **`SITE_NUM` 唯一定义 = 工程 `StdAfx.h` L23**（`#define SITE_NUM 12`，位于 include spec.h/treg.h **之前**）。2026-08-30 从 treg.h:49 迁移：库头文件不硬编码项目配置，换项目只改 StdAfx.h 一处。
- **库头文件禁定义 SITE_NUM**：`treg.h:49` 与 `spec.h:62` 的 SITE_NUM 行均为注释态，**勿解注**（否则重定义）。生成代码/新头文件里也不要自定义 SITE_NUM。

> 教训：曾误记"权威=StdAfx.h"→注释 treg.h:49（会让 SITE_NUM 未定义、编译崩）→实测打脸回滚→真正评估（查清循环包含 treg.h:28→stdafx.h guard `__TREG` L24 / 消费链）后再迁移并编译验收。**任何权威源论断必须实测+编译，不能推断。**
