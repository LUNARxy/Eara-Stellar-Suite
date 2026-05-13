<template>
  <Header v-if="!isLoggedIn"/>

  <MenuUser v-if="isLoggedIn"/>



  <div :class="content_menu">
    <div class="col s12 margin-3">
      <h4 class="text-center mb-3 mt-0">{{ $t('views.FAQ') }}</h4>
      <div class="card">
        <div class="card-content padding-5" v-html="$t('views.faq_des')">
        </div>
      </div>
    </div>

    <Footer />
  </div>

</template>



<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import Header from "@/components/Header.vue"
import Footer from "@/components/Footer.vue";
import M from "materialize-css";
import store from "@/store";
import MenuUser from "@/components/dashboard/MenuUser.vue";

@Options({
  components: {
    MenuUser,
    Header,
    Footer,
  },
})
export default class FaqView extends Vue {
  isLoggedIn = store.getters.isLoggedIn
  content_menu = ''
  mounted () {
    M.AutoInit();
    if (this.isLoggedIn){
      //se muestra el menu
      this.content_menu = 'content_menu'
    }
  }
}
</script>

