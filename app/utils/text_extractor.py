from pypdf import PdfReader
from docx import Document
from PIL import Image
import pytesseract
import io

def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().split(".")[-1]

    if ext == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        return " ".join(page.extract_text() or "" for page in reader.pages)

    if ext == "docx":
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)

    if ext == "txt":
        return file_bytes.decode("utf-8")

    if ext in ["jpg", "jpeg", "png"]:
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(image)

    raise ValueError("Unsupported file format")