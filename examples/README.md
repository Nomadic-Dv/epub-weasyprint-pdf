# 示例

本目录包含一个最小可用的示例，展示 EPUB → PDF 的转换效果。

## 文件

- `sample-input.epub` —— 输入（示例电子书，自制，无版权）
- `sample-output.pdf` —— 输出（由本项目转换生成）

## 试一下

```bash
python epub_to_html.py "examples/sample-input.epub" "examples/sample-output.html" examples/assets
python run.py "examples/sample-output.html" "examples/sample-output.pdf"
```

