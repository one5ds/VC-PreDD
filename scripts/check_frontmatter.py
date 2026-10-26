#!/usr/bin/env python3
"""校验 SKILL.md frontmatter 是否满足平台索引要求。

用法：
    python scripts/check_frontmatter.py [SKILL.md 路径]

退出码 0 表示通过，1 表示存在缺失或格式问题。
"""

import re
import sys

REQUIRED = ["name", "description", "display_name", "display_name_en", "description_zh"]
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def load_frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = FM_RE.match(text)
    if not m:
        raise SystemExit("SKILL.md: 未找到 YAML frontmatter（须以 --- 开始）")
    fm = m.group(1)
    data = {}
    for line in fm.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip()
    return data


def main(argv):
    path = argv[1] if len(argv) > 1 else "SKILL.md"
    data = load_frontmatter(path)

    problems = []
    for key in REQUIRED:
        if not data.get(key):
            problems.append("缺少字段：%s" % key)

    name = data.get("name", "")
    if name and not NAME_RE.match(name):
        problems.append("name 须为小写连字符格式：%s" % name)

    for key in ("description", "description_zh", "description_en"):
        value = data.get(key, "")
        if "<" in value or ">" in value:
            problems.append("%s 不能包含尖括号" % key)
        if len(value) > 1024:
            problems.append("%s 超过 1024 字符（当前 %d）" % (key, len(value)))

    if problems:
        for p in problems:
            print("[失败] %s" % p)
        return 1

    print("[通过] frontmatter 完整：%s" % name)
    for key in REQUIRED:
        print("       %-18s %d 字符" % (key, len(data[key])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
