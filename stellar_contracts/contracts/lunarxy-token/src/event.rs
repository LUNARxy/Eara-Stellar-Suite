use soroban_sdk::{contractevent, Address, BytesN, Env, Vec};

// --- Token Events ---

#[contractevent(data_format = "single-value")]
pub struct Mint {
    #[topic]
    pub admin: Address,
    #[topic]
    pub to: Address,
    pub amount: i128,
}

#[contractevent(data_format = "single-value")]
pub struct Burn {
    #[topic]
    pub from: Address,
    pub amount: i128,
}

#[contractevent(data_format = "single-value")]
pub struct Transfer {
    #[topic]
    pub from: Address,
    #[topic]
    pub to: Address,
    pub amount: i128,
}

#[contractevent]
pub struct Approve {
    #[topic]
    pub from: Address,
    #[topic]
    pub spender: Address,
    pub amount: i128,
    pub expiration_ledger: u32,
}

// --- Pause Events ---

#[contractevent(data_format = "single-value")]
pub struct Paused {
    pub admin: Address,
}

#[contractevent(data_format = "single-value")]
pub struct Unpaused {
    pub approvals: Vec<Address>,
}

// --- Upgrade Events ---

#[contractevent(data_format = "single-value")]
pub struct UpgradeProposed {
    #[topic]
    pub proposer: Address,
    pub wasm_hash: BytesN<32>,
}

#[contractevent(data_format = "single-value")]
pub struct UpgradeApproved {
    #[topic]
    pub approver: Address,
    pub approval_count: u32,
}

#[contractevent]
pub struct UpgradeExecuted {
    pub wasm_hash: BytesN<32>,
    pub approvals: Vec<Address>,
}

#[contractevent(data_format = "single-value")]
pub struct UpgradeCancelled {
    pub cancelled_by: Address,
}

// --- Admin Proposal Events ---

#[contractevent]
pub struct AdminProposalCreated {
    #[topic]
    pub proposer: Address,
    #[topic]
    pub target: Address,
    pub action: soroban_sdk::String,
}

#[contractevent(data_format = "single-value")]
pub struct AdminProposalApproved {
    #[topic]
    pub approver: Address,
    pub approval_count: u32,
}

#[contractevent(data_format = "single-value")]
pub struct AdminAdded {
    #[topic]
    pub new_admin: Address,
    pub approvals: Vec<Address>,
}

#[contractevent(data_format = "single-value")]
pub struct AdminRemoved {
    #[topic]
    pub removed: Address,
    pub approvals: Vec<Address>,
}

#[contractevent(data_format = "single-value")]
pub struct AdminProposalCancelled {
    pub cancelled_by: Address,
}

// --- Threshold Events ---

#[contractevent(data_format = "single-value")]
pub struct ThresholdProposalCreated {
    #[topic]
    pub proposer: Address,
    pub new_threshold: u32,
}

#[contractevent(data_format = "single-value")]
pub struct ThresholdProposalApproved {
    #[topic]
    pub approver: Address,
    pub approval_count: u32,
}

#[contractevent]
pub struct ThresholdChanged {
    pub old_threshold: u32,
    pub new_threshold: u32,
}

#[contractevent(data_format = "single-value")]
pub struct ThresholdProposalCancelled {
    pub cancelled_by: Address,
}

// --- Unpause Proposal Events ---

#[contractevent(data_format = "single-value")]
pub struct UnpauseProposed {
    #[topic]
    pub proposer: Address,
}

#[contractevent(data_format = "single-value")]
pub struct UnpauseApproved {
    #[topic]
    pub approver: Address,
    pub approval_count: u32,
}

#[contractevent(data_format = "single-value")]
pub struct UnpauseProposalCancelled {
    pub cancelled_by: Address,
}

// --- User Mint Event ---

#[contractevent]
pub struct UserMint {
    #[topic]
    pub caller: Address,
    pub amount: i128,
    pub uid: u64,
    pub nonce: u64,
}

#[contractevent]
pub struct UserMintWithToken {
    #[topic]
    pub caller: Address,
    pub amount: i128,
    pub payment_token: Address,
    pub payment_amount: i128,
    pub uid: u64,
    pub nonce: u64,
}

// --- Freeze Events ---

#[contractevent]
pub struct FreezeProposalCreated {
    #[topic]
    pub proposer: Address,
    #[topic]
    pub target: Address,
    pub action: soroban_sdk::String,
}

