// V2 capture: real screens of docs/index.html (the live Evidence Workbench), element by element, at 3x
// for clean zooms, plus a live Mol* WebGL rotation clip of structure 1B68.
// Usage: node video/v2/capture.mjs [outDir]   (default video/remotion/public/v2/shots)
// Writes <name>.png, molstar_spin.mp4 and shots.json (css size + relative callout rects per shot).
// Mol* loads from cdn.jsdelivr.net, so the page needs network; offline, the viewer steps are skipped cleanly.
const { chromium } = await import(process.env.PLAYWRIGHT_CORE || 'playwright-core');
import http from 'node:http';
import path from 'node:path';
import fs from 'node:fs';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const docs = path.join(root, 'docs');
const out = path.resolve(process.argv[2] || path.join(root, 'video/remotion/public/v2/shots'));
fs.mkdirSync(out, { recursive: true });

const CHROME = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const SCALE = 3;
const VIEWPORT = { width: 1400, height: 1000 };
const SPIN = { width: 1280, height: 720, seconds: 6 };
const LAUNCH_ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl'];
const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.json': 'application/json', '.cif': 'text/plain; charset=utf-8', '.mp4': 'video/mp4', '.vtt': 'text/vtt',
  '.jpg': 'image/jpeg', '.png': 'image/png', '.svg': 'image/svg+xml',
};

/** Static server for docs/ on an ephemeral loopback port. Refuses anything that resolves outside docs/. */
const serve = () => new Promise((resolve) => {
  const server = http.createServer((req, res) => {
    const rel = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    const file = path.normalize(path.join(docs, rel.endsWith('/') ? rel + 'index.html' : rel));
    if (file !== docs && !file.startsWith(docs + path.sep)) { res.writeHead(403).end('forbidden'); return; }
    fs.readFile(file, (err, buf) => {
      if (err) { res.writeHead(404).end('not found'); return; }
      res.writeHead(200, { 'content-type': MIME[path.extname(file)] || 'application/octet-stream' }).end(buf);
    });
  });
  server.listen(0, '127.0.0.1', () => resolve(server));
});

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** docs/app.js sets "<id> loaded (...)" and, in the same tick, overwrites it with "Focused A:112", so /loaded/i alone
 *  is never observable. An init script latches `window.__molLoaded` on /loaded/i OR the post-load states
 *  "Focused ..." / "Selected residue ..." (both only occur after loadStructureFromData resolved). */
