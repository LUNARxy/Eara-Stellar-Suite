# AGENTS.md - AI Coding Agent Guidelines

This document provides guidelines for AI coding agents working in this Stellar/Soroban smart contracts repository.

## Project Overview

| Attribute | Value |
|-----------|-------|
| Language | Rust (2021 edition) |
| Project Type | Soroban Smart Contracts (Stellar blockchain) |
| Build Target | WebAssembly (`wasm32v1-none`) |
| Primary SDK | `soroban-sdk = "25"` |
| Structure | Cargo workspace |

## Build Commands

```bash
stellar contract build          # Build all contracts to WASM
make build                      # From a contract directory
cargo build --profile release-with-logs  # Build with debug assertions for logging
```

## Test Commands

```bash
cargo test                                    # Run all tests
cargo test -p lunarxy-token                   # Run tests for a specific contract
cargo test -p lunarxy-token test_mint         # Run a single test by name
cargo test -p lunarxy-token -- --nocapture    # Show log output
cargo test -p lunarxy-token pattern           # Run tests matching a pattern
```

## Lint and Format Commands

```bash
cargo fmt --all                        # Format all code
cargo fmt --all -- --check             # Check formatting without applying
cargo clippy --all-targets             # Run linter
cargo clippy --all-targets -- -D warnings  # Warnings as errors
```

## Project Structure

For simple contracts, use a flat layout. For complex contracts, split logic into modules:

```
contracts/
└── <contract-name>/
    ├── Cargo.toml
    ├── Makefile
    └── src/
        ├── lib.rs          # #![no_std], module declarations, pub use re-exports
        ├── contract.rs     # #[contract] struct + #[contractimpl] (complex contracts)
        ├── admin.rs        # Admin/governance logic
        ├── allowance.rs    # Allowance logic
        ├── balance.rs      # Balance storage helpers
        ├── event.rs        # #[contractevent] typed events
        ├── metadata.rs     # Token metadata helpers
        ├── storage_types.rs # DataKey enum + TTL constants + proposal structs
        ├── upgrade.rs      # Upgrade proposal logic
        └── test.rs         # #![cfg(test)] tests
```

`lib.rs` for a multi-module contract:

```rust
#![no_std]

mod admin;
mod balance;
mod contract;
mod event;
mod storage_types;

mod test;

pub use contract::MyContract;
```

## Code Style Guidelines

### Required File Attributes

```rust
// lib.rs — must be first line
#![no_std]

// test.rs — must be first line
#![cfg(test)]
```

### Imports

- `soroban_sdk` imports first, then other crates
- Use specific imports; avoid wildcards except `use super::*;` in test.rs

```rust
use soroban_sdk::{contract, contractimpl, contracttype, Address, Env, String, Vec};
```

### Contract Definition

```rust
#[contract]
pub struct MyContract;

#[contractimpl]
impl MyContract {
    pub fn my_function(env: Env, caller: Address, amount: i128) -> i128 {
        caller.require_auth();
        // implementation
    }
}
```

### Naming Conventions

| Item | Convention | Example |
|------|------------|---------|
| Contracts | PascalCase | `LunarxyToken`, `Contract` |
| Functions | snake_case | `get_balance`, `propose_upgrade` |
| Variables | snake_case | `contract_id`, `user_balance` |
| Constants | SCREAMING_SNAKE_CASE | `INSTANCE_BUMP_AMOUNT`, `MAX_SUPPLY` |
| Types/Structs/Enums | PascalCase | `DataKey`, `AllowanceValue` |

### Storage Patterns

Use a `DataKey` enum with `#[contracttype]` for all storage keys. Apply TTL bumps on every read/write for persistent and instance storage.

```rust
const INSTANCE_LIFETIME_THRESHOLD: u32 = 518_400;
const INSTANCE_BUMP_AMOUNT: u32 = 1_036_800;
const BALANCE_LIFETIME_THRESHOLD: u32 = 518_400;
const BALANCE_BUMP_AMOUNT: u32 = 1_036_800;

#[contracttype]
pub enum DataKey {
    Balance(Address),
    Allowance(AllowanceDataKey),
    Admins,
    Paused,
}
```

Storage tiers:
- `env.storage().instance()` — contract-level data (metadata, admin list, paused flag); always bump TTL
- `env.storage().persistent()` — per-user data (balances); bump TTL on access
- `env.storage().temporary()` — short-lived data (allowances with expiration ledger)

### Events

Use the `#[contractevent]` macro for typed, structured events:

```rust
use soroban_sdk::contractevent;

#[contractevent]
pub struct Transfer {
    pub from: Address,
    pub to: Address,
    pub amount: i128,
}
```

Publish with `env.events().publish(Transfer { from, to, amount });`

### Error Handling

- Use `panic!` for unrecoverable invariant violations
- Use `#[contracterror]` enums for user-facing recoverable errors

```rust
use soroban_sdk::contracterror;

#[contracterror]
#[derive(Copy, Clone, Debug, Eq, PartialEq)]
#[repr(u32)]
pub enum Error {
    NotFound = 1,
    NotAuthorized = 2,
    InvalidAmount = 3,
}
```

### Testing Patterns

```rust
#![cfg(test)]

use super::*;
use soroban_sdk::{Env, String};

#[test]
fn test_transfer() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register(MyContract, ());
    let client = MyContractClient::new(&env, &contract_id);

    let result = client.transfer(&user, &recipient, &100i128);
    assert_eq!(result, ());
}
```

- Use `env.mock_all_auths()` to bypass auth checks in tests
- Test snapshots in `test_snapshots/` are auto-generated by the framework — do not edit manually
- For crypto tests, add `ed25519-dalek` and `rand` to `[dev-dependencies]`

### Cargo.toml Template

```toml
[package]
name = "contract-name"
version = "0.0.0"
edition = "2021"
publish = false

[lib]
crate-type = ["lib", "cdylib"]
doctest = false

[dependencies]
soroban-sdk = { workspace = true }

[dev-dependencies]
soroban-sdk = { workspace = true, features = ["testutils"] }
```

## Important Notes

- **No std**: All contracts must use `#![no_std]`; use Soroban SDK types (`String`, `Vec`, `Map`, `Address`) instead of std equivalents
- **Auth**: Always call `address.require_auth()` before privileged operations
- **WASM profile**: Release builds use `opt-level = "z"`, `lto = true`, `panic = "abort"`, `overflow-checks = true`
- **Debugging**: Use `release-with-logs` profile + `soroban_sdk::log!` macro + `--nocapture` flag

## Creating a New Contract

1. Create `contracts/<contract-name>/` with `Cargo.toml` using the template above
2. Add the contract to the workspace `members` in root `Cargo.toml` (glob `contracts/*` handles this automatically)
3. Create `src/lib.rs` starting with `#![no_std]`
4. Create `src/test.rs` starting with `#![cfg(test)]`
5. Add `mod test;` at the bottom of `lib.rs`
6. For complex contracts, split into modules (`contract.rs`, `storage_types.rs`, `event.rs`, etc.) and re-export the main struct with `pub use contract::MyContract;`
