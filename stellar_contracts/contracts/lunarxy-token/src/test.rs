#![cfg(test)]

use soroban_sdk::{testutils::Address as _, vec, Address, Env, String};

use crate::contract::{LunarxyToken, LunarxyTokenClient};

// ============================================================
// Helpers
// ============================================================

fn create_token<'a>(env: &Env) -> (LunarxyTokenClient<'a>, [Address; 5]) {
    let admins = [
        Address::generate(env),
        Address::generate(env),
        Address::generate(env),
        Address::generate(env),
        Address::generate(env),
    ];

    let admin_vec = vec![
        env,
        admins[0].clone(),
        admins[1].clone(),
        admins[2].clone(),
        admins[3].clone(),
        admins[4].clone(),
    ];

    let contract_id = env.register(
        LunarxyToken,
        (
            admin_vec,
            3u32,
            String::from_str(env, "LUNARXY"),
            String::from_str(env, "LUNARXY"),
        ),
    );

    let client = LunarxyTokenClient::new(env, &contract_id);
    (client, admins)
}

// ============================================================
// Constructor Tests
// ============================================================

#[test]
fn test_initialize() {
    let env = Env::default();
    let (client, _admins) = create_token(&env);

    assert_eq!(client.name(), String::from_str(&env, "LUNARXY"));
    assert_eq!(client.symbol(), String::from_str(&env, "LUNARXY"));
    assert_eq!(client.decimals(), 0);
    assert_eq!(client.total_supply(), 0);
    assert_eq!(client.version(), 1);
    assert!(!client.is_paused());
}

#[test]
fn test_admins_initialized() {
    let env = Env::default();
    let (client, admins) = create_token(&env);

    let stored_admins = client.get_admins();
    assert_eq!(stored_admins.len(), 5);
    assert_eq!(client.get_threshold(), 3);

    for admin in &admins {
        assert!(stored_admins.contains(admin));
    }
}

#[test]
#[should_panic(expected = "minimum 3 admins required")]
fn test_constructor_too_few_admins() {
    let env = Env::default();
    let admins = vec![&env, Address::generate(&env), Address::generate(&env)];
    env.register(
        LunarxyToken,
        (
            admins,
            2u32,
            String::from_str(&env, "LUNARXY"),
            String::from_str(&env, "LUNARXY"),
        ),
    );
}

#[test]
#[should_panic(expected = "threshold cannot exceed admin count")]
fn test_constructor_threshold_exceeds_admins() {
    let env = Env::default();
    let admins = vec![
        &env,
        Address::generate(&env),
        Address::generate(&env),
        Address::generate(&env),
    ];
    env.register(
        LunarxyToken,
        (
            admins,
            5u32,
            String::from_str(&env, "LUNARXY"),
            String::from_str(&env, "LUNARXY"),
        ),
    );
}

#[test]
#[should_panic(expected = "duplicate admin address")]
fn test_constructor_duplicate_admins() {
    let env = Env::default();
    let dup = Address::generate(&env);
    let admins = vec![&env, dup.clone(), dup.clone(), Address::generate(&env)];
    env.register(
        LunarxyToken,
        (
            admins,
            2u32,
            String::from_str(&env, "LUNARXY"),
            String::from_str(&env, "LUNARXY"),
        ),
    );
}

// ============================================================
// Mint Tests
// ============================================================

#[test]
fn test_mint_by_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user = Address::generate(&env);

    client.mint(&admins[0], &user, &1000);

    assert_eq!(client.balance(&user), 1000);
    assert_eq!(client.total_supply(), 1000);
}

#[test]
fn test_mint_by_any_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user = Address::generate(&env);

    // Each admin can mint independently
    client.mint(&admins[0], &user, &100);
    client.mint(&admins[2], &user, &200);
    client.mint(&admins[4], &user, &300);

    assert_eq!(client.balance(&user), 600);
    assert_eq!(client.total_supply(), 600);
}

#[test]
#[should_panic(expected = "not an admin")]
fn test_mint_fails_non_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admins) = create_token(&env);
    let user = Address::generate(&env);
    let non_admin = Address::generate(&env);

    client.mint(&non_admin, &user, &1000);
}

#[test]
#[should_panic(expected = "negative amount is not allowed")]
fn test_mint_negative_amount() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user = Address::generate(&env);

    client.mint(&admins[0], &user, &-100);
}

// ============================================================
// Transfer Tests
// ============================================================

#[test]
fn test_transfer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user1 = Address::generate(&env);
    let user2 = Address::generate(&env);

    client.mint(&admins[0], &user1, &1000);
    client.transfer(&user1, &user2, &400);

    assert_eq!(client.balance(&user1), 600);
    assert_eq!(client.balance(&user2), 400);
    assert_eq!(client.total_supply(), 1000); // Total supply unchanged
}

#[test]
#[should_panic(expected = "insufficient balance")]
fn test_transfer_insufficient_balance() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user1 = Address::generate(&env);
    let user2 = Address::generate(&env);

    client.mint(&admins[0], &user1, &100);
    client.transfer(&user1, &user2, &200);
}

// ============================================================
// Burn Tests
// ============================================================

#[test]
fn test_burn() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user = Address::generate(&env);

    client.mint(&admins[0], &user, &1000);
    client.burn(&user, &300);

    assert_eq!(client.balance(&user), 700);
    assert_eq!(client.total_supply(), 700);
}

