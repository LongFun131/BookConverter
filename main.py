#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ebook_converter.app import BookConverterApp


def main():
    app = BookConverterApp()
    app.run()


if __name__ == '__main__':
    main()
