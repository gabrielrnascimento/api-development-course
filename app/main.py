import click
from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings


click.clear() # fix color codes on terminal

# models.Base.metadata.create_all(bind=engine) # ! no more need for this command because we implemented Alembic

app = FastAPI()

# ! routing magic !!!!
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():
    return {"message": "Hello World"}




