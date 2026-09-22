# -*- coding: utf-8 -*-
"""EPUB 转 PDF —— 图形窗口版（不需要命令窗口输入）
   启动：双击 epub2pdf_gui.cmd
   界面：把 epub 路径粘到输入框（或点“选择文件”），点“开始转换”
   输出：成品 PDF 与中间文件都放在本脚本所在目录（_work\\书名\\）
"""
import os
import sys
import subprocess
import threading
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

HERE = os.path.dirname(os.path.abspath(__file__))
WORKROOT = os.path.join(HERE, "_work")
EPUB_TO_HTML = os.path.join(HERE, "epub_to_html.py")
RUN_PY = os.path.join(HERE, "run.py")
GUILOG = os.path.join(WORKROOT, "_gui_run.log")

# 关键：子进程必须用 UTF-8 输出。
# 否则 pythonw 子进程按系统 ANSI 代码页（中文 Windows = cp936/GBK）编码输出，
# 一旦要打印的路径里含 GBK 存不进的字符（例如本项目目录名里的 U+2011 “‑”），
# 子进程会直接 UnicodeEncodeError 崩掉 —— 表现就是“图形窗口转换失败”。
CHILD_ENV = dict(os.environ)
CHILD_ENV["PYTHONIOENCODING"] = "utf-8"
CHILD_ENV["PYTHONUTF8"] = "1"


def safe_name(epub_path):
    """用书名做中间文件夹名：去掉结尾的空格/点（Windows 建目录会自动去掉，路径就对不上），限长 60。"""
    name = os.path.splitext(os.path.basename(epub_path))[0].rstrip(" .")
    return (name or "book")[:60]


def collect_epubs(items):
    """把“路径列表”展开成 epub 列表（目录展开成里面的 *.epub，去重、保序）。"""
    out = []
    for it in items:
        it = it.strip().strip('"').strip()
        if not it:
            continue
        if os.path.isdir(it):
            for f in sorted(os.listdir(it)):
                if f.lower().endswith(".epub"):
                    out.append(os.path.join(it, f))
        else:
            out.append(it)
    seen, uniq = set(), []
    for p in out:
        k = os.path.normcase(os.path.abspath(p))
        if k not in seen:
            seen.add(k)
            uniq.append(p)
    return uniq


def _run(cmd):
    """跑一个子进程；输出统一按 UTF-8 收（配合 CHILD_ENV）。"""
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          env=CHILD_ENV, cwd=HERE)


def convert_one(epub, log):
    """转一本。返回 (成功?, 成品pdf路径或None)。log(str) 用来往界面/日志文件写。"""
    epub = os.path.abspath(epub)
    if not os.path.exists(epub):
        log("[错误] 文件不存在: %s" % epub)
        return False, None
    if not epub.lower().endswith(".epub"):
        log("[跳过] 不是 .epub 文件: %s" % epub)
        return False, None

    name = safe_name(epub)
    work = os.path.join(WORKROOT, name)
    html = os.path.join(work, "book.html")
    pdf = os.path.join(HERE, name + ".pdf")
    os.makedirs(work, exist_ok=True)

    log("")
    log("=" * 62)
    log("转换中: %s" % os.path.basename(epub))
    log("成品  : %s" % pdf)
    log("中间  : %s" % work)
    if os.path.exists(pdf):
        log("注意  : 同名 PDF 已存在，将被覆盖")
    log("=" * 62)

    log("[1/2] 拆书: epub 转成单个 html ...")
    try:
        r = _run([sys.executable, "-X", "utf8", EPUB_TO_HTML, epub, html, work])
    except Exception as ex:
        log("[错误] 启动拆书进程失败: %r" % (ex,))
        return False, None
    log(r.stdout.decode("utf-8", "replace").rstrip())
    if r.returncode != 0 or not os.path.exists(html):
        log("[错误] 拆书失败（返回码 %d）：epub 可能加密、损坏，或者不是标准 epub" % r.returncode)
        log("       中间文件保留在: %s" % work)
        return False, None

    log("[2/2] 排版: html 转成 pdf（页数多时要几秒到几十秒）...")
    try:
        r = _run([sys.executable, "-X", "utf8", RUN_PY, html, pdf])
    except Exception as ex:
        log("[错误] 启动排版进程失败: %r" % (ex,))
        return False, None
    log(r.stdout.decode("utf-8", "replace").rstrip())
    if r.returncode != 0 or not os.path.exists(pdf):
        log("[错误] 排版失败（返回码 %d），中间文件保留在: %s" % (r.returncode, work))
        return False, None

    log("[完成] %s" % pdf)
    return True, pdf


