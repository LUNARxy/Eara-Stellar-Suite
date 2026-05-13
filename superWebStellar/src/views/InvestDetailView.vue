<template>

  <MenuUser/>

  <div class="content_menu">


    <div class="row" style="display: flex; flex-wrap: wrap-reverse;">

      <div class="col s12 m4">
        <div class="card col s12" style="padding: 10px!important;">
          <img class="border-radius-15 responsive-img" :src="data_item.file">
          <div class="row mt-5">


            <div class="col s12 mt-2">
              <div class="col s6">
                <div class="div_icono_texto">
                  <i class="material-icons primary-color mr-2" style="font-size: 0.8rem">lens</i><span class="black-text">{{ $t('views.Objetivo') }}</span>
                </div>
              </div>
              <div class="col s6 text-right">
                <span id="value_round">{{ myFormatNumber(data_item.value_round)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
              </div>
            </div>
            <div class="col s12 mt-2">
              <div class="col s6">
                <div class="div_icono_texto">
                  <i class="material-icons primary-color mr-2" style="font-size: 0.8rem">lens</i><span class="black-text">{{ $t('views.Cantidad disponible') }}</span>
                </div>
              </div>
              <div class="col s6 text-right">
                  <span id="remaining_tokens_value">
                    <span v-if="data_item.phase === 'all'">0{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
                    <span v-if="data_item.phase !== 'all'">{{ data_item.remaining_tokens_value_txt }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
                  </span>
              </div>
            </div>
            <div v-if="data_item.contract_address != null" class="col s12 mt-2">
              <div class="col s12">
                <div class="div_icono_texto">
                  <i class="material-icons primary-color mr-2" style="font-size: 0.8rem">lens</i><span class="black-text">{{ $t('views.Dirección del contrato') }}</span>
                </div>
              </div>
              <div class="col s12 text-right">
                <span>{{ data_item.contract_address }}</span>
              </div>
            </div>
            <div v-if="data_item.location != null" class="col s12 mt-2">
              <div class="col s12">
                <div class="div_icono_texto">
                  <i class="material-icons primary-color mr-2" style="font-size: 0.8rem">lens</i><span class="black-text">{{ $t('views.Dirección') }}</span>
                </div>
              </div>
              <div class="col s12 text-right">
                <span>{{ data_item.location }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      <div class=" col s12 m8 text-center">
        <div v-if="data_loaded">
          <div class="card col s12" style="padding: 10px!important;">
            <div class="col s12 border-radius-15 pb-10 " :style="{backgroundImage: 'url(' + data_item.file_top + ')', backgroundSize: 'cover', backgroundRepeat: 'no-repeat'}">
              <div class="col s12 text-center pt-3" style="text-shadow: 1px 1px 10px #000000;">
                <h4 class="white-text invest-detail-name">{{ data_item.name }}</h4>
                <p class="col s12 padding-3 pt-0 white-text">{{ data_item.title }}</p>
              </div>
            </div>
            <p class="col s12 padding-3 text-justify content_description_detail" v-html="data_item.summary"></p>
          </div>



          <div v-if="(data_item.status === INVEST_STATUS_NEXT_LAUNCH || data_item.status === INVEST_STATUS_FINANCING_PHASE) && data_item.date_start_round !== '' && data_item.date_start_round !== 'yyyy-mm-dd' && data_item.date_start_round !== null" class="card col s12 pt-3 padding-4">
            <!--------Si el proyecto tiene fecha de lanzamiento-->
            <div class="text-center" v-if="data_item.date_end_round !== 'yyyy-mm-dd'">
              <h5 class="text-center" v-if="data_item.status !== INVEST_STATUS_NEXT_LAUNCH">
                <span>{{ $t('views.Fecha de fin de la fase x financiación', {phase_name: data_item.phase}) }}</span>
              </h5>
              <div>
                <p v-if="data_item.status !== INVEST_STATUS_NEXT_LAUNCH">{{myFormatDateCompletedText(data_item.date_end_round)}}</p>
                <h5 class="text-center" v-if="data_item.status === INVEST_STATUS_NEXT_LAUNCH">{{ $t('views.Fecha de inicio de la financiación') }}</h5>
                <p v-if="data_item.status === INVEST_STATUS_NEXT_LAUNCH">{{myFormatDateCompletedText(data_item.date_start_round)}}</p>
              </div>
              <div id="count_back" class="col s12 pt-3">
                <div class="col s6 m3 text-center">
                  <span id="div_days" style="font-size: 3rem;">0</span><br>
                  <span class="primary-color bold">{{ $t('views.Días') }}</span>
                </div>
                <div class="col s6 m3 text-center">
                  <span id="div_hours" style="font-size: 3rem;">0</span><br>
                  <span class="primary-color bold">{{ $t('views.Horas') }}</span>
                </div>
                <div class="col s6 m3 text-center">
                  <span id="div_minutes" style="font-size: 3rem;">0</span><br>
                  <span class="primary-color bold">{{ $t('views.Minutos') }}</span>
                </div>
                <div class="col s6 m3 text-center">
                  <span id="div_seconds" style="font-size: 3rem;">0</span><br>
                  <span class="primary-color bold">{{ $t('views.Segundos') }}</span>
                </div>
              </div>
            </div>
            <div class="col s12 pt-3" v-if="data_item.status === INVEST_STATUS_FINANCING_PHASE">
              <!--------Si el proyecto tiene fecha de lanzamiento y estamos en financiacion-->
              <div class="col s12 padding-0" v-if="data_item.status === INVEST_STATUS_FINANCING_PHASE">
                <h5 class="col s12 text-center mt-5">
                  <span>{{ $t('views.Recaudación') }}</span>
                </h5>
                <div class="col s12 padding-0 mb-0 meter">
                  <span :style="'width: '+data_item.collected+'%;'"></span>
                </div>
                <p class="col s4 padding-0 text-left">
                  {{ myFormatNumber(data_item.collected) }} %
                  <br>
                  <label style="color: black">{{ $t('views.Financiado') }}</label>
                </p>
                <p class="col s4 padding-0">
                  {{ myFormatNumber(data_item.sold_tokens_value) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}
                  <br>
                  <label style="color: black">{{ $t('views.Recaudado') }}</label>
                </p>
                <p class="col s4 padding-0 text-right">
                  {{ data_item.investors }}
                  <br>
                  <label style="color: black">{{ $t('views.Inversores') }}</label>
                </p>
              </div>
            </div>

            <div class="col s12 pt-5" v-if="(data_item.status === INVEST_STATUS_NEXT_LAUNCH || data_item.status === INVEST_STATUS_FINANCING_PHASE) && data_item.preference_to_buy !== '0'">
              <div v-if="data_item.status === INVEST_STATUS_NEXT_LAUNCH">
                <p>{{ $t('views.Estás interesado en invertir en el proyecto_', {'project_name': data_item.name}) }}</p>
              </div>
              <div v-if="data_item.status === INVEST_STATUS_FINANCING_PHASE">
                <!-- si tiene fase privada y no estoy incluido en la fase -->
                <div v-if="data_item.has_white_list && (data_item.preference_to_buy == null || data_item.preference_to_buy !== data_item.phase)">
                  <p>{{ $t('views.Estás interesado en invertir en el proyecto_ Apúntate a la whitelist_', {'project_name': data_item.name}) }}</p>
                </div>
                <!-- si tiene fase privada y si estoy incluido o si no tiene fase privada -->
                <div v-if="(data_item.has_white_list && data_item.preference_to_buy === data_item.phase) || !data_item.has_white_list">
                  <p v-if="!is_all_collected">{{ $t('views.Estás interesado en invertir en el proyecto_', {'project_name': data_item.name}) }}</p>
                </div>
                <p v-if="show_msg_max_tokens">{{ $t('server.Has supererado el máximo de inversión en el proyecto') }}</p>
              </div>
            </div>

            <div v-if="(data_item.status === INVEST_STATUS_NEXT_LAUNCH || data_item.status === INVEST_STATUS_FINANCING_PHASE)" class="col s12 text-center pb-5">
              <!-- he pedido apuntarme a la whitelist -->
              <div class="pt-3" v-if="data_item.preference_to_buy === 0 && data_item.value_to_invest !== null">
                <h5 class="mt-3 mb-3">{{ $t('views.Ya estás apuntado a la whitelist') }}</h5>
                <p>{{ $t('views.Has indicado que estás interesado en invertir en el proyecto', {'value':myFormatNumber(data_item.value_to_invest), 'project_name': data_item.name, 'currency': VUE_APP_WHITE_LABEL_CURRENCY})}}</p>
                <button type="button" class="btn-primary mt-3 mb-3" @click="popupSingUpWhiteList">{{ $t('views.Cambiar importe') }}</button>
              </div>

              <!-- si tiene fase privada y no me he apuntado a la whitelist todavia -->
              <div v-if="data_item.has_white_list && data_item.preference_to_buy === null" class="mt-3">
                <button type="button" class="btn-primary mt-3 mb-3" @click="popupSingUpWhiteList">{{ $t('views.Apuntarse a la whitelist') }}</button>
              </div>
              <div v-if="data_item.status === INVEST_STATUS_FINANCING_PHASE && (data_item.num_tokens_max_to_buy == null || data_item.num_tokens_max_to_buy > 0)">
                <!-- si tiene fase privada y si estoy incluido o si no tiene fase privada -->
                <div v-if="(data_item.has_white_list && data_item.preference_to_buy === data_item.phase) || !data_item.has_white_list">
                  <router-link v-if="!is_all_collected" :to="'/payment/' + data_item.id + '/' + data_item.slug"><button type="button" class="btn-primary mt-3">{{ $t('views.Invierte ahora') }}</button></router-link>
                </div>
              </div>
            </div>

          </div>

          <div v-if="data_item.date_start_round !== '' && data_item.date_end_round !== 'yyyy-mm-dd' && data_item.date_start_round !== null && (data_item.status === INVEST_STATUS_IN_PROGRESS || data_item.status === INVEST_STATUS_FINISHED)" class="card col s12 padding-4">
            <!--------Si el proyecto tiene fecha de lanzamiento y estamos en curso-->
            <h5 class="col s12 text-center mt-5">{{ $t('views.Fase de financiación terminada') }}</h5>
            <p class="text-center">{{myFormatDateCompletedText(data_item.date_end_round )}}</p>
            <h5 class="col s12 text-center mt-5">{{ $t('views.Recaudación') }}</h5>
            <div class="col s12 padding-0 mb-0 meter">
              <span :style="'width: '+data_item.collected+'%;'"></span>
            </div>
            <p class="col s4 padding-0 text-left">
              {{ data_item.sold_tokens_value_txt }} {{VUE_APP_WHITE_LABEL_CURRENCY}}
              <br>
              <label style="color: black">{{ $t('views.Financiado') }}</label>
            </p>
            <p class="col s4 padding-0">
              {{ myFormatNumber(data_item.collected) }} %
              <br>
              <label style="color: black">{{ $t('views.Recaudado') }}</label>
            </p>
            <p class="col s4 padding-0 text-right">
              {{ data_item.investors }}
              <br>
              <label style="color: black">{{ $t('views.Inversores') }}</label>
            </p>
          </div>

        </div>
      </div>
    </div>






    <h4 class="col s12 text-center pt-3 mb-3">{{ $t('views.Información adicional') }}</h4>



    <div class="row mb-0">


      <div id="card_details" class="col s12 m8">

        <div class="card padding-10px mt-0">
          <ul id="tabs" class="tabs">
            <li class="tab"><a href="#tab_description">{{ $t('views.Descripción') }}</a></li>
            <li class="tab" v-if="data_item.list_mint_phases?.length > 0 || data_item.list_status_description?.length > 0"><a href="#tab_status">{{ $t('views.Estado') }}</a></li>
            <li class="tab" v-if="data_item.news?.length > 0"><a href="#tab_news">{{ $t('views.Noticias') }}</a></li>
            <li class="tab" v-if="data_item.documents?.length > 0"><a href="#tab_documents">{{ $t('views.Documentos') }}</a></li>
            <li class="tab" v-if="data_item.questions?.length > 0"><a href="#tab_qa">{{ $t('views.Q&A') }}</a></li>
            <li class="tab" v-if="data_item.team?.length > 0"><a href="#tab_team">{{ $t('views.Equipo') }}</a></li>
            <li class="tab" v-if="data_item.media?.length > 0"><a href="#tab_media" @click="getImages">{{ $t('views.Galería') }}</a></li>
            <li class="tab"><a href="#tab_activity" @click="getActivity">{{ $t('views.Actividad') }}</a></li>
          </ul>
        </div>

        <div class="card padding-1">
          <div class="card-content content_description_detail">
            <div id="tab_description" style="display: block">
              <div class="text-justify" v-html="data_item.description"></div>
            </div>

            <div id="tab_status" v-if="data_item.list_mint_phases?.length > 0 || data_item.list_status_description?.length > 0" style="display: none;">
              <div v-if="data_item.list_mint_phases?.length > 0">
                <h6 class="text-center">{{ $t('views.Fases de financiación') }}</h6>
                <div class="row table_wrapper_big">
                  <table>
                    <thead>
                    <tr>
                      <th>{{ $t('views.Fase') }}</th>
                      <th>{{ $t('views.Inicio') }}</th>
                      <th>{{ $t('views.Fin') }}</th>
                      <th>{{ $t('views.N de tokens') }}</th>
                      <th>{{ $t('views.Precio token') }}</th>
                      <th>{{ $t('views.Mis tokens') }}</th>
                      <th>{{ $t('views.Total') }}</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="mint_phases in data_item.list_mint_phases" :key="mint_phases.id">
                      <td>{{ mint_phases.phase }}</td>
                      <td style="font-size: 0.8rem; width: 120px;">{{ formatDate(mint_phases.date_start) }}</td>
                      <td style="font-size: 0.8rem; width: 120px;">{{ formatDate(mint_phases.date_end) }}</td>
                      <td>{{ myFormatNumber(mint_phases.max_tokens) }}</td>
                      <td>{{ myFormatNumber(mint_phases.price_fiat) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                      <td>{{ myFormatNumber(mint_phases.num_tokens_mine)}}</td>
                      <td>{{ myFormatNumber(mint_phases.value_tokens_mine)}}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                    </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div v-if="data_item.list_status_description?.length > 0">
                <h6 class="text-center mt-7">{{ $t('views.Estado del proyecto') }}</h6>
                <div class="row mt-3" v-for="status_description in data_item.list_status_description" :key="status_description.id">
                  <span class="col s12 mt-2">{{status_description.description}}</span>
                  <span class="col s12 text-right mt-2" style="font-size: 0.8rem;">{{ formatDate(status_description.date_created)}}</span>
                  <br>
                </div>
              </div>
            </div>
            <div id="tab_news" v-if="data_item.news?.length > 0" style="display: none;">
              <div class="row" v-for="item_news in data_item.news" :key="item_news.id">
                <div class="col s12 m3">
                  <img class="responsive-img w100" :src="PUBLIC_URL+item_news.file" v-if="item_news.file != null">&nbsp;
                </div>
                <div class="col s12 m9">
                  <a :href="item_news.url" target="_blank" v-if="item_news.url !== null"><p class="title">{{item_news.title}}</p></a>
                  <p class="title" v-if="item_news.url === null">{{item_news.title}}</p>
                  <p class="mt-0" v-html="item_news.summary"></p>
                </div>
              </div>
            </div>
            <div id="tab_documents" v-if="data_item.documents?.length > 0" style="display: none;">
              <div class="row" v-for="item_documents in data_item.documents" :key="item_documents.id">
                <div class="col s12 text-image">
                  <a :href="PUBLIC_URL+item_documents.file" target="_blank"><img src="@/assets/img/pdf.png" class="mb-0" style="min-width: 80px; max-width: 80px;"></a>
                  <div class="mt-0" v-html="item_documents.description"></div>
                </div>
              </div>
            </div>
            <div id="tab_qa" v-if="data_item.questions?.length > 0" style="display: none;">
              <div class="row" v-for="item_questions in data_item.questions" :key="item_questions.id">
                <div class="col s12">
                  <p class="title">{{item_questions.title}}</p>
                  <div class="col s12 text-right pb-2" style="font-size: 0.8rem">{{item_questions.date_created}}</div>
                  <div class="col s12 text-justify" v-html="item_questions.comment"></div>
                </div>
              </div>
            </div>
            <div id="tab_team" v-if="data_item.team?.length > 0" style="display: none;">
              <div class="row mt-3 pb-3" style="border-bottom: 1px solid #c5c5c5;" v-for="item_team in data_item.team" :key="item_team.id">
                <div class="col s12 m3 l2 text-center">
                  <img class="w100" style="border-radius: 50%; max-width: 250px;" :src="PUBLIC_URL+item_team.file">
                </div>
                <div class="col s12 m9 l10">
                  <div class="col s11">
                    <!--<p class="title">{{item_team.name}} - {{ data_item.token_abbreviation }}</p>-->
                    <p class="title">{{item_team.name}}</p>
                    <p class="mt-2" style="font-size: 0.8rem">{{item_team.job}}</p>
                  </div>
                  <div class="col s1 text-right pr-2">
                    <a :href="item_team.url_linked_in" target="_blank" v-if="item_team.url_linked_in !== null"><img :src="getImgUrl('linkedin.png')" style="width: 32px;"></a>
                  </div>
                  <div class="col s12 text-justify mt-2">
                    <p v-html="item_team.description"></p>
                  </div>
                </div>
              </div>
            </div>
            <div id="tab_media" v-if="data_item.media?.length > 0" style="display: none;">
              <div class="row mt-3 mb-3">
                <div class="col s12 text-center">
                  <GallerySpide :slides="images" v-if="showGallery"/>
                </div>
              </div>
            </div>
            <div id="tab_activity" style="display: none">
              <div class="row mt-3 mb-3">
                <div class="col s12 table_wrapper_big">

                  <PaginationDynamic v-if="get_activity_function != null" :serviceFunction=get_activity_function :functionParams="list_params_paginated" :per-page="10">
                    <template v-slot:default="{ items }">
                      <table>
                        <thead>
                        <tr>
                          <th>{{ $t('views.Fecha') }}</th>
                          <th>{{ $t('views.Fase') }}</th>
                          <th>{{ $t('views.Tokens') }}</th>
                          <th>{{ $t('views.Precio') }}</th>
                          <th>{{ $t('views.Valor') }}</th>
                          <th>{{ $t('views.Tipo') }}</th>
                        </tr>
                        </thead>

                        <tbody>
                        <tr v-for="item in items" :key="item.id">
                          <td style="font-size: 0.8rem; width: 120px;">{{ formatDate(item.date_created) }}</td>
                          <td>{{ item.phase }}</td>
                          <td>{{ myFormatNumber(item.num_tokens) }}</td>
                          <td>{{ myFormatNumber(item.price_token) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                          <td>{{ myFormatNumber(item.value) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                          <td>
                            <span>{{ $t('views.Pago crypto') }}</span>
                          </td>
                          <td>
                            <a v-if="item.tx" :href="SCAN_URL + '/tx/' + item.tx" target="_blank"><img src="@/assets/img/polygon-matic-icon.png" class="ml-6" style="min-width: 40px; width: 40px"></a>
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


      <div class="col s12 m4 mb-4">
        <div class="card padding-1 margin-0">
          <div class="card-content">
            <h6 class="pb-3">{{ $t('views.Propuesta a inversores') }}</h6>
            <div class="text-justify content_description_detail">
              <div v-html="data_item.proposal_to_investors"></div>
            </div>
            <div class="text-center mt-3">
            </div>
          </div>
        </div>
      </div>

    </div>


    <div id="modal_white_list" class="modal border-radius-10 border-radius-15">
      <div class="modal-content text-center">
        <form @submit.prevent="singUpWhiteList">
          <h4 class="mt-3">{{ $t('views.Quiero invertir en el proyecto')}}<br>{{data_item.name}}</h4>
          <div class="row">
            <div class="col s12">
              <p>{{ $t("views.Si quieres apuntarte para invertir por favor introduce el importe aproximado que te gustaría invertir") }}</p>
            </div>
          </div>
          <div class="row">
            <div class="input-field col s12 m4 offset-m4">
              <label for="value_to_invest" class="center-align active">{{ $t('views.Importe')}} ({{VUE_APP_WHITE_LABEL_CURRENCY}})</label>
              <input id="value_to_invest" v-model="value_to_invest" type="number" required @keydown="myNumbersOnly($event)" min="1" value="1">
            </div>
          </div>
          <div class="row mt-5">
            <div class="col s12 m12 text-center">
              <div class="col s12 m2 hide-on-small-only">&nbsp;</div>
              <div class="col s12 m4">
                <button type="submit" class="btn-primary w100 mb-5" style="min-width: 155px">{{ $t('views.Quiero invertir')}}</button>
              </div>
              <div class="col s12 m4">
                <button type="button" class="btn-secondary w100 modal-close">{{ $t("views.Cancelar") }}</button>
              </div>
              <div class="col s12 m2 hide-on-small-only">&nbsp;</div>
            </div>
          </div>
        </form>
      </div>
    </div>


    <Footer />
  </div>
</template>


<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import Footer from "@/components/Footer.vue";
import M from "materialize-css";
import InvestServices from "@/services/InvestServices";
import store from "@/store";
import MenuUser from "@/components/dashboard/MenuUser.vue";
import {checkKYCValid, countDown, formatDateFromServer, formatNumber, funcGetImgUrl, hideAlertLoading, numbersOnly, reInitTabs, showAlert, showAlertError, showAlertLoading} from "@/functions";
import {PUBLIC_URL} from "@/services/Http-common"
import JQuery from 'jquery';
import {Locales} from "@/locales/locales";
import GallerySpide from "@/components/GallerySpide.vue";
import UserServices from "@/services/UserServices";
import {
  INVEST_STATUS_FINANCING_PHASE,
  INVEST_STATUS_FINISHED,
  INVEST_STATUS_IN_PROGRESS,
  INVEST_STATUS_NEXT_LAUNCH,
} from "@/const";

import PaginationDynamic from "@/components/pagination/PaginationDynamic.vue";

@Options({
  components: {
    PaginationDynamic,
    GallerySpide,
    MenuUser,
    Footer,
  },
})
export default class InvestDetailView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'

  INVEST_STATUS_FINANCING_PHASE = INVEST_STATUS_FINANCING_PHASE
  INVEST_STATUS_IN_PROGRESS = INVEST_STATUS_IN_PROGRESS
  INVEST_STATUS_NEXT_LAUNCH = INVEST_STATUS_NEXT_LAUNCH
  INVEST_STATUS_FINISHED = INVEST_STATUS_FINISHED

  SCAN_URL = process.env.VUE_APP_SCAN_URL
  isLoggedIn = store.getters.isLoggedIn
  data_loaded = false
  // eslint-disable-next-line
  data_item: any = {}
  PUBLIC_URL = PUBLIC_URL
  is_all_collected = false

  value_to_invest = 1

  images
  showGallery = false
  show_msg_max_tokens = false

  list_params_paginated = {
    invest_id: 0,
  }
  get_activity_function = null

  mounted(){
    M.AutoInit()
    checkKYCValid(this)

    // las tabs de material con vue no funcionan bien, hay que poner esto para reiniciarlas
    reInitTabs('tabs', 'tab_description')
  }

  updated(){
    // para que haga el scroll porque algunas veces no sale
    let html = (document.getElementById('html') as HTMLElement)
    if (html) {
      html.style.overflow = "scroll";
    }
  }

  getData(){
    showAlertLoading()
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    let project = this.$route.params.slug?.toString()

    InvestServices.getInvest(project)
        .then(response => {
          this.data_item = response.data;

          self.data_loaded = true
          hideAlertLoading()

          this.list_params_paginated.invest_id = this.data_item.id
          //console.log(response.data)

          //si no estoy logado y el proyecto no esta en completado no se puede ver
          if (!this.isLoggedIn && this.data_item.status != 99){
            this.$router.push('/')
          }


          this.data_item.file = PUBLIC_URL + this.data_item.file
          this.data_item.file_top = PUBLIC_URL+this.data_item.file_top
          //se suman los tokens vendidos con los que están esperando a validarse como vendidos
          this.data_item.sold_tokens_value = (this.data_item.sold_tokens_phase + this.data_item.waiting_tokens) * this.data_item.price_token
          this.data_item.sold_tokens_value_txt = formatNumber(this.data_item.sold_tokens_value)

          if (store.getters.getLocale == Locales.EN){
            this.data_item.name = this.data_item.name_EN
            this.data_item.title = this.data_item.title_EN
            this.data_item.summary = this.data_item.summary_EN
            this.data_item.description = this.data_item.description_EN
            this.data_item.proposal_to_investors = this.data_item.proposal_to_investors_EN
            this.data_item.time_limit = this.data_item.time_limit_EN
          }
          this.data_item.num_tokens_txt = formatNumber(this.data_item.num_tokens)
          this.data_item.remaining_tokens_txt = formatNumber(this.data_item.remaining_tokens)
          this.data_item.remaining_tokens_value_txt = formatNumber(this.data_item.remaining_tokens*this.data_item.price_token)
          this.data_item.investors = formatNumber(this.data_item.investors)

          this.data_item.collected = (((this.data_item.sold_tokens_value))*100/this.data_item.value_round)
          if (isNaN(this.data_item.collected)) this.data_item.collected = 0
          if (this.data_item.collected >= 100){
            this.is_all_collected = true
            this.data_item.remaining_tokens_value_txt = "0"
            this.data_item.remaining_tokens_txt = 0
          }

          this.data_item.date_start_round = formatDateFromServer(this.data_item.date_start_round, true)
          this.data_item.date_end_round = formatDateFromServer(this.data_item.date_end_round, true)
          if (this.data_item.date_end !== null) {
            this.data_item.date_end = formatDateFromServer(this.data_item.date_end, true)
          } else {
            this.data_item.date_end = null
          }

          this.desenfoque()

          if (this.data_item.status == this.INVEST_STATUS_NEXT_LAUNCH && !this.data_item.hide_date_start_round){
            setTimeout(() => {
              countDown(this.data_item.date_start_round)
            }, 100);
          } else {
            setTimeout(() => {
              countDown(this.data_item.date_end_round)
            }, 100);
          }

          // si no puedo comprar tokens
          if (this.data_item.num_tokens_max_to_buy != null && this.data_item.num_tokens_max_to_buy <= 0) {
            this.show_msg_max_tokens = true;
          }

        })
        .catch(function (error) {
          hideAlertLoading()
          self.data_loaded = false
          showAlertError(error, self, function (){
            window.location.href = "/"
          });
        });

  }

  getActivity(){
    this.get_activity_function = InvestServices.getInvestActivity
  }


  popupSingUpWhiteList(){

    const elems = document.querySelectorAll('.modal');
    M.Modal.init(elems, {dismissible: false});

    const singleModalElem = document.querySelector('#modal_white_list');
    if (singleModalElem != null) {
      const instance = M.Modal.getInstance(singleModalElem);

      instance.open();
    }
  }

  singUpWhiteList(){
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    UserServices.singUpWhiteList(this.data_item.id, this.value_to_invest)
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        .then(response => {
          showAlert(self.$t("views.Apuntarse a la whitelist"),self.$t("views.Te has apuntado a la Whitelist de proyecto_", { name: self.data_item.name}), false, function() {
            self.$router.go(0) //window.location.reload()
          })
        })
        .catch(function (error) {
          showAlertError(error, self)
        });
  }

  getImages(){
    this.images = [];
    for (let item of this.data_item.media) {
      let aux = {src: this.PUBLIC_URL+item.file, alt: item.description}
      this.images.push(aux)
    }
    this.showGallery = true
  }


  desenfoque(){
    //si esta marcado el check de poner borrosa la cuenta atrás
    if (this.data_item.hide_time_data){
      JQuery('#card_date_back').hide()
    }
    if (this.data_item.hide_date_start_round){
      this.data_item.date_start_round = "yyyy-mm-dd"
      JQuery('#date_start_round').addClass('desenfoque')
    }
    if (this.data_item.hide_date_end_round){
      this.data_item.date_end_round = "yyyy-mm-dd"
      JQuery('#date_end_round').addClass('desenfoque')
    }
    if (this.data_item.hide_profit_estimated_description){
      this.data_item.profit_estimated_description = "00000000"
      JQuery('#profit_estimated_description').addClass('desenfoque')
    }
    if (this.data_item.hide_value_round){
      this.data_item.value_round = "00000000"
      JQuery('#value_round').addClass('desenfoque')
    }
    if (this.data_item.hide_num_tokens){
      this.data_item.num_tokens = "00000000"
      JQuery('#num_tokens').addClass('desenfoque')
      this.data_item.remaining_tokens_txt = "00000000"
      this.data_item.remaining_tokens_value_txt = "00000000"
      JQuery('#remaining_tokens').addClass('desenfoque')
      JQuery('#remaining_tokens_value').addClass('desenfoque')
    }
  }

  myFormatNumber(val){
    return formatNumber(val)
  }


  getImgUrl(pic) {
    return funcGetImgUrl(pic)
  }

  formatDate(date) {
    return formatDateFromServer(date)
  }
  myFormatDateCompletedText(fechaString){
    // Crear un objeto Date a partir de la cadena proporcionada
    const fecha = new Date(fechaString);

    // Obtener el nombre del día de la semana
    const diasSemana = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    const nombreDiaSemana = diasSemana[fecha.getDay()];

    // Obtener el nombre del mes
    const meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
    const nombreMes = meses[fecha.getMonth()];

    // Obtener el día del mes
    const diaMes = fecha.getDate();

    // Obtener el año
    const año = fecha.getFullYear();

    // Obtener la hora y minutos
    const horas = fecha.getHours();
    const minutos = fecha.getMinutes();

    // Construir la cadena formateada
    const resultado = `${nombreDiaSemana} ${diaMes} de ${nombreMes} de ${año} a las ${horas}:${minutos}`;

    return resultado;
  }
  myNumbersOnly(evt, decimals = false){
    numbersOnly(evt, decimals)
  }
}
</script>
