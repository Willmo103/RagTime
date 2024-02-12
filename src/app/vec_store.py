import os
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from config import CHROMA_PATH, EMBED_MODEL

client_settings = Settings(
    chroma_path=CHROMA_PATH,
)


def create_new_vector_store(collection_name):
    vector_store_path = os.path.join(CHROMA_PATH, collection_name)
    if not os.path.exists(vector_store_path):
        os.makedirs(vector_store_path)
    return Chroma(
        collection_name=collection_name,
        embedding_function=EMBED_MODEL,
        vector_store_path=vector_store_path,
    )
