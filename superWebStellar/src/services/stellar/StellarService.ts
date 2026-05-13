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
  BASE_FEE,
  Address,
  nativeToScVal,
  xdr,
  Operation,
  rpc as StellarRpc,
} from '@stellar/stellar-sdk'
import { stellarConfig } from './StellarConfig'
import ContractDataService from '@/services/ContractDataService'
import store from '@/store'

import type {
  StellarWalletConnection,
  StellarPaymentResult,
  StellarSignatureResponse,
} from './StellarTypes'

// ─── Internal helper ──────────────────────────────────────────────────────────

/** Build an invokeHostFunction Operation for a Soroban contract call. */
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
      })
    ),
    auth: [],
  })
}

// ─── Service class ────────────────────────────────────────────────────────────

class StellarService {
  private horizonServer: Horizon.Server | null = null
  private rpcServer: StellarRpc.Server | null = null
  private publicKey: string | null = null
  private network = 'testnet'

  // ─── Initialization ───────────────────────────────────────────────────────

  async initialize(): Promise<StellarService> {
    this.network = stellarConfig.name
    this.horizonServer = new Horizon.Server(stellarConfig.horizonUrl)
    this.rpcServer = new StellarRpc.Server(stellarConfig.rpcUrl)
    console.debug('StellarService initialized:', {
      horizonUrl: stellarConfig.horizonUrl,
      rpcUrl: stellarConfig.rpcUrl,
    })
    return this
  }

  // ─── Wallet connection ────────────────────────────────────────────────────

  async checkWalletConnection(): Promise<StellarWalletConnection | null> {
    try {
      const connectedResult = await freighterIsConnected()
      if (!connectedResult.isConnected) {
        console.debug('Freighter not installed or not connected')
        return null
      }

      const allowedResult = await isAllowed()
      if (!allowedResult.isAllowed) {
        console.debug('App not allowed in Freighter')
        return null
      }

      const addressResult = await getAddress()
      if (addressResult.error || !addressResult.address) {
        console.debug('Could not get Freighter address silently:', addressResult.error)
        return null
      }

      this.publicKey = addressResult.address
      store.commit('ADDRESS_CHANGED', this.publicKey)
      console.debug('Found existing Freighter connection:', this.publicKey)

      return { address: this.publicKey, network: this.network }
    } catch (error) {
      console.debug('No existing Freighter connection found:', (error as Error).message)
      return null
    }
  }

  async connectWallet(): Promise<StellarWalletConnection> {
    try {
      store.commit('ADDRESS_CHANGED', null)

      const connectedResult = await freighterIsConnected()
      if (!connectedResult.isConnected) {
        throw new Error('Freighter wallet is not installed. Please install the Freighter browser extension.')
      }

      const accessResult = await requestAccess()
      if (accessResult.error || !accessResult.address) {
        throw new Error(accessResult.error?.message || 'User denied access to Freighter wallet')
      }

      this.publicKey = accessResult.address
      store.commit('ADDRESS_CHANGED', this.publicKey)
      console.debug('Freighter wallet connected:', this.publicKey)

      return { address: this.publicKey, network: this.network }
    } catch (error) {
      console.error('Error connecting Freighter wallet:', error)
      throw error
    }
  }

  disconnectWallet(): void {
    this.publicKey = null
    store.commit('ADDRESS_CHANGED', null)
    console.debug('Stellar wallet disconnected (local state cleared)')
  }

  // ─── Soroban helpers ──────────────────────────────────────────────────────

