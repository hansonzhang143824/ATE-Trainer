// Minimal Chrome DevTools Protocol helper for the Agent Trainer host acceptance (Claude, 2026-10-02).
// Zero dependencies: implements the small WebSocket client CDP needs on top of node:http,
// so it works on Node >= 18 without a global WebSocket or any npm package.
//
// It launches a SEPARATE Chrome/Edge process with its own temporary profile and a loopback-only
// remote-debugging port. It never touches the user's normal browser profile.
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { randomBytes } from 'node:crypto';

const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---------------------------------------------------------------- WebSocket (client side, RFC 6455 subset)
class MiniWebSocket {
  constructor(socket, head) {
    this.socket = socket;
    this.buffer = head && head.length ? Buffer.from(head) : Buffer.alloc(0);
    this.fragments = [];
    this.onmessage = () => {};
    this.onclose = () => {};
    this.closed = false;
    socket.on('data', chunk => { this.buffer = Buffer.concat([this.buffer, chunk]); this.#drain(); });
    socket.on('close', () => { if (!this.closed) { this.closed = true; this.onclose(); } });
    socket.on('error', () => { if (!this.closed) { this.closed = true; this.onclose(); } });
    if (this.buffer.length) this.#drain();
  }
  static connect(url, timeoutMs = 15000) {
    const u = new URL(url);
    return new Promise((resolve, reject) => {
      const key = randomBytes(16).toString('base64');
      const req = http.request({
        host: u.hostname, port: u.port, path: u.pathname + u.search, method: 'GET',
        headers: { Connection: 'Upgrade', Upgrade: 'websocket', 'Sec-WebSocket-Version': '13', 'Sec-WebSocket-Key': key },
      });
      const timer = setTimeout(() => { req.destroy(new Error(`WebSocket connect timeout: ${url}`)); }, timeoutMs);
      req.on('upgrade', (res, socket, head) => { clearTimeout(timer); socket.setNoDelay(true); resolve(new MiniWebSocket(socket, head)); });
      req.on('response', res => { clearTimeout(timer); reject(new Error(`WebSocket upgrade refused: HTTP ${res.statusCode}`)); });
      req.on('error', err => { clearTimeout(timer); reject(err); });
      req.end();
    });
  }
  send(text) {
    if (this.closed) throw new Error('WebSocket is closed');
    const payload = Buffer.from(text, 'utf8');
    const len = payload.length;
    let header;
    if (len < 126) { header = Buffer.alloc(2); header[1] = 0x80 | len; }
    else if (len < 65536) { header = Buffer.alloc(4); header[1] = 0x80 | 126; header.writeUInt16BE(len, 2); }
    else { header = Buffer.alloc(10); header[1] = 0x80 | 127; header.writeBigUInt64BE(BigInt(len), 2); }
    header[0] = 0x81; // FIN + text
    const mask = randomBytes(4);
    const masked = Buffer.alloc(len);
    for (let i = 0; i < len; i++) masked[i] = payload[i] ^ mask[i & 3];
    this.socket.write(Buffer.concat([header, mask, masked]));
  }
  #control(opcode, data = Buffer.alloc(0)) {
    const header = Buffer.from([0x80 | opcode, 0x80 | data.length]);
    const mask = randomBytes(4);
    const masked = Buffer.alloc(data.length);
    for (let i = 0; i < data.length; i++) masked[i] = data[i] ^ mask[i & 3];
    try { this.socket.write(Buffer.concat([header, mask, masked])); } catch { /* socket gone */ }
  }
  #drain() {
    for (;;) {
      const b = this.buffer;
      if (b.length < 2) return;
      const fin = (b[0] & 0x80) !== 0, opcode = b[0] & 0x0f, masked = (b[1] & 0x80) !== 0;
      let len = b[1] & 0x7f, off = 2;
      if (len === 126) { if (b.length < 4) return; len = b.readUInt16BE(2); off = 4; }
      else if (len === 127) { if (b.length < 10) return; len = Number(b.readBigUInt64BE(2)); off = 10; }
      const maskLen = masked ? 4 : 0;
      if (b.length < off + maskLen + len) return;
      let data = b.subarray(off + maskLen, off + maskLen + len);
      if (masked) { const m = b.subarray(off, off + 4); data = Buffer.from(data.map((x, i) => x ^ m[i & 3])); }
      this.buffer = b.subarray(off + maskLen + len);
      if (opcode === 0x8) { this.#control(0x8); this.closed = true; this.socket.end(); this.onclose(); return; }
      if (opcode === 0x9) { this.#control(0xA, Buffer.from(data)); continue; }
      if (opcode === 0xA) continue;
      if (opcode === 0x1 || opcode === 0x2 || opcode === 0x0) {
        this.fragments.push(Buffer.from(data));
        if (fin) { const full = Buffer.concat(this.fragments); this.fragments = []; this.onmessage(full.toString('utf8')); }
      }
    }
  }
  close() { if (!this.closed) { this.#control(0x8); this.closed = true; try { this.socket.end(); } catch { /* ignore */ } } }
}

// ---------------------------------------------------------------- HTTP endpoints of the debugging port
function httpJson(port, pathname, method = 'GET') {
  return new Promise((resolve, reject) => {
    const req = http.request({ host: '127.0.0.1', port, path: pathname, method }, res => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', c => { body += c; });
      res.on('end', () => {
        if (res.statusCode >= 400) return reject(new Error(`${method} ${pathname} → HTTP ${res.statusCode}: ${body.slice(0, 200)}`));
        try { resolve(body ? JSON.parse(body) : null); } catch { resolve(body); }
      });
    });
    req.on('error', reject);
    req.setTimeout(10000, () => req.destroy(new Error(`${method} ${pathname} timeout`)));
    req.end();
  });
}

// ---------------------------------------------------------------- Chrome launcher
export function findChrome(explicit) {
  const candidates = [
    explicit, process.env.CHROME_PATH,
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    path.join(os.homedir(), 'AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'),
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  ].filter(Boolean);
  const found = candidates.find(p => { try { return fs.statSync(p).isFile(); } catch { return false; } });
  if (!found) throw new Error(`找不到 Chrome/Edge，可执行文件候选：${candidates.join(' | ')}；用 --chrome <路径> 或环境变量 CHROME_PATH 指定`);
  return found;
}

export async function launchChrome({ chromePath, port = 9333, profileDir, headless = false, extraArgs = [] } = {}) {
  const exe = findChrome(chromePath);
  profileDir ||= fs.mkdtempSync(path.join(os.tmpdir(), 'b-host-verify-profile-'));
  try { await httpJson(port, '/json/version'); throw new Error(`端口 ${port} 已被另一个调试中的浏览器占用；关掉它或用 --port 换一个端口`); }
  catch (error) { if (/已被另一个/.test(error.message)) throw error; }
  const args = [
    `--remote-debugging-port=${port}`, '--remote-debugging-address=127.0.0.1', `--user-data-dir=${profileDir}`,
    '--no-first-run', '--no-default-browser-check', '--disable-sync', '--disable-extensions', '--disable-background-networking', '--disable-component-update',
    '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows',
    '--disable-features=CalculateNativeWinOcclusion,IntensiveWakeUpThrottling', '--window-size=1400,900',
    ...(headless ? ['--headless=new'] : []),
    ...(process.platform === 'linux' ? ['--no-sandbox', '--disable-dev-shm-usage'] : []),
    ...extraArgs, 'about:blank',
  ];
  const child = spawn(exe, args, { stdio: 'ignore', detached: false });
  let exited = null;
  child.on('exit', code => { exited = code; });
  const deadline = Date.now() + 30000;
  for (;;) {
    if (exited !== null) throw new Error(`浏览器进程启动后立即退出（exit ${exited}）：${exe}`);
    try { const version = await httpJson(port, '/json/version'); return { child, exe, port, profileDir, version }; }
    catch { if (Date.now() > deadline) { try { child.kill(); } catch { /* ignore */ } throw new Error(`30 秒内连不上调试端口 ${port}`); } await sleep(300); }
  }
}

export async function closeChrome(browser) {
  if (!browser?.child) return;
  try { const v = await httpJson(browser.port, '/json/version'); const ws = await MiniWebSocket.connect(v.webSocketDebuggerUrl); ws.send(JSON.stringify({ id: 1, method: 'Browser.close' })); await sleep(800); ws.close(); } catch { /* fall through */ }
  try { browser.child.kill(); } catch { /* ignore */ }
}

// ---------------------------------------------------------------- Page (one tab)
export class Page {
  constructor(port, target, ws) {
    this.port = port; this.target = target; this.ws = ws; this.nextId = 1; this.pending = new Map(); this.listeners = new Map();
    ws.onmessage = text => {
      let msg; try { msg = JSON.parse(text); } catch { return; }
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject, timer } = this.pending.get(msg.id); this.pending.delete(msg.id); clearTimeout(timer);
        if (msg.error) reject(new Error(`CDP ${msg.error.message} ${msg.error.data || ''}`.trim())); else resolve(msg.result);
      } else if (msg.method) for (const fn of this.listeners.get(msg.method) || []) fn(msg.params);
    };
    ws.onclose = () => { for (const { reject, timer } of this.pending.values()) { clearTimeout(timer); reject(new Error('CDP connection closed')); } this.pending.clear(); };
  }
  static async open(port, url = 'about:blank') {
    let target;
    try { target = await httpJson(port, `/json/new?${encodeURI(url)}`, 'PUT'); }
    catch { target = await httpJson(port, `/json/new?${encodeURI(url)}`, 'GET'); }
    const ws = await MiniWebSocket.connect(target.webSocketDebuggerUrl);
    const page = new Page(port, target, ws);
    await page.send('Page.enable'); await page.send('Runtime.enable');
    return page;
  }
  on(method, fn) { if (!this.listeners.has(method)) this.listeners.set(method, []); this.listeners.get(method).push(fn); }
  send(method, params = {}, timeoutMs = 60000) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { this.pending.delete(id); reject(new Error(`CDP ${method} timeout after ${timeoutMs}ms`)); }, timeoutMs);
      this.pending.set(id, { resolve, reject, timer });
      try { this.ws.send(JSON.stringify({ id, method, params })); } catch (error) { clearTimeout(timer); this.pending.delete(id); reject(error); }
    });
  }
  /** Evaluate an expression in the page and return its JSON value. Promises are awaited. */
  async eval(expression, timeoutMs = 60000) {
    const r = await this.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true, userGesture: true, timeout: timeoutMs }, timeoutMs + 5000);
    if (r.exceptionDetails) {
      const d = r.exceptionDetails; throw new Error(`页面脚本异常：${d.exception?.description || d.text || JSON.stringify(d).slice(0, 300)}`);
    }
    return r.result?.value;
  }
  async waitFor(expression, { timeoutMs = 30000, intervalMs = 250, label = expression } = {}) {
    const deadline = Date.now() + timeoutMs; let last;
    for (;;) {
      try { last = await this.eval(expression, 10000); if (last) return last; } catch (error) { last = error.message; }
      if (Date.now() > deadline) throw new Error(`等待超时（${timeoutMs}ms）：${label}；最后结果：${typeof last === 'string' ? last.slice(0, 300) : JSON.stringify(last)?.slice(0, 300)}`);
      await sleep(intervalMs);
    }
  }
  async navigate(url, { waitLoad = true, timeoutMs = 60000 } = {}) {
    const loaded = waitLoad ? new Promise(resolve => { const t = setTimeout(resolve, timeoutMs); this.on('Page.loadEventFired', () => { clearTimeout(t); resolve(); }); }) : null;
    await this.send('Page.navigate', { url });
    if (loaded) await loaded;
  }
  async reload({ timeoutMs = 60000 } = {}) {
    const loaded = new Promise(resolve => { const t = setTimeout(resolve, timeoutMs); this.on('Page.loadEventFired', () => { clearTimeout(t); resolve(); }); });
    await this.send('Page.reload', { ignoreCache: true });
    await loaded;
  }
  async screenshot(file) {
    try {
      await this.send('Page.bringToFront');
      const r = await this.send('Page.captureScreenshot', { format: 'png' }, 30000);
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, Buffer.from(r.data, 'base64'));
      return file;
    } catch (error) { return `截图失败：${error.message}`; }
  }
  async bringToFront() { try { await this.send('Page.bringToFront'); } catch { /* ignore */ } }
  async close() { try { await httpJson(this.port, `/json/close/${this.target.id}`); } catch { /* ignore */ } try { this.ws.close(); } catch { /* ignore */ } }
}

export { httpJson, MiniWebSocket, sleep };
