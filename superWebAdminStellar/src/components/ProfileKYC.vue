<template>

  <div class="col s12">
    <span v-if="data_item.name !== null">{{ $t('views.Nombre') }}: {{data_item.name}} {{data_item.surname}}</span>
    <p>{{ $t('views.Email') }}: {{data_item.email}}</p><br>

      <p class="bold">{{ $t('views.Estado de de la cuenta') }}:
        <template v-if="data_item.is_active">
        <span class="bold green-text">{{ $t('views.Activa') }}</span>&nbsp;&nbsp;&nbsp;
        <button class="btn-primary" style="background-color: #ff0000!important;" type="button" :disabled="loading" @click="changeStatusConfirm(false)">{{ $t('views.Desactivar usuario') }}</button>
        </template>
        <template v-if="!data_item.is_active">
        <span class="bold red-text">{{ $t('views.Desactivada') }}</span>&nbsp;&nbsp;&nbsp;
          <button class="btn-primary" style="background-color: #4CAF50!important;" type="button" :disabled="loading" @click="changeStatusConfirm(true)">{{ $t('views.Activar usuario') }}</button>
        </template>
      </p>
      <br>

    <template v-if="data_item.kyc_valid == 0">
      <p class="bold">{{ $t('views.Estado identificación') }}: <span class="bold" style="color: #deb268">{{ $t('views.SIN INICIAR') }}</span>&nbsp;&nbsp;&nbsp;
        <button class="btn-primary" type="button" :disabled="loading" @click="validateKYCConfirm(1)">{{ $t('views.Validar') }}</button>
      </p>
    </template>
    <template v-if="data_item.kyc_valid == 1">
      <br>
      <p class="bold">
        {{ $t('views.Estado identificación') }}: <span class="bold green-text">{{ $t('views.VÁLIDO') }}</span>&nbsp;&nbsp;&nbsp;
        <button id="bt_volver_rechazar" class="btn-primary" style="background-color: #ff0000!important;" type="button" @click="volverRechazar">{{ $t('views.Volver a rechazar') }}</button>
      </p>
      <div id="div_rechazar" style="display:none">
        <br>
        <p>{{ $t('views.Motivo del rechazo') }}:</p>
        <textarea v-model="kyc_no_valid_reason" maxlength="500"></textarea>
        <p>{{ $t('views.Motivo del rechazo_EN') }}:</p>
        <textarea v-model="kyc_no_valid_reason_EN" maxlength="500"></textarea>
        <button class="btn-primary right" style="background-color: #ff0000!important;" type="button" :disabled="loading" @click="validateKYCConfirm(3)">{{ $t('views.Rechazar') }}</button>
      </div>
    </template>

    <template v-if="data_item.kyc_valid == 2">
      <p class="bold">{{ $t('views.Estado identificación') }}: <span class="bold red-text">{{ $t('views.PENDIENTE DE VALIDAR') }}</span>&nbsp;&nbsp;&nbsp;
        <button class="btn-primary" type="button" :disabled="loading" @click="validateKYCConfirm(1)">{{ $t('views.Validar') }}</button>
      </p>
      <br>
      <p>{{ $t('views.Motivo del rechazo') }}:</p>
      <textarea v-model="kyc_no_valid_reason" maxlength="500"></textarea>
      <p>{{ $t('views.Motivo del rechazo_EN') }}:</p>
      <textarea v-model="kyc_no_valid_reason_EN" maxlength="500"></textarea>
      <button class="btn-primary right" style="background-color: #ff0000!important;" type="button" :disabled="loading" @click="validateKYCConfirm(3)">{{ $t('views.Rechazar') }}</button>
    </template>
    <template v-if="data_item.kyc_valid == 3">
      <p class="bold">{{ $t('views.Estado identificación') }}: <span class="bold red-text">{{ $t('views.RECHAZADO') }}</span>&nbsp;&nbsp;&nbsp;
        <button class="btn-primary" type="button" :disabled="loading" @click="validateKYCConfirm(1)">{{ $t('views.Validar') }}</button>
      </p>
      <br>
      <p class="bold">{{ $t('views.Motivo del rechazo') }}:</p>
      <p class="required text-left" v-html="data_item.kyc_no_valid_reason"></p>
    </template>


  </div>

</template>
<script lang="ts">
import {Options, Vue} from 'vue-class-component';

