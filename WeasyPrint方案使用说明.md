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

- 文件（都在**同一个文件夹**里，例如 `C:\Users\ZhangXu\Desktop\epub‑weasyprint‑pdf\`）：
  - `epub2pdf_gui.cmd` —— **双击这个启动图形窗口**（一键转换入口，见第零节）
  - `epub2pdf_gui.py` —— 图形窗口本体（粘贴/选文件/日志区，并调用下面两步）
  - `epub_to_html.py` —— 第 1 步「拆书」：EPUB → 单文件 HTML（跳过源目录页、自动生成目录）
  - `run.py` —— 第 2 步「排版」：HTML + book.css → PDF（WeasyPrint）
  - `book.css` —— 版式（纸型/页边距/页眉页码/正文/目录/分页/**第 8 节 源样式纠偏**）
  - `WeasyPrint方案使用说明.md` —— 本说明
- 依赖：Python、`pip install weasyprint`、**GTK 运行时**；图形窗口还要用 Python 自带的 **tkinter**。**不需要 Calibre / LaTeX**。
- **只需要这 5 个文件就能跑**：`epub2pdf_gui.cmd`、`epub2pdf_gui.py`、`epub_to_html.py`、`run.py`、`book.css`（其余是文档/示例/git 历史，删了不影响运行）。

---

## 零、怎么用

### 0.1 图形窗口版：三步转换

1. **复制 epub 路径**：资源管理器里选中 `.epub` → **按住 Shift 右键 →「复制文件地址」**（或在地址栏里选中路径复制）
2. **双击 `epub2pdf_gui.cmd`** → 弹出窗口
3. **把路径粘到输入框**（`Ctrl+V` 或右键粘贴），或点 **「选择文件…」** / **「选择文件夹…」**（选文件夹会把里面所有 epub 都转掉）→ 点 **「开始转换」**

日志区会实时显示进度，转完自动打开 PDF。两个勾选项：

| 勾选项 | 默认 | 作用 |
| --- | --- | --- |
| 转完自动打开 PDF | ✔ 勾上 | 转完用系统默认阅读器打开成品 |
| 转完删除中间文件（含 `_work` 整目录） | ✗ 不勾 | 一轮转换全部结束后，把整个 `_work` 目录删掉（含各书中间文件、`_gui_run.log`）；下次转换会自动重建。**要留现场排错就别勾** |

### 0.2 输出位置（都在脚本所在目录）

| 产物 | 位置 | 想换地方改哪一行 |
| --- | --- | --- |
| 成品 PDF | 脚本目录下的 `书名.pdf` | `epub2pdf_gui.py` **第 77 行** `pdf = os.path.join(HERE, name + ".pdf")` |
| 中间文件 | 脚本目录下的 `_work\书名\` | `epub2pdf_gui.py` **第 16 行** `WORKROOT = os.path.join(HERE, "_work")` |
| 图形版日志 | `_work\_gui_run.log` | `epub2pdf_gui.py` **第 19 行** `GUILOG = ...` |

举例：成品换到 `D:\epub_out` → 第 77 行改成 `pdf = os.path.join(r"D:\epub_out", name + ".pdf")`；中间文件也换 → 第 16 行改成 `WORKROOT = r"D:\epub_out\_work"`；别忘了**第 144 行**「打开成品目录」按钮也跟着改。

### 0.3 界面文字想改？全在 `epub2pdf_gui.py`

| 想改什么 | 行号 | 现在的写法 |
| --- | --- | --- |
| 窗口标题 | **122** | `root.title("EPUB 转 PDF")` |
| 窗口大小 | 123 | `root.geometry("780x540")` |
| 顶部备注文字 | **125–126** | `tip = ("把 epub 的路径粘贴到下面（…），" "也可以点“选择文件…”。成品 PDF 会放在本程序所在目录。")` |
| 备注换行宽度 | 127 | `wraplength=740` |
| 按钮：选择文件… / 选择文件夹… | 133 / 134 | `text="选择文件…"` / `text="选择文件夹…"` |
| 勾选项：转完自动打开 PDF | 139 | `text="转完自动打开 PDF"` |
| 勾选项：转完删除中间文件 | **141** | `text="转完删除中间文件（含 _work 整目录）"` |
| 按钮：开始转换 / 打开成品目录 | 143 / 144 | `text="开始转换"` / `text="打开成品目录"` |
| 日志区开头几行 | **152–154** | `self.log("成品 PDF 与中间文件都会放在: …")` 等 |
| 结束语 | 225 | `self.log("全部完成：成功 %d 本，失败 %d 本。…")` |
| 报错小弹窗 | 190 / 197 | `messagebox.showinfo(...)` / `showwarning(...)` |

改完**直接重开窗口即生效**（不用编译），文件保存为 UTF-8 就行。

### 0.4 命令行（可选；图形版用不到）

不带窗口、想批量转的时候，直接跑这两条（也是图形版内部实际执行的两条）：

```
python epub_to_html.py "D:\电子书\思考快与慢.epub" "_work\思考快与慢\book.html" "_work\思考快与慢"
python run.py          "_work\思考快与慢\book.html" "思考快与慢.pdf"
```

---

## 一、这几个文件各自的作用

### 1. `epub2pdf_gui.cmd` + `epub2pdf_gui.py` —— 入口与图形窗口

- `epub2pdf_gui.cmd`：**纯 ASCII** 的启动器（cmd 会按控制台代码页读文件，中文字符会让它解析出错，所以这个文件里不写中文）。它依次检查：Python → `weasyprint` → `tkinter`，都通过就用 `pythonw` 启动窗口（不弹黑窗口）。缺什么会给出中文提示。
- `epub2pdf_gui.py`：窗口本体。点「开始转换」后调 `convert_one()`，依次跑下面两条命令，并把它们的输出实时贴到日志区：
  - 第 91 行：`python epub_to_html.py 书.epub _work\书名\book.html _work\书名`（拆书）
  - 第 103 行：`python run.py _work\书名\book.html 书名.pdf`（排版，真正出 PDF）
  - 给子进程设了 `PYTHONIOENCODING=utf-8` + `PYTHONUTF8=1` + `-X utf8`（第 25–27 行）——**必须**：否则子进程按系统 GBK 编码输出，一旦要打印的路径里有 GBK 存不进的字符（例如本项目目录名里的 `‑` U+2011）就会 `UnicodeEncodeError` 崩掉。

### 2. `epub_to_html.py` —— 生成器（纯 Python 标准库，无需额外安装）
把 EPUB 解析成一个**单文件 HTML**（保留原 CSS 和图片），供 WeasyPrint 渲染。内部流程 6 步：

1. **解出整包**：把图片/字体/CSS/正文解压到工作目录，保留目录结构。
2. **按 spine 顺序合并正文**：按书页顺序拼成一个 `<body>`；**跳过源 EPUB 自带的目录页**（判据见下面 2.1）；**把每个源 xhtml 内容块包进 `<div class="epub-block">`**（让 CSS 让它独占一页）；并把 `<img src>` 改成**相对 html 目录的路径**（否则图片丢失）。
3. **内联合并 CSS**：把各 CSS 合成一个 `<style>`，并修正里面的 `url(...)` 路径。
4. **取书名**：优先取 EPUB 元数据 `dc:title`，取不到则用文件名(去扩展名)。注入一个隐藏标记 `<div id="booktitle">`，供页眉 `string(booktitle)` 用。
5. **加锚点 + 生成目录**：给 `h1`/`h2` 加 `id`，生成目录 `<nav class="toc">`（一级顶格、二级缩进），并给**目录后第一个一级标题**加 `class="page-one"`。
6. **拆成「前置页」+「正文」**：`frontmatter`（封面/书名/版权/目录）与 `maincontent`（正文，从 `page-one` 起）分开放，供 CSS 分别处理。

> ⚠️ 注意 1：第 6 步切分用的是 **`page-one` 独立词元**，不是 `class="page-one"` 字符串——后者因 h1 原本就带 class（如 `class="sigilNotInTOC page-one"`）会匹配不到。
> ⚠️ 注意 2：因为每个块都包了 `<div class="epub-block">`，切分点必须**回溯到包含 `page-one` 的那个 `.epub-block` 的开头**（让开/闭标签完整留在正文），否则 DOM 错乱 → 页眉页脚丢失、目录页码全 1。

#### 2.1 源 EPUB 的「目录页」怎么判断（三条判据）

源 epub 里那页"目录"其实是一张**正文页**（形如 `<a href="part0002.html">自序…</a>`），不处理就会跟着正文印进 PDF，跟第 5 步自动生成的目录重复，而且常带链接蓝。判断在**合并正文之前**做（`epub_to_html.py` 第 50–105 行算出要跳过的 id 集合），生效在第 119–121 行：命中就整页不参与合并。

| 判据 | 代码位置 | 内容 |
| --- | --- | --- |
| ① EPUB3 规范 | 第 68、73 行 | 项属性 `properties` 含 `nav` → 是 EPUB3 导航文档（`nav.xhtml`/`toc.xhtml`） |
| ② 名字带目录词 | 第 63、72–73 行 | `id + '/' + href` 小写后含 `toc` / `contents` / `directory` / `目录` 任一 → 跳过 |
| ③ **看内容**（专治名字毫无线索的） | 第 75–105 行 | 满足 `others >= 5 and textlen <= 4000 and others * 40 >= textlen` 就跳过：<br>· `others` = 页内指向**其它正文文件**的内部链接数（去锚点、跳过 http/mailto 等、只算属于本书 spine 的其它文件）<br>· `textlen` = 去掉标签/脚本后的纯文字字数<br>· 第三个条件 = 链接密度（平均每 40 字至少 1 个链接），避免误伤"长正文里链接多"的页 |
| ★ 手工名单 | 第 62 行 | `SKIP_HREFS = ()` 里写文件名或完整 href，例如 `('text/part0001.html',)` → 强制跳过并打印"跳过源目录页(手工指定)" |

- 命中时会打印一行，例如：`跳过源目录页(自动识别): text/part0001.html | 内部链接 65 个 / 文字 2222 字`
- 想调松/调紧就改**第 103 行**的三个阈值（判据做得保守，宁可漏判也不误删正文）
- 源 epub 的 `toc.ncx` **永远不会**被合并（它不是 xhtml，第 70–71 行只挑 xhtml）；PDF 里的目录是第 5 步从合并后的 `h1/h2` **自动生成**的，所以跳过源目录页不会丢目录
- 验证办法：`python epub_to_html.py "书.epub" out.html work` —— 控制台会列出每一页的跳过情况

### 3. `run.py` —— 渲染器
调用 WeasyPrint 把 HTML + 版式渲染成 PDF：
- 自动在**多个位置查找** `book.css`（`run.py` 同目录 → html 同目录 → 当前目录 → `weasyprint方案` 文件夹），找到就用。
- 以 html 所在目录为 base，保证相对图片路径能解析。

```python
HTML(html, base_url=base).write_pdf(out, stylesheets=[CSS(book_css)])
```

### 4. `book.css` —— 版式（所有外观都在这里改）
按「节」组织，文件头有「★ 快速找改动点 ★」表格。核心逻辑：
- **纸张**：`@page { size: A5 !important; }`（`!important` 用来压过源 EPUB 自带的 `@page{size:…}`）。
- **镜像边距**：`@page :right` / `@page :left` 各设一组 `margin`（奇数页左内侧、偶数页右内侧）。
- **页眉/页码**：用 `@page :right/:left` 里的 margin-box（`@top-*`/`@bottom-*`）。
- **正文**：标题起新页、首行缩进、两端对齐、行距等。
- **每个源 xhtml 独占一页**：`.epub-block { break-before: page }`（由生成器给每块包 class）。
- **块内连续排**：`.epub-block h1..h6 { break-before: auto }`，让「图→标题→正文」不拆页。
- **第 8 节「源 EPUB 样式纠偏」（通用，任何书都生效）**：对付源书里那些会造成插图大片空白的写法 ——
  `* { height:auto !important; min-height:0 !important }` 拆掉固定高度容器（如 `height:600px` + flex 垂直居中）；
  `img/svg { max-width:100%; max-height:68vh; height:auto }` 保证一图一页内放得下且不变形；
  `:has(> img:only-child)` 等结构选择器把插图当整体（图注必须跟图同页）；
  图注统一 `break-before: avoid`、行高归一；标题去调试边框。详见文件里第 8 节的注释（8.1~8.6）。
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

图形窗口还需要 **tkinter**（Python 自带，通常不用装）。不想手打命令的话，直接**双击 `epub2pdf_gui.cmd`**：它会自己依次检查 `python` / `weasyprint` / `tkinter` 三项，缺哪项就在黑窗口里写清楚缺哪项、怎么装，全齐了才启动图形窗口。

---

## 三、每本书 1 步（零改源码，书名/目录/页码/分页全自动）

**双击 `epub2pdf_gui.cmd`** → 图形窗口里粘贴 epub 的完整路径（资源管理器里选中 epub → 按住 Shift 右键 →「复制文件地址」，回来 `Ctrl+V`；也可点「选择文件…」/「选择文件夹…」）→ 点「开始转换」。转完日志最后一行是 `全部完成：成功 N 本，失败 M 本。成品在: …`，想打开成品所在目录就点「打开成品目录」。

窗口里那行小字是**说明/备注信息**（怎么用、结果放哪），不是你操作的输入框。

命令行等价写法（不用图形窗口时，分两步跑；也就是图形窗口内部实际执行的两条）：
```cmd
cd /d "C:\Users\ZhangXu\Desktop\epub‑weasyprint‑pdf"
python epub_to_html.py "D:\电子书\你的书.epub" "_work\你的书\book.html" "_work\你的书"
python run.py          "_work\你的书\book.html" "你的书.pdf"
```
> 第一条（拆书）会打印 `生成: … | 书名: … | 目录项: NN`，可核对取到的书名和目录条数；第二条（排版）打印 `完成 -> …pdf`。

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
把 epub 路径粘进窗口（或点「选择文件夹…」选一个装着一堆 epub 的文件夹，它会**把里面所有 epub 依次转完**，日志开头会打印 `共 N 个文件，开始转换 ...`）。**书名/目录/页码/分页全自动，`book.css` 不用动。**

换算例外的书：`epub_to_html.py` 和 `run.py` 都不认识「这本书」，只管拿 epub 里的文字和结构；排版外观完全由 `book.css` 决定，所以同一套 CSS 对任何 epub 都生效。真遇到某一本排歪了，才去 `book.css` 第 8 节（源 EPUB 样式纠偏）调。

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
11. **PDF 里出现「重复的目录」（常是蓝色的一大串链接）** → 源 EPUB 自带的目录 xhtml 没被跳过。重跑 `epub_to_html.py` 即可，它用三条规则自动识别并跳过源目录页（见「一、这些文件都是干嘛的」里的检测表），运行时打印 `跳过源目录页(自动识别): xxx` 就是识别到了。三条都没命中的极端书，把文件名手工填进 `epub_to_html.py` 第 62 行 `SKIP_HREFS`。
12. **插图周围一大片空白 / 图注被挤到下一页** → 源 EPUB 给图片或图注套了**固定高度**容器（如 `height:600px` + 垂直居中 flex），或给标题加了调试用边框。`book.css` **第 8 节「源 EPUB 样式纠偏」** 已通用处理：8.1 拆固定高度、8.2 图片限高 `68vh`（第 288 行）、8.3 把「图＋图注」当整体不分页（其后紧跟一段把 flex 横排改回竖排）、8.4 图注 `break-before: avoid`、8.6 去标题边框。改完重跑排版（不用重跑拆书）。想更紧/更松只调 8.2 的 `max-height: 68vh`。
13. **图形窗口报转换失败，日志里有 `UnicodeEncodeError`/`gbk codec`** → 子进程输出编码问题，本项目已用 `PYTHONIOENCODING=utf-8`（`epub2pdf_gui.py` 第 25–27 行）解决；若你把脚本搬去别处并改过这几行，注意别删。另外本项目目录名里有个特殊连字符 `‑`（U+2011，GBK 里没有），**建议把文件夹改名为 `epub-weasyprint-pdf`**（普通 ASCII 连字符），能避开这一整类编码坑。
14. **GLib 一堆警告** → 无关噪音，忽略。

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
