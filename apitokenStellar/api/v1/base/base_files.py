import base64
import os
import secrets
import shutil
import magic

from io import BytesIO
from pathlib import Path
from typing import Dict
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from starlette import status
from PIL import Image
from weasyprint import HTML
from jinja2 import Template
from api.v1 import const
from api.v1.base.base import _delete, _create, _update, Object
from api.v1.models import models_user


def _delete_all_other_types_images(current_user, db, types_to_delete):
    for ft in types_to_delete:
        db_files = db.query(models_user.UserDataDocuments).filter(models_user.UserDataDocuments.user_id == current_user.id).filter(models_user.UserDataDocuments.file_type == ft).all()
        if db_files:
            for db_file in db_files:
                _delete_file_in_folder(db_file.file, is_public=False)
                _delete(db=db, obj_delete=db_file)


def _delete_file_if_exists_for_person(current_user, db, file_type):
    types_to_delete = [const.FILE_TYPE_DNI_BACK,
                       const.FILE_TYPE_DNI_FRONT,
                       const.FILE_TYPE_DRIVE_LICENSE_BACK,
                       const.FILE_TYPE_DRIVE_LICENSE_FRONT,
                       const.FILE_TYPE_RESIDENCE_CARD_BACK,
                       const.FILE_TYPE_RESIDENCE_CARD_FRONT,
                       const.FILE_TYPE_PASSPORT_EU_BACK,
                       const.FILE_TYPE_PASSPORT_EU_FRONT,
                       const.FILE_TYPE_PASSPORT_OUTSIDE_EU_FRONT, ]
    if file_type == const.FILE_TYPE_DNI_FRONT:
        types_to_delete.remove(const.FILE_TYPE_DNI_BACK)
    elif file_type == const.FILE_TYPE_DNI_BACK:
        types_to_delete.remove(const.FILE_TYPE_DNI_FRONT)
    elif file_type == const.FILE_TYPE_DRIVE_LICENSE_FRONT:
        types_to_delete.remove(const.FILE_TYPE_DRIVE_LICENSE_BACK)
    elif file_type == const.FILE_TYPE_DRIVE_LICENSE_BACK:
        types_to_delete.remove(const.FILE_TYPE_DRIVE_LICENSE_FRONT)
    elif file_type == const.FILE_TYPE_RESIDENCE_CARD_FRONT:
        types_to_delete.remove(const.FILE_TYPE_RESIDENCE_CARD_BACK)
    elif file_type == const.FILE_TYPE_RESIDENCE_CARD_BACK:
        types_to_delete.remove(const.FILE_TYPE_RESIDENCE_CARD_FRONT)
    elif file_type == const.FILE_TYPE_PASSPORT_EU_FRONT:
        types_to_delete.remove(const.FILE_TYPE_PASSPORT_EU_BACK)
    elif file_type == const.FILE_TYPE_PASSPORT_EU_BACK:
        types_to_delete.remove(const.FILE_TYPE_PASSPORT_EU_FRONT)

    return _delete_all_other_types_images(current_user, db, types_to_delete)


def _delete_file_if_exists_for_legal_representative(current_user, db, file_type):
    types_to_delete = [const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_FRONT,
                       const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_FRONT,
                       const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_FRONT,
                       const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_FRONT
                       ]
    if file_type == const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_FRONT)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_FRONT)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_FRONT)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_FRONT)

    # borramos el fichero si existe para el usuario
    _delete_all_other_types_images(current_user, db, types_to_delete)


def _delete_file_if_exists_for_legal_person_holder_1(current_user, db, file_type):
    types_to_delete = [const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_FRONT,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_FRONT,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_FRONT,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_FRONT
                       ]
    if file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_FRONT)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_FRONT)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_FRONT)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_FRONT)

    # borramos el fichero si existe para el usuario
    _delete_all_other_types_images(current_user, db, types_to_delete)


def _delete_file_if_exists_for_legal_person_holder_2(current_user, db, file_type):
    types_to_delete = [const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_FRONT,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_FRONT,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_FRONT,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_FRONT
                       ]
    if file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_FRONT)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_FRONT)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_FRONT)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_FRONT)

    # borramos el fichero si existe para el usuario
    _delete_all_other_types_images(current_user, db, types_to_delete)


