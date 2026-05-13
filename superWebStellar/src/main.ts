import { createApp } from 'vue'
import App from "@/App.vue";
import router from "@/router";
import store from "@/store";

//https://medium.com/js-dojo/manage-vue-i18n-with-typescript-958b2f69846f
import { createI18n } from 'vue-i18n'
import {messages} from "@/locales/locales";

// materializeCss y estilos propios
import 'materialize-css/dist/css/materialize.css'
import 'materialize-css/dist/js/materialize.js'
import '@/style/helper.css'
import '@/style/mycss.css'
import '@/style/mycss_earastellar.css'
import '@/assets/fonts/fontawesome-5.11.2_all.css'
import '@/assets/fonts/MaterialIcons.css'
import {Locales} from "@/locales/locales";

//para las graficas de estadisticas
//https://apexcharts.com/vue-chart-demos/
import VueApexCharts from "vue3-apexcharts";


//miramos si se ha guardado en idioma sino cogemos el por defecto del navegador
let defaultLocale = ''
if (store.getters.getLocale == '' || store.getters.getLocale == undefined) {
    if (navigator.language == 'es-ES' || navigator.language == 'es') {
        defaultLocale = Locales.ES
        store.commit('LOCALE', Locales.ES)
    } else {
        defaultLocale = Locales.EN
        store.commit('LOCALE', Locales.EN)
    }
} else {
    defaultLocale = store.getters.getLocale
}
const i18n = createI18n({
    messages,
    locale: defaultLocale,
    warnHtmlInMessage: 'off' // disable of the Detected HTML in message
});

createApp(App)
    .use(store)
    .use(router)
    .use(i18n)
    .use(VueApexCharts)
    .mount('#app')
