use soroban_sdk::{
    contract, contractimpl, xdr::ToXdr, Address, Bytes, BytesN, Env, IntoVal, String, Symbol, Vec,
};

use crate::admin::{self, extend_instance_ttl, require_admin};
use crate::allowance::{read_allowance, spend_allowance, write_allowance};
use crate::balance::{
    check_not_frozen, decrease_total_supply, increase_total_supply, read_balance, read_frozen,
    read_total_supply, receive_balance, spend_balance,
};
use crate::event;
use crate::freeze;
use crate::metadata::{read_decimal, read_name, read_symbol, write_metadata};
use crate::seizure;
use crate::storage_types::{
    AdminProposal, DataKey, FreezeProposal, SeizureProposal, ThresholdProposal, UnpauseProposal,
    UpgradeProposal,
};
use crate::upgrade;

#[contract]
pub struct LunarxyToken;

fn check_nonnegative_amount(amount: i128) {
    if amount < 0 {
        panic!("negative amount is not allowed");
    }
}

fn check_not_paused(e: &Env) {
    let paused: bool = e
        .storage()
        .instance()
        .get(&DataKey::Paused)
        .unwrap_or(false);
    if paused {
        panic!("contract is paused");
    }
}

fn check_no_duplicate_admins(admins: &Vec<Address>) {
    for i in 0..admins.len() {
        let a = admins.get(i).unwrap();
        for j in (i + 1)..admins.len() {
            if a == admins.get(j).unwrap() {
                panic!("duplicate admin address");
            }
        }
    }
}

#[contractimpl]
impl LunarxyToken {
    // ============================================================
    // Constructor
    // ============================================================

    pub fn __constructor(
        env: Env,
        admins: Vec<Address>,
        threshold: u32,
        name: String,
        symbol: String,
    ) {
        if admins.len() < 3 {
            panic!("minimum 3 admins required");
        }
        if admins.len() > 10 {
            panic!("maximum 10 admins allowed");
        }
        if threshold < 1 {
            panic!("threshold must be at least 1");
        }
        if threshold > admins.len() {
            panic!("threshold cannot exceed admin count");
        }

        check_no_duplicate_admins(&admins);

        admin::write_admins(&env, &admins);
        admin::write_threshold(&env, threshold);
        write_metadata(&env, 0, name, symbol);
        env.storage().instance().set(&DataKey::Paused, &false);
        env.storage().instance().set(&DataKey::Version, &1u32);
        env.storage().instance().set(&DataKey::TotalSupply, &0i128);
    }

    // ============================================================
    // Token View Functions
    // ============================================================

    pub fn balance(env: Env, account: Address) -> i128 {
        extend_instance_ttl(&env);
        read_balance(&env, &account)
    }

    pub fn total_supply(env: Env) -> i128 {
        extend_instance_ttl(&env);
        read_total_supply(&env)
    }

    pub fn decimals(env: Env) -> u32 {
        extend_instance_ttl(&env);
        read_decimal(&env)
    }

    pub fn name(env: Env) -> String {
        extend_instance_ttl(&env);
        read_name(&env)
    }

    pub fn symbol(env: Env) -> String {
        extend_instance_ttl(&env);
        read_symbol(&env)
    }

    pub fn allowance(env: Env, from: Address, spender: Address) -> i128 {
        extend_instance_ttl(&env);
        read_allowance(&env, &from, &spender).amount
    }

    pub fn version(env: Env) -> u32 {
        env.storage().instance().get(&DataKey::Version).unwrap_or(1)
    }

    // ============================================================
    // Token Operations
    // ============================================================

    /// Mint new tokens. Any admin can call this without multi-sig.
    pub fn mint(env: Env, admin: Address, to: Address, amount: i128) {
        admin.require_auth();
        require_admin(&env, &admin);
        check_nonnegative_amount(amount);
        extend_instance_ttl(&env);

        receive_balance(&env, &to, amount);
        increase_total_supply(&env, amount);

        event::mint(&env, &admin, &to, amount);
    }

    /// Burn tokens from caller's own balance.
    pub fn burn(env: Env, from: Address, amount: i128) {
        from.require_auth();
        check_nonnegative_amount(amount);
        check_not_frozen(&env, &from);
        extend_instance_ttl(&env);

        spend_balance(&env, &from, amount);
        decrease_total_supply(&env, amount);

        event::burn(&env, &from, amount);
    }

