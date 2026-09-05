from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

from backend.app.core.config import get_settings
from backend.app.services.embedding_service import generate_embedding


# ---------------------------------------------------------
# Search configuration
# ---------------------------------------------------------

MIN_RELEVANCE_SCORE = 0.60
RELATIVE_SCORE_THRESHOLD = 0.80
MAX_RESULTS = 5


settings = get_settings()


def vector_search(
    query: str,
    top_k: int = MAX_RESULTS,
    relevance_ratio: float = RELATIVE_SCORE_THRESHOLD,
):
    """
    Perform vector search against Azure AI Search.

    Retrieval logic is unchanged.
    Diagnostic information is printed to establish
    the retrieval baseline.
    """

    # -----------------------------------------------------
    # 1. Validate query
    # -----------------------------------------------------

    if not query or not query.strip():
        return []

    query = query.strip()

    # -----------------------------------------------------
    # 2. Generate query embedding
    # -----------------------------------------------------

    embedding = generate_embedding(query)

    # -----------------------------------------------------
    # 3. Create Azure AI Search client
    # -----------------------------------------------------

    search_client = SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index_name,
        credential=AzureKeyCredential(
            settings.azure_search_api_key
        ),
    )

    # -----------------------------------------------------
    # 4. Vector search
    # -----------------------------------------------------

    results = search_client.search(
        search_text=None,
        vector_queries=[
            {
                "kind": "vector",
                "vector": embedding,
                "fields": "content_vector",
                "k": top_k,
            }
        ],
        select=[
            "id",
            "content",
            "document_name",
            "document_type",
            "source",
            "page_number",
            "chunk_number",
        ],
    )

    # -----------------------------------------------------
    # 5. Convert Azure results to dictionaries
    # -----------------------------------------------------

    documents = []
    seen = set()

    for result in results:

        score = result.get("@search.score")

        if score is None:
            continue

        document_name = result.get("document_name")
        page_number = result.get("page_number")
        chunk_number = result.get("chunk_number")

        unique_key = (
            document_name,
            page_number,
            chunk_number,
        )

        if unique_key in seen:
            continue

        seen.add(unique_key)

        documents.append(
            {
                "id": result.get("id"),
                "content": result.get("content"),
                "document_name": document_name,
                "document_type": result.get("document_type"),
                "source": result.get("source"),
                "page_number": page_number,
                "chunk_number": chunk_number,
                "score": float(score),
            }
        )

    # -----------------------------------------------------
    # 6. Retrieval diagnostics
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("🔎 RETRIEVAL DIAGNOSTICS")
    print("=" * 70)

    print(f"Query: {query}")
    print(f"Requested top_k: {top_k}")
    print(f"Retrieved before filtering: {len(documents)}")

    if documents:
        print("\nRetrieved chunks:")

        for rank, document in enumerate(documents, start=1):
            print(
                f"\n#{rank}"
                f"\n  File: {document['document_name']}"
                f"\n  Page: {document['page_number']}"
                f"\n  Chunk: {document['chunk_number']}"
                f"\n  Score: {document['score']:.4f}"
            )

    # -----------------------------------------------------
    # 7. No search results
    # -----------------------------------------------------

    if not documents:
        print("\n❌ No documents retrieved.")
        print("=" * 70)
        return []

    # -----------------------------------------------------
    # 8. Sort by relevance
    # -----------------------------------------------------

    documents.sort(
        key=lambda document: document["score"],
        reverse=True,
    )

    best_score = documents[0]["score"]

    print(f"\nBest score: {best_score:.4f}")
    print(f"Minimum absolute score: {MIN_RELEVANCE_SCORE}")
    print(f"Relative threshold: {relevance_ratio:.2f}")

    # -----------------------------------------------------
    # 9. Absolute relevance filter
    # -----------------------------------------------------

    if best_score < MIN_RELEVANCE_SCORE:

        print(
            "\n❌ Retrieval rejected:"
            f" best score {best_score:.4f}"
            f" < {MIN_RELEVANCE_SCORE}"
        )

        print("=" * 70)

        return []

    # -----------------------------------------------------
    # 10. Relative relevance filter
    # -----------------------------------------------------

    minimum_score = best_score * relevance_ratio

    filtered_documents = [
        document
        for document in documents
        if document["score"] >= minimum_score
    ]

    # -----------------------------------------------------
    # 11. Final diagnostics
    # -----------------------------------------------------

    print(f"\nRelative minimum score: {minimum_score:.4f}")
    print(
        f"Returned after filtering: "
        f"{len(filtered_documents)}"
    )

    print("\nFinal retrieved documents:")

    for rank, document in enumerate(
        filtered_documents,
        start=1,
    ):
        print(
            f"\n#{rank}"
            f"\n  File: {document['document_name']}"
            f"\n  Page: {document['page_number']}"
            f"\n  Chunk: {document['chunk_number']}"
            f"\n  Score: {document['score']:.4f}"
        )

    print("=" * 70)

    # -----------------------------------------------------
    # 12. Return filtered documents
    # -----------------------------------------------------

    return filtered_documents