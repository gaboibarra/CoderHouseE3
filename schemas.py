"""Contrato de salida: la respuesta y los archivos que la justifican."""
from pydantic import BaseModel, Field, ConfigDict, field_validator


class RAGResponse(BaseModel):
    # No aceptamos campos extra que el LLM invente.
    model_config = ConfigDict(extra="forbid")

    respuesta: str = Field(min_length=1, description="Respuesta fundada en los documentos o 'No lo sé'.")
    referencias: list[str] = Field(default_factory=list, description="Nombres de archivos fuente usados.")

    @field_validator("referencias")
    @classmethod
    def referencias_unicas(cls, values: list[str]) -> list[str]:
        # Evita referencias vacías y repetidas.
        if any(not v.strip() for v in values):
            raise ValueError("Las referencias no pueden estar vacías")
        if len(values) != len(set(values)):
            raise ValueError("No se permiten referencias repetidas")
        return values