    /// Burn tokens from another account using allowance.
    pub fn burn_from(env: Env, spender: Address, from: Address, amount: i128) {
        spender.require_auth();
        check_nonnegative_amount(amount);
        check_not_frozen(&env, &from);
        extend_instance_ttl(&env);

        spend_allowance(&env, &from, &spender, amount);
        spend_balance(&env, &from, amount);
        decrease_total_supply(&env, amount);

        event::burn(&env, &from, amount);
    }

    /// Transfer tokens between accounts. Blocked when paused or accounts frozen.
    pub fn transfer(env: Env, from: Address, to: Address, amount: i128) {
        from.require_auth();
        check_not_paused(&env);
        check_nonnegative_amount(amount);
        check_not_frozen(&env, &from);
        check_not_frozen(&env, &to);
        extend_instance_ttl(&env);

        spend_balance(&env, &from, amount);
        receive_balance(&env, &to, amount);

        event::transfer(&env, &from, &to, amount);
    }

    /// Transfer tokens using allowance. Blocked when paused or accounts frozen.
    pub fn transfer_from(env: Env, spender: Address, from: Address, to: Address, amount: i128) {
        spender.require_auth();
        check_not_paused(&env);
        check_nonnegative_amount(amount);
        check_not_frozen(&env, &from);
        check_not_frozen(&env, &to);
        extend_instance_ttl(&env);

        spend_allowance(&env, &from, &spender, amount);
        spend_balance(&env, &from, amount);
        receive_balance(&env, &to, amount);

        event::transfer(&env, &from, &to, amount);
    }

    /// Approve a spender to use tokens on behalf of the owner.
    pub fn approve(
        env: Env,
        from: Address,
        spender: Address,
        amount: i128,
        expiration_ledger: u32,
    ) {
        from.require_auth();
        check_nonnegative_amount(amount);
        check_not_frozen(&env, &from);
        extend_instance_ttl(&env);

        write_allowance(&env, &from, &spender, amount, expiration_ledger);

        event::approve(&env, &from, &spender, amount, expiration_ledger);
    }

    // ============================================================
    // Pause / Unpause
    // ============================================================

    /// Pause the contract. Any single admin can pause (emergency).
    pub fn pause(env: Env, admin: Address) {
        admin.require_auth();
        require_admin(&env, &admin);
        extend_instance_ttl(&env);

        env.storage().instance().set(&DataKey::Paused, &true);

        event::paused(&env, &admin);
    }

    /// Propose unpause (requires multi-sig).
    pub fn propose_unpause(env: Env, proposer: Address) {
        admin::propose_unpause(&env, &proposer);
    }

    /// Approve an unpause proposal.
    pub fn approve_unpause(env: Env, approver: Address) {
        admin::approve_unpause_proposal(&env, &approver);
    }

    /// Cancel an unpause proposal.
    pub fn cancel_unpause(env: Env, caller: Address) {
        admin::cancel_unpause_proposal(&env, &caller);
    }

    /// Check if contract is paused.
    pub fn is_paused(env: Env) -> bool {
        env.storage()
            .instance()
            .get(&DataKey::Paused)
            .unwrap_or(false)
    }

    /// Get the current unpause proposal, if any.
    pub fn get_unpause_proposal(env: Env) -> Option<UnpauseProposal> {
        admin::get_unpause_proposal(&env)
    }

    // ============================================================
    // Multi-Sig: Upgrade
    // ============================================================

    /// Propose a contract upgrade (multi-sig required).
    pub fn propose_upgrade(env: Env, proposer: Address, new_wasm_hash: BytesN<32>) {
        upgrade::propose_upgrade(&env, &proposer, &new_wasm_hash);
    }

    /// Approve a pending upgrade proposal.
    pub fn approve_upgrade(env: Env, approver: Address) {
        upgrade::approve_upgrade(&env, &approver);
    }

    /// Cancel a pending upgrade proposal (only the proposer).
    pub fn cancel_upgrade(env: Env, caller: Address) {
        upgrade::cancel_upgrade(&env, &caller);
    }

    /// Get the current upgrade proposal, if any.
    pub fn get_upgrade_proposal(env: Env) -> Option<UpgradeProposal> {
        upgrade::get_upgrade_proposal(&env)
    }

