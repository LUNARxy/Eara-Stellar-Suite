import http from "./Http-common";

class UserServices {

    getUsersPaginated({valid_kyc = -1, find = '', page = 1, perPage = 10}){
        return http.get("v1/private/users/list/paginated?valid_kyc="+valid_kyc+"&find="+find+"&page="+page+"&per_page="+perPage)
    }

    getUsersNums(){
        return http.get("v1/private/users/numbers_kyc")
    }
    getUser(id){
        return http.get("v1/private/users/user?user_id="+id)
    }
    getUsersExportExcel(valid_kyc = -1, find = '', invest_id = -1){
        return http.get("v1/private/users/download_excel?valid_kyc="+valid_kyc+"&invest_id="+invest_id+"&find="+find)
    }
    getUsersInvestors(invest_id, refund_type = -1){
        return http.get("v1/private/marketplace/investors/"+invest_id+"?refund_type="+refund_type)
    }
    getUsersInvestorsRefund(invest_id, refund_type){
        return http.get("v1/private/marketplace/investors_refund/"+invest_id+"?refund_type="+refund_type)
    }
    saveInvestUserRefund(invest_id, user_id, user_invest_id, refund_type, num_tokens){
        //refund_value = refund_value.toString().replace(/\./g, '').replace(',', '.')
        return http.post("v1/private/marketplace/user_contribution_refund/"+invest_id+"/"+user_id+"/"+user_invest_id+"?refund_type="+refund_type+"&num_tokens="+num_tokens)
    }

    getUsersWhiteList(invest_id){
        return http.get("v1/private/invest/invest_white_list/"+invest_id)
    }
    getUsersWhiteListCount(invest_id){
        return http.get("v1/private/invest/invest_white_list_total/"+invest_id)
    }
    getDataTablePortfolio(user_id = 0){
        return http.get("v1/private/portfolio/portfolio_table?category_id=2&user_id="+user_id)
    }
    getUserInvestListMyInvestsActive(user_id = 0){
        return http.get("v1/private/portfolio/my_invest_active?category_id=2&user_id="+user_id)
    }

    getUsersForSelect(){
        return http.get("v1/private/users/for_select")
    }

    saveUser(data, type = 'save'){
        const form = new FormData();
        if (data.name !== undefined && data.name != null) {
            form.append('name', data.name);
        }
        if (data.user_type !== undefined && data.user_type != null) {
            form.append('user_type', data.user_type);
        }
        if (data.surname !== undefined && data.surname != null) {
            form.append('surname', data.surname);
        }
        if (data.phone !== undefined && data.phone != null) {
            form.append('phone', data.phone);
        }
        if (data.address !== undefined && data.address != null) {
            form.append('address', data.address);
        }
        if (data.city !== undefined && data.city != null) {
            form.append('city', data.city);
        }
        if (data.province !== undefined && data.province != null) {
            form.append('province', data.province);
        }
        if (data.country !== undefined && data.country != null) {
            form.append('country', data.country);
        }
        if (data.postal_code !== undefined && data.postal_code != null) {
            form.append('postal_code', data.postal_code);
        }
        if (data.dni !== undefined && data.dni != null) {
            form.append('dni', data.dni);
        }
        if (data.occupation !== undefined && data.occupation != null) {
            form.append('occupation', data.occupation);
        }
        if (data.nationality !== undefined && data.nationality != null) {
            form.append('nationality', data.nationality);
        }
        if (data.civil_status !== undefined && data.civil_status != null) {
            form.append('civil_status', data.civil_status);
        }
        if (data.economic_matrimonial_regime !== undefined && data.economic_matrimonial_regime != null) {
            form.append('economic_matrimonial_regime', data.economic_matrimonial_regime);
        }
        if (data.date_birthday !== undefined && data.date_birthday != null) {
            form.append('date_birthday', data.date_birthday+"T00:00");
        }

        //empresa
        if (data.company_name !== undefined && data.company_name != null) {
            form.append('company_name', data.company_name);
        }
        if (data.activity !== undefined && data.activity != null) {
            form.append('activity', data.activity);
        }
        if (data.holders !== undefined && data.holders != null) {
            form.append('holders', data.holders);
        }
        if (data.is_representative_owner === false) {
            form.append('is_representative_owner', "0");
        } else if (data.is_representative_owner === true) {
            form.append('is_representative_owner', "1");
        }

        if (data.register_number !== undefined && data.register_number != null) {
            form.append('register_number', data.register_number);
        }
        if (data.nif !== undefined && data.nif != null) {
            form.append('nif', data.nif);
        }
        if (data.legal_form !== undefined && data.legal_form != null) {
            form.append('legal_form', data.legal_form);
        }
        if (data.company_address !== undefined && data.company_address != null) {
            form.append('company_address', data.company_address);
        }
        if (data.company_postal_code !== undefined && data.company_postal_code != null) {
            form.append('company_postal_code', data.company_postal_code);
        }
        if (data.company_city !== undefined && data.company_city != null) {
            form.append('company_city', data.company_city);
        }
        if (data.company_province !== undefined && data.company_province != null) {
            form.append('company_province', data.company_province);
        }
        if (data.company_country !== undefined && data.company_country != null) {
            form.append('company_country', data.company_country);
        }
        form.append('email', data.email);
        form.append('password', data.password);
        return http.post("v1/private/users", form)
    }
    getAccesToken(user, pass, client_secret){
        const form = new FormData();
        form.append('username', user);
        form.append('password', pass);
        form.append('client_secret', client_secret);
        form.append('grant_type', 'password');
        form.append('scope', ['admin'].join(' '));
        return http.post("v1/public/login/access_token", form)
    }
    validateKYC(id, type_validate, kyc_no_valid_reason = '', kyc_no_valid_reason_EN = ''){
        const form = new FormData();
        form.append('type_validate', type_validate);
        form.append('kyc_no_valid_reason', kyc_no_valid_reason);
        form.append('kyc_no_valid_reason_EN', kyc_no_valid_reason_EN);
        return http.put("v1/private/users/update_kyc_status/"+id, form)
    }
    changeStatus(id, status){
        return http.put("v1/private/users/update_is_active/"+id+"/"+status)
    }

