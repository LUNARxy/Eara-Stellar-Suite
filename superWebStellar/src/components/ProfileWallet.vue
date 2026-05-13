<template>
  <div class="col s12 padding-0 padding-0" style="display: block">
    <div class="card padding-7 pt-2 pb-2 mt-0">
      <form @submit.prevent="sendWallet">
        <fieldset :disabled="data_item.kyc_valid == 1 || data_item.kyc_valid == 2">
          <div class="row">
            <div class="col s12 text-center">
              <h5>{{ $t('views.Wallet') }}</h5>
              <p v-if="data_item.kyc_valid != 1" class="mt-3 mb-3 text-left">{{ $t('views.Info wallet') }}</p>
            </div>
          </div>
          <div class="row">
            <div class="input-field col s12">
              <input id="wallet_address" v-model="data_item.wallet_address" type="text"  maxlength="200" required>
              <label for="wallet_address" class="active"><span class="required">*</span> {{ $t('views.Dirección de la wallet') }}</label>
            </div>
          </div>

          <div v-if="loading" class="progress">
            <div class="indeterminate"></div>
          </div>
          <div class="mt-3 text-right">
            <button v-if="is_kyc" class="btn-primary mr-3" type="button" @click="changeStep(2)">{{ $t('views.Anterior') }}</button>
            <button v-if="is_kyc" class="btn-primary" type="submit">{{ $t('views.Guardar') }}</button>
          </div>

        </fieldset>
      </form>
    </div>
  </div>
</template>
<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import {closeAlertProgress, showAlert, showAlertError, showAlertProgress} from "@/functions";
import UserServices from "@/services/UserServices";

@Options({
  props: {
    data_item: Object,
    is_kyc: Boolean
  }
})
export default class ProfileWallet extends Vue {
  data_item
  is_kyc

  loading = false

  sendWallet() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    this.loading = true
    showAlertProgress(this)
    UserServices.sendWallet(this.data_item.wallet_address)
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        .then(response => {
          closeAlertProgress(this)
          showAlert(this.$t('views.Proceso de identificación completado'), this.$t('views.Muchas gracias por completar el proceso de identificación_'), false, function() {
            self.$router.push('/userDetail')
          })
          self.loading = false
        })
        .catch(function (error) {
          console.error(error);
          self.loading = false
          closeAlertProgress(self)
          showAlertError(error, self)
        });
  }
}
</script>
