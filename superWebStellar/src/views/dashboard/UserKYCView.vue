<template>
  <MenuUser />
  <div class="content_menu">

    <div class="col s12 text-center padding-3 pt-0">
          <h4 class="col s12 mt-0">{{ $t('views.Proceso de identificación') }}</h4>
          <p class="col s12 m10 offset-m1">{{ $t('views.Bienvenido a white_label Investing_') }}</p>
    </div>
    <div v-if="data_item.kyc_valid != 0" class="col s12">
      <div class="card">
        <div class="row card-content">
          <ProfileKYC v-if="loaded" :data_item="data_item" :show_button_process="false"/>
        </div>
      </div>
    </div>


    <!-- Stellar: loading while auto-checking wallet connection -->
    <div v-if="stellar_checking" class="col s12">
      <div class="card">
        <div class="card-content text-center">
          <div class="progress"><div class="indeterminate"></div></div>
          <p>{{ $t('views.Comprobando conexión de wallet...') }}</p>
        </div>
      </div>
    </div>

    <!-- Stellar wallet gate: shown when Stellar is active but wallet is not yet connected -->
    <div v-if="!stellar_checking && !stellar_wallet_connected" class="col s12">
      <div class="card">
        <div class="card-content text-center">
          <p>{{ $t('views.Para continuar con el proceso de identificación debes conectar tu wallet de Freighter (Stellar)') }}</p>
          <button class="btn-primary" @click="connectStellarWallet">
            {{ $t('views.Conectar Wallet') }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="stellar_wallet_connected" class="row">
      <div class="col s12">

        <div class="col s12 card">
          <div class="card-content">
            <div id="multi-step-form-container" class="mt-1">
              <ul class="form-stepper form-stepper-horizontal text-center mx-auto pl-0 mb-0">
                <!-- Step 1 -->
                <li class="form-stepper-active text-center form-stepper-list btn-navigate-form-step" step="1" step_number="1">
                  <a class="mx-2" style="cursor: initial;">
                    <span class="form-stepper-circle"><span>1</span></span>
                    <div class="label">{{ $t('views.Datos personales') }}</div>
                  </a>
                </li>
                <!-- Step 2 -->
                <li class="form-stepper-unfinished text-center form-stepper-list btn-navigate-form-step" step="2" step_number="2">
                  <a class="mx-2" style="cursor: initial;">
                    <span class="form-stepper-circle text-muted"><span>2</span></span>
                    <div class="label text-muted">{{ $t('views.Documentos') }}</div>
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div id="step-1" class="form-step">
          <ProfilePersonalData v-if="loaded" :data_item="data_item" :is_kyc="true"/>
        </div>
        <div id="step-2" class="form-step">
          <ProfileDocuments v-if="loaded" :data_item="data_item" :is_kyc="true" :on_saved="onDocumentsSaved"/>
        </div>

      </div>
    </div>

    <Footer />
  </div>
</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import M from "materialize-css";
import UserServices from "@/services/UserServices";
import {
  navigateToFormStep,
  showAlert,
  showAlertError,
  initStepper,
} from "@/functions";
import Editor from "@tinymce/tinymce-vue";
import MenuUser from "@/components/dashboard/MenuUser.vue";
import store from "@/store";
import {Locales} from "@/locales/locales";
import Footer from "@/components/Footer.vue";

import ProfileKYC from "@/components/ProfileKYC.vue";
import ProfilePersonalData from "@/components/ProfilePersonalData.vue";
import ProfileDocuments from "@/components/ProfileDocuments.vue";
import ProfileWallet from "@/components/ProfileWallet.vue";
import { stellarService } from "@/services/stellar/StellarService";
import ContractDataService from "@/services/ContractDataService";


@Options({
  components: {
    ProfileWallet,
    ProfileDocuments,
    ProfilePersonalData,
    ProfileKYC,
    Footer,
    MenuUser,
    Editor
  },
})
export default class UserKYCView extends Vue {

  loaded = false
  stellar_checking = false
  stellar_wallet_connected = false
  _isMounted = false
  // eslint-disable-next-line
  data_item: any = {}

  async mounted() {
    this._isMounted = true
    M.AutoInit();
    this.getUserData()
      this.stellar_checking = true
      try {
        await stellarService.initialize()
        const existing = await stellarService.checkWalletConnection()
        if (existing?.address) {
          await UserServices.sendWallet(existing.address)
          await this.checkTrustedAndProceed(existing.address)
        }
      } finally {
        this.stellar_checking = false
      }
  }

  beforeUnmount() {
    this._isMounted = false
  }

  async connectStellarWallet() {
    try {
      await stellarService.initialize()
      const connection = await stellarService.connectWallet()
      if (connection && connection.address) {
        await UserServices.sendWallet(connection.address)
        await this.checkTrustedAndProceed(connection.address)
      }
    } catch (error) {
      showAlertError(error, this)
    }
  }

  /**
   * After a Stellar wallet connects, check whether the address is a trusted
   * issuer in the CompliantId contract.
   * - Trusted  → redirect to /userDetail (no KYC needed)
   * - Not trusted → show the KYC form as normal
   * - Error → show alert and stay blocked so the user can retry
   */
  async checkTrustedAndProceed(address: string) {
    try {
      const response = await ContractDataService.isCompliantStellar(address)
      if (response.data.is_compliant) {
        showAlert(
          this.$t('views.Wallet verificada'),
          this.$t('views.Tu wallet ya está verificada como emisor de confianza'),
          false,
          () => this.$router.push('/userDetail')
        )
        return
      }
      // Not trusted — proceed with the KYC form
      this.stellar_wallet_connected = true
      await this.$nextTick()
      await this.$nextTick()
      initStepper()
      navigateToFormStep(1)
    } catch (error) {
      console.error('Error checking Stellar wallet compliance:', error)
      showAlertError(error, this)
    }
  }

  onDocumentsSaved() {
    this.$router.push('/userDetail')
  }

  getUserData() {
    UserServices.getUserData()
        .then(response => {
          this.data_item = response.data
          this.loaded = true

          if (this.data_item.kyc_valid == 1 || this.data_item.kyc_valid == 2) {
            this.$router.push('/userDetail')
            return
          }

          if (this.stellar_wallet_connected && this._isMounted) {
            navigateToFormStep(1)
          }

          if (store.getters.getLocale == Locales.EN) {
            this.data_item.kyc_no_valid_reason = this.data_item.kyc_no_valid_reason_EN
          }
        })
        .catch(function (error) {
          showAlertError(error, self)
        });
  }
}
</script>
<style>


.image-upload>input {
  display: none;
  position: relative;
  cursor: pointer;
}
.image-upload:hover .edit, .image-upload:hover .edit_profile {
  display: block;
}

.edit {
  padding-top: 7px;
  padding-right: 7px;
  position: absolute;
  right: 0;
  top: 0;
  display: none;
}
.edit_profile {
  padding-top: 7px;
  padding-right: 7px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: none;
}


</style>