<template>
  <div class="wrapper">

    <side-bar v-if="$route?.meta?.hideMenu === undefined"
        content-id="main-content"
        type="overlay">
        
      <template slot="links">
        <sidebar-link
          to="/dashboard"
          :name="$t('Dashboard')"
          icon="tim-icons icon-chart-pie-36"
        />
        <sidebar-link
          to="/vm"
          :name="$t('Virtual Machines')"
          icon="tim-icons icon-app"
        />
        <sidebar-link
          to="/containers"
          :name="$t('Containers ')"
          icon="tim-icons icon-molecule-40"
        />
        <sidebar-link
          to="/services"
          :name="$t('Services')"
          icon="tim-icons icon-components"
        />
      </template>
    </side-bar>
    <div class="main-panel">
      <top-navbar v-if="$route?.meta?.hideMenu === undefined"
        content-id="main-content"
        type="overlay"></top-navbar>

      <dashboard-content @click.native="toggleSidebar"> </dashboard-content>

      <content-footer></content-footer>
    </div>
  </div>
</template>
<style lang="scss"></style>
<script>
import TopNavbar from "./SampleNavbar.vue";
import ContentFooter from "./SampleFooter.vue";
import DashboardContent from "./Content.vue";
export default {
  components: {
    TopNavbar,
    ContentFooter,
    DashboardContent,
  },
  methods: {
    toggleSidebar() {
      if (this.$sidebar.showSidebar) {
        this.$sidebar.displaySidebar(false);
      }
    },
  },
};
</script>
