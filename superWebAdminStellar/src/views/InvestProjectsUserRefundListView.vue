<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="col s12 padding-0 mb-3 text-center">
          <h4 class="col s12 text-center">
            <template v-if="refund_type == USERS_INVEST_TYPE_REFUND">{{ $t('views.Devoluciones realizadas a los usuarios') }}</template>
            <template v-if="refund_type == USERS_INVEST_TYPE_REFUND_PARTIAL">{{ $t('views.Amortizaciones realizadas a los usuarios') }}</template>
          </h4>
        </div>

        <div class="col s12 card padding-3">
          <div class="card-content">
            <h5 class="text-center">
              <template v-if="refund_type == USERS_INVEST_TYPE_REFUND">{{ $t('views.Devoluciones realizadas a los usuarios') }}</template>
              <template v-if="refund_type == USERS_INVEST_TYPE_REFUND_PARTIAL">{{ $t('views.Amortizaciones realizadas a los usuarios') }}</template>
            </h5>
            <div class="mb-5 row table_wrapper">
              <table>
                <thead>
                <tr>
                  <th>{{ $t('views.Email') }}</th>
                  <th>{{ $t('views.Fase') }}</th>
                  <th>{{ $t('views.Tokens') }}</th>
                  <th>{{ $t('views.Precio') }}</th>
                  <th>{{ $t('views.Valor') }}</th>
                </tr>
                </thead>

                <tbody>
                <tr v-for="item in list_investors_refunds" :key="item.user_id">
                  <td><router-link :to="'/UserDetail/'+item.user_id">{{ item.email }}</router-link></td>
                  <td>{{ item.phase }}</td>
                  <td>{{ myFormatNumber(item.num_tokens) }}</td>
                  <td>{{ myFormatNumber(item.price_token, 10) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                  <td>{{ myFormatNumber(item.value, 10) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                </tr>
                </tbody>
              </table>
            </div>


            <h5 class="text-center">{{ $t('views.Usuarios inversores del proyecto') }}</h5>
            <div class="row table_wrapper">
              <table>
                <thead>
                <tr>
                  <th>{{ $t('views.Email') }}</th>
                  <th>{{ $t('views.Fase') }}</th>
                  <th>{{ $t('views.Tokens') }}</th>
                  <th>{{ $t('views.Precio/Token') }}</th>
                  <th>{{ $t('views.Valor') }}</th>
                </tr>
                </thead>

                <tbody>
                <tr v-for="item in list_investors" :key="item.user_id">
                  <td><router-link :to="'/UserDetail/'+item.user_id">{{ item.email }}</router-link></td>
                  <td>{{ item.phase }}</td>
                  <td>{{ myFormatNumber(item.num_tokens) }}</td>
                  <td>{{ myFormatNumber(item.price_token) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                  <td>{{ myFormatNumber(item.value, 10) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>

                  <td><button :disabled="loading" @click="popupNewRefund(item.user_id, item.user_invest_id, item.email, item.num_tokens, item.price_token)" class="btn-primary right">{{ $t('views.Devolver capital') }}</button></td>
                </tr>
                </tbody>
              </table>
            </div>



          </div>
        </div>
      </div>
    </div>





    <div id="modal_white_list" class="modal border-radius-10 border-radius-15">
      <div class="modal-content text-center">
        <h5 class="mt-3">
          {{ $t('views.Número de tokens a devolver a') }}: {{email_select}}
        </h5>
        <div class="row">
          <div class="col s12 mt-3">
            <div class="input-field col s12 m4">
              <label class="active" style="top: -30px" for="refund_value"><span class="required">*</span> {{ $t('views.N tokens a devolver') }}:<br>(MAX {{max_to_refund}})</label>
              <input type="number" id="refund_value" v-model="refund_num_tokens_select" required min="1" :max="max_to_refund" @blur="checkNumTokens">
            </div>
            <div class="input-field col s12 m4">
              {{ $t('views.Cantidad') }}: {{myFormatNumber(refund_num_tokens_select*price_token_select)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}
            </div>
            <div class="input-field col s12 m4">
              <button @click="selectAllTokensToRefund" class="btn-primary mt-5">{{ $t('views.Seleccionar MAX') }}</button>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer mb-3">
        <button :disabled="loading" @click="saveNewRefund" id="modal_alert_bt_ok" type="button" class="btn-primary modal-close">{{ $t('views.aceptar') }}</button>&nbsp;&nbsp;&nbsp;
        <button id="modal_alert_bt_cancel" type="button" class="btn-secondary modal-close">{{ $t('views.cancelar') }}</button>&nbsp;&nbsp;&nbsp;
      </div>
    </div>

  </div>
</template>



<script lang="ts">
import {Options, Vue} from "vue-class-component";
import Menu from "@/components/Menu.vue";
import {
  formatNumber,
  hideAlertLoading,
  showAlert,
  showAlertError,
  showAlertLoading
} from "@/functions";
import UserServices from "@/services/UserServices";
import {USERS_INVEST_TYPE_REFUND, USERS_INVEST_TYPE_REFUND_PARTIAL} from "@/const";
import M from "materialize-css";

@Options({
  components: {
    Menu,
  },
})
export default class InvestProjectsUserInvestListView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  USERS_INVEST_TYPE_REFUND = USERS_INVEST_TYPE_REFUND
  USERS_INVEST_TYPE_REFUND_PARTIAL = USERS_INVEST_TYPE_REFUND_PARTIAL

  list_investors = []
  list_investors_refunds = []
  loading = false
  invest_id
  refund_type
  link = ''
  max_to_refund = 0

  refund_num_tokens_select = 0
  user_id_select = 0
  email_select = ''
  user_invest_id_select = 0
  price_token_select = 0

  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    this.invest_id = this.$route.params.invest_id
    this.link = this.$route.params.category_name + '/' + this.invest_id
    this.refund_type = this.$route.params.type

    UserServices.getUsersInvestors(this.invest_id, this.refund_type)
        .then(response => {
          this.list_investors = response.data.list_users_tokens;
        })
        .catch(function (error) {
          showAlertError(error, self)
        });

    UserServices.getUsersInvestorsRefund(this.invest_id, this.refund_type)
        .then(response => {
          this.list_investors_refunds = response.data;
        })
        .catch(function (error) {
          showAlertError(error, self)
        });
  }


  saveNewRefund() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    showAlert("",self.$t('views.Estás seguro de hacer la devolución',{value:this.myFormatNumber(this.refund_num_tokens_select*this.price_token_select), email:this.email_select, currency: this.VUE_APP_WHITE_LABEL_CURRENCY}), true, function() {
      self.loading = true
      showAlertLoading()
      UserServices.saveInvestUserRefund(self.invest_id, self.user_id_select, self.user_invest_id_select, self.refund_type, self.refund_num_tokens_select)
          // eslint-disable-next-line no-unused-vars
          .then(response => {
            hideAlertLoading()
            showAlert("",self.$t('views.Datos guardados correctamente'), false, function() {
              self.$router.go(0)
            })
          })
          .catch(function (error) {
            hideAlertLoading()
            self.loading = false
            showAlertError(error, self)
          });
    })
  }

  popupNewRefund(user_id, user_invest_id, email, num_tokens, price_token_select){
    this.email_select = email
    this.user_id_select = user_id
    this.user_invest_id_select = user_invest_id
    this.max_to_refund = num_tokens
    this.price_token_select = price_token_select
    this.refund_num_tokens_select = 0

    const elems = document.querySelectorAll('.modal');
    M.Modal.init(elems, {dismissible: false});

    const singleModalElem = document.querySelector('#modal_white_list');
    if (singleModalElem != null) {
      const instance = M.Modal.getInstance(singleModalElem);

      instance.open();
    }
  }

  checkNumTokens(){
    if (this.refund_num_tokens_select < 1 || this.refund_num_tokens_select > this.max_to_refund){
      showAlertError(this.$t('views.Devolución de capital no válida_', {max: this.max_to_refund}), this)
    }
  }
  selectAllTokensToRefund(){
    this.refund_num_tokens_select = this.max_to_refund
  }

  myFormatNumber(val, decimals = 2){
    return formatNumber(val, decimals)
  }
}

</script>
