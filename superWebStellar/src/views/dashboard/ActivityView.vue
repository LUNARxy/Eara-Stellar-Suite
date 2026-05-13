<template>
  <MenuUser/>
  <div class="content_menu">

    <div class="row">

      <div class="col s12 text-center">
        <h4 class="pb-1 mt-0">{{ $t('views.Registro de actividad') }}</h4>
      </div>

      <div class="col s12">
        <div class="col s12">
          <div class="col s12 card padding-3">
            <TableActivity />
          </div>
        </div>
      </div>
    </div>

    <Footer />
  </div>
</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import MenuUser from "@/components/dashboard/MenuUser.vue";
import Footer from "@/components/Footer.vue";
import TableActivity from "@/components/TableActivity.vue";
import {checkKYCValid} from "@/functions";

@Options({
  components: {
    TableActivity,
    Footer,
    MenuUser,
  },
})
export default class ActivityView extends Vue {
  mounted(){
    checkKYCValid(this)
  }
}

</script>
