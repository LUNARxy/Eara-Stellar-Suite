from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime

from api.v1.database import Base


class GovernorTransactions(Base):
    __tablename__ = "governor_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, index=True,  nullable=False)
    block_chain_id = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False, comment="1 - Freeze, 2 - Unfreeze, 3 - Seize")
    legal_justification = Column(Integer, nullable=False, comment="1 Mandato Judicial - Embargo, 2 Mandato Judicial - Medida Cautelar, 3 Sucesión por Causa de Muerte, 4 Disolución de Sociedad de Gananciales, 6 Ejecución de Prenda, 7 Concurso de Acreedores, 8 Medidas de Apoyo a Persona con Discapacidad, 9 Restitución por Pérdida/Robo de Claves, 10 Otra (requiere justificación manual)")
    legal_justification_text = Column(String(500), nullable=True)
    external_reference = Column(String(256), nullable=True)
    evidence_document_path = Column(String(500), nullable=False)
    wallet_address = Column(String(100), nullable=False)

    tx = Column(String(200), nullable=False)
    status = Column(Integer, nullable=False, default=1, comment="1 - Pending, 2 - Completed, 3 - Canceled, 4 - Failed")
    date_created = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))


class GovernorConfirmations(Base):
    __tablename__ = "governor_confirmations"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    governor_transaction_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    tx = Column(String(200), nullable=False)
    type = Column(Integer, nullable=False, default=1, comment="1 - Confirm, 2 - Reject")

    date_created = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))

