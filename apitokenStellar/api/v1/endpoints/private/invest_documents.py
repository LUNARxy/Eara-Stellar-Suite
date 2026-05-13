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
def read_invest_docs_list(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int
):
    """
    Se recupera la lista de documentos de una inversión
    """
    return db.query(models_invest.InvestDocuments) \
        .filter(models_invest.InvestDocuments.invest_id == invest_id) \
        .filter(models_invest.InvestDocuments.invest_id == models_invest.Invest.id) \
        .all()


@router.post("/{invest_id}")
def create_invest_docs(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        file: UploadFile = File(...),
        description: str = Form(None, max_length=200),
):
    """
    Se sube una nuevo documento para la inversion
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # se crea la imagen el la carpeta del servidor
    my_folder = f"upload_files/earastellar/invest_project/{invest_project.slug}"
    file_name = _create_file_in_folder(uploaded_file=file, my_folder=my_folder, valid_file_type='document', name='document')
    file_name = f'{my_folder}/{file_name}'

    obj = Object()
    obj.invest_id = invest_id
    obj.file = file_name
    obj.description = description
    return _create(db=db, obj_in=obj, table='invest_documents')


@router.delete("/{invest_id}/{documents_id}")
def delete_docs(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        documents_id: int,
):
    """
    Se borra un documento de la inversion
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    item_db = db.query(models_invest.InvestDocuments).filter(models_invest.InvestDocuments.id == documents_id).first()
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.invest documents not found")

    if _delete(db, obj_delete=item_db, route_file=f"public/{item_db.file}"):
        return {"ok": True}
    return {"ok": False}
