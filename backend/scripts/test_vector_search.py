from backend.app.services.search_query_service import vector_search


questions = [
    "What is the annual leave policy?",
    "What are the official office timings?",
    "Are employees required to wear ID cards?",
]


for question in questions:

    print("=" * 60)
    print(f"Question: {question}")
    print("=" * 60)

    results = vector_search(question)

    print(f"Found {len(results)} relevant results.\n")

    for index, result in enumerate(results, start=1):

        print(f"Result {index}")
        print(f"Document : {result['document_name']}")
        print(f"Page     : {result['page_number']}")
        print(f"Chunk    : {result['chunk_number']}")
        print(f"Score    : {result['score']:.4f}")
        print(f"\n{result['content']}")
        print("-" * 60)