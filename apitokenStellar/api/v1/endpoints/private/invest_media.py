from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import roles
from api.v1.base.base import _can_access_roles, Object, _delete, _create
from api.v1.base.base_files import _create_file_in_folder
from api.v1.base.base_login import _get_user_login, UserCurrentLogin
from api.v1.deps import _get_db
from api.v1.models import models_invest

router = APIRouter()


@router.get("/list/{invest_id}")
def read_invest_media_list(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

    invest_id: int
):
    """
    Se recupera la galeria de imagenes de una inversión
    """
    return db.query(models_invest.InvestMedia) \
        .filter(models_invest.InvestMedia.invest_id == invest_id) \
        .filter(models_invest.InvestMedia.invest_id == models_invest.Invest.id) \
        .all()


@router.post("/{invest_id}")
def create_invest_media(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        file: UploadFile = File(...),
        description: str = Form(None, max_length=200),
):
    """
    Se sube una nueva imagen para la inversion
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # se crea la imagen el la carpeta del servidor
    my_folder = f"upload_files/earastellar/invest_project/{invest_project.slug}"
    file_name = _create_file_in_folder(
        name='gallery',
        uploaded_file=file,
        my_folder=my_folder,
        valid_file_type='image')
    file_name = f'{my_folder}/{file_name}'

    obj = Object()
    obj.invest_id = invest_id
    obj.file = file_name
    obj.description = description
    obj.is_video = False
    return _create(db=db, obj_in=obj, table='invest_media')


@router.delete("/{invest_id}/{media_id}")
def delete_media(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        media_id: int,
):
    """
    Se borra una foto de la galeria de la inversion
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    item_db = db.query(models_invest.InvestMedia).filter(models_invest.InvestMedia.id == media_id).first()
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invest media not found")

    if _delete(db, obj_delete=item_db, route_file=f"public/{item_db.file}"):
        return {"ok": True}
    return {"ok": False}
