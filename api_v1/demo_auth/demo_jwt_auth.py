from fastapi import(
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)
from api_v1.demo_auth.helpers import (
    create_access_token,
    create_refresh_token,
)
from users.shemas import UserSchema
from auth import utils as auth_utils
from pydantic import BaseModel

from api_v1.demo_auth.dependancy import (
    http_bearer,
    get_current_token_payload,
    get_curent_active_from_user,
    REFRESH_TOKEN_TYPE,
    UserGetterFromToken,
    
)
from api_v1.demo_auth.crud import user_db

class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None =None
    token_type: str = "Bearer"

router = APIRouter(prefix="/jwt", tags=["JWT"],
                   dependencies=[Depends(http_bearer)])

def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    if not (user := user_db.get(username)):
        raise unauthed_exc
    
    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.password,
    ):
        raise unauthed_exc
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactiva",
        )
    return user

@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(
    user: UserSchema = Depends(validate_auth_user)
):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post(
    "/refresh/",
    response_model=TokenInfo,
    response_model_exclude_none=True,
             )
def auth_refresh_jwt(
    # user: UserSchema = Depends(get_auth_user_from_token_of_type(REFRESH_TOKEN_TYPE))
    user: UserSchema = Depends(UserGetterFromToken(REFRESH_TOKEN_TYPE))
    ):
    
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=access_token,
    )

@router.get("/users/me/")
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserSchema = Depends(get_curent_active_from_user),
):
    iat = payload.get("iat")
    return{
        "username": user.username,
        "email": user.email,
        "loggin at:": iat,
    }
    
