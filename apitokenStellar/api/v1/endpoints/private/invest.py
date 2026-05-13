import io
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, or_, func
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import roles, const
from api.v1.base.base import _update, _create, _delete, _can_access_roles, Object, _get_random_string
from api.v1.base.base_files import _create_file_in_folder, _delete_file_in_folder
from api.v1.base.base_invest import _get_invest_list, _get_invest_data, _get_invest_totals_status, _get_users_invest_active_group, _get_users_invest_list_to_close_project
from api.v1.base.base_login import _get_user_login, UserCurrentLogin
from api.v1.base.base_user import _user_exist

from api.v1.deps import _get_db
from api.v1.emails import emails, emails_admin
from api.v1.models import models_invest, models_user
from config import STELLAR_NETWORK_PASSPHRASE

router = APIRouter()


#########################################################################################################
#   FUNCIONES TIPO GET
#########################################################################################################
@router.get("/list")
async def read_invest_list(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])),

        is_important: bool = False,
        is_in_white_list: bool = False,
        is_in_follow: bool = False,
        category_id: int = -1,
        status_invest: int = -1,
        page: int = Query(0, ge=0),
        limit: int = 100,
        search_text: str = ''
):
    """
    Se recupera la lista de proyectos segun sus caracteristicas
    """
    is_for_admin = False
    if current_user.role == roles.ROLE_ADMIN:
        is_for_admin = True

    return _get_invest_list(db=db, user_id=current_user.id, category_id=category_id, status=status_invest,
                            is_important=is_important, is_in_white_list=is_in_white_list, is_in_follow=is_in_follow, page=page, limit=limit, is_for_admin=is_for_admin,
                            only_invest_ids=current_user.invest_ids, search_text=search_text)


@router.get("/totals_status")
def read_get_invest_totals_status(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        category_id: int = -1
):
    """
    Devuelve los totales de proyectos por estado
    """
    return _get_invest_totals_status(db=db, category_id=category_id, only_invest_ids=current_user.invest_ids)


@router.get("/by_id/{invest_id}")
async def read_invest(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int = 0,
        get_status_description: bool = False,
        get_all_info: bool = False,
):
    """
    Devuelve todos los datos de una inversión mediante su slug
    """
    return _get_invest_data(db=db,
                            invest_id=invest_id,
                            get_status_description=get_status_description,
                            get_all_info=get_all_info,
                            only_invest_ids=current_user.invest_ids)


@router.get("/by_slug/{slug}")
async def read_invest(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_USER])),

        slug: str = '',
        get_invest_follows: bool = False,
):
    """
    Devuelve todos los datos de una inversión mediante su slug
    """
    return _get_invest_data(db=db,
                            invest_id=0,
                            slug=slug,
                            get_status_description=True,
                            get_data_media_doc=True,
                            get_preference_to_by=True,
                            user_id=current_user.id,
                            get_is_follow=get_invest_follows,
                            for_users=True,
                            get_value_to_invest=True,
                            get_all_info=True,
                            only_invest_ids=current_user.invest_ids)


@router.get("/for_select")
def read_invest_for_select(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),
):
    """
    se recuperan los proyectos de una marca blanca
    """
    q = db.query(models_invest.Invest.id, models_invest.Invest.name)
    
    list_my_invest = q.all()

    list_out = []
    for item in list_my_invest:
        aux = Object()
        aux.invest_id = item.id
        aux.name = item.name

        list_out.append(aux)

    return list_out


@router.get("/for_select/{user_id}")
def read_invest_for_select_user(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        user_id: int
):
    """
    se recuperan las inversiones de un usuario
    """
    _user_exist(db=db, user_id=user_id)

    list_my_invest = _get_users_invest_active_group(db=db, user_id=user_id)

    list_out = []
    for item in list_my_invest:
        aux = Object()
        aux.invest_id = item.id
        aux.name = item.name
        aux.num_tokens = item.num_tokens

        list_out.append(aux)

    return list_out


