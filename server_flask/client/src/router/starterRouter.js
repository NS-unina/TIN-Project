import Vue from "vue";
import Router from "vue-router";
import DashboardLayout from "../layout/starter/SampleLayout.vue";
import Test from "../layout/dashboard/ContentFooter.vue";

const Dashboard = () =>
  import(/* webpackChunkName: "dashboard" */ "@/pages/Dashboard.vue");

const VMS = () =>
  import(/* webpackChunkName: "containers" */ "@/layout/starter/SamplePage.vue");


const Container = () =>
  import(/* webpackChunkName: "containers" */ "@/layout/starter/ContainerPage.vue");


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
        },
        {
          path: "containers",
          name: "containers",
          components: { default: Container },
        },
      ],
    },
  ],
});
