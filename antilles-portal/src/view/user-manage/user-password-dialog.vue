<template>
<composite-form-dialog ref="innerDialog"
  :title="$t('User.ChangePassword.Title')" size="500px"
  :form-model="userForm"
  :form-rules="userRules"
  form-label-width='150px'
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
  <el-form-item :label="$t('User.Username')" prop="username">
    <el-input id="tid_user-change-password-username" v-model="userForm.username" :disabled="true"></el-input>
  </el-form-item>
  <el-form-item :label="$t('User.Password')" prop="password">
    <el-input id="tid_user-change-password-password" type="password" v-model="userForm.password"></el-input>
  </el-form-item>
  <el-form-item :label="$t('User.Password.Check')" prop="passwordCheck">
    <el-input id="tid_user-change-password-password-check" type="password" v-model="userForm.passwordCheck"></el-input>
  </el-form-item>
</composite-form-dialog>
</template>
<script>
import UserService from '../../service/user'
import CompositeFormDialog from '../../component/composite-form-dialog'
import ValidRoleFactory from '../../common/valid-role-factory'

export default {
  data() {
    var validatePasswordCheck = (rule, value, callback) => {
      if(this.userForm.password != this.userForm.passwordCheck) {
        return callback(new Error(this.$t("User.Password.Check.Valid")));
      } else {
        callback();
      }
    };
    return {
      userId: 0,
      userForm: {
        username: '',
        password: '',
        passwordCheck: ''
      },
      userRules: {
        username: [
          ValidRoleFactory.getRequireRoleForText(this.$t('User.Username')),
          ValidRoleFactory.getLengthRoleForText(this.$t('User.Username'), 3, 32)
        ],
        password: [
          ValidRoleFactory.getRequireRoleForText(this.$t('User.Password')),
          ValidRoleFactory.getPasswordRole(this.$t('User.Password'))
        ],
        passwordCheck: [
          ValidRoleFactory.getRequireRoleForText(this.$t('User.Password.Check')),
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
      return UserService.changeUserPassword(this.userId, this.userForm.password);
    },
    successMessageFormatter(res) {
      var user = res;
      return this.$t('User.ChangePassword.Success', {'name': this.userForm.username});
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    doChangePassword(user) {
      this.userId = user.id;
      this.userForm = {
        username: user.username,
        password: '',
        passwordCheck: ''
      };
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>
