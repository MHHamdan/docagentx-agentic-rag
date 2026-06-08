from typing import Any

import httpx

from app.core.settings import settings


def build_grounded_prompt(question: str, contexts: list[dict[str, Any]]) -> str:
    evidence_blocks = []

    for index, context in enumerate(contexts, start=1):
        evidence_blocks.append(
            f"[Source {index}] "
            f"Page {context['page_number']}, Chunk {context['chunk_index']}:\n"
            f"{context['text']}"
        )

    evidence = "\n\n".join(evidence_blocks)

    return f"""
You are DocAgentX, a grounded document intelligence assistant.

Answer the user question using ONLY the evidence below.

If the evidence is not enough, say:
"I could not find enough evidence in the document to answer this question."

Question:
{question}

Evidence:
{evidence}

Answer:
""".strip()


def generate_mock_answer(question: str, contexts: list[dict[str, Any]]) -> str:
    if not contexts:
        return "I could not find enough evidence in the document to answer this question."

    return (
        "Based on the retrieved document evidence, the document discusses: "
        f"{contexts[0]['text']}"
    )


def generate_ollama_answer(question: str, contexts: list[dict[str, Any]]) -> str:
    prompt = build_grounded_prompt(question, contexts)

    response = httpx.post(
        f"{settings.ollama_base_url}/api/generate",
        json={
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()
    data = response.json()

    return data.get("response", "").strip()


def generate_answer(question: str, contexts: list[dict[str, Any]]) -> str:
    if settings.llm_provider == "ollama":
        return generate_ollama_answer(question, contexts)

    return generate_mock_answer(question, contexts)
