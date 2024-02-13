import streamlit as st
from html_templates import css, bot_template, user_template
from vec_store import get_collections, get_or_create_vec_store
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.llms import ollama
from config import _log
from config import OLLAMA_API_URL


log = _log.getLogger(__name__)


def handle_user_input(user_question):
    response = st.session_state.conversation({"question": user_question})
    st.session_state.chat_history = response["chat_history"]

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(
                user_template.replace("{{MSG}}", message.content),
                unsafe_allow_html=True,
            )
        else:
            st.write(
                bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True
            )


def get_conversation_chain(vectorstore):
    llm = ollama.Ollama(base_url=OLLAMA_API_URL, model="mistral:latest")

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=vectorstore.as_retriever(), memory=memory
    )
    return conversation_chain


def main():
    st.session_state.collections = get_collections()
    st.set_page_config(page_title="Demo Chat App", page_icon=":speech_balloon:")
    st.title("Demo Chat App")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_user_input(user_question)

    with st.sidebar:
        st.header("Collections")
        # collections: [ {name: str, path: str} ]
        # omit the path from being rendered
        _collections = [c["name"] for c in st.session_state.collections]
        choice = st.radio("Select a collection", _collections)
        if st.button("Start Conversation"):
            vectorstore = get_or_create_vec_store(choice)
            st.session_state.conversation = get_conversation_chain(vectorstore)


if __name__ == "__main__":
    main()
