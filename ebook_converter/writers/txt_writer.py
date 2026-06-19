import re

from ebook_converter.core.models import Document
from ebook_converter.writers.base import BaseWriter


class TxtWriter(BaseWriter):

    @property
    def format_name(self) -> str:
        return 'txt'

    def write(self, document: Document, output_path: str) -> None:
        lines = []

        if document.metadata.title:
            lines.append(f"{'=' * 40}")
            lines.append(f"  {document.metadata.title}")
            if document.metadata.author:
                lines.append(f"  Author: {document.metadata.author}")
            lines.append(f"{'=' * 40}")
            lines.append("")

        for i, chapter in enumerate(document.chapters):
            if chapter.title:
                lines.append(f"\n{'─' * 36}")
                lines.append(f"  {chapter.title}")
                lines.append(f"{'─' * 36}\n")

            plain = self._html_to_plain(chapter.content)
            lines.append(plain)
            lines.append("")

        text = "\n".join(lines)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

    def _html_to_plain(self, html: str) -> str:
        text = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&quot;', '"', text)
        text = re.sub(r'&#\d+;', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
