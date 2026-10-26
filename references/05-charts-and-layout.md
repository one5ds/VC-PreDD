# 图表、排版与打印适配

## 一、图表清单

只做能承载判断的图，不做装饰图。总数控在 8-10 张，每张在正文里有对应的分析段落，图注写明数据来源与口径。

| 编号 | 位置 | 类型 | 承载的判断 |
|---|---|---|---|
| C1 | 记分卡 | 环形仪表 + 横向条形 | 总分与六维分布，一眼看出短板 |
| C2 | 市场与产业链 | 分组柱状 | TAM/SAM/SOM 三法测算结果对比，暴露口径分歧 |
| C3 | 市场与产业链 | 柱线组合 | 市场规模历史三年与预测三年，柱为规模，线为增速 |
| C4 | 市场与产业链 | 散点气泡 | 竞争矩阵，横轴成本优势、纵轴技术壁垒、气泡为份额 |
| C5 | 商业模式 | 环形图 | 收入结构或客户结构占比 |
| C6 | 商业模式 / 财务 | 横向柱状 | 单位经济：LTV、CAC、LTV/CAC 与同业对比 |
| C7 | 财务诊断 | 柱线组合 | 收入与毛利率趋势，或现金流三条线 |
| C8 | 财务诊断 | 分组柱状 | 收入 ±15% 三情景对估值与 MOIC 的影响 |
| C9 | 风险 | 雷达图 | 六类风险的相对强度 |
| C10 | 估值 | 柱状 + 参考线 | 可比公司倍数区间与本项目所处分位 |

图表类型选择规则：结构占比用饼图或环形；数值排序用柱状（类别多时用横向）；时间趋势用折线；多维度交叉用柱线组合或散点。不要用 3D、渐变填充、阴影，也避免堆叠面积图（早期项目数据点少，堆叠无意义）。

## 二、ECharts 配置要点

### 引入与初始化

CDN 引入写在 `<head>` 之后，图表脚本放在 body 末尾。初始化必须用容器实际宽高，不能用固定值，否则打印和缩放都会错位。

```javascript
function mount(id, option){
  var el = document.getElementById(id);
  if (!el || typeof echarts === 'undefined') return null;
  var chart = echarts.init(el, null, {
    renderer: 'canvas',
    width: el.clientWidth || 640,
    height: el.clientHeight || 340
  });
  chart.setOption(option);
  return chart;
}
```

容器 CSS 必须显式给高度，`min-height` 不够，ECharts 读不到高度会渲染成 0。

```css
.chart-container{
  display:flex; flex-direction:column;
  width:100%; height:360px; min-height:320px;
  margin:24px 0; padding:16px 8px 10px;
  background:#fff; border-radius:10px;
  box-shadow:0 1px 4px rgba(0,0,0,.04);
  page-break-inside:avoid; break-inside:avoid;
}
.chart{flex:1 1 auto;width:100%;min-height:240px;}
.chart-title{font-size:14px;font-weight:600;color:#1a3a5c;margin:0 0 8px 12px;}
.chart-note{font-size:12px;color:#8a8a8a;margin:6px 0 0 12px;}
```

HTML 结构必须三层，id 挂在最内层画布 div 上，不能挂在带内边距和图题的容器上：

```html
<div class="chart-container">
  <div class="chart-title">图 4-1 xxx</div>
  <div class="chart" id="c2"></div>
</div>
```

**这一步做错的后果**：把 id 直接写在 `.chart-container` 上，ECharts 生成的画布会作为容器最后一个子元素插入，位置落在标题下方，高度却按容器全高计算，于是画布整体向下溢出，底部图例被裁掉一半，顶部坐标轴标签也被标题压住。肉眼看 HTML 没问题，只有截图或导出 PDF 才会发现。图例被切、底部标签消失，先查这一条。

### 主题

