import { createStore } from 'vuex'
import createPersistedState from "vuex-persistedstate";

export default createStore({
  plugins: [createPersistedState({ key: 'earastellar' })],
  state: {
    token: '',
    token_refresh: '',
    user_id: '',
    expiration: 0,
    url_img_profile: '',
    current_wallet: '',
    locale: '',
    kyc_valid: false,
    blockchain_op_progress: {
      op: '',
      progress: true,
      title: "",
      step: 0,
      message: "blockchainDialog.confirmTransaction"
    },
  },
  mutations: {
    AUTH_SUCCESS(state, data) {
      state.token = data.access_token
      state.token_refresh = data.refresh_access_token
      state.user_id = data.user_id
      state.expiration = data.expiration
      state.url_img_profile = data.file_profile
    },
    AUTH_LOGOUT(state) {
      state.token = ''
      state.token_refresh = ''
      state.user_id = ''
      state.expiration = 0
      state.url_img_profile = ''
    },
    UPDATE_IMG_PROFILE(state, file_profile) {
      state.url_img_profile = file_profile
    },
    ADDRESS_CHANGED(state, data) {
      state.current_wallet = data
    },
    LOCALE(state, locale) {
      state.locale = locale
    },
    BLOCKCHAIN_OP_PROGRESS(state, data) {
      state.blockchain_op_progress = data
    },
    KYC_VALID(state, data) {
      state.kyc_valid = data
    }

  },
  getters: {
    isLoggedIn: state => !!state.token && state.expiration > Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), new Date().getUTCDate(), new Date().getUTCHours(), new Date().getUTCMinutes(), new Date().getUTCSeconds(), new Date().getUTCMilliseconds()),
    getKYCValid: state => state.kyc_valid,
    getUrlImgProfile: state => state.url_img_profile,
    getCurrentWallet: state => state.current_wallet,
    getLocale: state => state.locale,
    getBlockchainOpProgress: state => state.blockchain_op_progress,
    getUserId: state => state.user_id,
  },
  actions: {
  },
  modules: {
  }
})
