from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, SmallInteger, Text, Float

from api.v1.database import Base


class UserAdmin(Base):
    __tablename__ = "users_admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(50), nullable=False, index=True, unique=True)
    hashed_password = Column(String(200), nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    email = Column(String(100), nullable=False, index=True, unique=True)
    hashed_password = Column(String(200), nullable=False)

    user_type = Column(SmallInteger, nullable=True, default=None, comment="0->persona física 1->persona jurídica o empresa")
    description = Column(String(2000), nullable=True)
    language = Column(String(2), nullable=False, default="es", comment="Idioma con el que se registra el usuario")

    kyc_valid = Column(SmallInteger, nullable=False, default=0, comment="0->no se ha modificado 1->válido 2->a revisar por admin 3->inválido")
    kyc_no_valid_reason = Column(String(1000), nullable=True)
    kyc_no_valid_reason_EN = Column(String(1000), nullable=True)

    file_top = Column(String(200), nullable=True)
    file_profile = Column(String(200), nullable=True)

    wallet_address = Column(String(200), nullable=True)
    is_promoter = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=False)
    active_token = Column(String(100), nullable=True)
    change_hashed_password = Column(String(200), nullable=True)
    change_password_date = Column(DateTime, nullable=True)
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_modified = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserDataPhysicalPerson(Base):
    __tablename__ = "users_data_physical_person"  # personas físicas o administradores de una sociedad

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    name = Column(String(100), nullable=True)
    surname = Column(String(100), nullable=True)
    dni = Column(String(20), nullable=True)
    date_birthday = Column(DateTime, nullable=True)
    phone = Column(String(100), nullable=True)
    address = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    country = Column(String(5), nullable=True)
    postal_code = Column(String(10), nullable=True)
    nationality = Column(String(5), nullable=True)
    occupation = Column(String(100), nullable=True)
    civil_status = Column(SmallInteger, nullable=True, comment="0->Soltero 1->casado 2->separado 3->divorciado")
    economic_matrimonial_regime = Column(SmallInteger, nullable=True,
                                         comment="0->La sociedad de gananciales 1->El régimen de participación 2->El régimen de separación de bienes")
    politically_exposed = Column(SmallInteger, nullable=True, comment="Persona políticamente expuesta: 0->No 1->Si")


class UserDataLegalPerson(Base):
    __tablename__ = "users_data_legal_person"  # personas jurídicas, empresas

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    company_name = Column(String(200), nullable=False)
    activity = Column(String(100), nullable=False)
    holders = Column(SmallInteger, nullable=True)
    register_number = Column(String(100), nullable=True)
    nif = Column(String(100), nullable=True)
    legal_form = Column(SmallInteger, nullable=True,
                        comment="0->Autónomo 1->Sociedad Limitada 2->Sociedad Anónima 3->Cooperativa 4->Sociedad civil 5->Comunidad de bienes 6->Otras")
    company_address = Column(String(200), nullable=True)
    company_city = Column(String(100), nullable=True)
    company_province = Column(String(100), nullable=True)
    company_country = Column(String(5), nullable=True)
    company_postal_code = Column(String(10), nullable=True)
    is_representative_owner = Column(Boolean, nullable=False, default=False)


class UserDataDocuments(Base):
    __tablename__ = "users_data_documents"  # documentos que sube el usuario, dni, etc para el KYC

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    file = Column(String(200), nullable=False)
    file_type = Column(SmallInteger, nullable=False, comment="2->dni back 3->dni front 4->selfie")
    document_type = Column(String(50), nullable=True)


class UserDocumentsOthers(Base):
    __tablename__ = "users_documents_others"  # documentos que sube el administrador para que el usuario los pueda ver

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    file = Column(String(200), nullable=False)
    file_type = Column(SmallInteger, nullable=True)
    document_type = Column(String(50), nullable=True, comment='image, document')
    description = Column(String(250), nullable=True)


class UserFollows(Base):
    __tablename__ = "users_follows"

    user_follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    user_followed_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)


class UserSubscribed(Base):
    __tablename__ = "users_suscribed"

    email = Column(String(100), primary_key=True, nullable=False)


