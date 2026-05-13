import base64
from fastapi import HTTPException
from sqlalchemy import asc, literal_column, func, or_, desc
from sqlalchemy.orm import Session
from io import BytesIO
from typing import Any
from datetime import datetime
from starlette import status
from pdf2image import convert_from_path

from api.v1.base.base import _update, _create, Object

from api.v1.models import models_user


def _get_user_by_id(
        db: Session,
        
        user_id: int
):
    q = db.query(models_user.User)
    q = q.filter(models_user.User.id == user_id)

    q = q.filter(models_user.User.is_active)
    return q.first()


def _user_exist(
        db: Session,
        
        user_id: int
):
    q = db.query(models_user.User.id, models_user.User.email, models_user.User.user_type)
    q = q.filter(models_user.User.id == user_id)
    
    q = q.filter(models_user.User.is_active)
    db_user = q.first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.User not found")
    return db_user


def _get_user_data_all(
        db: Session,
        
        user_id: int = 0
):
    """
    Devuelve todos los datos personales de un usuario
    """
    q = db.query(models_user.User).filter(models_user.User.id == user_id)
    
    current_user = q.first()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="server.User not found")

    # datos de persona fisica
    current_users_data_physical_person = db.query(models_user.UserDataPhysicalPerson).filter(models_user.UserDataPhysicalPerson.user_id == current_user.id).first()

    current_user.hashed_password = None
    current_user.change_hashed_password = None

    if current_users_data_physical_person:
        current_user.name = current_users_data_physical_person.name
        current_user.surname = current_users_data_physical_person.surname
        current_user.dni = current_users_data_physical_person.dni
        current_user.date_birthday = current_users_data_physical_person.date_birthday
        current_user.phone = current_users_data_physical_person.phone
        current_user.address = current_users_data_physical_person.address
        current_user.city = current_users_data_physical_person.city
        current_user.province = current_users_data_physical_person.province
        current_user.country = current_users_data_physical_person.country
        current_user.postal_code = current_users_data_physical_person.postal_code
        current_user.nationality = current_users_data_physical_person.nationality
        current_user.occupation = current_users_data_physical_person.occupation
        current_user.civil_status = current_users_data_physical_person.civil_status
        current_user.economic_matrimonial_regime = current_users_data_physical_person.economic_matrimonial_regime
        current_user.politically_exposed = current_users_data_physical_person.politically_exposed

    # datos de la persona juridica empresa
    if current_user.user_type == 1:
        users_data_legal_person = db.query(models_user.UserDataLegalPerson).filter(models_user.UserDataLegalPerson.user_id == current_user.id).first()
        if users_data_legal_person:
            current_user.company_name = users_data_legal_person.company_name
            current_user.activity = users_data_legal_person.activity
            current_user.holders = users_data_legal_person.holders
            current_user.register_number = users_data_legal_person.register_number
            current_user.nif = users_data_legal_person.nif
            current_user.legal_form = users_data_legal_person.legal_form
            current_user.company_address = users_data_legal_person.company_address
            current_user.company_city = users_data_legal_person.company_city
            current_user.company_province = users_data_legal_person.company_province
            current_user.company_country = users_data_legal_person.company_country
            current_user.company_postal_code = users_data_legal_person.company_postal_code
            current_user.is_representative_owner = users_data_legal_person.is_representative_owner

    bank_account = db.query(models_user.UserBankAccount).filter(models_user.UserBankAccount.user_id == current_user.id).first()

    if bank_account:
        current_user.iban = bank_account.iban
        current_user.bic = bank_account.bic
        current_user.bank_status = bank_account.status
        current_user.bank_account_type = bank_account.bank_account_type
        current_user.bank_country = bank_account.bank_country
        current_user.bank_name = bank_account.bank_name
        current_user.bank_short_code = bank_account.bank_short_code
        current_user.bank_street = bank_account.bank_street
        current_user.bank_cp = bank_account.bank_cp
        current_user.bank_city = bank_account.bank_city
        current_user.bank_kyc_no_valid_reason = bank_account.kyc_no_valid_reason
        current_user.bank_kyc_no_valid_reason_EN = bank_account.kyc_no_valid_reason_EN

    # si el kyc no es valido traemos los dos si ya es valido ya no hace falta
    current_user.list_documents = []
    if current_user.kyc_valid != 1:
        # estas imagenes estan en la carpeta privada por lo que se pasan en base64
        db_documents = db.query(models_user.UserDataDocuments).filter(models_user.UserDataDocuments.user_id == current_user.id).all()

        for doc in db_documents:
            try:
                file_path = f"private/{doc.file}"
                if doc.document_type == "pdf":
                    output_path = "/".join(file_path.split("/")[:-1])
                    output_file = f'{file_path.split("/")[-1]}.jpg'
                    image = convert_from_path(file_path, 200, output_folder=output_path, output_file=output_file, fmt="jpg", first_page=1, last_page=1)
                    buffered = BytesIO()
                    image[0].save(buffered, format="JPEG")
                    doc.file = base64.b64encode(buffered.getvalue())
                else:
                    with open(file_path, "rb") as image_file:
                        doc.file = base64.b64encode(image_file.read())

            except Exception:
                pass

        current_user.list_documents = db_documents

    return current_user