    updateUserPassword(pass_new:string, user_id){
        const form = new FormData();
        form.append('old_password', "aux");
        form.append('new_password', pass_new);
        return http.put("v1/private/users/update_password?user_id="+user_id, form)
    }
    sendWallet(wallet:string, user_id) {
        const form = new FormData();
        form.append('wallet', wallet);
        return http.put("v1/private/users/wallet/"+user_id, form)
    }


    updateUser(data, user_id, is_kyc = false){
        const form = new FormData();
        if (!is_kyc){
            if (data.alias !== undefined && data.alias != null) {
                form.append('alias', data.alias);
            }
            if (data.description !== undefined && data.description != null) {
                form.append('description', data.description);
            }
        }
        if (data.name !== undefined && data.name != null) {
            form.append('name', data.name);
        }
        if (data.user_type !== undefined && data.user_type != null) {
            form.append('user_type', data.user_type);
        }
        if (data.surname !== undefined && data.surname != null) {
            form.append('surname', data.surname);
        }
        if (data.phone !== undefined && data.phone != null) {
            form.append('phone', data.phone);
        }
        if (data.address !== undefined && data.address != null) {
            form.append('address', data.address);
        }
        if (data.city !== undefined && data.city != null) {
            form.append('city', data.city);
        }
        if (data.province !== undefined && data.province != null) {
            form.append('province', data.province);
        }
        if (data.country !== undefined && data.country != null) {
            form.append('country', data.country);
        }
        if (data.postal_code !== undefined && data.postal_code != null) {
            form.append('postal_code', data.postal_code);
        }
        if (data.dni !== undefined && data.dni != null) {
            form.append('dni', data.dni);
        }
        if (data.occupation !== undefined && data.occupation != null) {
            form.append('occupation', data.occupation);
        }
        if (data.nationality !== undefined && data.nationality != null) {
            form.append('nationality', data.nationality);
        }
        if (data.civil_status !== undefined && data.civil_status != null) {
            form.append('civil_status', data.civil_status);
        }
        if (data.economic_matrimonial_regime !== undefined && data.economic_matrimonial_regime != null) {
            form.append('economic_matrimonial_regime', data.economic_matrimonial_regime);
        }
        if (data.date_birthday !== undefined && data.date_birthday != null) {
            form.append('date_birthday', data.date_birthday+"T00:00");
        }

        if (data.is_representative_owner === false) {
            form.append('is_representative_owner', "0");
        } else if (data.is_representative_owner === true) {
            form.append('is_representative_owner', "1");
        }


        //empresa
        if (data.company_name !== undefined && data.company_name != null) {
            form.append('company_name', data.company_name);
        }
        if (data.activity !== undefined && data.activity != null) {
            form.append('activity', data.activity);
        }
        if (data.holders !== undefined && data.holders != null) {
            form.append('holders', data.holders);
        }
        if (data.register_number !== undefined && data.register_number != null) {
            form.append('register_number', data.register_number);
        }
        if (data.nif !== undefined && data.nif != null) {
            form.append('nif', data.nif);
        }
        if (data.legal_form !== undefined && data.legal_form != null) {
            form.append('legal_form', data.legal_form);
        }
        if (data.company_address !== undefined && data.company_address != null) {
            form.append('company_address', data.company_address);
        }
        if (data.company_postal_code !== undefined && data.company_postal_code != null) {
            form.append('company_postal_code', data.company_postal_code);
        }
        if (data.company_city !== undefined && data.company_city != null) {
            form.append('company_city', data.company_city);
        }
        if (data.company_province !== undefined && data.company_province != null) {
            form.append('company_province', data.company_province);
        }
        if (data.company_country !== undefined && data.company_country != null) {
            form.append('company_country', data.company_country);
        }
        return http.put(`v1/private/users/${user_id}`, form)
    }

    getImageFromPdf(file){
        // metodo generico para subir ficheros
        const form = new FormData();
        form.append('proof_bank_pdf', file);
        return http.post("v1/private/users/get_image_from_pdf", form)
    }

    uploadKYCImages(data_images, user_id){
        const form = new FormData();
        form.append('files', JSON.stringify(data_images));  // Convertir a string JSON
        return http.put("v1/private/users/upload_kyc_images/" + user_id, form)
    }

}

export default new UserServices();
