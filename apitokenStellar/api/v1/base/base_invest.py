import logging
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException
from numpy.ma.core import floor
from sqlalchemy import asc, func, or_, desc
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import const
from api.v1.base.base import Object
from api.v1.base.base_invest_mint_phases import _get_actual_phase, _get_actual_phase_or_next, \
    _get_invest_status_calculated

from api.v1.models import models_invest, models_user


def _get_invest_by_id(
        db: Session,
        
        invest_id: int,
):
    q = db.query(models_invest.Invest)
    q = q.filter(models_invest.Invest.id == invest_id)
    q = q.filter(models_invest.Invest.is_draft == 0)
    
    return q.first()


def _get_invest_by_id_obligatory(
        db: Session,
        
        invest_id: int,
):
    q = db.query(models_invest.Invest)
    q = q.filter(models_invest.Invest.id == invest_id)
    q = q.filter(models_invest.Invest.is_draft == 0)
    
    item = q.first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")
    return item


def _get_invest_by_slug_obligatory(
        db: Session,
        
        slug: str,
):
    q = db.query(models_invest.Invest)
    q = q.filter(models_invest.Invest.slug == slug)
    q = q.filter(models_invest.Invest.is_draft == 0)
    
    item = q.first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")
    return item


def _get_invest(
        *,
        db: Session,
        
        invest_id: int,
        status_invest: int = -1
):
    # recupera un proyecto con su estado de minteo
    q = db.query(models_invest.Invest)
    q = q.filter(models_invest.Invest.id == invest_id)
    
    item = q.first()

    # se recupera la fase actual de minteo de un proyecto
    data_phase = _get_actual_phase_or_next(db=db, invest_id=item.id)
    item.phase = data_phase.phase
    item.date_start_round = data_phase.date_start_round
    item.date_end_round = data_phase.date_end_round
    item.price_token = data_phase.price_token
    item.num_tokens = data_phase.num_tokens
    item.num_tokens_min_to_buy = data_phase.num_tokens_min_to_buy
    item.value_round = data_phase.value_round
    item.status = _get_invest_status_calculated(is_draft=item.is_draft, is_completed=item.is_completed, date_start_round=item.date_start_round, date_end_round=item.date_end_round)

    if status_invest == const.INVEST_STATUS_FINANCING_PHASE and item.status != const.INVEST_STATUS_FINANCING_PHASE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.The project has no phase")

    if status_invest == const.INVEST_STATUS_IN_PROGRESS and item.status != const.INVEST_STATUS_IN_PROGRESS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.The project has no phase")

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")
    return item


