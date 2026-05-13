<template>
  <div class="col s12 padding-0 padding-0" style="display: block">
    <div class="card padding-7 pt-2 pb-2 mt-0">

      <form @submit.prevent="changePassword">
        <div class="row">
          <div class="col s12 text-center">
            <h5>{{ $t('views.Cambiar contraseña') }}</h5>
          </div>
        </div>
        <div class="row">
          <div class="input-field col s12 m6">
            <i class="material-icons prefix pt-2">lock_outline</i>
            <input id="pass1" v-model="data_item.pass1" type="password" required minlength="8" maxlength="50">
            <label for="pass1">{{ $t('views.Contraseña nueva') }}</label>
          </div>
          <div class="input-field col s12 m6">
            <i class="material-icons prefix pt-2">lock_outline</i>
            <input id="pass2" v-model="data_item.pass2" type="password" required minlength="8" maxlength="50">
            <label for="pass2">{{ $t('views.Repetir Contraseña') }}</label>
          </div>
        </div>
        <div class="row">
          <div class="s12">

            <div v-if="loading" class="progress">
              <div class="indeterminate"></div>
            </div>

            <button :disabled="loading" type="submit" class="btn-primary right">{{ $t('views.Cambiar contraseña') }}</button>
          </div>
        </div>
      </form>

    </div>
  </div>
</template>
<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import {hideAlertLoading, showAlert, showAlertError, showAlertLoading} from "@/functions";
import UserServices from "@/services/UserServices";

@Options({
  props: {
    data_item: Object,
  }
})
export default class ProfilePassword extends Vue {
  data_item

  loading = false

  changePassword(){
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    if (this.data_item.pass1 == "" || this.data_item.pass1 == "undefined"
        || this.data_item.pass1 == "" || this.data_item.pass1 == "undefined"){
      showAlert("",this.$t('views.Rellene todos los campos'))
    } else if (this.data_item.pass1 !== this.data_item.pass2){
      showAlert("",this.$t('views.Las claves son distintas'))
    } else {
      // eslint-disable-next-line @typescript-eslint/no-this-alias
      const self = this
      this.loading = true
      showAlertLoading()
      UserServices.updateUserPassword(this.data_item.pass1, this.data_item.user_id)
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          .then(response => {
            hideAlertLoading()
            self.loading = false

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


}
</script>
