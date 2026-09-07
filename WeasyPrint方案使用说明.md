# WeasyPrint 方案使用说明（纯 Python，脱离 Calibre）

## 用途

用 WeasyPrint 把 **EPUB → PDF**，达成书稿级排版：

- ✅ **保留 EPUB 原观感**（正文默认样式、居中图片/图注、首行缩进、字体——自动保留）
- ✅ **镜像边距**（奇数/偶数页左右不同，贴合书脊/翻口）
- ✅ **运行页眉/页码**（奇数页=「章／节」，偶数页=「书名」；页眉/页码分别放翻口侧）
- ✅ **目录**（自动生成，一级顶格 + 二级缩进，并列出每项对应的真实页码）
- ✅ **前置页无页码**（封面/版权/目录无页眉无页码）
- ✅ **正文从第 1 页开始**
- ✅ **目录与正文都强制从右手(奇数)页开始**（前一页若是偶数页，自动补一页空白）
- ✅ **每个源 xhtml 内容块独占一页**（内容不足一页也单独一页，不跟下一块接排）
- ✅ **块内图片连续排**（源的「图 → 标题 → 正文」块内不再被拆成图片一页、标题一页，像 EPUB 浏览）
- ✅ **图片限宽**（统一 `max-width`/等比缩放，超大图不再溢出/跨页）
- ✅ **跳过源 EPUB 自带的目录 html**（避免跟自动目录重复/串页）
- ✅ **目录排版**：一级顶格 + 二级缩进、带真实页码、**目录条目用正文字色**（压过源 EPUB 的链接蓝）
- ⚠️ **页眉倾斜**：WeasyPrint 对中文不会合成斜体，页眉是直体（引擎限制）

