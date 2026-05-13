import os
import secrets
import string
from typing import List, Any

from fastapi import Header, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from jose import jwt
from slugify import slugify
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import deps
from api.v1.deps import _reusable_oauth2
from api.v1.models import models_invest, models_user, models_governor


class Object(object):
    pass


def _can_access_roles(roles_can_access: List):
    # obligatorio en todas las funciones, nos dice si tenemos permiso para acceder o no
    # se hace de esta forma porque sino no acepta los parametros roles_can_access
    def dependency(token: str = Depends(_reusable_oauth2)):
        # Implementa aquí la lógica para verificar el rol del usuario con roles_can_access
        return _get_access_dependency_aux(token=token, roles_can_access=roles_can_access)

    return dependency


def _get_access_dependency_aux(
        *,
        token: str,
        roles_can_access: List
):
    # se recupera el rol del usuario del token
    payload = jwt.decode(token, deps.SECRET_KEY, algorithms=[deps.ALGORITHM])
    user_role: str = payload.get("role")
    # print(f'ROL USER: {user_role}')
    # print(f'roles_can_access {roles_can_access}')
    if user_role not in roles_can_access:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The function is not found")


def _get_random_string(txt: str = "", max_num: int = 5):
    txt = txt[0:30]
    letters = string.digits + string.ascii_lowercase + string.ascii_uppercase
    result_str = ''.join(secrets.choice(letters) for i in range(max_num))

    result_str = slugify(f"{txt}_{result_str}")
    # result_str = f"{txt}_{result_str}"
    return result_str


def _create(db: Session, obj_in: Any, table: str):
    db_obj = None
    if table == 'invest':
        db_obj = models_invest.Invest(**obj_in.__dict__)
    elif table == 'invest_team':
        db_obj = models_invest.InvestTeam(**obj_in.__dict__)
    elif table == 'invest_news':
        db_obj = models_invest.InvestNews(**obj_in.__dict__)
    elif table == 'invest_documents':
        db_obj = models_invest.InvestDocuments(**obj_in.__dict__)
    elif table == 'invest_media':
        db_obj = models_invest.InvestMedia(**obj_in.__dict__)
    elif table == 'invest_questions':
        db_obj = models_invest.InvestQuestions(**obj_in.__dict__)
    elif table == 'invest_follows':
        db_obj = models_invest.InvestFollows(**obj_in.__dict__)
    elif table == 'invest_status_description':
        db_obj = models_invest.InvestStatusDescription(**obj_in.__dict__)
    elif table == 'users':
        db_obj = models_user.User(**obj_in.__dict__)
    elif table == 'users_follows':
        db_obj = models_user.UserFollows(**obj_in.__dict__)
    elif table == 'users_data_documents':
        db_obj = models_user.UserDataDocuments(**obj_in.__dict__)
    elif table == 'users_documents_others':
        db_obj = models_user.UserDocumentsOthers(**obj_in.__dict__)
    elif table == 'users_data_physical_person':
        db_obj = models_user.UserDataPhysicalPerson(**obj_in.__dict__)
    elif table == 'users_data_legal_person':
        db_obj = models_user.UserDataLegalPerson(**obj_in.__dict__)
    elif table == 'users_suscribed':
        db_obj = models_user.UserSubscribed(**obj_in.__dict__)
    elif table == 'users_invest_white_list':
        db_obj = models_user.UserInvestWhiteList(**obj_in.__dict__)
    elif table == 'users_invest_profit_percentage':
        db_obj = models_user.UsersInvestProfitPercentage(**obj_in.__dict__)
    elif table == 'invest_mint_phases':
        db_obj = models_invest.InvestMintPhases(**obj_in.__dict__)
    elif table == 'governor_transactions':
        db_obj = models_governor.GovernorTransactions(**obj_in.__dict__)
    elif table == 'governor_confirmations':
        db_obj = models_governor.GovernorConfirmations(**obj_in.__dict__)

    if not db_obj:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="server.Table not found")

    try:
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="server.Se ha producido un error inesperado")


def _update(db: Session, *, db_obj: Any, obj_in: Any):
    try:
        # update_data = obj_in.dict(exclude_unset=True)
        update_data = obj_in.__dict__

        obj_data = jsonable_encoder(db_obj)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="server.Se ha producido un error inesperado")


def _delete(db: Session, *, obj_delete: Any, route_file: str = None):
    if route_file is not None:
        # si existe fichero a borrar
        # file_location = f"public/{route_file}"
        if os.path.exists(route_file):
            os.remove(route_file)

    # se borra el registro de la bd
    db.delete(obj_delete)
    db.commit()
    return True
