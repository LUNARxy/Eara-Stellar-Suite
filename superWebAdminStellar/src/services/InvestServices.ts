import http from "./Http-common";
import {parseDateToUTC} from "@/functions";

class InvestServices {


    getInvestList(status = -1, get_all_info = false, is_in_white_list = false, is_in_follow = false, search_text = ''){
        return http.get("v1/private/invest/list?status_invest=" + status + "&category_id=2&get_all_info=" + get_all_info + "&is_in_white_list=" + is_in_white_list + "&is_in_follow=" + is_in_follow + "&search_text=" + search_text)
    }
    getInvestTotals(){
        return http.get("v1/private/invest/totals_status?category_id=2")
    }
    getInvestProject(id, get_status_description = false, get_all_info = false){
        return http.get("v1/private/invest/by_id/"+id+"?get_status_description="+get_status_description+"&get_all_info="+get_all_info)
    }
    getInvestTotalsPendingVerifiedAndVerified(invest_id){
        return http.get("v1/private/invest/totals_pending_verified_and_verified/"+invest_id)
    }

    getInvestLastCollectedChart(){
        return http.get("v1/private/portfolio/last_invest_collected_by_month?category_id=2")
    }
    getInvestBalanceInvestProfitsList(invest_id = -1, user_id = -1, invest_child_id = -1){
        return http.get("v1/private/portfolio_nuevo/data_value_list?category_id=2&invest_id="+invest_id+"&user_id="+user_id+"&invest_child_id="+invest_child_id)
    }
    getInvestLastBalance(invest_id = -1, user_id = -1, invest_child_id = -1){
        return http.get("v1/private/portfolio_nuevo/data_percentage_value?type_value=0&category_id=2&invest_id="+invest_id+"&user_id="+user_id+"&invest_child_id="+invest_child_id)
    }
    getInvestLastInvest(invest_id = -1, user_id = -1, invest_child_id = -1){
        return http.get("v1/private/portfolio_nuevo/data_percentage_value?type_value=1&category_id=2&invest_id="+invest_id+"&user_id="+user_id+"&invest_child_id="+invest_child_id)
    }
    getInvestLastProfits(invest_id = -1, user_id = -1, invest_child_id = -1){
        return http.get("v1/private/portfolio_nuevo/data_percentage_value?type_value=2&category_id=2&invest_id="+invest_id+"&user_id="+user_id+"&invest_child_id="+invest_child_id)
    }
    getInvestListAllMarketplace(){
        return http.get("v1/private/specific_vannilo/list")
    }

    getInvestActivity({invest_id, page = 1, perPage = 10}){
        return http.get("v1/private/portfolio/activity?invest_id="+invest_id+"&page="+page+"&per_page="+perPage)
    }
    validateTransaction(sale_id){
        return http.post("v1/admin/specific_vannilo/sold/1/"+sale_id)
    }

