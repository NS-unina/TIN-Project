<template>
    <button  class="button__login btn btn-round btn-block btn-primary btn-lg" type="submit" @click="handleLogin">Log In</button>
    
  </template>
  
  <script>
  export default {
    methods: {
      handleLogin() {
        this.$auth0.loginWithRedirect({
          appState: {
            targetPath: "/dashboard",
          },
        });
      },
    },
  };
  </script>