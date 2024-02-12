import json
from langchain_community.embeddings import OllamaEmbeddings
from langchain.vectorstores.chroma import Chroma
from app.config import CHROMA_PATH, PARAMS_FILE


class DataSource:
    def __init__(self, source, collection_name = None, options = None):
        self.document_loader
        self.text_splitter
        self.chunksize
        self.embedding_model = OllamaEmbeddings(model='mistral:7b')
        self.collection_name = collection_name
        self.options = options
        self.documents = None
        self.chunks = None
        self.data_store = Chroma(persist_directory = CHROMA_PATH, collection_name = self.collection_name, embedding_function = self.embedding_model)

    def load_data(self, *args, **kwargs):
        pass

    def split_text(self, *args, **kwargs):
        pass

    def save_to_chroma(self):
        pass

    def add_to_collections(self):
        with open(PARAMS_FILE, 'r') as f:
            params = json.load(f)
            if self.collection_name not in params['collections']:
                params['collections'].append(self.collection_name)
                with open(PARAMS_FILE, 'w') as f:
                    json.dump(params, f)

    def process(self):
        self.load_data()
        self.split_text()
        self.save_to_chroma()
        self.add_to_collections()

