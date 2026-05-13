<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="col s12 padding-0 mb-3 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Estado del proyecto en curso') }}</h4>
        </div>


        <div class="col s12 card padding-3">
          <div class="card-content">

            <div class="col s12 mb-3">
              <button class="btn-primary right" @click="showForm">{{ $t('views.Nuevo') }}</button>
            </div>

            <form id="form" @submit.prevent="save" class="col s12 mb-4" style="display: none">
              <div class="row">
                <div class="input-field col s12 m3">
                  <label for="date_created" class="active">{{ $t('views.Fecha inicio de la fase') }}:</label>
                  <input id="date_created" name="date_created" v-model="data_form.date_created" type="datetime-local" required>
                </div>
                <div class="input-field col s12 m9">
                  <label for="description" class="active">{{ $t('views.Descripción') }}:</label>
                  <input type="text" id="description" v-model="data_form.description" maxlength="200">
                </div>
                <div class="input-field col s12">
                  <input type="hidden" id="id" v-model="data_form.id">
                  <button class="btn-primary right" type="submit" :disabled="loading">{{ $t('views.guardar') }}</button>
                </div>
              </div>
            </form>

            <div class="row table_wrapper">
              <table>
                <thead>
                <tr>
                  <th>{{ $t('views.Fecha') }}</th>
                  <th>{{ $t('views.Descripción') }}</th>
                  <th></th>
                </tr>
                </thead>

                <tbody>
                <tr v-for="item in list_status_description" :key="item.id">
                  <td>{{ formatDate(item.date_created) }}</td>
                  <td>{{ item.description }}</td>
                  <td width="80px">
                    <button class="btn-primary" @click.stop="deleteItem(item.id)"><i class="material-icons">delete</i></button>
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
</template>



<script lang="ts">
import InvestServices from '@/services/InvestServices'
import {Options, Vue} from "vue-class-component";
import Menu from "@/components/Menu.vue";
import {formatDateFromServer, isValidDate, showAlert, showAlertError} from "@/functions";

import JQuery from "jquery";



@Options({
  components: {
    Menu,
  },
})
export default class InvestStatusListView extends Vue {

  list_status_description = []
  loading = false


  // eslint-disable-next-line
  data_form: any = {}

  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    InvestServices.getInvestStatusDescription(this.$route.params.invest_id)
        .then(response => {
          this.list_status_description = response.data;
        })
        .catch(function (error) {
          showAlertError(error,self)
        });
  }

  save() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    if (this.$route.params.invest_id !== undefined){
      this.loading = true
      this.data_form.invest_id = this.$route.params.invest_id;

      //si tiene id de noticia entonces es actualizar sino es uno nuevo
      InvestServices.saveInvestStatusDescription(this.data_form)
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
    }
  }

  deleteItem(id) {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    showAlert("",self.$t('views.Estás seguro de borrar el estado del proyecto'), true, function() {
      InvestServices.deleteStatusDescription(self.$route.params.invest_id, id)
          .then(response => {
            self.$router.go(0)
          })
          .catch(function (error) {
            showAlertError(error, self)
          });
    })
  }
  showForm(){
    const myForm = document.getElementById('form')
    if (myForm != null) (myForm as HTMLInputElement).style.display = '';
    this.data_form.id = ''
    this.data_form.phase = ''
    this.data_form.description = ''
    this.data_form.date_created = new Date().toISOString().split('T')[0]
  }
  isValidDate(value){
    let date_in = JQuery('#' + value).val()
    if (date_in != undefined && date_in != "") {
      if (!isValidDate(date_in)) {
        showAlertError(this.$t('views.La fecha no es correcta'), this)
      }
    }
  }

  formatDate(date) {
    return formatDateFromServer(date)
  }
}


</script>
