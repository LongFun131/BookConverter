from ebook_converter.readers.base import BaseReader
from ebook_converter.readers.epub_reader import EpubReader
from ebook_converter.readers.mobi_reader import MobiReader
from ebook_converter.readers.txt_reader import TxtReader
from ebook_converter.readers.pdf_reader import PdfReader
from ebook_converter.readers.md_reader import MdReader

READERS = {
    'epub': EpubReader(),
    'mobi': MobiReader(),
    'txt': TxtReader(),
    'pdf': PdfReader(),
    'md': MdReader(),
}

__all__ = ["BaseReader", "EpubReader", "MobiReader", "TxtReader", "PdfReader", "MdReader", "READERS"]
