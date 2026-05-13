import base64
import io
import json
import logging
import secrets
import shutil
import tempfile
import uuid  # Add this import at the top with the other imports
from datetime import datetime
from io import BytesIO
from typing import Dict, Any

import pandas as pd
from fastapi import APIRouter, Depends, Form, UploadFile, File, Query
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pdf2image import convert_from_path
from sqlalchemy import desc, or_, asc, case, func, and_
from sqlalchemy.orm import Session, aliased
from starlette import status

import config
from api.v1 import roles, const
from api.v1.base.base import _update, _create, _can_access_roles, Object, _delete
from api.v1.base.base_files import _save_upload_files_user, _create_file_in_folder
from api.v1.base.base_login import (
    _get_user_login,
    UserCurrentLogin,
    pwd_context,
    _get_password_hash,
)
from api.v1.base.base_user import (
    _update_user,
    _get_user_by_id,
    _user_exist,
    _get_user_data_all,
    _mark_kyc_to_review,
)

from api.v1.deps import _get_db
from api.v1.emails import emails, emails_admin
from api.v1.models import models_user, models_invest

router = APIRouter()


#########################################################################################################
#   FUNCIONES TIPO GET
#########################################################################################################
@router.get("/user")
def read_user(
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
    user_id: int = 0,
):
    """
    Devuelve los datos personales del usuario
    """
    if current_user.role == roles.ROLE_USER:
        user_id = current_user.id

    return _get_user_data_all(
        db=db,
        
        user_id=user_id,
    )


@router.get("/list/paginated")
def read_users_paginated(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN])
    ),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=10),
    find: str = "",
    valid_kyc: int = -1,
):
    """
    Se recuperan los usuarios de la marca blanca de forma paginada
    """
    skip = (page - 1) * per_page
    limit = per_page

    q = db.query(
        models_user.User.id,
        models_user.User.email,
        models_user.User.is_active,
        models_user.User.kyc_valid,
        models_user.User.date_created,
    )

    # filtros de busqueda
    if find != "":
        q = q.filter(
            or_(
                models_user.User.email.contains(find),
                models_user.User.description.contains(find),
            )
        )

    if valid_kyc != -1:
        q = q.filter(models_user.User.kyc_valid == valid_kyc)

    # recuperamos el numero total de usuarios
    total = q.count()

    # recuperamos unos pocos usuarios
    list_items = (
        q.order_by(desc(models_user.User.date_created))
        .offset(skip)
        .limit(limit)
        .distinct()
        .all()
    )

    list_out = []
    num_users_kyc_without_start = 0
    num_users_kyc_valid = 0
    num_users_kyc_pending_validation = 0
    num_users_refused = 0

    for item in list_items:
        aux = Object()
        aux.id = item.id
        aux.email = item.email
        aux.kyc_valid = item.kyc_valid
        aux.is_active = item.is_active
        aux.date_created = item.date_created
        # se recalculan los totales
        if item.kyc_valid == 0:
            num_users_kyc_without_start = num_users_kyc_without_start + 1
        elif item.kyc_valid == 1:
            num_users_kyc_valid = num_users_kyc_valid + 1
        elif item.kyc_valid == 2:
            num_users_kyc_pending_validation = num_users_kyc_pending_validation + 1
        elif item.kyc_valid == 3:
            num_users_refused = num_users_refused + 1

        list_out.append(aux)

    return {"list": list_out, "total": total}


@router.get("/for_select")
def read_users_for_select(
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN])
    ),
):
    """
    se recuperan los usuarios de la marca blanca
    """
    # se recuperan los usuarios de la marca blanca
    q = db.query(
        models_user.User.id,
        models_user.User.email,
        models_user.UserDataPhysicalPerson.name,
        models_user.UserDataPhysicalPerson.surname,
    )
    q = q.filter(models_user.User.is_active == 1)

    q = q.outerjoin(
        models_user.UserDataPhysicalPerson,
        models_user.User.id == models_user.UserDataPhysicalPerson.user_id,
    )
    list_items = q.order_by(asc(models_user.User.email)).distinct().all()

    list_items_out = []
    for item in list_items:
        aux = Object()
        aux.id = item.id
        aux.email = item.email
        aux.name = item.name
        aux.surname = item.surname
        list_items_out.append(aux)
    return list_items_out



