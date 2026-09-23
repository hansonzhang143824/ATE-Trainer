#!/usr/bin/env node
/**
 * extract-claude-history-condense.mjs — 第 2 步：压缩提取（免费，零 LLM）
 *
 * 读取 knowledge/claude-history/00-inventory.json，
 * 对每个非空会话生成压缩页：knowledge/claude-history/sessions/<序号>-<短id>.md
 * 内容：元数据 + 会话摘要(summary) + 用户/助手文本（去工具输出、去 JSON 噪声）+ 工具调用一行标记
 *
 * 用法: node scripts/extract-claude-history-condense.mjs [输出目录]
 */
import { readFileSync, writeFileSync, mkdirSync, statSync } from "node:fs";
import { join, basename } from "node:path";
import { homedir } from "node:os";
import readline from "node:readline";
import { createReadStream } from "node:fs";

const PROJECTS_ROOT = join(homedir(), ".claude", "projects");
const OUT_DIR = process.argv[2] || "D:/Newtest/DSH/ATE-Coding-Platform/knowledge/claude-history";
const SESSIONS_DIR = join(OUT_DIR, "sessions");
const MAX_MSG_CHARS = 50000; // 单条消息截断，防病态输出
const MAX_TOOLS_PER_SESSION = 4000; // 工具行数上限

function esc(md) { return md.replace(/\\/g, "\\\\").replace(/\|/g, "\\|"); }
function clip(s, n) { return s.length > n ? s.slice(0, n) + `\n…[截断，原长 ${s.length} 字符]` : s; }
const isCommandy = (s) =>
  /<local-command|<command-|<tool-result|<system-reminder|<error>|<permission/i.test(s.slice(0, 200));

function textFromBlocks(content, acc) {
  // acc: { texts: [], tools: [], toolResults: 0 }
  if (typeof content === "string") { acc.texts.push(content); return; }
  if (!Array.isArray(content)) return;
  for (const b of content) {
    if (!b || typeof b !== "object") continue;
    if (b.type === "text" && typeof b.text === "string") acc.texts.push(b.text);
    else if (b.type === "tool_use" && b.name) acc.tools.push(b.name);
    else if (b.type === "tool_result") acc.toolResults++;
  }
}

async function condense(session) {
  const { index, file, title, firstTs, lastTs, sizeBytes, projectDir } = session;
  const abs = join(PROJECTS_ROOT, file);
  const lines = [];
  let userCount = 0, asstCount = 0, toolLines = 0, summaryText = null;

  const push = (label, text) => {
    const t = String(text).replace(/\s+$/u, "");
    if (!t.trim()) return;
    lines.push(`\n### ${label}\n\n${clip(t, MAX_MSG_CHARS)}\n`);
  };

  const rl = readline.createInterface({ input: createReadStream(abs), crlfDelay: Infinity });
  for await (const raw of rl) {
    if (!raw.trim()) continue;
    let j; try { j = JSON.parse(raw); } catch { continue; }
    if (!j || typeof j !== "object") continue;
    const ts = typeof j.timestamp === "string" ? j.timestamp.slice(0, 19).replace("T", " ") : "";
    const msg = j.message;
    switch (j.type) {
      case "summary": {
        // 会话滚动摘要：最有价值的浓缩
        const s = (msg && (typeof msg.content === "string" ? msg.content : msg.summary)) ||
                 (typeof j.summary === "string" ? j.summary : null);
        if (s && !summaryText) summaryText = String(s);
        break;
      }
      case "user": {
        const acc = { texts: [], tools: [], toolResults: 0 };
        textFromBlocks(msg && msg.content, acc);
        for (const t of acc.texts) { if (isCommandy(t)) continue; userCount++; push(`${ts} [user]`, t); }
        break;
      }
      case "assistant": {
        const acc = { texts: [], tools: [], toolResults: 0 };
        textFromBlocks(msg && msg.content, acc);
        for (const t of acc.texts) { if (isCommandy(t)) continue; asstCount++; push(`${ts} [assistant]`, t); }
        if (acc.tools.length && toolLines < MAX_TOOLS_PER_SESSION) {
          toolLines++;
          lines.push(`- [tool] ${acc.tools.join(", ")}\n`);
        }
        break;
      }
      default: break;
    }
  }

  let md = `# 会话 #${index} — ${esc(String(title).slice(0, 80))}\n\n`;
  md += `- 文件：\`${basename(file)}\`（项目 ${projectDir}）\n`;
  md += `- 时间：${firstTs || ""} → ${lastTs || ""}，大小 ${(sizeBytes / 1048576).toFixed(1)} MB\n`;
  md += `- 用户消息 ${userCount} 条 / 助手文本 ${asstCount} 段 / 工具调用标记 ${toolLines} 行\n`;
  if (summaryText) {
    md += `\n## 会话滚动摘要（Claude 自带）\n\n> ${clip(summaryText, 20000).replace(/\n/g, "\n> ")}\n`;
  }
  md += `\n---\n\n## 对话正文（工具输出已剥离）\n`;
  md += lines.join("") || "\n（无文本内容）\n";
  return md;
}

const inv = JSON.parse(readFileSync(join(OUT_DIR, "00-inventory.json"), "utf8"));
mkdirSync(SESSIONS_DIR, { recursive: true });
let done = 0, totalChars = 0;
for (const s of inv) {
  if (!s.sizeBytes || s.empty) continue;
  const md = await condense(s);
  const outFile = join(SESSIONS_DIR, `${String(s.index).padStart(2, "0")}-${basename(s.file).slice(0, 8)}.md`);
  writeFileSync(outFile, md);
  totalChars += md.length;
  done++;
  console.log(`  #${s.index} ${basename(s.file).slice(0, 8)} → ${(md.length / 1024).toFixed(0)} KB 压缩页`);
}
console.log(`\n完成：${done} 个会话压缩页 → ${SESSIONS_DIR}`);
console.log(`压缩页合计 ${(totalChars / 1048576).toFixed(2)} MB 文本（原始 ${(inv.reduce((n, s) => n + (s.sizeBytes || 0), 0) / 1048576).toFixed(1)} MB）`);
