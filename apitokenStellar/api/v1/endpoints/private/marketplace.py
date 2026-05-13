from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, asc
from starlette import status
from datetime import datetime

from api.v1 import roles, const
from api.v1.base.base import _can_access_roles, Object

from api.v1.base.base_invest import _get_invest, _get_total_num_tokens_sold_this_round, _get_num_tokens_in_date
from api.v1.base.base_invest_mint_phases import _get_actual_phase_or_next, _get_actual_phase
from api.v1.base.base_login import UserCurrentLogin, _get_user_login
from api.v1.base.base_marketplace import _buy_user_invest_tokens
from api.v1.base.base_portfolio import _get_users_invest_refund
from api.v1.base.base_user import _get_user_by_id

from api.v1.deps import _get_db
from api.v1.emails import emails
from api.v1.models import models_user, models_invest
from config import EARASTELLAR_PROMOTER

router = APIRouter()


#########################################################################################################
#   FUNCIONES TIPO GET
#########################################################################################################
@router.get("/promoter_contribution/list/{invest_id}")
def read_invest_promoter_contribution_list(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int
):
    """
    Se recupera la lista de contribuciones del promotor a la inversion
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    q = db.query(models_user.UsersInvest.invest_id, models_user.UsersInvest.num_tokens, models_user.UsersInvest.price_token, models_user.UsersInvest.date_created, models_user.UsersInvest.phase)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(models_user.UsersInvest.user_id == EARASTELLAR_PROMOTER)
    list_contributions = q.all()

    list_contributions_out = []
    for item in list_contributions:
        aux = Object()
        aux.invest_id = item.invest_id
        aux.num_tokens = item.num_tokens
        aux.price_token = item.price_token
        aux.phase = item.phase
        aux.date_created = item.date_created
        list_contributions_out.append(aux)

    # se recupera la fase actual de minteo de un proyecto
    data_phase = _get_actual_phase_or_next(db=db, invest_id=invest_id, is_obligatory=True)
    # se recuperan los tokens comprados por los usuarios para ver el maximo de token que quedan
    sold_tokens_phase = _get_num_tokens_in_date(db=db,  phase=data_phase.phase, invest_id=invest_id)['num_tokens']

    return {
        'is_completed': invest_project.is_completed,
        'list_contributions': list_contributions_out,
        'actual_phase': data_phase.phase,
        'actual_date_start_round': data_phase.date_start_round,
        'actual_date_end_round': data_phase.date_end_round,
        'actual_price_token': data_phase.price_token,
        'actual_num_tokens': data_phase.num_tokens,
        'num_tokens_min_to_buy': data_phase.num_tokens_min_to_buy,
        'actual_remaining_tokens': (data_phase.num_tokens - sold_tokens_phase)
    }


@router.get("/investors/{invest_id}")
def read_users_investors_projects(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        refund_type: int = -1  # cuando es -1 es el listado de inversores, cuando es 40 es devoluciones y 42 amortizaciones
):
    # devuelve el listado de inversores con sus tokens y su valor

    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # se recuperan todos los usuarios que han invertido en el proyecto
    q = db.query(models_user.UsersInvest.id, models_user.UsersInvest.user_id, models_user.UsersInvest.num_tokens, models_user.UsersInvest.price_token,
                 models_user.User.email, models_user.UsersInvest.type, models_user.UsersInvest.parent_id, models_user.UsersInvest.phase)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(models_user.UsersInvest.user_id == models_user.User.id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND_PARTIAL,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND))
    list_user_invest = q.order_by(asc(models_user.UsersInvest.date_created), asc(models_user.UsersInvest.id), asc(models_user.UsersInvest.id)).all()

    list_invest_out = []
    for user_invest in list_user_invest:
        aux = Object()
        aux.user_id = user_invest.user_id
        aux.email = user_invest.email
        aux.user_invest_id = user_invest.id
        aux.value = user_invest.num_tokens * user_invest.price_token
        aux.price_token = user_invest.price_token
        aux.num_tokens = user_invest.num_tokens
        aux.phase = user_invest.phase

        if user_invest.type == const.USERS_INVEST_TYPE_BUY:
            list_invest_out.append(aux)
        else:
            if refund_type == -1:
                if user_invest.type == const.USERS_INVEST_TYPE_REFUND:
                    # se restan del listado las devoluciones ya hechas
                    for user_invest_out in list_invest_out:
                        if user_invest_out.user_invest_id == user_invest.parent_id:
                            user_invest_out.num_tokens -= user_invest.num_tokens
                            user_invest_out.value = user_invest_out.num_tokens * user_invest_out.price_token
            else:
                # se restan del listado las devoluciones ya hechas y las ventas
                for user_invest_out in list_invest_out:
                    if user_invest_out.user_invest_id == user_invest.parent_id:
                        user_invest_out.num_tokens -= user_invest.num_tokens
                        user_invest_out.value = user_invest_out.num_tokens * user_invest_out.price_token

    # no devolvemos las que tengan 0 tokens
    for user_invest_out in list_invest_out:
        if user_invest_out.num_tokens == 0:
            list_invest_out.remove(user_invest_out)

    aux = Object()
    aux.list_users_tokens = list_invest_out

    if refund_type == -1:
        data_phase = _get_actual_phase(db=db, invest_id=invest_id)
        sold_tokens_phase = _get_total_num_tokens_sold_this_round(db=db, invest_id=invest_id, phase=data_phase.phase)
        remaining_tokens = data_phase.num_tokens - sold_tokens_phase
        aux.actual_price_token = data_phase.price_token
        aux.actual_num_tokens = data_phase.num_tokens
        aux.num_tokens_min_to_buy = data_phase.num_tokens_min_to_buy
        aux.actual_remaining_tokens = remaining_tokens
        if data_phase.phase:
            aux.phase = data_phase.phase
        else:
            aux.phase = 'all'
        aux.is_completed = invest_project.is_completed

    return aux


@router.get("/investors_refund/{invest_id}")
def read_investors_refund_list(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        refund_type: int = const.USERS_INVEST_TYPE_REFUND,
):
    list_refunds = _get_users_invest_refund(db=db,  invest_id=invest_id, refund_type=refund_type)
    list_out = []
    for item in list_refunds:
        aux = Object()
        aux.email = _get_user_by_id(db=db, user_id=item.user_id).email
        aux.user_id = item.user_id
        aux.num_tokens = item.num_tokens
        aux.price_token = item.price_token
        aux.value = item.value
        aux.phase = item.phase
        list_out.append(aux)

    return list_out


#########################################################################################################
#   FUNCIONES TIPO POST
#########################################################################################################
@router.post("/promoter_contribution/{invest_id}/{num_tokens}")
def create_invest_promoter_contribution(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        num_tokens: int,
):
    """
    aportacion de capital de un promotor, hecha desde el admin, tendra blockchain dependiendo de la plataforma
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # si el proyecto ya se ha cerrado error
    if invest_project.is_completed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.El proyecto ya se ha cerrado")

    return _buy_user_invest_tokens(
        db=db,
        
        user_id=EARASTELLAR_PROMOTER,
        invest_id=invest_id,
        num_tokens=num_tokens,
        type_buy=const.USERS_INVEST_TYPE_BUY,
        buy_subtype=const.BUY_SUBTYPE_PAYMENT_TRANSFER,  # como si fuese transferencia
    )


