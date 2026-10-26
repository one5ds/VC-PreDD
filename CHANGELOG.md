# Changelog

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows
[Semantic Versioning](https://semver.org/).

本文件记录技能的所有重要变更。格式遵循 Keep a Changelog，版本号遵循语义化版本。

---

## [1.0.0] - 2026-10-26

### Added

- Seven-stage workflow from material intake to delivery, with a blocking intake gate that returns a materials request list when the source material cannot support a report.
- Five evidence rules enforced in the procedure: sourced figures, four fact classes, risk resolution paths, falsifiable conclusions, structured gap register.
- Six-dimension 100-point scorecard with fixed weight anchors, grade bands, and a hard-stop override list.
- Seventeen-chapter report skeleton covering market, technology, business model, financials, team, risk, bear case, valuation, deal terms, monitoring and gaps.
- `assets/report-template.html`: print-ready single-file skeleton with 10 ECharts charts, cover, scorecard block, risk cards, footer, and a `fixPrintBreaks` routine that prevents A4 page-break truncation.
- Five reference documents covering intake and evidence, analysis modules, finance and valuation, scoring and risk, charts and layout.
- `scripts/check_report.py`: text-level audit for orphan source tags, shareholding sum, banned phrasing, word-count distribution and chart pairing. Includes `--template` mode.
- `scripts/render_check.js`: headless render audit for painted canvases, page errors, table overflow, page count and MediaBox, with optional PDF export.
- Bilingual documentation: `README.md` (English), `README.zh-CN.md` (Simplified Chinese).
- GitHub Actions workflow validating frontmatter, Python syntax and template self-check on every push.

### Changed

- Attribution in the report footer and disclaimer set to `AIOpenVC 投研中心`.
- Platform metadata added to frontmatter: `display_name`, `display_name_en`, `description_zh`.

### Fixed

- ECharts canvas overflow: chart initialisation moved from the padded `.chart-container` to an inner `div.chart`, which previously clipped legends in PDF export while looking correct in the browser.
- `check_report.py` failed to detect chart containers after the above restructure; the matcher now accepts both the container and the inner canvas layer.
- Template self-check reported a blocking error at skeleton stage; unresolved placeholders are now downgraded to a notice under `--template`.
- Print stylesheet corrected: `page-break-inside` syntax, and `break-inside: avoid` narrowed so Chrome stops clipping oversized elements instead of paginating them.

---

## 版本说明（中文）

### 新增

- 七阶段工作流，含阻断式受理闸门：材料不足时改出《材料需求清单》，不硬写报告。
- 五条证据纪律：无来源不落数、四类事实分级、风险必带解决路径、结论可反驳、缺口结构化登记。
- 六维 100 分记分卡，含固定权重锚点、评级档位与一票否决清单。
- 十七章节报告骨架，覆盖市场、技术、商业模式、财务、团队、风险、空头论证、估值、条款、投后监控与信息缺口。
- 打印就绪的单文件 HTML 模板，含 10 张 ECharts 图表与 `fixPrintBreaks` 防截断脚本。
- 五份参考文件，分别覆盖材料受理、分析模块、财务估值、评分风险、图表排版。
- 两个自检脚本：文本层审计与渲染审计，后者可顺带导出 PDF。
- 中英双语文档与 GitHub Actions 自动校验。

### 修复

- 图表画布溢出导致 PDF 中图例被裁。
- 图表容器识别失效、模板阶段自检误报阻断。
- 打印分页样式语法错误与超高元素被裁切问题。
