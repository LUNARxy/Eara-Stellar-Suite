from typing import Any

from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File, Query
from sqlalchemy.orm import Session
from starlette import status

from api.v1.models import models_invest

from api.v1.base.base_login import UserCurrentLogin, _get_user_login
from api.v1.deps import _get_db
from api.v1 import roles
from api.v1.base.base import _can_access_roles, _delete, _create, Object

router = APIRouter()


@router.post("/invest/{invest_id}")
def create_invest_me_follows(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_USER])),

        invest_id: int,
):
    """
    El usuario sigue una inversion
    """
    # comprobamos que exista el invest_id
    q = db.query(models_invest.Invest)
    q = q.filter(models_invest.Invest.id == invest_id)
    

    item = q.first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # miramos si ya estamos siguiendo
    q = db.query(models_invest.InvestFollows)
    q = q.filter(models_invest.InvestFollows.user_id == current_user.id)
    q = q.filter(models_invest.InvestFollows.invest_id == invest_id)
    item = q.first()
    if item:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="server.Project Invest already follow")

    obj = Object()
    obj.invest_id = invest_id
    obj.user_id = current_user.id
    return _create(db=db, obj_in=obj, table='invest_follows')


@router.delete("/invest/{invest_id}")
async def delete_follow(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_USER])),

        invest_id: int,
):
    """
    El usuario deja de seguir una inversion
    """
    q = db.query(models_invest.InvestFollows)
    q = q.filter(models_invest.InvestFollows.user_id == current_user.id)
    item = q.filter(models_invest.InvestFollows.invest_id == invest_id).first()
    if item and _delete(db, obj_delete=item):
        return {"ok": True}
    return {"ok": False}
