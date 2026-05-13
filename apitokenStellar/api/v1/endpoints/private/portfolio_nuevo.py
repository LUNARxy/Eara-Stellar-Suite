import logging
from datetime import datetime, time
from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, asc
from sqlalchemy import cast, Date
from starlette import status

from api.v1 import roles, const
from api.v1.base.base import _can_access_roles
from api.v1.deps import _get_db
from api.v1.base.base_login import _get_user_login, UserCurrentLogin
from api.v1.models import models_invest, models_user

router = APIRouter()

class Object(object):
    pass


def _get_dates_for_charts_and_percentage(
        *,
        db: Session = Depends(_get_db),
        
        num_dates: int = 1,

        category_id: int = -1,  # para filtrar por categoría de la inversion
        user_id: int = -1,  # para filtrar por usuario
        invest_id: int = -1,  # para filtrar por inversion
        only_invest_ids: str = None # ids, separados por comas de las inversiones que puede ver el usuario
):
    q = db.query(cast(models_user.UsersInvest.date_created, Date))
    
    q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
    q = q.filter(models_invest.Invest.category_id == category_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND_PARTIAL,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_PROFITS
                     ))
    if user_id != -1:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if invest_id != -1 and invest_id != 11:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)

    if only_invest_ids:
        only_invest_ids_list = [int(i.strip()) for i in only_invest_ids.split(',') if i.strip().isdigit()] if only_invest_ids else [-1]
        q = q.filter(models_user.UsersInvest.invest_id.in_(only_invest_ids_list))

    list_dates = q.distinct().order_by(desc(models_user.UsersInvest.date_created), desc(models_user.UsersInvest.id)).limit(num_dates).all()

    # se recuperan las fechas de las fases
    q = db.query(func.date(models_invest.InvestMintPhases.date_start))
    if invest_id != 0:
        q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
    q = q.filter(models_invest.InvestMintPhases.invest_id == models_invest.Invest.id)
    
    if category_id != -1:
        q = q.filter(models_invest.Invest.category_id == category_id)
    list_phases = q.distinct().limit(num_dates).all()

    list_out = []
    # Añadir items de list_dates con sus fechas
    for item in list_dates:
        # ponemos la hora y los minutos a 23:59:59
        dt_fixed = datetime.combine(item[0], time(23, 59, 59))
        if dt_fixed not in list_out:
            list_out.append(dt_fixed)

    # Añadir items de list_phases con sus fechas
    for item in list_phases:
        # ponemos la hora y los minutos a 23:59:59
        dt_fixed = datetime.combine(item[0], time(23, 59, 59))
        if dt_fixed not in list_out:
            list_out.append(dt_fixed)

    # Eliminar duplicados con set()
    list_out = list(set(list_out))

    # Ordenar por la fecha completa
    list_out.sort()

    # cogemos solo las num_dates ultimas fechas
    list_out = list_out[-num_dates:]
    return list_out

