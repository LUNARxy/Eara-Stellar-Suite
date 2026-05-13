from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, Integer, String, SmallInteger, DateTime, Boolean, Text, Float

from api.v1.database import Base


class Invest(Base):
    __tablename__ = "invest"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(100), index=True, unique=True, nullable=False)
    is_draft = Column(Boolean, nullable=False, default=True, index=True)
    is_completed = Column(Boolean, nullable=False, default=False, index=True)
    is_paused = Column(Boolean, nullable=False, default=False, index=True)
    category_id = Column(Integer, nullable=False, default=2, index=True)
    name = Column(String(200), nullable=False)
    name_EN = Column(String(200), nullable=True)

    time_limit = Column(String(50), nullable=True, comment="Plazo de la inversión, (Ej. 18-24 meses)")
    time_limit_EN = Column(String(50), nullable=True, comment="Plazo de la inversión, (Ej. 18-24 meses)")

    contract_address = Column(String(200), nullable=True)
    sign_address = Column(String(200), nullable=True)
    token_id = Column(String(200), nullable=True)
    token_abbreviation = Column(String(10), nullable=True)

    title = Column(String(500), nullable=False)
    title_EN = Column(String(500), nullable=True)
    summary = Column(Text, nullable=False)
    summary_EN = Column(Text, nullable=True)
    description = Column(Text, nullable=False)
    description_EN = Column(Text, nullable=True)
    proposal_to_investors = Column(Text, nullable=True)
    proposal_to_investors_EN = Column(Text, nullable=True)

    file = Column(String(200), nullable=False)
    file_top = Column(String(200), nullable=False)
    profit_estimated = Column(Float, nullable=True, default=0)
    profit_estimated_description = Column(String(50), nullable=True)
    risk = Column(SmallInteger, nullable=False, comment="x/6")
    web = Column(String(200), nullable=True)
    is_important = Column(Boolean, nullable=False, default=False, index=True)

    hide_time_data = Column(Boolean, nullable=False, default=False)
    hide_date_start_round = Column(Boolean, nullable=False, default=False)
    hide_date_end_round = Column(Boolean, nullable=False, default=False)
    hide_profit_estimated = Column(Boolean, nullable=False, default=False)
    hide_risk = Column(Boolean, nullable=False, default=False)
    hide_value_round = Column(Boolean, nullable=False, default=False)
    hide_num_tokens = Column(Boolean, nullable=False, default=False)

    location = Column(String(300), nullable=True)
    location_gps_lat = Column(String(20), nullable=True, comment="coordenadas gps latitud")
    location_gps_lon = Column(String(20), nullable=True, comment="coordenadas gps longitud")

    date_created = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    date_deleted = Column(DateTime, nullable=True)

    deploy_state = Column(SmallInteger, nullable=False, default=0, comment="0->no desplegado 1->marcado para deplegasr 2->desplegado")

    payment_wallet = Column(String(200), nullable=True)
    pooled_wallet = Column(String(200), nullable=True)
    pooled_wallet_key = Column(String(200), nullable=True)
    blockchain_network = Column(String(50), nullable=True)

    show_on_pentaken = Column(Boolean, nullable=False, default=False, index=True)

    token_type = Column(String(length=20), nullable=False, server_default='stellar')

    total_amount_invested_completed = Column(Float, nullable=True, comment="Para proyectos completados sin fases")
    num_tokens_completed = Column(Integer, nullable=True, comment="Para proyectos completados sin fases")
    num_investors_completed = Column(Integer, nullable=True, comment="Para proyectos completados sin fases")


    success_fee = Column(Float, nullable=True)
    management_fee = Column(Float, nullable=True)
    opening_commission = Column(Float, nullable=True)
    closing_commission = Column(Float, nullable=True)
    spread = Column(Float, nullable=True)
    entry_fee = Column(Float, nullable=True)
    annual_fee = Column(Float, nullable=True)



