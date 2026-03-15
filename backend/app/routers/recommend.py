from fastapi import APIRouter

from app.database import get_db
from app.schemas import RecommendRequest
from app.services.recommender import score_architecture

router = APIRouter(tags=["recommend"])


@router.post("/recommend")
async def recommend(req: RecommendRequest, limit: int = 5):
    db = await get_db()
    cursor = db["architectures"].find({"metadata": {"$exists": True}})
    scored = []
    async for doc in cursor:
        score, explanation = score_architecture(doc, req)
        scored.append((doc, score, explanation))

    scored.sort(key=lambda x: x[1], reverse=True)
    results = []
    for doc, score, explanation in scored[:limit]:
        meta = doc.get("metadata", {})
        results.append({
            "architecture": {
                "id": str(doc["_id"]),
                "source_url": doc.get("source_url", ""),
                "title": doc.get("title", ""),
                "description": doc.get("description", ""),
                "scraped_at": doc.get("scraped_at"),
                "resources": doc.get("resources", []),
                "metadata": meta,
            },
            "score": score,
            "explanation": explanation,
        })
    return {"recommendations": results}
