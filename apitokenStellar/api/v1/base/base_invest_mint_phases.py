from datetime import datetime

from fastapi import HTTPException, Depends
from sqlalchemy import asc, literal_column, desc
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import const
from api.v1.base.base import Object
from api.v1.deps import _get_db
from api.v1.models import models_invest


def _get_actual_phase(
        *,
        db: Session = Depends(_get_db),
        invest_id: int
):
    # se recupera la fase actual de minteo de un proyecto
    # si no existen fases se devuelven los datos con None
    q = db.query(models_invest.InvestMintPhases.phase, models_invest.InvestMintPhases.date_end, models_invest.InvestMintPhases.date_start,
                 models_invest.InvestMintPhases.price_fiat, models_invest.InvestMintPhases.max_tokens,
                 models_invest.InvestMintPhases.num_tokens_min_to_buy, models_invest.InvestMintPhases.pay_with_eth,
                 models_invest.InvestMintPhases.price_eth_wey, models_invest.InvestMintPhases.is_private,
                 (models_invest.InvestMintPhases.price_fiat * models_invest.InvestMintPhases.max_tokens).label("value_round"))
    q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
    q = q.filter(models_invest.InvestMintPhases.date_start <= datetime.today().strftime('%Y-%m-%d %H:%M'))
    q = q.filter(models_invest.InvestMintPhases.date_end >= datetime.today().strftime('%Y-%m-%d %H:%M'))
    phase = q.first()
    aux = Object()
    if phase:
        aux.phase = phase.phase
        aux.date_start_round = phase.date_start
        aux.date_end_round = phase.date_end
        aux.price_token = phase.price_fiat
        aux.pay_with_eth = phase.pay_with_eth
        aux.price_eth_wey = phase.price_eth_wey
        aux.num_tokens = phase.max_tokens
        aux.num_tokens_min_to_buy = int(phase.num_tokens_min_to_buy)
        aux.value_round = phase.value_round  # phase.max_tokens * decimal.Decimal(phase.price_fiat)
        aux.is_private = phase.is_private
    else:
        aux.phase = None
        aux.date_start_round = None
        aux.date_end_round = None
        aux.price_token = 0
        aux.num_tokens = 0
        aux.num_tokens_min_to_buy = 0
        aux.value_round = 0
        aux.pay_with_eth = None
        aux.price_eth_wey = None
        aux.is_private = 0

    return aux


