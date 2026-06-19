import os
from urllib.parse import unquote

from ebooklib import epub

from ebook_converter.core.models import Document, Chapter, TocEntry, BookMetadata
from ebook_converter.readers.base import BaseReader


class EpubReader(BaseReader):

    @property
    def format_name(self) -> str:
        return 'epub'

    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith('.epub')

    def read(self, file_path: str) -> Document:
        book = epub.read_epub(file_path, options={"ignore_ncx": False})

        metadata = self._extract_metadata(book)
        cover_image = self._extract_cover(book)
        chapters = self._extract_chapters(book)
        toc = self._extract_toc(book, chapters)

        return Document(
            metadata=metadata,
            chapters=chapters,
            toc=toc,
            cover_image=cover_image,
            language=metadata.language,
        )

    def _extract_metadata(self, book) -> BookMetadata:
        title = self._get_meta(book, 'title') or ""
        author = self._get_meta(book, 'creator') or ""
        language = self._get_meta(book, 'language') or "en"
        publisher = self._get_meta(book, 'publisher') or ""
        description = self._get_meta(book, 'description') or ""
        isbn = self._get_meta(book, 'ISBN') or ""
        identifier = self._get_meta(book, 'identifier') or ""

        return BookMetadata(
            title=title,
            author=author,
            language=language,
            publisher=publisher,
            description=description,
            isbn=isbn,
            identifier=identifier,
        )

    def _get_meta(self, book, name) -> str:
        values = book.get_metadata('DC', name)
        if values:
            val = values[0]
            if isinstance(val, tuple):
                return str(val[0])
            return str(val)
        return ""

    def _extract_cover(self, book) -> bytes:
        for item in book.get_items():
            if item.get_name() == 'cover-image' or \
               (hasattr(item, 'get_type') and item.get_type() == 9):
                return item.get_content()
            media_type = item.get_type() if hasattr(item, 'get_type') else None
            if hasattr(item, 'media_type') and 'image' in str(getattr(item, 'media_type', '')):
                return item.get_content()
        return None

    def _extract_chapters(self, book) -> list:
        chapters = []
        spine_ids = [item_id for item_id, _ in book.spine]

        for item_id in spine_ids:
            item = book.get_item_with_id(item_id)
            if item is None:
                continue

            media_type = getattr(item, 'media_type', '')
            if 'html' not in media_type and 'xhtml' not in media_type:
                continue

            content = item.get_content().decode('utf-8', errors='replace')
            name = item.get_name()

            title = self._extract_title_from_html(content) or os.path.basename(name)

            chapters.append(Chapter(
                title=title,
                level=1,
                content=content,
                href=name,
            ))

        return chapters

    def _extract_title_from_html(self, html_content: str) -> str:
        import re
        patterns = [
            re.compile(r'<h1[^>]*>(.*?)</h1>', re.IGNORECASE | re.DOTALL),
            re.compile(r'<h2[^>]*>(.*?)</h2>', re.IGNORECASE | re.DOTALL),
            re.compile(r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL),
        ]
        for pattern in patterns:
            match = pattern.search(html_content)
            if match:
                title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                if title:
                    return title
        return ""

    def _extract_toc(self, book, chapters: list) -> list:
        toc_entries = []

        for item in book.get_items():
            if item.get_name() == 'toc.ncx':
                ncx_content = item.get_content().decode('utf-8', errors='replace')
                toc_entries = self._parse_ncx(ncx_content)
                if toc_entries:
                    return toc_entries

        if not toc_entries:
            for item in book.get_items():
                if 'nav' in item.get_name().lower() and \
                   getattr(item, 'media_type', '') == 'application/xhtml+xml':
                    nav_content = item.get_content().decode('utf-8', errors='replace')
                    toc_entries = self._parse_nav(nav_content)
                    if toc_entries:
                        return toc_entries

        if not toc_entries:
            for ch in chapters:
                toc_entries.append(TocEntry(
                    title=ch.title,
                    level=1,
                    href=ch.href,
                ))

        return toc_entries

    def _parse_ncx(self, ncx_content: str) -> list:
        import re
        entries = []

        nav_points = re.findall(
            r'<navPoint[^>]*>(.*?)</navPoint>',
            ncx_content, re.DOTALL
        )

        for np in nav_points:
            label_match = re.search(r'<text>(.*?)</text>', np, re.DOTALL)
            src_match = re.search(r'<content[^>]*src="([^"]*)"', np)

            title = label_match.group(1).strip() if label_match else ""
            href = unquote(src_match.group(1).split('#')[0]) if src_match else ""

            if title:
                entries.append(TocEntry(title=title, level=1, href=href))

        return entries

    def _parse_nav(self, nav_content: str) -> list:
        import re
        entries = []

        nav_matches = re.findall(
            r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
            nav_content, re.DOTALL
        )

        for href, title in nav_matches:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            if clean_title:
                entries.append(TocEntry(
                    title=clean_title,
                    level=1,
                    href=unquote(href.split('#')[0]),
                ))

        return entries