  /**
   * Build, simulate (to attach footprint + resource fees), sign via Freighter,
   * and submit the transaction. Returns the transaction hash immediately after
   * submission, without waiting for on-chain confirmation.
   */
  private async buildSignAndSubmit(
    contractId: string,
    functionName: string,
    args: xdr.ScVal[],
    callerAddress: string,
  ): Promise<string> {
    if (!this.rpcServer) throw new Error('RPC server not initialized')

    const account = await this.rpcServer.getAccount(callerAddress)

    const tx = new TransactionBuilder(account, {
      fee: '1000000', // 0.1 XLM max fee cap — Soroban needs higher than classic
      networkPassphrase: stellarConfig.networkPassphrase,
    })
      .addOperation(makeContractCall(contractId, functionName, args))
      .setTimeout(180)
      .build()

    // Simulate to get the resource footprint
    const simResult = await this.rpcServer.simulateTransaction(tx)
    if (StellarRpc.Api.isSimulationError(simResult)) {
      throw new Error(`Simulation failed (${functionName}): ${simResult.error}`)
    }

    // Assemble = attach the footprint + resource fees from simulation
    const preparedTx = StellarRpc.assembleTransaction(tx, simResult).build()

    // Sign via Freighter
    const signResult = await signTransaction(preparedTx.toXDR(), {
      networkPassphrase: stellarConfig.networkPassphrase,
      address: callerAddress,
    })
    if (signResult.error) {
      throw new Error(signResult.error.message || 'Transaction signing rejected by user')
    }

    // Reconstruct signed transaction and submit
    const { TransactionBuilder: TB } = await import('@stellar/stellar-sdk')
    const signedTx = TB.fromXDR(signResult.signedTxXdr, stellarConfig.networkPassphrase)

    const sendResult = await this.rpcServer.sendTransaction(signedTx)
    if (sendResult.status === 'ERROR') {
      throw new Error(`Submission failed (${functionName}): ${JSON.stringify(sendResult.errorResult)}`)
    }

    return sendResult.hash
  }

  /**
   * Poll the RPC until the transaction reaches SUCCESS or FAILED (up to ~2 min).
   * Throws if the transaction does not succeed.
   */
  private async waitForTransaction(hash: string, functionName: string): Promise<void> {
    if (!this.rpcServer) throw new Error('RPC server not initialized')

    let getResult = await this.rpcServer.getTransaction(hash)
    for (
      let i = 0;
      i < 40 && getResult.status === StellarRpc.Api.GetTransactionStatus.NOT_FOUND;
      i++
    ) {
      await new Promise(r => setTimeout(r, 3000))
      getResult = await this.rpcServer.getTransaction(hash)
    }

    if (getResult.status !== StellarRpc.Api.GetTransactionStatus.SUCCESS) {
      throw new Error(`Transaction failed (${functionName}): status=${getResult.status}`)
    }
  }

  // ─── Main mint flow ───────────────────────────────────────────────────────

