export interface StellarNetworkConfig {
  networkPassphrase: string
  horizonUrl: string
  rpcUrl: string
  lunarxyContractAddress: string
  compliantIdContractAddress: string
  tokenDecimals: number
}

export const stellarConfig: StellarNetworkConfig = {
  networkPassphrase:
    process.env.VUE_APP_STELLAR_NETWORK_PASSPHRASE ??
    'Test SDF Network ; September 2015',
  horizonUrl:
    process.env.VUE_APP_STELLAR_HORIZON_URL ??
    'https://horizon-testnet.stellar.org',
  rpcUrl:
    process.env.VUE_APP_STELLAR_RPC_URL ??
    'https://soroban-testnet.stellar.org',
  lunarxyContractAddress:
    process.env.VUE_APP_LUNARXY_CONTRACT_ADDRESS ?? '',
  compliantIdContractAddress:
    process.env.VUE_APP_COMPLIANT_ID_CONTRACT_ADDRESS ?? '',
  tokenDecimals: parseInt(process.env.VUE_APP_LUNARXY_TOKEN_DECIMALS ?? '7', 10),
}