def _get_invest_list(
        db: Session,
        
        user_id: int = -1,
        category_id: int = -1,
        status: int = -1,  # INVEST_STATUS_PENDING = 0 INVEST_STATUS_NEXT_LAUNCH = 1 INVEST_STATUS_FINANCING_PHASE = 2 INVEST_STATUS_IN_PROGRESS = 3
        is_important: bool = False,
        is_in_white_list: bool = False,
        is_in_follow: bool = False,
        page: int = 0,
        limit: int = 100,
        is_for_admin: bool = False,
        only_invest_ids: str = None,  # ids, separados por comas de las inversiones que puede ver el usuario
        search_text: str = ''
):
    if limit > 100:
        limit = 100

    q = db.query(models_invest.Invest.id)
    if not is_for_admin:
        q = q.filter(models_invest.Invest.is_draft == 0)
    

    if category_id != -1:
        q = q.filter(models_invest.Invest.category_id == category_id)

    if is_important:
        q = q.filter(models_invest.Invest.is_important == 1)

    if not is_for_admin:
        q = q.filter(models_invest.Invest.is_draft == 0)

    if is_in_white_list:
        q = q.filter(models_user.UserInvestWhiteList.user_id == user_id)
        q = q.filter(models_user.UserInvestWhiteList.invest_id == models_invest.Invest.id)

    if is_in_follow:
        q = q.filter(models_invest.InvestFollows.user_id == user_id)
        q = q.filter(models_invest.InvestFollows.invest_id == models_invest.Invest.id)

    if only_invest_ids:
        only_invest_ids_list = [int(i.strip()) for i in only_invest_ids.split(',') if i.strip().isdigit()] if only_invest_ids else [-1]

        q = q.filter(models_invest.Invest.id.in_(only_invest_ids_list))

    if search_text != '':
        q = q.filter(or_(models_invest.Invest.title.ilike(f"%{search_text}%"), models_invest.Invest.title_EN.ilike(f"%{search_text}%"),
                         models_invest.Invest.name.ilike(f"%{search_text}%"), models_invest.Invest.name_EN.ilike(f"%{search_text}%")))

    q = q.order_by(desc(models_invest.Invest.date_created))
    list_items_ids = q.all()

    # se recuperan mas datos
    list_items = []
    total = 0
    for item in list_items_ids:
        if is_for_admin:
            list_items.append(_get_invest_data(db=db, invest_id=item.id))
        else:
            if user_id != -1:
                if status != -1:  # si existe estatus, solo traemos los proyectos con ese estatus
                    q = db.query(models_invest.Invest)
                    q = q.filter(models_invest.Invest.id == item.id)
                    
                    q = q.filter(models_invest.Invest.is_draft == 0)
                    item_invest = q.first()
                    # se recupera la fase actual de minteo de un proyecto
                    data_phase = _get_actual_phase_or_next(db=db, invest_id=item_invest.id)
                    actual_status = _get_invest_status_calculated(is_draft=item_invest.is_draft, is_completed=item_invest.is_completed, date_start_round=data_phase.date_start_round, date_end_round=data_phase.date_end_round)
                    if status == actual_status and total < limit:
                        total += 1
                        list_items.append(_get_invest_data(db=db, invest_id=item.id, get_is_follow=True, user_id=user_id, for_users=True))
                else:
                    list_items.append(_get_invest_data(db=db, invest_id=item.id, get_is_follow=True, user_id=user_id, for_users=True))
            else:
                list_items.append(_get_invest_data(db=db, invest_id=item.id, for_users=True))

    # los estados de los proyectos son calculados por eso se recogen todos y luego se ponen solo los del estado seleccionado
    if is_for_admin:
        # esta parte es para el usuario ADMIN, me traigo todos los proyectos y totales

        num_projects_draft = 0
        num_projects_next_launch = 0
        num_projects_financial_phase = 0
        num_projects_in_course = 0
        num_projects_finished = 0

        for item in list_items:
            if item.status == const.INVEST_STATUS_PENDING:
                num_projects_draft += 1
            elif item.status == const.INVEST_STATUS_NEXT_LAUNCH:
                num_projects_next_launch += 1
            elif item.status == const.INVEST_STATUS_FINANCING_PHASE:
                num_projects_financial_phase += 1
            elif item.status == const.INVEST_STATUS_IN_PROGRESS:
                num_projects_in_course += 1
            elif item.status == const.INVEST_STATUS_FINISHED:
                num_projects_finished += 1

        num_projects_all = num_projects_draft + num_projects_next_launch + num_projects_financial_phase + num_projects_in_course + num_projects_finished

        return {
            'list_projects': list_items,
            'num_projects_all': num_projects_all,
            'num_projects_draft': num_projects_draft,
            'num_projects_next_launch': num_projects_next_launch,
            'num_projects_financial_phase': num_projects_financial_phase,
            'num_projects_in_course': num_projects_in_course,
            'num_projects_finished': num_projects_finished
        }
    else:
        return list_items


def _get_invest_totals_status(
        db: Session,
        
        category_id: int = -1,
        only_invest_ids: str = None  # ids, separados por comas de las inversiones que puede ver el usuario
):
    # se recuperan los totales segun estado del proyecto
    q = db.query(models_invest.Invest.id, models_invest.Invest.is_draft, models_invest.Invest.is_completed)
    

    if category_id != -1:
        q = q.filter(models_invest.Invest.category_id == category_id)

    if only_invest_ids:
        only_invest_ids_list = [int(i.strip()) for i in only_invest_ids.split(',') if i.strip().isdigit()] if only_invest_ids else [-1]
        q = q.filter(models_invest.Invest.id.in_(only_invest_ids_list))

    q = q.order_by(desc(models_invest.Invest.date_created))
    list_items = q.all()

    num_projects_draft = 0
    num_projects_next_launch = 0
    num_projects_financial_phase = 0
    num_projects_in_course = 0
    num_projects_finished = 0

    for item in list_items:
        # se recupear la fase
        data_phase = _get_actual_phase_or_next(db=db, invest_id=item.id)

        # recalculamos el estado del proyecto
        status = _get_invest_status_calculated(is_draft=item.is_draft, is_completed=item.is_completed, date_start_round=data_phase.date_start_round, date_end_round=data_phase.date_end_round)
        if status == const.INVEST_STATUS_PENDING:
            num_projects_draft += 1
        elif status == const.INVEST_STATUS_NEXT_LAUNCH:
            num_projects_next_launch += 1
        elif status == const.INVEST_STATUS_FINANCING_PHASE:
            num_projects_financial_phase += 1
        elif status == const.INVEST_STATUS_IN_PROGRESS:
            num_projects_in_course += 1
        elif status == const.INVEST_STATUS_FINISHED:
            num_projects_finished += 1

    num_projects_all = num_projects_draft + num_projects_next_launch + num_projects_financial_phase + num_projects_in_course + num_projects_finished

    return {
        'num_projects_all': num_projects_all,
        'num_projects_draft': num_projects_draft,
        'num_projects_next_launch': num_projects_next_launch,
        'num_projects_financial_phase': num_projects_financial_phase,
        'num_projects_in_course': num_projects_in_course,
        'num_projects_finished': num_projects_finished
    }



