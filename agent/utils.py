import pymupdf as fitz  # PyMuPDF
#Hilfsfunktion, um Daten aus einer Datei zu extrahieren
def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)
