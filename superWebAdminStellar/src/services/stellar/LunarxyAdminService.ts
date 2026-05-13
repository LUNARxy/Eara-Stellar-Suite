import {
  isConnected as freighterIsConnected,
  isAllowed,
  requestAccess,
  getAddress,
  signTransaction,
} from '@stellar/freighter-api'
import {
  Horizon,
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
  LunarxyContractState,
  UpgradeProposal,
  AdminProposal,
  ThresholdProposal,
  UnpauseProposal,
  FreezeProposal,
  SeizureProposal,
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

class LunarxyAdminService {
  private horizonServer: Horizon.Server | null = null
  private rpcServer: StellarRpc.Server | null = null
  private publicKey: string | null = null

  // ─── Initialization ─────────────────────────────────────────────────────────

  initialize(): void {
    this.horizonServer = new Horizon.Server(stellarConfig.horizonUrl)
    this.rpcServer = new StellarRpc.Server(stellarConfig.rpcUrl)
  }

  // ─── Wallet ─────────────────────────────────────────────────────────────────

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

  isWalletConnected(): boolean {
    return this.publicKey !== null
  }

  getWalletAddress(): string | null {
    return this.publicKey
  }

  // ─── Core Soroban helper ─────────────────────────────────────────────────────

  /**
   * Build → simulate → assemble → sign via Freighter → submit → wait for SUCCESS.
   */
  private async callContract(
    functionName: string,
    args: xdr.ScVal[],
    callerAddress: string,
  ): Promise<StellarTxResult> {
    if (!this.rpcServer) this.initialize()
    const rpc = this.rpcServer!

    const contractId = stellarConfig.lunarxyContractAddress
    if (!contractId) throw new Error('VUE_APP_LUNARXY_CONTRACT_ADDRESS is not configured')

    // Load account
    const account = await rpc.getAccount(callerAddress)

    // Build TX
    const tx = new TransactionBuilder(account, {
      fee: '1000000',
      networkPassphrase: stellarConfig.networkPassphrase,
    })
      .addOperation(makeContractCall(contractId, functionName, args))
      .setTimeout(180)
      .build()

    // Simulate to get resource footprint
    const simResult = await rpc.simulateTransaction(tx)
    if (StellarRpc.Api.isSimulationError(simResult)) {
      throw new Error(`Simulation error (${functionName}): ${simResult.error}`)
    }

    // Assemble with footprint + resource fees
    const preparedTx = StellarRpc.assembleTransaction(tx, simResult).build()

    // Sign via Freighter
    const signResult = await signTransaction(preparedTx.toXDR(), {
      networkPassphrase: stellarConfig.networkPassphrase,
      address: callerAddress,
    })
    if (signResult.error) {
      throw new Error(signResult.error.message ?? 'Transaction signing rejected by user')
    }

    // Reconstruct and submit
    const { TransactionBuilder: TB } = await import('@stellar/stellar-sdk')
    const signedTx = TB.fromXDR(signResult.signedTxXdr, stellarConfig.networkPassphrase)

    const sendResult = await rpc.sendTransaction(signedTx)
    if (sendResult.status === 'ERROR') {
      throw new Error(`Submission error (${functionName}): ${JSON.stringify(sendResult.errorResult)}`)
    }

    const txHash = sendResult.hash

    // Wait for on-chain confirmation
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
   * Requires wallet to be connected (needs a valid source account for the TX envelope).
   */
  private async readContract(
    functionName: string,
    args: xdr.ScVal[],
  ): Promise<xdr.ScVal | null> {
    if (!this.rpcServer) this.initialize()
    const rpc = this.rpcServer!

    const contractId = stellarConfig.lunarxyContractAddress
    if (!contractId) throw new Error('VUE_APP_LUNARXY_CONTRACT_ADDRESS is not configured')

    // A valid source account is required for the TX envelope. Use the connected wallet.
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
      // Some view functions may have no active proposal — treat as null
      console.debug(`readContract ${functionName} simulation error:`, simResult.error)
      return null
    }

    const successSim = simResult as StellarRpc.Api.SimulateTransactionSuccessResponse
    if (!successSim.result?.retval) return null

    return successSim.result.retval
  }

  // ─── Single-admin operations ─────────────────────────────────────────────────

  /**
   * mint(env, admin, to, amount)
   * Any single admin can call this. Amount is in display units (e.g. 100.5),
   * will be multiplied by 10^decimals before sending.
   */
  async mint(
    adminAddress: string,
    toAddress: string,
    displayAmount: number,
  ): Promise<StellarTxResult> {
    const rawAmount = BigInt(Math.round(displayAmount * Math.pow(10, stellarConfig.tokenDecimals)))
    const args: xdr.ScVal[] = [
      new Address(adminAddress).toScVal(),
      new Address(toAddress).toScVal(),
      nativeToScVal(rawAmount, { type: 'i128' }),
    ]
    return this.callContract('mint', args, adminAddress)
  }

  /**
   * pause(env, admin)
   * Any single admin can pause the contract immediately (emergency action).
   */
  async pause(adminAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(adminAddress).toScVal()]
    return this.callContract('pause', args, adminAddress)
  }

  /**
   * set_signer_key(env, admin, signer_key)
   * signer_key is the Ed25519 public key as a 32-byte hex string.
   */
  async setSignerKey(adminAddress: string, signerKeyHex: string): Promise<StellarTxResult> {
    const cleanHex = signerKeyHex.replace(/^0x/, '')
    if (cleanHex.length !== 64) {
      throw new Error('Signer key must be a 32-byte (64 hex chars) Ed25519 public key')
    }
    const keyBytes = new Uint8Array(cleanHex.match(/.{1,2}/g)!.map(b => parseInt(b, 16)))
    const args: xdr.ScVal[] = [
      new Address(adminAddress).toScVal(),
      nativeToScVal(keyBytes, { type: 'bytes' }),
    ]
    return this.callContract('set_signer_key', args, adminAddress)
  }

  // ─── Multi-sig: Unpause ──────────────────────────────────────────────────────

  async proposeUnpause(proposerAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(proposerAddress).toScVal()]
    return this.callContract('propose_unpause', args, proposerAddress)
  }

  async approveUnpause(approverAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(approverAddress).toScVal()]
    return this.callContract('approve_unpause', args, approverAddress)
  }

  async cancelUnpause(callerAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(callerAddress).toScVal()]
    return this.callContract('cancel_unpause', args, callerAddress)
  }

  async getUnpauseProposal(): Promise<UnpauseProposal | null> {
    try {
      const retval = await this.readContract('get_unpause_proposal', [])
      if (!retval) return null
      const native = scValToNative(retval) as { proposer: string; approvals: string[] }
      return {
        proposer: native.proposer,
        approvals: native.approvals ?? [],
      }
    } catch {
      return null
    }
  }

  // ─── Multi-sig: Upgrade ──────────────────────────────────────────────────────

  async proposeUpgrade(proposerAddress: string, wasmHashHex: string): Promise<StellarTxResult> {
    const cleanHex = wasmHashHex.replace(/^0x/, '')
    if (cleanHex.length !== 64) {
      throw new Error('WASM hash must be a 32-byte (64 hex chars) hash')
    }
    const hashBytes = new Uint8Array(cleanHex.match(/.{1,2}/g)!.map(b => parseInt(b, 16)))
    const args: xdr.ScVal[] = [
      new Address(proposerAddress).toScVal(),
      nativeToScVal(hashBytes, { type: 'bytes' }),
    ]
    return this.callContract('propose_upgrade', args, proposerAddress)
  }

  async approveUpgrade(approverAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(approverAddress).toScVal()]
    return this.callContract('approve_upgrade', args, approverAddress)
  }

  async cancelUpgrade(callerAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(callerAddress).toScVal()]
    return this.callContract('cancel_upgrade', args, callerAddress)
  }

  async getUpgradeProposal(): Promise<UpgradeProposal | null> {
    try {
      const retval = await this.readContract('get_upgrade_proposal', [])
      if (!retval) return null
      const native = scValToNative(retval) as {
        wasm_hash: Uint8Array
        proposer: string
        approvals: string[]
      }
      const hashHex = Array.from(native.wasm_hash)
        .map(b => b.toString(16).padStart(2, '0'))
        .join('')
      return {
        wasmHash: hashHex,
        proposer: native.proposer,
        approvals: native.approvals ?? [],
      }
    } catch {
      return null
    }
  }

  // ─── Multi-sig: Admin Management ─────────────────────────────────────────────

  async proposeAddAdmin(proposerAddress: string, newAdmin: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [
      new Address(proposerAddress).toScVal(),
      new Address(newAdmin).toScVal(),
    ]
    return this.callContract('propose_add_admin', args, proposerAddress)
  }

  async proposeRemoveAdmin(proposerAddress: string, adminToRemove: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [
      new Address(proposerAddress).toScVal(),
      new Address(adminToRemove).toScVal(),
    ]
    return this.callContract('propose_remove_admin', args, proposerAddress)
  }

  async approveAdminProposal(approverAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(approverAddress).toScVal()]
    return this.callContract('approve_admin_proposal', args, approverAddress)
  }

  async cancelAdminProposal(callerAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(callerAddress).toScVal()]
    return this.callContract('cancel_admin_proposal', args, callerAddress)
  }

  async getAdminProposal(): Promise<AdminProposal | null> {
    try {
      const retval = await this.readContract('get_admin_proposal', [])
      if (!retval) return null
      const native = scValToNative(retval) as {
        action: { tag: string }
        target: string
        proposer: string
        approvals: string[]
      }
      return {
        action: native.action?.tag?.toLowerCase() === 'remove' ? 'remove' : 'add',
        target: native.target,
        proposer: native.proposer,
        approvals: native.approvals ?? [],
      }
    } catch {
      return null
    }
  }

  // ─── Multi-sig: Threshold ────────────────────────────────────────────────────

  async proposeChangeThreshold(proposerAddress: string, newThreshold: number): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [
      new Address(proposerAddress).toScVal(),
      nativeToScVal(newThreshold, { type: 'u32' }),
    ]
    return this.callContract('propose_change_threshold', args, proposerAddress)
  }

  async approveThresholdProposal(approverAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(approverAddress).toScVal()]
    return this.callContract('approve_threshold_proposal', args, approverAddress)
  }

  async cancelThresholdProposal(callerAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(callerAddress).toScVal()]
    return this.callContract('cancel_threshold_proposal', args, callerAddress)
  }

  async getThresholdProposal(): Promise<ThresholdProposal | null> {
    try {
      const retval = await this.readContract('get_threshold_proposal', [])
      if (!retval) return null
      const native = scValToNative(retval) as {
        new_threshold: number
        proposer: string
        approvals: string[]
      }
      return {
        newThreshold: native.new_threshold,
        proposer: native.proposer,
        approvals: native.approvals ?? [],
      }
    } catch {
      return null
    }
  }

  // ─── Multi-sig: Freeze / Unfreeze ────────────────────────────────────────────

  async proposeFreeze(proposerAddress: string, targetAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [
      new Address(proposerAddress).toScVal(),
      new Address(targetAddress).toScVal(),
    ]
    return this.callContract('propose_freeze', args, proposerAddress)
  }

  async proposeUnfreeze(proposerAddress: string, targetAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [
      new Address(proposerAddress).toScVal(),
      new Address(targetAddress).toScVal(),
    ]
    return this.callContract('propose_unfreeze', args, proposerAddress)
  }

  async approveFreezeProposal(approverAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(approverAddress).toScVal()]
    return this.callContract('approve_freeze_proposal', args, approverAddress)
  }

  async cancelFreezeProposal(callerAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(callerAddress).toScVal()]
    return this.callContract('cancel_freeze_proposal', args, callerAddress)
  }

  async getFreezeProposal(): Promise<FreezeProposal | null> {
    try {
      const retval = await this.readContract('get_freeze_proposal', [])
      if (!retval) return null
      const native = scValToNative(retval) as {
        action: { tag: string } | string
        target: string
        proposer: string
        approvals: string[]
      }
      // The action field comes as an enum variant — scValToNative may return
      // { tag: 'Freeze' } or the string directly depending on SDK version.
      let action: 'freeze' | 'unfreeze' = 'freeze'
      if (typeof native.action === 'string') {
        action = native.action.toLowerCase() === 'unfreeze' ? 'unfreeze' : 'freeze'
      } else if (native.action?.tag) {
        action = native.action.tag.toLowerCase() === 'unfreeze' ? 'unfreeze' : 'freeze'
      }
      return {
        action,
        target: native.target,
        proposer: native.proposer,
        approvals: native.approvals ?? [],
      }
    } catch {
      return null
    }
  }

  /**
   * is_frozen(env, account) -> bool
   * Check whether a given account is currently frozen.
   */
  async isFrozen(accountAddress: string): Promise<boolean> {
    try {
      const args: xdr.ScVal[] = [new Address(accountAddress).toScVal()]
      const retval = await this.readContract('is_frozen', args)
      if (!retval) return false
      return scValToNative(retval) as boolean
    } catch {
      return false
    }
  }

  // ─── Multi-sig: Seizure / Embargo ────────────────────────────────────────────

  /**
   * propose_seizure(env, proposer, target, destination, amount)
   * Target must be frozen. Amount is in display units.
   */
  async proposeSeizure(
    proposerAddress: string,
    targetAddress: string,
    destinationAddress: string,
    displayAmount: number,
  ): Promise<StellarTxResult> {
    const rawAmount = BigInt(Math.round(displayAmount * Math.pow(10, stellarConfig.tokenDecimals)))
    const args: xdr.ScVal[] = [
      new Address(proposerAddress).toScVal(),
      new Address(targetAddress).toScVal(),
      new Address(destinationAddress).toScVal(),
      nativeToScVal(rawAmount, { type: 'i128' }),
    ]
    return this.callContract('propose_seizure', args, proposerAddress)
  }

  async approveSeizure(approverAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(approverAddress).toScVal()]
    return this.callContract('approve_seizure', args, approverAddress)
  }

  async cancelSeizure(callerAddress: string): Promise<StellarTxResult> {
    const args: xdr.ScVal[] = [new Address(callerAddress).toScVal()]
    return this.callContract('cancel_seizure', args, callerAddress)
  }

  async getSeizureProposal(): Promise<SeizureProposal | null> {
    try {
      const retval = await this.readContract('get_seizure_proposal', [])
      if (!retval) return null
      const native = scValToNative(retval) as {
        target: string
        destination: string
        amount: bigint | number | string
        proposer: string
        approvals: string[]
      }
      return {
        target: native.target,
        destination: native.destination,
        amount: String(native.amount),
        proposer: native.proposer,
        approvals: native.approvals ?? [],
      }
    } catch {
      return null
    }
  }

  // ─── Contract state reads ────────────────────────────────────────────────────

  async getAdmins(): Promise<string[]> {
    try {
      const retval = await this.readContract('get_admins', [])
      if (!retval) return []
      return scValToNative(retval) as string[]
    } catch {
      return []
    }
  }

  async getThreshold(): Promise<number> {
    try {
      const retval = await this.readContract('get_threshold', [])
      if (!retval) return 0
      return Number(scValToNative(retval))
    } catch {
      return 0
    }
  }

  /**
   * Load the full contract state in parallel (all view calls at once).
   */
  async getContractState(): Promise<LunarxyContractState> {
    const [admins, threshold, upgradeProposal, adminProposal, thresholdProposal, unpauseProposal, freezeProposal, seizureProposal] =
      await Promise.allSettled([
        this.getAdmins(),
        this.getThreshold(),
        this.getUpgradeProposal(),
        this.getAdminProposal(),
        this.getThresholdProposal(),
        this.getUnpauseProposal(),
        this.getFreezeProposal(),
        this.getSeizureProposal(),
      ])

    // paused flag: we infer it from whether unpauseProposal exists or try a dedicated read
    // The contract stores Paused in instance storage but there's no direct getter in the ABI.
    // We check if unpause proposal exists to give a hint, but for a definitive read we
    // simulate calling a function that reverts when paused (e.g., transfer with zero amount)
    // to detect the paused state. Here we use a safe heuristic via simulation of get_admins
    // which always works regardless of pause state — so we leave paused detection as a
    // separate simulation below.
    let paused = false
    try {
      const rpc = this.rpcServer!
      const contractId = stellarConfig.lunarxyContractAddress
      if (contractId && rpc) {
        // Attempt to simulate mint(zeroAddress, zeroAddress, 0) — if paused it throws
        // Instead, we read the Paused key directly from ledger entries
        const ledgerKey = xdr.LedgerKey.contractData(
          new xdr.LedgerKeyContractData({
            contract: new Address(contractId).toScAddress(),
            key: xdr.ScVal.scvSymbol('Paused'),
            durability: xdr.ContractDataDurability.persistent(),
          }),
        )
        const ledgerResult = await rpc.getLedgerEntries(ledgerKey)
        if (ledgerResult.entries.length > 0) {
          const entry = ledgerResult.entries[0]
          const contractDataEntry = entry.val.contractData()
          paused = scValToNative(contractDataEntry.val()) as boolean
        }
      }
    } catch {
      paused = false
    }

    return {
      admins: admins.status === 'fulfilled' ? admins.value : [],
      threshold: threshold.status === 'fulfilled' ? threshold.value : 0,
      paused,
      version: 0, // version is not exposed via a getter; would need ledger entry read
      upgradeProposal: upgradeProposal.status === 'fulfilled' ? upgradeProposal.value : null,
      adminProposal: adminProposal.status === 'fulfilled' ? adminProposal.value : null,
      thresholdProposal: thresholdProposal.status === 'fulfilled' ? thresholdProposal.value : null,
      unpauseProposal: unpauseProposal.status === 'fulfilled' ? unpauseProposal.value : null,
      freezeProposal: freezeProposal.status === 'fulfilled' ? freezeProposal.value : null,
      seizureProposal: seizureProposal.status === 'fulfilled' ? seizureProposal.value : null,
    }
  }
}

// ─── Singleton ────────────────────────────────────────────────────────────────

export const lunarxyAdminService = new LunarxyAdminService()
