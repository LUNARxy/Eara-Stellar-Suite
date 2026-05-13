import base64
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import asc, func, or_, desc
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import const
from api.v1.base.base import Object
from api.v1.base.base_invest_mint_phases import _get_actual_phase_or_next, _get_invest_phases, \
    _get_invest_status_calculated
from api.v1.base.base_user import _get_profit_percentage_invest_user
from api.v1.endpoints.private.portfolio_nuevo import _get_list_balance_invest_profits
from api.v1.models import models_user, models_invest


def _get_user_invest_all_for_activity(
        db: Session,
        
        user_id: int = 0,
        invest_id: int = 0,
        get_file_document_transfer: bool = False,
        skip: int = 0,
        limit: int = 10,
        only_invest_ids: str = None  # ids, separados por comas de las inversiones que puede ver el usuario
):
    # listado de todas las transacciones de user invest
    q = db.query(models_user.UsersInvest, models_invest.Invest, models_user.User)
    
    # q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
    if user_id != 0:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if invest_id != 0:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)

    if only_invest_ids:
        only_invest_ids_list = [int(i.strip()) for i in only_invest_ids.split(',') if i.strip().isdigit()] if only_invest_ids else [-1]
        q = q.filter(models_user.UsersInvest.invest_id.in_(only_invest_ids_list))

    q = q.filter(models_user.UsersInvest.user_id == models_user.User.id)
    q = q.outerjoin(models_invest.Invest, models_user.UsersInvest.invest_id == models_invest.Invest.id)

    # recuperamos el numero total de usuarios
    total = q.count()
    # recuperamos la lista paginada
    list_items = q.order_by(desc(models_user.UsersInvest.id)).offset(skip).limit(limit).all()

    list_out = []
    for item in list_items:
        aux = Object()
        aux.id = item.UsersInvest.id
        aux.date_created = item.UsersInvest.date_created
        aux.price_token = item.UsersInvest.price_token
        aux.num_tokens = item.UsersInvest.num_tokens
        aux.phase = item.UsersInvest.phase
        aux.value = item.UsersInvest.value
        aux.fees = item.UsersInvest.fees
        aux.type = item.UsersInvest.type
        aux.buy_subtype = item.UsersInvest.buy_subtype
        aux.tx = item.UsersInvest.tx
        aux.email = item.User.email
        aux.parent_id = item.UsersInvest.parent_id
        aux.user_id = item.User.id
        if invest_id == 0:
            # se recuperan mas datos
            aux.invest_id = ''
            aux.invest_name = ''
            aux.slug = ''
            aux.token_abbreviation = ''
            aux.invest_category = ''
            if item.Invest:
                aux.invest_id = item.Invest.id
                aux.invest_name = item.Invest.name
                aux.slug = item.Invest.slug
                aux.token_abbreviation = item.Invest.token_abbreviation
                aux.invest_category = item.Invest.category_id
            aux.signature_documents_id = item.UsersInvest.signature_documents_id
            # aux.signature_documents_id = item.UsersInvest.signature_documents_id
            # aux.id_invest_user_token_buys_id = item.UsersInvest.other_user_id
            # aux.signature_id = item.UsersInvest.signature_id

            # si es del tipo USERS_INVEST_TYPE_BUY_WITHOUT_VERIFIED entonces se busca si tiene el pdf de justificante de transferencia
            aux.has_document_transfer = False
            if item.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_WITHOUT_VERIFIED:
                q = db.query(models_user.UsersInvestDocumentsTransfer)
                q = q.filter(models_user.UsersInvestDocumentsTransfer.user_invest_id == item.UsersInvest.id)
                q = q.filter(models_user.UsersInvestDocumentsTransfer.user_id == item.User.id)
                doc = q.first()
                if doc:
                    aux.has_document_transfer = True
                    if get_file_document_transfer:
                        try:
                            file_path = f"private/{doc.file}"
                            with open(file_path, "rb") as image_file:
                                aux.file_document_transfer = base64.b64encode(image_file.read())
                                aux.file_document_transfer_name = doc.file
                        except FileNotFoundError:
                            pass

        list_out.append(aux)

    return {'list': list_out, 'total': total}


def _get_count_type_invest(
        db: Session,
        
        user_id: int = 0,
        category_id: int = -1,  # para filtrar por categoría de la inversion
):
    # se recupera si tuvo alguna inversión de cada categoria y devuelve el listado con los tipos de categoria
    q = db.query(models_invest.Invest.category_id)
    
    q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
    q = q.filter(models_user.UsersInvest.user_id == user_id)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)

    if category_id != -1:
        q = q.filter(models_invest.Invest.category_id == category_id)

    list_invest = q.distinct().all()
    list_out = []
    for item in list_invest:
        list_out.append(item.category_id)
    return list_out


