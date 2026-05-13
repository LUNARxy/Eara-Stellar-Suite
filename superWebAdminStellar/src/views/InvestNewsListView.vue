<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="card padding-3">
          <div class="card-content">

            <h4 class="card-title mb-5">{{ $t('views.NOTICIAS RELACIONADAS') }}</h4>
            <button class="btn-primary right" @click="showForm">{{ $t('views.Nueva') }}</button>

            <form id="form" @submit.prevent="save" class="mb-4" style="display: none">
              <div class="row padding-7">
                <div class="input-field col s12 m6">
                  <label for="title" :class="{ active: classModify }"><span class="required">*</span> {{ $t('views.Título') }}:</label>
                  <input type="text" id="title" v-model="data_form.title" maxlength="200" required>
                </div>
                <div class="input-field col s12 m6">
                  <label for="url" :class="{ active: classModify }">URL:</label>
                  <input type="text" id="url" v-model="data_form.url" maxlength="250">
                </div>
                <div class="input-field col s12">
                  <label for="summary" class="active"><span class="required">*</span> {{ $t('views.Resumen_1000_caracteres') }}</label>
                  <!--<br><editor id="summary" v-model="data_form.summary" :init="{height: 500,plugins: 'wordcount',menubar: false,toolbar:'undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help'}"/>-->
                  <br><vue-editor id="summary" v-model="data_form.summary"></vue-editor>
                  <!--<input type="text" id="summary" v-model="data_form.summary" maxlength="2000" required>-->
                </div>

                <div class="input-field col s12 m6">
                  <img id="file_img" :src="data_form.file_img" class="responsive-img">
                </div>
                <div class="input-field col s12 m6">
                  <div class="mb-3">{{ $t('views.Imagen') }}</div>
                  <div>
                    <input id="file" type="file" @change="handleFileUpload( $event )"/>
                  </div>
                </div>
                <div class="input-field col s12">
                  <input type="hidden" id="id" v-model="data_form.id">
                  <button class="btn-primary right" type="submit" :disabled="loading">{{ $t('views.guardar') }}</button>
                </div>
              </div>
            </form>

            <table>
              <thead>
              <tr>
                <th></th>
                <th>Título</th>
                <th></th>
              </tr>
              </thead>

              <tbody>
              <tr v-for="(item, itemObjKey) in list_news" :key="item.id">
                <td width="200px"><img :src="item.file" class="responsive-img"></td>
                <td>{{ item.title }}</td>
                <td width="150px">
                  <button class="btn-primary right mr-3" @click.stop="showDescription(itemObjKey)"><i class="material-icons">edit</i></button>
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

import { VueEditor } from "vue3-editor";
import JQuery from "jquery";
import {PUBLIC_URL} from "@/services/Http-common";



@Options({
  components: {
    Menu,
    VueEditor
  },
})
export default class InvestNewsListView extends Vue {
  PUBLIC_URL = PUBLIC_URL
  list_news = []
  loading = false
  classModify = ''


  // eslint-disable-next-line
  data_form: any = {}

  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    InvestServices.getInvestNews(this.$route.params.invest_id)
        .then(response => {
          this.list_news = response.data;
          for (let item of this.list_news){
            if (item.file != undefined){
              item.file = this.PUBLIC_URL+item.file
            }
          }
        })
        .catch(function (error) {
          showAlertError(error,self)
        });
  }

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
  save() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    if (this.$route.params.invest_id !== undefined){
      this.loading = true
      this.data_form.invest_id = this.$route.params.invest_id;

      //si tiene id de noticia entonces es actualizar sino es uno nuevo
      InvestServices.saveInvestNews(this.data_form)
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
    showAlert("",self.$t('views.Estás seguro de borrar la noticia'), true, function() {
      InvestServices.deleteNews(self.$route.params.invest_id, id)
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
    this.data_form.title = ''
    this.data_form.url = ''
    this.data_form.summary = ''
    this.data_form.file_img = ''
  }

  showDescription(index){
    this.classModify = 'active';
    const myForm = document.getElementById('form')
    if (myForm != null) (myForm as HTMLInputElement).style.display = '';
    this.data_form = Object.assign({}, this.list_news[index]); // se pone asi para copiar sin perder los datos del listado
    if (this.data_form.file === undefined) {
      this.data_form.file_img = ""
    } else {
      this.data_form.file_img = this.data_form.file;
    }
    this.data_form.file = null;
  }
}


</script>
