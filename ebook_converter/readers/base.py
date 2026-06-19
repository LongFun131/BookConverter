from abc import ABC, abstractmethod

from ebook_converter.core.models import Document


class BaseReader(ABC):

    @abstractmethod
    def read(self, file_path: str) -> Document:
        pass

    @abstractmethod
    def can_handle(self, file_path: str) -> bool:
        pass

    @property
    @abstractmethod
    def format_name(self) -> str:
        pass
