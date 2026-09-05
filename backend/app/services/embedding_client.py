from openai import OpenAI
from azure.identity import AzureCliCredential, get_bearer_token_provider


credential = AzureCliCredential()

token_provider = get_bearer_token_provider(
    credential,
    "https://ai.azure.com/.default",
)

embedding_client = OpenAI(
    base_url="https://enterprise-rag-chatbot1-resource.services.ai.azure.com/openai/v1/",
    api_key=token_provider,
)