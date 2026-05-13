use soroban_sdk::{Address, Env, Vec};

use crate::admin::{extend_instance_ttl, read_threshold, require_admin};
use crate::balance::{read_balance, read_frozen, receive_balance, spend_balance};
use crate::event;
use crate::storage_types::{DataKey, SeizureProposal};

fn has_approved(approvals: &Vec<Address>, addr: &Address) -> bool {
    approvals.contains(addr)
}

// ============================================================
// Seizure Proposals (confiscate tokens from a frozen account)
// ============================================================

pub fn propose_seizure(
    e: &Env,
    proposer: &Address,
    target: &Address,
    destination: &Address,
    amount: i128,
) {
    proposer.require_auth();
    require_admin(e, proposer);
    extend_instance_ttl(e);

    if !read_frozen(e, target) {
        panic!("target account is not frozen");
    }

    if amount <= 0 {
        panic!("seizure amount must be positive");
    }

    let balance = read_balance(e, target);
    if balance < amount {
        panic!("seizure amount exceeds target balance");
    }

    if target == destination {
        panic!("destination cannot be the frozen account");
    }

    if e.storage()
        .instance()
        .get::<DataKey, SeizureProposal>(&DataKey::SeizureProposal)
        .is_some()
    {
        panic!("a seizure proposal is already active");
    }

    let mut approvals = Vec::new(e);
    approvals.push_back(proposer.clone());

    let proposal = SeizureProposal {
        target: target.clone(),
        destination: destination.clone(),
        amount,
        proposer: proposer.clone(),
        approvals,
    };

    e.storage()
        .instance()
        .set(&DataKey::SeizureProposal, &proposal);

    event::seizure_proposal_created(e, proposer, target, destination, amount);

    maybe_execute_seizure(e);
}

pub fn approve_seizure(e: &Env, approver: &Address) {
    approver.require_auth();
    require_admin(e, approver);
    extend_instance_ttl(e);

    let mut proposal: SeizureProposal = e
        .storage()
        .instance()
        .get(&DataKey::SeizureProposal)
        .expect("no active seizure proposal");

    if has_approved(&proposal.approvals, approver) {
        panic!("already approved this proposal");
    }

    proposal.approvals.push_back(approver.clone());
    e.storage()
        .instance()
        .set(&DataKey::SeizureProposal, &proposal);

    event::seizure_proposal_approved(e, approver, proposal.approvals.len());

    maybe_execute_seizure(e);
}

pub fn cancel_seizure(e: &Env, caller: &Address) {
    caller.require_auth();
    require_admin(e, caller);
    extend_instance_ttl(e);

    let proposal: SeizureProposal = e
        .storage()
        .instance()
        .get(&DataKey::SeizureProposal)
        .expect("no active seizure proposal");

    if proposal.proposer != *caller {
        panic!("only the proposer can cancel");
    }

    e.storage().instance().remove(&DataKey::SeizureProposal);
    event::seizure_proposal_cancelled(e, caller);
}

pub fn get_seizure_proposal(e: &Env) -> Option<SeizureProposal> {
    e.storage()
        .instance()
        .get::<DataKey, SeizureProposal>(&DataKey::SeizureProposal)
}

fn maybe_execute_seizure(e: &Env) {
    let proposal: SeizureProposal = match e.storage().instance().get(&DataKey::SeizureProposal) {
        Some(p) => p,
        None => return,
    };

    let threshold = read_threshold(e);
    if proposal.approvals.len() < threshold {
        return;
    }

    // Re-validate at execution time
    if !read_frozen(e, &proposal.target) {
        panic!("target account is no longer frozen");
    }

    let balance = read_balance(e, &proposal.target);
    if balance < proposal.amount {
        panic!("target balance is now insufficient for seizure");
    }

    // Move tokens from target to destination
    spend_balance(e, &proposal.target, proposal.amount);
    receive_balance(e, &proposal.destination, proposal.amount);

    event::seizure_executed(
        e,
        &proposal.target,
        &proposal.destination,
        proposal.amount,
        &proposal.approvals,
    );

    e.storage().instance().remove(&DataKey::SeizureProposal);
}
