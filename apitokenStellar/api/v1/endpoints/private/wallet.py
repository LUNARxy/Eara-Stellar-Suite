from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import asc, func, or_, desc
from starlette import status
from datetime import datetime


from api.v1 import roles, const
from api.v1.base.base import _can_access_roles, Object

from api.v1.base.base_login import _get_user_login, UserCurrentLogin
from api.v1.base.base_user import _get_user_by_id
from api.v1.base.base_wallet import _get_wallet_value
from api.v1.emails import emails
from api.v1.models import models_user, models_invest

from api.v1.deps import _get_db

router = APIRouter()


#########################################################################################################
#   FUNCIONES TIPO GET
#########################################################################################################
@router.get("/wallet_total_balance")
def read_wallet_total_balance_user(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_USER])),
):
    """
    se recuperan el balance total de mi wallet, mi wallet está en la tabla users_invest recuperando los estados
    """
    return _get_wallet_value(db=db, user_id=current_user.id)


@router.get("/wallet_data_all_users")
def read_wallet_data_all_users(
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        deposit_type: int = -1,
):
    """
    se recuperan datos de la pantalla de wallet
    """
    # se recuperan datos de la pantalla de wallet, solo los depositos que necesitan accion por parte del administrador
    q = db.query(models_user.UsersInvest, models_invest.Invest, models_user.User)

    q = q.filter(models_user.User.id == models_user.UsersInvest.user_id)
    if deposit_type == const.USERS_INVEST_TYPE_DEPOSIT_CLAIM:
        q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT_CLAIM)
    elif deposit_type == const.USERS_INVEST_TYPE_DEPOSIT_RECEIVED:
        q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT_RECEIVED)
    elif deposit_type == const.USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED:
        q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED)
    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="server.El tipo no es correcto")

    q = q.outerjoin(models_invest.Invest, models_user.UsersInvest.invest_id == models_invest.Invest.id)
    list_invest = q.order_by(desc(models_user.UsersInvest.date_created)).all()

    list_user_invest_verified = []
    # se recupera el listado de transacciones de reclamar wallet que ya se hayan verificado
    if deposit_type == const.USERS_INVEST_TYPE_DEPOSIT_CLAIM:
        q = db.query(models_user.UsersInvest.parent_id)
        
        q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT_RECEIVED)
        list_user_invest_verified = q.all()

    list_out = []
    for item in list_invest:
        put_item = True
        for item_verified in list_user_invest_verified:
            # si la transaccion ya ha sido verificada no se pone
            if item.UsersInvest.id == item_verified.parent_id:
                put_item = False
                break

        if put_item:
            aux = Object()
            aux.id = item.UsersInvest.id
            aux.user_id = item.UsersInvest.user_id
            aux.user_email = item.User.email
            aux.value = item.UsersInvest.value
            aux.iban = item.UsersInvest.iban
            aux.type = item.UsersInvest.type
            aux.buy_subtype = item.UsersInvest.buy_subtype
            aux.date_created = item.UsersInvest.date_created
            if item.Invest:
                aux.project_name = item.Invest.name
                aux.project_name_EN = item.Invest.name_EN

            list_out.append(aux)

    return list_out


@router.get("/wallet_data_user")
def read_wallet_data_user(
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])),

        user_id: int = 0,  # para filtrar por usuario
):
    """
    se recuperan datos de la wallet de un usuario
    """
    q = db.query(models_user.UsersInvest, models_invest.Invest)
    

    if current_user.role == roles.ROLE_ADMIN:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    elif current_user.role == roles.ROLE_USER:
        q = q.filter(models_user.UsersInvest.user_id == current_user.id)

    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT_CLAIM,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT_RECEIVED,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT_TO_INVEST,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED))
    q = q.outerjoin(models_invest.Invest, models_user.UsersInvest.invest_id == models_invest.Invest.id)
    list_invest = q.order_by(desc(models_user.UsersInvest.date_created)).all()
    list_out = []
    for item in list_invest:
        aux = Object()
        aux.id = item.UsersInvest.id
        aux.value = item.UsersInvest.value
        aux.parent_id = item.UsersInvest.parent_id
        aux.type = item.UsersInvest.type
        aux.iban = item.UsersInvest.iban
        aux.buy_subtype = item.UsersInvest.buy_subtype
        aux.date_created = item.UsersInvest.date_created
        if item.Invest:
            aux.project_name = item.Invest.name
            aux.project_name_EN = item.Invest.name_EN
        list_out.append(aux)

    return list_out