#[test]
fn test_burn_from_with_allowance() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user = Address::generate(&env);
    let spender = Address::generate(&env);

    client.mint(&admins[0], &user, &1000);
    client.approve(&user, &spender, &500, &10000);
    client.burn_from(&spender, &user, &200);

    assert_eq!(client.balance(&user), 800);
    assert_eq!(client.total_supply(), 800);
    assert_eq!(client.allowance(&user, &spender), 300);
}

#[test]
#[should_panic(expected = "insufficient balance")]
fn test_burn_insufficient_balance() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user = Address::generate(&env);

    client.mint(&admins[0], &user, &100);
    client.burn(&user, &200);
}

// ============================================================
// Allowance Tests
// ============================================================

#[test]
fn test_approve_and_transfer_from() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user = Address::generate(&env);
    let spender = Address::generate(&env);
    let recipient = Address::generate(&env);

    client.mint(&admins[0], &user, &1000);
    client.approve(&user, &spender, &500, &10000);

    assert_eq!(client.allowance(&user, &spender), 500);

    client.transfer_from(&spender, &user, &recipient, &300);

    assert_eq!(client.balance(&user), 700);
    assert_eq!(client.balance(&recipient), 300);
    assert_eq!(client.allowance(&user, &spender), 200);
}

#[test]
#[should_panic(expected = "insufficient allowance")]
fn test_transfer_from_insufficient_allowance() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user = Address::generate(&env);
    let spender = Address::generate(&env);
    let recipient = Address::generate(&env);

    client.mint(&admins[0], &user, &1000);
    client.approve(&user, &spender, &100, &10000);
    client.transfer_from(&spender, &user, &recipient, &200);
}

#[test]
fn test_allowance_zero_balance() {
    let env = Env::default();
    let (client, _admins) = create_token(&env);
    let user = Address::generate(&env);
    let spender = Address::generate(&env);

    // No allowance set, should return 0
    assert_eq!(client.allowance(&user, &spender), 0);
}

// ============================================================
// Pause Tests
// ============================================================

#[test]
fn test_pause_by_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    assert!(!client.is_paused());
    client.pause(&admins[0]);
    assert!(client.is_paused());
}

#[test]
#[should_panic(expected = "contract is paused")]
fn test_transfer_blocked_when_paused() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user1 = Address::generate(&env);
    let user2 = Address::generate(&env);

    client.mint(&admins[0], &user1, &1000);
    client.pause(&admins[0]);
    client.transfer(&user1, &user2, &100);
}

#[test]
#[should_panic(expected = "contract is paused")]
fn test_transfer_from_blocked_when_paused() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user = Address::generate(&env);
    let spender = Address::generate(&env);
    let recipient = Address::generate(&env);

    client.mint(&admins[0], &user, &1000);
    client.approve(&user, &spender, &500, &10000);
    client.pause(&admins[0]);
    client.transfer_from(&spender, &user, &recipient, &100);
}

#[test]
fn test_unpause_requires_multisig() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    client.pause(&admins[0]);
    assert!(client.is_paused());

    // Propose unpause (admin0 auto-approves)
    client.propose_unpause(&admins[0]);

    // Still paused (only 1 of 3)
    assert!(client.is_paused());

    // Second approval (2 of 3)
    client.approve_unpause(&admins[1]);
    assert!(client.is_paused());

    // Third approval (3 of 3 = threshold) -> auto-executes
    client.approve_unpause(&admins[2]);
    assert!(!client.is_paused());
}

#[test]
#[should_panic(expected = "not an admin")]
fn test_pause_fails_non_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admins) = create_token(&env);
    let non_admin = Address::generate(&env);

    client.pause(&non_admin);
}

// ============================================================
// Multi-Sig: Upgrade Proposal Tests
// ============================================================

#[test]
fn test_propose_upgrade() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let fake_hash = soroban_sdk::BytesN::from_array(&env, &[1u8; 32]);
    client.propose_upgrade(&admins[0], &fake_hash);

    let proposal = client.get_upgrade_proposal();
    assert!(proposal.is_some());
    let p = proposal.unwrap();
    assert_eq!(p.proposer, admins[0]);
    assert_eq!(p.approvals.len(), 1);
}

#[test]
#[should_panic(expected = "an upgrade proposal is already active")]
fn test_only_one_upgrade_proposal_at_time() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let hash1 = soroban_sdk::BytesN::from_array(&env, &[1u8; 32]);
    let hash2 = soroban_sdk::BytesN::from_array(&env, &[2u8; 32]);

    client.propose_upgrade(&admins[0], &hash1);
    client.propose_upgrade(&admins[1], &hash2); // Should panic
}

#[test]
#[should_panic(expected = "already approved this proposal")]
fn test_duplicate_upgrade_approval_fails() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let fake_hash = soroban_sdk::BytesN::from_array(&env, &[1u8; 32]);
    client.propose_upgrade(&admins[0], &fake_hash);
    client.approve_upgrade(&admins[0]); // Already approved by proposer
}

#[test]
fn test_cancel_upgrade() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let fake_hash = soroban_sdk::BytesN::from_array(&env, &[1u8; 32]);
    client.propose_upgrade(&admins[0], &fake_hash);
    assert!(client.get_upgrade_proposal().is_some());

    client.cancel_upgrade(&admins[0]);
    assert!(client.get_upgrade_proposal().is_none());
}

#[test]
#[should_panic(expected = "only the proposer can cancel")]
fn test_cancel_upgrade_non_proposer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let fake_hash = soroban_sdk::BytesN::from_array(&env, &[1u8; 32]);
    client.propose_upgrade(&admins[0], &fake_hash);
    client.cancel_upgrade(&admins[1]); // Not the proposer
}

