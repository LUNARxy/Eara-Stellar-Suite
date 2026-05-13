<template>
  <div class="compliantid-governance-container">

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
      <h1>Compliant-ID Registry — Stellar Admin</h1>
      <p class="subtitle">
        Manage the Compliant-ID identity registry on the Soroban contract via Freighter wallet.
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
          <div class="state-item full-width">
            <span class="state-label">Admin</span>
            <span class="state-value monospace">
              {{ contractState.admin || '(not loaded)' }}
              <em v-if="contractState.admin === connectedAddress" class="address-me"> (you)</em>
            </span>
          </div>
          <div class="state-item full-width">
            <span class="state-label">Trusted Issuers ({{ contractState.trustedIssuers.length }})</span>
            <ul v-if="contractState.trustedIssuers.length" class="address-list">
              <li v-for="issuer in contractState.trustedIssuers" :key="issuer" class="address-item">
                <span :class="issuer === connectedAddress ? 'address-me' : ''">
                  {{ issuer }}
                  <em v-if="issuer === connectedAddress"> (you)</em>
                </span>
              </li>
            </ul>
            <span v-else class="state-value">None</span>
          </div>
          <div class="state-item full-width">
            <span class="state-label">Restricted Countries ({{ contractState.restrictedCountries.length }})</span>
            <div v-if="contractState.restrictedCountries.length" class="country-list">
              <span
                v-for="cc in contractState.restrictedCountries"
                :key="cc"
                class="badge badge-danger"
              >{{ cc }}</span>
            </div>
            <span v-else class="state-value">None</span>
          </div>
        </div>
      </div>

      <!-- ─── ADMIN: Trusted Issuer Management ─────────────────────────────── -->
      <div class="section-card">
        <h2>Trusted Issuer Management</h2>
        <p class="description">
          Add or remove trusted issuers who can create and manage user compliance records.
          Only the contract admin can perform these operations.
        </p>

        <div class="tab-bar">
          <button
            :class="issuerTab === 'add' ? 'tab-active' : 'tab'"
            @click="issuerTab = 'add'"
          >Add Issuer</button>
          <button
            :class="issuerTab === 'remove' ? 'tab-active' : 'tab'"
            @click="issuerTab = 'remove'"
          >Remove Issuer</button>
        </div>

        <form @submit.prevent="issuerTab === 'add' ? handleAddTrustedIssuer() : handleRemoveTrustedIssuer()" class="operation-form">
          <div class="form-group">
            <label>{{ issuerTab === 'add' ? 'New Issuer Address' : 'Issuer Address to Remove' }}</label>
            <input
              v-model="issuerTargetAddress"
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
            :disabled="isSubmitting || !isValidStellarAddress(issuerTargetAddress)"
          >
            <span v-if="isSubmitting">Processing...</span>
            <span v-else-if="issuerTab === 'add'">Add Trusted Issuer</span>
            <span v-else>Remove Trusted Issuer</span>
          </button>
        </form>
      </div>

      <!-- ─── ADMIN: Country Restriction Management ────────────────────────── -->
      <div class="section-card">
        <h2>Country Restriction Management</h2>
        <p class="description">
          Add or remove country codes from the restricted list. Users from restricted countries
          will fail the <code>check_compliance_with_country</code> check.
          Only the contract admin can perform these operations.
        </p>

        <div class="tab-bar">
          <button
            :class="countryTab === 'add' ? 'tab-active' : 'tab'"
            @click="countryTab = 'add'"
          >Restrict Country</button>
          <button
            :class="countryTab === 'remove' ? 'tab-active' : 'tab'"
            @click="countryTab = 'remove'"
          >Remove Restriction</button>
        </div>

        <form @submit.prevent="countryTab === 'add' ? handleAddRestrictedCountry() : handleRemoveRestrictedCountry()" class="operation-form">
          <div class="form-group">
            <label>Country Code (ISO 3166-1 alpha-2)</label>
            <input
              v-model="countryCodeInput"
              type="text"
              placeholder="US"
              class="input-field"
              :disabled="isSubmitting"
              required
              maxlength="4"
              style="width: 120px;"
            />
            <small class="hint">
              Enter a 2-letter ISO country code (e.g. US, KP, IR).
            </small>
          </div>
          <button
            type="submit"
            class="btn-primary"
            :disabled="isSubmitting || countryCodeInput.trim().length < 2"
          >
            <span v-if="isSubmitting">Processing...</span>
            <span v-else-if="countryTab === 'add'">Add Restricted Country</span>
            <span v-else>Remove Restricted Country</span>
          </button>
        </form>
      </div>

      <!-- ─── ISSUER: Set Compliance Record ────────────────────────────────── -->
      <div class="section-card">
        <h2>Set Compliance Record</h2>
        <p class="description">
          Create or update a user's compliance record. This operation can only be performed
          by a trusted issuer registered in the contract.
        </p>
        <form @submit.prevent="handleSetCompliance" class="operation-form">
          <div class="form-group">
            <label>User Address (Stellar G...)</label>
            <input
              v-model="complianceUserAddress"
              type="text"
              placeholder="GABC..."
              class="input-field"
              :disabled="isSubmitting"
              required
            />
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="complianceStatus" class="input-field" :disabled="isSubmitting">
              <option value="Verified">Verified</option>
              <option value="Suspended">Suspended</option>
              <option value="Revoked">Revoked</option>
              <option value="Unverified">Unverified</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Level (min 1)</label>
              <input
                v-model.number="complianceLevel"
                type="number"
                min="1"
                placeholder="1"
                class="input-field"
                :disabled="isSubmitting"
                required
              />
            </div>
            <div class="form-group">
              <label>Country Code</label>
              <input
                v-model="complianceCountryCode"
                type="text"
                placeholder="US"
                class="input-field"
                :disabled="isSubmitting"
                required
                maxlength="4"
                style="width: 120px;"
              />
            </div>
          </div>
          <div class="form-group">
            <label>Expiration Date</label>
            <input
              v-model="complianceExpiresDate"
              type="datetime-local"
              class="input-field"
              :disabled="isSubmitting"
              required
            />
            <small class="hint">
              The compliance record will expire after this date. Must be in the future.
            </small>
          </div>
          <button
            type="submit"
            class="btn-primary"
            :disabled="isSubmitting || !isValidStellarAddress(complianceUserAddress) || complianceLevel < 1 || !complianceCountryCode || !complianceExpiresDate"
          >
            <span v-if="isSubmitting">Processing...</span>
            <span v-else>Set Compliance</span>
          </button>
        </form>
      </div>

      <!-- ─── ISSUER: Suspend / Revoke User ────────────────────────────────── -->
      <div class="section-card section-danger">
        <h2>Suspend / Revoke User</h2>
        <p class="description">
          Quick actions to suspend or revoke a user's compliance status.
          Suspending preserves the record but marks it inactive. Revoking is terminal.
          Only trusted issuers can perform these operations.
        </p>

        <div class="tab-bar">
          <button
            :class="suspendRevokeTab === 'suspend' ? 'tab-active' : 'tab'"
            @click="suspendRevokeTab = 'suspend'"
          >Suspend</button>
          <button
            :class="suspendRevokeTab === 'revoke' ? 'tab-active' : 'tab'"
            @click="suspendRevokeTab = 'revoke'"
          >Revoke</button>
        </div>

        <form @submit.prevent="suspendRevokeTab === 'suspend' ? handleSuspendUser() : handleRevokeUser()" class="operation-form">
          <div class="form-group">
            <label>User Address</label>
            <input
              v-model="suspendRevokeAddress"
              type="text"
              placeholder="GABC..."
              class="input-field"
              :disabled="isSubmitting"
              required
            />
          </div>
          <button
            type="submit"
            :class="suspendRevokeTab === 'revoke' ? 'btn-danger' : 'btn-primary'"
            :disabled="isSubmitting || !isValidStellarAddress(suspendRevokeAddress)"
          >
            <span v-if="isSubmitting">Processing...</span>
            <span v-else-if="suspendRevokeTab === 'suspend'">Suspend User</span>
            <span v-else>Revoke User</span>
          </button>
        </form>
      </div>

      <!-- ─── QUERY: Check Compliance ──────────────────────────────────────── -->
      <div class="section-card">
        <h2>Check Compliance</h2>
        <p class="description">
          Query whether a user is compliant at a given minimum level. Optionally checks
          country restrictions.
        </p>
        <form @submit.prevent="handleCheckCompliance" class="operation-form">
          <div class="form-group">
            <label>User Address</label>
            <input
              v-model="checkComplianceAddress"
              type="text"
              placeholder="GABC..."
              class="input-field"
              :disabled="isSubmitting"
              required
            />
          </div>
          <div class="form-group">
            <label>Minimum Level</label>
            <input
              v-model.number="checkComplianceMinLevel"
              type="number"
              min="1"
              placeholder="1"
              class="input-field"
              :disabled="isSubmitting"
              required
            />
          </div>
          <div class="form-row">
            <button
              type="submit"
              class="btn-secondary"
              :disabled="isSubmitting || !isValidStellarAddress(checkComplianceAddress) || checkComplianceMinLevel < 1"
            >
              Check (basic)
            </button>
            <button
              type="button"
              @click="handleCheckComplianceWithCountry"
              class="btn-secondary"
              :disabled="isSubmitting || !isValidStellarAddress(checkComplianceAddress) || checkComplianceMinLevel < 1"
            >
              Check (with country)
            </button>
          </div>
        </form>
        <div v-if="complianceCheckResult !== null" class="message" :class="complianceCheckResult ? 'success' : 'error'" style="margin-top: 1rem;">
          {{ checkComplianceAddress }} is
          <strong>{{ complianceCheckResult ? 'COMPLIANT' : 'NOT COMPLIANT' }}</strong>
          at level {{ checkComplianceMinLevel }}{{ complianceCheckMode === 'country' ? ' (with country check)' : '' }}.
        </div>
      </div>

      <!-- ─── QUERY: Lookup Compliance Record ──────────────────────────────── -->
      <div class="section-card">
        <h2>Lookup Compliance Record</h2>
        <p class="description">
          Retrieve the full compliance record for a user address.
        </p>
        <form @submit.prevent="handleLookupCompliance" class="operation-form">
          <div class="form-group">
            <label>User Address</label>
            <input
              v-model="lookupAddress"
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
            :disabled="isSubmitting || !isValidStellarAddress(lookupAddress)"
          >
            Lookup Record
          </button>
        </form>
        <div v-if="lookupResult" class="record-box" style="margin-top: 1rem;">
          <h3>Compliance Record</h3>
          <div class="record-grid">
            <div class="record-item">
              <span class="state-label">Status</span>
              <span :class="'badge badge-' + statusBadgeClass(lookupResult.status)">
                {{ lookupResult.status }}
              </span>
            </div>
            <div class="record-item">
              <span class="state-label">Level</span>
              <span class="state-value">{{ lookupResult.level }}</span>
            </div>
            <div class="record-item">
              <span class="state-label">Country</span>
              <span class="state-value">{{ lookupResult.countryCode }}</span>
            </div>
            <div class="record-item">
              <span class="state-label">Expires</span>
              <span class="state-value">{{ formatTimestamp(lookupResult.expiresAt) }}</span>
            </div>
            <div class="record-item full-width">
              <span class="state-label">Issuer</span>
              <span class="state-value monospace">{{ lookupResult.issuer }}</span>
            </div>
          </div>
        </div>
        <div v-if="lookupNotFound" class="message warning" style="margin-top: 1rem;">
          No compliance record found for {{ lookupAddress }}.
        </div>
      </div>

      <!-- ─── QUERY: Check Trusted Issuer ──────────────────────────────────── -->
      <div class="section-card">
        <h2>Check Trusted Issuer</h2>
        <p class="description">
          Verify whether an address is registered as a trusted issuer.
        </p>
        <form @submit.prevent="handleCheckTrustedIssuer" class="operation-form">
          <div class="form-group">
            <label>Address</label>
            <input
              v-model="checkIssuerAddress"
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
            :disabled="isSubmitting || !isValidStellarAddress(checkIssuerAddress)"
          >
            Check Issuer
          </button>
        </form>
        <div v-if="issuerCheckResult !== null" class="message" :class="issuerCheckResult ? 'success' : 'error'" style="margin-top: 1rem;">
          {{ checkIssuerAddress }} is <strong>{{ issuerCheckResult ? 'a trusted issuer' : 'NOT a trusted issuer' }}</strong>.
        </div>
      </div>

      <!-- ─── QUERY: Check Country Restriction ─────────────────────────────── -->
      <div class="section-card">
        <h2>Check Country Restriction</h2>
        <p class="description">
          Verify whether a country code is currently restricted.
        </p>
        <form @submit.prevent="handleCheckCountryRestricted" class="operation-form">
          <div class="form-group">
            <label>Country Code</label>
            <input
              v-model="checkCountryCode"
              type="text"
              placeholder="US"
              class="input-field"
              :disabled="isSubmitting"
              maxlength="4"
              style="width: 120px;"
              required
            />
          </div>
          <button
            type="submit"
            class="btn-secondary"
            :disabled="isSubmitting || checkCountryCode.trim().length < 2"
          >
            Check Country
          </button>
        </form>
        <div v-if="countryCheckResult !== null" class="message" :class="countryCheckResult ? 'error' : 'success'" style="margin-top: 1rem;">
          {{ checkCountryCode }} is <strong>{{ countryCheckResult ? 'RESTRICTED' : 'NOT restricted' }}</strong>.
        </div>
      </div>

    </div><!-- end .content -->
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { compliantIdService } from '@/services/stellar/CompliantIdService'
import type { CompliantIdContractState, UserComplianceRecord, ComplianceStatus } from '@/services/stellar/StellarTypes'

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

