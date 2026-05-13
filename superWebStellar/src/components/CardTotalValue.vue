<template>

  <div :class="'mb-3 col s12 l'+numberColumns">
    <div class="card" style="height: 100%">
      <div class="card-content row pb-0">
        <div class="col s12">
          <p class="bold text-grey mb-1">
            <template v-if="type === 'balance'">{{ $t('views.Balance invertido') }}</template>
            <template v-if="type === 'invests'">{{ $t('views.Balance actual') }}</template>
            <template v-if="type === 'profits'">{{ $t('views.Rendimiento generado') }}</template>
          </p>
          <span class="bold mt-0 mb-0 mr-3 text_value">{{myFormatNumber(total_value)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
          <template v-if="percentage != 0">
            <span v-if="percentage < 0" :style="'color: '+color_percentage+'; font-size: 1.2rem;'"><i class="material-icons pt-2">arrow_drop_down</i></span>
            <span v-if="percentage > 0" :style="'color: '+color_percentage+'; font-size: 1.2rem;'"><i class="material-icons pt-2">arrow_drop_up</i></span>
            <span :style="'color: '+color_percentage+'; font-size: 1.2rem;'">{{ myFormatNumber(percentage) }}%</span>
          </template>
        </div>
      </div>
    </div>
  </div>

</template>

<script lang="ts">

import {Options, Vue} from 'vue-class-component';
import M from "materialize-css";
import {formatNumber} from "@/functions";
import InvestServices from "@/services/InvestServices";

@Options({
  props: {
    type: String,
    invest_id: Number,
    user_id: Number,
    numberColumns: {
      type: String,
      default: "4"
    },
    total_balance: Number
  }
})
export default class CardTotalValue extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  total_value = 0
  numberColumns
  type
  invest_id
  user_id
  color_percentage = ''
  percentage = 0
  total_balance

  mounted () {
    M.AutoInit();
    if (this.type === "invests") {
      InvestServices.getInvestLastInvest(this.invest_id, this.user_id)
          .then(response => {
            let data = response.data
            this.total_value = data.value
            this.percentage = data.percentage
            if (this.percentage < 0) {
              this.color_percentage = '#ff0000'
            } else {
              this.color_percentage = '#08DA05'
            }
          })
    } else if (this.type === "profits") {
      InvestServices.getInvestLastProfits(this.invest_id, this.user_id)
          .then(response => {
            let data = response.data
            this.total_value = data.value
            this.percentage = data.percentage
            if (this.percentage < 0) {
              this.color_percentage = '#ff0000'
            } else {
              this.color_percentage = '#08DA05'
            }
          })
    } else {
      InvestServices.getInvestLastBalance(this.invest_id, this.user_id)
          .then(response => {
            let data = response.data
            this.total_value = data.value
            this.percentage = data.percentage
            if (this.percentage < 0) {
              this.color_percentage = '#ff0000'
            } else {
              this.color_percentage = '#08DA05'
            }
          })
    }
  }

  myFormatNumber(val){
    return formatNumber(val)
  }
}

</script>
