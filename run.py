# -*- coding: utf-8 -*-
"""WeasyPrint 渲染：把 epub_to_html.py 生成的单文件 HTML + book.css → PDF。

用法:
    python run.py  输入.html  输出.pdf
    (例: python run.py 小岛经济学.html 小岛经济学.pdf)
"""
import os, sys
from weasyprint import HTML, CSS

if len(sys.argv) < 3:
    print('用法: python run.py  输入.html  输出.pdf')
    sys.exit(1)
html, out = sys.argv[1], sys.argv[2]
base = os.path.dirname(os.path.abspath(html))   # 以 html 所在目录为基准，图片/资源才能正确解析

# 自动找 book.css：按优先级（run.py 同目录 → html 同目录 → 当前目录 → weasyprint方案文件夹）
here = os.path.dirname(os.path.abspath(__file__))
candidates = [
    os.path.join(here, 'book.css'),
    os.path.join(base, 'book.css'),
    os.path.join(os.getcwd(), 'book.css'),
    r'C:\Users\ZhangXu\Desktop\weasyprint方案\book.css',
]
book_css = next((p for p in candidates if os.path.exists(p)), None)
if not book_css:
    print('找不到 book.css（请把它和 run.py 放同一文件夹）')
    sys.exit(1)

# 渲染：入参为 html 路径 + 首页目录基准目录，输出覆盖到 out
HTML(html, base_url=base).write_pdf(out, stylesheets=[CSS(book_css)])
print('完成 ->', out)
