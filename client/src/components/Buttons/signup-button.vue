<template>
    <button class="button__sign-up" @click="handleSignUp">Sign Up</button>
  </template>
  
  <script>
  export default {
    methods: {
      handleSignUp() {
        this.$auth0.loginWithRedirect({
          appState: {
            targetPath: "/vm",
          },
          authorizationParams: {
            screen_hint: "signup",
          }
        });
      },
    },
  };
  </script>