class App:
    def __init__(self, root):
        self.root = root
        self.pdfs = []
        self.busy = False
        self.clean_now = False
        root.title("EPUB 转 PDF")
        root.geometry("780x540")

        tip = ("把 epub 的路径粘贴到下面（资源管理器里选中 epub → 按住 Shift 右键 →「复制文件地址」），"
               "也可以点“选择文件…”。成品 PDF 会放在本程序所在目录。")
        tk.Label(root, text=tip, justify="left", wraplength=740, anchor="w").pack(fill="x", padx=10, pady=(10, 4))

        row = tk.Frame(root)
        row.pack(fill="x", padx=10)
        self.entry = tk.Entry(row)
        self.entry.pack(side="left", fill="x", expand=True)
        tk.Button(row, text="选择文件…", command=self.pick_files, width=12).pack(side="left", padx=4)
        tk.Button(row, text="选择文件夹…", command=self.pick_dir, width=12).pack(side="left")

        row2 = tk.Frame(root)
        row2.pack(fill="x", padx=10, pady=6)
        self.open_var = tk.BooleanVar(value=False)
        tk.Checkbutton(row2, text="转完自动打开 PDF", variable=self.open_var).pack(side="left")
        self.clean_var = tk.BooleanVar(value=True)
        tk.Checkbutton(row2, text="转完删除中间文件（含 _work 整目录）",
                       variable=self.clean_var).pack(side="left", padx=(12, 0))
        tk.Button(row2, text="开始转换", command=self.start, width=12).pack(side="right")
        tk.Button(row2, text="打开成品目录", command=lambda: os.startfile(HERE), width=12).pack(side="right", padx=6)

        self.text = tk.Text(root, height=22, wrap="word")
        self.text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        sb = ttk.Scrollbar(self.text, command=self.text.yview)
        self.text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        self.log("成品 PDF 与中间文件都会放在: %s" % HERE)
        self.log("")
        self.log("中间文件在: %s\\书名\\ （可随时删）" % WORKROOT)
        self.log("")
        self.log("请粘贴 epub 路径后点“开始转换”。")

    # ---------- 界面小工具 ----------
    def log(self, msg):
        line = str(msg)
        try:
            os.makedirs(WORKROOT, exist_ok=True)
            with open(GUILOG, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass
        self.text.insert("end", line + "\n")
        self.text.see("end")
        self.root.update_idletasks()

    def pick_files(self):
        files = filedialog.askopenfilenames(title="选择 epub 文件",
                                            filetypes=[("EPUB 电子书", "*.epub"), ("所有文件", "*.*")])
        if files:
            self.entry.delete(0, "end")
            self.entry.insert(0, " ".join('"%s"' % f for f in files))

    def pick_dir(self):
        d = filedialog.askdirectory(title="选择放 epub 的文件夹（会把里面所有 epub 都转掉）")
        if d:
            self.entry.delete(0, "end")
            self.entry.insert(0, d)

    # ---------- 转换 ----------
    def start(self):
        if self.busy:
            return
        raw = self.entry.get().strip()
        if not raw:
            messagebox.showinfo("提示", "请先粘贴 epub 路径，或点“选择文件”。")
            return
        items = raw.replace('" "', '"|"').split("|")
        if len(items) == 1:
            items = [raw]
        epubs = collect_epubs(items)
        if not epubs:
            messagebox.showwarning("提示", "没认出 epub：请粘贴 .epub 的完整路径，或选择文件。")
            return
        self.busy = True
        self.log("")
        self.log("共 %d 个文件，开始转换 ..." % len(epubs))
        self.clean_now = self.clean_var.get()      # tkinter 变量别在子线程里读，先取好
        threading.Thread(target=self.work, args=(epubs,), daemon=True).start()

    def work(self, epubs):
        ok, fail = 0, 0
        self.pdfs = []
        for e in epubs:
            try:
                good, pdf = convert_one(e, lambda m: self.root.after(0, self.log, m))
            except Exception as ex:  # 兜底：任何异常都写在界面上，窗口不会消失
                self.root.after(0, self.log, "[错误] 转换异常: %r" % (ex,))
                good, pdf = False, None
            if good:
                ok += 1
                self.pdfs.append(pdf)
            else:
                fail += 1
        self.root.after(0, self.done, ok, fail)

    def done(self, ok, fail):
        self.busy = False
        self.log("")
        self.log("=" * 62)
        self.log("全部完成：成功 %d 本，失败 %d 本。成品在: %s" % (ok, fail, HERE))
        self.log("=" * 62)
        if self.open_var.get() and self.pdfs:
            for p in self.pdfs:
                try:
                    os.startfile(p)
                except Exception as ex:
                    self.log("[提示] 打开 PDF 失败: %r" % (ex,))
        # 勾了“转完删除中间文件”就把整个 _work 目录删掉（含里面的日志、各书的中间文件）。
        # 注意：先把上面的日志写完再删，所以界面上照样看得到这次的过程；_work 会消失，
        # 下次转换时自动重建。
        if getattr(self, "clean_now", False):
            self.log("[清理] 删除中间文件目录: %s" % WORKROOT)
            shutil.rmtree(WORKROOT, ignore_errors=True)


def main():
    os.makedirs(WORKROOT, exist_ok=True)
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