@router.get("/numbers_kyc")
def read_numbers_kyc(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN])
    ),
):
    """
    Se recuperan los numeros de usuarios de kyc validados, pendientes, etc
    """
    q = db.query(models_user.User.id)

    # recuperamos el numero de usuarios
    num_users_kyc_without_start = (
        q.filter(models_user.User.kyc_valid == 0).distinct().count()
    )
    num_users_kyc_valid = q.filter(models_user.User.kyc_valid == 1).distinct().count()
    num_users_kyc_pending_validation = (
        q.filter(models_user.User.kyc_valid == 2).distinct().count()
    )
    num_users_refused = q.filter(models_user.User.kyc_valid == 3).distinct().count()

    return {
        "num_users_kyc_without_start": num_users_kyc_without_start,
        "num_users_kyc_valid": num_users_kyc_valid,
        "num_users_kyc_pending_validation": num_users_kyc_pending_validation,
        "num_users_refused": num_users_refused,
    }


@router.get("/kyc_valid")
def read_user_me_kyc_valid(
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_USER])),
):
    """
    Devuelve los datos del kyc del usuario para saber si es válido o no y sus razones
    """
    if current_user.kyc_valid != 1:
        db_user = _get_user_by_id(
            db=db,
            
            user_id=current_user.id,
        )
        data = {
            "kyc_valid": db_user.kyc_valid,
            "kyc_no_valid_reason": db_user.kyc_no_valid_reason,
            "kyc_no_valid_reason_EN": db_user.kyc_no_valid_reason_EN,
        }
    else:
        data = {"kyc_valid": 1}

    return data



@router.get("/my_iban_number_and_wallet")
def my_iban_number_and_wallet(
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_USER])),
):
    """
    Recupera el dato de la cuenta bancaria
    """

    result = {"iban": "", "wallet_address": ""}

    user_bank = (
        db.query(models_user.UserBankAccount)
        .filter(models_user.UserBankAccount.user_id == current_user.id)
        .first()
    )
    if user_bank:
        result["iban"] = user_bank.iban
        # se recupera si hay wallet puesta
    wallet_address = _get_user_by_id(
        db=db,
        user_id=current_user.id,
        
    ).wallet_address
    if wallet_address:
        result["wallet_address"] = wallet_address
    return result


@router.get("/documents_others")
def read_user_me_documents_others(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
    user_id: int = 0,
):
    """
    Recupera los documentos del usuario de la tabla users_documents_others
    """
    if current_user.role == roles.ROLE_ADMIN:
        _user_exist(
            db=db,
            user_id=user_id,
            
        )
    elif current_user.role == roles.ROLE_USER:
        user_id = current_user.id

    db_documents = (
        db.query(models_user.UserDocumentsOthers)
        .filter(models_user.UserDocumentsOthers.user_id == user_id)
        .all()
    )
    if db_documents:
        try:
            for item in db_documents:
                with open(f"private/{item.file}", "rb") as image_file:
                    item.file = base64.b64encode(image_file.read())
        except FileNotFoundError:
            pass

    list_documents = []
    for item in db_documents:
        obj = Object()
        obj.id = item.id
        obj.user_id = item.user_id
        obj.file = item.file
        obj.file_type = item.file_type
        obj.document_type = item.document_type
        obj.description = item.description
        list_documents.append(obj)

    return list_documents



#########################################################################################################
#   FUNCIONES TIPO POST
#########################################################################################################
@router.post("/get_image_from_pdf")
def get_image_from_pdf(
    *,
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
    proof_bank_pdf: UploadFile = File(...),
):
    """
    transforma un pdf en una imagen y se lo devuelve
    """
    destination = tempfile.NamedTemporaryFile()
    with open(destination.name, "wb") as buffer:
        shutil.copyfileobj(proof_bank_pdf.file, buffer)

    output_file = tempfile.TemporaryDirectory()
    output_path = output_file.name
    image = convert_from_path(
        destination.name,
        200,
        output_folder=output_path,
        fmt="jpg",
        first_page=1,
        last_page=1,
    )
    destination.close()
    buffered = BytesIO()
    image[0].save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue())