def _delete_file_if_exists_for_legal_person_holder_3(current_user, db, file_type):
    types_to_delete = [const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_FRONT,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_FRONT,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_FRONT,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_BACK,
                       const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_FRONT
                       ]
    if file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_FRONT)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_FRONT)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_FRONT)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_FRONT:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_BACK)
    elif file_type == const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_BACK:
        types_to_delete.remove(const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_FRONT)

    _delete_all_other_types_images(current_user, db, types_to_delete)


def _delete_file_if_exists_proof_iban(current_user, db):
    types_to_delete = [const.FILE_TYPE_PROOF_IBAN]

    # borramos el fichero si existe para el usuario
    _delete_all_other_types_images(current_user, db, types_to_delete)


def _delete_file_if_exists_for_user(current_user, db, file_type):
    if 2 <= file_type <= 11:
        _delete_file_if_exists_for_person(current_user, db, file_type)
    elif 20 <= file_type <= 27:
        _delete_file_if_exists_for_legal_representative(current_user, db, file_type)
    elif 30 <= file_type <= 37:
        _delete_file_if_exists_for_legal_person_holder_1(current_user, db, file_type)
    elif 40 <= file_type <= 47:
        _delete_file_if_exists_for_legal_person_holder_2(current_user, db, file_type)
    elif 50 <= file_type <= 57:
        _delete_file_if_exists_for_legal_person_holder_3(current_user, db, file_type)
    elif 58 <= file_type <= 60:
        _delete_all_other_types_images(current_user, db, [file_type])
    elif file_type == 61:
        _delete_file_if_exists_proof_iban(current_user, db)


def _get_document_type(file_aux):
    file_type = magic.from_file(file_aux, mime=True)
    if file_type in ['image/jpeg', 'image/png', 'image/gif']:
        return 'image'
    elif file_type in ['application/pdf']:
        return 'pdf'


def _store_and_save_file(current_user, db, file, file_type, my_folder, name):
    file_aux_name = _create_file_in_folder(uploaded_file=file, my_folder=my_folder, valid_file_type='both', is_private=True, name=name)
    file_aux = f'{my_folder}/{file_aux_name}'
    document_type = _get_document_type(f'private/{file_aux}')

    obj_in = Object()
    obj_in.user_id = current_user.id
    obj_in.file = file_aux
    obj_in.file_type = file_type
    obj_in.document_type = document_type
    return _create(db=db, obj_in=obj_in, table='users_data_documents')


def _store_and_save_kyc_file(current_user, db, file, file_type, my_folder, name):
    return _store_and_save_file(current_user, db, file, file_type, my_folder, name)


