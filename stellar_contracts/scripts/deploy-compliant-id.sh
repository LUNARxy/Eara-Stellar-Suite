#!/usr/bin/env bash
# =============================================================================
# deploy-compliant-id.sh — Deploy / upgrade / info utility for CompliantID
#
# Subcommands:
#   deploy   Build + upload + instantiate the contract for the first time
#   upgrade  Build + upload new WASM (future-proof — contract needs upgrade fn)
#   info     Print current on-chain state (admin, issuers, restricted countries)
#
# Usage:
#   ./scripts/deploy-compliant-id.sh <subcommand> [flags]
#
# Examples:
#   ./scripts/deploy-compliant-id.sh deploy \
#       --network testnet \
#       --source admin1 \
#       --admin admin1
#
#   ./scripts/deploy-compliant-id.sh info \
#       --network testnet
#
#   ./scripts/deploy-compliant-id.sh upgrade \
#       --network testnet \
#       --source admin1
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Colour helpers — all log output goes to stderr so $() captures stay clean
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
# Script paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEPLOYED_DIR="${REPO_ROOT}/deployed"
WASM_PATH="${REPO_ROOT}/target/wasm32v1-none/release/compliant_id.wasm"

# ---------------------------------------------------------------------------
# Prerequisite check
# ---------------------------------------------------------------------------
check_prereqs() {
  if ! command -v stellar &>/dev/null; then
    die "'stellar' CLI not found. Install it from https://developers.stellar.org/docs/tools/stellar-cli"
  fi
}

# ---------------------------------------------------------------------------
# Validate --network value; echo normalised name
# ---------------------------------------------------------------------------
validate_network() {
  case "$1" in
    testnet|mainnet|local|futurenet) echo "$1" ;;
    "") die "--network is required (testnet | mainnet | local | futurenet)" ;;
    *)  die "Unknown network '${1}'. Valid values: testnet, mainnet, local, futurenet" ;;
  esac
}

# ---------------------------------------------------------------------------
# Build the WASM (output goes to stderr)
# ---------------------------------------------------------------------------
cmd_build() {
  header "Building compliant-id contract"
  (cd "${REPO_ROOT}" && stellar contract build) >&2
  [[ -f "$WASM_PATH" ]] || die "WASM not found at ${WASM_PATH} after build."
  success "WASM built: ${WASM_PATH}"
}

# ---------------------------------------------------------------------------
# Upload WASM — prints only the 64-char hex hash to stdout
# ---------------------------------------------------------------------------
upload_wasm() {
  local source="$1" network="$2"
  header "Uploading WASM to ${network}"

  local raw
  raw=$(stellar contract upload \
    --wasm "${WASM_PATH}" \
    --source "${source}" \
    --network "${network}" \
    2>&1)

  local wasm_hash
  wasm_hash=$(echo "$raw" | grep -E '^[0-9a-f]{64}$' | tail -1 || true)

  if [[ -z "$wasm_hash" ]]; then
    error "Could not parse wasm_hash from upload output:"
    echo "$raw" >&2
    die "Upload failed."
  fi

  success "WASM uploaded. Hash: ${wasm_hash}"
  echo "$wasm_hash"   # only this goes to stdout
}

# ---------------------------------------------------------------------------
# Resolve admin: if it looks like a G... address use it as-is,
# otherwise treat it as a stellar keys profile name and resolve.
# ---------------------------------------------------------------------------
resolve_admin() {
  local input="$1"
  if [[ "$input" =~ ^G[A-Z2-7]{55}$ ]]; then
    echo "$input"
  else
    local addr
    addr=$(stellar keys address "$input" 2>/dev/null || true)
    [[ -z "$addr" ]] && die "Could not resolve stellar keys address for profile '${input}'"
    echo "$addr"
  fi
}

# ---------------------------------------------------------------------------
# Save deployment state to deployed/<network>-compliant-id.env
# ---------------------------------------------------------------------------
save_deployed_env() {
  local network="$1" contract_id="$2" wasm_hash="$3" source="$4"
  local env_file="${DEPLOYED_DIR}/${network}-compliant-id.env"
  mkdir -p "${DEPLOYED_DIR}"
  cat > "${env_file}" <<EOF
# Auto-generated by scripts/deploy-compliant-id.sh — do not edit manually
CONTRACT_ID=${contract_id}
WASM_HASH=${wasm_hash}
NETWORK=${network}
SOURCE=${source}
DEPLOYED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF
  success "Deployment state saved to ${env_file}"
}

