<template>


  <div class="card border-radius-15 mb-0" style="height: 100%; padding: 0!important;">
    <div class="card-image padding-3">
      <router-link :to="link">
        <img loading="lazy" style="max-width: 100%; max-height:100%;min-width: 100%;" :src="PUBLIC_URL+data_item.file">
      </router-link>
    </div>
    <div class="card-content row margin-0" style="padding: 10px 10px 0 10px!important;">
      <div class="col s12 padding-0 mb-0">
        <div style="display: flex;width: 100%; justify-content: space-between;">
          <p class="pl-0 pr-2 bold"><router-link :to="link">{{data_item.name}}</router-link></p>
          <div class="right">
            <i :id="'followsInvest_'+data_item.id" v-if="data_item.is_follow" @click="followsInvest(data_item.id)" class="material-icons hand color-base" style="font-size: 26px;">favorite</i>
            <i :id="'followsInvest_'+data_item.id" v-if="!data_item.is_follow" @click="followsInvest(data_item.id)" class="material-icons hand color-base" style="font-size: 26px;">favorite_border</i>
          </div>
        </div>

        <div class="col s12 padding-0 mb-0">
          <div class="row mb-4">
            <div class="col s6">
              <p class="col s12 padding-0 pt-5" style="color: black" :id="'value_round'+this.data_item.id">{{myFormatNumber(data_item.value_round)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</p>
              <p class="col s12 padding-0 pt-2" style="font-size: 0.8rem;">{{ $t('views.Objetivo') }}</p>
              <p class="col s12 padding-0 pt-2" style="font-size: 0.8rem;">{{ $t('views.Valor de la ronda') }}</p>
            </div>
            <div class="col s6">
              <p v-if="data_item.status === INVEST_STATUS_FINANCING_PHASE" :id="'date_end_round_'+this.data_item.id" class="col s12 padding-0 pt-2 text-right" style="color: black">{{data_item.days}} {{ $t('views.días') }}</p>
              <p v-if="data_item.status === INVEST_STATUS_FINANCING_PHASE" class="col s12 padding-0 pt-2 text-right" style="font-size: 0.8rem;">{{ $t('views.Tiempo restante financiación') }}</p>

              <p v-if="data_item.status === INVEST_STATUS_NEXT_LAUNCH" :id="'date_start_round_'+this.data_item.id" class="col s12 padding-0 pt-5 text-right" style="color: black">{{data_item.date_start_round}}</p>
              <p v-if="data_item.status === INVEST_STATUS_NEXT_LAUNCH" class="col s12 padding-0 pt-2 text-right" style="font-size: 0.8rem;">{{ $t('views.Próximo lanzamiento') }}</p>

              <p v-if="data_item.status === INVEST_STATUS_FINISHED" class="col s12 padding-0 pt-2 text-right" style="color: black">{{ $t('views.Finalizado') }}</p>
              <p v-if="data_item.status === INVEST_STATUS_FINISHED" class="col s12 padding-0 pt-2 text-right" style="font-size: 0.8rem;">{{ $t('views.Estado') }}</p>

              <p v-if="data_item.status === INVEST_STATUS_IN_PROGRESS" class="col s12 padding-0 pt-2 text-right" style="color: black">{{ $t('views.En curso') }}</p>
              <p v-if="data_item.status === INVEST_STATUS_IN_PROGRESS" class="col s12 padding-0 pt-2 text-right" style="font-size: 0.8rem;">{{ $t('views.Estado') }}</p>
            </div>
          </div>
          <div class="row mb-2">
            <div class="col s6">
              <p v-if="data_item.profit_estimated_description != null" class="col s12 padding-0 pb-2" style="color: black">{{data_item.profit_estimated_description}}</p>
              <p v-if="data_item.profit_estimated_description != null" class="col s12 padding-0 pb-2" style="font-size: 0.8rem;">{{ $t('views.Rentabilidad') }}<br>{{ $t('views.estimada') }}</p>
            </div>
            <div class="col s6">
              <p v-if="data_item.time_limit != null" class="col s12 padding-0 pt-6 text-right" style="color: black">{{data_item.time_limit}}</p>
              <p v-if="data_item.time_limit != null" class="col s12 padding-0 pt-2 text-right" style="font-size: 0.8rem;">{{ $t('views.Duración del proyecto') }}</p>
            </div>
          </div>
          <div v-if="show_progress_bar && data_item.status !== INVEST_STATUS_NEXT_LAUNCH">
            <div class="row mb-0">
              <div class="col s12">
                <hr style="border: 1px solid #e5e5e5;"/>
              </div>
            </div>
            <!-- div datos fase actual -->
            <div>
              <p v-if="data_item.phase != null" class="col s12 text-center" style="font-size: 0.8rem;">{{ $t('views.Fase de fondeo') }}: {{ data_item.phase }}</p>
              <div class="row">
                <div class="col s6">
                  <p class="col s12 padding-0 pt-6" style="color: black">{{myFormatNumber(data_item.sold_tokens_value)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</p>
                  <p class="col s12 padding-0 pt-2" style="font-size: 0.8rem;">{{ $t('views.Recaudado') }}</p>
                </div>
                <div class="col s6">
                  <p class="col s12 padding-0 pt-6 text-right" style="color: black">{{myFormatNumber(data_item.collected)}}%</p>
                  <p class="col s12 padding-0 pt-2 text-right" style="font-size: 0.8rem;">{{ $t('views.Fondeado') }}</p>
                </div>
              </div>
              <div class="col s12 padding-0 mb-4 meter mt-0">
                <span :style="'width: '+data_item.collected+'%;'"></span>
              </div>
              <div class="row mb-0">
                <div class="col s6">
                  <p class="col s12 padding-0 pt-6" style="color: black">{{myFormatNumber(data_item.investors)}}</p>
                  <p class="col s12 padding-0 pt-2" style="font-size: 0.8rem;">{{ $t('views.Inversores') }}</p>
                </div>
                <div class="col s6">
                  <p class="col s12 padding-0 pt-2 text-right" style="color: black">{{myFormatNumber(data_item.remaining_tokens)}}</p>
                  <p class="col s12 padding-0 pt-2 text-right" style="font-size: 0.8rem;">{{ $t('views.Tokens disponibles') }}</p>
                </div>
              </div>
            </div>

            <!-- div datos todas las fases -->
            <div v-if="data_item.list_mint_phases?.length > 1">
              <div class="row mb-0">
                <div class="col s12">
                  <hr style="border: 1px solid #e5e5e5;"/>
                </div>
              </div>
              <p class="col s12 text-center" style="font-size: 0.8rem;">Financiación total</p>
              <div class="row">
                <div class="col s6">
                  <p class="col s12 padding-0 pt-6" style="color: black">{{myFormatNumber(data_item.sold_tokens_value_first_to_last)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</p>
                  <p class="col s12 padding-0 pt-2" style="font-size: 0.8rem;">{{ $t('views.Recaudado') }}</p>
                </div>
                <div class="col s6">
                  <p class="col s12 padding-0 pt-6 text-right" style="color: black">{{myFormatNumber(data_item.collected_first_to_last)}}%</p>
                  <p class="col s12 padding-0 pt-2 text-right" style="font-size: 0.8rem;">{{ $t('views.Fondeado') }}</p>
                </div>
              </div>
              <div class="col s12 padding-0 mb-4 meter mt-0">
                <span :style="'width: '+data_item.collected_first_to_last+'%;'"></span>
              </div>
              <div class="row mb-0">
                <div class="col s6">
                  <p class="col s12 padding-0 pt-6" style="color: black">{{myFormatNumber(data_item.investors_first_to_last)}}</p>
                  <p class="col s12 padding-0 pt-2" style="font-size: 0.8rem;">{{ $t('views.Inversores') }}</p>
                </div>
                <div class="col s6">
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>

    </div>

    <img v-if="is_all_collected" src="@/assets/img/sold_out.png" class="img_sold_out" alt="sold out">
  </div>


</template>
<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import M from "materialize-css";
import store from "@/store";
import {followsInvest, formatDateFromServer, formatNumber} from "@/functions";
import {
  INVEST_STATUS_NEXT_LAUNCH,
  INVEST_STATUS_FINANCING_PHASE,
  INVEST_STATUS_IN_PROGRESS,
  INVEST_STATUS_FINISHED
} from "@/const"
import {PUBLIC_URL} from "@/services/Http-common"
import JQuery from "jquery";

@Options({
  props: {
    data_item: Object,
    show_progress_bar: {
      type: Boolean,
      default: true
    },
  }
})

export default class CardInvest extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  INVEST_STATUS_NEXT_LAUNCH = INVEST_STATUS_NEXT_LAUNCH
  INVEST_STATUS_FINANCING_PHASE = INVEST_STATUS_FINANCING_PHASE
  INVEST_STATUS_IN_PROGRESS = INVEST_STATUS_IN_PROGRESS
  INVEST_STATUS_FINISHED = INVEST_STATUS_FINISHED

  PUBLIC_URL = PUBLIC_URL

  data_item
  show_progress_bar
  isLoggedIn = store.getters.isLoggedIn
  link = ''
  is_all_collected = false

  mounted () {
    M.AutoInit();

    //se suman los tokens vendidos con los que están esperando a validarse como vendidos
    if (this.data_item.price_token > 0) {
      if (isNaN(this.data_item.waiting_tokens)) this.data_item.waiting_tokens = 0
      this.data_item.sold_tokens_value = (this.data_item.sold_tokens_phase + this.data_item.waiting_tokens) * this.data_item.price_token
    } else {
      //se mira si es los totales pero sin fase
      if (this.data_item.total_amount_invested_completed != null){
        this.data_item.sold_tokens_value = this.data_item.total_amount_invested_completed
        this.data_item.value_round = this.data_item.total_amount_invested_completed
        this.data_item.investors = this.data_item.num_investors_completed
      }
    }

    this.data_item.collected = (((this.data_item.sold_tokens_value))*100/this.data_item.value_round)
    if (isNaN(this.data_item.collected)) this.data_item.collected = 0
    if (this.data_item.collected >= 100){
      this.is_all_collected = true
      this.data_item.remaining_tokens = 0
    }

    //se pone la barra de progreso total
    this.data_item.sold_tokens_value_first_to_last = 0
    this.data_item.value_round_first_to_last = 0
    if (this.data_item.list_mint_phases != null && this.data_item.list_mint_phases.length > 1) {
      for (const item_phase of this.data_item.list_mint_phases) {
        this.data_item.sold_tokens_value_first_to_last += item_phase.sold_tokens_phase * item_phase.price_fiat
        this.data_item.value_round_first_to_last += item_phase.max_tokens * item_phase.price_fiat
      }
    }
    this.data_item.collected_first_to_last = (((this.data_item.sold_tokens_value_first_to_last))*100/this.data_item.value_round_first_to_last)
    if (isNaN(this.data_item.collected_first_to_last)) this.data_item.collected_first_to_last = 0



    if (this.data_item.hide_date_start_round){
      this.data_item.date_start_round = "yyyy-mm-dd"
      JQuery('#date_start_round_'+this.data_item.id).addClass('desenfoque')
    } else {
      this.data_item.date_start_round = formatDateFromServer(this.data_item.date_start_round, false)
    }
    if (this.data_item.hide_date_end_round){
      this.data_item.days = "000"
      JQuery('#date_end_round_'+this.data_item.id).addClass('desenfoque')
    }
    if (this.data_item.hide_value_round){
      this.data_item.value_round = "00000000"
      JQuery('#value_round'+this.data_item.id).addClass('desenfoque')
    }
    if (this.data_item.status === INVEST_STATUS_FINANCING_PHASE) {
      this.data_item.days = formatNumber(this.data_item.days)
    } else {
      this.data_item.days = 0
    }

    this.link = '/debt/' + this.data_item.slug

  }

  followsInvest(invest_id){
    followsInvest(invest_id, this);
  }

  myFormatNumber(val){
    return formatNumber(val)
  }

}
</script>
