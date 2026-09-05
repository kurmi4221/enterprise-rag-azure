from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

from backend.app.core.config import get_settings

from azure.core.credentials import AzureKeyCredential
from typing import List


settings = get_settings()

credential = DefaultAzureCredential()

search_client = SearchClient(
    endpoint=settings.azure_search_endpoint,
    index_name=settings.azure_search_index_name,
    credential=AzureKeyCredential(
        settings.azure_search_api_key
    )
)





def upload_chunks(chunks: List[dict]) -> None:
    """
    Upload document chunks to Azure AI Search.

    Args:
        chunks: List of chunk dictionaries.
    """

    if not chunks:
        return

    result = search_client.upload_documents(
        documents=chunks
    )

    succeeded = sum(
        1 for r in result if r.succeeded
    )

    failed = len(result) - succeeded

    print(
        f"Uploaded {succeeded} documents."
    )

    if failed:
        print(
            f"{failed} documents failed."
        )