import os
from typing import Optional
from qdrant_client import QdrantClient

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "edge_rag") 

def get_client(prefer_grpc: bool = False) -> QdrantClient:
    
    return QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
        grpc_port=6334 if prefer_grpc else None,
        prefer_grpc=prefer_grpc,
        timeout=5.0, 
    )

def collection_exists(client: QdrantClient, collection_name: Optional[str] = None) -> bool:
    """
    Idempotent check: Returns True if collection exists (or is healthy).
    Rationale: Guards upserts/migrations; uses has_collection (Qdrant 1.10+ efficient alias).
    Handles QdrantError (e.g., not-ready) gracefully—retries in callers if needed.
    """
    name = collection_name or QDRANT_COLLECTION_NAME
    try:
        return client.collection_exists(collection_name=name)
    # except QdrantError:
    #     return False
    except Exception as e:
        raise ValueError(f"Qdrant connection failed: {e}")