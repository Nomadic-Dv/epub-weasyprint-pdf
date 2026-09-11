# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- 完善 CSS 模拟脚注体系，优化长脚注分页
- 升级目录页智能识别，兼容非常规 EPUB
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