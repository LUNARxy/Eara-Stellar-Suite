<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="col s12 padding-0 mb-3 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Usuarios inversores del proyecto') }}</h4>
        </div>

        <div class="col s12 card padding-3">
          <div class="card-content">

            <div class="col s12 mb-3">
              <button class="btn-primary right mb-3" type="button" :disabled="loading" @click="exportUsers()">{{ $t('views.Exportar') }}</button>
              <div v-if="data_item.phase !== 'all'">
                <p>{{ $t('views.Número de participaciones en esta fase de venta') }}: {{myFormatNumber(data_item.actual_num_tokens)}}</p>
                <p>{{ $t('views.Número de participaciones en venta') }}: {{myFormatNumber(data_item.actual_remaining_tokens)}}</p>
                <p>{{ $t('views.Número mínimo de participaciones a comprar') }}: {{myFormatNumber(data_item.num_tokens_min_to_buy)}}</p>
                <p>{{ $t('views.Precio de la participación') }}: {{myFormatNumber(data_item.actual_price_token)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</p>
              </div>
            </div>


            <div class="row table_wrapper">
              <table>
                <thead>
                <tr>
                  <th>{{ $t('views.Email') }}</th>
                  <th>{{ $t('views.Fase') }}</th>
                  <th>{{ $t('views.Tokens') }}</th>
                  <th>{{ $t('views.Precio/Token') }}</th>
                  <th>{{ $t('views.Valor') }}</th>
                </tr>
                </thead>

                <tbody>
                <tr v-for="item in list_investors" :key="item.user_id">
                  <td><router-link :to="'/UserDetail/'+item.user_id">{{ item.email }}</router-link></td>
                  <td>{{ item.phase }}</td>
                  <td>{{ myFormatNumber(item.num_tokens) }}</td>
                  <td>{{ myFormatNumber(item.price_token, 10) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                  <td>{{ myFormatNumber(item.value, 10) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                </tr>
                </tbody>
                <tfoot>
                <tr>
                  <th></th>
                  <th></th>
                  <th></th>
                  <th></th>
                  <th>{{ $t('views.Total') }}: {{ myFormatNumber(total_value_investors, 10) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</th>
                </tr>
                </tfoot>
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
  showAlertError,
} from "@/functions";
import UserServices from "@/services/UserServices";

@Options({
  components: {
    Menu,
  },
})
export default class InvestProjectsUserInvestListView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  list_investors = []
  list_users_select = []
  loading = false
  user_id = ""
  num_tokens = 0
  invest_id
  link = ''
  total_value_investors = 0

  // eslint-disable-next-line
  data_item: any = {}


  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this


    this.invest_id = this.$route.params.invest_id
    this.link = this.$route.params.category_name + '/' + this.invest_id

    UserServices.getUsersForSelect()
        .then(response => {
          this.list_users_select = response.data;
        })

    UserServices.getUsersInvestors(this.$route.params.invest_id)
        .then(response => {
          this.data_item = response.data;
          this.list_investors = response.data.list_users_tokens;
          for (const item of this.list_investors) {
            this.total_value_investors += item.value
          }
        })
        .catch(function (error) {
          showAlertError(error, self)
        });


  }

  exportUsers(){
    this.loading = true
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    UserServices.getUsersExportExcel(-1, '', this.invest_id)
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
  myFormatNumber(val, decimals = 2){
    return formatNumber(val, decimals)
  }


}

</script>
