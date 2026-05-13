<template>

  <div class="col s12">
    <span v-if="data_item.name !== null">{{ $t('views.Nombre') }}: {{data_item.name}} {{data_item.surname}}</span>
    <p>{{ $t('views.Email') }}: {{data_item.email}}</p><br>

    <template v-if="data_item.kyc_valid == 0">
      <p class="bold">{{ $t('views.Estado identificación') }}: <span class="bold">{{ $t('views.SIN INICIAR') }}</span></p>
      <br><p class="text-left">{{ $t('views.Bienvenido a white_label Investing_') }}</p>
      <br><div class="col s12 text-center mb-3">
        <router-link to="/userKYC"><button type="button" class="btn-primary">{{ $t('views.Proceso de identificación') }}</button></router-link>
      </div>
    </template>

    <template v-if="data_item.kyc_valid == 1">
      <p class="bold">{{ $t('views.Estado identificación') }}: <span class="bold green-text">{{ $t('views.VÁLIDO') }}</span></p>
      <br><p class="text-left">{{ $t('views.Muchas gracias por completar el proceso de identificación bien_') }}</p>
    </template>

    <template v-if="data_item.kyc_valid == 2">
      <p class="bold">{{ $t('views.Estado identificación') }}: <span class="bold red-text">{{ $t('views.PENDIENTE DE VALIDAR') }}</span></p>
      <br><p class="text-left">{{ $t('views.Muchas gracias por completar el proceso de identificación_') }}</p>
    </template>


    <template v-if="data_item.kyc_valid == 3">
      <p class="bold">{{ $t('views.Estado identificación') }}: <span class="bold red-text">{{ $t('views.RECHAZADO') }}</span></p>
      <br><p class="text-left">{{ $t('views.Muchas gracias por completar el proceso de identificación_rechazado_') }}</p>
      <br><p class="required text-left" v-html="data_item.kyc_no_valid_reason"></p>
      <br><p class="text-left">{{ $t('views.Por favor, revise los errores mencionados en el proceso de identificación para que volvamos a revisar su caso') }}</p>
      <br><div v-if="show_button_process" class="col s12 text-center">
        <router-link to="/userKYC"><button type="button" class="btn-primary">{{ $t('views.Proceso de identificación') }}</button></router-link>
      </div>
    </template>
  </div>

</template>
<script lang="ts">
import {Options, Vue} from 'vue-class-component';

import store from "@/store";
import {Locales} from "@/locales/locales";

@Options({
  props: {
    data_item: Object,
    show_button_process: Boolean
  }
})
export default class ProfileKYC extends Vue {
  data_item
  show_button_process


  mounted(){
    if (store.getters.getLocale == Locales.EN) {
      this.data_item.kyc_no_valid_reason = this.data_item.kyc_no_valid_reason_EN
    }
  }
}
</script>
