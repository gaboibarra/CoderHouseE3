"""Carga documentos .txt/.md, fragmenta en TOKENS y guarda embeddings persistentes."""
import argparse
import hashlib
import json
import logging

import chromadb
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import COLLECTION, DATA_DIR, MANIFEST, VECTOR_DIR, embedding_model_name, get_store

log = logging.getLogger(__name__)
CHUNK_TOKENS = 600  # tamaño objetivo MÁXIMO; últimos fragmentos pueden ser menores
OVERLAP_TOKENS = 50  # solapamiento en tokens (no caracteres)


def read_documents() -> list[Document]:
    documents = []
    for path in sorted(DATA_DIR.iterdir()):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            content = path.read_text(encoding="utf-8").strip()
            if content:
                documents.append(Document(page_content=content, metadata={"source": path.name}))
    if not documents:
        raise ValueError("No hay documentos .txt o .md con contenido en data/")
    return documents


def content_signature(documents: list[Document]) -> str:
    # La firma detecta cambios en archivos o en parámetros de chunking/embedding.
    h = hashlib.sha256()
    for doc in documents:
        h.update(doc.metadata["source"].encode())
        h.update(b"\0")
        h.update(doc.page_content.encode())
        h.update(b"\0")
    h.update(f"{COLLECTION}:{embedding_model_name()}:{CHUNK_TOKENS}:{OVERLAP_TOKENS}".encode())
    return h.hexdigest()


def split_documents(documents: list[Document]) -> list[Document]:
    # Usa tiktoken para contar TOKENS, no caracteres.
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=CHUNK_TOKENS,
        chunk_overlap=OVERLAP_TOKENS,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
    return chunks


def ingest(force: bool = False) -> int:
    documents = read_documents()
    signature = content_signature(documents)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    # Solo reutilizamos la colección si el manifiesto coincide y existen vectores.
    if not force and manifest.get("signature") == signature and VECTOR_DIR.exists():
        store = get_store()
        if store._collection.count() > 0:
            log.info("Colección existente: %s fragmentos; no se recalculan embeddings.", store._collection.count())
            return store._collection.count()

    chunks = split_documents(documents)
    log.info("Documentos=%d; fragmentos=%d; chunk_size=%d tokens; overlap=%d tokens", len(documents), len(chunks), CHUNK_TOKENS, OVERLAP_TOKENS)
    # Si cambiaron textos o modelo, reconstruimos la colección completa, sin mezclar embeddings.
    VECTOR_DIR.mkdir(exist_ok=True)
    client = chromadb.PersistentClient(path=str(VECTOR_DIR))
    try:
        client.delete_collection(COLLECTION)
    except chromadb.errors.NotFoundError:
        log.info(
            "La colección %s no existe todavía. "
            "Se creará una nueva.",
            COLLECTION
        )

    store = get_store()
    ids = [hashlib.sha256(f"{signature}:{i}".encode()).hexdigest() for i in range(len(chunks))]
    store.add_documents(chunks, ids=ids)
    MANIFEST.write_text(json.dumps({"signature": signature, "embedding_model": embedding_model_name(), "chunks": len(chunks)}, indent=2), encoding="utf-8")
    log.info("Indexación terminada: %d fragmentos persistidos en %s", len(chunks), VECTOR_DIR)
    return len(chunks)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    cli = argparse.ArgumentParser(description="Ingesta de documentos técnicos hacia ChromaDB")
    cli.add_argument("--force", action="store_true", help="Reconstruir índice incluso sin cambios")
    args = cli.parse_args()
    ingest(force=args.force)
