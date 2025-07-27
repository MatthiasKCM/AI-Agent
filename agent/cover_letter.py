import openai
#Logik um mit OpenAI zu kommunizieren

client = openai.OpenAI(api_key="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")

def generate_cover_letter(cv_text, job_description, stil,language):
    system_prompt = f"""
    Du bist ein professioneller Bewerbungsschreiber. Schreibe ein individuelles, überzeugendes Bewerbungsschreiben basierend auf Lebenslauf und Stellenanzeige.
    Kein Bullshit, keine Floskeln, sondern klar, persönlich und passend.
    Stil: {stil}
    Schreibe das Anschreiben in folgender Sprache: {language}.
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