class InvestProfit(Base):
    __tablename__ = "invest_profit"
    """
    el profit de los beneficios acumulados de ese mes a repartir entre todos los tokens
    es decir, creamos un proyecto, con 100 tokens y un valor de 1000 euros, cada token son 10 euros, yo compro 2 tokens, 20 euros
    metemos en el campo profit 300 euros en una fecha
    entonces para esa fecha, a mi que me sale que tengo, los 20 euros iniciales + (300 el profit/100 los tokens) que sería el total de tokens * mis tokens que son 2
    me tocarían 6 euros sumados a los 20 que tenia pues 26
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    invest_id = Column(Integer, ForeignKey("invest.id"), nullable=False)
    profit = Column(Float, nullable=False)
    date_profit = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))


class InvestStatusDescription(Base):
    __tablename__ = "invest_status_description"
    """
    Cuando el proyecto está en curso se puede añadir estados de como está avanzando
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    invest_id = Column(Integer, ForeignKey("invest.id"), nullable=False)
    phase = Column(Integer, nullable=False, comment="Coincide con el status de la tabla invest, por defecto en curso", default=3)
    description = Column(String(200), nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))


class InvestMedia(Base):
    __tablename__ = "invest_media"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invest_id = Column(Integer, ForeignKey("invest.id"), nullable=False)
    file = Column(String(200), nullable=False)
    description = Column(String(200), nullable=True)
    is_video = Column(Boolean, nullable=False, default=False)


class InvestDocuments(Base):
    __tablename__ = "invest_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invest_id = Column(Integer, ForeignKey("invest.id"), nullable=False)
    file = Column(String(200), nullable=False)
    description = Column(String(200), nullable=True)


class InvestNews(Base):
    __tablename__ = "invest_news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invest_id = Column(Integer, ForeignKey("invest.id"), nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(String(1000), nullable=False)
    file = Column(String(200), nullable=True)
    url = Column(String(250), nullable=False)


class InvestQuestions(Base):
    __tablename__ = "invest_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invest_id = Column(Integer, ForeignKey("invest.id"), nullable=False)
    title = Column(String(200), nullable=True)
    comment = Column(String(5000), nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))


class InvestTeam(Base):
    __tablename__ = "invest_team"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invest_id = Column(Integer, ForeignKey("invest.id"), nullable=False)
    name = Column(String(200), nullable=False)
    job = Column(String(200), nullable=True)
    description = Column(String(2000), nullable=True)
    url_linked_in = Column(String(250), nullable=True)
    file = Column(String(200), nullable=True)


class InvestFollows(Base):
    # inversiones favoritas de los usuarios
    __tablename__ = "invest_follows"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    invest_id = Column(Integer, ForeignKey("invest.id"), primary_key=True, nullable=False)


class InvestMintPhases(Base):
    __tablename__ = "invest_mint_phases"
    """
    fases de minteo de un proyecto
    """
    invest_id = Column(Integer, ForeignKey("invest.id"), primary_key=True, nullable=False)
    phase = Column(String(50), primary_key=True, nullable=False)
    is_private = Column(Boolean, nullable=False, default=False, comment="para saber si es privada para sacar whitelist")
    create_active = Column(Boolean, nullable=False, default=False)
    max_tokens = Column(Integer, nullable=False, default=0)
    pay_with_eth = Column(Boolean, nullable=False, default=False)
    mint_address = Column(String(200), nullable=True)
    mint_pk = Column(String(200), nullable=True)
    price_eth_wey = Column(String(100), nullable=False, default=0)
    price_fiat = Column(Float, nullable=True, default=None)
    symbol_fiat = Column(String(10), nullable=True, default=None)
    num_tokens_min_to_buy = Column(Integer, nullable=False, default=1)
    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    is_email_on_funding_back = Column(Boolean, nullable=False, default=False)
    is_email_on_funding = Column(Boolean, nullable=False, default=False)
    is_email_in_course = Column(Boolean, nullable=False, default=False)
    fee_percent = Column(Float, nullable=False, default=0)


class InvestMintERC20Tokens(Base):
    __tablename__ = "invest_mint_erc20_tokens"
    """
    fases de minteo de un proyecto
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    invest_id = Column(Integer, ForeignKey("invest.id"), nullable=False)
    token_symbol = Column(String(10), nullable=False)
    token_decimals = Column(Integer, nullable=False, default=0)
    token_address = Column(String(200), nullable=True)
    date_created = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
