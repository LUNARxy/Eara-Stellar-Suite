<template>
  <MenuUser />
  <div class="content_menu">


    <div class="row">


      <div class="col s12">
        <div class="card">
          <div class="row card-content">

            <div v-if="!loaded" class="progress mt-5 mb-5">
              <div class="indeterminate"></div>
            </div>

            <ProfileKYC v-if="loaded" :data_item="data_item" :show_button_process="true"/>
          </div>
        </div>
      </div>


      <div id="div_tabs" class="col s12" style="display: none">
        <div class="col s12 p-0 m-0">
          <div class="card col s12 padding-10px margin-0 mb-2">
            <ul id="tabs" class="tabs">
              <li class="tab"><a class="pl-7 pr-7" href="#tab_personal_data">{{ $t('views.Datos personales') }}</a></li>
              <li class="tab"><a class="pl-7 pr-7" href="#tab_wallet">{{ $t('views.Wallet') }}</a></li>
              <li class="tab"><a class="pl-7 pr-7" href="#tab_password">{{ $t('views.Contraseña') }}</a></li>
            </ul>
          </div>
        </div>
        <div id="tab_personal_data" style="display: block;">
          <ProfilePersonalData v-if="loaded && data_item.kyc_valid > 0" :data_item="data_item" :is_kyc="false"/>
          <ProfileDocuments v-if="loaded && data_item.kyc_valid > 1" :data_item="data_item" :is_kyc="false"/>
        </div>
        <div id="tab_wallet" style="display: none;">
          <ProfileWallet v-if="loaded && data_item.kyc_valid > 0" :data_item="data_item" :is_kyc="false"/>
        </div>
        <div id="tab_password" style="display: none;">
          <ProfilePassword v-if="loaded && data_item.kyc_valid > 0" :data_item="data_item"/>
        </div>
      </div>


      <div class="col s12" v-if="data_item.kyc_valid == 0">
        <ProfilePassword v-if="loaded" :data_item="data_item"/>
      </div>

    </div>

    <Footer />
  </div>
</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import M from "materialize-css";
import UserServices from "@/services/UserServices";
import {reInitTabs, showAlertError} from "@/functions";
import MenuUser from "@/components/dashboard/MenuUser.vue";
import Footer from "@/components/Footer.vue";
import ProfileKYC from "@/components/ProfileKYC.vue";
import ProfilePersonalData from "@/components/ProfilePersonalData.vue";
import ProfilePassword from "@/components/ProfilePassword.vue";
import JQuery from "jquery";

import ProfileWallet from "@/components/ProfileWallet.vue";
import ProfileDocuments from "@/components/ProfileDocuments.vue";
import store from "@/store";

@Options({
  components: {
    ProfileDocuments,
    ProfileWallet,
    ProfilePassword,
    ProfilePersonalData,
    ProfileKYC,
    Footer,
    MenuUser,
  },
})
export default class UserDetailView extends Vue {

  loaded = false
  // eslint-disable-next-line
  data_item: any = {}

  mounted() {
    M.AutoInit();
    // las tabs de material con vue no funcionan bien, hay que poner esto para reiniciarlas
    reInitTabs('tabs', 'tab_personal_data')

    this.getUserData()
  }

  getUserData() {

    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    UserServices.getUserData()
        .then(response => {
          this.data_item = response.data
          this.loaded = true
          if (this.data_item.kyc_valid == 1 || this.data_item.kyc_valid == 2) {
            JQuery('#div_tabs').show()
          }
        })
        .catch(function (error) {
          showAlertError(error, self)
        });
  }
}
</script>
