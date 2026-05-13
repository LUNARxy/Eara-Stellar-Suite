from datetime import datetime
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from starlette import status

import config
from api.v1 import roles, const
from api.v1.base.base import _update, _create, _delete, _can_access_roles, Object
from api.v1.base.base_login import UserCurrentLogin, _get_user_login
from api.v1.base.base_user import _get_user_by_id

from api.v1.deps import _get_db
from api.v1.emails import emails
from stellar_sdk import Keypair as StellarKeypair
from api.v1.models import models_invest, models_user
from api.v1.models.models_invest import InvestMintERC20Tokens

router = APIRouter()


#########################################################################################################
#   FUNCIONES TIPO GET
#########################################################################################################
@router.get("/list/{invest_id}")
def read_invest_phases_list(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int
):
    """
    Se recupera la lista de fases de una inversion
    """
    q = db.query(models_invest.InvestMintPhases)
    q = q.filter(models_invest.InvestMintPhases.invest_id == models_invest.Invest.id)
    q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
    
    q = q.order_by(models_invest.InvestMintPhases.date_start)
    return q.all()


#########################################################################################################
#   FUNCIONES TIPO POST
#########################################################################################################
@router.post("/{invest_id}")
def create_invest_phases(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        phase: str = Form(...),
        is_private: bool = Form(...),
        max_tokens: int = Form(...),
        num_tokens_min_to_buy: int = Form(...),
        symbol_fiat: str = Form(None),
        price_fiat: float = Form(...),
        date_start: datetime = Form(...),  # fecha de inicio de la fase
        date_end: datetime = Form(...),  # fecha de fin de la fase
):
    """
    Se crea una nueva fase para una inversion
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # si el proyecto ya se ha cerrado error
    if invest_project.is_completed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.El proyecto ya se ha cerrado")

    # si la fecha de fin es menor que la fecha de inicio
    if date_end < date_start:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.The End date cannot be less than the Start date")

    # se recuperan las fases que ya existen para su validacion
    list_phases = db.query(models_invest.InvestMintPhases) \
        .filter(models_invest.InvestMintPhases.invest_id == models_invest.Invest.id) \
        .filter(models_invest.InvestMintPhases.invest_id == invest_id) \
        .order_by(models_invest.InvestMintPhases.date_start) \
        .all()

    for item in list_phases:
        # se comprueba que no exista ya una fase con el mismo nombre
        if item.phase == phase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.There is a phase with the same name, choose another")
        # se comprueba que no se solapen fechas
        if (date_start <= item.date_start and date_end >= item.date_end) or (date_start <= item.date_end and date_end >= item.date_start):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Phase dates cannot overlap")

    obj = Object()
    obj.invest_id = invest_id
    obj.phase = phase
    obj.is_private = is_private
    obj.max_tokens = max_tokens
    obj.num_tokens_min_to_buy = num_tokens_min_to_buy
    obj.price_fiat = price_fiat
    obj.date_start = date_start
    obj.date_end = date_end
    obj.symbol_fiat = symbol_fiat

    stellar_kp = StellarKeypair.random()
    obj.mint_address = stellar_kp.public_key
    obj.mint_pk = stellar_kp.secret
    q = db.query(InvestMintERC20Tokens).filter(InvestMintERC20Tokens.invest_id == invest_id).filter(InvestMintERC20Tokens.token_symbol == 'XLM')
    if not q.first():
        invest_mint_token = InvestMintERC20Tokens(invest_id=invest_id, token_symbol='XLM', token_address='native', token_decimals=7)
        db.add(invest_mint_token)
        db.commit()

    return _create(db=db, obj_in=obj, table='invest_mint_phases')


#########################################################################################################
#   FUNCIONES TIPO PUT
#########################################################################################################
@router.put("/{invest_id}")
def update_invest_phases(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        phase: str = Form(...),
        is_private: bool = Form(...),
        max_tokens: int = Form(...),
        num_tokens_min_to_buy: int = Form(...),
        symbol_fiat: str = Form(None),
        price_fiat: float = Form(...),
        date_start: datetime = Form(...),  # fecha de inicio de la fase
        date_end: datetime = Form(...),  # fecha de fin de la fase
):
    """
    se actualiza la fase de inversion
    """
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_de=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # si el proyecto ya se ha cerrado error
    if invest_project.is_completed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.El proyecto ya se ha cerrado")

    # si la fecha de fin es menor que la fecha de inicio
    if date_end < date_start:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.The End date cannot be less than the Start date")

    db_phase = db.query(models_invest.InvestMintPhases).filter(models_invest.InvestMintPhases.invest_id == invest_id). \
        filter(models_invest.InvestMintPhases.phase == phase).first()

    if not db_phase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Phase not found")

    # se recuperan las fases que ya existen para su validacion
    list_phases = db.query(models_invest.InvestMintPhases) \
        .filter(models_invest.InvestMintPhases.invest_id == models_invest.Invest.id) \
        .filter(models_invest.InvestMintPhases.invest_id == invest_id) \
        .order_by(models_invest.InvestMintPhases.date_start) \
        .all()

    for item in list_phases:
        # se comprueba que no se solapen fechas
        if item.phase != phase and ((date_start <= item.date_start and date_end >= item.date_end) or (date_start <= item.date_end and date_end >= item.date_start)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Phase dates cannot overlap")

    db_phase.date_start = date_start
    db_phase.date_end = date_end

    db_phase.max_tokens = max_tokens
    db_phase.num_tokens_min_to_buy = num_tokens_min_to_buy
    db_phase.price_fiat = price_fiat
    db_phase.is_private = is_private

    db.add(db_phase)
    db.commit()
    db.flush()

    return db_phase


@router.put("/data_phase_completed/{invest_id}")
def update_invest_data_phase_completed(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        num_investors_completed: int = Form(...),
        num_tokens_completed: int = Form(...),
        total_amount_invested_completed: float = Form(...),
        invest_id: int,
):
    """
    Se guardan los datos como si la fase estuviera ya completa
    """
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    obj_to_save = Object()
    obj_to_save.num_investors_completed = num_investors_completed
    obj_to_save.num_tokens_completed = num_tokens_completed
    obj_to_save.total_amount_invested_completed = total_amount_invested_completed

    _update(db, db_obj=invest_project, obj_in=obj_to_save)

    return {"ok": True}


@router.put("/mark_deploy/{invest_id}")
async def mark_deploy(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        status_invest: int = Form(...),
        deploy_state: int = Form(...),
        # 0->pendiente 1->fase de pre lanzamiento 2->fase de financiacion 3->en curso 99->proyecto acabado 100->proyecto eliminado
        invest_id: int,
):
    """
    Se marca para desplegar una fase de una inversion
    """
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # si el proyecto ya se ha cerrado error
    if invest_project.is_completed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.El proyecto ya se ha cerrado")

    invest_project.deploy_state = deploy_state
    db.add(invest_project)
    db.commit()

    try:
        # mandar correo para avisar de desplegar contrato
        dev_emails = config.DEV_EMAILS

        for email in dev_emails:
            if deploy_state == 0:
                await emails.send_email_NO_deploy_contract(
                    
                    email=email,
                    project_name=invest_project.name
                )
            if deploy_state == 1:
                await emails.send_email_deploy_contract(
                    
                    email=email,
                    project_name=invest_project.name
                )
    except Exception as e:
        print(e)

    return {"ok": True}


@router.put("/update_phase_to_buy/{invest_id}/{user_id}/{preference_to_buy}")
async def update_phase_to_buy(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        user_id: int,
        preference_to_buy: str,
):
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # si el proyecto ya se ha cerrado error
    if invest_project.is_completed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.El proyecto ya se ha cerrado")

    # comprobamos que el usuario este en esta white label
    db_user = _get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.User not found")

    db_user_white_list = db.query(models_user.UserInvestWhiteList).filter(models_user.UserInvestWhiteList.user_id == user_id).filter(models_user.UserInvestWhiteList.invest_id == invest_id).first()
    if not db_user_white_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.User not found in white label")

    if preference_to_buy == 'public':
        preference_to_buy = None

    obj_in = Object()
    obj_in.preference_to_buy = preference_to_buy
    _update(db, db_obj=db_user_white_list, obj_in=obj_in)

    # se manda un correo al usuario para que sepa que se ha apuntado
    project_name = invest_project.name_EN
    if project_name is None or db_user.language == 'es':
        project_name = invest_project.name
    await emails.send_email_access_white_list_ok(
        language=db_user.language,
        
        email=db_user.email,
        project_name=project_name,
        project_slug=invest_project.slug,
        phase=preference_to_buy
    )

    return {"ok": True}


#########################################################################################################
#   FUNCIONES TIPO DELETE
#########################################################################################################
@router.delete("/{invest_id}/{phase}", status_code=status.HTTP_200_OK, summary="Delete a invest phases mint by Id")
def delete_phases(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
        phase: str,
):
    """
    Se borra una fase de una inversion
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # si el proyecto ya se ha cerrado error
    if invest_project.is_completed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.El proyecto ya se ha cerrado")

    item_db = db.query(models_invest.InvestMintPhases) \
        .filter(models_invest.InvestMintPhases.invest_id == invest_id) \
        .filter(models_invest.InvestMintPhases.phase == phase).first()
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.invest phases not found")

    if _delete(db, obj_delete=item_db):
        return {"ok": True}
    return {"ok": False}