#[test]
#[should_panic(expected = "not an admin")]
fn test_propose_upgrade_non_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admins) = create_token(&env);

    let non_admin = Address::generate(&env);
    let fake_hash = soroban_sdk::BytesN::from_array(&env, &[1u8; 32]);
    client.propose_upgrade(&non_admin, &fake_hash);
}

// ============================================================
// Multi-Sig: Admin Management Tests
// ============================================================

#[test]
fn test_add_admin_multisig() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let new_admin = Address::generate(&env);

    assert_eq!(client.get_admins().len(), 5);

    // Propose (admin0 auto-approves)
    client.propose_add_admin(&admins[0], &new_admin);
    // Approve by admin1 (2/3)
    client.approve_admin_proposal(&admins[1]);
    // Approve by admin2 (3/3 = threshold) -> auto-executes
    client.approve_admin_proposal(&admins[2]);

    let stored_admins = client.get_admins();
    assert_eq!(stored_admins.len(), 6);
    assert!(stored_admins.contains(&new_admin));
}

#[test]
fn test_remove_admin_multisig() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    // We have 5 admins, threshold 3, so we can remove one (5 > 3)
    client.propose_remove_admin(&admins[0], &admins[4]);
    client.approve_admin_proposal(&admins[1]);
    client.approve_admin_proposal(&admins[2]);

    let stored_admins = client.get_admins();
    assert_eq!(stored_admins.len(), 4);
    assert!(!stored_admins.contains(&admins[4]));
}

#[test]
#[should_panic(expected = "cannot remove admin: would go below threshold")]
fn test_cannot_remove_admin_below_threshold() {
    let env = Env::default();
    env.mock_all_auths();

    // Create with exactly 3 admins and threshold 3
    let admins_vec = vec![
        &env,
        Address::generate(&env),
        Address::generate(&env),
        Address::generate(&env),
    ];
    let contract_id = env.register(
        LunarxyToken,
        (
            admins_vec.clone(),
            3u32,
            String::from_str(&env, "LUNARXY"),
            String::from_str(&env, "LUNARXY"),
        ),
    );
    let client = LunarxyTokenClient::new(&env, &contract_id);

    // Try to remove one: 3 admins, threshold 3 -> 3 <= 3, cannot remove
    client.propose_remove_admin(&admins_vec.get(0).unwrap(), &admins_vec.get(2).unwrap());
}

#[test]
#[should_panic(expected = "address is already an admin")]
fn test_add_duplicate_admin_fails() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    client.propose_add_admin(&admins[0], &admins[1]); // admins[1] is already admin
}

#[test]
fn test_cancel_admin_proposal() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let new_admin = Address::generate(&env);

    client.propose_add_admin(&admins[0], &new_admin);
    assert!(client.get_admin_proposal().is_some());

    client.cancel_admin_proposal(&admins[0]);
    assert!(client.get_admin_proposal().is_none());
}

#[test]
#[should_panic(expected = "an admin proposal is already active")]
fn test_only_one_admin_proposal_at_time() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let new1 = Address::generate(&env);
    let new2 = Address::generate(&env);

    client.propose_add_admin(&admins[0], &new1);
    client.propose_add_admin(&admins[1], &new2); // Should panic
}

// ============================================================
// Multi-Sig: Threshold Change Tests
// ============================================================

#[test]
fn test_change_threshold() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    assert_eq!(client.get_threshold(), 3);

    // Propose change to 4 (need current threshold = 3 approvals)
    client.propose_change_threshold(&admins[0], &4);
    client.approve_threshold_proposal(&admins[1]);
    client.approve_threshold_proposal(&admins[2]);

    assert_eq!(client.get_threshold(), 4);
}

#[test]
#[should_panic(expected = "invalid threshold: must be between 1 and admin count")]
fn test_threshold_too_high() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    client.propose_change_threshold(&admins[0], &6); // Only 5 admins
}

#[test]
#[should_panic(expected = "invalid threshold: must be between 1 and admin count")]
fn test_threshold_zero() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    client.propose_change_threshold(&admins[0], &0);
}

#[test]
fn test_new_threshold_applies_to_next_proposals() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    // Change threshold from 3 to 2
    client.propose_change_threshold(&admins[0], &2);
    client.approve_threshold_proposal(&admins[1]);
    client.approve_threshold_proposal(&admins[2]);
    assert_eq!(client.get_threshold(), 2);

    // Now add admin only needs 2 approvals
    let new_admin = Address::generate(&env);
    client.propose_add_admin(&admins[0], &new_admin);
    // Proposer already counts as 1 approval, we need 1 more
    client.approve_admin_proposal(&admins[1]);
    // Should have auto-executed at threshold 2
    assert_eq!(client.get_admins().len(), 6);
}

#[test]
fn test_cancel_threshold_proposal() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    client.propose_change_threshold(&admins[0], &4);
    assert!(client.get_threshold_proposal().is_some());

    client.cancel_threshold_proposal(&admins[0]);
    assert!(client.get_threshold_proposal().is_none());
    assert_eq!(client.get_threshold(), 3); // Unchanged
}

// ============================================================
// Edge Cases and Integration Tests
// ============================================================

#[test]
fn test_decimals_is_zero() {
    let env = Env::default();
    let (client, _admins) = create_token(&env);

    assert_eq!(client.decimals(), 0);
}

