from pathlib import Path
import hashlib
import os
from typing import List, Dict
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models



BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = (BASE_DIR / "../../../data/docs/solana-whitepaper.pdf").resolve()
CHUNK_SIZE = 500
COLLECTION_NAME = "rag_core_embed"
EMBEDDING_DIM = 384
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
qdrant = QdrantClient(host="localhost", port=6333)


def load_pdf_text(pdf_path: Path) -> str:
    """
    Step 1: Convert binary PDF → raw text stream
    """
    reader = PdfReader(pdf_path)

    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)

    return "\n".join(pages_text)


def normalize_text(text: str) -> str:
    """
    Step 2: Normalize extracted text
    - Remove excessive whitespace
    - Make downstream chunking predictable
    """
    return " ".join(text.split())


def chunk_text(text: str, chunk_size: int) -> List[str]:
    """
    Step 3: Convert text → fixed-size chunks
    These are the atomic units for embedding later.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end

    return chunks


def ingest_pdf() -> List[Dict]:
    """
    Full ingest pipeline:
    PDF → normalized chunks with metadata
    """
    raw_text = load_pdf_text(PDF_PATH)
    normalized_text = normalize_text(raw_text)
    chunks = chunk_text(normalized_text, CHUNK_SIZE)

    documents = []
    for idx, chunk in enumerate(chunks):
        documents.append({
            "chunk_id": idx,
            "doc_id": PDF_PATH.name,
            "content": chunk
        })

    return documents

def embedding(docs: list[dict]) -> list:
    sentences = [docs]
    model = SentenceTransformer('sentence-transformers/all-MiniLM-l6-v2')
    embeddings = model.encode(sentences)
    print(embeddings)
    return embeddings


def _stable_point_id(doc_id: str, chunk_id: int) -> int:
    """
    Deterministic, Qdrant-valid point ID.
    """
    raw = f"{doc_id}:{chunk_id}".encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest(), 16) % (2**63)


def upsert_chunks_to_qdrant(chunks: List[Dict]) -> int:
    """
    Upserts chunks into Qdrant following the strict schema:
    id      → identity
    vector  → embedding
    payload → { chunk, doc_id }
    """

    texts = [c["content"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False)

    points = []
    for chunk, vector in zip(chunks, embeddings):
        points.append(
            models.PointStruct(
                id=_stable_point_id(chunk["doc_id"], chunk["chunk_id"]),
                vector=vector.tolist(),
                payload={
                    "chunk": chunk["content"],
                    "doc_id": chunk["doc_id"],
                },
            )
        )

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    return len(points)

# def upsert_chunks_to_qdrant(chunks: List[Dict]) -> int:
#     """
#     Takes ingested chunks, embeds them, and upserts into Qdrant.
#     Returns number of points upserted.
#     """

#     texts = [chunk["content"] for chunk in chunks]

#     # Step 1: Embed
#     embeddings = model.encode(texts, show_progress_bar=False)

#     # Step 2: Build Qdrant points
#     points = []
#     for chunk, vector in zip(chunks, embeddings):
#         point = models.PointStruct(
#             id=f'{chunk["doc_id"]}_{chunk["chunk_id"]}',  # deterministic ID
#             vector=vector.tolist(),
#             payload={
#                 "doc_id": chunk["doc_id"],
#                 "chunk_id": chunk["chunk_id"],
#                 "content": chunk["content"],
#             },
#         )
#         points.append(point)

#     # Step 3: Upsert
#     qdrant.upsert(
#         collection_name=COLLECTION_NAME,
#         points=points,
#     )

#     return len(points)