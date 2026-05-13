#!/usr/bin/env bash
# =============================================================================
# deploy.sh — Deploy / upgrade utility for the lunarxy-token Soroban contract
#
# Subcommands:
#   deploy   Build + upload + instantiate the contract for the first time
#   upgrade  Build + upload new WASM + call propose_upgrade (multi-sig step 1)
#   info     Print current on-chain state (version, admins, threshold, paused)
#
# Usage:
#   ./scripts/deploy.sh <subcommand> [flags]
#
# Examples:
#   ./scripts/deploy.sh deploy \
#       --network testnet \
#       --source admin1 \
#       --admin-keys "admin1,admin2,admin3" \
#       --threshold 2 \
#       --name "LUNARXY" \
#       --symbol "LUNARXY"
#
#   ./scripts/deploy.sh upgrade \
#       --network testnet \
#       --source admin1 \
#       --contract-id CXXXXXXXXX...
#
#   ./scripts/deploy.sh info \
#       --network testnet \
#       --contract-id CXXXXXXXXX...
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
WASM_PATH="${REPO_ROOT}/target/wasm32v1-none/release/lunarxy_token.wasm"

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
    "") die "--network is required (testnet | mainnet | local)" ;;
    *)  die "Unknown network '${1}'. Valid values: testnet, mainnet, local" ;;
  esac
}

# ---------------------------------------------------------------------------
# Build the WASM (output goes to stderr)
# ---------------------------------------------------------------------------
cmd_build() {
  header "Building lunarxy-token contract"
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
# Convert "profile1,profile2,..." → "GADDR1,GADDR2,..."
# by calling `stellar keys address <name>` for each entry
# ---------------------------------------------------------------------------
resolve_admin_keys() {
  local csv="$1"
  local result=""
  local IFS=','
  for name in $csv; do
    name="${name// /}"  # trim whitespace
    local addr
    addr=$(stellar keys address "$name" 2>/dev/null || true)
    [[ -z "$addr" ]] && die "Could not resolve stellar keys address for profile '${name}'"
    result="${result:+${result},}${addr}"
  done
  echo "$result"
}

# ---------------------------------------------------------------------------
# Convert "ADDR1,ADDR2,ADDR3" → '["ADDR1","ADDR2","ADDR3"]'
# ---------------------------------------------------------------------------
admins_to_json() {
  local csv="$1"
  echo "$csv" | awk -F',' '
  {
    printf "["
    for (i=1; i<=NF; i++) {
      gsub(/^[ \t]+|[ \t]+$/, "", $i)
      if (i>1) printf ","
      printf "\"%s\"", $i
    }
    printf "]"
  }'
}

# ---------------------------------------------------------------------------
# Save deployment state to deployed/<network>.env
# ---------------------------------------------------------------------------
save_deployed_env() {
  local network="$1" contract_id="$2" wasm_hash="$3" source="$4"
  local env_file="${DEPLOYED_DIR}/${network}.env"
  mkdir -p "${DEPLOYED_DIR}"
  cat > "${env_file}" <<EOF
# Auto-generated by scripts/deploy.sh — do not edit manually
CONTRACT_ID=${contract_id}
WASM_HASH=${wasm_hash}
NETWORK=${network}
SOURCE=${source}
DEPLOYED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF
  success "Deployment state saved to ${env_file}"
}

# ---------------------------------------------------------------------------
# Load contract-id from deployed/<network>.env (silent fallback)
# ---------------------------------------------------------------------------
load_contract_id() {
  local network="$1" contract_id_ref="$2"
  local env_file="${DEPLOYED_DIR}/${network}.env"
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
  local network="" source="" admins="" admin_keys="" threshold="" name="" symbol=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --network)    network="$2";    shift 2 ;;
      --source)     source="$2";     shift 2 ;;
      --admins)     admins="$2";     shift 2 ;;
      --admin-keys) admin_keys="$2"; shift 2 ;;
      --threshold)  threshold="$2";  shift 2 ;;
      --name)       name="$2";       shift 2 ;;
      --symbol)     symbol="$2";     shift 2 ;;
      *) die "Unknown flag for deploy: $1" ;;
    esac
  done

  [[ -z "$source"    ]] && die "--source is required (stellar keys profile name)"
  [[ -z "$threshold" ]] && die "--threshold is required (u32)"

  # Exactly one of --admins or --admin-keys must be provided
  if [[ -n "$admins" && -n "$admin_keys" ]]; then
    die "Specify either --admins or --admin-keys, not both."
  fi
  if [[ -z "$admins" && -z "$admin_keys" ]]; then
    die "Either --admins (raw G... addresses) or --admin-keys (stellar keys profile names) is required."
  fi
  if [[ -n "$admin_keys" ]]; then
    info "Resolving admin addresses from stellar keys profiles..."
    admins=$(resolve_admin_keys "$admin_keys")
    info "Resolved: ${admins}"
  fi
  [[ -z "$name"      ]] && die "--name is required (token name)"
  [[ -z "$symbol"    ]] && die "--symbol is required (token symbol)"

  network=$(validate_network "$network")

  # Validate admin count (contract enforces min 3, max 10)
  local admin_count
  admin_count=$(echo "$admins" | awk -F',' '{print NF}')
  [[ "$admin_count" -lt 3  ]] && die "Contract requires at least 3 admins (got ${admin_count})"
  [[ "$admin_count" -gt 10 ]] && die "Contract allows at most 10 admins (got ${admin_count})"
  [[ "$threshold" -lt 1 ]] && die "--threshold must be at least 1"
  [[ "$threshold" -gt "$admin_count" ]] && die "--threshold (${threshold}) cannot exceed admin count (${admin_count})"

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

  local admins_json
  admins_json=$(admins_to_json "$admins")

  header "Deploying contract on ${network}"
  info "Admins (${admin_count}): ${admins_json}"
  info "Threshold:  ${threshold}"
  info "Name:       ${name}"
  info "Symbol:     ${symbol}"

  # Use --alias so the CLI stores the contract-id; use tee to capture output
  # without $() to avoid any interactive-mode issues.
  local alias_name="lunarxy-token-${network}"
  local deploy_out="/tmp/stellar_deploy_$$.txt"

  stellar contract deploy \
    --wasm "${WASM_PATH}" \
    --source "${source}" \
    --network "${network}" \
    --alias "${alias_name}" \
    -- \
    --admins "${admins_json}" \
    --threshold "${threshold}" \
    --name "${name}" \
    --symbol "${symbol}" \
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
  echo >&2

  save_deployed_env "${network}" "$contract_id" "$wasm_hash" "$source"

  echo >&2
  info "Next steps:"
  echo "  # Verify deployment:" >&2
  echo "  ./scripts/deploy.sh info --network ${network}" >&2
  echo >&2
  echo "  # Set the Ed25519 signer key for user_mint (optional):" >&2
  echo "  stellar contract invoke \\" >&2
  echo "    --id ${contract_id} \\" >&2
  echo "    --source <ADMIN_KEY> \\" >&2
  echo "    --network ${network} \\" >&2
  echo "    -- set_signer_key \\" >&2
  echo "    --admin <ADMIN_ADDRESS> \\" >&2
  echo "    --signer_key <ED25519_PUBLIC_KEY_HEX>" >&2

  # Emit contract ID to stdout for scripting: CONTRACT=$(./deploy.sh deploy ...)
  echo "$contract_id"
}

