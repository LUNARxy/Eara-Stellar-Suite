<template>
  <div class="col s12 padding-0 padding-0" style="display: block">
    <div class="card padding-7 pt-2 pb-2 mt-0">
      <form @submit.prevent="updateImages">
        <fieldset :disabled="data_item.kyc_valid == 1 || data_item.kyc_valid == 2">

          <div class="row">
            <div class="col s12 text-center">
              <h5>{{ $t('views.Documentos') }}</h5>
              <p class="mt-3 mb-3 text-left">{{ $t('views.Para comprobar la veracidad de los datos introducidos en el paso anterior_') }}</p>
            </div>
          </div>
          <template v-if="data_item.user_type == 0">
            <div class="row">
              <div class="input-field col s12 m12">
                <label for="document_type" class="active active_select"><span class="required">*</span> {{ $t('views.Selecciona el tipo de documento') }}</label>
                <select class="browser-default" id="document_type" v-model="data_item.document_type" :required="!is_document_upload">
                  <option value="0">{{ $t('views.DNI') }}</option>
                  <option value="5">{{ $t('views.TarjetaResidencia') }}</option>
                  <option value="3">{{ $t('views.PasaporteUE') }}</option>
                  <option value="4">{{ $t('views.PasaporteOutsideUE') }}</option>
                </select>
              </div>
            </div>
            <template v-for="(docs, type, index) in documents_person" v-bind:key="index">
              <template v-if="data_item.document_type==type">
                <template v-for="doc in docs" v-bind:key="doc">
                  <div class="row display-flex">
                    <div class="input-field col s12 m6">
                      <img :id="documents_controls[doc]['img']" :src="data_item[documents_controls[doc]['img']]" class="responsive-img">
                    </div>
                    <div class="input-field col s12 m6" >
                      <div class="mb-3"><span class="required">*</span> {{ $t(documents_controls[doc]['label']) }}</div>
                      <input :required="!is_document_upload" :id="documents_controls[doc]['file']" :name="documents_controls[doc]['file']" type="file" @change="handleImageUpload($event, data_item[documents_controls[doc]['img']],documents_controls[doc]['img'], doc)" accept="image/png, image/jpeg, image/gif" />
                    </div>
                  </div>
                </template>
              </template>
            </template>
          </template>
          <template v-if="data_item.user_type == 1">
            <div class="row">
              <div class="col s12">
                <p class="bold">{{ $t('views.Documentos sobre el representante/administrador o directivo') }}</p>
              </div>
            </div>
            <div class="row">
              <div class="input-field col s12 m12">
                <label for="document_type" class="active active_select"><span class="required">*</span> {{ $t('views.Selecciona el tipo de documento representante') }}</label>
                <select class="browser-default" v-model="data_item.document_representative_type" :required="!is_document_representative_upload">
                  <option value="0">{{ $t('views.DNI') }}</option>
                  <option value="5">{{ $t('views.TarjetaResidencia') }}</option>
                  <option value="3">{{ $t('views.PasaporteUE') }}</option>
                </select>
              </div>
            </div>
            <template v-for="(docs, type, index) in documents_representative" v-bind:key="index">
              <template v-if="data_item.document_representative_type===type">
                <template v-for="doc in docs" v-bind:key="doc">
                  <div class="row display-flex">
                    <div class="input-field col s12 m6">
                      <img :id="documents_controls[doc]['img']" :src="data_item[documents_controls[doc]['img']]" class="responsive-img">
                    </div>
                    <div class="input-field col s12 m6" >
                      <div class="mb-3"><span class="required">*</span> {{ $t(documents_controls[doc]['label']) }}</div>
                      <input :id="documents_controls[doc]['file']" :name="documents_controls[doc]['file']" type="file" :required="!is_document_representative_upload" @change="handleImageUpload($event, data_item[documents_controls[doc]['img']],documents_controls[doc]['img'], doc)" accept="image/png, image/jpeg, image/gif"/>
                    </div>
                  </div>
                </template>
              </template>
            </template>


            <div class="row">
              <div class="col s12">
                <p class="bold">{{ $t('views.Documentos de los beneficiarios') }}</p>
              </div>
            </div>
            <template v-for="owner in legal_holders" :key="owner.ind">
              <div class="row">
                <div class="input-field col s12 m12">
                  <label for="document_type" class="active active_select"><span class="required">*</span> {{ $t('views.Selecciona el tipo de documento del beneficiario') }}</label>
                  <select class="browser-default" v-model="data_item['document_holder_type_' + owner.ind]" :required="!is_document_holder_upload[owner.ind]">
                    <option value="0">{{ $t('views.DNI') }}</option>
                    <option value="5">{{ $t('views.TarjetaResidencia') }}</option>
                    <option value="3">{{ $t('views.PasaporteUE') }}</option>
                  </select>
                </div>
              </div>
              <template v-for="(docs, type, index) in documents_holders[owner.ind]" v-bind:key="index">
                <template v-if="data_item['document_holder_type_' + owner.ind]==type">
                  <template v-for="doc in docs" v-bind:key="doc">

                    <div class="row display-flex">
                      <div class="input-field col s12 m6">
                        <img :id="documents_controls[doc]['img']" :src="data_item[documents_controls[doc]['img']]" class="responsive-img">
                      </div>
                      <div class="input-field col s12 m6" >
                        <div class="mb-3"><span class="required">*</span> {{ $t(documents_controls[doc]['label']) }}</div>
                        <input :id="documents_controls[doc]['file']" :name="documents_controls[doc]['file']" type="file" :required="!is_document_holder_upload[owner.ind]" @change="handleImageUpload($event, data_item[documents_controls[doc]['img']],documents_controls[doc]['img'], doc)" accept="image/png, image/jpeg, image/gif"/>
                      </div>
                    </div>
                  </template>
                </template>
              </template>
            </template>
            <hr style="border: 1px solid #e5e5e5;"/>
            <div class="row">
              <div class="col s12">
                <p class="bold">{{ $t('views.Documentos de la persona jurídica') }}</p>
              </div>
            </div>
            <template v-for="(doc, ind) in documents_company" v-bind:key="doc">
              <div class="row display-flex">
                <div class="input-field col s12 m6">
                  <img :id="documents_controls[doc]['img']" :src="data_item[documents_controls[doc]['img']]" class="responsive-img">
                </div>
                <div class="input-field col s12 m6" >
                  <div class="mb-3"><span class="required">*</span> {{ $t(documents_controls[doc]['label']) }}</div>
                  <input :id="documents_controls[doc]['file']" :name="documents_controls[doc]['file']" type="file" :required="!is_document_company_upload[ind]" @change="handleImageUpload($event, data_item[documents_controls[doc]['img']], documents_controls[doc]['img'], doc)" accept="image/png, image/jpeg, image/gif, application/pdf"/>
                </div>
              </div>
            </template>
          </template>



          <div v-if="loading" class="progress">
            <div class="indeterminate"></div>
          </div>
          <div v-if="is_kyc" class="mt-3 text-right">
            <button class="btn-primary mr-3" type="button" @click="changeStep(1)">{{ $t('views.Anterior') }}</button>
            <button class="btn-primary" type="submit">{{ $t('views.Siguiente') }}</button>
          </div>

        </fieldset>
      </form>
    </div>
  </div>
