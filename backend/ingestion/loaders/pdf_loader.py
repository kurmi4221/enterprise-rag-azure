from pathlib import Path

from pypdf import PdfReader


def load_pdf(file_path: str):

    path = Path(file_path)

    reader = PdfReader(path)

    documents = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):

        text = page.extract_text()

        if not text:
            continue

        documents.append(
            {
                "content": text,
                "document_name": path.name,
                "document_type": "pdf",
                "source": str(path),
                "page_number": page_number,
            }
        )

    return documents