from fastapi import FastAPI
from utils.qdrant_utils import get_client, collection_exists

app = FastAPI()

@app.get("/qdrant/health")
def qdrant_health():
    client = get_client()
    try:
        exists = collection_exists(client)
        return {
            "status": "connected",
            "collection_exists": exists
        }
    except Exception as e:
        return{
            "status": "error",
            "message": str(e)
        }

@app.get("/")
def read_root():
    return {"Hello": "World"} 

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = "100"):
    return {"item_id": item_id, "q": q}