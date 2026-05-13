#!/usr/bin/env bash
# =============================================================================
# mint.sh — Mint tokens and query balances for simple-token (Soroban/testnet)
#
# Subcommands:
#   mint     Mint tokens to a wallet
#   balance  Query the balance of a wallet
#
# Usage:
#   ./scripts/mint.sh <subcommand> [flags]
#
# Examples:
#   ./scripts/mint.sh mint \
#       --to GCNHXQLKFKSAYBPCVZBTYNNFOZ7ESJOBGSNDPWPFT6HNDDCWPOPSHGFX \
#       --amount 100000000
#
#   ./scripts/mint.sh mint \
#       --contract-id CCWUQCCVISUVSI77F6ENS3O4PGUUHZJX4DLS3WYZEU4X7WGDY2TDILUR \
#       --source admin1 \
#       --network testnet \
#       --to GCNHXQLKFKSAYBPCVZBTYNNFOZ7ESJOBGSNDPWPFT6HNDDCWPOPSHGFX \
#       --amount 100000000
#
#   ./scripts/mint.sh balance \
#       --wallet GCNHXQLKFKSAYBPCVZBTYNNFOZ7ESJOBGSNDPWPFT6HNDDCWPOPSHGFX
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

info()    { echo -e "${CYAN}[INFO]${RESET}  $*" >&2; }
success() { echo -e "${GREEN}[OK]${RESET}    $*" >&2; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*" >&2; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
die()     { error "$*"; exit 1; }
header()  { echo -e "\n${BOLD}==> $*${RESET}" >&2; }

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEPLOYED_ENV="${REPO_ROOT}/deployed/testnet.env"

# ---------------------------------------------------------------------------
# Defaults (loaded from deployed/testnet.env when available)
# ---------------------------------------------------------------------------
DEFAULT_CONTRACT_ID=""
DEFAULT_SOURCE="admin1"
DEFAULT_NETWORK="testnet"
DEFAULT_DECIMALS=7

if [[ -f "$DEPLOYED_ENV" ]]; then
  _saved_id=$(grep '^SIMPLE_TOKEN_CONTRACT_ID=' "$DEPLOYED_ENV" | cut -d= -f2 || true)
  [[ -n "$_saved_id" ]] && DEFAULT_CONTRACT_ID="$_saved_id"
fi

# ---------------------------------------------------------------------------
# Prerequisite check
# ---------------------------------------------------------------------------
check_prereqs() {
  if ! command -v stellar &>/dev/null; then
    die "'stellar' CLI not found. Install it from https://developers.stellar.org/docs/tools/stellar-cli"
  fi
}

# ---------------------------------------------------------------------------
# Format raw stroop amount as human-readable token amount
# e.g. 1000000000000000 (7 decimals) → "100,000,000.0000000 SUSD"
# ---------------------------------------------------------------------------
format_amount() {
  local raw="$1" decimals="${2:-$DEFAULT_DECIMALS}" symbol="${3:-tokens}"
  python3 -c "
raw = int('${raw}')
dec = ${decimals}
whole = raw // (10**dec)
frac = raw % (10**dec)
human = f'{whole:,}.{frac:0{dec}d}'
print(f'{human} ${symbol}')
" 2>/dev/null || echo "${raw} (raw stroops)"
}

# ---------------------------------------------------------------------------
# Strip CLI informational lines from invoke output; return last value line
# ---------------------------------------------------------------------------
parse_invoke_output() {
  grep -v '^$' \
    | grep -v $'^ℹ' \
    | grep -v '^[[:space:]]*$' \
    | tail -1 \
    || echo ""
}

# ---------------------------------------------------------------------------
# subcommand: mint
# ---------------------------------------------------------------------------
subcmd_mint() {
  local contract_id="$DEFAULT_CONTRACT_ID"
  local source="$DEFAULT_SOURCE"
  local network="$DEFAULT_NETWORK"
  local to="" amount=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --contract-id) contract_id="$2"; shift 2 ;;
      --source)      source="$2";      shift 2 ;;
      --network)     network="$2";     shift 2 ;;
      --to)          to="$2";          shift 2 ;;
      --amount)      amount="$2";      shift 2 ;;
      *) die "Unknown flag: $1" ;;
    esac
  done

  [[ -z "$contract_id" ]] && die "--contract-id is required (or set SIMPLE_TOKEN_CONTRACT_ID in deployed/testnet.env)"
  [[ -z "$to"          ]] && die "--to is required (destination G... address)"
  [[ -z "$amount"      ]] && die "--amount is required (token units, NOT stroops — e.g. 100000000 for 100M tokens)"

  # Validate that --amount is a positive integer
  if ! [[ "$amount" =~ ^[0-9]+$ ]] || [[ "$amount" -eq 0 ]]; then
    die "--amount must be a positive integer (token units with 7 implied decimals)"
  fi

  # Convert human units → stroops (multiply by 10^7)
  local stroops
  stroops=$(python3 -c "print(int('${amount}') * 10**${DEFAULT_DECIMALS})")

  # Resolve admin address from source key profile
  local admin
  admin=$(stellar keys address "${source}" 2>/dev/null || true)
  [[ -z "$admin" ]] && die "Could not resolve address for source profile '${source}'"

  header "Minting tokens"
  info "Contract:  ${contract_id}"
  info "Network:   ${network}"
  info "Admin:     ${admin} (${source})"
  info "To:        ${to}"
  info "Amount:    $(format_amount "$stroops")"

  stellar contract invoke \
    --id "${contract_id}" \
    --source "${source}" \
    --network "${network}" \
    -- mint \
    --admin "${admin}" \
    --to "${to}" \
    --amount "${stroops}" \
    >&2

  success "Mint complete!"

  # Query resulting balance
  echo >&2
  info "Querying new balance for ${to}..."
  local raw_balance
  raw_balance=$(stellar contract invoke \
    --id "${contract_id}" \
    --source "${source}" \
    --network "${network}" \
    -- balance \
    --id "${to}" \
    2>&1 | parse_invoke_output)

  # Strip surrounding quotes if present
  raw_balance="${raw_balance//\"/}"

  echo -e "  ${BOLD}New balance:${RESET} $(format_amount "$raw_balance")" >&2
  echo -e "  ${BOLD}Raw stroops:${RESET} ${raw_balance}" >&2
}

