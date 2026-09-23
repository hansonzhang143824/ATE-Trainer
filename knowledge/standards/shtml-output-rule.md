# 网页输出硬规则（R-SHTML）

> 适用：本项目**所有**网页交付文件（工作流视图文档、测试方案、进度视图、报告等）。
> 违反 = 输出不合格，交付前必须修复。
> 立项：2026-08-27 用户拍板，**替代原 R-HTML-1/2/3（已删除）**。背景 = 乱码事故（编辑引入 UTF-8 BOM + 缺 charset meta → 浏览器按 GBK 猜码全乱码）；agent_architecture 曾引 mermaid CDN、ATE/工作流全景曾引 Google Fonts。统一 `.shtml` 扩展名输出。

| ID | 规则 | 内容 | 强制 |
|----|------|------|:---:|
| **R-SHTML** | 统一 SHTML 格式输出 | 网页文件一律 `.shtml` 扩展名（**不再使用 `.html`**）；内容为标准 HTML5：首行 `<!doctype html>`；`<html lang="zh-CN">` → `<head>`（必含 `<meta charset="utf-8">` + viewport）→ `<body>`；标签闭合完整、结构合法；按需可含 SSI 指令（`<!--#include -->`），否则纯静态自包含 | ✅ |

**编码与自包含要求（继承原 R-HTML-2/3）**：
- UTF-8 编码、**无 BOM**（文件首 3 字节 ≠ `EF BB BF`）；纯文本，**禁加密 / 压缩 / 二进制封装 / 特殊文件格式**
- CSS 全部内联在文件内 `<style>`；**零外部资源**：禁 CDN `<script src>`、禁 Google Fonts / 外部字体、禁外部 stylesheet / 图片 / iframe；JS 如需同样内联

## 落地检查清单（每次输出/修改网页后自查）

- [ ] 文件名以 `.shtml` 结尾
- [ ] 第 1 行是 `<!doctype html>`
- [ ] `<head>` 内有 `<meta charset="utf-8">` 与 viewport
- [ ] 全文 grep `https?://` / `<link` / `<script src=` → **0 命中**（SVG 命名空间 `http://www.w3.org/2000/svg` 除外，非外部资源）
- [ ] 无 BOM（文件首 3 字节 ≠ `EF BB BF`）
- [ ] CSS/JS 全部内联在文件内

## 合规参考：无外部字体的系统字体回退栈

```css
--sans: system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;
--mono: ui-monospace,SFMono-Regular,Consolas,"Courier New",monospace;
```