    auxSave(data){
        const form = new FormData();
        form.append('category_id', '2');
        form.append('status_invest', data.status);
        form.append('name', data.name);
        if (data.name_EN !== undefined && data.name_EN !== null) {
            form.append('name_EN', data.name_EN);
        }
        form.append('title', data.title);
        if (data.title_EN !== undefined && data.title_EN !== null) {
            form.append('title_EN', data.title_EN);
        }
        form.append('summary', data.summary);
        if (data.summary_EN !== undefined && data.summary_EN !== null) {
            form.append('summary_EN', data.summary_EN);
        }
        form.append('description', data.description);
        if (data.description_EN !== undefined && data.description_EN !== null) {
            form.append('description_EN', data.description_EN);
        }
        if (data.proposal_to_investors !== undefined && data.proposal_to_investors !== null) {
            form.append('proposal_to_investors', data.proposal_to_investors);
        }
        if (data.proposal_to_investors_EN !== undefined && data.proposal_to_investors_EN !== null) {
            form.append('proposal_to_investors_EN', data.proposal_to_investors_EN);
        }
        if (data.profit_estimated != null) {
            data.profit_estimated = data.profit_estimated.toString().replace(/,/g, '.');
            form.append('profit_estimated', data.profit_estimated);
        }
        if (data.profit_estimated_description != null) {
            form.append('profit_estimated_description', data.profit_estimated_description);
        }
        //form.append('risk', data.risk);

        /*if (data.token_abbreviation !== undefined && data.token_abbreviation !== null) {
            form.append('token_abbreviation', data.token_abbreviation);
        }*/
        if (data.time_limit !== undefined && data.time_limit !== null) {
            form.append('time_limit', data.time_limit);
        }
        if (data.hide_time_data == null || data.hide_time_data == false){
            form.append('hide_time_data', "0");
        } else {
            form.append('hide_time_data', "1");
        }
        if (data.hide_date_start_round == null || data.hide_date_start_round == false){
            form.append('hide_date_start_round', "0");
        } else {
            form.append('hide_date_start_round', "1");
        }
        if (data.hide_date_end_round == null || data.hide_date_end_round == false){
            form.append('hide_date_end_round', "0");
        } else {
            form.append('hide_date_end_round', "1");
        }
        if (data.hide_profit_estimated == null || data.hide_profit_estimated == false){
            form.append('hide_profit_estimated', "0");
        } else {
            form.append('hide_profit_estimated', "1");
        }
        if (data.hide_value_round == null || data.hide_value_round == false){
            form.append('hide_value_round', "0");
        } else {
            form.append('hide_value_round', "1");
        }
        if (data.hide_num_tokens == null || data.hide_num_tokens == false){
            form.append('hide_num_tokens', "0");
        } else {
            form.append('hide_num_tokens', "1");
        }
        if (data.web !== undefined && data.web !== null) {
            form.append('web', data.web);
        }
        if (data.is_draft == null || data.is_draft == false){
            form.append('is_draft', "0");
        } else {
            form.append('is_draft', "1");
        }
        if (data.is_important == null || data.is_important == false){
            form.append('is_important', "0");
        } else {
            form.append('is_important', "1");
        }
        if (data.location !== undefined && data.location !== null) {
            form.append('location', data.location);
        }
        if (data.location_gps_lat !== undefined && data.location_gps_lat !== null) {
            form.append('location_gps_lat', data.location_gps_lat);
        }
        if (data.location_gps_lon !== undefined && data.location_gps_lon !== null) {
            form.append('location_gps_lon', data.location_gps_lon);
        }
        if (data.success_fee !== undefined && data.success_fee !== null) {
            form.append('success_fee', data.success_fee);
        }
        if (data.management_fee !== undefined && data.management_fee !== null) {
            form.append('management_fee', data.management_fee);
        }
        if (data.opening_commission !== undefined && data.opening_commission !== null) {
            form.append('opening_commission', data.opening_commission);
        }
        if (data.closing_commission !== undefined && data.closing_commission !== null) {
            form.append('closing_commission', data.closing_commission);
        }
        if (data.spread !== undefined && data.spread !== null) {
            form.append('spread', data.spread);
        }
        if (data.entry_fee !== undefined && data.entry_fee !== null) {
            form.append('entry_fee', data.entry_fee);
        }
        if (data.annual_fee !== undefined && data.annual_fee !== null) {
            form.append('annual_fee', data.annual_fee);
        }
        if (data.file_top != null) {
            form.append('file_top', data.file_top);
        }
        if (data.file != null) {
            form.append('file', data.file);
        }
        return form;
    }
    saveInvestProject(data){
        const form = this.auxSave(data);
        return http.post("v1/private/invest", form)
    }

    updateInvestProject(data){
        const form = this.auxSave(data);
        return http.put("v1/private/invest/"+data.id, form)
    }

    getUsersInvestorsToCompletedProyect(invest_id){
        return http.get("v1/private/invest/investors_to_close_invest/"+invest_id)
    }
    closeProject(invest_id) {
        return http.post("v1/private/invest/close_project/" + invest_id)
    }


