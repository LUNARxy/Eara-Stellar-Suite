from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Query
from sqlalchemy import func, desc, or_
from sqlalchemy.orm import Session
from starlette import status
from datetime import datetime

from api.v1 import roles, const
from api.v1.base.base import _can_access_roles, Object
from api.v1.base.base_invest_profits import _get_list_user_profit_percentage
from api.v1.base.base_login import _get_user_login, UserCurrentLogin
from api.v1.base.base_invest import _get_num_tokens_in_date

from api.v1.deps import _get_db
from api.v1.emails import emails
from api.v1.models import models_invest, models_user

router = APIRouter()


@router.get("/list/{invest_id}")
def read_invest_profits(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int
):
    """
    Devuelve la lista de usuarios inversores para poder calcular el beneficio, además el historico de beneficios
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    q = db.query(models_invest.InvestProfit)
    q = q.filter(models_invest.InvestProfit.invest_id == models_invest.Invest.id)
    q = q.filter(models_invest.InvestProfit.invest_id == invest_id)
    
    q = q.order_by(desc(models_invest.Invest.date_created))
    list_items = q.all()

    list_profits = []
    for item in list_items:
        aux = Object()
        aux.id = item.id
        aux.invest_id = item.invest_id
        aux.profit = item.profit
        aux.date_profit = item.date_profit
        list_profits.append(aux)

    if invest_project.category_id == const.INVEST_CATEGORY_ID_INTEREST:
        # se recupera el listado de usuarios a los que les toca actualmente un reparto de beneficios mediante porcentaje
        list_users_out = _get_list_user_profit_percentage(db=db, profit_percentage=invest_project.profit_estimated, invest_id=invest_id, profit_day=25)
    else:
        # se recupera el listado de usuarios a los que les toca actualmente un reparto de beneficios por numero de tokens entre el total repartido
        # se recuperan todos los usuarios que han invertido en el proyecto
        q = db.query(models_user.UsersInvest.user_id)
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
        q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
        list_users = q.distinct().all()

        # para cada inversion, si tiene tokens mayor que cero se guardan en el listado
        list_users_out = []
        for item in list_users:
            num_tokens = _get_num_tokens_in_date(db=db,  date_end=datetime.now(), user_id=item.user_id, invest_id=invest_id)['num_tokens']
            if num_tokens > 0:
                # se recuperan sus datos
                q = db.query(models_user.User, models_user.UserDataPhysicalPerson)
                q = q.filter(models_user.User.id == item.user_id)
                q = q.outerjoin(models_user.UserDataPhysicalPerson, models_user.User.id == models_user.UserDataPhysicalPerson.user_id)
                for users in q.all():
                    aux_user = Object()
                    aux_user.user_id = users.User.id
                    aux_user.email = users.User.email
                    if users.UserDataPhysicalPerson:
                        aux_user.name = users.UserDataPhysicalPerson.name
                        aux_user.surname = users.UserDataPhysicalPerson.surname
                    aux_user.value = num_tokens
                    list_users_out.append(aux_user)

    return {'is_completed': invest_project.is_completed, 'list_profits': list_profits,
            'list_users': list_users_out, 'profit_percentage': invest_project.profit_estimated,
            'category_id': invest_project.category_id}


@router.get("/list/users/{profit_id}")
def read_invest_profits(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        profit_id: int
):
    """
    Devuelve la lista de beneficios que ya ha recibido cada usuario mediante el profit_id
    """
    # por cada reparto de beneficios se recuperan los usuarios a los que se le ha hecho el reparto
    q = db.query(models_user.UsersInvest, models_user.User, models_user.UserBankAccount, models_user.UserDataPhysicalPerson)
    q = q.filter(models_user.UsersInvest.profit_id == profit_id)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_PROFITS)
    q = q.filter(models_user.UsersInvest.user_id == models_user.User.id)
    q = q.outerjoin(models_user.UserBankAccount, models_user.UsersInvest.user_id == models_user.UserBankAccount.user_id)
    q = q.outerjoin(models_user.UserDataPhysicalPerson, models_user.UsersInvest.user_id == models_user.UserDataPhysicalPerson.user_id)
    list_users = q.all()

    # se recupera si hay retirada de dinero asociada al beneficio
    q = db.query(models_user.UsersInvest)
    q = q.filter(models_user.UsersInvest.profit_id == profit_id)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_DEPOSIT)
    list_users_profits_to_refund = q.all()

    list_out = []
    for users in list_users:
        aux_user = Object()
        aux_user.user_id = users.User.id
        aux_user.email = users.User.email
        if users.UserDataPhysicalPerson:
            aux_user.name = users.UserDataPhysicalPerson.name
            aux_user.surname = users.UserDataPhysicalPerson.surname
        else:
            aux_user.name = ""
            aux_user.surname = ""
        if users.UserBankAccount:
            aux_user.bic = users.UserBankAccount.bic
            aux_user.iban = users.UserBankAccount.iban
        else:
            aux_user.bic = ""
            aux_user.iban = ""
        aux_user.value = users.UsersInvest.value

        # para las retiradas asociadas al beneficio
        for users_profits_to_refund in list_users_profits_to_refund:
            if users.User.id == users_profits_to_refund.user_id:
                aux_user.profit_to_refund = users_profits_to_refund.value
                break

        list_out.append(aux_user)

    return list_out


@router.post("/generate/{invest_id}/{profit}")
async def post_invest_generate_profit(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        profit: float,
):
    # se reparten beneficios de la inversion entre los usuarios

    # comprobamos que exista el invest_id
    q = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id)
    
    invest_project = q.first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")
    if invest_project.category_id == const.INVEST_CATEGORY_ID_INTEREST:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.Invest is profit percentage")

    # si el proyecto ya se ha cerrado error
    if invest_project.is_completed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.El proyecto ya se ha cerrado")

    try:
        # se guarda el beneficio en la tabla de beneficios
        item_profit = models_invest.InvestProfit(
            invest_id=invest_id,
            profit=profit,
        )
        db.add(item_profit)

        db.flush()  # se pone en la base de datos para que cree el id, todavia no hay commit

        actual_date = datetime.now()

        # se recuperan todos los usuarios que han invertido en el proyecto
        q = db.query(models_user.UsersInvest.user_id)
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
        q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
        list_users = q.distinct().all()

        num_tokens_sold_total = 0
        list_users_tokens = []
        # para cada inversion, si tiene tokens mayor que cero se guardan en el listado
        for user in list_users:
            num_tokens = _get_num_tokens_in_date(db=db,  date_end=actual_date, user_id=user.user_id, invest_id=invest_id)['num_tokens']
            if num_tokens > 0:
                num_tokens_sold_total += num_tokens
                aux = Object()
                aux.user_id = user.user_id
                aux.num_tokens = num_tokens
                list_users_tokens.append(aux)

        # se divide el beneficio por cada token
        # profit = math.floor((profit / float(num_tokens_sold_total)) * 100) / 100.0
        profit = profit / num_tokens_sold_total
        # print(f'total tokens {num_tokens_sold_total}')
        # print(f'beneficio por token {profit}')

        # se recorren los tokens que tenemos comprados y se inserta su beneficio
        # el beneficio no va a asociado a los id de la tabla invest_users sino que se suma lo comprado menos lo vendido y ese es el valor
        for item in list_users_tokens:
            # print(f'valor para el usuario {item.user_id} {round(item.num_tokens * profit, 2)}')

            # se inserta como beneficio
            user_tokens = models_user.UsersInvest(
                
                user_id=item.user_id,
                invest_id=invest_id,
                num_tokens=item.num_tokens,
                price_token=profit,
                value=item.num_tokens * profit,
                date_created=datetime.now(),
                type=const.USERS_INVEST_TYPE_PROFITS,
                profit_id=item_profit.id,
            )
            db.add(user_tokens)

        # una vez añadido todos los beneficios a los usuarios se guarda en base de datos
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="server.Se ha producido un error inesperado")

    # se manda un email a cada usuario
    for item in list_users_tokens:
        await emails.send_email_profit_distribution(current_user.language, current_user.email, invest_project.name, invest_project.slug)

    return {"ok": True}


@router.post("/generate_percentage/{invest_id}")
async def post_invest_generate_percentage(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int
):
    # se reparten beneficios de la inversion entre los usuarios
    # se reparten segun el porcentaje puesto en el proyecto en el campo profit_estimated
    # se recuperan las inversiones de los usuarios y se calcula su porcentaje de beneficio

    # comprobamos que exista el invest_id y que tenga el beneficio en porcentaje
    q = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id)
    
    invest_project = q.first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")
    if invest_project.category_id != const.INVEST_CATEGORY_ID_INTEREST:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.Invest is profit token")

    # si el proyecto ya se ha cerrado error
    if invest_project.is_completed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.El proyecto ya se ha cerrado")

    try:
        # se recupera el listado de usuarios a los que les toca actualmente un reparto de beneficios
        list_users = _get_list_user_profit_percentage(db=db, profit_percentage=invest_project.profit_estimated, invest_id=invest_id, profit_day=25)

        total_profit = 0
        for item in list_users:
            total_profit += item.value

        # se guarda el beneficio en la tabla de beneficios
        item_profit = models_invest.InvestProfit(
            invest_id=invest_id,
            profit=total_profit
        )
        db.add(item_profit)
        db.flush()  # se pone en la base de datos para que cree el id, todavia no hay commit

        # tenemos a cada usuario con su valor para insertarlo
        for item in list_users:
            # primero revisamos el porcentaje que el usuario no quiere sacar y el que si quiere y se resta del beneficio
            q = db.query(models_user.UsersInvestProfitPercentage)
            q = q.filter(models_user.UsersInvestProfitPercentage.invest_id == invest_id)
            q = q.filter(models_user.UsersInvestProfitPercentage.user_id == item.user_id)
            profit_percentage_to_refund = q.first()
            # print(f'Usuario: {item.user_id}')
            # print(f'valor total que le toca {item.value}€')
            value_to_refund = 0

            if profit_percentage_to_refund:
                profit_percentage_to_refund = profit_percentage_to_refund.profit_percentage
                value_to_refund = item.value * profit_percentage_to_refund / 100
                # print(f'valor porcentage a devolver {profit_percentage_to_refund}%')
                # print(f'valor total a devolver {value_to_refund}€')
                # print(f'valor total a reinvertir {(item.value - value_to_refund)}€')

            # se inserta el beneficio total, no se resta lo devuelto
            user_tokens = models_user.UsersInvest(
                
                user_id=item.user_id,
                invest_id=invest_id,
                num_tokens=1,
                price_token=item.value,
                value=item.value,
                date_created=datetime.now(),
                type=const.USERS_INVEST_TYPE_PROFITS,
                profit_id=item_profit.id
            )
            db.add(user_tokens)
            db.flush()

            # se inserta el resto como nueva inversión
            user_tokens_new_invest = models_user.UsersInvest(
                
                user_id=item.user_id,
                invest_id=invest_id,
                num_tokens=1,
                price_token=item.value - value_to_refund,
                value=item.value - value_to_refund,
                date_created=datetime.now(),
                type=const.USERS_INVEST_TYPE_BUY,
                buy_subtype=const.BUY_SUBTYPE_PAYMENT_PROFITS_INVEST,
                profit_id=item_profit.id
            )

            db.add(user_tokens_new_invest)

            # se inserta la devolución de los tokens a la wallet, es un deposito
            user_tokens_refund = models_user.UsersInvest(
                
                user_id=item.user_id,
                invest_id=invest_id,
                num_tokens=1,
                price_token=value_to_refund,
                value=value_to_refund,
                date_created=datetime.now(),
                type=const.USERS_INVEST_TYPE_DEPOSIT,
                buy_subtype=const.DEPOSIT_SUBTYPE_PROFITS,
                profit_id=item_profit.id
            )
            db.add(user_tokens_refund)

        # una vez añadido todos los beneficios a los usuarios se guarda en base de datos
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="server.Se ha producido un error inesperado")

    # se manda un email a cada usuario
    for item in list_users:
        await emails.send_email_profit_distribution(current_user.language, current_user.email, invest_project.name, invest_project.slug)
    return {"ok": True}