def _get_users_invest_buy_waiting_transfer_total_num(
        db: Session,
        invest_id: int,
        phase: str
):
    # devuelve el total de tokens reservados para hacer la transferencia
    # se excluyen los que luego ya han sido validados o los que se han rechazado

    # se recuperan los tokens comprados por los usuarios a la plataforma
    q = db.query(models_user.UsersInvest)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(models_user.UsersInvest.phase == phase)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
    # solo las compras a la plataforma
    q = q.filter(models_user.UsersInvest.other_user_id == None)
    sold_tokens = q.all()

    # se recuperan los tokens comprados pero sin pagar, estan a la espera de transferencia
    q = db.query(models_user.UsersInvest)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(models_user.UsersInvest.phase == phase)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_WITHOUT_VERIFIED,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_CARD_WITHOUT_VERIFIED))

    waiting_tokens = q.all()

    # se recuperan los tokens que han sido rechazados porque no se ha llegado a hacer la transferencia
    q = db.query(models_user.UsersInvest)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(models_user.UsersInvest.phase == phase)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_REJECTED)
    reject_tokens = q.all()

    total = 0
    for waiting_t in waiting_tokens:
        for sold_t in sold_tokens:
            if sold_t.parent_id == waiting_t.id:
                waiting_t.num_tokens = 0
        for reject_t in reject_tokens:
            if reject_t.parent_id == waiting_t.id:
                waiting_t.num_tokens = 0
        total += waiting_t.num_tokens

    return total


def _get_num_investors(
        db: Session,
        invest_id: int,
        date_start_round: datetime = None,
        date_end_round: datetime = None,
):
    # se recupera el número de inversores en las fechas dadas
    q = db.query(models_user.UsersInvest.user_id)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_WITHOUT_VERIFIED,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_CARD_WITHOUT_VERIFIED))

    if date_start_round and date_end_round:
        q = q.filter(date_start_round <= models_user.UsersInvest.date_created)
        q = q.filter(models_user.UsersInvest.date_created <= date_end_round)

    return q.distinct().count()


def _get_users_invest_buy_tokens_value(
        db: Session,
        invest_id: int,
        date_start_round: datetime = None,
        date_end_round: datetime = None,
        user_id: int = None,
):
    # el valor de venta total de todos los tokens comprados a la plataforma
    q = db.query(func.sum(models_user.UsersInvest.value).label("total_value"))
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
    q = q.filter(models_user.UsersInvest.other_user_id == None)
    if user_id:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if date_start_round and date_end_round:
        q = q.filter(date_start_round <= models_user.UsersInvest.date_created)
        q = q.filter(models_user.UsersInvest.date_created <= date_end_round)
    buys = q.first()
    if not buys or not buys.total_value:
        total_value = 0
    else:
        total_value = buys.total_value

    return total_value


