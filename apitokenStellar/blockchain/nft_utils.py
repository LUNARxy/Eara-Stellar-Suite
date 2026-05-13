import requests
from cachetools import cached, TTLCache
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from api.v1.models import models_invest
from blockchain.stellar.stellar_keypair import sign_user_mint
from blockchain.stellar.stellar_utils import invoke_and_wait, get_user_nonce


def get_api_crypto_fiat_price(crypto: str, fiat: str):
    url = f"https://min-api.cryptocompare.com/data/price?fsym={crypto}&tsyms={fiat}"
    response = requests.get(url).json()
    return response[fiat]


def _mint_tokens_stellar(
    invest: models_invest.Invest,
    amount: int,
    uid: int,
    db: Session,
    phase,
) -> dict:
    """
    Custodial mint of LunarXY tokens on Stellar/Soroban via user_mint.

    The backend acts as `caller` using invest.pooled_wallet (signs the Soroban tx
    with invest.pooled_wallet_key) and generates the Ed25519 off-chain signature
    (with phase.mint_pk) that the contract verifies.

    Flow:
        1. Get active phase (if not provided)
        2. Calculate price in XLM base units from phase fiat price + exchange rate
        3. Fetch the on-chain nonce for invest.pooled_wallet
        4. Sign the user_mint message with phase.mint_pk (off-chain Ed25519)
        5. Invoke user_mint on the contract, signing the tx with invest.pooled_wallet_key

    Args:
        invest: Invest record; invest.pooled_wallet is the Stellar caller (G...),
                invest.pooled_wallet_key is its secret key (S...)
        amount: Number of tokens to mint (i128)
        uid:    User ID in the database (u64)
        db:     SQLAlchemy session
        phase:  Active mint phase (or None to look it up)

    Returns:
        {"status": bool, "message": str, "result": ..., "transaction_hash": str}
    """
    import logging
    from stellar_sdk import scval

    # 1. Get active phase
    if not phase:
        phase = get_active_phase(invest.id, db)

    # 2. Get payment token data from DB to calculate the XLM price
    q = db.query(models_invest.InvestMintERC20Tokens)
    q = q.filter(models_invest.InvestMintERC20Tokens.invest_id == invest.id)
    q = q.filter(models_invest.InvestMintERC20Tokens.token_symbol == "XLM")
    tokens_data = q.first()
    if not tokens_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="server.InvestMintERC20Tokens not found",
        )

    token_decimals = int(tokens_data.token_decimals)
    price_token_fiat = get_api_crypto_fiat_price(
        phase.symbol_fiat, tokens_data.token_symbol
    )
    price = int((phase.price_fiat * price_token_fiat) * (10**token_decimals))
    if phase.fee_percent > 0:
        price = int(price * (1 + (phase.fee_percent / 100)))

    # 3. Get on-chain nonce for the caller (invest.pooled_wallet)
    caller_address = str(invest.pooled_wallet)
    nonce = get_user_nonce(
        caller_public_key=caller_address,
        contract_id=str(invest.contract_address),
    )

    # 4. Generate Ed25519 off-chain signature with phase.mint_pk
    sig_bytes = sign_user_mint(
        secret_key=str(phase.mint_pk),
        contract_id=str(invest.contract_address),
        amount=amount,
        price=price,
        nonce=nonce,
        uid=uid,
    )

    # 5. Build contract args for user_mint(caller, amount, price, nonce, uid, signature)
    args = [
        scval.to_address(caller_address),  # caller: Address
        scval.to_int128(amount),           # amount: i128
        scval.to_int128(price),            # price: i128
        scval.to_uint64(nonce),            # nonce: u64
        scval.to_uint64(uid),              # uid: u64
        scval.to_bytes(sig_bytes),         # signature: BytesN<64>
    ]

    # 6. Invoke user_mint — tx signed by invest.pooled_wallet_key
    caller_secret_key = str(invest.pooled_wallet_key)
    result = invoke_and_wait(
        secret_key=caller_secret_key,
        contract_id=str(invest.contract_address),
        function_name="user_mint",
        args=args,
    )

    logging.info(
        f"Stellar user_mint for user {uid} -> {caller_address}: "
        f"{amount} tokens, price={price}, tx={result.get('transaction_hash')}"
    )

    return result


def mint_tokens_to_pooled_wallets(
    invest: models_invest.Invest,
    amount: int,
    uid: int,
    db: Session,
    phase,
):
    return _mint_tokens_stellar(invest, amount, uid, db, phase)


def get_active_phase(invest_id: int, db: Session) -> models_invest.InvestMintPhases:
    current_datetime = datetime.now()

    q = db.query(models_invest.InvestMintPhases)
    q = q.filter(models_invest.InvestMintPhases.invest_id == invest_id)
    q = q.filter(models_invest.InvestMintPhases.date_start <= current_datetime)
    q = q.filter(models_invest.InvestMintPhases.date_end >= current_datetime)

    phase_item = q.first()

    if not phase_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="server.InvestMintPhases not found",
        )

    return phase_item