    /// Called after an upgrade to migrate data if needed.
    pub fn handle_upgrade(env: Env, admin: Address) {
        admin.require_auth();
        require_admin(&env, &admin);
        extend_instance_ttl(&env);
        // Future versions can add migration logic here.
    }

    // ============================================================
    // User Mint (signature-based)
    // ============================================================

    /// Set the Ed25519 public key of the trusted signer (backend server).
    /// Any single admin can call this.
    pub fn set_signer_key(env: Env, admin: Address, signer_key: BytesN<32>) {
        admin.require_auth();
        require_admin(&env, &admin);
        extend_instance_ttl(&env);
        env.storage()
            .instance()
            .set(&DataKey::SignerKey, &signer_key);
    }

    /// Get the configured signer key, if any.
    pub fn get_signer_key(env: Env) -> Option<BytesN<32>> {
        extend_instance_ttl(&env);
        env.storage().instance().get(&DataKey::SignerKey)
    }

    /// Get the current nonce for a wallet address.
    pub fn get_nonce(env: Env, account: Address) -> u64 {
        extend_instance_ttl(&env);
        env.storage()
            .persistent()
            .get(&DataKey::Nonce(account))
            .unwrap_or(0u64)
    }

    /// Mint tokens to the caller using a backend-issued signature.
    ///
    /// The backend signs a message containing all parameters plus the contract
    /// address to prevent cross-contract replay attacks.
    ///
    /// Message layout (SHA-256 over the concatenation of):
    ///   - amount    : 16 bytes little-endian (i128)
    ///   - price     : 16 bytes little-endian (i128)
    ///   - nonce     : 8  bytes little-endian (u64)
    ///   - uid       : 8  bytes little-endian (u64)
    ///   - contract  : 32 bytes (contract's own address bytes)
    ///
    /// The `nonce` must equal the caller's current on-chain nonce; it is
    /// incremented after a successful mint to prevent replay.
    pub fn user_mint(
        env: Env,
        caller: Address,
        amount: i128,
        price: i128,
        nonce: u64,
        uid: u64,
        signature: BytesN<64>,
    ) {
        caller.require_auth();
        check_not_paused(&env);
        check_nonnegative_amount(amount);
        check_not_frozen(&env, &caller);
        extend_instance_ttl(&env);

        // 1. Load signer key (must be configured first).
        let signer_key: BytesN<32> = env
            .storage()
            .instance()
            .get(&DataKey::SignerKey)
            .unwrap_or_else(|| panic!("signer key not configured"));

        // 2. Verify nonce (anti-replay per wallet).
        let stored_nonce: u64 = env
            .storage()
            .persistent()
            .get(&DataKey::Nonce(caller.clone()))
            .unwrap_or(0u64);
        if nonce != stored_nonce {
            panic!("invalid nonce");
        }

        // 3. Build the message to verify.
        //    Layout: amount(16) | price(16) | nonce(8) | uid(8) | contract_addr(32)
        let mut msg_bytes = Bytes::new(&env);

        // amount — 16 bytes little-endian
        for b in amount.to_le_bytes() {
            msg_bytes.push_back(b);
        }
        // price — 16 bytes little-endian
        for b in price.to_le_bytes() {
            msg_bytes.push_back(b);
        }
        // nonce — 8 bytes little-endian
        for b in nonce.to_le_bytes() {
            msg_bytes.push_back(b);
        }
        // uid — 8 bytes little-endian
        for b in uid.to_le_bytes() {
            msg_bytes.push_back(b);
        }
        // contract address — serialized via XDR into the message
        let contract_addr: Address = env.current_contract_address();
        contract_addr.to_xdr(&env).iter().for_each(|b| {
            msg_bytes.push_back(b);
        });

        // 4. Hash the message (Ed25519 verify expects the raw 32-byte digest).
        let message_hash: BytesN<32> = env.crypto().sha256(&msg_bytes).into();

        // 5. Verify Ed25519 signature.
        env.crypto()
            .ed25519_verify(&signer_key, &message_hash.into(), &signature);

        // 6. Advance the nonce to prevent replay.
        env.storage()
            .persistent()
            .set(&DataKey::Nonce(caller.clone()), &(stored_nonce + 1));

        // 7. Mint tokens.
        receive_balance(&env, &caller, amount);
        increase_total_supply(&env, amount);

        event::user_mint(&env, &caller, amount, uid, nonce);
    }

