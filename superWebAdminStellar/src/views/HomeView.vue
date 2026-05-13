<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12 text-center">
        <h4 class="col s12 text-center">Admin {{ $t('views.white_label_name') }}</h4>
      </div>

      <template>
        <div class="col s12 padding-0" style=" display: flex; flex-wrap: wrap; clear: both;">
          <CardTotalValue type="balance"/>
          <CardTotalValue type="invests"/>
          <CardTotalValue type="profits"/>
        </div>

        <div class="col s12 padding-0" style=" display: flex; flex-wrap: wrap; clear: both;">
          <div class="col s12 l6">
            <CardStatisticsLine/>
          </div>
          <div class="col s12 hide-on-large-only">&nbsp;</div>
          <div class="col s12 l6">
            <CardStatisticsDonut/>
          </div>
        </div>
        <div class="col s12 hide-on-large-only">&nbsp;</div>
      </template>




      <template>
        <div class="col s12 mt-3 mb-2 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Usuarios') }}</h4>
        </div>

        <div class="col s12 padding-0" style=" display: flex; flex-wrap: wrap; clear: both;">
          <div class="col s6">
            <div class="card" style="height: 100%">
              <div class="card-content row pb-0">
                <div class="col s12">
                  <p class="bold text-grey mb-1">{{ $t('views.TODOS') }}</p>
                  <span class="bold mt-0 mb-0 mr-3 text_value">{{num_users_kyc_valid+num_users_kyc_pending_validation+num_users_kyc_without_start+num_users_refused}}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="col s6">
            <div class="card" style="height: 100%">
              <div class="card-content row pb-0">
                <div class="col s12">
                  <p class="bold text-grey mb-1">{{ $t('views.VALIDADO') }}</p>
                  <span class="bold mt-0 mb-0 mr-3 text_value">{{num_users_kyc_valid}}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col s12 padding-0 mt-3" style=" display: flex; flex-wrap: wrap; clear: both;">
          <div class="col s12 l4">
            <div class="card pb-0" style="height: 100%">
              <div class="card-content row">
                <div class="col s12">
                  <p class="bold text-grey mb-1">{{ $t('views.INDENTIFICACIÓN PENDIENTE') }}</p>
                  <span class="bold mt-0 mb-0 mr-3 text_value">{{num_users_kyc_without_start}}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="col s12 hide-on-large-only">&nbsp;</div>
          <div class="col s12 l4">
            <div class="card pb-0" style="height: 100%">
              <div class="card-content row">
                <div class="col s12">
                  <p class="bold text-grey mb-1">{{ $t('views.PENDIENTE DE VALIDAR') }}</p>
                  <span class="bold mt-0 mb-0 mr-3 text_value">{{num_users_kyc_pending_validation}}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="col s12 hide-on-large-only">&nbsp;</div>
          <div class="col s12 l4">
            <div class="card" style="height: 100%">
              <div class="card-content row pb-0">
                <div class="col s12">
                  <p class="bold text-grey mb-1">{{ $t('views.RECHAZADO') }}</p>
                  <span class="bold mt-0 mb-0 mr-3 text_value">{{num_users_refused}}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col s12 mb-2 mt-3 text-center">
            <h4 class="col s12 text-center">{{ $t('views.Proyectos') }}</h4>
          </div>

          <div class="col s12 padding-0" style=" display: flex; flex-wrap: wrap; clear: both;">
            <div class="col s12 l4">
              <div class="card pb-0" style="height: 100%">
                <div class="card-content row">
                  <div class="col s12">
                    <p class="bold text-grey mb-1">{{ $t('views.Todos') }}</p>
                    <span class="bold mt-0 mb-0 mr-3 text_value">{{num_projects_all}}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="col s12 hide-on-large-only">&nbsp;</div>
            <div class="col s12 l4">
              <div class="card pb-0" style="height: 100%">
                <div class="card-content row">
                  <div class="col s12">
                    <p class="bold text-grey mb-1">{{ $t('views.Borrador') }}</p>
                    <span class="bold mt-0 mb-0 mr-3 text_value">{{num_projects_draft}}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="col s12 hide-on-large-only">&nbsp;</div>
            <div class="col s12 l4">
              <div class="card" style="height: 100%">
                <div class="card-content row pb-0">
                  <div class="col s12">
                    <p class="bold text-grey mb-1">{{ $t('views.Próximo lanzamiento') }}</p>
                    <span class="bold mt-0 mb-0 mr-3 text_value">{{num_projects_next_launch}}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>


          <div class="col s12 padding-0 mt-3" style=" display: flex; flex-wrap: wrap; clear: both;">
            <div class="col s12 l4">
              <div class="card pb-0" style="height: 100%">
                <div class="card-content row">
                  <div class="col s12">
                    <p class="bold text-grey mb-1">{{ $t('views.Financiación') }}</p>
                    <span class="bold mt-0 mb-0 mr-3 text_value">{{num_projects_financial_phase}}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="col s12 hide-on-large-only">&nbsp;</div>
            <div class="col s12 l4">
              <div class="card pb-0" style="height: 100%">
                <div class="card-content row">
                  <div class="col s12">
                    <p class="bold text-grey mb-1">{{ $t('views.En curso') }}</p>
                    <span class="bold mt-0 mb-0 mr-3 text_value">{{num_projects_in_course}}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="col s12 hide-on-large-only">&nbsp;</div>
            <div class="col s12 l4">
              <div class="card" style="height: 100%">
                <div class="card-content row pb-0">
                  <div class="col s12">
                    <p class="bold text-grey mb-1">{{ $t('views.Finalizado') }}</p>
                    <span class="bold mt-0 mb-0 mr-3 text_value">{{num_projects_finished}}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <div class="row" v-if="data_last_invest.length > 0">
        <div class="col s12 text-center mt-1 mb-2">
          <h4 class="col s12 text-center">{{ $t('views.Últimos proyectos en financiación') }}</h4>
        </div>
        <div class="col s12 m6">
          <div class="card mt-0">
            <div class="card-content padding-7">
              <h6 class="text-grey mb-7">{{ $t('views.Proyectos en fase de financiación') }}</h6>
              <div v-for="item in data_last_invest" :key="item.id">
                <router-link :to="item.link">
                  <div class="row mt-3">
                    <div class="col s7 display-flex">
                      <div class="mr-5" style="min-width: 60px; height: 60px;">
                        <img :src="item.file" class="responsive-img" style="max-height: 100%;border-radius: 5px;">
                      </div>
                      <p>
                        <span class="bold">{{ item.name }}</span>
                        <!--<br>{{ item.token_abbreviation }}-->
                      </p>
                    </div>
                    <div class="col s5">
                      <p class="text-right pt-3">{{ myFormatNumber(item.total_balance) }}{{VUE_APP_WHITE_LABEL_CURRENCY}} - {{ myFormatNumber(item.percentage) }}% ({{ myFormatNumber(item.value_round) }}{{VUE_APP_WHITE_LABEL_CURRENCY}})</p>
                      <div class="col s12 padding-0 mb-0 meter">
                        <span :style="'width: '+item.percentage+'%'"></span>
                      </div>
                    </div>
                  </div>
                </router-link>
              </div>

            </div>
          </div>
        </div>
        <div class="col s12 m6">
          <div class="card mt-0">
            <div class="card-content padding-7">
              <h6 class="text-grey mb-7">{{ $t('views.Porcentaje de recaudación') }}</h6>
              <apexchart type="area"  :options="chart_last_invest_options" :series="chart_last_invest"></apexchart>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script lang="ts">

