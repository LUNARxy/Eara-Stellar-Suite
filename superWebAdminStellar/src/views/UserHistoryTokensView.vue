<template>
  <Menu/>
  <div class="content_menu">

    <TableInvestHistory user_id="0"/>

  </div>
</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import Menu from "@/components/Menu.vue";
import TableInvestHistory from "@/components/TableInvestHistory.vue";


@Options({
  components: {
    TableInvestHistory,
    Menu,
  },
})
export default class UserHistoryTokensView extends Vue {

}

</script>