@router.get("/invest_white_list/{invest_id}")
def read_invest_white_list(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
):
    """
    Devuelve datos de la whitelist de la inversion
    """
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    q = db.query(models_user.UserInvestWhiteList.user_id, models_user.UserInvestWhiteList.invest_id,
                 models_user.UserInvestWhiteList.preference_to_buy, models_user.UserInvestWhiteList.date_created,
                 models_user.UserInvestWhiteList.value_to_invest, models_user.User.email)
    q = q.filter(models_user.UserInvestWhiteList.invest_id == invest_id)
    q = q.filter(models_user.UserInvestWhiteList.user_id == models_user.User.id)
    list_users_white_list = q.order_by(desc(models_user.UserInvestWhiteList.date_created)).all()

    list_out = []
    for item in list_users_white_list:
        if current_user.invest_ids:
            only_invest_ids_list = [int(i.strip()) for i in current_user.invest_ids.split(',') if i.strip().isdigit()] if current_user.invest_ids else [-1]
            if item.invest_id not in only_invest_ids_list:
                continue
        aux = Object()
        aux.invest_id = item.invest_id
        aux.user_id = item.user_id
        aux.preference_to_buy = item.preference_to_buy
        aux.date_created = item.date_created
        aux.value_to_invest = item.value_to_invest
        aux.email = item.email
        list_out.append(aux)

    # se recuperan las fases privadas que son las que entran en whitelist
    q = db.query(models_invest.InvestMintPhases)
    q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
    q = q.filter(models_invest.InvestMintPhases.is_private)
    q = q.filter(models_invest.InvestMintPhases.date_end >= datetime.today().strftime('%Y-%m-%d %H:%M'))
    list_phases = q.all()
    list_out_phases = []
    for item in list_phases:
        aux = Object()
        aux.phase = item.phase
        list_out.append(aux)

    return {'is_completed': invest_project.is_completed, 'list_users_white_list': list_out, 'list_phases': list_out_phases}


@router.get("/invest_white_list_total/{invest_id}")
def read_invest_white_list_total(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
):
    """
    el numero de usuarios en whitelist
    """
    # comprobamos que exista el invest_id
    q = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id)

    if current_user.invest_ids:
        only_invest_ids_list = [int(i.strip()) for i in current_user.invest_ids.split(',') if i.strip().isdigit()] if current_user.invest_ids else [-1]
        q = q.filter(models_invest.Invest.id.in_(only_invest_ids_list))

    invest_project = q.first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    q = db.query(models_user.UserInvestWhiteList)
    q = q.filter(models_user.UserInvestWhiteList.invest_id == invest_id)
    return q.count()


@router.get("/totals_pending_verified_and_verified/{invest_id}")
def read_invest_totals_pending_verified_and_verified(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
):
    """
    el numero de usuarios pendientes de verificar y el valor total
    """
    # comprobamos que exista el invest_id
    q = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id)

    invest_project = q.first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    q = db.query(models_user.UsersInvest.id, models_user.UsersInvest.value)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_WITHOUT_VERIFIED,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY_CARD_WITHOUT_VERIFIED))
    list_buy_without_verified = q.all()
    q = db.query(models_user.UsersInvest.parent_id, models_user.UsersInvest.value)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY)
    list_buy_verified = q.all()

    # para las verificadas
    total_invest_verified = 0
    total_balance_verified = 0
    for item_verified in list_buy_verified:
        total_balance_verified += item_verified.value
        total_invest_verified += 1

    # para las no verificadas
    total_invest_pending = 0
    total_balance_pending = 0
    for item_without_verified in list_buy_without_verified:
        found = False
        for item_verified in list_buy_verified:
            if item_verified.parent_id == item_without_verified.id:
                found = True
                break
        if not found:
            total_balance_pending += item_without_verified.value
            total_invest_pending += 1

    # TODO el total_balance_pending  y el total_balance_verified no estan bien calculados, hay que mirar las ventas etc
    return {'total_invest_pending': total_invest_pending, 'total_balance_pending': total_balance_pending, 'total_invest_verified': total_invest_verified, 'total_balance_verified': total_balance_verified}


@router.get("/investors_to_close_invest/{invest_id}")
def read_investors_to_close_invest(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int
):
    # devuelve el listado de inversores con sus tokens y su valor y mas datos para poder completar y acabar un proyecto

    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    aux = Object()
    aux.is_completed = invest_project.is_completed
    aux.list_investors = _get_users_invest_list_to_close_project(db=db, invest_id=invest_id)
    return aux