# ---------------------------------------------------------------------------
# Load contract-id from deployed/<network>-compliant-id.env (silent fallback)
# ---------------------------------------------------------------------------
load_contract_id() {
  local network="$1" contract_id_ref="$2"
  local env_file="${DEPLOYED_DIR}/${network}-compliant-id.env"
  if [[ -f "$env_file" ]]; then
    local saved_id
    saved_id=$(grep '^CONTRACT_ID=' "$env_file" | cut -d= -f2 || true)
    if [[ -n "$saved_id" ]]; then
      warn "No --contract-id provided. Using saved value from ${env_file}: ${saved_id}"
      eval "$contract_id_ref='$saved_id'"
    fi
  fi
}

# ---------------------------------------------------------------------------
# Load source from deployed/<network>-compliant-id.env
# ---------------------------------------------------------------------------
load_source() {
  local network="$1" source_ref="$2"
  local env_file="${DEPLOYED_DIR}/${network}-compliant-id.env"
  if [[ -f "$env_file" ]]; then
    local saved_source
    saved_source=$(grep '^SOURCE=' "$env_file" | cut -d= -f2 || true)
    if [[ -n "$saved_source" ]]; then
      eval "$source_ref='$saved_source'"
    fi
  fi
}

# ---------------------------------------------------------------------------
# Read-only contract invoke helper
#   _invoke_view <contract_id> <network> <source_or_empty> <fn>
# ---------------------------------------------------------------------------
_invoke_view() {
  local contract_id="$1" network="$2" source="$3" fn="$4"
  local source_args=()
  [[ -n "$source" ]] && source_args=(--source "$source")
  local out
  out=$(stellar contract invoke \
    --id "${contract_id}" \
    --network "${network}" \
    "${source_args[@]}" \
    -- "${fn}" 2>&1) || true
  # Strip CLI informational lines; keep the last substantive line (the value)
  echo "$out" \
    | grep -v '^$' \
    | grep -v $'^ℹ' \
    | grep -v '^[[:space:]]*$' \
    | tail -1 \
    || echo "(error)"
}

