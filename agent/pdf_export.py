# agent/pdf_export.py
from fpdf import FPDF

def create_pdf(letter_text, filename="Anschreiben.pdf"):
    # minimal – entspricht deinem ursprünglichen Ansatz
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_left_margin(25)
    pdf.set_right_margin(25)
    pdf.set_font("Arial", size=11)

    lines = [l.rstrip() for l in letter_text.split("\n")]
    for line in lines:
        txt = line.strip()
        if txt == "":
            pdf.ln(3)
            continue
        if txt.startswith("**") and txt.endswith("**"):
            pdf.set_font("Arial", "B", 11)
            betreff = txt.strip("* ").replace("Betreff:", "").strip()
            pdf.multi_cell(0, 10, betreff, align="L")
            pdf.set_font("Arial", "", 11)
            pdf.ln(2)
            continue
        pdf.multi_cell(0, 7, txt)
        pdf.ln(1)

    pdf.output(filename)
    return filename
