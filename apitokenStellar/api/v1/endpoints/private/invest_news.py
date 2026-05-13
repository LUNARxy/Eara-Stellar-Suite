from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import roles
from api.v1.base.base import _can_access_roles, Object, _delete, _create, _update
from api.v1.base.base_files import _create_file_in_folder, _delete_file_in_folder
from api.v1.base.base_login import _get_user_login, UserCurrentLogin
from api.v1.deps import _get_db
from api.v1.models import models_invest

router = APIRouter()


@router.get("/list/{invest_id}")
def read_invest_news_list(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int
):
    """
    Se recuperan las noticias de una inversión
    """
    return db.query(models_invest.InvestNews) \
        .filter(models_invest.InvestNews.invest_id == invest_id) \
        .filter(models_invest.InvestNews.invest_id == models_invest.Invest.id) \
        .all()


@router.post("/{invest_id}")
def create_invest_news(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        title: str = Form(..., max_length=200),
        summary: str = Form(..., max_length=5000),
        url: str = Form(None, max_length=250),
        file: UploadFile = File(None),
):
    """
    Se sube una nueva noticia para la inversion
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    obj = Object()
    obj.invest_id = invest_id
    obj.title = title
    obj.summary = summary
    obj.url = url

    if file:
        # se crea la imagen el la carpeta del servidor
        my_folder = f"upload_files/earastellar/invest_project/{invest_project.slug}"
        file_name = _create_file_in_folder(uploaded_file=file, my_folder=my_folder, valid_file_type='image', name='news')
        obj.file = f'{my_folder}/{file_name}'

    return _create(db=db, obj_in=obj, table='invest_news')


@router.put("/{invest_id}/{news_id}")
def update_invest_news(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        news_id: int,
        title: str = Form(..., max_length=200),
        summary: str = Form(..., max_length=5000),
        url: str = Form(None, max_length=250),
        file: UploadFile = File(None),
):
    """
    se actualiza la noticia
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    invest_doc = db.query(models_invest.InvestNews).filter(models_invest.InvestNews.id == news_id).first()
    if not invest_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest document not found")

    obj = Object()
    obj.title = title
    obj.summary = summary
    obj.url = url

    if file:
        # se borra la imagen anterior de la carpeta del servidor
        _delete_file_in_folder(invest_doc.file)
        # se crea la imagen el la carpeta del servidor
        my_folder = f"upload_files/earastellar/invest_project/{invest_project.slug}"
        file_name = _create_file_in_folder(uploaded_file=file, my_folder=my_folder, valid_file_type='image', name='news')
        obj.file = f'{my_folder}/{file_name}'

    return _update(db=db, db_obj=invest_doc, obj_in=obj)


@router.delete("/{invest_id}/{news_id}")
def delete_news(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        news_id: int,
):
    """
    Se borra una noticia de la inversion
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    item_db = db.query(models_invest.InvestNews).filter(models_invest.InvestNews.id == news_id).first()
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.invest news not found")

    if _delete(db, obj_delete=item_db, route_file=f"public/{item_db.file}"):
        return {"ok": True}
    return {"ok": False}
