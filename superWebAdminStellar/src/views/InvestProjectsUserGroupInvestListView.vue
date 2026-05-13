<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="col s12 padding-0 mb-3 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Lista de inversiones agrupadas por usuario') }}</h4>
        </div>

        <div class="col s12 card padding-3">
          <div class="card-content">

            <div class="row table_wrapper">
              <table>
                <thead>
                <tr>
                  <th>{{ $t('views.Email') }}</th>
                  <th>{{ $t('views.Tokens') }}</th>
                  <th>{{ $t('views.Precio/Token') }}</th>
                  <th>{{ $t('views.Valor') }}</th>
                </tr>
                </thead>

                <tbody>
                <tr v-for="item in list_investors" :key="item.user_id">
                  <td><router-link :to="'/UserDetail/'+item.user_id">{{ item.email }}</router-link></td>
                  <td>{{ myFormatNumber(item.num_tokens) }}</td>
                  <td>{{ myFormatNumber(item.price_token, 10) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                  <td>{{ myFormatNumber(item.value, 10) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
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
import {
  formatNumber,
  showAlert,
  showAlertError,
} from "@/functions";
import UserServices from "@/services/UserServices";

@Options({
  components: {
    Menu,
  },
})
export default class InvestProjectsUserGroupInvestListView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  list_investors = []
  loading = false
  category_name = ""
  invest_id


  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this


    this.category_name = this.$route.params.category_name
    this.invest_id = this.$route.params.invest_id

    UserServices.getUsersInvestors(this.$route.params.invest_id)
        .then(response => {
          this.list_investors = response.data.list_users_tokens;

          //agrupamos las inversiones de los usuarios
          if (this.list_investors.length > 0) {
            this.list_investors = Object.values(
                this.list_investors.reduce((acc: any, item: any) => {
                  if (!acc[item.user_id]) {
                    acc[item.user_id] = {
                      user_id: item.user_id,
                      email: item.email,
                      phase: item.phase,
                      value: 0,
                      num_tokens: 0,
                      price_token: 0,
                    };
                  }
                  acc[item.user_id].num_tokens += item.num_tokens;
                  acc[item.user_id].price_token = item.price_token;
                  //el valor es el ultimo precio por el total de tokens
                  acc[item.user_id].value = acc[item.user_id].num_tokens * item.price_token;
                  return acc;
                }, {})
            );
          }

        })
        .catch(function (error) {
          showAlertError(error, self)
        });


  }

  myFormatNumber(val, decimals = 2){
    return formatNumber(val, decimals)
  }
}

</script>
