from vec_store import get_collections, get_or_create_vec_store
from html_templates import css, bot_template, user_template
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import ollama
from config import OLLAMA_API_URL
from config import CACHE, _log
import streamlit as st

# import json
# import os


log = _log.getLogger(__name__)


def handle_user_input(user_question):
    if not user_question:
        return

    # Get response from the conversation chain
    response = st.session_state.conversation({"question": user_question})
    st.session_state.chat_history = response["chat_history"]

    # Update the chat display
    for i, message in enumerate(st.session_state.chat_history):
        if st.session_state.chat_msgs is None:
            st.session_state.chat_msgs = []
        log.debug(f"Message: {message}")
        if i % 2 == 0:
            st.session_state.chat_msgs.append({"sender": "user", "message": message})
        else:
            st.session_state.chat_msgs.append({"sender": "bot", "message": message})


def get_conversation_chain(vectorstore):
    llm = ollama.Ollama(base_url=OLLAMA_API_URL, model="mistral:latest")

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=vectorstore.as_retriever(), memory=memory
    )
    return conversation_chain


# def persist_conversation(chat_history: list, collection_name: str):
#     if chat_history is not None:
#         import datetime as dt

#         file_name = f"{os.path.join(CACHE, collection_name)}.json"
#         try:
#             with open(file_name, "r") as f:
#                 data = json.load(f)
#         except FileNotFoundError:
#             data = {}
#             data[dt.datetime.now().isoformat()] = str(chat_history)
#             with open(file_name, "w") as f:
#                 json.dump(data, f)
#         except Exception as e:
#             log.exception(f"Error persisting conversation: {e}")
#             return None


# def get_last_conversation(collection_name: str):
#     try:
#         files = os.listdir(f"{os.path.join(CACHE, collection_name)}")
#         files = [f for f in files if f.endswith(".json")]
#         files = sorted(files, reverse=True)
#         if files:
#             with open(f"{os.path.join(CACHE, collection_name)}{files[0]}", "r") as f:
#                 return json.load(f)
#         else:
#             return None
#     except Exception as e:
#         log.exception(f"Error getting last conversation: {e}")
#         return None


def main():
    # Get collections
    st.session_state.collections = get_collections()
    st.set_page_config(page_title="Demo Chat App", page_icon=":speech_balloon:")
    st.title("Demo Chat App")
    st.write(css, unsafe_allow_html=True)

    # Initialize session state variables
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "chat_msgs" not in st.session_state:
        st.session_state.chat_msgs = None

    with st.sidebar:
        # Radio button to select a collection
        st.header("Collections")
        _collections = [c["name"] for c in st.session_state.collections]
        choice = st.radio("Select a collection", _collections)

        # Button to start the conversation using a selected collection
        if st.button("Start Conversation"):
            vectorstore = get_or_create_vec_store(choice)
            st.session_state.conversation = get_conversation_chain(vectorstore)

    # Use columns to create a two-row layout, with the top for messages and bottom for input
    col1, col2 = st.columns([1, 5])  # Adjust the ratio as needed

    with col1:
        st.empty()  # You can place something else here or adjust the ratio

    with col2:
        # Create a container for messages and make it scrollable
        message_container = st.container()
        with message_container:
            st.markdown('<div class="scrollable-chat-area">', unsafe_allow_html=True)
            if st.session_state.chat_msgs is not None:
                for msg in st.session_state.chat_msgs:
                    if msg["sender"] == "user":
                        st.markdown(
                            user_template.replace("{{MSG}}", msg["message"].content),
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            bot_template.replace("{{MSG}}", msg["message"].content),
                            unsafe_allow_html=True,
                        )
            st.markdown("</div>", unsafe_allow_html=True)

    # This empty space is used to push the chat input to the bottom of the screen
    st.empty()

    # Fixed input at the bottom
    st.markdown('<div class="fixed-input">', unsafe_allow_html=True)
    user_question = st.text_input(
        "", placeholder="Ask a question about your documents:", key="user_input"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if user_question:
        handle_user_input(user_question)


if __name__ == "__main__":
    main()
