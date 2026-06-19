import os
import re

from ebook_converter.core.models import Document
from ebook_converter.writers.base import BaseWriter


class MdWriter(BaseWriter):

    @property
    def format_name(self) -> str:
        return 'md'

    def write(self, document: Document, output_path: str) -> None:
        lines = []

        meta = document.metadata
        if meta.title:
            lines.append(f"# {meta.title}\n")
            if meta.author:
                lines.append(f"*by {meta.author}*\n")
            lines.append("---\n")

        for chapter in document.chapters:
            level = min(chapter.level + 1, 6)
            prefix = '#' * level

            if chapter.title:
                lines.append(f"\n{prefix} {chapter.title}\n")

            md_content = self._html_to_markdown(chapter.content)
            lines.append(md_content)
            lines.append("")

        text = '\n'.join(lines)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

    def _html_to_markdown(self, html: str) -> str:
        text = html

        text = re.sub(r'<h([1-6])[^>]*>(.*?)</h\1>', lambda m: '#' * int(m.group(1)) + ' ' + m.group(2), text, flags=re.DOTALL)
        text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
        text = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', text, flags=re.DOTALL)
        text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text, flags=re.DOTALL)
        text = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', text, flags=re.DOTALL)
        text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text, flags=re.DOTALL)
        text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)
        text = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>',r'![\2](\1)', text, flags=re.DOTALL)
        text = re.sub(r'<img[^>]*src="([^"]*)"[^>]*/?>', r'![](\1)', text, flags=re.DOTALL)

        text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', text, flags=re.DOTALL)
        text = re.sub(r'</?[ou]l[^>]*>', '', text)

        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<div[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', lambda m: '> ' + m.group(1).strip(), text, flags=re.DOTALL)
        text = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', lambda m: '```\n' + m.group(1) + '\n```', text, flags=re.DOTALL)
        text = re.sub(r'<hr\s*/?>', '\n---\n', text, flags=re.IGNORECASE)

        text = re.sub(r'<[^>]+>', '', text)

        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&quot;', '"', text)
        text = re.sub(r'&#39;', "'", text)
        text = re.sub(r'&\w+;', '', text)

        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()
