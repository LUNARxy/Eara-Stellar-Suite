<template>
  <MenuUser/>
  <div class="content_menu">

    <div class="row">
      <div class="col s12 text-center">
        <h4 class="pb-1 mt-0">{{ $t('views.Proyectos en Whitelist') }}</h4>
      </div>
      <div class="col s12">
        <LaunchPadInvest :list="list_invest" numberColumns="4"/>
      </div>
    </div>

    <div class="row hide-on-small-only">
      <div class="col s12">
        <div class="col s12">
          <div class="card row padding-3 pb-6 margin-0 text-center">
            <h5 class="mb-3">{{ $t('views.Descubre más proyectos para ti') }}</h5>
            <router-link to="/debt"><button type="button" class="btn-primary">{{ $t('views.Ver proyectos') }}</button></router-link>
          </div>
        </div>
      </div>
    </div>


    <div class="row hide-on-med-and-up">
      <div class="col s12">
        <div class="card row padding-3 pb-6 margin-0 text-center">
          <h6 class="mb-3">{{ $t('views.Descubre más proyectos para ti') }}</h6>
          <router-link to="/debt"><button type="button" class="btn-primary">{{ $t('views.Ver proyectos') }}</button></router-link>
        </div>
      </div>
    </div>

    <Footer />
  </div>
</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import M from "materialize-css";
import MenuUser from "@/components/dashboard/MenuUser.vue";
import InvestServices from "@/services/InvestServices";
import {checkKYCValid, sortTable} from "@/functions";
import LaunchPadInvest from "@/components/LaunchPadInvest.vue";
import Footer from "@/components/Footer.vue";


@Options({
  components: {
    Footer,
    LaunchPadInvest,
    MenuUser,
  },
})
export default class WhitelistView extends Vue {

  list_invest = []

  sortTableAux
  mounted() {
    M.AutoInit();
    checkKYCValid(this)
  }

  getData(){
    this.sortTableAux = sortTable

    InvestServices.getInvestList(-1, false, true)
        .then(response => {
          this.list_invest = response.data;
        })
  }
}
</script>