</template>
<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import {
  FILE_TYPE_ARTICLES_OF_ASSOCIATION,
  FILE_TYPE_CERTIFICATE_OF_INCORPORATION,
  FILE_TYPE_DEEPS_OF_INCORPORATION,
  FILE_TYPE_DNI_BACK,
  FILE_TYPE_DNI_FRONT,
  FILE_TYPE_DRIVE_LICENSE_BACK,
  FILE_TYPE_DRIVE_LICENSE_FRONT,
  FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_BACK,
  FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_FRONT,
  FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_BACK,
  FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_FRONT,
  FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_BACK,
  FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_FRONT,
  FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_BACK,
  FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_FRONT,
  FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_BACK,
  FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_FRONT,
  FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_BACK,
  FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_FRONT,
  FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_BACK,
  FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_FRONT,
  FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_BACK,
  FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_FRONT,
  FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_BACK,
  FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_FRONT,
  FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_BACK,
  FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_BACK, FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_FRONT,
  FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_BACK,
  FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_FRONT,
  FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_BACK,
  FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_FRONT,
  FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_BACK,
  FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_FRONT,
  FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_BACK,
  FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_FRONT,
  FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_BACK,
  FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_FRONT,
  FILE_TYPE_PASSPORT_EU_BACK,
  FILE_TYPE_PASSPORT_EU_FRONT,
  FILE_TYPE_PASSPORT_OUTSIDE_EU_FRONT,
  FILE_TYPE_RESIDENCE_CARD_BACK,
  FILE_TYPE_RESIDENCE_CARD_FRONT,
} from "@/const";
import JQuery from "jquery";
import {closeAlertProgress, navigateToFormStep, showAlert, showAlertError, showAlertProgress} from "@/functions";
import UserServices from "@/services/UserServices";
import store from "@/store";


