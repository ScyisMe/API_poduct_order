from api_v1.demo_auth.helpers import(
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
)
from fastapi import(
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)
from jwt import InvalidTokenError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from users.shemas import UserSchema
from auth import utils as auth_utils
from pydantic import BaseModel
from users.shemas import UserSchema
import logging
from api_v1.demo_auth.crud import user_db

logger = logging.getLogger(__name__)


http_bearer = HTTPBearer(auto_error=False)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/demo-auth/jwt/login/")

def get_current_token_payload(
    token: str = Depends(oauth2_scheme)
) -> UserSchema:
    try:
        payload = auth_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error {e}",
        )
    return payload

def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload)
) -> UserSchema:
    token_type = payload.get(TOKEN_TYPE_FIELD)
    if token_type != ACCESS_TOKEN_TYPE:
        logger.warning(f"Invalid token type: {token_type}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token type {token_type!r} expected {ACCESS_TOKEN_TYPE}",
        )
    username: str | None = payload.get("sub")
    if (user := user_db.get(username)):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid not found",
    )
    
def validate_token_type(payload: dict, token_type: str) -> str:
    
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"invalid token type {current_token_type!r} expected {token_type}",
    )
    
def get_user_by_token_sub(payload: dict) -> UserSchema:
    username: str | None = payload.get("sub")
    if (user := user_db.get(username)):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid not found",
    )
    
def get_curent_active_from_user(
    user: UserSchema = Depends(get_current_auth_user)
):
    print(f"DEBUG user.active = {user.active}")
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="user inactive",
    )
    
def get_auth_user_from_token_of_type(token_type: str):
    def get_auth_user_from_token(
        payload: dict = Depends(get_current_token_payload),
) -> UserSchema:
        validate_token_type(payload, token_type)
        return get_user_by_token_sub(payload)
    return get_auth_user_from_token

class UserGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type
        
    def __call__(self,
                 payload: dict = Depends(get_current_token_payload)
    ):
        validate_token_type(payload, self.token_type)
        return get_user_by_token_sub(payload)

get_current_auth_user = get_auth_user_from_token_of_type(ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = UserGetterFromToken(REFRESH_TOKEN_TYPE)
