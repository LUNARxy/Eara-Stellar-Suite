import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import store from "@/store";

console.log("router")
let routes: Array<RouteRecordRaw> = []

routes = []

routes.push(
    { path: '/', name: 'HomeView', component: () => import('./views/dashboard/DashboardView.vue')},
    { path: '/dashboard', name: 'dashboard', component: () => import('./views/dashboard/DashboardView.vue')},
    { path: "/:pathMatch(.*)*", name: 'HomeView', component: () => import('./views/dashboard/DashboardView.vue')},
    { path: '/portfolio', name: 'portfolio', component: () => import('./views/dashboard/PortfolioView.vue')},
    { path: '/userDetail', name: 'UserDetail', component: () => import('./views/dashboard/UserDetailView.vue')},
    { path: '/login/:go_back*', name: 'LoginView', component: () => import('./views/LoginView.vue'), meta: { guest: true } },
    { path: '/login/:email', name: 'LoginEmailView', component: () => import('./views/LoginView.vue'), meta: { guest: true } },
    { path: '/logout', name: 'Logout', component: () => null, meta: { logout: true } },
    { path: '/activity', name: 'Activity', component: () => import('./views/dashboard/ActivityView.vue')},
    { path: '/follow', name: 'follow', component: () => import('./views/dashboard/FollowsView.vue')},
    { path: '/debt', name: 'DebtView', component: () => import('./views/ProjectsView.vue')},
    { path: '/debt/:slug', name: 'DebtDetailView', component: () => import('./views/InvestDetailView.vue')},
    { path: '/debt-financing-phase-list', name: 'DebtFinancingPhaseListView', component: () => import('./views/InvestFinancingPhaseListView.vue')},
    { path: '/debt-next-launch-list', name: 'DebtNextLaunchListView', component: () => import('./views/InvestNextLaunchListView.vue')},
    { path: '/debt-in-progress-list', name: 'DebtInProgressListView', component: () => import('./views/InvestInProgressListView.vue')},
    { path: '/debt-completed-list', name: 'DebtCompletedListView', component: () => import('./views/InvestCompletedListView.vue')},
    { path: '/register', name: 'RegisterView', component: () => import('./views/RegisterView.vue'), meta: { guest: true } },
    { path: '/payment/:id/:slug', name: 'PaymentView', component: () => import('./views/dashboard/PaymentView.vue')},
    { path: '/userKYC', name: 'UserKYC', component: () => import('./views/dashboard/UserKYCView.vue')},
    { path: '/wallet', name: 'WalletView', component: () => import('./views/dashboard/WalletBlockchainView.vue')},
    { path: '/whitelist', name: 'whitelist', component: () => import('./views/dashboard/WhitelistView.vue')},
)


const router = createRouter({
  history: createWebHistory(process.env.VUE_APP_WHITE_LABEL_IS_DEVELOPMENT === "true" ? ('earastellar' + 'app/') : ''),
  routes,
  //https://router.vuejs.org/guide/advanced/scroll-behavior.html
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      //para las anclas en la web
      return { el: to.hash, top: 100 }
    } else if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.login)) {
    if (!store.getters.isLoggedIn) {
      next()
    } else {
      next({ path: '/' })
    }
  } else if (to.matched.some(record => record.meta.logout)) {
    store.commit('AUTH_LOGOUT')
    next({
      path: '/login',
    })
  } else if (to.matched.some(record => record.meta.guest)) {
    next()
  } else {
    if (!store.getters.isLoggedIn) {
      next({
        path: '/login',
      })
    } else {
      next()
    }
  }
})

export default router
