import os

import openai
from datetime import datetime
#Logik um mit OpenAI zu kommunizieren

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_cover_letter(cv_text, job_description, stil, language):
    today = datetime.now().strftime("%d.%m.%Y")
    system_prompt = f"""
    Du bist ein professioneller Bewerbungsschreiber für den DACH‑Markt.

    Ziel: Ein individuelles, flüssig lesbares Anschreiben nach DIN 5008, maximal 300 Wörter, mit klarer Storyline und konkreten Belegen aus CV/Anzeige. Keine Bulletpoints.

    Layout & Pflichtblöcke (alle AUSGEFÜLLT, fehlendes mit klaren Platzhaltern in eckigen Klammern):
    [Dein Name]
    [Deine Adresse]
    [PLZ Ort]

    [Empfänger/Firma]
    [Empfänger-Adresse]
    [PLZ Ort]

    [Ort, Datum: {today}]

    **[Stellenbezeichnung]**  (fett, zentriert, ohne „Betreff:“)

    [Anrede]  (falls Ansprechpartner in der Anzeige erkennbar, benutze ihn; sonst „Sehr geehrte Damen und Herren,“)

    [Fließtext mit 2 Absätzen + kurzer Abschlusszeile]
    - Absatz 1: Relevanz-Statement (warum diese Rolle + 1–2 belegte Stärken). Verknüpfe Jobanforderung mit 1 Mini‑Beispiel (Was? Wie? Ergebnis?).
    - Absatz 2: Technische/Methoden‑Passung (max. 2–3 Qualifikationen), Bezug zum Stack/Produkt, Lernkurve nur wenn nötig. Nenne 1 konkrete Schnittstelle/Aufgabe aus der Anzeige und wie du sie angehst.
    - Abschluss (1 Satz): Gesprächsangebot + Verfügbarkeit.

    Formalia & Stil:
    - Flüssige Übergänge, variierende Satzlängen. Keine Phrasen („Teamplayer“, „leidenschaftlich“ etc.).
    - Jede Aussage möglichst mit Wirkung unterlegt (Kennzahl, Resultat, Prozessverbesserung). Wenn keine Zahl im CV/der Anzeige, kurze qualitative Wirkung nennen.
    - Keine Wiederholung reiner CV‑Aufzählung. Keine Auflistungen/Bullets. Max. 4 Zeilen pro Absatz.
    - Höchstens 2–3 wirklich relevante Qualifikationen; alles andere weglassen.
    - Ton: {stil} | Sprache: {language} | Zielgruppe: Fach‑Hiring.
    - Vermeide gehäufte Füllwörter. Konjunktionen sind erlaubt, aber nicht aneinanderreihen.
    - Wenn Informationen fehlen (z. B. Ansprechpartner, Adresse, Tech‑Stack), nutze präzise Platzhalter in eckigen Klammern, niemals Blöcke auslassen.

    Gib ausschließlich den finalen Brieftext in genau dieser Blockreihenfolge aus, ohne zusätzliche Erklärungen.
    """

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"LEBENSLAUF:\n{cv_text}"},
            {"role": "user", "content": f"STELLENANZEIGE:\n{job_description}"},
            {"role": "user", "content": "Schreibe ein Bewerbungsanschreiben."}
        ]
    )
    return response.choices[0].message.content

def check_cv(cv_text):
    prompt = """
    Du bist ein erfahrener Karriereberater. Analysiere diesen Lebenslauf auf Schwächen, Lücken, Unklarheiten oder Verbesserungspotenzial.
    Gib konkrete, praxisnahe Verbesserungsvorschläge. Antworte stichpunktartig und ehrlich.
    """
    response = client.chat.completions.create(
        model="gpt-5",
        #Liste mit Dics
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"LEBENSLAUF:\n{cv_text}"},
            {"role": "user", "content": "Analysiere und gib Verbesserungsvorschläge."}
        ]
    )
    return response.choices[0].message.content

def uniqueness_check(letter):
    prompt = """
    Du bist Bewerbungsexperte. Prüfe, ob das folgende Anschreiben einzigartig ist oder zu sehr nach Standard klingt.
    Bewerte zuerst kurz (1 Satz). Dann liste bitte stichpunktartig die Passagen oder Formulierungen, die besonders generisch oder austauschbar wirken – und schlage für jeden Punkt eine bessere, individuellere Alternative vor.
    """
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"ANSCHREIBEN:\n{letter}"},
            {"role": "user", "content": "Bewerte Einzigartigkeit und mache Verbesserungsvorschläge."}
        ]
    )
    return response.choices[0].message.content

def improve_letter(letter, kritikpunkte):
    prompt = f"""
    Hier ist ein Bewerbungsschreiben, gefolgt von Kritikpunkten und Verbesserungsvorschlägen.
    Überarbeite das Anschreiben so, dass es die Vorschläge optimal umsetzt. Baue die Kritikpunkte ein, mache es einzigartiger und vermeide alle generischen Floskeln. Gib nur den neuen Text aus!
    

    Anschreiben:
    {letter}

    Kritikpunkte und Verbesserungsvorschläge:
    {kritikpunkte}
    """
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Verbessere das Anschreiben entsprechend."}
        ]
    )
    return response.choices[0].message.content