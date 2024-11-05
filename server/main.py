from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from database import create_tables
from contextlib import asynccontextmanager

from api.main import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:8080",
    "https://registry.csuwf.com",
    "http://localhost:1234",
]

app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"]
)

app.include_router(api_router)
