use soroban_sdk::{contract, contractimpl, Address, Env, Symbol, Vec};

use crate::event;
use crate::storage_types::{
    ComplianceStatus, CompliantIdError, DataKey, UserComplianceRecord, COMPLIANCE_BUMP_AMOUNT,
    COMPLIANCE_LIFETIME_THRESHOLD, INSTANCE_BUMP_AMOUNT, INSTANCE_LIFETIME_THRESHOLD,
};

#[contract]
pub struct CompliantId;

// --- Internal helpers ---

fn extend_instance_ttl(env: &Env) {
    env.storage()
        .instance()
        .extend_ttl(INSTANCE_LIFETIME_THRESHOLD, INSTANCE_BUMP_AMOUNT);
}

fn extend_compliance_ttl(env: &Env, key: &DataKey) {
    env.storage().persistent().extend_ttl(
        key,
        COMPLIANCE_LIFETIME_THRESHOLD,
        COMPLIANCE_BUMP_AMOUNT,
    );
}

fn require_admin(env: &Env, addr: &Address) -> Result<(), CompliantIdError> {
    let admin: Address = env.storage().instance().get(&DataKey::Admin).unwrap();
    if *addr != admin {
        return Err(CompliantIdError::NotAdmin);
    }
    Ok(())
}

fn read_trusted_issuers(env: &Env) -> Vec<Address> {
    env.storage()
        .instance()
        .get(&DataKey::TrustedIssuers)
        .unwrap_or(Vec::new(env))
}

fn write_trusted_issuers(env: &Env, issuers: &Vec<Address>) {
    env.storage()
        .instance()
        .set(&DataKey::TrustedIssuers, issuers);
}

fn require_trusted_issuer(env: &Env, addr: &Address) -> Result<(), CompliantIdError> {
    let issuers = read_trusted_issuers(env);
    for i in 0..issuers.len() {
        if issuers.get(i).unwrap() == *addr {
            return Ok(());
        }
    }
    Err(CompliantIdError::NotTrustedIssuer)
}

fn read_restricted_countries(env: &Env) -> Vec<Symbol> {
    env.storage()
        .instance()
        .get(&DataKey::RestrictedCountries)
        .unwrap_or(Vec::new(env))
}

fn write_restricted_countries(env: &Env, countries: &Vec<Symbol>) {
    env.storage()
        .instance()
        .set(&DataKey::RestrictedCountries, countries);
}

#[contractimpl]
impl CompliantId {
    // ============================================================
    // Constructor
    // ============================================================

    pub fn __constructor(env: Env, admin: Address) {
        env.storage().instance().set(&DataKey::Admin, &admin);
        let empty_issuers: Vec<Address> = Vec::new(&env);
        write_trusted_issuers(&env, &empty_issuers);
        let empty_countries: Vec<Symbol> = Vec::new(&env);
        write_restricted_countries(&env, &empty_countries);
    }

    // ============================================================
    // Admin — Trusted Issuer Management
    // ============================================================

    /// Add a trusted issuer. Only admin can call this.
    pub fn add_trusted_issuer(
        env: Env,
        admin: Address,
        issuer: Address,
    ) -> Result<(), CompliantIdError> {
        admin.require_auth();
        extend_instance_ttl(&env);
        require_admin(&env, &admin)?;

        let mut issuers = read_trusted_issuers(&env);

        // Check for duplicates
        for i in 0..issuers.len() {
            if issuers.get(i).unwrap() == issuer {
                return Err(CompliantIdError::AlreadyTrustedIssuer);
            }
        }

        issuers.push_back(issuer.clone());
        write_trusted_issuers(&env, &issuers);

        event::trusted_issuer_added(&env, &issuer);
        Ok(())
    }

