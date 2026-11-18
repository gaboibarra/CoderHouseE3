import pytest
from pydantic import ValidationError
from schemas import RAGResponse
from rag import check_references, format_context
from langchain_core.documents import Document


def test_valid_response():
    r = RAGResponse(respuesta="Guardar la clave en .env", referencias=["seguridad.md"])
    assert r.referencias == ["seguridad.md"]


def test_no_se():
    assert RAGResponse(respuesta="No lo sé", referencias=[]).respuesta == "No lo sé"


def test_repeated_refs_rejected():
    with pytest.raises(ValidationError):
        RAGResponse(respuesta="Sí", referencias=["a.md", "a.md"])


def test_extra_field_rejected():
    with pytest.raises(ValidationError):
        RAGResponse.model_validate({"respuesta": "Sí", "referencias": [], "otro": 5})


def test_references_must_come_from_context():
    doc = Document(page_content="X", metadata={"source": "seguridad.md", "chunk_id": 0})
    with pytest.raises(ValueError):
        check_references(RAGResponse(respuesta="X", referencias=["inventado.md"]), [doc])


def test_no_se_drops_references():
    doc = Document(page_content="X", metadata={"source": "seguridad.md", "chunk_id": 0})
    result = check_references(RAGResponse(respuesta="No lo sé", referencias=["seguridad.md"]), [doc])
    assert result.referencias == []


def test_context_includes_filename():
    doc = Document(page_content="Guardar las claves en variables de entorno.", metadata={"source": "seguridad.md", "chunk_id": 1})
    assert "seguridad.md" in format_context([doc])
