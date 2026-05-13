<template>
  <Menu/>
  <div v-if="page_loaded" class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="col s12 padding-0 mb-3 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Proyecto completado') }}</h4>
        </div>

        <div class="col s12 card padding-3">
          <div class="card-content">
            <p v-if="!is_completed">{{ $t('views.Una vez terminado el proyecto y repartidos los beneficios del mismo_') }}</p>
            <p v-if="is_completed">{{ $t('views.El proyecto ha terminado y no se puede modificar_') }}</p>

            <div class="col s12 mt-3 mb-3">
            <button @click="exportData()" class="btn-primary right">{{ $t('views.Exportar') }}</button>
            <button v-if="!is_completed" @click="closeProject()" class="btn-primary right mr-3">{{ $t('views.Cerrar proyecto') }}</button>
            </div>

            <div class="row table_wrapper">
              <table id="table_download">
                <thead>
                <tr>
                  <th>{{ $t('views.Email') }}</th>
                  <th>{{ $t('views.Nombre') }}</th>
                  <th>{{ $t('views.Apellidos') }}</th>
                  <th>{{ $t('views.Tokens') }}</th>
                  <th>{{ $t('views.Valor') }}</th>
                  <th>{{ $t('views.Concepto') }}</th>
                  <th>{{ $t('views.BIC') }}</th>
                  <th>{{ $t('views.IBAN') }}</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="item in list_investors" :key="item.user_id">
                  <td><router-link :to="'/UserDetail/'+item.user_id">{{ item.email }}</router-link></td>
                  <td>{{ item.name }}</td>
                  <td>{{ item.name }}</td>
                  <td>{{ myFormatNumber(item.num_tokens) }}</td>
                  <td>{{ myFormatNumber(item.value) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                  <td>{{ $t('views.white_label_name') }}_{{ $t('views.CIERRE') }}_{{invest_id}}</td>
                  <td>{{ item.bic }}</td>
                  <td>{{ item.iban }}</td>
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
import {Options, Vue} from "vue-class-component";
import Menu from "@/components/Menu.vue";
import {
  download_table_as_csv,
  formatDateFromServer,
  formatNumber,
  hideAlertLoading,
  showAlert,
  showAlertError, showAlertLoading
} from "@/functions";
import InvestServices from "@/services/InvestServices";

@Options({
  components: {
    Menu,
  },
})
export default class InvestCompletedListView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  page_loaded = false

  list_investors = []
  loading = false
  invest_id = ''
  is_completed = false


  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    showAlertLoading()

    this.invest_id = this.$route.params.invest_id.toString()
    InvestServices.getUsersInvestorsToCompletedProyect(this.$route.params.invest_id)
        .then(response => {
          this.is_completed = response.data.is_completed;
          this.list_investors = response.data.list_investors;

          self.page_loaded = true
          hideAlertLoading()
        })
        .catch(function (error) {
          self.page_loaded = true
          hideAlertLoading()
          showAlertError(error, self)
        });
  }

  closeProject(){
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    showAlert("",self.$t('views.Estás seguro de hacer el cierre del proyecto, esta acción es irreversible'), true, function() {
      self.loading = true
      showAlertLoading()
      InvestServices.closeProject(self.$route.params.invest_id)
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

  exportData(){
    download_table_as_csv('table_download',',', 'users_invest')
  }

  formatDate(date) {
    return formatDateFromServer(date)
  }
  myFormatNumber(val){
    return formatNumber(val)
  }
}

</script>
