# agent/utils.py
import pymupdf as fitz  # PyMuPDF

def extract_text_from_pdf(file):
    data = file.read()
    with fitz.open(stream=data, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)

