use soroban_sdk::{Address, Env, Vec};

use crate::event;
use crate::storage_types::{
    AdminAction, AdminProposal, DataKey, ThresholdProposal, UnpauseProposal, INSTANCE_BUMP_AMOUNT,
    INSTANCE_LIFETIME_THRESHOLD,
};

// ============================================================
// Admin list helpers
// ============================================================

pub fn read_admins(e: &Env) -> Vec<Address> {
    e.storage().instance().get(&DataKey::Admins).unwrap()
}

pub fn write_admins(e: &Env, admins: &Vec<Address>) {
    e.storage().instance().set(&DataKey::Admins, admins);
}

pub fn read_threshold(e: &Env) -> u32 {
    e.storage().instance().get(&DataKey::Threshold).unwrap()
}

pub fn write_threshold(e: &Env, threshold: u32) {
    e.storage().instance().set(&DataKey::Threshold, &threshold);
}

pub fn is_admin(e: &Env, addr: &Address) -> bool {
    let admins = read_admins(e);
    admins.contains(addr)
}

pub fn require_admin(e: &Env, addr: &Address) {
    if !is_admin(e, addr) {
        panic!("not an admin");
    }
}

pub fn extend_instance_ttl(e: &Env) {
    e.storage()
        .instance()
        .extend_ttl(INSTANCE_LIFETIME_THRESHOLD, INSTANCE_BUMP_AMOUNT);
}

fn has_approved(approvals: &Vec<Address>, addr: &Address) -> bool {
    approvals.contains(addr)
}

// ============================================================
// Admin Proposals (Add / Remove admin)
// ============================================================

pub fn propose_add_admin_with_target(e: &Env, proposer: &Address, new_admin: &Address) {
    proposer.require_auth();
    require_admin(e, proposer);
    extend_instance_ttl(e);

    if is_admin(e, new_admin) {
        panic!("address is already an admin");
    }

    if e.storage()
        .instance()
        .get::<DataKey, AdminProposal>(&DataKey::AdminProposal)
        .is_some()
    {
        panic!("an admin proposal is already active");
    }

    let mut approvals = Vec::new(e);
    approvals.push_back(proposer.clone());

    let proposal = AdminProposal {
        action: AdminAction::Add,
        target: new_admin.clone(),
        proposer: proposer.clone(),
        approvals,
    };

    e.storage()
        .instance()
        .set(&DataKey::AdminProposal, &proposal);

    event::admin_proposal_created(e, proposer, new_admin, "add");

    maybe_execute_admin_proposal(e);
}

pub fn propose_remove_admin_with_target(e: &Env, proposer: &Address, admin_to_remove: &Address) {
    proposer.require_auth();
    require_admin(e, proposer);
    extend_instance_ttl(e);

    if !is_admin(e, admin_to_remove) {
        panic!("address is not an admin");
    }

    let admins = read_admins(e);
    let threshold = read_threshold(e);
    if admins.len() <= threshold {
        panic!("cannot remove admin: would go below threshold");
    }

    if e.storage()
        .instance()
        .get::<DataKey, AdminProposal>(&DataKey::AdminProposal)
        .is_some()
    {
        panic!("an admin proposal is already active");
    }

    let mut approvals = Vec::new(e);
    approvals.push_back(proposer.clone());

    let proposal = AdminProposal {
        action: AdminAction::Remove,
        target: admin_to_remove.clone(),
        proposer: proposer.clone(),
        approvals,
    };

    e.storage()
        .instance()
        .set(&DataKey::AdminProposal, &proposal);

    event::admin_proposal_created(e, proposer, admin_to_remove, "remove");

    maybe_execute_admin_proposal(e);
}