  /**
   * Two-step Soroban mint flow:
   *  Step 1 — approve(caller, mainContract, paymentAmount, expirationLedger)
   *           on the payment token contract (so the main contract can pull funds)
   *  Step 2 — user_mint_with_token(caller, amount, paymentToken,
   *            paymentAmount, nonce, uid, signature)
   *           on the main LunarXY contract
   *
   * All numeric/signature parameters come from the backend response.
   */
  async mintWithToken(
    sigResponse: StellarSignatureResponse,
    investId: string,
  ): Promise<StellarPaymentResult> {
    if (!this.rpcServer || !this.publicKey) {
      throw new Error('Wallet not connected or Stellar service not initialized')
    }

    const callerAddress = this.publicKey
    const { paymentTokenContract, mainContract } = stellarConfig

    if (!paymentTokenContract || !mainContract) {
      throw new Error('Stellar contract addresses not configured')
    }

    // Convert string/number values to BigInt (avoids JS precision issues for i128/u64)
    const amount        = BigInt(sigResponse.amount)
    const paymentAmount = BigInt(sigResponse.payment_amount)
    const nonce         = BigInt(sigResponse.nonce)
    const uid           = BigInt(sigResponse.uid)

    // Decode hex signature → Uint8Array (64 bytes)
    const sigHex   = sigResponse.signature.replace(/^0x/, '')
    const sigBytes = new Uint8Array(sigHex.match(/.{1,2}/g)!.map(b => parseInt(b, 16)))

    console.debug('Stellar mintWithToken params:', {
      amount: amount.toString(),
      paymentAmount: paymentAmount.toString(),
      nonce: nonce.toString(),
      uid: uid.toString(),
      paymentTokenContract,
      mainContract,
    })

    // ── Step 1 — approve ─────────────────────────────────────────────────────
    store.commit('BLOCKCHAIN_OP_PROGRESS', {
      op: 'stellarPayment',
      progress: true,
      title: 'Pago Crypto',
      message: 'blockchainDialog.confirmTransaction',
      step: 1,
      tokensToTransfer: `${sigResponse.payment_amount} tokens`,
    })

    // Get current ledger to compute expiration_ledger for the allowance
    const latestLedger = await this.rpcServer.getLatestLedger()
    const expirationLedger = latestLedger.sequence + 500  // ~42 minutes

    // approve(from: Address, spender: Address, amount: i128, expiration_ledger: u32)
    const approveArgs: xdr.ScVal[] = [
      new Address(callerAddress).toScVal(),
      new Address(mainContract).toScVal(),
      nativeToScVal(paymentAmount, { type: 'i128' }),
      nativeToScVal(expirationLedger, { type: 'u32' }),
    ]

    console.debug('Submitting approve...')
    const approveTxHash = await this.buildSignAndSubmit(paymentTokenContract, 'approve', approveArgs, callerAddress)
    console.debug('approve submitted, waiting for confirmation:', approveTxHash)
    await this.waitForTransaction(approveTxHash, 'approve')
    console.debug('approve confirmed.')

    // ── Step 2 — user_mint_with_token ────────────────────────────────────────
    store.commit('BLOCKCHAIN_OP_PROGRESS', {
      op: 'stellarPayment',
      progress: true,
      title: 'Pago Crypto',
      message: 'blockchainDialog.confirmTransaction',
      step: 2,
      tokensToTransfer: `${sigResponse.amount} tokens`,
    })

    // user_mint_with_token(caller, amount: i128, payment_token: Address,
    //   payment_amount: i128, nonce: u64, uid: u64, signature: BytesN<64>)
    const mintArgs: xdr.ScVal[] = [
      new Address(callerAddress).toScVal(),
      nativeToScVal(amount, { type: 'i128' }),
      new Address(paymentTokenContract).toScVal(),
      nativeToScVal(paymentAmount, { type: 'i128' }),
      nativeToScVal(nonce, { type: 'u64' }),
      nativeToScVal(uid, { type: 'u64' }),
      nativeToScVal(sigBytes, { type: 'bytes' }),
    ]

    // Submit and get the hash immediately — do not wait for on-chain confirmation
    console.debug('Submitting user_mint_with_token...')
    const mintTxHash = await this.buildSignAndSubmit(
      mainContract,
      'user_mint_with_token',
      mintArgs,
      callerAddress,
    )
    console.debug('user_mint_with_token submitted:', mintTxHash)

    // ── Notify backend as soon as the hash is available ───────────────────────
    ContractDataService.checkTransaction(investId, mintTxHash, 0)

    store.commit('BLOCKCHAIN_OP_PROGRESS', {
      op: 'stellarPayment',
      progress: false,
      title: 'Pago Crypto',
      message: 'views.Tus tokens aparecerán en la plataforma card_',
      step: 2,
    })

    return {
      transactionHash: mintTxHash,
      status: 'confirmed',
      amount: sigResponse.amount.toString(),
      asset: paymentTokenContract,
    }
  }

  // ─── Utility ──────────────────────────────────────────────────────────────

  isConnected(): boolean {
    return this.publicKey !== null
  }

  getAccountAddress(): string | null {
    return this.publicKey
  }

  getCurrentNetwork(): string {
    return this.network
  }
}

// Singleton instance
export const stellarService = new StellarService()