def _get_profit_percentage_invest_user(
        db: Session,
        invest_id: int,
        user_id: int
):
    # devuelve el valor del porcentaje puesto por el usuario para esta inversion
    q = db.query(models_user.UsersInvestProfitPercentage)
    q = q.filter(models_user.UsersInvestProfitPercentage.invest_id == invest_id)
    q = q.filter(models_user.UsersInvestProfitPercentage.user_id == user_id)
    value = q.first()
    if value:
        return value.profit_percentage
    else:
        return 0


def _mark_kyc_to_review(
        db: Session,
        
        user_id: int,
        user_kyc_valid: int,
        force: bool = False
):
    # se marca el kyc para revisar
    if not force and user_kyc_valid == 0:
        return

    q = db.query(models_user.User)
    q = q.filter(models_user.User.id == user_id)
    user_db = q.first()

    obj_in = Object()
    obj_in.kyc_valid = 2  # al modificar marcamos como KYC a revisar
    _update(db, db_obj=user_db, obj_in=obj_in)


def _update_user(
        db: Session,
        db_user: Any,

        name: str = None,
        surname: str = None,
        dni: str = None,
        phone: str = None,
        address: str = None,
        city: str = None,
        province: str = None,
        nationality: str = None,
        country: str = None,
        postal_code: str = None,
        occupation: str = None,
        politically_exposed: bool = False,
        user_type: int = None,
        civil_status: int = None,
        date_birthday: datetime = None,
        economic_matrimonial_regime: int = None,

        company_name: str = None,
        activity: str = None,
        holders: str = None,
        register_number: str = None,
        nif: str = None,
        legal_form: int = None,
        company_address: str = None,
        company_city: str = None,
        company_province: str = None,
        company_country: str = None,
        company_postal_code: str = None,
        is_representative_owner: bool = False,

):
    # actualizamos el usuario con el tipo de usuario que es de la tabla users

    # miramos para actualizar el kyc a revision o no
    _mark_kyc_to_review(db=db, user_id=db_user.id, user_kyc_valid=db_user.kyc_valid)

    # si es usuario fisico o empresa
    if user_type is not None:
        # se actualiza la tabla users con el user_type
        obj_in = Object()
        obj_in.user_type = user_type
        _update(db, db_obj=db_user, obj_in=obj_in)

        # se actualiza la tabla users_data_physical_person
        obj_in = Object()
        obj_in.user_id = db_user.id
        obj_in.name = name
        obj_in.surname = surname
        obj_in.phone = phone
        obj_in.dni = dni
        obj_in.address = address
        obj_in.city = city
        obj_in.province = province
        obj_in.country = country
        obj_in.nationality = nationality
        obj_in.occupation = occupation
        obj_in.postal_code = postal_code
        obj_in.civil_status = civil_status
        obj_in.date_birthday = date_birthday
        obj_in.economic_matrimonial_regime = economic_matrimonial_regime
        obj_in.politically_exposed = politically_exposed

        # se comprueba si existen datos
        db_users_data_physical_person = db.query(models_user.UserDataPhysicalPerson).filter(models_user.UserDataPhysicalPerson.user_id == db_user.id).first()
        if db_users_data_physical_person:
            # se actualiza la tabla users_data_physical_person
            _update(db, db_obj=db_users_data_physical_person, obj_in=obj_in)
        else:
            # se inserta en la tabla users_data_physical_person como nuevo
            _create(db, obj_in=obj_in, table='users_data_physical_person')

        # ademas si el user_type es 1 es que es una empresa
        if user_type == 1:
            obj_in = Object()
            obj_in.user_id = db_user.id
            obj_in.company_name = company_name
            obj_in.activity = activity
            obj_in.holders = holders
            obj_in.register_number = register_number
            obj_in.nif = nif
            obj_in.legal_form = legal_form
            obj_in.company_address = company_address
            obj_in.company_city = company_city
            obj_in.company_province = company_province
            obj_in.company_country = company_country
            obj_in.company_postal_code = company_postal_code
            obj_in.is_representative_owner = is_representative_owner

            # se comprueba si existen datos
            users_data_legal_person = db.query(models_user.UserDataLegalPerson).filter(models_user.UserDataLegalPerson.user_id == db_user.id).first()
            if users_data_legal_person:
                # se actualiza la tabla users_data_legal_person
                _update(db, db_obj=users_data_legal_person, obj_in=obj_in)
            else:
                # se inserta en la tabla users_data_legal_person como nuevo
                _create(db, obj_in=obj_in, table='users_data_legal_person')