```javascript
var THEME = {
  primary:'#1a3a5c', secondary:'#2d5a87', accent:'#c5a572',
  riskHigh:'#c0392b', riskMid:'#e67e22', riskLow:'#27ae60',
  axis:'#d9d4cd', text:'#2c2c2c', textSoft:'#6b6b6b',
  palette:['#1a3a5c','#2d5a87','#c5a572','#5b8ab0','#8aa9c0','#dcc9a4']
};
var AXIS = {
  axisLine:{lineStyle:{color:THEME.axis}},
  axisLabel:{color:THEME.textSoft, fontSize:11},
  splitLine:{lineStyle:{color:'#efece7'}}
};
```

所有图表必须包含：标题、图例（单系列可省）、坐标轴标签（含单位）、数据标签（`label:{show:true}`）、tooltip。数据标签在类别超过 8 个时可关闭，用 tooltip 替代。

### 三条硬约束

1. **图文数据一致**。图表数据取自正文的同一张表，不要重新算。图注写明"数据来源：表 4-2"。改数时先改表再改图。
2. **单位统一**。正文用万元，图表也用万元，不要图表换亿元。轴标签写"（万元）"。
3. **零基准**。柱状图 y 轴从 0 开始，避免视觉夸大。折线图在跨度大时可以不为 0，但要在轴标签标明。

### 自适应

```javascript
var charts = [];
window.addEventListener('resize', function(){
  charts.forEach(function(c){ c && c.resize(); });
});
if (window.ResizeObserver){
  var ro = new ResizeObserver(function(){
    charts.forEach(function(c){ c && c.resize(); });
  });
  document.querySelectorAll('.chart-container').forEach(function(el){ ro.observe(el); });
}
```

## 三、字号与排版规范

### 一级标题

原规范写"白色文字 + 浅米色背景"，实际渲染会变成白底白字看不清。改为深蓝色通栏色块承载白字，序号块用辅助蓝并加白色描边，对比度达标。

```css
h1.sec{
  display:flex; align-items:center; gap:14px;
  font-size:20px; font-weight:700; line-height:1.5;
  color:#ffffff; background:#1a3a5c;
  margin:48px 0 20px; padding:14px 20px;
  border-radius:10px; border-bottom:2px solid #d9d4cd;
  text-align:left; text-indent:0;
  page-break-after:avoid; break-after:avoid;
}
h1.sec .num{
  flex:0 0 32px; width:32px; height:32px; border-radius:8px;
  background:#2d5a87; border:1px solid rgba(255,255,255,.4);
  color:#fff; font-size:15px; font-weight:700;
  display:flex; align-items:center; justify-content:center;
}
```

### 二级与三级标题

```css
h2{font-size:16px;font-weight:600;color:#1a3a5c;line-height:1.5;margin:32px 0 12px;text-indent:0;page-break-after:avoid;}
h3{font-size:15px;font-weight:600;color:#1a3a5c;line-height:1.6;margin:20px 0 8px;text-indent:0;page-break-after:avoid;}
```

### 正文

```css
body{font-family:"Microsoft YaHei","PingFang SC","Hiragino Sans GB",sans-serif;background:#f5f3f0;color:#2c2c2c;}
p{font-size:15px;line-height:1.8;margin:0 0 12px;text-align:justify;text-indent:0;}
```

数字与英文用 `font-family:"Segoe UI","Microsoft YaHei",sans-serif`，通过 `.num-block` 或 `font-variant-numeric:tabular-nums` 让表格数字对齐。表格里的数字统一加 `tabular-nums`，否则位数不齐很难读。

### 表格

```css
table{width:100%;border-collapse:collapse;font-size:14px;margin:16px 0;border-radius:8px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.04);}
thead th{background:#1a3a5c;color:#fff;font-size:13px;font-weight:600;padding:12px 14px;text-align:left;}
tbody td{padding:11px 14px;border-bottom:1px solid #efece7;vertical-align:top;}
tbody tr:nth-child(even){background:#faf9f7;}
tbody td.n{text-align:right;font-variant-numeric:tabular-nums;}
```

