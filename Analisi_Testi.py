import streamlit as st
import fitz  # PyMuPDF
import docx
import spacy
import openai
import re

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# OpenAI key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- Functions ---

def extract_text_from_pdf(uploaded_file):
    text = ""
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])

def analyze_text(text):
    doc = nlp(text)
    sentences = list(doc.sents)
    tokens = [token.text for token in doc if not token.is_punct]
    words = [token for token in doc if token.is_alpha]

    passive_sentences = [sent.text for sent in doc.sents if "by" in sent.text and "was" in sent.text]

    return {
        "num_sentences": len(sentences),
        "avg_sentence_length": sum(len(s.text.split()) for s in sentences) / len(sentences),
        "lexical_diversity": len(set(words)) / len(words) if words else 0,
        "passive_sentence_count": len(passive_sentences),
        "keywords": [token.lemma_ for token in doc if token.is_alpha and not token.is_stop][:20]
    }

def gpt_analysis(text, prompt_task="Find the thesis and arguments"):
    prompt = f"""
    Please analyze the following text and {prompt_task}.\n\n
    TEXT:\n{text[:3000]}  # truncate to fit token limit
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT Error: {e}"

# --- Streamlit App ---

st.set_page_config(page_title="Text Analysis AI", layout="wide")
st.title("📚 AI-Powered Text Analysis for Researchers")

uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])

if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        text = extract_text_from_pdf(uploaded_file)
    else:
        text = extract_text_from_docx(uploaded_file)

    st.subheader("📄 Extracted Text")
    st.write(text[:1000] + "...")

    st.subheader("🔍 Linguistic Analysis")
    with st.spinner("Analyzing with spaCy..."):
        results = analyze_text(text)
        st.write(f"**Number of sentences:** {results['num_sentences']}")
        st.write(f"**Average sentence length:** {results['avg_sentence_length']:.2f} words")
        st.write(f"**Lexical diversity:** {results['lexical_diversity']:.2f}")
        st.write(f"**Passive sentences detected:** {results['passive_sentence_count']}")
        st.write(f"**Top keywords:** {', '.join(results['keywords'])}")

    st.subheader("🧠 Argument & Thesis Detection (GPT)")
    with st.spinner("Asking GPT..."):
        gpt_output = gpt_analysis(text)
        st.markdown(gpt_output)

