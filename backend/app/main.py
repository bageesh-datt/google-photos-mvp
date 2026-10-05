import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.routes.mvp_routes import router as mvp_router
from backend.app.mvp.photo_store import get_photo_store
from backend.app.mvp.embedding_service import get_embedding_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize PhotoStore on startup
    get_photo_store()
    # Pre-initialize embedding model on startup
    get_embedding_model()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Google Photos AI-Assisted Vague-Memory Photo Retrieval MVP API",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import RedirectResponse

class PhotosStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        if not path or path.strip("/") in ["", "."]:
            return RedirectResponse(url="/", status_code=307)
        return await super().get_response(path, scope)

# Mount photos static directory
photos_dir = settings.PHOTOS_DIR
if os.path.exists(photos_dir):
    app.mount("/photos", PhotosStaticFiles(directory=photos_dir), name="photos")

@app.get("/photos", include_in_schema=False)
@app.get("/photos/", include_in_schema=False)
def redirect_photos_root():
    return RedirectResponse(url="/", status_code=307)

# Include MVP API Routes
app.include_router(mvp_router)

@app.get("/")
def root_endpoint():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
