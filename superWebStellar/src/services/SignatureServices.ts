import http from "./Http-common";


class SignatureServices {


    getContractForSignature(invest_slug, document_name, language = "") {
        return http.get(`v1/private/signature/get_by_document_name/${invest_slug}/${document_name}?language=${language}`)
    }

    modifyContract(invest_slug, document_name) {
        return http.get(`v1/private/signature/modify_contract/${invest_slug}/${document_name}`)
    }
    attachSignature(document_name, image, num_tokens, invest_slug, language) {
        const form = new FormData();
        form.append('image_data', image);
        form.append('num_tokens', num_tokens);
        form.append('language', language);
        return http.post(`v1/private/signature/attach_signature/${invest_slug}/${document_name}`, form)
    }

    getFinishedContract(signature_id) {
        return http.get(`v1/private/signature/document/${signature_id}`)
    }

    getResignContrct(signature_id) {
        return http.get(`v1/private/signature/has_resign_contract/${signature_id}`)
    }

    attachSignatureResign(document_name, image, signature_id, economic_check_selected, other_economic_text, capital_check_selected, other_capital_text, bank) {
        const form = new FormData();
        form.append('image_data', image);
        form.append('economic_check_selected', economic_check_selected);
        form.append('other_economic_text', other_economic_text);
        form.append('capital_check_selected', capital_check_selected);
        form.append('other_capital_text', other_capital_text);
        form.append('bank', bank);
        return http.post(`v1/private/signature/attach_signature_resign/${document_name}/${signature_id}`, form)
    }

    getHasToResignContract() {
        return http.get("v1/private/signature/has_to_resign_any_contract")
    }


}

export default new SignatureServices();