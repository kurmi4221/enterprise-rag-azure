from backend.app.services.document_ingestion_service import ingest_document


if __name__ == "__main__":
    result = ingest_document("test.txt")

    print("Ingestion successful!")
    print(result)