#[test]
fn test_zero_amount_transfer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user1 = Address::generate(&env);
    let user2 = Address::generate(&env);

    client.mint(&admins[0], &user1, &100);
    client.transfer(&user1, &user2, &0);

    assert_eq!(client.balance(&user1), 100);
    assert_eq!(client.balance(&user2), 0);
}

#[test]
fn test_mint_burn_supply_tracking() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user = Address::generate(&env);

    client.mint(&admins[0], &user, &1000);
    assert_eq!(client.total_supply(), 1000);

    client.burn(&user, &300);
    assert_eq!(client.total_supply(), 700);

    client.mint(&admins[1], &user, &500);
    assert_eq!(client.total_supply(), 1200);
}

#[test]
fn test_multiple_users_balances() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let users: [Address; 5] = [
        Address::generate(&env),
        Address::generate(&env),
        Address::generate(&env),
        Address::generate(&env),
        Address::generate(&env),
    ];

    for (i, user) in users.iter().enumerate() {
        client.mint(&admins[0], user, &((i as i128 + 1) * 100));
    }

    assert_eq!(client.balance(&users[0]), 100);
    assert_eq!(client.balance(&users[1]), 200);
    assert_eq!(client.balance(&users[2]), 300);
    assert_eq!(client.balance(&users[3]), 400);
    assert_eq!(client.balance(&users[4]), 500);
    assert_eq!(client.total_supply(), 1500);
}

#[test]
fn test_mint_while_paused_still_works() {
    // Mint is NOT blocked by pause - only transfers are
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user = Address::generate(&env);

    client.pause(&admins[0]);
    assert!(client.is_paused());

    // Mint should still work
    client.mint(&admins[0], &user, &500);
    assert_eq!(client.balance(&user), 500);
}

#[test]
fn test_burn_while_paused_still_works() {
    // Burn is NOT blocked by pause - only transfers are
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);
    let user = Address::generate(&env);

    client.mint(&admins[0], &user, &500);
    client.pause(&admins[0]);
    assert!(client.is_paused());

    client.burn(&user, &200);
    assert_eq!(client.balance(&user), 300);
}

#[test]
fn test_version_starts_at_one() {
    let env = Env::default();
    let (client, _admins) = create_token(&env);

    assert_eq!(client.version(), 1);
}

#[test]
fn test_handle_upgrade_by_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    // Should not panic
    client.handle_upgrade(&admins[0]);
}

#[test]
#[should_panic(expected = "not an admin")]
fn test_handle_upgrade_non_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admins) = create_token(&env);
    let non_admin = Address::generate(&env);

    client.handle_upgrade(&non_admin);
}

// ============================================================
// User Mint Tests
// ============================================================

use ed25519_dalek::{Signer, SigningKey};
use rand::rngs::OsRng;
use soroban_sdk::{xdr::ToXdr, Bytes, BytesN};

/// Build the same message the contract hashes and verify with.
/// Layout: amount(16 LE) | price(16 LE) | nonce(8 LE) | uid(8 LE) | contract_xdr
fn build_message(
    env: &Env,
    amount: i128,
    price: i128,
    nonce: u64,
    uid: u64,
    contract_id: &Address,
) -> BytesN<32> {
    let mut msg = Bytes::new(env);
    for b in amount.to_le_bytes() {
        msg.push_back(b);
    }
    for b in price.to_le_bytes() {
        msg.push_back(b);
    }
    for b in nonce.to_le_bytes() {
        msg.push_back(b);
    }
    for b in uid.to_le_bytes() {
        msg.push_back(b);
    }
    let addr_xdr: Bytes = contract_id.to_xdr(env);
    msg.append(&addr_xdr);
    env.crypto().sha256(&msg).into()
}

fn setup_user_mint<'a>(
    env: &'a Env,
) -> (LunarxyTokenClient<'a>, [Address; 5], SigningKey, BytesN<32>) {
    env.mock_all_auths();
    let (client, admins) = create_token(env);
    let signing_key = SigningKey::generate(&mut OsRng);
    let verifying_key: [u8; 32] = signing_key.verifying_key().to_bytes();
    let signer_key = BytesN::from_array(env, &verifying_key);
    client.set_signer_key(&admins[0], &signer_key);
    (client, admins, signing_key, signer_key)
}

#[test]
fn test_user_mint_happy_path() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admins, signing_key, _) = setup_user_mint(&env);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();
    let amount: i128 = 500;
    let price: i128 = 100;
    let nonce: u64 = 0;
    let uid: u64 = 42;

    let msg_hash = build_message(&env, amount, price, nonce, uid, &contract_id);
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    assert_eq!(client.get_nonce(&caller), 0);
    client.user_mint(&caller, &amount, &price, &nonce, &uid, &signature);

    assert_eq!(client.balance(&caller), 500);
    assert_eq!(client.total_supply(), 500);
    assert_eq!(client.get_nonce(&caller), 1);
}

#[test]
fn test_user_mint_nonce_increments() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admins, signing_key, _) = setup_user_mint(&env);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();

    for expected_nonce in 0u64..3u64 {
        let amount: i128 = 100;
        let price: i128 = 10;
        let uid: u64 = 1;
        let msg_hash = build_message(&env, amount, price, expected_nonce, uid, &contract_id);
        let hash_bytes: [u8; 32] = msg_hash.to_array();
        let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
        let signature = BytesN::from_array(&env, &sig_bytes);

        client.user_mint(&caller, &amount, &price, &expected_nonce, &uid, &signature);
        assert_eq!(client.get_nonce(&caller), expected_nonce + 1);
    }

    assert_eq!(client.balance(&caller), 300);
}