#########################################################################################################
#   FUNCIONES TIPO POST
#########################################################################################################
@router.post("/sing_up_white_list/{invest_id}")
async def sing_up_white_list(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_USER])),

        invest_id: int,
        language: str = 'en',
        value_to_invest: str = 'en',
):
    """
    para apuntarse a la whitelist de un proyecto
    """
    # comprobamos que la inversion sea de la white label
    q = db.query(models_invest.Invest)
    q = q.filter(models_invest.Invest.id == invest_id)
    
    db_invest = q.first()
    if not db_invest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # comprobamos si ya esta dado de alta
    q = db.query(models_user.UserInvestWhiteList)
    q = q.filter(models_user.UserInvestWhiteList.user_id == current_user.id)
    q = q.filter(models_user.UserInvestWhiteList.invest_id == invest_id)
    user_white_list = q.first()

    if user_white_list:
        # si existe lo borramos para actualizarlo abajo
        _delete(db=db, obj_delete=user_white_list)

    obj_to_save = Object()
    obj_to_save.user_id = current_user.id
    obj_to_save.invest_id = invest_id
    obj_to_save.value_to_invest = value_to_invest
    _create(db=db, obj_in=obj_to_save, table='users_invest_white_list')

    if not user_white_list:
        # se manda un correo al usuario para que sepa que se ha apuntado
        project_name = db_invest.name_EN
        if project_name is None or language == 'es':
            project_name = db_invest.name
        await emails.send_email_access_white_list(
            language=language,
            
            email=current_user.email,
            project_name=project_name,
            project_slug=db_invest.slug,
            value_to_invest=value_to_invest
        )
        # se manda email al admin
        await emails_admin.admin_send_email_user_whitelist(email=current_user.email,
                                                           invest_id=db_invest.id, project_name=db_invest.name, value_to_invest=value_to_invest)

    return {"ok": True}


@router.post("/close_project/{invest_id}")
async def close_project(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        invest_id: int,
):
    # comprobamos que exista el invest_id
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    # si el proyecto ya se ha cerrado error
    if invest_project.is_completed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.El proyecto ya se ha cerrado")

    # se recupera el listado de los usuarios inversores del proyecto
    list_investors = _get_users_invest_list_to_close_project(db=db, invest_id=invest_id)

    # se les crea el registro de la devolución
    try:
        # Eliminar todas las consultas pendientes
        db.expunge_all()
        actual_date = datetime.now()

        for investor in list_investors:
            # se guarda la devolucion de la inversion
            user_tokens = models_user.UsersInvest(
                
                user_id=investor.user_id,
                invest_id=invest_id,
                num_tokens=investor.num_tokens,
                price_token=int(float(investor.value) / float(investor.num_tokens)),
                value=investor.value,
                date_created=actual_date,
                type=const.USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND,
            )
            db.add(user_tokens)
            db.flush()

        # se actualiza el proyecto con el cierre
        invest_project.is_draft = 0
        invest_project.is_completed = 1
        db.add(invest_project)

        # se guarda en base de datos
        db.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="server.Se ha producido un error inesperado")

    # se les manda un correo
    for investor in list_investors:
        # se manda un correo al usuario para que sepa que se ha apuntado
        project_name = invest_project.name_EN
        if project_name is None or investor.language == 'es':
            project_name = invest_project.name
        await emails.send_email_project_completed(
            language=investor.language,
            
            email=investor.email,
            project_name=project_name,
            project_slug=invest_project.slug
        )

    return {"ok": True}


