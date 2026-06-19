[app]

title = BookConverter
package.name = bookconverter
package.domain = org.bookconverter

source.dir = .
source.include_exts = py,json
source.include_patterns = ebook_converter/i18n/*

version = 1.1.0

requirements = python3==3.11.9,
    pillow,
    chardet,
    ebooklib,
    mobi,
    lxml

orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 31
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

p4a.branch = develop
log_level = 2
warn_on_root = 0

android.add_aars = []
android.add_gradle_resources = []
