<template>

  <Header/>

  <h4 v-if="is_dev_env" CLASS="text-center red-text">
    ESTO ES UN ENTORNO DE PRUEBAS
  </h4>


  <div class="row mb-0 mb-0">
    <div class="col s12 m6 offset-m3">
      <div class="card mt-10 padding-5">
        <div class="col s12 text-center padding-5">
          <img :src="getImgUrl('logo_large.png')" style="max-width: 150px">
        </div>
        <h4 class="text-center">
          {{ $t('views.Bienvenido a') }} {{ $t('views.white_label_name') }}
        </h4>
        <p class="text-center">{{ $t('views.Introduce tus datos para iniciar sesión') }}</p>
        <form @submit.prevent="login" class="padding-5">
          <div class="row mt-0 mb-0">
            <div class="input-field col s12">
              <i class="material-icons prefix pt-2">person_outline</i>
              <input id="user" name="user" v-model="user" required type="email">
              <label for="user" class="active">{{ $t('views.Email') }}</label>
            </div>
          </div>
          <div class="row mt-0 mb-0">
            <div class="input-field col s12">
              <i class="material-icons prefix pt-2">lock_outline</i>
              <input id="pass" name="pass" v-model="pass" required type="password">
              <label for="pass" class="active">{{ $t('views.Clave') }}</label>
            </div>
          </div>
          <input id="client_secret" name="client_secret" v-model="client_secret" type="text" style="display: none">
          <div class="row">
            <div class="col s12 text-right">
              <a href="#modal_box_recovery_pass" class="modal-trigger mt-3 primary-color">{{ $t('views.Olvidé mi contraseña') }}</a>
            </div>
          </div>
          <div class="row">
            <div class="input-field col s12 text-center">
              <button :disabled="loading" type="submit" class="btn-primary">{{ $t('views.Iniciar sesión') }}</button>&nbsp;
            </div>
          </div>
        </form>

        <div class="row">
          <div class="col s12">
            {{ $t('views.Nuevo en nuestra plataforma') }} <router-link to="/register" class="primary-color">{{ $t('views.Registrate ahora') }}</router-link>
          </div>
        </div>

      </div>
    </div>
  </div>



  <div id="modal_box_recovery_pass" class="modal border-radius-15">
    <form @submit.prevent="recovery">
      <div class="modal-content " style="text-align: center;">
        <div class="row">
          <div class="input-field col s12">
            <h5 class="mt-3">{{ $t('views.Recordar contraseña') }}</h5>
          </div>
        </div>
        <p id="modal_box_confirm_text">{{ $t('views.Te enviaremos un email y podrás restaurar una nueva contraseña') }}</p>
        <div class="row">
          <div class="input-field col s12 m12">
            <label for="r_email" class="center-align">{{ $t('views.Email') }}</label>
            <input id="r_email" name="r_email" type="email" required>
          </div>
        </div>
      </div>
      <div id="modal_box_close_button" class="modal-footer mb-3 ">
        <input type="hidden" name="g-recaptcha-response" id="g-recaptcha-response_recovery">
        <button :disabled="loading" type="submit" class="btn-primary">{{ $t('views.Aceptar') }}</button>&nbsp;&nbsp;&nbsp;
        <button type="button" class="btn-secondary modal-close">{{ $t('views.Cerrar') }}</button>&nbsp;&nbsp;&nbsp;
      </div>
    </form>
  </div>

  <!-- Modal alert -->
  <div id="modal_alert" class="modal border-radius-10 border-radius-15"  style="margin-top: 60px;">
    <div class="modal-content text-center">
      <h5 class="text-grey" id="modal_alert_header">{{ $t('views.Alerta') }}</h5>
      <div id="modal_alert_text"></div>
    </div>
    <div class="modal-footer mb-3">
      <button id="modal_alert_bt_ok" type="button" class="btn-secondary modal-close">{{ $t('views.Aceptar') }}</button>&nbsp;&nbsp;&nbsp;
      <button id="modal_alert_bt_cancel" type="button" class="btn-secondary modal-close display-none">{{ $t('views.Cancelar') }}</button>&nbsp;&nbsp;&nbsp;
    </div>
  </div>

  <Footer />
</template>



<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import Header from "@/components/Header.vue"
import Footer from "@/components/Footer.vue";
import UserServices from '@/services/UserServices'
import store from "../store";
import M from "materialize-css";
import {funcGetImgUrl, showAlert, showAlertError} from "@/functions";
import JQuery from 'jquery';

@Options({
  components: {
    Header,
    Footer,
  },
})
export default class LoginView extends Vue {
  is_dev_env = process.env.VUE_APP_BASEURL.toString().includes('api.desa.lunarxy.com')

  loading = false
  user = ''
  pass = ''
  client_secret = ''


  mounted () {
    M.AutoInit();
    if (this.$route.params.email){
      this.user = this.$route.params.email
    }
  }

  login() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    this.loading = true
    UserServices.getAccesToken(this.user, this.pass, this.client_secret)
        .then(response => {
          self.loading = false

          store.commit('AUTH_SUCCESS', response.data)

          if (this.$route.params.go_back != undefined && this.$route.params.go_back == "go_back"){
            // es un login por alguna accion, volvemos a la pagina donde estabamos
            this.$router.go(-1)
          } else {
            if (process.env.VUE_APP_WHITE_LABEL_IS_DEVELOPMENT === "true"){
              window.location.href = '/earastellarapp/';
            } else {
              window.location.href = "/";
            }
          }
        })
        .catch(function (error) {
          self.loading = false
          showAlertError(error, self)
        });
  }

  recovery() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    this.loading = true
    let email = JQuery('#r_email').val()
    UserServices.recoveryPass(email.toString())
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        .then(response => {
          self.loading = false
          showAlert(self.$t('views.Recuperar contraseña'),self.$t('views.Se ha enviado un correo a la dirección')+':<br>'+email+'<br>'+self.$t('views.Revise su correo y siga las instrucciones'))
        })
        .catch(function (error) {
          self.loading = false
          showAlertError(error, self)
        });
  }

  getImgUrl(pic) {
    return funcGetImgUrl(pic)
  }
}
</script>

