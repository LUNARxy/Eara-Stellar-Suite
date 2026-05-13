from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, asc, or_
from starlette import status

from api.v1 import roles
from api.v1.base.base import _can_access_roles, Object, _delete, _create, _update
from api.v1.base.base_files import _create_file_in_folder, _delete_file_in_folder
from api.v1.base.base_login import _get_user_login, UserCurrentLogin
from api.v1.deps import _get_db
from api.v1.models import models_invest

router = APIRouter()


@router.get("/list/{invest_id}")
def read_invest_status_description_list(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int
):
    """
    Devuelve la lista de descripciones del estado de la inversion
    """
    return db.query(models_invest.InvestStatusDescription) \
        .filter(models_invest.InvestStatusDescription.invest_id == invest_id) \
        .filter(models_invest.Invest.id == models_invest.InvestStatusDescription.invest_id) \
        .order_by(desc(models_invest.InvestStatusDescription.date_created)) \
        .all()


@router.post("/{invest_id}")
def create_invest_status_description(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        phase: int = Form(None),
        description: str = Form(..., max_length=200),
        date_created: datetime = Form(None),  # fecha de inicio de la fase
):
    """
    Se crea una nueva descripcion
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    obj = Object()
    obj.invest_id = invest_id
    obj.description = description
    obj.date_created = date_created

    if phase:
        obj.phase = phase

    return _create(db=db, obj_in=obj, table='invest_status_description')


@router.delete("/{invest_id}/{description_id}", status_code=status.HTTP_200_OK, summary="Delete a invest status description by Id")
def delete_status_description(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        description_id: int,
):
    """
    Se borra
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    item_db = db.query(models_invest.InvestStatusDescription).filter(models_invest.InvestStatusDescription.id == description_id).first()
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.invest phases not found")

    if _delete(db, obj_delete=item_db):
        return {"ok": True}
    return {"ok": False}