def _create_file_in_folder(
        uploaded_file: UploadFile,
        my_folder: str,
        valid_file_type: str,
        is_private: bool = False,
        name: str = ''
):
    if valid_file_type not in ['image', 'document', 'both']:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid file type")

    # si queremos coger el mismo nombre que nos viene:
    # file_name_arr = uploaded_file.filename.split('/')
    # file_name = file_name_arr[len(file_name_arr)-1]

    # extension
    # file_ext = os.path.splitext(uploaded_file.filename)[-1].lower()

    # ponemos un nombre aleatorio al fichero
    file_name_1 = secrets.randbelow(1000000000001)
    file_name_2 = secrets.randbelow(1000000000001)

    my_folder = f"{'private' if is_private else 'public'}/{my_folder}/"
    os.makedirs(my_folder, exist_ok=True)

    file_name = f"{name}_{file_name_1}_{file_name_2}"
    file_location = f"{my_folder}{file_name}"
    destination = Path(file_location)
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)
    finally:
        uploaded_file.file.close()

    # se recupera el mime type del fichero para ver si es correcto, sino lo es se borra el fichero y se da error
    file_type = magic.from_file(file_location, mime=True)
    # if file_type == 'application/octet-stream':
    #     file_type = clear_upload_file_parts_headers(file_location)

    # file_type = uploaded_file.content_type
    if valid_file_type == 'image' and file_type != 'image/jpeg' and file_type != 'image/png' and file_type != 'image/gif':
        os.unlink(file_location)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"File type {file_type} not allowed. It is allowed (image/jpeg, gif or png)")
    elif valid_file_type == 'document' and file_type != 'application/pdf':
        os.unlink(file_location)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"File type {file_type} not allowed. It is allowed (application/pdf)")
    elif valid_file_type == 'both' and file_type != 'image/jpeg' and file_type != 'image/png' and file_type != 'image/gif' and file_type != 'application/pdf':
        os.unlink(file_location)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"File type {file_type} not allowed. It is allowed (image/jpeg, gif, png or application/pdf)")

    """
    file_ext = ''
    if file_type == 'image/jpeg':
        file_ext = "jpg"
    elif file_type == 'image/png':
        file_ext = "png"
    elif file_type == 'image/gif':
        file_ext = "gif"
    elif file_type == 'application/pdf':
        file_ext = "pdf"

    os.rename(file_location, f"{file_location}.{file_ext}")
    """

    # Si es una imagen, la comprimimos y redimensionamos
    if file_type.startswith("image/"):
        img = Image.open(file_location)

        # Convertir a modo RGB si es necesario (para evitar problemas con GIF y PNG con transparencias)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Redimensionar si excede el tamaño máximo
        img.thumbnail((800, 800))

        # Determinar extensión y guardar con compresión
        file_ext = file_type.split("/")[-1]
        compressed_location = f"{file_location}.{file_ext}"
        if file_ext == "jpeg":
            img.save(compressed_location, "JPEG", quality=85)
        elif file_ext == "png":
            img.save(compressed_location, "PNG", optimize=True)
        elif file_ext == "gif":
            img.save(compressed_location, "GIF")

        os.unlink(file_location)  # Borrar la imagen original no comprimida
        os.rename(compressed_location, f"{file_location}.{file_ext}")
    else:
        file_ext = "pdf"
        os.rename(file_location, f"{file_location}.{file_ext}")

    return f"{file_name}.{file_ext}"


def _delete_file_in_folder(path_file: str, is_public: bool = True):
    try:
        # print(f'se elimina el fichero {path_file}')
        if is_public:
            os.remove(f"public/{path_file}")
        else:
            os.remove(f"private/{path_file}")
    finally:
        pass

    return {"ok": True}


def _save_upload_files_user(
        db: Session,
        user_id: int,
        
        files: Dict[str, str] = None,
        file_type: int = None,
        file: UploadFile = None,
):
    # si solo viene un fichero

    if file_type is not None and file:
        _save_upload_file_user_aux(db=db, user_id=user_id, file_type=file_type, file=file)

    # si vienen muchos ficheros
    if files:
        for file_type, file in files.items():
            # tranfrom  base64 to  UploadFile
            file = UploadFile(filename=file_type, file=BytesIO(base64.b64decode(file.split(',')[1])))

            file_type = int(file_type)
            _save_upload_file_user_aux(db=db, user_id=user_id, file_type=file_type, file=file)