import store from "@/store";
import {Locales} from "@/locales/locales";
import {hideAlertLoading, showAlert, showAlertError, showAlertLoading} from "@/functions";
import UserServices from "@/services/UserServices";
import JQuery from "jquery";
import {compliantIdService} from "@/services/stellar/CompliantIdService";
import {lunarxyAdminService} from "@/services/stellar/LunarxyAdminService";

@Options({
  props: {
    data_item: Object,
  }
})
export default class ProfileKYC extends Vue {

  data_item
  kyc_no_valid_reason_EN = ''
  kyc_no_valid_reason = ''
  loading = false

  mounted(){
    if (store.getters.getLocale == Locales.EN) {
      this.data_item.kyc_no_valid_reason = this.data_item.kyc_no_valid_reason_EN
    }
  }


  async validateKYCConfirm(type){
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    // earastellar KYC approval: Soroban contract first, then backend.
    if (type == 1) {
      // 1. Require a connected Freighter wallet — attempt to connect if not already.
      let adminAddress = ''
      try {
        adminAddress = await compliantIdService.getConnectedAddress()
      } catch {
        // Not connected — try to connect now (will prompt the Freighter extension)
        try {
          const connection = await lunarxyAdminService.connectWallet()
          adminAddress = connection.address
        } catch (connectErr: unknown) {
          const msg = connectErr instanceof Error ? connectErr.message : String(connectErr)
          showAlert('Freighter', msg, false, function() { /* close only */ })
          return
        }
      }

      // 2. Require the user to have a wallet address and country configured.
      const walletAddress = self.data_item.wallet_address
      if (!walletAddress) {
        showAlert(
          'Stellar',
          'El usuario no tiene una dirección de wallet configurada. Añade una wallet al usuario antes de validar el KYC.',
          false,
          function() { /* close only */ }
        )
        return
      }
      const countryCode = self.data_item.country
      if (!countryCode) {
        showAlert(
          'Stellar',
          'El usuario no tiene un país configurado. Añade el país al usuario antes de validar el KYC.',
          false,
          function() { /* close only */ }
        )
        return
      }

      // 3. Show confirmation dialog; on confirm run Soroban → backend in order.
      let new_status = self.$t('views.VALIDADO')
      showAlert("KYC", self.$t('views.Estás seguro de cambiar el estado del KYC del usuario a', {'new_status': new_status}), true, async function() {
        self.loading = true
        showAlertLoading()

        // 3a. Call set_compliance on the Soroban contract first.
        //     status = 'Verified', level = 1, expires_at = now + 1 year
        try {
          const expiresAt = Math.floor(Date.now() / 1000) + 365 * 24 * 3600
          const result = await compliantIdService.setCompliance(adminAddress, walletAddress, 'Verified', 1, expiresAt, countryCode)
          if (!result.success) {
            hideAlertLoading()
            self.loading = false
            showAlert("Stellar", `No se pudo registrar el compliance en el contrato: ${result.errorMessage ?? 'error desconocido'}`, false, function() { /* close only */ })
            return
          }
        } catch (err: unknown) {
          hideAlertLoading()
          self.loading = false
          const msg = err instanceof Error ? err.message : String(err)
          showAlert("Stellar", `No se pudo registrar el compliance en el contrato: ${msg}`, false, function() { /* close only */ })
          return
        }

        // 3b. Contract succeeded — now call the backend.
        UserServices.validateKYC(self.data_item.user_id, type, self.kyc_no_valid_reason, self.kyc_no_valid_reason_EN)
          // eslint-disable-next-line no-unused-vars
          .then(response => {
            hideAlertLoading()
            self.loading = false
            showAlert("", self.$t('views.Datos guardados correctamente'), false, function() {
              self.$router.go(0)
            })
          })
          .catch(function(error) {
            hideAlertLoading()
            showAlertError(error, self)
            self.loading = false
          })
      })
      return
    }

    // earastellar KYC rejection: revoke_user on contract first, then backend.
    if (type == 3) {
      // 1. Require a connected Freighter wallet — attempt to connect if not already.
      let adminAddress = ''
      try {
        adminAddress = await compliantIdService.getConnectedAddress()
      } catch {
        try {
          const connection = await lunarxyAdminService.connectWallet()
          adminAddress = connection.address
        } catch (connectErr: unknown) {
          const msg = connectErr instanceof Error ? connectErr.message : String(connectErr)
          showAlert('Freighter', msg, false, function() { /* close only */ })
          return
        }
      }

      // 2. Require the user to have a wallet address configured.
      const walletAddress = self.data_item.wallet_address
      if (!walletAddress) {
        showAlert(
          'Stellar',
          'El usuario no tiene una dirección de wallet configurada. No se puede revocar en el contrato.',
          false,
          function() { /* close only */ }
        )
        return
      }

      // 3. Pre-flight: revoke_user requires the caller to be a registered trusted issuer.
      const isTrusted = await compliantIdService.isTrustedIssuer(adminAddress)
      if (!isTrusted) {
        showAlert(
          'Stellar',
          'Tu wallet no está registrada como trusted issuer en el contrato. Debes añadirla como trusted issuer antes de rechazar el KYC.',
          false,
          function() { /* close only */ }
        )
        return
      }

      // 4. Show confirmation dialog; on confirm run contract → backend.
      const new_status = self.$t('views.RECHAZADO')
      showAlert("KYC", self.$t('views.Estás seguro de cambiar el estado del KYC del usuario a', {'new_status': new_status}), true, async function() {
        self.loading = true
        showAlertLoading()

        // 4a. Call revoke_user on the Soroban contract first.
        try {
          const result = await compliantIdService.revokeUser(adminAddress, walletAddress)
          if (!result.success) {
            hideAlertLoading()
            self.loading = false
            showAlert("Stellar", `No se pudo revocar el usuario en el contrato: ${result.errorMessage ?? 'error desconocido'}`, false, function() { /* close only */ })
            return
          }
        } catch (err: unknown) {
          hideAlertLoading()
          self.loading = false
          const msg = err instanceof Error ? err.message : String(err)
          showAlert("Stellar", `No se pudo revocar el usuario en el contrato: ${msg}`, false, function() { /* close only */ })
          return
        }

        // 4b. Contract succeeded — now call the backend.
        UserServices.validateKYC(self.data_item.user_id, type, self.kyc_no_valid_reason, self.kyc_no_valid_reason_EN)
          // eslint-disable-next-line no-unused-vars
          .then(response => {
            hideAlertLoading()
            self.loading = false
            showAlert("", self.$t('views.Datos guardados correctamente'), false, function() {
              self.$router.go(0)
            })
          })
          .catch(function(error) {
            hideAlertLoading()
            showAlertError(error, self)
            self.loading = false
          })
      })
      return
    }

    let new_status = ''
    if (type == 1){
      new_status = self.$t('views.VALIDADO')
    } else if (type == 3){
      new_status = self.$t('views.RECHAZADO')
    }
    showAlert("KYC", self.$t('views.Estás seguro de cambiar el estado del KYC del usuario a', {'new_status': new_status}), true, function() {
      self.validateKYC(type)
    })
  }
  validateKYC(type){
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    self.loading = true
    showAlertLoading()
    UserServices.validateKYC(this.data_item.user_id, type, this.kyc_no_valid_reason, this.kyc_no_valid_reason_EN)
        // eslint-disable-next-line no-unused-vars
        .then(response => {
          hideAlertLoading()
          self.loading = false

          showAlert("",self.$t('views.Datos guardados correctamente'), false, function() {
            self.$router.go(0)
          })
        })
        .catch(function (error) {
          hideAlertLoading()
          showAlertError(error, self)
          self.loading = false
        });
  }


  changeStatusConfirm(status){
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    let new_status = self.$t('views.ACTIVA')
    if (!status){
      new_status = self.$t('views.DESACTIVADA')
    }
    showAlert(self.$t('views.Estado de de la cuenta'),self.$t('views.Estás seguro de cambiar el estado de la cuenta del usuario a ', {'new_status': new_status}), true, function() {
      self.changeStatus(status)
    })
  }

  changeStatus(status){
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    self.loading = true
    showAlertLoading()
    UserServices.changeStatus(this.data_item.user_id, status)
        // eslint-disable-next-line no-unused-vars
        .then(response => {
          hideAlertLoading()
          self.loading = false

          showAlert("",self.$t('views.Datos guardados correctamente'), false, function() {
            self.$router.go(0)
          })
        })
        .catch(function (error) {
          hideAlertLoading()
          showAlertError(error, self)
          self.loading = false
        });
  }

  volverRechazar(){
    JQuery('#bt_volver_rechazar').hide()
    JQuery('#div_rechazar').show()
  }

  generateReport(){
    console.log("generateReport")
  }
}
</script>
