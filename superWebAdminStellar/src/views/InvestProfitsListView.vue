<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div v-if="!is_completed" class="col s12 padding-0 mb-3 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Reparto de beneficios') }}</h4>
        </div>

        <div v-if="!is_completed && !loading" class="col s12 card padding-3">
          <div class="card-content">

            <p v-if="list_users.length === 0">{{ $t('views.No existen usuarios con inversiones para hacer el reparto de beneficios') }}</p>

            <div v-if="list_users.length > 0">

              <div class="row">
                <div class="input-field col s12">
                  <p>{{ $t('views.Para realizar un nuevo reparto de beneficios, introduce la cantidad de dinero a repartir entre todos los inversores del proyecto_') }}</p>
                </div>
                <div class="input-field col s12 m4">
                  <label for="profit" class="active"><span class="required">*</span> {{ $t('views.Valor') }}:</label>
                  <input type="number" id="profit" v-model="profit">
                </div>
                <div class="input-field col s12 m8">
                  <button @click="showForm" class="btn-primary mr-3">{{ $t('views.Calcular reparto') }}</button>
                </div>
              </div>



              <div id="table_data_profits" style="display: none">
                <div class="row table_wrapper">
                  <table>
                    <thead>
                    <tr>
                      <th>{{ $t('views.Email') }}</th>
                      <th>{{ $t('views.Nombre') }}</th>
                      <th>{{ $t('views.Apellidos') }}</th>
                      <th>{{ $t('views.N tokens') }}</th>
                      <th>{{ $t('views.Valor') }}</th>
                    </tr>
                    </thead>

                    <tbody>
                    <tr v-for="item in list_users" :key="item.id">
                      <td><router-link :to="'/UserDetail/'+item.user_id">{{ item.email }}</router-link></td>
                      <td>{{ item.name }}</td>
                      <td>{{ item.surname }}</td>
                      <td>{{ myFormatNumber(item.value) }}</td>
                      <td>{{ myFormatNumber(item.profit) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                    </tr>
                    </tbody>
                  </table>
                </div>
                <div class="input-field col s12">
                  <button :disabled="loading" @click="save" class="btn-primary right">{{ $t('views.Repartir beneficios') }}</button>
                </div>
              </div>

            </div>
          </div>
        </div>

        <div class="col s12 padding-0 mb-3 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Histórico de reparto de beneficios') }}</h4>
        </div>

        <div v-if="list_profits.length > 0" class="col s12 card padding-3">
          <div class="card-content">
            <div class="row table_wrapper">
              <table>
                <thead>
                <tr>
                  <th>{{ $t('views.Fecha') }}</th>
                  <th>{{ $t('views.Valor') }}</th>
                  <th>{{ $t('views.Concepto') }}</th>
                  <th style="min-width: 280px; width: 280px"></th>
                </tr>
                </thead>

                <tbody>
                <tr v-for="item in list_profits" :key="item.id" :id="item.id">
                  <td>{{ formatDate(item.date_profit) }}</td>
                  <td>{{ myFormatNumber(item.profit) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                  <td>{{ $t('views.white_label_name')}}_{{item.id}}</td>
                  <td>
                    <button :disabled="loading" @click="getListUsersProfits(item.id)" class="btn-primary mr-3">{{ $t('views.Ver usuarios') }}</button>
                    <button :disabled="loading" @click="getListUsersProfitsToExport(item.id, item.date_profit)" class="btn-primary">{{ $t('views.Exportar') }}</button>
                  </td>
                </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>

      </div>
    </div>
  </div>

  <div id="div_table_download" style="display: none;"></div>
</template>



<script lang="ts">
import InvestServices from '@/services/InvestServices'
import {Options, Vue} from "vue-class-component";
import Menu from "@/components/Menu.vue";
import {download_table_as_csv, formatDateFromServer, formatNumber, showAlert, showAlertError} from "@/functions";
import JQuery from "jquery";


@Options({
  components: {
    Menu
  },
})
export default class InvestPromoterContributionsListView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  loading = false
  profit = 0
  total_tokens_sold = 0

  list_profits = []
  list_users = []
  is_completed = false
  profit_percentage = 0
  category_id = -1

  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    self.loading = true
    InvestServices.getInvestProfits(this.$route.params.invest_id)
        .then(response => {
          this.is_completed = response.data.is_completed
          this.list_profits = response.data.list_profits
          this.list_users = response.data.list_users
          this.category_id = response.data.category_id
          this.profit_percentage = response.data.profit_percentage

          for (let user of this.list_users) {
            this.total_tokens_sold += user.value
          }
          self.loading = false
        })
  }

  save() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    if (isNaN(this.profit) || this.profit <= 0){
      return;
    }
    if (this.$route.params.invest_id !== undefined){
      showAlert("",self.$t('views.Estás a punto de realizar un reparto de beneficios de XX entre todos los usuarios inversores_', {'value': formatNumber(self.profit), currency: this.VUE_APP_WHITE_LABEL_CURRENCY}), true, function() {

        self.loading = true
        InvestServices.generateProfit(self.$route.params.invest_id, self.profit)
            // eslint-disable-next-line no-unused-vars
            .then(response => {
              showAlert("",self.$t('views.Datos guardados correctamente'), false, function() {
                self.$router.go(0)
              })
            })
            .catch(function (error) {
              self.loading = false
              showAlertError(error, self)
            });
      })

    }
  }

  showForm() {
    if (isNaN(this.profit) || this.profit <= 0){
      return;
    }
    const myForm = document.getElementById('table_data_profits')
    if (myForm != null) (myForm as HTMLInputElement).style.display = '';

    let profit_token = this.profit / this.total_tokens_sold
    for (let user of this.list_users){
      user.profit = user.value * profit_token
    }
  }

  getListUsersProfits(profit_id){
    InvestServices.getInvestProfitsUser(profit_id)
        .then(response => {
          //se borran las tablas expandidas
          JQuery('#table_row_'+profit_id).html('')

          let content =
              '<table>' +
              '                    <thead>' +
              '                    <tr>' +
              '                      <th>'+this.$t('views.Email')+'</th>' +
              '                      <th>'+this.$t('views.Nombre')+'</th>' +
              '                      <th>'+this.$t('views.Apellidos')+'</th>' +
              '                      <th>'+this.$t('views.Valor')+'</th>' +
              '                      <th>'+this.$t('views.Concepto')+'</th>' +
              '                      <th>'+this.$t('views.BIC')+'</th>' +
              '                      <th>'+this.$t('views.IBAN')+'</th>' +
              '                    </tr>' +
              '                    </thead>' +
              '                    <tbody>';
          for (let item of response.data){
            content +=            '<tr>'+
                '                      <td>'+item.email+'</td>' +
                '                      <td>'+item.name+'</td>' +
                '                      <td>'+item.surname+'</td>' +
                '                      <td>'+this.myFormatNumber(item.value)+this.VUE_APP_WHITE_LABEL_CURRENCY+'</td>' +
                '                      <td>'+this.$t('views.white_label_name')+'_'+profit_id+'</td>' +
                '                      <td>'+item.bic+'</td>' +
                '                      <td>'+item.iban+'</td>' +
                '                    </tr>'
          }
          content +=
              '                    </tbody>' +
              '                  </table>'
          JQuery('<tr id="table_row_'+profit_id+'"><td colspan="4">'+content+'</td></tr>').insertAfter('#'+profit_id);
        })
  }

  getListUsersProfitsToExport(profit_id, date_profit){
    InvestServices.getInvestProfitsUser(profit_id)
        .then(response => {
          let content =
              '<table id="table_download">' +
              '                    <thead>' +
              '                    <tr>' +
              '                      <th>'+this.$t('views.Email')+'</th>' +
              '                      <th>'+this.$t('views.Nombre')+'</th>' +
              '                      <th>'+this.$t('views.Apellidos')+'</th>' +
              '                      <th>'+this.$t('views.Valor')+'</th>' +
              '                      <th>'+this.$t('views.Concepto')+'</th>' +
              '                      <th>'+this.$t('views.BIC')+'</th>' +
              '                      <th>'+this.$t('views.IBAN')+'</th>' +
              '                    </tr>' +
              '                    </thead>' +
              '                    <tbody>';
          for (let item of response.data){
            content +=            '<tr>'+
                '                      <td>'+item.email+'</td>' +
                '                      <td>'+item.name+'</td>' +
                '                      <td>'+item.surname+'</td>' +
                '                      <td>'+this.myFormatNumber(item.value)+this.VUE_APP_WHITE_LABEL_CURRENCY+'</td>' +
                '                      <td>'+this.$t('views.white_label_name')+'_'+profit_id+'</td>' +
                '                      <td>'+item.bic+'</td>' +
                '                      <td>'+item.iban+'</td>' +
                '                    </tr>'
          }
          content +=
              '                    </tbody>' +
              '                  </table>'

          JQuery('#div_table_download').html(content)

          download_table_as_csv('table_download',',', 'users_profits_'+date_profit.replace('T', ' '))
        })
  }




  formatDate(date) {
    return formatDateFromServer(date)
  }

  myFormatNumber(val){
    return formatNumber(val)
  }
}


</script>
