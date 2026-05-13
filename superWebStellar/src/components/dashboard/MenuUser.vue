<template>
  <nav>
    <div class="my_nav_menu_user cab-with-menu row">

      <div class="col s2 m2 hide-on-large-only hide-on-extra-large-only" style="max-height: 70px;">
        <a href="#" data-target="slide-out" class="sidenav-trigger s2" style="color: #ffffff"><i class="material-icons" style="font-size:20px;">menu</i></a>
      </div>
      <div class="col s8 m8 text-center hide-on-large-only hide-on-extra-large-only">
        <router-link to="/" class="mt-1" style="font-size: 13px">
          <img style="max-height: 50px; vertical-align: middle; padding:10px 20px 5px 20px;" :src="getImgUrl('logo_white.png')" alt="logo">
        </router-link>
      </div>
      <div class="col s2 m2 l12">
        <div class="text-right" style="display: flex; align-items: center; justify-content: right;">
          <button v-if="!wallet_connected" type="button" class="btn-terciary mr-3 hide-on-med-and-down" style="padding: 8px 24px" @click="connect">{{ $t('views.Conectar Wallet') }}</button>
          <button v-if="wallet_connected" type="button" class="btn-terciary mr-3 hide-on-med-and-down" style="padding: 8px 24px">{{current_addressSubMobile}}</button>
          <MenuUserRight />
        </div>
      </div>
    </div>
  </nav>

  <ul id="slide-out" class="sidenav sidenav-fixed pb-5">
    <li>
      <div class="user-view pt-3 text-center">
        <router-link to="/" class=" sidenav-close" style="font-size: 13px">
          <img style="max-height: 50px; padding-top: 10px" :src="getImgUrl('logo_white.png')" alt="logo">
        </router-link>
      </div>
    </li>
    <li>
      <router-link id="dashboard" to="/dashboard" class="menu-item menu-item-selected sidenav-close">
        <i class="material-icons" style="font-size:20px;">developer_board</i><span>{{ $t('views.Dashboard') }}</span>
      </router-link>
    </li>

    <li>
      <router-link id="portfolio" to="/portfolio" class="menu-item sidenav-close">
        <i class="material-icons" style="font-size:20px;">assessment</i><span>{{ $t('views.Portfolio') }}</span>
      </router-link>
    </li>
    <li>
      <router-link id="wallet" to="/wallet" class="menu-item sidenav-close">
        <i class="material-icons" style="font-size:20px;">account_balance_wallet</i><span>{{ $t('views.Wallet virtual') }}</span>
      </router-link>
    </li>


    <li class="menu-item pl-5">{{ $t('views.INVERTIR') }}</li>

    <li>
      <router-link id="debt" to="/debt" class="menu-item sidenav-close">
        <i class="material-icons" style="font-size:20px;">dashboard</i><span>{{ $t('views.Proyectos') }}</span>
      </router-link>
    </li>

    <li>
      <router-link id="follow" to="/follow" class="menu-item sidenav-close">
        <i class="material-icons" style="font-size:20px;">favorite</i><span>{{ $t('views.Favoritos') }}</span>
      </router-link>
    </li>

    <li>
      <router-link id="whitelist" to="/whitelist" class="menu-item sidenav-close">
        <i class="material-icons" style="font-size:20px;">beenhere</i><span>{{ $t('views.Whitelist') }}</span>
      </router-link>
    </li>

    <li class="menu-item pl-5">INFO</li>

    <li>
      <router-link id="activity" to="/activity" class="menu-item sidenav-close">
        <i class="material-icons" style="font-size:20px;">dvr</i><span>{{ $t('views.Actividad') }}</span>
      </router-link>
    </li>

  </ul>

  <!-- Modal alert -->
  <div id="modal_alert" class="modal border-radius-10 border-radius-15"  style="margin-top: 60px;">
    <div class="modal-content text-center">
      <h5 class="text-grey" id="modal_alert_header"></h5>
      <div id="modal_alert_text"></div>
    </div>
    <div class="modal-footer mb-3">
      <button id="modal_alert_bt_ok" type="button" class="btn-primary modal-close">{{ $t('views.Aceptar') }}</button>&nbsp;&nbsp;&nbsp;
      <button id="modal_alert_bt_cancel" type="button" class="btn-secondary modal-close display-none">{{ $t('views.Cancelar') }}</button>&nbsp;&nbsp;&nbsp;
    </div>
  </div>

  <!-- Modal alert loading -->
  <div id="modal_loading" class="modal" >
    <div class="modal-content" style="text-align: center;">
      <p id="msg_modal_loading">{{ $t('views.Cargando datos') }}...</p>
      <div class="progress"><div class="indeterminate"></div></div>
    </div>
  </div>



  <!-- Modal contract transaction -->
  <div class="modal border-radius-10 border-radius-15" id="modal_progress_contract_2_steps" style="margin-top: 60px;">
    <div class="modal-content text-center">
      <h5 class="text-grey">{{ $t(blockchain_op_progress.title) }}</h5>
      <p>{{ $t('blockchainDialog.Para realizar la operación de compra de tokens a través de pago crypto es necesario seguir los siguientes pasos')}}:</p>

      <template v-if="blockchain_op_progress.step === 1 && !end">
        <h6 class="pt-2">{{ $t('blockchainDialog.step1') }}</h6>
        <p v-html="$t('blockchainDialog.step1_desc')"></p>
        <p v-html="blockchain_op_progress.tokensToTransfer"></p>
      </template>

      <template v-if="blockchain_op_progress.step === 2 && !end">
        <h6 class="pt-2">{{ $t('blockchainDialog.step2') }}</h6>
        <p v-html="$t('blockchainDialog.step2_desc')"></p>
        <p v-html="blockchain_op_progress.tokensToTransfer"></p>
      </template>

      <h6 class="pt-2" v-html="$t(blockchain_op_progress.message)"></h6>
      <div class="center-align" v-show="end===false">
        <div class="progress">
          <div class="indeterminate"></div>
        </div>
      </div>
    </div>
    <div class="col s12 text-center mb-5">
      <button v-if="end" type="button" class="btn-primary modal-close mr-2">{{ $t('generic.Aceptar') }}</button>&nbsp;&nbsp;&nbsp;
    </div>
  </div>



  <div id="modal_alert_kyc" class="modal border-radius-15">
    <div class="modal-content">
      <div class="row">
        <div class="col s12 padding-0">
          <div class="mySlides">
            <div class="col s12 m4 offset-m4">
              <img :src="getImgUrl('img_home_2.png')" class="responsive-img">
            </div>
            <div class="col s12 mt-1 text-center">
              <h4 class="mb-5">{{ $t('views.Estas a un paso de formar parte del Club') }} {{ $t('views.white_label_name') }}</h4>
              <p class="mb-0">{{ $t('views.Completa ahora el proceso de registro') }}</p>
              <p class="mt-0">{{ $t('views.Si ya has completado todos los datos_') }}</p>
              <p class="mt-0">{{ $t('views.Si lo prefieres, siempre podrás terminar el proceso en la sección de Mi Cuenta') }}</p>
              <button type="button" class="btn-primary mt-5" @click="goKYC">{{ $t('views.Proceso de identificación') }}</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>