def _get_value_profits_in_date(
        *,
        db: Session,
        
        date_end: datetime,
        invest_id: int,
        user_id: int,
        category_id: int = -1,
):
    # se recupera, para cada fecha, el valor de los beneficios

    # se recuperan las inversiones del usuario que se compraron y vendieron y se reembolsaron para las graficas de balances
    q = db.query(models_user.UsersInvest.id, models_user.UsersInvest.invest_id, models_user.UsersInvest.type, models_user.UsersInvest.price_token, models_user.UsersInvest.num_tokens,
                 models_user.UsersInvest.value, models_user.UsersInvest.date_created, models_user.UsersInvest.other_user_id)
    
    q = q.filter(models_user.UsersInvest.date_created <= date_end)

    q = q.filter(models_user.UsersInvest.user_id == user_id)

    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD))

    q = q.filter(models_user.UsersInvest.invest_id == invest_id)

    if category_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
        q = q.filter(models_invest.Invest.category_id == category_id)

    list_items = q.order_by(asc(models_user.UsersInvest.date_created), asc(models_user.UsersInvest.id)).all()

    list_items_buys = []  # List to store purchases
    total_sold = 0  # Total profit from all sales

    # Process each transaction
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
                last_buy = list_items_buys[0]  # Take the newest purchase
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

            # Calculate profit for this sale
            profit = total_sale_revenue - total_cost
            total_sold += profit

    # ademas se le suman los rendimientos
    q = db.query(func.sum(models_user.UsersInvest.value).label("total_value"))
    
    q = q.filter(models_user.UsersInvest.date_created <= date_end)
    if invest_id != 0:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    if user_id != 0:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if category_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
        q = q.filter(models_invest.Invest.category_id == category_id)

    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_PROFITS)
    total_profit = q.first()
    total_profit_value = 0
    if total_profit and total_profit.total_value:
        total_profit_value = total_profit.total_value

    return total_sold + total_profit_value


def _get_value_tokens_in_date(
        db: Session,
        date_end: datetime,
        invest_id: int,
        num_tokens: int,
):
    # se recupera el valor de tokens que teniamos en esa fecha
    q = db.query(models_invest.InvestMintPhases.price_fiat)
    q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
    q = q.filter(models_invest.InvestMintPhases.date_start <= date_end)
    phase = q.order_by(desc(models_invest.InvestMintPhases.date_start)).first()
    if phase:
        return phase.price_fiat * num_tokens
    return 0


def _get_users_invest_buy(
        db: Session,
        
        user_id: int = 0,
        invest_id: int = 0,
        buy_type: int = 0,  # 0->all 1->plataforma 2->usuarios
        category_id: int = -1,  # para filtrar por categoría de la inversion
):
    # se recuperan las inversiones del usuario que se compraron en la plataforma o usuarios o ambos
    # aunque se hayan vendido despues tambien van en este listado
    q = db.query(models_user.UsersInvest.id, models_user.UsersInvest.invest_id, models_user.UsersInvest.phase, models_user.UsersInvest.price_token, models_user.UsersInvest.num_tokens,
                 models_user.UsersInvest.value, models_user.UsersInvest.type, models_user.UsersInvest.other_user_id, models_user.UsersInvest.profit_id, models_user.UsersInvest.date_created)
    

    if category_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
        q = q.filter(models_invest.Invest.category_id == category_id)

    if user_id != 0:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if invest_id != 0:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    if buy_type == 1:
        q = q.filter(models_user.UsersInvest.other_user_id == None)
    if buy_type == 2:
        q = q.filter(models_user.UsersInvest.other_user_id != None)
    # las que han sido pagadas y validadas
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
    list_invest = q.order_by(asc(models_user.UsersInvest.date_created), asc(models_user.UsersInvest.id)).all()
    list_invest_out = []
    for item in list_invest:
        obj = Object()
        obj.id = item.id
        obj.invest_id = item.invest_id
        obj.phase = item.phase
        obj.type = item.type
        obj.price_token = item.price_token
        obj.num_tokens = item.num_tokens
        obj.value = item.value
        obj.date_created = item.date_created
        obj.other_user_id = item.other_user_id
        obj.profit_id = item.profit_id
        list_invest_out.append(obj)
    return list_invest_out


