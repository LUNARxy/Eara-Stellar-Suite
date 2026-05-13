<template>


  <div class="row">
    <div class="col s12">
      <div class="card row padding-10px margin-0">
        <ul id="tabs_2" class="tabs">
          <li class="tab"><a class="pl-7 pr-7" href="#tab_12">{{ $t('views.Todos los proyectos') }}</a></li>
          <li class="tab"><a class="pl-7 pr-7" href="#tab_22">{{ $t('views.Fase de financiación') }}</a></li>
          <li class="tab"><a class="pl-7 pr-7" href="#tab_32">{{ $t('views.Proyectos en curso') }}</a></li>
          <li class="tab"><a class="pl-7 pr-7" href="#tab_42">{{ $t('views.Proyectos finalizados') }}</a></li>
        </ul>
      </div>

      <div id="tab_12" class="col s12 padding-0" style="display: block">
        <TableMyProjects :table="list_items_all" id="all2"/>
      </div>
      <div id="tab_22" class="col s12 padding-0">
        <TableMyProjects :table="list_items_1" id="list_12"/>
      </div>
      <div id="tab_32" class="col s12 padding-0">
        <TableMyProjects :table="list_items_2" id="list_22"/>
      </div>
      <div id="tab_42" class="col s12 padding-0">
        <TableMyProjects :table="list_items_3" id="list_32"/>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import M from "materialize-css";
import TableMyProjects from "@/components/dashboard/TableMyProjects.vue";
import {chartOptions, formatDateFromServer, formatNumber, reInitTabs} from "@/functions";

import UserServices from "@/services/UserServices";


@Options({
  components: {
    TableMyProjects,
  },
  props: {
    total_profits_month: Number
  }
})

export default class CardMyProjects extends Vue {

  list_items_all = []
  list_items_1 = []
  list_items_2 = []
  list_items_3 = []

