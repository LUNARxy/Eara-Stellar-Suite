#!/usr/bin/env bash
# =============================================================================
# pem-to-strkey.sh — Convert an Ed25519 PEM private key to Stellar Strkey S...
#
# Extracts the raw 32-byte Ed25519 seed from an OpenSSL PEM file and outputs
# the Stellar-compatible Strkey secret (S...) and public key (G...).
#
# Usage:
#   ./scripts/pem-to-strkey.sh [--pem path/to/private.pem]
#
# Flags:
#   --pem <path>   Ed25519 private key PEM file (default: ./private.pem)
#
# Output:
#   Secret key (S...) — use with stellar_sdk.Keypair.from_secret() in Python
#   Public key (G...) — should match the signer key registered in the contract
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------
if [ -t 2 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; RESET=''
fi

log_info()    { echo -e "${CYAN}[INFO]${RESET}  $*" >&2; }
log_success() { echo -e "${GREEN}[OK]${RESET}    $*" >&2; }
log_error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
die()         { log_error "$*"; exit 1; }
header()      { echo -e "\n${BOLD}==> $*${RESET}" >&2; }

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PEM="${REPO_ROOT}/private.pem"

# ---------------------------------------------------------------------------
# Arg parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --pem)     PEM="$2"; shift 2 ;;
    --help|-h)
      sed -n '/^# Usage:/,/^# ====/p' "$0" | grep '^#' | sed 's/^# \?//'
      exit 0 ;;
    *) die "Unknown flag: $1. Use --help for usage." ;;
  esac
done

# ---------------------------------------------------------------------------
# Prerequisite checks
# ---------------------------------------------------------------------------
command -v openssl &>/dev/null || die "'openssl' not found."
command -v xxd     &>/dev/null || die "'xxd' not found."
command -v python3 &>/dev/null || die "'python3' not found."

# ---------------------------------------------------------------------------
# Validate PEM
# ---------------------------------------------------------------------------
[[ -f "$PEM" ]] || die "PEM file not found: ${PEM}"

KEY_TYPE=$(openssl pkey -in "$PEM" -text -noout 2>/dev/null | grep 'ED25519' || true)
[[ -n "$KEY_TYPE" ]] || die "The PEM file does not appear to be an Ed25519 key: ${PEM}"

# ---------------------------------------------------------------------------
# Extract raw 32-byte seed from PEM
# DER encoding: 48 bytes = 16-byte ASN.1 header + 32-byte seed
# ---------------------------------------------------------------------------
RAW_SEED_HEX=$(openssl pkey -in "$PEM" -outform DER 2>/dev/null | tail -c 32 | xxd -p -c 32)
[[ ${#RAW_SEED_HEX} -eq 64 ]] || die "Failed to extract 32-byte seed (got ${#RAW_SEED_HEX} hex chars, expected 64)."

# Also extract the public key for cross-verification
RAW_PUB_HEX=$(openssl pkey -in "$PEM" -pubout -outform DER 2>/dev/null | tail -c 32 | xxd -p -c 32)

header "Converting PEM to Stellar Strkey"
log_info "PEM file:       ${PEM}"
log_info "Raw seed (hex): ${RAW_SEED_HEX}"
log_info "Raw pub  (hex): ${RAW_PUB_HEX}"

# ---------------------------------------------------------------------------
# Convert to Strkey using Python
# Tries stellar_sdk first; falls back to pure-Python CRC-16 + base32
# ---------------------------------------------------------------------------
RESULT=$(python3 - "$RAW_SEED_HEX" "$RAW_PUB_HEX" <<'PYEOF'
import sys

raw_seed_hex = sys.argv[1]
raw_pub_hex  = sys.argv[2]
raw_seed = bytes.fromhex(raw_seed_hex)

try:
    from stellar_sdk import Keypair
    kp = Keypair.from_raw_ed25519_seed(raw_seed)
    secret = kp.secret
    public = kp.public_key
except ImportError:
    # Fallback: pure-Python Strkey encoding (no external dependencies)
    import base64, struct

    def crc16_xmodem(data: bytes) -> int:
        crc = 0x0000
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return crc

    def to_strkey(version_byte: int, payload: bytes) -> str:
        body = bytes([version_byte]) + payload
        checksum = struct.pack('<H', crc16_xmodem(body))
        return base64.b32encode(body + checksum).decode('ascii').rstrip('=')

    # Stellar Strkey version bytes are the type enum left-shifted by 3:
    #   seed (S...)    = 18 << 3 = 144 (0x90)
    #   account (G...) =  6 << 3 =  48 (0x30)
    secret = to_strkey(18 << 3, raw_seed)
    public = to_strkey(6 << 3, bytes.fromhex(raw_pub_hex))

# Verify the public key matches what OpenSSL extracted
try:
    from stellar_sdk import Keypair as Kp2
    kp_verify = Kp2.from_secret(secret)
    derived_pub_hex = kp_verify.raw_public_key().hex()
    if derived_pub_hex != raw_pub_hex:
        print(f"MISMATCH|derived={derived_pub_hex}|pem={raw_pub_hex}", file=sys.stderr)
        sys.exit(1)
except ImportError:
    pass  # skip verification if stellar_sdk unavailable

print(f"{secret}|{public}")
PYEOF
)

if [[ $? -ne 0 ]]; then
  die "Python conversion failed."
fi

SECRET_KEY=$(echo "$RESULT" | cut -d'|' -f1)
PUBLIC_KEY=$(echo "$RESULT" | cut -d'|' -f2)

echo >&2
log_success "Secret key (S...): ${SECRET_KEY}"
log_success "Public key (G...): ${PUBLIC_KEY}"
echo >&2
log_info "Use the S... key as the secret_key parameter in your Python backend:"
echo -e "  keypair = Keypair.from_secret(\"${SECRET_KEY}\")" >&2
echo >&2
log_info "Verify the signer key matches the contract (raw pub hex should be ${RAW_PUB_HEX}):"
echo -e "  ./scripts/deploy.sh info --network testnet" >&2

# Print just the secret to stdout for scripting: SECRET=$(./scripts/pem-to-strkey.sh)
echo "$SECRET_KEY"
