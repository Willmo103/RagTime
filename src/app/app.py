import streamlit as st
import pypdf2 import PdfReader


def get_doc_text(docs):



def main():
    import app.config as conf

    st.set_page_config(page_title="Demo Chat App", page_icon=":speech_balloon:")
    st.title("Demo Chat App")

    with st.sidebar:
        st.subheader("Your Documents")
        docs = st.file_uploader("Upload a document", type=["txt", "pdf"], accept_multiple_files=True)
        if st.button("Upload"):
            # get the text
            raw_text = get_doc_text(docs)
