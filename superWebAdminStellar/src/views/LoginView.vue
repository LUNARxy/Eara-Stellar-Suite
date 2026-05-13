<template>

  <h4 v-if="is_dev_env" CLASS="text-center red-text">
    ESTO ES UN ENTORNO DE PRUEBAS
  </h4>

  <div class="row mb-0 mb-0">
    <div class="col s12 m6 offset-m3">
      <div class="card mt-10 text-center">
        <form @submit.prevent="login" class="padding-7">
          <div class="row">
            <div class="col s12">
              <img :src="getImgUrl('logo_large.png')" style="max-width: 150px">
            </div>
            <div class="col s12">
              <h5>{{ $t('views.Panel administrador') }}</h5>
            </div>
          </div>
          <div class="row margin">
            <div class="input-field col s12">
              <i class="material-icons prefix pt-2">person_outline</i>
              <input id="user" name="user" v-model="user" required type="text">
              <label for="user" class="center-align">{{ $t('views.Usuario') }}</label>
            </div>
          </div>
          <div class="row margin">
            <div class="input-field col s12">
              <i class="material-icons prefix pt-2">lock_outline</i>
              <input id="pass" name="pass" v-model="pass" required type="password">
              <label for="pass">{{ $t('views.Clave') }}</label>
            </div>
          </div>

          <input id="client_secret" name="client_secret" v-model="client_secret" type="text" style="display: none">

          <div class="row">
            <div class="input-field col s12">
              <button :disabled="loading" type="submit" class="btn-primary">{{ $t('views.Entrar') }}</button>&nbsp;
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>


  <!-- Modal alert -->
  <div id="modal_alert" class="modal border-radius-10 border-radius-15"  style="margin-top: 60px;">
    <div class="modal-content text-center">
      <h4 id="modal_alert_header"></h4>
      <div id="modal_alert_text"></div>
    </div>
    <div class="modal-footer mb-3">
      <button id="modal_alert_bt_ok" type="button" class="btn-secondary modal-close">{{ $t('views.aceptar') }}</button>&nbsp;&nbsp;&nbsp;
      <button id="modal_alert_bt_cancel" type="button" class="btn-secondary modal-close display-none">{{ $t('views.cancelar') }}</button>&nbsp;&nbsp;&nbsp;
    </div>
  </div>

</template>



<script lang="ts">
import { Vue } from 'vue-class-component';
import UserServices from '@/services/UserServices'
import store from "../store";
import M from "materialize-css";
import {showAlertError} from "@/functions";



export default class LoginView extends Vue {
  is_dev_env = process.env.VUE_APP_BASEURL.toString().includes('api.desa.lunarxy.com')

  loading = false
  user = ''
  pass = ''
  client_secret = ''


  mounted () {
    M.AutoInit();
  }

  login() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    this.loading = true
    store.commit('AUTH_LOGOUT')
    UserServices.getAccesToken(this.user, this.pass, this.client_secret)
        .then(response => {
          store.commit('AUTH_SUCCESS', response.data)
          if (process.env.VUE_APP_WHITE_LABEL_IS_DEVELOPMENT !== "true"){
            window.location.href = '/'
          } else {
            window.location.href = '/earastellaradmin'
          }
        })
        .catch(function (error) {
          self.loading = false
          showAlertError(error, self)
        });
  }

  getImgUrl(pic) {
    if (process.env.VUE_APP_WHITE_LABEL_IS_DEVELOPMENT !== "true"){
      return '/earastellar/' + pic
    } else {
      return '/earastellaradmin/earastellar/' + pic
    }
  }
}
</script>

