import {
  isConnected as freighterIsConnected,
  isAllowed,
  requestAccess,
  getAddress,
  signTransaction,
} from '@stellar/freighter-api'
import {
  TransactionBuilder,
  Address,
  nativeToScVal,
  scValToNative,
  xdr,
  Operation,
  rpc as StellarRpc,
} from '@stellar/stellar-sdk'
import { stellarConfig } from './StellarConfig'
import store from '../../store'
import type {
  StellarWalletConnection,
  StellarTxResult,
  CompliantIdContractState,
  UserComplianceRecord,
  ComplianceStatus,
} from './StellarTypes'

// ─── Internal helper ──────────────────────────────────────────────────────────

function makeContractCall(
  contractId: string,
  functionName: string,
  args: xdr.ScVal[],
): ReturnType<typeof Operation.invokeHostFunction> {
  return Operation.invokeHostFunction({
    func: xdr.HostFunction.hostFunctionTypeInvokeContract(
      new xdr.InvokeContractArgs({
        contractAddress: new Address(contractId).toScAddress(),
        functionName,
        args,
      }),
    ),
    auth: [],
  })
}

// ─── Service ──────────────────────────────────────────────────────────────────

class CompliantIdService {
  private rpcServer: StellarRpc.Server | null = null
  private publicKey: string | null = null

  // ─── Initialization ─────────────────────────────────────────────────────────

  initialize(): void {
    this.rpcServer = new StellarRpc.Server(stellarConfig.rpcUrl)
  }

  private getRpc(): StellarRpc.Server {
    if (!this.rpcServer) this.initialize()
    return this.rpcServer!
  }

  private getContractId(): string {
    const contractId = stellarConfig.compliantIdContractAddress
    if (!contractId) throw new Error('VUE_APP_COMPLIANT_ID_CONTRACT_ADDRESS is not configured')
    return contractId
  }

  // ─── Wallet ─────────────────────────────────────────────────────────────────

  /**
   * Get the address of the currently connected Freighter wallet.
   * Throws if Freighter is not connected. Kept for backwards compatibility
   * with ProfileKYC.vue.
   */
  async getConnectedAddress(): Promise<string> {
    const result = await getAddress()
    if (result.error || !result.address) {
      throw new Error('Freighter wallet is not connected. Please connect your wallet first.')
    }
    return result.address
  }

  async checkWalletConnection(): Promise<StellarWalletConnection | null> {
    try {
      const connectedResult = await freighterIsConnected()
      if (!connectedResult.isConnected) return null

      const allowedResult = await isAllowed()
      if (!allowedResult.isAllowed) return null

      const addressResult = await getAddress()
      if (addressResult.error || !addressResult.address) return null

      this.publicKey = addressResult.address
      store.commit('ADDRESS_CHANGED', this.publicKey)
      return { address: this.publicKey, network: stellarConfig.networkPassphrase }
    } catch {
      return null
    }
  }

  async connectWallet(): Promise<StellarWalletConnection> {
    const connectedResult = await freighterIsConnected()
    if (!connectedResult.isConnected) {
      throw new Error('Freighter wallet is not installed. Please install the Freighter browser extension.')
    }

    const accessResult = await requestAccess()
    if (accessResult.error || !accessResult.address) {
      throw new Error(accessResult.error?.message ?? 'User denied access to Freighter wallet')
    }

    this.publicKey = accessResult.address
    store.commit('ADDRESS_CHANGED', this.publicKey)
    return { address: this.publicKey, network: stellarConfig.networkPassphrase }
  }

  disconnectWallet(): void {
    this.publicKey = null
    store.commit('ADDRESS_CHANGED', null)
  }

  // ─── Core Soroban helpers ───────────────────────────────────────────────────

  /**
   * Build → simulate → assemble → sign via Freighter → submit → wait for SUCCESS.
   */
  private async callContract(
    functionName: string,
    args: xdr.ScVal[],
    callerAddress: string,
  ): Promise<StellarTxResult> {
    const rpc = this.getRpc()
    const contractId = this.getContractId()

    const account = await rpc.getAccount(callerAddress)

    const tx = new TransactionBuilder(account, {
      fee: '1000000',
      networkPassphrase: stellarConfig.networkPassphrase,
    })
      .addOperation(makeContractCall(contractId, functionName, args))
      .setTimeout(180)
      .build()

    const simResult = await rpc.simulateTransaction(tx)
    if (StellarRpc.Api.isSimulationError(simResult)) {
      throw new Error(`Simulation error (${functionName}): ${simResult.error}`)
    }

    const preparedTx = StellarRpc.assembleTransaction(tx, simResult).build()

    const signResult = await signTransaction(preparedTx.toXDR(), {
      networkPassphrase: stellarConfig.networkPassphrase,
      address: callerAddress,
    })
    if (signResult.error) {
      throw new Error(signResult.error.message ?? 'Transaction signing rejected by user')
    }

    const { TransactionBuilder: TB } = await import('@stellar/stellar-sdk')
    const signedTx = TB.fromXDR(signResult.signedTxXdr, stellarConfig.networkPassphrase)

    const sendResult = await rpc.sendTransaction(signedTx)
    if (sendResult.status === 'ERROR') {
      throw new Error(`Submission error (${functionName}): ${JSON.stringify(sendResult.errorResult)}`)
    }

    const txHash = sendResult.hash

    let getResult = await rpc.getTransaction(txHash)
    for (
      let i = 0;
      i < 40 && getResult.status === StellarRpc.Api.GetTransactionStatus.NOT_FOUND;
      i++
    ) {
      await new Promise(r => setTimeout(r, 3000))
      getResult = await rpc.getTransaction(txHash)
    }

    if (getResult.status !== StellarRpc.Api.GetTransactionStatus.SUCCESS) {
      return {
        txHash,
        success: false,
        errorMessage: `Transaction did not succeed: status=${getResult.status}`,
      }
    }

    return { txHash, success: true }
  }

