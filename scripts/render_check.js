/**
 * 报告渲染自检：确认 ECharts 是否出图、有无脚本错误、表格是否溢出，可选导出 PDF。
 *
 * 用法：
 *   NODE_PATH=<node_modules 路径> node render_check.js <报告.html> [输出.pdf]
 *
 * 浏览器自动探测顺序：
 *   1. 环境变量 REPORT_BROWSER
 *   2. puppeteer 缓存中的 chrome-headless-shell（优先，headless:'shell' 模式最稳）
 *   3. puppeteer 缓存中的 chrome
 *   4. 系统 Edge / Chrome
 *
 * 说明：本机若以管理员权限运行，Edge 与 chrome 的 headless 启动会失败并报
 * "Failed to launch the browser process"，此时必须用 chrome-headless-shell。
 */
const fs = require('fs');
const path = require('path');

function findBrowser() {
  if (process.env.REPORT_BROWSER) return { exe: process.env.REPORT_BROWSER, shell: /headless-shell/.test(process.env.REPORT_BROWSER) };
  const cache = path.join(process.env.USERPROFILE || process.env.HOME || '', '.cache', 'puppeteer');
  for (const kind of ['chrome-headless-shell', 'chrome']) {
    const base = path.join(cache, kind);
    if (!fs.existsSync(base)) continue;
    for (const ver of fs.readdirSync(base)) {
      const dir = path.join(base, ver);
      for (const sub of fs.readdirSync(dir)) {
        for (const name of ['chrome-headless-shell.exe', 'chrome.exe']) {
          const p = path.join(dir, sub, name);
          if (fs.existsSync(p)) return { exe: p, shell: /headless-shell/.test(name) };
        }
      }
    }
  }
  for (const p of [
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Google/Chrome/Application/chrome.exe'
  ]) if (fs.existsSync(p)) return { exe: p, shell: false };
  return null;
}

(async () => {
  const target = process.argv[2];
  if (!target) { console.error('用法: node render_check.js <html> [out.pdf]'); process.exit(2); }

  let puppeteer;
  try { puppeteer = require('puppeteer-core'); }
  catch (e) { console.error('缺少 puppeteer-core，请先 npm install puppeteer-core'); process.exit(2); }

  const b = findBrowser();
  if (!b) { console.error('未找到可用浏览器'); process.exit(2); }

  const browser = await puppeteer.launch({
    executablePath: b.exe,
    headless: b.shell ? 'shell' : true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu',
           '--disable-dev-shm-usage', '--allow-file-access-from-files',
           '--no-first-run', '--no-default-browser-check', '--font-render-hinting=none']
  });

  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  const url = 'file:///' + path.resolve(target).replace(/\\/g, '/');
  await page.setViewport({ width: 1000, height: 1400, deviceScaleFactor: 1 });
  await page.goto(url, { waitUntil: 'networkidle0', timeout: 120000 });
  await new Promise(r => setTimeout(r, 2500));

  const report = await page.evaluate(() => {
    const out = {
      echarts: typeof echarts !== 'undefined',
      containers: document.querySelectorAll('.chart-container').length,
      ok: [], empty: [], noCanvas: [],
      tables: document.querySelectorAll('table').length,
      captions: document.querySelectorAll('caption').length,
      sections: document.querySelectorAll('h1.sec').length,
      overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2
    };
    document.querySelectorAll('.chart-container').forEach(el => {
      const id = el.id || (el.querySelector('.chart') || {}).id || '(无id)';
      const cv = el.querySelector('canvas');
      if (!cv) { out.noCanvas.push(id); return; }
      if (cv.width < 10 || cv.height < 10) out.empty.push(id);
      else out.ok.push(id);
    });
    const h1 = document.querySelector('h1.sec');
    if (h1) {
      const cs = getComputedStyle(h1);
      out.h1 = { bg: cs.backgroundColor, color: cs.color };
    }
    return out;
  });

  let pdfInfo = null;
  if (process.argv[3]) {
    await page.emulateMediaType('print');
    await page.setViewport({ width: Math.round(184 * 96 / 25.4), height: Math.round(265 * 96 / 25.4), deviceScaleFactor: 2 });
    await page.evaluate(() => window.dispatchEvent(new Event('resize')));
    await new Promise(r => setTimeout(r, 2500));
    await page.evaluate(() => window.fixPrintBreaks && window.fixPrintBreaks());
    await new Promise(r => setTimeout(r, 1500));

    const contentH = await page.evaluate(() => document.body.scrollHeight);
    const pageH = Math.round(265 * 96 / 25.4);
    await page.pdf({
      path: process.argv[3], format: 'A4', printBackground: true, preferCSSPageSize: true,
      margin: { top: '16mm', right: '13mm', bottom: '16mm', left: '13mm' }, timeout: 180000
    });
    pdfInfo = { out: process.argv[3], minPages: Math.ceil(contentH / pageH), contentH, pageH };
    if (fs.existsSync(process.argv[3])) {
      const buf = fs.readFileSync(process.argv[3]);
      const m = buf.toString('latin1').match(/\/MediaBox\s*\[([^\]]*)\]/);
      pdfInfo.bytes = buf.length;
      pdfInfo.mediaBox = m ? m[1].trim() : null;
    }
  }

  const verdict = [];
  if (!report.echarts) verdict.push('ECharts 未加载（CDN 不通？）');
  if (report.noCanvas.length) verdict.push('无 canvas: ' + report.noCanvas.join(','));
  if (report.empty.length) verdict.push('canvas 为空: ' + report.empty.join(','));
  if (report.overflowX) verdict.push('页面出现横向滚动，检查宽元素');
  if (report.tables !== report.captions) verdict.push('表格与表题数量不一致 ' + report.tables + '/' + report.captions);
  if (errors.length) verdict.push('脚本错误 ' + errors.length + ' 条');

  console.log(JSON.stringify({
    browser: b.exe,
    mode: b.shell ? 'shell' : 'headless',
    charts_ok: report.ok.length,
    charts_failed: report.ok.length === 0 ? report.containers : report.noCanvas.length + report.empty.length,
    sections: report.sections,
    tables: report.tables,
    captions: report.captions,
    h1: report.h1,
    pdf: pdfInfo,
    errors,
    verdict: verdict.length ? verdict : 'PASS'
  }, null, 2));

  await browser.close();
  process.exit(verdict.length ? 1 : 0);
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
