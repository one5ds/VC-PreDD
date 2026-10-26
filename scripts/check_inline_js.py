#!/usr/bin/env python3
"""抽取报告 HTML 中的内联脚本，供 node --check 做语法校验。

图表全部由内联脚本初始化，一旦有语法错误，整份报告的十张图会同时空白，
而浏览器控制台之外的任何检查都发现不了。故单独成步。

用法：
    python scripts/check_inline_js.py [报告.html] [输出.js]
默认输出到 /tmp/report_inline.js。仅抽取，不执行。
"""

import pathlib
import re
import sys

SCRIPT_RE = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.DOTALL)


def main(argv):
    src = argv[1] if len(argv) > 1 else "assets/report-template.html"
    out = argv[2] if len(argv) > 2 else "/tmp/report_inline.js"

    html = pathlib.Path(src).read_text(encoding="utf-8")
    blocks = SCRIPT_RE.findall(html)
    if not blocks:
        print("[失败] 未找到内联脚本：%s" % src)
        return 1

    code = max(blocks, key=len)
    pathlib.Path(out).write_text(code, encoding="utf-8")
    print("[通过] 已抽取内联脚本 %d 字符 -> %s" % (len(code), out))
    print("       下一步：node --check %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