  /**
   * Read-only simulation — gets the return value without signing/submitting.
   */
  private async readContract(
    functionName: string,
    args: xdr.ScVal[],
  ): Promise<xdr.ScVal | null> {
    const rpc = this.getRpc()
    const contractId = this.getContractId()

    const sourceAddress = this.publicKey
    if (!sourceAddress) throw new Error('Wallet not connected — connect Freighter before reading contract state')

    const account = await rpc.getAccount(sourceAddress)

    const tx = new TransactionBuilder(account, {
      fee: '100',
      networkPassphrase: stellarConfig.networkPassphrase,
    })
      .addOperation(makeContractCall(contractId, functionName, args))
      .setTimeout(30)
      .build()

    const simResult = await rpc.simulateTransaction(tx)
    if (StellarRpc.Api.isSimulationError(simResult)) {
      console.debug(`readContract ${functionName} simulation error:`, simResult.error)
      return null
    }

    const successSim = simResult as StellarRpc.Api.SimulateTransactionSuccessResponse
    if (!successSim.result?.retval) return null

    return successSim.result.retval
  }

  // ─── Admin operations: Trusted Issuer Management ────────────────────────────

  async addTrustedIssuer(adminAddress: string, issuerAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [
      new Address(adminAddress).toScVal(),
      new Address(issuerAddress).toScVal(),
    ]
    return this.callContract('add_trusted_issuer', args, adminAddress)
  }

  async removeTrustedIssuer(adminAddress: string, issuerAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [
      new Address(adminAddress).toScVal(),
      new Address(issuerAddress).toScVal(),
    ]
    return this.callContract('remove_trusted_issuer', args, adminAddress)
  }

  // ─── Admin operations: Country Restriction Management ───────────────────────

  async addRestrictedCountry(adminAddress: string, countryCode: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [
      new Address(adminAddress).toScVal(),
      xdr.ScVal.scvSymbol(countryCode),
    ]
    return this.callContract('add_restricted_country', args, adminAddress)
  }

  async removeRestrictedCountry(adminAddress: string, countryCode: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [
      new Address(adminAddress).toScVal(),
      xdr.ScVal.scvSymbol(countryCode),
    ]
    return this.callContract('remove_restricted_country', args, adminAddress)
  }

  // ─── Trusted Issuer operations: Compliance Records ──────────────────────────

  /**
   * set_compliance(env, issuer, user, status, level, expires_at, country_code)
   * Creates or overwrites a user's compliance record.
   */
  async setCompliance(
    issuerAddress: string,
    userAddress: string,
    status: ComplianceStatus,
    level: number,
    expiresAt: number,
    countryCode: string,
  ): Promise<StellarTxResult> {
    // Build the enum variant for ComplianceStatus
    const statusVal = this.buildComplianceStatusScVal(status)
    const args: xdr.ScVal[] = [
      new Address(issuerAddress).toScVal(),
      new Address(userAddress).toScVal(),
      statusVal,
      nativeToScVal(level, { type: 'u32' }),
      nativeToScVal(expiresAt, { type: 'u64' }),
      xdr.ScVal.scvSymbol(countryCode),
    ]
    return this.callContract('set_compliance', args, issuerAddress)
  }

  /**
   * suspend_user(env, issuer, user)
   */
  async suspendUser(issuerAddress: string, userAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [
      new Address(issuerAddress).toScVal(),
      new Address(userAddress).toScVal(),
    ]
    return this.callContract('suspend_user', args, issuerAddress)
  }

  /**
   * revoke_user(env, issuer, user)
   */
  async revokeUser(issuerAddress: string, userAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [
      new Address(issuerAddress).toScVal(),
      new Address(userAddress).toScVal(),
    ]
    return this.callContract('revoke_user', args, issuerAddress)
  }

