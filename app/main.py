from fastapi import FastAPI
from .routers import auth, gemini
from .core.database import engine
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(gemini.router, prefix="/gemini", tags=["gemini"])


@app.get("/")
async def root():
    return {"message": "Hello World"}