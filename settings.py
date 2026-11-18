"""Configuración compartida por ingesta y consultas (Python 3.12)."""
from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
DATA_DIR = ROOT / 'data'
VECTOR_DIR = ROOT / 'vectorstore'
COLLECTION = 'manuales_tecnicos_v1'
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
# Tamaño y solapamiento medidos en tokens de tiktoken, no caracteres.
CHUNK_TOKENS = 650
OVERLAP_TOKENS = 75
TOP_K = 4


def embeddings():
    """Mismo proveedor/modelo de embeddings para escribir y leer Chroma."""
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError('Falta OPENAI_API_KEY en .env (necesaria para embeddings).')
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


def vector_store():
    """Chroma usa una carpeta local persistente, sin servidor externo."""
    from langchain_chroma import Chroma
    return Chroma(collection_name=COLLECTION, embedding_function=embeddings(), persist_directory=str(VECTOR_DIR))