  // ─── Query operations (read-only) ──────────────────────────────────────────

  async getAdmin(): Promise<string> {
    try {
      const retval = await this.readContract('get_admin', [])
      if (!retval) return ''
      return scValToNative(retval) as string
    } catch {
      return ''
    }
  }

  async getTrustedIssuers(): Promise<string[]> {
    try {
      const retval = await this.readContract('get_trusted_issuers', [])
      if (!retval) return []
      return scValToNative(retval) as string[]
    } catch {
      return []
    }
  }

  async getRestrictedCountries(): Promise<string[]> {
    try {
      const retval = await this.readContract('get_restricted_countries', [])
      if (!retval) return []
      return scValToNative(retval) as string[]
    } catch {
      return []
    }
  }

  async isTrustedIssuer(issuerAddress: string): Promise<boolean> {
    try {
      const args: xdr.ScVal[] = [new Address(issuerAddress).toScVal()]
      const retval = await this.readContract('is_trusted_issuer', args)
      if (!retval) return false
      return scValToNative(retval) as boolean
    } catch {
      return false
    }
  }

  async isCountryRestricted(countryCode: string): Promise<boolean> {
    try {
      const args: xdr.ScVal[] = [xdr.ScVal.scvSymbol(countryCode)]
      const retval = await this.readContract('is_country_restricted', args)
      if (!retval) return false
      return scValToNative(retval) as boolean
    } catch {
      return false
    }
  }

  async getCompliance(userAddress: string): Promise<UserComplianceRecord | null> {
    try {
      const args: xdr.ScVal[] = [new Address(userAddress).toScVal()]
      const retval = await this.readContract('get_compliance', args)
      if (!retval) return null
      const native = scValToNative(retval) as {
        status: { tag?: string } | string
        level: number
        expires_at: number | bigint
        country_code: string
        issuer: string
      }
      return {
        status: this.parseComplianceStatus(native.status),
        level: Number(native.level),
        expiresAt: Number(native.expires_at),
        countryCode: native.country_code,
        issuer: native.issuer,
      }
    } catch {
      return null
    }
  }

  async isCompliant(userAddress: string, minLevel: number): Promise<boolean> {
    try {
      const args: xdr.ScVal[] = [
        new Address(userAddress).toScVal(),
        nativeToScVal(minLevel, { type: 'u32' }),
      ]
      const retval = await this.readContract('is_compliant', args)
      if (!retval) return false
      return scValToNative(retval) as boolean
    } catch {
      return false
    }
  }

  async checkComplianceWithCountry(userAddress: string, minLevel: number): Promise<boolean> {
    try {
      const args: xdr.ScVal[] = [
        new Address(userAddress).toScVal(),
        nativeToScVal(minLevel, { type: 'u32' }),
      ]
      const retval = await this.readContract('check_compliance_with_country', args)
      if (!retval) return false
      return scValToNative(retval) as boolean
    } catch {
      return false
    }
  }

  // ─── Aggregate state read ───────────────────────────────────────────────────

  async getContractState(): Promise<CompliantIdContractState> {
    const [admin, trustedIssuers, restrictedCountries] = await Promise.allSettled([
      this.getAdmin(),
      this.getTrustedIssuers(),
      this.getRestrictedCountries(),
    ])

    return {
      admin: admin.status === 'fulfilled' ? admin.value : '',
      trustedIssuers: trustedIssuers.status === 'fulfilled' ? trustedIssuers.value : [],
      restrictedCountries: restrictedCountries.status === 'fulfilled' ? restrictedCountries.value : [],
    }
  }

  // ─── Private helpers ────────────────────────────────────────────────────────

  /**
   * Build a Soroban enum ScVal for ComplianceStatus.
   * Soroban enums are represented as UDT enums: scvVec([scvSymbol(variant)])
   */
  private buildComplianceStatusScVal(status: ComplianceStatus): xdr.ScVal {
    return xdr.ScVal.scvVec([xdr.ScVal.scvSymbol(status)])
  }

  /**
   * Parse the ComplianceStatus from scValToNative output.
   * The SDK may return it as { tag: 'Verified' } or as a plain string.
   */
  private parseComplianceStatus(raw: { tag?: string } | string): ComplianceStatus {
    let tag: string
    if (typeof raw === 'string') {
      tag = raw
    } else if (raw?.tag) {
      tag = raw.tag
    } else {
      return 'Unverified'
    }
    const normalized = tag.charAt(0).toUpperCase() + tag.slice(1).toLowerCase()
    const valid: ComplianceStatus[] = ['Unverified', 'Verified', 'Suspended', 'Revoked']
    return valid.includes(normalized as ComplianceStatus) ? (normalized as ComplianceStatus) : 'Unverified'
  }
}

// ─── Singleton ────────────────────────────────────────────────────────────────

export const compliantIdService = new CompliantIdService()
