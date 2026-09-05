from azure.identity import AzureCliCredential
from azure.ai.projects import AIProjectClient

from backend.app.core.config import settings

credential = AzureCliCredential(
    process_timeout=60
)

project_client = AIProjectClient(
    endpoint=settings.azure_ai_project_endpoint,
    credential=credential,
)