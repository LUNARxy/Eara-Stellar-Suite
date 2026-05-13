<template>
  <Menu/>
  <div class="content_menu">


    <div class="row">


      <div class="col s12">
        <div class="card">
          <div class="row card-content">

            <div v-if="!loaded" class="progress mt-5 mb-5">
              <div class="indeterminate"></div>
            </div>

            <ProfileKYC v-if="loaded" :data_item="data_item"/>
          </div>
        </div>
      </div>


      <div id="div_tabs" class="col s12">
        <div class="col s12 p-0 m-0">
          <div class="card col s12 padding-10px margin-0 mb-2">
            <ul id="tabs" class="tabs">
              <li class="tab"><a class="pl-7 pr-7" href="#tab_other_data">{{ $t('views.Portfolio') }}</a></li>
              <li class="tab"><a class="pl-7 pr-7" href="#tab_personal_data">{{ $t('views.Datos personales') }}</a></li>
              <li class="tab"><a class="pl-7 pr-7" href="#tab_wallet">{{ $t('views.Wallet') }}</a></li>
              <li class="tab"><a class="pl-7 pr-7" href="#tab_password">{{ $t('views.Contraseña') }}</a></li>
            </ul>
          </div>
        </div>
        <div id="tab_other_data" style="display: block;">
          <ProfilePortfolio v-if="loaded" :user_id="user_id"/>
        </div>
        <div id="tab_personal_data" style="display: none;">
          <ProfilePersonalData v-if="loaded" :data_item="data_item"/>
          <ProfileDocuments v-if="loaded && data_item.kyc_valid > 1" :data_item="data_item"/>
        </div>
        <div id="tab_wallet" style="display: none;">
          <ProfileWallet v-if="loaded" :data_item="data_item"/>
        </div>
        <div id="tab_password" style="display: none;">
          <ProfilePassword v-if="loaded" :data_item="data_item"/>
        </div>
      </div>


    </div>

  </div>
</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import M from "materialize-css";
import UserServices from "@/services/UserServices";
import {reInitTabs, showAlertError} from "@/functions";
import ProfileKYC from "@/components/ProfileKYC.vue";
import ProfilePersonalData from "@/components/ProfilePersonalData.vue";
import ProfilePassword from "@/components/ProfilePassword.vue";

import ProfileWallet from "@/components/ProfileWallet.vue";
import ProfileDocuments from "@/components/ProfileDocuments.vue";
import Menu from "@/components/Menu.vue";
import ProfilePortfolio from "@/components/ProfilePortfolio.vue";
import store from "@/store";

@Options({
  components: {
    ProfilePortfolio,
    Menu,
    ProfileDocuments,
    ProfileWallet,
    ProfilePassword,
    ProfilePersonalData,
    ProfileKYC,
  },
})
export default class UserDetailView extends Vue {

  loaded = false
  // eslint-disable-next-line
  data_item: any = {}

  user_id

  beforeMount() {
    this.user_id = this.$route.params.id
  }

  mounted() {
    M.AutoInit();
    // las tabs de material con vue no funcionan bien, hay que poner esto para reiniciarlas
    reInitTabs('tabs', 'tab_other_data')

    this.getUserData()
  }

  getUserData() {

    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    UserServices.getUser(this.user_id)
        .then(response => {
          this.data_item = response.data
          this.data_item.user_id = this.user_id

          this.loaded = true
        })
        .catch(function (error) {
          showAlertError(error, self)
        });
  }
}
</script>
