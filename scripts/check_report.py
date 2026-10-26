#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投研报告成稿自检。

用法:
    python check_report.py 报告.html [--json]

检查项:
    1. 占位符残留 {{ }}
    2. 来源编号孤儿（正文引用但台账缺失）与台账冗余
    3. 持股比例合计是否为 100
    4. 禁用措辞（em dash / 不是…而是 / 有望 / 赋能 / 闭环 / 打通）
    5. 各章节字数分布，价值+风险占比是否达 50%
    6. 图表容器与初始化调用是否一一对应，图表是否带数据来源注
    7. 表格是否缺 caption
    8. 数字精度粗查（亿元口径混用）

退出码 0 表示无阻断级问题，1 表示存在阻断级问题。
"""
import argparse
import json
import os
import re
import sys

BLOCK, WARN, INFO = "阻断", "警告", "提示"

TAG_RE = re.compile(r"<[^>]+>")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
PLACEHOLDER_RE = re.compile(r"\{\{[^}]*\}\}")
SRC_REF_RE = re.compile(r"\[(S\d+)\]")
CHART_DIV_RE = re.compile(
    r'<div(?=[^>]*\bid="(c\d+)")(?=[^>]*\bclass="[^"]*chart)[^>]*>', re.I)
MOUNT_RE = re.compile(r"mount\(\s*['\"](c\d+)['\"]")

FORBIDDEN = [
    ("——", "em dash", BLOCK),
    ("有望", "模糊预期措辞", WARN),
    ("或将", "模糊预期措辞", WARN),
    ("赋能", "无信息量词", WARN),
    ("闭环", "无信息量词", WARN),
    ("打通", "无信息量词", WARN),
    ("凭经验", "无来源估计", BLOCK),
    ("预计将大幅", "无信息量措辞", WARN),
    ("积极观望", "模糊结论", BLOCK),
    ("谨慎推荐", "模糊结论", BLOCK),
]

VALUE_SECTIONS = ["市场与产业链", "技术与产品", "商业模式", "差异化", "估值", "财务诊断"]
RISK_SECTIONS = ["风险", "空头论证"]


def strip_tags(html):
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    return TAG_RE.sub(" ", text)


def count_cjk(text):
    return len(CJK_RE.findall(text))


def split_sections(html):
    """按 h1.sec 切分章节，返回 [(标题, 内容)]。"""
    parts = re.split(r'<h1[^>]*class="[^"]*sec[^"]*"[^>]*>([\s\S]*?)</h1>', html, flags=re.I)
    if len(parts) < 3:
        return []
    out = [("（封面及摘要前）", parts[0])]
    for i in range(1, len(parts), 2):
        title = TAG_RE.sub("", parts[i])
        title = re.sub(r"^\s*\d+\s*", "", title).strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        out.append((title or "未命名章节", body))
    return out


def find_ledger_sources(html):
    """从来源台账表格中提取 S 编号。"""
    m = re.search(r"来源台账([\s\S]*?)(?:免责声明|<div class=\"disclaimer\"|$)", html)
    scope = m.group(1) if m else html
    ids = set(re.findall(r"<td>\s*(S\d+)\s*</td>", scope))
    if not ids:
        ids = set(re.findall(r"<td[^>]*>\s*(S\d+)\s*</td>", scope))
    return ids


def check_shareholding(html):
    """检查含'持股比例'的表内百分比合计。"""
    issues = []
    for tbl in re.findall(r"<table[\s\S]*?</table>", html, flags=re.I):
        if "持股比例" not in tbl and "股比" not in tbl:
            continue
        pcts = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*%", tbl)]
        if not pcts:
            continue
        total = sum(pcts)
        if 99.5 <= total <= 101.5:
            issues.append((INFO, "持股比例合计 %.2f%%，校验通过" % total))
        elif total > 101.5:
            issues.append((BLOCK, "持股比例合计 %.2f%%，超过 100%%，疑似重复披露或含非股比数据" % total))
        else:
            issues.append((WARN, "持股比例合计 %.2f%%，不足 100%%，请检查是否有股东遗漏" % total))
    return issues


def check_charts(html, findings):
    ids = set(CHART_DIV_RE.findall(html))
    mounts = set(MOUNT_RE.findall(html))
    if not ids:
        findings.append((WARN, "未发现图表容器，确认是否需要配图"))
        return
    orphan_div = ids - mounts
    orphan_mount = mounts - ids
    if orphan_div:
        findings.append((BLOCK, "图表容器无初始化调用：%s" % ", ".join(sorted(orphan_div))))
    if orphan_mount:
        findings.append((BLOCK, "初始化调用无对应容器：%s" % ", ".join(sorted(orphan_mount))))
    if not orphan_div and not orphan_mount:
        findings.append((INFO, "图表容器与初始化调用一一对应，共 %d 张" % len(ids)))

    # 图表是否带数据来源注
    blocks = re.findall(r'<div[^>]*class="[^"]*chart-container[^"]*"[\s\S]*?(?=<div[^>]*class="[^"]*chart-container|<h1|<h2|<table)', html)
    missing = 0
    for b in blocks:
        if "chart-note" not in b:
            missing += 1
    if missing:
        findings.append((WARN, "%d 张图表缺少 chart-note 数据来源注" % missing))
    else:
        findings.append((INFO, "全部图表均附数据来源注"))


def check_tables(html, findings):
    tables = re.findall(r"<table[\s\S]*?</table>", html, flags=re.I)
    no_caption = len([t for t in tables if "<caption" not in t])
    if no_caption:
        findings.append((WARN, "%d / %d 张表格缺 caption 表题" % (no_caption, len(tables))))
    else:
        findings.append((INFO, "全部表格均有 caption"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--template", action="store_true",
                    help="模板模式：未替换的 {{占位符}} 视为待填项（提示），不判阻断")
    args = ap.parse_args()

    if not os.path.isfile(args.path):
        print("文件不存在：%s" % args.path)
        return 1

    with open(args.path, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    findings = []

    # 1 占位符
    ph = PLACEHOLDER_RE.findall(html)
    if ph and args.template:
        findings.append((INFO, "模板模式：待填占位符 %d 处，例：%s" % (len(ph), ph[:3])))
    elif ph:
        findings.append((BLOCK, "占位符未替换 %d 处，例：%s" % (len(ph), ph[:3])))
    else:
        findings.append((INFO, "无占位符残留"))

    # 2 来源
    ledger = find_ledger_sources(html)
    refs = set(SRC_REF_RE.findall(html))
    body_refs = set()
    for m in re.finditer(r"<span class=\"src\">\[(S\d+)\]</span>", html):
        body_refs.add(m.group(1))
    orphan = body_refs - ledger
    unused = ledger - body_refs
    if orphan:
        findings.append((BLOCK, "正文引用了台账中不存在的来源：%s" % ", ".join(sorted(orphan))))
    if unused:
        findings.append((WARN, "台账中登记但正文未引用的来源：%s" % ", ".join(sorted(unused))))
    if body_refs and not orphan:
        findings.append((INFO, "来源编号全部可追溯，正文引用 %d 个、台账登记 %d 个" % (len(body_refs), len(ledger))))
    if not body_refs:
        findings.append((BLOCK, "正文未发现任何来源标注，违反'无来源不落数'"))

    # 3 持股
    findings.extend(check_shareholding(html))

    # 4 禁用措辞
    text = strip_tags(html)
    for token, desc, level in FORBIDDEN:
        n = text.count(token)
        if n:
            findings.append((level, "命中「%s」%d 次（%s）" % (token, n, desc)))

    # 4b 破折号与句式：用正则避开表格里的 "—" 占位符
    dash = re.findall(r"[\u4e00-\u9fff][ \t]*—{1,2}[ \t]*[\u4e00-\u9fff]", text)
    if dash:
        sample = dash[0].replace(" ", "").replace("\n", "")
        findings.append((BLOCK, "正文出现 %d 处破折号连接中文，例：%s" % (len(dash), sample)))
    contra = re.findall(r"不是[\s\S]{0,40}?而是", text)
    if contra:
        findings.append((WARN, "出现 %d 处'不是…而是'句式" % len(contra)))

    # 5 字数
    sections = split_sections(html)
    total = count_cjk(text)
    findings.append((INFO, "全文中文字符数 %d" % total))
    if total < 3000:
        findings.append((BLOCK, "全文不足 3000 字，篇幅不达最低要求"))
    elif total < 8000:
        findings.append((WARN, "全文 %d 字，低于建议区间 8000-15000" % total))

    value_chars = 0
    risk_chars = 0
    dist = []
    for title, body in sections:
        n = count_cjk(strip_tags(body))
        if n:
            dist.append((title, n))
        if any(k in title for k in VALUE_SECTIONS):
            value_chars += n
        if any(k in title for k in RISK_SECTIONS):
            risk_chars += n
    if total:
        ratio = (value_chars + risk_chars) / float(total)
        msg = "价值+风险章节占比 %.1f%%（价值 %d 字 / 风险 %d 字）" % (ratio * 100, value_chars, risk_chars)
        if ratio < 0.5:
            findings.append((BLOCK, msg + "，低于 50% 硬指标"))
        else:
            findings.append((INFO, msg))

    # 6 图表
    check_charts(html, findings)

    # 7 表格
    check_tables(html, findings)

    # 8 口径混用
    if re.search(r"\d+(?:\.\d+)?\s*亿元", text) and re.search(r"单位[：:]\s*万元", text):
        findings.append((WARN, "正文同时出现'亿元'与'万元'口径，确认是否已统一换算并标注"))

    # 输出
    order = {BLOCK: 0, WARN: 1, INFO: 2}
    findings.sort(key=lambda x: order[x[0]])
    blocked = [f for f in findings if f[0] == BLOCK]

    if args.json:
        print(json.dumps({
            "file": args.path,
            "chars": total,
            "distribution": dist,
            "findings": [{"level": l, "msg": m} for l, m in findings],
            "blocked": len(blocked)
        }, ensure_ascii=False, indent=2))
    else:
        print("=" * 62)
        print("投研报告自检  %s" % os.path.basename(args.path))
        print("=" * 62)
        for level, msg in findings:
            mark = {BLOCK: "[阻断]", WARN: "[警告]", INFO: "[通过]"}[level]
            print("%s %s" % (mark, msg))
        if dist:
            print("-" * 62)
            print("章节字数分布：")
            for title, n in dist:
                bar = "█" * max(1, int(n / max(total, 1) * 40))
                print("  %-18s %6d  %s" % (title[:18], n, bar))
        print("-" * 62)
        print("结论：%s" % ("存在 %d 项阻断问题，须修复后再交付" % len(blocked) if blocked else "通过，可交付"))

    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
