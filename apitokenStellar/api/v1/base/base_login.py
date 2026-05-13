from datetime import timedelta, datetime, timezone
from typing import Optional, List

from fastapi import HTTPException, Depends, Header, Request
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette import status

from api.v1 import roles, deps
from api.v1.deps import _reusable_oauth2


class UserCurrentLogin(BaseModel):
    id: int
    role: str
    invest_ids: Optional[str] = None  # Añade = None
    email: Optional[str] = None
    username: Optional[str] = None
    kyc_valid: Optional[int] = None
    language: Optional[str] = None
    user_type: Optional[int] = None



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _create_access_token(data: dict, expires_delta: Optional[timedelta]):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)  + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, deps.SECRET_KEY, algorithm=deps.ALGORITHM)
    return encoded_jwt


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )


def _get_user_login(
        *,
        token: str = Depends(_reusable_oauth2),
        request: Request
) -> UserCurrentLogin:
    # comprueba que el usuario o administrador esta logado si no lo esta error
    try:
        user = None
        payload = jwt.decode(token, deps.SECRET_KEY, algorithms=[deps.ALGORITHM])
        user_id: str = payload.get("id")
        role: str = payload.get("role")
        invest_ids: str = payload.get("invest_ids")

        if role == roles.ROLE_ADMIN:
            username: str = payload.get("username")
            # datos para el usuario ADMIN
            user = UserCurrentLogin(
                id=user_id,
                role=role,
                invest_ids=invest_ids,
                username=username,
            )
        elif role == roles.ROLE_USER:
            # datos para el usuario USER
            email: str = payload.get("email")
            name: str = payload.get("name")
            kyc_valid: str = payload.get("kyc_valid")
            language: str = payload.get("language")
            user_type: str = payload.get("user_type")

            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user = UserCurrentLogin(
                id=user_id,
                role=role,
                email=email,
                name=name,
                kyc_valid=kyc_valid,
                user_type=user_type
            )
            if language:
                user.language = language

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        request.state.user = user
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _get_user_if_login(
        *,
        token: str = Depends(_reusable_oauth2)
):
    # comprueba que el usuario esta logado pero no es obligatorio, es por si se necesitan mas datos
    try:
        payload = jwt.decode(token, deps.SECRET_KEY, algorithms=[deps.ALGORITHM])
        user_id: int = payload.get("id")
        if not user_id:
            return -1
    except Exception:
        return None
    return user_id