    //-----------------------------------------------------
    //  IMAGENES
    //-----------------------------------------------------
    getInvestGallery(id){
        return http.get("v1/private/invest/media/list/"+id)
    }
    saveInvestGallery(data){
        const form = new FormData();
        if (data.description !== undefined && data.description !== null) {
            form.append('description', data.description);
        }
        form.append('file', data.file);
        return http.post("v1/private/invest/media/"+data.invest_id, form)
    }
    deleteGallery(invest_id, id){
        return http.delete("v1/private/invest/media/"+invest_id+"/"+id)
    }


    //-----------------------------------------------------
    //  DOCUMENTOS
    //-----------------------------------------------------
    getInvestDocs(id){
        return http.get("v1/private/invest/documents/list/"+id)
    }
    saveInvestDocs(data){
        const form = new FormData();
        form.append('description', data.description);
        form.append('file', data.file);
        return http.post("v1/private/invest/documents/"+data.invest_id, form)
    }
    deleteDocs(invest_id, id){
        return http.delete("v1/private/invest/documents/"+invest_id+"/"+id)
    }


    //-----------------------------------------------------
    //  NOTICIAS
    //-----------------------------------------------------
    getInvestNews(id){
        return http.get("v1/private/invest/news/list/"+id)
    }
    saveInvestNews(data){
        const form = new FormData();
        form.append('title', data.title);
        form.append('summary', data.summary);
        if (data.url !== undefined && data.url !== null) {
            form.append('url', data.url);
        }
        if (data.file !== undefined && data.file !== null) {
            form.append('file', data.file);
        }
        //si tiene id entonces es actualizar si no es uno nuevo
        if (data.id != undefined && data.id != ""){
            return http.put("v1/private/invest/news/"+data.invest_id+"/"+data.id, form)
        } else {
            return http.post("v1/private/invest/news/" + data.invest_id, form)
        }
    }

    deleteNews(invest_id, id){
        return http.delete("v1/private/invest/news/"+invest_id+"/"+id)
    }


    //-----------------------------------------------------
    //  EQUIPO
    //-----------------------------------------------------
    getInvestTeam(id){
        return http.get("v1/private/invest/team/list/"+id)
    }
    saveInvestTeam(data){
        const form = new FormData();
        form.append('name', data.name);
        if (data.job !== undefined && data.job !== null) {
            form.append('job', data.job);
        }
        if (data.description !== undefined && data.description !== null) {
            form.append('description', data.description);
        }
        if (data.url_linked_in !== undefined && data.url_linked_in !== null) {
            form.append('url_linked_in', data.url_linked_in);
        }
        if (data.file !== undefined && data.file !== null) {
            form.append('file', data.file);
        }
        //si tiene id entonces es actualizar si no es uno nuevo
        if (data.id != undefined && data.id != ""){
            return http.put("v1/private/invest/team/"+data.invest_id+"/"+data.id, form)
        } else {
            return http.post("v1/private/invest/team/" + data.invest_id, form)
        }
    }
    deleteTeam(invest_id, id){
        return http.delete("v1/private/invest/team/"+invest_id+"/"+id)
    }


    //-----------------------------------------------------
    //  PREGUNTAS Y RESPUESTAS
    //-----------------------------------------------------
    getInvestQuestions(id){
        return http.get("v1/private/invest/questions/list/"+id)
    }
    saveInvestQuestions(data){
        const form = new FormData();
        form.append('title', data.title);
        form.append('comment', data.comment);
        //si tiene id entonces es actualizar si no es uno nuevo
        if (data.id != undefined && data.id != ""){
            return http.put("v1/private/invest/questions/"+data.invest_id+"/"+data.id, form)
        } else {
            return http.post("v1/private/invest/questions/" + data.invest_id, form)
        }
    }
    deleteQuestions(invest_id, id){
        return http.delete("v1/private/invest/questions/"+invest_id+"/"+id)
    }

