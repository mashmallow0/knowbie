"""
Search API Routes - Semantic Search with Qdrant
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

# Optional imports - gracefully handle if not available
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None
    Distance = VectorParams = PointStruct = FieldCondition = MatchValue = None

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    SentenceTransformer = None

router = APIRouter()

# Qdrant configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "knowbie_knowledge"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 produces 384-dim vectors

# Initialize embedding model (lazy loading)
_model = None
_qdrant = None


def get_model():
    """Lazy load the embedding model"""
    global _model
    if not EMBEDDINGS_AVAILABLE:
        return None
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def get_qdrant():
    """Lazy load Qdrant client"""
    global _qdrant
    if not QDRANT_AVAILABLE:
        return None
    if _qdrant is None:
        try:
            _qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
            # Ensure collection exists
            collections = _qdrant.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if COLLECTION_NAME not in collection_names:
                _qdrant.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
                )
        except Exception as e:
            print(f"Qdrant connection error: {e}")
            return None
    return _qdrant


class SearchQuery(BaseModel):
    query: str
    limit: int = 10
    type_filter: Optional[str] = None


class SearchResult(BaseModel):
    id: str
    score: float
    title: str
    content: str
    type: str
    tags: str


@router.post("/")
async def search_knowledge(query: SearchQuery):
    """Semantic search using Qdrant"""
    try:
        qdrant = get_qdrant()
        if qdrant is None:
            # Fallback: return empty results with message
            return {
                "results": [],
                "message": "Qdrant not available. Please ensure Qdrant is running.",
                "fallback": True
            }
        
        model = get_model()
        
        # Generate embedding for query
        query_embedding = model.encode(query.query).tolist()
        
        # Build filter if type_filter provided
        search_filter = None
        if query.type_filter:
            from qdrant_client.models import FieldCondition, MatchValue
            search_filter = {
                "must": [
                    FieldCondition(
                        key="type",
                        match=MatchValue(value=query.type_filter)
                    )
                ]
            }
        
        # Search in Qdrant
        results = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=query.limit,
            query_filter=search_filter
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.payload.get("item_id", ""),
                "score": result.score,
                "title": result.payload.get("title", ""),
                "content": result.payload.get("content", ""),
                "type": result.payload.get("type", ""),
                "tags": result.payload.get("tags", "")
            })
        
        return {
            "query": query.query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/suggest")
async def get_search_suggestions(q: str = "", limit: int = 5):
    """Get search suggestions based on partial query"""
    try:
        qdrant = get_qdrant()
        if qdrant is None or not q:
            return {"suggestions": []}
        
        model = get_model()
        query_embedding = model.encode(q).tolist()
        
        results = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit
        )
        
        suggestions = [r.payload.get("title", "") for r in results if r.payload.get("title")]
        return {"suggestions": suggestions}
        
    except Exception:
        return {"suggestions": []}


@router.post("/index/{item_id}")
async def index_item(item_id: str, title: str, content: str, type: str, tags: str = ""):
    """Index a knowledge item in Qdrant for semantic search"""
    try:
        qdrant = get_qdrant()
        if qdrant is None:
            return {"message": "Qdrant not available", "indexed": False}
        
        model = get_model()
        
        # Combine text for embedding
        text_to_embed = f"{title} {content} {tags}"
        embedding = model.encode(text_to_embed).tolist()
        
        # Generate unique point ID
        point_id = str(uuid.uuid4())
        
        # Upsert to Qdrant
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "item_id": item_id,
                        "title": title,
                        "content": content,
                        "type": type,
                        "tags": tags
                    }
                )
            ]
        )
        
        return {
            "message": "Item indexed successfully",
            "indexed": True,
            "vector_id": point_id
        }
        
    except Exception as e:
        return {"message": f"Indexing error: {str(e)}", "indexed": False}


@router.delete("/index/{vector_id}")
async def remove_from_index(vector_id: str):
    """Remove a knowledge item from Qdrant index"""
    try:
        qdrant = get_qdrant()
        if qdrant is None:
            return {"message": "Qdrant not available", "deleted": False}
        
        qdrant.delete(
            collection_name=COLLECTION_NAME,
            points_selector=[vector_id]
        )
        
        return {"message": "Item removed from index", "deleted": True}
        
    except Exception as e:
        return {"message": f"Error: {str(e)}", "deleted": False}


@router.get("/health")
async def search_health():
    """Check search service health"""
    try:
        qdrant = get_qdrant()
        if qdrant is None:
            return {"status": "unavailable", "message": "Qdrant not connected"}
        
        # Try to get collection info
        collection = qdrant.get_collection(COLLECTION_NAME)
        return {
            "status": "healthy",
            "collection": COLLECTION_NAME,
            "vectors_count": collection.vectors_count
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}