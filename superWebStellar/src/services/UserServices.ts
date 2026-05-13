import http from "./Http-common";
import store from "@/store";

class UserServices {


    recoveryPass(email: string) {
        return http.get("v1/public/login/email_recovery_pass/" + email + "?language=" + store.getters.getLocale)
    }

    getAccesToken(user: string, pass: string, client_secret: string) {
        const form = new FormData();
        form.append('username', user);
        form.append('password', pass);
        form.append('client_secret', client_secret);
        form.append('grant_type', 'password');
        form.append('scope', ['user'].join(' '));
        return http.post("v1/public/login/access_token", form)
    }
    getUserData() {
        return http.get("v1/private/users/user")
    }
    getIfKYCValid() {
        return http.get("v1/private/users/kyc_valid")
    }
    getDataWalletUser() {
        return http.get("v1/private/wallet/wallet_data_user")
    }
    getMyIBANNumber() {
        return http.get("v1/private/users/my_iban_number")
    }
    getDataTablePortfolio() {
        return http.get("v1/private/portfolio/portfolio_table?category_id=2")
    }
    saveRefundWallet(refund_value) {
        refund_value = refund_value.toString().replace(/\./g, '').replace(',', '.')
        return http.post("v1/private/wallet/wallet_refund/" + refund_value)
    }

    getUserInvestListActivityHistory({ page = 1, perPage = 10 }) {
        return http.get("v1/private/portfolio/activity?page=" + page + "&per_page=" + perPage)
    }
    getUserInvestListMyInvestsActive() {
        return http.get("v1/private/portfolio/my_invest_active?category_id=2")
    }

    sendWallet(wallet: string) {
        const form = new FormData();
        form.append('wallet', wallet);
        return http.put("v1/private/users/wallet/0", form)
    }

    getImageFromPdf(file) {
        // metodo generico para subir ficheros
        const form = new FormData();
        form.append('proof_bank_pdf', file);
        return http.post("v1/private/users/get_image_from_pdf", form)
    }

    updateUserFile(file, file_type) {
        // metodo generico para subir ficheros
        const form = new FormData();
        form.append('file', file);
        form.append('file_type', file_type);
        return http.put("v1/private/users/upload_file_profile", form)
    }
    uploadKYCImages(data_images, user_id = 0) {
        const form = new FormData();
        form.append('files', JSON.stringify(data_images));  // Convertir a string JSON
        return http.put("v1/private/users/upload_kyc_images/" + user_id, form)
    }
    getUserWalletBalance() {
        return http.get("v1/private/wallet/wallet_total_balance")
    }

    singUpWhiteList(invest_id, value_to_invest) {
        return http.post("v1/private/invest/sing_up_white_list/" + invest_id + "?language=" + store.getters.getLocale + "&value_to_invest=" + value_to_invest)
    }
    updateUserPassword(pass_old: string, pass_new: string) {
        const form = new FormData();
        form.append('old_password', pass_old);
        form.append('new_password', pass_new);
        return http.put("v1/private/users/update_password", form)
    }

    createUser(data) {
        const form = new FormData();
        form.append('email', data.email);
        form.append('password', data.pass1);
        form.append('language', store.getters.getLocale);
        if (data.name !== undefined && data.name !== null) {
            form.append('name', data.name);
        }
        if (data.surname !== undefined && data.surname !== null) {
            form.append('surname', data.surname);
        }
        if (data.phone !== undefined && data.phone !== null) {
            form.append('phone', data.phone);
        }
        if (data.referral_code !== undefined && data.referral_code != null) {
            form.append('referral_code', data.referral_code);
        }
        return http.post("v1/public/login/create_user", form)
    }
    updateUser(data, is_kyc = false) {
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
            form.append('date_birthday', data.date_birthday + "T00:00");
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
        return http.put("v1/private/users/0", form)
    }
}

export default new UserServices();
