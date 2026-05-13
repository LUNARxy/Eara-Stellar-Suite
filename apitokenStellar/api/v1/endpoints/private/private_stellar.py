import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import roles
from api.v1.base.base import Object, _can_access_roles, _update
from api.v1.base.base_login import UserCurrentLogin, _get_user_login
from api.v1.deps import _get_db
from api.v1.models import models_user
from blockchain.stellar.stellar_utils import is_trusted_issuer, is_compliant
from config import COMPLIANT_ID_CONTRACT_ID

router = APIRouter()


class IsTrustedIssuerResponse(BaseModel):
    wallet: str
    is_trusted_issuer: bool


@router.get("/is_trusted_issuer", response_model=IsTrustedIssuerResponse)
def get_is_trusted_issuer(
    wallet: str = Query(..., description="Stellar public key (G...)"),
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
) -> Dict[str, Any]:
    """Check whether a wallet address is a trusted issuer in the CompliantId contract.

    If the wallet is trusted, the associated user's KYC status is set to valid (kyc_valid=1).
    """

    if not COMPLIANT_ID_CONTRACT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="server.Stellar CompliantId contract is not configured",
        )

    try:
        result = is_trusted_issuer(
            issuer_public_key=wallet, contract_id=COMPLIANT_ID_CONTRACT_ID
        )
    except Exception as e:
        logging.error(f"Stellar is_trusted_issuer error for wallet {wallet}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="server.Error querying Stellar contract",
        )

    if result:
        user = (
            db.query(models_user.User).filter(models_user.User.wallet_address == wallet).first()
        )
        if user:
            if user.kyc_valid != 1:
                obj_in = Object()
                obj_in.kyc_valid = 1
                _update(db=db, db_obj=user, obj_in=obj_in)
                logging.info(f"KYC set to valid for user {user.id} (wallet {wallet})")
        else:
            logging.warning(f"Trusted issuer wallet {wallet} has no associated user")

    return IsTrustedIssuerResponse(wallet=wallet, is_trusted_issuer=result)


class IsCompliantResponse(BaseModel):
    wallet: str
    min_level: int
    is_compliant: bool


@router.get("/is_compliant", response_model=IsCompliantResponse)
def get_is_compliant(
    wallet: str = Query(..., description="Stellar public key (G...)"),
    min_level: int = Query(1, ge=1, description="Minimum compliance level required"),
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
) -> Dict[str, Any]:
    """Check whether a wallet address meets the compliance requirements in the CompliantId contract.

    Returns True if the user's record has status=Verified, level >= min_level, and is not expired.
    """

    if not COMPLIANT_ID_CONTRACT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="server.Stellar CompliantId contract is not configured",
        )

    try:
        result = is_compliant(
            user_public_key=wallet,
            contract_id=COMPLIANT_ID_CONTRACT_ID,
            min_level=min_level,
        )
    except Exception as e:
        logging.error(f"Stellar is_compliant error for wallet {wallet}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="server.Error querying Stellar contract",
        )

    if result:
        user = (
            db.query(models_user.User)
            .filter(
                models_user.User.wallet_address == wallet
            )
            .first()
        )
        if user:
            if user.kyc_valid != 1:
                obj_in = Object()
                obj_in.kyc_valid = 1
                _update(db=db, db_obj=user, obj_in=obj_in)
                logging.info(f"KYC set to valid for user {user.id} (wallet {wallet})")
        else:
            logging.warning(f"Compliant wallet {wallet} has no associated user")

    return IsCompliantResponse(wallet=wallet, min_level=min_level, is_compliant=result)