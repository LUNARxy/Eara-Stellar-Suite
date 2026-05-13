<template>

  <div v-if="table.length > 0" class="row margin-0 padding-0 padding-0">
    <div class="col s12">
      <div class="row card" style="padding: 0 20px 20px 20px!important;">


        <div class="display-flex col s12 mt-3 mb-2 padding-0 hide-on-med-and-down">
          <div class="col s1 bold">&nbsp;</div>
          <div class="col s2 bold">{{ $t('views.Proyecto') }}</div>
          <div class="col s1 bold">{{ $t('views.Estado') }}</div>
          <div class="col s2 bold text-right">{{ $t('views.N tokens') }}</div>
          <div class="col s2 bold text-right">
            <span>{{ $t('views.Balance invertido') }}</span>
          </div>

          <div class="col s2 bold text-right">{{ $t('views.Rendimiento acumulado') }}</div>
          <div class="col s2 bold text-right">
            <span>{{ $t('views.Valor inversión') }}</span>
          </div>
        </div>



        <div v-for="(item, itemObjKey) in table" :key="item.id">
          <div :id="id+'_'+itemObjKey" @click="expandTable(id+'_'+itemObjKey)" class="table-line-project col s12 padding-1 hand border-radius-15 mt-3">


            <div class="display-flex hide-on-med-and-down">
              <div class="col s12 m1"><img :src="PUBLIC_URL + item.file" class="responsive-img" style="max-height: 100%; border-radius: 15px;margin-top: 6px;"></div>
              <div class="col s12 m2">{{item.name}}</div>
              <div class="col s12 m1">
                <span v-if="item.status === INVEST_STATUS_FINANCING_PHASE">{{ $t('views.Fase de financiación') }}</span>
                <span v-if="item.status === INVEST_STATUS_IN_PROGRESS">{{ $t('views.En curso') }}</span>
                <span v-if="item.status === INVEST_STATUS_FINISHED">{{ $t('views.Finalizado') }}</span>
              </div>
              <div class="col s12 m2 text-right">{{item.num_tokens_mine}}</div>
              <div class="col s12 m2 text-right">
                {{myFormatNumber(item.total_balance)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}<br>
              </div>
              <div class="col s12 m2 text-right">
                {{myFormatNumber(item.total_profits)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}<br>
              </div>
              <div class="col s12 m2 text-right">
                {{myFormatNumber(item.total_final_values)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}<br>
              </div>
            </div>




            <div class="display-flex hide-on-large-only pt-3 pb-3">
              <div class="col s3"><img :src="PUBLIC_URL + item.file" class="responsive-img" style="max-height: 100%; border-radius: 15px;margin-top: 6px;"></div>
              <div class="col s9 padding-0 margin-0">
                <div class="col s12 padding-0 margin-0"><span class="bold">{{item.name}}</span></div>
                <div class="col s12 padding-0 margin-0">{{ $t('views.Estado') }}:
                  <span v-if="item.status === INVEST_STATUS_FINANCING_PHASE">{{ $t('views.Fase de financiación') }}</span>
                  <span v-if="item.status === INVEST_STATUS_IN_PROGRESS">{{ $t('views.En curso') }}</span>
                  <span v-if="item.status === INVEST_STATUS_FINISHED">{{ $t('views.Finalizado') }}</span>
                </div>
                <div class="col s12 padding-0 margin-0">{{ $t('views.Categoría') }}:
                  <span>{{ $t('views.Deuda') }}</span>
                </div>
                <div class="col s12 padding-0 margin-0">{{ $t('views.N tokens') }}: {{item.num_tokens_mine}}</div>
                <div class="col s12 padding-0 margin-0">
                  <span>{{ $t('views.Balance invertido') }}</span>
                  : {{myFormatNumber(item.total_balance)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}
                </div>
                <div class="col s12 padding-0 margin-0">{{ $t('views.Rendimiento acumulado') }}: {{myFormatNumber(item.total_profits)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}
                </div>
                <div class="col s12 padding-0 margin-0">
                  <span>{{ $t('views.Valor inversión') }}</span>
                  : {{myFormatNumber(item.total_final_values)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}
                </div>
              </div>
            </div>
          </div>
          <div :id="'data_'+id+'_'+itemObjKey" style="display: none">
            <div class="row">

              <div v-if="item.status === INVEST_STATUS_FINISHED" class="col s12 padding-0 mt-2">
                <div class="col s12 ">
                  <div class="card bg-grey padding-3 text-center">
                    <h6 class="text-center">{{ $t('views.Proyecto finalizado') }}</h6>
                    <p>{{ $t('views.El proyecto se ha completado y se ha efectuado una devolución a su favor de la inversión inicial por una cantidad_', {value: myFormatNumber(item.refund_value), currency: VUE_APP_WHITE_LABEL_CURRENCY}) }}</p>
                  </div>
                </div>
              </div>


              <div class="col s12 padding-0 mt-1">
                <div :class="'col s12 '+class_col_chart_total_balance">
                  <div class="card bg-grey card-apex-padding-10" style="box-shadow: initial;">
                    <div class="card-content">
                      <h6 class="text-grey mb-1">{{ $t('views.Balance') }}</h6>
                      <span class="bold mt-0 mb-0 mr-3" style="font-size: 2rem;">{{myFormatNumber(item.total_balance)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
                    </div><br>
                    <apexchart type="area" :options="item.chart_last_invest_balance_config" :series="item.chart_last_invest_balance" height="250"></apexchart>
                  </div>
                </div>

                <div class="col s12 m6">
                  <div class="card bg-grey card-apex-padding-10" style="box-shadow: initial;">
                    <div class="card-content">
                      <h6 class="text-grey mb-1">{{ $t('views.Rendimiento') }}</h6>
                      <span class="bold mt-0 mb-0 mr-3" style="font-size: 2rem;">{{myFormatNumber(item.total_profits)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
                    </div><br>
                    <apexchart type="area"  :options="item.chart_last_invest_profit_config" :series="item.chart_last_invest_profits"></apexchart>
                  </div>
                </div>
              </div>


              <div class="col s12">
                <div class="card bg-grey padding-5 pt-3" style="box-shadow: initial;">
                  <h6 class="text-center">{{ $t('views.Histórico de inversiones') }}</h6>
                  <div class="row mt-3 table_wrapper">
                    <table>
                      <thead>
                      <tr>
                        <th>{{ $t('views.ID') }}</th>
                        <th>{{ $t('views.Fase') }}</th>
                        <th>{{ $t('views.Tipo') }}</th>
                        <th>{{ $t('views.Fecha') }}</th>
                        <th>{{ $t('views.N de tokens') }}</th>
                        <th>{{ $t('views.Precio token') }}</th>
                        <th>{{ $t('views.Cantidad total') }}</th>
                      </tr>
                      </thead>

                      <tbody>
                      <tr v-for="my_invest in item.list_invest_buy" :key="my_invest.id">
                        <td>{{ my_invest.id }}</td>
                        <td>{{ my_invest.phase }}</td>
                        <td v-if="my_invest.profit_id == null">Inversión</td>
                        <td v-if="my_invest.profit_id != null">Reinversión</td>
                        <td>{{ formatDate(my_invest.date_created) }}</td>
                        <td>{{ myFormatNumber(my_invest.num_tokens) }}</td>
                        <td>{{ myFormatNumber(my_invest.price_token, 9) }}</td>
                        <td>{{ myFormatNumber(my_invest.value) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                      </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>



              <div class="col s12" v-if="item.list_invest_buy_market.length > 0">
                <div class="card bg-grey padding-5 pt-3" style="box-shadow: initial;">
                  <h6 class="text-center">{{ $t('views.Tokens comprados en Marketplace') }}</h6>
                  <div class="row mt-3 table_wrapper">
                    <table>
                      <thead>
                      <tr>
                        <th>{{ $t('views.Fecha') }}</th>
                        <th>{{ $t('views.Precio/Token') }}</th>
                        <th>{{ $t('views.N tokens') }}</th>
                        <th>{{ $t('views.Balance total') }}</th>
                      </tr>
                      </thead>
                      <tbody>
                      <tr v-for="buy in item.list_invest_buy_market" :key="buy.phase">
                        <td>{{ formatDate(buy.date_created) }}</td>
                        <td>{{ myFormatNumber(buy.price_token, 9) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                        <td>{{ myFormatNumber(buy.num_tokens) }}</td>
                        <td>{{ myFormatNumber(buy.num_tokens * buy.price_token)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                      </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>


              <div class="col s12" v-if="item.list_invest_sold.length > 0">
                <div class="card bg-grey padding-5 pt-3" style="box-shadow: initial;">
                  <h6 class="text-center">{{ $t('views.Tokens vendidos en Marketplace') }}</h6>
                  <div class="row mt-3 table_wrapper">
                    <table>
                      <thead>
                      <tr>
                        <th>{{ $t('views.Fecha') }}</th>
                        <th>{{ $t('views.Precio/Token') }}</th>
                        <th>{{ $t('views.N tokens') }}</th>
                        <th>{{ $t('views.Balance total') }}</th>
                      </tr>
                      </thead>
                      <tbody>
                      <tr v-for="sale in item.list_invest_sold" :key="sale.phase">
                        <td>{{ formatDate(sale.date_created) }}</td>
                        <td>{{ myFormatNumber(sale.price_token, 9) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                        <td>{{ myFormatNumber(sale.num_tokens) }}</td>
                        <td>{{ myFormatNumber((sale.num_tokens * sale.price_token))}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                      </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>


              <div class="col s12 padding-0">

                <div v-if="item.list_user_invest_refund_platform.length > 0" class="col s12">
                  <div class="card bg-grey padding-5 pt-3" style="box-shadow: initial;">
                    <h6 class="text-center">{{ $t('views.Retiradas de inversión') }}</h6>
                    <div class="row mt-3 table_wrapper">
                      <table>
                        <thead>
                        <tr>
                          <th>{{ $t('views.Fecha') }}</th>
                          <th>{{ $t('views.Concepto') }}</th>
                          <th>{{ $t('views.Valor') }}</th>
                        </tr>
                        </thead>

                        <tbody>
                        <tr v-for="refund in item.list_user_invest_refund_platform" :key="refund.id">
                          <td>{{ formatDate(refund.date_created) }}</td>
                          <td>{{ $t('views.white_label_name')}}_{{refund.id}}</td>
                          <td>{{ myFormatNumber(refund.value) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                        </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

                <div v-if="item.list_history_profits?.length > 0" class="col s12">
                  <div class="card bg-grey padding-5 pt-3" style="box-shadow: initial;">
                    <h6 class="text-center">{{ $t('views.Rendimientos generados') }}</h6>
                    <div class="row mt-3 table_wrapper">
                      <table>
                        <thead>
                        <tr>
                          <th>{{ $t('views.Fecha') }}</th>
                          <th>{{ $t('views.Concepto') }}</th>
                          <th>{{ $t('views.Rendimiento') }}</th>
                        </tr>
                        </thead>

                        <tbody>
                        <tr v-for="profit in item.list_history_profits" :key="profit.id">
                          <td>{{ formatDate(profit.date_created) }}</td>
                          <td v-if="profit.type !== USERS_INVEST_TYPE_SOLD">{{ $t('views.Reparto') }}</td>
                          <td v-if="profit.type === USERS_INVEST_TYPE_SOLD">{{ $t('views.Venta') }}</td>
                          <td>{{ myFormatNumber(profit.profit_value) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                        </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

                <div class="col s12">
                  <div class="card bg-grey padding-5 pt-3" style="box-shadow: initial;">
                    <h6 class="text-center">{{ $t('views.Fases de financiación') }}</h6>
                    <div class="row mt-3 table_wrapper">
                      <table>
                        <thead>
                        <tr>
                          <th>{{ $t('views.Fase') }}</th>
                          <th>{{ $t('views.Inicio') }}</th>
                          <th>{{ $t('views.Fin') }}</th>
                          <th>{{ $t('views.N de tokens') }}</th>
                          <th>{{ $t('views.Precio token') }}</th>
                          <th>{{ $t('views.Cantidad fase') }}</th>
                        </tr>
                        </thead>

                        <tbody>
                        <tr v-for="mint_phases in item.list_mint_phases" :key="mint_phases.phase">
                          <td>{{ mint_phases.phase }}</td>
                          <td>{{ formatDate(mint_phases.date_start) }}</td>
                          <td>{{ formatDate(mint_phases.date_end) }}</td>
                          <td>{{ myFormatNumber(mint_phases.max_tokens) }}</td>
                          <td>{{ myFormatNumber(mint_phases.price_fiat, 9) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                          <td>{{ myFormatNumber(mint_phases.max_tokens*mint_phases.price_fiat)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                        </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

                <div v-if="item.list_status_description.length > 0" class="col s12">
                  <div class="card bg-grey padding-5 pt-3" style="box-shadow: initial;">
                    <h6 class="text-center">{{ $t('views.Estado del proyecto') }}</h6>
                    <p class="row mt-3" v-for="status_description in item.list_status_description" :key="status_description.id">
                      <span class="col s12 mt-2">{{status_description.description}}</span>
                      <span class="col s12 text-right mt-2" style="font-size: 0.8rem;">{{ formatDate(status_description.date_created) }}</span>
                      <br>
                    </p>
                  </div>
                </div>
              </div>

              <div class="col s12">
                <router-link :to="item.slug">
                  <p class="text-center"><button type="button" class="btn-primary">{{ $t('views.Ver proyecto') }}</button></p>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>


</template>

<script lang="ts">

import {Options, Vue} from 'vue-class-component';
import {formatDateFromServer, formatNumber} from "@/functions";
import {PUBLIC_URL} from "@/services/Http-common";
import {
  INVEST_STATUS_FINANCING_PHASE,
  INVEST_STATUS_FINISHED,
  INVEST_STATUS_IN_PROGRESS,
  USERS_INVEST_TYPE_SOLD,
} from "@/const";

@Options({
  props: {
    table: Array,
    id: String,
  }
})

export default class TableMyProjects extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'
  id
  table
  user_id = "0"

  PUBLIC_URL = PUBLIC_URL


  INVEST_STATUS_FINANCING_PHASE = INVEST_STATUS_FINANCING_PHASE
  INVEST_STATUS_IN_PROGRESS = INVEST_STATUS_IN_PROGRESS
  INVEST_STATUS_FINISHED = INVEST_STATUS_FINISHED

  USERS_INVEST_TYPE_SOLD = USERS_INVEST_TYPE_SOLD

  loading = false

  class_col_chart_total_balance = 'm6'

  mounted () {
    this.user_id = this.$route.params.id?.toString()
  }

  expandTable(id){
    //se cierran todos y se ponen en blanco
    let elementsOpen = document.getElementsByClassName('table-line-project')
    for (let element of elementsOpen) {
      document.getElementById(element.id)?.classList.remove("bg-grey")
      if ('data_' + element.id != 'data_'+id) {
        const data_item = document.getElementById('data_' + element.id)
        if (data_item != null) {
          data_item.style.display = 'none'
        }
      }
    }

    //se abre y se pone en gris o se cierra y se poen en blanco
    const data_item = document.getElementById('data_'+id)
    if (data_item != null) {
      if (data_item.style.display == 'none') {
        data_item.style.display = ''
        document.getElementById(id)?.classList.add("bg-grey")
      } else {
        data_item.style.display = 'none'
        data_item.classList.remove("bg-grey")
      }
    }
  }
  formatDate(date) {
    return formatDateFromServer(date)
  }

  myFormatNumber(val, decimals = 2){
    return formatNumber(val, decimals)
  }

}




</script>
