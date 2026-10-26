# Contributing

[English](#english) | [简体中文](#简体中文)

---

## English

### What is worth contributing

Three kinds of changes genuinely improve this skill:

1. **Sector calibration.** The scoring anchors are tuned for hard tech and enterprise software. If you work in biotech, consumer or fintech, the anchors in `references/04-scoring-and-risk.md` will misjudge your deals. Propose sector-specific anchor tables rather than changing the general ones.
2. **New chart recipes.** If you have a chart that carries analysis the current ten cannot, add it to `references/05-charts-and-layout.md` with a working ECharts config. Every new chart needs a stated purpose and the question it answers.
3. **Checker rules.** Any failure mode you hit twice should become a rule in `scripts/check_report.py`. Evidence discipline that depends on memory fails at scale.

Documentation fixes, typo corrections and better examples are welcome too.

### What will be declined

- Rewriting the template's CSS, font sizes or spacing. The A4 pagination was tuned against actual rendering, and cosmetic changes silently break print output.
- Adding charts that duplicate an existing one with different styling.
- Loosening the evidence rules, for example allowing unsourced figures "when data is hard to obtain". That is the exact failure this skill exists to prevent.
- Vendor-specific branding in the core files.

### Required checks

Three checks must pass before a pull request is reviewed.

```bash
# 1. Frontmatter must carry all indexing fields
python scripts/check_frontmatter.py SKILL.md

# 2. Template must pass the self-check in template mode
python scripts/check_report.py assets/report-template.html --template

# 3. Inline report script must parse
python scripts/check_inline_js.py assets/report-template.html /tmp/report_inline.js
node --check /tmp/report_inline.js
```

All three run in CI on every pull request, so a green local run and a green check are the same thing.

If your change touches the template or the charts, also run the render audit and confirm `verdict: PASS`:

```bash
NODE_PATH=<path-to-node_modules> node scripts/render_check.js assets/report-template.html /tmp/out.pdf
```

### Style rules for generated content

These apply to anything that ends up in a produced report:

- No em dash. Use a comma, colon or full stop.
- No vague hedges such as "is expected to grow significantly". Give a number or delete the sentence.
- Every figure carries a source tag `[Sn]` and appears in the source ledger.
- Risk entries carry five fields: description, quantified impact, probability, resolution path, residual risk.
- Financial figures keep original precision. Amounts in CNY ten-thousand units keep two decimals.

### Commit messages

Conventional Commits format, one logical change per commit:

```
feat(charts): add supply-chain concentration chart
fix(checker): detect chart containers after template restructure
docs(readme): correct install path for Windows
```

---

## 简体中文

### 值得贡献的改动

三类改动能真正提升这个技能：

1. **行业锚点校准。** 现有评分锚点按硬科技与企业服务调过。如果你做生物医药、消费或金融科技，`references/04-scoring-and-risk.md` 里的锚点会误判你的项目。请提交行业专属的锚点表，不要改动通用锚点。
2. **新增图表配方。** 如果你有一张图能承载现有十张图承载不了的分析，把它加进 `references/05-charts-and-layout.md`，附可用的 ECharts 配置。每张新图都要写明它回答什么问题。
3. **检查规则。** 同一个坑踩到第二次，就应该变成 `scripts/check_report.py` 里的一条规则。靠记忆维持的证据纪律，规模一大必然失守。

文档纠错、示例补充同样欢迎。

### 不接受的改动

- 重写模板的 CSS、字号或间距。A4 分页是按实际渲染调出来的，任何看起来无害的样式改动都可能悄悄破坏打印效果。
- 新增与现有图表重复、只是换了配色的图。
- 放松证据纪律，例如允许「数据难获取时可不标来源」。这正是本技能要防的事。
- 在核心文件里植入特定厂商的品牌信息。

### 必须通过的检查

三项检查都通过才会进入评审。

```bash
# 1. frontmatter 必须包含全部索引字段
python scripts/check_frontmatter.py SKILL.md

# 2. 模板必须在模板模式下通过自检
python scripts/check_report.py assets/report-template.html --template

# 3. 报告内联脚本必须能被解析
python scripts/check_inline_js.py assets/report-template.html /tmp/report_inline.js
node --check /tmp/report_inline.js
```

三项检查在每次 PR 时由 CI 自动执行，本地通过等同线上通过。

改动涉及模板或图表时，再跑一次渲染审计，确认输出 `verdict: PASS`：

```bash
NODE_PATH=<node_modules 路径> node scripts/render_check.js assets/report-template.html /tmp/out.pdf
```

### 生成内容的文字纪律

以下规则适用于任何进入报告的文本：

- 不使用破折号「——」，改用逗号、冒号或句号。
- 不使用「有望大幅增长」这类模糊预期，要么给数字，要么删掉这句话。
- 每个数字挂来源编号 `[Sn]`，并在来源台账中登记。
- 风险条目五要素齐全：描述、量化影响、触发概率、解决路径、残余风险。
- 财务数字保留原始精度，万元保留两位小数。

### 提交信息

遵循 Conventional Commits，一次提交只做一件逻辑上的事：

```
feat(charts): 新增供应链集中度图
fix(checker): 模板结构调整后图表容器识别失效
docs(readme): 修正 Windows 安装路径
```
