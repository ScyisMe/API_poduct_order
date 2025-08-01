from typing import Annotated
from fastapi import Path, APIRouter


router = APIRouter(prefix="/items", tags=["items"])



@router.get("/items/lastest/")
def get_lastest_item():
    return {"item": {"id": "0", "name": "lastest"}}

@router.get("/items/{item_id}")
def get_item_by_id(item_id: Annotated[int, Path(ge=1, lt=1_000)]):
    return {
        "item": {
            "id": item_id,
        },
    }