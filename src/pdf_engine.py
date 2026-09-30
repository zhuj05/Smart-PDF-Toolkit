import io
from typing import BinaryIO, Optional


class PDFEngine:
    """PDF operations that work with browser-provided bytes and in-memory streams."""

    @staticmethod
    def _as_stream(source) -> BinaryIO:
        if isinstance(source, (bytes, bytearray, memoryview)):
            return io.BytesIO(bytes(source))
        if isinstance(source, str):
            return open(source, "rb")
        if hasattr(source, "seek"):
            source.seek(0)
        return source

    @staticmethod
    def _reader(source, password: Optional[str] = None):
        from pypdf import PdfReader
        reader = PdfReader(PDFEngine._as_stream(source))
        if reader.is_encrypted:
            if password is None or reader.decrypt(password) == 0:
                raise ValueError("PDF 已加密，請先使用正確密碼解密")
        return reader

    @staticmethod
    def _save_output(writer, output_dest):
        if isinstance(output_dest, str):
            with open(output_dest, "wb") as output_file:
                writer.write(output_file)
        else:
            if hasattr(output_dest, "seek"):
                output_dest.seek(0)
                if hasattr(output_dest, "truncate"):
                    output_dest.truncate(0)
            writer.write(output_dest)
            if hasattr(output_dest, "seek"):
                output_dest.seek(0)

    @staticmethod
    def page_count(input_source) -> int:
        return len(PDFEngine._reader(input_source).pages)

    @staticmethod
    def merge_pdfs(file_inputs, output_dest):
        from pypdf import PdfWriter
        writer = PdfWriter()
        for source in file_inputs:
            reader = PDFEngine._reader(source)
            writer.append(reader)
        PDFEngine._save_output(writer, output_dest)

    @staticmethod
    def split_pdf(input_source, page_ranges: list[int], output_dest):
        from pypdf import PdfWriter
        reader = PDFEngine._reader(input_source)
        writer = PdfWriter()
        for index in page_ranges:
            if not 0 <= index < len(reader.pages):
                raise ValueError(f"頁碼索引超出範圍：{index + 1}")
            writer.add_page(reader.pages[index])
        if not page_ranges:
            raise ValueError("至少需要選取一頁")
        PDFEngine._save_output(writer, output_dest)

    @staticmethod
    def rotate_pages(
        input_source,
        output_dest,
        angle: int = 90,
        page_indices: Optional[list[int]] = None,
    ):
        if angle not in (90, 180, 270):
            raise ValueError("旋轉角度必須是 90、180 或 270 度")
        from pypdf import PdfWriter
        reader = PDFEngine._reader(input_source)
        writer = PdfWriter()
        for index, page in enumerate(reader.pages):
            if page_indices is None or index in page_indices:
                page.rotate(angle)
            writer.add_page(page)
        PDFEngine._save_output(writer, output_dest)

    @staticmethod
    def crop_pages(
        input_source,
        output_dest,
        left: float = 0,
        bottom: float = 0,
        right: float = 0,
        top: float = 0,
    ):
        margins = (left, bottom, right, top)
        if any(value < 0 for value in margins):
            raise ValueError("裁切邊距不可為負數")
        from pypdf import PdfWriter
        reader = PDFEngine._reader(input_source)
        writer = PdfWriter()
        for page in reader.pages:
            box = page.mediabox
            new_left = float(box.left) + left
            new_bottom = float(box.bottom) + bottom
            new_right = float(box.right) - right
            new_top = float(box.top) - top
            if new_left >= new_right or new_bottom >= new_top:
                raise ValueError("裁切邊距過大，頁面尺寸必須大於零")
            page.mediabox.lower_left = (new_left, new_bottom)
            page.mediabox.upper_right = (new_right, new_top)
            page.cropbox.lower_left = (new_left, new_bottom)
            page.cropbox.upper_right = (new_right, new_top)
            page.cropbox.lower_left = (new_left, new_bottom)
            page.cropbox.upper_right = (new_right, new_top)
            writer.add_page(page)
        PDFEngine._save_output(writer, output_dest)

    @staticmethod
    def extract_text(input_source) -> str:
        reader = PDFEngine._reader(input_source)
        content = []
        for index, page in enumerate(reader.pages):
            content.append(f"--- [Page {index + 1}] ---\n{page.extract_text() or ''}")
        return "\n\n".join(content)

    @staticmethod
    def encrypt_pdf(input_source, output_dest, password: str):
        if not password:
            raise ValueError("加密密碼不可空白")
        from pypdf import PdfWriter
        reader = PDFEngine._reader(input_source)
        writer = PdfWriter()
        writer.append(reader)
        writer.encrypt(user_password=password)
        PDFEngine._save_output(writer, output_dest)

    @staticmethod
    def decrypt_pdf(input_source, output_dest, password: str) -> bool:
        from pypdf import PdfReader, PdfWriter
        reader = PdfReader(PDFEngine._as_stream(input_source))
        if reader.is_encrypted and reader.decrypt(password) == 0:
            return False
        writer = PdfWriter()
        writer.append(reader)
        PDFEngine._save_output(writer, output_dest)
        return True

    @staticmethod
    def update_metadata(input_source, output_dest, metadata: dict[str, Optional[str]]):
        from pypdf import PdfWriter
        reader = PDFEngine._reader(input_source)
        writer = PdfWriter()
        writer.append(reader)
        formatted_metadata = {
            key if key.startswith("/") else f"/{key}": str(value)
            for key, value in metadata.items()
            if value is not None and str(value).strip()
        }
        if formatted_metadata:
            writer.add_metadata(formatted_metadata)
        PDFEngine._save_output(writer, output_dest)

    @staticmethod
    def add_watermark(input_source, output_dest, watermark_text: str = "CONFIDENTIAL"):
        if not watermark_text:
            raise ValueError("浮水印文字不可空白")
        from pypdf import PdfReader, PdfWriter
        from reportlab.lib.colors import Color
        from reportlab.pdfgen import canvas

        reader = PDFEngine._reader(input_source)
        writer = PdfWriter()
        for page in reader.pages:
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            overlay_stream = io.BytesIO()
            pdf_canvas = canvas.Canvas(overlay_stream, pagesize=(width, height))
            pdf_canvas.saveState()
            pdf_canvas.setFillColor(Color(0.5, 0.5, 0.5, alpha=0.30))
            pdf_canvas.setFont("Helvetica-Bold", max(18, min(width, height) * 0.07))
            pdf_canvas.translate(width / 2, height / 2)
            pdf_canvas.rotate(45)
            pdf_canvas.drawCentredString(0, 0, watermark_text)
            pdf_canvas.restoreState()
            pdf_canvas.save()
            overlay_stream.seek(0)
            overlay_page = PdfReader(overlay_stream).pages[0]
            page.merge_page(overlay_page)
            writer.add_page(page)
        PDFEngine._save_output(writer, output_dest)
