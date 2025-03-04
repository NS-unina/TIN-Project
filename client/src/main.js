/*
 =========================================================
 * Vue Black Dashboard - v1.1.3
 =========================================================

 * Product Page: https://www.creative-tim.com/product/black-dashboard
 * Copyright 2024 Creative Tim (http://www.creative-tim.com)

 =========================================================

 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

 */
import { Auth0Plugin } from "./auth0-plugin";
import Vue from "vue";
import VueRouter from "vue-router";
import RouterPrefetch from "vue-router-prefetch";
import App from "./App";
// TIP: change to import router from "./router/starterRouter"; to start with a clean layout
import router from "./router/starterRouter";
import { reactive } from "vue";

import BlackDashboard from "./plugins/blackDashboard";
import i18n from "./i18n";
import "./registerServiceWorker";
Vue.use(BlackDashboard);
Vue.use(VueRouter);
Vue.use(RouterPrefetch);
Vue.use(Auth0Plugin, {
  domain: process.env.VUE_APP_DOMAIN,
  clientId: process.env.VUE_APP_CLIENT_ID,
  redirectUri: process.env.VUE_APP_CALLBACK_URL,
  onRedirectCallback: (appState) => {
    router.push(
      appState && appState.targetPath
        ? appState.targetPath
        : window.location.pathname
    );
  },
});

export const selectedVm = reactive({
  vmId: "",
});

export const selectedContainer = reactive({
  containerIp: "",
});

new Vue({
  router,
  i18n,
  render: (h) => h(App),
}).$mount("#app");

