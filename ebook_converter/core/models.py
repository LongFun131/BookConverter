from dataclasses import dataclass, field


@dataclass
class BookMetadata:
    title: str = ""
    author: str = ""
    language: str = "en"
    publisher: str = ""
    description: str = ""
    isbn: str = ""
    identifier: str = ""


@dataclass
class TocEntry:
    title: str = ""
    level: int = 1
    href: str = ""
    children: list = field(default_factory=list)


@dataclass
class Chapter:
    title: str = ""
    level: int = 1
    content: str = ""
    href: str = ""


@dataclass
class Document:
    metadata: BookMetadata = field(default_factory=BookMetadata)
    chapters: list = field(default_factory=list)
    toc: list = field(default_factory=list)
    cover_image: bytes = None
    language: str = "en"

    def get_flat_toc(self):
        result = []

        def _flatten(entries, depth=0):
            for entry in entries:
                result.append((entry.title, entry.level, entry.href))
                if entry.children:
                    _flatten(entry.children, depth + 1)

        _flatten(self.toc)
        return result

    def find_chapter_by_href(self, href: str):
        for ch in self.chapters:
            if ch.href == href:
                return ch
        return None
