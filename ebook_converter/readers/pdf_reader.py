import os

from ebook_converter.core.models import Document, Chapter, TocEntry, BookMetadata
from ebook_converter.readers.base import BaseReader


class PdfReader(BaseReader):

    @property
    def format_name(self) -> str:
        return 'pdf'

    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith('.pdf')

    def read(self, file_path: str) -> Document:
        try:
            return self._read_with_pdfminer(file_path)
        except ImportError:
            return self._read_with_pypdf(file_path)

    def _read_with_pdfminer(self, file_path: str) -> Document:
        from pdfminer.high_level import extract_text
        from pdfminer.layout import LAParams

        text = extract_text(file_path, laparams=LAParams())

        chapters = self._split_into_chapters(text)
        toc = [TocEntry(title=ch.title, level=1, href=ch.href) for ch in chapters]

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        metadata = BookMetadata(title=base_name)

        return Document(metadata=metadata, chapters=chapters, toc=toc)

    def _read_with_pypdf(self, file_path: str) -> Document:
        import PyPDF2

        chapters = []
        toc = []

        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            full_text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text.append(page_text)

            text = '\n\n'.join(full_text)

        chapters = self._split_into_chapters(text)
        toc = [TocEntry(title=ch.title, level=1, href=ch.href) for ch in chapters]

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        metadata = BookMetadata(title=base_name)

        return Document(metadata=metadata, chapters=chapters, toc=toc)

    def _split_into_chapters(self, text: str) -> list:
        import re

        chapters = []
        heading_pattern = re.compile(
            r'^(#{1,3})\s+(.+)$',
            re.MULTILINE
        )

        parts = heading_pattern.split(text)

        if len(parts) <= 1:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            content = ''.join(f'<p>{p}</p>' for p in paragraphs)
            chapters.append(Chapter(
                title="Content",
                level=1,
                content=content,
                href="chapter_0",
            ))
        else:
            i = 0
            while i < len(parts):
                part = parts[i].strip()
                if not part:
                    i += 1
                    continue

                if i + 2 < len(parts) and part.startswith('#'):
                    level = len(part)
                    title = parts[i + 1].strip()
                    content_text = parts[i + 2].strip() if i + 2 < len(parts) else ""

                    paragraphs = [p.strip() for p in content_text.split('\n') if p.strip()]
                    content = ''.join(f'<p>{p}</p>' for p in paragraphs)

                    chapters.append(Chapter(
                        title=title,
                        level=level,
                        content=content,
                        href=f"chapter_{len(chapters)}",
                    ))
                    i += 3
                else:
                    paragraphs = [p.strip() for p in part.split('\n') if p.strip()]
                    content = ''.join(f'<p>{p}</p>' for p in paragraphs)
                    if content:
                        chapters.append(Chapter(
                            title=f"Section {len(chapters) + 1}",
                            level=1,
                            content=content,
                            href=f"chapter_{len(chapters)}",
                        ))
                    i += 1

        if not chapters:
            chapters.append(Chapter(
                title="Content",
                level=1,
                content=f"<p>{text}</p>",
                href="chapter_0",
            ))

        return chapters
