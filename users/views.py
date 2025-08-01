from fastapi import APIRouter

from users import croud
from users.shemas import CreateUser

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/")
def create_user(user: CreateUser):
    return croud.create_user(user_in=user)
