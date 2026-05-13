// Stellar Application Types

export interface StellarNetworkConfig {
  networkPassphrase: string
  horizonUrl: string
  rpcUrl: string
  name: 'testnet' | 'mainnet'
  assetCode?: string
  assetIssuer?: string
  /** Payment token contract address (SEP-41 / Soroban) */
  paymentTokenContract: string
  /** Main LunarXY token contract address */
  mainContract: string
}

export interface StellarWalletConnection {
  address: string   // Clave pública G... del account
  network: string   // 'testnet' | 'mainnet'
}

export interface StellarAsset {
  code: string       // 'XLM' o código del token custom
  issuer?: string    // undefined si es XLM nativo
  isNative: boolean
}

export interface StellarPaymentResult {
  transactionHash: string
  status: 'confirmed' | 'pending' | 'failed'
  amount: string
  asset: string      // 'XLM' o 'CODE:ISSUER'
}

/**
 * Response from the backend signature endpoint for Stellar user_mint_with_token.
 *
 * The backend signs: SHA256(amount_le16 | payment_amount_le16 | nonce_le8 | uid_le8
 *                            | contract_xdr | payment_token_xdr)
 * with its Ed25519 key and returns the hex-encoded 64-byte signature.
 */
export interface StellarSignatureResponse {
  /** Number of LunarXY tokens to mint (integer, decimals=0) */
  amount: number
  /** Cost in payment token units (i128 as a string to avoid JS precision loss) */
  payment_amount: string
  /** Current on-chain nonce for the caller (u64 as number) */
  nonce: number
  /** Hex-encoded 64-byte Ed25519 signature */
  signature: string
  /** Payment token contract address (for verification) */
  payment_token: string
  /** Main contract address (for verification) */
  contract: string
  /** Platform user ID */
  uid: number
}
