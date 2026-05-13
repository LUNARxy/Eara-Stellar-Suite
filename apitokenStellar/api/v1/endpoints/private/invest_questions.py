from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import roles
from api.v1.base.base import _can_access_roles, Object, _delete, _create, _update
from api.v1.base.base_login import _get_user_login, UserCurrentLogin
from api.v1.deps import _get_db
from api.v1.models import models_invest

router = APIRouter()


@router.get("/list/{invest_id}")
def read_invest_questions_list(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int
):
    """
    Se recupera el listado de preguntas de una inversion
    """
    return db.query(models_invest.InvestQuestions) \
        .filter(models_invest.InvestQuestions.invest_id == invest_id) \
        .filter(models_invest.InvestQuestions.invest_id == models_invest.Invest.id) \
        .all()


@router.post("/{invest_id}")
def create_invest_questions(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        title: str = Form(..., max_length=200),
        comment: str = Form(..., max_length=2000),
):
    """
    Se sube una nueva pregunta
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    obj = Object()
    obj.invest_id = invest_id
    obj.title = title
    obj.comment = comment

    return _create(db=db, obj_in=obj, table='invest_questions')


@router.put("/{invest_id}/{questions_id}")
def update_invest_questions(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        questions_id: int,
        title: str = Form(..., max_length=200),
        comment: str = Form(..., max_length=2000),
):
    """
    Se actualiza el item
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    invest_questions = db.query(models_invest.InvestQuestions).filter(models_invest.InvestQuestions.id == questions_id).first()
    if not invest_questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest question not found")

    obj = Object()
    obj.title = title
    obj.comment = comment

    return _update(db=db, db_obj=invest_questions, obj_in=obj)


@router.delete("/{invest_id}/{questions_id}")
def delete_questions(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        questions_id: int,
):
    """
    Se borra
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    item_db = db.query(models_invest.InvestQuestions).filter(models_invest.InvestQuestions.id == questions_id).first()
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.invest questions not found")

    if _delete(db, obj_delete=item_db):
        return {"ok": True}
    return {"ok": False}