def _get_user_invest_buy_waiting_transfer_total_num(
        db: Session,
        invest_id: int,
        date_start_round: datetime = None,
        date_end_round: datetime = None,
        user_id: int = None,
):
    # el valor de venta total de todos los tokens comprados a la plataforma
    q = db.query(func.sum(models_user.UsersInvest.value).label("total_value"))
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_WITHOUT_VERIFIED,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_CARD_WITHOUT_VERIFIED))
    q = q.filter(models_user.UsersInvest.other_user_id == None)
    if user_id:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if date_start_round and date_end_round:
        q = q.filter(date_start_round <= models_user.UsersInvest.date_created)
        q = q.filter(models_user.UsersInvest.date_created <= date_end_round)
    buys = q.first()
    if not buys or not buys.total_value:
        total_value = 0
    else:
        total_value = buys.total_value

    return total_value


def _get_buys_without_document_transfer_for_user(invest_id: int, user_id: int, db: Session):
    # se recuperan las compras del usuario que no se han verificado
    q = db.query(models_user.UsersInvest)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(models_user.UsersInvest.user_id == user_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_WITHOUT_VERIFIED,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_CARD_WITHOUT_VERIFIED
                     # models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY
                     ))

    buys = q.all()
    for buy in buys:
        q = db.query(models_user.UsersInvestDocumentsTransfer)
        q = q.filter(models_user.UsersInvestDocumentsTransfer.user_invest_id == buy.id)
        q = q.filter(models_user.UsersInvestDocumentsTransfer.user_id == user_id)
        if not q.first():
            return True

    return False