pub fn approve_admin_proposal(e: &Env, approver: &Address) {
    approver.require_auth();
    require_admin(e, approver);
    extend_instance_ttl(e);

    let mut proposal: AdminProposal = e
        .storage()
        .instance()
        .get(&DataKey::AdminProposal)
        .expect("no active admin proposal");

    if has_approved(&proposal.approvals, approver) {
        panic!("already approved this proposal");
    }

    proposal.approvals.push_back(approver.clone());
    e.storage()
        .instance()
        .set(&DataKey::AdminProposal, &proposal);

    event::admin_proposal_approved(e, approver, proposal.approvals.len());

    maybe_execute_admin_proposal(e);
}

pub fn cancel_admin_proposal(e: &Env, caller: &Address) {
    caller.require_auth();
    require_admin(e, caller);
    extend_instance_ttl(e);

    let proposal: AdminProposal = e
        .storage()
        .instance()
        .get(&DataKey::AdminProposal)
        .expect("no active admin proposal");

    if proposal.proposer != *caller {
        panic!("only the proposer can cancel");
    }

    e.storage().instance().remove(&DataKey::AdminProposal);
    event::admin_proposal_cancelled(e, caller);
}

pub fn get_admin_proposal(e: &Env) -> Option<AdminProposal> {
    e.storage()
        .instance()
        .get::<DataKey, AdminProposal>(&DataKey::AdminProposal)
}

fn maybe_execute_admin_proposal(e: &Env) {
    let proposal: AdminProposal = match e.storage().instance().get(&DataKey::AdminProposal) {
        Some(p) => p,
        None => return,
    };

    let threshold = read_threshold(e);
    if proposal.approvals.len() < threshold {
        return;
    }

    let mut admins = read_admins(e);

    match proposal.action {
        AdminAction::Add => {
            admins.push_back(proposal.target.clone());
            write_admins(e, &admins);
            event::admin_added(e, &proposal.target, &proposal.approvals);
        }
        AdminAction::Remove => {
            let mut new_admins = Vec::new(e);
            for i in 0..admins.len() {
                let a = admins.get(i).unwrap();
                if a != proposal.target {
                    new_admins.push_back(a);
                }
            }
            write_admins(e, &new_admins);
            event::admin_removed(e, &proposal.target, &proposal.approvals);
        }
    }

    e.storage().instance().remove(&DataKey::AdminProposal);
}

// ============================================================
// Threshold Proposals
// ============================================================

pub fn propose_change_threshold(e: &Env, proposer: &Address, new_threshold: u32) {
    proposer.require_auth();
    require_admin(e, proposer);
    extend_instance_ttl(e);

    let admins = read_admins(e);
    if new_threshold < 1 || new_threshold > admins.len() {
        panic!("invalid threshold: must be between 1 and admin count");
    }

    if e.storage()
        .instance()
        .get::<DataKey, ThresholdProposal>(&DataKey::ThresholdProposal)
        .is_some()
    {
        panic!("a threshold proposal is already active");
    }

    let mut approvals = Vec::new(e);
    approvals.push_back(proposer.clone());

    let proposal = ThresholdProposal {
        new_threshold,
        proposer: proposer.clone(),
        approvals,
    };

    e.storage()
        .instance()
        .set(&DataKey::ThresholdProposal, &proposal);

    event::threshold_proposal_created(e, proposer, new_threshold);

    maybe_execute_threshold_proposal(e);
}

pub fn approve_threshold_proposal(e: &Env, approver: &Address) {
    approver.require_auth();
    require_admin(e, approver);
    extend_instance_ttl(e);

    let mut proposal: ThresholdProposal = e
        .storage()
        .instance()
        .get(&DataKey::ThresholdProposal)
        .expect("no active threshold proposal");

    if has_approved(&proposal.approvals, approver) {
        panic!("already approved this proposal");
    }

    proposal.approvals.push_back(approver.clone());
    e.storage()
        .instance()
        .set(&DataKey::ThresholdProposal, &proposal);

    event::threshold_proposal_approved(e, approver, proposal.approvals.len());

    maybe_execute_threshold_proposal(e);
}

