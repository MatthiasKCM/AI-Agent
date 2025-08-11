import os

import openai
from datetime import datetime
#Logik um mit OpenAI zu kommunizieren

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_cover_letter(cv_text, job_description, stil, language):
    today = datetime.now().strftime("%d.%m.%Y")
    system_prompt = f"""
    Du bist ein professioneller Bewerbungsschreiber.

    Schreibe ein vollständiges Anschreiben nach deutschem DIN‑5008‑Standard.
    Alle Blöcke MÜSSEN vorhanden sein. Platzhalter in eckigen Klammern sind nur in den Kopfblöcken erlaubt (Empfänger/Adresse/Datum etc.). Im Fließtext KEINE Platzhalter.

    Formatierung:
    - Nur der Betreff ist fett und zentriert. Alle anderen Blöcke normal, linksbündig.
    - Maximal 350 Wörter. Wenn es länger wird: zuerst Unwichtiges kürzen.
    - Jeder Absatz max. 4 Zeilen. Keine Bulletpoints. Kein reines Wiederholen des CV.

    Inhalt & Stil:
    - Schreibe natürlich und menschlich: variiere Satzlängen, nutze aktive Verben, setze klare Übergänge.
    - Vermeide Konjunktiv („würde/könnte/möchte“). Präsens oder Präteritum.
    - Fokussiere dich auf maximal 2–3 wirklich relevante Qualifikationen zur konkreten Anzeige.
    - Belege Aussagen kurz („Was? Wie? Ergebnis?“). Wenn keine Zahl vorhanden, eine sachliche qualitative Wirkung nennen – ohne zu erfinden.
    - Nutze die exakten Namen aus der Anzeige (Rolle, Unternehmen, Technologien), sofern vorhanden.
    - Vermeide Floskeln („teamfähig“, „leidenschaftlich“) und Prozess‑Blabla ohne Nutzen.
    - Variere Satzanfänge; pro Absatz höchstens einmal mit „Ich …“ beginnen.
    - Nutze Konjunktionen maßvoll (z. B. „und“, „aber“), um einen natürlichen Fluss zu erzeugen; keine Schachtelketten.

    Struktur (exakt in dieser Reihenfolge, alle Blöcke ausfüllen):
    [Dein Name]
    [Deine Adresse]
    [PLZ Ort]

    [Empfänger/Firma]
    [Empfänger-Adresse]
    [PLZ Ort]

    [Ort, Datum: {today}]

    [Stellenbezeichnung]  (fett, zentriert, ohne „Betreff:“ davor)

    [Anrede]  (wenn ein Ansprechpartner in der Anzeige steht, nutze ihn; sonst „Sehr geehrte Damen und Herren,“)

    [Fließtext – genau 2 Absätze + 1 Abschlusszeile]
    Absatz 1 (3–5 Sätze): Warum diese Rolle bei <Unternehmen> jetzt? Verknüpfe 1–2 Anforderungen aus der Anzeige mit einer kurzen Erfahrung aus dem CV.
    Absatz 2 (3–5 Sätze): Passung zu Stack/Produkt/Arbeitsweise. Nenne 2–3 Qualifikationen mit mini‑Beleg. Keine Platzhalter. Keine Checklisten. Nimm alles aus dem Lebenslauf, NICHTS ERFINDEN!

    Abschluss wie bei einem klassischen Anschreiben.

    [Abschiedsformel]  („Mit freundlichen Grüßen“)
    [Dein Name], Name aus Lebenslauf nehmen

    Stil: {stil}
    Sprache: {language}

    Gib ausschließlich den finalen Brieftext in genau dieser Blockreihenfolge aus, ohne Erklärungen.
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