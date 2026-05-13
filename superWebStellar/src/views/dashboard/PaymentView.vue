<template>
  <Header v-if="!isLoggedIn"/>

  <MenuUser v-if="isLoggedIn"/>


  <div class="content_menu">

    <div class="row">
      <div class="col s12 m4">
        <div class="card col s12" style="padding: 10px!important;">
          <img class="border-radius-15 responsive-img" :src="data_item.file">
          <div class="row mt-5">

            <div class="col s12 mt-2">
              <div class="col s6">
                <div class="div_icono_texto">
                  <i class="material-icons primary-color mr-2" style="font-size: 0.8rem">lens</i><span class="black-text">{{ $t('views.Objetivo') }}</span>
                </div>
              </div>
              <div class="col s6 text-right">
                <span id="value_round">{{ myFormatNumber(data_item.value_round)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
              </div>
            </div>
            <div class="col s12 mt-2">
              <div class="col s6">
                <div class="div_icono_texto">
                  <i class="material-icons primary-color mr-2" style="font-size: 0.8rem">lens</i><span class="black-text">{{ $t('views.Cantidad disponible') }}</span>
                </div>
              </div>
              <div class="col s6 text-right">
                  <span id="remaining_tokens_value">
                    <span v-if="data_item.phase === 'all'">0{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
                    <span v-if="data_item.phase !== 'all'">{{ data_item.remaining_tokens_value_txt }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
                  </span>
              </div>
            </div>


            <div v-if="data_item.contract_address != null" class="col s12 mt-2">
              <div class="col s12">
                <div class="div_icono_texto">
                  <i class="material-icons primary-color mr-2" style="font-size: 0.8rem">lens</i><span class="black-text">{{ $t('views.Dirección del contrato') }}</span>
                </div>
              </div>
              <div class="col s12 text-right">
                <span>{{ data_item.contract_address }}</span>
              </div>
            </div>
            <div v-if="data_item.location != null" class="col s12 mt-2">
              <div class="col s12">
                <div class="div_icono_texto">
                  <i class="material-icons primary-color mr-2" style="font-size: 0.8rem">lens</i><span class="black-text">{{ $t('views.Dirección') }}</span>
                </div>
              </div>
              <div class="col s12 text-right">
                <span>{{ data_item.location }}</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div class="col s12 m8">
        <div class="card" style="padding: 10px;">
          <div class="col s12 border-radius-15 pb-10" :style="{backgroundImage: 'url(' + data_item.file_top + ')', backgroundSize: 'cover', backgroundRepeat: 'no-repeat'}">
            <div class="col s12 text-center pt-3" style="text-shadow: 1px 1px 10px #000000;">
              <h4 class="white-text invest-detail-name">{{ data_item.name }}</h4>
              <p class="col s12 padding-3 pt-0 white-text">{{ data_item.title }}</p>
            </div>
          </div>

          <div class="row">
            <div class="col s12 padding-3 mt-3 mb-0">

              <div class="text-center">
                <h5>{{ $t('views.Compra de tokens del proyecto') }}</h5>
                <p>{{ $t('views.Número de tokens a comprar') }} ({{ $t('views.mínimo') }} {{myFormatNumber(data_item.num_tokens_min_to_buy)}} y {{ $t('views.máximo') }} {{myFormatNumber(data_item.num_tokens_max_to_buy)}}):</p>
                <div class="col s12">
                  <button type="button" class="btn-secondary mr-2" @click="changePrice(-1)">
                    <span type="button" style="padding: 8px 14px;">
                      <i class="material-icons">remove</i>
                    </span>
                  </button>
                  <input type="text" id="num_tokens" name="num_tokens" v-model="data_form.num_tokens" @change="calculatePrice()" required style="width: 80px;text-align: center; ">
                  <button type="button" class="btn-secondary ml-2" @click="changePrice(1)">
                    <span type="button" style="padding: 8px 14px;">
                      <i class="material-icons">add</i>
                    </span>
                  </button>
                </div>
                <p class="col s12 mt-3">{{ $t('views.Precio del token') }}: {{myFormatNumber(data_item.price_token)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</p>

                <h6 class="col s12 bold mb-4 mt-3">{{ $t('views.Importe de la inversión') }}: {{myFormatNumber(invest_price)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</h6>

                <div v-if="loading" class="progress">
                  <div class="indeterminate"></div>
                </div>


              </div>




            </div>
          </div>
        </div>

        <div v-if="!buy_ok" class="card padding-10px">
          <div class="row margin-0">
            <div class="col s12 margin-0 padding-0">
              <ul id="tabs" class="tabs">
                <li class="tab"><a href="#tab_buy_crypto"  >{{ $t('views.PAGO CRYPTO') }}</a></li>
              </ul>
            </div>
          </div>
        </div>

        <div v-if="!buy_ok" class="card" style="padding: 20px;">
          <div class="row">
            <div class="input-field col s12 text-center">
              <div id="tab_buy_wallet" style="display: none">
                <div class="input-field col s12 text-center">
                  <p>{{ $t('views.Balance disponible en mi wallet virtual') }}: {{ myFormatNumber(balance) }}</p>
                  <p class="mt-3" v-if="balance >= (this.data_item.price_token * this.data_form.num_tokens)">{{ $t('views.Para realizar la compra de los tokens a través de este método de pago deberás pulsar el siguiente botón para invertir con los fondos de tu Wallet virtual') }}</p>
                  <p class="mt-3" v-if="balance < (this.data_item.price_token * this.data_form.num_tokens)">{{ $t('views.El balance de tu Wallet virtual es inferior a la cantidad que deseas invertir Puedes cargar tu Wallet virtual o elegir otro método de pago para realizar la operación')}}</p>
                  <button v-if="!is_contract_signed || balance >= (this.data_item.price_token * this.data_form.num_tokens)" :disabled="loading" @click="buyTokensAlert('virtual')" class="btn-primary mt-3">{{ $t('views.Comprar tokens') }}</button>
                </div>
              </div>

              <div id="tab_buy_crypto" style="display: none">
                <!-- Stellar payment UI -->
                <div>
                  <h6 class="col s12 bold mb-4 mt-3">{{ $t('views.Importe total') }}: {{myFormatNumber(invest_price_crypto)}} {{token_selected}}</h6>
                  <p class="mb-5">{{ $t('views.Para realizar la compra de tokens a través de Stellar deberás conectar tu wallet Freighter y confirmar la transacción') }}</p>
                </div>

                <button v-if="!is_contract_signed" :disabled="loading" @click="buyTokensAlert('crypto')" class="btn-primary mt-3">{{ $t('views.Realizar pago') }}</button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>




    <Footer />

  </div>

</template>


<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import Header from "@/components/Header.vue"
import Footer from "@/components/Footer.vue";

import store from "@/store";
import MenuUser from "@/components/dashboard/MenuUser.vue";
import InvestServices from "@/services/InvestServices";
import UserServices from "@/services/UserServices";
import {
  checkKYCValid,
  formatDateFromServer,
  formatNumber,
  showAlert,
  showAlertError, showAlertKYC,
} from "@/functions";
import {Locales} from "@/locales/locales";
import {PUBLIC_URL} from "@/services/Http-common";

import ContractDataService from "@/services/ContractDataService";
import { stellarService } from "@/services/stellar/StellarService";
import { stellarConfig } from "@/services/stellar/StellarConfig";
import type { StellarSignatureResponse } from "@/services/stellar/StellarTypes";
import JQuery from "jquery";


@Options({
  components: {
    MenuUser,
    Header,
    Footer,
  },
})
export default class PaymentView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  invest_id
  isLoggedIn = store.getters.isLoggedIn

  kyc_valid = 1
  kyc_no_valid_reason = ''


  buy_ok = false

  // eslint-disable-next-line
  data_item: any = {}

  data_form = {"invest_id":0, "num_tokens":0, "payment_method": "", "signature_documents_id": 0}
  loading = false
  invest_price = 0
  invest_price_crypto = 0
  remaining_tokens = 0
  is_contract_signed = true
  signature_documents_id = 0
  signature_tokens = 0

  balance = 0

  token_selected = ""
  token_data: any[] = []

  beforeMount () {
    this.invest_id = this.$route.params.id.toString()
    if (this.invest_id === undefined || this.invest_id == ""){
      this.$router.push('/')
    }
    if (!this.isLoggedIn){
      this.$router.push('/login/go_back')
    }
  }

  mounted(){
    checkKYCValid(this)

    this.is_contract_signed = store.getters.getSignatureData?.status == 'completed'
    this.signature_documents_id = store.getters.getSignatureData?.id
    if (store.getters.getSignatureData?.num_tokens) {
      this.signature_tokens = store.getters.getSignatureData?.num_tokens
    }
  }

  getData(){

    if (this.kyc_valid != 1){
      showAlertKYC()
      return;
    }

    this.loading = true

    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    InvestServices.getInvest(this.$route.params.slug.toString())
        .then(response => {
          this.loading = false

          this.data_item = response.data;
          //console.log(response.data)

          //para poder comprar el proyecto tiene que estar en el estado adecuado
          if ((this.data_item.has_white_list && this.data_item.preference_to_buy === this.data_item.phase) || !this.data_item.has_white_list) {
            this.remaining_tokens = this.data_item.remaining_tokens-this.data_item.waiting_tokens
            if (this.remaining_tokens <= 0) {
              showAlert(this.$t("views.Error al comprar tokens"), this.$t('views.Antes de que realizases la compra de los tokens, otro usuario ha comprado todos los tokens del proyecto'), false, function () {
                self.$router.push('/project/' + self.$route.params.slug.toString())
              })
            } else if (this.data_item.num_tokens_max_to_buy != null && this.data_item.num_tokens_max_to_buy <= 0) {
              showAlert(this.$t("views.Error al comprar tokens"), this.$t('server.Has supererado el máximo de inversión en el proyecto'), false, function () {
                self.$router.push('/project/' + self.$route.params.slug.toString())
              })
            } else {

              //se pone por defecto el ticket mínimo
              this.data_form.num_tokens = this.signature_tokens
              if (this.data_item.num_tokens_max_to_buy == null || this.data_item.num_tokens_max_to_buy > this.data_item.remaining_tokens) {
                this.data_item.num_tokens_max_to_buy = this.data_item.remaining_tokens
              }

              this.data_item.file = PUBLIC_URL + this.data_item.file
              this.data_item.file_top = PUBLIC_URL+this.data_item.file_top
              this.data_item.sold_tokens_value_txt = formatNumber(this.data_item.sold_tokens_value)

              if (store.getters.getLocale == Locales.EN){
                this.data_item.name = this.data_item.name_EN
                this.data_item.title = this.data_item.title_EN
                this.data_item.summary = this.data_item.summary_EN
                this.data_item.description = this.data_item.description_EN
                this.data_item.proposal_to_investors = this.data_item.proposal_to_investors_EN
                this.data_item.time_limit = this.data_item.time_limit_EN
              }
              this.data_item.num_tokens_txt = formatNumber(this.data_item.num_tokens)
              this.data_item.remaining_tokens_txt = formatNumber(this.data_item.remaining_tokens)
              this.data_item.remaining_tokens_value_txt = formatNumber(this.data_item.remaining_tokens*this.data_item.price_token)
              this.data_item.investors = formatNumber(this.data_item.investors)

              this.data_item.collected = (((this.data_item.sold_tokens_value))*100/this.data_item.value_round)
              if (isNaN(this.data_item.collected)) this.data_item.collected = 0

              this.data_item.date_start_round = formatDateFromServer(this.data_item.date_start_round, true)
              this.data_item.date_end_round = formatDateFromServer(this.data_item.date_end_round, true)
              if (this.data_item.date_end !== null) {
                this.data_item.date_end = formatDateFromServer(this.data_item.date_end, true)
              } else {
                this.data_item.date_end = null
              }

              this.desenfoque()
            }
          } else {
            //no esta en el estado correcto para poder comprar
            self.$router.push('/project/' + self.$route.params.slug.toString())
          }
        })


    UserServices.getUserWalletBalance()
        .then(response => {
          this.balance = response.data
        })

    // For Stellar, use the configured asset (XLM by default or custom token)
    this.token_data = []
    this.token_selected = stellarConfig.assetCode || "XLM"
    this.changeSelectedCrypto()


    let tab = document.getElementById("tab_buy_crypto")
    if (tab != null) tab.style.display = 'block'

  }

  desenfoque(){
    //si esta marcado el check de poner borrosa la cuenta atrás
    if (this.data_item.hide_time_data){
      JQuery('#card_date_back').hide()
    }
    if (this.data_item.hide_date_start_round){
      this.data_item.date_start_round = "yyyy-mm-dd"
      JQuery('#date_start_round').addClass('desenfoque')
    }
    if (this.data_item.hide_date_end_round){
      this.data_item.date_end_round = "yyyy-mm-dd"
      JQuery('#date_end_round').addClass('desenfoque')
    }
    if (this.data_item.hide_profit_estimated_description){
      this.data_item.profit_estimated_description = "00000000"
      JQuery('#profit_estimated_description').addClass('desenfoque')
    }
    if (this.data_item.hide_value_round){
      this.data_item.value_round = "00000000"
      JQuery('#value_round').addClass('desenfoque')
    }
    if (this.data_item.hide_num_tokens){
      this.data_item.num_tokens = "00000000"
      JQuery('#num_tokens_txt').addClass('desenfoque')
      this.data_item.remaining_tokens_txt = "00000000"
      this.data_item.remaining_tokens_value_txt = "00000000"
      JQuery('#remaining_tokens').addClass('desenfoque')
      JQuery('#remaining_tokens_value').addClass('desenfoque')
    }
  }

  changePrice(add_or_subtraction){
    let val = parseInt(this.data_form.num_tokens?.toString())
    if (isNaN(val)) val = 1
    val += add_or_subtraction;
    if (val <= 0) val = 1
    this.data_form.num_tokens = val
    if (val < this.data_item.num_tokens_min_to_buy){
      val = this.data_item.num_tokens_min_to_buy
      this.data_form.num_tokens = this.data_item.num_tokens_min_to_buy
    }

    if (val > this.remaining_tokens){
      val = this.remaining_tokens
      this.data_form.num_tokens = this.remaining_tokens
    }

    if (this.data_item.num_tokens_max_to_buy != null) {
      if (val > this.data_item.num_tokens_max_to_buy) {
        val = this.data_item.num_tokens_max_to_buy
        this.data_form.num_tokens = this.data_item.num_tokens_max_to_buy
      }
    }

    this.invest_price = this.data_item.price_token * val

    this.changeSelectedCrypto()
  }
  calculatePrice(){
    let val = parseInt(this.data_form.num_tokens?.toString())
    if (isNaN(val)) val = 0
    if (val < 0) val = 0

    if (val < this.data_item.num_tokens_min_to_buy){
      val = this.data_item.num_tokens_min_to_buy
      this.data_form.num_tokens = this.data_item.num_tokens_min_to_buy
    }

    if (val > this.remaining_tokens){
      val = this.remaining_tokens
      this.data_form.num_tokens = this.remaining_tokens
    }

    if (this.data_item.num_tokens_max_to_buy != null) {
      if (val > this.data_item.num_tokens_max_to_buy) {
        val = this.data_item.num_tokens_max_to_buy
        this.data_form.num_tokens = this.data_item.num_tokens_max_to_buy
      }
    }

    this.invest_price = this.data_item.price_token * val

    this.changeSelectedCrypto()
  }


  buyTokensAlert(type_buy){

    if (this.kyc_valid != 1){
      showAlertKYC()
      return;
    }

    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    this.data_form.payment_method = type_buy

    if (isNaN(this.data_form.num_tokens) || this.data_form.num_tokens == 0
        || this.data_form.num_tokens > this.data_item.remaining_tokens){
      showAlert("","El número de tokens no es correcto")
      return
    } else if (this.data_item.num_tokens_min_to_buy == this.data_item.remaining_tokens && this.data_form.num_tokens < this.data_item.remaining_tokens) {
      showAlert("", "El número de tokens no es correcto, el ticket mínimo es: " + this.data_item.remaining_tokens)
      return
    }

    if (this.data_form.payment_method === "virtual") {
      const price = parseFloat(this.invest_price.toString().replace(/\./g, '').replace(',', '.'))
      if (price > this.balance) {
        showAlert(this.$t('views.Compra de tokens'), this.$t('views.No tienes suficiente saldo para comprar los tokens'), false)
        return
      }
    }

    showAlert(this.$t('views.Compra de tokens'), this.$t('views.Estas seguro de que quieres comprar_', { num_tokens: self.data_form.num_tokens, total_value: self.invest_price, currency: this.VUE_APP_WHITE_LABEL_CURRENCY}), true, function() {
      self.buyTokens()
    })
  }

  async buyTokens() {

    if (this.kyc_valid != 1){
      showAlertKYC()
      return;
    }

    if (isNaN(this.data_form.num_tokens) || this.data_form.num_tokens == 0
        || this.data_form.num_tokens > this.data_item.remaining_tokens){
      showAlert("","El número de tokens no es correcto")
    } else if (this.data_item.num_tokens_min_to_buy == this.data_item.remaining_tokens && this.data_form.num_tokens < this.data_item.remaining_tokens) {
      showAlert("", "El número de tokens no es correcto, el ticket mínimo es: " + this.data_item.remaining_tokens)
    } else if (!this.data_form.payment_method.length) {
      showAlert("", "Seleccione un método de pago")
    } else {
      this.loading = true
      this.data_form.invest_id = this.invest_id
      this.data_form.signature_documents_id = this.signature_documents_id || 0

      if (!this.token_selected){
        showAlertError(this.$t('Debe seleccionar una stable coin'), this)
        this.loading = false
        return
      }

      // Use Stellar payment
      await this.buyTokensWithStellar()
    }
  }



  myFormatNumber(val){
    return formatNumber(val)
  }


  changeSelectedCrypto() {
    this.invest_price_crypto = this.invest_price
  }

  async buyTokensWithStellar() {
    if (this.kyc_valid != 1) {
      showAlertKYC()
      return
    }

    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    try {
      // Initialize Stellar service (idempotent)
      await stellarService.initialize()

      // Ensure wallet is connected
      let walletConnection = await stellarService.checkWalletConnection()
      if (!walletConnection) {
        walletConnection = await stellarService.connectWallet()
      }
      if (!walletConnection) {
        showAlertError(this.$t('No se pudo conectar la wallet de Freighter (Stellar)'), this)
        this.loading = false
        return
      }

      const callerAddress = walletConnection.address

      // Fetch backend signature (amount, payment_amount, nonce, uid, sig, etc.)
      const sigResponse = await ContractDataService.getTokenMintSignatureStellar(
          this.invest_id,
          callerAddress,
          this.data_form.num_tokens,
          this.data_item.price_token,
      )
      const sigData: StellarSignatureResponse = sigResponse.data

      console.debug('Stellar signature response:', sigData)

      // Execute the two-step Soroban flow (approve + user_mint_with_token)
      const result = await stellarService.mintWithToken(sigData, this.invest_id)

      if (result.status === 'confirmed') {
        self.loading = false
        showAlert(
            self.$t('views.Compra de tokens realizada con éxito'),
            self.$t('views.éxito compra, has comprado_', {
              token_number: this.data_form.num_tokens,
              token_value: this.invest_price,
              project: this.data_item.name,
              currency: this.VUE_APP_WHITE_LABEL_CURRENCY,
            }),
            false,
            function () {
              self.$router.push('/portfolio')
            }
        )
      } else {
        self.loading = false
        showAlertError(this.$t('Error en la transacción de Stellar'), this)
      }
    } catch (error) {
      self.loading = false
      console.error('Stellar payment error:', error)

      if ((error as Error).message.includes('superado maximo numero de tokens')) {
        showAlert(
            self.$t('views.Error al comprar tokens'),
            self.$t('views.Antes de que realizases la compra de los tokens, otro usuario ha comprado uno o varios_'),
            false,
            function () {
              self.$router.push('/project/' + self.$route.params.slug.toString())
            }
        )
      } else if ((error as Error).message.includes('Insufficient balance') || (error as Error).message.includes('op_underfunded')) {
        showAlertError(this.$t('Saldo insuficiente en tu wallet de Stellar'), this)
      } else if ((error as Error).message.includes('not installed')) {
        showAlertError(this.$t('Por favor instala la extensión Freighter para usar Stellar'), this)
      } else if ((error as Error).message.includes('rejected') || (error as Error).message.includes('denied')) {
        showAlertError(this.$t('La firma de la transacción fue rechazada'), this)
      } else if ((error as Error).message.includes('Simulation failed')) {
        showAlertError(this.$t('Error al simular la transacción Stellar. Verifica tu saldo y allowance.'), this)
      } else {
        showAlertError(error as Error, this)
      }
    }
  }
}
</script>