pub fn cancel_threshold_proposal(e: &Env, caller: &Address) {
    caller.require_auth();
    require_admin(e, caller);
    extend_instance_ttl(e);

    let proposal: ThresholdProposal = e
        .storage()
        .instance()
        .get(&DataKey::ThresholdProposal)
        .expect("no active threshold proposal");

    if proposal.proposer != *caller {
        panic!("only the proposer can cancel");
    }

    e.storage().instance().remove(&DataKey::ThresholdProposal);
    event::threshold_proposal_cancelled(e, caller);
}

pub fn get_threshold_proposal(e: &Env) -> Option<ThresholdProposal> {
    e.storage()
        .instance()
        .get::<DataKey, ThresholdProposal>(&DataKey::ThresholdProposal)
}

fn maybe_execute_threshold_proposal(e: &Env) {
    let proposal: ThresholdProposal = match e.storage().instance().get(&DataKey::ThresholdProposal)
    {
        Some(p) => p,
        None => return,
    };

    let threshold = read_threshold(e);
    if proposal.approvals.len() < threshold {
        return;
    }

    let old_threshold = threshold;
    write_threshold(e, proposal.new_threshold);
    event::threshold_changed(e, old_threshold, proposal.new_threshold);

    e.storage().instance().remove(&DataKey::ThresholdProposal);
}

// ============================================================
// Unpause Proposals
// ============================================================

pub fn propose_unpause(e: &Env, proposer: &Address) {
    proposer.require_auth();
    require_admin(e, proposer);
    extend_instance_ttl(e);

    if e.storage()
        .instance()
        .get::<DataKey, UnpauseProposal>(&DataKey::UnpauseProposal)
        .is_some()
    {
        panic!("an unpause proposal is already active");
    }

    let mut approvals = Vec::new(e);
    approvals.push_back(proposer.clone());

    let proposal = UnpauseProposal {
        proposer: proposer.clone(),
        approvals,
    };

    e.storage()
        .instance()
        .set(&DataKey::UnpauseProposal, &proposal);

    event::unpause_proposed(e, proposer);

    maybe_execute_unpause_proposal(e);
}

pub fn approve_unpause_proposal(e: &Env, approver: &Address) {
    approver.require_auth();
    require_admin(e, approver);
    extend_instance_ttl(e);

    let mut proposal: UnpauseProposal = e
        .storage()
        .instance()
        .get(&DataKey::UnpauseProposal)
        .expect("no active unpause proposal");

    if has_approved(&proposal.approvals, approver) {
        panic!("already approved this proposal");
    }

    proposal.approvals.push_back(approver.clone());
    e.storage()
        .instance()
        .set(&DataKey::UnpauseProposal, &proposal);

    event::unpause_approved(e, approver, proposal.approvals.len());

    maybe_execute_unpause_proposal(e);
}

pub fn cancel_unpause_proposal(e: &Env, caller: &Address) {
    caller.require_auth();
    require_admin(e, caller);
    extend_instance_ttl(e);

    let proposal: UnpauseProposal = e
        .storage()
        .instance()
        .get(&DataKey::UnpauseProposal)
        .expect("no active unpause proposal");

    if proposal.proposer != *caller {
        panic!("only the proposer can cancel");
    }

    e.storage().instance().remove(&DataKey::UnpauseProposal);
    event::unpause_proposal_cancelled(e, caller);
}

pub fn get_unpause_proposal(e: &Env) -> Option<UnpauseProposal> {
    e.storage()
        .instance()
        .get::<DataKey, UnpauseProposal>(&DataKey::UnpauseProposal)
}

fn maybe_execute_unpause_proposal(e: &Env) {
    let proposal: UnpauseProposal = match e.storage().instance().get(&DataKey::UnpauseProposal) {
        Some(p) => p,
        None => return,
    };

    let threshold = read_threshold(e);
    if proposal.approvals.len() < threshold {
        return;
    }

    e.storage().instance().set(&DataKey::Paused, &false);
    event::unpaused(e, &proposal.approvals);

    e.storage().instance().remove(&DataKey::UnpauseProposal);
}
