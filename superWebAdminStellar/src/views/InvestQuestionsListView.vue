<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="card padding-3">
          <div class="card-content">

            <h4 class="card-title mb-5">{{ $t('views.PREGUNTAS Y RESPUESTAS') }}</h4>
            <button class="btn-primary right" @click="showForm">{{ $t('views.Nueva') }}</button>

            <form id="form" @submit.prevent="save" class="mb-4" style="display: none">
              <div class="row padding-7">
                <div class="input-field col s12">
                  <label for="title" :class="{ active: classModify }"><span class="required">*</span> {{ $t('views.Título') }}:</label>
                  <input type="text" id="title" v-model="data_form.title" maxlength="200" required>
                </div>
                <div class="input-field col s12">
                  <label for="comment" class="active"><span class="required">*</span> {{ $t('views.Respuesta_') }}</label>
                  <!--<br><editor id="comment" v-model="data_form.comment" :init="{height: 500,plugins: 'wordcount',menubar: false,toolbar:'undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help'}"/>-->
                  <br><vue-editor id="comment" v-model="data_form.comment"></vue-editor>
                  <!--<input type="text" id="comment" v-model="data_form.comment" maxlength="2000" required>-->
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
                <th>{{ $t('views.Título') }}</th>
                <th></th>
              </tr>
              </thead>

              <tbody>
              <tr v-for="(item, itemObjKey) in list_questions" :key="item.id">
                <td>{{ item.title }}</td>
                <td width="150px">
                  <button class="btn-primary mr-3" @click.stop="showDescription(itemObjKey)"><i class="material-icons">edit</i></button>
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
import {showAlert, showAlertError} from "@/functions";

import { VueEditor } from "vue3-editor";
import JQuery from "jquery";
import {PUBLIC_URL} from "@/services/Http-common";



@Options({
  components: {
    Menu,
    VueEditor
  },
})
export default class InvestQuestionsListView extends Vue {
  PUBLIC_URL = PUBLIC_URL
  list_questions = []
  loading = false
  classModify = ''


  // eslint-disable-next-line
  data_form: any = {}

  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    InvestServices.getInvestQuestions(this.$route.params.invest_id)
        .then(response => {
          this.list_questions = response.data;
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
      InvestServices.saveInvestQuestions(this.data_form)
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
    showAlert("",self.$t('views.Estás seguro de borrar la pregunta'), true, function() {
      InvestServices.deleteQuestions(self.$route.params.invest_id, id)
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
    this.data_form.comment = ''
  }

  showDescription(index){
    this.classModify = 'active';
    const myForm = document.getElementById('form')
    if (myForm != null) (myForm as HTMLInputElement).style.display = '';
    this.data_form = Object.assign({}, this.list_questions[index]); // se pone asi para copiar sin perder los datos del listado
  }
}


</script>
