"""Prueba manual del RAG: una pregunta con respuesta y una pregunta trampa."""
import argparse
import asyncio
import logging

from dotenv import load_dotenv
from rag import get_rag_response

load_dotenv()


async def main() -> None:
    cli = argparse.ArgumentParser(description="Consultas RAG locales sobre documentos técnicos")
    cli.add_argument("--provider", choices=["openai", "anthropic"], default="openai")
    cli.add_argument("--question", help="Pregunta libre. Si se omite se ejecutan dos pruebas")
    args = cli.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
    questions = [args.question] if args.question else [
        "¿Qué mecanismos se usan para proteger las credenciales de las APIs?",
        "¿Cuál es el sueldo del director general de esta empresa?",
    ]
    for question in questions:
        print(f"\nProveedor: {args.provider} | Pregunta: {question}")
        try:
            response = await get_rag_response(question, provider=args.provider)
            print(response.model_dump_json(indent=2))
        except Exception as exc:
            logging.getLogger(__name__).error("Fallo controlado: %s", exc)


if __name__ == "__main__":
    asyncio.run(main())