def _balance_value(
        *,
        db: Session,
        

        category_id: int = -1,  # para filtrar por categoría de la inversion
        user_id: int = -1,  # para filtrar por usuario
        invest_id: int = -1,  # para filtrar por inversion
        date_end: datetime = None, # fecha de calculo para coger lo anterior
        only_invest_ids: str = None # ids, separados por comas de las inversiones que puede ver el usuario
):
    """
    Devuelve el dato de balance inicial
    """

    # se recupera lo comprado y vendido
    q = db.query(models_user.UsersInvest.invest_id, models_user.UsersInvest.type, models_user.UsersInvest.num_tokens, models_user.UsersInvest.price_token)
    
    q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
    q = q.filter(models_invest.Invest.category_id == category_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD))

    if user_id != -1:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if invest_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    if date_end:
        q = q.filter(models_user.UsersInvest.date_created <= date_end)
    if only_invest_ids:
        only_invest_ids_list = [int(i.strip()) for i in only_invest_ids.split(',') if i.strip().isdigit()] if only_invest_ids else [-1]
        q = q.filter(models_user.UsersInvest.invest_id.in_(only_invest_ids_list))

    list_items = q.order_by(asc(models_user.UsersInvest.date_created), asc(models_user.UsersInvest.id)).all()

    value_total = 0

    # a lo comprado se le resta lo vendido, lo primero comprado es lo primero en venderse
    list_items_buys = []  # List to store purchases
    total_cost = 0
    for item in list_items:
        if item.type == const.USERS_INVEST_TYPE_BUY:
            # Añadimos cada compra a la lista de compras
            aux = Object()
            aux.num_tokens = item.num_tokens
            aux.price_token = item.price_token
            value_total += item.num_tokens * item.price_token
            list_items_buys.append(aux)
        else:
            num_tokens_to_sold = item.num_tokens
            while num_tokens_to_sold > 0 and list_items_buys:
                last_buy = list_items_buys[0]  # Take the old purchase
                if last_buy.num_tokens <= num_tokens_to_sold:
                    # Calculate the cost for all tokens in this purchase
                    cost = last_buy.price_token * last_buy.num_tokens
                    total_cost += cost

                    # Subtract the sold quantity
                    num_tokens_to_sold -= last_buy.num_tokens
                    list_items_buys.pop(0)  # Remove the processed purchase
                else:
                    # Calculate the cost for only part of the purchase
                    cost = last_buy.price_token * num_tokens_to_sold
                    total_cost += cost

                    # Subtract the sold quantity from this purchase
                    last_buy.num_tokens -= num_tokens_to_sold
                    num_tokens_to_sold = 0

    # se recupera lo devuelto para restarlo de las compras
    q = db.query(models_user.UsersInvest.type, models_user.UsersInvest.value)
    
    q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
    q = q.filter(models_invest.Invest.category_id == category_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND,
                     #models_user.UsersInvest.type == const.USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND_PARTIAL
                     ))
    if user_id != -1:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if invest_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    if date_end:
        q = q.filter(models_user.UsersInvest.date_created <= date_end)

    list_items = q.order_by(asc(models_user.UsersInvest.date_created), asc(models_user.UsersInvest.id)).all()
    value_refund = 0
    for item in list_items:
        # restamos
        value_refund += item.value

    value_total -= total_cost+value_refund

    return value_total


def _invest_value(
        *,
        db: Session,
        

        category_id: int = -1,  # para filtrar por categoría de la inversion
        user_id: int = -1,  # para filtrar por usuario
        invest_id: int = -1,  # para filtrar por inversion
        date_end: datetime = None, # fecha de calculo para coger lo anterior
        invest_child_id: int = -1, # para filtrar por inversion hijo (caso credere)
        only_invest_ids: str = None # ids, separados por comas de las inversiones que puede ver el usuario
):
    """
    Devuelve el dato de la inversion que es el balance mas los beneficios
    """
    balance = _balance_value(db=db, category_id=category_id, invest_id=invest_id, user_id=user_id, date_end=date_end, only_invest_ids=only_invest_ids)
    profits = _profits_value(db=db, category_id=category_id, invest_id=invest_id, user_id=user_id, date_end=date_end, only_invest_ids=only_invest_ids)

    return balance + profits