def _get_actual_phase_or_next(
        *,
        db: Session = Depends(_get_db),
        invest_id: int,
        is_obligatory: bool = False
):
    # se recupera la fase actual de minteo de un proyecto
    # si no existe fase actual se busca la siguiente fase
    # esto ya no: si no existe fase a futuro cogemos la fase anterior ya terminada
    # si no existen fases se devuelven los datos con None
    q = db.query(models_invest.InvestMintPhases.phase, models_invest.InvestMintPhases.date_end, models_invest.InvestMintPhases.date_start,
                 models_invest.InvestMintPhases.price_fiat, models_invest.InvestMintPhases.max_tokens,
                 models_invest.InvestMintPhases.num_tokens_min_to_buy, models_invest.InvestMintPhases.pay_with_eth,
                 models_invest.InvestMintPhases.price_eth_wey, models_invest.InvestMintPhases.is_private,
                 models_invest.InvestMintPhases.symbol_fiat, models_invest.InvestMintPhases.mint_pk, models_invest.InvestMintPhases.fee_percent,
                 (models_invest.InvestMintPhases.price_fiat * models_invest.InvestMintPhases.max_tokens).label("value_round"))
    q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
    q = q.filter(models_invest.InvestMintPhases.date_start <= datetime.today().strftime('%Y-%m-%d %H:%M'))
    q = q.filter(models_invest.InvestMintPhases.date_end >= datetime.today().strftime('%Y-%m-%d %H:%M'))
    phase = q.first()
    put_data = False
    if phase:
        put_data = True
    else:
        # si no existe fase se busca la siguiente fase
        q = db.query(models_invest.InvestMintPhases.phase, models_invest.InvestMintPhases.date_end, models_invest.InvestMintPhases.date_start,
                     models_invest.InvestMintPhases.price_fiat, models_invest.InvestMintPhases.max_tokens, literal_column("'0'").label('num_tokens_min_to_buy'),
                     (models_invest.InvestMintPhases.price_fiat * models_invest.InvestMintPhases.max_tokens).label("value_round"),
                     models_invest.InvestMintPhases.symbol_fiat,models_invest.InvestMintPhases.mint_pk, models_invest.InvestMintPhases.fee_percent,
                     models_invest.InvestMintPhases.price_eth_wey, models_invest.InvestMintPhases.pay_with_eth, models_invest.InvestMintPhases.is_private)
        q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
        q = q.filter(models_invest.InvestMintPhases.date_start > datetime.today().strftime(' %Y-%m-%d %H:%M'))
        phase = q.first()
        if phase:
            put_data = True
        else:
            # si no existe fase a futuro y el proyecto está finalizado cogemos las fechas de inicio de la primera fase y fin de la ultima
            """
            q = db.query(literal_column("'all'").label('phase'), func.min(models_invest.InvestMintPhases.date_start).label('date_start'),
                         func.max(models_invest.InvestMintPhases.date_end).label('date_end'),
                         func.sum(models_invest.InvestMintPhases.price_fiat * models_invest.InvestMintPhases.max_tokens).label("value_round"),
                         func.sum(models_invest.InvestMintPhases.max_tokens).label("max_tokens"), models_invest.InvestMintPhases.price_eth_wey, models_invest.InvestMintPhases.pay_with_eth,
                         literal_column("'0'").label('price_fiat'), literal_column("'0'").label('num_tokens_min_to_buy'), models_invest.InvestMintPhases.is_private)
            q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
            phase = q.first()
            if phase.max_tokens:  # si hay tokens
                put_data = True
            """
            # cogemos la fase anterior ya terminada
            q = db.query(models_invest.InvestMintPhases.phase)
            q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
            last_phase = q.order_by(desc(models_invest.InvestMintPhases.date_end)).first()
            if last_phase:
                q = db.query(models_invest.InvestMintPhases.phase, models_invest.InvestMintPhases.date_end, models_invest.InvestMintPhases.date_start,
                             models_invest.InvestMintPhases.price_fiat, models_invest.InvestMintPhases.max_tokens,
                             models_invest.InvestMintPhases.num_tokens_min_to_buy, models_invest.InvestMintPhases.pay_with_eth,
                             models_invest.InvestMintPhases.price_eth_wey, models_invest.InvestMintPhases.is_private,
                             models_invest.InvestMintPhases.symbol_fiat,models_invest.InvestMintPhases.mint_pk, models_invest.InvestMintPhases.fee_percent,
                             (models_invest.InvestMintPhases.price_fiat * models_invest.InvestMintPhases.max_tokens).label("value_round"))
                q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
                q = q.filter(models_invest.InvestMintPhases.phase == last_phase.phase)
                phase = q.first()
                if phase.max_tokens:  # si hay tokens
                    put_data = True

    aux = Object()
    if put_data:
        aux.phase = phase.phase
        aux.date_start_round = phase.date_start
        aux.date_end_round = phase.date_end
        aux.price_token = phase.price_fiat
        aux.pay_with_eth = phase.pay_with_eth
        aux.price_eth_wey = phase.price_eth_wey
        aux.num_tokens = phase.max_tokens
        aux.num_tokens_min_to_buy = int(phase.num_tokens_min_to_buy)
        aux.value_round = phase.value_round  # phase.max_tokens * decimal.Decimal(phase.price_fiat)
        aux.is_private = phase.is_private
        aux.symbol_fiat = phase.symbol_fiat
        aux.price_fiat = phase.price_fiat
        aux.mint_pk = phase.mint_pk
        aux.fee_percent = phase.fee_percent
    else:
        aux.phase = None
        aux.date_start_round = None
        aux.date_end_round = None
        aux.price_token = 0
        aux.num_tokens = 0
        aux.num_tokens_min_to_buy = 0
        aux.value_round = 0
        aux.pay_with_eth = None
        aux.price_eth_wey = None
        aux.is_private = 0
        aux.symbol_fiat = None
        aux.price_fiat = 0
        aux.mint_pk = None
        aux.fee_percent = 0

    if is_obligatory and not aux.phase:
        # si la fase es obligatoria y no hay error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.InvestMintPhases not found")

    return aux


