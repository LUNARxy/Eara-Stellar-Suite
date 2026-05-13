<template>


  <MenuUser/>
  <div class="content_menu">
    <div class="pl-5 pr-5">
      <div class="row pb-0">
        <div class="col s12 text-center">
          <h4 class="pb-1 mt-0">{{ $t('views.Próximos lanzamientos') }}</h4>
          <p>{{ $t('views.Descubre nuestros siguientes proyectos') }}</p>
        </div>
      </div>
      <LaunchPadInvest v-if="data_loaded" :list="list_items" numberColumns="4" class="mb-0"/>
    </div>

    <Footer />
  </div>

</template>


<script lang="ts">
import { Options, Vue } from 'vue-class-component';

import Footer from "@/components/Footer.vue";
import InvestServices from "@/services/InvestServices";
import M from "materialize-css";
import LaunchPadInvest from "@/components/LaunchPadInvest.vue";
import MenuUser from "@/components/dashboard/MenuUser.vue";
import {INVEST_STATUS_NEXT_LAUNCH} from "@/const";
import {checkKYCValid} from "@/functions";


@Options({
  components: {
    MenuUser,
    LaunchPadInvest,
    Footer,
  },
})
export default class InvestNextLaunchListView extends Vue {

  list_items = []
  data_loaded = false

  mounted () {
    M.AutoInit();
    checkKYCValid(this)
  }

  getData(){
    InvestServices.getInvestList(INVEST_STATUS_NEXT_LAUNCH)
        .then(response => {
          this.list_items = response.data;
          this.data_loaded = true
        })

  }

}
</script>
