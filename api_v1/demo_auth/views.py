import secrets
import uuid
from time import time
from fastapi import APIRouter, Depends, HTTPException, status, Header, Response, Cookie
from typing import Annotated
from fastapi.security import HTTPBasic, HTTPBasicCredentials


router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"])

security = HTTPBasic()

@router.get("/basic-auth/")
def demo_basic_auth_creadentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    return{
        "message": "Hi!",
        "username": credentials.username,
        "password": credentials.password,
    }
    
username_to_passwords = {
    "admin": "admin",
    "john": "password",
}

static_auth_token_to_username = {
    "OueGldkrSUaOLduEMGlw57HWaM43jaFGk": "admin",
    "qZuTBgmT2gI29xpRZIw50RGKhYEjXz3": "john",
}

def get_username_by_static_auth_token(
    static_token: str = Header(alias="x-auth-token")
    ) -> str:
    if username := static_auth_token_to_username.get(static_token):
        return username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid",
    )


def get_auth_user_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    unauth_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    correct_password = username_to_passwords.get(credentials.username)
    if correct_password is None:
        raise unauth_exc
    
    if not secrets.compare_digest(
        credentials.password.encode("utf-8"),
        correct_password.encode("utf-8"),
    ):
        raise unauth_exc
    
    return credentials.username
    
    
@router.get("/basic-auth-username/")
def demo_basic_auth_username(
    auth_username: str = Depends(get_auth_user_username)
):
    return{
        "message": f"Hi!, {auth_username}!",
        "username": auth_username,
    }
    
@router.get("/basic-http-header-auth/")
def demo_auth_some_http_header(
    auth_username: str = Depends(get_username_by_static_auth_token)
):
    return{
        "message": f"Hi!, {auth_username}!",
        "username": auth_username,
    }
    
COOKIES: dict[str, dict[str, any]] = {}
COOKIE_SESSION_ID_KEY = "web-app-session-id"


def generate_session_id() -> str:
    return uuid.uuid4().hex
    
def get_session_data(
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
):
    if session_id not in COOKIES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated",
        )
    return COOKIES[session_id]

@router.post("/login-cookie/")
def demo_auth_login_set_cookie(
    response: Response,
    auth_username: str = Depends(get_auth_user_username),
):
    session_id =generate_session_id()
    COOKIES[session_id] = {
        "username": auth_username,
        "login_at": int(time())
    }
    response.set_cookie(COOKIE_SESSION_ID_KEY, session_id)
    return {"result": "ok"}

@router.get("/check-cookie")
def demo_auth_check_cookie(
    user_session_data: dict = Depends(get_session_data),
):
    username = user_session_data["username"]
    return {
        "massage": f"Hello , {username}!",
        **user_session_data,
    }

@router.get("/logout-cookie")
def demo_auth_check_cookie(\
    response: Response,
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
    user_session_data: dict = Depends(get_session_data),
):
    COOKIES.pop(session_id)
    username = user_session_data["username"]
    response.delete_cookie(COOKIE_SESSION_ID_KEY)
    return {
        "massage": f"Bye , {username}!",
    }