</template>

<script lang="ts">

import {Options, Vue} from 'vue-class-component';
import M from "materialize-css";
import MenuUserRight from "@/components/dashboard/MenuUserRight.vue";
import store from "@/store";
import { stellarService } from "@/services/stellar/StellarService";

import { funcGetImgUrl } from "@/functions";

@Options({
  components: {
    MenuUserRight,
  },
  watch: {
    current_address(newAddress: string | null) {
      if (newAddress) {
        this.wallet_connected = true
        this.current_addressSub = newAddress.substring(0, 10) + '...'
        this.current_addressSubMobile = newAddress.substring(0, 20) + '...'
      } else {
        this.wallet_connected = false
        this.current_addressSub = ''
        this.current_addressSubMobile = ''
      }
    }
  },
})
export default class MenuUser extends Vue {

  wallet_connected = false
  current_addressSub = ''
  current_addressSubMobile = ''

  get current_address () {
    return store.getters.getCurrentWallet;
  }

  get blockchain_op_progress() {
    return store.getters.getBlockchainOpProgress;
  }
  get end () {
    return !store.getters.getBlockchainOpProgress.progress;
  }

  get kyc_valid () {
    return store.getters.getKYCValid;
  }

  async mounted () {
    M.AutoInit();
    selectMenu()

    await stellarService.initialize()
    const existingConnection = await stellarService.checkWalletConnection()
    if (existingConnection && existingConnection.address) {
      this.wallet_connected = true
      store.commit('ADDRESS_CHANGED', existingConnection.address)
      this.current_addressSub = existingConnection.address.substring(0, 10) + '...'
      this.current_addressSubMobile = existingConnection.address.substring(0, 20) + '...'
    }

    this.isConnect()
  }


