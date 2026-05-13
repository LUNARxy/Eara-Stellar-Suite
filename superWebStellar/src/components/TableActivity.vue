<template>

  <div class="table_wrapper_big">

    <PaginationDynamic :serviceFunction=get_activity_function :functionParams="list_params_paginated" :per-page="10" @update-items="updateItems">
      <template v-slot:default="{ items }">
        <table>
          <thead>
          <tr>
            <th>{{ $t('views.ID') }}</th>
            <th>{{ $t('views.Fecha') }}</th>
            <th>{{ $t('views.Proyecto') }}</th>
            <th>{{ $t('views.Fase') }}</th>
            <th>{{ $t('views.Tokens') }}</th>
            <th>{{ $t('views.Precio') }}</th>
            <th>{{ $t('views.Valor') }}</th>
            <th>{{ $t('views.Tipo') }}</th>
          </tr>
          </thead>

          <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{item.id}}</td>
            <td style="font-size: 0.8rem; width: 120px;">{{ formatDate(item.date_created) }}</td>
            <td><router-link :to="item.slug" class="color-base">{{item.invest_name}}</router-link></td>
            <td>{{ item.phase }}</td>
            <td>{{ myFormatNumber(item.num_tokens) }}</td>
            <td>{{ myFormatNumber(item.price_token, 9) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
            <td>{{ myFormatNumber(item.value, 2) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
            <td>
              <span v-if="item.type === USERS_INVEST_TYPE_BUY">{{ $t('views.Pago crypto') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_BUY_REJECTED">{{ $t('views.Compra rechazada') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_SALE_CANCELLED">{{ $t('views.Venta rechazada') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_PROFITS">{{ $t('views.Beneficios') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_PROFITS_CLAIM">{{ $t('views.Beneficios reclamados') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_PROFITS_RECEIVED">{{ $t('views.Beneficios recibidos') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_BUY_CANCELED">{{ $t('views.Compra tarjeta cancelada') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_BUY_ERROR">{{ $t('views.Compra tarjeta error') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_REFUND">{{ $t('views.Devolución de la inversión') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_REFUND_PARTIAL">{{ $t('views.Amortización de la inversión') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND">{{ $t('views.Devolución de la inversión') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_CLAIM">{{ $t('views.Retirada en proceso') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_RECEIVED">{{ $t('views.Retirada realizada') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_TO_INVEST">{{ $t('views.Invertido en proyecto') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED">{{ $t('views.Añadir fondos (pendiente de verificar)') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT && item.buy_subtype === DEPOSIT_SUBTYPE_CLOSE_PROJECT">{{ $t('views.Retirada de inversión en proyecto') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT && item.buy_subtype === DEPOSIT_SUBTYPE_ADD_BY_CRYPTO">{{ $t('views.Añadir fondos con Crypto') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT && item.buy_subtype === DEPOSIT_SUBTYPE_PROFITS">{{ $t('views.Rendimiento proyecto') }}</span>
              <span v-if="item.type === USERS_INVEST_TYPE_DEPOSIT && item.buy_subtype === DEPOSIT_SUBTYPE_REFERRAL">{{ $t('views.Usuarios referidos')}}</span>
            </td>
            <td>
              <a v-if="item.tx && item.type === USERS_INVEST_TYPE_BUY" :href="SCAN_URL + '/tx/' + item.tx" target="_blank"><img src="@/assets/img/polygon-matic-icon.png" class="ml-6" style="min-width: 40px; width: 40px"></a>
              <span v-if="item.show_ok" class="green-text">{{ $t("views.Transferencia verificada") }} ({{ $t('views.ID') }}: {{item.child_id}})</span>
              <span v-if="item.show_ko" class="red-text">{{ $t("views.Transferencia rechazada") }} ({{ $t('views.ID') }}: {{item.child_id}})</span>
            </td>
            <td style="text-align: right" v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_RECEIVED && item.parent_id">({{ $t('views.ID') }}: {{ item.parent_id }})</td>
            <td style="text-align: right" v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_CLAIM && item.child_id">({{ $t('views.ID') }}: {{item.child_id}})</td>
          </tr>
          </tbody>
        </table>
      </template>
    </PaginationDynamic>

  </div>




</template>

<script lang="ts">

import {Options, Vue} from "vue-class-component";
import {formatDateFromServer, formatNumber, showAlert, showAlertError} from "@/functions";
import UserServices from "@/services/UserServices";
import PaginationDynamic from "@/components/pagination/PaginationDynamic.vue";
import {
  USERS_INVEST_TYPE_BUY,
  USERS_INVEST_TYPE_BUY_REJECTED,
  USERS_INVEST_TYPE_PROFITS,
  USERS_INVEST_TYPE_PROFITS_CLAIM,
  USERS_INVEST_TYPE_PROFITS_RECEIVED,
  USERS_INVEST_TYPE_BUY_CANCELED,
  USERS_INVEST_TYPE_BUY_ERROR,
  USERS_INVEST_TYPE_SALE_CANCELLED,
  USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND,
  USERS_INVEST_TYPE_REFUND,
  USERS_INVEST_TYPE_DEPOSIT,
  USERS_INVEST_TYPE_DEPOSIT_CLAIM,
  USERS_INVEST_TYPE_DEPOSIT_RECEIVED,
  USERS_INVEST_TYPE_DEPOSIT_TO_INVEST,
  USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED,
  DEPOSIT_SUBTYPE_CLOSE_PROJECT,
  DEPOSIT_SUBTYPE_ADD_BY_CRYPTO,
  DEPOSIT_SUBTYPE_PROFITS,
  DEPOSIT_SUBTYPE_REFERRAL,
  USERS_INVEST_TYPE_REFUND_PARTIAL
} from "@/const"


@Options({
  components: {
    PaginationDynamic,
  },
})
export default class TableActivity extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  USERS_INVEST_TYPE_BUY = USERS_INVEST_TYPE_BUY
  USERS_INVEST_TYPE_BUY_REJECTED = USERS_INVEST_TYPE_BUY_REJECTED
  USERS_INVEST_TYPE_PROFITS = USERS_INVEST_TYPE_PROFITS
  USERS_INVEST_TYPE_PROFITS_CLAIM = USERS_INVEST_TYPE_PROFITS_CLAIM
  USERS_INVEST_TYPE_PROFITS_RECEIVED = USERS_INVEST_TYPE_PROFITS_RECEIVED
  USERS_INVEST_TYPE_BUY_CANCELED = USERS_INVEST_TYPE_BUY_CANCELED
  USERS_INVEST_TYPE_BUY_ERROR=USERS_INVEST_TYPE_BUY_ERROR
  USERS_INVEST_TYPE_SALE_CANCELLED = USERS_INVEST_TYPE_SALE_CANCELLED
  USERS_INVEST_TYPE_REFUND = USERS_INVEST_TYPE_REFUND
  USERS_INVEST_TYPE_REFUND_PARTIAL = USERS_INVEST_TYPE_REFUND_PARTIAL
  USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND = USERS_INVEST_TYPE_CLOSE_PROJECT_REFUND
  USERS_INVEST_TYPE_DEPOSIT = USERS_INVEST_TYPE_DEPOSIT
  USERS_INVEST_TYPE_DEPOSIT_CLAIM = USERS_INVEST_TYPE_DEPOSIT_CLAIM
  USERS_INVEST_TYPE_DEPOSIT_RECEIVED = USERS_INVEST_TYPE_DEPOSIT_RECEIVED
  USERS_INVEST_TYPE_DEPOSIT_TO_INVEST = USERS_INVEST_TYPE_DEPOSIT_TO_INVEST
  USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED = USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED

  DEPOSIT_SUBTYPE_CLOSE_PROJECT = DEPOSIT_SUBTYPE_CLOSE_PROJECT
  DEPOSIT_SUBTYPE_ADD_BY_CRYPTO = DEPOSIT_SUBTYPE_ADD_BY_CRYPTO
  DEPOSIT_SUBTYPE_PROFITS = DEPOSIT_SUBTYPE_PROFITS
  DEPOSIT_SUBTYPE_REFERRAL = DEPOSIT_SUBTYPE_REFERRAL

  // eslint-disable-next-line
  data_item: any = {}

  list_activity = []
  loading = false
  
  SCAN_URL = process.env.VUE_APP_SCAN_URL


  list_params_paginated = {}
  get_activity_function = UserServices.getUserInvestListActivityHistory

  mounted(){
      this.SCAN_URL = process.env.VUE_APP_SCAN_URL
  }

  updateItems(items){
    for (let item of items){
        item.slug = '/debt/'+item.slug

      //se busca si tiene parent_id
      if ((item.type === USERS_INVEST_TYPE_BUY || item.type === USERS_INVEST_TYPE_BUY_REJECTED ) && item.parent_id != null){
        for (let item2 of this.list_activity){
          if (item.parent_id == item2.id){
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

      for (let item2 of this.list_activity){
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
