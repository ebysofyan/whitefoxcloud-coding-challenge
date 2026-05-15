from fastapi import FastAPI

from src.routes.auth import router as auth_router

app = FastAPI(title="Books API", version="0.1.0")
app.include_router(auth_router)