@router.post("/documents_others/{user_id}")
def create_invest_documents_others(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),
    user_id: int,
    file: UploadFile = File(...),
    description: str = Form(None, max_length=200),
):
    _user_exist(
        db=db,
        user_id=user_id,
        
    )

    # se crea la imagen el la carpeta del servidor
    my_folder = f"upload_files/earastellar/users/{user_id}"
    file_name = _create_file_in_folder(
        uploaded_file=file,
        my_folder=my_folder,
        valid_file_type="document",
        name="document",
        is_private=True,
    )
    file_name = f"{my_folder}/{file_name}"

    obj = Object()
    obj.document_type = "document"
    obj.user_id = user_id
    obj.file = file_name
    obj.description = description

    return _create(db=db, obj_in=obj, table="users_documents_others")


@router.post("")
def create_user(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),
    email: str = Form(..., max_length=100),
    password: str = Form(..., min_length=8, max_length=50),
    language: str = Form("es"),  # idioma para el mensaje de email
    name: str = Form(None, max_length=100),
    surname: str = Form(None, max_length=100),
    dni: str = Form(None, max_length=20),
    phone: str = Form(None, max_length=100),
    address: str = Form(None, max_length=200),
    city: str = Form(None, max_length=100),
    province: str = Form(None, max_length=100),
    nationality: str = Form(None, max_length=5),
    country: str = Form(None, max_length=5),
    postal_code: str = Form(None, max_length=10),
    occupation: str = Form(None, max_length=100),
    politically_exposed: bool = Form(0),
    user_type: int = Form(None, me=0, le=1),
    civil_status: int = Form(None, me=0, le=3),
    date_birthday: datetime = Form(None),
    economic_matrimonial_regime: int = Form(None, me=0, le=2),
    company_name: str = Form(None, max_length=200),
    activity: str = Form(None, max_length=100),
    holders: str = Form(None, max_length=1),
    register_number: str = Form(None, max_length=100),
    nif: str = Form(None, max_length=100),
    legal_form: int = Form(None),
    company_address: str = Form(None, max_length=200),
    company_city: str = Form(None, max_length=100),
    company_province: str = Form(None, max_length=100),
    company_country: str = Form(None, max_length=5),
    company_postal_code: str = Form(None, max_length=10),
    is_representative_owner: bool = Form(0),
):
    """
    El admin crea un usuario
    """
    # error si el email existe
    db_user = (
        db.query(models_user.User)
        .filter(models_user.User.email == email)
        .first()
    )
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="server.Email already registered",
        )

    # el usuario no existe, lo creamos
    obj_in = Object()
    obj_in.email = email
    obj_in.hashed_password = _get_password_hash(password)
    obj_in.is_active = 1
    obj_in.language = language
    obj_in.user_type = user_type
    obj_in.kyc_valid = 1
    db_user = _create(db=db, obj_in=obj_in, table="users")

    _update_user(
        db=db,
        db_user=db_user,
        name=name,
        surname=surname,
        dni=dni,
        phone=phone,
        address=address,
        city=city,
        province=province,
        nationality=nationality,
        country=country,
        postal_code=postal_code,
        occupation=occupation,
        politically_exposed=politically_exposed,
        user_type=user_type,
        civil_status=civil_status,
        date_birthday=date_birthday,
        economic_matrimonial_regime=economic_matrimonial_regime,
        company_name=company_name,
        activity=activity,
        holders=holders,
        register_number=register_number,
        nif=nif,
        legal_form=legal_form,
        company_address=company_address,
        company_city=company_city,
        company_province=company_province,
        company_country=company_country,
        company_postal_code=company_postal_code,
        is_representative_owner=is_representative_owner,
    )

    # actualizamos el dato de kyc_valid porque en el update se modifica a 2
    obj_in = Object()
    obj_in.id = db_user.id
    obj_in.kyc_valid = 0

    _update(db, db_obj=db_user, obj_in=obj_in)

    return {"ok": True}


