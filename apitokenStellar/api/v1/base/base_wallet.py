from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from api.v1 import const
from api.v1.deps import _get_db
from api.v1.models import models_user


def _get_wallet_value(
        *,
        db: Session = Depends(_get_db),
        user_id: int,
        with_claim: bool = True
):
    # recupera el valor que tiene el usuario en wallet
    q = db.query(models_user.UsersInvest.type, models_user.UsersInvest.value)
    q = q.filter(models_user.UsersInvest.user_id == user_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT_CLAIM,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT_TO_INVEST))
    list_invest = q.all()
    my_wallet_value = 0
    for item in list_invest:
        if item.type == const.USERS_INVEST_TYPE_DEPOSIT:
            my_wallet_value += item.value
        elif item.type == const.USERS_INVEST_TYPE_DEPOSIT_CLAIM and with_claim:
            my_wallet_value -= item.value
        elif item.type == const.USERS_INVEST_TYPE_DEPOSIT_TO_INVEST:
            my_wallet_value -= item.value

    return my_wallet_value
