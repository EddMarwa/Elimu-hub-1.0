from fastapi import FastAPI
from app.api import ingest, documents, chat

app = FastAPI(title="Elimu Hub Document Management & Chat API")

app.include_router(ingest.router)
app.include_router(documents.router)
app.include_router(chat.router) 