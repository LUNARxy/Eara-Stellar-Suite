use soroban_sdk::{contractevent, Address, Env, Symbol};

use crate::storage_types::ComplianceStatus;

// --- Compliance Events ---

#[contractevent]
pub struct ComplianceUpdated {
    #[topic]
    pub user: Address,
    #[topic]
    pub issuer: Address,
    pub status: ComplianceStatus,
    pub level: u32,
}

// --- Trusted Issuer Events ---

#[contractevent(data_format = "single-value")]
pub struct TrustedIssuerAdded {
    #[topic]
    pub issuer: Address,
}

#[contractevent(data_format = "single-value")]
pub struct TrustedIssuerRemoved {
    #[topic]
    pub issuer: Address,
}

// --- Country Restriction Events ---

#[contractevent(data_format = "single-value")]
pub struct CountryRestricted {
    #[topic]
    pub country_code: Symbol,
}

#[contractevent(data_format = "single-value")]
pub struct CountryUnrestricted {
    #[topic]
    pub country_code: Symbol,
}

// --- Helper publish functions ---

pub fn compliance_updated(
    e: &Env,
    user: &Address,
    issuer: &Address,
    status: ComplianceStatus,
    level: u32,
) {
    ComplianceUpdated {
        user: user.clone(),
        issuer: issuer.clone(),
        status,
        level,
    }
    .publish(e);
}

pub fn trusted_issuer_added(e: &Env, issuer: &Address) {
    TrustedIssuerAdded {
        issuer: issuer.clone(),
    }
    .publish(e);
}

pub fn trusted_issuer_removed(e: &Env, issuer: &Address) {
    TrustedIssuerRemoved {
        issuer: issuer.clone(),
    }
    .publish(e);
}

pub fn country_restricted(e: &Env, country_code: &Symbol) {
    CountryRestricted {
        country_code: country_code.clone(),
    }
    .publish(e);
}

pub fn country_unrestricted(e: &Env, country_code: &Symbol) {
    CountryUnrestricted {
        country_code: country_code.clone(),
    }
    .publish(e);
}