# ---------------------------------------------------------------------------
# subcommand: upgrade
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
    warn "You are proposing an upgrade on MAINNET."
    read -r -p "Type 'yes' to continue: " confirm
    [[ "$confirm" == "yes" ]] || die "Aborted."
  fi

  # Build + upload
  cmd_build
  local wasm_hash
  wasm_hash=$(upload_wasm "$source" "$network")

  # Resolve proposer address from the source key profile
  local proposer
  proposer=$(stellar keys address "${source}" 2>/dev/null || true)
  [[ -z "$proposer" ]] && die "Could not resolve address for '${source}'. Is it a valid stellar keys profile?"

  header "Calling propose_upgrade on ${network}"
  info "Contract:  ${contract_id}"
  info "Proposer:  ${proposer}"
  info "New hash:  ${wasm_hash}"

  stellar contract invoke \
    --id "${contract_id}" \
    --source "${source}" \
    --network "${network}" \
    -- propose_upgrade \
    --proposer "${proposer}" \
    --new_wasm_hash "${wasm_hash}" \
    >&2

  success "propose_upgrade submitted!"

  # Update wasm_hash in the saved env file
  local env_file="${DEPLOYED_DIR}/${network}.env"
  if [[ -f "$env_file" ]]; then
    sed -i "s/^WASM_HASH=.*/WASM_HASH=${wasm_hash}/" "$env_file"
    success "Updated WASM_HASH in ${env_file}"
  fi

  echo >&2
  info "The upgrade proposal is now active. Each remaining admin must approve:"
  echo >&2
  echo "  stellar contract invoke \\" >&2
  echo "    --id ${contract_id} \\" >&2
  echo "    --source <OTHER_ADMIN_KEY> \\" >&2
  echo "    --network ${network} \\" >&2
  echo "    -- approve_upgrade \\" >&2
  echo "    --approver <OTHER_ADMIN_ADDRESS>" >&2
  echo >&2
  echo "  # After reaching threshold, run handle_upgrade (any admin):" >&2
  echo "  stellar contract invoke \\" >&2
  echo "    --id ${contract_id} \\" >&2
  echo "    --source <ADMIN_KEY> \\" >&2
  echo "    --network ${network} \\" >&2
  echo "    -- handle_upgrade \\" >&2
  echo "    --admin <ADMIN_ADDRESS>" >&2
  echo >&2
  info "Check proposal status:"
  echo "  ./scripts/deploy.sh info --network ${network} --contract-id ${contract_id}" >&2
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
    local env_file="${DEPLOYED_DIR}/${network}.env"
    if [[ -f "$env_file" ]]; then
      source=$(grep '^SOURCE=' "$env_file" | cut -d= -f2 || true)
    fi
  fi

  header "Contract info — ${network}"

  local version total_supply is_paused admins threshold name symbol decimals upgrade_proposal
  version=$(_invoke_view          "$contract_id" "$network" "$source" version)
  total_supply=$(_invoke_view     "$contract_id" "$network" "$source" total_supply)
  is_paused=$(_invoke_view        "$contract_id" "$network" "$source" is_paused)
  admins=$(_invoke_view           "$contract_id" "$network" "$source" get_admins)
  threshold=$(_invoke_view        "$contract_id" "$network" "$source" get_threshold)
  name=$(_invoke_view             "$contract_id" "$network" "$source" name)
  symbol=$(_invoke_view           "$contract_id" "$network" "$source" symbol)
  decimals=$(_invoke_view         "$contract_id" "$network" "$source" decimals)
  upgrade_proposal=$(_invoke_view "$contract_id" "$network" "$source" get_upgrade_proposal)

  echo -e "  ${BOLD}Contract ID:${RESET}      ${contract_id}"
  echo -e "  ${BOLD}Network:${RESET}          ${network}"
  echo ""
  echo -e "  ${BOLD}Name:${RESET}             ${name}"
  echo -e "  ${BOLD}Symbol:${RESET}           ${symbol}"
  echo -e "  ${BOLD}Decimals:${RESET}         ${decimals}"
  echo -e "  ${BOLD}Version:${RESET}          ${version}"
  echo -e "  ${BOLD}Total Supply:${RESET}     ${total_supply}"
  echo -e "  ${BOLD}Paused:${RESET}           ${is_paused}"
  echo ""
  echo -e "  ${BOLD}Threshold:${RESET}        ${threshold}"
  echo -e "  ${BOLD}Admins:${RESET}           ${admins}"
  echo ""
  echo -e "  ${BOLD}Upgrade Proposal:${RESET} ${upgrade_proposal}"
  echo ""
}

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
print_help() {
  cat <<EOF

${BOLD}lunarxy-token deploy utility${RESET}

Usage:
  $(basename "$0") <subcommand> [flags]

Subcommands:
  deploy     Build + upload + instantiate the contract (first time)
  upgrade    Build + upload new WASM + call propose_upgrade (multi-sig step 1)
  info       Print current on-chain contract state

${BOLD}Flags — deploy:${RESET}
  --network <testnet|mainnet|local>   Target network (required)
  --source <profile>                  stellar keys profile name (required)
  --admins <addr1,addr2,...>          Comma-separated admin G... addresses (min 3)
  --admin-keys <p1,p2,...>            Comma-separated stellar keys profile names (min 3)
                                      Mutually exclusive with --admins
  --threshold <n>                     Minimum approvals for multi-sig actions (required)
  --name <str>                        Token name (required)
  --symbol <str>                      Token symbol (required)

${BOLD}Flags — upgrade:${RESET}
  --network <testnet|mainnet|local>   Target network (required)
  --source <profile>                  Admin stellar keys profile (required)
  --contract-id <C...>                Contract address (auto-loaded from deployed/<network>.env)

${BOLD}Flags — info:${RESET}
  --network <testnet|mainnet|local>   Target network (required)
  --source <profile>                  stellar keys profile (auto-loaded from deployed/<network>.env)
  --contract-id <C...>                Contract address (auto-loaded from deployed/<network>.env)

${BOLD}Examples:${RESET}

  # Initial deploy on testnet using raw addresses (3-of-3 multisig, threshold 2)
  ./scripts/deploy.sh deploy \\
      --network testnet \\
      --source dev_account \\
      --admins "GAAA...,GBBB...,GCCC..." \\
      --threshold 2 \\
      --name "LUNARXY" \\
      --symbol "LUNARXY"

  # Initial deploy using stellar keys profile names (auto-resolves to G... addresses)
  ./scripts/deploy.sh deploy \\
      --network testnet \\
      --source dev_account \\
      --admin-keys "admin1,admin2,admin3" \\
      --threshold 2 \\
      --name "LUNARXY" \\
      --symbol "LUNARXY"

  # Propose an upgrade (after editing the contract source)
  ./scripts/deploy.sh upgrade \\
      --network testnet \\
      --source admin1

  # Query on-chain state (contract-id auto-loaded from deployed/testnet.env)
  ./scripts/deploy.sh info --network testnet

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