#########################################################################################################
#   FUNCIONES TIPO PUT
#########################################################################################################
@router.put("/update_password")
def update_user_password(
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
    user_id: int = 0,
    old_password: str = Form(None),
    new_password: str = Form(..., min_length=8, max_length=50),
):
    """
    Se actualiza el password del usuario
    """
    if current_user.role == roles.ROLE_USER:
        user_id = current_user.id

    db_user = db.query(models_user.User).filter(models_user.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # se comprueba si el password antiguo esta bien
    if current_user.role == roles.ROLE_USER:
        if not pwd_context.verify(
            old_password, db_user.hashed_password
        ) and not pwd_context.verify(old_password, db_user.change_hashed_password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Old password is different",
            )

    try:
        db_user.hashed_password = pwd_context.hash(new_password)
        db_user.change_hashed_password = None
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {"ok": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="server.Se ha producido un error inesperado",
        )


@router.put("/update_is_active/{user_id}/{is_active}")
async def update_is_active(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),
    user_id: int,
    is_active: bool,
):
    """
    Se actualiza el estado del usuario, si es activo o no
    """
    q = db.query(models_user.User)
    q = q.filter(models_user.User.id == user_id)
    db_user = q.first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="server.User not found"
        )

    obj_in = Object()
    obj_in.id = user_id
    obj_in.is_active = is_active
    _update(db, db_obj=db_user, obj_in=obj_in)

    return {"ok": True}


@router.put("/update_kyc_status/{user_id}")
async def update_kyc_status(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),
    user_id: int,
    type_validate: int = Form(
        ..., ge=0, le=3
    ),  # 0->no se ha modificado 1->válido 2->a revisar por admin 3->inválido
    kyc_no_valid_reason: str = Form(None, max_length=1000),
    kyc_no_valid_reason_EN: str = Form(None, max_length=1000),
):
    """
    Se actualiza el kyc del usuario
    """
    db_user = _get_user_by_id(
        db=db,
        user_id=user_id,
        
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="server.User not found"
        )

    obj_in = Object()
    obj_in.id = user_id
    obj_in.kyc_valid = type_validate
    obj_in.kyc_no_valid_reason = kyc_no_valid_reason
    obj_in.kyc_no_valid_reason_EN = kyc_no_valid_reason_EN
    _update(db, db_obj=db_user, obj_in=obj_in)

    # Si se aprueba el KYC para EARASTELLAR, registrar la wallet como trusted issuer en el contrato
    if (type_validate == 1):
        if (
            db_user.wallet_address
            and config.COMPLIANT_ID_CONTRACT_ID
            and config.STELLAR_ADMIN_SECRET_KEY
        ):
            try:
                from blockchain.stellar.stellar_utils import add_trusted_issuer

                add_trusted_issuer(
                    admin_secret_key=config.STELLAR_ADMIN_SECRET_KEY,
                    contract_id=config.COMPLIANT_ID_CONTRACT_ID,
                    issuer_public_key=db_user.wallet_address,
                )
                logging.info(
                    f"Trusted issuer added on-chain for user {user_id} (wallet {db_user.wallet_address})"
                )
            except Exception as e:
                logging.error(
                    f"Failed to add trusted issuer on-chain for user {user_id}: {e}"
                )

    if type_validate == 1:
        await emails.send_email_kyc_ok(
            db_user.language, db_user.email
        )
    elif type_validate == 3:
        await emails.send_email_kyc_ko(
            db_user.language, db_user.email
        )

    return {"ok": True}


@router.put("/upload_file_profile")
def upload_file_profile(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
    user_id: int = None,
    file: UploadFile = File(...),
    file_type: int = Form(
        ..., ge=0, le=62
    ),  # 0->file profile 1->file top 2->dni back 3->dni front 4->selfie
):
    """
    Se guarda las imagenes de perfil del usuario
    """
    if current_user.role == roles.ROLE_ADMIN:
        _user_exist(
            db=db,
            user_id=user_id,
            
        )
    elif current_user.role == roles.ROLE_USER:
        user_id = current_user.id

    _save_upload_files_user(
        db=db,
        
        user_id=user_id,
        file=file,
        file_type=file_type,
    )


@router.put("/wallet/{user_id}")
async def put_wallet(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
    user_id: int = None,
    wallet: str = Form(None),
):
    """
    Se actualiza la información bancaria del usuario
    """
    if current_user.role == roles.ROLE_ADMIN:
        _user_exist(
            db=db,
            user_id=user_id,
            
        )
    elif current_user.role == roles.ROLE_USER:
        user_id = current_user.id

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="server.Wallet is required"
        )

    db_user = _get_user_by_id(
        db=db,
        user_id=user_id,
        
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="server.User not found"
        )

    db_user.wallet_address = wallet
    db.add(db_user)

    db.commit()
    db.refresh(db_user)

    return {"ok": True}


