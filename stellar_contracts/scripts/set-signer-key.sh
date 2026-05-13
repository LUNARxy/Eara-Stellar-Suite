#!/usr/bin/env bash
# =============================================================================
# set-signer-key.sh — Set the Ed25519 signer key for user_mint on lunarxy-token
#
# Extracts the raw 32-byte Ed25519 public key from a PEM file and calls
# set_signer_key on the deployed contract. Any single registered admin can
# perform this operation.
#
# Usage:
#   ./scripts/set-signer-key.sh [flags]
#
# Flags:
#   --network <testnet|mainnet|local>   Target network (default: testnet)
#   --source <profile>                  stellar keys profile name (default: admin1)
#   --pem <path>                        Ed25519 private key PEM file (default: ./private.pem)
#   --contract-id <C...>                Contract address (auto-loaded from deployed/<network>.env)
#
# Example:
#   ./scripts/set-signer-key.sh
#   ./scripts/set-signer-key.sh --network testnet --source admin1 --pem ./private.pem
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Colour helpers — all log output goes to stderr
# ---------------------------------------------------------------------------
if [ -t 2 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; RESET=''
fi

log_info()    { echo -e "${CYAN}[INFO]${RESET}  $*" >&2; }
log_success() { echo -e "${GREEN}[OK]${RESET}    $*" >&2; }
log_warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*" >&2; }
log_error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
die()         { log_error "$*"; exit 1; }
header()      { echo -e "\n${BOLD}==> $*${RESET}" >&2; }

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEPLOYED_DIR="${REPO_ROOT}/deployed"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
NETWORK="testnet"
SOURCE="admin1"
PEM="${REPO_ROOT}/private.pem"
CONTRACT_ID=""

# ---------------------------------------------------------------------------
# Arg parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --network)     NETWORK="$2";     shift 2 ;;
    --source)      SOURCE="$2";      shift 2 ;;
    --pem)         PEM="$2";         shift 2 ;;
    --contract-id) CONTRACT_ID="$2"; shift 2 ;;
    --help|-h)
      sed -n '/^# Usage:/,/^# ====/p' "$0" | grep '^#' | sed 's/^# \?//'
      exit 0 ;;
    *) die "Unknown flag: $1. Use --help for usage." ;;
  esac
done

# ---------------------------------------------------------------------------
# Prerequisite checks
# ---------------------------------------------------------------------------
command -v stellar &>/dev/null || die "'stellar' CLI not found."
command -v openssl &>/dev/null || die "'openssl' not found."
command -v xxd     &>/dev/null || die "'xxd' not found."

# ---------------------------------------------------------------------------
# Validate network
# ---------------------------------------------------------------------------
case "$NETWORK" in
  testnet|mainnet|local|futurenet) ;;
  *) die "Unknown network '${NETWORK}'. Valid: testnet, mainnet, local" ;;
esac

# ---------------------------------------------------------------------------
# Validate PEM file
# ---------------------------------------------------------------------------
[[ -f "$PEM" ]] || die "PEM file not found: ${PEM}"

# Confirm it is an Ed25519 key
KEY_TYPE=$(openssl pkey -in "$PEM" -text -noout 2>/dev/null | grep 'ED25519' || true)
[[ -n "$KEY_TYPE" ]] || die "The PEM file does not appear to be an Ed25519 key: ${PEM}"

# ---------------------------------------------------------------------------
# Auto-load contract ID from deployed/<network>.env
# ---------------------------------------------------------------------------
if [[ -z "$CONTRACT_ID" ]]; then
  ENV_FILE="${DEPLOYED_DIR}/${NETWORK}.env"
  if [[ -f "$ENV_FILE" ]]; then
    CONTRACT_ID=$(grep '^CONTRACT_ID=' "$ENV_FILE" | cut -d= -f2 || true)
    [[ -n "$CONTRACT_ID" ]] && log_warn "No --contract-id provided. Using saved value from ${ENV_FILE}: ${CONTRACT_ID}"
  fi
fi
[[ -z "$CONTRACT_ID" ]] && die "--contract-id is required (or run deploy first to save it automatically)"

# ---------------------------------------------------------------------------
# Resolve admin address from stellar keys profile
# ---------------------------------------------------------------------------
ADMIN=$(stellar keys address "$SOURCE" 2>/dev/null || true)
[[ -z "$ADMIN" ]] && die "Could not resolve address for profile '${SOURCE}'. Is it a valid stellar keys profile?"

# ---------------------------------------------------------------------------
# Extract raw 32-byte Ed25519 public key from PEM → hex
# DER encoding of an Ed25519 public key is 44 bytes: 12-byte header + 32-byte key
# ---------------------------------------------------------------------------
SIGNER_KEY=$(openssl pkey -in "$PEM" -pubout -outform DER 2>/dev/null | tail -c 32 | xxd -p -c 32)
[[ ${#SIGNER_KEY} -eq 64 ]] || die "Failed to extract 32-byte public key from PEM (got ${#SIGNER_KEY} hex chars, expected 64)."

# ---------------------------------------------------------------------------
# Mainnet guard
# ---------------------------------------------------------------------------
if [[ "$NETWORK" == "mainnet" ]]; then
  log_warn "You are calling set_signer_key on MAINNET. This will consume real XLM."
  read -r -p "Type 'yes' to continue: " confirm
  [[ "$confirm" == "yes" ]] || die "Aborted."
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
header "Setting signer key on ${NETWORK}"
log_info "Contract:   ${CONTRACT_ID}"
log_info "Admin:      ${ADMIN} (${SOURCE})"
log_info "PEM file:   ${PEM}"
log_info "Signer key: ${SIGNER_KEY}"

# ---------------------------------------------------------------------------
# Invoke set_signer_key
# ---------------------------------------------------------------------------
stellar contract invoke \
  --id "${CONTRACT_ID}" \
  --source "${SOURCE}" \
  --network "${NETWORK}" \
  -- set_signer_key \
  --admin "${ADMIN}" \
  --signer_key "${SIGNER_KEY}"

log_success "set_signer_key complete!"

# ---------------------------------------------------------------------------
# Verify: read back the value
# ---------------------------------------------------------------------------
header "Verifying — calling get_signer_key"
RESULT=$(stellar contract invoke \
  --id "${CONTRACT_ID}" \
  --source "${SOURCE}" \
  --network "${NETWORK}" \
  -- get_signer_key 2>&1 | grep -v '^$' | grep -v $'^ℹ' | tail -1 || true)

log_info "Stored signer key: ${RESULT}"
log_success "Done."
