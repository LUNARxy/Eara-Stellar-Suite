<template>
  <div class="lunarxy-governance-container">

    <!-- Loading Overlay -->
    <div v-if="isProcessingTx" class="loading-overlay">
      <div class="loading-modal">
        <div class="spinner"></div>
        <h3>{{ processingMessage }}</h3>
        <p>Please wait while the transaction is being processed...</p>
      </div>
    </div>

    <!-- Header -->
    <div class="header">
      <h1>LunarXY Token — Stellar Admin</h1>
      <p class="subtitle">
        Manage admin operations on the LunarXY Soroban contract via Freighter wallet.
      </p>
    </div>

    <!-- Wallet Connection -->
    <div v-if="!isConnected" class="connection-warning">
      <p>Please connect your Freighter wallet to use this panel.</p>
      <button @click="connectWallet" class="btn-connect" :disabled="isConnecting">
        <span v-if="isConnecting">Connecting...</span>
        <span v-else>Connect Freighter Wallet</span>
      </button>
      <div v-if="errorMessage && !isConnected" class="message error" style="margin-top: 1rem;">
        {{ errorMessage }}
      </div>
    </div>

    <div v-else class="content">

      <!-- Connected bar -->
      <div class="connected-bar">
        <span class="wallet-address">
          Connected: {{ truncateAddress(connectedAddress) }}
        </span>
        <button @click="disconnectWallet" class="btn-disconnect">Disconnect</button>
        <button @click="loadContractState" class="btn-secondary" :disabled="isLoadingState">
          <span v-if="isLoadingState">Loading...</span>
          <span v-else>Refresh State</span>
        </button>
      </div>

      <!-- Global messages -->
      <div v-if="successMessage" class="message success">{{ successMessage }}</div>
      <div v-if="errorMessage" class="message error">{{ errorMessage }}</div>

      <!-- ─── Contract State Panel ─────────────────────────────────────────── -->
      <div class="section-card state-panel">
        <h2>Contract State</h2>
        <div v-if="isLoadingState" class="loading-inline">Loading state...</div>
        <div v-else class="state-grid">
          <div class="state-item">
            <span class="state-label">Status</span>
            <span :class="contractState.paused ? 'badge badge-danger' : 'badge badge-success'">
              {{ contractState.paused ? 'PAUSED' : 'ACTIVE' }}
            </span>
          </div>
          <div class="state-item">
            <span class="state-label">Threshold</span>
            <span class="state-value">{{ contractState.threshold }} / {{ contractState.admins.length }} admins</span>
          </div>
          <div class="state-item full-width">
            <span class="state-label">Admins ({{ contractState.admins.length }})</span>
            <ul class="address-list">
              <li v-for="admin in contractState.admins" :key="admin" class="address-item">
                <span :class="admin === connectedAddress ? 'address-me' : ''">
                  {{ admin }}
                  <em v-if="admin === connectedAddress"> (you)</em>
                </span>
              </li>
            </ul>
          </div>

          <!-- Active Proposals Summary -->
          <div v-if="contractState.upgradeProposal" class="state-item full-width proposal-badge">
            <span class="badge badge-warning">Active: Upgrade Proposal</span>
            <span class="proposal-detail">
              Proposer: {{ truncateAddress(contractState.upgradeProposal.proposer) }} |
              Approvals: {{ contractState.upgradeProposal.approvals.length }} / {{ contractState.threshold }}
            </span>
          </div>
          <div v-if="contractState.adminProposal" class="state-item full-width proposal-badge">
            <span class="badge badge-warning">
              Active: Admin Proposal ({{ contractState.adminProposal.action === 'add' ? 'Add' : 'Remove' }})
            </span>
            <span class="proposal-detail">
              Target: {{ truncateAddress(contractState.adminProposal.target) }} |
              Approvals: {{ contractState.adminProposal.approvals.length }} / {{ contractState.threshold }}
            </span>
          </div>
          <div v-if="contractState.thresholdProposal" class="state-item full-width proposal-badge">
            <span class="badge badge-warning">Active: Threshold Proposal</span>
            <span class="proposal-detail">
              New threshold: {{ contractState.thresholdProposal.newThreshold }} |
              Approvals: {{ contractState.thresholdProposal.approvals.length }} / {{ contractState.threshold }}
            </span>
          </div>
          <div v-if="contractState.unpauseProposal" class="state-item full-width proposal-badge">
            <span class="badge badge-warning">Active: Unpause Proposal</span>
            <span class="proposal-detail">
              Proposer: {{ truncateAddress(contractState.unpauseProposal.proposer) }} |
              Approvals: {{ contractState.unpauseProposal.approvals.length }} / {{ contractState.threshold }}
            </span>
          </div>
          <div v-if="contractState.freezeProposal" class="state-item full-width proposal-badge">
            <span class="badge badge-warning">
              Active: {{ contractState.freezeProposal.action === 'freeze' ? 'Freeze' : 'Unfreeze' }} Proposal
            </span>
            <span class="proposal-detail">
              Target: {{ truncateAddress(contractState.freezeProposal.target) }} |
              Approvals: {{ contractState.freezeProposal.approvals.length }} / {{ contractState.threshold }}
            </span>
          </div>
          <div v-if="contractState.seizureProposal" class="state-item full-width proposal-badge">
            <span class="badge badge-danger">Active: Seizure Proposal</span>
            <span class="proposal-detail">
              Target: {{ truncateAddress(contractState.seizureProposal.target) }} |
              Dest: {{ truncateAddress(contractState.seizureProposal.destination) }} |
              Approvals: {{ contractState.seizureProposal.approvals.length }} / {{ contractState.threshold }}
            </span>
          </div>
        </div>
      </div>

      <!-- ─── SINGLE-ADMIN OPERATIONS ──────────────────────────────────────── -->

      <!-- Mint Tokens -->
      <div class="section-card">
        <h2>Mint Tokens</h2>
        <p class="description">
          Mint new LunarXY tokens to any address. Any single admin can call this operation.
        </p>
        <form @submit.prevent="handleMint" class="operation-form">
          <div class="form-group">
            <label>Recipient Address (Stellar G...)</label>
            <input
              v-model="mintTo"
              type="text"
              placeholder="GABC..."
              class="input-field"
              :disabled="isSubmitting"
              required
            />
          </div>
          <div class="form-group">
            <label>Amount</label>
            <input
              v-model="mintAmount"
              type="number"
              min="0"
              step="any"
              placeholder="100.0"
              class="input-field"
              :disabled="isSubmitting"
              required
            />
            <small class="hint">Amount in display units (e.g. 100 = 100 tokens)</small>
          </div>
          <button type="submit" class="btn-primary" :disabled="isSubmitting || !isValidStellarAddress(mintTo) || !mintAmount">
            <span v-if="isSubmitting">Processing...</span>
            <span v-else>Mint Tokens</span>
          </button>
        </form>
      </div>

      <!-- Pause Contract -->
      <div class="section-card section-danger">
        <h2>Pause Contract (Emergency)</h2>
        <p class="description">
          Immediately pauses all token transfers. Any single admin can execute this.
          Unpausing requires multi-sig approval.
        </p>
        <div v-if="contractState.paused" class="message warning">
          The contract is already paused. Use "Multi-sig: Unpause" below to propose unpausing.
        </div>
        <div v-else>
          <button
            @click="handlePause"
            class="btn-danger"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting">Processing...</span>
            <span v-else>Pause Contract</span>
          </button>
        </div>
      </div>

      <!-- Set Signer Key -->
      <div class="section-card">
        <h2>Set Signer Key</h2>
        <p class="description">
          Update the Ed25519 public key used to verify backend-issued mint signatures.
          Any single admin can call this.
        </p>
        <form @submit.prevent="handleSetSignerKey" class="operation-form">
          <div class="form-group">
            <label>Ed25519 Public Key (32 bytes / 64 hex chars)</label>
            <input
              v-model="signerKeyHex"
              type="text"
              placeholder="aabbcc...  (64 hex characters)"
              class="input-field"
              :disabled="isSubmitting"
              required
              maxlength="66"
            />
            <small class="hint">
              Hex-encoded 32-byte Ed25519 public key. No 0x prefix needed.
              Current key length: {{ signerKeyHex.replace(/^0x/, '').length }} / 64 chars
            </small>
          </div>
          <button
            type="submit"
            class="btn-primary"
            :disabled="isSubmitting || signerKeyHex.replace(/^0x/, '').length !== 64"
          >
            <span v-if="isSubmitting">Processing...</span>
            <span v-else>Set Signer Key</span>
          </button>
        </form>
      </div>

      <!-- ─── MULTI-SIG: UNPAUSE ────────────────────────────────────────────── -->
      <div class="section-card">
        <h2>Multi-sig: Unpause</h2>
        <p class="description">
          Unpausing the contract requires {{ contractState.threshold }} admin approval(s).
        </p>

        <!-- Active proposal -->
        <div v-if="contractState.unpauseProposal" class="proposal-box">
          <h3>Active Unpause Proposal</h3>
          <p><strong>Proposer:</strong> {{ contractState.unpauseProposal.proposer }}</p>
          <p>
            <strong>Approvals:</strong>
            {{ contractState.unpauseProposal.approvals.length }} / {{ contractState.threshold }}
          </p>
          <ul class="address-list">
            <li v-for="a in contractState.unpauseProposal.approvals" :key="a">{{ a }}</li>
          </ul>

          <div class="proposal-actions">
            <button
              v-if="!contractState.unpauseProposal.approvals.includes(connectedAddress)"
              @click="handleApproveUnpause"
              class="btn-primary"
              :disabled="isSubmitting"
            >
              Approve Unpause
            </button>
            <span v-else class="already-approved">You have already approved</span>

            <button
              v-if="contractState.unpauseProposal.proposer === connectedAddress"
              @click="handleCancelUnpause"
              class="btn-secondary"
              :disabled="isSubmitting"
            >
              Cancel Proposal
            </button>
          </div>
        </div>

        <!-- No active proposal -->
        <div v-else>
          <div v-if="!contractState.paused" class="message warning">
            The contract is not paused — no unpause proposal is needed.
          </div>
          <button
            v-else
            @click="handleProposeUnpause"
            class="btn-primary"
            :disabled="isSubmitting"
          >
            Propose Unpause
          </button>
        </div>
      </div>

      <!-- ─── MULTI-SIG: UPGRADE ────────────────────────────────────────────── -->
      <div class="section-card">
        <h2>Multi-sig: Contract Upgrade</h2>
        <p class="description">
          Upgrading the contract WASM requires {{ contractState.threshold }} admin approval(s).
        </p>

        <!-- Active proposal -->
        <div v-if="contractState.upgradeProposal" class="proposal-box">
          <h3>Active Upgrade Proposal</h3>
          <p><strong>WASM Hash:</strong> <code>{{ contractState.upgradeProposal.wasmHash }}</code></p>
          <p><strong>Proposer:</strong> {{ contractState.upgradeProposal.proposer }}</p>
          <p>
            <strong>Approvals:</strong>
            {{ contractState.upgradeProposal.approvals.length }} / {{ contractState.threshold }}
          </p>
          <ul class="address-list">
            <li v-for="a in contractState.upgradeProposal.approvals" :key="a">{{ a }}</li>
          </ul>

          <div class="proposal-actions">
            <button
              v-if="!contractState.upgradeProposal.approvals.includes(connectedAddress)"
              @click="handleApproveUpgrade"
              class="btn-primary"
              :disabled="isSubmitting"
            >
              Approve Upgrade
            </button>
            <span v-else class="already-approved">You have already approved</span>

            <button
              v-if="contractState.upgradeProposal.proposer === connectedAddress"
              @click="handleCancelUpgrade"
              class="btn-secondary"
              :disabled="isSubmitting"
            >
              Cancel Proposal
            </button>
          </div>
        </div>

        <!-- Propose new upgrade -->
        <div v-else>
          <form @submit.prevent="handleProposeUpgrade" class="operation-form">
            <div class="form-group">
              <label>New WASM Hash (32 bytes / 64 hex chars)</label>
              <input
                v-model="upgradeWasmHash"
                type="text"
                placeholder="aabbcc... (64 hex characters)"
                class="input-field"
                :disabled="isSubmitting"
                required
                maxlength="64"
              />
              <small class="hint">
                Hex-encoded SHA-256 hash of the new contract WASM, as returned by
                <code>soroban contract install</code>.
              </small>
            </div>
            <button
              type="submit"
              class="btn-primary"
              :disabled="isSubmitting || upgradeWasmHash.replace(/^0x/, '').length !== 64"
            >
              Propose Upgrade
            </button>
          </form>
        </div>
      </div>

      <!-- ─── MULTI-SIG: ADMINS ─────────────────────────────────────────────── -->
      <div class="section-card">
        <h2>Multi-sig: Admin Management</h2>
        <p class="description">
          Adding or removing admins requires {{ contractState.threshold }} approval(s).
          Only one proposal can be active at a time.
        </p>

        <!-- Active proposal -->
        <div v-if="contractState.adminProposal" class="proposal-box">
          <h3>
            Active Proposal: {{ contractState.adminProposal.action === 'add' ? 'Add Admin' : 'Remove Admin' }}
          </h3>
          <p><strong>Target:</strong> {{ contractState.adminProposal.target }}</p>
          <p><strong>Proposer:</strong> {{ contractState.adminProposal.proposer }}</p>
          <p>
            <strong>Approvals:</strong>
            {{ contractState.adminProposal.approvals.length }} / {{ contractState.threshold }}
          </p>
          <ul class="address-list">
            <li v-for="a in contractState.adminProposal.approvals" :key="a">{{ a }}</li>
          </ul>

          <div class="proposal-actions">
            <button
              v-if="!contractState.adminProposal.approvals.includes(connectedAddress)"
              @click="handleApproveAdminProposal"
              class="btn-primary"
              :disabled="isSubmitting"
            >
              Approve
            </button>
            <span v-else class="already-approved">You have already approved</span>

            <button
              v-if="contractState.adminProposal.proposer === connectedAddress"
              @click="handleCancelAdminProposal"
              class="btn-secondary"
              :disabled="isSubmitting"
            >
              Cancel Proposal
            </button>
          </div>
        </div>

        <!-- Propose add/remove -->
        <div v-else>
          <div class="tab-bar">
            <button
              :class="adminTab === 'add' ? 'tab-active' : 'tab'"
              @click="adminTab = 'add'"
            >Add Admin</button>
            <button
              :class="adminTab === 'remove' ? 'tab-active' : 'tab'"
              @click="adminTab = 'remove'"
            >Remove Admin</button>
          </div>

          <form @submit.prevent="adminTab === 'add' ? handleProposeAddAdmin() : handleProposeRemoveAdmin()" class="operation-form">
            <div class="form-group">
              <label>{{ adminTab === 'add' ? 'New Admin Address' : 'Admin Address to Remove' }}</label>
              <input
                v-model="adminTargetAddress"
                type="text"
                placeholder="GABC..."
                class="input-field"
                :disabled="isSubmitting"
                required
              />
            </div>
            <button
              type="submit"
              class="btn-primary"
              :disabled="isSubmitting || !isValidStellarAddress(adminTargetAddress)"
            >
              <span v-if="adminTab === 'add'">Propose Add Admin</span>
              <span v-else>Propose Remove Admin</span>
            </button>
          </form>
        </div>
      </div>

      <!-- ─── MULTI-SIG: THRESHOLD ──────────────────────────────────────────── -->
      <div class="section-card">
        <h2>Multi-sig: Change Threshold</h2>
        <p class="description">
          Changing the approval threshold requires {{ contractState.threshold }} approval(s).
          Current threshold: {{ contractState.threshold }}.
        </p>

        <!-- Active proposal -->
        <div v-if="contractState.thresholdProposal" class="proposal-box">
          <h3>Active Threshold Proposal</h3>
          <p><strong>New Threshold:</strong> {{ contractState.thresholdProposal.newThreshold }}</p>
          <p><strong>Proposer:</strong> {{ contractState.thresholdProposal.proposer }}</p>
          <p>
            <strong>Approvals:</strong>
            {{ contractState.thresholdProposal.approvals.length }} / {{ contractState.threshold }}
          </p>
          <ul class="address-list">
            <li v-for="a in contractState.thresholdProposal.approvals" :key="a">{{ a }}</li>
          </ul>

          <div class="proposal-actions">
            <button
              v-if="!contractState.thresholdProposal.approvals.includes(connectedAddress)"
              @click="handleApproveThresholdProposal"
              class="btn-primary"
              :disabled="isSubmitting"
            >
              Approve
            </button>
            <span v-else class="already-approved">You have already approved</span>

            <button
              v-if="contractState.thresholdProposal.proposer === connectedAddress"
              @click="handleCancelThresholdProposal"
              class="btn-secondary"
              :disabled="isSubmitting"
            >
              Cancel Proposal
            </button>
          </div>
        </div>

        <!-- Propose new threshold -->
        <div v-else>
          <form @submit.prevent="handleProposeChangeThreshold" class="operation-form">
            <div class="form-group">
              <label>New Threshold (1 – {{ contractState.admins.length }})</label>
              <input
                v-model.number="newThreshold"
                type="number"
                :min="1"
                :max="contractState.admins.length"
                class="input-field"
                :disabled="isSubmitting"
                required
              />
            </div>
            <button
              type="submit"
              class="btn-primary"
              :disabled="isSubmitting || newThreshold < 1 || newThreshold > contractState.admins.length"
            >
              Propose Change Threshold
            </button>
          </form>
        </div>
      </div>

      <!-- ─── FROZEN STATUS CHECK ───────────────────────────────────────────── -->
      <div class="section-card">
        <h2>Check Frozen Status</h2>
        <p class="description">
          Check whether a given account address is currently frozen on the contract.
        </p>
        <form @submit.prevent="handleCheckFrozen" class="operation-form">
          <div class="form-group">
            <label>Account Address</label>
            <input
              v-model="frozenCheckAddress"
              type="text"
              placeholder="GABC..."
              class="input-field"
              :disabled="isSubmitting"
              required
            />
          </div>
          <button
            type="submit"
            class="btn-secondary"
            :disabled="isSubmitting || !isValidStellarAddress(frozenCheckAddress)"
          >
            Check Frozen
          </button>
        </form>
        <div v-if="frozenCheckResult !== null" class="message" :class="frozenCheckResult ? 'error' : 'success'" style="margin-top: 1rem;">
          {{ frozenCheckAddress }} is <strong>{{ frozenCheckResult ? 'FROZEN' : 'NOT frozen' }}</strong>.
        </div>
      </div>

      <!-- ─── MULTI-SIG: FREEZE / UNFREEZE ──────────────────────────────────── -->
      <div class="section-card">
        <h2>Multi-sig: Freeze / Unfreeze</h2>
        <p class="description">
          Freezing or unfreezing an account requires {{ contractState.threshold }} admin approval(s).
          Only one freeze proposal can be active at a time. Admin addresses cannot be frozen.
        </p>

        <!-- Active proposal -->
        <div v-if="contractState.freezeProposal" class="proposal-box">
          <h3>
            Active Proposal: {{ contractState.freezeProposal.action === 'freeze' ? 'Freeze Account' : 'Unfreeze Account' }}
          </h3>
          <p><strong>Target:</strong> {{ contractState.freezeProposal.target }}</p>
          <p><strong>Proposer:</strong> {{ contractState.freezeProposal.proposer }}</p>
          <p>
            <strong>Approvals:</strong>
            {{ contractState.freezeProposal.approvals.length }} / {{ contractState.threshold }}
          </p>
          <ul class="address-list">
            <li v-for="a in contractState.freezeProposal.approvals" :key="a">{{ a }}</li>
          </ul>

          <div class="proposal-actions">
            <button
              v-if="!contractState.freezeProposal.approvals.includes(connectedAddress)"
              @click="handleApproveFreezeProposal"
              class="btn-primary"
              :disabled="isSubmitting"
            >
              Approve
            </button>
            <span v-else class="already-approved">You have already approved</span>

            <button
              v-if="contractState.freezeProposal.proposer === connectedAddress"
              @click="handleCancelFreezeProposal"
              class="btn-secondary"
              :disabled="isSubmitting"
            >
              Cancel Proposal
            </button>
          </div>
        </div>

        <!-- Propose new freeze/unfreeze -->
        <div v-else>
          <div class="tab-bar">
            <button
              :class="freezeTab === 'freeze' ? 'tab-active' : 'tab'"
              @click="freezeTab = 'freeze'"
            >Freeze</button>
            <button
              :class="freezeTab === 'unfreeze' ? 'tab-active' : 'tab'"
              @click="freezeTab = 'unfreeze'"
            >Unfreeze</button>
          </div>

          <form @submit.prevent="freezeTab === 'freeze' ? handleProposeFreeze() : handleProposeUnfreeze()" class="operation-form">
            <div class="form-group">
              <label>{{ freezeTab === 'freeze' ? 'Account to Freeze' : 'Account to Unfreeze' }}</label>
              <input
                v-model="freezeTargetAddress"
                type="text"
                placeholder="GABC..."
                class="input-field"
                :disabled="isSubmitting"
                required
              />
              <small class="hint" v-if="freezeTab === 'freeze'">
                Cannot freeze admin addresses. Account must not already be frozen.
              </small>
              <small class="hint" v-else>
                Account must currently be frozen.
              </small>
            </div>
            <button
              type="submit"
              class="btn-primary"
              :disabled="isSubmitting || !isValidStellarAddress(freezeTargetAddress)"
            >
              <span v-if="freezeTab === 'freeze'">Propose Freeze</span>
              <span v-else>Propose Unfreeze</span>
            </button>
          </form>
        </div>
      </div>

      <!-- ─── MULTI-SIG: SEIZURE / EMBARGO ──────────────────────────────────── -->
      <div class="section-card section-danger">
        <h2>Multi-sig: Seizure / Embargo</h2>
        <p class="description">
          Confiscate tokens from a frozen account and transfer them to a destination address.
          Requires {{ contractState.threshold }} admin approval(s). The target must be frozen first.
        </p>

        <!-- Active proposal -->
        <div v-if="contractState.seizureProposal" class="proposal-box">
          <h3>Active Seizure Proposal</h3>
          <p><strong>Target (frozen):</strong> {{ contractState.seizureProposal.target }}</p>
          <p><strong>Destination:</strong> {{ contractState.seizureProposal.destination }}</p>
          <p><strong>Amount (raw):</strong> {{ contractState.seizureProposal.amount }}</p>
          <p><strong>Proposer:</strong> {{ contractState.seizureProposal.proposer }}</p>
          <p>
            <strong>Approvals:</strong>
            {{ contractState.seizureProposal.approvals.length }} / {{ contractState.threshold }}
          </p>
          <ul class="address-list">
            <li v-for="a in contractState.seizureProposal.approvals" :key="a">{{ a }}</li>
          </ul>

          <div class="proposal-actions">
            <button
              v-if="!contractState.seizureProposal.approvals.includes(connectedAddress)"
              @click="handleApproveSeizure"
              class="btn-danger"
              :disabled="isSubmitting"
            >
              Approve Seizure
            </button>
            <span v-else class="already-approved">You have already approved</span>

            <button
              v-if="contractState.seizureProposal.proposer === connectedAddress"
              @click="handleCancelSeizure"
              class="btn-secondary"
              :disabled="isSubmitting"
            >
              Cancel Proposal
            </button>
          </div>
        </div>

        <!-- Propose new seizure -->
        <div v-else>
          <form @submit.prevent="handleProposeSeizure" class="operation-form">
            <div class="form-group">
              <label>Target Account (must be frozen)</label>
              <input
                v-model="seizureTargetAddress"
                type="text"
                placeholder="GABC..."
                class="input-field"
                :disabled="isSubmitting"
                required
              />
            </div>
            <div class="form-group">
              <label>Destination Address</label>
              <input
                v-model="seizureDestinationAddress"
                type="text"
                placeholder="GABC..."
                class="input-field"
                :disabled="isSubmitting"
                required
              />
              <small class="hint">Address that will receive the seized tokens. Cannot be the target.</small>
            </div>
            <div class="form-group">
              <label>Amount</label>
              <input
                v-model="seizureAmount"
                type="number"
                min="0"
                step="any"
                placeholder="100.0"
                class="input-field"
                :disabled="isSubmitting"
                required
              />
              <small class="hint">Amount in display units (e.g. 100 = 100 tokens). Must not exceed target balance.</small>
            </div>
            <button
              type="submit"
              class="btn-danger"
              :disabled="isSubmitting || !isValidStellarAddress(seizureTargetAddress) || !isValidStellarAddress(seizureDestinationAddress) || !seizureAmount"
            >
              Propose Seizure
            </button>
          </form>
        </div>
      </div>

    </div><!-- end .content -->
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { lunarxyAdminService } from '@/services/stellar/LunarxyAdminService'
import type { LunarxyContractState } from '@/services/stellar/StellarTypes'

