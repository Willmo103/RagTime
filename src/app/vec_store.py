import os
import json
from langchain_community.vectorstores import chroma
from config import CHROMA_PATH, EMBED_MODEL, _log, PARAMS_FILE

log = _log.getLogger(__name__)


def update_params(collection_dict):
    with open(PARAMS_FILE, "r") as f:
        params = json.load(f)
        if collection_dict not in params["collections"]:
            log.info(f"Adding {collection_dict} to the collections in {PARAMS_FILE}")
            params["collections"].append(collection_dict)
            with open(PARAMS_FILE, "w") as f:
                json.dump(params, f)
        else:
            log.info(f"{collection_dict} already in the collections in {PARAMS_FILE}")
    return None


def get_or_create_vec_store(collection_name):
    vector_store_path = os.path.join(CHROMA_PATH, collection_name)
    if not os.path.exists(vector_store_path):
        log.info(f"Creating a ChromaDB client at {CHROMA_PATH}")
        os.makedirs(vector_store_path)
        update_params({"name": collection_name, "path": vector_store_path})
    return chroma.Chroma(
        collection_name=collection_name,
        embedding_function=EMBED_MODEL,
        persist_directory=vector_store_path,
    )


def get_collections():
    try:
        with open(PARAMS_FILE, "r") as f:
            params = json.load(f)
            return params["collections"]
    except FileNotFoundError:
        log.warning("No params.json file found.")
        return []