# ---------------------------------------------------------------------------
# subcommand: deploy
# ---------------------------------------------------------------------------
subcmd_deploy() {
  local network="" source="" admin=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --network) network="$2"; shift 2 ;;
      --source)  source="$2";  shift 2 ;;
      --admin)   admin="$2";   shift 2 ;;
      *) die "Unknown flag for deploy: $1" ;;
    esac
  done

  [[ -z "$source" ]] && die "--source is required (stellar keys profile name)"
  [[ -z "$admin"  ]] && die "--admin is required (G... address or stellar keys profile name)"

  network=$(validate_network "$network")

  # Resolve admin to a G... address if it's a profile name
  info "Resolving admin address..."
  local admin_addr
  admin_addr=$(resolve_admin "$admin")
  info "Admin: ${admin_addr}"

  # Mainnet confirmation guard
  if [[ "$network" == "mainnet" ]]; then
    warn "You are deploying to MAINNET. This will consume real XLM."
    read -r -p "Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || die "Aborted."
  fi

  # Build
  cmd_build

  # Upload (hash captured cleanly; log messages go to stderr inside the function)
  local wasm_hash
  wasm_hash=$(upload_wasm "$source" "$network")

  header "Deploying CompliantID contract on ${network}"
  info "Admin: ${admin_addr}"

  # Use --alias so the CLI stores the contract-id
  local alias_name="compliant-id-${network}"
  local deploy_out="/tmp/stellar_deploy_compliant_id_$$.txt"

  stellar contract deploy \
    --wasm "${WASM_PATH}" \
    --source "${source}" \
    --network "${network}" \
    --alias "${alias_name}" \
    -- \
    --admin "${admin_addr}" \
    2>&1 | tee "${deploy_out}" >&2

  # Parse contract ID (C + 55 base32 chars)
  local contract_id
  contract_id=$(grep -E '^C[A-Z2-7]{55}$' "${deploy_out}" | tail -1 || true)
  rm -f "${deploy_out}"

  if [[ -z "$contract_id" ]]; then
    die "Deploy failed: could not determine contract ID from output."
  fi

  success "Contract deployed!"
  echo >&2
  echo -e "  ${BOLD}Contract ID:${RESET} ${contract_id}" >&2
  echo -e "  ${BOLD}WASM Hash:  ${RESET} ${wasm_hash}" >&2
  echo -e "  ${BOLD}Network:    ${RESET} ${network}" >&2
  echo -e "  ${BOLD}Admin:      ${RESET} ${admin_addr}" >&2
  echo >&2

  save_deployed_env "${network}" "$contract_id" "$wasm_hash" "$source"

  echo >&2
  info "Next steps:"
  echo >&2
  echo "  # Verify deployment:" >&2
  echo "  ./scripts/deploy-compliant-id.sh info --network ${network}" >&2
  echo >&2
  echo "  # Add a trusted issuer:" >&2
  echo "  stellar contract invoke \\" >&2
  echo "    --id ${contract_id} \\" >&2
  echo "    --source ${source} \\" >&2
  echo "    --network ${network} \\" >&2
  echo "    -- add_trusted_issuer \\" >&2
  echo "    --admin ${admin_addr} \\" >&2
  echo "    --issuer <ISSUER_G_ADDRESS>" >&2
  echo >&2
  echo "  # Set compliance for a user (as a trusted issuer):" >&2
  echo "  stellar contract invoke \\" >&2
  echo "    --id ${contract_id} \\" >&2
  echo "    --source <ISSUER_KEY> \\" >&2
  echo "    --network ${network} \\" >&2
  echo "    -- set_compliance \\" >&2
  echo "    --issuer <ISSUER_G_ADDRESS> \\" >&2
  echo "    --user <USER_G_ADDRESS> \\" >&2
  echo "    --status Verified \\" >&2
  echo "    --level 1 \\" >&2
  echo "    --expires_at <UNIX_TIMESTAMP> \\" >&2
  echo "    --country_code US" >&2

  # Emit contract ID to stdout for scripting: CONTRACT=$(./deploy-compliant-id.sh deploy ...)
  echo "$contract_id"
}

# ---------------------------------------------------------------------------
# subcommand: upgrade (future-proof)
# ---------------------------------------------------------------------------
subcmd_upgrade() {
  local network="" source="" contract_id=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --network)     network="$2";     shift 2 ;;
      --source)      source="$2";      shift 2 ;;
      --contract-id) contract_id="$2"; shift 2 ;;
      *) die "Unknown flag for upgrade: $1" ;;
    esac
  done

  [[ -z "$source" ]] && die "--source is required (stellar keys profile name)"
  network=$(validate_network "$network")

  if [[ -z "$contract_id" ]]; then
    load_contract_id "${network}" contract_id
  fi
  [[ -z "$contract_id" ]] && die "--contract-id is required (or run deploy first to save it automatically)"

  if [[ "$network" == "mainnet" ]]; then
    warn "You are uploading a new WASM on MAINNET."
    read -r -p "Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || die "Aborted."
  fi

  # Build + upload
  cmd_build
  local wasm_hash
  wasm_hash=$(upload_wasm "$source" "$network")

  success "New WASM uploaded for CompliantID"
  echo >&2
  echo -e "  ${BOLD}Contract ID:${RESET} ${contract_id}" >&2
  echo -e "  ${BOLD}New Hash:   ${RESET} ${wasm_hash}" >&2
  echo -e "  ${BOLD}Network:    ${RESET} ${network}" >&2
  echo >&2

  # Update wasm_hash in the saved env file
  local env_file="${DEPLOYED_DIR}/${network}-compliant-id.env"
  if [[ -f "$env_file" ]]; then
    sed -i "s/^WASM_HASH=.*/WASM_HASH=${wasm_hash}/" "$env_file"
    success "Updated WASM_HASH in ${env_file}"
  fi

  echo >&2
  warn "The CompliantID contract does not yet have an on-chain upgrade function."
  info "The new WASM has been uploaded and its hash saved."
  info "To complete the upgrade, add an upgrade mechanism to the contract and invoke it with:"
  echo >&2
  echo "  stellar contract invoke \\" >&2
  echo "    --id ${contract_id} \\" >&2
  echo "    --source ${source} \\" >&2
  echo "    --network ${network} \\" >&2
  echo "    -- <upgrade_function> \\" >&2
  echo "    --new_wasm_hash ${wasm_hash}" >&2
}

