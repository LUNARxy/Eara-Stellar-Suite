<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="card padding-3">
          <div class="card-content">
            <h4 class="card-title">{{ $t('views.DOCUMENTOS') }}</h4>
            <button class="btn-primary right" @click="showForm">{{ $t('views.Nuevo') }}</button>

            <form id="form" @submit.prevent="save" style="display: none">
              <div class="row padding-7">
                <div class="input-field col s12">
                  <label for="description"><span class="required">*</span> {{ $t('views.Descripción del documento') }}:</label>
                  <input type="text" id="description" v-model="data_form.description" maxlength="200" required>
                </div>
                <div class="input-field col s12">
                  <div>
                    <input type="file" @change="handleFileUpload( $event )" required/>
                  </div>
                </div>
                <div class="input-field col s12">
                  <input type="hidden" id="id" name="id">
                  <button class="btn-primary right" type="submit" :disabled="loading">{{ $t('views.guardar') }}</button>
                </div>
              </div>
            </form>

            <table>
              <thead>
              <tr>
                <th></th>
                <th>{{ $t('views.Descripción') }}</th>
                <th></th>
              </tr>
              </thead>

              <tbody>
              <tr v-for="item in list_docs" :key="item.id">
                <td width="80px"><a :href="PUBLIC_URL+item.file" target="_blank"><img src="@/assets/img/pdf.png" class="responsive-img"></a></td>
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
</template>



<script lang="ts">
import InvestServices from '@/services/InvestServices'
import {Options, Vue} from "vue-class-component";
import Menu from "@/components/Menu.vue";
import {showAlert, showAlertError, showAlertLoading, hideAlertLoading} from "@/functions";
import {PUBLIC_URL} from "@/services/Http-common";



@Options({
  components: {
    Menu,
  },
})
export default class InvestDocumentsListView extends Vue {
  PUBLIC_URL = PUBLIC_URL
  list_docs = []
  loading = false

  // eslint-disable-next-line
  data_form: any = {}

  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    InvestServices.getInvestDocs(this.$route.params.invest_id)
        .then(response => {
          this.list_docs = response.data;
        })
        .catch(function (error) {
          showAlertError(error, self)
        });
  }

  handleFileUpload( event ){
    this.data_form.file = event.target.files[0];
  }
  save() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    if (this.$route.params.invest_id !== undefined){
      this.loading = true
      showAlertLoading()
      this.data_form.invest_id = this.$route.params.invest_id;
      InvestServices.saveInvestDocs(this.data_form)
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
    }
  }
  deleteItem(id) {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    showAlert("",self.$t('views.Estás seguro de borrar el documento'), true, function() {
      InvestServices.deleteDocs(self.$route.params.invest_id, id)
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
  }
}


</script>
