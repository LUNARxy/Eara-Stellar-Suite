import secrets
import time
from datetime import timedelta, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import roles, deps
from api.v1.base.base import _get_random_string, _update, _create, Object
from api.v1.base.base_login import UserCurrentLogin, _get_user_login
from api.v1.base.base_login import _verify_password, _create_access_token, _get_password_hash
from api.v1.deps import _get_db
from api.v1.emails import emails
from api.v1.models import models_user

router = APIRouter()


class Token(BaseModel):
    access_token: str
    refresh_access_token: str
    token_type: str
    user_id: Optional[int]=0
    expiration: int



@router.post("/access_token")
async def get_access_token(
        db: Session = Depends(_get_db),
        form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    If 2FA is enabled for the white label, returns a temp_token instead and sends 2FA code via email.
    """
    # si viene el client_secret como es un campo oculto que no deberia venir es que es un bot, rechazamos el login
    if form_data.client_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.Incorrect email or password")

    role = roles.ROLE_USER

    if form_data.scopes and len(form_data.scopes) == 1 and form_data.scopes[0] == 'admin':
        # se mira si existe como usuario administrador
        user = db.query(models_user.UserAdmin).filter(models_user.UserAdmin.user == form_data.username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
        else:
            if not _verify_password(form_data.password, user.hashed_password):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
            role = roles.ROLE_ADMIN

        # Datos del token para admin
        token_data = {
            "id": user.id,
            "role": role,
            "invest_ids": getattr(user, "invest_ids", None),
            "username": form_data.username,
        }

        access_token = _create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=deps.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_access_token_expires = timedelta(minutes=deps.REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_access_token = _create_access_token(
            data={**token_data, "is_refresh": True},
            expires_delta=refresh_access_token_expires
        )
    else:
        # miramos en la parte de login de usuario
        q = db.query(models_user.User.id, models_user.User.email, models_user.User.hashed_password, models_user.User.change_hashed_password,
                     models_user.User.change_password_date, models_user.User.is_active, models_user.User.kyc_valid,
                     models_user.User.language, models_user.User.user_type)
        q = q.filter(models_user.User.email == form_data.username)
        
        user = q.first()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.Incorrect email or password")
        elif not _verify_password(form_data.password, user.hashed_password):
            # el password principal falla, comprobamos si hay un password de recuperar clave
            if _verify_password(form_data.password, user.change_hashed_password):
                # coincide pero no es el password normal, es el de recuperar del campo change_hashed_password
                # hay que validar que no haya pasado mas tiempo de 24 horas para ese password
                if datetime.now() - timedelta(days=+1) > user.change_password_date:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.It has been more than 24 hours since you retrieved your password. Recover again to create a new one")
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.Incorrect email or password")
        elif not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.Inactive user")

        # Datos del token para usuario
        token_data = {
            "id": user.id,
            "role": role,
            "email": user.email,
            "kyc_valid": user.kyc_valid,
            "language": user.language,
            "user_type": user.user_type
        }

        access_token = _create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=deps.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_access_token_expires = timedelta(minutes=deps.REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_access_token = _create_access_token(
            data={**token_data, "is_refresh": True},
            expires_delta=refresh_access_token_expires
        )

    user_out = Token(
        access_token=access_token,
        refresh_access_token=refresh_access_token,
        token_type="bearer",
        user_id=user.id,
        expiration=int((time.time() + (60 * deps.REFRESH_TOKEN_EXPIRE_MINUTES)) * 1000),
    )

    return user_out



@router.get("/access_token_refresh", response_model=Token, summary="Refresh tokens")
def get_access_token_refresh(
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
):
    if current_user.role == roles.ROLE_ADMIN:

        access_token_expires = timedelta(minutes=deps.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = _create_access_token(
            data={
                "id": current_user.id,
                "role": current_user.role,
                "invest_ids": current_user.invest_ids,
                "username": current_user.username,
            },
            expires_delta=access_token_expires
        )
        refresh_access_token_expires = timedelta(minutes=deps.REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_access_token = _create_access_token(
            data={
                "id": current_user.id,
                "role": current_user.role,
                "invest_ids": current_user.invest_ids,
                "username": current_user.username,
                "is_refresh": True
            },
            expires_delta=refresh_access_token_expires
        )
        user_out = Token(
            access_token=access_token,
            refresh_access_token=refresh_access_token,
            token_type="bearer",
            user_id=current_user.id,
            expiration=int((time.time() + (60 * deps.REFRESH_TOKEN_EXPIRE_MINUTES)) * 1000),
        )
        return user_out
    elif current_user.role == roles.ROLE_USER:
        access_token_expires = timedelta(minutes=deps.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = _create_access_token(
            data={
                "id": current_user.id,
                "role": current_user.role,
                "email": current_user.email,
                "kyc_valid": current_user.kyc_valid,
                "language": current_user.language,
                "user_type": current_user.user_type
            },
            expires_delta=access_token_expires
        )
        refresh_access_token_expires = timedelta(minutes=deps.REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_access_token = _create_access_token(
            data={
                "id": current_user.id,
                "role": current_user.role,
                "email": current_user.email,
                "kyc_valid": current_user.kyc_valid,
                "language": current_user.language,
                "user_type": current_user.user_type,
                "is_refresh": True
            },
            expires_delta=refresh_access_token_expires
        )
        user_out = Token(
            access_token=access_token,
            refresh_access_token=refresh_access_token,
            token_type="bearer",
            user_id=current_user.id,
            expiration=int((time.time() + (60 * deps.REFRESH_TOKEN_EXPIRE_MINUTES)) * 1000),
        )
        return user_out
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.User not found")


@router.post("/create_user")
async def create_user(
        db: Session = Depends(_get_db),
        email: str = Form(..., max_length=100),
        password: str = Form(..., min_length=8, max_length=50),
        language: str = Form('es'),  # idioma para el mensaje de email
):
    """
    Se crea un usuario nuevo si es que se puede por la marca blanca
    """
    # error si el email existe
    db_user = db.query(models_user.User).filter(models_user.User.email == email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="server.Email already registered")

    # el usuario no existe, lo creamos
    obj_in = Object()
    obj_in.email = email
    obj_in.hashed_password = _get_password_hash(password)
    obj_in.is_active = 1
    obj_in.language = language

    return _create(db=db, obj_in=obj_in, table='users')


@router.get("/email_recovery_pass/{email}")
async def email_recovery_pass(
        *,
        db: Session = Depends(_get_db),
        email: str,
        language: str = 'en'  # idioma para el mensaje de email
):
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.Email not exist or is not active")

    db_user = db.query(models_user.User).filter(models_user.User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Email not exist or is not active")

    # creamos una nueva clave y una fecha de validez de la nueva contraseña
    new_pass = _get_random_string('', 20)
    obj_in = Object()
    obj_in.change_hashed_password = _get_password_hash(new_pass)
    obj_in.change_password_date = datetime.now()
    user = _update(db, db_obj=db_user, obj_in=obj_in)

    if user:
        await emails.send_email_user_recovery_pass(language=language, email=email, new_pass=new_pass)
        return {'ok': True}
    else:
        return {'ok': False}

