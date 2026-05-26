from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from config import settings
import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_token_from_cookie(request: Request) -> Optional[str]:
    return request.cookies.get("access_token")

def get_current_admin(request: Request, db: Session = Depends(get_db)) -> models.Utente:
    token = get_token_from_cookie(request)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Non autenticato"
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    utente = db.query(models.Utente).filter(models.Utente.email == email).first()
    if utente is None or not utente.is_admin:
        raise credentials_exception
    return utente

def require_admin(request: Request, db: Session = Depends(get_db)):
    try:
        return get_current_admin(request, db)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Redirect",
            headers={"Location": "/admin/login"}
        )