  beforeMount () {
    M.AutoInit();

    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    UserServices.getDataTablePortfolio()
        .then(response => {
          let data = response.data;

          let total_profits_month = 0

          //recorremos la lista para distribuirla
          for (let element of data.list_invest) {

            // se recogen las fases del proyecto
            for (let element_extra_data of data.list_extra_data) {
              if (element.id == element_extra_data.invest_id){
                element.list_mint_phases = element_extra_data.list_mint_phases
                element.list_profits_to_chart = element_extra_data.list_profits_to_chart
                element.list_history_profits = element_extra_data.list_profits
                element.list_balance = element_extra_data.list_balance_profits_final_value.list_balance
                element.list_final_values = element_extra_data.list_balance_profits_final_value.list_final_values
                element.list_status_description = element_extra_data.list_status_description
              }
            }

            // se calculan los totales con la suma de las compras en phases, compras a usuarios y ventas
            element.num_tokens_mine = 0
            element.value_tokens_mine = 0
            element.list_invest_buy = []
            for (let element_user_invest_buy of data.list_user_invest_buy_platform) {
              if (element.id == element_user_invest_buy.invest_id){
                element.num_tokens_mine = element.num_tokens_mine + element_user_invest_buy.num_tokens
                element.value_tokens_mine = element.value_tokens_mine + (element_user_invest_buy.num_tokens * element_user_invest_buy.price_token)
                //se pone en la lista de tokens comparators
                element.list_invest_buy.push(element_user_invest_buy)
              }
            }
            element.list_invest_buy_market = []
            if (data.list_user_invest_buy_other_users != undefined) {
              for (let element_user_invest_other_users of data.list_user_invest_buy_other_users) {
                if (element.id == element_user_invest_other_users.invest_id) {
                  element.num_tokens_mine = element.num_tokens_mine + element_user_invest_other_users.num_tokens
                  element.value_tokens_mine = element.value_tokens_mine + (element_user_invest_other_users.num_tokens * element_user_invest_other_users.price_token)
                  //para la lista de tokens comprados a otros usuarios
                  element.list_invest_buy_market.push(element_user_invest_other_users)
                }
              }
            }
            element.list_invest_sold = []
            if (data.list_user_invest_sold != undefined) {
              for (let user_invest_sold of data.list_user_invest_sold) {
                if (element.id == user_invest_sold.invest_id) {
                  element.num_tokens_mine = element.num_tokens_mine - user_invest_sold.num_tokens
                  element.value_tokens_mine = element.value_tokens_mine - (user_invest_sold.num_tokens * user_invest_sold.price_token)
                  //para la lista de tokens vendidos a otros usuarios
                  element.list_invest_sold.push(user_invest_sold)
                }
              }
            }
            element.list_user_invest_refund_platform = []
            if (data.list_user_invest_refund_platform != undefined) {
              for (let user_invest_refund of data.list_user_invest_refund_platform) {
                if (element.id == user_invest_refund.invest_id) {
                  element.num_tokens_mine = element.num_tokens_mine - user_invest_refund.num_tokens
                  element.value_tokens_mine = element.value_tokens_mine - (user_invest_refund.num_tokens * user_invest_refund.price_token)
                  //para la lista de tokens que me han devuelto
                  element.list_user_invest_refund_platform.push(user_invest_refund)
                }
              }
            }

            let acumulated = 0
            if (element.list_history_profits != undefined) {
              for (let profit of element.list_history_profits) {
                profit.profit_value -= acumulated
                acumulated += profit.profit_value
              }
            }


            // ponemos los datos para la grafica de balance
            let list_balance = []
            let chart_last_invest_balance_xaxis = []
            for (let users_invest_buy_and_sold of element.list_balance){
              list_balance.push(users_invest_buy_and_sold.value.toFixed(2))
              chart_last_invest_balance_xaxis.push(formatDateFromServer(users_invest_buy_and_sold.date_created))
            }

            // los totales
            if (list_balance.length > 0) element.total_balance = list_balance[list_balance.length-1]

            element.percentage_balance = 0
            if (list_balance.length > 1) {
              // Toma los dos últimos valores de la lista ordenada
              const totalBack_balance = list_balance[list_balance.length-2]
              let percentage_balance = 0
              if (element.total_balance == 0) {
                percentage_balance = element.total_balance
              } else {
                percentage_balance = ((element.total_balance * 100 / totalBack_balance) - 100)
              }
              if (percentage_balance < 0) {
                element.color_percentage_balance = '#ff0000'
              } else {
                element.color_percentage_balance = '#08DA05'
              }
              element.percentage_balance = percentage_balance
            }


            // ponemos los datos para la grafica de final_values
            let list_final_values = []
            for (let final_values of element.list_final_values){
              list_final_values.push(final_values.value.toFixed(2))
            }

            // los totales
            if (list_final_values.length > 0) element.total_final_values = list_final_values[list_final_values.length-1]

            element.percentage_final_values = 0
            if (list_final_values.length > 1) {
              let percentage_final_values = ((element.total_final_values - element.total_balance) / element.total_balance) * 100
              if (percentage_final_values < 0) {
                element.color_percentage_final_values = '#ff0000'
              } else {
                element.color_percentage_final_values = '#08DA05'
              }
              element.percentage_final_values = percentage_final_values
            }


            element.chart_last_invest_balance_config = chartOptions(chart_last_invest_balance_xaxis)


            // para la grafica de rendimiento
            let list_profit = []
            let chart_last_invest_profits_xaxis = []
            for (let profit of element.list_profits_to_chart) {
              if (element.id == profit.invest_id) {
                if (profit.profit_value != undefined) {
                  list_profit.push(profit.profit_value?.toFixed(2))
                } else {
                  list_profit.push(profit.value?.toFixed(2))
                }
                chart_last_invest_profits_xaxis.push(formatDateFromServer(profit.date_created))
              }
            }
            element.total_profits = list_profit[list_profit.length - 1]
            element.percentage_profit = 0
            if (list_profit.length > 1) {
              let percentage_profit = 0;
              if (parseFloat(element.total_balance) > 0) percentage_profit = (element.total_profits / element.total_balance) * 100
              if (percentage_profit < 0) {
                element.color_percentage_profit = '#ff0000'
              } else {
                element.color_percentage_profit = '#08DA05'
              }
              element.percentage_profit = percentage_profit
            }
            element.chart_last_invest_profit_config = chartOptions(chart_last_invest_profits_xaxis)
            element.chart_last_invest_profits = [{
              name: self.$t('views.Rendimiento'),
              data: list_profit
            }]

            //para los proyectos de interés que se saca el valor del rendimiento mensual
            if (list_profit.length == 1) {
              element.total_profits_month = list_profit[0]
            } else if (list_profit.length > 1) {
              element.total_profits_month = list_profit[list_profit.length-1]-list_profit[list_profit.length-2]
            } else {
              element.total_profits_month = 0
            }
            total_profits_month += element.total_profits_month

            element.chart_last_invest_balance = []
            element.chart_last_invest_balance.push(
                {
                  name: self.$t("views.Balance invertido"),
                  data: list_balance
                })

            let txt = self.$t("views.Balance actual")
            element.chart_last_invest_balance.push(
                {
                  name: txt,
                  data: list_final_values
                })


            element.chart_last_invest_balance.push(
                {
                  name: self.$t("views.Rendimiento generado"),
                  data: list_profit
                })

            let last_phase = element.list_mint_phases[element.list_mint_phases.length - 1]
            if (last_phase != null){
              // para la Valoración del proyecto
              let total_num_tokens  = 0
              for (let phase of element.list_mint_phases) {
                total_num_tokens += parseInt(phase.max_tokens.toString())
              }
              element.total_value_tokens_txt = formatNumber(last_phase.price_fiat * total_num_tokens)
              element.total_num_tokens_txt = formatNumber(total_num_tokens)
              element.last_price_fiat_txt = formatNumber(last_phase.price_fiat)
            }

            for (let phase of element.list_mint_phases){
              phase.num_tokens_mine = 0
              phase.value_tokens_mine = 0
              //se calculan los tokens y su valor en cada fase
              for (let element_user_invest_buy of data.list_user_invest_buy_platform) {
                if (element.id == element_user_invest_buy.invest_id && phase.phase == element_user_invest_buy.phase){
                  phase.num_tokens_mine = phase.num_tokens_mine + element_user_invest_buy.num_tokens
                  phase.value_tokens_mine = phase.value_tokens_mine + (element_user_invest_buy.num_tokens * element_user_invest_buy.price_token)
                  phase.contracts = element_user_invest_buy.contracts
                }
              }
            }



            element.num_tokens_mine = formatNumber(element.num_tokens_mine)
            element.value_tokens_mine = formatNumber(element.value_tokens_mine)
            element.slug = '/debt/' + element.slug

            //para las pestañas de los listados
            if (element.status == 2){
              this.list_items_1.push(element)
            } else if (element.status == 3){
              this.list_items_2.push(element)
            } else if (element.status == 99){
              this.list_items_3.push(element)
            }
          }

          this.list_items_all = data.list_invest
          this.$emit('update:total_profits_month', total_profits_month)

        })

  }

  mounted(){
    // las tabs de material con vue no funcionan bien, hay que poner esto para reiniciarlas
    reInitTabs('tabs2', 'tab_12')
  }

}
</script>
