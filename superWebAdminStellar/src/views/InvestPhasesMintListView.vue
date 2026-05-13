<template>
  <Menu/>
  <div class="content_menu">
    <div class="row">
      <div class="col s12">
        <div class="col s12 padding-0 mb-3 text-center">
          <h4 class="col s12 text-center">{{ $t('views.Fases de venta de tokens del proyecto') }}</h4>
        </div>


        <div class="col s12 card padding-3">
          <div class="card-content">

            <p class="mb-3 bold text-center">{{ $t('views.Una vez desplegado el contrato en blockchain las fases de venta no se podrán cambiar') }}</p>
            <button v-if="deploy_state !== DEPLOY_STATUS_DEPLOYED && data_form.status !== INVEST_STATUS_FINISHED" class="btn-primary right" @click="showForm(null)">{{ $t('views.Nueva') }}</button>

            <form id="form" @submit.prevent="save" class="mb-4"  v-show="formVisible">
              <div class="row padding-7">
                <div class="input-field col s12 m3">
                  <label for="phase" class="active"><span class="required">*</span> {{ $t('views.Phase') }}:</label>
                  <input type="text" id="phase" v-model="data_form.phase" maxlength="50" onkeydown="return /^[0-9a-zA-Z-_.]+$/i.test(event.key)" required :disabled="data_form.update">
                </div>
                <div class="input-field col s12 m3">
                  <label for="max_tokens" class="active"><span class="required">*</span> {{ $t('views.N tokens') }}:</label>
                  <input type="text" id="max_tokens" v-model="data_form.max_tokens" @keydown="myNumbersOnly" required  :disabled="deploy_state === DEPLOY_STATUS_DEPLOYED">
                </div>
                <div class="input-field col s12 m3">
                  <label for="price_fiat" class="active"><span class="required">*</span> {{ $t('views.Precio token') }}:</label>
                  <input type="text" id="price_fiat" v-model="data_form.price_fiat" @keydown="myNumbersOnly($event, true)" required  :disabled="deploy_state === DEPLOY_STATUS_DEPLOYED">
                </div>
                <div class="input-field col s12 m3">
                  <label for="num_tokens_min_to_buy" class="active"><span class="required">*</span> {{ $t('views.Ticket mínimo') }}:</label>
                  <input type="text" id="num_tokens_min_to_buy" v-model="data_form.num_tokens_min_to_buy" @keydown="myNumbersOnly" required  :disabled="deploy_state === DEPLOY_STATUS_DEPLOYED">
                </div>
                <!--
                <div class="input-field col s12 m2">
                  <select class="browser-default" id="symbol_fiat" required v-model="data_form.symbol_fiat">
                    <option value="EUR" selected>Euro</option>
                    <option value="USDT"><span class="required">*</span> Dolar:</option>
                  </select>
                  <label for="symbol_fiat" class="active active_select"><span class="required">*</span> {{ $t('views.Moneda') }}:</label>
                </div>
                -->
                <div class="input-field col s12 m6">
                  <label for="date_start" class="active"><span class="required">*</span> {{ $t('views.Fecha inicio de la fase') }}:</label>
                  <input id="date_start" name="date_start" v-model="data_form.date_start" type="datetime-local" required>
                </div>
                <div class="input-field col s12 m6">
                  <label for="date_end" class="active"><span class="required">*</span> {{ $t('views.Fecha FIN de la fase') }}:</label>
                  <input id="date_end" name="date_end" v-model="data_form.date_end" type="datetime-local" required>
                </div>

                <div class="input-field col s12">
                  <input type="hidden" id="id" v-model="data_form.id">
                  <button class="btn-primary right" type="submit" :disabled="loading">{{ $t('views.guardar') }}</button>
                </div>
              </div>
            </form>

            <div class="table_wrapper">
              <table>
                <thead>
                <tr>
                  <th>{{ $t('views.Fecha Inicio') }}</th>
                  <th>{{ $t('views.Fecha Fin') }}</th>
                  <th>{{ $t('views.Fase') }}</th>
                  <th>{{ $t('views.N tokens') }}</th>
                  <th>{{ $t('views.Precio token') }}</th>
                  <th>{{ $t('views.Ticket mínimo') }}</th>
                  <th>{{ $t('views.Es privada') }}</th>
                  <!--<th>{{ $t('views.Moneda') }}</th>-->
                  <th></th>
                </tr>
                </thead>

                <tbody>
                <tr v-for="item in list_phases" :key="item.id">
                  <td>{{ item.date_start_txt }}</td>
                  <td>{{ item.date_end_txt }}</td>
                  <td>{{ item.phase }}</td>
                  <td>{{ item.max_tokens }}</td>
                  <td>{{ item.price_fiat }}</td>
                  <td>{{ item.num_tokens_min_to_buy }}</td>
                  <td>{{ item.is_private }}</td>
                  <!--<td>{{ item.symbol_fiat }}</td>-->
                  <td width="160px" v-if="data_form.status !== INVEST_STATUS_FINISHED">
                    <button class="btn-primary mr-3" @click.stop="showForm(item)"><i class="material-icons">edit</i></button>
                    <button v-if="deploy_state !== DEPLOY_STATUS_DEPLOYED" class="btn-primary" @click.stop="deleteItem(item.phase)"><i class="material-icons">delete</i></button>
                  </td>
                </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>

        <div v-if="!has_phase" class="col s12 card padding-3">
          <div class="card-content">

            <p class="mb-3 bold text-center">{{ $t('views.Si el proyecto estaba completado y no queremos poner las fases de venta, puedes rellenar estos campos') }}</p>

            <form @submit.prevent="saveWhithoutPhase" class="mb-4">
              <div class="row">
                <div class="input-field col s12 m3">
                  <label for="num_investors_completed" class="active"><span class="required">*</span> {{ $t('views.N de inversores') }}:</label>
                  <input type="text" id="num_investors_completed" v-model="data_form.num_investors_completed" required @keydown="myNumbersOnly">
                </div>
                <div class="input-field col s12 m3">
                  <label for="num_tokens_completed" class="active"><span class="required">*</span> {{ $t('views.N tokens') }}:</label>
                  <input type="text" id="num_tokens_completed" v-model="data_form.num_tokens_completed" @keydown="myNumbersOnly" required>
                </div>
                <div class="input-field col s12 m3">
                  <label for="total_amount_invested_completed" class="active"><span class="required">*</span> {{ $t('views.Total invertido') }}:</label>
                  <input type="text" id="total_amount_invested_completed" v-model="data_form.total_amount_invested_completed" @keydown="myNumbersOnly" required>
                </div>
                <div class="input-field col s12 m3">
                  <button class="btn-primary right" type="submit" :disabled="loading">{{ $t('views.guardar') }}</button>
                </div>
              </div>
            </form>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>



