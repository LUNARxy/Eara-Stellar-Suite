use soroban_sdk::{Address, Env};

use crate::storage_types::{DataKey, BALANCE_BUMP_AMOUNT, BALANCE_LIFETIME_THRESHOLD};

pub fn read_balance(e: &Env, addr: &Address) -> i128 {
    let key = DataKey::Balance(addr.clone());
    if let Some(balance) = e.storage().persistent().get::<DataKey, i128>(&key) {
        e.storage()
            .persistent()
            .extend_ttl(&key, BALANCE_LIFETIME_THRESHOLD, BALANCE_BUMP_AMOUNT);
        balance
    } else {
        0
    }
}

fn write_balance(e: &Env, addr: &Address, amount: i128) {
    let key = DataKey::Balance(addr.clone());
    e.storage().persistent().set(&key, &amount);
    e.storage()
        .persistent()
        .extend_ttl(&key, BALANCE_LIFETIME_THRESHOLD, BALANCE_BUMP_AMOUNT);
}

pub fn receive_balance(e: &Env, addr: &Address, amount: i128) {
    let balance = read_balance(e, addr);
    write_balance(e, addr, balance + amount);
}

pub fn spend_balance(e: &Env, addr: &Address, amount: i128) {
    let balance = read_balance(e, addr);
    if balance < amount {
        panic!("insufficient balance");
    }
    write_balance(e, addr, balance - amount);
}

// --- Total Supply ---

pub fn read_total_supply(e: &Env) -> i128 {
    e.storage()
        .instance()
        .get(&DataKey::TotalSupply)
        .unwrap_or(0)
}

pub fn increase_total_supply(e: &Env, amount: i128) {
    let supply = read_total_supply(e);
    e.storage()
        .instance()
        .set(&DataKey::TotalSupply, &(supply + amount));
}

pub fn decrease_total_supply(e: &Env, amount: i128) {
    let supply = read_total_supply(e);
    if supply < amount {
        panic!("total supply underflow");
    }
    e.storage()
        .instance()
        .set(&DataKey::TotalSupply, &(supply - amount));
}

// --- Freeze Helpers ---

pub fn read_frozen(e: &Env, addr: &Address) -> bool {
    let key = DataKey::Frozen(addr.clone());
    if let Some(frozen) = e.storage().persistent().get::<DataKey, bool>(&key) {
        e.storage()
            .persistent()
            .extend_ttl(&key, BALANCE_LIFETIME_THRESHOLD, BALANCE_BUMP_AMOUNT);
        frozen
    } else {
        false
    }
}

pub fn write_frozen(e: &Env, addr: &Address, frozen: bool) {
    let key = DataKey::Frozen(addr.clone());
    e.storage().persistent().set(&key, &frozen);
    e.storage()
        .persistent()
        .extend_ttl(&key, BALANCE_LIFETIME_THRESHOLD, BALANCE_BUMP_AMOUNT);
}

pub fn check_not_frozen(e: &Env, addr: &Address) {
    if read_frozen(e, addr) {
        panic!("account is frozen");
    }
}
