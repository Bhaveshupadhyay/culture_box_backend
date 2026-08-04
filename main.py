from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.movies import router as movies_router
from app.api.v1.genres import router as genres_router
from app.api.v1.people import router as people_router
from app.api.v1.homepage import router as homepage_router
from app.core.lifecycle import lifespan

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(movies_router, prefix=settings.API_V1_STR)
app.include_router(genres_router, prefix=settings.API_V1_STR)
app.include_router(people_router, prefix=settings.API_V1_STR)
app.include_router(homepage_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
