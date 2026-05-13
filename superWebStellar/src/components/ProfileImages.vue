<template>
  <div class="col s12 m4">
    <div class="col s12 p-0 m-0">
      <div class="col s12 text-center pr-0 pl-0">
        <div class="card border-radius-15 mt-0">
          <div class="card-image">
            <div class="image-upload">
              <label for="file-input-top">
                <img id="file_top_img" :src="data_item.file_top_img" class="responsive-img"  style="border-top-left-radius: 15px; border-top-right-radius: 15px" alt="cabecera">
                <span class="edit"><i class="material-icons prefix pt-2">edit</i></span>
              </label>
              <input id="file-input-top" type="file" @change="handleFileUploadTop( $event )"/>
            </div>
          </div>
          <div class="col s12 circle-profile-top-artist">
            <div class="row">
              <div class="col s12 text-center">
                <div class="image-upload">
                  <label for="file-input">
                    <img id="file_profile_img" class="z-depth-5 circle circle-profile circle-profile-artist" :src="data_item.file_profile_img" alt="perfil"/>
                    <span class="edit_profile"><i class="material-icons prefix pt-2">edit</i></span>
                  </label>
                  <input id="file-input" type="file" @change="handleFileUploadProfile( $event )"/>
                </div>
              </div>
            </div>
          </div>

          <div class="row card-content">
            <ProfileKYC :data_item="data_item"/>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>
<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import ProfileKyc from "@/components/ProfileKYC.vue";
import UserServices from "@/services/UserServices";
import {FILE_TYPE_PROFILE, FILE_TYPE_PROFILE_TOP} from "@/const";
import {funcGetImgUrl, showAlert, showAlertError} from "@/functions";
import store from "@/store";
import {PUBLIC_URL} from "@/services/Http-common";

@Options({
  components: {ProfileKYC: ProfileKyc},
  props: {
    data_item: Object
  }
})
export default class ProfileImages extends Vue {
  data_item

  mounted(){
    if (this.data_item.file_top === null) {
      this.data_item.file_top_img = this.getImgUrl('profile_top_default.jpg')
    } else {
      this.data_item.file_top_img = PUBLIC_URL + this.data_item.file_top;
    }
    this.data_item.file_top = null;

    if (this.data_item.file_profile === null) {
      //this.data_item.file_profile_img = require("@/assets/img/avatar_default.jpg")
      this.data_item.file_profile_img = this.getImgUrl('avatar_default.jpg')
    } else {
      this.data_item.file_profile_img = PUBLIC_URL + this.data_item.file_profile;
    }
    this.data_item.file_profile = null;
  }

  handleFileUploadTop( event ){
    this.data_item.file_top = event.target.files[0];
    if (this.data_item.file_top) {
      const file_top_img = document.getElementById('file_top_img')
      if (file_top_img != null) (file_top_img as HTMLInputElement).src = URL.createObjectURL(this.data_item.file_top)

      // eslint-disable-next-line @typescript-eslint/no-this-alias
      const self = this
      UserServices.updateUserFile(this.data_item.file_top, FILE_TYPE_PROFILE_TOP)
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          .then(response => {
            showAlert("",this.$t('views.Se ha guardado correctamente'))
          })
          .catch(function (error) {
            showAlertError(error, self)
          });
    }
  }

  handleFileUploadProfile( event ){
    this.data_item.file_profile = event.target.files[0];
    if (this.data_item.file_profile) {
      const file_profile_img = document.getElementById('file_profile_img')
      if (file_profile_img != null) (file_profile_img as HTMLInputElement).src = URL.createObjectURL(this.data_item.file_profile)

      // eslint-disable-next-line @typescript-eslint/no-this-alias
      const self = this
      UserServices.updateUserFile(this.data_item.file_profile, FILE_TYPE_PROFILE)
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          .then(response => {
            showAlert("",this.$t('views.Se ha guardado correctamente'))
            store.commit('UPDATE_IMG_PROFILE', response.data.file_profile)
          })
          .catch(function (error) {
            showAlertError(error, self)
          });
    }
  }

  getImgUrl(pic) {
    return funcGetImgUrl(pic)
  }
}
</script>
<style>
.image-upload>input {
  display: none;
  position: relative;
  cursor: pointer;
}
.image-upload:hover .edit, .image-upload:hover .edit_profile {
  display: block;
}
.edit_profile {
  padding-top: 7px;
  padding-right: 7px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: none;
}
.edit {
  padding-top: 7px;
  padding-right: 7px;
  position: absolute;
  right: 0;
  top: 0;
  display: none;
}
</style>