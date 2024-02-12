import streamlit as st

st.set_page_config(page_title="Demo Chat App", page_icon=":speech_balloon:")
st.title("Demo Chat App")

chats = [{"name": "how to use the app"}, {"name": "what can I cook for Dinner?"}]

with st.sidebar:
    st.header("Settings")
    st.subheader("Webhook")
    website_url = st.text_input("webhook URL")
    st.subheader("Chats")
    for chat in chats:
        st.button(chat["name"])
    st.subheader("Upload a file")
    file = st.file_uploader("Upload a file")