// ─── Reactive state ────────────────────────────────────────────────────────────

const isConnected     = ref(false)
const isConnecting    = ref(false)
const isSubmitting    = ref(false)
const isLoadingState  = ref(false)
const isProcessingTx  = ref(false)
const processingMessage = ref('')
const successMessage  = ref('')
const errorMessage    = ref('')
const connectedAddress = ref('')

// Form fields — single-admin
const mintTo       = ref('')
const mintAmount   = ref<number | null>(null)
const signerKeyHex = ref('')

// Form fields — multi-sig upgrade
const upgradeWasmHash = ref('')

// Form fields — multi-sig admins
const adminTab          = ref<'add' | 'remove'>('add')
const adminTargetAddress = ref('')

// Form fields — multi-sig threshold
const newThreshold = ref(1)

// Form fields — freeze / unfreeze
const freezeTab          = ref<'freeze' | 'unfreeze'>('freeze')
const freezeTargetAddress = ref('')

// Form fields — seizure
const seizureTargetAddress      = ref('')
const seizureDestinationAddress = ref('')
const seizureAmount             = ref<number | null>(null)

// Frozen check
const frozenCheckAddress = ref('')
const frozenCheckResult  = ref<boolean | null>(null)

// Contract state
const contractState = reactive<LunarxyContractState>({
  admins: [],
  threshold: 0,
  paused: false,
  version: 0,
  upgradeProposal: null,
  adminProposal: null,
  thresholdProposal: null,
  unpauseProposal: null,
  freezeProposal: null,
  seizureProposal: null,
})