const LATCH = () => {
  window.__molLoaded = false;
  const watch = () => {
    const el = document.querySelector('#molstar-status');
    if (!el) return;
    const check = () => { if (/loaded|^\s*(focused|selected residue)/i.test(el.textContent || '')) window.__molLoaded = true; };
    check();
    new MutationObserver(check).observe(el, { childList: true, characterData: true, subtree: true });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', watch); else watch();
};

/** Waits (up to `ms`) for the latch; false if Mol* never reports loaded (offline). */
const molstarLoaded = async (page, ms = 15000) => {
  try {
    await page.waitForFunction(() => window.__molLoaded === true, null, { timeout: ms });
    return true;
  } catch { return false; }
};

/** Opens structure 1B68 in the select (value matches /1b68/i); resolves true once Mol* reports loaded. */
const openStructure = async (page, pattern = '1b68') => {
  const value = await page.$eval('#structure-select', (sel, p) => {
    const re = new RegExp(p, 'i');
    const o = [...sel.options].find((x) => re.test(x.value) || re.test(x.textContent));
    return o ? o.value : null;
  }, pattern);
  if (!value) { console.log('MISSING structure option', pattern); return false; }
  await page.evaluate(() => { window.__molLoaded = false; });
  await page.selectOption('#structure-select', value);
  return molstarLoaded(page);
};

/** Reset the workbench filters so every shot starts from the same state. */
const resetFilters = async (page) => {
  await page.click('[data-hyp="ALL"]');
  await page.click('[data-dir="ALL"]');
  await page.fill('#search-input', '');
  await page.evaluate(() => { const l = document.querySelector('#findings-list'); if (l) l.scrollTop = 0; });
  await page.waitForTimeout(200);
};

/** css-px rects, relative to `root`, of text needles / selectors / the finding row that carries `rowId`. */
const collectRects = (rootEl, spec) => rootEl.evaluate((root, spec) => {
  if (spec.rowId) { // bring the row to the top of the scrolling list so the shot and the rects agree
    const target = [...root.querySelectorAll('.finding-row')].find((e) => e.innerText.includes(spec.rowId));
    const list = root.querySelector('#findings-list');
    if (target && list) list.scrollTop += target.getBoundingClientRect().top - list.getBoundingClientRect().top;
  }
  const R = root.getBoundingClientRect();
  const rel = (r) => ({ x: Math.round(r.left - R.left), y: Math.round(r.top - R.top), w: Math.round(r.width), h: Math.round(r.height) });
  const out = {};
  let scope = root;
  if (spec.rowId) {
    const row = [...root.querySelectorAll('.finding-row')].find((e) => e.innerText.includes(spec.rowId));
    if (!row) return { row: null };
    out.row = rel(row.getBoundingClientRect());
    scope = row;
  }
  for (const [key, sel] of Object.entries(spec.selectors || {})) {
    const el = scope.querySelector(sel);
    out[key] = el ? rel(el.getBoundingClientRect()) : null;
  }
  const walk = (needle) => {
    const tw = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
    for (let n = tw.nextNode(); n; n = tw.nextNode()) {
      const i = n.textContent.indexOf(needle);
      if (i >= 0) return { node: n, i };
    }
    return null;
  };
  for (const t of spec.text || []) {
    const hit = walk(t);
    if (!hit) { out['text:' + t] = null; continue; }
    const r = document.createRange();
    r.setStart(hit.node, hit.i); r.setEnd(hit.node, hit.i + t.length);
    out['text:' + t] = rel(r.getBoundingClientRect());
  }
  if (spec.contraRows) {
    out.contraRows = [...root.querySelectorAll('.finding-row.is-contra')].map((e) => ({
      ...rel(e.getBoundingClientRect()), id: (e.querySelector('.finding-id')?.innerText || '').split('|')[0].trim(),
    }));
  }
  return out;
}, spec);

// [name, selector, prepare(page), rect spec]
const SHOTS = [
  ['c5_banner', '.rule-c5-banner', null, null],
  ['controls_bar', '.controls-bar', null, null],
  ['viewer_1b68', '.viewer-pane', async (p) => {
    const ok = await openStructure(p, '1b68');
    if (ok && (await p.$('#residue-bar button, #residue-bar .residue-pill'))) {
      await p.click('#residue-bar button, #residue-bar .residue-pill');
    }
    await p.waitForTimeout(800);
  }, null],
  ['drawer_h5_35750033', '.drawer-pane', async (p) => {
    await resetFilters(p);
    await p.click('[data-hyp="H5"]');
    await p.fill('#search-input', '35750033');
    await p.waitForTimeout(400);
  }, {
    rowId: 'H5-P4.F1',
    selectors: { quote: '.finding-quote', meta: '.finding-meta', id: '.finding-id' },
    text: ['3-fold, p<0.001', 'Fig 6H', 'PMID 35750033'],
  }],
  ['drawer_h2_29946028', '.drawer-pane', async (p) => {
    await resetFilters(p);
    await p.click('[data-hyp="H2"]');
    await p.fill('#search-input', '29946028');
    await p.waitForTimeout(400);
  }, {
    rowId: 'H2-P2.F12',
    selectors: { quote: '.finding-quote', meta: '.finding-meta', id: '.finding-id' },
    text: ['decreased by', 'Fig 4C'],
  }],
  ['drawer_h2_contra', '.drawer-pane', async (p) => {
    await resetFilters(p);
    await p.click('[data-hyp="H2"]');
    await p.fill('#search-input', 'NHE6');
    await p.click('[data-dir="contradicts"]');
    await p.waitForTimeout(400);
    await p.evaluate(() => { const l = document.querySelector('#findings-list'); if (l) l.scrollTop = 0; });
    await p.waitForTimeout(150);
  }, { contraRows: true }],
];

/** Live Mol* WebGL rotation of 1B68: record a 1280x720 page video, drag-rotate, crop .molstar-wrap, H.264 30 fps. */
const recordSpin = async (browser, base) => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'meccog-spin-'));
  try {
    const ctx = await browser.newContext({
      viewport: { width: SPIN.width, height: SPIN.height }, deviceScaleFactor: 1,
      recordVideo: { dir: tmp, size: { width: SPIN.width, height: SPIN.height } },
    });
    const page = await ctx.newPage();
    await page.addInitScript(LATCH);
    const t0 = Date.now();
    await page.goto(base, { waitUntil: 'load' });
    await page.waitForSelector('#findings-list .finding-row');
    // let the viewer fill the 16:9 frame so the crop is sharp (no upscaling); the crop still uses the measured box
    await page.addStyleTag({ content: '.molstar-wrap{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}' });
    await page.evaluate(() => window.dispatchEvent(new Event('resize')));
    if (!(await openStructure(page, '1b68'))) {
      console.log('SKIP molstar_spin (1b68 not loaded; offline?)');
      await ctx.close();
      return false;
    }
    await page.waitForTimeout(600);
    const box = await (await page.$('.molstar-wrap')).boundingBox();
    const tStart = (Date.now() - t0) / 1000;
    const canvas = await (await page.$('#molstar-container')).boundingBox();
    const y = canvas.y + canvas.height / 2;
    const x0 = canvas.x + canvas.width * 0.2;
    const x1 = canvas.x + canvas.width * 0.8;
    await page.mouse.move(x0, y);
    await page.mouse.down();
    const steps = SPIN.seconds * 20;
    for (let i = 1; i <= steps; i++) {
      const u = i / steps;
      const e = u * u * (3 - 2 * u); // smoothstep: eases in and out of the rotation
      await page.mouse.move(x0 + (x1 - x0) * e, y + Math.sin(u * Math.PI) * 40, { steps: 1 });
      await sleep(1000 / 20);
    }
    await page.mouse.up();
    await page.waitForTimeout(500);
    const video = page.video();
    await ctx.close(); // finalizes the .webm
    const webm = await video.path();
    const crop = `crop=${Math.round(box.width)}:${Math.round(box.height)}:${Math.round(box.x)}:${Math.round(box.y)}`;
    const mp4 = path.join(out, 'molstar_spin.mp4');
    const r = spawnSync('ffmpeg', [
      '-v', 'error', '-y', '-ss', (tStart + 0.2).toFixed(2), '-i', webm, '-t', String(SPIN.seconds + 0.5),
      '-vf', `${crop},scale=${SPIN.width}:${SPIN.height}:flags=lanczos,fps=30,format=yuv420p`,
      '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', '-an', mp4,
    ], { stdio: 'inherit' });
    if (r.status !== 0) throw new Error('ffmpeg failed');
    console.log('molstar_spin'.padEnd(22), crop, '->', path.relative(root, mp4));
    return true;
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
};

