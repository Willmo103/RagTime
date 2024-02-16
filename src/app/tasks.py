from typing import Any
from langchain.prompts import Prompt, PromptTemplate
from langchain_community.llms.ollama import Ollama
from config import OLLAMA_API_URL


class OllamaModel:
    model_name: str
    config = {}

    def __init__(self, model_name: str, config: dict = {}):
        static_config = {
            "name": model_name,
            "base_url": OLLAMA_API_URL,
        }
        self.model = Ollama(**{**static_config, **config})

class Task:
    llm: OllamaModel
    inputs: dict | None
    data_sources: list[str]
    prompts: list[Prompt]
    chains: list[Any]


class SMSSummerizer(Task):
    def __init__(self):
        self.llm = OllamaModel("sms_summarizer", )
        self.data_sources = ["will_sms"]


class ImageClassifyerAgent(Task):
    def __init__(self):
        self.llm = OllamaModel("llava_image_classifyer", {'model': 'llava:13b', 'temprature': 0.3})