# ---------------------------------------------------------------------------
# subcommand: info
# ---------------------------------------------------------------------------
subcmd_info() {
  local network="" contract_id="" source=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --network)     network="$2";     shift 2 ;;
      --contract-id) contract_id="$2"; shift 2 ;;
      --source)      source="$2";      shift 2 ;;
      *) die "Unknown flag for info: $1" ;;
    esac
  done

  network=$(validate_network "$network")

  if [[ -z "$contract_id" ]]; then
    load_contract_id "${network}" contract_id
  fi
  [[ -z "$contract_id" ]] && die "--contract-id is required"

  # Load source from the saved env file if not provided on the CLI
  if [[ -z "$source" ]]; then
    load_source "${network}" source
  fi

  header "CompliantID contract info — ${network}"

  local admin trusted_issuers restricted_countries
  admin=$(_invoke_view                "$contract_id" "$network" "$source" get_admin)
  trusted_issuers=$(_invoke_view      "$contract_id" "$network" "$source" get_trusted_issuers)
  restricted_countries=$(_invoke_view "$contract_id" "$network" "$source" get_restricted_countries)

  echo ""
  echo -e "  ${BOLD}Contract ID:${RESET}          ${contract_id}"
  echo -e "  ${BOLD}Network:${RESET}              ${network}"
  echo ""
  echo -e "  ${BOLD}Admin:${RESET}                ${admin}"
  echo -e "  ${BOLD}Trusted Issuers:${RESET}      ${trusted_issuers}"
  echo -e "  ${BOLD}Restricted Countries:${RESET}  ${restricted_countries}"
  echo ""
}

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
print_help() {
  cat <<EOF

${BOLD}CompliantID deploy utility${RESET}

Usage:
  $(basename "$0") <subcommand> [flags]

Subcommands:
  deploy     Build + upload + instantiate the contract (first time)
  upgrade    Build + upload new WASM (future-proof — saves hash for later use)
  info       Print current on-chain contract state

${BOLD}Flags — deploy:${RESET}
  --network <testnet|mainnet|local|futurenet>  Target network (required)
  --source <profile>                           stellar keys profile name (required)
  --admin <addr|profile>                       Admin G... address or profile name (required)

${BOLD}Flags — upgrade:${RESET}
  --network <testnet|mainnet|local|futurenet>  Target network (required)
  --source <profile>                           Admin stellar keys profile (required)
  --contract-id <C...>                         Contract address (auto-loaded from deployed/)

${BOLD}Flags — info:${RESET}
  --network <testnet|mainnet|local|futurenet>  Target network (required)
  --source <profile>                           stellar keys profile (auto-loaded from deployed/)
  --contract-id <C...>                         Contract address (auto-loaded from deployed/)

${BOLD}Examples:${RESET}

  # Deploy on testnet using a stellar keys profile for the admin
  ./scripts/deploy-compliant-id.sh deploy \\
      --network testnet \\
      --source admin1 \\
      --admin admin1

  # Deploy on testnet using a raw G... address for the admin
  ./scripts/deploy-compliant-id.sh deploy \\
      --network testnet \\
      --source admin1 \\
      --admin GABC...XYZ

  # Query on-chain state (contract-id auto-loaded from deployed/)
  ./scripts/deploy-compliant-id.sh info --network testnet

  # Upload new WASM for future upgrade
  ./scripts/deploy-compliant-id.sh upgrade \\
      --network testnet \\
      --source admin1

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
    deploy)         subcmd_deploy  "$@" ;;
    upgrade)        subcmd_upgrade "$@" ;;
    info)           subcmd_info    "$@" ;;
    help|--help|-h) print_help ;;
    *) die "Unknown subcommand '${subcommand}'. Use: deploy | upgrade | info" ;;
  esac
}

main "$@"
