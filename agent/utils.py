# agent/utils.py
import pymupdf as fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup


def extract_text_from_pdf(file):
    data = file.read()
    with fitz.open(stream=data, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)
def get_job_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text
    except Exception as e:
        return f"Fehler beim Laden der Stellenanzeige: {e}"