def _get_invest_data(
        db: Session,
        
        invest_id: int,
        user_id: int = 0,
        slug: str = '',
        for_users: bool = False,
        get_status_description: bool = False,
        get_data_media_doc: bool = False,
        get_preference_to_by: bool = False,
        get_is_follow: bool = False,
        get_value_to_invest: bool = False,
        get_all_info: bool = False,
        only_invest_ids: str = None  # ids, separados por comas de las inversiones que puede ver el usuario
):
    # recupera un proyecto con muchos datos sobre el proyecto
    q = db.query(models_invest.Invest)
    if invest_id != 0:
        q = q.filter(models_invest.Invest.id == invest_id)
    else:
        q = q.filter(models_invest.Invest.slug == slug)

    if only_invest_ids:
        only_invest_ids_list = [int(i.strip()) for i in only_invest_ids.split(',') if i.strip().isdigit()] if only_invest_ids else [-1]
        q = q.filter(models_invest.Invest.id.in_(only_invest_ids_list))

    

    # si es solo para los usuarios no se recogen los pendientes
    if for_users:
        q = q.filter(models_invest.Invest.is_draft == 0)

    data_invest = q.first()
    if not data_invest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # se ponen los datos necesarios
    item = Object()
    item.id = data_invest.id
    item.slug = data_invest.slug
    item.name = data_invest.name
    item.name_EN = data_invest.name_EN
    item.title = data_invest.title
    item.title_EN = data_invest.title_EN
    item.summary = data_invest.summary
    item.summary_EN = data_invest.summary_EN
    item.description = data_invest.description
    item.description_EN = data_invest.description_EN
    item.file = data_invest.file
    item.file_top = data_invest.file_top
    item.category_id = data_invest.category_id
    item.web = data_invest.web
    item.location = data_invest.location
    item.location_gps_lat = data_invest.location_gps_lat
    item.location_gps_lon = data_invest.location_gps_lon
    item.time_limit = data_invest.time_limit
    item.time_limit_EN = data_invest.time_limit_EN
    item.token_abbreviation = data_invest.token_abbreviation
    item.profit_estimated = data_invest.profit_estimated
    item.profit_estimated_description = data_invest.profit_estimated_description
    item.hide_profit_estimated = data_invest.hide_profit_estimated
    item.hide_value_round = data_invest.hide_value_round
    item.hide_date_start_round = data_invest.hide_date_start_round
    item.hide_date_end_round = data_invest.hide_date_end_round
    item.date_end = None
    item.proposal_to_investors = data_invest.proposal_to_investors
    item.proposal_to_investors_EN = data_invest.proposal_to_investors_EN
    item.deploy_state = data_invest.deploy_state
    item.total_amount_invested_completed = data_invest.total_amount_invested_completed
    item.num_tokens_completed = data_invest.num_tokens_completed
    item.hide_num_tokens = data_invest.hide_num_tokens
    item.hide_time_data = data_invest.hide_time_data
    item.num_investors_completed = data_invest.num_investors_completed
    item.success_fee = data_invest.success_fee
    item.management_fee = data_invest.management_fee
    item.opening_commission = data_invest.opening_commission
    item.closing_commission = data_invest.closing_commission
    item.spread = data_invest.spread
    item.entry_fee = data_invest.entry_fee
    item.annual_fee = data_invest.annual_fee
    item.investors = 0
    item.days = None
    item.is_follow = False
    item.sold_tokens_phase = 0
    item.remaining_tokens = 0
    item.waiting_tokens = 0
    item.preference_to_buy = None
    item.date_to_invest = False
    item.list_mint_phases = None
    item.num_tokens_max_to_buy = None
    item.value_to_invest = None
    item.is_draft = data_invest.is_draft
    item.is_paused = data_invest.is_paused

    # se recupera la fase actual o siguiente de minteo de un proyecto
    data_phase = _get_actual_phase_or_next(db=db, invest_id=data_invest.id)
    item.phase = data_phase.phase
    item.date_start_round = data_phase.date_start_round
    item.date_end_round = data_phase.date_end_round
    item.price_token = data_phase.price_token
    item.num_tokens = data_phase.num_tokens
    item.num_tokens_min_to_buy = data_phase.num_tokens_min_to_buy
    item.value_round = data_phase.value_round
    item.has_white_list = data_phase.is_private

    # recalculamos el estado del proyecto
    item.status = _get_invest_status_calculated(is_draft=data_invest.is_draft, is_completed=data_invest.is_completed, date_start_round=item.date_start_round, date_end_round=item.date_end_round)

    # se recuperan los estados del proyecto
    if get_status_description:
        item.list_status_description = db.query(models_invest.InvestStatusDescription).filter(models_invest.InvestStatusDescription.invest_id == item.id).all()

    actual_date = datetime.now()

    # se recuperan datos de la fase actual
    if item.phase:
        item.days = (item.date_end_round - actual_date).days
        if item.days < 0:
            item.days = 0
        if item.date_start_round.strftime(' %Y-%m-%d %H:%M') <= actual_date.strftime(' %Y-%m-%d %H:%M') <= item.date_end_round.strftime(' %Y-%m-%d %H:%M'):
            item.date_to_invest = True

        # se recuperan los tokens vendidos
        # sold_tokens_phase = _get_users_invest_buy_tokens_num(db=db, invest_id=item.id, buy_type=1, phase=item.phase)
        # sold_tokens_phase = _get_num_tokens_in_date(db=db, phase=item.phase, invest_id=item.id, user_id=user_id)
        sold_tokens_phase = _get_num_tokens_in_date(db=db, phase=item.phase, invest_id=item.id)
        item.sold_tokens_phase = sold_tokens_phase['num_tokens']
        item.sold_tokens_value = sold_tokens_phase['value_tokens']
        item.remaining_tokens = item.num_tokens - item.sold_tokens_phase

        # se recuperan los tokens que estan esperando la transferencia
        item.waiting_tokens = _get_users_invest_buy_waiting_transfer_total_num(db=db, invest_id=item.id, phase=item.phase)

        # se recupera el numero de inversores que alguna vez han comprado
        item.investors = _get_num_investors(db=db, invest_id=item.id, date_start_round=item.date_start_round, date_end_round=item.date_end_round)

        # se recuperan las fases del minteo para sacarlo en la info si no esta puesto como oculto
        item.list_mint_phases = []
        if not data_invest.hide_date_start_round and not data_invest.hide_date_end_round and not data_invest.hide_num_tokens and not data_invest.hide_value_round:
            item.list_mint_phases = db.query(models_invest.InvestMintPhases).filter(models_invest.InvestMintPhases.invest_id == item.id).all()
            # se recorren las fases y las inversiones para ver cuantos tokens por fase se han vendido mios
            for mint_phase in item.list_mint_phases:
                q = db.query(func.sum(models_user.UsersInvest.num_tokens).label("num_tokens"), func.sum(models_user.UsersInvest.value).label("value"))
                q = q.filter(models_user.UsersInvest.invest_id == mint_phase.invest_id)
                q = q.filter(models_user.UsersInvest.phase == mint_phase.phase)
                q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
                q = q.filter(models_user.UsersInvest.other_user_id == None)
                q = q.filter(models_user.UsersInvest.user_id == user_id)
                q = q.first()
                mint_phase.num_tokens_mine = q.num_tokens
                mint_phase.value_tokens_mine = q.value

                # se pone la fecha final del proyecto con la ultima ronda
                item.date_end = mint_phase.date_end

                # mint_phase.sold_tokens_phase = _get_users_invest_buy_tokens_num(db=db, invest_id=item.id, buy_type=1, phase=mint_phase.phase)
                # mint_phase.sold_tokens_value = _get_users_invest_buy_tokens_value(db=db, invest_id=item.id, date_start_round=mint_phase.date_start, date_end_round=mint_phase.date_end)
                mint_phase.sold_tokens_phase = _get_num_tokens_in_date(db=db, phase=mint_phase.phase, invest_id=item.id, user_id=user_id)['num_tokens']

            # se recupera el numero de inversores que alguna vez han comprado en el proyecto
            item.investors_first_to_last = _get_num_investors(db=db, invest_id=item.id)


    if get_data_media_doc:
        item.documents = db.query(models_invest.InvestDocuments).filter(models_invest.InvestDocuments.invest_id == item.id).all()
        item.media = db.query(models_invest.InvestMedia).filter(models_invest.InvestMedia.invest_id == item.id).all()
        item.news = db.query(models_invest.InvestNews).filter(models_invest.InvestNews.invest_id == item.id).all()
        item.questions = db.query(models_invest.InvestQuestions).filter(models_invest.InvestQuestions.invest_id == item.id).all()
        item.team = db.query(models_invest.InvestTeam).filter(models_invest.InvestTeam.invest_id == item.id).all()

    if get_preference_to_by:
        # cogemos si estamos en venta publica, privada etc
        q = db.query(models_user.UserInvestWhiteList.preference_to_buy)
        q = q.filter(models_user.UserInvestWhiteList.invest_id == item.id)
        q = q.filter(models_user.UserInvestWhiteList.user_id == user_id)
        user_white_list = q.first()
        if user_white_list:
            if user_white_list.preference_to_buy:
                item.preference_to_buy = user_white_list.preference_to_buy
            else:
                item.preference_to_buy = 0

    if get_is_follow and user_id != 0:
        # se mira si seguimos el proyecto
        q = db.query(models_invest.InvestFollows.invest_id)
        q = q.filter(models_invest.InvestFollows.user_id == user_id)
        q = q.filter(models_invest.InvestFollows.invest_id == item.id)
        follow = q.first()
        if follow:
            item.is_follow = True

    if (get_preference_to_by or get_value_to_invest) and user_id != 0:
        # se mira si estamos en whitelist que valor hemos puesto para invertir
        q = db.query(models_user.UserInvestWhiteList.value_to_invest)
        q = q.filter(models_user.UserInvestWhiteList.user_id == user_id)
        q = q.filter(models_user.UserInvestWhiteList.invest_id == item.id)
        # q = q.filter(models_user.UserInvestWhiteList.preference_to_buy == item.phase)
        value_to_invest = q.first()
        if value_to_invest:
            item.value_to_invest = value_to_invest.value_to_invest

    item.has_buys_without_document_transfer = _get_buys_without_document_transfer_for_user(invest_id=item.id, user_id=user_id, db=db)

    if not get_all_info:
        # si no se necesita esta informacion no se devuelve
        item.description = None
        item.description_EN = None
        item.proposal_to_investors = None
        item.proposal_to_investors_EN = None
        item.summary = None
        item.summary_EN = None
        item.file_top = None
        item.location = None
        # item.time_limit = None
        item.success_fee = None
        item.management_fee = None
        item.opening_commission = None
        item.closing_commission = None
        item.spread = None
        item.entry_fee = None
        item.annual_fee = None
    return item