    /// Mint tokens to the caller using a backend-issued signature, paying with
    /// an external fungible token (any SEP-41 / Stellar Asset Contract).
    ///
    /// Before calling this method the caller MUST have called
    /// `approve(caller, this_contract, payment_amount, expiration_ledger)`
    /// on the `payment_token` contract so that this contract can pull the funds.
    ///
    /// Message layout (SHA-256 over the concatenation of):
    ///   - amount         : 16 bytes little-endian (i128)
    ///   - payment_amount : 16 bytes little-endian (i128)
    ///   - nonce          : 8  bytes little-endian (u64)
    ///   - uid            : 8  bytes little-endian (u64)
    ///   - contract       : XDR bytes of this contract's own address
    ///   - payment_token  : XDR bytes of the payment token contract address
    ///
    /// Including `payment_token` and `payment_amount` in the signed message
    /// prevents the caller from substituting a cheaper token or a lower amount.
    #[allow(clippy::too_many_arguments)]
    pub fn user_mint_with_token(
        env: Env,
        caller: Address,
        amount: i128,
        payment_token: Address,
        payment_amount: i128,
        nonce: u64,
        uid: u64,
        signature: BytesN<64>,
    ) {
        caller.require_auth();
        check_not_paused(&env);
        check_nonnegative_amount(amount);
        check_nonnegative_amount(payment_amount);
        check_not_frozen(&env, &caller);
        extend_instance_ttl(&env);

        // 1. Load signer key (must be configured first).
        let signer_key: BytesN<32> = env
            .storage()
            .instance()
            .get(&DataKey::SignerKey)
            .unwrap_or_else(|| panic!("signer key not configured"));

        // 2. Verify nonce (anti-replay per wallet).
        let stored_nonce: u64 = env
            .storage()
            .persistent()
            .get(&DataKey::Nonce(caller.clone()))
            .unwrap_or(0u64);
        if nonce != stored_nonce {
            panic!("invalid nonce");
        }

        // 3. Build the message to verify.
        //    Layout: amount(16) | payment_amount(16) | nonce(8) | uid(8)
        //            | contract_xdr | payment_token_xdr
        let mut msg_bytes = Bytes::new(&env);

        // amount — 16 bytes little-endian
        for b in amount.to_le_bytes() {
            msg_bytes.push_back(b);
        }
        // payment_amount — 16 bytes little-endian
        for b in payment_amount.to_le_bytes() {
            msg_bytes.push_back(b);
        }
        // nonce — 8 bytes little-endian
        for b in nonce.to_le_bytes() {
            msg_bytes.push_back(b);
        }
        // uid — 8 bytes little-endian
        for b in uid.to_le_bytes() {
            msg_bytes.push_back(b);
        }
        // this contract's address — prevents cross-contract replay
        let contract_addr: Address = env.current_contract_address();
        contract_addr.to_xdr(&env).iter().for_each(|b| {
            msg_bytes.push_back(b);
        });
        // payment token address — prevents swapping the token after signing
        payment_token.clone().to_xdr(&env).iter().for_each(|b| {
            msg_bytes.push_back(b);
        });

        // 4. Hash the message.
        let message_hash: BytesN<32> = env.crypto().sha256(&msg_bytes).into();

        // 5. Verify Ed25519 signature.
        env.crypto()
            .ed25519_verify(&signer_key, &message_hash.into(), &signature);

        // 6. Advance the nonce to prevent replay.
        env.storage()
            .persistent()
            .set(&DataKey::Nonce(caller.clone()), &(stored_nonce + 1));

        // 7. Pull payment tokens from the caller into this contract.
        //    Requires the caller to have pre-approved this contract as spender.
        env.invoke_contract::<()>(
            &payment_token,
            &Symbol::new(&env, "transfer_from"),
            Vec::from_array(
                &env,
                [
                    env.current_contract_address().into_val(&env),
                    caller.clone().into_val(&env),
                    env.current_contract_address().into_val(&env),
                    payment_amount.into_val(&env),
                ],
            ),
        );

        // 8. Mint LunarXY tokens to the caller.
        receive_balance(&env, &caller, amount);
        increase_total_supply(&env, amount);

        event::user_mint_with_token(
            &env,
            &caller,
            amount,
            &payment_token,
            payment_amount,
            uid,
            nonce,
        );
    }

    // ============================================================
    // Multi-Sig: Admin Management
    // ============================================================