@Options({
  props: {
    data_item: Object,
    is_kyc: Boolean,
    on_saved: Function,
  }
})
export default class ProfileDocuments extends Vue {

  data_item
  is_kyc
  on_saved: (() => void) | undefined

  loading = false
  data_images: any = {}
  is_document_upload = false
  is_document_representative_upload = false
  is_document_holder_upload = []
  is_document_company_upload = []
  legal_holders = []

  documents_controls = {}
  documents_person = {
    0: [FILE_TYPE_DNI_FRONT, FILE_TYPE_DNI_BACK],
    11: [FILE_TYPE_DRIVE_LICENSE_FRONT, FILE_TYPE_DRIVE_LICENSE_BACK],
    5: [FILE_TYPE_RESIDENCE_CARD_FRONT, FILE_TYPE_RESIDENCE_CARD_BACK],
    3: [FILE_TYPE_PASSPORT_EU_FRONT, FILE_TYPE_PASSPORT_EU_BACK],
    4: [FILE_TYPE_PASSPORT_OUTSIDE_EU_FRONT]
  }

  documents_company = [
    FILE_TYPE_CERTIFICATE_OF_INCORPORATION,
    FILE_TYPE_DEEPS_OF_INCORPORATION,
    FILE_TYPE_ARTICLES_OF_ASSOCIATION
  ]

  documents_representative = {
    0: [FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_FRONT, FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_BACK],
    11: [FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_FRONT, FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_BACK],
    5: [FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_FRONT, FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_BACK],
    3: [FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_FRONT, FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_BACK]
  }

  documents_holders = {
    14: {
      0: [FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_BACK],
      11: [FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_BACK],
      5: [FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_BACK],
      3: [FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_BACK]
    },
    15: {
      0: [FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_BACK],
      11: [FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_BACK],
      5: [FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_BACK],
      3: [FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_BACK]
    },
    16: {
      0: [FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_BACK],
      11: [FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_BACK],
      5: [FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_BACK],
      3: [FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_FRONT, FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_BACK]
    }
  }

  mounted(){
    if (this.data_item.kyc_valid == 1 || this.data_item.kyc_valid == 2) {
      JQuery('#fieldset').prop('disabled', true)
    }

    //lista de documentos
    if (this.data_item.list_documents != null){
      let documents_controls_keys = Object.keys(this.documents_controls)

      for (let i = 0; i < this.data_item.list_documents.length; i++){
        let doc = this.data_item.list_documents[i]
        if (documents_controls_keys.includes(doc.file_type.toString())) {
          this.data_item[this.documents_controls[doc.file_type]['img']] = 'data:image/png;base64, ' + doc.file;
          this.data_item[this.documents_controls[doc.file_type]['file']] = null;
          this.data_item.document_representative_type = this.documents_controls[doc.file_type]['document_representative_type']
        }
      }
    }

    this.legal_holders = []
    let num_holders = this.data_item.holders
    if (this.data_item.is_representative_owner) {
      num_holders = num_holders - 1
    }
    for(let i = 0; i < num_holders; i++){
      this.legal_holders.push({ind: i + 14, "name":"name"})
    }

    if (this.data_item.kyc_valid == 0 || (this.data_item.kyc_valid > 2)) {
      this.is_document_upload = false
      this.is_document_representative_upload = false
      for(let i = 0; i < num_holders; i++){
        this.is_document_holder_upload[i + 14] = false
      }
      this.is_document_company_upload[0] = false
      this.is_document_company_upload[1] = false
      this.is_document_company_upload[2] = false
    }

    this.changeDocumentType()
  }
  changeStep(step) {
    navigateToFormStep(step)
  }