// ─── Mount ─────────────────────────────────────────────────────────────────────

onMounted(async () => {
  lunarxyAdminService.initialize()
  try {
    const connection = await lunarxyAdminService.checkWalletConnection()
    if (connection) {
      isConnected.value = true
      connectedAddress.value = connection.address
      await loadContractState()
    }
  } catch (err) {
    console.debug('No existing Freighter connection', err)
  }
})

// ─── Wallet ────────────────────────────────────────────────────────────────────

const connectWallet = async () => {
  isConnecting.value = true
  errorMessage.value = ''
  try {
    const connection = await lunarxyAdminService.connectWallet()
    isConnected.value = true
    connectedAddress.value = connection.address
    await loadContractState()
  } catch (err: any) {
    errorMessage.value = err.message ?? 'Failed to connect Freighter wallet'
    isConnected.value = false
  } finally {
    isConnecting.value = false
  }
}

const disconnectWallet = () => {
  lunarxyAdminService.disconnectWallet()
  isConnected.value = false
  connectedAddress.value = ''
}

// ─── State loading ─────────────────────────────────────────────────────────────

const loadContractState = async () => {
  isLoadingState.value = true
  try {
    const state = await lunarxyAdminService.getContractState()
    Object.assign(contractState, state)
    newThreshold.value = state.threshold || 1
  } catch (err: any) {
    console.error('Error loading contract state:', err)
    errorMessage.value = 'Failed to load contract state: ' + (err.message ?? err)
  } finally {
    isLoadingState.value = false
  }
}

