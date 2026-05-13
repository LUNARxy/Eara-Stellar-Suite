<template>

  <Menu/>
  <div class="content_menu">
    <div class="row">


      <h4 class="col s12 text-center" v-if="category_name === 'holding'">{{ $t('views.Holding') }}</h4>
      <h4 class="col s12 text-center" v-if="category_name === 'equity'">{{ $t('views.Equity') }}</h4>
      <h4 class="col s12 text-center" v-if="category_name === 'debt'">{{ $t('views.Deuda') }}</h4>
      <h4 class="col s12 text-center" v-if="category_name === 'interest'">{{ $t('views.Interés compuesto') }}</h4>

      <form @submit.prevent="save">
        <div class="col s12">
          <div class="card">
            <div class="card-content">
              <!--
              <div>Token ID: {{data_form.token_id}}</div>
              <div>Contract Address: {{data_form.contract_address}}</div>
              -->
              <div v-if="!data_form.is_completed && data_form.id !== 41" class="row mt-3">
                <div class="input-field col s12">
                  <p>
                    <label>
                      <input type="checkbox" class="filled-in" v-model="data_form.is_draft"/>
                      <span>{{ $t('views.Marcar si el proyecto está en borrador') }}</span>
                    </label>
                  </p>
                </div>
              </div>
              <div class="row">
                <div class="input-field col s12 m6">
                  <label for="name" :class="{ active: classModify }"><span class="required">*</span> {{ $t('views.Nombre') }}:</label>
                  <input type="text" id="name" v-model="data_form.name" maxlength="200" required>
                </div>
                <div class="input-field col s12">
                  <label for="title" :class="{ active: classModify }"><span class="required">*</span> {{ $t('views.Título') }}:</label>
                  <input type="text" id="title" v-model="data_form.title" maxlength="500" required>
                </div>
                <div class="input-field col s12">
                  <label for="summary" class="active"><span class="required">*</span> {{ $t('views.resumen_dos_mil') }}</label>
                  <br><vue-editor id="summary" v-model="data_form.summary"></vue-editor>
                </div>
                <div class="input-field col s12">
                  <label for="description" class="active"><span class="required">*</span> {{ $t('views.Descripción_diez_mil') }}</label>
                  <br><vue-editor id="description" v-model="data_form.description"></vue-editor>
                </div>
                <div class="input-field col s12">
                  <label for="proposal_to_investors" class="active">{{ $t('views.Propuesta a los inversores_dos_mil_car') }}</label>
                  <br><vue-editor id="proposal_to_investors" v-model="data_form.proposal_to_investors"></vue-editor>
                </div>

                <div class="input-field col s12">
                  <h5>Otros datos del proyecto</h5>
                </div>
                <div class="row pl-2">
                  <div class="input-field col s12 m9">
                    <label for="profit_estimated_description" :class="{ active: classModify }">{{ $t('views.Descripcion Rentabilidad') }}:</label>
                    <input type="text" id="profit_estimated_description" v-model="data_form.profit_estimated_description" maxlength="20">
                  </div>
                  <div class="input-field col s12 m3" v-if="category_name === 'interest'">
                    <label for="profit_estimated" :class="{ active: classModify }"><span class="required">*</span> % {{ $t('views.Rentabilidad') }}:</label>
                    <input type="text" id="profit_estimated" v-model="data_form.profit_estimated" maxlength="5" required @keydown="myNumbersOnly($event, true)">
                  </div>
                  <div class="input-field col s12 m6">
                  </div>
                  <div class="input-field col s12 m4">
                  </div>
                </div>

                <div class="row pl-2">
                  <div class="input-field col s12 m6">
                    <label for="time_limit" :class="{ active: classModify }">{{ $t('views.Tiempo de finalización') }}:</label>
                    <input type="text" id="time_limit" v-model="data_form.time_limit" maxlength="50">
                  </div>
                </div>



                <div class="input-field col s12">
                  <p>
                    <label>
                      <input type="checkbox" class="filled-in" id="hide_time_data" v-model="data_form.hide_time_data"/>
                      <span>{{ $t('views.Ocultar la tarjeta entera de datos de cuenta atrás') }}</span>
                    </label>
                  </p>
                </div>
                <div class="input-field col s12">
                  <p>
                    <label>
                      <input type="checkbox" class="filled-in" id="hide_date_start_round" v-model="data_form.hide_date_start_round"/>
                      <span>{{ $t('views.Ocultar la fecha de inicio de la ronda') }}</span>
                    </label>
                  </p>
                </div>
                <div class="input-field col s12">
                  <p>
                    <label>
                      <input type="checkbox" class="filled-in" id="hide_date_end_round" v-model="data_form.hide_date_end_round"/>
                      <span>{{ $t('views.Ocultar la fecha de fin de la ronda') }}</span>
                    </label>
                  </p>
                </div>
                <div class="input-field col s12">
                  <p>
                    <label>
                      <input type="checkbox" class="filled-in" id="hide_profit_estimated" v-model="data_form.hide_profit_estimated"/>
                      <span>{{ $t('views.Ocultar la rentabilidad estimada') }}</span>
                    </label>
                  </p>
                </div>

                <div class="input-field col s12">
                  <p>
                    <label>
                      <input type="checkbox" class="filled-in" id="hide_value_round" v-model="data_form.hide_value_round"/>
                      <span>{{ $t('views.Ocultar el valor de la ronda') }}</span>
                    </label>
                  </p>
                </div>
                <div class="input-field col s12">
                  <p>
                    <label>
                      <input type="checkbox" class="filled-in" id="hide_num_tokens" v-model="data_form.hide_num_tokens"/>
                      <span>{{ $t('views.Ocultar el número de tokens') }}</span>
                    </label>
                  </p>
                </div>

                <div class="input-field col s12">
                  <h5>{{ $t('views.Localización del proyecto') }}</h5>
                </div>
                <div class="input-field col s12">
                  <label for="location" :class="{ active: classModify }">{{ $t('views.Dirección') }}:</label>
                  <input type="text" id="location" v-model="data_form.location" maxlength="300">
                </div>
                <div class="input-field col s12 m6">
                  <label for="web" :class="{ active: classModify }">{{ $t('views.WEB') }}:</label>
                  <input type="text" id="web" v-model="data_form.web" maxlength="200">
                </div>


              </div>
            </div>
          </div>


          <div class="card">
            <div class="card-content">
              <h4 class="card-title">{{ $t('views.Fotos del proyecto') }}:</h4>

              <div class="row">
                <div class="input-field col s12 m6">
                  <img id="file_top_img" :src="data_form.file_top_img" class="responsive-img">
                </div>
                <div class="input-field col s12 m6">
                  <div class="mb-3"><span class="required">*</span> {{ $t('views.Foto grande del detalle') }}</div>
                  <div>
                    <input id="file_top" type="file" @change="handleFileUploadBig( $event )" required/>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="input-field col s12 m6">
                  <img id="file_img" :src="data_form.file_img" class="responsive-img">
                </div>
                <div class="input-field col s12 m6">
                  <div class="mb-3"><span class="required">*</span> {{ $t('views.Foto de las cartas') }}</div>
                  <div>
                    <input id="file" type="file" @change="handleFileUploadSmall( $event )" required/>
                  </div>
                </div>
              </div>

            </div>
          </div>


          <div class="row">
            <div class="input-field col s12">
              <input type="hidden" id="id" name="id" v-model="data_form.id">
              <button class="btn-primary right" type="submit" :disabled="loading">{{ $t('views.guardar') }}</button>
            </div>
          </div>

        </div>
      </form>
    </div>
  </div>

