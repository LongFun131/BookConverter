import os
import re
import shutil
import subprocess
import tempfile

from ebook_converter.core.models import Document
from ebook_converter.writers.base import BaseWriter


class MobiWriter(BaseWriter):

    @property
    def format_name(self) -> str:
        return 'mobi'

    def write(self, document: Document, output_path: str) -> None:
        if self._try_calibre_convert(document, output_path):
            return

        if self._try_epub_fallback(document, output_path):
            return

        self._fallback_write_txt(document, output_path)

    def _build_full_html(self, document: Document) -> str:
        meta = document.metadata
        parts = []

        parts.append(f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>{meta.title or 'Untitled'}</title>
<style>
body {{ font-family: serif; margin: 1em; }}
h1, h2, h3 {{ text-indent: 0; }}
p {{ text-indent: 1.5em; margin: 0.5em 0; }}
</style>
</head>
<body>
<h1>{meta.title or 'Untitled'}</h1>
""")

        if meta.author:
            parts.append(f"<p><i>by {meta.author}</i></p>\n")

        for chapter in document.chapters:
            parts.append(f"\n<hr/>\n<h2>{chapter.title}</h2>\n")
            parts.append(chapter.content)

        parts.append("\n</body>\n</html>")
        return "\n".join(parts)

    def _try_calibre_convert(self, document: Document, output_path: str) -> bool:
        try:
            tmp_dir = tempfile.mkdtemp()
            html_path = os.path.join(tmp_dir, 'input.html')

            html_content = self._build_full_html(document)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            result = subprocess.run(
                ['ebook-convert', html_path, output_path],
                capture_output=True, text=True, timeout=60
            )

            shutil.rmtree(tmp_dir, ignore_errors=True)
            return result.returncode == 0 and os.path.exists(output_path)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        except Exception:
            return False

    def _try_epub_fallback(self, document: Document, output_path: str) -> bool:
        try:
            from ebook_converter.writers.epub_writer import EpubWriter

            tmp_dir = tempfile.mkdtemp()
            epub_path = os.path.join(tmp_dir, 'temp.epub')

            writer = EpubWriter()
            writer.write(document, epub_path)

            if os.path.exists(epub_path):
                shutil.copy2(epub_path, output_path)
                shutil.rmtree(tmp_dir, ignore_errors=True)
                return True

            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass
        return False

    def _fallback_write_txt(self, document: Document, output_path: str) -> None:
        txt_path = os.path.splitext(output_path)[0] + '.txt'

        lines = []
        meta = document.metadata
        if meta.title:
            lines.append(f"{'=' * 40}")
            lines.append(f"  {meta.title}")
            if meta.author:
                lines.append(f"  by {meta.author}")
            lines.append(f"{'=' * 40}\n")

        for chapter in document.chapters:
            if chapter.title:
                lines.append(f"\n{'─' * 36}")
                lines.append(f"  {chapter.title}")
                lines.append(f"{'─' * 36}\n")

            plain = re.sub(r'<[^>]+>', '', chapter.content)
            plain = re.sub(r'&nbsp;', ' ', plain)
            plain = re.sub(r'&amp;', '&', plain)
            plain = re.sub(r'&lt;', '<', plain)
            plain = re.sub(r'&gt;', '>', plain)
            lines.append(plain.strip())

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