  async handleImageUpload( event, data_item_field, input_id, upload_file_type){
    data_item_field = event.target.files[0];
    if (data_item_field) {
      const toBase64 = file => new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
      });
      this.data_images[upload_file_type] = await toBase64(data_item_field)
      const file_img = document.getElementById(input_id)
      if (data_item_field.type == "application/pdf") {
        const image = await UserServices.getImageFromPdf(data_item_field)
        if (file_img != null) (file_img as HTMLInputElement).src = 'data:image/png;base64, ' + image.data
      } else {
        if (file_img != null) (file_img as HTMLInputElement).src = URL.createObjectURL(data_item_field)
      }
    }
  }



  updateImages(){
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this

    showAlertProgress(this)
    this.loading = true
    UserServices.uploadKYCImages(this.data_images)
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        .then(response => {
          self.loading = false
          if (self.on_saved) {
            self.on_saved()
          } else {
            navigateToFormStep(4);
          }
        })
        .catch(function (error) {
          closeAlertProgress(self)
          showAlertError(error, self)
          self.loading = false
        });
  }



  changeDocumentType() {
    try {
      if (this.data_item.file_dni_front_img || this.data_item.file_dni_back_img) {
        this.data_item.document_type = 0;
      } else if (this.data_item.file_drive_license_front_img || this.data_item.file_drive_license_back_img) {
        this.data_item.document_type = 11;
      } else if (this.data_item.file_residence_card_front_img || this.data_item.file_residence_card_back_img) {
        this.data_item.document_type = 5;
      } else if (this.data_item.file_passport_eu_front_img || this.data_item.file_passport_eu_back_img) {
        this.data_item.document_type = 3;
      }

      if (this.data_item.file_dni_front_img && this.data_item.file_dni_back_img) {
        this.data_item.document_type = 0;
        this.is_document_upload = true;
      } else if (this.data_item.file_drive_license_front_img && this.data_item.file_drive_license_back_img) {
        this.data_item.document_type = 11;
        this.is_document_upload = true;
      } else if (this.data_item.file_residence_card_front_img && this.data_item.file_residence_card_back_img) {
        this.data_item.document_type = 5;
        this.is_document_upload = true;
      } else if (this.data_item.file_passport_eu_front_img && this.data_item.file_passport_eu_back_img) {
        this.data_item.document_type = 3;
        this.is_document_upload = true;
      } else if (this.data_item.file_passport_outside_eu_front_img) {
        this.data_item.document_type = 4;
        this.is_document_upload = true;
      }

      for (let ind_doc of Object.keys(this.documents_representative)) {
        // console.log("ind_doc", ind_doc)
        let images_uploaded = true;
        for (let doc_type of this.documents_representative[ind_doc]) {
          // console.log("doc_type", doc_type)
          const data = this.data_item[this.documents_controls[doc_type]['img']]
          // console.log("data", data)
          if (!data) {
            // console.log("NO data")
            images_uploaded = false;
            break;
          } else {
            this.data_item.document_representative_type = ind_doc;
          }
        }
        if (images_uploaded) {

          this.is_document_representative_upload = true;
          break;
        }
      }
    } catch (e) {
      console.log("error", e)
    }
  }


  beforeMount() {

    this.documents_controls[FILE_TYPE_DNI_FRONT] = {
      img: 'file_dni_front_img',
      file: 'file_dni_front',
      document_type: 0,
      label: 'views.DNI Cara A'
    }
    this.documents_controls[FILE_TYPE_DNI_BACK] = {
      img: 'file_dni_back_img',
      file: 'file_dni_back',
      document_type: 0,
      label: 'views.DNI Cara B'
    }
    this.documents_controls[FILE_TYPE_DRIVE_LICENSE_FRONT] = {
      img: 'file_drive_license_front_img',
      file: 'file_drive_license_front',
      document_type: 11,
      label: 'views.CarnetConducir Cara A'
    }
    this.documents_controls[FILE_TYPE_DRIVE_LICENSE_BACK] = {
      img: 'file_drive_license_back_img',
      file: 'file_drive_license_back',
      document_type: 11,
      label: 'views.CarnetConducir Cara B'
    }
    this.documents_controls[FILE_TYPE_RESIDENCE_CARD_FRONT] = {
      img: 'file_residence_card_front_img',
      file: 'file_residence_card_front',
      document_type: 5,
      label: 'views.TarjetaResidencia Cara A'
    }
    this.documents_controls[FILE_TYPE_RESIDENCE_CARD_BACK] = {
      img: 'file_residence_card_back_img',
      file: 'file_residence_card_back',
      document_type: 5,
      label: 'views.TarjetaResidencia Cara B'
    }
    this.documents_controls[FILE_TYPE_PASSPORT_EU_FRONT] = {
      img: 'file_passport_eu_front_img',
      file: 'file_passport_eu_front',
      document_type: 3,
      label: 'views.PasaporteUE Cara A'
    }
    this.documents_controls[FILE_TYPE_PASSPORT_EU_BACK] = {
      img: 'file_passport_eu_back_img',
      file: 'file_passport_eu_back',
      document_type: 3,
      label: 'views.PasaporteUE Cara B'
    }
    this.documents_controls[FILE_TYPE_PASSPORT_OUTSIDE_EU_FRONT] = {
      img: 'file_passport_outside_eu_front_img',
      file: 'file_passport_outside_eu_front',
      document_type: 4,
      label: 'views.PasaporteOutsideUE Cara A'

    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_FRONT] = {
      img: 'file_dni_representative_front_img',
      file: 'file_dni_representative_front',
      document_representative_type: 0,
      label: 'views.DNI Cara A'
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DNI_BACK] = {
      img: 'file_dni_representative_back_img',
      file: 'file_dni_representative_back',
      document_representative_type: 0,
      label: 'views.DNI Cara A'
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_FRONT] = {
      img: 'file_drive_license_representative_front_img',
      file: 'file_drive_license_representative_front',
      document_representative_type: 11,
      label: 'views.CarnetConducir Cara A'
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_DRIVE_LICENSE_BACK] = {
      img: 'file_drive_license_representative_back_img',
      file: 'file_drive_license_representative_back',
      document_representative_type: 11,
      label: 'views.CarnetConducir Cara B'
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_FRONT] = {
      img: 'file_residence_card_representative_front_img',
      file: 'file_residence_card_representative_front',
      document_representative_type: 5,
      label: 'views.TarjetaResidencia Cara A'
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_RESIDENCE_CARD_BACK] = {
      img: 'file_residence_card_representative_back_img',
      file: 'file_residence_card_representative_back',
      document_representative_type: 5,
      label: 'views.TarjetaResidencia Cara B'
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_FRONT] = {
      img: 'file_passport_eu_representative_front_img',
      file: 'file_passport_eu_representative_front',
      document_representative_type: 3,
      label: 'views.PasaporteUE Cara A'
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_REPRESENTATIVE_PASSPORT_EU_BACK] = {
      img: 'file_passport_eu_representative_back_img',
      file: 'file_passport_eu_representative_back',
      document_representative_type: 3,
      label: 'views.PasaporteUE Cara B'
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_FRONT] = {
      img: 'file_dni_holder_1_front_img',
      file: 'file_dni_holder_1_front',
      document_holder_type_1: 0,
      label: 'views.DNI Cara A',
      document_type: 14
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_1_DNI_BACK] = {
      img: 'file_dni_holder_1_back_img',
      file: 'file_dni_holder_1_back',
      document_holder_type_1: 0,
      label: 'views.DNI Cara A',
      document_type: 14
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_FRONT] = {
      img: 'file_drive_license_holder_1_front_img',
      file: 'file_drive_license_holder_1_front',
      document_holder_type_1: 11,
      label: 'views.CarnetConducir Cara A',
      document_type: 14
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_1_DRIVE_LICENSE_BACK] = {
      img: 'file_drive_license_holder_1_back_img',
      file: 'file_drive_license_holder_1_back',
      document_holder_type_1: 11,
      label: 'views.CarnetConducir Cara B',
      document_type: 14
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_FRONT] = {
      img: 'file_residence_card_holder_1_front_img',
      file: 'file_residence_card_holder_1_front',
      document_holder_type_1: 5,
      label: 'views.TarjetaResidencia Cara A',
      document_type: 14
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_1_RESIDENCE_CARD_BACK] = {
      img: 'file_residence_card_holder_1_back_img',
      file: 'file_residence_card_holder_1_back',
      document_holder_type_1: 5,
      label: 'views.TarjetaResidencia Cara B',
      document_type: 14
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_FRONT] = {
      img: 'file_passport_eu_holder_1_front_img',
      file: 'file_passport_eu_holder_1_front',
      document_holder_type_1: 3,
      label: 'views.PasaporteUE Cara A',
      document_type: 14
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_1_PASSPORT_EU_BACK] = {
      img: 'file_passport_eu_holder_1_back_img',
      file: 'file_passport_eu_holder_1_back',
      document_holder_type_1: 3,
      label: 'views.PasaporteUE Cara B',
      document_type: 14
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_FRONT] = {
      img: 'file_dni_holder_2_front_img',
      file: 'file_dni_holder_2_front',
      document_holder_type_2: 0,
      label: 'views.DNI Cara A',
      document_type: 15
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_2_DNI_BACK] = {
      img: 'file_dni_holder_2_back_img',
      file: 'file_dni_holder_2_back',
      document_holder_type_2: 0,
      label: 'views.DNI Cara A',
      document_type: 15
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_FRONT] = {
      img: 'file_drive_license_holder_2_front_img',
      file: 'file_drive_license_holder_2_front',
      document_holder_type_2: 11,
      label: 'views.CarnetConducir Cara A',
      document_type: 15
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_2_DRIVE_LICENSE_BACK] = {
      img: 'file_drive_license_holder_2_back_img',
      file: 'file_drive_license_holder_2_back',
      document_holder_type_2: 11,
      label: 'views.CarnetConducir Cara B',
      document_type: 15
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_FRONT] = {
      img: 'file_residence_card_holder_2_front_img',
      file: 'file_residence_card_holder_2_front',
      document_holder_type_2: 5,
      label: 'views.TarjetaResidencia Cara A',
      document_type: 15
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_2_RESIDENCE_CARD_BACK] = {
      img: 'file_residence_card_holder_2_back_img',
      file: 'file_residence_card_holder_2_back',
      document_holder_type_2: 5,
      label: 'views.TarjetaResidencia Cara B',
      document_type: 15
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_FRONT] = {
      img: 'file_passport_eu_holder_2_front_img',
      file: 'file_passport_eu_holder_2_front',
      document_holder_type_2: 3,
      label: 'views.PasaporteUE Cara A',
      document_type: 15
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_2_PASSPORT_EU_BACK] = {
      img: 'file_passport_eu_holder_2_back_img',
      file: 'file_passport_eu_holder_2_back',
      document_holder_type_2: 3,
      label: 'views.PasaporteUE Cara B',
      document_type: 15
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_FRONT] = {
      img: 'file_dni_holder_3_front_img',
      file: 'file_dni_holder_3_front',
      document_holder_type_3: 0,
      label: 'views.DNI Cara A',
      document_type: 16
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_3_DNI_BACK] = {
      img: 'file_dni_holder_3_back_img',
      file: 'file_dni_holder_3_back',
      document_holder_type_3: 0,
      label: 'views.DNI Cara A',
      document_type: 16
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_FRONT] = {
      img: 'file_drive_license_holder_3_front_img',
      file: 'file_drive_license_holder_3_front',
      document_holder_type_3: 11,
      label: 'views.CarnetConducir Cara A',
      document_type: 16
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_3_DRIVE_LICENSE_BACK] = {
      img: 'file_drive_license_holder_3_back_img',
      file: 'file_drive_license_holder_3_back',
      document_holder_type_3: 11,
      label: 'views.CarnetConducir Cara B',
      document_type: 16
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_FRONT] = {
      img: 'file_residence_card_holder_3_front_img',
      file: 'file_residence_card_holder_3_front',
      document_holder_type_3: 5,
      label: 'views.TarjetaResidencia Cara A',
      document_type: 16
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_3_RESIDENCE_CARD_BACK] = {
      img: 'file_residence_card_holder_3_back_img',
      file: 'file_residence_card_holder_3_back',
      document_holder_type_3: 5,
      label: 'views.TarjetaResidencia Cara B',
      document_type: 16
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_FRONT] = {
      img: 'file_passport_eu_holder_3_front_img',
      file: 'file_passport_eu_holder_3_front',
      document_holder_type_3: 3,
      label: 'views.PasaporteUE Cara A',
      document_type: 16
    }
    this.documents_controls[FILE_TYPE_LEGAL_PERSON_HOLDER_3_PASSPORT_EU_BACK] = {
      img: 'file_passport_eu_holder_3_back_img',
      file: 'file_passport_eu_holder_3_back',
      document_holder_type_3: 3,
      label: 'views.PasaporteUE Cara B',
      document_type: 16
    }
    this.documents_controls[FILE_TYPE_CERTIFICATE_OF_INCORPORATION] = {
      img: 'file_certificate_of_incorporation_img',
      file: 'file_certificate_of_incorporation',
      label: 'views.Certificado de empresa',
      document_type: 7
    }
    this.documents_controls[FILE_TYPE_ARTICLES_OF_ASSOCIATION] = {
      img: 'file_articles_of_association_img',
      file: 'file_articles_of_association',
      label: 'views.Escrituras de constitución',
      document_type: 12
    }
    this.documents_controls[FILE_TYPE_DEEPS_OF_INCORPORATION] = {
      img: 'file_deeps_of_incorporation_img',
      file: 'file_deeps_of_incorporation',
      label: 'views.Modelo 200 o Acta de titularidad real',
      document_type: 18
    }
  }
}
</script>
