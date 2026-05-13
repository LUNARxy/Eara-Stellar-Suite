#![cfg(test)]

use super::*;
use contract::CompliantIdClient;
use soroban_sdk::{
    testutils::{Address as _, Ledger as _},
    Address, Env, Symbol,
};
use storage_types::{ComplianceStatus, CompliantIdError};

// ============================================================
// Test Helpers
// ============================================================

fn create_contract<'a>(env: &'a Env) -> (CompliantIdClient<'a>, Address) {
    let admin = Address::generate(env);
    let contract_id = env.register(CompliantId, (&admin,));
    let client = CompliantIdClient::new(env, &contract_id);
    (client, admin)
}

fn setup_with_issuer<'a>(env: &'a Env) -> (CompliantIdClient<'a>, Address, Address) {
    let (client, admin) = create_contract(env);
    let issuer = Address::generate(env);
    client.add_trusted_issuer(&admin, &issuer);
    (client, admin, issuer)
}

const FUTURE_TIMESTAMP: u64 = 1_000_000_000;
const PAST_TIMESTAMP: u64 = 100;

fn default_country(env: &Env) -> Symbol {
    Symbol::new(env, "US")
}

// ============================================================
// Constructor Tests
// ============================================================

#[test]
fn test_constructor() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_contract(&env);

    assert_eq!(client.get_admin(), admin);
}

// ============================================================
// Trusted Issuer Management Tests
// ============================================================

#[test]
fn test_add_trusted_issuer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_contract(&env);
    let issuer = Address::generate(&env);

    client.add_trusted_issuer(&admin, &issuer);
    assert!(client.is_trusted_issuer(&issuer));
}

#[test]
fn test_add_trusted_issuer_duplicate() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_contract(&env);
    let issuer = Address::generate(&env);

    client.add_trusted_issuer(&admin, &issuer);
    let result = client.try_add_trusted_issuer(&admin, &issuer);
    assert_eq!(result, Err(Ok(CompliantIdError::AlreadyTrustedIssuer)));
}

#[test]
fn test_add_trusted_issuer_not_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin) = create_contract(&env);
    let not_admin = Address::generate(&env);
    let issuer = Address::generate(&env);

    let result = client.try_add_trusted_issuer(&not_admin, &issuer);
    assert_eq!(result, Err(Ok(CompliantIdError::NotAdmin)));
}

#[test]
fn test_remove_trusted_issuer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin, issuer) = setup_with_issuer(&env);

    assert!(client.is_trusted_issuer(&issuer));
    client.remove_trusted_issuer(&admin, &issuer);
    assert!(!client.is_trusted_issuer(&issuer));
}

#[test]
fn test_remove_trusted_issuer_not_found() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_contract(&env);
    let issuer = Address::generate(&env);

    let result = client.try_remove_trusted_issuer(&admin, &issuer);
    assert_eq!(result, Err(Ok(CompliantIdError::IssuerNotFound)));
}

#[test]
fn test_is_trusted_issuer_false() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin) = create_contract(&env);
    let random = Address::generate(&env);

    assert!(!client.is_trusted_issuer(&random));
}

// ============================================================
// Compliance Record Tests
// ============================================================

#[test]
fn test_set_compliance() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &2u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );

    let record = client.get_compliance(&user);
    assert_eq!(record.status, ComplianceStatus::Verified);
    assert_eq!(record.level, 2);
    assert_eq!(record.expires_at, FUTURE_TIMESTAMP);
    assert_eq!(record.country_code, default_country(&env));
    assert_eq!(record.issuer, issuer);
}

#[test]
fn test_set_compliance_not_trusted_issuer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin) = create_contract(&env);
    let not_issuer = Address::generate(&env);
    let user = Address::generate(&env);

    let result = client.try_set_compliance(
        &not_issuer,
        &user,
        &ComplianceStatus::Verified,
        &1u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );
    assert_eq!(result, Err(Ok(CompliantIdError::NotTrustedIssuer)));
}

#[test]
fn test_set_compliance_invalid_level() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    let result = client.try_set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &0u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );
    assert_eq!(result, Err(Ok(CompliantIdError::InvalidLevel)));
}

#[test]
fn test_set_compliance_invalid_expiration() {
    let env = Env::default();
    env.mock_all_auths();
    // Set ledger timestamp so PAST_TIMESTAMP is in the past
    env.ledger().set_timestamp(1000);
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    let result = client.try_set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &1u32,
        &PAST_TIMESTAMP,
        &default_country(&env),
    );
    assert_eq!(result, Err(Ok(CompliantIdError::InvalidExpiration)));
}

#[test]
fn test_set_compliance_update_existing() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    // Initial record
    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &1u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );

    // Update to level 3
    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &3u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );

    let record = client.get_compliance(&user);
    assert_eq!(record.level, 3);
}

// ============================================================
// Suspend / Revoke Tests
// ============================================================

