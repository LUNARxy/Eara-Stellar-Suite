<template>

  <Menu/>
  <div class="content_menu">
    <div class="row">

      <div class="col s12 padding-0 mb-3 text-center">
        <h4 class="col s12 text-center">{{ $t('views.Usuarios') }}</h4>
      </div>



      <div class="col s12">
        <div class="card-content">
          <form @submit.prevent="findByKYC(data_form.valid_kyc)">
            <div class="row">
              <div class="col s12">
                <div class="card">
                  <div class="card-content row">
                    <div class="input-field col s12 m7">
                      <label for="find_text" class="active">{{ $t('views.Buscar por email, nombre') }}</label>
                      <input type="text" id="find_text" v-model="data_form.find_text" maxlength="100">
                    </div>

                    <div class="input-field col s12 m1">
                      <i class="material-icons left hand" style="margin-top: 10px;" @click="clearFindByKYC">clear</i>
                    </div>
                    <div class="input-field col s12 m2">
                      <button class="btn-primary right mr-3" type="submit">Buscar</button>
                    </div>
                    <div class="input-field col s12 m2">
                      <router-link to="/UserFormNew"><button class="btn-primary right" type="button">{{ $t('views.Nuevo usuario') }}</button></router-link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>

      </div>



      <div class="col s12">
        <div class="card padding-3">
          <div class="card-content">
            <div class="col s12">
              <button class="btn-primary right mb-3" type="button" :disabled="loading" @click="exportUsers()">{{ $t('views.Exportar') }}</button>
            </div>
            <div class="row table_wrapper">
              <PaginationDynamic :serviceFunction=get_users_function :functionParams="list_params_paginated" :per-page="10">
                <template v-slot:default="{ items }">
                  <table>
                    <thead>
                    <tr>
                      <th>{{ $t('views.Fecha registro') }}</th>
                      <th>{{ $t('views.Email') }}</th>
                      <th>{{ $t('views.Estado identificación') }}</th>
                      <th>{{ $t('views.Activo') }}</th>
                    </tr>
                    </thead>

                    <tbody>
                    <tr v-for="item in items" :key="item.id">
                      <td>{{ formatDate(item.date_created) }}</td>
                      <td><router-link :to="'/UserDetail/'+item.id" class="primary-color underline">{{ item.email }}</router-link></td>
                      <td>
                        <span v-if="item.kyc_valid === 0" class="bold" style="color: #deb268">{{ $t('views.SIN INICIAR') }}</span>
                        <span v-if="item.kyc_valid === 1" class="bold green-text">{{ $t('views.VÁLIDO') }}</span>
                        <span v-if="item.kyc_valid === 2" class="bold purple-text">{{ $t('views.PENDIENTE DE VALIDAR') }}</span>
                        <span v-if="item.kyc_valid === 3" class="bold red-text">{{ $t('views.RECHAZADO') }}</span>
                      </td>
                      <td>
                        <template v-if="item.is_active">{{ $t('views.SI') }}</template>
                        <template v-if="!item.is_active">{{ $t('views.NO') }}</template>
                      </td>
                    </tr>
                    </tbody>
                  </table>
                </template>
              </PaginationDynamic>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>



<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import PaginationDynamic from "@/components/pagination/PaginationDynamic.vue";
import Menu from "@/components/Menu.vue";
import UserServices from '@/services/UserServices'
import {formatDateFromServer, showAlertError} from "@/functions";
import JQuery from "jquery";

import store from "@/store";


@Options({
  components: {
    Menu,
    PaginationDynamic
  },
})

export default class UsersListView extends Vue {

  loading = false
  num_users_kyc_pending_validation = 0
  num_users_kyc_valid = 0
  num_users_kyc_without_start = 0
  num_users_refused = 0

  get_users_function = UserServices.getUsersPaginated

  // eslint-disable-next-line
  data_form: any = {}

  list_params_paginated = {
    valid_kyc: -1,
    find: ''
  }

  mounted () {
    this.data_form.active = -1
    this.data_form.valid_kyc = -1
  }

  exportUsers(){
    this.loading = true
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    UserServices.getUsersExportExcel(this.data_form.valid_kyc, this.data_form.find_text)
        .then(response => {
          self.loading = false

          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', 'data_list.csv');
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        })
        .catch(function (error) {
          self.loading = false
          showAlertError(error, self);
        });

  }

  findByKYC(valid_kyc = -1){
    this.data_form.valid_kyc = valid_kyc
    this.list_params_paginated.valid_kyc = valid_kyc
    this.list_params_paginated.find = this.data_form.find_text
  }

  clearFindByKYC(){
    this.data_form.find_text = ''
    JQuery('#tab_sin_iniciar').removeClass('active')
    JQuery('#tab_valido').removeClass('active')
    JQuery('#tab_pendiente').removeClass('active')
    JQuery('#tab_rechazado').removeClass('active')
    JQuery('#tab_todos').addClass('active')
    this.findByKYC()
  }

  formatDate(date) {
    return formatDateFromServer(date)
  }
}

</script>
