# Path: /src/app/ingest.py
# Description: ...

from config import EMBED_MODEL, log, PARAMS, INGESTION_CONFIG
from vec_store import get_or_create_vec_store
import os
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    Docx2txtLoader,
    UnstructuredEPubLoader,
    UnstructuredMarkdownLoader,
    UnstructuredXMLLoader,
    UnstructuredRSTLoader,
    UnstructuredExcelLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

_log = log.getLogger(__name__)
ingestion_path = PARAMS["outside_data_path"]


def get_loader(file_path):
    known_source_ext = INGESTION_CONFIG["known_source_ext"]
    loader_configs = INGESTION_CONFIG["loader_configs"]
    file_ext = file_path.split(".")[-1]
    config = {}
    _log.debug(f"File extension: {file_ext}")

    if file_ext == "pdf":
        loader = PyPDFLoader(file_path)
        config = loader_configs["PyPDFLoader"]
    elif file_ext == "csv":
        loader = CSVLoader(file_path)
        config = loader_configs["CSVLoader"]
    elif file_ext == "rst":
        loader = UnstructuredRSTLoader(file_path, mode="elements")
        config = loader_configs["UnstructuredRSTLoader"]
    elif file_ext == "xml":
        loader = UnstructuredXMLLoader(file_path)
        config = loader_configs["UnstructuredXMLLoader"]
    elif file_ext == "md":
        loader = UnstructuredMarkdownLoader(file_path)
        config = loader_configs["UnstructuredMarkdownLoader"]
    elif file_ext == "epub":
        loader = UnstructuredEPubLoader(file_path)
        config = loader_configs["UnstructuredEPubLoader"]
    elif file_ext in ["doc", "docx"]:
        loader = Docx2txtLoader(file_path)
        config = loader_configs["Docx2txtLoader"]
    elif file_ext in ["xls", "xlsx"]:
        loader = UnstructuredExcelLoader(file_path)
        config = loader_configs["UnstructuredExcelLoader"]
    elif file_ext in known_source_ext:
        loader = TextLoader(file_path)
        config = loader_configs["TextLoader"]
    else:
        loader = TextLoader(file_path)
        config = loader_configs["TextLoaderUnknown"]
        _log.warning(f"Unknown file type: {file_ext}")

    return loader, config


def store_data_in_vector_db(data, collection_name, loader_conf) -> bool:
    chunk_size = loader_conf["chunk"]
    overlap = loader_conf["overlap"]
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap
    )
    docs = text_splitter.split_documents(data)

    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]

    try:
        # Try to get the existing collection; if not found, create a new one
        try:
            get_or_create_vec_store(collection_name).from_texts(
                texts=texts, metadatas=metadatas
            )
        except Exception:
            get_or_create_vec_store(collection_name).add_texts(
                texts=texts, metadatas=metadatas
            )
    except Exception as e:
        print(e)
        return False


def store_doc(file_path, collection_name=None):
    try:
        filename = os.path.basename(file_path)
        if collection_name is None:
            collection_name = filename.split(".")[0]

        loader, config = get_loader(file_path)
        data = loader.load()
        result = store_data_in_vector_db(data, collection_name, config)

        if result:
            _log.info(f"Document {filename} stored in collection {collection_name}")
    except Exception as e:
        _log.exception(f"Error storing document: {e}")
        return None


# Adjust main function to pass file paths to store_doc
def recursive_store_doc(root_ingestion_path, recurse=False, last_collection_name=None):
    try:
        for item in os.listdir(root_ingestion_path):
            folder_path = os.path.join(root_ingestion_path, item)
            if os.path.isdir(
                folder_path
            ):  # Root folder should only ever be filled with folders
                for file in os.listdir(folder_path):
                    if os.path.isfile(os.path.join(folder_path, file)):
                        file_path = os.path.join(folder_path, file)
                        store_doc(
                            file_path,
                            collection_name=item
                            if last_collection_name is None
                            else last_collection_name + "_" + item,
                        )
                    elif os.path.isdir(os.path.join(folder_path, file)):
                        recursive_store_doc(
                            os.path.join(folder_path, file),
                            recurse=True,
                            last_collection_name=item
                            if last_collection_name is None
                            else last_collection_name + "_" + item,
                        )
            elif os.path.isfile(folder_path):
                if recurse:
                    store_doc(
                        folder_path, collection_name=last_collection_name + "_" + item
                    )
                log.warning(f"Item {item} is not a folder. Skipping {folder_path}.")
                continue
            else:
                log.warning(
                    f"Item {item} is not a folder or file. WTF is it?\n\n\t\t'{folder_path}'\n\nYou got some strange stuff there...."
                )
    except Exception as e:
        log.exception(f"Error: {e}")


if __name__ == "__main__":
    recursive_store_doc(ingestion_path)
    # This
