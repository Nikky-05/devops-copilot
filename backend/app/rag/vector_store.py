from functools import lru_cache

from langchain_chroma import Chroma

from app.rag.embeddings import get_embeddings
from app.utils.config import get_settings


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    settings = get_settings()
    return Chroma(
        collection_name=settings.chroma_collection,
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_db_path,
    )
