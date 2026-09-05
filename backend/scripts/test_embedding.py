from backend.app.services.embedding_service import generate_embedding


if __name__ == "__main__":
    embedding = generate_embedding("Hello Azure AI")

    print("Embedding generated successfully")
    print("Dimensions:", len(embedding))