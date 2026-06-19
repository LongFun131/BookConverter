import os
import re
import shutil
import tempfile

from ebook_converter.core.models import Document, Chapter, TocEntry, BookMetadata
from ebook_converter.core.encoding import detect_and_decode
from ebook_converter.readers.base import BaseReader


class MobiReader(BaseReader):

    @property
    def format_name(self) -> str:
        return 'mobi'

    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith(('.mobi', '.azw', '.azw3', '.prc'))

    def read(self, file_path: str) -> Document:
        import mobi

        tempdir, filepath = mobi.extract(file_path)

        try:
            return self._parse_extracted(tempdir, filepath, file_path)
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)

    def _parse_extracted(self, tempdir: str, filepath: str, original_path: str) -> Document:
        ext = os.path.splitext(filepath)[1].lower()

        if ext == '.epub':
            from ebook_converter.readers.epub_reader import EpubReader
            reader = EpubReader()
            return reader.read(filepath)

        if ext == '.pdf':
            return self._parse_pdf(filepath, original_path)

        return self._parse_html(filepath, original_path)

    def _parse_html(self, filepath: str, original_path: str) -> Document:
        with open(filepath, 'rb') as f:
            raw = f.read()

        content = detect_and_decode(raw)

        base_name = os.path.splitext(os.path.basename(original_path))[0]
        chapters = []
        toc = []

        heading_pattern = re.compile(
            r'<h([1-6])[^>]*>(.*?)</h\1>',
            re.IGNORECASE | re.DOTALL
        )

        parts = re.split(r'(?=<h[1-6][^>]*>)', content, flags=re.IGNORECASE)

        if len(parts) <= 1:
            chapters.append(Chapter(
                title=base_name,
                level=1,
                content=content,
                href="chapter_0",
            ))
            toc.append(TocEntry(title=base_name, level=1, href="chapter_0"))
        else:
            for i, part in enumerate(parts):
                if not part.strip():
                    continue

                match = heading_pattern.search(part)
                if match:
                    level = int(match.group(1))
                    title = re.sub(r'<[^>]+>', '', match.group(2)).strip()
                else:
                    level = 1
                    title = f"Section {i + 1}"

                chapters.append(Chapter(
                    title=title,
                    level=level,
                    content=part,
                    href=f"chapter_{len(chapters)}",
                ))
                toc.append(TocEntry(
                    title=title,
                    level=level,
                    href=f"chapter_{len(chapters) - 1}",
                ))

        metadata = BookMetadata(title=base_name)

        return Document(
            metadata=metadata,
            chapters=chapters,
            toc=toc,
        )

    def _parse_pdf(self, filepath: str, original_path: str) -> Document:
        base_name = os.path.splitext(os.path.basename(original_path))[0]

        chapters = [Chapter(
            title=base_name,
            level=1,
            content=f"<p>PDF content from: {filepath}</p>",
            href="chapter_0",
        )]
        toc = [TocEntry(title=base_name, level=1, href="chapter_0")]

        return Document(
            metadata=BookMetadata(title=base_name),
            chapters=chapters,
            toc=toc,
        )
