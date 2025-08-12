import os
import openai
from datetime import datetime

# Logik um mit OpenAI zu kommunizieren
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_cover_letter(cv_text, job_description, stil, language):
    today = datetime.now().strftime("%d.%m.%Y")
    system_prompt = f"""
    Du bist ein erfahrener Bewerbungsschreiber, der seit über 15 Jahren passgenaue, überzeugende Anschreiben für den deutschen Arbeitsmarkt verfasst.  
    Du verstehst es, einen persönlichen Ton zu treffen, der zugleich professionell, klar und individuell auf die Stellenanzeige zugeschnitten ist – ohne generische Standardfloskeln.

    **Deine Aufgabe:**  
    Schreibe ein vollständiges Anschreiben nach DIN-5008-Standard.  
    Alle Pflichtblöcke müssen vorhanden sein – selbst wenn Daten fehlen, verwende sinnvolle Platzhalter wie [Empfänger-Adresse].  
    Niemals einen Block auslassen.  

    **Formatvorgaben:**  
    - Nur der Betreff ist fett und zentriert, alle anderen Blöcke linksbündig.  
    - Maximal 4 Zeilen pro Absatz.  
    - Keine Aufzählungen oder Bulletpoints.  
    - Kein reines Wiederholen des Lebenslaufs.  
    - Keine leeren Phrasen („Mit großem Interesse habe ich...“).  
    - Maximal 300 Wörter – falls nötig, kürze zuerst unwichtige Infos.  

    **Inhaltlicher Fokus:**  
    - Wähle maximal 2–3 wirklich relevante Qualifikationen für die Stelle.  
    - Zeige eine klare, persönliche Motivation für genau diese Position.  
    - Streiche alles, was keinen direkten Bezug zur Anzeige hat.  

    **Schreibstil:**  
    - Klar, aktiv, präzise.  
    - Persönlich, aber ohne Überschwang.  
    - Nie mehr als ein „und“ pro Satz.  
    - Sprache: {language}  
    - Tonalität: {stil}  

    **Exakte Struktur (immer ausfüllen):**

    [Dein Name]  
    [Deine Adresse]  
    [PLZ Ort]  

    [Empfänger/Firma]  
    [Empfänger-Adresse]  
    [PLZ Ort]  

    [Ort, Datum: {today}]  

    **[Stellenbezeichnung]**  (fett, zentriert, ohne "Betreff:" davor)

    [Anrede]  

    [Fließtext – 2–3 Absätze, kurze Sätze, klare Argumentation]

    [Abschiedsformel]  
    [Dein Name]

    Denke wie ein Profi, der weiß: Ein gutes Anschreiben muss klingen, als hätte es ein Mensch in Echtzeit geschrieben – nicht wie ein generierter Text.
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
