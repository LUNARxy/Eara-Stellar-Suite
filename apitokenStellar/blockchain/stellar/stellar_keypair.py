"""
Utilidades para la gestión de keypairs Ed25519 en la red Stellar.
Las claves Stellar usan Ed25519 y se codifican en formato Strkey:
  - Clave pública: empieza por 'G...' (56 caracteres)
  - Clave privada (seed): empieza por 'S...' (56 caracteres)
"""

import base64
import logging
from typing import Dict

from stellar_sdk import Keypair


def generate_stellar_keypair() -> Dict[str, str]:
    """
    Genera un nuevo keypair Ed25519 aleatorio para la red Stellar.

    Returns:
        Dict con:
            - public_key: Strkey público (G...)
            - secret_key: Strkey secreto (S...) — mantener en secreto
    """
    keypair = Keypair.random()

    public_key = keypair.public_key
    secret_key = keypair.secret

    logging.info(f"Nuevo keypair Stellar generado. Public key: {public_key}")

    return {
        "public_key": public_key,
        "secret_key": secret_key,
    }


def keypair_from_secret(secret_key: str) -> Keypair:
    """
    Carga un keypair Stellar a partir de la clave secreta (Strkey S...).

    Args:
        secret_key: Clave secreta en formato Strkey (empieza por 'S')

    Returns:
        Objeto Keypair de stellar-sdk listo para firmar
    """
    return Keypair.from_secret(secret_key)


def sign_data(secret_key: str, data: bytes) -> bytes:
    """
    Firma un payload arbitrario usando Ed25519 con la clave privada Stellar.
    Útil para firmar mensajes fuera del contexto de transacciones Stellar.

    Args:
        secret_key: Clave secreta Stellar en formato Strkey (S...)
        data: Bytes a firmar

    Returns:
        Firma Ed25519 en bytes (64 bytes)
    """
    keypair = Keypair.from_secret(secret_key)
    return keypair.sign(data)


def verify_signature(public_key: str, data: bytes, signature: bytes) -> bool:
    """
    Verifica una firma Ed25519 usando la clave pública Stellar.

    Args:
        public_key: Clave pública Stellar en formato Strkey (G...)
        data: Bytes originales que fueron firmados
        signature: Firma Ed25519 (64 bytes)

    Returns:
        True si la firma es válida, False en caso contrario
    """
    try:
        keypair = Keypair.from_public_key(public_key)
        keypair.verify(data, signature)
        return True
    except Exception:
        return False


def get_public_key(secret_key: str) -> str:
    """
    Deriva la clave pública desde la clave secreta Stellar.

    Args:
        secret_key: Clave secreta en formato Strkey (S...)

    Returns:
        Clave pública en formato Strkey (G...)
    """
    return Keypair.from_secret(secret_key).public_key


def sign_user_mint(
    secret_key: str,
    contract_id: str,
    amount: int,
    price: int,
    nonce: int,
    uid: int,
) -> bytes:
    """
    Construye y firma el mensaje exacto que espera la función user_mint del
    contrato Soroban LunarXY.

    Layout del mensaje (SHA-256 sobre la concatenación de):
      - amount   : 16 bytes little-endian (i128)
      - price    : 16 bytes little-endian (i128)
      - nonce    :  8 bytes little-endian (u64)
      - uid      :  8 bytes little-endian (u64)
      - contract : bytes XDR del Address del contrato (contract_addr.to_xdr(&env))

    El digest SHA-256 se firma con Ed25519 usando la clave privada Stellar del
    servidor (formato Strkey S...).

    Args:
        secret_key:  Clave secreta Stellar del servidor (S...)
        contract_id: Contract ID del contrato Soroban (C...)
        amount:      Tokens a mintear en unidades base del token (i128)
        price:       Precio en unidades base del token de pago (i128)
        nonce:       Nonce on-chain actual del caller (u64)
        uid:         user_id del usuario en la base de datos (u64)

    Returns:
        Firma Ed25519 de 64 bytes
    """
    import hashlib
    from stellar_sdk import Address

    msg = b""
    msg += amount.to_bytes(16, byteorder="little", signed=True)
    msg += price.to_bytes(16, byteorder="little", signed=True)
    msg += nonce.to_bytes(8, byteorder="little", signed=False)
    msg += uid.to_bytes(8, byteorder="little", signed=False)
    # Serializar el Address del contrato como XDR, igual que contract_addr.to_xdr(&env) en Rust
    msg += base64.b64decode(Address(contract_id).to_xdr_sc_val().to_xdr())

    digest = hashlib.sha256(msg).digest()

    keypair = Keypair.from_secret(secret_key)
    return keypair.sign(digest)


def sign_user_mint_with_token(
    secret_key: str,
    contract_id: str,
    amount: int,
    payment_amount: int,
    nonce: int,
    uid: int,
    payment_token_id: str,
) -> bytes:
    """
    Construye y firma el mensaje exacto que espera la función user_mint_with_token
    del contrato Soroban LunarXY.

    Layout del mensaje (SHA-256 sobre la concatenación de):
      - amount          : 16 bytes little-endian (i128)
      - payment_amount  : 16 bytes little-endian (i128)
      - nonce           :  8 bytes little-endian (u64)
      - uid             :  8 bytes little-endian (u64)
      - contract        : bytes XDR del Address del contrato (contract_addr.to_xdr(&env))
      - payment_token   : bytes XDR del Address del token de pago (payment_token.to_xdr(&env))

    El digest SHA-256 se firma con Ed25519 usando la clave privada Stellar del
    servidor (formato Strkey S...).

    Args:
        secret_key:        Clave secreta Stellar del servidor (S...)
        contract_id:       Contract ID del contrato Soroban (C...)
        amount:            Tokens a mintear en unidades base del token (i128)
        payment_amount:    Precio en unidades base del token de pago (i128)
        nonce:             Nonce on-chain actual del caller (u64)
        uid:               user_id del usuario en la base de datos (u64)
        payment_token_id:  Contract ID del token de pago (C...)

    Returns:
        Firma Ed25519 de 64 bytes
    """
    import hashlib
    from stellar_sdk import Address

    msg = b""
    msg += amount.to_bytes(16, byteorder="little", signed=True)
    msg += payment_amount.to_bytes(16, byteorder="little", signed=True)
    msg += nonce.to_bytes(8, byteorder="little", signed=False)
    msg += uid.to_bytes(8, byteorder="little", signed=False)
    msg += base64.b64decode(Address(contract_id).to_xdr_sc_val().to_xdr())
    msg += base64.b64decode(Address(payment_token_id).to_xdr_sc_val().to_xdr())

    digest = hashlib.sha256(msg).digest()

    keypair = Keypair.from_secret(secret_key)
    return keypair.sign(digest)