def _get_users_invest_refund(
        db: Session,
        
        user_id: int = 0,
        invest_id: int = 0,
        category_id: int = -1,  # para filtrar por categoría de la inversion
        refund_type: int = -1
):
    # se recuperan las inversiones del usuario que la plataforma le ha devuelto
    q = db.query(models_user.UsersInvest.id, models_user.UsersInvest.user_id, models_user.UsersInvest.invest_id, models_user.UsersInvest.phase, models_user.UsersInvest.price_token,
                 models_user.UsersInvest.num_tokens,
                 models_user.UsersInvest.value, models_user.UsersInvest.type, models_user.UsersInvest.other_user_id, models_user.UsersInvest.date_created)
    

    if category_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
        q = q.filter(models_invest.Invest.category_id == category_id)

    if user_id != 0:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if invest_id != 0:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)

    if refund_type == -1:
        q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND,
                         models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND_PARTIAL,
                         models_user.UsersInvest.type == const.USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND,
                         # models_user.UsersInvest.type == const.USERS_INVEST_TYPE_PROFITS_RECEIVED
                         ))
    elif refund_type == const.USERS_INVEST_TYPE_REFUND:
        q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND,
                         models_user.UsersInvest.type == const.USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND,
                         # models_user.UsersInvest.type == const.USERS_INVEST_TYPE_PROFITS_RECEIVED
                         ))
    elif refund_type == const.USERS_INVEST_TYPE_REFUND_PARTIAL:
        q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND_PARTIAL,
                         models_user.UsersInvest.type == const.USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND,
                         # models_user.UsersInvest.type == const.USERS_INVEST_TYPE_PROFITS_RECEIVED
                         ))
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.El tipo de devolución no es correcto")

    list_invest = q.order_by(asc(models_user.UsersInvest.date_created), asc(models_user.UsersInvest.id)).all()
    list_invest_out = []
    for item in list_invest:
        obj = Object()
        obj.id = item.id
        obj.user_id = item.user_id
        obj.invest_id = item.invest_id
        obj.phase = item.phase
        obj.type = item.type
        obj.price_token = item.price_token
        obj.num_tokens = item.num_tokens
        obj.value = item.value
        obj.date_created = item.date_created
        obj.other_user_id = item.other_user_id
        list_invest_out.append(obj)
    return list_invest_out


def _get_users_invest_sold(
        db: Session,
        
        user_id: int = 0,
        invest_id: int = 0,
        category_id: int = -1,  # para filtrar por categoría de la inversion
):
    # se recuperan las inversiones del usuario vendidas
    q = db.query(models_user.UsersInvest.id, models_user.UsersInvest.invest_id, models_user.UsersInvest.type, models_user.UsersInvest.price_token, models_user.UsersInvest.num_tokens,
                 models_user.UsersInvest.value, models_user.UsersInvest.date_created)
    
    if user_id != 0:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD)
    if invest_id != 0:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    if category_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
        q = q.filter(models_invest.Invest.category_id == category_id)

    list_items = q.order_by(asc(models_user.UsersInvest.date_created), asc(models_user.UsersInvest.id)).all()
    list_out = []
    for item in list_items:
        obj = Object()
        obj.id = item.id
        obj.invest_id = item.invest_id
        obj.type = item.type
        obj.price_token = item.price_token
        obj.num_tokens = item.num_tokens
        obj.value = item.value
        obj.date_created = item.date_created
        list_out.append(obj)
    return list_out


def _get_invest_data_for_invest_user(
        db: Session,
        
        user_id: int = 0,
        category_id: int = -1,  # para filtrar por categoría de la inversion
):
    # se recuperan los datos de la inversion del usuario
    q = db.query(
        models_invest.Invest.id,
        models_invest.Invest.name,
        models_invest.Invest.name_EN,
        models_invest.Invest.title,
        models_invest.Invest.title_EN,
        models_invest.Invest.slug,
        models_invest.Invest.category_id,
        models_invest.Invest.file,
        models_invest.Invest.token_abbreviation,
        models_invest.Invest.is_completed,
        models_invest.Invest.is_draft
    )
    
    q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
    if user_id != 0:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if category_id != -1:
        q = q.filter(models_invest.Invest.category_id == category_id)
    # las que han sido pagadas y validadas
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
    list_invest = q.distinct().all()
    list_invest_out = []
    for item_invest in list_invest:
        # se recupera la fase actual de minteo de un proyecto para recuperar el estado
        data_phase = _get_actual_phase_or_next(db=db, invest_id=item_invest.id)
        date_start_round = data_phase.date_start_round
        date_end_round = data_phase.date_end_round
        status_invest = _get_invest_status_calculated(is_draft=item_invest.is_draft, is_completed=item_invest.is_completed, date_start_round=date_start_round, date_end_round=date_end_round)

        # se recupera el valor de la inversión inicial, que es lo que se pone en el mensaje de devolución
        q = db.query(models_user.UsersInvest.value)
        q = q.filter(models_user.UsersInvest.invest_id == item_invest.id)
        q = q.filter(models_user.UsersInvest.user_id == user_id)
        q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND)
        refund_value = q.first()
        if refund_value:
            refund_value = refund_value.value

        obj = Object()
        obj.id = item_invest.id
        obj.name = item_invest.name
        obj.name_EN = item_invest.name_EN
        obj.title = item_invest.title
        obj.title_EN = item_invest.title_EN
        obj.slug = item_invest.slug
        obj.category_id = item_invest.category_id
        obj.file = item_invest.file
        obj.token_abbreviation = item_invest.token_abbreviation
        obj.status = status_invest
        obj.refund_value = refund_value
        list_invest_out.append(obj)
    return list_invest_out


