import Vue from "vue";
import Router from "vue-router";
import DashboardLayout from "../layout/starter/SampleLayout.vue";
import Test from "../layout/dashboard/ContentFooter.vue";
import { authenticationGuard } from "../authentication-guard";

const Dashboard = () =>
  import(/* webpackChunkName: "dashboard" */ "@/pages/Dashboard.vue");

const VMS = () =>
  import(/* webpackChunkName: "vms" */ "@/layout/starter/SamplePage.vue");


const Container = () =>
  import(/* webpackChunkName: "containers" */ "@/layout/starter/ContainerPage.vue");

const Services = () =>
  import(/* webpackChunkName: "services" */ "@/layout/starter/ServicesPage.vue");



Vue.use(Router);

export default new Router({
  routes: [
    {
      path: "/",
      name: "home",
      redirect: "/dashboard",
      component: DashboardLayout,
      children: [
        {
          path: "dashboard",
          name: "dashboard",
          components: { default: Dashboard },
        },
        {
          path: "vm",
          name: "vm",
          components: { default: VMS },
          beforeEnter: authenticationGuard,

        },
        {
          path: "containers",
          name: "containers",
          components: { default: Container },
          beforeEnter: authenticationGuard,

        },
        {
          path: "services",
          name: "services",
          components: { default: Services },
          beforeEnter: authenticationGuard,

        },
      ],
    },
  ],
});
