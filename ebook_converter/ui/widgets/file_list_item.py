import os

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class FileListItem(BoxLayout):

    def __init__(self, file_path: str, on_remove=None, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 36
        self.spacing = 5

        ext = os.path.splitext(file_path)[1].upper()
        name = os.path.basename(file_path)

        info = Label(
            text=f"[{ext}] {name}",
            font_size=12,
            halign='left',
            valign='middle',
            size_hint_x=0.85,
        )
        info.bind(size=info.setter('text_size'))
        self.add_widget(info)

        if on_remove:
            remove_btn = Button(
                text="×",
                size_hint_x=0.1,
                font_size=16,
                background_color=(0.8, 0.2, 0.2, 1),
            )
            remove_btn.bind(on_press=lambda x: on_remove(self.file_path))
            self.add_widget(remove_btn)
