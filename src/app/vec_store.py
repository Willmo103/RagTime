import os
from langchain_community.vectorstores import chroma
from config import CHROMA_PATH, EMBED_MODEL


def get_or_create_vec_store(collection_name):
    vector_store_path = os.path.join(CHROMA_PATH, collection_name)
    if not os.path.exists(vector_store_path):
        os.makedirs(vector_store_path)
    return chroma.Chroma(
        collection_name=collection_name,
        embedding_function=EMBED_MODEL,
        persist_directory=vector_store_path,
    )
