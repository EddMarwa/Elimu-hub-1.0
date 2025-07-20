from fastapi import FastAPI
from app.api import ingest, chat

app = FastAPI(title="Elimu Hub Offline AI Backend")

app.include_router(ingest.router)
app.include_router(chat.router) 