#!/usr/bin/env python3
import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ebook_converter.core.converter import Converter
from ebook_converter.i18n import t, set_language, get_language

VERSION = "1.1.0"
APP_TITLE = "BookConverter"

SUPPORTED_FORMATS = {
    'epub': 'EPUB',
    'mobi': 'MOBI',
    'azw3': 'AZW3',
    'txt': 'TXT',
    'pdf': 'PDF',
    'md': 'MD',
}


class BookConverterApp:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_TITLE} v{VERSION}")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self.converter = Converter()
        self.selected_files = []
        self.output_dir = os.path.expanduser("~/Desktop")
        self.current_lang = "zh_CN"

        set_language(self.current_lang)
        self._setup_ui()

    def _setup_ui(self):
        self.root.configure(bg="#f0f0f0")

        header = tk.Frame(self.root, bg="#2196F3", height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        self.title_label = tk.Label(
            header, text=t("app_title"),
            font=("Microsoft YaHei", 18, "bold"),
            fg="white", bg="#2196F3"
        )
        self.title_label.pack(side=tk.LEFT, padx=15)

        self.lang_btn = tk.Button(
            header, text="EN", font=("Arial", 12),
            command=self._toggle_lang, width=4
        )
        self.lang_btn.pack(side=tk.RIGHT, padx=10)

        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=15, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        file_label_frame = tk.Frame(main_frame, bg="#f0f0f0")
        file_label_frame.pack(fill=tk.X, pady=(0, 5))

        self.file_count_label = tk.Label(
            file_label_frame, text=t("no_file_selected"),
            font=("Microsoft YaHei", 10), bg="#f0f0f0", anchor="w"
        )
        self.file_count_label.pack(side=tk.LEFT)

        btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.add_btn = tk.Button(
            btn_frame, text=t("select_files"),
            font=("Microsoft YaHei", 10), command=self._pick_files,
            bg="#4CAF50", fg="white", padx=15, pady=5
        )
        self.add_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_btn = tk.Button(
            btn_frame, text=t("clear_files"),
            font=("Microsoft YaHei", 10), command=self._clear_files,
            padx=15, pady=5
        )
        self.clear_btn.pack(side=tk.LEFT)

        list_frame = tk.Frame(main_frame, bg="white", relief=tk.SUNKEN, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.file_listbox = tk.Listbox(
            list_frame, font=("Consolas", 10),
            selectmode=tk.EXTENDED, bg="white"
        )
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        format_frame = tk.Frame(main_frame, bg="#f0f0f0")
        format_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(format_frame, text=t("target_format") + ":", font=("Microsoft YaHei", 10), bg="#f0f0f0").pack(side=tk.LEFT)

        self.target_var = tk.StringVar(value="EPUB")
        self.target_combo = ttk.Combobox(
            format_frame, textvariable=self.target_var,
            values=["EPUB", "MOBI", "TXT", "PDF", "MD"],
            state="readonly", width=10, font=("Microsoft YaHei", 10)
        )
        self.target_combo.pack(side=tk.LEFT, padx=(10, 20))

        tk.Label(format_frame, text=t("output_dir") + ":", font=("Microsoft YaHei", 10), bg="#f0f0f0").pack(side=tk.LEFT)

        self.outdir_label = tk.Label(
            format_frame, text=self.output_dir,
            font=("Consolas", 9), bg="#f0f0f0", anchor="w"
        )
        self.outdir_label.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)

        self.outdir_btn = tk.Button(
            format_frame, text="...", command=self._pick_dir, width=3
        )
        self.outdir_btn.pack(side=tk.LEFT)

        action_frame = tk.Frame(main_frame, bg="#f0f0f0")
        action_frame.pack(fill=tk.X, pady=(0, 5))

        self.progress = ttk.Progressbar(action_frame, length=400, mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.convert_btn = tk.Button(
            action_frame, text=t("start_convert"),
            font=("Microsoft YaHei", 12, "bold"),
            command=self._start_convert,
            bg="#2196F3", fg="white", padx=20, pady=8
        )
        self.convert_btn.pack(side=tk.RIGHT)

        self.status_label = tk.Label(
            main_frame, text=t("supported_formats"),
            font=("Microsoft YaHei", 9), bg="#f0f0f0", anchor="w",
            fg="#666666"
        )
        self.status_label.pack(fill=tk.X)

    def _toggle_lang(self):
        if self.current_lang == "zh_CN":
            self.current_lang = "en_US"
            self.lang_btn.config(text="中")
        else:
            self.current_lang = "zh_CN"
            self.lang_btn.config(text="EN")

        set_language(self.current_lang)
        self.title_label.config(text=t("app_title"))
        self.add_btn.config(text=t("select_files"))
        self.clear_btn.config(text=t("clear_files"))
        self.convert_btn.config(text=t("start_convert"))
        self.file_count_label.config(text=t("no_file_selected") if not self.selected_files else t("file_added", count=len(self.selected_files)))
        self.status_label.config(text=t("supported_formats"))

    def _pick_files(self):
        files = filedialog.askopenfilenames(
            title=t("select_files"),
            filetypes=[
                ("E-Books", "*.epub *.mobi *.txt *.pdf *.md *.azw3"),
                ("EPUB", "*.epub"),
                ("MOBI/AZW3", "*.mobi *.azw3"),
                ("TXT", "*.txt"),
                ("PDF", "*.pdf"),
                ("Markdown", "*.md"),
                ("All files", "*.*"),
            ]
        )
        if files:
            for f in files:
                if f not in self.selected_files:
                    self.selected_files.append(f)
            self._refresh_list()

    def _clear_files(self):
        self.selected_files.clear()
        self._refresh_list()

    def _refresh_list(self):
        self.file_listbox.delete(0, tk.END)
        for f in self.selected_files:
            name = os.path.basename(f)
            ext = os.path.splitext(name)[1].upper()
            self.file_listbox.insert(tk.END, f"[{ext}] {name}")

        count = len(self.selected_files)
        if count > 0:
            self.file_count_label.config(text=t("file_added", count=count))
        else:
            self.file_count_label.config(text=t("no_file_selected"))

    def _pick_dir(self):
        d = filedialog.askdirectory(title=t("output_dir_select"), initialdir=self.output_dir)
        if d:
            self.output_dir = d
            self.outdir_label.config(text=d)

    def _start_convert(self):
        if not self.selected_files:
            messagebox.showwarning(APP_TITLE, t("error_no_input"))
            return

        target = self.target_var.get().lower()
        if target not in SUPPORTED_FORMATS:
            messagebox.showwarning(APP_TITLE, t("error_unsupported"))
            return

        self.convert_btn.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.status_label.config(text=t("converting"))

        thread = threading.Thread(target=self._do_convert, args=(target,))
        thread.daemon = True
        thread.start()

    def _do_convert(self, target_format):
        total = len(self.selected_files)
        success = 0
        fail = 0

        for i, filepath in enumerate(self.selected_files):
            self.root.after(0, self._update_progress, i, total)

            result = self.converter.convert(filepath, target_format, self.output_dir)
            if result.success:
                success += 1
            else:
                fail += 1

        self.root.after(0, self._convert_done, success, fail)

    def _update_progress(self, current, total):
        self.progress["value"] = (current / total) * 100 if total > 0 else 0
        self.status_label.config(text=t("conversion_progress", current=current + 1, total=total))

    def _convert_done(self, success, fail):
        self.convert_btn.config(state=tk.NORMAL)
        self.progress["value"] = 100

        parts = []
        if success > 0:
            parts.append(t("success_count", count=success))
        if fail > 0:
            parts.append(t("fail_count", count=fail))

        msg = " | ".join(parts) if parts else t("convert_complete")
        self.status_label.config(text=msg)
        messagebox.showinfo(APP_TITLE, msg)

    def run(self):
        self.root.mainloop()


def main():
    app = BookConverterApp()
    app.run()


if __name__ == '__main__':
    main()
