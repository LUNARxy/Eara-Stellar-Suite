<template>
  <MenuUser/>
  <div class="content_menu">


    <div class="pl-5 pr-5 pb-0">

      <div v-if="list_financing_phase.length === 0 && list_next_launch.length === 0 && list_in_progress.length === 0 && list_completed.length === 0">
        <div class="row pb-0">
          <div class="col s12 text-center">
            <h4 class="pb-1 mt-0">{{ $t('views.Proyectos') }}</h4>
          </div>
        </div>
      </div>

      <div v-if="list_financing_phase.length > 0">
        <div class="row pb-0">
          <div class="col s12 text-center">
            <h4 class="pb-1 mt-0">{{ $t('views.Proyectos en marcha') }}</h4>
            <p>{{ $t('views.Descubre todos los proyectos en fase de financiación') }}</p>
          </div>
        </div>
        <LaunchPadInvestSplide :list="list_financing_phase"/>
        <div class="col s12 text-center mt-5 mb-7">
          <router-link :to="'/debt-financing-phase-list'" class="mt-1"><button type="button" class="btn-primary">{{ $t('views.Ver más') }}</button></router-link>&nbsp;
        </div>
      </div>


      <div v-if="list_next_launch.length > 0">
        <div class="row pb-0">
          <div class="col s12 text-center">
            <h4 class="pb-1 mt-0">{{ $t('views.Próximos lanzamientos') }}</h4>
            <p>{{ $t('views.Descubre nuestros siguientes proyectos') }}</p>
          </div>
        </div>
        <LaunchPadInvestSplide :list="list_next_launch"/>
        <div class="col s12 text-center mt-5 mb-7">
          <router-link :to="'/debt-next-launch-list'" class="mt-1"><button type="button" class="btn-primary">{{ $t('views.Ver más') }}</button></router-link>&nbsp;
        </div>
      </div>


      <div v-if="list_in_progress.length > 0">
        <div class="row pb-0">
          <div class="col s12 text-center">
            <h4 class="pb-1 mt-0">{{ $t('views.Financiación completada') }}</h4>
            <p>{{ $t('views.Descubre los proyectos que ya se han financiado') }}</p>
          </div>
        </div>
        <LaunchPadInvestSplide :list="list_in_progress"/>
        <div class="col s12 text-center mt-5 mb-7">
          <router-link :to="'/debt-in-progress-list'" class="mt-1"><button type="button" class="btn-primary">{{ $t('views.Ver más') }}</button></router-link>&nbsp;
        </div>
      </div>


      <div v-if="list_completed.length > 0">
        <div class="row pb-0">
          <div class="col s12 text-center">
            <h4 class="pb-1 mt-0">{{ $t('views.Inversiones completadas') }}</h4>
            <p>{{ $t('views.Descubre los proyectos que ya han terminado') }}</p>
          </div>
        </div>
        <LaunchPadInvestSplide :list="list_completed"/>
        <div class="col s12 text-center mt-5 mb-7">
          <router-link :to="'/debt-completed-list'" class="mt-1"><button type="button" class="btn-primary">{{ $t('views.Ver más') }}</button></router-link>&nbsp;
        </div>
      </div>


    </div>


    <Footer/>
  </div>

</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import M from "materialize-css";
import InvestServices from "@/services/InvestServices";
import Footer from "@/components/Footer.vue";
import MenuUser from "@/components/dashboard/MenuUser.vue";
import LaunchPadInvestSplide from "@/components/LaunchPadInvestSplide.vue";
import {
  INVEST_STATUS_FINANCING_PHASE,
  INVEST_STATUS_FINISHED,
  INVEST_STATUS_IN_PROGRESS,
  INVEST_STATUS_NEXT_LAUNCH
} from "@/const";
import {checkKYCValid, formatNumber, funcGetImgUrl} from "@/functions";
import CardStatisticsDonut from "@/components/CardStatisticsDonut.vue";
import CardMyProjects from "@/components/dashboard/CardMyProjects.vue";

@Options({
  components: {
    CardMyProjects,
    LaunchPadInvestSplide,
    MenuUser,
    Footer,
    CardStatisticsDonut
  },
})
export default class ProjectsView extends Vue {
  list_financing_phase = []
  list_next_launch = []
  list_in_progress = []
  list_completed = []
  url = window.location.href

  mounted () {
    M.AutoInit();
    checkKYCValid(this)
  }

  getData(){
    InvestServices.getInvestListLimit(INVEST_STATUS_FINANCING_PHASE)
        .then(response => {
          this.list_financing_phase = response.data;
          InvestServices.getInvestListLimit(INVEST_STATUS_NEXT_LAUNCH)
              .then(response => {
                this.list_next_launch = response.data;
                InvestServices.getInvestListLimit(INVEST_STATUS_IN_PROGRESS)
                    .then(response => {
                      this.list_in_progress = response.data;
                      InvestServices.getInvestListLimit(INVEST_STATUS_FINISHED)
                          .then(response => {
                            this.list_completed = response.data;
                          })
                    })
              })
        })
  }
}
</script>
