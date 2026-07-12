"""Load documents from backend/data/ and index them into ChromaDB.

Run from the backend/ directory:
    python -m app.rag.ingest            # incremental add
    python -m app.rag.ingest --reset    # clear collection first
"""
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.vector_store import get_vector_store
from app.utils.logger import get_logger

logger = get_logger("rag.ingest")

DATA_ROOT = Path(__file__).resolve().parents[2] / "data"
SUPPORTED_SUFFIXES = {".md", ".txt", ".rst"}

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def _load_documents(root: Path) -> list[Document]:
    if not root.exists():
        logger.warning("Data root does not exist: %s", root)
        return []

    docs: list[Document] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        try:
            loaded = TextLoader(str(path), encoding="utf-8").load()
        except UnicodeDecodeError:
            logger.warning("Skipping non-UTF8 file: %s", path)
            continue
        rel = path.relative_to(root).as_posix()
        category = rel.split("/", 1)[0] if "/" in rel else "root"
        for d in loaded:
            d.metadata["source"] = rel
            d.metadata["category"] = category
        docs.extend(loaded)
    return docs


def ingest(reset: bool = False) -> int:
    logger.info("Loading documents from %s", DATA_ROOT)
    documents = _load_documents(DATA_ROOT)
    if not documents:
        logger.warning("No documents found — nothing to index.")
        return 0

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)

    store = get_vector_store()
    if reset:
        logger.info("Resetting collection")
        store.reset_collection()
    store.add_documents(chunks)
    logger.info(
        "Indexed %d chunks from %d documents into %r",
        len(chunks),
        len(documents),
        store._collection_name,
    )
    return len(chunks)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest DevOps docs into ChromaDB.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear the collection before indexing.",
    )
    args = parser.parse_args()
    ingest(reset=args.reset)
