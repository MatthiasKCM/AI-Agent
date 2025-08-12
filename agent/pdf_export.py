# agent/pdf_export.py
import os
from fpdf import FPDF

def create_pdf(letter_text: str, filename: str = "Anschreiben.pdf") -> str:
    # Unicode-fähig: DejaVuSans.ttf im selben Ordner ablegen
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_left_margin(25)
    pdf.set_right_margin(25)

    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.add_font("DejaVu", "B", font_path, uni=True)
        pdf.set_font("DejaVu", size=11)
        bold = ("DejaVu","B",11)
        normal = ("DejaVu","",11)
    else:
        # Fallback (keine perfekten Umlaute)
        pdf.set_font("Arial", size=11)
        bold = ("Arial","B",11)
        normal = ("Arial","",11)

    lines = [l.rstrip() for l in letter_text.split("\n")]

    for idx, line in enumerate(lines):
        txt = line.strip()

        if idx in (0,1,2):
            pdf.set_font(*normal); pdf.cell(0, 8, txt, ln=1); continue
        if idx == 3: pdf.ln(2); continue
        if 3 < idx < 7:
            pdf.cell(0, 8, txt, ln=1); continue
        if idx == 7: pdf.ln(2); continue

        if (idx == 8 and "," in line) or "datum:" in txt.lower():
            pdf.cell(0, 8, txt, ln=1, align="R"); pdf.ln(2); continue

        if txt.startswith("**") and txt.endswith("**"):
            betreff = txt.strip("* ").replace("Betreff:", "").strip()
            pdf.set_font(*bold)
            pdf.cell(0, 10, betreff, ln=1, align="C")
            pdf.set_font(*normal)
            pdf.ln(2); continue

        if "geehrte" in txt.lower():
            pdf.cell(0, 8, txt, ln=1); pdf.ln(2); continue

        if "mit freundlichen grüßen" in txt.lower():
            pdf.ln(4); pdf.set_font(*normal); pdf.cell(0, 8, txt, ln=1); continue

        if txt == "":
            pdf.ln(3); continue

        pdf.multi_cell(0, 7, txt); pdf.ln(1)

    pdf.output(filename)
    return filename
