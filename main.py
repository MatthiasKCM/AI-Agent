# main.py
from agent.cover_letter import generate_cover_letter, check_cv, uniqueness_check, improve_letter
from agent.pdf_export import create_pdf
from agent.utils import extract_text_from_pdf, get_job_text_from_url
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="KI-Bewerbungs-Agent", page_icon="🧠")

# Hintergrund einstellbar!
st.markdown(
    """
    <style>
        .stApp {
            background-image: url('https://raw.githubusercontent.com/MatthiasKCM/AI-Agent/main/assets/pictures/AIAgent.png');
            background-size: 400px auto;
            background-repeat: repeat;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Google Analytics Tracking
GA_ID = "G-NW6J93TNXC"
components.html(
    f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_ID}');
    </script>
    """,
    height=0,
)

# Titel
st.title("🧠 KI-Bewerbungs-Agent")

st.success("""
🎯 **So funktioniert’s in 5 Schritten:**

1. Lebenslauf als PDF hochladen  
2. Stellenanzeige kopieren & einfügen (kein Link)  
3. Stil und Sprache auswählen  
4. Auf „Anschreiben generieren“ klicken  
5. Anschreiben prüfen, anpassen und als PDF exportieren
""")

# Frontend Boxen
cv_file = st.file_uploader("📎 Lebenslauf (PDF)")
job_url = st.text_area("🧾 Stellenanzeige einfügen (Link)")
stil = st.selectbox("Stil wählen", ["Formell", "Kreativ", "Selbstbewusst"])
language = st.selectbox("Sprache wählen", ["Deutsch", "Englisch", "Französisch"])

# Lebenslauf-Check
if cv_file:
    if st.button("🕵️ Lebenslauf checken"):
        cv_text = extract_text_from_pdf(cv_file)
        cv_feedback = check_cv(cv_text)
        st.info("CV-Check: \n" + cv_feedback)

# Anschreiben generieren
if st.button("✍️ Anschreiben generieren") and cv_file and job_url:
    cv_text = extract_text_from_pdf(cv_file)
    st.session_state['letter'] = generate_cover_letter(cv_text, job_url, stil, language)
    st.success("✅ Anschreiben erstellt!")
    job_description = get_job_text_from_url(job_url)
    lower = job_description.lower()

    if lower.startswith(("http://", "https://")):
        if "indeed." in lower:
            st.error("❌ Indeed blockt automatische Abrufe. Bitte den **reinen Text** der Stellenanzeige hier einfügen (kein Link).")
            st.stop()

# Hinweis zu Platzhaltern
st.warning("""
⚠️ **Wichtiger Hinweis:**  
Im Anschreiben können Platzhalter (z. B. `[Unternehmensname]`, `[Plattformname]`, `[Teamname]`, `[Empfänger-Adresse]` etc.) erscheinen, 
wenn entsprechende Infos im Lebenslauf oder in der Stellenanzeige fehlen. 
**Bitte prüfe dein Anschreiben sorgfältig und ersetze alle Platzhalter durch echte Daten, bevor du es versendest!**
""")

# Anschreiben anzeigen, falls vorhanden
if 'letter' in st.session_state and st.session_state['letter']:
    edited_letter = st.text_area("📄 Ergebnis (bearbeitbar)", value=st.session_state['letter'], height=500, key="editable_letter")
    st.session_state['letter'] = edited_letter

    # Plagiat-Check
    if st.button("🕵️‍♂️ Einzigartigkeit prüfen"):
        unique = uniqueness_check(st.session_state['letter'])
        st.session_state['kritikpunkte'] = unique
        st.info("Plagiat-Check & Kritikpunkte:\n" + unique)

    # Auto-Verbesserung
    if 'kritikpunkte' in st.session_state and st.session_state['kritikpunkte']:
        if st.button("💡 Kritikpunkte automatisch verbessern"):
            improved_letter = improve_letter(st.session_state['letter'], st.session_state['kritikpunkte'])
            st.session_state['letter'] = improved_letter
            st.success("✅ Verbesserte Version erstellt!")
            st.text_area("📄 Neue Version", value=improved_letter, height=500)

    # PDF Export
    if st.button("📄 PDF-Export"):
        filename = create_pdf(st.session_state['letter'])
        with open(filename, "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f,
                file_name=filename,
                mime="application/pdf"
            )