def _save_upload_file_user_aux(
        db: Session,
        user_id: int,
        
        file_type: int = None,
        file: UploadFile = None,
):
    # se crea la imagen el la carpeta publica del servidor
    my_folder = f"upload_files/earastellar/users/{user_id}"

    file_types_data = {
        const.FILE_TYPE_DNI_BACK: 'dni_back',
        const.FILE_TYPE_DNI_FRONT: 'dni_front',
        const.FILE_TYPE_DRIVE_LICENSE_BACK: 'drive_license_back',
        const.FILE_TYPE_DRIVE_LICENSE_FRONT: 'drive_license_front',
        const.FILE_TYPE_RESIDENCE_CARD_BACK: 'residence_card_back',
        const.FILE_TYPE_RESIDENCE_CARD_FRONT: 'residence_card_front',
        const.FILE_TYPE_PASSPORT_EU_BACK: 'passport_eu_back',
        const.FILE_TYPE_PASSPORT_EU_FRONT: 'passport_eu_front',
        const.FILE_TYPE_PASSPORT_OUTSIDE_EU_FRONT: 'passport_outside_eu_front',
        const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_BACK: 'legal_person_representative_dni_back',
        const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_FRONT: 'legal_person_representative_dni_front',
        const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_BACK: 'legal_person_representative_drive_license_back',
        const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_FRONT: 'legal_person_representative_drive_license_front',
        const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_BACK: 'legal_person_representative_residence_card_back',
        const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_FRONT: 'legal_person_representative_residence_card_front',
        const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_BACK: 'legal_person_representative_passport_eu_back',
        const.FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_FRONT: 'legal_person_representative_passport_eu_front',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_BACK: 'legal_person_holder_1_dni_back',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_FRONT: 'legal_person_holder_1_dni_front',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_BACK: 'legal_person_holder_1_drive_license_back',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_FRONT: 'legal_person_holder_1_drive_license_front',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_BACK: 'legal_person_holder_1_residence_card_back',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_FRONT: 'legal_person_holder_1_residence_card_front',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_BACK: 'legal_person_holder_1_passport_eu_back',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_FRONT: 'legal_person_holder_1_passport_eu_front',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_BACK: 'legal_person_holder_2_dni_back',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_FRONT: 'legal_person_holder_2_dni_front',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_BACK: 'legal_person_holder_2_drive_license_back',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_FRONT: 'legal_person_holder_2_drive_license_front',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_BACK: 'legal_person_holder_2_residence_card_back',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_FRONT: 'legal_person_holder_2_residence_card_front',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_BACK: 'legal_person_holder_2_passport_eu_back',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_FRONT: 'legal_person_holder_2_passport_eu_front',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_BACK: 'legal_person_holder_3_dni_back',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_FRONT: 'legal_person_holder_3_dni_front',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_BACK: 'legal_person_holder_3_drive_license_back',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_FRONT: 'legal_person_holder_3_drive_license_front',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_BACK: 'legal_person_holder_3_residence_card_back',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_FRONT: 'legal_person_holder_3_residence_card_front',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_BACK: 'legal_person_holder_3_passport_eu_back',
        const.FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_FRONT: 'legal_person_holder_3_passport_eu_front',
        const.FILE_TYPE_CERTIFICATE_OF_INCORPORATION: 'certificate_of_incorporation',
        const.FILE_TYPE_ARTICLES_OF_ASSOCIATION: 'articles_of_association',
        const.FILE_TYPE_DEEPS_OF_INCORPORATION: 'deeps_of_incorporation',
        const.FILE_TYPE_PROOF_IBAN: 'proof_of_iban'
    }

    # se recupera al usuario
    q = db.query(models_user.User)
    q = q.filter(models_user.User.id == user_id)
    user_db = q.first()

    if file_type == const.FILE_TYPE_PROFILE:  # foto de perfil
        obj_in = Object()
        _delete_file_in_folder(user_db.file_profile)
        file_aux_name = _create_file_in_folder(uploaded_file=file, my_folder=my_folder, valid_file_type='image', name='profile')
        file_aux = f'{my_folder}/{file_aux_name}'
        obj_in.file_profile = file_aux
        _update(db, db_obj=user_db, obj_in=obj_in)
    elif file_type == const.FILE_TYPE_PROFILE_TOP:  # foto top de perfil
        obj_in = Object()
        _delete_file_in_folder(user_db.file_top)
        file_aux_name = _create_file_in_folder(uploaded_file=file, my_folder=my_folder, valid_file_type='image', name='file_top')
        file_aux = f'{my_folder}/{file_aux_name}'
        obj_in.file_top = file_aux
        _update(db, db_obj=user_db, obj_in=obj_in)
    elif file_type == const.FILE_TYPE_SELFIE:  # selfie
        _delete_file_if_exists_for_user(user_db, db, file_type)

        _store_and_save_file(user_db, db, file, file_type, my_folder, 'selfie')
    elif file_type in file_types_data.keys():
        if const.FILE_TYPE_PROOF_IBAN == file_type:
            pass
        else:
            if user_db.kyc_valid == 1:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="server.The user does have a valid kyc")


        _delete_file_if_exists_for_user(user_db, db, file_type)

        _store_and_save_kyc_file(user_db, db, file, file_type, my_folder, file_types_data[file_type])

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Server.Error")


