<template>
<composite-form-dialog ref="innerDialog"
  :title="$t('LDAP.Login.Title')" size="500px"
  :form-model="loginForm"
  :form-rules="loginRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter"
  :notChangeParent="true">
  <el-form-item :label="$t('LDAP.Login.Username')" prop="username">
    <el-input id="tid_login-ldap-username" v-model="loginForm.username"></el-input>
  </el-form-item>
  <el-form-item :label="$t('LDAP.Login.Password')" prop="password">
    <el-input id="tid_login-ldap-password" type="password" v-model="loginForm.password"></el-input>
  </el-form-item>
</composite-form-dialog>
</template>
<script>
import AuthService from '../../service/auth'
import CompositeFormDialog from '../../component/composite-form-dialog'
import ValidRoleFactory from '../../common/valid-role-factory'

export default {
  data() {
    return {
      loginForm: {
        username: this.$store.state.auth.ldapDefaultUsername,
        password: ''
      },
      loginRules: {
        username: [
          ValidRoleFactory.getRequireRoleForText(this.$t('LDAP.Login.Username')),
          ValidRoleFactory.getLengthRoleForText(this.$t('LDAP.Login.Username'), 3, 50)
        ],
        password: [
          ValidRoleFactory.getRequireRoleForText(this.$t('LDAP.Login.Password'))
          //ValidRoleFactory.getPasswordRole(this.$t('LDAP.Login.Password'))
        ]
      }
    };
  },
  components: {
    'composite-form-dialog': CompositeFormDialog
  },
  methods: {
    submitForm() {
      return AuthService.loginLDAP(this.loginForm.username, this.loginForm.password);
    },
    successMessageFormatter(res) {
      return this.$t('LDAP.Login.Success');
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    doLogin() {
      this.userForm = {
        username: '',
        password: ''
      };
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>
