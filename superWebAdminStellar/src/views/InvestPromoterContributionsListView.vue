<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="col s12 padding-0 mb-3 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Disposiciones') }}</h4>
        </div>


        <div class="col s12 card padding-3">
          <div class="card-content">

            <div class="col s12 mb-3">
              <button v-if="!data_item.is_completed && data_item.actual_phase !== 'all'" class="btn-primary right" @click="showForm">{{ $t('views.Nueva') }}</button>
              <div class="text-center" v-if="data_item.actual_phase === 'all'">
                <span class="red-text mr-2">{{ $t('views.No hay fase activa en fecha actual para poder hacer una aportación') }}</span>
                <router-link :to="'/InvestPhasesMintList/'+link"><button class="btn-primary">{{ $t('views.Ver fases') }}</button></router-link>
              </div>
            </div>

            <div v-if="!data_item.is_completed" class="row" id="form" style="display: none">
              <div class="col s12 text-center">
                <p>{{ $t('views.Número de participaciones en esta fase de venta') }}: {{data_item.actual_num_tokens}}</p>
                <p>{{ $t('views.Número de participaciones en venta') }}: {{data_item.actual_remaining_tokens}}</p>
                <p>{{ $t('views.Número mínimo de participaciones a comprar') }}: {{data_item.num_tokens_min_to_buy}}</p>
                <p>{{ $t('views.Precio de la participación') }}: {{data_item.actual_price_token}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</p>
                <div class="row mt-3">
                  <div class="col s12">
                    <button type="button" class="btn-secondary mr-2" @click="changePrice(-1)">
                        <span type="button" style="padding: 8px 14px;">
                          <i class="material-icons white-text">remove</i>
                        </span>
                    </button>
                    <input type="text" id="num_tokens" name="num_tokens" v-model="num_tokens" @change="calculatePrice()" required style="width: 80px;text-align: right; ">
                    <button type="button" class="btn-secondary ml-2" @click="changePrice(1)">
                        <span type="button" style="padding: 8px 14px;">
                          <i class="material-icons white-text">add</i>
                        </span>
                    </button>
                  </div>
                </div>
                <p>Vas a invertir {{invest_price}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</p>
                <div class="row">
                  <div class="input-field col s12 mt-3">
                    <button :disabled="loading" @click="save" class="btn-primary">Comprar tokens</button>&nbsp;
                  </div>
                </div>
              </div>
            </div>
            <div class="row table_wrapper">
              <table>
                <thead>
                <tr>
                  <th>{{ $t('views.Fecha') }}</th>
                  <th>{{ $t('views.Fase') }}</th>
                  <th>{{ $t('views.N Tokens') }}</th>
                  <th>{{ $t('views.Precio token') }}</th>
                  <th>{{ $t('views.Valor') }}</th>
                </tr>
                </thead>

                <tbody>
                <tr v-for="item in data_item.list_contributions" :key="item.invest_id">
                  <td>{{ formatDate(item.date_created) }}</td>
                  <td>{{ item.phase }}</td>
                  <td>{{ myFormatNumber(item.num_tokens) }}</td>
                  <td>{{ myFormatNumber(item.price_token) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                  <td>{{ myFormatNumber(item.num_tokens*item.price_token) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                </tr>
                </tbody>
              </table>
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
  formatNumber, hideAlertLoading,
  showAlert,
  showAlertError,
  showAlertLoading
} from "@/functions";


@Options({
  components: {
    Menu,
  },
})
export default class InvestPromoterContributionsListView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  loading = false
  invest_price = 0
  num_tokens = 0
  invest_id
  link = ''

  // eslint-disable-next-line
  data_item: any = {}

  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    
    this.invest_id = this.$route.params.invest_id
    this.link = this.$route.params.category_name + '/' + this.invest_id

    InvestServices.getInvestPromoterContributionList(this.invest_id)
        .then(response => {
          this.data_item = response.data
        })
        .catch(function (error) {
          showAlertError(error,self)
        });
  }

  save() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    if (isNaN(this.num_tokens) || this.num_tokens <= 0){
      showAlertError(this.$t('views.Aportación de capital no válida_'),self)
      return;
    }
    if (this.num_tokens > this.data_item.actual_remaining_tokens){
      showAlertError(this.$t('views.El máximo número de tokens a comprar no puede_'),self)
      return;
    }
    if (this.num_tokens < this.data_item.num_tokens_min_to_buy){
      showAlertError(this.$t('views.El mínimo número de tokens a comprar es de_',{'num_tokens_min':this.data_item.num_tokens_min_to_buy}),self)
      return;
    }
    if (this.$route.params.invest_id !== undefined){
      showAlert("",self.$t('views.Estás seguro de hacer la aportación'), true, function() {
        self.loading = true
        showAlertLoading()
        InvestServices.saveInvestPromoterContribution(self.$route.params.invest_id, self.num_tokens)
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
  }

  showForm(){
    const myForm = document.getElementById('form')
    if (myForm != null) (myForm as HTMLInputElement).style.display = '';
    this.num_tokens = 0
  }

  changePrice(add_or_subtraction){
    let val = parseInt(this.num_tokens.toString())
    if (isNaN(val)) val = 0
    val += add_or_subtraction;
    if (val < 0) val = 0
    this.num_tokens = val
    this.invest_price = this.data_item.actual_price_token*val
  }
  calculatePrice(){
    let val = parseInt(this.num_tokens.toString())
    if (isNaN(val)) val = 0
    if (val < 0) val = 0
    this.invest_price = this.data_item.actual_price_token*val
  }
  formatDate(date) {
    return formatDateFromServer(date)
  }
  myFormatNumber(val){
    return formatNumber(val)
  }
}


</script>
