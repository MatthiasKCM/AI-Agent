from fpdf import FPDF
import os


def create_pdf(letter_text, filename="Anschreiben.pdf", style="klassisch"):
    pdf = FPDF()
    pdf.add_page()

    # Verwende DejaVu als Unicode-Font
    font_path = os.path.join("assets", "fonts", "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=12)

    if style == "modern":
        pdf.set_text_color(40, 70, 200)
    elif style == "kreativ":
        pdf.set_text_color(200, 40, 70)
    else:
        pdf.set_text_color(0, 0, 0)

    pdf.multi_cell(0, 10, letter_text)
    pdf.output(filename)
    return filename