from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.client import open_connection, close_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await open_connection()
    yield
    # Teardown
    await close_connection()
