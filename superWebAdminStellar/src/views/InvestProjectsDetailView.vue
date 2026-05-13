<template>

  <Menu/>
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
                <span id="value_round">{{ data_item.value_round_txt }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</span>
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
                <!--<h4 class="white-text">{{ data_item.name }} - {{ data_item.token_abbreviation }}</h4>-->
                <h4 class="white-text invest-detail-name">{{ data_item.name }}</h4>
                <p class="col s12 padding-3 pt-0 white-text">{{ data_item.title }}</p>
              </div>
            </div>

            <div class="col s12 padding-3 text-justify content_description_detail card-content" v-html="data_item.summary"></div>
          </div>

          <div v-if="(data_item.status === INVEST_STATUS_NEXT_LAUNCH || data_item.status === INVEST_STATUS_FINANCING_PHASE) && data_item.date_start_round === '' || data_item.date_start_round === 'yyyy-mm-dd' || data_item.date_start_round === null" class="card col s12 padding-4">
            <!--------Si el proyecto no tiene fecha de lanzamiento-->
            <div v-if="data_item.preference_to_buy !== '0'">
            </div>
            <div class="col s12 text-center">
              <!-- hay fase y si hay whitelist, pero no estoy admitido en la whitelist -->
              <div v-if="data_item.preference_to_buy !== '0' && (data_item.preference_to_buy == null || data_item.preference_to_buy !== data_item.phase)" class="mt-3">
              </div>
              <!-- hay fase y si hay whitelist, pero no estoy admitido en la whitelist pero lo he pedido -->
              <div v-if="data_item.preference_to_buy === '0' && data_item.value_to_invest !== null">
                <h5 class="mt-3 mb-3">{{ $t('views.Ya estás apuntado a la whitelist') }}</h5>
                <p>{{ $t('views.Has indicado que estás interesado en invertir en el proyecto', {'value':myFormatNumber(data_item.value_to_invest), 'project_name': data_item.name, currency: VUE_APP_WHITE_LABEL_CURRENCY})}}</p>
                <button type="button" class="btn-primary mt-3 mb-3" @click="popupSingUpWhiteList">{{ $t('views.Cambiar importe') }}</button>
              </div>
            </div>
          </div>

          <div v-if="(data_item.status === INVEST_STATUS_NEXT_LAUNCH || data_item.status === INVEST_STATUS_FINANCING_PHASE) && data_item.date_start_round !== '' && data_item.date_start_round !== 'yyyy-mm-dd' && data_item.date_start_round !== null" class="card col s12 pt-3 padding-4">
            <!--------Si el proyecto tiene fecha de lanzamiento-->
            <div class="text-center" v-if="data_item.date_end_round !== 'yyyy-mm-dd'">
              <h5 class="text-center" v-if="data_item.status !== INVEST_STATUS_NEXT_LAUNCH">{{ $t('views.Fecha de fin de la fase x financiación', {phase_name: data_item.phase}) }}</h5>
              <p v-if="data_item.status !== INVEST_STATUS_NEXT_LAUNCH">{{myFormatDateCompletedText(data_item.date_end_round)}}</p>
              <h5 class="text-center" v-if="data_item.status === INVEST_STATUS_NEXT_LAUNCH">{{ $t('views.Fecha de inicio de la financiación') }}</h5>
              <p v-if="data_item.status === INVEST_STATUS_NEXT_LAUNCH">{{myFormatDateCompletedText(data_item.date_start_round)}}</p>
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
                <h5 class="col s12 text-center mt-5">{{ $t('views.Recaudación') }}</h5>
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
              <div>
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
                </div>
              </div>
            </div>

            <div v-if="(data_item.status === INVEST_STATUS_NEXT_LAUNCH || data_item.status === INVEST_STATUS_FINANCING_PHASE)" class="col s12 text-center pb-5">
              <div>
                <div v-if="data_item.status === INVEST_STATUS_NEXT_LAUNCH">
                  <!-- he pedido apuntarme a la whitelist -->
                  <div class="pt-3" v-if="data_item.preference_to_buy === '0' && data_item.value_to_invest !== null">
                    <h5 class="mt-3 mb-3">{{ $t('views.Ya estás apuntado a la whitelist') }}</h5>
                    <p>{{ $t('views.Has indicado que estás interesado en invertir en el proyecto', {'value':myFormatNumber(data_item.value_to_invest), 'project_name': data_item.name, currency: VUE_APP_WHITE_LABEL_CURRENCY})}}</p>
                    <button type="button" class="btn-primary mt-3 mb-3" @click="popupSingUpWhiteList">{{ $t('views.Cambiar importe') }}</button>
                  </div>

                  <!-- si tiene fase privada y si estoy incluido o si no tiene fase privada y no me he apuntado a la whitelist -->
                  <div v-if="(data_item.has_white_list && data_item.preference_to_buy === data_item.phase) || (!data_item.has_white_list && data_item.preference_to_buy === null)" class="mt-3">
                    <button type="button" class="btn-primary mt-3 mb-3" @click="popupSingUpWhiteList">{{ $t('views.Apuntarse a la whitelist') }}</button>
                  </div>
                </div>
                <div v-if="data_item.status === INVEST_STATUS_FINANCING_PHASE">
                  <!-- si tiene fase privada y si estoy incluido o si no tiene fase privada -->
                  <div v-if="(data_item.has_white_list && data_item.preference_to_buy === data_item.phase) || !data_item.has_white_list">
                    <button v-if="!is_all_collected" type="button" class="btn-primary mt-3">{{ $t('views.Invierte ahora') }}</button>
                  </div>
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
              {{ data_item.sold_tokens_value_txt }}{{VUE_APP_WHITE_LABEL_CURRENCY}}
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






    <h4 class="col s12 text-center pt-3">{{ $t('views.Información adicional') }}</h4>



    <div class="row padding-3 mb-0">


      <div class="col s12 m8">

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
            <div id="tab_metrics" style="display: none;">
              <div class="row mt-3 mb-3">
                <div class="col s12 text-center">
                  <apexchart type="area" :options="chart_options" :series="chart_balance_profits"></apexchart>
                </div>
              </div>
            </div>
            <div id="tab_activity" style="display: none">
              <div class="row mt-3 mb-3">
                <div class="col s12 table_wrapper_big">

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
                    <tr v-for="item in list_activity" :key="item.id">
                      <td style="font-size: 0.8rem; width: 120px;">{{ formatDate(item.date_created) }}</td>
                      <td>{{ item.phase }}</td>
                      <td>{{ myFormatNumber(item.num_tokens) }}</td>
                      <td>{{ myFormatNumber(item.price_token) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                      <td>{{ myFormatNumber(item.value) }}{{VUE_APP_WHITE_LABEL_CURRENCY}}</td>
                      <td>
                        <span>{{ $t('views.Pago cripto') }}</span>
                      </td>
                      <td>
                        <a v-if="item.tx" :href="SCAN_URL + '/tx/' + item.tx" target="_blank"><img src="@/assets/img/polygon-matic-icon.png" class="ml-6" style="min-width: 40px; width: 40px"></a>
                      </td>
                    </tr>
                    </tbody>
                  </table>

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
          </div>
        </div>
      </div>

    </div>


    <div id="modal_white_list" class="modal border-radius-10 border-radius-15">
      <div class="modal-content text-center">
        <h4 class="mt-3">{{ $t('views.Quiero invertir en el proyecto')}}<br>{{data_item.name}}</h4>
        <div class="row">
          <div class="col s12">
            <p>{{ $t("views.Si quieres apuntarte para invertir por favor introduce el importe aproximado que te gustaría invertir") }}</p>
          </div>
        </div>
        <div class="row">
          <div class="input-field col s12 m4 offset-m4">
            <label for="value_to_invest" class="center-align">{{ $t('views.Importe')}} ({{VUE_APP_WHITE_LABEL_CURRENCY}})</label>
            <input id="value_to_invest" v-model="value_to_invest" type="number" required>
          </div>
        </div>
        <div class="row mt-5">
          <div class="col s12 m12 text-center">
            <div class="col s6 m2 hide-on-small-only">&nbsp;</div>
            <div class="col s6 m4">
              <button type="button" class="btn-primary w100" style="min-width: 155px" @click="singUpWhiteList">{{ $t('views.Quiero invertir')}}</button>
            </div>
            <div class="col s6 m4">
              <button type="button" class="btn-secondary w100 modal-close">{{ $t("views.Cancelar") }}</button>
            </div>
            <div class="col s6 m2 hide-on-small-only">&nbsp;</div>
          </div>
        </div>
      </div>
    </div>


  </div>
</template>


<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import M from "materialize-css";
import InvestServices from "@/services/InvestServices";
import store from "@/store";
import {countDown, formatDateFromServer, formatNumber, getMonthName, reInitTabs, showAlertError} from "@/functions";
import JQuery from 'jquery';
import {Locales} from "@/locales/locales";
import GallerySpide from "@/components/GallerySpide.vue";
import {
  INVEST_STATUS_FINANCING_PHASE,
  INVEST_STATUS_FINISHED,
  INVEST_STATUS_IN_PROGRESS,
  INVEST_STATUS_NEXT_LAUNCH,
} from "@/const";
import Menu from "@/components/Menu.vue";
import {PUBLIC_URL} from "@/services/Http-common";

@Options({
  components: {
    Menu,
    GallerySpide,
  },
})
export default class InvestProjectsDetailView extends Vue {
  VUE_APP_WHITE_LABEL_CURRENCY = '$'


  INVEST_STATUS_FINANCING_PHASE = INVEST_STATUS_FINANCING_PHASE
  INVEST_STATUS_IN_PROGRESS = INVEST_STATUS_IN_PROGRESS
  INVEST_STATUS_NEXT_LAUNCH = INVEST_STATUS_NEXT_LAUNCH
  INVEST_STATUS_FINISHED = INVEST_STATUS_FINISHED

  SCAN_URL = process.env.VUE_APP_SCAN_URL
  data_loaded = false
  // eslint-disable-next-line
  data_item: any = {}
  PUBLIC_URL = PUBLIC_URL
  is_all_collected = false

  value_to_invest = ''
  list_activity = []

  images
  showGallery = false

  month = new Date().getMonth();
  chart_balance_profits = []
  chart_options = {
    chart: {
      type: 'line',
      toolbar: false
    },
    dataLabels: {
      enabled: true,
      style: {
        colors: ['#4f2d7f','#6c6a6a','#08da05']
      }
    },
    stroke: {
      curve: 'stepline'
    },
    xaxis: {
      type: 'string',
      categories: [getMonthName(this.month-5),getMonthName(this.month-4),getMonthName(this.month-3),
        getMonthName(this.month-2),getMonthName(this.month-1), getMonthName(this.month)]
    },
    legend: {
      position: 'top',
    },
    colors: ['#4f2d7f','#6c6a6a','#08da05']
  }

  beforeMount(){
    M.AutoInit()

    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    InvestServices.getInvestProject(this.$route.params.id.toString(), true, true)
        .then(response => {
          this.data_item = response.data;
          //console.log(response.data)

          this.data_loaded = true

          this.data_item.file = this.PUBLIC_URL + this.data_item.file
          this.data_item.file_top = this.PUBLIC_URL+this.data_item.file_top
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
          this.data_item.value_round_txt = formatNumber(this.data_item.value_round)
          this.data_item.num_tokens_txt = formatNumber(this.data_item.num_tokens)
          this.data_item.remaining_tokens_txt = formatNumber(this.data_item.remaining_tokens)
          this.data_item.remaining_tokens_value_txt = formatNumber(this.data_item.remaining_tokens*this.data_item.price_token)
          this.data_item.investors = formatNumber(this.data_item.investors)

          this.data_item.collected = (((this.data_item.sold_tokens_value))*100/this.data_item.value_round)
          //this.data_item.collected = (((this.data_item.sold_tokens_value)*this.data_item.price_token)*100/this.data_item.value_round)
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
        })
        .catch(function (error) {
          showAlertError(error, self, function (){
            window.location.href = "/"
          });
        });


    // las tabs de material con vue no funcionan bien, hay que poner esto para reiniciarlas
    reInitTabs('tabs', 'tab_description')
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
    console.log('')
  }

  getImages(){
    this.images = [];
    for (let item of this.data_item.media) {
      let aux = {src: this.PUBLIC_URL+item.file, alt: item.description}
      this.images.push(aux)
    }
    this.showGallery = true
  }

  getActivity(){
    console.log('')
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
    if (this.data_item.hide_profit_estimated){
      this.data_item.profit_estimated = "00000000"
      JQuery('#profit_estimated').addClass('desenfoque')
    }
    if (this.data_item.hide_value_round){
      this.data_item.value_round_txt = "00000000"
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
    if (process.env.VUE_APP_WHITE_LABEL_IS_DEVELOPMENT !== "true"){
      return '/earastellar/' + pic
    } else {
      return '/earastellaradmin/earastellar/' + pic
    }
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
}
</script>