- 文件（都在桌面 `C:\Users\ZhangXu\Desktop\`）：
  - `epub_to_html.py` —— 把 EPUB 转成单文件 HTML
  - `run.py` —— 用 WeasyPrint 渲染 HTML + book.css → PDF
  - `book.css` —— 版式（页边距/页眉/页码/正文/目录/分页/图片）
  - `WeasyPrint方案使用说明.md` —— 本说明
- 依赖：Python、`pip install weasyprint`、**GTK 运行时**。**不需要 Calibre / LaTeX**。

---

## 一、这三个文件各自的作用

### 1. `epub_to_html.py` —— 生成器（纯 Python 标准库，无需额外安装）
把 EPUB 解析成一个**单文件 HTML**（保留原 CSS 和图片），供 WeasyPrint 渲染。内部流程 6 步：

1. **解出整包**：把图片/字体/CSS/正文解压到工作目录（`assets\`），保留目录结构。
2. **按 spine 顺序合并正文**：按书页顺序拼成一个 `<body>`；**跳过源 EPUB 自带的目录 html**（`properties="nav"` 或文件名/id 含 `toc/contents/目录` 的 xhtml）；**把每个源 xhtml 内容块包进 `<div class="epub-block">`**（让 CSS 让它独占一页）；并把 `<img src>` 改成**相对 html 目录的路径**（否则图片丢失）。
3. **内联合并 CSS**：把各 CSS 合成一个 `<style>`，并修正里面的 `url(...)` 路径。
4. **取书名**：优先取 EPUB 元数据 `dc:title`，取不到则用文件名(去扩展名)。注入一个隐藏标记 `<div id="booktitle">`，供页眉 `string(booktitle)` 用。
5. **加锚点 + 生成目录**：给 `h1`/`h2` 加 `id`，生成目录 `<nav class="toc">`（一级顶格、二级缩进），并给**目录后第一个一级标题**加 `class="page-one"`。
6. **拆成「前置页」+「正文」**：`frontmatter`（封面/书名/版权/目录）与 `maincontent`（正文，从 `page-one` 起）分开放，供 CSS 分别处理。

> ⚠️ 注意 1：第 6 步切分用的是 **`page-one` 独立词元**，不是 `class="page-one"` 字符串——后者因 h1 原本就带 class（如 `class="sigilNotInTOC page-one"`）会匹配不到。
> ⚠️ 注意 2：因为每个块都包了 `<div class="epub-block">`，切分点必须**回溯到包含 `page-one` 的那个 `.epub-block` 的开头**（让开/闭标签完整留在正文），否则 DOM 错乱 → 页眉页脚丢失、目录页码全 1。
> ℹ️ 关于识别目录：只对 xhtml 类判断 `properties="nav"` 或文件名/id 含目录词，**不会误删**正文分片(`index_split_*.html`)、纯编号正文(`part*.html`)或图片/字体/NCX。

### 2. `run.py` —— 渲染器
调用 WeasyPrint 把 HTML + 版式渲染成 PDF：
- 自动在**多个位置查找** `book.css`（`run.py` 同目录 → html 同目录 → 当前目录 → `weasyprint方案` 文件夹），找到就用。
- 以 html 所在目录为 base，保证相对图片路径能解析。

```python
HTML(html, base_url=base).write_pdf(out, stylesheets=[CSS(book_css)])
```

### 3. `book.css` —— 版式（所有外观都在这里改）
按「节」组织，文件头有「★ 快速找改动点 ★」表格。核心逻辑：
- **纸张**：`@page { size: A5; }`。
- **镜像边距**：`@page :right` / `@page :left` 各设一组 `margin`（奇数页左内侧、偶数页右内侧）。
- **页眉/页码**：用 `@page :right/:left` 里的 margin-box（`@top-*`/`@bottom-*`）。
- **打印样式**：标题起新页、首行缩进、两端对齐等。
- **图片限宽**：`img { max-width:100%; height:auto }` 和 `.chatu img`，避免超大图溢出/跨页。
- **每个源 xhtml 独占一页**：`.epub-block { break-before: page }`（由生成器给每块包 class）。
- **块内连续排**：`.epub-block h1..h6 { break-before: auto }`，让「图→标题→正文」不拆页。
- **目录排版**：`.toc a` 去掉下划线并 `color: inherit !important`（压过源 EPUB 的链接蓝）；`.toc a::after` 填页码。
- **前置页/正文分页 + 页码分组**：命名页 `frontmatter` / `main`，正文序号用自定义计数器 `main-pagecounter`。

---

## 二、一次性安装（只做一次）
```powershell
python -m pip install weasyprint
```
再装 **GTK 运行时**（图形库，必要；第一次可走镜像加速链接），装后**重开 cmd** 验证：
```cmd
python -c "import weasyprint; print(weasyprint.__version__)"
```
打印版本号即成功。`epub_to_html.py` 只用标准库，无需额外装。

---

## 三、每本书 2 步（零改源码，书名/目录/页码/分页全自动）
```cmd
cd /d C:\Users\ZhangXu\Desktop
python epub_to_html.py "你的书.epub" "你的书.html" assets
python run.py "你的书.html" "你的书.pdf"
```
> 运行时打印 `生成: xxx.html | 书名: xxx | 目录项: NN`，可核对取到的书名和目录条数。

---

## 四、想改什么 → 都改 `book.css`

### 纸张 / 页边距 / 镜像（cm）
```css
@page { size: A5; }                    /* 改 A4 也行 */
@page :right { margin-top/left/right/bottom: ...; }   /* 奇数页 */
@page :left  { margin-left/right: ...; }              /* 偶数页(左右镜像) */
```
内侧(书脊)/外侧(翻口)用不同值即镜像；想让页眉靠翻口，减小对应外侧边距或用负 `margin`。

### 页眉 / 页脚（内容 + 字体）
```css
@top-right   { content: string(chapter) string(section); font-size: 0.7em; ... }  /* 奇数页：章／节 */
@top-left    { content: string(booktitle); ... }                                 /* 偶数页：书名 */
@bottom-right / @bottom-left { content: counter(main-pagecounter); ... }          /* 页码(用自定义计数器) */
```
- 字体：`font-family`；字号 `font-size`；样式 `font-style`/`font-weight` 加 `!important`。
- 位置：靠左/靠右由 margin box（`@top-left`/`@top-right`……）决定。
- 下划线：`text-decoration: underline` + `text-underline-thickness` + `text-underline-offset`。

### 页眉分隔符（只有一级标题时自动不显示）
改 `book.css` 第 5 节这一行的 `"／"`：
```css
h2 { string-set: section "／" content(); }
```
把 `"／"` 换成 `" - "` / `" | "` / `" · "` 等即可；只有一级标题（无二级）时页眉只显示一级标题、不带分隔符。

### 正文字号 / 行距 / 缩进
```css
body { font-family: ...; font-size: 0.76em; line-height: 1.7; }
p { text-indent: 2em; }
```

### 目录（颜色 + 页码）
目录条目默认**跟正文同色、无下划线**，显示标题 + 真实页码：
```css
.toc a { text-decoration: none; color: inherit !important; }   /* 压过源 EPUB 的链接蓝 a{color:#0000CC} */
.toc a::after { content: leader(".") "　" target-counter(attr(href url), main-pagecounter); }
```
- 想只列标题不带页码 → 删掉 `::after` 那条规则。
- 想目录条目用别的颜色 → 改 `color: inherit` 为 `color: #333` 等；注意 `!important` 别删（否则源 EPUB 的链接蓝会盖回来）。

