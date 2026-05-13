# Lunarxy-Token Test Suite — Complete Reference

**Contract:** `lunarxy-token` (Soroban/Soroban SDK)  
**File:** `contracts/lunarxy-token/src/test.rs`  
**Total tests:** 77  
**Tests expecting panic:** 27  

---

## Summary by Category

| Category | Tests | Panics | First line |
|----------|-------|--------|------------|
| Constructor | 5 | 3 | `test_initialize` (47) |
| Mint | 4 | 2 | `test_mint_by_admin` (133) |
| Transfer | 2 | 1 | `test_transfer` (189) |
| Burn | 3 | 1 | `test_burn` (222) |
| Allowance | 3 | 1 | `test_approve_and_transfer_from` (269) |
| Pause | 5 | 2 | `test_pause_by_admin` (320) |
| Upgrade (multisig) | 7 | 4 | `test_propose_upgrade` (400) |
| Admin management (multisig) | 8 | 3 | `test_add_admin_multisig` (484) |
| Threshold change (multisig) | 6 | 2 | `test_change_threshold` (591) |
| Edge cases / integration | 9 | 0 | `test_decimals_is_zero` (666) |
| User Mint (with signer) | 14 | 4 | `test_user_mint_happy_path` (841) |
| User Mint With Token | 11 | 4 | `test_user_mint_with_token_happy_path` (1129) |

---

## Detailed Test Catalog

### 1. Constructor Tests

| Test | Line | Description | Expected panic |
|------|------|-------------|----------------|
| `test_initialize` | 48 | Verifies name, symbol, decimals=0, total_supply=0, version=1, not paused | — |
| `test_admins_initialized` | 61 | Checks that 5 admins are stored and threshold=3 | — |
| `test_constructor_too_few_admins` | 75 | Constructor with <3 admins | `"minimum 3 admins required"` |
| `test_constructor_threshold_exceeds_admins` | 91 | threshold > admin count | `"threshold cannot exceed admin count"` |
| `test_constructor_duplicate_admins` | 112 | Duplicate addresses in admin list | `"duplicate admin address"` |

**Helper:** `create_token(env)` — creates contract with 5 admins, threshold=3.

---

### 2. Mint Tests

| Test | Line | Description | Panic |
|------|------|-------------|-------|
| `test_mint_by_admin` | 133 | Admin can mint; balance and total supply increase | — |
| `test_mint_by_any_admin` | 146 | Multiple different admins can mint independently | — |
| `test_mint_fails_non_admin` | 162 | Non-admin calls mint | `"not an admin"` |
| `test_mint_negative_amount` | 174 | mint with negative amount | `"negative amount is not allowed"` |

---

### 3. Transfer Tests

| Test | Line | Description | Panic |
|------|------|-------------|-------|
| `test_transfer` | 189 | Simple transfer between users | — |
| `test_transfer_insufficient_balance` | 205 | Transfer amount > balance | `"insufficient balance"` |

---

### 4. Burn Tests

| Test | Line | Description | Panic |
|------|------|-------------|-------|
| `test_burn` | 222 | burn reduces balance and total supply | — |
| `test_burn_from_with_allowance` | 236 | burn_from consumes allowance correctly | — |
| `test_burn_insufficient_balance` | 253 | burn amount > balance | `"insufficient balance"` |

---

### 5. Allowance Tests

| Test | Line | Description | Panic |
|------|------|-------------|-------|
| `test_approve_and_transfer_from` | 269 | approve + transfer_from work correctly | — |
| `test_transfer_from_insufficient_allowance` | 290 | transfer_from > allowance | `"insufficient allowance"` |
| `test_allowance_zero_balance` | 305 | No allowance set, returns 0 | — |

---

### 6. Pause Tests

| Test | Line | Description | Panic |
|------|------|-------------|-------|
| `test_pause_by_admin` | 320 | Admin can pause; is_paused() becomes true | — |
| `test_transfer_blocked_when_paused` | 332 | transfer fails when paused | `"contract is paused"` |
| `test_transfer_from_blocked_when_paused` | 345 | transfer_from fails when paused | `"contract is paused"` |
| `test_unpause_requires_multisig` | 361 | Unpause needs threshold approvals (3/3) | — |
| `test_pause_fails_non_admin` | 385 | Non-admin calls pause | `"not an admin"` |

