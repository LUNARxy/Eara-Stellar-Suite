<template>
    <a class="dropdown-trigger pr-2" href="#" data-target='menu-right'>
      <img class="circle" style="width: 42px; height: 42px; vertical-align: middle" :src="url_img_profile">
    </a>
    <ul id='menu-right' class='card dropdown-content border-radius-15' style="padding: 10px!important;">
      <li>
        <router-link to="/userDetail">
          <i class="material-icons">person</i>{{ $t('views.Mi cuenta') }}
        </router-link>
      </li>
      <li class="divider" tabindex="-1"></li>
      <li>
        <router-link to="/legal#condiciones_uso">
          {{ $t('views.Términos de uso') }}
        </router-link>
      </li>
      <li>
        <router-link to="/cookiesPolicy">
          {{ $t('views.Aviso legal') }}
        </router-link>
      </li>
      <li>
        <router-link to="/privacyPolicy">
          {{ $t('views.Política de privacidad') }}
        </router-link>
      </li>
      <li>
        <router-link to="/cookiesPolicy">
          {{ $t('views.Política de cookies') }}
        </router-link>
      </li>


      <li class="divider" tabindex="-1"></li>
      <li>
        <router-link to="/logout">
          <i class="material-icons">exit_to_app</i>{{ $t('views.Cerrar sesión') }}
        </router-link>
      </li>
    </ul>
</template>

<script lang="ts">
import { Vue } from 'vue-class-component';
import M from "materialize-css";
import store from "@/store";
import {PUBLIC_URL} from "@/services/Http-common"
import {funcGetImgUrl} from "@/functions";


export default class MenuUserRight extends Vue {

  url_img_profile = this.getImgUrl('/logo192.jpg')

  mounted () {
    M.AutoInit();
    if (store.getters.getUrlImgProfile != undefined && store.getters.getUrlImgProfile != ""){
      this.url_img_profile = PUBLIC_URL+store.getters.getUrlImgProfile
    }
  }
    getImgUrl(pic) {
    return funcGetImgUrl(pic)
  }
}
</script>
