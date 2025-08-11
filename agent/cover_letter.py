import os

import openai
from datetime import datetime
#Logik um mit OpenAI zu kommunizieren

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


import re, urllib.request
from html import unescape

# ---------- Utility: safe length + light extraction ----------
def _limit_chars(text: str, max_len: int = 12000) -> str:
    """Hard-limit long texts to protect the API from 400/BadRequest due to context size."""
    if not text:
        return ""
    t = text.strip()
    if len(t) <= max_len:
        return t
    return t[:max_len] + " …"

def _extract_relevant_sections(jd_text: str) -> str:
    """
    Try to keep only the most relevant parts of a job ad to reduce prompt size.
    Looks for German section headers like Aufgaben/Profil/Wir bieten etc.
    Falls back to a trimmed body.
    """
    if not jd_text:
        return ""
    # Normalize
    text = jd_text.replace("\\r", "\\n")
    # Heuristic split on common headers
    sections = []
    patterns = [
        r"(Aufgaben|Ihre Aufgaben|Was dich erwartet).*?(?=\\n\\s*[-A-ZÄÖÜ].{0,40}:|\\Z)",
        r"(Profil|Ihr Profil|Was du mitbringst|Anforderungen).*?(?=\\n\\s*[-A-ZÄÖÜ].{0,40}:|\\Z)",
        r"(Wir bieten|Benefits|Das bieten wir).*?(?=\\n\\s*[-A-ZÄÖÜ].{0,40}:|\\Z)",
        r"(Über uns|Das sind wir).*?(?=\\n\\s*[-A-ZÄÖÜ].{0,40}:|\\Z)",
        r"(Tech-Stack|Technologien).*?(?=\\n\\s*[-A-ZÄÖÜ].{0,40}:|\\Z)"
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.I | re.S | re.M)
        if m:
            sections.append(m.group(0).strip())
    joined = "\\n\\n".join(sections) if sections else text
    return _limit_chars(joined, 8000)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

def _fetch_html(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="ignore")

