from backend.app.services.azure_ai import project_client
from backend.app.core.config import settings


def generate_response(user_message: str) -> str:

    openai_client = project_client.get_openai_client()

    response = openai_client.chat.completions.create(
        model=settings.chat_deployment_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an enterprise AI assistant. "
                    "Answer clearly and accurately."
                ),
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
    )

    return response.choices[0].message.content