@router.post("")
def create_invest(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        is_draft: bool = Form(1),
        category_id: int = Form(None),
        name: str = Form(..., max_length=200),
        name_EN: str = Form(None, max_length=200),
        token_abbreviation: str = Form(None, max_length=10),

        time_limit: str = Form(None, max_length=50),  # plazo de finalizacion del proyecto en texto
        time_limit_EN: str = Form(None, max_length=50),  # plazo de finalizacion del proyecto en texto

        title: str = Form(..., max_length=500),
        title_EN: str = Form(None, max_length=500),
        summary: str = Form(...),
        summary_EN: str = Form(None),
        description: str = Form(...),
        description_EN: str = Form(None),
        proposal_to_investors: str = Form(None),
        proposal_to_investors_EN: str = Form(None),

        profit_estimated: float = Form(0),
        profit_estimated_description: str = Form(None),
        risk: int = Form(1, ge=1, le=6),  # del 1 al 6
        web: str = Form(None, max_length=200),
        is_important: bool = Form(0),

        hide_time_data: bool = Form(0),
        hide_date_start_round: bool = Form(0),
        hide_date_end_round: bool = Form(0),
        hide_profit_estimated: bool = Form(0),
        hide_risk: bool = Form(0),
        hide_value_round: bool = Form(0),
        hide_num_tokens: bool = Form(0),

        success_fee: float = Form(0),
        management_fee: float = Form(0),
        opening_commission: float = Form(0),
        closing_commission: float = Form(0),
        spread: float = Form(0),
        entry_fee: float = Form(0),
        annual_fee: float = Form(0),

        location: str = Form(None, max_length=300),
        location_gps_lat: str = Form(None, max_length=20),
        location_gps_lon: str = Form(None, max_length=20),

        file: UploadFile = File(...),
        file_top: UploadFile = File(...),
):
    slug = _get_random_string(f"invest_{name}")

    obj_to_save = Object()
    obj_to_save.slug = slug
    obj_to_save.is_draft = is_draft
    obj_to_save.category_id = category_id
    obj_to_save.name = name
    obj_to_save.name_EN = name_EN
    obj_to_save.token_abbreviation = token_abbreviation

    obj_to_save.time_limit = time_limit
    obj_to_save.time_limit_EN = time_limit_EN

    obj_to_save.title = title
    obj_to_save.title_EN = title_EN
    obj_to_save.summary = summary
    obj_to_save.summary_EN = summary_EN
    obj_to_save.description = description
    obj_to_save.description_EN = description_EN
    obj_to_save.proposal_to_investors = proposal_to_investors
    obj_to_save.proposal_to_investors_EN = proposal_to_investors_EN

    obj_to_save.profit_estimated = profit_estimated
    obj_to_save.profit_estimated_description = profit_estimated_description
    obj_to_save.risk = risk
    obj_to_save.web = web
    obj_to_save.is_important = is_important
    obj_to_save.location = location
    obj_to_save.location_gps_lat = location_gps_lat
    obj_to_save.location_gps_lon = location_gps_lon

    obj_to_save.hide_time_data = hide_time_data
    obj_to_save.hide_date_start_round = hide_date_start_round
    obj_to_save.hide_date_end_round = hide_date_end_round
    obj_to_save.hide_profit_estimated = hide_profit_estimated
    obj_to_save.hide_risk = hide_risk
    obj_to_save.hide_value_round = hide_value_round
    obj_to_save.hide_num_tokens = hide_num_tokens

    obj_to_save.success_fee = success_fee
    obj_to_save.management_fee = management_fee
    obj_to_save.opening_commission = opening_commission
    obj_to_save.closing_commission = closing_commission
    obj_to_save.spread = spread
    obj_to_save.entry_fee = entry_fee
    obj_to_save.annual_fee = annual_fee

    obj_to_save.blockchain_network = "stellar"


    # los ficheros
    my_folder = f"upload_files/earastellar/invest_project/{slug}"
    # se crea la imagen el la carpeta del servidor
    file_name = _create_file_in_folder(uploaded_file=file, my_folder=my_folder, valid_file_type='image', name='file')
    obj_to_save.file = f'{my_folder}/{file_name}'
    # se crea la imagen el la carpeta del servidor
    file_name = _create_file_in_folder(uploaded_file=file_top, my_folder=my_folder, valid_file_type='image', name='file_top')
    obj_to_save.file_top = f'{my_folder}/{file_name}'

    invest = _create(db=db, obj_in=obj_to_save, table='invest')

    return {"invest_id": invest.id}