@router.put("/{user_id}")
def update_user(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
    user_id: int,
    name: str = Form(None, max_length=100),
    surname: str = Form(None, max_length=100),
    dni: str = Form(None, max_length=20),
    phone: str = Form(None, max_length=100),
    address: str = Form(None, max_length=200),
    city: str = Form(None, max_length=100),
    province: str = Form(None, max_length=100),
    nationality: str = Form(None, max_length=5),
    country: str = Form(None, max_length=5),
    postal_code: str = Form(None, max_length=10),
    occupation: str = Form(None, max_length=100),
    politically_exposed: bool = Form(0),
    user_type: int = Form(None, me=0, le=1),
    civil_status: int = Form(None, me=0, le=3),
    date_birthday: datetime = Form(None),
    economic_matrimonial_regime: int = Form(None, me=0, le=2),
    company_name: str = Form(None, max_length=200),
    activity: str = Form(None, max_length=100),
    holders: str = Form(None, max_length=1),
    register_number: str = Form(None, max_length=100),
    nif: str = Form(None, max_length=100),
    legal_form: int = Form(None),
    company_address: str = Form(None, max_length=200),
    company_city: str = Form(None, max_length=100),
    company_province: str = Form(None, max_length=100),
    company_country: str = Form(None, max_length=5),
    company_postal_code: str = Form(None, max_length=10),
    is_representative_owner: bool = Form(0),
):
    """
    se actualizan los datos del usuario
    """
    if current_user.role == roles.ROLE_USER:
        user_id = current_user.id
        # son datos del kyc, si el kyc ya es valido no se pueden modificar
        if current_user.kyc_valid == 1:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="server.The user does have a valid kyc",
            )

    db_user = _get_user_by_id(
        db=db,
        user_id=user_id,
        
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="server.User not found"
        )

    _update_user(
        db=db,
        db_user=db_user,
        name=name,
        surname=surname,
        dni=dni,
        phone=phone,
        address=address,
        city=city,
        province=province,
        nationality=nationality,
        country=country,
        postal_code=postal_code,
        occupation=occupation,
        politically_exposed=politically_exposed,
        user_type=user_type,
        civil_status=civil_status,
        date_birthday=date_birthday,
        economic_matrimonial_regime=economic_matrimonial_regime,
        company_name=company_name,
        activity=activity,
        holders=holders,
        register_number=register_number,
        nif=nif,
        legal_form=legal_form,
        company_address=company_address,
        company_city=company_city,
        company_province=company_province,
        company_country=company_country,
        company_postal_code=company_postal_code,
        is_representative_owner=is_representative_owner,
    )

    return {"ok": True}


#########################################################################################################
#   FUNCIONES TIPO DELETE
#########################################################################################################
@router.delete("/documents_others/{user_id}/{documents_id}")
def delete_documents_others(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(_can_access_roles(roles_can_access=[roles.ROLE_ADMIN])),
    user_id: int,
    documents_id: int,
):
    """
    Elimina el documento de un usuario
    """
    _user_exist(
        db=db,
        user_id=user_id,
        
    )

    item_db = (
        db.query(models_user.UserDocumentsOthers)
        .filter(models_user.UserDocumentsOthers.id == documents_id)
        .first()
    )
    if not item_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="server.user document not found",
        )

    if _delete(db, obj_delete=item_db, route_file=f"private/{item_db.file}"):
        return {"ok": True}
    return {"ok": False}


@router.put("/upload_kyc_images/{user_id}")
def upload_kyc_images(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
    user_id: int = 0,
    files: str = Form(...),  # 📌 Recibir como string porque viene en FormData
):
    """
    Se guarda las imagenes del kyc, dni, etc
    """
    if current_user.role == roles.ROLE_ADMIN:
        _user_exist(
            db=db,
            user_id=user_id,
        )
    elif current_user.role == roles.ROLE_USER:
        user_id = current_user.id

    files_dict: Dict[str, str] = json.loads(
        files
    )  # Convertir string JSON a diccionario
    _save_upload_files_user(
        db=db,
        user_id=user_id,
        files=files_dict,
    )

    q = db.query(models_user.User)
    q = q.filter(models_user.User.id == user_id)
    user_db = q.first()
    _mark_kyc_to_review(
        db=db,
        user_id=user_db.id,
        user_kyc_valid=2,
    )
