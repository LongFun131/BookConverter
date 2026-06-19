import os
import re

from ebook_converter.core.models import Document
from ebook_converter.writers.base import BaseWriter


class PdfWriter(BaseWriter):

    @property
    def format_name(self) -> str:
        return 'pdf'

    def write(self, document: Document, output_path: str) -> None:
        try:
            self._write_with_fpdf2(document, output_path)
        except ImportError:
            self._write_with_reportlab(document, output_path)

    def _write_with_fpdf2(self, document: Document, output_path: str) -> None:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        font_name = "Helvetica"
        font_paths = [
            "assets/fonts/NotoSansSC-Regular.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/simhei.ttf",
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    pdf.add_font("CustomFont", "", fp, uni=True)
                    font_name = "CustomFont"
                    break
                except Exception:
                    continue

        meta = document.metadata
        if meta.title:
            pdf.add_page()
            pdf.set_font(font_name, size=20)
            pdf.cell(0, 20, txt=meta.title, new_x="LMARGIN", new_y="NEXT", align="C")
            if meta.author:
                pdf.set_font(font_name, size=12)
                pdf.cell(0, 10, txt=f"by {meta.author}", new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.ln(10)

        for chapter in document.chapters:
            pdf.add_page()

            if chapter.title:
                pdf.set_font(font_name, size=16)
                pdf.cell(0, 10, txt=chapter.title, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(5)

            plain = self._html_to_plain(chapter.content)
            pdf.set_font(font_name, size=11)
            pdf.multi_cell(0, 7, txt=plain)

        pdf.output(output_path)

    def _write_with_reportlab(self, document: Document, output_path: str) -> None:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            alignment=1,
        )

        meta = document.metadata
        if meta.title:
            story.append(Paragraph(meta.title, title_style))
            if meta.author:
                story.append(Paragraph(f"by {meta.author}", styles['Normal']))
            story.append(Spacer(1, 20))

        for chapter in document.chapters:
            if chapter.title:
                story.append(Paragraph(chapter.title, styles['Heading2']))
                story.append(Spacer(1, 10))

            plain = self._html_to_plain(chapter.content)
            for para in plain.split('\n\n'):
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['Normal']))
                    story.append(Spacer(1, 6))

        doc.build(story)

    def _html_to_plain(self, html: str) -> str:
        text = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&#\d+;', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
