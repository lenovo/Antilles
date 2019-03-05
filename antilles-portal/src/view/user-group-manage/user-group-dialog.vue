<template>
<composite-form-dialog ref="innerDialog"
  :title="title" size="500px"
  :form-model="userGroupForm"
  :form-rules="userGroupRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
  <el-form-item :label="$t('UserGroup.Name')" prop="name">
    <el-input id="tid_user-group-name" v-model="userGroupForm.name" :disabled="mode == 'delete'"></el-input>
  </el-form-item>
</composite-form-dialog>
</template>
<script>
import UserGroupService from '../../service/user-group'
import CompositeFormDialog from '../../component/composite-form-dialog'
import ValidRoleFactory from '../../common/valid-role-factory'

export default {
  data() {
    return {
      title: '',
      mode: '',
      userGroupName: '',
      userGroupForm: {
        name: ''
      },
      userGroupRules: {
        name: [
          ValidRoleFactory.getRequireRoleForText(this.$t('UserGroup.Name')),
          ValidRoleFactory.getLengthRoleForText(this.$t('UserGroup.Name'), 3, 31),
          ValidRoleFactory.getValidSystemNameRoleForText(this.$t('UserGroup.Name'), true)
        ]
      }
    };
  },
  components: {
    'composite-form-dialog': CompositeFormDialog
  },
  methods: {
    submitForm() {
      if(this.mode == 'create') {
        return UserGroupService.createUserGroup(this.userGroupForm.name);
      }
      if(this.mode == 'edit') {
        return UserGroupService.updateUserGroup(this.userGroupName, this.userGroupForm.name);
      }
      if(this.mode == 'delete') {
        return UserGroupService.deleteUserGroup(this.userGroupName);
      }
    },
    successMessageFormatter(res) {
      var userGroup = res;
      if(this.mode == 'create') {
        return this.$t('UserGroup.Create.Success', {'name': userGroup.name});
      }
      if(this.mode == 'edit') {
        return this.$t('UserGroup.Edit.Success', {'name': userGroup.name});
      }
      if(this.mode == 'delete') {
        return this.$t('UserGroup.Delete.Success', {'name': userGroup.name});
      }
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    doCreate() {
      this.mode = 'create';
      this.userGroupName = '';
      this.userGroupForm = {
        name: ''
      };
      this.title = this.$t('UserGroup.Create.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doEdit(userGroup) {
      this.mode = 'edit';
      this.userGroupName = userGroup.name;
      this.userGroupForm = {
        name: userGroup.name
      };
      this.title = this.$t('UserGroup.Edit.Title', {id: userGroup.name});
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doDelete(userGroup) {
      this.mode = 'delete';
      this.userGroupName = userGroup.name;
      this.userGroupForm = {
        name: userGroup.name
      };
      this.title = this.$t('UserGroup.Delete.Title', {id: userGroup.name});
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>
