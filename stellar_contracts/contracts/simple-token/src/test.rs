#![cfg(test)]

use super::*;
use crate::contract::SimpleTokenClient;
use soroban_sdk::{testutils::Address as _, Address, Env, String};

fn create_token<'a>(env: &'a Env) -> (SimpleTokenClient<'a>, Address) {
    let admin = Address::generate(env);
    let contract_id = env.register(
        SimpleToken,
        (
            admin.clone(),
            String::from_str(env, "Test USD"),
            String::from_str(env, "TUSD"),
        ),
    );
    let client = SimpleTokenClient::new(env, &contract_id);
    (client, admin)
}

// ============================================================
// Constructor Tests
// ============================================================

#[test]
fn test_initialize() {
    let env = Env::default();
    let (client, _admin) = create_token(&env);

    assert_eq!(client.name(), String::from_str(&env, "Test USD"));
    assert_eq!(client.symbol(), String::from_str(&env, "TUSD"));
    assert_eq!(client.decimals(), 7);
    assert_eq!(client.total_supply(), 0);
}

// ============================================================
// Mint Tests
// ============================================================

#[test]
fn test_mint() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_token(&env);
    let user = Address::generate(&env);

    client.mint(&admin, &user, &1_000_000_000i128);

    assert_eq!(client.balance(&user), 1_000_000_000);
    assert_eq!(client.total_supply(), 1_000_000_000);
}

#[test]
#[should_panic(expected = "not authorized")]
fn test_mint_non_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin) = create_token(&env);
    let non_admin = Address::generate(&env);
    let user = Address::generate(&env);

    client.mint(&non_admin, &user, &1_000i128);
}

#[test]
#[should_panic(expected = "negative amount is not allowed")]
fn test_mint_negative_amount() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_token(&env);
    let user = Address::generate(&env);

    client.mint(&admin, &user, &-1i128);
}

// ============================================================
// Transfer Tests
// ============================================================

#[test]
fn test_transfer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_token(&env);
    let user1 = Address::generate(&env);
    let user2 = Address::generate(&env);

    client.mint(&admin, &user1, &1_000i128);
    client.transfer(&user1, &user2, &400i128);

    assert_eq!(client.balance(&user1), 600);
    assert_eq!(client.balance(&user2), 400);
    assert_eq!(client.total_supply(), 1_000); // unchanged
}

#[test]
#[should_panic(expected = "insufficient balance")]
fn test_transfer_insufficient_balance() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_token(&env);
    let user1 = Address::generate(&env);
    let user2 = Address::generate(&env);

    client.mint(&admin, &user1, &100i128);
    client.transfer(&user1, &user2, &200i128);
}

// ============================================================
// Allowance Tests
// ============================================================

#[test]
fn test_approve_and_transfer_from() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_token(&env);
    let user = Address::generate(&env);
    let spender = Address::generate(&env);
    let recipient = Address::generate(&env);

    client.mint(&admin, &user, &1_000i128);
    let expiration = env.ledger().sequence() + 10_000;
    client.approve(&user, &spender, &500i128, &expiration);

    assert_eq!(client.allowance(&user, &spender), 500);

    client.transfer_from(&spender, &user, &recipient, &300i128);

    assert_eq!(client.balance(&user), 700);
    assert_eq!(client.balance(&recipient), 300);
    assert_eq!(client.allowance(&user, &spender), 200);
}

#[test]
#[should_panic(expected = "insufficient allowance")]
fn test_transfer_from_insufficient_allowance() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_token(&env);
    let user = Address::generate(&env);
    let spender = Address::generate(&env);
    let recipient = Address::generate(&env);

    client.mint(&admin, &user, &1_000i128);
    let expiration = env.ledger().sequence() + 10_000;
    client.approve(&user, &spender, &100i128, &expiration);
    client.transfer_from(&spender, &user, &recipient, &200i128);
}

#[test]
fn test_allowance_expired() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_token(&env);
    let user = Address::generate(&env);
    let spender = Address::generate(&env);

    client.mint(&admin, &user, &1_000i128);

    // Set allowance that expires at current ledger (already expired)
    let expiration = env.ledger().sequence(); // expires immediately
    client.approve(&user, &spender, &500i128, &expiration);

    // Should read as 0 since it's expired
    assert_eq!(client.allowance(&user, &spender), 0);
}

#[test]
fn test_allowance_zero_if_not_set() {
    let env = Env::default();
    let (client, _admin) = create_token(&env);
    let user = Address::generate(&env);
    let spender = Address::generate(&env);

    assert_eq!(client.allowance(&user, &spender), 0);
}