#[test]
fn test_suspend_user() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &2u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );

    client.suspend_user(&issuer, &user);

    let record = client.get_compliance(&user);
    assert_eq!(record.status, ComplianceStatus::Suspended);
    // Level, expiry, and country should be preserved
    assert_eq!(record.level, 2);
    assert_eq!(record.expires_at, FUTURE_TIMESTAMP);
    assert_eq!(record.country_code, default_country(&env));
}

#[test]
fn test_suspend_user_not_found() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    let result = client.try_suspend_user(&issuer, &user);
    assert_eq!(result, Err(Ok(CompliantIdError::UserNotFound)));
}

#[test]
fn test_suspend_user_not_trusted_issuer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);
    let not_issuer = Address::generate(&env);

    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &1u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );

    let result = client.try_suspend_user(&not_issuer, &user);
    assert_eq!(result, Err(Ok(CompliantIdError::NotTrustedIssuer)));
}

#[test]
fn test_revoke_user() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &2u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );

    client.revoke_user(&issuer, &user);

    let record = client.get_compliance(&user);
    assert_eq!(record.status, ComplianceStatus::Revoked);
    assert_eq!(record.level, 2);
}

#[test]
fn test_revoke_user_not_found() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    let result = client.try_revoke_user(&issuer, &user);
    assert_eq!(result, Err(Ok(CompliantIdError::UserNotFound)));
}

// ============================================================
// is_compliant Tests
// ============================================================

#[test]
fn test_is_compliant_verified() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &2u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );

    assert!(client.is_compliant(&user, &1u32));
    assert!(client.is_compliant(&user, &2u32));
    assert!(!client.is_compliant(&user, &3u32)); // Level too high
}

#[test]
fn test_is_compliant_not_verified() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Suspended,
        &2u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );

    assert!(!client.is_compliant(&user, &1u32));
}

#[test]
fn test_is_compliant_no_record() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin) = create_contract(&env);
    let user = Address::generate(&env);

    assert!(!client.is_compliant(&user, &1u32));
}

#[test]
fn test_is_compliant_expired() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    // Set compliance with a timestamp that will be in the past once we advance the ledger
    let near_future: u64 = 500;
    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &1u32,
        &near_future,
        &default_country(&env),
    );

    // Advance the ledger timestamp past expiration
    env.ledger().set_timestamp(1000);

    assert!(!client.is_compliant(&user, &1u32));
}

// ============================================================
// get_compliance Tests
// ============================================================

#[test]
fn test_get_compliance_not_found() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin) = create_contract(&env);
    let user = Address::generate(&env);

    let result = client.try_get_compliance(&user);
    assert_eq!(result, Err(Ok(CompliantIdError::UserNotFound)));
}

// ============================================================
// Country Restriction Tests
// ============================================================

#[test]
fn test_add_restricted_country() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_contract(&env);
    let country = Symbol::new(&env, "KP");

    client.add_restricted_country(&admin, &country);
    assert!(client.is_country_restricted(&country));
}

#[test]
fn test_add_restricted_country_duplicate() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_contract(&env);
    let country = Symbol::new(&env, "KP");

    client.add_restricted_country(&admin, &country);
    let result = client.try_add_restricted_country(&admin, &country);
    assert_eq!(result, Err(Ok(CompliantIdError::CountryAlreadyRestricted)));
}

#[test]
fn test_add_restricted_country_not_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin) = create_contract(&env);
    let not_admin = Address::generate(&env);
    let country = Symbol::new(&env, "KP");

    let result = client.try_add_restricted_country(&not_admin, &country);
    assert_eq!(result, Err(Ok(CompliantIdError::NotAdmin)));
}

#[test]
fn test_remove_restricted_country() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_contract(&env);
    let country = Symbol::new(&env, "KP");

    client.add_restricted_country(&admin, &country);
    assert!(client.is_country_restricted(&country));

    client.remove_restricted_country(&admin, &country);
    assert!(!client.is_country_restricted(&country));
}

#[test]
fn test_remove_restricted_country_not_found() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_contract(&env);
    let country = Symbol::new(&env, "KP");

    let result = client.try_remove_restricted_country(&admin, &country);
    assert_eq!(result, Err(Ok(CompliantIdError::CountryNotRestricted)));
}

#[test]
fn test_is_country_restricted_false() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin) = create_contract(&env);
    let country = Symbol::new(&env, "US");

    assert!(!client.is_country_restricted(&country));
}

// ============================================================
// check_compliance_with_country Tests
// ============================================================

#[test]
fn test_check_compliance_with_country_pass() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &2u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );

    // US is not restricted
    assert!(client.check_compliance_with_country(&user, &1u32));
}

#[test]
fn test_check_compliance_with_country_restricted() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);
    let country = Symbol::new(&env, "KP");

    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &2u32,
        &FUTURE_TIMESTAMP,
        &country,
    );

    // Restrict KP
    client.add_restricted_country(&admin, &country);

    // Should fail even though user is verified
    assert!(!client.check_compliance_with_country(&user, &1u32));
}

