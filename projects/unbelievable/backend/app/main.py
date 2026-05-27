import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Router imports (placeholders to be created next)
from app.routes import upload, analysis, detox, dashboard

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for prototype simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(upload, prefix=settings.API_V1_STR, tags=["Upload"])
app.include_router(analysis, prefix=settings.API_V1_STR, tags=["Analysis"])
app.include_router(detox, prefix=settings.API_V1_STR, tags=["Detox"])
app.include_router(dashboard, prefix=settings.API_V1_STR, tags=["Dashboard"])

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
