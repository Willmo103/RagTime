from langchain.vectorstores.chroma import Chroma
from config import CHROMA_PATH, PARAMS_FILE, _log
import json, os


log = _log.getLogger(__name__)


def update_params(collection_name):
    with open(PARAMS_FILE, "r") as f:
        params = json.load(f)
        if collection_name not in params["collections"]:
            log.info(f"Adding {collection_name} to the collections in {PARAMS_FILE}")
            params["collections"].append(collection_name)
            with open(PARAMS_FILE, "w") as f:
                json.dump(params, f)
        else:
            log.info(f"{collection_name} already in the collections in {PARAMS_FILE}")
    return None


def create_new_vector_store(db_name):
    with open(PARAMS_FILE, "r") as f:
        params = json.load(f)
        if db_name in params["vector_stores"]:
            log.info(f"{db_name} already in the vector stores in {PARAMS_FILE}")
            return None
    # check the physical directory
    if db_name in os.listdir(CHROMA_PATH):
        log.info(f"{db_name} already in the vector stores in {CHROMA_PATH}")
        return None
    # create the new vector store
    try:
        os.mkdir(os.path.join(CHROMA_PATH, db_name))
        c = Chroma(persist_directory=CHROMA_PATH)
        c.persist()
    except Exception as e:
        log.error(f"Error creating new vector store: {e}")
    try:
        with open(PARAMS_FILE, "r") as f:
            params = json.load(f)
            params["vector_stores"].append(db_name)
            with open(PARAMS_FILE, "w") as f:
                json.dump(params, f)
    except Exception as e:
        log.error(f"Error updating {PARAMS_FILE}: {e}")
    log.info(f"Added {db_name} to the vector stores in {PARAMS_FILE}")
    return None