#[contractevent(data_format = "single-value")]
pub struct FreezeProposalApproved {
    #[topic]
    pub approver: Address,
    pub approval_count: u32,
}

#[contractevent(data_format = "single-value")]
pub struct AccountFrozen {
    #[topic]
    pub target: Address,
    pub approvals: Vec<Address>,
}

#[contractevent(data_format = "single-value")]
pub struct AccountUnfrozen {
    #[topic]
    pub target: Address,
    pub approvals: Vec<Address>,
}

#[contractevent(data_format = "single-value")]
pub struct FreezeProposalCancelled {
    pub cancelled_by: Address,
}

// --- Seizure Events ---

#[contractevent]
pub struct SeizureProposalCreated {
    #[topic]
    pub proposer: Address,
    #[topic]
    pub target: Address,
    pub destination: Address,
    pub amount: i128,
}

#[contractevent(data_format = "single-value")]
pub struct SeizureProposalApproved {
    #[topic]
    pub approver: Address,
    pub approval_count: u32,
}

#[contractevent]
pub struct SeizureExecuted {
    #[topic]
    pub target: Address,
    #[topic]
    pub destination: Address,
    pub amount: i128,
    pub approvals: Vec<Address>,
}

#[contractevent(data_format = "single-value")]
pub struct SeizureProposalCancelled {
    pub cancelled_by: Address,
}

// --- Helper publish functions ---

pub fn mint(e: &Env, admin: &Address, to: &Address, amount: i128) {
    Mint {
        admin: admin.clone(),
        to: to.clone(),
        amount,
    }
    .publish(e);
}

pub fn burn(e: &Env, from: &Address, amount: i128) {
    Burn {
        from: from.clone(),
        amount,
    }
    .publish(e);
}

pub fn transfer(e: &Env, from: &Address, to: &Address, amount: i128) {
    Transfer {
        from: from.clone(),
        to: to.clone(),
        amount,
    }
    .publish(e);
}

pub fn approve(e: &Env, from: &Address, spender: &Address, amount: i128, expiration_ledger: u32) {
    Approve {
        from: from.clone(),
        spender: spender.clone(),
        amount,
        expiration_ledger,
    }
    .publish(e);
}

pub fn paused(e: &Env, admin: &Address) {
    Paused {
        admin: admin.clone(),
    }
    .publish(e);
}

pub fn unpaused(e: &Env, approvals: &Vec<Address>) {
    Unpaused {
        approvals: approvals.clone(),
    }
    .publish(e);
}

pub fn upgrade_proposed(e: &Env, proposer: &Address, wasm_hash: &BytesN<32>) {
    UpgradeProposed {
        proposer: proposer.clone(),
        wasm_hash: wasm_hash.clone(),
    }
    .publish(e);
}

pub fn upgrade_approved(e: &Env, approver: &Address, approval_count: u32) {
    UpgradeApproved {
        approver: approver.clone(),
        approval_count,
    }
    .publish(e);
}

pub fn upgrade_executed(e: &Env, wasm_hash: &BytesN<32>, approvals: &Vec<Address>) {
    UpgradeExecuted {
        wasm_hash: wasm_hash.clone(),
        approvals: approvals.clone(),
    }
    .publish(e);
}

pub fn upgrade_cancelled(e: &Env, cancelled_by: &Address) {
    UpgradeCancelled {
        cancelled_by: cancelled_by.clone(),
    }
    .publish(e);
}

pub fn admin_proposal_created(e: &Env, proposer: &Address, target: &Address, action: &str) {
    AdminProposalCreated {
        proposer: proposer.clone(),
        target: target.clone(),
        action: soroban_sdk::String::from_str(e, action),
    }
    .publish(e);
}

pub fn admin_proposal_approved(e: &Env, approver: &Address, approval_count: u32) {
    AdminProposalApproved {
        approver: approver.clone(),
        approval_count,
    }
    .publish(e);
}

pub fn admin_added(e: &Env, new_admin: &Address, approvals: &Vec<Address>) {
    AdminAdded {
        new_admin: new_admin.clone(),
        approvals: approvals.clone(),
    }
    .publish(e);
}

pub fn admin_removed(e: &Env, removed: &Address, approvals: &Vec<Address>) {
    AdminRemoved {
        removed: removed.clone(),
        approvals: approvals.clone(),
    }
    .publish(e);
}