    /// Remove a trusted issuer. Only admin can call this.
    pub fn remove_trusted_issuer(
        env: Env,
        admin: Address,
        issuer: Address,
    ) -> Result<(), CompliantIdError> {
        admin.require_auth();
        extend_instance_ttl(&env);
        require_admin(&env, &admin)?;

        let issuers = read_trusted_issuers(&env);
        let mut found = false;
        let mut new_issuers: Vec<Address> = Vec::new(&env);

        for i in 0..issuers.len() {
            let existing = issuers.get(i).unwrap();
            if existing == issuer {
                found = true;
            } else {
                new_issuers.push_back(existing);
            }
        }

        if !found {
            return Err(CompliantIdError::IssuerNotFound);
        }

        write_trusted_issuers(&env, &new_issuers);

        event::trusted_issuer_removed(&env, &issuer);
        Ok(())
    }

    /// Check if an address is a trusted issuer.
    pub fn is_trusted_issuer(env: Env, issuer: Address) -> bool {
        extend_instance_ttl(&env);
        require_trusted_issuer(&env, &issuer).is_ok()
    }

    // ============================================================
    // Trusted Issuer — Compliance Record Management
    // ============================================================

    /// Set or update a user's compliance record. Only trusted issuers can call.
    pub fn set_compliance(
        env: Env,
        issuer: Address,
        user: Address,
        status: ComplianceStatus,
        level: u32,
        expires_at: u64,
        country_code: Symbol,
    ) -> Result<(), CompliantIdError> {
        issuer.require_auth();
        extend_instance_ttl(&env);
        require_trusted_issuer(&env, &issuer)?;

        if level == 0 {
            return Err(CompliantIdError::InvalidLevel);
        }
        if expires_at <= env.ledger().timestamp() {
            return Err(CompliantIdError::InvalidExpiration);
        }

        let record = UserComplianceRecord {
            status: status.clone(),
            level,
            expires_at,
            country_code,
            issuer: issuer.clone(),
        };

        let key = DataKey::Compliance(user.clone());
        env.storage().persistent().set(&key, &record);
        extend_compliance_ttl(&env, &key);

        event::compliance_updated(&env, &user, &issuer, status, level);
        Ok(())
    }

    /// Suspend a user. Shortcut for issuers — preserves existing level/expiry/country.
    pub fn suspend_user(env: Env, issuer: Address, user: Address) -> Result<(), CompliantIdError> {
        issuer.require_auth();
        extend_instance_ttl(&env);
        require_trusted_issuer(&env, &issuer)?;

        let key = DataKey::Compliance(user.clone());
        let mut record: UserComplianceRecord = env
            .storage()
            .persistent()
            .get(&key)
            .ok_or(CompliantIdError::UserNotFound)?;

        record.status = ComplianceStatus::Suspended;
        record.issuer = issuer.clone();

        env.storage().persistent().set(&key, &record);
        extend_compliance_ttl(&env, &key);

        event::compliance_updated(
            &env,
            &user,
            &issuer,
            ComplianceStatus::Suspended,
            record.level,
        );
        Ok(())
    }

    /// Revoke a user. Shortcut for issuers — preserves existing level/expiry/country.
    pub fn revoke_user(env: Env, issuer: Address, user: Address) -> Result<(), CompliantIdError> {
        issuer.require_auth();
        extend_instance_ttl(&env);
        require_trusted_issuer(&env, &issuer)?;

        let key = DataKey::Compliance(user.clone());
        let mut record: UserComplianceRecord = env
            .storage()
            .persistent()
            .get(&key)
            .ok_or(CompliantIdError::UserNotFound)?;

        record.status = ComplianceStatus::Revoked;
        record.issuer = issuer.clone();

        env.storage().persistent().set(&key, &record);
        extend_compliance_ttl(&env, &key);

        event::compliance_updated(
            &env,
            &user,
            &issuer,
            ComplianceStatus::Revoked,
            record.level,
        );
        Ok(())
    }

    // ============================================================
    // Query Functions
    // ============================================================

    /// Get the full compliance record for a user.
    pub fn get_compliance(
        env: Env,
        user: Address,
    ) -> Result<UserComplianceRecord, CompliantIdError> {
        extend_instance_ttl(&env);
        let key = DataKey::Compliance(user);
        let record: UserComplianceRecord = env
            .storage()
            .persistent()
            .get(&key)
            .ok_or(CompliantIdError::UserNotFound)?;
        extend_compliance_ttl(&env, &key);
        Ok(record)
    }

