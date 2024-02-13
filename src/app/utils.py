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