def _get_invest_profits_acumulated(
        db: Session,
        
        user_id: int = 0,
        invest_id: int = 0,
        category_id: int = -1,  # para filtrar por categoría de la inversion
):
    # se recuperan los datos de los beneficios de la inversion para las graficas, son datos acumulados
    q = db.query(models_user.UsersInvest.date_created, models_user.UsersInvest.type)
    
    if invest_id != 0:
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    if user_id != 0:
        q = q.filter(models_user.UsersInvest.user_id == user_id)
    if category_id != -1:
        q = q.filter(models_user.UsersInvest.invest_id == models_invest.Invest.id)
        q = q.filter(models_invest.Invest.category_id == category_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_PROFITS,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD))
    list_items = q.order_by(asc(models_user.UsersInvest.date_created), asc(models_user.UsersInvest.id)).all()

    list_profits = []
    for item in list_items:
        aux = Object()
        aux.invest_id = invest_id
        aux.type = item.type
        aux.date_created = item.date_created
        aux.profit_value = _get_value_profits_in_date(db=db, date_end=item.date_created, invest_id=invest_id, user_id=user_id, category_id=category_id)
        list_profits.append(aux)

    return list_profits


def _get_all_portfolio_table(
        db: Session,
        
        user_id: int = 0,
        category_id: int = -1,  # para filtrar por categoría de la inversion
        only_invest_ids: str = None # ids, separados por comas de las inversiones que puede ver el usuario
):
    # se recuperan las inversiones del usuario que se compraron a la plataforma
    list_user_invest_buy_platform = _get_users_invest_buy(db=db, user_id=user_id, invest_id=0, buy_type=1, category_id=category_id)

    # se recuperan las inversiones del usuario que se compraron a otros usuarios
    list_user_invest_buy_other_users = _get_users_invest_buy(db=db, user_id=user_id, invest_id=0, buy_type=2, category_id=category_id)

    # se recuperan las inversiones del usuario vendidas
    list_user_invest_sold = _get_users_invest_sold(db=db, user_id=user_id, category_id=category_id)

    # se recuperan las inversiones del usuario que la plataforma le ha devuelto
    list_user_invest_refund_platform = _get_users_invest_refund(db=db, user_id=user_id, invest_id=0, category_id=category_id)

    # se recuperan los datos de las inversiones del usuario, nombre, titulo, etc
    list_data_invest = _get_invest_data_for_invest_user(db=db, user_id=user_id, category_id=category_id)

    # por cada inversion se recuperan datos
    list_extra_data = []
    for item_data_invest in list_data_invest:
        list_profits = _get_invest_profits_acumulated(db=db, user_id=user_id, invest_id=item_data_invest.id, category_id=category_id)
        obj = {
            'invest_id': item_data_invest.id,
            'list_mint_phases': _get_invest_phases(db=db, invest_id=item_data_invest.id),
            'list_profits_to_chart': list_profits,
            'list_profits': list_profits,
            'list_status_description': db.query(models_invest.InvestStatusDescription).filter(models_invest.InvestStatusDescription.invest_id == item_data_invest.id).all(),
            'list_balance_profits_final_value': _get_list_balance_invest_profits(db=db, category_id=category_id, invest_id=item_data_invest.id, user_id=user_id, only_invest_ids=only_invest_ids)
        }

        list_extra_data.append(obj)
        # recuperamos el profit_percentage del usuario para cada inversion
        if user_id != 0:
            item_data_invest.profit_percentage = _get_profit_percentage_invest_user(db=db, invest_id=item_data_invest.id, user_id=user_id)

    return {
        "list_user_invest_buy_platform": list_user_invest_buy_platform,
        "list_user_invest_buy_other_users": list_user_invest_buy_other_users,
        "list_user_invest_sold": list_user_invest_sold,
        "list_user_invest_refund_platform": list_user_invest_refund_platform,
        "list_invest": list_data_invest,
        "list_extra_data": list_extra_data
    }