@router.post("/user_contribution/{invest_id}/{user_id}/{num_tokens}/{user_invest_parent_id}/{signature_documents_id}")
async def create_invest_user_contribution(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        user_id: int,
        num_tokens: int,
        user_invest_parent_id: int,  # si viene este dato distinto de 0 es una compra sin verificar que se va a verificar por el admin
        signature_documents_id: str = None
):
    # aportacion de capital de un usuario, hecha desde el admin
    # tambien para verificar una transaccion hecha desde el user por transferencia y se verifica desde el admin

    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # si el proyecto ya se ha cerrado error
    if invest_project.is_completed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.El proyecto ya se ha cerrado")

    date_created = None
    if user_invest_parent_id != 0:
        # recuperamos el registro de user_invest_parent_id
        q = db.query(models_user.UsersInvest)
        q = q.filter(models_user.UsersInvest.id == user_invest_parent_id)
        q = q.filter(models_user.UsersInvest.user_id == user_id)
        q = q.filter(models_user.UsersInvest.invest_id == invest_id)
        q = q.filter(models_user.UsersInvest.num_tokens == num_tokens)
        # el padre tiene que ser o sin verificar o rechazado para poder volver a verificarlo
        q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_WITHOUT_VERIFIED,
                         models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_CARD_WITHOUT_VERIFIED,
                         models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_REJECTED))
        data_user_invest = q.first()
        date_created = data_user_invest.date_created
        if not data_user_invest:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Se ha producido un error inesperado")
        # se recupera si existe un registro que ya este verificado o rechazado con ese parent_id para no duplicar
        q = db.query(models_user.UsersInvest)
        q = q.filter(models_user.UsersInvest.parent_id == user_invest_parent_id)
        if q.count() > 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.La transacción ya se había ejecutado")

    if not signature_documents_id or signature_documents_id == 'null' or signature_documents_id == '0':
        signature_documents_id = None
    try:
        buy = _buy_user_invest_tokens(
            db=db,
            
            user_id=user_id,
            invest_id=invest_id,
            num_tokens=num_tokens,
            type_buy=const.USERS_INVEST_TYPE_BUY,
            buy_subtype=const.BUY_SUBTYPE_PAYMENT_TRANSFER,  # como si fuese transferencia
            user_contribution_by_admin=True,
            date_created=date_created,
            user_invest_parent_id=user_invest_parent_id,
            signature_documents_id=signature_documents_id
        )
    except:
        buy = _buy_user_invest_tokens(
            db=db,
            
            user_id=user_id,
            invest_id=invest_id,
            num_tokens=num_tokens,
            type_buy=const.USERS_INVEST_TYPE_BUY,
            buy_subtype=const.BUY_SUBTYPE_PAYMENT_TRANSFER,  # como si fuese transferencia
            user_contribution_by_admin=True,
            date_created=date_created,
            user_invest_parent_id=user_invest_parent_id,
            signature_documents_id=signature_documents_id,
            financing_phase=False
        )

    # se manda email al usuario
    db_user = _get_user_by_id(db=db, user_id=user_id)
    q = db.query(models_user.User.email)
    q = q.filter(models_user.User.id == user_id)
    data_email = q.first()
    q = db.query(models_invest.Invest.name, models_invest.Invest.name_EN, models_invest.Invest.slug)
    q = q.filter(models_invest.Invest.id == invest_id)
    data_invest = q.first()
    name = data_invest.name_EN
    if db_user.language == 'es':
        name = data_invest.name
    await emails.send_email_buy_fiat_without_verified_ok(
        language=db_user.language,
        
        email=data_email.email,
        project_name=name,
        token_number=str(num_tokens),
        token_value=str(num_tokens * buy.price_token),
        symbol_fiat="EUR"
    )

    return buy



