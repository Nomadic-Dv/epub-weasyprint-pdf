# -*- coding: utf-8 -*-
"""
把 EPUB 转成一个“单文件 HTML”，供 WeasyPrint 渲染成 PDF。
纯 Python，不依赖 Calibre。

流程:
  1. 解出整包(图片/字体/CSS/正文)到 work_dir，保留目录结构
  2. 按 spine 顺序合并正文；把每个源 xhtml 内容块包进 <div class="epub-block">，
     并把 <img src> 改成相对 html 的路径
  3. 内联合并 CSS，修正 url(...) 路径
  4. 取书名(dc:title，取不到用文件名)，生成隐藏的书名标记
  5. 给标题加锚点 / 生成目录(TOC) / 给正文第一个一级标题加 page-one
  6. 拆成“前置页(frontmatter)” + “正文(maincontent)”，写出单文件 HTML

用法:
  python epub_to_html.py  输入.epub  输出.html  工作目录
"""
import os, sys, re, zipfile
from xml.etree import ElementTree as ET

OPF_NS = 'http://www.idpf.org/2007/opf'
DC_NS  = 'http://purl.org/dc/elements/1.1/'


def norm(base, rel):
    return os.path.normpath(os.path.join(base, rel.replace('/', os.sep)))


def fpath(p):
    return p.replace(os.sep, '/')


def external(u):
    return (not u) or u.startswith(('data:', 'http', 'https', 'file:', '//', '#'))


