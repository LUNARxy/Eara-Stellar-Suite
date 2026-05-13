<template>



    <div class="row pt-0">
      <div class="col s12 padding-0">
        <Splide :options="{ rewind: true, pagination: false, perPage: perPage }">
          <SplideSlide class="padding-1"  v-for="item in list" :key="item.id">
            <CardInvest :data_item="item"/>
          </SplideSlide>
        </Splide>
      </div>
    </div>




</template>

<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import { Splide, SplideSlide } from '@splidejs/vue-splide';
import '@splidejs/splide/dist/css/splide.min.css';
import CardInvest from "@/components/CardInvest.vue";


@Options({
  components:{
    CardInvest,
    Splide,
    SplideSlide,
  },
  props: {
    list: Array
  }
})

export default class LaunchPadInvestSplide extends Vue {
  perPage = 4

  beforeMount(){
    if (window.innerWidth < 600){//Small to large phone
      this.perPage = 1
    } else if (window.innerWidth < 960){//Small to medium tablet
      this.perPage = 2
    } else if (window.innerWidth < 1264){//Large tablet to laptop
      this.perPage = 3
    } else if (window.innerWidth < 1904){//Desktop
      this.perPage = 4
    } else {
      this.perPage = 5
    }
  }
}
</script>
