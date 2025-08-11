import os

import openai
from datetime import datetime
#Logik um mit OpenAI zu kommunizieren

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_cover_letter(cv_text, job_description, stil, language):
    today = datetime.now().strftime("%d.%m.%Y")
    system_prompt = f"""
    Du bist ein professioneller Bewerbungsschreiber für den DACH‑Markt.

    Ziel: Erstelle ein individuelles, natürlich klingendes Anschreiben nach DIN 5008. Max. 300 Wörter. Keine Bulletpoints, keine Listen, keine Metatexte.

    HARTE REGELN
    - Alle Blöcke MÜSSEN vorhanden sein. Platzhalter in eckigen Klammern sind NUR in den Kopfblöcken erlaubt (z. B. Ansprechpartner, Quelle), NICHT im Fließtext.
    - Verwende Name, Telefonnummer und E‑Mail aus dem Lebenslauf; falls nicht eindeutig vorhanden: Name = „Matthias Popp“, Telefonnummer = „[Telefonnummer]“, E‑Mail = „[E‑Mail]“.
    - Nutze Stellenbezeichnung, Unternehmen, Quelle und Ansprechpartner aus der Anzeige; wenn nicht eindeutig erkennbar, setze im Kopfblock einen Platzhalter in eckigen Klammern.
    - Exakt ZWEI Absätze Fließtext. Jeder Absatz ≤ 4 Zeilen. Keine Checklisten/Prozess‑Blabla ohne Nutzen.
    - Präsens/Präteritum, kein Konjunktiv („würde/könnte/möchte“). Varie­re Satzlängen natürlich (kein Stakkato, keine Bandwurmsätze).
    - Keine zusätzlichen Leerzeilen außer den vorgegebenen Block‑Trennungen. Gib NUR den finalen Brieftext aus.

    FORMAT (exakt so, Reihenfolge und Zeilenumbrüche beibehalten)
    [Dein Name]
    [Deine Adresse]
    [PLZ Ort]
    [Telefonnummer]
    [E‑Mail]

    [Unternehmen]
    [Name Ansprechpartner/in, falls bekannt]
    [Adresse]
    [PLZ Ort]

    [Ort], [Datum: {today}]

    Bewerbung um die Stelle als [Stellenbezeichnung]

    Sehr geehrte/r [Name Ansprechpartner/in] / Damen und Herren,

    [Absatz 1: 3–5 Sätze. Konkreter Bezug auf die Stelle/Quelle. Warum diese Rolle bei diesem Unternehmen jetzt? Verknüpfe 1–2 Anforderungen aus der Anzeige mit einer kurzen Erfahrung aus dem CV (Was? Wie? Ergebnis?). Natürlich, ohne Floskeln.]

    [Absatz 2: 3–5 Sätze. Wie passt dein Stack/Arbeitsweise konkret? Nenne 2–3 Qualifikationen mit Mini‑Beleg („Was? Wie? Ergebnis?“). Keine Platzhalter, keine generischen Phrasen.]

    Über die Einladung zu einem persönlichen Gespräch freue ich mich.

    Mit freundlichen Grüßen

    [Dein Name]

    Stil: {stil}
    Sprache: {language}
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
    Du bist ein erfahrener DACH‑Karriereberater. Analysiere den Lebenslauf prägnant und ehrlich.
    Liefere klare Handlungsanweisungen, keine Allgemeinplätze.

    Strukturiere deine Antwort in genau diesen Abschnitten:
    1) Red Flags & Lücken (stichpunktartig, mit kurzer Begründung)
    2) Wirkung verstärken (wo Kennzahlen, Outcomes, Verantwortungsumfang ergänzt werden können; konkrete Beispiele nennen)
    3) Inhaltliche Schärfung (überflüssige Punkte streichen/verdichten; Dopplungen; deutsche Terminologie vereinheitlichen)
    4) ATS & Lesbarkeit (Datei‑/Sektionstitel, Keywords aus typischen Anzeigen, konsistente Zeitformen)
    5) To‑dos (konkrete Änderungsbefehle im Imperativ, je 1 Zeile)

    Beziehe dich auf den tatsächlichen CV‑Text. Wenn Infos fehlen, fordere gezielt nach („Fehlt: Zeitraum bei Projekt X“, „Fehlt: Tech‑Stack bei Rolle Y“).
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