</template>


<script lang="ts">
import InvestServices from '@/services/InvestServices'
import {Options, Vue} from "vue-class-component";
import Menu from "@/components/Menu.vue";
import {formatDateFromServer, isValidDate, numbersOnly, showAlert, showAlertError, validateCorrectFile} from "@/functions";
import { VueEditor } from "vue3-editor";
import {PUBLIC_URL} from "@/services/Http-common";

@Options({
  components: {
    Menu,
    VueEditor
  },
})
export default class InvestProjectsFormView extends Vue {
  PUBLIC_URL = PUBLIC_URL

  loading = false
  classModify = ''
  category_name = ''

  // eslint-disable-next-line
  data_form: any = {}

  invest_id = 0

  mounted () {
    if (this.$route.params.category_name != null) {
      this.category_name = this.$route.params.category_name?.toString()
    }

    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    this.invest_id = this.$route.params.id
    if (this.$route.params.id !== undefined) {

      //quitamos el required al ser modificacion
      (document.getElementById("file") as HTMLInputElement).required = false;
      (document.getElementById("file_top") as HTMLInputElement).required = false;

      InvestServices.getInvestProject(this.$route.params.id, false, true)
          .then(response => {
            this.classModify = 'active';
            this.data_form = response.data;
            if (this.data_form.file_top === undefined) {
              this.data_form.file_top_img = ""
            } else {
              this.data_form.file_top_img = this.PUBLIC_URL + this.data_form.file_top;
            }
            this.data_form.file_top = null;

            if (this.data_form.file === undefined) {
              this.data_form.file_img = ""
            } else {
              this.data_form.file_img = this.PUBLIC_URL + this.data_form.file;
            }
            this.data_form.file = null;

            this.data_form.date_start_round = formatDateFromServer(this.data_form.date_start_round, false)
            this.data_form.date_end_round = formatDateFromServer(this.data_form.date_end_round, false)
            this.data_form.date_end_over_value_round = formatDateFromServer(this.data_form.date_end_over_value_round, false)
            this.data_form.date_end = formatDateFromServer(this.data_form.date_end, false)


            this.calculatePriceToken()
          })
          .catch(function (error) {
            showAlertError(error, self)
          });
    } else {
      this.data_form.is_draft = 1;
    }
  }

