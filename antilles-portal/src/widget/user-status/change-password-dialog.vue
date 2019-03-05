<template>
<composite-form-dialog id="tid_change-password-dialog" ref="innerDialog"
  :title="$t('Auth.ChangePassword.Title')" size="540px"
  :form-model="userForm"
  :form-rules="userRules"
  form-label-width='180px'
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
  <el-form-item :label="$t('Auth.CurrentPassword')" prop="currentPassword">
    <el-input id="tid_change-password-current-password" type="password" v-model="userForm.currentPassword"></el-input>
  </el-form-item>
  <el-form-item :label="$t('Auth.NewPassword')" prop="password">
    <el-input id="tid_change-password-password" type="password" v-model="userForm.password"></el-input>
  </el-form-item>
  <el-form-item :label="$t('Auth.NewPassword.Check')" prop="passwordCheck">
    <el-input id="tid_change-password-password-check" type="password" v-model="userForm.passwordCheck"></el-input>
  </el-form-item>
</composite-form-dialog>
</template>
<script>
import AuthService from '../../service/auth'
import CompositeFormDialog from '../../component/composite-form-dialog'
import ValidRoleFactory from '../../common/valid-role-factory'

export default {
  data() {
    var validatePasswordCheck = (rule, value, callback) => {
      if(this.userForm.password != this.userForm.passwordCheck) {
        return callback(new Error(this.$t("Auth.NewPassword.Check.Valid")));
      } else {
        callback();
      }
    };
    return {
      userId: 0,
      userForm: {
        currentPassword: '',
        password: '',
        passwordCheck: ''
      },
      userRules: {
        currentPassword: [
          ValidRoleFactory.getRequireRoleForText(this.$t('Auth.CurrentPassword'))
        ],
        password: [
          ValidRoleFactory.getRequireRoleForText(this.$t('Auth.NewPassword')),
          ValidRoleFactory.getPasswordRole(this.$t('Auth.NewPassword'))
        ],
        passwordCheck: [
          ValidRoleFactory.getRequireRoleForText(this.$t('Auth.NewPassword.Check')),
          {
            validator: validatePasswordCheck,
            trigger: 'blur'
          }
        ]
      }
    };
  },
  components: {
    'composite-form-dialog': CompositeFormDialog
  },
  methods: {
    submitForm() {
      return AuthService.changePassword(this.userForm.currentPassword, this.userForm.password);
    },
    successMessageFormatter(res) {
      var user = res;
      return this.$t('Auth.ChangePassword.Success');
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    doChangePassword() {
      this.userForm = {
        currentPassword: '',
        password: '',
        passwordCheck: ''
      };
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>
