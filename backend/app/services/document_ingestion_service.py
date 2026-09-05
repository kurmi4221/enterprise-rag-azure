import re
import logging
from io import BytesIO
from pathlib import Path

from azure.storage.blob import BlobServiceClient

from backend.app.core.config import get_settings
from backend.app.services.embedding_service import generate_embedding
from backend.app.services.search_upload_service import upload_chunks


CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

settings = get_settings()


def create_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Split document text into retrieval-friendly chunks.

    Strategy:
    1. Normalize whitespace.
    2. Split the document into paragraphs.
    3. Split long paragraphs into sentences.
    4. Build chunks without exceeding chunk_size.
    5. Preserve sentence boundaries where possible.
    6. Carry complete previous sentences into the next chunk
       for contextual overlap.
    7. Fall back to word-based splitting for extremely long
       sentences.

    This keeps chunks semantically coherent while providing
    enough overlap for retrieval.
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    # ---------------------------------------------------------
    # 1. Normalize text
    # ---------------------------------------------------------

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Normalize excessive whitespace while preserving
    # paragraph boundaries.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if not text:
        return []

    # ---------------------------------------------------------
    # 2. Split into paragraphs
    # ---------------------------------------------------------

    paragraphs = re.split(
        r"\n\s*\n+",
        text,
    )

    paragraphs = [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]

    # If there are no paragraph boundaries, treat each
    # non-empty line as a logical paragraph.
    if len(paragraphs) == 1:
        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        if len(lines) > 1:
            paragraphs = lines

    # ---------------------------------------------------------
    # 3. Convert paragraphs into sentence units
    # ---------------------------------------------------------

    units = []

    for paragraph in paragraphs:

        # Short paragraph: keep it as one semantic unit.
        if len(paragraph) <= chunk_size:
            units.append(paragraph)
            continue

        # Long paragraph: split into sentences.
        sentences = re.split(
            r"(?<=[.!?])\s+",
            paragraph,
        )

        for sentence in sentences:
            sentence = sentence.strip()

            if sentence:
                units.append(sentence)

    # ---------------------------------------------------------
    # 4. Build chunks
    # ---------------------------------------------------------

    chunks = []
    current_units = []
    current_length = 0

    for unit in units:

        # -----------------------------------------------------
        # Extremely long unit
        # -----------------------------------------------------

        if len(unit) > chunk_size:

            # Flush existing chunk first.
            if current_units:
                chunks.append(
                    " ".join(current_units).strip()
                )

                current_units = []
                current_length = 0

            # Split extremely long sentence by words.
            words = unit.split()

            word_chunk = []
            word_length = 0

            for word in words:

                additional_length = (
                    len(word)
                    if not word_chunk
                    else len(word) + 1
                )

                if (
                    word_chunk
                    and word_length + additional_length
                    > chunk_size
                ):
                    chunks.append(
                        " ".join(word_chunk).strip()
                    )

                    # Word-level fallback overlap.
                    overlap_words = []
                    overlap_length = 0

                    for previous_word in reversed(word_chunk):
                        extra = (
                            len(previous_word)
                            if not overlap_words
                            else len(previous_word) + 1
                        )

                        if (
                            overlap_length + extra
                            > chunk_overlap
                        ):
                            break

                        overlap_words.insert(
                            0,
                            previous_word,
                        )
                        overlap_length += extra

                    word_chunk = overlap_words
                    word_length = overlap_length

                if word_chunk:
                    word_chunk.append(word)
                    word_length += len(word) + 1
                else:
                    word_chunk = [word]
                    word_length = len(word)

            if word_chunk:
                chunks.append(
                    " ".join(word_chunk).strip()
                )

            continue

        # -----------------------------------------------------
        # Add unit to current chunk
        # -----------------------------------------------------

        additional_length = (
            len(unit)
            if not current_units
            else len(unit) + 1
        )

        if (
            current_units
            and current_length + additional_length
            > chunk_size
        ):
            # Save current chunk.
            chunks.append(
                " ".join(current_units).strip()
            )

            # -------------------------------------------------
            # Sentence-aware overlap
            # -------------------------------------------------

            overlap_units = []
            overlap_length = 0

            for previous_unit in reversed(current_units):

                extra = (
                    len(previous_unit)
                    if not overlap_units
                    else len(previous_unit) + 1
                )

                if (
                    overlap_length + extra
                    > chunk_overlap
                ):
                    break

                overlap_units.insert(
                    0,
                    previous_unit,
                )

                overlap_length += extra

            current_units = overlap_units

            current_length = (
                len(" ".join(current_units))
                if current_units
                else 0
            )

        # Add current unit.
        current_units.append(unit)

        current_length = len(
            " ".join(current_units)
        )

    # ---------------------------------------------------------
    # 5. Add final chunk
    # ---------------------------------------------------------

    if current_units:
        chunks.append(
            " ".join(current_units).strip()
        )

    # ---------------------------------------------------------
    # 6. Remove empty / duplicate chunks
    # ---------------------------------------------------------

    cleaned_chunks = []
    seen = set()

    for chunk in chunks:

        chunk = re.sub(
            r"\s+",
            " ",
            chunk,
        ).strip()

        if not chunk:
            continue

        if chunk in seen:
            continue

        seen.add(chunk)
        cleaned_chunks.append(chunk)

    return cleaned_chunks


logger = logging.getLogger(__name__)


def ingest_document(*args, **kwargs) -> bool:
    """
    Placeholder for document ingestion.

    The core RAG /chat path is currently decoupled from the
    batch ingestion pipeline.
    """
    logger.info("Ingestion skipped for now.")
    return True