def _get_invest_status_calculated(
        is_draft: bool,
        is_completed: bool,
        date_start_round: datetime,
        date_end_round: datetime
):
    # devuelve el estado actual de un proyecto, ya que depende de las fases de minteo, no es solo el valor de status de la tabla Invest
    if not is_draft and not is_completed:
        if not date_start_round:
            # si no tiene fase lo ponemos como proximo lanzamiento
            return const.INVEST_STATUS_NEXT_LAUNCH
        else:
            if date_start_round > datetime.now():
                # si tiene ronda a futuro estamos en proximo lanzamiento
                return const.INVEST_STATUS_NEXT_LAUNCH
            elif date_start_round < datetime.now() < date_end_round:
                # estamos en medio de una ronda entonces en curso
                return const.INVEST_STATUS_FINANCING_PHASE
            elif date_end_round < datetime.now():
                return const.INVEST_STATUS_IN_PROGRESS
    elif is_completed:
        return const.INVEST_STATUS_FINISHED

    return const.INVEST_STATUS_PENDING


def _get_invest_phases_for_ids_invest(
        db: Session,
        arr_invest_id: [int]
):
    # se recuperan los datos de las fases que ya esten empezadas de las inversiones entrantes
    current_datetime = datetime.now()
    q = db.query(models_invest.InvestMintPhases.invest_id, models_invest.InvestMintPhases.phase, models_invest.InvestMintPhases.date_end, models_invest.InvestMintPhases.date_start,
                 models_invest.InvestMintPhases.max_tokens,
                 models_invest.InvestMintPhases.price_fiat)
    q = q.filter(models_invest.InvestMintPhases.invest_id.in_(arr_invest_id))
    q = q.filter(models_invest.InvestMintPhases.date_start <= current_datetime)
    list_phases = q.order_by(asc(models_invest.InvestMintPhases.date_end)).all()
    list_out = []

    for item in list_phases:
        aux = Object()
        aux.invest_id = item.invest_id
        aux.phase = item.phase
        aux.date_end = item.date_end
        aux.date_start = item.date_start
        aux.max_tokens = item.max_tokens
        aux.price_fiat = item.price_fiat
        list_out.append(aux)
    return list_out


def _get_invest_phases(
        db: Session,
        invest_id: int
):
    # se recuperan los datos de las fases que ya esten empezadas de un proyecto
    current_datetime = datetime.now()
    q = db.query(models_invest.InvestMintPhases.invest_id, models_invest.InvestMintPhases.phase, models_invest.InvestMintPhases.date_end, models_invest.InvestMintPhases.date_start,
                 models_invest.InvestMintPhases.max_tokens,
                 models_invest.InvestMintPhases.price_fiat)
    q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
    q = q.filter(models_invest.InvestMintPhases.date_start <= current_datetime)
    list_phases = q.order_by(asc(models_invest.InvestMintPhases.date_end)).all()
    list_out = []

    for item in list_phases:
        aux = Object()
        aux.invest_id = item.invest_id
        aux.phase = item.phase
        aux.date_end = item.date_end
        aux.date_start = item.date_start
        aux.max_tokens = item.max_tokens
        aux.price_fiat = item.price_fiat
        list_out.append(aux)
    return list_out
