import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Router imports (placeholders to be created next)
from app.routes import upload, analysis, detox, dashboard, survey, tracker

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(upload, prefix=settings.API_V1_STR, tags=["Upload"])
app.include_router(analysis, prefix=settings.API_V1_STR, tags=["Analysis"])
app.include_router(detox, prefix=settings.API_V1_STR, tags=["Detox"])
app.include_router(dashboard, prefix=settings.API_V1_STR, tags=["Dashboard"])
app.include_router(survey, prefix=settings.API_V1_STR, tags=["Survey"])
app.include_router(tracker, prefix=settings.API_V1_STR, tags=["Tracker"])

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/api/v1/debug/pipeline-status")
def pipeline_status():
    from app.core.nlp_enhanced import get_okt
    from app.core.config import settings
    okt_available = get_okt() is not None
    gcp_api_configured = settings.GOOGLE_LANGUAGE_API_KEY != "mock-nl-api-key" and bool(settings.GOOGLE_LANGUAGE_API_KEY)
    
    return {
        "nlp_pipeline": {
            "okt_tagger_loaded": okt_available,
            "gcp_api_key_configured": gcp_api_configured,
            "default_provider": "gcp" if gcp_api_configured else "rule_based_fallback"
        },
        "backward_compatibility": {
            "legacy_mbti_retained": True,
            "dsao_type_code_active": True
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
