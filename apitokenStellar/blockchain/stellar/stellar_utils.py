"""
Utilidades para interactuar con contratos inteligentes Soroban en la red Stellar.
Proporciona funciones para:
  - Conectarse a Horizon (API REST) y al RPC de Stellar (Soroban)
  - Construir, firmar y enviar transacciones Stellar con firmas Ed25519
  - Invocar funciones de contratos Soroban
  - Esperar confirmación de transacciones
"""

import logging
from typing import Any, Dict, List, Optional

from stellar_sdk import (
    Keypair,
    Server,
    SorobanServer,
    TransactionBuilder,
)
from stellar_sdk.exceptions import NotFoundError
from stellar_sdk.soroban_rpc import GetTransactionStatus
from stellar_sdk.xdr import ContractEventType

from config import STELLAR_HORIZON_URL, STELLAR_RPC_URL, STELLAR_NETWORK_PASSPHRASE


# ============================================================================
# Clientes de red
# ============================================================================


def _get_horizon_server() -> Server:
    """Retorna un cliente Horizon para la red configurada."""
    return Server(STELLAR_HORIZON_URL)


def _get_soroban_server() -> SorobanServer:
    """Retorna un cliente RPC Soroban para la red configurada."""
    return SorobanServer(STELLAR_RPC_URL)


# ============================================================================
# Información de cuenta
# ============================================================================


def get_account_info(public_key: str) -> Dict[str, Any]:
    """
    Obtiene la información de una cuenta Stellar desde Horizon.

    Args:
        public_key: Clave pública de la cuenta (Strkey G...)

    Returns:
        Dict con balances, sequence number y demás datos de la cuenta

    Raises:
        NotFoundError: Si la cuenta no existe en la red
        Exception: Error de red u otro error inesperado
    """
    server = _get_horizon_server()
    try:
        account = server.accounts().account_id(public_key).call()
        return account
    except NotFoundError:
        logging.warning(f"Cuenta Stellar no encontrada: {public_key}")
        raise
    except Exception as e:
        logging.error(f"Error al obtener cuenta Stellar {public_key}: {e}")
        raise


def get_xlm_balance(public_key: str) -> str:
    """
    Obtiene el saldo nativo XLM de una cuenta.

    Args:
        public_key: Clave pública de la cuenta (Strkey G...)

    Returns:
        Saldo XLM como string (ej. "100.0000000")
    """
    account_data = get_account_info(public_key)
    for balance in account_data.get("balances", []):
        if balance.get("asset_type") == "native":
            return balance.get("balance", "0.0000000")
    return "0.0000000"


# ============================================================================
# Construcción y envío de transacciones Stellar clásicas
# ============================================================================


def build_and_sign_transaction(
    secret_key: str,
    operations: list,
    memo: Optional[str] = None,
    timeout: int = 30,
) -> str:
    """
    Construye, firma con Ed25519 y envía una transacción Stellar clásica.

    Args:
        secret_key: Clave secreta del firmante (Strkey S...)
        operations: Lista de operaciones Stellar (Payment, ManageData, etc.)
        memo: Memo de texto opcional para la transacción
        timeout: Validez de la transacción en segundos

    Returns:
        Hash de la transacción enviada

    Raises:
        Exception: Si hay error al construir, firmar o enviar la transacción
    """
    keypair = Keypair.from_secret(secret_key)
    server = _get_horizon_server()

    source_account = server.load_account(keypair.public_key)
    base_fee = server.fetch_base_fee()

    builder = TransactionBuilder(
        source_account=source_account,
        network_passphrase=STELLAR_NETWORK_PASSPHRASE,
        base_fee=base_fee,
    )

    for operation in operations:
        builder.append_operation(operation)

    if memo:
        builder.add_text_memo(memo)

    builder.set_timeout(timeout)
    transaction = builder.build()

    # Firma Ed25519 con la clave privada Stellar
    transaction.sign(keypair)

    try:
        response = server.submit_transaction(transaction)
        tx_hash = response.get("hash", "")
        logging.info(f"Transaccion Stellar enviada: {tx_hash}")
        return tx_hash
    except Exception as e:
        logging.error(f"Error al enviar transaccion Stellar: {e}")
        raise


# ============================================================================
# Parseo de eventos Soroban
# ============================================================================


