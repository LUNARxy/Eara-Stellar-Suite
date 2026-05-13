<template>




  <div class="row padding-2 pt-0" style="padding: 0; display: flex; flex-wrap: wrap; clear: both;">


    <div :class="'col s12 mt-3 pl-1 pr-1 '+classCol" v-for="item in list" :key="item.id">
      <CardInvest :data_item="item" :show_progress_bar="show_progress_bar"/>
    </div>

    <div v-if="numberColumns === '3' && list.length % 3 === 2" class="col s12 l4"></div>
    <div v-if="numberColumns === '3' && list.length % 3 === 1" class="col s12 l4"></div>
    <div v-if="numberColumns === '3' && list.length % 3 === 1" class="col s12 l4"></div>

    <div v-if="numberColumns === '4' && list.length % 4 === 3" class="col s12 l3"></div>
    <div v-if="numberColumns === '4' && list.length % 4 === 2" class="col s12 l3"></div>
    <div v-if="numberColumns === '4' && list.length % 4 === 2" class="col s12 l3"></div>
    <div v-if="numberColumns === '4' && list.length % 4 === 1" class="col s12 l3"></div>
    <div v-if="numberColumns === '4' && list.length % 4 === 1" class="col s12 l3"></div>
    <div v-if="numberColumns === '4' && list.length % 4 === 1" class="col s12 l3"></div>
  </div>




</template>

<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import CardInvest from "@/components/CardInvest.vue";


@Options({
  components:{
    CardInvest
  },
  props: {
    list: Array,
    numberColumns: {
      type: String,
      default: "4"
    },
    show_progress_bar: {
      type: Boolean,
      default: true
    },
  }
})

export default class LaunchPadInvest extends Vue {

  classCol
  numberColumns
  show_progress_bar

  beforeMount(){
    //optimizado para 3 y 4 columnas
    if (this.numberColumns == '3'){
      this.classCol = 'l4';
    } else {
      this.classCol = 'l3';
    }
  }
}
</script>