    /// Check if a user is compliant: status == Verified, level >= min_level, not expired.
    pub fn is_compliant(env: Env, user: Address, min_level: u32) -> bool {
        extend_instance_ttl(&env);
        let key = DataKey::Compliance(user);
        if let Some(record) = env
            .storage()
            .persistent()
            .get::<DataKey, UserComplianceRecord>(&key)
        {
            extend_compliance_ttl(&env, &key);
            let current_time = env.ledger().timestamp();
            record.status == ComplianceStatus::Verified
                && record.level >= min_level
                && record.expires_at > current_time
        } else {
            false
        }
    }

    /// Combined check: is_compliant AND the user's country is not restricted.
    pub fn check_compliance_with_country(env: Env, user: Address, min_level: u32) -> bool {
        extend_instance_ttl(&env);
        let key = DataKey::Compliance(user);
        if let Some(record) = env
            .storage()
            .persistent()
            .get::<DataKey, UserComplianceRecord>(&key)
        {
            extend_compliance_ttl(&env, &key);
            let current_time = env.ledger().timestamp();
            if record.status != ComplianceStatus::Verified
                || record.level < min_level
                || record.expires_at <= current_time
            {
                return false;
            }
            // Check country restriction
            let countries = read_restricted_countries(&env);
            for i in 0..countries.len() {
                if countries.get(i).unwrap() == record.country_code {
                    return false;
                }
            }
            true
        } else {
            false
        }
    }

    // ============================================================
    // Admin — Country Restriction Management
    // ============================================================

    /// Add a restricted country code. Only admin can call this.
    pub fn add_restricted_country(
        env: Env,
        admin: Address,
        country_code: Symbol,
    ) -> Result<(), CompliantIdError> {
        admin.require_auth();
        extend_instance_ttl(&env);
        require_admin(&env, &admin)?;

        let mut countries = read_restricted_countries(&env);

        // Check for duplicates
        for i in 0..countries.len() {
            if countries.get(i).unwrap() == country_code {
                return Err(CompliantIdError::CountryAlreadyRestricted);
            }
        }

        countries.push_back(country_code.clone());
        write_restricted_countries(&env, &countries);

        event::country_restricted(&env, &country_code);
        Ok(())
    }

    /// Remove a restricted country code. Only admin can call this.
    pub fn remove_restricted_country(
        env: Env,
        admin: Address,
        country_code: Symbol,
    ) -> Result<(), CompliantIdError> {
        admin.require_auth();
        extend_instance_ttl(&env);
        require_admin(&env, &admin)?;

        let countries = read_restricted_countries(&env);
        let mut found = false;
        let mut new_countries: Vec<Symbol> = Vec::new(&env);

        for i in 0..countries.len() {
            let existing = countries.get(i).unwrap();
            if existing == country_code {
                found = true;
            } else {
                new_countries.push_back(existing);
            }
        }

        if !found {
            return Err(CompliantIdError::CountryNotRestricted);
        }

        write_restricted_countries(&env, &new_countries);

        event::country_unrestricted(&env, &country_code);
        Ok(())
    }

    /// Check if a country code is restricted.
    pub fn is_country_restricted(env: Env, country_code: Symbol) -> bool {
        extend_instance_ttl(&env);
        let countries = read_restricted_countries(&env);
        for i in 0..countries.len() {
            if countries.get(i).unwrap() == country_code {
                return true;
            }
        }
        false
    }

    // ============================================================
    // Admin View
    // ============================================================

    /// Get the admin address.
    pub fn get_admin(env: Env) -> Address {
        env.storage().instance().get(&DataKey::Admin).unwrap()
    }

    /// Get all trusted issuers.
    pub fn get_trusted_issuers(env: Env) -> Vec<Address> {
        extend_instance_ttl(&env);
        read_trusted_issuers(&env)
    }

    /// Get all restricted country codes.
    pub fn get_restricted_countries(env: Env) -> Vec<Symbol> {
        extend_instance_ttl(&env);
        read_restricted_countries(&env)
    }
}