// ─── Helpers ───────────────────────────────────────────────────────────────────

const truncateAddress = (addr: string): string => {
  if (!addr || addr.length < 12) return addr
  return addr.slice(0, 6) + '...' + addr.slice(-4)
}

const isValidStellarAddress = (addr: string): boolean => {
  return /^G[A-Z2-7]{55}$/.test(addr)
}

const handleSuccess = async (message: string) => {
  isSubmitting.value = false
  isProcessingTx.value = false
  successMessage.value = message
  setTimeout(() => { successMessage.value = '' }, 5000)
  await loadContractState()
}

const handleError = (err: any) => {
  isSubmitting.value = false
  isProcessingTx.value = false
  errorMessage.value = err?.message ?? String(err)
  console.error(err)
}

// ─── Single-admin: Mint ────────────────────────────────────────────────────────

const handleMint = async () => {
  if (!mintAmount.value || mintAmount.value <= 0) return
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Minting tokens — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.mint(connectedAddress.value, mintTo.value, mintAmount.value)
    if (!result.success) throw new Error(result.errorMessage)
    mintTo.value = ''
    mintAmount.value = null
    await handleSuccess(`Minted successfully. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

// ─── Single-admin: Pause ───────────────────────────────────────────────────────

const handlePause = async () => {
  if (!confirm('Are you sure you want to PAUSE the contract? This will halt all token transfers.')) return
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Pausing contract — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.pause(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Contract paused. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

// ─── Single-admin: Set Signer Key ──────────────────────────────────────────────

const handleSetSignerKey = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Setting signer key — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.setSignerKey(connectedAddress.value, signerKeyHex.value)
    if (!result.success) throw new Error(result.errorMessage)
    signerKeyHex.value = ''
    await handleSuccess(`Signer key updated. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

// ─── Multi-sig: Unpause ────────────────────────────────────────────────────────

const handleProposeUnpause = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Proposing unpause — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.proposeUnpause(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Unpause proposed. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleApproveUnpause = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Approving unpause — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.approveUnpause(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Unpause approved. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleCancelUnpause = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Cancelling unpause proposal — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.cancelUnpause(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Unpause proposal cancelled. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

// ─── Multi-sig: Upgrade ────────────────────────────────────────────────────────

const handleProposeUpgrade = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Proposing upgrade — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.proposeUpgrade(connectedAddress.value, upgradeWasmHash.value)
    if (!result.success) throw new Error(result.errorMessage)
    upgradeWasmHash.value = ''
    await handleSuccess(`Upgrade proposed. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleApproveUpgrade = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Approving upgrade — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.approveUpgrade(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Upgrade approved. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleCancelUpgrade = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Cancelling upgrade proposal — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.cancelUpgrade(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Upgrade proposal cancelled. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

// ─── Multi-sig: Admin Management ──────────────────────────────────────────────

const handleProposeAddAdmin = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Proposing add admin — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.proposeAddAdmin(connectedAddress.value, adminTargetAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    adminTargetAddress.value = ''
    await handleSuccess(`Add admin proposed. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleProposeRemoveAdmin = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Proposing remove admin — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.proposeRemoveAdmin(connectedAddress.value, adminTargetAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    adminTargetAddress.value = ''
    await handleSuccess(`Remove admin proposed. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleApproveAdminProposal = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Approving admin proposal — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.approveAdminProposal(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Admin proposal approved. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleCancelAdminProposal = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Cancelling admin proposal — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.cancelAdminProposal(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Admin proposal cancelled. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

// ─── Multi-sig: Threshold ──────────────────────────────────────────────────────

const handleProposeChangeThreshold = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Proposing threshold change — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.proposeChangeThreshold(connectedAddress.value, newThreshold.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Threshold change proposed. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleApproveThresholdProposal = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Approving threshold proposal — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.approveThresholdProposal(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Threshold proposal approved. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleCancelThresholdProposal = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Cancelling threshold proposal — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.cancelThresholdProposal(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Threshold proposal cancelled. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

// ─── Frozen status check ───────────────────────────────────────────────────────

const handleCheckFrozen = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  frozenCheckResult.value = null
  try {
    const frozen = await lunarxyAdminService.isFrozen(frozenCheckAddress.value)
    frozenCheckResult.value = frozen
  } catch (err) {
    handleError(err)
  }
}

// ─── Multi-sig: Freeze / Unfreeze ──────────────────────────────────────────────

const handleProposeFreeze = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Validating freeze request...'
  try {
    // Pre-flight: fetch fresh admin list
    const admins = await lunarxyAdminService.getAdmins()

    // Pre-flight: proposer must be an admin
    if (!admins.includes(connectedAddress.value)) {
      throw new Error('You are not an admin. Only admins can propose a freeze.')
    }

    // Pre-flight: target cannot be an admin
    if (admins.includes(freezeTargetAddress.value)) {
      throw new Error('Cannot freeze an admin address.')
    }

    // Pre-flight: check if target is already frozen
    const frozen = await lunarxyAdminService.isFrozen(freezeTargetAddress.value)
    if (frozen) {
      throw new Error('This account is already frozen.')
    }

    // Pre-flight: check if a freeze proposal is already active
    const proposal = await lunarxyAdminService.getFreezeProposal()
    if (proposal) {
      throw new Error('A freeze proposal is already active. Cancel it first.')
    }

    processingMessage.value = 'Proposing freeze — please confirm in Freighter...'
    const result = await lunarxyAdminService.proposeFreeze(connectedAddress.value, freezeTargetAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    freezeTargetAddress.value = ''
    await handleSuccess(`Freeze proposed. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleProposeUnfreeze = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Proposing unfreeze — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.proposeUnfreeze(connectedAddress.value, freezeTargetAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    freezeTargetAddress.value = ''
    await handleSuccess(`Unfreeze proposed. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleApproveFreezeProposal = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Approving freeze proposal — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.approveFreezeProposal(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Freeze proposal approved. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleCancelFreezeProposal = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Cancelling freeze proposal — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.cancelFreezeProposal(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Freeze proposal cancelled. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

// ─── Multi-sig: Seizure / Embargo ──────────────────────────────────────────────

const handleProposeSeizure = async () => {
  if (!seizureAmount.value || seizureAmount.value <= 0) return
  if (!confirm('Are you sure you want to propose a SEIZURE? This will confiscate tokens from the frozen account.')) return
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Proposing seizure — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.proposeSeizure(
      connectedAddress.value,
      seizureTargetAddress.value,
      seizureDestinationAddress.value,
      seizureAmount.value,
    )
    if (!result.success) throw new Error(result.errorMessage)
    seizureTargetAddress.value = ''
    seizureDestinationAddress.value = ''
    seizureAmount.value = null
    await handleSuccess(`Seizure proposed. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleApproveSeizure = async () => {
  if (!confirm('Are you sure you want to approve this seizure? This action is irreversible once threshold is met.')) return
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Approving seizure — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.approveSeizure(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Seizure approved. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleCancelSeizure = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Cancelling seizure proposal — please confirm in Freighter...'
  try {
    const result = await lunarxyAdminService.cancelSeizure(connectedAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    await handleSuccess(`Seizure proposal cancelled. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}
</script>

<style scoped>
/* ─── Layout ─────────────────────────────────────────────────────────────────── */
.lunarxy-governance-container {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
  font-family: inherit;
  color: #333;
}

.header {
  margin-bottom: 2rem;
}
.header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}
.subtitle {
  color: #666;
  font-size: 0.95rem;
}

/* ─── Wallet connection warning ──────────────────────────────────────────────── */
.connection-warning {
  background: #fff8e1;
  border: 1px solid #ffecb3;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
}
.connection-warning p {
  margin-bottom: 1rem;
  color: #795548;
}
.btn-connect {
  background: #1565c0;
  color: #fff;
  border: none;
  padding: 0.7rem 1.6rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
}
.btn-connect:hover:not(:disabled) { background: #0d47a1; }
.btn-connect:disabled { opacity: 0.6; cursor: not-allowed; }

/* ─── Connected bar ───────────────────────────────────────────────────────────── */
.connected-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #e8f5e9;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.wallet-address {
  font-family: monospace;
  font-size: 0.85rem;
  flex: 1;
}
.btn-disconnect {
  background: transparent;
  border: 1px solid #e53935;
  color: #e53935;
  padding: 0.35rem 0.9rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-disconnect:hover { background: #ffebee; }

/* ─── Cards ───────────────────────────────────────────────────────────────────── */
.section-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.section-card h2 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.section-danger {
  border-color: #ef9a9a;
  background: #fff8f8;
}
.description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

/* ─── State panel ─────────────────────────────────────────────────────────────── */
.state-panel { background: #f5f7fa; }
.state-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.state-item { display: flex; flex-direction: column; gap: 0.25rem; }
.full-width { grid-column: 1 / -1; }
.state-label { font-size: 0.78rem; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }
.state-value { font-size: 0.95rem; font-weight: 500; }
.loading-inline { color: #888; font-size: 0.9rem; }

/* ─── Badges ──────────────────────────────────────────────────────────────────── */
.badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.05em;
}
.badge-success { background: #e8f5e9; color: #2e7d32; }
.badge-danger  { background: #ffebee; color: #c62828; }
.badge-warning { background: #fff8e1; color: #f57f17; }

.proposal-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.proposal-detail { font-size: 0.82rem; color: #555; }

/* ─── Address list ────────────────────────────────────────────────────────────── */
.address-list {
  list-style: none;
  padding: 0;
  margin: 0.25rem 0 0;
}
.address-item, .address-list li {
  font-family: monospace;
  font-size: 0.8rem;
  color: #444;
  padding: 0.15rem 0;
  word-break: break-all;
}
.address-me { color: #1565c0; font-weight: 600; }

/* ─── Proposal box ────────────────────────────────────────────────────────────── */
.proposal-box {
  background: #fffde7;
  border: 1px solid #fff176;
  border-radius: 8px;
  padding: 1rem;
}
.proposal-box h3 { font-size: 1rem; margin-bottom: 0.5rem; }
.proposal-box p { font-size: 0.88rem; margin: 0.2rem 0; }
.proposal-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  flex-wrap: wrap;
  align-items: center;
}
.already-approved { font-size: 0.85rem; color: #888; font-style: italic; }

/* ─── Tabs ────────────────────────────────────────────────────────────────────── */
.tab-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.tab, .tab-active {
  padding: 0.4rem 1rem;
  border-radius: 6px;
  border: 1px solid #bdbdbd;
  cursor: pointer;
  font-size: 0.9rem;
  background: #f5f5f5;
  color: #444;
  transition: background 0.15s;
}
.tab-active {
  background: #1565c0;
  color: #fff;
  border-color: #1565c0;
}
.tab:hover:not(.tab-active) { background: #e3f2fd; }

/* ─── Forms ───────────────────────────────────────────────────────────────────── */
.operation-form { display: flex; flex-direction: column; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.form-group label { font-size: 0.88rem; font-weight: 500; color: #444; }
.input-field {
  padding: 0.55rem 0.75rem;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  font-size: 0.95rem;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.15s;
}
.input-field:focus { outline: none; border-color: #1565c0; }
.input-field:disabled { background: #f5f5f5; color: #9e9e9e; }
.hint { font-size: 0.78rem; color: #888; }

/* ─── Buttons ─────────────────────────────────────────────────────────────────── */
.btn-primary {
  background: #1565c0;
  color: #fff;
  border: none;
  padding: 0.6rem 1.4rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  align-self: flex-start;
}
.btn-primary:hover:not(:disabled) { background: #0d47a1; }
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }

.btn-secondary {
  background: #fff;
  color: #1565c0;
  border: 1px solid #1565c0;
  padding: 0.6rem 1.4rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  align-self: flex-start;
}
.btn-secondary:hover:not(:disabled) { background: #e3f2fd; }
.btn-secondary:disabled { opacity: 0.55; cursor: not-allowed; }

.btn-danger {
  background: #c62828;
  color: #fff;
  border: none;
  padding: 0.6rem 1.6rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
}
.btn-danger:hover:not(:disabled) { background: #b71c1c; }
.btn-danger:disabled { opacity: 0.55; cursor: not-allowed; }

/* ─── Messages ────────────────────────────────────────────────────────────────── */
.message {
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
.message.success { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
.message.error   { background: #ffebee; color: #c62828; border: 1px solid #ef9a9a; }
.message.warning { background: #fff8e1; color: #f57f17; border: 1px solid #ffe082; }

/* ─── Loading overlay ─────────────────────────────────────────────────────────── */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.loading-modal {
  background: #fff;
  border-radius: 12px;
  padding: 2rem 3rem;
  text-align: center;
  max-width: 380px;
  width: 90%;
}
.loading-modal h3 { margin: 1rem 0 0.5rem; font-size: 1.1rem; }
.loading-modal p  { color: #666; font-size: 0.88rem; }
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top-color: #1565c0;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ─── code ────────────────────────────────────────────────────────────────────── */
code {
  font-family: monospace;
  font-size: 0.82rem;
  background: #f5f5f5;
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  word-break: break-all;
}
</style>
