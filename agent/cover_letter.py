import os

import openai
from datetime import datetime
#Logik um mit OpenAI zu kommunizieren

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_cover_letter(cv_text, job_description, stil, language):
    today = datetime.now().strftime("%d.%m.%Y")
    system_prompt = f"""
    Du bist ein professioneller Bewerbungsschreiber für den DACH‑Markt.

    Ziel: Ein individuelles, flüssiges Anschreiben nach DIN 5008, max. 300 Wörter, mit klarer Story und konkreten Belegen aus Lebenslauf und Stellenanzeige. Keine Bulletpoints, keine Prozessaufzählungen.

    Pflichtblöcke (alle AUSGEFÜLLT; fehlende Stammdaten nur in den Kopfblöcken als Platzhalter):
    [Dein Name]
    [Deine Adresse]
    [PLZ Ort]

    [Empfänger/Firma]
    [Empfänger-Adresse]
    [PLZ Ort]

    [Ort, Datum: {today}]

    **[Stellenbezeichnung]**  (fett, zentriert, ohne „Betreff:“)

    [Anrede]  (wenn Ansprechpartner in der Anzeige steht, benutze ihn; sonst „Sehr geehrte Damen und Herren,“)

    Fließtext (genau 2 Absätze + 1 Abschlusszeile):
    - Absatz 1 (3–5 Sätze): Warum diese Rolle bei <Unternehmen> + 1–2 belegte Stärken. Nenne eine konkrete Aufgabe/Anforderung aus der Anzeige und knüpfe sie an eine kurze, greifbare Erfahrung (Was? Wie? Ergebnis?).
    - Absatz 2 (3–5 Sätze): Passung zu Stack/Produkt/Arbeitsweise. Max. 2–3 Qualifikationen mit Mini‑Beleg. Präsens statt Konjunktiv, keine „würde/könnte/möchte“-Formulierungen. Kein Platzhalter im Fließtext. Wenn eine konkrete Info fehlt, formuliere allgemein und wahrheitsgemäß (ohne Erfindungen).
    - Abschluss (1 kurzer Satz): Gesprächsangebot + Verfügbarkeit.

    Stilregeln:
    - Benutze die exakten Namen aus der Anzeige (Unternehmen, Rolle, Technologien), sofern vorhanden.
    - Keine Platzhalter in eckigen Klammern im Fließtext. Niemals Sätze wie „die in der Anzeige genannte Aufgabe [ ... ]“.
    - Vermeide leere Phrasen („leidenschaftlich“, „Teamplayer“) und Prozess‑Blabla („Schnittstellen als Contracts definieren“, „kritische Pfade zuerst testen“) ohne Nutzen.
    - Varriere Satzanfänge; max. einmal „Ich …“ pro Absatz.
    - Belege Aussagen mit Wirkung: Kennzahl oder kurze qualitative Verbesserung. Wenn keine Zahl vorhanden ist, beschreibe Ergebnis knapp („höhere Sichtbarkeit“, „weniger Nacharbeit“), aber ohne zu halluzinieren.
    - Kein Wiederkäuen des CV; nur direkt rollenrelevantes Material.
    - Ton: {stil} | Sprache: {language} | Zielgruppe: Fach‑Hiring.

    Gib ausschließlich den finalen Brieftext in genau dieser Blockreihenfolge aus – ohne Erklärungen, ohne zusätzliche Abschnitte.
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