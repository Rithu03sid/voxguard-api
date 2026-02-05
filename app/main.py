from fastapi import FastAPI
from app.api import router

app = FastAPI(title="VoxGuard – AI Generated Voice Detection API")
app.include_router(router)