# ---------------------------------------------------------------------------
# subcommand: balance
# ---------------------------------------------------------------------------
subcmd_balance() {
  local contract_id="$DEFAULT_CONTRACT_ID"
  local source="$DEFAULT_SOURCE"
  local network="$DEFAULT_NETWORK"
  local wallet=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --contract-id) contract_id="$2"; shift 2 ;;
      --source)      source="$2";      shift 2 ;;
      --network)     network="$2";     shift 2 ;;
      --wallet)      wallet="$2";      shift 2 ;;
      *) die "Unknown flag: $1" ;;
    esac
  done

  [[ -z "$contract_id" ]] && die "--contract-id is required (or set SIMPLE_TOKEN_CONTRACT_ID in deployed/testnet.env)"
  [[ -z "$wallet"      ]] && die "--wallet is required (G... address)"

  header "Querying balance"
  info "Contract: ${contract_id}"
  info "Network:  ${network}"
  info "Wallet:   ${wallet}"

  local raw_balance
  raw_balance=$(stellar contract invoke \
    --id "${contract_id}" \
    --source "${source}" \
    --network "${network}" \
    -- balance \
    --id "${wallet}" \
    2>&1 | parse_invoke_output)

  raw_balance="${raw_balance//\"/}"

  echo >&2
  echo -e "  ${BOLD}Balance:${RESET}     $(format_amount "$raw_balance")" >&2
  echo -e "  ${BOLD}Raw stroops:${RESET} ${raw_balance}" >&2

  # Emit raw value to stdout for scripting
  echo "$raw_balance"
}

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
print_help() {
  cat <<EOF

${BOLD}simple-token mint utility${RESET}

Usage:
  $(basename "$0") <subcommand> [flags]

Subcommands:
  mint     Mint tokens to a wallet
  balance  Query the balance of a wallet

${BOLD}Flags — mint:${RESET}
  --to <G...>           Destination wallet address (required)
  --amount <n>          Amount in whole token units, 7 implied decimals
                        e.g. --amount 100000000 mints 100,000,000.0000000 tokens
  --contract-id <C...>  Contract address (default: SIMPLE_TOKEN_CONTRACT_ID from deployed/testnet.env)
  --source <profile>    stellar keys profile for the admin (default: admin1)
  --network <name>      Stellar network (default: testnet)

${BOLD}Flags — balance:${RESET}
  --wallet <G...>       Wallet address to query (required)
  --contract-id <C...>  Contract address (default: SIMPLE_TOKEN_CONTRACT_ID from deployed/testnet.env)
  --source <profile>    stellar keys profile for simulation (default: admin1)
  --network <name>      Stellar network (default: testnet)

${BOLD}Examples:${RESET}

  # Mint 100M tokens to a wallet (uses defaults from deployed/testnet.env)
  ./scripts/mint.sh mint \\
      --to GCNHXQLKFKSAYBPCVZBTYNNFOZ7ESJOBGSNDPWPFT6HNDDCWPOPSHGFX \\
      --amount 100000000

  # Mint with explicit flags
  ./scripts/mint.sh mint \\
      --contract-id CCWUQCCVISUVSI77F6ENS3O4PGUUHZJX4DLS3WYZEU4X7WGDY2TDILUR \\
      --source admin1 \\
      --network testnet \\
      --to GCNHXQLKFKSAYBPCVZBTYNNFOZ7ESJOBGSNDPWPFT6HNDDCWPOPSHGFX \\
      --amount 500000

  # Query balance
  ./scripts/mint.sh balance \\
      --wallet GCNHXQLKFKSAYBPCVZBTYNNFOZ7ESJOBGSNDPWPFT6HNDDCWPOPSHGFX

${BOLD}Notes:${RESET}
  - --amount is in whole token units (decimals = 7 are applied automatically).
    To mint 1 token, pass --amount 1. To mint 100M, pass --amount 100000000.
  - The contract defaults are loaded from deployed/testnet.env automatically.
  - The raw stroop balance is printed to stdout; human-readable info goes to stderr.
    This makes the balance subcommand scriptable: BAL=\$(./mint.sh balance --wallet G...)

EOF
}

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
main() {
  check_prereqs

  local subcommand="${1:-}"
  [[ -z "$subcommand" ]] && { print_help; exit 0; }
  shift

  case "$subcommand" in
    mint)           subcmd_mint    "$@" ;;
    balance)        subcmd_balance "$@" ;;
    help|--help|-h) print_help ;;
    *) die "Unknown subcommand '${subcommand}'. Use: mint | balance" ;;
  esac
}

main "$@"
