from ebook_converter.writers.base import BaseWriter
from ebook_converter.writers.epub_writer import EpubWriter
from ebook_converter.writers.txt_writer import TxtWriter
from ebook_converter.writers.mobi_writer import MobiWriter
from ebook_converter.writers.pdf_writer import PdfWriter
from ebook_converter.writers.md_writer import MdWriter

WRITERS = {
    'epub': EpubWriter(),
    'mobi': MobiWriter(),
    'txt': TxtWriter(),
    'pdf': PdfWriter(),
    'md': MdWriter(),
}

__all__ = ["BaseWriter", "EpubWriter", "TxtWriter", "MobiWriter", "PdfWriter", "MdWriter", "WRITERS"]
