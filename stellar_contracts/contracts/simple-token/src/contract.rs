use soroban_sdk::{contract, contractimpl, contracttype, Address, Env, String};

// ---------------------------------------------------------------------------
// TTL constants (approx 30-day threshold / 60-day bump)
// ---------------------------------------------------------------------------
const INSTANCE_LIFETIME_THRESHOLD: u32 = 518_400;
const INSTANCE_BUMP_AMOUNT: u32 = 1_036_800;
const BALANCE_LIFETIME_THRESHOLD: u32 = 518_400;
const BALANCE_BUMP_AMOUNT: u32 = 1_036_800;

// ---------------------------------------------------------------------------
// Storage keys
// ---------------------------------------------------------------------------
#[derive(Clone)]
#[contracttype]
pub enum DataKey {
    Admin,
    Name,
    Symbol,
    TotalSupply,
    Balance(Address),
    Allowance(AllowanceKey),
}

#[derive(Clone)]
#[contracttype]
pub struct AllowanceKey {
    pub from: Address,
    pub spender: Address,
}

#[derive(Clone)]
#[contracttype]
pub struct AllowanceValue {
    pub amount: i128,
    pub expiration_ledger: u32,
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
fn extend_instance_ttl(env: &Env) {
    env.storage()
        .instance()
        .extend_ttl(INSTANCE_LIFETIME_THRESHOLD, INSTANCE_BUMP_AMOUNT);
}

fn get_balance(env: &Env, addr: &Address) -> i128 {
    let key = DataKey::Balance(addr.clone());
    if env.storage().persistent().has(&key) {
        env.storage().persistent().extend_ttl(
            &key,
            BALANCE_LIFETIME_THRESHOLD,
            BALANCE_BUMP_AMOUNT,
        );
        env.storage().persistent().get(&key).unwrap()
    } else {
        0
    }
}

fn set_balance(env: &Env, addr: &Address, amount: i128) {
    let key = DataKey::Balance(addr.clone());
    env.storage().persistent().set(&key, &amount);
    env.storage()
        .persistent()
        .extend_ttl(&key, BALANCE_LIFETIME_THRESHOLD, BALANCE_BUMP_AMOUNT);
}

fn get_allowance(env: &Env, from: &Address, spender: &Address) -> i128 {
    let key = DataKey::Allowance(AllowanceKey {
        from: from.clone(),
        spender: spender.clone(),
    });
    if let Some(val) = env
        .storage()
        .temporary()
        .get::<DataKey, AllowanceValue>(&key)
    {
        if env.ledger().sequence() >= val.expiration_ledger {
            0
        } else {
            val.amount
        }
    } else {
        0
    }
}

fn set_allowance(
    env: &Env,
    from: &Address,
    spender: &Address,
    amount: i128,
    expiration_ledger: u32,
) {
    let key = DataKey::Allowance(AllowanceKey {
        from: from.clone(),
        spender: spender.clone(),
    });
    let val = AllowanceValue {
        amount,
        expiration_ledger,
    };
    env.storage().temporary().set(&key, &val);
    if expiration_ledger > env.ledger().sequence() {
        env.storage().temporary().extend_ttl(
            &key,
            expiration_ledger - env.ledger().sequence(),
            expiration_ledger - env.ledger().sequence(),
        );
    }
}

fn require_admin(env: &Env, caller: &Address) {
    let admin: Address = env.storage().instance().get(&DataKey::Admin).unwrap();
    if *caller != admin {
        panic!("not authorized");
    }
}

// ---------------------------------------------------------------------------
// Contract
// ---------------------------------------------------------------------------
#[contract]
pub struct SimpleToken;

#[contractimpl]
impl SimpleToken {
    /// Initialize the token.
    /// `decimals` is fixed to 7 (Stellar convention).
    pub fn __constructor(env: Env, admin: Address, name: String, symbol: String) {
        env.storage().instance().set(&DataKey::Admin, &admin);
        env.storage().instance().set(&DataKey::Name, &name);
        env.storage().instance().set(&DataKey::Symbol, &symbol);
        env.storage().instance().set(&DataKey::TotalSupply, &0i128);
        extend_instance_ttl(&env);
    }

