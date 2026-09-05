import sys
from pathlib import Path


if __package__ in (None, ""):
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from backend.app.services.blob_storage_service import (
    upload_file,
)


if __name__ == "__main__":

    file_name = "test.txt"

    file_content = (
        b"Enterprise RAG Blob Storage test file."
    )

    try:
        blob_url = upload_file(
            file_name=file_name,
            file_data=file_content,
        )
    except Exception as exc:
        print(f"Blob upload failed: {exc}")
        raise

    print("File uploaded successfully!")
    print(f"Blob URL: {blob_url}")