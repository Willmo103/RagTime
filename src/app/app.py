import streamlit as st


def main():
    # import app.config as conf

    # _tmp = conf.TMP

    st.set_page_config(page_title="Demo Chat App", page_icon=":speech_balloon:")
    st.title("Demo Chat App")

    # with st.sidebar:
    #     st.subheader("Your Documents")
    #     docs = st.file_uploader(
    #         "Upload a document", type=["txt", "pdf"], accept_multiple_files=True
    #     )
