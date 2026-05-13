<template>
  <MenuUser/>
  <div class="content_menu">

    <div class="row" v-if="kyc_valid !== 1">
      <div class="col s12">
        <div class="col s12 mb-0">
          <div class="card mb-0">
            <div class="row card-content mb-0">
              <div class="col s12">
                <template v-if="kyc_valid === 2">
                  <p class="bold">{{ $t('views.Estado identificación') }}: <span class="bold red-text">{{ $t('views.PENDIENTE DE VALIDAR') }}</span></p>
                  <p class="mt-1 text-left">{{ $t('views.Muchas gracias por completar el proceso de identificación_') }}</p>
                </template>
                <template v-if="kyc_valid === 3">
                  <p class="bold">{{ $t('views.Estado identificación') }}: <span class="bold red-text">{{ $t('views.RECHAZADO') }}</span></p>
                  <p class="mt-1 text-left">{{ $t('views.Muchas gracias por completar el proceso de identificación_rechazado_') }}</p>
                  <p class="required mt-1 text-left" v-html="kyc_no_valid_reason"></p>
                  <p class="mt-1 text-left">{{ $t('views.Por favor, revise los errores mencionados en el proceso de identificación para que volvamos a revisar su caso') }}</p>
                  <div class="col s12 text-center mt-3 mb-3">
                    <router-link to="/userKYC"><button type="button" class="btn-primary mt-1">{{ $t('views.Proceso de identificación') }}</button></router-link>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>


    <div class="row">
      <div class="col s12" style=" display: flex; flex-wrap: wrap; clear: both;">
        <div class="col s12 l6">
          <div class="col s12 card">
            <div class="card-content row padding-7 pt-4 pb-3">
              <h5 class="bold text-grey mt-0">{{ $t('views.Bienvenido a') }}<br class="hide-on-med-and-up"/> {{ $t('views.white_label_name') }}</h5>
              <p class="mb-1">{{ $t('views.Descubre nuestro ecosistema de inversión tokenizada_') }}</p>
              <div class="col s12 pt-5 pb-5 text-center">
                <router-link to="/debt"><button type="button" class="btn-primary mr-3 mt-3">{{ $t('views.Invierte ahora') }}</button></router-link>
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col s12 margin-0 padding-0" style="height: 100%">

              <div class="col s12 padding-0" style=" display: flex; flex-wrap: wrap; clear: both;">
                <CardTotalValue type="balance"/>
                <CardTotalValue type="invests"/>
                <CardTotalValue type="profits"/>
              </div>

              <div class="col s12 padding-0 mt-3" style=" display: flex; flex-wrap: wrap; clear: both;">
                <div class="col s12">
                  <div class="card" style="height: 100%">
                    <div class="card-content row">
                      <div class="col s12">
                        <p class="bold text-grey mb-1">{{ $t('views.Wallet virtual') }}</p>
                        <span class="bold mt-0 mb-0 mr-3 text_value">{{myFormatNumber(wallet_balance)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col s12 l6">
          <div class="row">
            <div class="col s12">
              <CardStatisticsLine />
            </div>
            <div class="col s12 hide-on-large-only">&nbsp;</div>
            <div class="col s12">
              <CardStatisticsDonut />
            </div>
          </div>
        </div>
      </div>
    </div>


    <div class="mt-10 hide-on-med-and-up">&nbsp;</div>

    <div class="padding-5 pt-3" v-if="list_financing_phase.length > 0">
      <div class="row pb-0">
        <div class="col s12 text-center">
          <router-link to="/financing-phase-list"><h5 class="pb-1 mt-0">{{ $t('views.Proyectos en marcha') }}</h5></router-link>
          <p>{{ $t('views.Descubre todos los proyectos en fase de financiación') }}</p>
        </div>
      </div>
      <LaunchPadInvestSplide :menu="true" :list="list_financing_phase"/>
      <div class="col s12 text-center mt-3 mb-3">
        <router-link to="/financing-phase-list"><button type="button" class="btn-primary">{{ $t('views.Ver más') }}</button></router-link>&nbsp;
      </div>
    </div>


    <div class="padding-5" v-if="list_next_launch.length > 0">
      <div class="row pb-0">
        <div class="col s12 text-center">
          <router-link to="/next-launch-list"><h5 class="pb-1 mt-0">{{ $t('views.Próximos lanzamientos') }}</h5></router-link>
          <p>{{ $t('views.Descubre nuestros siguientes proyectos') }}</p>
        </div>
      </div>
      <LaunchPadInvestSplide :menu="true" :list="list_next_launch"/>
      <div class="col s12 text-center mt-3 mb-0">
        <router-link to="/next-launch-list"><button type="button" class="btn-primary">{{ $t('views.Ver más') }}</button></router-link>&nbsp;
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
import {checkKYCValid, formatNumber} from "@/functions";
import {
  INVEST_STATUS_FINANCING_PHASE,
  INVEST_STATUS_NEXT_LAUNCH
} from "@/const";
import Footer from "@/components/Footer.vue";
import LaunchPadInvestSplide from "@/components/LaunchPadInvestSplide.vue";
import UserServices from "@/services/UserServices";

import CardStatisticsDonut from "@/components/CardStatisticsDonut.vue";
import CardStatisticsLine from "@/components/CardStatisticsLine.vue";
import CardTotalValue from "@/components/CardTotalValue.vue";


@Options({
  components: {
    CardTotalValue,
    CardStatisticsLine,
    CardStatisticsDonut,
    LaunchPadInvestSplide,
    Footer,
    MenuUser,
  },
})
export default class DashboardView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  kyc_valid = 1
  kyc_no_valid_reason = ''

  wallet_balance = 0

  list_financing_phase = []
  list_next_launch = []


  mounted () {
    M.AutoInit();
    checkKYCValid(this)



  }
  updated(){
    window.scrollTo(0, 0);
  }


  getData(){
    InvestServices.getInvestList(INVEST_STATUS_FINANCING_PHASE)
        .then(response => {
          this.list_financing_phase = response.data;
        })
    InvestServices.getInvestList(INVEST_STATUS_NEXT_LAUNCH)
        .then(response => {
          this.list_next_launch = response.data;
        })
    UserServices.getUserWalletBalance()
        .then(response => {
          this.wallet_balance = response.data;
        })
  }

  myFormatNumber(val){
    return formatNumber(val)
  }
}
</script>
