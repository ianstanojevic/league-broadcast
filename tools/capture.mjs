// Screenshot a League Broadcast overlay at 1920x1080 with a transparent background.
//
//   node tools/capture.mjs <url> <out.png> [waitSeconds=8] [selectorToWaitFor] [minVisibleCount=1]
//
// Starts a headless Edge with its own throwaway profile, waits in real time so the
// overlay can receive live/mock data from League Broadcast, then captures the page.
import { spawn } from "node:child_process";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [url, out, waitArg = "8", selector, minArg = "1"] = process.argv.slice(2);
if (!url || !out) {
  console.error("usage: node tools/capture.mjs <url> <out.png> [waitSeconds] [selector]");
  process.exit(2);
}
const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const PORT = 9300 + Math.floor(Math.random() * 500);
const profile = mkdtempSync(join(tmpdir(), "lb-capture-"));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const edge = spawn(EDGE, [
  "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`,
  "--window-size=1920,1080", "about:blank",
], { stdio: "ignore" });

try {
  let target;
  for (let i = 0; i < 50 && !target; i++) {
    await sleep(200);
    try {
      const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      target = list.find((t) => t.type === "page");
    } catch { /* not up yet */ }
  }
  if (!target) throw new Error("Edge did not start");

  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  let id = 0;
  const pending = new Map();
  ws.onmessage = (m) => {
    const msg = JSON.parse(m.data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
  };
  const send = (method, params = {}) => new Promise((r) => {
    const n = ++id; pending.set(n, r); ws.send(JSON.stringify({ id: n, method, params }));
  });

  await send("Emulation.setDeviceMetricsOverride", { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
  await send("Emulation.setDefaultBackgroundColorOverride", { color: { r: 0, g: 0, b: 0, a: 0 } });
  await send("Page.navigate", { url });

  const deadline = Date.now() + Number(waitArg) * 1000;
  if (selector) {
    // Wait until enough matching elements are visible (mock champ select runs in cycles).
    while (Date.now() < deadline + 90000) {
      const r = await send("Runtime.evaluate", {
        expression: `[...document.querySelectorAll(${JSON.stringify(selector)})].filter(e => { const b = e.getBoundingClientRect(); return b.width > 10 && b.height > 10; }).length >= ${Number(minArg)}`,
        returnByValue: true,
      });
      if (r.result?.result?.value && Date.now() >= deadline) break;
      await sleep(250);
    }
    await sleep(2500);   // let late images (e.g. the tournament icon) swap in

  } else {
    await sleep(deadline - Date.now());
  }

  const shot = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  writeFileSync(out, Buffer.from(shot.result.data, "base64"));
  console.log("wrote", out);
  ws.close();
} finally {
  edge.kill();
  await sleep(500);
  try { rmSync(profile, { recursive: true, force: true }); } catch { /* Edge may still hold files */ }
}
