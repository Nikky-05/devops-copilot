from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from app.rag.vector_store import get_vector_store
from app.utils.config import get_settings


def get_retriever(k: int | None = None) -> BaseRetriever:
    top_k = k if k is not None else get_settings().rag_top_k
    return get_vector_store().as_retriever(search_kwargs={"k": top_k})


def retrieve(query: str, k: int | None = None) -> list[Document]:
    return get_retriever(k).invoke(query)
