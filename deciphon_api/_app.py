from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

__all__ = ["app"]

app = FastAPI()

origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