def _clean_html(text: str) -> str:
    # naive HTML->Text
    text = re.sub(r"(?is)<script.*?>.*?</script>|<style.*?>.*?</style>", "", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()

def extract_job_from_url(url: str):
    """Gibt dict(title, company, location, source_text) zurück (None, wenn nicht gefunden)."""
    try:
        html = _fetch_html(url)
    except Exception:
        return {"title": None, "company": None, "location": None, "source_text": None}

    def grab(pattern, s=html):
        m = re.search(pattern, s, flags=re.I | re.S)
        return m.group(1).strip() if m else None

    # Titel aus <h1>, og:title oder <title>
    title = grab(r"<h1[^>]*>(.*?)</h1>")
    if not title:
        title = grab(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']')
    if not title:
        raw_title = grab(r"<title[^>]*>(.*?)</title>")
        if raw_title:
            title = re.sub(r"\s*[-–|].*$", "", raw_title).strip()

    # Firma/Ort heuristisch (Indeed u.ä. Seiten)
    company = grab(r'"hiringOrganization"\s*:\s*{[^}]*"name"\s*:\s*"(.*?)"')
    if not company:
        company = grab(r'data-company-name=["\'](.*?)["\']')
    if not company:
        company = grab(r'itemprop=["\']name["\']\s*content=["\'](.*?)["\']')

    location = grab(r'"addressLocality"\s*:\s*"(.*?)"')
    if not location:
        location = grab(r'data-testid=["\']job-location["\'][^>]*>(.*?)</')

    source_text = _clean_html(html)
    return {"title": title, "company": company, "location": location, "source_text": source_text}

def extract_contact_from_cv(cv_text: str):
    """Gibt dict(name, address, zip_city, phone, email) zurück mit Fallbacks."""
    text = cv_text or ""
    # E‑Mail / Telefon
    email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    phone = re.search(r'(\+?\d[\d \-/()]{6,})', text)

    # Name (heuristisch: erste Zeile mit 2 Wörtern Groß/klein)
    name = re.search(r'(?m)^\s*([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)+)\s*$', text)
    # Adresse / PLZ Ort
    zip_city = re.search(r'(?m)\b(\d{5})\s+([A-ZÄÖÜ][\wäöüÄÖÜß\- ]+)\b', text)
    address = re.search(r'(?m)^\s*([A-ZÄÖÜ][\wäöüÄÖÜß\.\- ]+\s+\d+[A-Za-z]?)\s*$', text)

    return {
        "name": (name.group(1) if name else "Matthias Popp").strip(),
        "address": (address.group(1) if address else "[Deine Adresse]").strip(),
        "zip_city": (zip_city.group(0) if zip_city else "[PLZ Ort]").strip(),
        "phone": (phone.group(1) if phone else "[Telefonnummer]").strip(),
        "email": (email.group(0) if email else "[E‑Mail]").strip(),
    }

def generate_cover_letter(cv_text, job_description, stil, language):
    today = datetime.now().strftime("%d.%m.%Y")

    # 1) Metadaten aus CV
    contact = extract_contact_from_cv(cv_text)

    # 2) Metadaten & Volltext aus URL oder Plaintext
    jd_meta = {"title": None, "company": None, "location": None, "source_text": None}
    jd_text_input = job_description or ""

    if re.match(r'https?://', jd_text_input.strip()):
        jd_meta = extract_job_from_url(jd_text_input.strip())
        jd_text = jd_meta.get("source_text") or jd_text_input
    else:
        jd_text = jd_text_input

    # Reduce payload to avoid BadRequest on overly long inputs
    cv_text_short = _limit_chars(cv_text, 8000)
    jd_text = _extract_relevant_sections(jd_text)

    # Sicherungen
    job_title = jd_meta.get("title") or "[Stellenbezeichnung]"
    company = jd_meta.get("company") or "[Unternehmen]"
    job_location = jd_meta.get("location") or "[PLZ Ort]"

    # 3) Systemprompt (straff, ohne Widersprüche)
    system_prompt = f"""
Du bist ein professioneller Bewerbungsschreiber für den DACH‑Markt.

Ziel: Erstelle ein individuelles, natürlich klingendes Anschreiben nach DIN 5008. Max. 300 Wörter. Keine Bulletpoints/Listen/Metatexte.

HARTE REGELN
- Alle Blöcke MÜSSEN vorhanden sein. Platzhalter sind NUR in den Kopfblöcken erlaubt; im Fließtext KEINE Platzhalter.
- Nutze die folgenden Werte verbindlich:
  Name: {contact['name']}
  Adresse: {contact['address']}
  PLZ Ort (Absender): {contact['zip_city']}
  Telefon: {contact['phone']}
  E‑Mail: {contact['email']}
  Unternehmen (Empfänger): {company}
  Ort (Empfänger): {job_location}
  Stellenbezeichnung: {job_title}
- Exakt ZWEI Absätze Fließtext + 1 Abschlusszeile. Jeder Absatz ≤ 4 Zeilen.
- Präsens/Präteritum; kein Konjunktiv. Natürliche Satzlängen, keine Floskeln und kein Prozess‑Blabla ohne Nutzen.
- Keine zusätzlichen Leerzeilen außer den Block‑Trennungen. Gib NUR den finalen Brieftext in der vorgegebenen Reihenfolge aus.

FORMAT (exakt so, Reihenfolge/Zeilenumbrüche beibehalten)
{contact['name']}
{contact['address']}
{contact['zip_city']}
{contact['phone']}
{contact['email']}

{company}
[Name Ansprechpartner/in, falls bekannt]
[Empfänger-Adresse]
{job_location}

Würzburg, {today}

Bewerbung um die Stelle als {job_title}

Sehr geehrte/r [Name Ansprechpartner/in] / Damen und Herren,

[Absatz 1: 3–5 Sätze. Konkreter Bezug auf die Stelle/Quelle. Warum diese Rolle bei diesem Unternehmen jetzt? Verknüpfe 1–2 Anforderungen aus der Anzeige mit einer kurzen Erfahrung aus dem CV (Was? Wie? Ergebnis?). Natürlich, ohne Floskeln.]

[Absatz 2: 3–5 Sätze. Wie passt dein Stack/Arbeitsweise konkret? Nenne 2–3 Qualifikationen mit Mini‑Beleg („Was? Wie? Ergebnis?“). Keine Platzhalter, keine generischen Phrasen.]

Über die Einladung zu einem persönlichen Gespräch freue ich mich.

Mit freundlichen Grüßen

{contact['name']}

Stil: {stil}
Sprache: {language}
"""

    # 4) Dem Modell den ANZEIGENTEXT wirklich geben (nicht nur URL)
    user_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"LEBENSLAUF (gekürzt):\n{cv_text_short}"},
        {"role": "user", "content": f"STELLENANZEIGE:\n{jd_text}"},
        {"role": "user", "content": "Erstelle jetzt das Anschreiben exakt im vorgegebenen Format."}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-5",
            temperature=0.2,
            presence_penalty=0,
            frequency_penalty=0,
            max_tokens=900,
            messages=user_messages
        )
        return response.choices[0].message.content
    except Exception:
        # Fallback: further trim inputs and retry; also try a broadly available model
        cv_text_shorter = _limit_chars(cv_text_short, 4000)
        jd_text_shorter = _limit_chars(jd_text, 5000)
        user_messages_fallback = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"LEBENSLAUF (gekürzt):\n{cv_text_shorter}"},
            {"role": "user", "content": f"STELLENANZEIGE (gekürzt):\n{jd_text_shorter}"},
            {"role": "user", "content": "Erstelle jetzt das Anschreiben exakt im vorgegebenen Format."}
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            presence_penalty=0,
            frequency_penalty=0,
            max_tokens=900,
            messages=user_messages_fallback
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