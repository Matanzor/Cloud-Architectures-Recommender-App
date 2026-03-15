from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import close_db, get_db
from app.routers import architectures, recommend


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    from app.database import get_db
    for _ in range(30):
        try:
            db = await get_db()
            await db.command("ping")
            break
        except Exception:
            await asyncio.sleep(1)
    yield
    await close_db()


app = FastAPI(
    title="Cloud Architecture Recommender",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(architectures.router)
app.include_router(recommend.router)


@app.get("/")
async def root():
    return {"message": "Cloud Architecture API"}


@app.get("/health")
async def health():
    return {"status": "ok"}