    ///-----------------------------------------------------
    //  DESCRIPCIONES DE LOS ESTADOS DEL PROYECTO
    //-----------------------------------------------------
    getInvestStatusDescription(id){
        return http.get("v1/private/invest/status_description/list/"+id)
    }
    saveInvestStatusDescription(data){
        const form = new FormData();
        form.append('phase', data.phase);
        if (data.description !== undefined && data.description !== null) {
            form.append('description', data.description);
        }
        if (data.date_created !== undefined && data.date_created !== null && data.date_created !== "") {
            form.append('date_created', parseDateToUTC(data.date_created));
        }
        //si tiene id entonces es actualizar si no es uno nuevo
        if (data.id != undefined && data.id != ""){
            return http.put("v1/private/invest/status_description/"+data.invest_id+"/"+data.id, form)
        } else {
            return http.post("v1/private/invest/status_description/" + data.invest_id, form)
        }
    }
    deleteStatusDescription(invest_id, id){
        return http.delete("v1/private/invest/status_description/"+invest_id+"/"+id)
    }

    ///-----------------------------------------------------
    //  FASES DE MINTEO DE COMPRA
    //-----------------------------------------------------
    getInvestPhasesMint(invest_id){
        return http.get("v1/private/invest/phases_mint/list/"+invest_id)
    }
    savePhaseCompleted(data){
        const form = new FormData();
        form.append('num_investors_completed', data.num_investors_completed);
        form.append('num_tokens_completed', data.num_tokens_completed);
        form.append('total_amount_invested_completed', data.total_amount_invested_completed);
        return http.put("v1/private/invest/phases_mint/data_phase_completed/"+data.invest_id, form)
    }
    saveInvestPhasesMint(data){
        const form = new FormData();
        form.append('phase', data.phase);
        form.append('max_tokens', data.max_tokens);
        if (data.is_private == null || data.is_private == false){
            form.append('is_private', "0");
        } else {
            form.append('is_private', "1");
        }
        data.price_fiat = data.price_fiat.replaceAll(",",".")
        form.append('price_fiat', data.price_fiat);
        form.append('num_tokens_min_to_buy', data.num_tokens_min_to_buy);
        form.append('date_start', parseDateToUTC(data.date_start));
        form.append('date_end', parseDateToUTC(data.date_end));
        form.append('symbol_fiat', data.symbol_fiat);
        //si tiene id entonces es actualizar si no es uno nuevo
        if (data.update){
            return http.put("v1/private/invest/phases_mint/"+data.invest_id, form)
        } else {
            return http.post("v1/private/invest/phases_mint/" + data.invest_id, form)
        }
    }
    deletePhasesMint(invest_id, phase){
        return http.delete("v1/private/invest/phases_mint/"+invest_id+"/"+phase)
    }

    getInvestListActivityHistory({user_id = 0, page = 1, perPage = 10}){
        return http.get("v1/private/portfolio/activity?user_id="+user_id+"&page="+page+"&per_page="+perPage)
    }


    ///-----------------------------------------------------
    //  APORTACIONES DEL PROMOTOR
    //-----------------------------------------------------
    getInvestPromoterContributionList(invest_id){
        return http.get("v1/private/marketplace/promoter_contribution/list/"+invest_id)
    }
    saveInvestPromoterContribution(invest_id, num_tokens){
        return http.post("v1/private/marketplace/promoter_contribution/"+invest_id+"/"+num_tokens)
    }


    ///-----------------------------------------------------
    //  BENEFICIOS
    //-----------------------------------------------------
    getInvestProfits(invest_id){
        return http.get("v1/private/invest/profits/list/"+invest_id)
    }
    getInvestProfitsUser(profit_id){
        return http.get("v1/private/invest/profits/list/users/"+profit_id)
    }
    generateProfit(invest_id, profit){
        return http.post("v1/private/invest/profits/generate/"+invest_id+"/"+profit)
    }

    ///-----------------------------------------------------
    //  MARCAR PARA DESPLEGAR CONTRATO
    //-----------------------------------------------------
    markToDeploy(invest_id, status, deploy_state){
        const form = new FormData();
        form.append('status_invest', status);
        form.append('deploy_state', deploy_state);
        return http.put("v1/private/invest/phases_mint/mark_deploy/"+invest_id, form)
    }

}

export default new InvestServices();