    // --- Metadata ---

    pub fn name(env: Env) -> String {
        extend_instance_ttl(&env);
        env.storage().instance().get(&DataKey::Name).unwrap()
    }

    pub fn symbol(env: Env) -> String {
        extend_instance_ttl(&env);
        env.storage().instance().get(&DataKey::Symbol).unwrap()
    }

    pub fn decimals(_env: Env) -> u32 {
        7
    }

    pub fn total_supply(env: Env) -> i128 {
        extend_instance_ttl(&env);
        env.storage()
            .instance()
            .get(&DataKey::TotalSupply)
            .unwrap_or(0)
    }

    // --- Admin ---

    pub fn admin(env: Env) -> Address {
        extend_instance_ttl(&env);
        env.storage().instance().get(&DataKey::Admin).unwrap()
    }

    // --- Balances ---

    pub fn balance(env: Env, id: Address) -> i128 {
        extend_instance_ttl(&env);
        get_balance(&env, &id)
    }

    // --- Mint ---

    pub fn mint(env: Env, admin: Address, to: Address, amount: i128) {
        admin.require_auth();
        require_admin(&env, &admin);
        if amount < 0 {
            panic!("negative amount is not allowed");
        }
        extend_instance_ttl(&env);

        let new_balance = get_balance(&env, &to) + amount;
        set_balance(&env, &to, new_balance);

        let supply: i128 = env
            .storage()
            .instance()
            .get(&DataKey::TotalSupply)
            .unwrap_or(0);
        env.storage()
            .instance()
            .set(&DataKey::TotalSupply, &(supply + amount));
    }

    // --- Transfer ---

    pub fn transfer(env: Env, from: Address, to: Address, amount: i128) {
        from.require_auth();
        if amount < 0 {
            panic!("negative amount is not allowed");
        }
        extend_instance_ttl(&env);

        let from_balance = get_balance(&env, &from);
        if from_balance < amount {
            panic!("insufficient balance");
        }
        set_balance(&env, &from, from_balance - amount);
        set_balance(&env, &to, get_balance(&env, &to) + amount);
    }

    // --- Allowance ---

    pub fn allowance(env: Env, from: Address, spender: Address) -> i128 {
        extend_instance_ttl(&env);
        get_allowance(&env, &from, &spender)
    }

    pub fn approve(
        env: Env,
        from: Address,
        spender: Address,
        amount: i128,
        expiration_ledger: u32,
    ) {
        from.require_auth();
        if amount < 0 {
            panic!("negative amount is not allowed");
        }
        extend_instance_ttl(&env);
        set_allowance(&env, &from, &spender, amount, expiration_ledger);
    }

    pub fn transfer_from(env: Env, spender: Address, from: Address, to: Address, amount: i128) {
        spender.require_auth();
        if amount < 0 {
            panic!("negative amount is not allowed");
        }
        extend_instance_ttl(&env);

        let current_allowance = get_allowance(&env, &from, &spender);
        if current_allowance < amount {
            panic!("insufficient allowance");
        }

        let from_balance = get_balance(&env, &from);
        if from_balance < amount {
            panic!("insufficient balance");
        }

        // Update allowance — preserve expiration_ledger by reading the stored value
        let key = DataKey::Allowance(AllowanceKey {
            from: from.clone(),
            spender: spender.clone(),
        });
        let stored: AllowanceValue = env.storage().temporary().get(&key).unwrap();
        set_allowance(
            &env,
            &from,
            &spender,
            stored.amount - amount,
            stored.expiration_ledger,
        );

        set_balance(&env, &from, from_balance - amount);
        set_balance(&env, &to, get_balance(&env, &to) + amount);
    }
}