def _parse_user_mint_amount_from_events(events_obj: Any) -> int:
    """
    Extrae el campo `amount` del evento UserMint o UserMintWithToken emitido
    por el contrato LunarXY.

    Usa tx_response.events.contract_events_xdr, que es la lista de
    ContractEvent por operación devuelta directamente por el RPC Soroban.
    Es más fiable que parsear result_meta_xdr porque el RPC ya extrae
    y expone los eventos del contrato sin importar la versión de meta (v3/v4).

    El macro #[contractevent] de soroban-sdk convierte el nombre del struct
    a snake_case para el topic de prefijo, por lo que:
      UserMint          → topic[0] = SCV_SYMBOL(b"user_mint")
      UserMintWithToken → topic[0] = SCV_SYMBOL(b"user_mint_with_token")

    Layout del evento:
      topics: [SCV_SYMBOL("user_mint"|"user_mint_with_token"), SCV_ADDRESS(caller)]
      data:   SCV_MAP { "amount": i128, "nonce": u64, "uid": u64, ... }

    Args:
        events_obj: tx_response.events (instancia de soroban_rpc.Events o None)

    Returns:
        El valor de `amount` como int, o 0 si no se encuentra el evento.
    """
    from stellar_sdk.xdr import ContractEvent

    if events_obj is None:
        return 0

    # contract_events_xdr: list[list[str]] — una lista por operación,
    # cada elemento es un ContractEvent en base64 XDR
    contract_events_xdr = getattr(events_obj, "contract_events_xdr", None)
    if not contract_events_xdr:
        return 0

    # El macro genera el topic de prefijo en snake_case
    target_names = {b"user_mint", b"user_mint_with_token"}

    try:
        for op_events in contract_events_xdr:
            for event_xdr in op_events:
                event = ContractEvent.from_xdr(event_xdr)
                if event.type != ContractEventType.CONTRACT:
                    continue
                body_v0 = event.body.v0
                if body_v0 is None:
                    continue
                topics = body_v0.topics
                if not topics:
                    continue
                first = topics[0]
                # El primer topic es SCV_SYMBOL con el nombre del evento (type value = 15)
                if first.type.value != 15:
                    continue
                if first.sym is None:
                    continue
                if first.sym.sc_symbol not in target_names:
                    continue

                # data es SCV_MAP — buscar la clave "amount"
                data = body_v0.data
                if data.map is None:
                    continue
                for entry in data.map.sc_map:
                    key = entry.key
                    if key.type.value != 15:  # SCV_SYMBOL
                        continue
                    if key.sym is None or key.sym.sc_symbol != b"amount":
                        continue
                    val = entry.val
                    if val.i128 is None:
                        continue
                    # amount es i128: reconstruir desde hi (Int64) y lo (Uint64)
                    hi = val.i128.hi.int64
                    lo = val.i128.lo.uint64
                    return (hi << 64) | lo

    except Exception as e:
        logging.warning(f"No se pudo parsear el evento UserMint: {e}")

    return 0


# ============================================================================
# Espera de transacciones Soroban
# ============================================================================