#[test]
#[should_panic(expected = "invalid nonce")]
fn test_user_mint_wrong_nonce() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admins, signing_key, _) = setup_user_mint(&env);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();
    let amount: i128 = 100;
    let price: i128 = 10;
    let wrong_nonce: u64 = 5; // expected 0
    let uid: u64 = 1;

    let msg_hash = build_message(&env, amount, price, wrong_nonce, uid, &contract_id);
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    client.user_mint(&caller, &amount, &price, &wrong_nonce, &uid, &signature);
}

#[test]
#[should_panic]
fn test_user_mint_invalid_signature() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admins, _signing_key, _) = setup_user_mint(&env);

    let caller = Address::generate(&env);
    // Use a different key to produce an invalid signature
    let evil_key = SigningKey::generate(&mut OsRng);
    let contract_id = client.address.clone();
    let amount: i128 = 100;
    let price: i128 = 10;
    let nonce: u64 = 0;
    let uid: u64 = 1;

    let msg_hash = build_message(&env, amount, price, nonce, uid, &contract_id);
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = evil_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    client.user_mint(&caller, &amount, &price, &nonce, &uid, &signature);
}

#[test]
#[should_panic]
fn test_user_mint_replay_attack() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admins, signing_key, _) = setup_user_mint(&env);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();
    let amount: i128 = 100;
    let price: i128 = 10;
    let nonce: u64 = 0;
    let uid: u64 = 1;

    let msg_hash = build_message(&env, amount, price, nonce, uid, &contract_id);
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    // First call succeeds
    client.user_mint(&caller, &amount, &price, &nonce, &uid, &signature);
    // Second call with same signature/nonce must fail
    client.user_mint(&caller, &amount, &price, &nonce, &uid, &signature);
}

#[test]
#[should_panic(expected = "signer key not configured")]
fn test_user_mint_no_signer_key() {
    let env = Env::default();
    env.mock_all_auths();
    // Do NOT call set_signer_key
    let (client, _admins) = create_token(&env);

    let caller = Address::generate(&env);
    let signing_key = SigningKey::generate(&mut OsRng);
    let contract_id = client.address.clone();
    let amount: i128 = 100;
    let price: i128 = 10;
    let nonce: u64 = 0;
    let uid: u64 = 1;

    let msg_hash = build_message(&env, amount, price, nonce, uid, &contract_id);
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    client.user_mint(&caller, &amount, &price, &nonce, &uid, &signature);
}

#[test]
#[should_panic(expected = "not an admin")]
fn test_set_signer_key_non_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admins) = create_token(&env);
    let non_admin = Address::generate(&env);
    let signing_key = SigningKey::generate(&mut OsRng);
    let verifying_key: [u8; 32] = signing_key.verifying_key().to_bytes();
    let signer_key = BytesN::from_array(&env, &verifying_key);

    client.set_signer_key(&non_admin, &signer_key);
}

#[test]
fn test_get_signer_key() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins, _signing_key, signer_key) = setup_user_mint(&env);

    assert_eq!(client.get_signer_key(), Some(signer_key));
    let _ = admins; // suppress unused warning
}

#[test]
#[should_panic(expected = "contract is paused")]
fn test_user_mint_blocked_when_paused() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins, signing_key, _) = setup_user_mint(&env);

    client.pause(&admins[0]);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();
    let amount: i128 = 100;
    let price: i128 = 10;
    let nonce: u64 = 0;
    let uid: u64 = 1;

    let msg_hash = build_message(&env, amount, price, nonce, uid, &contract_id);
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    client.user_mint(&caller, &amount, &price, &nonce, &uid, &signature);
}

#[test]
#[should_panic(expected = "negative amount is not allowed")]
fn test_user_mint_negative_amount() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admins, signing_key, _) = setup_user_mint(&env);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();
    let amount: i128 = -1;
    let price: i128 = 10;
    let nonce: u64 = 0;
    let uid: u64 = 1;

    let msg_hash = build_message(&env, amount, price, nonce, uid, &contract_id);
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    client.user_mint(&caller, &amount, &price, &nonce, &uid, &signature);
}

// ============================================================
// User Mint With Token Tests
// ============================================================

/// Build the signed message for user_mint_with_token.
/// Layout: amount(16 LE) | payment_amount(16 LE) | nonce(8 LE) | uid(8 LE)
///         | contract_xdr | payment_token_xdr
fn build_message_with_token(
    env: &Env,
    amount: i128,
    payment_amount: i128,
    nonce: u64,
    uid: u64,
    contract_id: &Address,
    payment_token: &Address,
) -> BytesN<32> {
    let mut msg = Bytes::new(env);
    for b in amount.to_le_bytes() {
        msg.push_back(b);
    }
    for b in payment_amount.to_le_bytes() {
        msg.push_back(b);
    }
    for b in nonce.to_le_bytes() {
        msg.push_back(b);
    }
    for b in uid.to_le_bytes() {
        msg.push_back(b);
    }
    let contract_xdr: Bytes = contract_id.to_xdr(env);
    msg.append(&contract_xdr);
    let payment_token_xdr: Bytes = payment_token.to_xdr(env);
    msg.append(&payment_token_xdr);
    env.crypto().sha256(&msg).into()
}

