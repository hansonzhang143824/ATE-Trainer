#!/usr/bin/env node
/**
 * extract-claude-history.mjs — 第 1 步：免费盘点 Claude Code 会话（不调用任何 LLM）
 *
 * 扫描 ~/.claude/projects 下所有 jsonl 会话文件，逐会话提取：
 *   标题（首个用户文本）、日期区间、消息/工具统计、涉及文件、用到的工具、本地命令
 * 输出：
 *   knowledge/claude-history/00-inventory.md   （人类可读目录）
 *   knowledge/claude-history/00-inventory.json （机器可读）
 * 控制台只打印紧凑汇总。
 */
import { readFileSync, writeFileSync, mkdirSync, readdirSync, statSync } from "node:fs";
import { join, basename, dirname, extname, relative } from "node:path";
import { homedir } from "node:os";
import readline from "node:readline";
import { createReadStream } from "node:fs";

const PROJECTS_ROOT = join(homedir(), ".claude", "projects");
const OUT_DIR = process.argv[2] || "D:/Newtest/DSH/ATE-Coding-Platform/knowledge/claude-history";

// ---------- 小工具 ----------
function walk(dir, out = []) {
  let entries;
  try { entries = readdirSync(dir, { withFileTypes: true }); } catch { return out; }
  for (const e of entries) {
    const p = join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.isFile() && extname(e.name).toLowerCase() === ".jsonl") out.push(p);
  }
  return out;
}
const isCommandy = (s) =>
  /<local-command|<command-|<tool-result|<system-reminder|<error>|<permission/i.test(s.slice(0, 200));

function extractTextFromContent(content, out) {
  // content: string | array of blocks
  if (typeof content === "string") { out.text.push(content); return; }
  if (!Array.isArray(content)) return;
  for (const b of content) {
    if (!b || typeof b !== "object") continue;
    if (b.type === "text" && typeof b.text === "string") out.text.push(b.text);
    else if (b.type === "tool_use") {
      out.toolUses++;
      if (b.name) out.tools.add(b.name);
      collectPaths(b.input, out.paths);
    } else if (b.type === "tool_result") out.toolResults++;
    else if (b.type === "local-command-caveat" || b.type === "local-command-stdout" ||
             b.type === "local-command-error" || b.type === "local-command-execution-error") out.commands++;
    else if (typeof b.type === "string" && b.type.startsWith("local-command")) out.commands++;
  }
}
function collectPaths(input, set) {
  if (!input || typeof input !== "object") return;
  for (const key of ["file_path", "path", "directory", "root", "cwd", "glob", "pattern"]) {
    const v = input[key];
    if (typeof v === "string" && v.length > 0 && v.length < 500 && !/^[A-Za-z0-9_\-.:/\\]+$/.test(v) === false ? true : false) {
      // 只收看起来像路径的（含分隔符或扩展名）
      if (/[\\/]/.test(v) || /\.[a-zA-Z0-9]{1,5}$/.test(v)) set.add(v.replace(/\\/g, "/"));
    }
  }
}
function normPath(p) { return p.replace(/\\/g, "/").replace(/^\/+/, ""); }

// ---------- 逐会话解析 ----------
async function parseSession(file) {
  const s = {
    file: relative(PROJECTS_ROOT, file), projectDir: basename(dirname(file)),
    title: "", firstTs: null, lastTs: null,
    userLines: 0, assistantLines: 0, summaryLines: 0,
    userTextChars: 0, assistantTextChars: 0,
    toolUseCount: 0, toolResultCount: 0, commandCount: 0,
    tools: new Set(), paths: new Set(), commands: [],
  };
  const rl = readline.createInterface({ input: createReadStream(file), crlfDelay: Infinity });
  let firstUserText = null;
  for await (const line of rl) {
    if (!line.trim()) continue;
    let j; try { j = JSON.parse(line); } catch { continue; }
    if (!j || typeof j !== "object") continue;
    const ts = typeof j.timestamp === "string" ? j.timestamp : null;
    if (ts) {
      if (!s.firstTs || ts < s.firstTs) s.firstTs = ts;
      if (!s.lastTs || ts > s.lastTs) s.lastTs = ts;
    }
    switch (j.type) {
      case "user": {
        s.userLines++;
        const msg = j.message;
        const content = msg && msg.content;
        const acc = { text: [], toolUses: 0, toolResults: 0, commands: 0, tools: s.tools, paths: s.paths };
        extractTextFromContent(content, acc);
        s.toolUseCount += acc.toolUses; s.toolResultCount += acc.toolResults; s.commandCount += acc.commands;
        for (const t of acc.text) {
          s.userTextChars += t.length;
          if (firstUserText === null && !isCommandy(t)) firstUserText = t.replace(/\s+/g, " ").trim().slice(0, 120);
        }
        break;
      }
      case "assistant": {
        s.assistantLines++;
        const msg = j.message;
        const content = msg && msg.content;
        const acc = { text: [], toolUses: 0, toolResults: 0, commands: 0, tools: s.tools, paths: s.paths };
        extractTextFromContent(content, acc);
        s.toolUseCount += acc.toolUses; s.toolResultCount += acc.toolResults; s.commandCount += acc.commands;
        for (const t of acc.text) s.assistantTextChars += t.length;
        break;
      }
      case "summary": s.summaryLines++; break;
      case "file-history-snapshot": {
        const fh = j.fileHistory;
        if (Array.isArray(fh)) for (const f of fh) if (f && typeof f.path === "string") s.paths.add(normPath(f.path));
        break;
      }
      default: break;
    }
  }
  s.title = firstUserText || "(无用户文本)";
  if (!s.firstTs) { const st = statSync(file); s.firstTs = st.mtime.toISOString(); s.lastTs = st.mtime.toISOString(); }
  s.toolUseCount = s.toolUseCount; // already accumulated
  return s;
}

