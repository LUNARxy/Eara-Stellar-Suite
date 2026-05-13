import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import store from "./store";


let routes: Array<RouteRecordRaw> = []

routes = []

//RUTAS GENERALES
routes.push(
    {path:'/',name:'HomeView',component:()=>import('./views/HomeView.vue')},
    {path:'/home',name:'HomeView',component:()=>import('./views/HomeView.vue')},
    {path: "/:pathMatch(.*)*",name:'HomeView',component:()=>import('./views/HomeView.vue')},

    {path:'/login',name:'LoginView',component:()=>import('./views/LoginView.vue'),meta:{login:true}},
    {path:'/logout',name:'Logout',component:()=>null,meta:{logout:true}},

    {path:'/InvestProjectsList/:category_name',name:'InvestProjectsListView',component:()=>import('./views/InvestProjectsListView.vue')},
    {path:'/InvestProjects/:category_name/:id',name:'InvestProjectsView',component:()=>import('./views/InvestProjectsView.vue')},
    {path:'/InvestProjectsFormNew/:category_name',name:'InvestProjectsFormNewView',component:()=>import('./views/InvestProjectsFormView.vue')},
    {path:'/InvestProjectsForm/:category_name/:id',name:'InvestProjectsFormView',component:()=>import('./views/InvestProjectsFormView.vue')},
    {path:'/InvestProjectsDetail/:category_name/:id',name:'InvestProjectsDetailView',component:()=>import('./views/InvestProjectsDetailView.vue')},
    {path:'/InvestGalleryList/:category_name/:invest_id',name:'InvestGalleryListView',component:()=>import('./views/InvestGalleryListView.vue')},
    {path:'/InvestDocumentsList/:category_name/:invest_id',name:'InvestDocumentsListView',component:()=>import('./views/InvestDocumentsListView.vue')},
    {path:'/InvestNewsList/:category_name/:invest_id',name:'InvestNewsListView',component:()=>import('./views/InvestNewsListView.vue')},
    {path:'/InvestTeamList/:category_name/:invest_id',name:'InvestTeamListView',component:()=>import('./views/InvestTeamListView.vue')},
    {path:'/InvestQuestionsList/:category_name/:invest_id',name:'InvestQuestionsListView',component:()=>import('./views/InvestQuestionsListView.vue')},
    {path:'/InvestStatusList/:category_name/:invest_id',name:'InvestStatusListView',component:()=>import('./views/InvestStatusListView.vue')},
    {path:'/InvestPromoterContributionsList/:category_name/:invest_id',name:'InvestPromoterContributionsListView',component:()=>import('./views/InvestPromoterContributionsListView.vue')},
    {path:'/InvestPhasesMintList/:category_name/:invest_id',name:'InvestPhasesMintListView',component:()=>import('./views/InvestPhasesMintListView.vue')},
    {path:'/InvestProjectsUserInvestList/:category_name/:invest_id',name:'InvestProjectsUserInvestListView',component:()=>import('./views/InvestProjectsUserInvestListView.vue')},
    {path:'/InvestProjectsUserGroupInvestList/:category_name/:invest_id',name:'InvestProjectsUserGroupInvestListView',component:()=>import('./views/InvestProjectsUserGroupInvestListView.vue')},
    {path:'/InvestProjectsUserRefundList/:type/:category_name/:invest_id',name:'InvestProjectsUserRefundListView',component:()=>import('./views/InvestProjectsUserRefundListView.vue')},
    {path:'/InvestProjectsUserWhitelistList/:category_name/:invest_id',name:'InvestProjectsUserWhitelistListView',component:()=>import('./views/InvestProjectsUserWhitelistListView.vue')},
    {path:'/InvestProfitsList/:category_name/:invest_id',name:'InvestProfitsListView',component:()=>import('./views/InvestProfitsListView.vue')},
    {path:'/InvestCompletedList/:category_name/:invest_id',name:'InvestCompletedListView',component:()=>import('./views/InvestCompletedListView.vue')},

    {path:'/userActivity',name:'UserHistoryTokens',component:()=>import('./views/UserHistoryTokensView.vue')},
    {path:'/UsersList',name:'UsersListView',component:()=>import('./views/UsersListView.vue')},
    {path:'/UserFormNew',name:'UserFormNewView',component:()=>import('./views/UserFormView.vue')},
    {path:'/UserDetail/:id',name:'UserDetailView',component:()=>import('./views/UserDetailView.vue')},

    {path:'/governor',name:'governor',component:()=>import('./views/GovernorView.vue')},

)

const router = createRouter({
  history: createWebHistory(process.env.VUE_APP_WHITE_LABEL_IS_DEVELOPMENT==="true"?'earastellaradmin/':''),
  routes,
  //https://router.vuejs.org/guide/advanced/scroll-behavior.html
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      //para las anclas en la web
      return { el: to.hash, top: 100 }
    } else  if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})



router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.login)) {
    if (!store.getters.isLoggedIn){
      next()
    } else {
      next({ path: '/' })
    }
  } else if (to.matched.some(record => record.meta.logout)) {
    store.commit('AUTH_LOGOUT')
    next({
      path: '/login',
    })
  } else {
    if (!store.getters.isLoggedIn){
      next({
        path: '/login',
      })
    } else {
      next()
    }
  }
})

export default router
