<template>

  <!-- para movil si estamos con login -->
  <div class="hide-on-med-and-up">
    <MenuUser v-if="isLoggedIn" />
  </div>


  <!-- Modal alert -->
  <div id="modal_alert" class="modal padding-1 border-radius-15"  style="margin-top: 60px;">
    <div class="modal-content text-center">
      <h5 class="text-grey" id="modal_alert_header"></h5>
      <div id="modal_alert_text"></div>
    </div>
    <div class="modal-footer mb-3">
      <button id="modal_alert_bt_ok" type="button" class="btn-primary modal-close">{{ $t('views.Aceptar') }}</button>&nbsp;&nbsp;&nbsp;
      <button id="modal_alert_bt_cancel" type="button" class="btn-secondary modal-close display-none">{{ $t('views.Cancelar') }}</button>&nbsp;&nbsp;&nbsp;
    </div>
  </div>

</template>
<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import M from "materialize-css";
import JQuery from 'jquery';
import store from "@/store";
import MenuUserRight from "@/components/dashboard/MenuUserRight.vue";
import MenuUser from "@/components/dashboard/MenuUser.vue";
import {funcGetImgUrl} from "@/functions";

@Options({
  components: {
    MenuUser,
    MenuUserRight,
  },
})
export default class Header extends Vue {
  isLoggedIn = store.getters.isLoggedIn

  mounted () {
    M.AutoInit();
    //para que la barra de navegacion haga sticky
    JQuery('#nav_desktop').parents().css("overflow", "visible")
  }

}
</script>
