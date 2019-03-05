<style scoped>
</style>
<template>
<login-ldap-dialog id="tid_login-ldap-dialog" ref="loginDialog"></login-ldap-dialog>
</template>
<script>
import AuthService from '../service/auth'
import LoginLDAPDialog from './login-ldap/login-ldap-dialog'

export default {
  data() {
    return {};
  },
  components: {
    "login-ldap-dialog": LoginLDAPDialog
  },
  mounted() {
    this.login();
  },
  methods: {
    login() {
      this.$refs.loginDialog.doLogin().then((res) => {
        this.$router.push(this.$route.query.redirect);
      }, (res) => {
        this.$router.push({ path: '/main' });
      });
    }
  }
}
</script>