/// Register a second LunarxyToken to act as the payment token, mint some
/// balance to `holder`, and approve `spender` to pull `allowance` from it.
fn setup_payment_token<'a>(
    env: &'a Env,
    admins: &[Address; 5],
    holder: &Address,
    spender: &Address,
    mint_amount: i128,
    allowance: i128,
) -> LunarxyTokenClient<'a> {
    let admin_vec = vec![
        env,
        admins[0].clone(),
        admins[1].clone(),
        admins[2].clone(),
        admins[3].clone(),
        admins[4].clone(),
    ];
    let payment_contract_id = env.register(
        LunarxyToken,
        (
            admin_vec,
            3u32,
            String::from_str(env, "PAY"),
            String::from_str(env, "PAY"),
        ),
    );
    let pay_client = LunarxyTokenClient::new(env, &payment_contract_id);
    // Mint payment tokens to holder
    pay_client.mint(&admins[0], holder, &mint_amount);
    // Approve spender (the main contract) to pull payment_amount
    let expiration_ledger = env.ledger().sequence() + 10_000;
    pay_client.approve(holder, spender, &allowance, &expiration_ledger);
    pay_client
}

#[test]
fn test_user_mint_with_token_happy_path() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins, signing_key, _) = setup_user_mint(&env);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();
    let amount: i128 = 500;
    let payment_amount: i128 = 100;
    let nonce: u64 = 0;
    let uid: u64 = 7;

    let pay_client = setup_payment_token(
        &env,
        &admins,
        &caller,
        &contract_id,
        payment_amount,
        payment_amount,
    );
    let payment_token = pay_client.address.clone();

    let msg_hash = build_message_with_token(
        &env,
        amount,
        payment_amount,
        nonce,
        uid,
        &contract_id,
        &payment_token,
    );
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    assert_eq!(client.get_nonce(&caller), 0);
    client.user_mint_with_token(
        &caller,
        &amount,
        &payment_token,
        &payment_amount,
        &nonce,
        &uid,
        &signature,
    );

    // LunarXY minted
    assert_eq!(client.balance(&caller), 500);
    assert_eq!(client.total_supply(), 500);
    // Nonce advanced
    assert_eq!(client.get_nonce(&caller), 1);
    // Payment tokens deducted from caller, now held by main contract
    assert_eq!(pay_client.balance(&caller), 0);
    assert_eq!(pay_client.balance(&contract_id), payment_amount);
}

#[test]
#[should_panic(expected = "invalid nonce")]
fn test_user_mint_with_token_wrong_nonce() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins, signing_key, _) = setup_user_mint(&env);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();
    let amount: i128 = 100;
    let payment_amount: i128 = 10;
    let wrong_nonce: u64 = 5;
    let uid: u64 = 1;

    let pay_client = setup_payment_token(
        &env,
        &admins,
        &caller,
        &contract_id,
        payment_amount,
        payment_amount,
    );
    let payment_token = pay_client.address.clone();

    let msg_hash = build_message_with_token(
        &env,
        amount,
        payment_amount,
        wrong_nonce,
        uid,
        &contract_id,
        &payment_token,
    );
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    client.user_mint_with_token(
        &caller,
        &amount,
        &payment_token,
        &payment_amount,
        &wrong_nonce,
        &uid,
        &signature,
    );
}

#[test]
#[should_panic]
fn test_user_mint_with_token_invalid_signature() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins, _signing_key, _) = setup_user_mint(&env);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();
    let amount: i128 = 100;
    let payment_amount: i128 = 10;
    let nonce: u64 = 0;
    let uid: u64 = 1;

    let pay_client = setup_payment_token(
        &env,
        &admins,
        &caller,
        &contract_id,
        payment_amount,
        payment_amount,
    );
    let payment_token = pay_client.address.clone();

    // Sign with a different (evil) key
    let evil_key = SigningKey::generate(&mut OsRng);
    let msg_hash = build_message_with_token(
        &env,
        amount,
        payment_amount,
        nonce,
        uid,
        &contract_id,
        &payment_token,
    );
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = evil_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    client.user_mint_with_token(
        &caller,
        &amount,
        &payment_token,
        &payment_amount,
        &nonce,
        &uid,
        &signature,
    );
}

#[test]
#[should_panic]
fn test_user_mint_with_token_replay_attack() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins, signing_key, _) = setup_user_mint(&env);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();
    let amount: i128 = 100;
    let payment_amount: i128 = 10;
    let nonce: u64 = 0;
    let uid: u64 = 1;

    // Mint enough for two transfers
    let pay_client = setup_payment_token(
        &env,
        &admins,
        &caller,
        &contract_id,
        payment_amount * 2,
        payment_amount * 2,
    );
    let payment_token = pay_client.address.clone();

    let msg_hash = build_message_with_token(
        &env,
        amount,
        payment_amount,
        nonce,
        uid,
        &contract_id,
        &payment_token,
    );
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    // First call succeeds
    client.user_mint_with_token(
        &caller,
        &amount,
        &payment_token,
        &payment_amount,
        &nonce,
        &uid,
        &signature,
    );
    // Replay with same nonce/signature must fail
    client.user_mint_with_token(
        &caller,
        &amount,
        &payment_token,
        &payment_amount,
        &nonce,
        &uid,
        &signature,
    );
}