// Form fields — Trusted Issuer Management
const issuerTab          = ref<'add' | 'remove'>('add')
const issuerTargetAddress = ref('')

// Form fields — Country Restriction Management
const countryTab      = ref<'add' | 'remove'>('add')
const countryCodeInput = ref('')

// Form fields — Set Compliance
const complianceUserAddress  = ref('')
const complianceStatus       = ref<ComplianceStatus>('Verified')
const complianceLevel        = ref(1)
const complianceCountryCode  = ref('')
const complianceExpiresDate  = ref('')

// Form fields — Suspend / Revoke
const suspendRevokeTab     = ref<'suspend' | 'revoke'>('suspend')
const suspendRevokeAddress = ref('')

// Query — Check Compliance
const checkComplianceAddress  = ref('')
const checkComplianceMinLevel = ref(1)
const complianceCheckResult   = ref<boolean | null>(null)
const complianceCheckMode     = ref<'basic' | 'country'>('basic')

// Query — Lookup Record
const lookupAddress  = ref('')
const lookupResult   = ref<UserComplianceRecord | null>(null)
const lookupNotFound = ref(false)

// Query — Check Trusted Issuer
const checkIssuerAddress = ref('')
const issuerCheckResult  = ref<boolean | null>(null)

// Query — Check Country Restriction
const checkCountryCode   = ref('')
const countryCheckResult = ref<boolean | null>(null)