**Note:** Mint and burn are NOT blocked by pause (verified in Edge Cases).

---

### 7. Multi-Sig: Upgrade Proposal Tests

| Test | Line | Description | Panic |
|------|------|-------------|-------|
| `test_propose_upgrade` | 400 | propose_upgrade creates proposal; proposer auto-approves | — |
| `test_only_one_upgrade_proposal_at_time` | 416 | Second proposal while one active | `"an upgrade proposal is already active"` |
| `test_duplicate_upgrade_approval_fails` | 431 | Same admin approves twice | `"already approved this proposal"` |
| `test_cancel_upgrade` | 442 | Proposer can cancel their proposal | — |
| `test_cancel_upgrade_non_proposer` | 456 | Non-proposer cancel attempt | `"only the proposer can cancel"` |
| `test_propose_upgrade_non_admin` | 468 | Non-admin proposes upgrade | `"not an admin"` |
| `test_handle_upgrade_by_admin` | 472 | handle_upgrade by admin succeeds | — |
| `test_handle_upgrade_non_admin` | 782 | Non-admin calls handle_upgrade | `"not an admin"` |

---

### 8. Multi-Sig: Admin Management Tests

| Test | Line | Description | Panic |
|------|------|-------------|-------|
| `test_add_admin_multisig` | 484 | propose_add_admin + 2 approvals (threshold=3) executes | — |
| `test_remove_admin_multisig` | 505 | propose_remove_admin + 2 approvals executes | — |
| `test_cannot_remove_admin_below_threshold` | 521 | Removal would leave <= threshold admins | `"cannot remove admin: would go below threshold"` |
| `test_add_duplicate_admin_fails` | 549 | Adding an already-admin address | `"address is already an admin"` |
| `test_cancel_admin_proposal` | 559 | Proposer cancels admin proposal | — |
| `test_only_one_admin_proposal_at_time` | 573 | Second admin proposal while one active | `"an admin proposal is already active"` |

---

### 9. Multi-Sig: Threshold Change Tests

| Test | Line | Description | Panic |
|------|------|-------------|-------|
| `test_change_threshold` | 591 | propose_change_threshold + approvals updates threshold | — |
| `test_threshold_too_high` | 607 | Threshold > current admin count | `"invalid threshold: must be between 1 and admin count"` |
| `test_threshold_zero` | 617 | Threshold = 0 | `"invalid threshold: must be between 1 and admin count"` |
| `test_new_threshold_applies_to_next_proposals` | 627 | After changing threshold, new proposals use new value | — |
| `test_cancel_threshold_proposal` | 648 | Proposer cancels threshold change | — |

---

### 10. Edge Cases / Integration Tests

| Test | Line | Description |
|------|------|-------------|
| `test_decimals_is_zero` | 666 | decimals() always returns 0 |
| `test_zero_amount_transfer` | 674 | Transferring 0 tokens is a no-op (no panic) |
| `test_mint_burn_supply_tracking` | 689 | Supply increases/decreases correctly across multiple mints/burns |
| `test_multiple_users_balances` | 706 | Multiple users have independent balances |
| `test_mint_while_paused_still_works` | 732 | Mint is NOT blocked by pause |
| `test_burn_while_paused_still_works` | 748 | Burn is NOT blocked by pause |
| `test_version_starts_at_one` | 764 | version() returns 1 after constructor |
| `test_handle_upgrade_by_admin` | 772 | handle_upgrade by admin does not panic |
| `test_set_signer_key_non_admin` | 988 | Non-admin calls set_signer_key | `"not an admin"` |

---

### 11. User Mint Tests (with Ed25519 signer)

**External dev-dependencies:** `ed25519-dalek`, `rand`.  
**Helper functions:**
- `build_message(env, amount, price, nonce, uid, contract_id)` → `BytesN<32>` hash. Layout: `amount(16 LE) | price(16 LE) | nonce(8 LE) | uid(8 LE) | contract_xdr`
- `setup_user_mint(env)` → generates random Ed25519 key, registers public key via `set_signer_key`, returns `(client, admins, SigningKey, signer_key)`

