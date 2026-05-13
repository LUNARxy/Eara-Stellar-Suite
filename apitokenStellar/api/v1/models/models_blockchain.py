from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean

from api.v1.database import Base


class CustodianWalletsIds(Base):
    __tablename__ = "custodian_wallets_ids"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    wallet_address = Column(String(200), nullable=False)
    blockchain_network = Column(String(50), nullable=False)
    provider = Column(String(100), nullable=False)
    provider_id = Column(String(200), nullable=False)
    is_master_wallet = Column(Boolean, nullable=False, default=False)
    date_created = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