    /// Propose adding a new admin (multi-sig required).
    pub fn propose_add_admin(env: Env, proposer: Address, new_admin: Address) {
        admin::propose_add_admin_with_target(&env, &proposer, &new_admin);
    }

    /// Propose removing an admin (multi-sig required).
    pub fn propose_remove_admin(env: Env, proposer: Address, admin_to_remove: Address) {
        admin::propose_remove_admin_with_target(&env, &proposer, &admin_to_remove);
    }

    /// Approve a pending admin proposal.
    pub fn approve_admin_proposal(env: Env, approver: Address) {
        admin::approve_admin_proposal(&env, &approver);
    }

    /// Cancel a pending admin proposal (only the proposer).
    pub fn cancel_admin_proposal(env: Env, caller: Address) {
        admin::cancel_admin_proposal(&env, &caller);
    }

    /// Get the current admin proposal, if any.
    pub fn get_admin_proposal(env: Env) -> Option<AdminProposal> {
        admin::get_admin_proposal(&env)
    }

    /// Get all admins.
    pub fn get_admins(env: Env) -> Vec<Address> {
        admin::read_admins(&env)
    }

    /// Get the current threshold.
    pub fn get_threshold(env: Env) -> u32 {
        admin::read_threshold(&env)
    }

    // ============================================================
    // Multi-Sig: Threshold Change
    // ============================================================

    /// Propose changing the approval threshold (multi-sig required).
    pub fn propose_change_threshold(env: Env, proposer: Address, new_threshold: u32) {
        admin::propose_change_threshold(&env, &proposer, new_threshold);
    }

    /// Approve a pending threshold change proposal.
    pub fn approve_threshold_proposal(env: Env, approver: Address) {
        admin::approve_threshold_proposal(&env, &approver);
    }

    /// Cancel a pending threshold change proposal (only the proposer).
    pub fn cancel_threshold_proposal(env: Env, caller: Address) {
        admin::cancel_threshold_proposal(&env, &caller);
    }

    /// Get the current threshold proposal, if any.
    pub fn get_threshold_proposal(env: Env) -> Option<ThresholdProposal> {
        admin::get_threshold_proposal(&env)
    }

    // ============================================================
    // Multi-Sig: Freeze / Unfreeze
    // ============================================================

    /// Propose freezing an account (multi-sig required).
    pub fn propose_freeze(env: Env, proposer: Address, target: Address) {
        freeze::propose_freeze(&env, &proposer, &target);
    }

    /// Propose unfreezing an account (multi-sig required).
    pub fn propose_unfreeze(env: Env, proposer: Address, target: Address) {
        freeze::propose_unfreeze(&env, &proposer, &target);
    }

    /// Approve a pending freeze/unfreeze proposal.
    pub fn approve_freeze_proposal(env: Env, approver: Address) {
        freeze::approve_freeze_proposal(&env, &approver);
    }

    /// Cancel a pending freeze/unfreeze proposal (only the proposer).
    pub fn cancel_freeze_proposal(env: Env, caller: Address) {
        freeze::cancel_freeze_proposal(&env, &caller);
    }

    /// Check if an account is frozen.
    pub fn is_frozen(env: Env, account: Address) -> bool {
        extend_instance_ttl(&env);
        read_frozen(&env, &account)
    }

    /// Get the current freeze proposal, if any.
    pub fn get_freeze_proposal(env: Env) -> Option<FreezeProposal> {
        freeze::get_freeze_proposal(&env)
    }

    // ============================================================
    // Multi-Sig: Seizure (Embargo)
    // ============================================================

    /// Propose seizing tokens from a frozen account (multi-sig required).
    pub fn propose_seizure(
        env: Env,
        proposer: Address,
        target: Address,
        destination: Address,
        amount: i128,
    ) {
        seizure::propose_seizure(&env, &proposer, &target, &destination, amount);
    }

    /// Approve a pending seizure proposal.
    pub fn approve_seizure(env: Env, approver: Address) {
        seizure::approve_seizure(&env, &approver);
    }

    /// Cancel a pending seizure proposal (only the proposer).
    pub fn cancel_seizure(env: Env, caller: Address) {
        seizure::cancel_seizure(&env, &caller);
    }

    /// Get the current seizure proposal, if any.
    pub fn get_seizure_proposal(env: Env) -> Option<SeizureProposal> {
        seizure::get_seizure_proposal(&env)
    }
}