### 每个源 xhtml 独占一页 / 块内连续排
默认每个源 xhtml 内容块独占一页（`.epub-block` 起新页），块内「图→标题→正文」连续排：
```css
.epub-block { break-before: page; }              /* 块独占一页 */
.epub-block h1, .epub-block h2, ... { break-before: auto; }   /* 块内标题不强制起页 */
```
- 想要「每个源 xhtml」连续排（不独占）→ 删掉 `.epub-block { break-before: page }`。
- 想要块内标题也起新页 → 删掉 `.epub-block h1..h6 { break-before: auto }`。

### 强制从右手页开始（目录 / 正文）
```css
.toc { break-before: right; }                              /* 目录起右手页，不足补空白 */
.maincontent { page: main; break-before: right; }          /* 正文起右手页，不足补空白 */
```
补的空白页不会计入正文页码（页码只在 `main` 命名页递增）。

---

## 五、换一本书
只改**命令里的书名**（其余自动），`book.css` 不用动：
```
python epub_to_html.py "新书.epub" "新书.html" assets
python run.py "新书.html" "新书.pdf"
```

---

## 六、常见问题
1. **图片丢失** → 用新书文件重跑 `epub_to_html.py`（旧 html 没图片/标记）。
2. **图片独自占一页（图/标题被拆开）** → 源 xhtml 是「图→标题→正文」结构，块内标题被全局 `break-before: page` 推到下一页。保持 `.epub-block h1..h6 { break-before: auto }`（块内连续排）。
3. **超大图溢出/跨页** → 缺图片限宽；保持 `img { max-width:100%; height:auto }` 和 `.chatu img`。
4. **正文不是从 1** → 检查 `@page main` 是否只有 `counter-increment: main-pagecounter`（不要用 `counter-reset: page`；内置 `page` 计数器在 WeasyPrint 命名页上无法干净重置，会导致「10,11,10,11」或全 0）。
5. **正文从 10 开始** → 说明 `counter-increment` 被放到了 `@page :left/:right` 上（它会连前置页也计数）；应放在 `@page main` 上。
6. **页眉出现「目录」** → 目录标题也是 `<h2>`，未被排除；保持 `.toc-title { string-set: none; }`。
7. **页眉页脚丢失 + 目录页码全 1** → 多半是 `.epub-block` 切分点切错了（开/闭标签被劈开，`.maincontent` 识别不到 `page:main`）；重跑 `epub_to_html.py` 并确认其第 6 步回溯到块开头切分。
8. **前置页仍有页码/页眉** → 确认 `.frontmatter { page: frontmatter; }` 且 `@page frontmatter` 里 `@top-*`/`@bottom-*` 都设了 `content: none`。
9. **目录页码全 1** → 不要用 `counter-reset: page`（与 `target-counter` 冲突）；页码/目录都指向 `main-pagecounter`。
10. **目录条目是蓝色/带下划线** → 源 EPUB 有全局 `a{color:#0000CC}`；保持 `.toc a { color: inherit !important; text-decoration: none; }`（`!important` 必须保留）。
11. **PDF 里出现「重复的目录」** → 源 EPUB 自带了目录 html 没被跳过；重跑 `epub_to_html.py`（它会识别 `properties="nav"` 或文件名/id 含 `toc/contents/目录` 的 xhtml 并跳过）。
12. **GLib 一堆警告** → 无关噪音，忽略。

---

## 七、和另外两种对比
| | Calibre(py) | WeasyPrint | LaTeX |
|---|---|---|---|
| 保留 EPUB 原观感 | ✅ | ✅ | ❌ |
| 镜像边距 | ❌ | ✅ | ✅ |
| 目录自动页码 + 正文从1 | ❌ | ✅ | 需额外配置 |
| 章节起始页去页眉 | ❌ | ❌ | ✅ |
| 需要 Calibre | 要 | **不要** | 不要 |
| 需装 GTK / MiKTeX | 无 | GTK | MiKTeX+pandoc |