#########################################################################################################
#   FUNCIONES TIPO PUT
#########################################################################################################
@router.put("/{invest_id}")
def update_invest(
        *,
        db: Session = Depends(_get_db),
        current_user: UserCurrentLogin = Depends(_get_user_login),
        access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),

        is_draft: bool = Form(1),
        category_id: int = Form(None),
        # 0->pendiente 1->fase de pre lanzamiento 2->fase de financiacion 3->en curso 99->proyecto acabado 100->proyecto eliminado
        name: str = Form(..., max_length=200),
        name_EN: str = Form(None, max_length=200),
        token_abbreviation: str = Form(None, max_length=10),

        time_limit: str = Form(None, max_length=50),  # plazo de finalizacion del proyecto en texto
        time_limit_EN: str = Form(None, max_length=50),  # plazo de finalizacion del proyecto en texto

        title: str = Form(..., max_length=500),
        title_EN: str = Form(None, max_length=500),
        summary: str = Form(...),
        summary_EN: str = Form(None),
        description: str = Form(...),
        description_EN: str = Form(None),
        proposal_to_investors: str = Form(None),
        proposal_to_investors_EN: str = Form(None),

        profit_estimated: float = Form(0),  # porcentaje de rentabilidad estimada, sacar de esto el de anualizada
        profit_estimated_description: str = Form(None),
        risk: int = Form(1, ge=1, le=6),  # del 1 al 6
        web: str = Form(None, max_length=200),
        is_important: bool = Form(0),

        hide_time_data: bool = Form(0),
        hide_date_start_round: bool = Form(0),
        hide_date_end_round: bool = Form(0),
        hide_profit_estimated: bool = Form(0),
        hide_risk: bool = Form(0),
        hide_value_round: bool = Form(0),
        hide_num_tokens: bool = Form(0),

        location: str = Form(None, max_length=300),
        location_gps_lat: str = Form(None, max_length=20),
        location_gps_lon: str = Form(None, max_length=20),

        success_fee: float = Form(0),
        management_fee: float = Form(0),
        opening_commission: float = Form(0),
        closing_commission: float = Form(0),
        spread: float = Form(0),
        entry_fee: float = Form(0),
        annual_fee: float = Form(0),

        file: UploadFile = File(None),
        file_top: UploadFile = File(None),

        invest_id: int,
):
    invest_project = db.query(models_invest.Invest).filter(models_invest.Invest.id == invest_id).first()
    if not invest_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.Invest not found")

    obj_to_save = Object()
    obj_to_save.category_id = category_id
    obj_to_save.name = name
    obj_to_save.name_EN = name_EN
    obj_to_save.token_abbreviation = token_abbreviation
    obj_to_save.is_draft = is_draft

    obj_to_save.time_limit = time_limit
    obj_to_save.time_limit_EN = time_limit_EN

    obj_to_save.title = title
    obj_to_save.title_EN = title_EN
    obj_to_save.summary = summary
    obj_to_save.summary_EN = summary_EN
    obj_to_save.description = description
    obj_to_save.description_EN = description_EN
    obj_to_save.proposal_to_investors = proposal_to_investors
    obj_to_save.proposal_to_investors_EN = proposal_to_investors_EN

    obj_to_save.profit_estimated = profit_estimated
    obj_to_save.profit_estimated_description = profit_estimated_description
    obj_to_save.risk = risk
    obj_to_save.web = web
    obj_to_save.is_important = is_important
    obj_to_save.location = location
    obj_to_save.location_gps_lat = location_gps_lat
    obj_to_save.location_gps_lon = location_gps_lon

    obj_to_save.hide_time_data = hide_time_data
    obj_to_save.hide_date_start_round = hide_date_start_round
    obj_to_save.hide_date_end_round = hide_date_end_round
    obj_to_save.hide_profit_estimated = hide_profit_estimated
    obj_to_save.hide_risk = hide_risk
    obj_to_save.hide_value_round = hide_value_round
    obj_to_save.hide_num_tokens = hide_num_tokens

    obj_to_save.success_fee = success_fee
    obj_to_save.management_fee = management_fee
    obj_to_save.opening_commission = opening_commission
    obj_to_save.closing_commission = closing_commission
    obj_to_save.spread = spread
    obj_to_save.entry_fee = entry_fee
    obj_to_save.annual_fee = annual_fee

    my_folder = f"upload_files/earastellar/invest_project/{invest_project.slug}"
    # si existen los ficheros
    if file is not None:
        # se borra la imagen anterior de la carpeta del servidor
        _delete_file_in_folder(invest_project.file)
        # se crea la imagen el la carpeta del servidor
        file_name = _create_file_in_folder(uploaded_file=file, my_folder=my_folder, valid_file_type='image', name='file')
        obj_to_save.file = f'{my_folder}/{file_name}'

    if file_top is not None:
        # se borra la imagen anterior de la carpeta del servidor
        _delete_file_in_folder(invest_project.file_top)
        # se crea la imagen el la carpeta del servidor
        file_name = _create_file_in_folder(uploaded_file=file_top, my_folder=my_folder, valid_file_type='image', name='file_top')
        obj_to_save.file_top = f'{my_folder}/{file_name}'

    _update(db, db_obj=invest_project, obj_in=obj_to_save)

    return {"ok": True}


