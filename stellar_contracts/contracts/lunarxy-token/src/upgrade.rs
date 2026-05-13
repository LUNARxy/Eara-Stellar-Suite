use soroban_sdk::{Address, BytesN, Env, Vec};

use crate::admin::{read_threshold, require_admin};
use crate::event;
use crate::storage_types::{
    DataKey, UpgradeProposal, INSTANCE_BUMP_AMOUNT, INSTANCE_LIFETIME_THRESHOLD,
};

fn extend_instance_ttl(e: &Env) {
    e.storage()
        .instance()
        .extend_ttl(INSTANCE_LIFETIME_THRESHOLD, INSTANCE_BUMP_AMOUNT);
}

fn has_approved(approvals: &Vec<Address>, addr: &Address) -> bool {
    approvals.contains(addr)
}

pub fn propose_upgrade(e: &Env, proposer: &Address, new_wasm_hash: &BytesN<32>) {
    proposer.require_auth();
    require_admin(e, proposer);
    extend_instance_ttl(e);

    if e.storage()
        .instance()
        .get::<DataKey, UpgradeProposal>(&DataKey::UpgradeProposal)
        .is_some()
    {
        panic!("an upgrade proposal is already active");
    }

    let mut approvals = Vec::new(e);
    approvals.push_back(proposer.clone());

    let proposal = UpgradeProposal {
        wasm_hash: new_wasm_hash.clone(),
        proposer: proposer.clone(),
        approvals: approvals.clone(),
    };

    e.storage()
        .instance()
        .set(&DataKey::UpgradeProposal, &proposal);

    event::upgrade_proposed(e, proposer, new_wasm_hash);

    maybe_execute_upgrade(e);
}

pub fn approve_upgrade(e: &Env, approver: &Address) {
    approver.require_auth();
    require_admin(e, approver);
    extend_instance_ttl(e);

    let mut proposal: UpgradeProposal = e
        .storage()
        .instance()
        .get(&DataKey::UpgradeProposal)
        .expect("no active upgrade proposal");

    if has_approved(&proposal.approvals, approver) {
        panic!("already approved this proposal");
    }

    proposal.approvals.push_back(approver.clone());
    e.storage()
        .instance()
        .set(&DataKey::UpgradeProposal, &proposal);

    event::upgrade_approved(e, approver, proposal.approvals.len());

    maybe_execute_upgrade(e);
}

pub fn cancel_upgrade(e: &Env, caller: &Address) {
    caller.require_auth();
    require_admin(e, caller);
    extend_instance_ttl(e);

    let proposal: UpgradeProposal = e
        .storage()
        .instance()
        .get(&DataKey::UpgradeProposal)
        .expect("no active upgrade proposal");

    if proposal.proposer != *caller {
        panic!("only the proposer can cancel");
    }

    e.storage().instance().remove(&DataKey::UpgradeProposal);
    event::upgrade_cancelled(e, caller);
}

pub fn get_upgrade_proposal(e: &Env) -> Option<UpgradeProposal> {
    e.storage()
        .instance()
        .get::<DataKey, UpgradeProposal>(&DataKey::UpgradeProposal)
}

fn maybe_execute_upgrade(e: &Env) {
    let proposal: UpgradeProposal = match e.storage().instance().get(&DataKey::UpgradeProposal) {
        Some(p) => p,
        None => return,
    };

    let threshold = read_threshold(e);
    if proposal.approvals.len() < threshold {
        return;
    }

    // Increment version
    let version: u32 = e.storage().instance().get(&DataKey::Version).unwrap_or(1);
    e.storage()
        .instance()
        .set(&DataKey::Version, &(version + 1));

    event::upgrade_executed(e, &proposal.wasm_hash, &proposal.approvals);

    // Remove proposal before executing the upgrade
    e.storage().instance().remove(&DataKey::UpgradeProposal);

    // Execute the upgrade - this replaces the contract code
    e.deployer()
        .update_current_contract_wasm(proposal.wasm_hash);
}