`border-radius` 配 `overflow:hidden` 在打印时会裁剪跨页内容。表格外层不要包 `overflow:auto` 的容器，长表格让它自然跨页，用 `thead{display:table-header-group}` 重复表头。

### 卡片与区块

```css
.card{background:#fff;border-radius:10px;padding:24px 28px;margin:20px 0;box-shadow:0 1px 4px rgba(0,0,0,.04);border-left:4px solid #c5a572;}
.card.high{border-left-color:#c0392b;}
.card.mid{border-left-color:#e67e22;}
.card.low{border-left-color:#27ae60;}
.card.h{font-size:15px;font-weight:600;color:#1a3a5c;margin:0 0 10px;}
```

### 页面

```css
.wrap{max-width:960px;margin:0 auto;padding:0 24px;}
body{padding:32px 0;}
```

## 四、字数分配

全文 8000-15000 字。信息量大的项目取上限，早期项目可取下限。价值分析与风险分析合计不低于 50%，这是硬指标。

| 章节 | 字数 |
|---|---|
| 执行摘要 | ≤500 |
| 交易标的概况 | 600-900 |
| 市场与产业链 | 1800-2800 |
| 技术与产品 | 1500-2500 |
| 商业模式 | 1200-2000 |
| 财务诊断 | 1500-2500 |
| 团队与组织 | 800-1200 |
| 差异化优势 | 600-900 |
| 风险登记表 | 1500-2500 |
| 空头论证 | 800-1200 |
| 估值与交易结构 | 1500-2500 |
| 投后监控 | 400-600 |

问题清单、信息缺口、来源台账、免责声明不计入正文字数。

执行摘要只放判断与逻辑：这个项目是什么、为什么值得或不值得投、最大的三个变量是什么、结论在什么条件下会翻转。不出现具体财务数字，不出现表格。

## 五、打印适配

### 关键坑：`break-inside:avoid` 会吞内容

Chrome 打印时，若一个设了 `break-inside:avoid` 的元素高度超过一页版心，它不会分页，而是整块压在一页并裁掉溢出部分，PDF 里表现为"后半章节凭空消失"。图表容器、风险卡片、长表格都容易中招。

解决方式：导出前按实际高度动态放开限制。

```javascript
(function(){
  function fixPrintBreaks(){
    var mm2px = 96/25.4, pageH = 265*mm2px, safe = pageH*0.92;  // A4 版心高 265mm
    var fixed = 0, list = document.querySelectorAll('.chart-container,.card,.kpi,table,section,div');
    for (var i=0;i<list.length;i++){
      var el = list[i], cs = getComputedStyle(el);
      var avoid = cs.breakInside === 'avoid' || cs.pageBreakInside === 'avoid';
      if (avoid && el.getBoundingClientRect().height > safe){
        el.style.breakInside = 'auto';
        el.style.pageBreakInside = 'auto';
        fixed++;
      }
    }
    return {pageH: Math.round(pageH), fixed: fixed};
  }
  window.fixPrintBreaks = fixPrintBreaks;
  window.addEventListener('beforeprint', fixPrintBreaks);
})();
```

### 打印样式

```css
@page{ size:A4; margin:16mm 13mm; }

@media print{
  body{ background:#fff; padding:0; }
  .wrap{ max-width:none; padding:0; }
  .chart-container{ height:340px !important; break-inside:avoid; page-break-inside:avoid; box-shadow:none; border:1px solid #efece7; }
  .chart-container,.card,table,section,div{ overflow:visible !important; }
  table{ break-inside:auto; page-break-inside:auto; }
  thead{ display:table-header-group; }
  tr{ break-inside:avoid; page-break-inside:avoid; }
  h1.sec,h2,h3{ break-after:avoid; page-break-after:avoid; }
  .no-print{ display:none; }
  a{ color:#1a3a5c; text-decoration:none; }
}
```