#########################################################################################################
#   FUNCIONES TIPO POST
#########################################################################################################
@router.post("/wallet_refund/{value_to_refund}")
async def save_wallet_refund(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_USER])),

        value_to_refund: float
):
    """
    El usuario pide una devolucion de dinero de su wallet y se apunta como reclamado para que desde el admin se haga
    """

    # se recupera el dato de la cuenta bancaria
    # user_bank = db.query(models_user.UserBankAccount).filter(models_user.UserBankAccount.user_id == current_user.id).first()
    # if not user_bank:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.No se han encontrado datos bancarios")

    # se mira si nos estamos pasando del maximo que tiene en wallet
    my_wallet_value = _get_wallet_value(db=db, user_id=current_user.id)
    # print(f'my_wallet_value {my_wallet_value} value_to_refund {value_to_refund}')

    if my_wallet_value < value_to_refund:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="server.No se puede retirar más dinero del que hay en la wallet")

    user_tokens_refund = models_user.UsersInvest(
        
        user_id=current_user.id,
        num_tokens=value_to_refund,
        price_token=1,
        value=value_to_refund,
        date_created=datetime.now(),
        type=const.USERS_INVEST_TYPE_DEPOSIT_CLAIM,
    )
    db.add(user_tokens_refund)
    db.commit()

    # se manda email
    await emails.send_email_profit_claim(current_user.language, current_user.email, str(value_to_refund))

    return {"ok": True}


@router.post("/wallet_validate_claim/{user_invest_id}/{user_id}")
async def save_wallet_validate_claim(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        user_invest_id: int,
        user_id: int
):
    # se valida por parte del administrador que hemos devuelto el dinero reclamado de la wallet

    # se valida que el usuario sea de esta marca blanca
    db_user = _get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.User not found")

    # recuperamos mediante el id el valor a devolver
    q = db.query(models_user.UsersInvest.value)
    q = q.filter(models_user.UsersInvest.id == user_invest_id)
    q = q.filter(models_user.UsersInvest.user_id == user_id)
    user_invest = q.first()
    if not user_invest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Unexpected error")

    # comprobamos que no se haya validado ya esta transacion con otra
    q = db.query(models_user.UsersInvest.id)
    q = q.filter(models_user.UsersInvest.parent_id == user_invest_id)
    q = q.filter(models_user.UsersInvest.user_id == user_id)
    user_invest_verified = q.first()
    if user_invest_verified:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.La transacción ya ha sido validada")

    value_to_refund = user_invest.value
    my_wallet_value = _get_wallet_value(db=db, user_id=user_id, with_claim=False)
    # print(f'my_wallet_value {my_wallet_value} value_to_refund {value_to_refund}')

    if my_wallet_value < value_to_refund:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="server.No se puede retirar más dinero del que hay en la wallet")

    # se recupera el dato de la cuenta bancaria
    user_bank = db.query(models_user.UserBankAccount.iban).filter(models_user.UserBankAccount.user_id == user_id).first()
    if not user_bank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.No se han encontrado datos bancarios")

    user_tokens_refund = models_user.UsersInvest(
        
        user_id=user_id,
        num_tokens=0,
        price_token=0,
        value=value_to_refund,
        date_created=datetime.now(),
        type=const.USERS_INVEST_TYPE_DEPOSIT_RECEIVED,
        parent_id=user_invest_id,
        iban=user_bank.iban
    )
    db.add(user_tokens_refund)
    db.commit()

    # email
    # send_email_refund_wallet_verified(language='es', email=current_user.email, value_to_refund=value_to_refund)

    return {"ok": True}
