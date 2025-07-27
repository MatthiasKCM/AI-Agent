from agent.cover_letter import generate_cover_letter, check_cv, uniqueness_check, improve_letter
from agent.pdf_export import create_pdf
from agent.utils import extract_text_from_pdf
import streamlit as st

st.title("🧠 KI-Bewerbungs-Agent")

cv_file = st.file_uploader("📎 Lebenslauf (PDF)")
job_text = st.text_area("🧾 Stellenanzeige einfügen")
stil = st.selectbox("Stil wählen", ["Formell", "Kreativ", "Selbstbewusst"])
language = st.selectbox("Sprache wählen", ["Deutsch", "Englisch", "Französisch"])

# Lebenslauf-Check
if cv_file:
    if st.button("🕵️ Lebenslauf checken"):
        cv_text = extract_text_from_pdf(cv_file)
        cv_feedback = check_cv(cv_text)
        st.info("CV-Check: \n" + cv_feedback)

# Anschreiben generieren
if st.button("✍️ Anschreiben generieren") and cv_file and job_text:
    cv_text = extract_text_from_pdf(cv_file)
    st.session_state['letter'] = generate_cover_letter(cv_text, job_text, stil, language)
    st.success("✅ Anschreiben erstellt!")

# Anschreiben anzeigen, falls vorhanden
if 'letter' in st.session_state and st.session_state['letter']:
    st.text_area("📄 Ergebnis", value=st.session_state['letter'], height=500)

    # Plagiat-Check nur, wenn Anschreiben existiert
    if st.button("🕵️‍♂️ Einzigartigkeit prüfen"):
        unique = uniqueness_check(st.session_state['letter'])
        st.session_state['kritikpunkte'] = unique
        st.info("Plagiat-Check & Kritikpunkte:\n" + unique)

    # Kritikpunkte an Anschreiben erkennen und verbessern
    if 'kritikpunkte' in st.session_state and st.session_state['kritikpunkte']:
        if st.button("💡 Kritikpunkte automatisch verbessern"):
            improved_letter = improve_letter(st.session_state['letter'], st.session_state['kritikpunkte'])
            st.session_state['letter'] = improved_letter
            st.success("✅ Verbesserte Version erstellt!")
            st.text_area("📄 Neue Version", value=improved_letter, height=500)

    # PDF Export für aktuelles Anschreiben
    if st.button("📄 PDF-Export"):
        filename = create_pdf(
            st.session_state['letter'],
            style="klassisch"  # Stil kann auswählbar gemacht werden!
        )
        with open(filename, "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f,
                file_name=filename,
                mime="application/pdf"
            )