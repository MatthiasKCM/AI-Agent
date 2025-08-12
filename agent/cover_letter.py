# agent/cover_letter.py
import os, json, re, requests
from datetime import datetime
from bs4 import BeautifulSoup
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- Fetch ----------
# ---------- Fetch (robust mit Headern + Fallback) ----------
def _fetch_job_text(job_url: str) -> str:
    import urllib.parse as up
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    def _try(url: str):
        r = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        # viele Sites geben 200 + leeren Body -> fallback erzwingen
        if r.status_code == 200 and r.text and len(r.text) > 2000:
            return r.text
        r.raise_for_status()  # wirft HTTPError -> Fallback
        return r.text

    # 1) Direktabruf
    try:
        html = _try(job_url)
    except Exception:
        html = ""

    # 2) Fallback über r.jina.ai (liefert reinen Text aus dem Web)
    if not html:
        try:
            parsed = up.urlparse(job_url)
            # r.jina.ai erwartet http/https nicht doppelt – wir geben die Ziel-URL roh durch
            proxy_url = f"https://r.jina.ai/{job_url}"
            proxied = requests.get(proxy_url, headers=headers, timeout=20)
            if proxied.status_code == 200 and len(proxied.text) > 500:
                # der Proxy gibt Plaintext zurück – verpacken, damit der Extraktor was hat
                return proxied.text[:40000]
        except Exception:
            pass

    if not html:
        raise RuntimeError("Stellenanzeige konnte nicht geladen werden (Block durch Zielseite). Bitte Text der Anzeige einfügen oder eine andere URL probieren.")

    # regulärer BeautifulSoup-Flow
    soup = BeautifulSoup(html, "html.parser")
    texts = [t.get_text(" ", strip=True) for t in soup.find_all(
        ["h1","h2","h3","p","li","div","span","section","article"]
    )]
    long_text = "\n".join([t for t in texts if t and len(t.split()) > 3])
    # Notfallback: Wenn HTML leer war, lange genug war aber (z.B. Script-Only), nimm Roh-HTML
    if len(long_text) < 500:
        long_text = soup.get_text(" ", strip=True)
    return long_text[:40000]


def _extract_job_json(job_text: str) -> dict:
    resp = client.chat.completions.create(
        model="gpt-5",
        temperature=0.2, top_p=0.9, frequency_penalty=0.1,
        messages=[{"role":"system","content":_EXTRACT_PROMPT},
                  {"role":"user","content":job_text}]
    )
    raw = resp.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except Exception:
        m = re.search(r"\{.*\}", raw, re.S)
        return json.loads(m.group(0)) if m else {
            "company":"","role":"","location":"","contact_person":"","language":"",
            "must_have":[],"top_tasks":[],"benefits":[],"culture_notes":""
        }

# ---------- CV distill ----------
def _distill_cv(cv_text: str, job: dict) -> str:
    focus_list = job.get("must_have", [])[:3] + job.get("top_tasks", [])[:3]
    focus = "; ".join(focus_list) if focus_list else "Rollenpassung allgemein"
    prompt = f"""Ziehe aus diesem CV nur Belege für folgende Schwerpunkte: {focus}.
Gib 2–3 ultrakurze, faktenreiche Sätze aus, keine Listen, keine Floskeln."""
    resp = client.chat.completions.create(
        model="gpt-5", temperature=0.3,
        messages=[{"role":"system","content":prompt},{"role":"user","content":cv_text}]
    )
    return resp.choices[0].message.content.strip()

