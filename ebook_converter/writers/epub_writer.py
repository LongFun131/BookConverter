import os

from ebooklib import epub

from ebook_converter.core.models import Document
from ebook_converter.writers.base import BaseWriter


class EpubWriter(BaseWriter):

    @property
    def format_name(self) -> str:
        return 'epub'

    def write(self, document: Document, output_path: str) -> None:
        book = epub.EpubBook()

        meta = document.metadata
        book.set_identifier(meta.identifier or meta.title or "unknown")
        book.set_title(meta.title or "Untitled")
        book.set_language(meta.language or "en")

        if meta.author:
            book.add_author(meta.author)

        if document.cover_image:
            ext = self._guess_cover_ext(document.cover_image)
            cover_name = f"cover{ext}"
            book.set_cover(cover_name, document.cover_image)

        spine = ['nav']
        toc_items = []
        chapters_written = []

        for i, chapter in enumerate(document.chapters):
            item_name = f"chapter_{i}.xhtml"
            content = self._ensure_xhtml(chapter.content, chapter.title)

            epub_chapter = epub.EpubHtml(
                title=chapter.title or f"Chapter {i + 1}",
                file_name=item_name,
                lang=meta.language or "en",
            )
            epub_chapter.set_content(content.encode('utf-8'))

            book.add_item(epub_chapter)
            spine.append(epub_chapter)
            chapters_written.append(epub_chapter)

        if document.toc:
            toc_items = self._build_epub_toc(document.toc, chapters_written)
            book.toc = toc_items
        else:
            book.toc = [(ch.title, ch) for ch in chapters_written]

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        book.spine = spine

        epub.write_epub(output_path, book)

    def _ensure_xhtml(self, content: str, title: str = "") -> str:
        if content.strip().startswith('<?xml') or content.strip().startswith('<!DOCTYPE'):
            return content

        return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>{title}</title>
    <meta charset="utf-8"/>
    <style>
        body {{ margin: 1em; font-family: serif; }}
        p {{ text-indent: 1.5em; margin: 0.5em 0; }}
        h1, h2, h3 {{ text-indent: 0; }}
    </style>
</head>
<body>
{content}
</body>
</html>"""

    def _build_epub_toc(self, toc_entries, chapters_written) -> list:
        result = []
        chapter_map = {}
        for ch in chapters_written:
            chapter_map[ch.file_name] = ch
            chapter_map[ch.get_name()] = ch

        for entry in toc_entries:
            epub_section = epub.Link(
                entry.href + ".xhtml" if not entry.href.endswith(".xhtml") else entry.href,
                entry.title,
                entry.href,
            )
            if entry.children:
                sub_links = []
                for child in entry.children:
                    sub_links.append(epub.Link(
                        child.href + ".xhtml" if not child.href.endswith(".xhtml") else child.href,
                        child.title,
                        child.href,
                    ))
                result.append((epub.Section(entry.title), sub_links))
            else:
                result.append(epub_section)

        return result

    def _guess_cover_ext(self, image_data: bytes) -> str:
        if image_data[:8] == b'\x89PNG\r\n\x1a\n':
            return '.png'
        if image_data[:2] == b'\xff\xd8':
            return '.jpg'
        if image_data[:4] == b'GIF8':
            return '.gif'
        return '.png'
