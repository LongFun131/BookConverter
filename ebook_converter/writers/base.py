from abc import ABC, abstractmethod

from ebook_converter.core.models import Document


class BaseWriter(ABC):

    @abstractmethod
    def write(self, document: Document, output_path: str) -> None:
        pass

    @property
    @abstractmethod
    def format_name(self) -> str:
        pass
