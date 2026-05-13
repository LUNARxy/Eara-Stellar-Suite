import http from "./Http-common";


class InvestServices {

    getInvestListLimit(status = -1, limit = 6){
        return http.get("v1/private/invest/list?status_invest=" + status + "&category_id=2&limit=" + limit)
    }
    getInvestList(status = -1, get_all_info = false, is_in_white_list = false, is_in_follow = false){
        return http.get("v1/private/invest/list?status_invest=" + status + "&category_id=2&get_all_info=" + get_all_info + "&is_in_white_list=" + is_in_white_list + "&is_in_follow=" + is_in_follow)
    }
    getInvest(slug: string){
        return http.get("v1/private/invest/by_slug/"+slug)
    }
    getInvestActivity({invest_id = 0, page = 1, perPage = 10}){
        return http.get("v1/private/portfolio/activity?invest_id="+invest_id+"&page="+page+"&per_page="+perPage)
    }
    getInvestBalanceInvestProfitsList(invest_id = -1, user_id = -1, invest_child_id = -1){
        return http.get("v1/private/portfolio_nuevo/data_value_list?category_id=2&invest_id="+invest_id+"&user_id="+user_id+"&invest_child_id="+invest_child_id)
    }
    getInvestLastBalance(invest_id = -1, user_id = -1){
        return http.get("v1/private/portfolio_nuevo/data_percentage_value?type_value=0&category_id=2&invest_id="+invest_id+"&user_id="+user_id)
    }
    getInvestLastInvest(invest_id = -1, user_id = -1){
        return http.get("v1/private/portfolio_nuevo/data_percentage_value?type_value=1&category_id=2&invest_id="+invest_id+"&user_id="+user_id)
    }
    getInvestLastProfits(invest_id = -1, user_id = -1){
        return http.get("v1/private/portfolio_nuevo/data_percentage_value?type_value=2&category_id=2&invest_id="+invest_id+"&user_id="+user_id)
    }


    //-----------------------------------------------------
    //  FAVORITOS
    //-----------------------------------------------------
    postFollows(invest_id){
        return http.post("v1/private/follows/invest/"+invest_id)
    }
    deleteFollows(invest_id){
        return http.delete("v1/private/follows/invest/"+invest_id)
    }

}

export default new InvestServices();