class UserInvestWhiteList(Base):
    __tablename__ = "users_invest_white_list"
    # si existe registro en esta tabla para un usuario es que está en white_list
    # si ademas de existir el preference_to_buy es 1, 2... esta en privada, vip

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    invest_id = Column(Integer, ForeignKey("invest.id"), primary_key=True, nullable=False)
    preference_to_buy = Column(String(50), nullable=True, default=None, comment="Fase a la que tenemos acceso a comprar")
    value_to_invest = Column(String(20), nullable=True, default=None, comment="Cantidad dispuesta a invertir")
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)


class UserNFTWhiteList(Base):
    __tablename__ = "users_nft_white_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    email = Column(String(100), nullable=False)
    name = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    wallet = Column(String(200), nullable=True)
    telegram = Column(String(200), nullable=True)
    discord = Column(String(200), nullable=True)
    twitter = Column(String(200), nullable=True)
    message = Column(String(2000), nullable=True)
    preference_code = Column(String(200), nullable=True)
    is_vip = Column(Boolean, nullable=False, default=False)
    num_nfts_to_buy = Column(Integer, default=0)
    who_i_am = Column(String(200), nullable=True)
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)


class UserTickets(Base):
    __tablename__ = "users_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    parent_id = Column(Integer, ForeignKey("users_tickets.id"), nullable=True,
                       comment="si son respuestas tienen el id de la pregunta inicial")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_admin = Column(Boolean, default=False, comment="si es una respuesta del administrador")
    status = Column(SmallInteger, nullable=False,
                    comment="0->leer por admin 1->contestado admin 2-> leído usuario 99->cerrado")
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=False)

    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_modified = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserBankAccount(Base):
    __tablename__ = "users_bank_account"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=True)
    bic = Column(String(12), nullable=False)
    iban = Column(String(34), nullable=False)
    bank_country = Column(String(255), nullable=True)
    bank_name = Column(String(255), nullable=False)
    bank_street = Column(String(255), nullable=False)
    bank_cp = Column(String(255), nullable=False)
    bank_city = Column(String(255), nullable=False)
    bank_short_code = Column(String(2), nullable=False)
    bank_account_type = Column(SmallInteger, nullable=False)
    status = Column(SmallInteger, nullable=False, comment="0->no se ha modificado 1->válido 2->a revisar por admin 3->inválido")
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_modified = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    kyc_no_valid_reason = Column(String(255), nullable=True)
    kyc_no_valid_reason_EN = Column(String(255), nullable=True)


class UsersInvest(Base):
    # inversiones de los usuarios
    __tablename__ = "users_invest"
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invest_id = Column(Integer, ForeignKey("invest.id"), nullable=True)
    num_tokens = Column(Integer, nullable=False)
    price_token = Column(Float, nullable=False)
    value = Column(Float, nullable=False)
    other_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    type = Column(SmallInteger, nullable=False, index=True)
    phase = Column(String(50), nullable=True)
    profit_id = Column(Integer, ForeignKey("invest_profit.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("users_invest.id"), nullable=True)
    tx = Column(String(200), nullable=True)
    invest_mint_erc20_tokens_id = Column(Integer, ForeignKey("invest_mint_erc20_tokens.id"), nullable=True, comment="id de la stable coin")
    iban = Column(String(50), nullable=True, comment="numero de cuenta al que se le ha devuelto")
    date_upload_pdf_signature = Column(DateTime, nullable=True, comment="fecha de firma del pdf del contrato de compra de tokens")
    buy_subtype = Column(SmallInteger, nullable=True, comment="0->wallet virtual 1->Transferencia 2->tarjeta 3->Cripto")
    fees = Column(Float, nullable=False, default=0, comment="dato de las fees cobradas al comprar el token")
    date_modified = Column(DateTime, nullable=False, default=datetime.utcnow)


class UsersInvestDocumentsTransfer(Base):
    __tablename__ = "users_invest_documents_transfer"  # documentos que sube el usuario para justificar el pago por transferencia

    user_invest_id = Column(Integer, ForeignKey("users_invest.id"), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    file = Column(String(200), nullable=False)


class UsersInvestProfitPercentage(Base):
    __tablename__ = "users_invest_profit_percentage"  # porcentaje de retirada de dinero que pone el usuario para los proyectos con reparto de beneficios con porcentaje

    invest_id = Column(Integer, ForeignKey("invest.id"), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    profit_percentage = Column(Integer, nullable=False, default=0)

