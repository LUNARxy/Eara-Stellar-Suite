import axios, {AxiosRequestConfig, InternalAxiosRequestConfig} from "axios";
import store from "../store";
const access_token_refresh = 'v1/public/login/access_token_refresh'


export const PUBLIC_URL = process.env.VUE_APP_WHITE_LABEL_URL;
const baseURL= process.env.VUE_APP_BASEURL;
const headers = {
    "Content-type": "application/json"
}


const http = axios.create({
    baseURL: baseURL,
    headers: headers
})

http.interceptors.request.use(
    function (config: InternalAxiosRequestConfig) {
        if (!config) {
            config = {data: undefined, headers: undefined};
        }
        if (!config.headers) {
            config.headers = new axios.AxiosHeaders();
        }
        // Configura el tipo de contenido como form-urlencoded para que no vaya como json
        config.headers.set('Content-Type', 'application/x-www-form-urlencoded');

        // Do something before request is sent
        if (config.url === access_token_refresh) {
            config.headers.Authorization = 'Bearer ' + store.state.token_refresh;
        } else {
            config.headers.Authorization = 'Bearer ' + store.state.token;
        }
        config.headers['white-label-access-key'] = 'earastellar';
        return config;
    }, function (error) {
        // Do something with request error
        return Promise.reject(error);
    });

http.interceptors.response.use(
    (response) => {
        // Any status code that lie within the range of 2xx cause this function to trigger
        // Do something with response data
        return response
    },
    (err) => {
        // Any status codes that falls outside the range of 2xx cause this function to trigger
        // Do something with response error
        // return other errors
        // console.log(err)
        if (err.response.status !== 401) {
            return new Promise((resolve, reject) => {
                reject(err)
            })
        }
        // error on refresh
        if (err.response.config.url === access_token_refresh) {
            if (process.env.VUE_APP_WHITE_LABEL_IS_DEVELOPMENT !== "true"){
                window.location.href = "/Logout";
            } else {
                window.location.href = '/earastellaradmin/Logout';
            }
            return new Promise((resolve, reject) => {
                reject(err)
            })
        }
        // refresh
        return http.get(access_token_refresh, { headers }).then(
            response => {
                const config = err.response.config
                config.headers.Authorization = 'Bearer ' + response.data.access_token
                store.commit('AUTH_SUCCESS', response.data)
                return http(config)
            }
        )
    }
)

export default http
