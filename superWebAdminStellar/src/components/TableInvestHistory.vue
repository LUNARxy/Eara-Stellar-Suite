<template>

  <div class="row">
    <div class="col s12">

      <div class="col s12 padding-0 mb-3 text-center">
        <h4 class="col s12 text-center">{{ $t('views.Histórico de transacciones') }}</h4>
      </div>

      <div class="col s12 card padding-3">

        <div class="input-field col s12" v-if="user_id === '0'">
          <select class="browser-default" id="user_id_find" v-model="list_params_paginated.user_id" @change="get_activity_function">
            <option value="0">{{ $t('views.Ver todos los usuarios') }}</option>
            <option v-for="item in list_users_select" :key="item.id" :value="item.id">{{ item.email }} - {{ item.name }} {{ item.surname }}</option>
          </select>
        </div>


        <div class="card-content">

          <div class="row table_wrapper">
            <PaginationDynamic :serviceFunction=get_activity_function :functionParams="list_params_paginated" :per-page="10" @update-items="updateItems">
              <template v-slot:default="{ items }">
                <table>
                  <thead>
                  <tr>
                    <th>{{ $t('views.ID') }}</th>
                    <th>{{ $t('views.Fecha') }}</th>
                    <th>{{ $t('views.Proyecto') }}</th>
                    <th>{{ $t('views.Fase') }}</th>
                    <th v-if="user_id === '0'">{{ $t('views.Email') }}</th>
                    <th>{{ $t('views.N Tokens') }}</th>
                    <th>{{ $t('views.Precio') }}</th>
                    <th>{{ $t('views.Valor') }}</th>
                  </tr>
                  </thead>

                  <tbody>
                  <tr v-for="item in items" :key="item.id" :id="item.id">
                    <td>{{ item.id }}</td>
                    <td style="font-size: 0.8rem; width: 120px;">{{ formatDate(item.date_created) }}</td>
                    <td><router-link :to="item.slug" class="primary-color">{{item.invest_name}}</router-link></td>
                    <td>{{ item.phase }}</td>
                    <td v-if="user_id === '0'"><router-link :to="'/UserDetail/'+item.user_id">{{ item.email }}</router-link></td>
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
                    <td style="text-align: right" v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_RECEIVED && item.parent_id">({{ $t('views.ID') }}: {{ item.parent_id }})</td>
                    <td style="text-align: right" v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_CLAIM && item.child_id">({{ $t('views.ID') }}: {{item.child_id}})</td>
                    <td>
                      <a v-if="item.tx && item.type === USERS_INVEST_TYPE_BUY" :href="SCAN_URL + '/tx/' + item.tx" target="_blank"><img src="@/assets/img/polygon-matic-icon.png" class="ml-6" style="width: 40px;"></a>
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


</template>
<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import {formatDateFromServer, formatNumber, showAlertError} from "@/functions";
import InvestServices from "@/services/InvestServices";
import {
  USERS_INVEST_TYPE_BUY,
  USERS_INVEST_TYPE_BUY_REJECTED,
  USERS_INVEST_TYPE_PROFITS,
  USERS_INVEST_TYPE_PROFITS_CLAIM,
  USERS_INVEST_TYPE_PROFITS_RECEIVED,
  USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND,
  USERS_INVEST_TYPE_REFUND,
  USERS_INVEST_TYPE_DEPOSIT,
  USERS_INVEST_TYPE_DEPOSIT_CLAIM,
  USERS_INVEST_TYPE_DEPOSIT_RECEIVED,
  USERS_INVEST_TYPE_DEPOSIT_TO_INVEST,
  DEPOSIT_SUBTYPE_CLOSE_PROJECT,
  DEPOSIT_SUBTYPE_ADD_BY_CRYPTO,
  DEPOSIT_SUBTYPE_PROFITS,
  USERS_INVEST_TYPE_REFUND_PARTIAL,
} from "@/const"
import UserServices from "@/services/UserServices";
import PaginationDynamic from "@/components/pagination/PaginationDynamic.vue";

@Options({
  components: {PaginationDynamic},
  props: {
    user_id: String,
  }
})

export default class TableInvestHistory extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'
  SCAN_URL = process.env.VUE_APP_SCAN_URL


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


  list_history = []
  list_users_select = []
  loading = false
  user_id

  list_params_paginated = {
    user_id: 0,
  }
  get_activity_function = InvestServices.getInvestListActivityHistory


  beforeMount () {
    this.list_params_paginated.user_id = this.user_id
    if (this.user_id === '0') {
      UserServices.getUsersForSelect()
          .then(response => {
            this.list_users_select = response.data;
          })
    }
  }

  updateItems(items){
    for (let item of items){
      item.slug = '/InvestProjects/debt/' + item.invest_id

      for (let item2 of this.list_history){
        if (item.parent_id == item2.id){
          if (item.type == USERS_INVEST_TYPE_DEPOSIT_RECEIVED) {
            item2.child_id = item.id
          }
        }
      }
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