def main(epub, out_html, work_dir):
    work_dir = os.path.abspath(work_dir)
    html_dir = os.path.dirname(os.path.abspath(out_html))  # 资源相对 html 所在目录
    os.makedirs(work_dir, exist_ok=True)
    z = zipfile.ZipFile(epub)
    names = z.namelist()
    opf = [n for n in names if n.lower().endswith('.opf')][0]
    opf_dir = os.path.dirname(opf)  # 可能是 '' 或 'OEBPS'

    root = ET.fromstring(z.read(opf))
    items = list(root.iter('{%s}item' % OPF_NS))
    man = {it.get('id'): it.get('href') for it in items}
    spine = [r.get('idref') for r in root.iter('{%s}itemref' % OPF_NS)]
    # 目录 html：跳过源 EPUB 自带的目录页，避免跟自动生成的目录重复。
    # 识别两法(都会命中，且不会命中正文/图片)：
    #   1) EPUB3 规范 properties="nav" 的导航文档(toc.xhtml/nav.xhtml)
    #   2) 文件名/id 明确带目录词(如 x_TOC.xhtml, contents.html, 目录)的 xhtml
    # media-type 是 application/xhtml+xml，要匹配 'xhtml'(后缀其实是 +xml，不能 endswith('xhtml'))。
    _TOC_WORDS = ('toc', 'contents', 'directory', '目录')
    nav_ids = set()
    for it in items:
        props = it.get('properties') or ''
        mt = it.get('media-type') or ''
        if 'xhtml' not in mt:
            continue                       # 只对 xhtml 类正文判断；图片/字体/NCX 一律不动
        idh = ((it.get('id') or '') + '/' + (it.get('href') or '')).lower()
        if 'nav' in props.split() or any(w in idh for w in _TOC_WORDS):
            nav_ids.add(it.get('id'))
    css_hrefs = [it.get('href') for it in items if (it.get('media-type') or '').endswith('css')]

    # ---- 1) 解出整包到 work_dir，保留目录结构 ----
    for n in names:
        if n.endswith('/'):
            continue
        t = norm(work_dir, n)
        os.makedirs(os.path.dirname(t) or '.', exist_ok=True)
        with open(t, 'wb') as f:
            f.write(z.read(n))

    # ---- 2) 按 spine 顺序合并正文，并把 <img src> 改成相对 html 的路径 ----
    bodies = []
    for idref in spine:
        if idref in nav_ids:
            continue                      # 跳过源 EPUB 自带的目录 html(properties=nav)，避免跟自动目录重复
        href = man.get(idref)
        if not href:
            continue
        xh = fpath(norm(opf_dir, href))  # zip 内相对路径，如 text/part0000.html
        try:
            xhtml = z.read(xh).decode('utf-8', 'ignore')
        except Exception:
            continue
        m = re.search(r'<body[^>]*>(.*)</body>', xhtml, re.S)
        if not m:
            continue
        wd = os.path.dirname(norm(work_dir, xh)) or work_dir  # 该正文文件在 work_dir 下的目录

        def fix_img(mm):
            src = mm.group(2).strip('"\'')
            if external(src):
                return mm.group(0)
            rel = os.path.relpath(norm(wd, src), html_dir)  # 相对 html 目录
            return mm.group(1) + fpath(rel) + mm.group(3)

        body = re.sub(r'(?is)(<img[^>]*\ssrc=["\'])([^"\']+)(["\'])', fix_img, m.group(1))
        # 每个源 xhtml 内容块独立包一层 <div class="epub-block">，
        # 由 book.css 的 break-before:page 让“内容不足一页也独占一页、不跟下一块接排”。
        bodies.append('<div class="epub-block">' + body + '</div>')

    # ---- 3) 内联合并 CSS，并修正 url(...) 路径 ----
    css_all = []
    for chref in css_hrefs:
        cfull = fpath(norm(opf_dir, chref))
        try:
            ctxt = z.read(cfull).decode('utf-8', 'ignore')
        except Exception:
            continue
        cwd = os.path.dirname(norm(work_dir, cfull)) or work_dir

        def fix_url(mm):
            u = mm.group(1).strip('"\'')
            if external(u):
                return mm.group(0)
            rel = os.path.relpath(norm(cwd, u), html_dir)  # 相对 html 目录
            return 'url(%s)' % fpath(rel)

        css_all.append(re.sub(r'url\(([^)]+)\)', fix_url, ctxt))
    style = '<style>\n' + '\n'.join(css_all) + '\n</style>'

    # ---- 4) 书名：优先取 EPUB 元数据 dc:title，取不到再用文件名(去扩展名) ----
    import html as _html
    import re as _re
    title = None
    for t in root.iter('{%s}title' % DC_NS):
        if t.text and t.text.strip():
            title = t.text.strip()
            break
    if not title:
        title = os.path.splitext(os.path.basename(epub))[0]

    # 隐藏的书名标记：供 book.css 用 string(booktitle) 取偶数页页眉
    marker = '<div id="booktitle" style="visibility:hidden;height:0;overflow:hidden;">%s</div>' % _html.escape(title)

    # ---- 5) 给标题加锚点 & 生成目录 ----
    body_html = '\n'.join(bodies)

    toc = []
    chc = [0]; sec = [0]
    title_skipped = [False]
    first_content_id = [None]
    _norm = lambda s: _re.sub(r'\s+', '', s or '').replace('，', ',').replace('、', ',')

    def add_id(m):
        tag = m.group(1).lower()
        attrs = _re.sub(r'(?i)\s*id\s*=\s*["\'][^"\']*["\']', '', m.group(2))  # 去掉已有 id，避免重复
        inner = m.group(3)
        txt = _re.sub(r'<[^>]+>', '', inner).strip()
        txt = _html.unescape(txt)          # &#160; 等实体 → 正常字符
        if tag == 'h1':
            chc[0] += 1; aid = 'toc-ch-%d' % chc[0]
            if _norm(txt) == _norm(title) and not title_skipped[0]:
                title_skipped[0] = True    # 跳过第一个与书名相同的 h1(书名页)
            else:
                toc.append((1, aid, txt))  # 一级标题
                if first_content_id[0] is None:
                    first_content_id[0] = aid
                    # 给“目录后第一个一级标题”加 page-one 类（该页=1、页眉从这里开始）
                    if _re.search(r'(?i)\bclass\s*=', attrs):
                        attrs = _re.sub(r'(?i)(class\s*=\s*["\'][^"\']*)(["\'])', r'\1 page-one\2', attrs)
                    else:
                        attrs += ' class="page-one"'
        else:
            sec[0] += 1; aid = 'toc-sec-%d' % sec[0]
            toc.append((2, aid, txt))      # 二级标题(小节)，目录里缩进
        return '<%s id="%s"%s>%s</%s>' % (m.group(1), aid, attrs, inner, m.group(1))

    body_html = _re.sub(r'(?is)<(h[12])([^>]*)>(.*?)</\1>', add_id, body_html)

    # 目录 HTML（一级 + 二级，二级缩进）
    toc_html = ''
    if toc:
        lis = ''.join('<li class="lvl%d"><a href="#%s">%s</a></li>' % (lvl, aid, _html.escape(txt))
                      for lvl, aid, txt in toc)
        toc_html = ('<nav class="toc"><h2 class="toc-title">目　录</h2><ul>' + lis + '</ul></nav>')

    # ---- 6) 拆成「前置页」+「正文」 ----
    # 注意：不能用 find('class="page-one"') 切分——该 h1 可能原本就有 class，
    # page-one 被注入到 class 值里（如 class="sigilNotInTOC page-one"），
    # find('class="page-one"') 匹配不到(-1)，会导致整本都进了 maincontent。
    pm = _re.search(r'<h1[^>]*\bpage-one\b', body_html)
    pos = pm.start() if pm else -1
    if pos >= 0:
        # 关键：page-one 这个 h1 位于某个 .epub-block 的开头。
        # 切分点必须回溯到“包含 page-one 的那个 <div class="epub-block"> 的开头”，
        # 让这块<div>…</div>整体留在 content_part。否则开/闭标签被切成两半，
        # DOM 错乱 → .maincontent 识别不到 page:main → 页眉页脚丢失、目录页码全1。
        block_start = body_html.rfind('<div class="epub-block">', 0, pos)
        if block_start != -1:
            pos = block_start
    front_part = body_html[:pos] if pos >= 0 else ''
    content_part = body_html[pos:] if pos >= 0 else body_html

    doc = ('<!DOCTYPE html><html><head><meta charset="utf-8">' + style +
           '</head><body>'
           '<div class="frontmatter">' + marker + front_part + toc_html + '</div>'   # 封面/书名/版权/目录
           '<div class="maincontent">' + content_part + '</div>'                     # 正文(从 page-one 起)
           '</body></html>')
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(doc)
    print('生成:', out_html, '| 书名:', title, '| 目录项:', len(toc))


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
