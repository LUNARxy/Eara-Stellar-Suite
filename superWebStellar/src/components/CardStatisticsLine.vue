<template>

  <div class="card padding-3 card-apex-padding-0" style="height: 100%">
    <h6 class="bold text-grey margin-3" style="margin-bottom: 45px!important;">{{ $t('views.Estadísticas proyectos') }}</h6>
    <apexchart v-if="render_chart_balance_profits_final_values" type="area" :options="chart_balance_profits_final_values_config" height="300" :series="chart_balance_profits_final_values"></apexchart>
  </div>

</template>

<script lang="ts">

import {Options, Vue} from 'vue-class-component';
import M from "materialize-css";
import InvestServices from "@/services/InvestServices";
import {chartOptions, formatNumber} from "@/functions";

@Options({
  props: {
    invest_id: Number,
    invest_child_id: Number,
    user_id: Number,
  }
})
export default class CardStatisticsLine extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  invest_id
  invest_child_id
  user_id

  render_chart_balance_profits_final_values = false
  chart_balance_profits_final_values_config
  chart_balance_profits_final_values = []

  total_balance = 0

  mounted () {
    M.AutoInit();

    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    InvestServices.getInvestBalanceInvestProfitsList(this.invest_id, this.user_id, this.invest_child_id)
        .then(response => {
          let lists_server = response.data
          let chart_xaxis = []
          let list_balance = []
          for (let balance of lists_server.list_balance){
            list_balance.push(parseFloat(balance.value+"").toFixed(2))
            chart_xaxis.push(balance.date_created)
            this.total_balance = balance.value
          }

          let list_profits = []
          for (let profits of lists_server.list_profits){
            let val = parseFloat(profits.value+"").toFixed(2)
            list_profits.push(val)
          }
          let list_final_values = []
          for (let final_values of lists_server.list_final_values){
            list_final_values.push(parseFloat(final_values.value+"").toFixed(2))
          }

          this.chart_balance_profits_final_values_config = chartOptions(chart_xaxis)

          this.chart_balance_profits_final_values.push(
              {
                name: self.$t("views.Balance invertido"),
                data: list_balance
              })

          let txt = self.$t("views.Balance actual")
          this.chart_balance_profits_final_values.push(
              {
                name: txt,
                data: list_final_values
              })


          this.chart_balance_profits_final_values.push(
              {
                name: self.$t("views.Rendimiento generado"),
                data: list_profits
              })

          this.render_chart_balance_profits_final_values = true
        })
  }
  myFormatNumber(val){
    return formatNumber(val)
  }
}

</script>
