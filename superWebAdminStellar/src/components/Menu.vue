<template>

  <nav class="hide-on-large-only hide-on-extra-large-only">
    <div class="my_nav_menu_user cab-with-menu row" style="z-index: 1">

      <div class="col s2 m2 hide-on-large-only hide-on-extra-large-only" style="max-height: 70px;">
        <a href="#" data-target="slide-out" class="sidenav-trigger s2"><i class="material-icons">menu</i></a>
      </div>
      <div class="col s8 m8 text-center hide-on-large-only hide-on-extra-large-only">
        <router-link to="/home" class="mt-1" style="font-size: 13px">
          <img style="max-height: 50px; vertical-align: middle; padding:10px 20px 5px 20px;" :src="getImgUrl('logo_white.png')" alt="logo">
        </router-link>
      </div>
    </div>
  </nav>

  <ul id="slide-out" class="sidenav sidenav-fixed">
    <div class="text-center mt-3 mb-3">
      <router-link to="/home" class="mr-3 sidenav-close">
        <img style="max-height: 66px; max-width:90%; vertical-align: middle; padding:5px 20px;" :src="getImgUrl('logo_white.png')" alt="logo">
      </router-link>
    </div>
    <li>
      <router-link to="/home" id="menu_home" class="menu-item menu-item sidenav-close">
        <i class="material-icons">home</i><span>{{ $t('views.Inicio') }}</span>
      </router-link>
    </li>

    <li>
      <router-link to="/InvestProjectsList/debt" id="menu_debt" class="menu-item sidenav-close">
        <i class="material-icons">swap_vertical_circle</i><span>{{ $t('views.Proyectos') }}</span>
      </router-link>
    </li>

    <li>
      <router-link to="/UsersList" id="menu_user" class="menu-item sidenav-close">
        <i class="material-icons">people_outline</i><span>{{ $t('views.Usuarios') }}</span>
      </router-link>
    </li>
    <li>
      <router-link id="menu_stellar_governor" to="/governor" class="menu-item sidenav-close">
        <i class="material-icons" style="font-size:20px;">stars</i><span>Stellar Admin</span>
      </router-link>
    </li>


    <li>
      <router-link id="menu_user_activity" to="/userActivity" class="menu-item sidenav-close">
        <i class="material-icons">dvr</i><span>{{ $t('views.Actividad') }}</span>
      </router-link>
    </li>

    <li><div class="divider"></div></li>
    <li>
      <router-link to="/logout" class="menu-item">
        <i class="material-icons">exit_to_app</i><span>{{ $t('views.Salir') }}</span>
      </router-link>
    </li>
  </ul>


  <!-- Modal alert -->
  <div id="modal_alert" class="modal border-radius-10 border-radius-15"  style="margin-top: 60px;">
    <div class="modal-content text-center">
      <h5 class="text-grey" id="modal_alert_header"></h5>
      <div id="modal_alert_text"></div>
    </div>
    <div class="modal-footer mb-3">
      <button id="modal_alert_bt_ok" type="button" class="btn-primary modal-close">{{ $t('views.aceptar') }}</button>&nbsp;&nbsp;&nbsp;
      <button id="modal_alert_bt_cancel" type="button" class="btn-secondary modal-close display-none">{{ $t('views.cancelar') }}</button>&nbsp;&nbsp;&nbsp;
    </div>
  </div>

  <!-- Modal alert loading -->
  <div id="modal_loading" class="modal" >
    <div class="modal-content" style="text-align: center;">
      <p id="msg_modal_loading">{{ $t('views.Cargando datos') }}...</p>
      <div class="progress"><div class="indeterminate"></div></div>
    </div>
  </div>

</template>

<script lang="ts">
import { Vue } from 'vue-class-component';
import M from "materialize-css";

export default class MenuUser extends Vue {

  mounted () {
    M.AutoInit();

    selectMenu()
  }

  getImgUrl(pic) {
    if (process.env.VUE_APP_WHITE_LABEL_IS_DEVELOPMENT !== "true"){
      return '/earastellar/' + pic
    } else {
      return '/' + 'earastellaradmin/earastellar/' + pic
    }
  }
}

function selectMenu(){
  const url = window.location.href
  const listS = document.getElementsByClassName("menu-item-selected")
  for (const item of listS) {
    item.classList.remove("menu-item-selected");
  }
  if (url.includes("/debt")){
    document.getElementById("menu_debt")?.classList.add("menu-item-selected")
  } else if (url.includes("/UsersList") || url.includes("/UserDetail") || url.includes("/UserDocumentsList") || url.includes("/UserFormNew")){
    document.getElementById("menu_user")?.classList.add("menu-item-selected")
  } else if (url.includes("/userActivity")){
    document.getElementById("menu_user_activity")?.classList.add("menu-item-selected")
  } else if (url.includes("/InvestProjectsList") || url.includes("/InvestProjectsDetail") || url.includes("/InvestProjectsForm")
      || url.includes("/InvestStatusList") || url.includes("/InvestPhasesMintList") || url.includes("/InvestGalleryList")
      || url.includes("/InvestDocumentsList") || url.includes("/InvestNewsList") || url.includes("/InvestTeamList")
      || url.includes("/InvestQuestionsList") || url.includes("/InvestProjectsUserInvestList")
      || url.includes("/InvestProjectsUserWhitelistList") || url.includes("/InvestProfitsList")
      || url.includes("/InvestPromoterContributionsList") || url.includes("/InvestProjects")
      || url.includes("/InvestCompletedList")
  ){
    if (url.includes("/debt")){
      document.getElementById("menu_debt")?.classList.add("menu-item-selected")
    }
  } else if (url.includes("/governor")){
    document.getElementById("menu_governor")?.classList.add("menu-item-selected")
    document.getElementById("menu_stellar_governor")?.classList.add("menu-item-selected")
  } else {
    document.getElementById("menu_home")?.classList.add("menu-item-selected")
  }
}


</script>