#[test]
#[should_panic(expected = "contract is paused")]
fn test_user_mint_with_token_blocked_when_paused() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins, signing_key, _) = setup_user_mint(&env);

    client.pause(&admins[0]);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();
    let amount: i128 = 100;
    let payment_amount: i128 = 10;
    let nonce: u64 = 0;
    let uid: u64 = 1;

    let pay_client = setup_payment_token(
        &env,
        &admins,
        &caller,
        &contract_id,
        payment_amount,
        payment_amount,
    );
    let payment_token = pay_client.address.clone();

    let msg_hash = build_message_with_token(
        &env,
        amount,
        payment_amount,
        nonce,
        uid,
        &contract_id,
        &payment_token,
    );
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    client.user_mint_with_token(
        &caller,
        &amount,
        &payment_token,
        &payment_amount,
        &nonce,
        &uid,
        &signature,
    );
}

#[test]
#[should_panic]
fn test_user_mint_with_token_wrong_payment_token_in_sig() {
    // Signature is built with a different payment_token address than what is
    // passed in the call — the contract must reject it.
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins, signing_key, _) = setup_user_mint(&env);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();
    let amount: i128 = 100;
    let payment_amount: i128 = 10;
    let nonce: u64 = 0;
    let uid: u64 = 1;

    // Actual payment token used in the call
    let pay_client = setup_payment_token(
        &env,
        &admins,
        &caller,
        &contract_id,
        payment_amount,
        payment_amount,
    );
    let real_payment_token = pay_client.address.clone();

    // A different (fake) address used when building the signature
    let fake_payment_token = Address::generate(&env);

    let msg_hash = build_message_with_token(
        &env,
        amount,
        payment_amount,
        nonce,
        uid,
        &contract_id,
        &fake_payment_token,
    );
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    client.user_mint_with_token(
        &caller,
        &amount,
        &real_payment_token,
        &payment_amount,
        &nonce,
        &uid,
        &signature,
    );
}

#[test]
#[should_panic]
fn test_user_mint_with_token_wrong_payment_amount_in_sig() {
    // Signature is built with payment_amount=100 but the call passes 1 —
    // the contract must reject it because the amounts don't match the hash.
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins, signing_key, _) = setup_user_mint(&env);

    let caller = Address::generate(&env);
    let contract_id = client.address.clone();
    let amount: i128 = 100;
    let signed_payment_amount: i128 = 100;
    let actual_payment_amount: i128 = 1;
    let nonce: u64 = 0;
    let uid: u64 = 1;

    let pay_client = setup_payment_token(
        &env,
        &admins,
        &caller,
        &contract_id,
        signed_payment_amount,
        signed_payment_amount,
    );
    let payment_token = pay_client.address.clone();

    // Sign with the higher payment_amount
    let msg_hash = build_message_with_token(
        &env,
        amount,
        signed_payment_amount,
        nonce,
        uid,
        &contract_id,
        &payment_token,
    );
    let hash_bytes: [u8; 32] = msg_hash.to_array();
    let sig_bytes = signing_key.sign(&hash_bytes).to_bytes();
    let signature = BytesN::from_array(&env, &sig_bytes);

    // But pass the lower amount in the actual call
    client.user_mint_with_token(
        &caller,
        &amount,
        &payment_token,
        &actual_payment_amount,
        &nonce,
        &uid,
        &signature,
    );
}

// ============================================================
// Freeze Tests
// ============================================================

#[test]
fn test_propose_freeze_and_approve() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Not frozen initially
    assert!(!client.is_frozen(&user));

    // Propose freeze — admin[0] proposes
    client.propose_freeze(&admins[0], &user);
    assert!(client.get_freeze_proposal().is_some());

    // Approve by admin[1]
    client.approve_freeze_proposal(&admins[1]);

    // Approve by admin[2] — meets threshold (3)
    client.approve_freeze_proposal(&admins[2]);

    // Now frozen
    assert!(client.is_frozen(&user));
    assert!(client.get_freeze_proposal().is_none());
}

#[test]
fn test_propose_unfreeze_and_approve() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze the account first
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);
    assert!(client.is_frozen(&user));

    // Propose unfreeze
    client.propose_unfreeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    // Now unfrozen
    assert!(!client.is_frozen(&user));
}

#[test]
fn test_frozen_account_cannot_transfer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    let recipient = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    // Transfer should fail
    let result = client.try_transfer(&user, &recipient, &100);
    assert!(result.is_err());
}

#[test]
fn test_frozen_account_cannot_receive_transfer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let sender = Address::generate(&env);
    let frozen_user = Address::generate(&env);
    client.mint(&admins[0], &sender, &1000);

    // Freeze the recipient
    client.propose_freeze(&admins[0], &frozen_user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    // Transfer to frozen account should fail
    let result = client.try_transfer(&sender, &frozen_user, &100);
    assert!(result.is_err());
}

#[test]
fn test_frozen_account_cannot_burn() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    // Burn should fail
    let result = client.try_burn(&user, &100);
    assert!(result.is_err());
}

#[test]
fn test_frozen_account_cannot_burn_from() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    let spender = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);
    client.approve(&user, &spender, &500, &10000);

    // Freeze the user (token owner)
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    // burn_from should fail
    let result = client.try_burn_from(&spender, &user, &100);
    assert!(result.is_err());
}

#[test]
fn test_frozen_account_cannot_approve() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    let spender = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    // Approve should fail
    let result = client.try_approve(&user, &spender, &500, &10000);
    assert!(result.is_err());
}

#[test]
fn test_frozen_account_can_receive_admin_mint() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    // Admin mint should still work
    client.mint(&admins[0], &user, &500);
    assert_eq!(client.balance(&user), 1500);
}