// Contract state
const contractState = reactive<CompliantIdContractState>({
  admin: '',
  trustedIssuers: [],
  restrictedCountries: [],
})

// ─── Mount ─────────────────────────────────────────────────────────────────────

onMounted(async () => {
  compliantIdService.initialize()
  try {
    const connection = await compliantIdService.checkWalletConnection()
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
    const connection = await compliantIdService.connectWallet()
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
  compliantIdService.disconnectWallet()
  isConnected.value = false
  connectedAddress.value = ''
}

// ─── State loading ─────────────────────────────────────────────────────────────

const loadContractState = async () => {
  isLoadingState.value = true
  try {
    const state = await compliantIdService.getContractState()
    Object.assign(contractState, state)
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

const statusBadgeClass = (status: ComplianceStatus): string => {
  switch (status) {
    case 'Verified': return 'success'
    case 'Suspended': return 'warning'
    case 'Revoked': return 'danger'
    default: return 'secondary'
  }
}

const formatTimestamp = (ts: number): string => {
  if (!ts) return 'N/A'
  try {
    return new Date(ts * 1000).toLocaleString()
  } catch {
    return String(ts)
  }
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

// ─── Admin: Trusted Issuer Management ──────────────────────────────────────────

const handleAddTrustedIssuer = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Adding trusted issuer — please confirm in Freighter...'
  try {
    const result = await compliantIdService.addTrustedIssuer(connectedAddress.value, issuerTargetAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    issuerTargetAddress.value = ''
    await handleSuccess(`Trusted issuer added. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleRemoveTrustedIssuer = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Removing trusted issuer — please confirm in Freighter...'
  try {
    const result = await compliantIdService.removeTrustedIssuer(connectedAddress.value, issuerTargetAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    issuerTargetAddress.value = ''
    await handleSuccess(`Trusted issuer removed. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

// ─── Admin: Country Restriction Management ─────────────────────────────────────

const handleAddRestrictedCountry = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Adding restricted country — please confirm in Freighter...'
  try {
    const cc = countryCodeInput.value.trim().toUpperCase()
    const result = await compliantIdService.addRestrictedCountry(connectedAddress.value, cc)
    if (!result.success) throw new Error(result.errorMessage)
    countryCodeInput.value = ''
    await handleSuccess(`Country ${cc} restricted. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleRemoveRestrictedCountry = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Removing country restriction — please confirm in Freighter...'
  try {
    const cc = countryCodeInput.value.trim().toUpperCase()
    const result = await compliantIdService.removeRestrictedCountry(connectedAddress.value, cc)
    if (!result.success) throw new Error(result.errorMessage)
    countryCodeInput.value = ''
    await handleSuccess(`Country ${cc} restriction removed. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

// ─── Issuer: Set Compliance ────────────────────────────────────────────────────

const handleSetCompliance = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Setting compliance record — please confirm in Freighter...'
  try {
    // Convert local date to Unix timestamp (seconds)
    const expiresAt = Math.floor(new Date(complianceExpiresDate.value).getTime() / 1000)
    if (expiresAt <= Math.floor(Date.now() / 1000)) {
      throw new Error('Expiration date must be in the future')
    }
    const cc = complianceCountryCode.value.trim().toUpperCase()
    const result = await compliantIdService.setCompliance(
      connectedAddress.value,
      complianceUserAddress.value,
      complianceStatus.value,
      complianceLevel.value,
      expiresAt,
      cc,
    )
    if (!result.success) throw new Error(result.errorMessage)
    complianceUserAddress.value = ''
    complianceExpiresDate.value = ''
    await handleSuccess(`Compliance record set. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

// ─── Issuer: Suspend / Revoke ──────────────────────────────────────────────────

const handleSuspendUser = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  // Pre-flight: suspend_user requires the caller to be a registered trusted issuer.
  const isTrusted = await compliantIdService.isTrustedIssuer(connectedAddress.value)
  if (!isTrusted) {
    errorMessage.value = 'Tu wallet no está registrada como trusted issuer en el contrato. Debes añadirla como trusted issuer antes de realizar esta operación.'
    return
  }
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Suspending user — please confirm in Freighter...'
  try {
    const result = await compliantIdService.suspendUser(connectedAddress.value, suspendRevokeAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    suspendRevokeAddress.value = ''
    await handleSuccess(`User suspended. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

const handleRevokeUser = async () => {
  if (!confirm('Are you sure you want to REVOKE this user? This action is terminal — the user cannot be reactivated.')) return
  errorMessage.value = ''
  successMessage.value = ''
  // Pre-flight: revoke_user requires the caller to be a registered trusted issuer.
  const isTrusted = await compliantIdService.isTrustedIssuer(connectedAddress.value)
  if (!isTrusted) {
    errorMessage.value = 'Tu wallet no está registrada como trusted issuer en el contrato. Debes añadirla como trusted issuer antes de realizar esta operación.'
    return
  }
  isSubmitting.value = true
  isProcessingTx.value = true
  processingMessage.value = 'Revoking user — please confirm in Freighter...'
  try {
    const result = await compliantIdService.revokeUser(connectedAddress.value, suspendRevokeAddress.value)
    if (!result.success) throw new Error(result.errorMessage)
    suspendRevokeAddress.value = ''
    await handleSuccess(`User revoked. TX: ${result.txHash}`)
  } catch (err) {
    handleError(err)
  }
}

// ─── Query: Check Compliance ───────────────────────────────────────────────────

const handleCheckCompliance = async () => {
  errorMessage.value = ''
  complianceCheckResult.value = null
  complianceCheckMode.value = 'basic'
  try {
    const result = await compliantIdService.isCompliant(checkComplianceAddress.value, checkComplianceMinLevel.value)
    complianceCheckResult.value = result
  } catch (err) {
    handleError(err)
  }
}

const handleCheckComplianceWithCountry = async () => {
  errorMessage.value = ''
  complianceCheckResult.value = null
  complianceCheckMode.value = 'country'
  try {
    const result = await compliantIdService.checkComplianceWithCountry(checkComplianceAddress.value, checkComplianceMinLevel.value)
    complianceCheckResult.value = result
  } catch (err) {
    handleError(err)
  }
}

// ─── Query: Lookup Compliance Record ───────────────────────────────────────────

const handleLookupCompliance = async () => {
  errorMessage.value = ''
  lookupResult.value = null
  lookupNotFound.value = false
  try {
    const record = await compliantIdService.getCompliance(lookupAddress.value)
    if (record) {
      lookupResult.value = record
    } else {
      lookupNotFound.value = true
    }
  } catch (err) {
    handleError(err)
  }
}

// ─── Query: Check Trusted Issuer ───────────────────────────────────────────────

const handleCheckTrustedIssuer = async () => {
  errorMessage.value = ''
  issuerCheckResult.value = null
  try {
    const result = await compliantIdService.isTrustedIssuer(checkIssuerAddress.value)
    issuerCheckResult.value = result
  } catch (err) {
    handleError(err)
  }
}

// ─── Query: Check Country Restriction ──────────────────────────────────────────

const handleCheckCountryRestricted = async () => {
  errorMessage.value = ''
  countryCheckResult.value = null
  try {
    const cc = checkCountryCode.value.trim().toUpperCase()
    const result = await compliantIdService.isCountryRestricted(cc)
    countryCheckResult.value = result
  } catch (err) {
    handleError(err)
  }
}
</script>

<style scoped>
/* ─── Layout ─────────────────────────────────────────────────────────────────── */
.compliantid-governance-container {
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
.monospace { font-family: monospace; font-size: 0.82rem; word-break: break-all; }

/* ─── Country list ────────────────────────────────────────────────────────────── */
.country-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.25rem;
}

/* ─── Record box ──────────────────────────────────────────────────────────────── */
.record-box {
  background: #f5f7fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
}
.record-box h3 { font-size: 1rem; margin-bottom: 0.75rem; }
.record-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.record-item { display: flex; flex-direction: column; gap: 0.25rem; }

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
.badge-secondary { background: #f5f5f5; color: #757575; }

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
.form-row { display: flex; gap: 1rem; flex-wrap: wrap; align-items: flex-end; }
.input-field {
  padding: 0.55rem 0.75rem;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  font-size: 0.95rem;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.15s;
}
select.input-field { cursor: pointer; }
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
