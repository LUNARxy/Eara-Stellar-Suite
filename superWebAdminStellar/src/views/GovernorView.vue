<template>
  <Menu/>
  <div class="content_menu">

      <div class="stellar-tab-bar">
        <button
          :class="stellarTab === 'lunarxy' ? 'stellar-tab-active' : 'stellar-tab'"
          @click="stellarTab = 'lunarxy'"
        >LunarXY Token</button>
        <button
          :class="stellarTab === 'compliantid' ? 'stellar-tab-active' : 'stellar-tab'"
          @click="stellarTab = 'compliantid'"
        >Compliant-ID Registry</button>
      </div>
      <LunarxyAdminGovernance v-if="stellarTab === 'lunarxy'"></LunarxyAdminGovernance>
      <CompliantIdAdminGovernance v-if="stellarTab === 'compliantid'"></CompliantIdAdminGovernance>

  </div>
</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import {PUBLIC_URL} from "@/services/Http-common";
import {formatNumber} from "@/functions";
import CompliantIdAdminGovernance from "@/components/CompliantIdAdminGovernance.vue";
import LunarxyAdminGovernance from "@/components/LunarxyAdminGovernance.vue";
import Menu from "@/components/Menu.vue";

@Options({
  components: {
    Menu,
    CompliantIdAdminGovernance,
    LunarxyAdminGovernance,
  },
})
export default class PruebasView extends Vue {
  PUBLIC_URL = PUBLIC_URL

  stellarTab: 'lunarxy' | 'compliantid' = 'lunarxy'


  mounted () {
    console.log('')
  }


  myFormatNumber(val){
    return formatNumber(val)
  }
}

</script>

<style>
.stellar-tab-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 0;
}
.stellar-tab, .stellar-tab-active {
  padding: 0.55rem 1.4rem;
  border: none;
  border-bottom: 3px solid transparent;
  background: transparent;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  color: #666;
  margin-bottom: -2px;
  transition: color 0.15s, border-color 0.15s;
}
.stellar-tab-active {
  color: #1565c0;
  border-bottom-color: #1565c0;
}
.stellar-tab:hover:not(.stellar-tab-active) {
  color: #1565c0;
}
</style>
