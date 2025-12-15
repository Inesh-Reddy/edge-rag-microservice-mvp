import os
from dotenv import load_dotenv
from typing import Any, Optional
from qdrant_client import QdrantClient, models


load_dotenv()
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "edge_rag") 
DISTANCE = os.getenv("QDRANT_DISTANCE_NAME", "cosine")

points = [
    models.PointStruct(
        id = 1,
        vector = [0.1, 0.2, 0.3, 0.4],
        payload = {"category": "example"}
    ),
    models.PointStruct(
        id = 2,
        vector = [0.2, 0.3, 0.4, 0.5],
        payload = {"category": "demo"}
    )
]

def get_client(prefer_grpc: bool = False) -> QdrantClient:
    
    return QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
        grpc_port=6334 if prefer_grpc else None,
        prefer_grpc=prefer_grpc,
        timeout=5.0, 
    )

def create_collection(client: QdrantClient, collection_name: str, size: int ) -> bool :
    name = collection_name
    size = size
    print(f"{models.Distance.COSINE}")
    try:
        return client.create_collection(
            collection_name = name,
            vectors_config=models.VectorParams(
                size=size,
                distance=models.Distance.COSINE
            )
        )
    except Exception as e:
        raise ValueError(f"Qdrant collection creation error: {e}")


def verify_collection_creation(client: QdrantClient) -> dict :
    try:
        collections = client.get_collections()
        print("Existing collections: ", collections)
        return collections
    except Exception as e:
        raise ValueError(f"Error while getting collections: {e}")
    
def insert_vector_into_collection(client: QdrantClient, name:str) -> Any:
    try:
        result = client.upsert(
            collection_name=name,
            points=points
        )
        return result
    except Exception as e:
        raise ValueError(f"Error while inserting points into collection: {e}")


def retrive_collection_details(client: QdrantClient, name: str) -> Any :
    try:
        result = client.get_collection(name)
        return result
    except Exception as e:
        raise ValueError(f"Error while retriving collection info: {e}")
    
def similarity_search(client: QdrantClient, name:str) -> Any:
    query_vector = [0.08, 0.14, 0.33, 0.28]
    try:
        result = client.query_points(
            collection_name=name,
            query=query_vector,
            limit=1
        )
        return result
    except Exception as e:
        raise ValueError(f"Error while searching similarity: {e}")