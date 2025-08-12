# agent/cover_letter.py
import os, json
from datetime import datetime
from openai import OpenAI

# Modell zentral steuerbar (ENV), fällt zurück auf gpt-4o-mini
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Helfer zum Call ohne Sampling-Parameter (vermeidet 400-Fehler) ---
def _chat(messages):
    return client.chat.completions.create(model=MODEL, messages=messages)

# --- Prompts ---
EXTRACT_PROMPT = """Du bist Recruiter. Extrahiere Kerndaten aus der Stellenanzeige.
Gib NUR gültiges JSON mit genau diesen Keys zurück:
{"company":"","role":"","location":"","contact_person":"","language":"","must_have":[],"top_tasks":[],"benefits":[],"culture_notes":""}
Regeln:
- must_have: max 3 präzise Muss-Kriterien
- top_tasks: max 3 konkrete Aufgaben
- benefits: max 3 kurze Punkte
- language: "de" oder "en"
- Leere Felder mit "" bzw. []
"""

def _extract_job_json(job_text: str) -> dict:
    job_text = job_text.strip()[:20000]
    resp = _chat([
        {"role":"system","content":EXTRACT_PROMPT},
        {"role":"user","content":job_text}
    ])
    raw = resp.choices[0].message.content.strip()
    # Defensive JSON-Parse
    import re, json as _json
    try:
        return _json.loads(raw)
    except Exception:
        m = re.search(r"\{.*\}", raw, re.S)
        if m:
            try:
                return _json.loads(m.group(0))
            except Exception:
                pass
    return {"company":"","role":"","location":"","contact_person":"","language":"",
            "must_have":[],"top_tasks":[],"benefits":[],"culture_notes":""}

def _distill_cv(cv_text: str, job: dict) -> str:
    focus_list = (job.get("must_have") or [])[:3] + (job.get("top_tasks") or [])[:3]
    focus = "; ".join(focus_list) if focus_list else "Rollenpassung allgemein"
    prompt = f"""Ziehe aus diesem CV nur Belege für folgende Schwerpunkte: {focus}.
Gib 2–3 sehr kurze, faktenreiche Sätze aus. Keine Listen. Keine Floskeln."""
    resp = _chat([
        {"role":"system","content":prompt},
        {"role":"user","content":cv_text[:20000]}
    ])
    return resp.choices[0].message.content.strip()

def _generate_letter(cv_focus: str, job: dict, stil: str, language: str) -> str:
    today = datetime.now().strftime("%d.%m.%Y")
    system_prompt = f"""
Du bist ein erfahrener Bewerbungsschreiber (DE-Markt). DIN-5008.
Pflicht: Alle Blöcke ausfüllen. Platzhalter erlaubt. Keine Bulletpoints. Max 300 Wörter.
Fokus: exakt 2–3 Qualifikationen aus CV_FOKUS; klare Motivation für genau diese Rolle.
Tabu: Floskeln („mit großem Interesse“, „teamfähig“), generische Phrasen.
Sätze kurz; max ein „und“ pro Satz. Betreff fett+zentriert; Rest linksbündig.
Stil: {stil} | Sprache: {language}
"""
    user_prompt = f"""
JOB_JSON:
{json.dumps(job, ensure_ascii=False)}
CV_FOKUS:
{cv_focus}

Erzeuge das Anschreiben in exakt dieser Struktur:

[Dein Name]
[Deine Adresse]
[PLZ Ort]

[{job.get('company','[Empfänger/Firma]')}]
[Empfänger-Adresse]
[PLZ Ort]

[Ort, Datum: {today}]

**[{job.get('role','[Stellenbezeichnung]')}]**

[Anrede]

[Fließtext – 2–3 Absätze, je ≤4 Zeilen, mit 2–3 konkreten Qualifikationsbezügen
und persönlicher Motivation; Bezug auf {job.get('location','[Ort]')} oder Benefit, falls sinnvoll]

[Abschiedsformel]
[Dein Name]
"""
    resp = _chat([
        {"role":"system","content":system_prompt},
        {"role":"user","content":user_prompt}
    ])
    return resp.choices[0].message.content.strip()

def _validate_and_fix(letter: str) -> str:
    import re
    def wc(s): return len(re.findall(r"\w+", s))
    violations = []
    if wc(letter) > 300: violations.append("Wortzahl > 300")
    must = ["[Dein Name]","[Deine Adresse]","[PLZ Ort]","**[","]**","[Anrede]","[Abschiedsformel]"]
    if not all(b in letter for b in must): violations.append("Pflichtblöcke fehlen")
    if re.search(r"\bmit großem Interesse\b|teamfähig|belastbar|flexibel", letter, re.I):
        violations.append("Floskeln enthalten")
    for s in re.split(r"[.!?]\s+", letter):
        if s.count(" und ") > 1:
            violations.append("Zu viele 'und' in einem Satz"); break
    if not violations: return letter
    fix_prompt = f"""Korrigiere den Text gemäß Regeln: {', '.join(violations)}.
Kürze präzise. DIN-5008-Struktur exakt beibehalten. Gib NUR den korrigierten Text."""
    resp = _chat([
        {"role":"system","content":fix_prompt},
        {"role":"user","content":letter}
    ])
    return resp.choices[0].message.content.strip()

# --- Public API ---
def generate_cover_letter(cv_text: str, job_text_plain_or_url: str, stil: str, language: str) -> str:
    # Kein Scraping mehr. Wenn URL erkannt wird: Fehlermeldung fordern, Text einzufügen.
    source = job_text_plain_or_url.strip()
    if source.lower().startswith(("http://","https://")):
        raise RuntimeError("Bitte den reinen Text der Stellenanzeige einfügen (URLs werden nicht geladen).")
    job_json = _extract_job_json(source)
    cv_focus = _distill_cv(cv_text, job_json)
    draft = _generate_letter(cv_focus, job_json, stil, language)
    final = _validate_and_fix(draft)
    return final

def check_cv(cv_text: str) -> str:
    prompt = """Du bist Karriereberater. Analysiere Schwächen, Lücken, Unklarheiten, Verbesserungen.
Gib konkrete, praxisnahe Vorschläge. Stichpunktartig. Ehrlich."""
    resp = _chat([
        {"role":"system","content":prompt},
        {"role":"user","content":cv_text[:20000]}
    ])
    return resp.choices[0].message.content

def uniqueness_check(letter: str) -> str:
    prompt = """Bewerte kurz (1 Satz), ob das Anschreiben generisch wirkt.
Liste stichpunktartig generische Passagen und gib jeweils eine bessere Alternative."""
    resp = _chat([
        {"role":"system","content":prompt},
        {"role":"user","content":f"ANSCHREIBEN:\n{letter[:12000]}"}]
    )
    return resp.choices[0].message.content

def improve_letter(letter: str, kritikpunkte: str) -> str:
    prompt = f"""Überarbeite das Anschreiben so, dass alle Kritikpunkte präzise umgesetzt werden.
Mache es spezifisch, entferne Floskeln. Gib NUR den neuen Text zurück.

Anschreiben:
{letter[:12000]}

Kritikpunkte:
{kritikpunkte[:8000]}
"""
    resp = _chat([
        {"role":"system","content":prompt}
    ])
    return resp.choices[0].message.content.strip()
