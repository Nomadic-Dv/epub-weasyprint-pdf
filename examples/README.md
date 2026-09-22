# 示例

本目录包含一个最小可用的示例，展示 EPUB → PDF 的转换效果。

## 文件

- `sample-input.epub` —— 输入（示例电子书，自制，无版权）
- `sample-output.pdf` —— 输出（由本项目转换生成）

> `sample-output.html` 是转换过程中生成的中间文件，不随仓库提供（已被 `.gitignore` 忽略），
> 按下面的命令跑一次就会在本目录出现。

## 试一下

**图形窗口**：双击项目根目录的 `epub2pdf_gui.cmd`，把 `sample-input.epub` 的路径粘贴进去（或点「选择文件…」），点「开始转换」。

**命令行**（等价，分两步；第 3 个参数是中间文件目录）：
```bash
python epub_to_html.py "examples/sample-input.epub" "examples/_work/sample/book.html" "examples/_work/sample"
python run.py          "examples/_work/sample/book.html" "examples/sample-output.pdf"
```
