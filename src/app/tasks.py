from typing import Any
from langchain.prompts import Prompt
from langchain.chains.base import Chain
from langchain.llms.base import LLM
from langchain_community.llms.ollama import Ollama, OllamaEndpointNotFoundError
from config import OLLAMA_API_URL


class BaseModelInterface:
    model_name: str
    config = {}

    def __init__(self, model_name: str, config: dict = {}):
        self.model = Ollama(model_name, base_url=OLLAMA_API_URL,)



class Task:
    llm: Any
    prompt: Prompt
    inputs: dict | None = None


class PIDRemoval:
    ...
    prompt
    inputs = {}