pub fn admin_proposal_cancelled(e: &Env, cancelled_by: &Address) {
    AdminProposalCancelled {
        cancelled_by: cancelled_by.clone(),
    }
    .publish(e);
}

pub fn threshold_proposal_created(e: &Env, proposer: &Address, new_threshold: u32) {
    ThresholdProposalCreated {
        proposer: proposer.clone(),
        new_threshold,
    }
    .publish(e);
}

pub fn threshold_proposal_approved(e: &Env, approver: &Address, approval_count: u32) {
    ThresholdProposalApproved {
        approver: approver.clone(),
        approval_count,
    }
    .publish(e);
}

pub fn threshold_changed(e: &Env, old_threshold: u32, new_threshold: u32) {
    ThresholdChanged {
        old_threshold,
        new_threshold,
    }
    .publish(e);
}

pub fn threshold_proposal_cancelled(e: &Env, cancelled_by: &Address) {
    ThresholdProposalCancelled {
        cancelled_by: cancelled_by.clone(),
    }
    .publish(e);
}

pub fn unpause_proposed(e: &Env, proposer: &Address) {
    UnpauseProposed {
        proposer: proposer.clone(),
    }
    .publish(e);
}

pub fn unpause_approved(e: &Env, approver: &Address, approval_count: u32) {
    UnpauseApproved {
        approver: approver.clone(),
        approval_count,
    }
    .publish(e);
}

pub fn unpause_proposal_cancelled(e: &Env, cancelled_by: &Address) {
    UnpauseProposalCancelled {
        cancelled_by: cancelled_by.clone(),
    }
    .publish(e);
}

pub fn user_mint(e: &Env, caller: &Address, amount: i128, uid: u64, nonce: u64) {
    UserMint {
        caller: caller.clone(),
        amount,
        uid,
        nonce,
    }
    .publish(e);
}

pub fn user_mint_with_token(
    e: &Env,
    caller: &Address,
    amount: i128,
    payment_token: &Address,
    payment_amount: i128,
    uid: u64,
    nonce: u64,
) {
    UserMintWithToken {
        caller: caller.clone(),
        amount,
        payment_token: payment_token.clone(),
        payment_amount,
        uid,
        nonce,
    }
    .publish(e);
}

// --- Freeze event helpers ---

pub fn freeze_proposal_created(e: &Env, proposer: &Address, target: &Address, action: &str) {
    FreezeProposalCreated {
        proposer: proposer.clone(),
        target: target.clone(),
        action: soroban_sdk::String::from_str(e, action),
    }
    .publish(e);
}

pub fn freeze_proposal_approved(e: &Env, approver: &Address, approval_count: u32) {
    FreezeProposalApproved {
        approver: approver.clone(),
        approval_count,
    }
    .publish(e);
}

pub fn account_frozen(e: &Env, target: &Address, approvals: &Vec<Address>) {
    AccountFrozen {
        target: target.clone(),
        approvals: approvals.clone(),
    }
    .publish(e);
}

pub fn account_unfrozen(e: &Env, target: &Address, approvals: &Vec<Address>) {
    AccountUnfrozen {
        target: target.clone(),
        approvals: approvals.clone(),
    }
    .publish(e);
}

pub fn freeze_proposal_cancelled(e: &Env, cancelled_by: &Address) {
    FreezeProposalCancelled {
        cancelled_by: cancelled_by.clone(),
    }
    .publish(e);
}

// --- Seizure event helpers ---

pub fn seizure_proposal_created(
    e: &Env,
    proposer: &Address,
    target: &Address,
    destination: &Address,
    amount: i128,
) {
    SeizureProposalCreated {
        proposer: proposer.clone(),
        target: target.clone(),
        destination: destination.clone(),
        amount,
    }
    .publish(e);
}

pub fn seizure_proposal_approved(e: &Env, approver: &Address, approval_count: u32) {
    SeizureProposalApproved {
        approver: approver.clone(),
        approval_count,
    }
    .publish(e);
}

pub fn seizure_executed(
    e: &Env,
    target: &Address,
    destination: &Address,
    amount: i128,
    approvals: &Vec<Address>,
) {
    SeizureExecuted {
        target: target.clone(),
        destination: destination.clone(),
        amount,
        approvals: approvals.clone(),
    }
    .publish(e);
}

pub fn seizure_proposal_cancelled(e: &Env, cancelled_by: &Address) {
    SeizureProposalCancelled {
        cancelled_by: cancelled_by.clone(),
    }
    .publish(e);
}
