<template>
  <MenuUser/>
  <div class="content_menu">



    <div class="col s12 text-center">
      <h4 class="col s12 mt-0 text-center">{{ $t('views.Portfolio') }}</h4>
    </div>


    
    <div class="row">
      <div class="col s12 padding-0" style=" display: flex; flex-wrap: wrap; clear: both;">
        <CardTotalValue type="balance"/>
        <CardTotalValue type="invests"/>
        <CardTotalValue type="profits"/>
      </div>

      <div class="row">
        <div class="col s12 padding-0" style=" display: flex; flex-wrap: wrap; clear: both;">
          <div class="col s12 l6">
            <CardStatisticsLine />
          </div>
          <div class="col s12 hide-on-large-only">&nbsp;</div>
          <div class="col s12 l6">
            <CardStatisticsDonut />
          </div>
        </div>
      </div>

      <div class="col s12 mt-2">
        <CardMyProjects />
      </div>
    </div>







    

    <div class="row hide-on-small-only">
        <div class="col s12">
          <div class="card row padding-3 pb-6 margin-0 text-center">
            <h5 class="mb-3">{{ $t('views.Descubre más proyectos para ti') }}</h5>
            <router-link to="/debt"><button type="button" class="btn-primary">{{ $t('views.Ver proyectos') }}</button></router-link>
          </div>
        </div>
    </div>


    <div class="row hide-on-med-and-up">
        <div class="card row padding-3 pb-6 margin-0 text-center">
          <h6 class="mb-3">{{ $t('views.Descubre más proyectos para ti') }}</h6>
          <router-link to="/debt"><button type="button" class="btn-primary">{{ $t('views.Ver proyectos') }}</button></router-link>
        </div>
    </div>

    <Footer />
  </div>

</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import M from "materialize-css";
import MenuUser from "@/components/dashboard/MenuUser.vue";
import {checkKYCValid, formatNumber} from "@/functions";
import Footer from "@/components/Footer.vue";
import LaunchPadInvestSplide from "@/components/LaunchPadInvestSplide.vue";
import CardMyProjects from "@/components/dashboard/CardMyProjects.vue";
import UserServices from "@/services/UserServices";
import CardStatisticsLine from "@/components/CardStatisticsLine.vue";
import CardStatisticsDonut from "@/components/CardStatisticsDonut.vue";
import CardTotalValue from "@/components/CardTotalValue.vue";


@Options({
  components: {
    CardTotalValue,
    CardStatisticsDonut,
    CardStatisticsLine,
    CardMyProjects,
    LaunchPadInvestSplide,
    Footer,
    MenuUser,
  },
})
export default class Portfolio2View extends Vue {
  //TODO demos https://apexcharts.com/vue-chart-demos/
  VUE_APP_WHITE_LABEL_CURRENCY = '$'
  total_profits_month = 0

  mounted () {
    M.AutoInit();
    checkKYCValid(this)
  }

  updated(){
    window.scrollTo(0, 0);
  }

  myFormatNumber(val){
    return formatNumber(val)
  }
}
</script>
