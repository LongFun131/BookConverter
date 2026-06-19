import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ebook_converter.core.models import Document, Chapter, TocEntry, BookMetadata
from ebook_converter.writers.txt_writer import TxtWriter
from ebook_converter.writers.epub_writer import EpubWriter


class TestTxtWriter:

    def setup_method(self):
        self.writer = TxtWriter()
        self.tmp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_write_simple(self):
        doc = Document(
            metadata=BookMetadata(title="Test"),
            chapters=[Chapter(title="Chapter 1", content="<p>Hello World</p>")],
        )
        out_path = os.path.join(self.tmp_dir, "output.txt")
        self.writer.write(doc, out_path)

        assert os.path.exists(out_path)
        with open(out_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "Hello World" in content
        assert "Chapter 1" in content

    def test_html_to_plain(self):
        writer = TxtWriter()
        result = writer._html_to_plain("<p>Hello</p><p>World</p>")
        assert "Hello" in result
        assert "World" in result
        assert "<p>" not in result


class TestEpubWriter:

    def setup_method(self):
        self.writer = EpubWriter()
        self.tmp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_write_epub(self):
        doc = Document(
            metadata=BookMetadata(title="Test Book", author="Author", language="en"),
            chapters=[
                Chapter(title="Chapter 1", content="<p>Content 1</p>", href="ch1"),
                Chapter(title="Chapter 2", content="<p>Content 2</p>", href="ch2"),
            ],
            toc=[
                TocEntry(title="Chapter 1", level=1, href="ch1"),
                TocEntry(title="Chapter 2", level=1, href="ch2"),
            ],
        )
        out_path = os.path.join(self.tmp_dir, "output.epub")
        self.writer.write(doc, out_path)

        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0

    def test_ensure_xhtml(self):
        writer = EpubWriter()
        result = writer._ensure_xhtml("<p>Content</p>", "Title")
        assert '<?xml' in result
        assert "Title" in result
        assert "<p>Content</p>" in result