def _get_num_tokens_in_date(
        *,
        db: Session,
        
        invest_id,
        phase: str = None,
        date_start: datetime = None,
        date_end: datetime = None,
        user_id: int = 0,
        category_id: int = -1,  # para filtrar por categoría de la inversion
        with_refund: bool = True,
):
    # se recupera el numero de tokens que teniamos en esa fecha
    q = db.query(models_user.UsersInvest.num_tokens, models_user.UsersInvest.type, models_user.UsersInvest.price_token)
    
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    if user_id != 0:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    # las que han sido pagadas y vendidas y reembolsadas
    if with_refund:
        q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY,
                         models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD,
                         models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND
                         # models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND_PARTIAL,
                         # models_user.UsersInvest.type == const.USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND
                         ))
    else:
        # las que han sido pagadas y vendidas
        q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY,
                         models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD))

    if phase:
        q = q.filter(models_user.UsersInvest.phase == phase)

    if date_start:
        q = q.filter(models_user.UsersInvest.date_created >= date_start)

    if date_end:
        q = q.filter(models_user.UsersInvest.date_created <= date_end)

    if category_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
        q = q.filter(models_invest.Invest.category_id == category_id)

    list_items = q.order_by(asc(models_user.UsersInvest.date_created), asc(models_user.UsersInvest.id)).all()

    list_items_buys = []  # Lista para almacenar compras
    total_value = 0  # Valor total de las compras restantes
    total_num_tokens = 0  # numero de tokens de las compras restantes

    # Procesamos cada transacción para quitar a las compras las ventas en orden ascendente
    for item in list_items:
        if item.type == const.USERS_INVEST_TYPE_BUY:
            # Añadimos cada compra a la lista de compras
            aux = Object()
            aux.num_tokens = item.num_tokens
            aux.price_token = item.price_token
            list_items_buys.append(aux)
        elif item.type == const.USERS_INVEST_TYPE_SOLD:
            # Procesamos la venta, restando las cantidades de las compras en orden
            num_tokens_to_sold = item.num_tokens
            while num_tokens_to_sold > 0 and list_items_buys:
                last_buy = list_items_buys[0]  # Tomamos la compra mas antigua
                if last_buy.num_tokens <= num_tokens_to_sold:
                    # Restamos lo que queda de la compra más antigua
                    num_tokens_to_sold -= last_buy.num_tokens
                    list_items_buys.pop(0)
                else:
                    # Solo restamos parte de la compra más reciente
                    last_buy.num_tokens -= num_tokens_to_sold
                    num_tokens_to_sold = 0

    # Calculamos el valor de las compras restantes
    for buy in list_items_buys:
        total_value += buy.num_tokens * buy.price_token
        total_num_tokens += buy.num_tokens

    # le quitamos las devoluciones y sumamos el resto de amortizacion y cierre de proyecto
    for item in list_items:
        if item.type == const.USERS_INVEST_TYPE_REFUND:
            total_num_tokens -= item.num_tokens
            total_value -= item.num_tokens * item.price_token

    return {'num_tokens': total_num_tokens, 'value_tokens': total_value}