# ---------- Letter generate ----------
def _generate_letter(cv_focus: str, job: dict, stil: str, language: str) -> str:
    today = datetime.now().strftime("%d.%m.%Y")
    system_prompt = f"""
Du bist ein erfahrener Bewerbungsschreiber (DE-Markt). Schreibe DIN-5008-konform.
Pflicht: Alle Blöcke ausfüllen. Platzhalter zulässig. Keine Bulletpoints. Max 300 Wörter.
Fokus: exakt 2–3 relevante Qualifikationen aus CV_FOKUS; klare Motivation für genau diese Rolle.
Tabu: Floskeln („mit großem Interesse“, „teamfähig“), Wiederholung des Lebenslaufs, Generika.
Sätze kurz; höchstens ein „und“ pro Satz. Betreff fett+zentriert; Rest linksbündig.
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

[Fließtext – 2–3 Absätze, je ≤4 Zeilen, mit 2–3 konkreten Qualifikationsbezügen und persönlicher Motivation, Bezug auf {job.get('location','[Ort]')} oder Benefit falls sinnvoll]

[Abschiedsformel]
[Dein Name]
"""
    resp = client.chat.completions.create(
        model="gpt-5", temperature=0.3, top_p=0.9, frequency_penalty=0.2,
        messages=[{"role":"system","content":system_prompt},
                  {"role":"user","content":user_prompt}],
    )
    return resp.choices[0].message.content.strip()

# ---------- Validate & fix ----------
def _validate_and_fix(letter: str) -> str:
    def word_count(s): return len(re.findall(r"\w+", s))
    violations = []
    if word_count(letter) > 300: violations.append("Wortzahl > 300")
    must_blocks = ["[Dein Name]","[Deine Adresse]","[PLZ Ort]","**[","]**","[Anrede]","[Abschiedsformel]"]
    if not all(b in letter for b in must_blocks): violations.append("Pflichtblöcke fehlen")
    if re.search(r"\bmit großem Interesse\b|teamfähig|belastbar|flexibel", letter, re.I):
        violations.append("Floskeln enthalten")
    for s in re.split(r"[.!?]\s+", letter):
        if s.count(" und ") > 1: violations.append("Zu viele 'und' in einem Satz"); break
    if not violations: return letter
    fix_prompt = f"""Korrigiere den Text gemäß Regeln: {', '.join(violations)}.
Behalte Inhalt, aber kürze präzise. DIN-5008 Struktur unverändert lassen. Gib NUR den korrigierten Text."""
    resp = client.chat.completions.create(
        model="gpt-5", temperature=0.2,
        messages=[{"role":"system","content":fix_prompt},{"role":"user","content":letter}]
    )
    return resp.choices[0].message.content.strip()

# ---------- Public API ----------
def generate_cover_letter(cv_text: str, job_url: str, stil: str, language: str) -> str:
    job_text = _fetch_job_text(job_url)
    job_json = _extract_job_json(job_text)
    cv_focus = _distill_cv(cv_text, job_json)
    draft = _generate_letter(cv_focus, job_json, stil, language)
    final = _validate_and_fix(draft)
    return final

def check_cv(cv_text: str) -> str:
    prompt = """Du bist ein erfahrener Karriereberater. Analysiere diesen Lebenslauf auf Schwächen,
Lücken, Unklarheiten oder Verbesserungspotenzial. Gib konkrete, praxisnahe Verbesserungsvorschläge.
Antworte stichpunktartig und ehrlich."""
    resp = client.chat.completions.create(
        model="gpt-5", temperature=0.3,
        messages=[{"role":"system","content":prompt},
                  {"role":"user","content":cv_text}]
    )
    return resp.choices[0].message.content

def uniqueness_check(letter: str) -> str:
    prompt = """Du bist Bewerbungsexperte. Prüfe, ob das folgende Anschreiben einzigartig wirkt.
Bewerte kurz (1 Satz). Liste stichpunktartig generische Passagen und gib jeweils eine bessere Alternative."""
    resp = client.chat.completions.create(
        model="gpt-5", temperature=0.3,
        messages=[{"role":"system","content":prompt},
                  {"role":"user","content":f"ANSCHREIBEN:\n{letter}"}]
    )
    return resp.choices[0].message.content

def improve_letter(letter: str, kritikpunkte: str) -> str:
    prompt = f"""Überarbeite das Anschreiben so, dass alle Kritikpunkte präzise umgesetzt werden.
Mache es spezifisch, entferne jede Floskel. Gib NUR den neuen Text zurück.

Anschreiben:
{letter}

Kritikpunkte:
{kritikpunkte}
"""
    resp = client.chat.completions.create(
        model="gpt-5", temperature=0.3,
        messages=[{"role":"system","content":prompt}]
    )
    return resp.choices[0].message.content.strip()