def invoke_soroban_contract(
    secret_key: str,
    contract_id: str,
    function_name: str,
    args: Optional[List[Any]] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Invoca una función de un contrato Soroban (smart contract Stellar).
    Maneja automáticamente la simulación y el envío de la transacción.

    Args:
        secret_key: Clave secreta del invocador (Strkey S...)
        contract_id: Contract ID en formato Strkey (C...) o dirección hex
        function_name: Nombre de la función del contrato a invocar
        args: Lista de argumentos XDR para la función del contrato
        timeout: Validez de la transacción en segundos

    Returns:
        Dict con:
            - hash: Hash de la transacción
            - status: Estado final de la transacción
            - result: Valor de retorno de la función (si aplica)

    Raises:
        Exception: Si la simulación falla, si la transacción es rechazada,
                   o si hay error de red
    """

    keypair = Keypair.from_secret(secret_key)
    soroban_server = _get_soroban_server()

    source_account = soroban_server.load_account(keypair.public_key)
    base_fee = 100  # stroops — el soroban server no expone fetch_base_fee

    builder = TransactionBuilder(
        source_account=source_account,
        network_passphrase=STELLAR_NETWORK_PASSPHRASE,
        base_fee=base_fee,
    )

    builder.append_invoke_contract_function_op(
        contract_id=contract_id,
        function_name=function_name,
        parameters=args or [],
    )
    builder.set_timeout(timeout)
    transaction = builder.build()

    # Simular la transacción para obtener los recursos necesarios
    simulation = soroban_server.simulate_transaction(transaction)
    if simulation.error:
        logging.error(
            f"Error en simulacion Soroban ({function_name}): {simulation.error}"
        )
        raise Exception(f"server.Error en simulacion del contrato: {simulation.error}")

    # Preparar la transacción con los recursos estimados por el simulador
    transaction = soroban_server.prepare_transaction(transaction, simulation)

    # Firma Ed25519
    transaction.sign(keypair)

    # Enviar la transacción
    response = soroban_server.send_transaction(transaction)
    tx_hash = response.hash

    logging.info(
        f"Transaccion Soroban enviada: {tx_hash} (contrato: {contract_id}, funcion: {function_name})"
    )

    return {
        "hash": tx_hash,
        "status": response.status,
        "result": None,
    }


def wait_for_soroban_transaction(
    tx_hash: str,
    timeout: int = 300,
    check_interval: int = 5,
) -> Dict[str, Any]:
    """
    Espera a que una transacción Soroban se confirme en la red.

    Args:
        tx_hash: Hash de la transacción a monitorizar
        timeout: Tiempo máximo de espera en segundos
        check_interval: Intervalo en segundos entre comprobaciones

    Returns:
        Dict con:
            - status: True si la transacción fue exitosa
            - message: Descripción del resultado
            - result: Valor de retorno XDR de la función (si existe)
            - transaction_hash: Hash de la transacción

    Raises:
        TimeoutError: Si se supera el tiempo máximo de espera
        Exception: Si la transacción falla o es rechazada
    """
    import time

    soroban_server = _get_soroban_server()
    elapsed = 0

    logging.info(f"Esperando confirmacion de transaccion Stellar: {tx_hash}")

    while elapsed < timeout:
        try:
            tx_response = soroban_server.get_transaction(tx_hash)
            status = tx_response.status

            if status == GetTransactionStatus.SUCCESS:
                result_xdr = getattr(tx_response, "result_xdr", None)
                events_obj = getattr(tx_response, "events", None)
                amount = _parse_user_mint_amount_from_events(events_obj)
                message = f"Transaccion {tx_hash} completada exitosamente"
                logging.info(message)
                return {
                    "status": True,
                    "message": message,
                    "result": result_xdr,
                    "tx": tx_hash,
                    "amount": amount,
                }

            elif status == GetTransactionStatus.FAILED:
                result_xdr = getattr(tx_response, "result_xdr", None)
                message = f"Transaccion {tx_hash} fallida"
                logging.error(message)
                return {
                    "status": False,
                    "message": message,
                    "result": result_xdr,
                    "tx": tx_hash,
                }

            # NOT_FOUND o PENDING — seguir esperando
            logging.debug(
                f"Transaccion {tx_hash} en estado {status} ({elapsed}s/{timeout}s)"
            )

        except Exception as e:
            logging.warning(f"Error al consultar transaccion {tx_hash}: {e}")

        time.sleep(check_interval)
        elapsed += check_interval

    raise TimeoutError(
        f"Timeout: La transaccion Stellar {tx_hash} no se confirmo en {timeout} segundos"
    )


def invoke_and_wait(
    secret_key: str,
    contract_id: str,
    function_name: str,
    args: Optional[List[Any]] = None,
    timeout: int = 300,
) -> Dict[str, Any]:
    """
    Invoca una función de contrato Soroban y espera su confirmación.
    Combina invoke_soroban_contract y wait_for_soroban_transaction.

    Args:
        secret_key: Clave secreta del invocador (Strkey S...)
        contract_id: Contract ID del contrato Soroban (C...)
        function_name: Nombre de la función a invocar
        args: Argumentos de la función
        timeout: Tiempo máximo de espera en segundos

    Returns:
        Dict con el resultado final de la transacción
    """
    invoke_result = invoke_soroban_contract(
        secret_key=secret_key,
        contract_id=contract_id,
        function_name=function_name,
        args=args,
    )

    return wait_for_soroban_transaction(
        tx_hash=invoke_result["hash"],
        timeout=timeout,
    )


# ============================================================================
# Consulta de estado de contrato (read-only)
# ============================================================================


def get_user_nonce(caller_public_key: str, contract_id: str) -> int:
    """
    Consulta el nonce on-chain actual de una cuenta en el contrato Soroban.
    Operación de solo lectura (simulación): no genera ninguna transacción ni gasta fees.

    Args:
        caller_public_key: Clave pública del usuario (Strkey G...)
        contract_id:       Contract ID del contrato Soroban (C...)

    Returns:
        Nonce actual como entero (u64). Devuelve 0 si la cuenta aún no ha minteado.

    Raises:
        Exception: Si la simulación falla o el contrato no responde
    """
    from stellar_sdk import scval
    from stellar_sdk.xdr import SCVal

    xdr_str = simulate_soroban_call(
        caller_public_key=caller_public_key,
        contract_id=contract_id,
        function_name="get_nonce",
        args=[scval.to_address(caller_public_key)],
    )

    if xdr_str is None:
        return 0

    try:
        sc_val = SCVal.from_xdr(xdr_str)
        if sc_val.u64 is None:
            logging.warning(f"Nonce SCVal no es u64: {xdr_str}")
            return 0
        return sc_val.u64.uint64
    except Exception:
        logging.warning(f"No se pudo extraer nonce del XDR: {xdr_str}")
        return 0


def simulate_soroban_call(
    caller_public_key: str,
    contract_id: str,
    function_name: str,
    args: Optional[List[Any]] = None,
) -> Any:
    """
    Simula (sin enviar) una llamada a un contrato Soroban para leer estado.
    Equivalente a una llamada `view` en Ethereum.

    Args:
        caller_public_key: Clave pública del invocador (Strkey G...)
        contract_id: Contract ID del contrato (C...)
        function_name: Nombre de la función a consultar
        args: Argumentos de la función

    Returns:
        Resultado XDR de la simulación

    Raises:
        Exception: Si la simulación falla
    """
    soroban_server = _get_soroban_server()
    source_account = soroban_server.load_account(caller_public_key)

    builder = TransactionBuilder(
        source_account=source_account,
        network_passphrase=STELLAR_NETWORK_PASSPHRASE,
        base_fee=100,
    )
    builder.append_invoke_contract_function_op(
        contract_id=contract_id,
        function_name=function_name,
        parameters=args or [],
    )
    builder.set_timeout(30)
    transaction = builder.build()

    simulation = soroban_server.simulate_transaction(transaction)
    if simulation.error:
        logging.error(
            f"Error en simulacion read-only ({function_name}): {simulation.error}"
        )
        raise Exception(f"server.Error al consultar el contrato: {simulation.error}")

    if not simulation.results:
        return None
    return simulation.results[0].xdr  # base64-encoded SCVal XDR


# ============================================================================
# CompliantId contract
# ============================================================================

# Valores válidos para ComplianceStatus (enum en el contrato Rust)
COMPLIANCE_STATUS_VALUES = {"Unverified", "Verified", "Suspended", "Revoked"}


def set_compliance(
    issuer_secret_key: str,
    contract_id: str,
    user_public_key: str,
    status: str,
    level: int,
    expires_at: int,
    country_code: str,
    wait: bool = True,
    timeout: int = 300,
) -> Dict[str, Any]:
    """
    Invoca la función set_compliance del contrato CompliantId en Stellar/Soroban.

    Crea o actualiza el registro de cumplimiento KYC/AML de un usuario.
    Solo puede ser llamada por un emisor de confianza (trusted issuer) registrado
    en el contrato. La firma Ed25519 del emisor se genera automáticamente.

    Firma del contrato Rust:
        set_compliance(env, issuer, user, status, level, expires_at, country_code)

    Args:
        issuer_secret_key: Clave secreta del emisor de confianza (Strkey S...).
                           El emisor debe estar previamente registrado como
                           trusted issuer en el contrato.
        contract_id:       Contract ID del contrato CompliantId desplegado (C...).
        user_public_key:   Clave pública del usuario a registrar (Strkey G...).
        status:            Estado de cumplimiento. Uno de:
                           "Unverified" | "Verified" | "Suspended" | "Revoked"
        level:             Nivel de verificación (entero >= 1).
                           Ej. 1 = KYC básico, 2 = KYC avanzado.
        expires_at:        Timestamp Unix (segundos) de expiración del registro.
                           Debe ser una fecha futura.
        country_code:      Código ISO del país del usuario (ej. "ES", "US").
                           Máximo 32 caracteres (límite de Symbol en Soroban).
        wait:              Si True (por defecto), bloquea hasta confirmar la tx
                           on-chain. Si False, retorna inmediatamente con el hash.
        timeout:           Tiempo máximo de espera en segundos (sólo aplica si
                           wait=True). Por defecto 300s.

    Returns:
        Si wait=True:
            Dict con claves "status" (bool), "message" (str), "result" (XDR|None),
            "transaction_hash" (str).
        Si wait=False:
            Dict con claves "hash" (str), "status" (str del RPC).

    Raises:
        ValueError: Si alguno de los parámetros no supera las validaciones previas.
        Exception:  Si la simulación Soroban falla, o si hay error de red.
    """
    import time
    from stellar_sdk import scval

    # --- Validaciones previas ---
    if status not in COMPLIANCE_STATUS_VALUES:
        raise ValueError(
            f"server.Estado de cumplimiento invalido: '{status}'. "
            f"Valores permitidos: {sorted(COMPLIANCE_STATUS_VALUES)}"
        )
    if level < 1:
        raise ValueError(
            f"server.El nivel de cumplimiento debe ser >= 1, recibido: {level}"
        )
    if expires_at <= int(time.time()):
        raise ValueError("server.La fecha de expiracion debe ser futura")
    if not country_code:
        raise ValueError("server.El codigo de pais no puede estar vacio")

    # --- Construcción de argumentos XDR ---
    # Orden idéntico a la firma Rust (env se inyecta por el SDK, no se pasa):
    #   issuer: Address, user: Address, status: ComplianceStatus,
    #   level: u32, expires_at: u64, country_code: Symbol
    issuer_keypair = Keypair.from_secret(issuer_secret_key)

    args = [
        scval.to_address(issuer_keypair.public_key),  # issuer (Address)
        scval.to_address(user_public_key),  # user (Address)
        scval.to_enum(status, None),  # status (ComplianceStatus enum)
        scval.to_uint32(level),  # level (u32)
        scval.to_uint64(expires_at),  # expires_at (u64)
        scval.to_symbol(country_code),  # country_code (Symbol)
    ]

    logging.info(
        f"set_compliance: user={user_public_key} status={status} "
        f"level={level} country={country_code} expires_at={expires_at}"
    )

    if wait:
        return invoke_and_wait(
            secret_key=issuer_secret_key,
            contract_id=contract_id,
            function_name="set_compliance",
            args=args,
            timeout=timeout,
        )
    else:
        return invoke_soroban_contract(
            secret_key=issuer_secret_key,
            contract_id=contract_id,
            function_name="set_compliance",
            args=args,
        )


def is_trusted_issuer(
    issuer_public_key: str,
    contract_id: str,
) -> bool:
    """
    Verifica si una dirección es un emisor de confianza registrado en el contrato CompliantId.

    Consulta read-only (simulación): no genera transacción ni gasta fees.

    Firma del contrato Rust:
        is_trusted_issuer(env, issuer: Address) -> bool

    Args:
        issuer_public_key: Clave pública a verificar (Strkey G...)
        contract_id:       Contract ID del contrato CompliantId desplegado (C...)

    Returns:
        True si la dirección está registrada como trusted issuer, False si no lo está.

    Raises:
        Exception: Si la simulación falla o hay error de red.
    """
    from stellar_sdk import scval
    from stellar_sdk.xdr import SCVal

    xdr_str = simulate_soroban_call(
        caller_public_key=issuer_public_key,
        contract_id=contract_id,
        function_name="is_trusted_issuer",
        args=[scval.to_address(issuer_public_key)],
    )

    if xdr_str is None:
        return False

    try:
        sc_val = SCVal.from_xdr(xdr_str)
        return bool(sc_val.b)
    except Exception:
        logging.warning(f"No se pudo extraer bool del XDR is_trusted_issuer: {xdr_str}")
        return False


def add_trusted_issuer(
    admin_secret_key: str,
    contract_id: str,
    issuer_public_key: str,
    wait: bool = True,
    timeout: int = 300,
) -> Dict[str, Any]:
    """
    Registra una dirección como emisor de confianza (trusted issuer) en el contrato CompliantId.

    Solo el admin del contrato puede invocar esta función.

    Firma del contrato Rust:
        add_trusted_issuer(env, admin: Address, issuer: Address) -> Result<(), CompliantIdError>

    Args:
        admin_secret_key:  Clave secreta del admin del contrato (Strkey S...).
        contract_id:       Contract ID del contrato CompliantId desplegado (C...).
        issuer_public_key: Clave pública de la dirección a registrar como
                           trusted issuer (Strkey G...).
        wait:              Si True (por defecto), bloquea hasta confirmar la tx
                           on-chain. Si False, retorna inmediatamente con el hash.
        timeout:           Tiempo máximo de espera en segundos (sólo aplica si
                           wait=True). Por defecto 300s.

    Returns:
        Si wait=True:
            Dict con claves "status" (bool), "message" (str), "result" (XDR|None),
            "transaction_hash" (str).
        Si wait=False:
            Dict con claves "hash" (str), "status" (str del RPC).

    Raises:
        ValueError: Si alguno de los parámetros no supera las validaciones previas.
        Exception:  Si la simulación Soroban falla, o si hay error de red.
                    AlreadyTrustedIssuer se propaga como excepción si el issuer
                    ya estaba registrado.
    """
    from stellar_sdk import scval

    # --- Validaciones previas ---
    if not admin_secret_key:
        raise ValueError("server.La clave secreta del admin no puede estar vacia")
    if not issuer_public_key or not issuer_public_key.startswith("G"):
        raise ValueError(
            f"server.Clave publica del issuer invalida: '{issuer_public_key}'"
        )

    # --- Construcción de argumentos XDR ---
    # Orden idéntico a la firma Rust (env se inyecta por el SDK, no se pasa):
    #   admin: Address, issuer: Address
    admin_keypair = Keypair.from_secret(admin_secret_key)

    args = [
        scval.to_address(admin_keypair.public_key),  # admin (Address)
        scval.to_address(issuer_public_key),  # issuer (Address)
    ]

    logging.info(
        f"add_trusted_issuer: issuer={issuer_public_key} "
        f"admin={admin_keypair.public_key}"
    )

    if wait:
        return invoke_and_wait(
            secret_key=admin_secret_key,
            contract_id=contract_id,
            function_name="add_trusted_issuer",
            args=args,
            timeout=timeout,
        )
    else:
        return invoke_soroban_contract(
            secret_key=admin_secret_key,
            contract_id=contract_id,
            function_name="add_trusted_issuer",
            args=args,
        )


def is_compliant(
    user_public_key: str,
    contract_id: str,
    min_level: int = 1,
) -> bool:
    """
    Verifica si un usuario cumple los requisitos de compliance en el contrato CompliantId.

    Consulta read-only (simulación): no genera transacción ni gasta fees.

    Retorna True si:
      - El registro del usuario tiene status == Verified
      - El nivel del registro >= min_level
      - El registro no ha expirado

    Firma del contrato Rust:
        is_compliant(env, user: Address, min_level: u32) -> bool

    Args:
        user_public_key: Clave pública del usuario a verificar (Strkey G...)
        contract_id:     Contract ID del contrato CompliantId desplegado (C...)
        min_level:       Nivel mínimo de verificación requerido (>= 1). Por defecto 1.

    Returns:
        True si el usuario es compliant, False si no lo es o no tiene registro.

    Raises:
        Exception: Si la simulación falla o hay error de red.
    """
    from stellar_sdk import scval
    from stellar_sdk.xdr import SCVal

    xdr_str = simulate_soroban_call(
        caller_public_key=user_public_key,
        contract_id=contract_id,
        function_name="is_compliant",
        args=[
            scval.to_address(user_public_key),  # user (Address)
            scval.to_uint32(min_level),          # min_level (u32)
        ],
    )

    if xdr_str is None:
        return False

    try:
        sc_val = SCVal.from_xdr(xdr_str)
        return bool(sc_val.b)
    except Exception:
        logging.warning(f"No se pudo extraer bool del XDR is_compliant: {xdr_str}")
        return False
