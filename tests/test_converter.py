import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ebook_converter.core.converter import Converter


class TestConverter:

    def setup_method(self):
        self.converter = Converter()
        self.tmp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_supported_formats(self):
        assert 'epub' in self.converter.get_supported_input_formats()
        assert 'mobi' in self.converter.get_supported_input_formats()
        assert 'txt' in self.converter.get_supported_input_formats()
        assert 'epub' in self.converter.get_supported_output_formats()
        assert 'mobi' in self.converter.get_supported_output_formats()
        assert 'txt' in self.converter.get_supported_output_formats()

    def test_txt_to_epub(self):
        txt_path = os.path.join(self.tmp_dir, "input.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("第一章 测试\n这是内容。\n第二章 继续\n更多内容。")

        out_dir = os.path.join(self.tmp_dir, "output")
        result = self.converter.convert(txt_path, 'epub', out_dir)

        assert result.success, result.message
        assert os.path.exists(result.output_path)

    def test_txt_to_txt_same_format(self):
        txt_path = os.path.join(self.tmp_dir, "input.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("test content")

        result = self.converter.convert(txt_path, 'txt')
        assert not result.success

    def test_nonexistent_file(self):
        result = self.converter.convert("/nonexistent/file.txt", 'epub')
        assert not result.success

    def test_batch_convert(self):
        for i in range(3):
            path = os.path.join(self.tmp_dir, f"book{i}.txt")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"Book {i}\nContent {i}")

        files = [
            os.path.join(self.tmp_dir, f"book{i}.txt")
            for i in range(3)
        ]
        out_dir = os.path.join(self.tmp_dir, "batch_out")
        results = self.converter.convert_batch(files, 'epub', out_dir)

        assert len(results) == 3
        assert all(r.success for _, r in results)
