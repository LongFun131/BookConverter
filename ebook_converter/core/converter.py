import os
import logging

from ebook_converter.core.models import Document
from ebook_converter.readers import READERS
from ebook_converter.writers import WRITERS
from ebook_converter.core.utils import get_file_extension, get_format_from_extension

logger = logging.getLogger(__name__)


class ConvertResult:
    def __init__(self, success: bool, message: str = "", output_path: str = ""):
        self.success = success
        self.message = message
        self.output_path = output_path


class Converter:

    def __init__(self):
        self.readers = dict(READERS)
        self.writers = dict(WRITERS)

    def get_supported_input_formats(self) -> list:
        return list(self.readers.keys())

    def get_supported_output_formats(self) -> list:
        return list(self.writers.keys())

    def get_format_for_file(self, file_path: str) -> str:
        ext = get_file_extension(file_path)
        return get_format_from_extension(ext)

    def convert(self, input_path: str, target_format: str, output_dir: str = None) -> ConvertResult:
        if not os.path.exists(input_path):
            return ConvertResult(False, f"File not found: {input_path}")

        src_format = self.get_format_for_file(input_path)
        if not src_format:
            return ConvertResult(False, f"Unsupported input format: {input_path}")

        if src_format not in self.readers:
            return ConvertResult(False, f"No reader for format: {src_format}")

        if target_format not in self.writers:
            return ConvertResult(False, f"No writer for format: {target_format}")

        if src_format == target_format:
            return ConvertResult(False, "Source and target formats are the same")

        try:
            logger.info(f"Reading {input_path} ({src_format})")
            reader = self.readers[src_format]
            document = reader.read(input_path)

            logger.info(f"Writing {target_format}")
            writer = self.writers[target_format]

            from ebook_converter.core.utils import output_path_for
            out_path = output_path_for(input_path, target_format, output_dir)

            writer.write(document, out_path)

            logger.info(f"Conversion complete: {out_path}")
            return ConvertResult(True, "Conversion successful", out_path)

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return ConvertResult(False, f"Conversion failed: {str(e)}")

    def convert_batch(self, file_paths: list, target_format: str, output_dir: str = None) -> list:
        results = []
        for path in file_paths:
            result = self.convert(path, target_format, output_dir)
            results.append((path, result))
        return results
