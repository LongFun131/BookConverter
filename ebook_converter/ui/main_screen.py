from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window

import os
import threading

from ebook_converter.i18n import t, get_language
from ebook_converter.core.converter import Converter


class MainScreenBuilder:
    def __init__(self, app):
        self.app = app
        self.selected_files = []
        self.output_dir = os.path.expanduser("~/Desktop")
        self.converting = False

    def build(self) -> BoxLayout:
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        root.add_widget(self._build_header())
        root.add_widget(self._build_file_area(), weight=1)
        root.add_widget(self._build_format_bar())
        root.add_widget(self._build_output_bar())
        root.add_widget(self._build_action_bar())
        root.add_widget(self._build_status_bar())

        return root

    def _build_header(self) -> BoxLayout:
        header = BoxLayout(size_hint_y=None, height=50, spacing=10)

        title = Label(
            text=t("app_title"),
            font_size=22,
            bold=True,
            size_hint_x=0.6,
            halign='left',
            valign='middle',
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)

        lang_btn = Button(
            text="EN" if get_language() == "zh_CN" else "中",
            size_hint_x=0.12,
            font_size=14,
        )
        lang_btn.bind(on_press=self._toggle_language)
        header.add_widget(lang_btn)

        settings_btn = Button(
            text=t("settings"),
            size_hint_x=0.15,
            font_size=14,
        )
        settings_btn.bind(on_press=self._show_settings)
        header.add_widget(settings_btn)

        return header

    def _build_file_area(self) -> BoxLayout:
        file_area = BoxLayout(orientation='vertical', spacing=5)

        self.file_list = GridLayout(
            cols=1,
            spacing=2,
            size_hint_y=None,
        )
        self.file_list.bind(minimum_height=self.file_list.setter('height'))

        scroll = ScrollView()
        scroll.add_widget(self.file_list)
        file_area.add_widget(scroll, weight=1)

        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=5)
        add_btn = Button(text=t("select_files"), font_size=14)
        add_btn.bind(on_press=self._pick_files)
        btn_row.add_widget(add_btn)

        clear_btn = Button(text=t("clear_files"), font_size=14, size_hint_x=0.3)
        clear_btn.bind(on_press=self._clear_files)
        btn_row.add_widget(clear_btn)

        file_area.add_widget(btn_row)

        return file_area

    def _build_format_bar(self) -> BoxLayout:
        bar = BoxLayout(size_hint_y=None, height=45, spacing=10)

        src_label = Label(text=t("source_format") + ":", size_hint_x=0.15, font_size=14)
        bar.add_widget(src_label)

        self.src_spinner = Spinner(
            text=t("auto_detect"),
            values=(t("auto_detect"), "EPUB", "MOBI", "TXT"),
            size_hint_x=0.2,
            font_size=13,
        )
        bar.add_widget(self.src_spinner)

        arrow = Label(text="  →  ", font_size=20, size_hint_x=0.1)
        bar.add_widget(arrow)

        tgt_label = Label(text=t("target_format") + ":", size_hint_x=0.15, font_size=14)
        bar.add_widget(tgt_label)

        self.tgt_spinner = Spinner(
            text="EPUB",
            values=("EPUB", "MOBI", "TXT"),
            size_hint_x=0.2,
            font_size=13,
        )
        bar.add_widget(self.tgt_spinner)

        bar.add_widget(Label(size_hint_x=0.1))

        return bar

    def _build_output_bar(self) -> BoxLayout:
        bar = BoxLayout(size_hint_y=None, height=40, spacing=10)

        out_label = Label(text=t("output_dir") + ":", size_hint_x=0.15, font_size=14)
        bar.add_widget(out_label)

        self.out_dir_label = Label(
            text=self.output_dir,
            size_hint_x=0.6,
            font_size=12,
            halign='left',
            valign='middle',
            shorten=True,
        )
        self.out_dir_label.bind(size=self.out_dir_label.setter('text_size'))
        bar.add_widget(self.out_dir_label)

        choose_btn = Button(text="...", size_hint_x=0.1, font_size=14)
        choose_btn.bind(on_press=self._choose_output_dir)
        bar.add_widget(choose_btn)

        return bar

    def _build_action_bar(self) -> BoxLayout:
        bar = BoxLayout(size_hint_y=None, height=50, spacing=10)

        self.progress_bar = ProgressBar(max=100, size_hint_x=0.6)
        bar.add_widget(self.progress_bar)

        self.convert_btn = Button(
            text=t("start_convert"),
            font_size=16,
            bold=True,
            size_hint_x=0.3,
        )
        self.convert_btn.bind(on_press=self._start_convert)
        bar.add_widget(self.convert_btn)

        return bar

    def _build_status_bar(self) -> BoxLayout:
        bar = BoxLayout(size_hint_y=None, height=30)

        self.status_label = Label(
            text=t("supported_formats"),
            font_size=11,
            halign='left',
            valign='middle',
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        bar.add_widget(self.status_label)

        return bar

    def _pick_files(self, *args):
        content = FileChooserIconView(
            path=os.path.expanduser("~"),
            filters=["*.epub", "*.mobi", "*.txt", "*.azw3"],
            multiselect=True,
        )

        def on_selection(instance, selection):
            if selection:
                for f in selection:
                    if f not in self.selected_files:
                        self.selected_files.append(f)
                self._refresh_file_list()
                popup.dismiss()

        content.bind(on_submit=on_selection)

        popup = Popup(
            title=t("select_files"),
            content=content,
            size_hint=(0.9, 0.9),
        )
        popup.open()

    def _refresh_file_list(self):
        self.file_list.clear_widgets()

        if not self.selected_files:
            placeholder = Label(
                text=t("drag_hint"),
                font_size=14,
                size_hint_y=None,
                height=40,
                color=(0.5, 0.5, 0.5, 1),
            )
            self.file_list.add_widget(placeholder)
            return

        for i, filepath in enumerate(self.selected_files):
            row = BoxLayout(size_hint_y=None, height=32, spacing=5)

            name = os.path.basename(filepath)
            ext = os.path.splitext(name)[1].upper()

            info = Label(
                text=f"[{ext}] {name}",
                font_size=12,
                halign='left',
                valign='middle',
                size_hint_x=0.85,
            )
            info.bind(size=info.setter('text_size'))
            row.add_widget(info)

            remove_btn = Button(
                text="×",
                size_hint_x=0.1,
                font_size=16,
                background_color=(0.8, 0.2, 0.2, 1),
            )
            idx = i
            remove_btn.bind(on_press=lambda x, idx=idx: self._remove_file(idx))
            row.add_widget(remove_btn)

            self.file_list.add_widget(row)

    def _remove_file(self, index):
        if 0 <= index < len(self.selected_files):
            self.selected_files.pop(index)
            self._refresh_file_list()

    def _clear_files(self, *args):
        self.selected_files.clear()
        self._refresh_file_list()

    def _choose_output_dir(self, *args):
        content = FileChooserIconView(
            path=self.output_dir,
            dirselect=True,
        )

        def on_submit(instance, selection, touch=None):
            if selection:
                self.output_dir = selection[0]
                self.out_dir_label.text = self.output_dir
                popup.dismiss()

        content.bind(on_submit=on_submit)

        popup = Popup(
            title=t("output_dir_select"),
            content=content,
            size_hint=(0.9, 0.9),
        )
        popup.open()

    def _start_convert(self, *args):
        if self.converting:
            return

        if not self.selected_files:
            self.status_label.text = t("error_no_input")
            return

        target = self.tgt_spinner.text.lower()
        if target not in ('epub', 'mobi', 'txt'):
            self.status_label.text = t("error_unsupported")
            return

        self.converting = True
        self.convert_btn.disabled = True
        self.progress_bar.value = 0
        self.status_label.text = t("converting")

        thread = threading.Thread(target=self._do_convert, args=(target,))
        thread.daemon = True
        thread.start()

    def _do_convert(self, target_format: str):
        converter = self.app.converter
        total = len(self.selected_files)
        success = 0
        fail = 0

        for i, filepath in enumerate(self.selected_files):
            Clock.schedule_once(
                lambda dt, idx=i: self._update_progress(idx, total), 0
            )

            result = converter.convert(filepath, target_format, self.output_dir)
            if result.success:
                success += 1
            else:
                fail += 1

        Clock.schedule_once(
            lambda dt: self._convert_done(success, fail, total), 0
        )

    def _update_progress(self, current, total):
        self.progress_bar.value = (current / total) * 100 if total > 0 else 0
        self.status_label.text = t("conversion_progress", current=current + 1, total=total)

    def _convert_done(self, success, fail, total):
        self.converting = False
        self.convert_btn.disabled = False
        self.progress_bar.value = 100

        parts = []
        if success > 0:
            parts.append(t("success_count", count=success))
        if fail > 0:
            parts.append(t("fail_count", count=fail))

        self.status_label.text = " | ".join(parts) if parts else t("convert_complete")

    def _toggle_language(self, *args):
        current = get_language()
        new_lang = "en_US" if current == "zh_CN" else "zh_CN"
        self.app.switch_language(new_lang)

    def _show_settings(self, *args):
        from kivy.uix.boxlayout import BoxLayout as BL
        from kivy.uix.label import Label as LBL

        content = BL(orientation='vertical', padding=20, spacing=10)

        lang_label = LBL(text=t("language") + ":", font_size=14, size_hint_y=None, height=30)
        content.add_widget(lang_label)

        lang_spinner = Spinner(
            text="中文" if get_language() == "zh_CN" else "English",
            values=("中文", "English"),
            size_hint_y=None,
            height=40,
            font_size=14,
        )
        content.add_widget(lang_spinner)

        close_btn = Button(
            text="OK",
            size_hint_y=None,
            height=40,
            font_size=14,
        )

        def on_close(*args):
            if lang_spinner.text == "中文":
                self.app.switch_language("zh_CN")
            else:
                self.app.switch_language("en_US")
            popup.dismiss()

        close_btn.bind(on_press=on_close)
        content.add_widget(close_btn)

        popup = Popup(
            title=t("settings"),
            content=content,
            size_hint=(0.5, 0.4),
        )
        popup.open()
