# EPUB → PDF 书稿级排版转换（WeasyPrint 实现）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![WeasyPrint](https://img.shields.io/badge/WeasyPrint-60%2B-blue.svg)](https://weasyprint.org/)
[![GitHub stars](https://img.shields.io/github/stars/Nomadic-Dv/epub-weasyprint-pdf.svg)](https://github.com/Nomadic-Dv/epub-weasyprint-pdf/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/Nomadic-Dv/epub-weasyprint-pdf.svg)](https://github.com/Nomadic-Dv/epub-weasyprint-pdf/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/Nomadic-Dv/epub-weasyprint-pdf.svg)](https://github.com/Nomadic-Dv/epub-weasyprint-pdf/commits/main)

> **不丢失原书样式**，把 EPUB 转成**出版级排版**的 PDF。  
> 镜像页边距 · 奇偶页差异化页眉 · 翻口页码 · 右手页起章 · 真实目录页码锚点。  
> 全程纯 Python + WeasyPrint，无需 LaTeX，无需 Calibre，本地离线即可跑。  
> **双击 `epub2pdf_gui.cmd` → 粘贴 epub 路径 → 开始转换**，无需敲命令。


## 1\. 项目概述

本项目实现**无损保留 EPUB 原生排版观感**的高质量 PDF 转换，区别于 Calibre、Pandoc 通用转换方案，主打「原书样式保真 \+ 出版级书籍版式」。全程基于纯 Python \+ WeasyPrint 实现，不依赖 LaTeX、不依赖 Calibre、无大型环境依赖，轻量化、可本地离线运行，专为中文电子书书稿排版优化。

项目核心目标：**最大限度保留原 EPUB 字体、缩进、图文布局、配色样式，同时补齐标准纸质书籍的专业排版规范**（镜像页边距、奇偶页差异化页眉、翻口页码、右手页起章、自动出版级目录、干净页码计数体系）。

## 2\. 整体技术架构

项目采用**预处理解析 \+ CSS版式渲染**分层架构，解析层与渲染层完全解耦，可插拔替换渲染引擎。

### 2\.1 两层核心架构

- **图形窗口层（epub2pdf\_gui\.cmd + epub2pdf\_gui\.py，可选）**：一键入口。负责挑文件、实时显示进度、隔离子进程编码环境，并依次调用下面两层；不用窗口时可直接跑命令行。

- **解析预处理层（epub\_to\_html\.py）**：解包EPUB、清洗DOM、修复资源路径、过滤无效目录页、重构章节结构、生成锚点与标准目录、区分前置页/正文页、统一全局DOM结构，输出标准化纯净HTML。

- **版式渲染层（run\.py \+ book\.css）**：基于WeasyPrint实现完整CSS分页媒体排版，控制纸张、边距、奇偶页页眉页码、分页规则、图文自适应、目录样式，最终输出书稿级PDF。

### 2\.2 核心特性：不破坏原书样式

区别于所有主流开源方案，本项目**不清洗、不覆写、不重置原EPUB CSS**，以内联源样式为主、自定义版式CSS为辅，最大程度保留电子书原生阅读观感，仅补充出版书籍必备的规范版式。

## 3\. 核心实现功能清单

### 3\.1 原书样式保真能力

- 完整保留EPUB原生CSS、正文样式、首行缩进、字体配色、图文排版

- 自动修复图片相对路径，解决图片丢失、加载异常问题

- 图片自适应页面宽高，防止超页、变形、截断（宽度上限=正文栏宽，高度上限=`68vh`=版心高的 68%，源书写死 `width:100%` 时用 `object-fit:contain` 保住比例）

- **源 EPUB 样式纠偏（`book.css` 第 8 节，通用）**：拆掉源书给图片/图注写死的固定高度容器（如 `height:600px` + flex 垂直居中）与撑空白的超大行高，图片按版心限高等比缩放，**插图与其图注始终同页**，避免"图片独占一页、图注被挤到下一页"的大片空白；章标题上的调试用边框一并去掉

### 3\.2 专业出版级版式（自研核心能力）

- **镜像页边距**：奇偶页区分内外侧边距，适配书籍装订翻阅规范

- **奇偶页差异化页眉**：偶数页展示书名、奇数页展示章节名，版式贴合正式出版物

- **翻口侧页码**：页码始终位于书籍外侧翻口，符合图书印刷标准

- **纯净页码计数体系**：自研自定义计数器 `main-pagecounter`，彻底解决 WeasyPrint 原生页码错乱BUG，前置页、目录页不占用正文页码，正文从第1页开始计数

- **右手页起章**：目录、正文、新章节强制从右手奇数页开始，空白页自动补全

- **前后内容隔离**：前置页无页眉、无页码，正文页独立版式体系

### 3\.3 智能目录系统

- 自动扫描 h1/h2 标题生成标准化书籍目录

- 目录支持真实页码锚点联动，基于 `target-counter` 实现精准页码展示

- 一级标题顶格、二级标题缩进，层级规范清晰

- 自动过滤 EPUB 原生自带目录页，避免重复目录、排版混乱

- 重置默认链接蓝色样式，目录字体、字号、配色独立可控

### 3\.4 精细化分页防崩逻辑

- 每个源XHTML章节独占新页面，章节结构完整不拆分

- 优化图文、标题、正文分页优先级，避免标题孤行、图片截断、内容撕裂；**插图与其图注强制同页**（`break-after: avoid` + 图注 `break-before: avoid`）

- 回溯DOM节点修复分页错位，解决页眉丢失、目录页码全1、DOM错乱等疑难问题

- 智能处理章节分隔符、标题层级，保证全书版式统一

## 4\. 关键技术难点与自研解决方案

本项目解决了全网 WeasyPrint 开源方案普遍存在的经典内核BUG与排版痛点，属于独家工程化适配方案。

### 4\.1 WeasyPrint 原生页码错乱终极解决

原生 `counter(page)` 在命名页、多版式页面场景下会出现页码跳变、重复、前置页占位、归零错乱问题。项目自研**独立自定义计数器**，仅在正文命名页递增，彻底隔离前置页、目录页，实现正文页码从1开始纯净计数。

### 4\.2 页眉智能渲染逻辑

通过 CSS string\-set 动态抓取章节标题，自动适配层级：二级标题存在则展示「章节/小节」分隔样式，单一级标题自动清空冗余分隔符；同时排除目录标题干扰，杜绝页眉显示“目录”异常问题。

### 4\.3 精准目录页识别过滤

适配 EPUB 标准规范，**三条判据**过滤原生目录页面，避免目录重复、版式冲突：

- **① EPUB3 规范**：spine 项属性 `properties` 含 `nav`（`nav.xhtml`/`toc.xhtml`）
- **② 命名特征**：`id`/`href` 小写后含 `toc`、`contents`、`directory`、`目录`
- **③ 内容特征**（专治文件名毫无线索的，如某书目录页叫 `text/part0001.html`）：页面内指向「其它正文文件」的内部链接 ≥ 5 个、纯文字 ≤ 4000 字，且「平均每 40 字至少 1 个链接」的链接密度 —— 即"这一页几乎全是通往别页的链接"，判为目录页

判据做得保守（宁可漏判也不误删正文）；三条都没命中的极端书，可在 `epub_to_html.py` 的 `SKIP_HREFS` 里手工写文件名强制跳过。命中时会打印 `跳过源目录页(自动识别): … | 内部链接 N 个 / 文字 M 字`，便于核对。

### 4\.4 防DOM崩页、版式丢失机制

优化分页节点优先级，回溯章节根节点进行分页控制，解决复杂图文书籍出现的页眉消失、内容断层、页码统一为1、区块撕裂等问题，大幅提升复杂EPUB兼容性。

## 5\. 项目文件结构与作用

- **epub2pdf\_gui\.cmd**：图形窗口启动器（纯 ASCII，避免 cmd 代码页把中文读坏）。依次检查 Python → `weasyprint` → `tkinter`，都通过就用 `pythonw` 启动窗口（不弹黑窗口），缺什么给出中文安装提示
- **epub2pdf\_gui\.py**：图形窗口本体（粘贴/选择 epub、实时日志、转完自动打开 PDF、可选"转完删除中间文件"）。内部依次调用下面两条，并为子进程设置 `PYTHONIOENCODING=utf-8` + `-X utf8` —— 否则中文 Windows 下按 GBK 输出，路径含 GBK 无法表示的字符时会 `UnicodeEncodeError` 崩溃
- **epub\_to\_html\.py**：核心解析器，负责EPUB解包、DOM清洗、样式内联、路径修复、目录生成、章节结构化、前置/正文页拆分，输出标准化HTML
- **run\.py**：渲染调度器，自动读取自定义CSS、指定资源根目录，调用WeasyPrint完成PDF渲染
- **book\.css**：全书式核心文件，包含纸张配置、镜像边距、奇偶页眉页码、分页规则、目录样式、图文适配、源样式纠偏（第 8 节）、全局版式规范
- **WeasyPrint方案使用说明\.md**：部署安装、使用步骤、输出位置、界面文字改法、常见问题、方案对比文档

> **最小可用集合**：`epub2pdf_gui.cmd`、`epub2pdf_gui.py`、`epub_to_html.py`、`run.py`、`book.css` 这 5 个文件即可完整转换（其余为文档 / 示例 / 仓库元数据）。

## 6\. 快速使用流程

### 6.1、下载仓库代码

```
git clone https://github.com/Nomadic-Dv/epub-weasyprint-pdf.git
```

### 6.2、安装 Python

Python >= 3.10（安装时勾选 `Add Python to PATH`）

### 6.3、安装依赖：

```bash
pip install -r requirements.txt
```

再安装 **GTK 运行时**（WeasyPrint 的图形库依赖，必需；Windows 下见 [WeasyPrint 官方安装说明](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)）。装完**重开命令行**验证：

```cmd
python -c "import weasyprint; print(weasyprint.__version__)"
```

打印版本号即成功。图形窗口还需 Python 自带的 `tkinter`（通常无需安装）；直接双击 `epub2pdf_gui.cmd`，它会自动检查 `python` / `weasyprint` / `tkinter` 三项并提示缺哪项。

### 6.4、开始使用

**图形窗口版（推荐，一步搞定）**

1. 资源管理器里选中 `.epub` → 按住 `Shift` 右键 →「复制文件地址」
2. **双击 `epub2pdf_gui.cmd`**
3. 把路径粘贴进输入框（或点「选择文件…」/「选择文件夹…」，选文件夹会把里面所有 epub 依次转完），点「开始转换」

成品 PDF 与中间文件都放在**脚本所在目录**（中间文件在 `_work\书名\`，可随时删；勾选「转完删除中间文件」则一轮结束后自动清掉整个 `_work`）。输出路径与界面文字的修改位置见说明文档第零节。

**命令行版（等价，分两步）**

```cmd
cd /d "项目文件夹"

# 1. EPUB解析预处理，生成标准化HTML（第 3 个参数是图片/资源的解包工作目录）
python epub_to_html.py "你的书籍.epub" "_work\你的书\book.html" "_work\你的书"

# 2. WeasyPrint渲染生成最终PDF
python run.py "_work\你的书\book.html" "你的书.pdf"
```

## 7\. 方案选型对比（行业横向优势）

### 7\.1 对比 Calibre 转换

- Calibre：强制重写全部样式、丢失原书排版、无镜像装订边距、页眉页码简陋、分页混乱、无右手起章规范

- 本项目：**保留原书所有样式 \+ 专业出版版式**，书稿质感碾压Calibre输出效果

### 7\.2 对比 Pandoc 全方案

- Pandoc\+LaTeX：拥有原生页底脚注，但**完全丢弃EPUB原生CSS与排版**，所有图文、缩进、样式全部重排，彻底丢失原书观感，部署环境庞大繁琐

- Pandoc\+WeasyPrint：无原生脚注能力，且无法精细控制书籍级分页与奇偶版式，适配性远不如本项目定制CSS体系

### 7\.3 对比 GitHub 同类开源项目

调研全网同类 WeasyPrint EPUB2PDF 开源项目，无任何项目同时满足「中文适配 \+ 原样式保真 \+ 纯净页码体系 \+ 完整出版级版式」：

- 海外开源项目：优先适配英文公版书，强制清洗原书样式，无中文缩进、字体、目录适配，工程架构复杂、上手难度高

- 国内零散Demo：仅实现基础转换，无任何出版版式、页码错乱、样式丢失、分页崩坏问题严重，仅为玩具级脚本

**结论：本项目是目前开源圈内，中文EPUB转PDF「保真\+出版级排版」最优轻量化方案。**

## 8\. 当前能力边界与局限性（透明说明）

### 8\.1 脚注能力限制（内核硬限制）

WeasyPrint 未实现完整 CSS Paged Media 脚注标准（`float:footnote` / 物理页底吸附），**无法原生实现出版级页底脚注**。

现有最优妥协方案：CSS模拟脚注（紧贴正文、分割线、小字排版、防分页撕裂），观感接近出版样式，但无法强制吸附物理页面底部、无法超长自动跨页拆分。

若需**100%出版级物理页底脚注**，需替换渲染引擎为 PrinceXML（商业）/ Vivliostyle（开源），可完全复用本项目预处理HTML与CSS，无需重构解析层。

### 8\.2 中文斜体限制

WeasyPrint 内核不支持中文伪斜体合成，页眉及正文中文无法倾斜，属于引擎通用硬限制，无适配解决方案。

### 8\.3 极端非常规EPUB兼容

目录页识别已实现第三条**内容特征判据**（看页内通往其它正文文件的链接密度），可覆盖"文件名毫无线索"的情况。但仍非100%：例如目录页混入大量说明文字（纯文字 > 4000 字）、链接数少于 5 个，或目录被拆到多个文件时仍可能漏判。此时可用 `epub_to_html.py` 的 `SKIP_HREFS` 手工指定文件名强制跳过（会打印"跳过源目录页(手工指定)"）。

## 9\. 迭代扩展方向

- 完善 CSS 模拟脚注体系，优化长脚注分页、间距、排版细节，无限贴近出版效果

- 目录页识别阈值（链接数 / 字数 / 链接密度）抽成可配置参数，并支持跨多文件目录页的合并识别

- 实现**双渲染引擎可切换架构**：保留默认WeasyPrint轻量化方案，可选Prince/Vivliostyle高级引擎，解锁原生物理页底脚注

- 增加孤行/寡行控制、页面溢出校验、版式自动纠错能力

- 简易配置化改造，将纸张大小、边距、页眉文字、字号参数抽离配置文件，无需修改CSS源码

## 10\. 最终项目定位总结

本项目**放弃复杂学术公式、顶级出版脚注能力**，换取：

**100% 保留EPUB原生排版观感 \+ 轻量化纯Python部署 \+ 完整中文书稿出版版式 \+ 稳定无BUG的页码与分页体系**

是普通中文电子书、读物、书籍 EPUB→PDF 高质量转换的**最优工程方案**，兼顾美观、实用性、易用性与稳定性，远超市面所有开源通用转换工具。


## 更新日志

详见 [CHANGELOG.md](./CHANGELOG.md)。


## 相关项目

- [obsidian-pandoc-epub](https://github.com/Nomadic-Dv/obsidian-pandoc-epub) —— 把 Obsidian 多文件夹笔记合并导出为 EPUB  
  👉 **工作流**：Obsidian → EPUB → PDF