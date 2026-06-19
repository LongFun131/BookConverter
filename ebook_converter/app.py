from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.properties import StringProperty

from ebook_converter.i18n import set_language, get_language, t
from ebook_converter.core.converter import Converter

Window.size = (800, 600)


class MainScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class BookConverterApp(App):
    current_lang = StringProperty("zh_CN")

    def build(self):
        self.title = "BookConverter"
        self.converter = Converter()
        set_language(self.current_lang)

        from ebook_converter.ui.main_screen import MainScreenBuilder
        builder = MainScreenBuilder(self)
        return builder.build()

    def switch_language(self, lang: str):
        self.current_lang = lang
        set_language(lang)
        self.title = t("app_title")

    def get_t(self, key, **kwargs):
        return t(key, **kwargs)
