import os
import re

from ebook_converter.core.models import Document, Chapter, TocEntry, BookMetadata
from ebook_converter.core.encoding import detect_and_decode
from ebook_converter.readers.base import BaseReader


class MdReader(BaseReader):

    @property
    def format_name(self) -> str:
        return 'md'

    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith(('.md', '.markdown'))

    def read(self, file_path: str) -> Document:
        with open(file_path, 'rb') as f:
            raw = f.read()

        text = detect_and_decode(raw)

        chapters = self._parse_markdown(text)
        toc = self._build_toc(chapters)

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        metadata = BookMetadata(title=base_name)

        return Document(metadata=metadata, chapters=chapters, toc=toc)

    def _parse_markdown(self, text: str) -> list:
        chapters = []
        lines = text.split('\n')

        current_title = ""
        current_level = 1
        current_lines = []

        for line in lines:
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if heading_match:
                if current_lines or current_title:
                    content = self._lines_to_html(current_lines)
                    chapters.append(Chapter(
                        title=current_title or "Untitled",
                        level=current_level,
                        content=content,
                        href=f"chapter_{len(chapters)}",
                    ))

                current_level = len(heading_match.group(1))
                current_title = heading_match.group(2).strip()
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines or current_title:
            content = self._lines_to_html(current_lines)
            chapters.append(Chapter(
                title=current_title or "Content",
                level=current_level,
                content=content,
                href=f"chapter_{len(chapters)}",
            ))

        if not chapters:
            content = self._lines_to_html(lines)
            chapters.append(Chapter(
                title="Content",
                level=1,
                content=content,
                href="chapter_0",
            ))

        return chapters

    def _lines_to_html(self, lines: list) -> str:
        html_parts = []
        in_list = False
        in_code_block = False
        code_lines = []

        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    html_parts.append(f'<pre><code>{"".join(code_lines)}</code></pre>')
                    code_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            stripped = line.strip()

            if not stripped:
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                html_parts.append('')
                continue

            if stripped.startswith('- ') or stripped.startswith('* '):
                if not in_list:
                    html_parts.append('<ul>')
                    in_list = True
                html_parts.append(f'<li>{stripped[2:]}</li>')
                continue

            if re.match(r'^\d+\.\s', stripped):
                if not in_list:
                    html_parts.append('<ol>')
                    in_list = True
                html_parts.append(f'<li>{re.sub(r"^\d+\.\s", "", stripped)}</li>')
                continue

            if in_list:
                html_parts.append('</ul>')
                in_list = False

            paragraph = self._inline_formatting(stripped)
            html_parts.append(f'<p>{paragraph}</p>')

        if in_list:
            html_parts.append('</ul>')

        if in_code_block and code_lines:
            html_parts.append(f'<pre><code>{"".join(code_lines)}</code></pre>')

        return '\n'.join(html_parts)

    def _inline_formatting(self, text: str) -> str:
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
        return text

    def _build_toc(self, chapters: list) -> list:
        toc = []
        for ch in chapters:
            toc.append(TocEntry(
                title=ch.title,
                level=ch.level,
                href=ch.href,
            ))
        return toc
