<template>

  <MenuUser/>

  <div v-if="data_loaded" class="content_menu">

    <div class="row">
      <div class="col s12">
        <div class="col s12 m10 offset-m1 l8 offset-l2">
          <CardDrop v-if="this.last_drop != null" :data_item="last_drop"/>
        </div>
      </div>
      <div class="col s12" v-if="this.last_drop != null">
        <LaunchPadInvest :list="list_financing_phase" numberColumns="4" />
        <div class="col s12 text-center">
          <router-link to="/debt"><button class="btn-primary" >{{ $t('views.Ver todos') }}</button></router-link>
        </div>
      </div>
    </div>


    <div class="row margin-0 mt-5">
      <div class="col s12">
        <div class="col s12 mb-3 text-center">
          <h4 class="mt-0"><router-link to="/invest-next-launch-list">{{ $t('views.Próximos lanzamientos') }}</router-link></h4>
        </div>
        <div class="col s12 m6">
          <CardNextDropsTimeLine :list_items="list_next_drops"/>
        </div>
        <div class="col s12 m6">
          <div v-for="(item, itemObjKey) in list_next_drops" :key="item.id">
            <CardDrop v-if="itemObjKey===0" :id="'div_drop_'+item.id" :data_item="item"/>
            <CardDrop v-if="itemObjKey!==0" :id="'div_drop_'+item.id" :data_item="item" style="display:none;"/>
          </div>
        </div>
      </div>
    </div>


    <Footer/>
  </div>

</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import M from "materialize-css";
import CardDrop from "@/components/CardDrop.vue";
import InvestServices from "@/services/InvestServices";
import Footer from "@/components/Footer.vue";
import LaunchPadInvest from "@/components/LaunchPadInvest.vue";
import CardNextDropsTimeLine from "@/components/CardNextDropsTimeLine.vue";
import MenuUser from "@/components/dashboard/MenuUser.vue";
import {INVEST_STATUS_FINANCING_PHASE, INVEST_STATUS_NEXT_LAUNCH} from "@/const";
import {checkKYCValid, hideAlertLoading, showAlertLoading} from "@/functions";

@Options({
  components: {
    MenuUser,
    CardNextDropsTimeLine,
    LaunchPadInvest,
    Footer,
    CardDrop
  },
})
export default class LastProjectsView extends Vue {

  last_drop: any = {}
  list_financing_phase = []
  list_next_drops = []
  data_loaded = false

  mounted () {
    M.AutoInit();

    checkKYCValid(this)
  }

  getData(){

    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    showAlertLoading()

    InvestServices.getInvestList(INVEST_STATUS_FINANCING_PHASE,true)
        .then(response => {
          this.list_financing_phase = response.data;
          if (this.list_financing_phase.length > 0){
            this.last_drop = this.list_financing_phase.shift()
          }
          hideAlertLoading()
          self.data_loaded = true

          InvestServices.getInvestList(INVEST_STATUS_NEXT_LAUNCH, true)
              .then(response => {
                this.list_next_drops = response.data;

              })
        })
  }
}
</script>

<style>
</style>
