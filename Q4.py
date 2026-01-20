import streamlit as st
import nltk
from PyPDF2 import PdfReader

nltk.download("punkt", quiet=True)

st.set_page_config(page_title="PDF Sentence Chunking", layout="wide")

st.title("PDF Sentence Chunking using NLTK")
st.write(
    "Upload a PDF file, extract text, and split it into sentences "
    "using NLTK sentence tokenizer."
)

# Upload PDF
uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])

if uploaded_file is not None:

    reader = PdfReader(uploaded_file)
    full_text = ""

    for page in reader.pages:
        page_text = page.extract_text() or ""
        full_text += page_text + " "

    #Step3
    sentences = nltk.sent_tokenize(full_text)

    st.subheader("Sample Extracted Sentences (Index 58 to 68)")
    sample = sentences[58:68]

    for i, s in enumerate(sample, start=58):
        st.markdown(f"**{i}.** {s}")

    #Step4
    st.subheader("Sentence Chunks")
    for s in sample:
        st.write(s)

else:
    st.info("Please upload a PDF file to start.")
