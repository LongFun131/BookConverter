import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ebook_converter.core.models import Document, Chapter, TocEntry, BookMetadata
from ebook_converter.readers.txt_reader import TxtReader
from ebook_converter.readers.epub_reader import EpubReader
from ebook_converter.readers.mobi_reader import MobiReader


class TestTxtReader:

    def setup_method(self):
        self.reader = TxtReader()
        self.tmp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_can_handle(self):
        assert self.reader.can_handle("test.txt")
        assert self.reader.can_handle("test.text")
        assert not self.reader.can_handle("test.epub")

    def test_read_simple(self):
        path = os.path.join(self.tmp_dir, "test.txt")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("Hello World\nSecond line\n")

        doc = self.reader.read(path)
        assert doc is not None
        assert len(doc.chapters) > 0
        assert "Hello World" in doc.chapters[0].content

    def test_read_chinese(self):
        path = os.path.join(self.tmp_dir, "test_cn.txt")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("第一章 开始\n这是中文内容。\n第二章 继续\n更多中文。\n")

        doc = self.reader.read(path)
        assert doc is not None
        assert len(doc.chapters) >= 2
        assert any("第一章" in ch.title for ch in doc.chapters)

    def test_read_empty(self):
        path = os.path.join(self.tmp_dir, "empty.txt")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("")

        doc = self.reader.read(path)
        assert doc is not None
        assert len(doc.chapters) > 0


class TestDocumentModel:

    def test_create_document(self):
        doc = Document(
            metadata=BookMetadata(title="Test Book", author="Author"),
            chapters=[Chapter(title="Ch1", content="<p>Content</p>")],
            toc=[TocEntry(title="Ch1", level=1, href="chapter_0")],
        )
        assert doc.metadata.title == "Test Book"
        assert len(doc.chapters) == 1

    def test_flat_toc(self):
        child = TocEntry(title="Child", level=2, href="c1")
        parent = TocEntry(title="Parent", level=1, href="p1", children=[child])
        doc = Document(toc=[parent])

        flat = doc.get_flat_toc()
        assert len(flat) == 2
        assert flat[0][0] == "Parent"
        assert flat[1][0] == "Child"