def _profits_value(
        *,
        db: Session,
        

        category_id: int = -1,  # para filtrar por categoría de la inversion
        user_id: int = -1,  # para filtrar por usuario
        invest_id: int = -1,  # para filtrar por inversion
        date_end: datetime = None, # fecha de calculo para coger lo anterior
        invest_child_id: int = -1, # para filtrar por inversion hijo (caso credere)
        only_invest_ids: str = None # ids, separados por comas de las inversiones que puede ver el usuario
):
    """
    Devuelve el dato de los beneficios
    """
    # se recupera lo comprado y vendido
    q = db.query(models_user.UsersInvest.invest_id, models_user.UsersInvest.type, models_user.UsersInvest.num_tokens, models_user.UsersInvest.price_token)
    
    q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
    q = q.filter(models_invest.Invest.category_id == category_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD))
    if user_id != -1:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if invest_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    if date_end:
        q = q.filter(models_user.UsersInvest.date_created <= date_end)
    if only_invest_ids:
        only_invest_ids_list = [int(i.strip()) for i in only_invest_ids.split(',') if i.strip().isdigit()] if only_invest_ids else [-1]
        q = q.filter(models_user.UsersInvest.invest_id.in_(only_invest_ids_list))

    list_items = q.order_by(asc(models_user.UsersInvest.date_created), asc(models_user.UsersInvest.id)).all()

    # a lo comprado se le resta lo vendido, lo primero comprado es lo primero en venderse
    list_items_buys = []  # List to store purchases
    total_sold = 0  # Total profit from all sales
    for item in list_items:
        if item.type == const.USERS_INVEST_TYPE_BUY:
            # Añadimos cada compra a la lista de compras
            aux = Object()
            aux.num_tokens = item.num_tokens
            aux.price_token = item.price_token
            list_items_buys.append(aux)
        else:
            num_tokens_to_sold = item.num_tokens
            total_sale_revenue = num_tokens_to_sold * item.price_token  # Total amount of the sale

            total_cost = 0
            while num_tokens_to_sold > 0 and list_items_buys:
                last_buy = list_items_buys[0]  # Take the old purchase
                if last_buy.num_tokens <= num_tokens_to_sold:
                    # Calculate the cost for all tokens in this purchase
                    cost = last_buy.price_token * last_buy.num_tokens
                    total_cost += cost

                    # Subtract the sold quantity
                    num_tokens_to_sold -= last_buy.num_tokens
                    list_items_buys.pop(0)  # Remove the processed purchase
                else:
                    # Calculate the cost for only part of the purchase
                    cost = last_buy.price_token * num_tokens_to_sold
                    total_cost += cost

                    # Subtract the sold quantity from this purchase
                    last_buy.num_tokens -= num_tokens_to_sold
                    num_tokens_to_sold = 0

            # tenemos la cantidad vendida
            profit = total_sale_revenue - total_cost
            total_sold += profit

    # ademas se le suman los beneficios
    q = db.query(func.sum(models_user.UsersInvest.value).label("total_value"))
    
    q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
    q = q.filter(models_invest.Invest.category_id == category_id)
    if user_id != -1:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if invest_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    if date_end:
        q = q.filter(models_user.UsersInvest.date_created <= date_end)
    if only_invest_ids:
        only_invest_ids_list = [int(i.strip()) for i in only_invest_ids.split(',') if i.strip().isdigit()] if only_invest_ids else [-1]
        q = q.filter(models_user.UsersInvest.invest_id.in_(only_invest_ids_list))

    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_PROFITS)
    total_profit = q.first()
    total_profit_value = 0
    if total_profit and total_profit.total_value:
        total_profit_value = total_profit.total_value

    value_total = total_sold + total_profit_value

    return value_total

def _get_list_balance_invest_profits(
        *,
        db: Session,
        

        category_id: int = -1,  # para filtrar por categoría de la inversion
        user_id: int = -1,  # para filtrar por usuario
        invest_id: int = -1,  # para filtrar por inversion
        invest_child_id: int = -1, # para filtrar por inversion hijo (caso credere)
        only_invest_ids: str = None # ids, separados por comas de las inversiones que puede ver el usuario
):
    list_balance_total = []
    list_final_values_total = []
    list_profits_total = []

    # recuperamos las fechas
    list_dates = _get_dates_for_charts_and_percentage(db=db, category_id=category_id, invest_id=invest_id, user_id=user_id, num_dates=4, only_invest_ids=only_invest_ids)
    # ademas le añadimos la fecha actual
    list_dates.append(datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))

    for date_end in list_dates:
        value = _balance_value(db=db, category_id=category_id, invest_id=invest_id, user_id=user_id, date_end=date_end, only_invest_ids=only_invest_ids)
        list_balance_total.append({"date_created": date_end, "value": value})
        value = _invest_value(db=db, category_id=category_id, invest_id=invest_id, user_id=user_id, date_end=date_end, only_invest_ids=only_invest_ids)
        list_final_values_total.append({"date_created": date_end, "value": value})
        value = _profits_value(db=db, category_id=category_id, invest_id=invest_id, user_id=user_id, date_end=date_end, only_invest_ids=only_invest_ids)
        list_profits_total.append({"date_created": date_end, "value": value})
    return {
        'list_balance': list_balance_total,
        'list_final_values': list_final_values_total,
        'list_profits': list_profits_total
    }


