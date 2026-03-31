import os
from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from utils.config_handler import rag_conf


def resolve_oneapi_api_key() -> str:
    config_key = str(rag_conf.get("oneapi_api_key", "")).strip()
    if config_key:
        return config_key
    return os.getenv("ONEAPI_API_KEY", "").strip()


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        openai_api_key = resolve_oneapi_api_key()
        openai_api_base = rag_conf["oneapi_base_url"]
        return ChatOpenAI(
            model=rag_conf["chat_model_name"],
            api_key=openai_api_key,
            base_url=openai_api_base,
        )


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        openai_api_key = resolve_oneapi_api_key()
        openai_api_base = rag_conf["oneapi_base_url"]
        return OpenAIEmbeddings(
            model=rag_conf["embedding_model_name"],
            api_key=openai_api_key,
            base_url=openai_api_base,
        )


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()
