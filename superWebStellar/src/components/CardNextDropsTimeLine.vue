<template>


      <div class="card">
        <div class="card-content padding-7">
            <div class="row hand display-flex padding-3 rounded" v-for="item in list_items" :key="item.id" :id="'drop_time_'+item.id" @click="showNextDrop(item.id)">
              <div class="col s8 display-flex">
                <div class="mr-5" style="min-width: 60px; height: 60px;">
                  <img :src="PUBLIC_URL+item.file" class="responsive-img" style="max-height: 100%;border-radius: 10px;">
                </div>
                <p><span class="bold">{{ item.name }}</span><br>{{ item.title?.substring(0,50)+"..."}}</p>
              </div>
              <div class="col s3">
                <p class="col s12 padding-0 mt-0 text-right" style="font-size: 0.8rem;">{{formatDate(item.date_start_round)}}</p>
                <p class="col s12 padding-0 mt-0 text-right" style="font-size: 0.8rem;">{{ $t('views.Próximo lanzamiento') }}</p>
              </div>
              <div class="col s1">
                <p class="bold mt-20"><i class="material-icons" style="cursor: pointer">arrow_forward</i></p>
              </div>
            </div>
        </div>
      </div>


</template>

<script lang="ts">

import {Options, Vue} from "vue-class-component";
import {PUBLIC_URL} from "@/services/Http-common"
import {formatDateFromServer} from "@/functions";

@Options({
  props: {
    list_items: Array
  }
})

export default class CardNextDropsTimeLine extends Vue {
  PUBLIC_URL = PUBLIC_URL

  list_items

  updated(){
    if (this.list_items?.length > 0) {
      const drop_time_ = document.getElementById('drop_time_' + this.list_items[0].id);
      drop_time_.classList.add("grey-white");
    }
  }
  showNextDrop(id){
    //con animacion
    //https://es.stackoverflow.com/questions/280242/como-hacer-en-javascript-puro-el-equivalente-a-fadein-y-fadeout-de-jquery
    for (const item of this.list_items) {
      const drop = document.getElementById('div_drop_'+item.id);
      if (drop != null) drop.style.display = 'none';

      const drop_time_ = document.getElementById('drop_time_'+item.id);
      drop_time_.classList.remove("grey-white");
    }
    const drop = document.getElementById('div_drop_'+id);
    if (drop != null) drop.style.display = '';

    const drop_time_ = document.getElementById('drop_time_'+id);
    drop_time_.classList.add("grey-white");
  }

  formatDate(date) {
    return formatDateFromServer(date)
  }
}
</script>
