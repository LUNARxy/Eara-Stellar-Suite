// ─── Wallet ───────────────────────────────────────────────────────────────────

export interface StellarWalletConnection {
  address: string
  network: string
}

// ─── Proposal Types (mirror of Soroban contract storage_types.rs) ─────────────

export interface UpgradeProposal {
  wasmHash: string            // hex-encoded BytesN<32>
  proposer: string            // Stellar address
  approvals: string[]         // list of addresses that have approved
}

export type AdminAction = 'add' | 'remove'

export interface AdminProposal {
  action: AdminAction
  target: string              // address to add or remove
  proposer: string
  approvals: string[]
}

export interface ThresholdProposal {
  newThreshold: number
  proposer: string
  approvals: string[]
}

export interface UnpauseProposal {
  proposer: string
  approvals: string[]
}

export type FreezeAction = 'freeze' | 'unfreeze'

export interface FreezeProposal {
  action: FreezeAction
  target: string              // address to freeze or unfreeze
  proposer: string
  approvals: string[]
}

export interface SeizureProposal {
  target: string              // frozen account to confiscate from
  destination: string         // address to send seized tokens to
  amount: string              // raw i128 amount as string (display conversion done in UI)
  proposer: string
  approvals: string[]
}

// ─── Contract State ───────────────────────────────────────────────────────────

export interface LunarxyContractState {
  admins: string[]
  threshold: number
  paused: boolean
  version: number
  upgradeProposal: UpgradeProposal | null
  adminProposal: AdminProposal | null
  thresholdProposal: ThresholdProposal | null
  unpauseProposal: UnpauseProposal | null
  freezeProposal: FreezeProposal | null
  seizureProposal: SeizureProposal | null
}

// ─── TX result ────────────────────────────────────────────────────────────────

export interface StellarTxResult {
  txHash: string
  success: boolean
  errorMessage?: string
}

// ─── Compliant-ID Contract Types ──────────────────────────────────────────────

export type ComplianceStatus = 'Unverified' | 'Verified' | 'Suspended' | 'Revoked'

export interface UserComplianceRecord {
  status: ComplianceStatus
  level: number                 // verification tier (min 1)
  expiresAt: number             // ledger timestamp
  countryCode: string           // ISO country code (e.g. "US", "ES")
  issuer: string                // Stellar address of the trusted issuer that wrote this record
}

export interface CompliantIdContractState {
  admin: string
  trustedIssuers: string[]
  restrictedCountries: string[]
}
