from backend.app.services.blob_storage_service import (
    container_client,
)


if __name__ == "__main__":

    print("Testing Azure Blob Storage connection...")

    properties = container_client.get_container_properties()

    print("Blob Storage connection successful!")
    print(
        f"Container: {properties.name}"
    )