<script lang="ts">
import InvestServices from '@/services/InvestServices'
import {Options, Vue} from "vue-class-component";
import Menu from "@/components/Menu.vue";
import {formatDateFromServer, formatNumber, isValidDate, numbersOnly, showAlert, showAlertError} from "@/functions";

import {
  DEPLOY_STATUS_DEPLOYED,
  DEPLOY_STATUS_PENDING, INVEST_STATUS_FINISHED,
} from "@/const";
import JQuery from "jquery";


@Options({
  components: {
    Menu,
  },
})
export default class InvestPhasesMintListView extends Vue {

  list_phases = []
  loading = false
  deploy_state = DEPLOY_STATUS_PENDING
  DEPLOY_STATUS_DEPLOYED = DEPLOY_STATUS_DEPLOYED
  INVEST_STATUS_FINISHED = INVEST_STATUS_FINISHED

  // eslint-disable-next-line
  data_form: any = {
    "id": " ",
    "phase": " ",
    "max_tokens": " ",
    "price_fiat": " ",
    "num_tokens_min_to_buy": " ",
    "date_start": " ",
    "date_end": " ",
  }


  has_phase = false

  current_phase:any = null
  formVisible = false

  mounted () {

    this.data_form.symbol_fiat = "EUR"
    this.data_form.is_private = false

    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    InvestServices.getInvestPhasesMint(this.$route.params.invest_id)
        .then(response => {
          this.list_phases = response.data;
          let i = 0
          for (let item of this.list_phases){
            item.is_private = item.is_private==0?self.$t("views.NO"):self.$t("views.SI")
            item.max_tokens = formatNumber(item.max_tokens)
            item.price_fiat = formatNumber(item.price_fiat, 9)
            item.num_tokens_min_to_buy = formatNumber(item.num_tokens_min_to_buy)
            item.date_start_txt = formatDateFromServer(item.date_start, true)
            item.date_end_txt = formatDateFromServer(item.date_end, true)
            item.id = i
            i++
            this.has_phase = true
          }
        })
        .catch(function (error) {
          showAlertError(error,self)
        });

    //se recupera para saber el estado de si esta el contrato desplegado
    InvestServices.getInvestProject(this.$route.params.invest_id)
        .then(response => {
          this.data_form.status = response.data.status
          this.deploy_state = response.data.deploy_state;
          this.data_form.num_investors_completed = response.data.num_investors_completed;
          this.data_form.num_tokens_completed = response.data.num_tokens_completed;
          this.data_form.total_amount_invested_completed = response.data.total_amount_invested_completed;
        })
        .catch(function (error) {
          showAlertError(error,self)
        });
  }

