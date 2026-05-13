<template>

  <Header/>

  <h4 v-if="is_dev_env" CLASS="text-center red-text margin-0">
    ESTO ES UN ENTORNO DE PRUEBAS
  </h4>


  <div class="row mb-0 mb-0">
    <div class="col s12 m8 offset-m2">
      <div class="card mt-10">
        <div class="col s12 text-center padding-5">
          <img :src="getImgUrl('logo_large.png')" style="max-width: 150px">
        </div>
        <h4 class="text-center">
          {{ $t('views.Bienvenido a') }} {{ $t('views.white_label_name') }}
        </h4>
        <p class="text-center">{{ $t('views.Regístrate ahora y forma parte de nuestra comunidad') }}</p>
        <form @submit.prevent="register" class="padding-5">
          <div class="row mt-0 mb-0">
            <div class="input-field col s12">
              <i class="material-icons prefix pt-2">email</i>
              <input id="email" name="email" v-model="data_form.email" required type="email">
              <label for="email" class="center-align"><span class="required">*</span> {{ $t('views.Email') }}</label>
            </div>
          </div>
          <div class="row mt-0 mb-0">
            <div class="input-field col s12 m6">
              <i class="material-icons prefix pt-2">lock_outline</i>
              <input id="pass1" name="pass1" v-model="data_form.pass1" required type="password" minlength="8" maxlength="50">
              <label for="pass1"><span class="required">*</span> {{ $t('views.Clave') }}</label>
              <div v-if="data_form.pass1" class="col s12 mb-2" style="padding-left: 3rem;">
                <small>
                  <ul class="mb-0" style="margin-top: 0;">
                    <li :class="{'green-text': passwordComplexity.length, 'red-text': !passwordComplexity.length}">
                      <i class="material-icons tiny left" v-if="passwordComplexity.length">check</i>
                      <i class="material-icons tiny left" v-else>close</i>
                      {{ $t('Mínimo 8 caracteres') }}
                    </li>
                    <li :class="{'green-text': passwordComplexity.uppercase, 'red-text': !passwordComplexity.uppercase}">
                      <i class="material-icons tiny left" v-if="passwordComplexity.uppercase">check</i>
                      <i class="material-icons tiny left" v-else>close</i>
                      {{ $t('Al menos una mayúscula') }}
                    </li>
                    <li :class="{'green-text': passwordComplexity.lowercase, 'red-text': !passwordComplexity.lowercase}">
                      <i class="material-icons tiny left" v-if="passwordComplexity.lowercase">check</i>
                      <i class="material-icons tiny left" v-else>close</i>
                      {{ $t('Al menos una minúscula') }}
                    </li>
                    <li :class="{'green-text': passwordComplexity.special, 'red-text': !passwordComplexity.special}">
                      <i class="material-icons tiny left" v-if="passwordComplexity.special">check</i>
                      <i class="material-icons tiny left" v-else>close</i>
                      {{ $t('Al menos un carácter especial') }}
                    </li>
                  </ul>
                </small>
              </div>
            </div>
            <div class="input-field col s12 m6">
              <i class="material-icons prefix pt-2">lock_outline</i>
              <input id="pass2" name="pass2" v-model="data_form.pass2" required type="password" minlength="8" maxlength="50">
              <label for="pass2"><span class="required">*</span> {{ $t('views.Repetir Clave') }}</label>
            </div>
          </div>
          <div class="row">
            <div class="col s12">
              <p class="ml-2">
                <label>
                  <input type="checkbox" class="filled-in" required/>
                  <span style="color: #757575" v-html="$t('views.Acepto la Política de Privacidad de')"></span>
                </label>
              </p>
            </div>
          </div>
          <div class="row">
            <div class="input-field col s12 text-center">
              <button :disabled="loading" type="submit" class="btn-terciary">{{ $t('views.Registrarse') }}</button>&nbsp;
            </div>
          </div>

          <div class="row">
            <div class="col s12">
              {{ $t('views.Ya estás registrado') }} <router-link to="/login" class="primary-color">{{ $t('views.Inicia sesión aquí') }}</router-link>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>



  <!-- Modal alert loading -->
  <div id="modal_loading" class="modal" >
    <div class="modal-content" style="text-align: center;">
      <p id="msg_modal_loading">{{ $t('views.Cargando datos') }}...</p>
      <div class="progress"><div class="indeterminate"></div></div>
    </div>
  </div>

  <Footer />
</template>



<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import Header from "@/components/Header.vue"
import Footer from "@/components/Footer.vue";
import UserServices from '@/services/UserServices'
import M from "materialize-css";
import {funcGetImgUrl, hideAlertLoading, showAlert, showAlertError, showAlertLoading} from "@/functions";

@Options({
  components: {
    Header,
    Footer,
  },
})
export default class RegisterView extends Vue {
  is_dev_env = process.env.VUE_APP_BASEURL.toString().includes('api.desa.lunarxy.com')

  loading = false
  data_form = {"email":null,"pass1":null,"pass2":null,"name":null,"surname":null,"phone": null}

  mounted () {
    M.AutoInit();
  }

  get passwordComplexity() {
    const password = this.data_form.pass1 || '';
    return {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      special: /[^A-Za-z0-9]/.test(password)
    }
  }

  register() {
    if (this.data_form.email == "" || this.data_form.email == "undefined"
        || this.data_form.pass1 == "" || this.data_form.pass1 == "undefined"
        || this.data_form.pass2 == "" || this.data_form.pass2 == "undefined"){
      showAlert("",this.$t('views.Rellene todos los campos'))
    } else if (!this.passwordComplexity.length || !this.passwordComplexity.uppercase || !this.passwordComplexity.lowercase || !this.passwordComplexity.special) {
      showAlert("", this.$t('views.La contraseña no cumple con los requisitos de complejidad'));
    } else if (this.data_form.pass1 !== this.data_form.pass2){
      showAlert("",this.$t('views.Las claves son distintas'))
    } else {
      // eslint-disable-next-line @typescript-eslint/no-this-alias
      const self = this
      this.loading = true

      let txt_key = 'views.Se ha registrado correctamente'
      showAlertLoading()
      UserServices.createUser(this.data_form)
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          .then(response => {
            hideAlertLoading()
            showAlert(self.$t('views.Se ha registrado correctamente'),self.$t(txt_key),
                false,
                function() {
                  self.$router.push('/login')
                })
          })
          .catch(function (error) {
            self.loading = false
            hideAlertLoading()
            showAlertError(error, self)
          });
    }
  }

  getImgUrl(pic) {
    return funcGetImgUrl(pic)
  }
}
</script>