| Test | Line | Description | Panic |
|------|------|-------------|-------|
| `test_user_mint_happy_path` | 841 | Full flow: valid signature, nonce increments | — |
| `test_user_mint_nonce_increments` | 867 | Nonce on-chain increases after each mint | — |
| `test_user_mint_wrong_nonce` | 892 | Nonce mismatch (expected 0, got 5) | `"invalid nonce"` |
| `test_user_mint_invalid_signature` | 914 | Signature from different key | (generic panic) |
| `test_user_mint_replay_attack` | 938 | Replay same signature/nonce | (nonce reuse) |
| `test_user_mint_no_signer_key` | 963 | Attempt user_mint without set_signer_key | `"signer key not configured"` |
| `test_get_signer_key` | 1001 | get_signer_key returns Some(signer_key) after setup | — |
| `test_set_signer_key_non_admin` | 987 | Non-admin calls set_signer_key | `"not an admin"` |
| `test_user_mint_blocked_when_paused` | 1011 | user_mint fails if contract paused | `"contract is paused"` |
| `test_user_mint_negative_amount` | 1035 | amount = -1 | `"negative amount is not allowed"` |

---

### 12. User Mint With Token Tests

**Extended message layout:**  
`amount(16 LE) | payment_amount(16 LE) | nonce(8 LE) | uid(8 LE) | contract_xdr | payment_token_xdr`

**Helper:** `setup_payment_token(env, admins, holder, spender, mint_amount, allowance)` — creates a second LunarxyToken contract, mints payment tokens to `holder`, approves `spender` (the main contract) to spend `allowance`.

| Test | Line | Description | Panic |
|------|------|-------------|-------|
| `test_user_mint_with_token_happy_path` | 1129 | Full flow with secondary payment token | — |
| `test_user_mint_with_token_wrong_nonce` | 1186 | Wrong nonce | `"invalid nonce"` |
| `test_user_mint_with_token_invalid_signature` | 1234 | Signature from different key | (generic panic) |
| `test_user_mint_with_token_replay_attack` | 1283 | Replay with same nonce | (panic) |
| `test_user_mint_with_token_blocked_when_paused` | 1344 | Contract paused | `"contract is paused"` |
| `test_user_mint_with_token_wrong_payment_token_in_sig` | 1395 | Signature includes token A, call passes token B | (panic, mismatched hash) |
| `test_user_mint_with_token_wrong_payment_amount_in_sig` | 1448 | Signature uses payment_amount=100, call passes 1 | (panic, mismatched hash) |

---

## How to Run Tests

```bash
# All tests
cargo test

# Specific test by name
cargo test test_user_mint_happy_path

# All user_mint tests
cargo test user_mint

# With log output (if any)
cargo test -- --nocapture

# For a specific package in workspace
cargo test -p lunarxy-token

# Single test with release-with-logs profile (if logging enabled)
cargo test -p lunarxy-token --profile release-with-logs -- test_user_mint_happy_path --nocapture
```

---

## Dev Dependencies Required

In `contracts/lunarxy-token/Cargo.toml`:

```toml
[dev-dependencies]
soroban-sdk = { workspace = true, features = ["testutils"] }
ed25519-dalek = { version = "2", features = ["rand_core"] }
rand = "0.8"
```

Without `ed25519-dalek` and `rand`, the `user_mint` and `user_mint_with_token` tests will fail to compile.

---

## Notes

- All tests use `env.mock_all_auths()` to bypass signature checks unless testing auth explicitly.
- The `setup_user_mint` helper is reused by ~13 tests and ensures `set_signer_key` has been called.
- Multi-sig proposals auto-approve the proposer on creation (counts as 1 approval toward threshold).
- Pause does **not** block mint or burn operations, only `transfer` and `transfer_from`.
- `BytesN<32>` is used for:
  - WASM hashes (upgrade proposals)
  - Ed25519 public keys (signer key)
  - SHA-256 digests (message hashes for user_mint)
- All amounts are `i128`; nonces are `u64`.