  async isConnect () {
    this.wallet_connected = stellarService.isConnected()
    if (this.wallet_connected) {
      const stellarAddress = stellarService.getAccountAddress()
      if (stellarAddress) {
        store.commit('ADDRESS_CHANGED', stellarAddress)
        this.current_addressSub = stellarAddress.substring(0, 10) + '...'
        this.current_addressSubMobile = stellarAddress.substring(0, 20) + '...'
      }
    }
  }

  async connect () {
    console.debug("connect")
    let current_address = stellarService.getAccountAddress() || ""
    console.debug("current_address", current_address)
    if (current_address) {
      this.wallet_connected = true
      store.commit('ADDRESS_CHANGED', current_address)
    } else {
      const walletConnection = await stellarService.connectWallet()
      if (walletConnection && walletConnection.address) {
        current_address = walletConnection.address
        this.wallet_connected = true
      }
    }
    console.debug("this.current_address", this.current_address, this.wallet_connected)
    if (this.current_address) {
      this.current_addressSub = this.current_address.substring(0,10)+"..."
      this.current_addressSubMobile = this.current_address.substring(0,20)+"..."
    }
  }

  goKYC() {
    if (process.env.VUE_APP_WHITE_LABEL_IS_DEVELOPMENT === "true"){
      window.location.href = '/' + 'earastellar' + "app/userKYC";
    } else {
      window.location.href = '/userKYC'
    }

  }


  getImgUrl(pic) {
    return funcGetImgUrl(pic)
  }
}

function selectMenu(){
  const url = window.location.href
  //console.log(url)

  const listS = document.getElementsByClassName("menu-item-selected")
  for (const item of listS) {
    item.classList.remove("menu-item-selected");
  }
  if (url.includes("/dashboard")){
    document.getElementById("dashboard")?.classList.add("menu-item-selected")
  }  else if (url.includes("/portfolio")){
    document.getElementById("portfolio")?.classList.add("menu-item-selected")
  }  else if (url.includes("/wallet")){
    document.getElementById("wallet")?.classList.add("menu-item-selected")
  } else if (url.includes("/payment")){
    document.getElementById("projects")?.classList.add("menu-item-selected")
  } else if (url.includes("/last-projects")){
    document.getElementById("last-projects")?.classList.add("menu-item-selected")
  } else if (url.includes("/debt")){
    document.getElementById("debt")?.classList.add("menu-item-selected")
  } else if (url.includes("/follow")){
    document.getElementById("follow")?.classList.add("menu-item-selected")
  } else if (url.includes("/userDetail")){
    document.getElementById("userDetail")?.classList.add("menu-item-selected")
  } else if (url.includes("/activity")){
    document.getElementById("activity")?.classList.add("menu-item-selected")
  } else if (url.includes("/whitelist")){
    document.getElementById("whitelist")?.classList.add("menu-item-selected")
  } else {
    document.getElementById("dashboard")?.classList.add("menu-item-selected")
  }
}



</script>
