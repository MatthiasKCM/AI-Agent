from fpdf import FPDF
import os


from fpdf import FPDF

def create_pdf(letter_text, filename="Anschreiben.pdf"):
    letter_text = letter_text.replace("–", "-")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_left_margin(25)
    pdf.set_right_margin(25)
    pdf.set_font("Arial", size=11)

    lines = [l.rstrip() for l in letter_text.split("\n")]

    for idx, line in enumerate(lines):
        # Absender: Immer die ersten 3 Zeilen, einfach normal ausgeben
        if idx == 0 or idx == 1 or idx == 2:
            pdf.cell(0, 8, line, ln=1)
            continue
        # Leere Zeile nach Absender
        if idx == 3:
            pdf.ln(2)
        # Empfänger-Block: bis zu einer weiteren Leerzeile oder max. 3 weitere Zeilen
        if 3 < idx < 7:
            pdf.cell(0, 8, line, ln=1)
            continue
        # Leerzeile nach Empfänger
        if idx == 7:
            pdf.ln(2)
        # Datum-Zeile (rechtsbündig)
        if "datum:" in line.lower() or (idx == 8 and "," in line):
            pdf.cell(0, 8, line.strip(), ln=1, align="R")
            pdf.ln(2)
            continue
        # Betreff fett und links-zentriert
        if "**" in line.lower():
            pdf.set_font("Arial", "B", 11)
            betreff = line.replace("**", "").replace("Betreff:", "").strip()
            pdf.multi_cell(0, 10, betreff, align="L")
            pdf.set_font("Arial", "", 11)
            pdf.ln(2)
            continue
        # Anrede (klassisch, direkt nach Betreff)
        if "geehrte" in line.lower():
            pdf.cell(0, 8, line.strip(), ln=1)
            pdf.ln(2)
            continue
        # Abschiedsformel fett (optional)
        if "mit freundlichen grüßen" in line.lower():
            pdf.ln(4)
            pdf.set_font("Arial","", 11)
            pdf.cell(0, 8, line.strip(), ln=1)
            pdf.set_font("Arial", "", 11)
            continue
        # Name unter Grußformel (leicht mehr Abstand)
        if idx == len(lines) - 1:
            pdf.ln(2)
            pdf.cell(0, 8, line.strip(), ln=1)
            continue
        # Leere Zeile für Absatz
        if line.strip() == "":
            pdf.ln(3)
            continue
        # Fließtext
        pdf.multi_cell(0, 7, line.strip())
        pdf.ln(1)

    pdf.output(filename)
    return filename