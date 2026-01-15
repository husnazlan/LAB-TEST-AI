import streamlit as st
import nltk
from PyPDF2 import PdfReader

# Ensure punkt is available
nltk.download("punkt", quiet=True)
from nltk.tokenize import sent_tokenize

st.set_page_config(page_title="PDF Sentence Chunker (NLTK)", layout="wide")

st.title("Text Chunking using NLTK Sentence Tokenizer")
st.write("Upload a PDF file, extract text, view sample, and perform sentence chunking.")

# Step 1: Upload PDF (PyPDF2 PdfReader)
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    try:
        reader = PdfReader(uploaded_file)
        
        # Step 2: Extract text
        pages_text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)

        full_text = " ".join(pages_text).strip()

        st.subheader("PDF Information")
        st.write(f"Number of pages: **{len(reader.pages)}**")
        st.write(f"Total characters extracted: **{len(full_text)}**")

        if not full_text:
            st.warning("No text could be extracted from this PDF.")
        else:
            # Step 3: Preprocess & sample text (58 to 68)
            st.subheader("Sample Extracted Text (Indices 58 to 68)")
            if len(full_text) >= 68:
                sample_text = full_text[58:68]
                st.code(sample_text)
            else:
                st.warning("PDF text is too short to show indices 58 to 68.")

            # Step 4: Sentence Chunking using NLTK
            sentences = sent_tokenize(full_text)
            st.success(f"Sentence chunks detected: {len(sentences)}")

            # Display first N sentences
            st.subheader("Chunked Sentences (First 10)")
            for i, sent in enumerate(sentences[:10]):
                st.markdown(f"**{i}**. {sent}")

            # Optional: Show full text
            with st.expander("Show raw extracted text (first 2000 chars)"):
                st.text(full_text[:2000])

    except Exception as e:
        st.error(f"Error reading PDF: {e}")
else:
    st.info("Please upload a PDF to begin.")