@router.post("/user_contribution_refund/{invest_id}/{user_id}/{user_invest_id}")
async def create_invest_user_contribution_refund(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        user_id: int,
        user_invest_id: int,
        refund_type: int = const.USERS_INVEST_TYPE_REFUND,
        num_tokens: int
):
    # se devuelve la compra de un usuario

    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # si el proyecto ya se ha cerrado error
    if invest_project.is_completed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.El proyecto ya se ha cerrado")

    # comprobamos que el usuario tenga invertida la cantidad suficiente para poder devolverle y no se haya devuelto ya

    # se recupera la inversion que se va a devolver
    q = db.query(models_user.UsersInvest)
    q = q.filter(models_user.UsersInvest.user_id == user_id)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(models_user.UsersInvest.id == user_invest_id)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
    invest_to_refund = q.first()
    if not invest_to_refund:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.No se ha encontrado la inversión")

    # comprobamos que no exista ya una devolución sobre esa inversión y que sume ya el total de tokens
    q = db.query(func.sum(models_user.UsersInvest.num_tokens).label("num_tokens"))
    q = q.filter(models_user.UsersInvest.user_id == user_id)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(models_user.UsersInvest.parent_id == user_invest_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND_PARTIAL,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND))
    num_tokens_already_refund = q.first().num_tokens
    if not num_tokens_already_refund:
        num_tokens_already_refund = 0
    if num_tokens_already_refund + num_tokens > invest_to_refund.num_tokens:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.La inversión ya se ha devuelto con anterioridad")

    if refund_type != const.USERS_INVEST_TYPE_REFUND and refund_type != const.USERS_INVEST_TYPE_REFUND_PARTIAL:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.El tipo de devolución no es correcto")

    # insertamos el registro de devolución
    item = models_user.UsersInvest(
        
        user_id=user_id,
        invest_id=invest_id,
        num_tokens=num_tokens,
        price_token=invest_to_refund.price_token,
        value=invest_to_refund.price_token * num_tokens,
        date_created=datetime.now(),
        type=refund_type,
        parent_id=invest_to_refund.id,
        phase=invest_to_refund.phase
    )
    try:
        # se guarda la devolucion de la compra
        db.add(item)
        db.commit()

    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="server.Unexpected error")


