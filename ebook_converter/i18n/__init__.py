import json
import os

_translations = {}
_current_lang = "zh_CN"


def set_language(lang: str):
    global _current_lang, _translations
    _current_lang = lang
    _translations = _load_language(lang)


def get_language() -> str:
    return _current_lang


def t(key: str, **kwargs) -> str:
    if not _translations:
        set_language(_current_lang)

    text = _translations.get(key, key)

    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass

    return text


def _load_language(lang: str) -> dict:
    i18n_dir = os.path.join(os.path.dirname(__file__), '')
    path = os.path.join(i18n_dir, f'{lang}.json')

    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    fallback = os.path.join(i18n_dir, 'zh_CN.json')
    if os.path.exists(fallback):
        with open(fallback, 'r', encoding='utf-8') as f:
            return json.load(f)

    return {}


def get_available_languages() -> list:
    i18n_dir = os.path.dirname(__file__)
    langs = []
    for f in os.listdir(i18n_dir):
        if f.endswith('.json'):
            langs.append(f[:-5])
    return sorted(langs)


set_language(_current_lang)
