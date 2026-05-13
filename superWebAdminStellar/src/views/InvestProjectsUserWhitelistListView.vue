<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="col s12 padding-0 mb-3 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Usuarios en Whitelist en el proyecto') }}</h4>
        </div>

        <div class="col s12 card padding-3">
          <div class="card-content">
            <!--<p class="mb-3">{{ $t('views.Al cambiar de fase a un usuario, se le notificará por email') }}</p>-->

            <div class="row table_wrapper">
              <table>
                <thead>
                <tr>
                  <th>{{ $t('views.Fecha') }}</th>
                  <th>{{ $t('views.Email') }}</th>
                  <th>{{ $t('views.Cantidad') }}</th>
                </tr>
                </thead>

                <tbody>
                <tr v-for="item in list_users_white_list" :key="item.user_id">
                  <td>{{ item.date_created }}</td>
                  <td><router-link :to="'/UserDetail/'+item.user_id">{{ item.email }}</router-link></td>
                  <td>{{ item.value_to_invest }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>
      </div>
    </div>


  </div>
</template>



<script lang="ts">
import {Options, Vue} from "vue-class-component";
import Menu from "@/components/Menu.vue";
import {formatDateFromServer, formatNumber, showAlert, showAlertError} from "@/functions";
import UserServices from "@/services/UserServices";

@Options({
  components: {
    Menu,
  },
})
export default class InvestProjectsUserWhitelistListView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  list_users_white_list = []
  list_phases = []
  loading = false
  is_completed = false

  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    UserServices.getUsersWhiteList(this.$route.params.invest_id)
        .then(response => {
          this.is_completed = response.data.is_completed;
          this.list_users_white_list = response.data.list_users_white_list;
          this.list_phases = response.data.list_phases;
          for (let item of this.list_users_white_list){
            item.date_created = formatDateFromServer(item.date_created)
            item.value_to_invest = formatNumber(item.value_to_invest)
            item.preference_to_buy_txt = item.preference_to_buy
            if (item.preference_to_buy == null) item.preference_to_buy_txt = self.$t('views.Pública')
          }
        })
  }
}

</script>
