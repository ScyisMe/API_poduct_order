
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from contextlib import asynccontextmanager

from core.config import settings
from Item_views import router as items_router
from api_v1 import router as api_v1_router
from users.views import router as user_router
from core.models import Base, db_helper


import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)
app.include_router(items_router)
app.include_router(user_router)

    
@app.get("/")
def hello_index():
    return {
     "message": "Hello index!"   
    }
    
@app.get("/hello/")
def hello(name: str = "World"):
    name = name.strip().title()
    return {"message": f"Hello {name}!"}


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)