const server = await serve();
const base = `http://127.0.0.1:${server.address().port}/index.html`;
let browser;
try {
  browser = await chromium.launch({ executablePath: CHROME, headless: true, args: LAUNCH_ARGS });
  const ctx = await browser.newContext({ viewport: VIEWPORT, deviceScaleFactor: SCALE });
  const page = await ctx.newPage();
  await page.addInitScript(LATCH);
  await page.goto(base, { waitUntil: 'load' });
  await page.waitForSelector('#findings-list .finding-row');
  await page.evaluate(() => document.fonts.ready);
  const loaded = await molstarLoaded(page, 15000);
  console.log('mol* initial load:', loaded ? 'loaded' : 'not loaded (offline? continuing)');

  const meta = {};
  for (const [name, sel, prep, spec] of SHOTS) {
    if (prep) await prep(page);
    await page.waitForTimeout(300);
    const el = await page.$(sel);
    if (!el) { console.log('MISSING', name, sel); continue; }
    await el.scrollIntoViewIfNeeded();
    const box = await el.boundingBox();
    const rects = spec ? await collectRects(el, spec) : undefined;
    await el.screenshot({ path: path.join(out, name + '.png') });
    meta[name] = { selector: sel, cssW: Math.round(box.width), cssH: Math.round(box.height), scale: SCALE, rects };
    console.log(name.padEnd(22), sel.padEnd(20), `${meta[name].cssW}x${meta[name].cssH}`);
  }
  fs.writeFileSync(path.join(out, 'shots.json'), JSON.stringify(meta, null, 1));
  await ctx.close();

  await recordSpin(browser, base);
} finally {
  await browser?.close();
  await new Promise((r) => server.close(r));
}
