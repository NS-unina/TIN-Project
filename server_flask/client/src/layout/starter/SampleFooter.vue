<template>
  <footer class="footer">
    <div class="container-fluid">
      <div class="copyright">
        ඞ{{ year }} made by
        <a href="https://github.com/AndreaDino" target="_blank" rel="noopener"
          >andrea</a
        >&nbsp;&
        <a href="https://github.com/MarikaSasso" target="_blank" rel="noopener"
          >marika</a
        >
      </div>
    </div>
  </footer>
</template>
<script>
export default {
  data() {
    return {
      year: new Date().getFullYear(),
    };
  },
};
</script>
<style></style>
