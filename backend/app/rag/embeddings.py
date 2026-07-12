from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.utils.config import get_settings


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=get_settings().embedding_model)
