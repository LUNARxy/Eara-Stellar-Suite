import type { StellarNetworkConfig } from './StellarTypes'

export const stellarConfig: StellarNetworkConfig = {
  networkPassphrase: process.env.VUE_APP_STELLAR_NETWORK_PASSPHRASE
    || 'Test SDF Network ; September 2015',
  horizonUrl: process.env.VUE_APP_STELLAR_HORIZON_URL
    || 'https://horizon-testnet.stellar.org',
  rpcUrl: process.env.VUE_APP_STELLAR_RPC_URL
    || 'https://soroban-testnet.stellar.org',
  name: 'testnet',
  assetCode: process.env.VUE_APP_STELLAR_ASSET_CODE || 'XLM',
  assetIssuer: process.env.VUE_APP_STELLAR_ASSET_ISSUER || undefined,
  paymentTokenContract: process.env.VUE_APP_STELLAR_PAYMENT_TOKEN_CONTRACT || '',
  mainContract: process.env.VUE_APP_STELLAR_MAIN_CONTRACT || '',
}
