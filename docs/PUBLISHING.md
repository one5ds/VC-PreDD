# 发布到 GitHub 的操作清单

[English](#english-checklist) | [简体中文](#中文清单)

本文件集中放好创建仓库时需要填写的全部文案，中英双版，直接复制即可。

---

## 中文清单

### 1. 仓库基本信息

**仓库名**

```
vc-dd-360-report
```

**About 描述（中文，建议优先用英文版放 About，中文放 README）**

```
一级市场 360 度投研尽调报告生成器：BP 进，投决会可用的 HTML 报告出，含 100 分记分卡、风险雷达、估值与交易结构、尽调问题清单与信息缺口台账。
```

**About 描述（英文，GitHub About 栏位建议填这条）**

```
Turn a pitch deck into an IC-ready due diligence report: single-file HTML with 10 ECharts, a 100-point scorecard, risk radar, valuation and deal structure, plus a DD question list and information-gap register.
```

**Website**

```
https://github.com/AIOpenVC
```

### 2. Topics（话题标签）

GitHub 最多 20 个，按优先级：

```
venture-capital  due-diligence  investment-research  china  private-equity
investment-thesis  pitch-deck  financial-analysis  valuation  risk-assessment
echarts  html-report  skill  ai-agent  claude-skill
prompt-engineering  startup-analysis  term-sheet  ic-memo  report-generation
```

### 3. 首次发布 Release

**Tag**

```
v1.0.0
```

**Release 标题**

```
v1.0.0 · 首个公开版本
```

**Release 说明（中文）**

```markdown
首个公开版本，覆盖从 BP 到投决会报告的全流程。

## 包含内容

- 七阶段工作流，受理阶段为阻断式闸门，材料不足时改出《材料需求清单》
- 六维 100 分记分卡，含固定权重锚点与一票否决清单
- 十七章节报告骨架，覆盖市场、技术、商业、财务、团队、风险、空头论证、估值条款、投后监控
- 打印就绪的单文件 HTML 模板，10 张 ECharts 图表，A4 直出 18 页
- 五份参考文件：材料受理、分析模块、财务估值、评分风险、图表排版
- 四个自检脚本：前置信息、文本审计、内联脚本语法、渲染审计

## 已验证

模板通过全部自检：17 章、21 表 21 题、10 图出图、零脚本错误、PDF 18 页。

## 已知限制

桌面研究性质，不替代法律、财务、技术尽调。估值区间为敏感性区间，非价格发现。详见 README 的局限一节。
```

**Release 说明（英文）**

```markdown
First public release. Covers the full path from pitch deck to investment committee report.

## What is included

- Seven-stage workflow with a blocking intake gate that returns a materials request list when sources are insufficient
- Six-dimension 100-point scorecard with fixed weight anchors and a hard-stop veto list
- Seventeen-chapter report skeleton covering market, technology, business model, financials, team, risk, bear case, valuation and terms, post-investment monitoring
- Print-ready single-file HTML template with 10 ECharts charts, paginates to 18 A4 pages
- Five reference documents: intake and evidence, analysis modules, finance and valuation, scoring and risk, charts and layout
- Four check scripts: frontmatter, text audit, inline script syntax, render audit

## Verified

The template passes all checks: 17 sections, 21 tables with 21 captions, 10 charts painted, zero script errors, 18 PDF pages.

## Known limitations

Desk research. Does not replace legal, financial or technical due diligence. Valuation ranges are sensitivity ranges, not price discovery. See the Limitations section of the README.
```

### 4. 社区文件与社交预览

- **Social preview 图**：用 `docs/images/01-cover.png` 上传到 Settings → Social preview，尺寸 1280×640 效果最佳，建议单独做一张带项目名的图。
- **仓库描述旁的许可证**：选择 MIT，GitHub 会自动识别 `LICENSE`。
- **Discussions**：可选开启，适合收集各行业锚点校准意见。
- **Issue 模板**：可选，建议至少提供「锚点校准」与「图表需求」两类。

### 5. 推送命令

```bash
cd dist/repo/vc-dd-360-report

git init
git branch -M main
git add .
git commit -m "feat: initial release of vc-dd-360-report skill"
git remote add origin https://github.com/<your-org>/vc-dd-360-report.git
git push -u origin main
```

发布 release 前，先打标签再推送：

```bash
git tag -a v1.0.0 -m "v1.0.0 首个公开版本"
git push origin v1.0.0
```

在 GitHub 页面选择该标签创建 Release，把上面的说明贴进去。

### 6. 发布前自查

- [ ] `python scripts/check_frontmatter.py SKILL.md` 通过
- [ ] `python scripts/check_report.py assets/report-template.html --template` 通过
- [ ] 七张截图都在 `docs/images/`，README 中引用的路径正确
- [ ] `LICENSE` 中的版权主体是你要的主体
- [ ] README 里的 `git clone` 地址已替换为真实组织名
- [ ] 演示数据说明保留在 README（截图使用虚构项目）
- [ ] 确认仓库中没有任何真实项目材料、客户名单或未公开数据

---

## English checklist

### 1. Repository basics

**Name**

```
vc-dd-360-report
```

**About**

```
Turn a pitch deck into an IC-ready due diligence report: single-file HTML with 10 ECharts, a 100-point scorecard, risk radar, valuation and deal structure, plus a DD question list and information-gap register.
```

**Topics**

```
venture-capital  due-diligence  investment-research  china  private-equity
investment-thesis  pitch-deck  financial-analysis  valuation  risk-assessment
echarts  html-report  skill  ai-agent  claude-skill
prompt-engineering  startup-analysis  term-sheet  ic-memo  report-generation
```

### 2. First release

Tag `v1.0.0`, title `v1.0.0 · First public release`. Use the English release notes above.

### 3. Social preview

Upload `docs/images/01-cover.png` under Settings → Social preview. Ideally produce a dedicated 1280×640 image with the project name.

### 4. Push

```bash
cd dist/repo/vc-dd-360-report

git init
git branch -M main
git add .
git commit -m "feat: initial release of vc-dd-360-report skill"
git remote add origin https://github.com/<your-org>/vc-dd-360-report.git
git push -u origin main

git tag -a v1.0.0 -m "v1.0.0 First public release"
git push origin v1.0.0
```

### 5. Pre-publish checklist

- [ ] `python scripts/check_frontmatter.py SKILL.md` passes
- [ ] `python scripts/check_report.py assets/report-template.html --template` passes
- [ ] All seven screenshots exist in `docs/images/` and README paths resolve
- [ ] Copyright holder in `LICENSE` is the entity you want
- [ ] Placeholder `<your-org>` in README clone URLs replaced with the real organisation
- [ ] Demo-data disclaimer retained in the README
- [ ] No real deal materials, client lists or non-public data anywhere in the repository