`height:340px !important` 必须锁死，否则 canvas 在打印时塌缩成空白。

### 导出 PDF

用 puppeteer-core 驱动本机浏览器。不要用 `--print-to-pdf` 命令行，本机 Edge 以管理员权限运行时会静默失败、PDF 不落盘。

**浏览器选择有坑**：本机以管理员权限运行时，Edge 与 chrome 的 headless 启动都会报 `Failed to launch the browser process`，加 `--no-sandbox`、`--disable-gpu` 均无效。可行的做法是用 puppeteer 缓存里的 `chrome-headless-shell`，并用 `headless: 'shell'` 模式：

```javascript
const browser = await puppeteer.launch({
  executablePath: 'C:/Users/<用户>/.cache/puppeteer/chrome-headless-shell/<版本>/chrome-headless-shell-win64/chrome-headless-shell.exe',
  headless: 'shell',
  args: ['--no-sandbox','--disable-setuid-sandbox','--disable-gpu','--disable-dev-shm-usage',
         '--allow-file-access-from-files','--no-first-run','--no-default-browser-check']
});
```

`scripts/render_check.js` 已内置浏览器自动探测（环境变量 `REPORT_BROWSER` 可覆盖），优先 headless-shell，其次 chrome，最后系统 Edge。用法：

```bash
NODE_PATH="<node_modules>" node scripts/render_check.js 报告.html 报告.pdf
```

脚本会输出图表出图数量、表格与表题是否配对、有无脚本错误、PDF 页数与 MediaBox，末行 `verdict` 为 `PASS` 才算通过。

若要自己写导出脚本，关键步骤是这三段：

```javascript
// 1. 等所有 canvas 渲染完成，否则图表是空白
await page.waitForFunction(function(){
  return Array.prototype.every.call(
    document.querySelectorAll('.chart canvas'),
    function(cv){ return cv.width > 10; });
}, {timeout:60000, polling:500});
await new Promise(r => setTimeout(r, 4000));

// 2. 切打印媒体，并把视口设成 A4 版心，让 ECharts 按纸宽重排
await page.emulateMediaType('print');
await page.setViewport({width: Math.round(184*96/25.4), height: Math.round(265*96/25.4), deviceScaleFactor: 2});
await page.evaluate(() => window.dispatchEvent(new Event('resize')));
await new Promise(r => setTimeout(r, 3000));
await page.evaluate(() => window.fixPrintBreaks());
await new Promise(r => setTimeout(r, 1500));

// 3. 导出
await page.pdf({path: OUT, format:'A4', printBackground:true, preferCSSPageSize:true,
                margin:{top:'16mm',right:'13mm',bottom:'16mm',left:'13mm'}, timeout:180000});
```

A4 版心宽度 = 210 - 13×2 = 184mm，高度 = 297 - 16×2 = 265mm。视口必须按这个尺寸设，否则量出的元素高度偏小，`fixPrintBreaks` 判断失效。

### 交付前校验

1. `node --check` 检查内联脚本语法。每次改动图表代码后都要重跑，少一个闭括号会让整段脚本中断，表现为十张图全白，而 HTML 本身看起来毫无异常。
2. 每个图表画布的 id 都有对应的 `mount()` 调用，一一比对，不能有孤儿容器。
3. 用 `page.on('pageerror')` 收运行时错误，应为 0。
4. 页数只作参考，不作判据。实测同一份报告 `ceil(body.scrollHeight / 版心高)` 会比实际页数高 10%-15%（打印态字号变化、页边距合并、分页留白都会影响），按这个比值判断截断会产生假阳性，浪费时间。可靠的判法是第 5 条。
5. 用 pypdf 抽取全文文本，逐个确认末章标题、落款单位、免责声明都在。中文常有字间空格，比对前先 `replace(' ','')`，关键词用短词。
6. 抽查一页图表密集区与一页长表格，确认图例、坐标轴标签、表头没有被裁切。
