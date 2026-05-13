# Eara Stellar Suite

### Institutional RWA Infrastructure on Stellar/Soroban

<p align="center">
  <a href="URL_DE_TU_WEB_STELLAR">
    <img src="https://img.shields.io/badge/Built%20on-Stellar-7C3AED?style=flat-square&logo=stellar&logoColor=white" alt="Stellar" />
  </a>
  <a href="URL_DE_TU_CONTRATO_O_CODIGO">
    <img src="https://img.shields.io/badge/Smart%20Contracts-Soroban-0F172A?style=flat-square" alt="Soroban" />
  </a>
  <a href="URL_DE_TU_ARCHIVO_LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" alt="License: MIT" />
  </a>
  <a href="URL_DE_TU_RED_O_EXPLORADOR">
    <img src="https://img.shields.io/badge/Network-Testnet-F59E0B?style=flat-square" alt="Testnet" />
  </a>
  <a href="URL_DE_TU_ANUNCIO_DE_BECA">
    <img src="https://img.shields.io/badge/Stellar%20Foundation-Grant%20Recipient-6366F1?style=flat-square" alt="Grant" />
  </a>
</p>


---

**Eara Stellar Suite** is an institutional-grade infrastructure developed by [Eara](https://eara.io/) for issuing, managing, and operating **Real World Assets (RWAs)** on the Stellar network.

This project ports Eara's core technology to the Stellar/Soroban ecosystem, enabling enterprises to operate regulated assets in an automated, auditable, and secure manner — while maintaining the professional operational standards already established in our platform.

> **This is not an all-or-nothing solution.** The suite is designed as a collection of independent modules that can be adopted individually or as a complete stack, depending on each organization's compliance and business needs.

---

## Table of Contents

- Why Stellar?
- Architecture Overview
- Eara Base Platform
- The Eara-Module Suite
    - CompliantID
    - Secure Custodian
- Repository Structure
- Stellar Standards (SEPs)
- Tech Setup: Quick Start
- Project Demo
- Security & Compliance Design
- Contact

---

## 🌐 Why Stellar?

Stellar's architecture provides native capabilities that are critical for regulated financial products:

- **Native multisignature** at the protocol level — no need for external contracts to govern critical admin operations.
- **Soroban smart contracts** — deterministic, auditable, and resource-bound execution ideal for compliance logic.
- **Low and predictable fees** — suitable for high-frequency compliance checks and registry reads.
- **Built-in asset issuance** — Stellar's asset model aligns naturally with regulated token issuance (RWAs, funds, securities).
- **SEP ecosystem** — standardized protocols for authentication (SEP-10), signing (SEP-7), and key management (SEP-5).

---

## 🏗 Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                        EARA PLATFORM                           │
│              (Existing backend + dashboards)                   │
└────────────────────────────┬───────────────────────────────────┘
                             │
          ┌──────────────────▼────────────────────┐
          │     Soroban Integration Module        │
          │ (Python backend — invoke, sign, read) │
          │     SEP-10 Auth · SEP-7 Signing       │
          └──────────────────┬────────────────────┘
                             │
   ┌─────────────────────────▼────────────────────────────────┐
   │                  STELLAR NETWORK (Soroban)               │
   │                                                          │
   │          ┌──────────────┐    ┌────────────────┐          │
   │          │ CompliantID  │    │Secure Custodian│          │
   │          │              │    │    Multisign   │          │
   │          └──────────────┘    └────────────────┘          │
   │                                                          │
   └──────────────────────────────────────────────────────────┘
```

The platform backend acts as the operational layer, calling into Soroban contracts for enforcement. Each module is independently deployable and composable with the rest.

---

## 🏦 Eara Base Platform

Before the Stellar Suite, there is the platform it extends. The Eara-module suite is not a standalone product — it integrates as a modular layer on top of Eara's existing operational infrastructure, which already handles the full lifecycle of a regulated tokenized investment.

The base platform has two distinct interfaces:

### Admin Panel

The control center for asset issuers and compliance operators. From here, an authorized organization can:

- **Create and configure investment projects** — define the asset type, tokenomics, legal structure, subscription terms, and documentation for each issuance.
- **Manage KYC/AML validation** — review, approve, reject, or revoke investor verifications. The admin panel is the operator's interface to the compliance workflow.
- **Monitor investor portfolios** — track token holdings, transaction history, and cap table composition in real time across all active projects.
- **Control access and permissions** — manage which investors are eligible for which assets, apply restrictions, and enforce compliance rules through the dashboard.

### Investor Platform

The end-user interface for accredited investors and retail participants (depending on the asset). From here, a user can:

- **Complete the KYC process** — submit identity verification through a guided flow. Once approved, the verification status is reflected across all eligible assets on the platform.
- **Browse and access investment projects** — view available tokenized assets, their terms, documents, and status (open, closed, vesting, etc.).
- **Manage their portfolio** — track holdings, view transaction history, access documents related to their investments, and follow asset performance.

### How the Stellar Suite Extends This

Each of the Eara modules in this suite connects directly to the base platform's existing workflows:

|Base Platform action|Stellar Suite module invoked|
|---|---|
|KYC approved for a user|**CompliantID** — verification state written on-chain|
|Admin executes a critical action|**Secure Custodian** — multisign threshold must be met|

The result is a platform where the dashboards and workflows operators already know are preserved, and the Stellar layer operates as the enforcement and auditability backbone underneath.

---

## 🧩 The Eara-Module Suite

### Eara CompliantID: Zero-Proof KYC Passport

**What it is:** A privacy-first on-chain identity system that stores the _verification state_ of an investor — not their personal data. Once verified, a user holds a reusable "compliance passport" that any regulated asset in the ecosystem can query.

**The problem it solves:** KYC/AML re-verification is the biggest friction point in regulated investment. CompliantID allows a verified investor to participate in multiple assets without repeating the compliance process every time.

**Design principle — Zero-Proof KYC:** Eara does not store or custody any Personally Identifiable Information (PII) on-chain. The system produces a verification outcome (`verified / not_verified / revoked / suspended`) with metadata:

- Verification status (enum)
- Expiry timestamp
- Issuer address (who certified this user)
- Last updated timestamp
- Optional evidence hash (one-way, non-reversible)

**Smart contracts:**

|Contract|Role|
|---|---|
|`IdentityRegistry.rs`|Stores and exposes user verification profiles|
|`TrustedIssuers.rs`|Access control — only authorized issuers can write profiles|

**Key functions:**

```rust
// Write a user's compliance state (only callable by a trusted issuer)
set_compliance(env: Env, issuer: Address, user: Address, status: ComplianceStatus, level: u32, expires_at: u64, country_code: Symbol,) -> Result<(), CompliantIdError>

// Read — used by other contracts before allowing any transfer
is_compliant(env: Env, user: Address, min_level: u32) -> bool

// Optional — retrieve full profile metadata
pub fn get_compliance(env: Env, user: Address) -> Result<UserComplianceRecord, CompliantIdError> {
```

**Verification logic:**`is_compliant` returns `true` only if:

1. `status == Verified`
2. `expiry > current_ledger_timestamp`

**Interoperability:** The passport is designed to be reusable across any Eara-powered asset. Future iterations will support cross-chain interoperability.

**Access flow:**

```
User → SEP-10 Wallet Auth → Off-chain KYC (Eara backend)
       → Backend (as Trusted Issuer) → set_user_profile()
       → Any asset contract → is_compliant() → allow/deny transfer
```

---

### Eara Secure Custodian: Multisign Governance

**What it is:** A governance framework that ensures no single person can execute critical administrative actions alone. Built on Stellar's **native multisignature** mechanism (no additional contract complexity needed).

**The problem it solves:** In regulated asset management, the "admin key" is one of the highest-risk single points of failure. Investors, regulators, and auditors need assurance that sensitive changes (freeze, rule updates, key rotation) are governed by a robust, verifiable process.

**Configuration (Phase 1):**

|Parameter|Value|
|---|---|
|Total signers|7|
|High threshold|5 (required for critical ops)|
|Medium threshold|3 (standard ops)|
|Network|Stellar Testnet|

**Governed operations (requiring threshold approval):**

- Freeze / unfreeze an asset or address
- Update compliance rules on a deployed asset
- Rotate trusted issuers in CompliantID
- Publish or invalidate NAV data
- Notarize documents (Registry & Notary)

**Operational workflow (Phase 2 — full implementation):**

```
1. PROPOSE  → An authorized party creates and submits a signed transaction (XDR)
2. COLLECT  → Other signers review and add signatures via SEP-7 signing requests
3. VALIDATE → System checks threshold is met (e.g. 5-of-7)
4. EXECUTE  → Transaction is submitted to the network
```

**Phase 1 scope:** Phase 1 establishes the multisign account with correct thresholds and produces an on-chain proof of configuration (transaction hash). The full proposal/collection/execution workflow is implemented in Phase 2.

**SEP-7 integration:** Signing requests are formatted as SEP-7 URIs, allowing any compatible Stellar wallet to participate in governance signing flows without custom tooling.

---

## 📁 Repository Structure

```
eara-stellar-suite/
├── contracts/
│   ├── compliant-id/
│   │   ├── Cargo.toml
│   │   ├── COMPLIANT_ID.md
│   │   ├── Makefile
│   │   ├── src/
│   │   │   ├── contract.rs
│   │   │   ├── event.rs
│   │   │   ├── lib.rs
│   │   │   ├── storage_types.rs
│   │   │   └── test.rs
│   │   └── test_snapshots/test/
│   │       └── [38 snapshot JSON files]
│   ├── lunarxy-token/
│   │   ├── Cargo.toml
│   │   ├── Makefile
│   │   ├── src/
│   │   │   ├── admin.rs
│   │   │   ├── allowance.rs
│   │   │   ├── balance.rs
│   │   │   ├── contract.rs
│   │   │   ├── event.rs
│   │   │   ├── freeze.rs
│   │   │   ├── lib.rs
│   │   │   ├── metadata.rs
│   │   │   ├── seizure.rs
│   │   │   ├── storage_types.rs
│   │   │   ├── test.rs
│   │   │   └── upgrade.rs
│   │   └── test_snapshots/test/
│   │       └── [82 snapshot JSON files]
│   └── simple-token/
│       ├── Cargo.toml
│       ├── src/
│       │   ├── contract.rs
│       │   ├── lib.rs
│       │   └── test.rs
│       └── test_snapshots/test/
│           └── [10 snapshot JSON files]
│
├── scripts/
│   ├── deploy-compliant-id.sh
│   ├── deploy.sh
│   ├── mint.sh
│   ├── pem-to-strkey.sh
│   ├── set-signer-key.sh
│   └── upgrade-lunarxy-token.sh
│
├── backend/                      # Soroban Integration Module (Python)
│   └── blockchain/
│	      └── stellar/
│           ├── __init__.py
│           ├── stellar_utils.py          ⭐ Core: Horizon, Soroban, contratos
│           └── stellar_keypair.py        🔑 Gestión Ed25519 keypairs
│       └── api/
│           └── v1/
│               └── endpoints/
│                   └── private/
│                       └── private_stellar.py ⚙️  GET /is_trusted_issuer, /is_compliant
│
├── docs/
│   ├── architecture.md           # Full system architecture
│   ├── sep_integration.md        # SEP-10, SEP-7, SEP-5 implementation notes
│   ├── multisig_operations.md    # Governance procedures
│   ├── contract_interfaces.md    # All public contract APIs
│   └── diagrams/
│       └── system_flow.png
│
└── README.md
```

---

## 📋 Stellar Standards (SEPs) Applied

|SEP|Standard|Application in this project|
|---|---|---|
|**SEP-10**|Wallet Authentication|Users authenticate via challenge/response before any compliance operation. The backend validates signatures and binds sessions to wallet addresses.|
|**SEP-7**|Transaction Signing URI|Multisign governance flows generate SEP-7 URIs so any compatible Stellar wallet can participate in signing without custom tooling.|
|**SEP-5**|HD Wallet Key Derivation|Reference standard for custodian key management and hardware wallet compatibility in the multisign setup.|

---

## 🚀 Tech Setup: Quick Start

### Prerequisites

- [Rust](https://rustup.rs/) + [Soroban CLI](https://developers.stellar.org/docs/tools/developer-tools/cli/stellar-cli)
- Python 3.10+
- A funded Stellar Testnet account ([Friendbot](https://friendbot.stellar.org/))

### Installation

```bash
# Clone the repository
git clone <https://github.com/eara-labs/eara-stellar-suite.git>
cd eara-stellar-suite

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### Run Smart Contract Tests

```bash
cd contracts/
cargo test
```

### Deploy to Testnet

```bash
# Deploy token
bash scripts/deploy.sh deploy --network testnet --source admin1 --admin-keys "admin1,admin2,admin3" --threshold 2 --name "LUNARXY" --symbol "LUNARXY"

# deploy compliant
bash scripts/deploy-compliant-id.sh deploy --network testnet --source admin1 --admin admin1

```

The script outputs the deployed contract IDs, which are required for the demo.

---

## 🚀 Project Demo

### Prerequisites

- A funded Stellar Testnet account ([Friendbot](https://friendbot.stellar.org/))
- Access to the Eara Admin Panel and Investor App (Testnet environment)

### End-to-End Demo

The full demo can be executed through the Eara platform interfaces — no CLI interaction required. The demo covers the complete lifecycle from project creation to on-chain identity verification and multisign governance setup.

- **Step 1 — Create a project from the Admin Panel**
    
    Log into the Eara Admin Panel and create a new investment project. Configure the asset parameters (name, token supply, subscription terms, documentation) and publish it to the Testnet environment. The project becomes visible to investors on the Investor App.
    
- **Step 2 — Investor registers and submits KYC**
    
    A user accesses the Investor App, creates an account, and initiates the KYC process for the published project. The investor submits their verification data through the guided flow in the app.
    
- **Step 3 — Admin validates the KYC**
    
    Back in the Admin Panel, the compliance operator reviews the submitted KYC and approves it. This triggers the backend to act as a Trusted Issuer and invoke `set_user_profile()` on the `IdentityRegistry` contract, writing the investor's verified status on-chain.
    
- **Step 4 — On-chain verification confirmed**
    
    The system queries `is_verified()` against the contract and confirms the investor's compliance passport is active. The investor can now see their verified status reflected in the Investor App and access the project.
    
- **Step 5 — Multisign governance from the Admin Panel**
    
    From the Admin Panel's governance section, the admin configures and reviews the multisign account (7 signers, threshold = 5). The panel displays the current signers, pending actions, and the on-chain proof of threshold configuration (transaction hash), verifiable on [Stellar Expert (Testnet)](https://testnet.stellar.expert/).
    

All on-chain activity — contract IDs, transaction hashes, and verification states — is logged in the Admin Panel and independently verifiable on the [Stellar Expert (Testnet)](https://testnet.stellar.expert/).

---

## 🔒 Security & Compliance Design

### Privacy by Design (Zero-Proof KYC)

- **No PII on-chain.** Eara does not store names, documents, or personal data in any on-chain state.
- **Minimal on-chain surface.** Only verification status, expiry, issuer, level, country and timestamp are stored — the minimum necessary to enable downstream compliance checks.

### Smart Contract Security Practices

- **Authorization is enforced, not assumed.** Every write operation in `IdentityRegistry` and future contracts verifies the caller against `TrustedIssuers` before proceeding.
- **Explicit error types.** All failure paths return typed errors (`Unauthorized`, `Expired`, `NotFound`) — no silent failures.
- **Actualizaciones por consenso.** Para que un contrato pueda actualizarse, se ha de hacer por medio del contrato Multi-sign autorizado por el número mínimo de firmas para esa operación (por ejemplo 5 de 7) .

### Governance Assurance

The 5-of-7 multisignature threshold on the admin account ensures:

- No single operator can freeze assets, rotate issuers, or change rules unilaterally.
- Every critical action produces an on-chain audit trail (transaction hash, signers, timestamp).
- Key compromise of up to 2 signers does not compromise the system.

---

## 📎 Technical References

- [Stellar Documentation](https://developers.stellar.org/)
- [Soroban Smart Contract Docs](https://soroban.stellar.org/)
- [SEP-10: Stellar Web Authentication](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0010.md)
- [SEP-7: URI Scheme for Transactions](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0007.md)
- [SEP-5: Key Derivation Methods](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0005.md)
- [Stellar Expert — Testnet Explorer](https://testnet.stellar.expert/)

---

## 🤝 Contact & Commercial Enquiries

**Eara** develops regulated tokenization infrastructure for institutional use cases. If you are a financial institution, fund manager, or crypto-native enterprise exploring RWA tokenization:

- **Website:** [earaglobal.com](https://earaglobal.com/)
- **Email:** [team@earaglobal.com](mailto:team@earaglobal.com)
- **LinkedIn:** [Eara Tokenization](http://linkedin.com/company/earaglobal/)

The modules in this suite are available for licensing individually. You do not need to adopt the full stack.

---

_Eara Stellar Suite is funded by a grant from the [Stellar Development Foundation](https://stellar.org/foundation)._