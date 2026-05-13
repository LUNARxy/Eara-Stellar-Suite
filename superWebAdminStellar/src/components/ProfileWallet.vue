<template>
  <div class="col s12 padding-0 padding-0" style="display: block">
    <div class="card padding-7 pt-2 pb-2 mt-0">
      <form @submit.prevent="sendWallet">
        <fieldset>

          <div class="row">
            <div class="input-field col s12">
              <input id="wallet_address" v-model="data_item.wallet_address" type="text"  maxlength="200" required>
              <label for="wallet_address" class="active"><span class="required">*</span> {{ $t('views.Dirección de la wallet') }}</label>
            </div>
          </div>

          <div class="mt-3 text-right">
            <button class="btn-primary" type="submit">{{ $t('views.Guardar') }}</button>
          </div>

        </fieldset>
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
    data_item: Object
  }
})
export default class ProfileWallet extends Vue {
  data_item

  loading = false

  sendWallet() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    this.loading = true
    showAlertLoading()
    UserServices.sendWallet(this.data_item.wallet_address, this.data_item.user_id)
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        .then(response => {
          hideAlertLoading()
          self.loading = false

          showAlert("",self.$t('views.Datos guardados correctamente'), false, function() {
            self.$router.go(0)
          })
        })
        .catch(function (error) {
          console.error(error);
          self.loading = false
          hideAlertLoading()
          showAlertError(error, self)
        });
  }
}
</script>