@router.get("/data_percentage_value")
def data_percentage_value(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])),
        type_value: int = 0, # 0->balance 1->valor inversion 2->rendimientos

        category_id: int = -1,  # para filtrar por categoría de la inversion
        user_id: int = -1,  # para filtrar por usuario
        invest_id: int = -1,  # para filtrar por inversion
        invest_child_id: int = -1, # para filtrar por inversion hijo (caso credere)
):
    """
    Devuelve el dato de valor y el porcentaje de si sube o baja respecto al anterior
    """
    if current_user.role == roles.ROLE_USER:
        user_id = current_user.id

    item_prev = 0
    list_dates = _get_dates_for_charts_and_percentage(db=db,  category_id=category_id, invest_id=invest_id, user_id=user_id, num_dates=2, only_invest_ids=current_user.invest_ids)

    if len(list_dates) > 1:
        date_end = list_dates[-2]
        if type_value == 0:
            item_prev = _balance_value(db=db,  category_id=category_id, invest_id=invest_id, user_id=user_id, date_end=date_end, only_invest_ids=current_user.invest_ids)
        elif type_value == 1:
            item_prev = _invest_value(db=db,  category_id=category_id, invest_id=invest_id, user_id=user_id, date_end=date_end, invest_child_id=invest_child_id, only_invest_ids=current_user.invest_ids)
        elif type_value == 2:
            item_prev = _profits_value(db=db,  category_id=category_id, invest_id=invest_id, user_id=user_id, date_end=date_end, invest_child_id=invest_child_id, only_invest_ids=current_user.invest_ids)

    item_last = 0
    if type_value == 0:
        item_last = _balance_value(db=db,  category_id=category_id, invest_id=invest_id, user_id=user_id, only_invest_ids=current_user.invest_ids)
    elif type_value == 1:
        item_last = _invest_value(db=db,  category_id=category_id, invest_id=invest_id, user_id=user_id, invest_child_id=invest_child_id, only_invest_ids=current_user.invest_ids)
    elif type_value == 2:
        item_last = _profits_value(db=db,  category_id=category_id, invest_id=invest_id, user_id=user_id, invest_child_id=invest_child_id, only_invest_ids=current_user.invest_ids)

    if item_prev != 0:
        percentage = ((item_last - item_prev) / item_prev) * 100
        percentage = round(percentage, 2)
    else:
        percentage = 0

    return {'value': item_last, 'percentage': percentage}


@router.get("/data_value_list")
def data_value_list(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])),

        category_id: int = -1,  # para filtrar por categoría de la inversion
        user_id: int = -1,  # para filtrar por usuario
        invest_id: int = -1,  # para filtrar por inversion
        invest_child_id: int = -1 # para filtrar por inversion hijo (caso credere)
):
    """
    Devuelve el listado de balance, inversion y rendimiento para las graficas
    """
    if current_user.role == roles.ROLE_USER:
        user_id = current_user.id

    return _get_list_balance_invest_profits(db=db,  category_id=category_id, invest_id=invest_id, user_id=user_id, invest_child_id=invest_child_id, only_invest_ids=current_user.invest_ids)