def _get_total_num_tokens_sold_this_round(
        db: Session,
        invest_id: int,
        phase: str
):
    # para un proyecto, se devuelve el total de tokens vendidos en una fase
    q = db.query(models_user.UsersInvest.id, models_user.UsersInvest.num_tokens)
    q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
    q = q.filter(models_invest.InvestMintPhases.phase == phase)
    q = q.filter(models_invest.InvestMintPhases.invest_id == models_user.UsersInvest.invest_id)
    q = q.filter(models_invest.InvestMintPhases.phase == models_user.UsersInvest.phase)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
    buy_tokens = q.all()

    # se recuperan los tokens devueltos para restarlos
    q = db.query(models_user.UsersInvest.num_tokens, models_user.UsersInvest.parent_id)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND)
    refund_tokens = q.all()

    total_refund = 0
    # si coincide que la devolucion es de esta fase
    for item_buy in buy_tokens:
        for item_refund in refund_tokens:
            if item_buy.id == item_refund.parent_id:
                total_refund += item_refund.num_tokens

    total_num_token = 0
    for item_buy in buy_tokens:
        total_num_token += item_buy.num_tokens

    return total_num_token - total_refund


def _get_users_invest_list_to_close_project(
        db: Session,
        
        invest_id: int = 0,
):
    # se recuperan todos los usuarios que han invertido en el proyecto y tienen sus tokens activos sin vender
    q = db.query(models_user.UsersInvest.user_id)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
    list_users = q.distinct().all()
    list_invest_out = []
    for user in list_users:
        # se recuperan mas datos
        q = db.query(models_user.User, models_user.UserBankAccount, models_user.UserDataPhysicalPerson)
        q = q.filter(user.user_id == models_user.User.id)
        q = q.outerjoin(models_user.UserDataPhysicalPerson, models_user.User.id == models_user.UserDataPhysicalPerson.user_id)
        q = q.outerjoin(models_user.UserBankAccount, models_user.User.id == models_user.UserBankAccount.user_id)
        data_user = q.distinct().first()

        invest = _get_users_invest_active_group(db=db, user_id=user.user_id, invest_id=invest_id, with_refund=True)
        if len(invest) == 1:
            aux = Object()
            aux.user_id = user.user_id
            aux.email = data_user.User.email
            if data_user.UserDataPhysicalPerson:
                aux.name = data_user.UserDataPhysicalPerson.name
                aux.surname = data_user.UserDataPhysicalPerson.surname
            else:
                aux.name = ""
                aux.surname = ""
            if data_user.UserBankAccount:
                aux.bic = data_user.UserBankAccount.bic
                aux.iban = data_user.UserBankAccount.iban
            else:
                aux.bic = ""
                aux.iban = ""
            aux.language = data_user.User.language
            aux.num_tokens = invest[0].num_tokens
            # aux.price_token = invest[0].price_token
            aux.value = invest[0].value
            list_invest_out.append(aux)

    return list_invest_out


