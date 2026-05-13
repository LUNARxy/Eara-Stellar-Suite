<template>
  <MenuUser/>
  <div class="content_menu">

    <div class="col s12 mb-3 text-center">
      <h4 class="mt-0">{{ $t('views.Wallet virtual') }}</h4>
    </div>


    <div class="row">
      <div class="col s12" style=" display: flex; flex-wrap: wrap; clear: both;">
        <div class="col s12 m6">
          <div class="card" style="height: 100%">
            <div class="card-content">
              <p class="bold text-grey mb-1">{{ $t('views.Balance virtual') }}</p>
              <span class="bold mt-0 mb-0 mr-3 text_value">{{ myFormatNumber(value_wallet) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
            </div>
          </div>
        </div>
        <div class="col s12 hide-on-med-and-up">&nbsp;</div>
        <div class="col s12 m6">
          <div class="card" style="height: 100%">
            <div class="card-content">
              <p class="bold text-grey mb-1">{{ $t('views.Retiradas verificadas') }}</p>
              <span class="bold mt-0 mb-0 mr-3 text_value">{{ myFormatNumber(value_received) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
            </div>
          </div>
        </div>
      </div>
    </div>


    <div class="row pb-0">
      <div class="col s12 text-center">
        <h4>{{ $t('views.Registro de actividad wallet') }}</h4>
      </div>
    </div>

    <div class="row">
      <div class="col s12">
        <div class="col s12">
          <div class="card table_wrapper_big pl-3 pr-3">
            <table>
              <thead>
              <tr>
                <th>{{ $t('views.ID') }}</th>
                <th>{{ $t('views.Fecha') }}</th>
                <th>{{ $t('views.Proyecto') }}</th>
                <th>{{ $t('views.Tipo') }}</th>
                <th style="text-align: right">{{ $t('views.Valor') }}</th>
                <th>{{ $t('views.N cuenta') }}</th>
                <th></th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="item in list_activity" :key="item.id">
                <td>{{ item.id }}</td>
                <td style="font-size: 0.8rem; width: 120px;">{{ formatDate(item.date_created) }}</td>
                <td>{{ item.project_name }}</td>
                <td v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_CLAIM">{{ $t('views.Retirada en proceso') }}</td>
                <td v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_RECEIVED">{{ $t('views.Retirada realizada') }}</td>
                <td v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_TO_INVEST">{{ $t('views.Invertido en proyecto') }}</td>
                <td v-if="item.type === USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED">{{ $t('views.Añadir fondos (pendiente de verificar)') }}</td>
                <td v-if="item.type === USERS_INVEST_TYPE_DEPOSIT && item.buy_subtype === DEPOSIT_SUBTYPE_CLOSE_PROJECT">{{ $t('views.Retirada de inversión en proyecto') }}</td>
                <td v-if="item.type === USERS_INVEST_TYPE_DEPOSIT && item.buy_subtype === DEPOSIT_SUBTYPE_ADD_BY_CRYPTO">{{ $t('views.Añadir fondos con Crypto') }}</td>
                <td v-if="item.type === USERS_INVEST_TYPE_DEPOSIT && item.buy_subtype === DEPOSIT_SUBTYPE_PROFITS">{{ $t('views.Rendimiento proyecto') }}</td>
                <td v-if="item.type === USERS_INVEST_TYPE_DEPOSIT && item.buy_subtype === DEPOSIT_SUBTYPE_REFERRAL">{{ $t('views.Usuarios referidos')}}</td>
                <td style="text-align: right">{{ myFormatNumber(item.value) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                <td>{{ item.iban }}</td>
                <td style="text-align: right" v-if="item.parent_id">({{ $t('views.ID') }}: {{ item.parent_id }})</td>
                <td style="text-align: right" v-if="item.child_id">({{ $t('views.ID') }}: {{item.child_id}})</td>
                <td v-if="item.type === USERS_INVEST_TYPE_DEPOSIT && item.buy_subtype === DEPOSIT_SUBTYPE_PROFITS">
                  <button type="button" class="btn-primary mt-2" @click="refund" :disabled="loading">{{ $t('views.Retirar fondos') }}</button>
                </td>
              </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>


    <Footer />
  </div>
</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import M from "materialize-css";
import MenuUser from "@/components/dashboard/MenuUser.vue";
import Footer from "@/components/Footer.vue";
import {
  checkKYCValid, formatDateFromServer,
  formatNumber, showAlert, showAlertError,
} from "@/functions";
import TableActivity from "@/components/TableActivity.vue";
import UserServices from "@/services/UserServices";
import {
  DEPOSIT_SUBTYPE_ADD_BY_CRYPTO,
  DEPOSIT_SUBTYPE_CLOSE_PROJECT,
  DEPOSIT_SUBTYPE_PROFITS,
  DEPOSIT_SUBTYPE_REFERRAL,
  USERS_INVEST_TYPE_DEPOSIT,
  USERS_INVEST_TYPE_DEPOSIT_CLAIM,
  USERS_INVEST_TYPE_DEPOSIT_RECEIVED,
  USERS_INVEST_TYPE_DEPOSIT_TO_INVEST,
  USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED
} from "@/const";
import store from "@/store";
import {Locales} from "@/locales/locales";


@Options({
  components: {
    TableActivity,
    Footer,
    MenuUser,
  },
})
export default class WalletBlockchainView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'
  USERS_INVEST_TYPE_DEPOSIT = USERS_INVEST_TYPE_DEPOSIT
  USERS_INVEST_TYPE_DEPOSIT_CLAIM = USERS_INVEST_TYPE_DEPOSIT_CLAIM
  USERS_INVEST_TYPE_DEPOSIT_RECEIVED = USERS_INVEST_TYPE_DEPOSIT_RECEIVED
  USERS_INVEST_TYPE_DEPOSIT_TO_INVEST = USERS_INVEST_TYPE_DEPOSIT_TO_INVEST
  USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED = USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED

  DEPOSIT_SUBTYPE_CLOSE_PROJECT = DEPOSIT_SUBTYPE_CLOSE_PROJECT
  DEPOSIT_SUBTYPE_ADD_BY_CRYPTO = DEPOSIT_SUBTYPE_ADD_BY_CRYPTO
  DEPOSIT_SUBTYPE_PROFITS = DEPOSIT_SUBTYPE_PROFITS
  DEPOSIT_SUBTYPE_REFERRAL = DEPOSIT_SUBTYPE_REFERRAL


  loading = false
  list_activity = []

  value_put_money = 0
  value_refund = 0
  user_iban = ''
  user_iban_hover = ''

  value_wallet = 0
  value_received = 0
  value_claim = 0
  value_without_verified = 0




  mounted() {
    M.AutoInit();
    let elems = document.querySelectorAll('.tooltipped');
    M.Tooltip.init(elems);

    checkKYCValid(this)
  }

  getData(){
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    UserServices.getMyIBANNumber()
        .then(response => {
          this.user_iban = response.data
          this.user_iban_hover = response.data

          if (this.user_iban == ''){
            showAlert(this.$t('views.Datos Bancarios wallet'), this.$t('server.No se han encontrado datos bancarios'), false, function () {
              self.$router.push('/userDetail')
            })
          } else {
            this.user_iban = this.user_iban.slice(-20)+"..."
          }
        })
        .catch(error => {
          showAlertError(error, self);
        })


    UserServices.getDataWalletUser()
        .then(response => {
          this.list_activity = response.data

          for (let item of this.list_activity) {
            if (store.getters.getLocale == Locales.EN) {
              item.project_name = item.project_name_EN
            }

            if (item.type === this.USERS_INVEST_TYPE_DEPOSIT){
              this.value_wallet += item.value
            } else if (item.type === this.USERS_INVEST_TYPE_DEPOSIT_CLAIM){
              this.value_claim += item.value
              this.value_wallet -= item.value
            } else if (item.type === this.USERS_INVEST_TYPE_DEPOSIT_RECEIVED){
              this.value_received += item.value
              //this.value_wallet -= item.value
              this.value_claim -= item.value
            } else if (item.type === this.USERS_INVEST_TYPE_DEPOSIT_TO_INVEST){
              this.value_wallet -= item.value
            } else if (item.type === this.USERS_INVEST_TYPE_DEPOSIT_WITHOUT_VERIFIED){
              this.value_claim += item.value
            }

            for (let item2 of this.list_activity){
              if (item.parent_id == item2.id){
                if (item.type == USERS_INVEST_TYPE_DEPOSIT_RECEIVED) {
                  item2.child_id = item.id
                }
              }
            }
          }
        })
        .catch(error => {
          showAlertError(error, self);
        })
  }


  refund(){
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    if (!isNaN(this.value_refund) && this.value_refund > 0) {
      showAlert(self.$t('views.Retirada de fondos'), self.$t('views.Estás a punto de solicitar la retirada de _', {value: this.value_refund, user_iban: this.user_iban, currency: this.VUE_APP_WHITE_LABEL_CURRENCY}), true, function () {
        UserServices.saveRefundWallet(self.value_refund)
            .then(response => {
              showAlert("", self.$t('views.Se ha guardado correctamente'), false, function () {
                self.$router.go(0)
              })
            })
            .catch(error => {
              showAlertError(error, self, function () {
                self.$router.go(0)
              })
            })
      })
    }
  }

  myFormatNumber(val){
    return formatNumber(val)
  }

  formatDate(date) {
    return formatDateFromServer(date)
  }
}
</script>

