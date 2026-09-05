import os
import sys
import uuid

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(script_dir)
repo_root = os.path.dirname(backend_root)

for path in (repo_root, backend_root):
    if path not in sys.path:
        sys.path.insert(0, path)

from backend.app.services.search_upload_service import (
    upload_chunks,
)


if __name__ == "__main__":

    chunk = {
        "id": str(uuid.uuid4()),
        "content": "Azure AI Search upload test.",
        "content_vector": [0.0] * 1536,
        "document_name": "test.pdf",
        "document_type": "pdf",
        "source": "manual-test",
        "page_number": 1,
        "chunk_number": 1,
    }

    upload_chunks([chunk])

    print("Upload finished.")