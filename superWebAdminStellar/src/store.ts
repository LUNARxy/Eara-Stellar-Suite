import { createStore } from 'vuex'
import createPersistedState from "vuex-persistedstate";

export default createStore({
  plugins: [createPersistedState({key: 'earastellar_admin'})],
  state: {
    token: '',
    token_refresh: '',
    current_wallet: '',
    expiration: 0,
  },
  mutations: {
    AUTH_SUCCESS(state, data) {
      state.token = data.access_token
      state.token_refresh = data.refresh_access_token
      state.expiration = data.expiration
    },
    AUTH_LOGOUT(state) {
      state.token = ''
      state.token_refresh = ''
      state.expiration = 0
    },
    ADDRESS_CHANGED(state, data) {
      state.current_wallet = data
    },

  },
  getters: {
    isLoggedIn: state => !!state.token && state.expiration > Date.UTC(new Date().getUTCFullYear(),new Date().getUTCMonth(), new Date().getUTCDate(), new Date().getUTCHours(), new Date().getUTCMinutes(), new Date().getUTCSeconds(), new Date().getUTCMilliseconds()),
    getCurrentWallet: state => state.current_wallet,
  },
  actions: {
  },
  modules: {
  }
})
