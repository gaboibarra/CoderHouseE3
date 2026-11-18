"""Configuración compartida por ingesta y consultas: no cambiar embeddings entre ambas."""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
VECTOR_DIR = ROOT / "vectorstore"
MANIFEST = ROOT / ".vectorstore_manifest.json"
COLLECTION = "arquitectura_tecnica_e3"


def embedding_model_name() -> str:
    return os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


def get_embeddings() -> OpenAIEmbeddings:
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Falta OPENAI_API_KEY. Se usa para embeddings, incluso con Anthropic.")
    return OpenAIEmbeddings(model=embedding_model_name())


def get_store() -> Chroma:
    # Chroma almacena datos en disco y vuelve a abrir la misma colección.
    return Chroma(collection_name=COLLECTION, persist_directory=str(VECTOR_DIR), embedding_function=get_embeddings())
