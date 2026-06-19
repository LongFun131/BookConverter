import os

from ebook_converter.core.models import Document, Chapter, TocEntry, BookMetadata
from ebook_converter.readers.base import BaseReader


class TxtReader(BaseReader):

    @property
    def format_name(self) -> str:
        return 'txt'

    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith(('.txt', '.text'))

    def read(self, file_path: str) -> Document:
        from ebook_converter.core.encoding import detect_and_decode

        with open(file_path, 'rb') as f:
            raw = f.read()

        text = detect_and_decode(raw)
        lines = text.splitlines()

        chapters = []
        toc = []
        current_title = ""
        current_lines = []

        chapter_patterns = [
            __import__('re').compile(r'^第[一二三四五六七八九十百千万\d]+[章回节卷篇]'),
            __import__('re').compile(r'^Chapter\s+\d+', __import__('re').IGNORECASE),
            __import__('re').compile(r'^CHAPTER\s+\d+'),
            __import__('re').compile(r'^第\d+章'),
            __import__('re').compile(r'^\d+\.\s+.+'),
        ]

        import re

        for line in lines:
            stripped = line.strip()
            is_chapter = False
            for pattern in chapter_patterns:
                if pattern.match(stripped):
                    is_chapter = True
                    break

            if is_chapter:
                if current_lines:
                    content = '<p>' + '</p><p>'.join(
                        l.strip() for l in current_lines if l.strip()
                    ) + '</p>'
                    chapters.append(Chapter(
                        title=current_title,
                        level=1,
                        content=content,
                        href=f"chapter_{len(chapters)}",
                    ))
                    toc.append(TocEntry(
                        title=current_title,
                        level=1,
                        href=f"chapter_{len(chapters) - 1}",
                    ))
                current_title = stripped
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines or current_title:
            content = '<p>' + '</p><p>'.join(
                l.strip() for l in current_lines if l.strip()
            ) + '</p>'
            chapters.append(Chapter(
                title=current_title or "全文",
                level=1,
                content=content,
                href=f"chapter_{len(chapters)}",
            ))
            toc.append(TocEntry(
                title=current_title or "全文",
                level=1,
                href=f"chapter_{len(chapters) - 1}",
            ))

        if not chapters:
            content = '<p>' + '</p><p>'.join(
                l.strip() for l in lines if l.strip()
            ) + '</p>'
            chapters.append(Chapter(
                title="全文",
                level=1,
                content=content,
                href="chapter_0",
            ))
            toc.append(TocEntry(title="全文", level=1, href="chapter_0"))

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        metadata = BookMetadata(title=base_name)

        return Document(
            metadata=metadata,
            chapters=chapters,
            toc=toc,
        )
