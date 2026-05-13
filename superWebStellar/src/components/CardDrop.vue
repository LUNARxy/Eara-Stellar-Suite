<template>
  <div v-if="data_item != null">
    <div class="card border-radius-15 " style="height: 96%; padding: 0!important;">

      <router-link :to="link">
        <div class="col s12 pb-10 border-radius-15" :style="{backgroundImage: 'url(' + PUBLIC_URL + data_item.file_top + ')', backgroundSize: 'cover', backgroundRepeat: 'no-repeat'}">
          <div class="col s12 text-center" style="min-height: 200px;">&nbsp;</div>
        </div>
        <div class="col s12 position-drop-img-floating">
          <div class="row padding-0 margin-0">
            <div class="col s6 offset-s3 m4 offset-m4">
              <img class="z-depth-5 border-radius-15 responsive-img" :src="PUBLIC_URL+data_item.file">
            </div>
          </div>
        </div>
      </router-link>


      <div class="row card-content padding-0">
        <div class="col s12 pl-7 pr-7">
          <div style="display: flex;width: 100%; justify-content: space-between;">
            <router-link :to="link"><p class="pl-0 pr-2 bold" style="min-width: 250px;">{{data_item.name}}</p></router-link>
            <div class="right">
              <i :id="'followsInvest_'+data_item.id" v-if="data_item.is_follow" @click="followsInvest(data_item.id)" class="material-icons hand color-base" style="font-size: 26px;">favorite</i>
              <i :id="'followsInvest_'+data_item.id" v-if="!data_item.is_follow" @click="followsInvest(data_item.id)" class="material-icons hand color-base" style="font-size: 26px;">favorite_border</i>
            </div>
          </div>

          <div>
            <div class="row mb-4">
              <div class="col s6">
                <p class="col s12 padding-0 pt-5" style="color: black" :id="'value_round'+this.data_item.id">{{myFormatNumber(data_item.value_round)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</p>
                <p class="col s12 padding-0 pt-2" style="font-size: 0.8rem;">{{ $t('views.Objetivo') }}</p>
                <p class="col s12 padding-0 pt-2" style="font-size: 0.8rem;">{{ $t('views.Valor de la ronda') }}</p>
              </div>
              <div class="col s6">
                <p v-if="data_item.status === INVEST_STATUS_FINANCING_PHASE" class="col s12 padding-0 pt-2 text-right" style="color: black">{{data_item.days}} {{ $t('views.días') }}</p>
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
                <p v-if="data_item.profit_estimated_description === null" class="col s12 padding-0 pb-2" style="color: black">0%</p>
                <p class="col s12 padding-0 pb-2" style="font-size: 0.8rem;">{{ $t('views.Rentabilidad') }}<br>{{ $t('views.estimada') }}</p>
              </div>
              <div class="col s6">
                <p v-if="data_item.time_limit != null" class="col s12 padding-0 pt-6 text-right" style="color: black">{{data_item.time_limit}}</p>
                <p v-if="data_item.time_limit == null" class="col s12 padding-0 pt-6 text-right desenfoque" style="color: black">000000</p>
                <p class="col s12 padding-0 pt-2 text-right" style="font-size: 0.8rem;">{{ $t('views.Duración del proyecto') }}</p>
              </div>
            </div>
          </div>
          <div v-if="data_item.status !== INVEST_STATUS_NEXT_LAUNCH">
            <div class="row mb-0">
              <div class="col s12">
                <hr style="border: 1px solid #e5e5e5;"/>
              </div>
            </div>
            <div class="row">
              <div class="col s6">
                <p class="col s12 padding-0 pt-6" style="color: black">{{myFormatNumber(data_item.sold_tokens_value)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</p>
                <p class="col s12 padding-0 pt-2" style="font-size: 0.8rem;">{{ $t('views.Recaudado') }}</p>
              </div>
              <div class="col s6">
                <p class="col s12 padding-0 pt-6 text-right" style="color: black">{{myFormatNumber(data_item.collected)}}%</p>
                <p class="col s12 padding-0 pt-2 text-right" style="font-size: 0.8rem;">{{ $t('views.Financiado') }}</p>
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
        </div>


        <div class="col s12">
          <hr style="border: 1px solid #e5e5e5;"/>
        </div>
        <div class="col s12 text-justify card-content pl-6 pr-6">
          <div v-html="data_item.proposal_to_investors"></div>
          <div class="text-center mt-3 mb-3">
            <router-link :to="link">
              <button type="button" class="btn-primary">{{ $t('views.Saber más') }}</button>
            </router-link>
          </div>
        </div>

      </div>
    </div>
  </div>


</template>

<script lang="ts">

import {Options, Vue} from "vue-class-component";
import {countDown, followsInvest, formatDateFromServer, formatNumber} from "@/functions";
import {PUBLIC_URL} from "@/services/Http-common"
import store from "@/store";
import {Locales} from "@/locales/locales";
import JQuery from "jquery";
import {
  INVEST_STATUS_FINANCING_PHASE,
  INVEST_STATUS_FINISHED,
  INVEST_STATUS_IN_PROGRESS,
  INVEST_STATUS_NEXT_LAUNCH,
} from "@/const";

@Options({
  props: {
    data_item: Object
  }
})

export default class CardDrop extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  INVEST_STATUS_NEXT_LAUNCH = INVEST_STATUS_NEXT_LAUNCH
  INVEST_STATUS_FINANCING_PHASE = INVEST_STATUS_FINANCING_PHASE
  INVEST_STATUS_IN_PROGRESS = INVEST_STATUS_IN_PROGRESS
  INVEST_STATUS_FINISHED = INVEST_STATUS_FINISHED

  PUBLIC_URL = PUBLIC_URL

  data_item
  link = ''

  mounted(){
    if (store.getters.getLocale == Locales.EN){
      this.data_item.proposal_to_investors = this.data_item.proposal_to_investors_EN
    }

    this.data_item.collected = (((this.data_item.sold_tokens_value))*100/this.data_item.value_round)
    if (isNaN(this.data_item.collected)) this.data_item.collected = 0

    if (this.data_item.hide_date_start_round){
      this.data_item.date_start_round = "yyyy-mm-dd"
      JQuery('#date_start_round_'+this.data_item.id).addClass('desenfoque')
    } else {
      this.data_item.date_start_round = formatDateFromServer(this.data_item.date_start_round, false)
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
