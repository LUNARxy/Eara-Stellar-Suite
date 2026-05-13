<template>
  <Menu/>
  <div v-if="page_loaded" class="content_menu">
    <div class="row">

      <div class="col s12 padding-0 mb-3 text-center">
        <h4 class="col s12 text-center">{{ $t('views.Deuda') }}</h4>
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



    <form @submit.prevent="getData(-1)">
      <div class="row mt-3">
        <div class="col s12">
          <div class="card">
            <div class="card-content row">
              <div class="input-field col s12 m7">
                <label for="find_text" class="active">{{ $t('views.Buscar por nombre, descripción') }}</label>
                <input type="text" id="find_text" v-model="search_text" maxlength="100">
              </div>
              <div class="input-field col s12 m5">
                <i class="material-icons left hand" style="margin-top: 10px;" @click="clearFind">clear</i>
                <router-link to="/InvestProjectsFormNew/debt" class="right"><button type="button" class="btn-primary btn-green">{{ $t('views.Nuevo proyecto') }}</button></router-link>
                <button class="btn-primary right mr-3" type="submit" :disabled="loading">{{ $t('views.Buscar') }}</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </form>

    <div class="row mb-0">
      <div class="col s12">
        <div class="col s12 p-0 m-0">
          <div class="card col s12 padding-10px margin-0">
            <ul id="tabs" class="tabs">
              <li class="tab"><a class="pl-7 pr-7" href="#" id="tab_todos" @click="getData(-1)">{{ $t('views.Todos') }}</a></li>
              <li class="tab"><a class="pl-7 pr-7" href="#" id="tab_pendiente" @click="getData(INVEST_STATUS_PENDING)">{{ $t('views.Borrador') }}</a></li>
              <li class="tab"><a class="pl-7 pr-7" href="#" id="tab_prox_lanza" @click="getData(INVEST_STATUS_NEXT_LAUNCH)">{{ $t('views.Próximo lanzamiento') }}</a></li>
              <li class="tab"><a class="pl-7 pr-7" href="#" id="tab_financiacion" @click="getData(INVEST_STATUS_FINANCING_PHASE)">{{ $t('views.Financiación') }}</a></li>
              <li class="tab"><a class="pl-7 pr-7" href="#" id="tab_en_curso" @click="getData(INVEST_STATUS_IN_PROGRESS)">{{ $t('views.En curso') }}</a></li>
              <li class="tab"><a class="pl-7 pr-7" href="#" id="tab_Finalizado" @click="getData(INVEST_STATUS_FINISHED)">{{ $t('views.Finalizado') }}</a></li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div class="row pt-0" style="padding: 0; display: flex; flex-wrap: wrap; clear: both;">
      <div class="col s12 m6 l3 mt-3 pl-1 pr-1" v-for="item in list_projects" :key="item.id">
        <CardInvest :data_item="item"/>
      </div>

      <div v-if="list_projects.length % 4 === 3" class="col s12 l3"></div>
      <div v-if="list_projects.length % 4 === 2" class="col s12 l3"></div>
      <div v-if="list_projects.length % 4 === 2" class="col s12 l3"></div>
      <div v-if="list_projects.length % 4 === 1" class="col s12 l3"></div>
      <div v-if="list_projects.length % 4 === 1" class="col s12 l3"></div>
      <div v-if="list_projects.length % 4 === 1" class="col s12 l3"></div>
    </div>


  </div>
</template>



<script lang="ts">
import InvestServices from '@/services/InvestServices'
import {Options, Vue} from "vue-class-component";
import Menu from "@/components/Menu.vue";
import {
  formatDateFromServer,
  hideAlertLoading,
  showAlertLoading
} from "@/functions";
import {
  INVEST_STATUS_PENDING,
  INVEST_STATUS_NEXT_LAUNCH,
  INVEST_STATUS_FINANCING_PHASE,
  INVEST_STATUS_IN_PROGRESS,
  INVEST_STATUS_FINISHED,
} from "@/const"
import CardInvest from "@/components/CardInvest.vue";
import JQuery from "jquery";
import CardMyProjects from "@/components/CardMyProjects.vue";
import store from "@/store";
import CardStatisticsDonut from "@/components/CardStatisticsDonut.vue";
import CardStatisticsLine from "@/components/CardStatisticsLine.vue";
import CardTotalValue from "@/components/CardTotalValue.vue";


@Options({
  components: {
    CardTotalValue,
    CardStatisticsLine, CardStatisticsDonut,
    CardMyProjects,
    CardInvest,
    Menu,
  },
})
export default class InvestProjectsListView extends Vue {

  page_loaded = false

  INVEST_STATUS_PENDING = INVEST_STATUS_PENDING
  INVEST_STATUS_NEXT_LAUNCH = INVEST_STATUS_NEXT_LAUNCH
  INVEST_STATUS_FINANCING_PHASE = INVEST_STATUS_FINANCING_PHASE
  INVEST_STATUS_IN_PROGRESS = INVEST_STATUS_IN_PROGRESS
  INVEST_STATUS_FINISHED = INVEST_STATUS_FINISHED

  list_projects_all = []
  list_projects = []
  loading = false

  num_projects_all = 0
  num_projects_draft = 0
  num_projects_next_launch = 0
  num_projects_financial_phase = 0
  num_projects_in_course = 0
  num_projects_finished = 0

  search_text = ''

  mounted () {
    this.getData(-1)
  }

  getData(status){

    showAlertLoading()

    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    InvestServices.getInvestList(status, false, false, false, this.search_text)
        .then(response => {
          this.list_projects = response.data.list_projects;
          this.num_projects_all = response.data.num_projects_all;
          this.num_projects_draft = response.data.num_projects_draft;
          this.num_projects_next_launch = response.data.num_projects_next_launch;
          this.num_projects_financial_phase = response.data.num_projects_financial_phase;
          this.num_projects_in_course = response.data.num_projects_in_course;
          this.num_projects_finished = response.data.num_projects_finished;
          for (let item of this.list_projects){
            item.date_end_round = formatDateFromServer(item.date_end_round, false)
          }
          //ponemos todos los proyectos para no perderlos con los filtros
          this.list_projects_all = this.list_projects;

          self.page_loaded = true
          hideAlertLoading()
        })
  }

  clearFind(){
    this.search_text = ''
    JQuery('#tab_pendiente').removeClass('active')
    JQuery('#tab_prox_lanza').removeClass('active')
    JQuery('#tab_financiacion').removeClass('active')
    JQuery('#tab_en_curso').removeClass('active')
    JQuery('#tab_Finalizado').removeClass('active')
    JQuery('#tab_todos').addClass('active')
    this.getData(-1)
  }
}

</script>
