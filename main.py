# main.py
from agent.cover_letter import generate_cover_letter, check_cv, uniqueness_check, improve_letter
from agent.pdf_export import create_pdf
from agent.utils import extract_text_from_pdf
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="KI-Bewerbungs-Agent", page_icon="🧠")

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

GA_ID = "G-NW6J93TNXC"
components.html(
    f"""
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

st.title("🧠 KI-Bewerbungs-Agent")

st.success(
    "🎯 **Ablauf:**\n"
    "1. Lebenslauf als PDF hochladen\n"
    "2. **Reinen Text** der Stellenanzeige einfügen (URLs werden nicht geladen)\n"
    "3. Stil & Sprache wählen\n"
    "4. „Anschreiben generieren“\n"
    "5. Prüfen, verbessern, PDF exportieren"
)

cv_file = st.file_uploader("📎 Lebenslauf (PDF)")
job_plain = st.text_area("🧾 Reinen Text der Stellenanzeige hier einfügen (kein Link!)", height=220)

stil = st.selectbox("Stil wählen", ["Formell", "Kreativ", "Selbstbewusst"])
language = st.selectbox("Sprache wählen", ["Deutsch", "Englisch", "Französisch"])

# Lebenslauf-Check
if cv_file and st.button("🕵️ Lebenslauf checken"):
    try:
        cv_text = extract_text_from_pdf(cv_file)
        cv_feedback = check_cv(cv_text)
        st.info("CV-Check:\n" + cv_feedback)
    except Exception as e:
        st.error("❌ Konnte den Lebenslauf nicht lesen.")
        st.exception(e)

# Anschreiben generieren
if st.button("✍️ Anschreiben generieren") and cv_file and job_plain.strip():
    try:
        cv_text = extract_text_from_pdf(cv_file)
        with st.status("⏳ Erstelle Anschreiben …", expanded=False) as status:
            st.session_state['letter'] = generate_cover_letter(cv_text, job_plain, stil, language)
            status.update(label="✅ Anschreiben erstellt", state="complete")
        st.success("✅ Anschreiben erstellt!")
    except Exception as e:
        st.error("❌ Konnte die Stellenanzeige nicht verarbeiten.")
        st.exception(e)

st.warning(
    "⚠️ **Hinweis:** Platzhalter (z. B. `[Empfänger-Adresse]`) erscheinen, wenn Infos fehlen. "
    "Bitte vor dem Versenden ersetzen."
)

# Ergebnis / Nachbearbeitung
if 'letter' in st.session_state and st.session_state['letter']:
    edited_letter = st.text_area("📄 Ergebnis (bearbeitbar)",
                                 value=st.session_state['letter'],
                                 height=500,
                                 key="editable_letter")
    st.session_state['letter'] = edited_letter

    if st.button("🕵️‍♂️ Einzigartigkeit prüfen"):
        try:
            unique = uniqueness_check(st.session_state['letter'])
            st.session_state['kritikpunkte'] = unique
            st.info("Plagiat-Check & Kritikpunkte:\n" + unique)
        except Exception as e:
            st.error("❌ Prüfen der Einzigartigkeit fehlgeschlagen.")
            st.exception(e)

    if 'kritikpunkte' in st.session_state and st.session_state['kritikpunkte']:
        if st.button("💡 Kritikpunkte automatisch verbessern"):
            try:
                improved_letter = improve_letter(st.session_state['letter'], st.session_state['kritikpunkte'])
                st.session_state['letter'] = improved_letter
                st.success("✅ Verbesserte Version erstellt!")
                st.text_area("📄 Neue Version", value=improved_letter, height=500)
            except Exception as e:
                st.error("❌ Verbesserung fehlgeschlagen.")
                st.exception(e)

    if st.button("📄 PDF-Export"):
        try:
            filename = create_pdf(st.session_state['letter'])
            with open(filename, "rb") as f:
                st.download_button("Download PDF", f, file_name=filename, mime="application/pdf")
        except Exception as e:
            st.error("❌ PDF-Export fehlgeschlagen.")
            st.exception(e)
