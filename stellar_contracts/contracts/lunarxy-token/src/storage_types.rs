use soroban_sdk::{contracttype, Address};

// --- TTL Constants ---

/// Threshold for instance storage TTL extension (approx 30 days).
pub const INSTANCE_LIFETIME_THRESHOLD: u32 = 518_400;
/// Bump amount for instance storage TTL (approx 60 days).
pub const INSTANCE_BUMP_AMOUNT: u32 = 1_036_800;

/// Threshold for balance (persistent) storage TTL extension.
pub const BALANCE_LIFETIME_THRESHOLD: u32 = 518_400;
/// Bump amount for balance (persistent) storage TTL.
pub const BALANCE_BUMP_AMOUNT: u32 = 1_036_800;

// --- Storage Keys ---

#[derive(Clone)]
#[contracttype]
pub enum DataKey {
    // Token metadata
    Decimal,
    Name,
    Symbol,
    TotalSupply,

    // Balances and allowances
    Balance(Address),
    Allowance(AllowanceDataKey),

    // Multi-sig administration
    Admins,
    Threshold,

    // Proposals (only one of each type active at a time)
    UpgradeProposal,
    AdminProposal,
    ThresholdProposal,
    UnpauseProposal,

    // Contract state
    Paused,
    Version,

    // User mint
    SignerKey,
    Nonce(Address),

    // Freeze / Seizure
    Frozen(Address),
    FreezeProposal,
    SeizureProposal,
}

// --- Allowance Types ---

#[derive(Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub struct AllowanceDataKey {
    pub from: Address,
    pub spender: Address,
}

#[derive(Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub struct AllowanceValue {
    pub amount: i128,
    pub expiration_ledger: u32,
}

// --- Proposal Types ---

#[derive(Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub struct UpgradeProposal {
    pub wasm_hash: soroban_sdk::BytesN<32>,
    pub proposer: Address,
    pub approvals: soroban_sdk::Vec<Address>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub enum AdminAction {
    Add,
    Remove,
}

#[derive(Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub struct AdminProposal {
    pub action: AdminAction,
    pub target: Address,
    pub proposer: Address,
    pub approvals: soroban_sdk::Vec<Address>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub struct ThresholdProposal {
    pub new_threshold: u32,
    pub proposer: Address,
    pub approvals: soroban_sdk::Vec<Address>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub struct UnpauseProposal {
    pub proposer: Address,
    pub approvals: soroban_sdk::Vec<Address>,
}

// --- Freeze / Seizure Types ---

#[derive(Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub enum FreezeAction {
    Freeze,
    Unfreeze,
}

#[derive(Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub struct FreezeProposal {
    pub action: FreezeAction,
    pub target: Address,
    pub proposer: Address,
    pub approvals: soroban_sdk::Vec<Address>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub struct SeizureProposal {
    pub target: Address,
    pub destination: Address,
    pub amount: i128,
    pub proposer: Address,
    pub approvals: soroban_sdk::Vec<Address>,
}
