from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from datetime import datetime
from starlette import status


from api.v1 import roles, const
from api.v1.base.base import _can_access_roles, Object

from api.v1.base.base_invest import _get_users_invest_buy_tokens_value, _get_users_invest_active_group
from api.v1.base.base_invest_mint_phases import _get_invest_status_calculated, _get_actual_phase_or_next
from api.v1.base.base_portfolio import _get_user_invest_all_for_activity, _get_all_portfolio_table, \
    _get_count_type_invest
from api.v1.deps import _get_db
from api.v1.base.base_login import _get_user_login, UserCurrentLogin
from api.v1.models import models_invest

router = APIRouter()


#########################################################################################################
#   FUNCIONES TIPO GET
#########################################################################################################
@router.get("/my_invest_active")
def read_list_my_invest_active(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])),

        category_id: int = -1,  # para filtrar por categoría de la inversion
        user_id: int = 0,  # para filtrar por usuario
):
    """
    se recuperan las inversiones del usuario que se compraron y no se han vendido, ya sean compras a la plataforma o al otro usuario
    se agrupan por inversion y se saca su sumatorio
    """
    if current_user.role == roles.ROLE_USER:
        user_id = current_user.id

    return _get_users_invest_active_group(db=db,  user_id=user_id, category_id=category_id, only_invest_ids=current_user.invest_ids)


@router.get("/portfolio_table")
def read_my_portfolio_table(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])),

        category_id: int = -1,  # para filtrar por categoría de la inversion
        user_id: int = 0,  # para filtrar por usuario
):
    """
    se recuperan los datos para la tabla general de portfolio
    """
    if current_user.role == roles.ROLE_USER:
        user_id = current_user.id

    return _get_all_portfolio_table(db=db,  user_id=user_id, category_id=category_id, only_invest_ids=current_user.invest_ids)


@router.get("/activity")
def read_activity_list(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])),

        page: int = Query(1, ge=1),
        per_page: int = Query(10, ge=10),
        invest_id: int = 0,  # para filtrar por proyecto
        user_id: int = 0,  # para filtrar por usuario
):
    """
    Devuelve el listado de actividad del usuario, compras, ventas, beneficios etc
    """
    skip = (page - 1) * per_page
    limit = per_page

    if invest_id != 0:
        # si hay inversion traemos solo los datos de compras y no devolvemos todos los valores, sino unos pocos
        data = _get_user_invest_all_for_activity(db=db,  invest_id=invest_id, skip=skip, limit=limit, only_invest_ids=current_user.invest_ids)
        if current_user.role == roles.ROLE_USER:
            # si es para el usuario no traemos que otros usuarios han invertido
            for item in data['list']:
                item.user_id = 0
                item.email = ''

        return data
    else:
        # traemos todos los datos
        if current_user.role == roles.ROLE_USER:
            user_id = current_user.id
        return _get_user_invest_all_for_activity(db=db,  user_id=user_id, skip=skip, limit=limit, only_invest_ids=current_user.invest_ids)


@router.get("/list_count_type_invest")
def read_list_count_type_invest(
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])),

        user_id: int = 0
):
    """
    se recupera si tuvo alguna inversión de cada categoria para mostrar los listados del portfolio
    """
    if current_user.role == roles.ROLE_USER:
        user_id = current_user.id
    return _get_count_type_invest(db=db,  user_id=user_id)


@router.get("/last_invest_collected_by_month", summary="Get last invest with chart data")
async def last_invest_collected_by_month(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        category_id: int = -1,  # para filtrar por categoría de la inversion
):
    """
    por cada inversion se recupera su grafica de invertido en el proyecto por meses
    """

    limit = 10

    q = db.query(models_invest.Invest)
    
    if category_id != -1:
        q = q.filter(models_invest.Invest.category_id == category_id)

    if current_user.invest_ids:
        only_invest_ids_list = [int(i.strip()) for i in current_user.invest_ids.split(',') if i.strip().isdigit()] if current_user.invest_ids else [-1]
        q = q.filter(models_invest.Invest.id.in_(only_invest_ids_list))

    list_invests = q.order_by(desc(models_invest.Invest.date_created)).limit(limit).all()

    today = datetime.today()
    num_month = 6
    list_out = []
    total = 0
    for invest in list_invests:
        # se recupera la fase actual de minteo de un proyecto
        data_phase = _get_actual_phase_or_next(db=db, invest_id=invest.id)
        actual_status = _get_invest_status_calculated(is_draft=invest.is_draft, is_completed=invest.is_completed, date_start_round=data_phase.date_start_round, date_end_round=data_phase.date_end_round)
        if const.INVEST_STATUS_FINANCING_PHASE == actual_status and total < limit:
            total += 1

            list_history = []
            aux = Object()
            aux.id = invest.id
            aux.slug = invest.slug
            aux.category_id = invest.category_id
            aux.name = invest.name
            aux.title = invest.title
            aux.value_round = data_phase.value_round
            aux.file = invest.file
            aux.token_abbreviation = invest.token_abbreviation
            aux.total_balance = 0

            total_balance = 0
            for i in range(num_month):
                month = today.month + i - num_month + 2
                year = today.year
                if month > 12:  # para no pasarnos del mes 12
                    month = month % 12
                    year = year + 1
                if month < 1:  # para meses anteriores a enero
                    month = 12 + month  # al ser negatimo lo resta
                    year = year - 1
                past_date = datetime(year, month, 1)  # desde este mes
                month = today.month + i - num_month + 1
                year = today.year
                if month > 12:  # para no pasarnos del mes 12
                    month = month % 12
                    year = year + 1
                if month < 1:  # para meses anteriores a enero
                    month = 12 + month  # al ser negatimo lo resta
                    year = year - 1
                past_date_back = datetime(year, month, 1)  # desde el mes anterior
                # print(f'--------------fecha entre: {past_date_back} y {past_date}')

                # se recuperan las compras que han sido a la plataforma
                total_value = _get_users_invest_buy_tokens_value(db=db, invest_id=invest.id, date_start_round=past_date_back, date_end_round=past_date)
                aux.total_balance += total_value

                list_history.append(total_value)

            aux.total_balance = total_balance
            aux.list_balance = list_history
            list_out.append(aux)

    return list_out