// ---------- 主流程 ----------
const files = walk(PROJECTS_ROOT).sort();
console.log(`扫描 ${PROJECTS_ROOT} → ${files.length} 个 jsonl 会话文件`);
const sessions = [];
for (const f of files) {
  const st = statSync(f);
  if (st.size === 0) { sessions.push({ file: relative(PROJECTS_ROOT, f), projectDir: basename(dirname(f)), sizeBytes: 0, empty: true }); continue; }
  try { sessions.push(await parseSession(f)); } catch (e) { console.error("解析失败:", f, e.message); }
}
for (const s of sessions) if (s.sizeBytes === undefined) s.sizeBytes = statSync(join(PROJECTS_ROOT, s.file)).size;

sessions.sort((a, b) => String(a.lastTs || "").localeCompare(String(b.lastTs || "")));

mkdirSync(OUT_DIR, { recursive: true });

// ---------- Markdown 目录 ----------
const totalMB = (sessions.reduce((n, s) => n + (s.sizeBytes || 0), 0) / 1048576).toFixed(1);
let md = `# Claude Code 会话目录（盘点，非语义摘要）\n\n`;
md += `- 数据源：\`${PROJECTS_ROOT}\`\n`;
md += `- 会话数：${sessions.length}（其中空文件 ${sessions.filter(s => s.empty).length}）\n`;
md += `- 总大小：${totalMB} MB\n`;
md += `- 生成时间：${new Date().toISOString()}\n`;
md += `- 说明：本目录由脚本机械提取（零 LLM），用于挑选精读对象；语义摘要见各会话页。\n\n`;
md += `| # | 会话(文件) | 项目 | 标题（首个用户消息） | 起止时间 | 大小 | 用户/助手文本字符 | 工具调用 | 涉及文件数 | 用到的工具 |\n`;
md += `|---|-----------|------|---------------------|---------|------|-----------------|---------|-----------|-----------|\n`;
sessions.forEach((s, i) => {
  if (s.empty) { md += `| ${i + 1} | \`${basename(s.file)}\` | ${s.projectDir} | (空文件) | - | 0 | - | - | - | - |\n`; return; }
  const tools = [...s.tools].slice(0, 6).join(", ") || "-";
  md += `| ${i + 1} | \`${basename(s.file)}\` | ${s.projectDir} | ${String(s.title).slice(0, 40).replace(/\|/g, "\\|")} | ${(s.firstTs || "").slice(0, 16)} → ${(s.lastTs || "").slice(0, 16)} | ${(s.sizeBytes / 1048576).toFixed(1)}M | ${s.userTextChars}/${s.assistantTextChars} | ${s.toolUseCount} | ${s.paths.size} | ${tools} |\n`;
});
writeFileSync(join(OUT_DIR, "00-inventory.md"), md);

// ---------- JSON ----------
const json = sessions.map((s, i) => ({ index: i + 1, ...s, tools: [...s.tools].sort(), paths: [...s.paths].sort() }));
writeFileSync(join(OUT_DIR, "00-inventory.json"), JSON.stringify(json, null, 2));

// ---------- 控制台汇总 ----------
console.log(`已写入 ${OUT_DIR}\\00-inventory.md 和 00-inventory.json`);
console.log("非空会话:", sessions.filter(s => !s.empty).length, "| 空文件:", sessions.filter(s => s.empty).length, "| 合计:", totalMB, "MB");
const nonEmpty = sessions.filter(s => !s.empty);
if (nonEmpty.length) {
  console.log("\n最近 8 个会话:");
  [...nonEmpty].sort((a, b) => String(b.lastTs || "").localeCompare(String(a.lastTs || ""))).slice(0, 8).forEach((s, i) => {
    console.log(`  ${i + 1}. [${(s.lastTs || "").slice(0, 16)}] ${String(s.title).slice(0, 60)} (${(s.sizeBytes / 1048576).toFixed(1)}M, 工具${s.toolUseCount}次, ${s.paths.size}文件)`);
  });
}