#[test]
fn test_check_compliance_with_country_not_compliant() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Suspended,
        &2u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );

    assert!(!client.check_compliance_with_country(&user, &1u32));
}

#[test]
fn test_check_compliance_with_country_no_record() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin) = create_contract(&env);
    let user = Address::generate(&env);

    assert!(!client.check_compliance_with_country(&user, &1u32));
}

#[test]
fn test_check_compliance_with_country_expired() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    let near_future: u64 = 500;
    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &1u32,
        &near_future,
        &default_country(&env),
    );

    env.ledger().set_timestamp(1000);

    assert!(!client.check_compliance_with_country(&user, &1u32));
}

// ============================================================
// Multiple Issuers Test
// ============================================================

#[test]
fn test_multiple_issuers() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_contract(&env);
    let issuer_a = Address::generate(&env);
    let issuer_b = Address::generate(&env);

    client.add_trusted_issuer(&admin, &issuer_a);
    client.add_trusted_issuer(&admin, &issuer_b);

    assert!(client.is_trusted_issuer(&issuer_a));
    assert!(client.is_trusted_issuer(&issuer_b));

    let user = Address::generate(&env);

    // Issuer A sets compliance
    client.set_compliance(
        &issuer_a,
        &user,
        &ComplianceStatus::Verified,
        &1u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );

    let record = client.get_compliance(&user);
    assert_eq!(record.issuer, issuer_a);

    // Issuer B updates compliance
    client.set_compliance(
        &issuer_b,
        &user,
        &ComplianceStatus::Verified,
        &3u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );

    let record = client.get_compliance(&user);
    assert_eq!(record.issuer, issuer_b);
    assert_eq!(record.level, 3);
}

// ============================================================
// Full Lifecycle Test
// ============================================================

#[test]
fn test_full_lifecycle() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin, issuer) = setup_with_issuer(&env);
    let user = Address::generate(&env);

    // 1. User starts with no record
    assert!(!client.is_compliant(&user, &1u32));

    // 2. Issuer verifies user at level 2
    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &2u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );
    assert!(client.is_compliant(&user, &1u32));
    assert!(client.is_compliant(&user, &2u32));
    assert!(client.check_compliance_with_country(&user, &1u32));

    // 3. Admin restricts the user's country
    client.add_restricted_country(&admin, &default_country(&env));
    assert!(client.is_compliant(&user, &1u32)); // Still compliant individually
    assert!(!client.check_compliance_with_country(&user, &1u32)); // Fails combined check

    // 4. Admin lifts restriction
    client.remove_restricted_country(&admin, &default_country(&env));
    assert!(client.check_compliance_with_country(&user, &1u32)); // Passes again

    // 5. Issuer suspends user
    client.suspend_user(&issuer, &user);
    assert!(!client.is_compliant(&user, &1u32));

    // 6. Issuer re-verifies user
    client.set_compliance(
        &issuer,
        &user,
        &ComplianceStatus::Verified,
        &2u32,
        &FUTURE_TIMESTAMP,
        &default_country(&env),
    );
    assert!(client.is_compliant(&user, &1u32));

    // 7. Issuer revokes user
    client.revoke_user(&issuer, &user);
    assert!(!client.is_compliant(&user, &1u32));
    let record = client.get_compliance(&user);
    assert_eq!(record.status, ComplianceStatus::Revoked);
}

// ============================================================
// View Function Tests
// ============================================================

#[test]
fn test_get_trusted_issuers_empty() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin) = create_contract(&env);

    let issuers = client.get_trusted_issuers();
    assert_eq!(issuers.len(), 0);
}

#[test]
fn test_get_trusted_issuers() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_contract(&env);
    let issuer_a = Address::generate(&env);
    let issuer_b = Address::generate(&env);

    client.add_trusted_issuer(&admin, &issuer_a);
    client.add_trusted_issuer(&admin, &issuer_b);

    let issuers = client.get_trusted_issuers();
    assert_eq!(issuers.len(), 2);
    assert_eq!(issuers.get(0).unwrap(), issuer_a);
    assert_eq!(issuers.get(1).unwrap(), issuer_b);
}

#[test]
fn test_get_restricted_countries_empty() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, _admin) = create_contract(&env);

    let countries = client.get_restricted_countries();
    assert_eq!(countries.len(), 0);
}

#[test]
fn test_get_restricted_countries() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, admin) = create_contract(&env);
    let kp = Symbol::new(&env, "KP");
    let ir = Symbol::new(&env, "IR");

    client.add_restricted_country(&admin, &kp);
    client.add_restricted_country(&admin, &ir);

    let countries = client.get_restricted_countries();
    assert_eq!(countries.len(), 2);
    assert_eq!(countries.get(0).unwrap(), kp);
    assert_eq!(countries.get(1).unwrap(), ir);
}
