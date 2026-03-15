from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse

from app.database import get_db
from app.services.scraper import run_scrape

router = APIRouter(prefix="/architectures", tags=["architectures"])


@router.get("")
async def list_architectures(skip: int = 0, limit: int = 50):
    db = await get_db()
    cursor = db["architectures"].find().sort("scraped_at", -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        meta = doc.get("metadata", {})
        items.append({
            "id": str(doc["_id"]),
            "title": doc.get("title", ""),
            "source_url": doc.get("source_url", ""),
            "scraped_at": doc.get("scraped_at"),
            "metadata": meta,
        })
    return {"architectures": items}


@router.get("/{arch_id}")
async def get_architecture(arch_id: str):
    from bson import ObjectId
    db = await get_db()
    try:
        doc = await db["architectures"].find_one({"_id": ObjectId(arch_id)})
    except Exception:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    if not doc:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return {
        "id": str(doc["_id"]),
        "source_url": doc.get("source_url", ""),
        "title": doc.get("title", ""),
        "description": doc.get("description", ""),
        "scraped_at": doc.get("scraped_at"),
        "resources": doc.get("resources", []),
        "metadata": doc.get("metadata", {}),
    }


@router.post("/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_scrape)
    return {"status": "Scraping started", "message": "Running in background"}