def _get_users_invest_active_group(
        db: Session,
        
        user_id: int = 0,
        invest_id: int = 0,
        category_id: int = -1,  # para filtrar por categoría de la inversion
        with_refund: bool = True,
        only_invest_ids: str = None  # ids, separados por comas de las inversiones que puede ver el usuario
):
    # se recuperan las inversiones del usuario que se compraron y no se han vendido, ya sean compras a la plataforma o al otro usuario
    # se agrupan por inversion y se saca su sumatorio de numero de tokens
    q = db.query(models_user.UsersInvest.invest_id, models_user.UsersInvest.phase, func.sum(models_user.UsersInvest.num_tokens).label("num_tokens"),
                 func.sum(models_user.UsersInvest.value).label("value"))
    
    if user_id != 0:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if invest_id != 0:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    if category_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
        q = q.filter(models_invest.Invest.category_id == category_id)
    # las que han sido pagadas y validadas
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
    if only_invest_ids:
        only_invest_ids_list = [int(i.strip()) for i in only_invest_ids.split(',') if i.strip().isdigit()] if only_invest_ids else [-1]
        q = q.filter(models_user.UsersInvest.invest_id.in_(only_invest_ids_list))
    list_invest_buy = q.group_by(models_user.UsersInvest.invest_id).all()

    # lista de inversiones vendidas o devueltas
    q = db.query(models_user.UsersInvest.invest_id, func.sum(models_user.UsersInvest.num_tokens).label("num_tokens"), func.sum(models_user.UsersInvest.value).label("value"))
    
    if user_id != 0:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if invest_id != 0:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    if category_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
        q = q.filter(models_invest.Invest.category_id == category_id)

    if with_refund:
        q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD,
                         models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND,
                         models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND_PARTIAL,
                         models_user.UsersInvest.type == const.USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND))
    else:
        q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD)

    if only_invest_ids:
        only_invest_ids_list = [int(i.strip()) for i in only_invest_ids.split(',') if i.strip().isdigit()] if only_invest_ids else [-1]
        q = q.filter(models_user.UsersInvest.invest_id.in_(only_invest_ids_list))
    list_invest_refund_sold = q.group_by(models_user.UsersInvest.invest_id).all()

    list_invest_out = []
    for item_buy in list_invest_buy:
        num_tokens = item_buy.num_tokens
        value_tokens = item_buy.value
        for item_sold in list_invest_refund_sold:
            if item_buy.invest_id == item_sold.invest_id:
                num_tokens -= item_sold.num_tokens
                value_tokens -= item_sold.value

        # se recuperan mas datos de la inversion
        q = db.query(models_invest.Invest)
        q = q.filter(models_invest.Invest.id == item_buy.invest_id)
        invest = q.first()
        if num_tokens > 0:
            aux = Object()
            aux.id = invest.id
            aux.slug = invest.slug
            aux.name = invest.name
            aux.category_id = invest.category_id
            aux.num_tokens = num_tokens
            # aux.price_token = item_buy.price_token
            # aux.value = item_buy.price_token * int(num_tokens)
            aux.value = value_tokens

            # se recalcula el estado
            data_phase = _get_actual_phase_or_next(db=db, invest_id=invest_id)
            # if data_phase.phase:
            aux.status = _get_invest_status_calculated(is_draft=invest.is_draft, is_completed=invest.is_completed, date_start_round=data_phase.date_start_round,
                                                       date_end_round=data_phase.date_end_round)

            list_invest_out.append(aux)

    return list_invest_out

