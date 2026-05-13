<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="card">
          <div class="card-content">

            <h4 class="card-title">{{ $t('views.GALERÍA DE IMÁGENES') }}</h4>
            <button class="btn-primary right" @click="showForm">{{ $t('views.NUEVA') }}</button>



            <form id="form" @submit.prevent="save" class="mb-4 padding-7" style="display: none">
              <div class="row">
                <div class="input-field col s12">
                  <label for="description">Descripción:</label>
                  <input type="text" id="description" v-model="data_form.description" maxlength="200">
                </div>
                <div class="input-field col s12 m6">
                  <img id="file_img"  class="responsive-img">
                </div>
                <div class="input-field col s12 m6">
                  <div>
                    <input type="file" @change="handleFileUpload( $event )" required/>
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="input-field col s12 text-center">
                  <input type="hidden" id="id" name="id">
                  <button class="btn-primary" type="submit">{{ $t('views.guardar') }}</button>
                </div>
              </div>
            </form>

            <table>

              <tbody>
              <tr v-for="item in list_gallery" :key="item.id">
                <td width="300px"><img :src="PUBLIC_URL+item.file" class="responsive-img"></td>
                <td>{{ item.description }}</td>
                <td width="80px">
                  <button class="btn-primary right" @click.stop="deleteItem(item.id)"><i class="material-icons">delete</i></button>
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
import {showAlert, showAlertError, validateCorrectFile} from "@/functions";
import {PUBLIC_URL} from "@/services/Http-common";




@Options({
  components: {
    Menu,
  },
})
export default class InvestGalleryListView extends Vue {
  PUBLIC_URL = PUBLIC_URL
  list_gallery = []

  // eslint-disable-next-line
  data_form: any = {}

  async handleFileUpload( event ){
    this.data_form.file = event.target.files[0];
    if (this.data_form.file) {
      // Validar el tipo de archivo
      if (await validateCorrectFile(this.data_form.file, this)) {
        const file_img = document.getElementById('file_img')
        if (file_img != null) (file_img as HTMLInputElement).src = URL.createObjectURL(this.data_form.file)
      } else {
        this.data_form.file = null
      }
    }
  }
  getInvestGallery() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    InvestServices.getInvestGallery(this.$route.params.invest_id)
        .then(response => {
          this.list_gallery = response.data;
        })
        .catch(function (error) {
          showAlertError(error, self)
        });
  }
  save() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    if (this.$route.params.invest_id !== undefined && this.data_form.file != null){
      this.data_form.invest_id = this.$route.params.invest_id;
      InvestServices.saveInvestGallery(this.data_form)
          .then(response => {
            showAlert("","Datos guardados correctamente", false, function() {
              self.$router.go(0)
            })
          })
          .catch(function (error) {
            showAlertError(error, self)
          });
    }
  }
  deleteItem(id) {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    showAlert("",self.$t('views.Estás seguro de borrar la imagen'), true, function() {
      InvestServices.deleteGallery(self.$route.params.invest_id, id)
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
  mounted () {
    this.getInvestGallery();

  }
}


</script>