import { Options, Vue } from 'vue-class-component';
import M from "materialize-css";
import {formatNumber, getMonthName} from "@/functions";

import Menu from "@/components/Menu.vue";
import CardTotalValue from "@/components/CardTotalValue.vue";
import CardStatisticsLine from "@/components/CardStatisticsLine.vue";
import CardStatisticsDonut from "@/components/CardStatisticsDonut.vue";
import InvestServices from "@/services/InvestServices";
import {PUBLIC_URL} from "@/services/Http-common";
import UserServices from "@/services/UserServices";

@Options({
  components: {
    CardStatisticsDonut,
    CardStatisticsLine,
    CardTotalValue: CardTotalValue,
    Menu,
  },
})
export default class HomeView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'
  PUBLIC_URL = PUBLIC_URL

  month = new Date().getMonth();
  data_last_invest = []
  chart_last_invest = []
  chart_last_invest_options = {
    chart: {
      type: 'line',
      toolbar: false
    },
    stroke: {
      curve: 'stepline',
    },
    dataLabels: {
      enabled: true,
    },
    xaxis: {
      categories: [getMonthName(this.month-5),getMonthName(this.month-4),getMonthName(this.month-3),
        getMonthName(this.month-2),getMonthName(this.month-1), getMonthName(this.month)],
    },
    legend: {
      position: 'top',
    }
  }


  num_users_kyc_pending_validation = 0
  num_users_kyc_valid = 0
  num_users_kyc_without_start = 0
  num_users_refused = 0

  num_projects_all = 0
  num_projects_draft = 0
  num_projects_next_launch = 0
  num_projects_financial_phase = 0
  num_projects_in_course = 0
  num_projects_finished = 0

  mounted () {
    M.AutoInit();

    InvestServices.getInvestLastCollectedChart()
        .then(response => {
          let data = response.data
          let aux = []
          for (const item of data) {
            let valueBack = 0
            let list_balance_aux = []
            for (let i = 0; i < item.list_balance.length; i++) {
              valueBack += item.list_balance[i]
              list_balance_aux.push(valueBack)
            }
            aux.push({
              name: item.name,
              data: list_balance_aux
            })
            item.total_balance = parseFloat(list_balance_aux?.slice(-1)+"")

            let percentage = (item.total_balance * 100) / item.value_round

            this.data_last_invest.push({
              id: item.id,
              slug: item.slug,
              name: item.name,
              link: '/InvestProjects/debt/' + item.id,
              token_abbreviation: item.token_abbreviation,
              value_round: item.value_round,
              file: this.PUBLIC_URL + item.file,
              percentage: percentage,
              total_balance: item.total_balance
            })
          }
          this.chart_last_invest = aux
        })

    UserServices.getUsersNums()
        .then(response => {
          this.num_users_kyc_pending_validation = response.data.num_users_kyc_pending_validation
          this.num_users_kyc_valid = response.data.num_users_kyc_valid
          this.num_users_kyc_without_start = response.data.num_users_kyc_without_start
          this.num_users_refused = response.data.num_users_refused
        })
    InvestServices.getInvestTotals()
        .then(response => {
          this.num_projects_all = response.data.num_projects_all;
          this.num_projects_draft = response.data.num_projects_draft;
          this.num_projects_next_launch = response.data.num_projects_next_launch;
          this.num_projects_financial_phase = response.data.num_projects_financial_phase;
          this.num_projects_in_course = response.data.num_projects_in_course;
          this.num_projects_finished = response.data.num_projects_finished;
        })
  }



  myFormatNumber(val){
    return formatNumber(val)
  }
}
</script>
