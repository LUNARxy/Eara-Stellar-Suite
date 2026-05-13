import http from "./Http-common";

class ContractDataService {
    /**
     * Get backend Ed25519 signature for Stellar user_mint_with_token.
     * Returns: { amount, payment_amount, nonce, signature (hex 64 bytes),
     *            payment_token, contract, uid }
     */
    getTokenMintSignatureStellar(invest_id, address, amount, price) {
        return http.get(`v1/private/tokens/mint_signature_token_stellar/${invest_id}?address=${address}&amount=${amount}&price=${price}`)
    }

    /**
     * Check whether a Stellar wallet address is compliant in the
     * CompliantId contract (public endpoint — no auth required).
     * Returns: { wallet: string, is_compliant: boolean }
     */
    isCompliantStellar(wallet: string) {
        return http.get(`v1/private/stellar/is_compliant?wallet=${wallet}`)
    }

    getTokenData(invest_slug) {
        return http.get(`v1/private/tokens/phase_tokens_data/${invest_slug}`)
    }

    checkTransaction(invest_id, tx_hash, signature_documents_id) {
        return http.get(`v1/private/tokens/check_transaction/${invest_id}/${tx_hash}/${signature_documents_id}`)
    }
}

export default new ContractDataService();