  save () {
    if (this.data_form.summary == undefined || this.data_form.summary.length == 0){
      showAlertError(this.$t('views.El campo Resumen tiene que tener contenido'), this)
    } else if (this.data_form.description == undefined || this.data_form.description.length == 0){
      showAlertError(this.$t('views.El campo Descripción tiene que tener contenido'), this)
    } else {
      // eslint-disable-next-line @typescript-eslint/no-this-alias
      const self = this
      this.loading = true

      if (this.data_form.id !== undefined && this.data_form.id !== "") {
        //es una actualizacion
        InvestServices.updateInvestProject(this.data_form)
            .then(response => {
              showAlert("", self.$t('views.Datos guardados correctamente'), false, function () {
                if (self.category_name != '') {
                  self.$router.go(-1)
                } else {
                  self.$router.go(-1)
                }
              })
            })
            .catch(function (error) {
              self.loading = false
              showAlertError(error, self)
            });
      } else {
        //es nuevo
        InvestServices.saveInvestProject(this.data_form)
            .then(response => {
              showAlert("", self.$t('views.Datos guardados correctamente'), false, function () {
                self.$router.go(-1)
                //window.location.href = '/InvestProjectsList/'+self.category_name
              })
            })
            .catch(function (error) {
              self.loading = false
              showAlertError(error, self)
            });
      }
    }
  }


  async handleFileUploadBig( event ){
    this.data_form.file_top = event.target.files[0];
    if (this.data_form.file_top) {
      // Validar el tipo de archivo
      if (await validateCorrectFile(this.data_form.file_top, this)) {
        const file_img = document.getElementById('file_top_img')
        if (file_img != null) (file_img as HTMLInputElement).src = URL.createObjectURL(this.data_form.file_top)
      } else {
        this.data_form.file_top = null
      }
    }
  }

  async handleFileUploadSmall( event ){
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

  calculatePriceToken(){
    this.data_form.price_token = this.data_form.value_round/this.data_form.num_tokens
  }


  myNumbersOnly(evt, decimals = false){
    numbersOnly(evt, decimals)
  }
}



</script>
