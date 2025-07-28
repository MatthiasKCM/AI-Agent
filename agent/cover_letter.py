import os

import openai
from datetime import datetime
#Logik um mit OpenAI zu kommunizieren

client = openai.OpenAI(api_key="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")
#Tagesdatum


def generate_cover_letter(cv_text, job_description, stil, language):
    today = datetime.now().strftime("%d.%m.%Y")
    system_prompt = f"""
Du bist ein professioneller Bewerbungsschreiber. 
Schreibe ein individuelles, professionelles Bewerbungsanschreiben im deutschen Standardlayout. 
Maximal eine DIN-A4-Seite, 3–5 Absätze.Maximal 350 Wörter. 
Keine Aufzählungen, keine Wiederholung aus dem Lebenslauf, kein Blabla.
Fokussiere dich auf 2–3 wirklich relevante Qualifikationen und Motivation für die konkrete Stelle – streiche alles, was nicht im direkten Bezug zur Anzeige steht.
Formatiere das Anschreiben nach deutschem Standard:

[Dein Name]
[Deine Adresse]
[PLZ Ort]

[Empfänger/Firma]
[Empfänger-Adresse]
[PLZ Ort]

[Ort, Datum: {today}]

Betreff: [Stellenbezeichnung] (fett, zentriert, ohne "Betreff:" davor)

[Anrede] (z. B. "Sehr geehrte Frau Müller," oder "Sehr geehrte Damen und Herren,")

[Fließtext – sinnvolle Absätze, kurze, aktive Sätze]

[Abschiedsformel] (z. B. "Mit freundlichen Grüßen")
[Dein Name]

Halte dich exakt an diese Struktur und schreibe klar, persönlich und überzeugend.
Stil: {stil}
Sprache: {language}.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
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
        model="gpt-4o",
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
        model="gpt-4o",
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
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Verbessere das Anschreiben entsprechend."}
        ]
    )
    return response.choices[0].message.content