#[test]
#[should_panic(expected = "account is already frozen")]
fn test_cannot_freeze_already_frozen() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);

    // Freeze
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    // Try to freeze again
    client.propose_freeze(&admins[0], &user);
}

#[test]
#[should_panic(expected = "account is not frozen")]
fn test_cannot_unfreeze_not_frozen() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    client.propose_unfreeze(&admins[0], &user);
}

#[test]
#[should_panic(expected = "cannot freeze an admin address")]
fn test_cannot_freeze_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    client.propose_freeze(&admins[0], &admins[1]);
}

#[test]
fn test_freeze_cancel_by_proposer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    client.propose_freeze(&admins[0], &user);
    assert!(client.get_freeze_proposal().is_some());

    // Cancel
    client.cancel_freeze_proposal(&admins[0]);
    assert!(client.get_freeze_proposal().is_none());
    assert!(!client.is_frozen(&user));
}

#[test]
#[should_panic(expected = "only the proposer can cancel")]
fn test_freeze_cancel_by_non_proposer_fails() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    client.propose_freeze(&admins[0], &user);

    // admin[1] tries to cancel — should fail
    client.cancel_freeze_proposal(&admins[1]);
}

#[test]
#[should_panic(expected = "a freeze proposal is already active")]
fn test_freeze_only_one_proposal_at_a_time() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user1 = Address::generate(&env);
    let user2 = Address::generate(&env);

    client.propose_freeze(&admins[0], &user1);
    // Second proposal should fail
    client.propose_freeze(&admins[1], &user2);
}

// ============================================================
// Seizure Tests
// ============================================================

#[test]
fn test_propose_seizure_and_approve() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    let treasury = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze the account first
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    // Propose seizure
    client.propose_seizure(&admins[0], &user, &treasury, &600);
    assert!(client.get_seizure_proposal().is_some());

    // Approve
    client.approve_seizure(&admins[1]);
    client.approve_seizure(&admins[2]);

    // Executed — balances updated
    assert_eq!(client.balance(&user), 400);
    assert_eq!(client.balance(&treasury), 600);
    assert!(client.get_seizure_proposal().is_none());

    // Total supply unchanged
    assert_eq!(client.total_supply(), 1000);
}

#[test]
#[should_panic(expected = "target account is not frozen")]
fn test_seizure_requires_frozen_target() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    let treasury = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Not frozen — should fail
    client.propose_seizure(&admins[0], &user, &treasury, &500);
}

#[test]
#[should_panic(expected = "seizure amount must be positive")]
fn test_seizure_zero_amount() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    let treasury = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze first
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    client.propose_seizure(&admins[0], &user, &treasury, &0);
}

#[test]
#[should_panic(expected = "seizure amount exceeds target balance")]
fn test_seizure_exceeds_balance() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    let treasury = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    client.propose_seizure(&admins[0], &user, &treasury, &1001);
}

#[test]
#[should_panic(expected = "destination cannot be the frozen account")]
fn test_seizure_destination_cannot_be_target() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    client.propose_seizure(&admins[0], &user, &user, &500);
}

#[test]
fn test_seizure_cancel_by_proposer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    let treasury = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    // Propose seizure and cancel
    client.propose_seizure(&admins[0], &user, &treasury, &500);
    assert!(client.get_seizure_proposal().is_some());

    client.cancel_seizure(&admins[0]);
    assert!(client.get_seizure_proposal().is_none());

    // Balance unchanged
    assert_eq!(client.balance(&user), 1000);
}

#[test]
#[should_panic(expected = "only the proposer can cancel")]
fn test_seizure_cancel_by_non_proposer_fails() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    let treasury = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    client.propose_seizure(&admins[0], &user, &treasury, &500);
    client.cancel_seizure(&admins[1]);
}

#[test]
fn test_frozen_transfer_after_unfreeze_works() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    let recipient = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);
    assert!(client.is_frozen(&user));

    // Cannot transfer while frozen
    let result = client.try_transfer(&user, &recipient, &100);
    assert!(result.is_err());

    // Unfreeze
    client.propose_unfreeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);
    assert!(!client.is_frozen(&user));

    // Transfer works again
    client.transfer(&user, &recipient, &100);
    assert_eq!(client.balance(&user), 900);
    assert_eq!(client.balance(&recipient), 100);
}

#[test]
fn test_seizure_full_balance() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    let treasury = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    // Seize entire balance
    client.propose_seizure(&admins[0], &user, &treasury, &1000);
    client.approve_seizure(&admins[1]);
    client.approve_seizure(&admins[2]);

    assert_eq!(client.balance(&user), 0);
    assert_eq!(client.balance(&treasury), 1000);
    assert_eq!(client.total_supply(), 1000);
}

#[test]
#[should_panic(expected = "already approved this proposal")]
fn test_freeze_double_approval_fails() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    client.propose_freeze(&admins[0], &user);

    // admin[0] already approved during propose — try again
    client.approve_freeze_proposal(&admins[0]);
}

#[test]
#[should_panic(expected = "already approved this proposal")]
fn test_seizure_double_approval_fails() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admins) = create_token(&env);

    let user = Address::generate(&env);
    let treasury = Address::generate(&env);
    client.mint(&admins[0], &user, &1000);

    // Freeze
    client.propose_freeze(&admins[0], &user);
    client.approve_freeze_proposal(&admins[1]);
    client.approve_freeze_proposal(&admins[2]);

    client.propose_seizure(&admins[0], &user, &treasury, &500);
    // admin[0] already approved during propose
    client.approve_seizure(&admins[0]);
}
