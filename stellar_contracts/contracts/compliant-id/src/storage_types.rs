use soroban_sdk::{contracterror, contracttype, Address, Symbol};

// --- TTL Constants ---

/// Threshold for instance storage TTL extension (approx 30 days).
pub const INSTANCE_LIFETIME_THRESHOLD: u32 = 518_400;
/// Bump amount for instance storage TTL (approx 60 days).
pub const INSTANCE_BUMP_AMOUNT: u32 = 1_036_800;

/// Threshold for compliance record (persistent) storage TTL extension.
pub const COMPLIANCE_LIFETIME_THRESHOLD: u32 = 518_400;
/// Bump amount for compliance record (persistent) storage TTL.
pub const COMPLIANCE_BUMP_AMOUNT: u32 = 1_036_800;

// --- Errors ---

#[contracterror]
#[derive(Copy, Clone, Debug, Eq, PartialEq)]
#[repr(u32)]
pub enum CompliantIdError {
    NotAdmin = 1,
    NotTrustedIssuer = 2,
    UserNotFound = 3,
    InvalidLevel = 4,
    InvalidExpiration = 5,
    RestrictedCountry = 6,
    AlreadyTrustedIssuer = 7,
    IssuerNotFound = 8,
    CountryAlreadyRestricted = 9,
    CountryNotRestricted = 10,
}

// --- Compliance Types ---

#[derive(Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub enum ComplianceStatus {
    Unverified,
    Verified,
    Suspended,
    Revoked,
}

#[derive(Clone, Debug, Eq, PartialEq)]
#[contracttype]
pub struct UserComplianceRecord {
    pub status: ComplianceStatus,
    pub level: u32,
    pub expires_at: u64,
    pub country_code: Symbol,
    pub issuer: Address,
}

// --- Storage Keys ---

#[derive(Clone)]
#[contracttype]
pub enum DataKey {
    Admin,
    TrustedIssuers,
    Compliance(Address),
    RestrictedCountries,
}
