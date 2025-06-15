import streamlit as st
import fitz  # PyMuPDF
import docx
import os

st.set_page_config(page_title="Analisi Testuale AI", layout="wide")

st.title("📄 Analisi Testuale AI per Studenti e Ricercatori")

# Upload del file
uploaded_file = st.file_uploader("Carica un file PDF o DOCX", type=["pdf", "docx"])

# Funzione per leggere PDF
def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# Funzione per leggere DOCX
def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# Estrazione e visualizzazione
if uploaded_file:
    file_type = os.path.splitext(uploaded_file.name)[1].lower()
    
    try:
        if file_type == ".pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif file_type == ".docx":
            text = extract_text_from_docx(uploaded_file)
        else:
            st.error("Formato file non supportato.")
            text = ""
        
        if text:
            st.success("✅ Testo estratto con successo!")
            st.subheader("📝 Anteprima del contenuto")
            st.text_area("Testo", text[:3000], height=400)  # Mostra solo i primi 3000 caratteri
        else:
            st.warning("Il file è vuoto o non è stato possibile estrarre testo.")
    
    except Exception as e:
        st.error(f"Errore durante l'estrazione del testo: {e}")