  save() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    if (this.$route.params.invest_id !== undefined){
      this.data_form.invest_id = this.$route.params.invest_id;
      if (Date.parse(this.data_form.date_end) < Date.parse(this.data_form.date_start)){
        showAlertError(this.$t('views.La fecha de Fin no puede ser menor que la fecha de Inicio'), this)
        return;
      }
      for (let item of this.list_phases){
        if (this.data_form.id == item.id){
          continue;
        }
        //comprobamos si ya hay una fase con el mismo nombre
        if (item.phase == this.data_form.phase){
          showAlertError(this.$t('views.Existe una fase con el mismo nombre, introduce otro'), this)
          return;
        }
        //comprobamos que no haya fechas solapadas
        if ((Date.parse(this.data_form.date_start) <= Date.parse(item.date_start) && Date.parse(this.data_form.date_end) >= Date.parse(item.date_start))
            || (Date.parse(this.data_form.date_start) <= Date.parse(item.date_end) && Date.parse(this.data_form.date_end) >= Date.parse(item.date_start))
        ){
          showAlertError(this.$t('views.Las fechas de las fases no se pueden solapar'), this)
          return;
        }
      }
      this.data_form.max_tokens = this.data_form.max_tokens.replace(/\./g, '')
      this.data_form.price_fiat = this.data_form.price_fiat.replace(/\./g, '')
      this.data_form.num_tokens_min_to_buy = this.data_form.num_tokens_min_to_buy.replace(/\./g, '')

      this.loading = true
      //si tiene id de noticia entonces es actualizar sino es uno nuevo
      InvestServices.saveInvestPhasesMint(this.data_form)
          // eslint-disable-next-line no-unused-vars
          .then(response => {
            showAlert("",self.$t('views.Datos guardados correctamente'), false, function() {
              self.$router.go(0)
            })
          })
          .catch(function (error) {
            self.loading = false
            showAlertError(error, self)
          });
    }
  }

  deleteItem(phase) {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    showAlert("",self.$t('views.Estás seguro de borrar la fase'), true, function() {
      InvestServices.deletePhasesMint(self.$route.params.invest_id, phase)
          .then(response => {
            self.$router.go(0)
          })
          .catch(function (error) {
            showAlertError(error, self)
          });
    })
  }
  showForm(item){

    this.formVisible = true

    if (item) {
      this.current_phase = item
      this.data_form.id = this.current_phase.id
      this.data_form.phase = this.current_phase.phase
      this.data_form.max_tokens = this.current_phase.max_tokens
      this.data_form.price_fiat = this.current_phase.price_fiat
      this.data_form.num_tokens_min_to_buy = this.current_phase.num_tokens_min_to_buy
      this.data_form.date_start = formatDateFromServer(this.current_phase.date_start)
      this.data_form.date_end = formatDateFromServer(this.current_phase.date_end)
      this.data_form.update = true
      if (this.current_phase.is_private == this.$t("views.SI")) this.data_form.is_private = true
      else this.data_form.is_private = false
    } else {
      this.current_phase = null
      this.data_form.id = ''
      this.data_form.phase = ''
      this.data_form.max_tokens = ''
      this.data_form.price_fiat = ''
      this.data_form.date_start = new Date().toISOString().split('T')[0]
      this.data_form.date_end = new Date().toISOString().split('T')[0]
      this.data_form.update = false
    }

    console.log(this.data_form.update)
    // const myForm = document.getElementById('form')
    // if (myForm != null) (myForm as HTMLInputElement).style.display = '';
  }

  saveWhithoutPhase(){
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this
    if (this.$route.params.invest_id !== undefined){
      this.data_form.invest_id = this.$route.params.invest_id;

      this.data_form.num_investors_completed = parseInt(this.data_form.num_investors_completed)
      this.data_form.num_tokens_completed = parseInt(this.data_form.num_tokens_completed)
      this.data_form.total_amount_invested_completed = this.data_form.total_amount_invested_completed.replace(/\./g, '')
      this.loading = true

      InvestServices.savePhaseCompleted(this.data_form)
          // eslint-disable-next-line no-unused-vars
          .then(response => {
            showAlert("",self.$t('views.Datos guardados correctamente'), false, function() {
              self.$router.go(0)
            })
          })
          .catch(function (error) {
            self.loading = false
            showAlertError(error, self)
          });
    }
  }


  isValidDateHour(value){
    let date_in = JQuery('#' + value).val().toString()
    if (date_in != undefined && date_in != "") {
      const date_hour =  date_in.split("T")
      date_in = date_hour[0]
      if (!isValidDate(date_in)) {
        showAlertError(this.$t('views.La fecha no es correcta'), this)
      } else {
        //comprobamos la hora
        if (date_hour[1] != undefined) {
          let hour_minute = date_hour[1].split(":")
          let hour = parseInt(hour_minute[0])
          let minute = parseInt(hour_minute[1])
          if (isNaN(hour) || isNaN(minute) || hour < 0 || hour > 24 || minute < 0 || minute > 59) {
            showAlertError(this.$t('views.La fecha no es correcta'), this)
          }
        } else {
          showAlertError(this.$t('views.La hora no es correcta'), this)
        }
      }
    }
  }

  myNumbersOnly(evt, decimals = false){
    numbersOnly(evt, decimals)
  }
}


</script>
