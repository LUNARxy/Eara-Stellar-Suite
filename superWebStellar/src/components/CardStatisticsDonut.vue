<template>


  <div class="card pt-3 card-apex-padding-0" style="height: 100%">
    <h6 class="bold text-grey margin-3 ml-5">{{ $t('views.Distribución proyectos') }}</h6>
    <apexchart v-if="renderChart" :options="chart_my_invest_options" :series="chart_my_invest_values"></apexchart>
  </div>

</template>

<script lang="ts">

import {Options, Vue} from 'vue-class-component';
import M from "materialize-css";
import UserServices from "@/services/UserServices";
import {chartOptionsDonut, formatNumber} from "@/functions";
import store from "@/store";

@Options({
  props: {
    user_id: String,
  }
})
export default class CardStatisticsDonut extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  user_id

  //grafico donus
  renderChart = false
  chart_my_invest_values = []
  chart_my_invest_options = chartOptionsDonut()

  mounted () {
    M.AutoInit();

    UserServices.getUserInvestListMyInvestsActive()
        .then(response => {
          let list_my_invest = response.data;
          let list_my_invest_names = []
          let list_my_invest_values = []
          //let total_num_tokens = 0
          for (const item of list_my_invest) {
            list_my_invest_names.push(item.name+'<br>'+this.myFormatNumberConPunto(item.value)+this.VUE_APP_WHITE_LABEL_CURRENCY)
            list_my_invest_values.push(this.myFormatNumberConPunto(item.value))
            //total_num_tokens += item.value
          }

          this.chart_my_invest_values = list_my_invest_values
          this.chart_my_invest_options = {...this.chart_my_invest_options, ...{
              labels: list_my_invest_names,
            }}

          this.renderChart = true

          //this.$emit('update:total_num_tokens', total_num_tokens)
        })
  }
  myFormatNumberConPunto(val){
    let aux = formatNumber(val)
    aux = aux.replaceAll('.','')
    aux = aux.replaceAll(',','.')
    return parseFloat(aux)
  }
}

</script>
<style>
.apexcharts-legend.apx-legend-position-right {
  width: 30%!important;
}
</style>