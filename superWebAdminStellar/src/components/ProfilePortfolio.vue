<template>





  <div class="row">

    <div class="col s12 padding-0" style=" display: flex; flex-wrap: wrap; clear: both;">
      <CardTotalValue type="balance" :user_id="user_id"/>
      <CardTotalValue type="invests" :user_id="user_id"/>
      <CardTotalValue type="profits" :user_id="user_id"/>
    </div>

    <div class="col s12 padding-0" style=" display: flex; flex-wrap: wrap; clear: both;">
      <div class="col s12 l6">
        <CardStatisticsLine :user_id="user_id"/>
      </div>
      <div class="col s12 hide-on-large-only">&nbsp;</div>
      <div class="col s12 l6">
        <CardStatisticsDonut :user_id="user_id"/>
      </div>
      <div class="col s12 hide-on-large-only">&nbsp;</div>
    </div>

    <div class="col s12 mt-2 padding-0">
      <CardMyProjects :user_id="user_id"/>
    </div>
  </div>

  <TableInvestHistory :user_id="user_id"/>


</template>
<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import CardStatisticsDonut from "@/components/CardStatisticsDonut.vue";
import CardMyProjects from "@/components/CardMyProjects.vue";
import TableInvestHistory from "@/components/TableInvestHistory.vue";
import {PUBLIC_URL} from "@/services/Http-common";
import CardTotalValue from "@/components/CardTotalValue.vue";
import CardStatisticsLine from "@/components/CardStatisticsLine.vue";

@Options({
  components: {CardStatisticsLine, CardTotalValue, TableInvestHistory, CardMyProjects, CardStatisticsDonut},
  props: {
    user_id: Number
  }
})
export default class ProfilePortfolio extends Vue {

  user_id
  loading = false

  VUE_APP_WHITE_LABEL_CURRENCY = '$'
  PUBLIC_URL = PUBLIC_URL

}
</script>
