from backend.app.core.config import get_settings
from backend.app.services.azure_ai import project_client
from backend.app.services.search_query_service import vector_search


settings = get_settings()


def ask_rag(question: str):
    """
    Retrieve relevant document chunks and generate
    a grounded answer using Azure OpenAI.

    Returns:
        answer:
            Generated answer.

        sources:
            Citation metadata for retrieved chunks.

        contexts:
            Actual retrieved text chunks.
            This is used by RAGAS evaluation.
    """

    # ---------------------------------------------------------
    # 1. Validate question
    # ---------------------------------------------------------

    if not question or not question.strip():
        return {
            "answer": "Please provide a question.",
            "sources": [],
            "contexts": [],
        }

    question = question.strip()

    # ---------------------------------------------------------
    # 2. Retrieve relevant document chunks
    # ---------------------------------------------------------

    documents = vector_search(question)

    if not documents:
        return {
            "answer": (
                "The information was not found "
                "in the available documents."
            ),
            "sources": [],
            "contexts": [],
        }

    # ---------------------------------------------------------
    # 3. Build context for LLM
    # ---------------------------------------------------------

    context_parts = []

    for index, document in enumerate(documents, start=1):

        document_name = document.get(
            "document_name",
            "Unknown document",
        )

        page_number = document.get(
            "page_number",
            "Unknown",
        )

        chunk_number = document.get(
            "chunk_number",
            "Unknown",
        )

        content = document.get(
            "content",
            "",
        )

        context_parts.append(
            f"[Source {index}]\n"
            f"Document: {document_name}\n"
            f"Page: {page_number}\n"
            f"Chunk: {chunk_number}\n\n"
            f"{content}"
        )

    context = "\n\n---\n\n".join(context_parts)

    # ---------------------------------------------------------
    # 4. Get Azure OpenAI client
    # ---------------------------------------------------------

    openai_client = project_client.get_openai_client()

    # ---------------------------------------------------------
    # 5. Generate grounded answer
    # ---------------------------------------------------------

    response = openai_client.chat.completions.create(
        model=settings.chat_deployment_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an enterprise document assistant.\n\n"

                    "Answer the user's question using ONLY "
                    "the provided document context.\n\n"

                    "Do not use outside knowledge.\n\n"

                    "If the answer cannot be found in the "
                    "provided context, say:\n"
                    "\"The information was not found in "
                    "the available documents.\"\n\n"

                    "When using information from a source, "
                    "cite it using [Source N], where N is "
                    "the source number provided in the context.\n\n"

                    "Do not create citations for information "
                    "that is not supported by the context.\n\n"

                    "Keep the answer concise and factual."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Document Context:\n\n"
                    f"{context}\n\n"
                    f"User Question:\n\n"
                    f"{question}"
                ),
            },
        ],
    )

    # ---------------------------------------------------------
    # 6. Extract answer
    # ---------------------------------------------------------

    answer = response.choices[0].message.content

    if not answer:
        answer = (
            "The system was unable to generate an answer "
            "from the available documents."
        )

    # ---------------------------------------------------------
    # 7. Build citation sources
    # ---------------------------------------------------------

    sources = []
    seen_sources = set()

    for index, document in enumerate(documents, start=1):

        source = {
            "source_id": index,
            "document_name": document.get(
                "document_name"
            ),
            "page_number": document.get(
                "page_number"
            ),
            "chunk_number": document.get(
                "chunk_number"
            ),
            "score": document.get(
                "score"
            ),
            "snippet": (
                document.get("content", "")[:500]
            ),
        }

        source_key = (
            source["document_name"],
            source["page_number"],
            source["chunk_number"],
        )

        if source_key in seen_sources:
            continue

        seen_sources.add(source_key)

        sources.append(source)

    # ---------------------------------------------------------
    # 8. Build RAGAS contexts
    # ---------------------------------------------------------

    contexts = []

    seen_contexts = set()

    for document in documents:

        content = document.get(
            "content",
            "",
        ).strip()

        if not content:
            continue

        if content in seen_contexts:
            continue

        seen_contexts.add(content)

        contexts.append(content)

    # ---------------------------------------------------------
    # 9. Return complete RAG response
    # ---------------------------------------------------------

    return {
    "answer": answer,
    "sources": sources,
    "retrieval_context": [
        document.get("content", "")
        for document in documents
        if document.get("content")
    ],
}