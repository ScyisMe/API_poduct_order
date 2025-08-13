import jwt
import bcrypt

from datetime import datetime, timedelta, timezone

from core.config import settings

def encode_jwt(
    payload: dict,
    key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_timedelta: timedelta | None = None,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    
):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    
    if expire_timedelta:
        expire = now + timedelta(minutes=expire_minutes)
    else:
        expire = now + expire_minutes
        
    to_encode.update(
        exp=expire,
        iat=now,
    )
    
    
    encoded = jwt.encode(
        to_encode,
        key,
        algorithm=algorithm,
    )
    return encoded



def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(), 
    algorithm: str = settings.auth_jwt.algorithm,
):
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],)
    return decoded

def hash_password(
    password: str
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)

def validate_password(
    password: str,
    hashed_password: bytes  
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )
    