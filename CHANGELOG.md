# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- **图形窗口版**：`epub2pdf_gui.cmd`（纯 ASCII 启动器，自检 `python` / `weasyprint` / `tkinter`，用 `pythonw` 启动不弹黑窗口）+ `epub2pdf_gui.py`（粘贴路径或「选择文件…」/「选择文件夹…」批量转换、实时日志、转完自动打开 PDF）
- 输出位置明确化：成品 PDF 放在脚本同目录，中间文件统一放 `_work\书名\`
- 新增「转完删除中间文件（含 `_work` 整目录）」勾选项（默认不勾，便于排错留现场）
- 子进程强制 UTF-8（`PYTHONIOENCODING=utf-8` + `PYTHONUTF8=1` + `-X utf8`）：修复中文 Windows 下路径含 GBK 无法表示的字符（如项目目录名里的 U+2011）时子进程 `UnicodeEncodeError`、表现为"图形窗口转换失败"的问题
- **目录页识别新增第三条「内容特征」判据**：按页内通往其它正文文件的内部链接数、纯文字字数、链接密度判断，覆盖文件名毫无目录线索的 EPUB（如目录页名叫 `text/part0001.html` 的书）；保留 `SKIP_HREFS` 手工名单兜底
- **`book.css` 第 8 节「源 EPUB 样式纠偏」（通用，任何书都生效）**：
  - 8.1 拆掉源书写死的固定高度/最小高度容器（如 `height:600px` + flex 垂直居中）
  - 8.2 图片按版心限高等比缩放（`max-width:100%` + `max-height:68vh` + `object-fit:contain`），保证一页放得下且不变形
  - 8.3 只要容器里只有一张图就按插图处理（块级、`break-inside/break-after: avoid`）；图片与图注同一个 flex 横排容器时改回竖排
  - 8.4 图注 `break-before: avoid` 跟着图片走，行高/边距归一
  - 8.5 结构兜底与超大 `line-height` 内联样式的纠偏
  - 8.6 去掉章标题上的调试用边框
- `@page { size: A5 !important; }` 强制纸型，压过源 EPUB 自带的 `@page { size: … }`
- 文档：使用说明新增「零、怎么用」（图形窗口三步、输出位置与对应代码行号、界面文字修改位置表、可选命令行）、源 EPUB 目录页三条判据表、常见问题补充插图空白与编码两类问题

### 修复
- 图片与其图注被拆到两页（源书 CSS 固定高度 + 居中容器所致），转换后图片周围大片空白
- 源书写了 `width:100%` 的插图在 `max-height:68vh` 限高下被**横向拉宽变形**（WeasyPrint 保留定宽、只压高度）→ 8.2 增加 `object-fit: contain !important`。实测：`硬派健身` 113 张图、`真需求` 43 张图、`反焦虑` 60 张图全部比例正确，页数与其它图片尺寸均不变
- 章标题被 `height:600px` 容器与红色虚线调试图边框撑出空白
- 目录条目、页眉等继承源书全局链接蓝 / 异常样式
- 插图尺寸过大挤占整页：`硬派健身` 源书插图由 `width:100%` 撑到 108.8 × 178.2mm（占页高 85%），现按 68vh 限制为 74.7 × 122.4mm（占页高 58%），面积约减半

### 计划中
- 完善 CSS 模拟脚注体系，优化长脚注分页
- 目录页识别阈值（链接数 / 字数 / 密度）抽成可配置参数，支持跨多文件目录页合并识别
- 实现双渲染引擎可切换架构（WeasyPrint / Prince / Vivliostyle）
- 增加孤行/寡行控制、页面溢出校验
- 配置化改造，抽离纸张、边距、页眉、字号参数

## [1.0.0] - 2026-09-07

### 新增
- 首次发布
- EPUB 解析 → 标准化 HTML（`epub_to_html.py`）
- WeasyPrint 渲染 PDF（`run.py` + `book.css`）
- 镜像页边距、奇偶页差异化页眉、翻口页码
- 自研自定义页码计数器 `main-pagecounter`，解决原生错乱
- 智能目录系统，基于 `target-counter` 实现真实页码锚点
- 前置页 / 正文页隔离体系
- 右手页起章规则
- 自动过滤 EPUB 原生目录页
- 中文排版优化