@router.post("/buy_tokens")
async def buy_tokens(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])),

        invest_id: int = Form(..., ge=1),
        num_tokens: int = Form(..., ge=1),
        type_buy: int = Form(...),  # 0-> wallet virtual 1->transferencia 2->tarjeta pero sin verificar
        signature_documents_id: int = Form(0, ge=0)
):
    """
    Compras de los usuarios a la plataforma
    """
    # se comprueba que exista la inversion
    invest = _get_invest(db=db,  invest_id=invest_id)

    if invest.is_paused:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="server.el proyecto esta en pausa")

    if not signature_documents_id:
        signature_documents_id = None
    item_buy = _buy_user_invest_tokens(
        db=db,
        
        user_id=current_user.id,
        invest_id=invest_id,
        num_tokens=num_tokens,
        type_buy=const.USERS_INVEST_TYPE_BUY,
        buy_subtype=type_buy,
        signature_documents_id=signature_documents_id
    )

    db_user = _get_user_by_id(db=db,  user_id=current_user.id)

    q = db.query(models_invest.Invest.name, models_invest.Invest.name_EN, models_invest.Invest.slug)
    q = q.filter(models_invest.Invest.id == invest_id)
    data_invest = q.first()
    name = data_invest.name_EN
    if db_user.language == 'es':
        name = data_invest.name

    await emails.send_email_buy_fiat_without_verified_ok(
        language=db_user.language,
        
        email=db_user.email,
        project_name=name,
        token_number=str(item_buy.num_tokens),
        token_value=str(item_buy.num_tokens * item_buy.price_token),
        symbol_fiat="EUR"
    )

    if type_buy == 1:  # si es por transferencia se devuelven los datos del IBAN
        name_bank = ''
        beneficiary = ''
        iban = ''
        swift = ''
        return {
            'user_invest_id': item_buy.id,
            'name_bank': name_bank,
            'beneficiary': beneficiary,
            'iban': iban,
            'swift': swift,
            'concept': f"{current_user.id}-earastellar-{item_buy.id}"
        }

    return {"ok": True}
