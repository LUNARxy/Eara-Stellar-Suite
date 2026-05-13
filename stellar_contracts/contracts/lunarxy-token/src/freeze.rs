use soroban_sdk::{Address, Env, Vec};

use crate::admin::{extend_instance_ttl, is_admin, read_threshold, require_admin};
use crate::balance::{read_frozen, write_frozen};
use crate::event;
use crate::storage_types::{DataKey, FreezeAction, FreezeProposal};

fn has_approved(approvals: &Vec<Address>, addr: &Address) -> bool {
    approvals.contains(addr)
}

// ============================================================
// Freeze Proposals (Freeze / Unfreeze an account)
// ============================================================

pub fn propose_freeze(e: &Env, proposer: &Address, target: &Address) {
    proposer.require_auth();
    require_admin(e, proposer);
    extend_instance_ttl(e);

    if is_admin(e, target) {
        panic!("cannot freeze an admin address");
    }

    if read_frozen(e, target) {
        panic!("account is already frozen");
    }

    if e.storage()
        .instance()
        .get::<DataKey, FreezeProposal>(&DataKey::FreezeProposal)
        .is_some()
    {
        panic!("a freeze proposal is already active");
    }

    let mut approvals = Vec::new(e);
    approvals.push_back(proposer.clone());

    let proposal = FreezeProposal {
        action: FreezeAction::Freeze,
        target: target.clone(),
        proposer: proposer.clone(),
        approvals,
    };

    e.storage()
        .instance()
        .set(&DataKey::FreezeProposal, &proposal);

    event::freeze_proposal_created(e, proposer, target, "freeze");

    maybe_execute_freeze_proposal(e);
}

pub fn propose_unfreeze(e: &Env, proposer: &Address, target: &Address) {
    proposer.require_auth();
    require_admin(e, proposer);
    extend_instance_ttl(e);

    if !read_frozen(e, target) {
        panic!("account is not frozen");
    }

    if e.storage()
        .instance()
        .get::<DataKey, FreezeProposal>(&DataKey::FreezeProposal)
        .is_some()
    {
        panic!("a freeze proposal is already active");
    }

    let mut approvals = Vec::new(e);
    approvals.push_back(proposer.clone());

    let proposal = FreezeProposal {
        action: FreezeAction::Unfreeze,
        target: target.clone(),
        proposer: proposer.clone(),
        approvals,
    };

    e.storage()
        .instance()
        .set(&DataKey::FreezeProposal, &proposal);

    event::freeze_proposal_created(e, proposer, target, "unfreeze");

    maybe_execute_freeze_proposal(e);
}

pub fn approve_freeze_proposal(e: &Env, approver: &Address) {
    approver.require_auth();
    require_admin(e, approver);
    extend_instance_ttl(e);

    let mut proposal: FreezeProposal = e
        .storage()
        .instance()
        .get(&DataKey::FreezeProposal)
        .expect("no active freeze proposal");

    if has_approved(&proposal.approvals, approver) {
        panic!("already approved this proposal");
    }

    proposal.approvals.push_back(approver.clone());
    e.storage()
        .instance()
        .set(&DataKey::FreezeProposal, &proposal);

    event::freeze_proposal_approved(e, approver, proposal.approvals.len());

    maybe_execute_freeze_proposal(e);
}

pub fn cancel_freeze_proposal(e: &Env, caller: &Address) {
    caller.require_auth();
    require_admin(e, caller);
    extend_instance_ttl(e);

    let proposal: FreezeProposal = e
        .storage()
        .instance()
        .get(&DataKey::FreezeProposal)
        .expect("no active freeze proposal");

    if proposal.proposer != *caller {
        panic!("only the proposer can cancel");
    }

    e.storage().instance().remove(&DataKey::FreezeProposal);
    event::freeze_proposal_cancelled(e, caller);
}

pub fn get_freeze_proposal(e: &Env) -> Option<FreezeProposal> {
    e.storage()
        .instance()
        .get::<DataKey, FreezeProposal>(&DataKey::FreezeProposal)
}

fn maybe_execute_freeze_proposal(e: &Env) {
    let proposal: FreezeProposal = match e.storage().instance().get(&DataKey::FreezeProposal) {
        Some(p) => p,
        None => return,
    };

    let threshold = read_threshold(e);
    if proposal.approvals.len() < threshold {
        return;
    }

    match proposal.action {
        FreezeAction::Freeze => {
            write_frozen(e, &proposal.target, true);
            event::account_frozen(e, &proposal.target, &proposal.approvals);
        }
        FreezeAction::Unfreeze => {
            write_frozen(e, &proposal.target, false);
            event::account_unfrozen(e, &proposal.target, &proposal.approvals);
        }
    }

    e.storage().instance().remove(&DataKey::FreezeProposal);
}
