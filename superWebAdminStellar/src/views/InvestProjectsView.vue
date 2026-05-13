<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="col s12 padding-0 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Proyecto') }}: {{data_item.name}}</h4>
        </div>
      </div>
    </div>


    <div class="row">
      <div class="col s12 m4">
        <CardInvest v-if="data_loaded" :data_item="data_item" :show_all_buttons="true"/>
      </div>

      <div class="col s12 m8">

        <div class="row mb-0">
          <div class="col s12 padding-0" style=" display: flex; flex-wrap: wrap; clear: both;">
            <CardTotalValue v-if="data_loaded" type="balance" :invest_id="list_params_paginated.invest_id"/>
            <CardTotalValue v-if="data_loaded" type="invests" :invest_id="list_params_paginated.invest_id"/>
            <CardTotalValue v-if="data_loaded" type="profits" :invest_id="list_params_paginated.invest_id"/>
          </div>

          <div class="col s12 padding-0">
            <div class="col s12">
              <CardStatisticsLine v-if="data_loaded" :invest_id="data_item.id" :category_invest="data_item.category_id"/>
            </div>
          </div>
        </div>





        <div class="col s12 padding-0 mb-1" style=" display: flex; flex-wrap: wrap; clear: both;">
          <div class="col s6 l6">
            <div class="card" style="height: 100%">
              <div class="card-content row pb-0">
                <div class="col s12">
                  <p class="bold text-grey mb-1">{{ $t('views.Usuarios en whitelist') }}</p>
                  <span class="bold mt-0 mb-0 mr-3 text_value">{{total_distinct_user_whitelist}}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="list_params_paginated.invest_id == 11" class="col s6 l6">
            <div class="card pb-0" style="height: 100%">
              <div class="card-content row">
                <div class="col s12">
                  <p class="bold text-grey mb-1">{{ $t('views.Usuarios inversores') }}</p>
                  <span class="bold mt-0 mb-0 mr-3 text_value">{{data_item.investors}} {{ $t('views.Usuarios') }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col s12 padding-0 mb-1" style=" display: flex; flex-wrap: wrap; clear: both;">
          <div class="col s6 l6">
            <div class="card" style="height: 100%">
              <div class="card-content row pb-0">
                <div class="col s12">
                  <p class="bold text-grey mb-1">{{ $t('views.Inversiones pendientes de verificar') }}</p>
                  <span class="bold mt-0 mb-0 mr-3 text_value">{{myFormatNumber(total_invest_pending)}}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="col s6 l6">
            <div class="card pb-0" style="height: 100%">
              <div class="card-content row">
                <div class="col s12">
                  <p class="bold text-grey mb-1">{{ $t('views.Inversiones verificadas') }}</p>
                  <span class="bold mt-0 mb-0 mr-3 text_value">{{myFormatNumber(total_invest_verified)}}</span>
                </div>
              </div>
            </div>
          </div>
        </div>


      </div>
    </div>

    <div class="row">
      <div class="col s12">
        <div class="col s12 padding-0 mb-3 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Histórico de transacciones') }}</h4>
        </div>

        <div class="col s12 card padding-3">

          <div class="card-content">

            <div class="row table_wrapper_big">
              <PaginationDynamic :serviceFunction=get_activity_function :functionParams="list_params_paginated" :per-page="10" @update-items="updateItems">
                <template v-slot:default="{ items }">
                  <table>
                    <thead>
                    <tr>
                      <th>{{ $t('views.ID') }}</th>
                      <th>{{ $t('views.Fecha') }}</th>
                      <th>{{ $t('views.Fase') }}</th>
                      <th>{{ $t('views.Email') }}</th>
                      <th>{{ $t('views.N tokens') }}</th>
                      <th>{{ $t('views.Precio') }}</th>
                      <th>{{ $t('views.Valor') }}</th>
                      <th>{{ $t('views.Tipo') }}</th>
                    </tr>
                    </thead>

                    <tbody>

                    <tr v-for="item in items" :key="item.id">
                      <td>{{item.id}}</td>
                      <td style="font-size: 0.8rem; width: 120px;">{{ formatDate(item.date_created) }}</td>
                      <td>{{ item.phase }}</td>
                      <td><router-link :to="'/UserDetail/'+item.user_id">{{ item.email }}</router-link></td>
                      <td>{{ myFormatNumber(item.num_tokens) }}</td>
                      <td>{{ myFormatNumber(item.price_token, 9) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                      <td>{{ myFormatNumber(item.value, 2) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                      <td>
                        <span v-if="item.type === USERS_INVEST_TYPE_BUY">{{ $t('views.Pago cripto') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_BUY_REJECTED">{{ $t('views.Compra rechazada') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_PROFITS">{{ $t('views.Beneficios') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_PROFITS_CLAIM">{{ $t('views.Beneficios reclamados') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_PROFITS_RECEIVED">{{ $t('views.Beneficios recibidos') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_REFUND">{{ $t('views.Devolución de la inversión') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_REFUND_PARTIAL">{{ $t('views.Amortización de la inversión') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND">{{ $t('views.Devolución de la inversión') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_CLAIM">{{ $t('views.Retirada en proceso') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_RECEIVED">{{ $t('views.Retirada realizada') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_TO_INVEST">{{ $t('views.Invertido en proyecto') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT && item.buy_subtype === DEPOSIT_SUBTYPE_CLOSE_PROJECT">{{ $t('views.Retirada de inversión en proyecto') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT && item.buy_subtype === DEPOSIT_SUBTYPE_ADD_BY_CRYPTO">{{ $t('views.Añadir fondos con Crypto') }}</span>
                        <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT && item.buy_subtype === DEPOSIT_SUBTYPE_PROFITS">{{ $t('views.Rendimiento proyecto') }}</span>
                      </td>


                    </tr>
                    </tbody>
                  </table>
                </template>
              </PaginationDynamic>
            </div>



          </div>
        </div>
      </div>
    </div>




  </div>
</template>



<script lang="ts">
import InvestServices from '@/services/InvestServices'
import {Options, Vue} from "vue-class-component";
import Menu from "@/components/Menu.vue";
import {
  formatDateFromServer,
  formatNumber,
  showAlertError,
} from "@/functions";

import CardInvest from "@/components/CardInvest.vue";
import UserServices from "@/services/UserServices";
import {
  USERS_INVEST_TYPE_BUY,
  USERS_INVEST_TYPE_BUY_REJECTED,
  USERS_INVEST_TYPE_PROFITS,
  USERS_INVEST_TYPE_PROFITS_CLAIM,
  USERS_INVEST_TYPE_PROFITS_RECEIVED,
  USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND,
  USERS_INVEST_TYPE_DEPOSIT,
  USERS_INVEST_TYPE_DEPOSIT_CLAIM,
  USERS_INVEST_TYPE_DEPOSIT_RECEIVED,
  USERS_INVEST_TYPE_DEPOSIT_TO_INVEST,
  USERS_INVEST_TYPE_REFUND,
  USERS_INVEST_TYPE_REFUND_PARTIAL,
  DEPOSIT_SUBTYPE_CLOSE_PROJECT,
  DEPOSIT_SUBTYPE_ADD_BY_CRYPTO,
  DEPOSIT_SUBTYPE_PROFITS,
} from "@/const";
import {PUBLIC_URL} from "@/services/Http-common";
import PaginationDynamic from "@/components/pagination/PaginationDynamic.vue";
import CardTotalValue from "@/components/CardTotalValue.vue";
import CardStatisticsLine from "@/components/CardStatisticsLine.vue";


@Options({
  components: {
    CardStatisticsLine,
    CardTotalValue,
    PaginationDynamic,
    CardInvest,
    Menu,
  },
})
export default class InvestProjectsView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  PUBLIC_URL = PUBLIC_URL

  USERS_INVEST_TYPE_BUY = USERS_INVEST_TYPE_BUY
  USERS_INVEST_TYPE_BUY_REJECTED = USERS_INVEST_TYPE_BUY_REJECTED
  USERS_INVEST_TYPE_PROFITS = USERS_INVEST_TYPE_PROFITS
  USERS_INVEST_TYPE_PROFITS_CLAIM = USERS_INVEST_TYPE_PROFITS_CLAIM
  USERS_INVEST_TYPE_PROFITS_RECEIVED = USERS_INVEST_TYPE_PROFITS_RECEIVED
  USERS_INVEST_TYPE_REFUND = USERS_INVEST_TYPE_REFUND
  USERS_INVEST_TYPE_REFUND_PARTIAL = USERS_INVEST_TYPE_REFUND_PARTIAL
  USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND = USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND
  USERS_INVEST_TYPE_DEPOSIT = USERS_INVEST_TYPE_DEPOSIT
  USERS_INVEST_TYPE_DEPOSIT_CLAIM = USERS_INVEST_TYPE_DEPOSIT_CLAIM
  USERS_INVEST_TYPE_DEPOSIT_RECEIVED = USERS_INVEST_TYPE_DEPOSIT_RECEIVED
  USERS_INVEST_TYPE_DEPOSIT_TO_INVEST = USERS_INVEST_TYPE_DEPOSIT_TO_INVEST

  DEPOSIT_SUBTYPE_CLOSE_PROJECT = DEPOSIT_SUBTYPE_CLOSE_PROJECT
  DEPOSIT_SUBTYPE_ADD_BY_CRYPTO = DEPOSIT_SUBTYPE_ADD_BY_CRYPTO
  DEPOSIT_SUBTYPE_PROFITS = DEPOSIT_SUBTYPE_PROFITS


  list_investors = []

  // eslint-disable-next-line
  data_item: any = {}

  total_distinct_user_invest = 0
  total_distinct_user_whitelist = 0
  total_invest_pending = 0
  total_invest_verified = 0
  data_loaded = false
  loading = false

  nav = 0

  list_params_paginated = {
    invest_id: 0,
  }
  col_nav = 'l6'

  get_activity_function = InvestServices.getInvestActivity

  beforeMount () {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this


    if (this.$route.params.id !== undefined) {
      this.list_params_paginated.invest_id = parseInt(this.$route.params.id+"")

      if (this.$route.params.id != 11){
        this.col_nav = 'l12'
      }

      InvestServices.getInvestProject(this.$route.params.id.toString(), false, true)
          .then(response => {
            this.data_item = response.data;
            this.data_item.category_name = 'debt'
            this.data_loaded = true
            this.getData()
          })
          .catch(function (error) {
            showAlertError(error, self, function () {
              self.$router.go(-1)
            });
          });
    }
  }

  getData(){

    if (this.$route.params.id) {
      UserServices.getUsersWhiteListCount(this.$route.params.id)
          .then(response => {
            this.total_distinct_user_whitelist = response.data
          })

      InvestServices.getInvestTotalsPendingVerifiedAndVerified(this.$route.params.id)
          .then(response => {
            this.total_invest_pending = response.data.total_invest_pending
            this.total_invest_verified = response.data.total_invest_verified
          })
    }
  }


  updateItems(items){
    for (let item of items){
      let arr_distinct_user_invest = []

      if (arr_distinct_user_invest.indexOf(item.email) === -1) {
        arr_distinct_user_invest.push(item.email);
      }

      //se busca si tiene parent_id y si tiene no se muestran los botones de aceptar y rechazar transaccion
      if ((item.type === USERS_INVEST_TYPE_BUY || item.type === USERS_INVEST_TYPE_BUY_REJECTED) && item.parent_id != null) {
        for (let item2 of this.list_investors) {
          if (item.parent_id == item2.id) {
            if (item.type == USERS_INVEST_TYPE_BUY) {
              item2.show_ok = true
              item2.show_ko = false
              item2.child_id = item.id
            } else if (item.type == USERS_INVEST_TYPE_BUY_REJECTED) {
              item2.show_ok = false
              item2.show_ko = true
              item2.child_id = item.id
            }
          }
        }
      }
      this.total_distinct_user_invest = arr_distinct_user_invest.length
    }
  }

  myFormatNumber(val, decimals = 2){
    return formatNumber(val, decimals)
  }

  formatDate(date) {
    return formatDateFromServer(date)
  }
}

</script>
