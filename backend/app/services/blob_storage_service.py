from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from backend.app.core.config import get_settings


settings = get_settings()

credential = DefaultAzureCredential()

storage_account_url = (
    f"https://{settings.storage_account_name}.blob.core.windows.net"
)

blob_service_client = BlobServiceClient(
    account_url=storage_account_url,
    credential=credential,
)

container_client = (
    blob_service_client.get_container_client(
        settings.storage_container_name
    )
)


def upload_file(
    file_name: str,
    file_data: bytes,
) -> str:

    blob_client = container_client.get_blob_client(
        file_name
    )

    try:
        blob_client.upload_blob(
            file_data,
            overwrite=True,
        )
    except HttpResponseError as exc:
        if exc.status_code in (401, 403):
            raise PermissionError(
                "Azure Blob upload failed because the active identity does not have Blob write access. "
                "Assign the 'Storage Blob Data Contributor' or 'Storage Blob Data Owner' role to the identity "
                "resolved by DefaultAzureCredential() on the storage account/container, or run 'az login' to use the correct account."
            ) from exc
        raise

    return blob_client.url