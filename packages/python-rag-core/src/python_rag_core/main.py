from fastapi import FastAPI
from utils.qdrant_utils import get_client, create_collection, verify_collection_creation, insert_vector_into_collection, retrive_collection_details, similarity_search
from rag_pipeline import ingest_pdf, embedding, upsert_chunks_to_qdrant

app = FastAPI()

chunks: list[dict] = []

@app.post("/ingest")
def ingest_pdf_endpoint():
    docs: list[dict] = ingest_pdf()

    if docs is None:
        return {"status": "error", "message": "ingest_pdf returned None"}

    chunks.clear()
    chunks.extend(docs)

    print(f"Ingested {len(chunks)} chunks")
    print(chunks[1])

    return {
        "status": "success",
        "chunks_ingested": len(chunks)
    }


@app.post("/embed")
def embed():
    if not chunks:
        return {
            "status": "error",
            "message": "No chunks available. Call /ingest first."
        }

    embeddings = embedding(chunks)

    return {
        "status": "success",
        "chunks_embedded": len(embeddings),
        "embedding_dim": len(embeddings[0]),
    }


@app.post("/upsert-embeddings")
def upsert_endpoint():
    if not chunks:
        return {
            "status": "error",
            "message": "No chunks available. Call /ingest first."
        }

    points_upserted = upsert_chunks_to_qdrant(chunks)

    return {
        "status": "success",
        "points_upserted": points_upserted,
        "collection": "rag_core_embed",
    }


@app.post("/qdrant/create")
def qdrant_create_collection():
    client = get_client()
    try:
        exists = create_collection(client, "rag_core_embed", 384)
        return {
            "status": "created collection",
            "create_collection": exists
        }
    except Exception as e:
        return{
            "status": "error",
            "message": str(e)
        }
    
@app.get("/qdrant/verifyCollections")
def qdrant_verifyCollections():
    client = get_client()
    try:
        collections = verify_collection_creation(client)
        return {
            "status": "existing collections",
            "collections": collections
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    
@app.post("/qdrant/upsert")
def qdrant_upsert():
    client= get_client()
    try:
        result = insert_vector_into_collection(client,"rag_core")
        return {
            "status": "upsert collection",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/qdrant/retrive")
def qdrant_retrive_collection_details():
    client=get_client()
    try:
        result = retrive_collection_details(client, "rag_core")
        return {
            "status": "collection retrival",
            "collection_info": {
                "points_count": result.points_count
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/qdrant/similarity")
def qdrant_similarity_search():
    client = get_client()
    try:
        result = similarity_search(client, "rag_core")
        return {
            "status": "200",
            "similarity_data":result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }