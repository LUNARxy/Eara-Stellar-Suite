from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from api.v1 import const, roles
from api.v1.base.base import _can_access_roles
from api.v1.base.base_invest import (
    _get_invest,
    _get_invest_by_id_obligatory,
    _get_invest_by_slug_obligatory,
)
from api.v1.base.base_invest_mint_phases import _get_actual_phase_or_next
from api.v1.base.base_login import UserCurrentLogin, _get_user_login
from api.v1.base.base_marketplace import _buy_user_invest_tokens
from api.v1.base.base_user import _get_user_by_id

from api.v1.deps import _get_db
from api.v1.emails import emails, emails_admin
from api.v1.models import models_invest
from blockchain.nft_utils import get_api_crypto_fiat_price
from blockchain.stellar.stellar_keypair import (
    sign_user_mint_with_token,
    get_public_key as stellar_get_public_key,
)
from blockchain.stellar.stellar_utils import (
    wait_for_soroban_transaction,
    get_user_nonce,
)

router = APIRouter()


@router.get("/contract_address/{invest_id}")
def get_contract_address(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
    invest_id: int,
):
    invest = _get_invest_by_id_obligatory(
        db=db,
        invest_id=invest_id,
    )
    return {"contract_address": invest.contract_address}


@router.get("/mint_signature_token_stellar/{invest_id}")
def mint_signature_token_stellar(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
    invest_id: str = "",
    address: str,
    amount: int,
):
    """
    Genera la firma off-chain para que el usuario pueda invocar user_mint_with_token
    en el contrato Soroban LunarXY desde su propia wallet Stellar.

    El backend NO envía ninguna transacción. El frontend recibe los parámetros
    y la firma, construye la tx Soroban y la firma con la wallet del usuario
    (Freighter, xBull, etc.).

    Parámetros:
        invest_id: ID del proyecto de inversión
        address:   Dirección pública Stellar del usuario (G...)
        amount:    Tokens a mintear (enteros, decimals=0)

    Respuesta:
        amount:         Tokens a mintear
        payment_amount: Precio calculado en unidades base del token de pago (i128)
        nonce:          Nonce on-chain actual del usuario (anti-replay)
        uid:            user_id del usuario en la BD
        signature:      Firma Ed25519 del backend en hex (128 chars = 64 bytes)
        payment_token:  Contract ID del token de pago (C...)
        contract:       Contract ID del contrato LunarXY (C...)
    """
    if current_user.kyc_valid != 1:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="server.The user does not have a valid kyc",
        )

    db_user = _get_user_by_id(
        db=db,
        user_id=current_user.id,
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="server.User not found"
        )

    if db_user.wallet_address != address:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="server.The address is not valid",
        )

    invest = _get_invest(
        db=db,
        invest_id=invest_id,
    )

    phase = _get_actual_phase_or_next(db=db, invest_id=invest_id)
    if not phase.phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="server.InvestMintPhases not found",
        )

    # Calcular el precio en unidades del token de pago a partir del precio fiat de la fase
    q = db.query(models_invest.InvestMintERC20Tokens)
    q = q.filter(models_invest.InvestMintERC20Tokens.invest_id == invest_id)
    q = q.filter(models_invest.InvestMintERC20Tokens.token_symbol == "SUSD")
    tokens_data = q.first()
    if not tokens_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="server.InvestMintERC20Tokens not found",
        )

    price_token_fiat = get_api_crypto_fiat_price(
        phase.symbol_fiat, tokens_data.token_symbol
    )
    price_token_unit = int(
        (phase.price_fiat * price_token_fiat) * (10**tokens_data.token_decimals)
    )
    if phase.fee_percent > 0:
        price_token_unit = int(price_token_unit * (1 + (phase.fee_percent / 100)))

    # Obtener el nonce on-chain actual del usuario (llamada read-only, sin tx)
    try:
        nonce = get_user_nonce(
            caller_public_key=address, contract_id=str(invest.contract_address)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="server.Error al consultar el nonce on-chain",
        )

    # Firmar el mensaje con el layout exacto que espera el contrato Soroban:
    #   SHA-256( amount(16 LE) | price(16 LE) | nonce(8 LE) | uid(8 LE) | contract_addr_xdr )
    try:
        sig_bytes = sign_user_mint_with_token(
            secret_key=str(phase.mint_pk),
            contract_id=str(invest.contract_address),
            amount=amount,
            payment_amount=price_token_unit,
            nonce=nonce,
            uid=current_user.id,
            payment_token_id=str(tokens_data.token_address),
        )
        signer_public_key = stellar_get_public_key(str(phase.mint_pk))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="server.Error al firmar el mensaje Stellar",
        )

    return {
        "amount": amount,
        "payment_amount": price_token_unit,
        "nonce": nonce,
        "uid": current_user.id,
        "signature": sig_bytes.hex(),
        "payment_token": str(tokens_data.token_address),
        "contract": str(invest.contract_address),
    }


@router.get("/phase_tokens_data/{invest_slug}")
def phase_tokens_data(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
    invest_slug: str = "",
):
    invest = _get_invest_by_slug_obligatory(
        db=db,
        slug=invest_slug,
    )
    q = db.query(models_invest.InvestMintERC20Tokens).filter(
        models_invest.InvestMintERC20Tokens.invest_id == invest.id
    )
    tokens_data = q.all()
    if not tokens_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="server.InvestMintPhases not found",
        )

    return tokens_data


@router.get("/check_transaction/{invest_id}/{tx_hash}/{signature_documents_id}")
async def check_transaction(
    *,
    db: Session = Depends(_get_db),
    current_user: UserCurrentLogin = Depends(_get_user_login),
    access: Any = Depends(
        _can_access_roles(roles_can_access=[roles.ROLE_ADMIN, roles.ROLE_USER])
    ),
    invest_id: int,
    tx_hash: str,
    signature_documents_id: int = 0,
):
    invest = _get_invest(
        db=db,
        invest_id=invest_id,
        status_invest=const.INVEST_STATUS_FINANCING_PHASE,
    )

    receipt = wait_for_soroban_transaction(tx_hash)
    if not receipt.get("status"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="server.fallo al realizar el mint de los tokens",
        )

    # Para Stellar el hash es un string opaco — lo usamos directamente como mint_tx
    num_tokens = receipt.get("amount", 0)
    mint_tx = tx_hash

    if not signature_documents_id:
        signature_documents_id = None

    buy = _buy_user_invest_tokens(
        db=db,
        user_id=current_user.id,
        invest_id=invest.id,
        num_tokens=num_tokens,
        type_buy=const.USERS_INVEST_TYPE_BUY,
        buy_subtype=const.BUY_SUBTYPE_PAYMENT_CRYPTO,
        mint_tx=mint_tx,
        signature_documents_id=signature_documents_id,
    )

    await emails.send_email_buy_fiat_without_verified_ok(
        language=current_user.language,
        email=current_user.email,
        project_name=invest.name,
        token_number=str(num_tokens),
        token_value=str(num_tokens * buy.price_token),
        symbol_fiat="EUR",
    )

    # se manda email al admin
    await emails_admin.admin_send_email_user_buy_crypto(
        email=current_user.email,
        invest_id=invest.id,
        project_name=invest.name,
        num_tokens=num_tokens,
    )
    return {"status": "ok"}
