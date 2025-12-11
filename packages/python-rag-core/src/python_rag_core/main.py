from fastapi import FastAPI
from utils.qdrant_utils import get_client, create_collection, verify_collection_creation, insert_vector_into_collection, retrive_collection_details, similarity_search

app = FastAPI()

@app.post("/qdrant/create")
def qdrant_create_collection():
    client = get_client()
    try:
        exists = create_collection(client, "rag_core", 4)
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