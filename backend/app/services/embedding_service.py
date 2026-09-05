from backend.app.services.embedding_client import embedding_client
from backend.app.core.config import get_settings

settings = get_settings()


def generate_embedding(text: str) -> list[float]:
    response = embedding_client.embeddings.create(
        model=settings.embedding_deployment_name,
        input=text,
    )

    return response.data[0].embedding