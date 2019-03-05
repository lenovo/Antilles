<template>
<composite-form-dialog ref="innerDialog"
  :title="title" size="540px"
  :form-model="userForm"
  :form-rules="userRules"
  form-label-width='180px'
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
  <el-form-item :label="$t('User.Username')" prop="username" v-if="mode != 'unfreezed'">
    <el-input id="tid_user-username" v-model="userForm.username" :disabled="mode == 'edit' || mode == 'delete' || mode == 'freezed'"></el-input>
  </el-form-item>
  <!-- <el-form-item :label="$t('User.Username')" prop="username" v-if="mode == 'import'">
    <el-select id="tid_user-username-select" v-model="userForm.username" >
      <el-option
        v-for="item in usernameOptions"
        :key="item.value"
        :label="item.label"
        :value="item.value">
      </el-option>
    </el-select>
  </el-form-item> -->
  <el-form-item :label="$t('User.Role')" prop="role" v-if="freezed()">
    <el-select id="tid_user-role" v-model="userForm.role" :disabled="mode == 'delete'">
      <el-option
        v-for="item in roleOptions"
        :key="item.value"
        :label="item.label"
        :value="item.value">
      </el-option>
    </el-select>
  </el-form-item>
  <el-form-item :label="$t('User.FirstName')" prop="firstName" v-if="freezed()">
    <el-input id="tid_user-firstname" v-model="userForm.firstName" :disabled="mode == 'delete'"></el-input>
  </el-form-item>
  <el-form-item :label="$t('User.LastName')" prop="lastName" v-if="freezed()">
    <el-input id="tid_user-lastname" v-model="userForm.lastName" :disabled="mode == 'delete'"></el-input>
  </el-form-item>
  <el-form-item :label="$t('BillGroup')" prop="billGroupId" v-if="freezed()">
    <el-select id="tid_user-billgroup" v-model.number="userForm.billGroupId" :disabled="mode == 'delete'">
      <el-option
        v-for="item in billGroupOptions"
        :key="item.value"
        :label="item.label"
        :value="item.value">
      </el-option>
    </el-select>
  </el-form-item>
  <el-form-item :label="$t('User.Email')" prop="email" v-if="freezed()">
    <el-input id="tid_user-email" v-model="userForm.email" :disabled="mode == 'delete'"></el-input>
  </el-form-item>
  <!-- <el-form-item :label="$t('User.HomeDirectory')" prop="homeDirectory" v-if="mode == 'import'">
    <el-input id="tid_user-home-directory" v-model="userForm.homeDirectory" :disabled="mode == 'delete'"></el-input>
  </el-form-item> -->
  <el-form-item :label="$t('UserGroup')" prop="userGroupName" v-if="ldapManaged && freezed()">
    <el-select id="tid_user-usergroup" v-model="userForm.userGroupName" :disabled="mode == 'delete'">
      <el-option
        v-for="item in userGroupOptions"
        :key="item.value"
        :label="item.label"
        :value="item.value">
      </el-option>
    </el-select>
  </el-form-item>
  <el-form-item :label="$t('User.Password')" prop="password" v-if="mode == 'create'">
    <el-input id="tid_user-password" type="password" v-model="userForm.password"></el-input>
  </el-form-item>
  <el-form-item :label="$t('User.Password.Check')" prop="passwordCheck" v-if="mode == 'create'">
    <el-input id="tid_user-password-check" type="password" v-model="userForm.passwordCheck"></el-input>
  </el-form-item>

  <el-form-item :label="$t('User.Freezed.Time')" prop="freezedTimeDay" v-if="mode == 'freezed'">
    <el-input id="tid_user-freezed-day" v-model="userForm.freezedTimeDay">
      <template slot="append">{{$t('User.Freezed.Time.Days')}}</template>
    </el-input>
  </el-form-item>
  <el-form-item label="" prop="freezedTimeHour" v-if="mode == 'freezed'">
    <el-input id="tid_user-freezed-hour" v-model="userForm.freezedTimeHour">
      <template slot="append">{{$t('User.Freezed.Time.Hours')}}</template>
    </el-input>
  </el-form-item>
  <p v-if="mode == 'unfreezed'">{{$t('User.Unfreezed.Text', {'name': userForm.username})}}</p>
</composite-form-dialog>
</template>
<script>
import UserService from '../../service/user'
import UserGroupService from '../../service/user-group'
import BillGroupService from '../../service/bill-group'
import CompositeFormDialog from '../../component/composite-form-dialog'
import ValidRoleFactory from '../../common/valid-role-factory'
import AuthService from '../../service/auth'

export default {
  data() {
    var roleOptions = [];
    UserService.UserRoleEnums.forEach((role) => {
      roleOptions.push({
        value: role,
        label: UserService.getUserRoleDisplayName(role)
      });
    });
    var validatePasswordCheck = (rule, value, callback) => {
      if(this.userForm.password != this.userForm.passwordCheck) {
        return callback(new Error(this.$t("User.Password.Check.Valid")));
      } else {
        callback();
      }
    };
    return {
      title: '',
      mode: '',
      ldapManaged: AuthService.isLDAPManaged(),
      userId: 0,
      userForm: {
        username: '',
        role: 'admin',
        firstName: '',
        lastName: '',
        billGroupId: null,
        userGroupName: '',
        email: '',
        homeDirectory: '',
        password: '',
        passwordCheck: '',
        freezedTimeDay: 0,
        freezedTimeHour: 0
      },
      usernameOptions: [],
      roleOptions: roleOptions,
      userGroupOptions: [],
      billGroupOptions: [],
      userRules: {
        username: [
          ValidRoleFactory.getRequireRoleForText(this.$t('User.Username')),
          ValidRoleFactory.getLengthRoleForText(this.$t('User.Username'), 3, 31),
          ValidRoleFactory.getValidSystemNameRoleForText(this.$t('User.Username'), false)
        ],
        role: [
          ValidRoleFactory.getRequireRoleForText(this.$t('User.Role'))
        ],
        firstName: [
          ValidRoleFactory.getLengthRoleForText(this.$t('User.FirstName'), 1, 20)
        ],
        lastName: [
          ValidRoleFactory.getLengthRoleForText(this.$t('User.LastName'), 1, 20)
        ],
        userGroupName: [
          ValidRoleFactory.getRequireRoleForText(this.$t('UserGroup'))
        ],
        billGroupId: [
          ValidRoleFactory.getRequireRoleForNumber(this.$t('BillGroup'))
        ],
        email: [
          ValidRoleFactory.getEmailRole(this.$t('User.Email'))
        ],
        homeDirectory: [
          ValidRoleFactory.getLengthRoleForText(this.$t('User.HomeDirectory'), 0, 255)
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
        ],
        freezedTimeDay: [
          ValidRoleFactory.getValidNumberRoleForText(this.$t('User.Freezed.Time')),
          ValidRoleFactory.getNumberDecimalRoleForText(this.$t('User.Freezed.Time'), 0),
          ValidRoleFactory.getNumberRangeRoleForText(this.$t('User.Freezed.Time'), 0, 999),
        ],
        freezedTimeHour: [
          ValidRoleFactory.getValidNumberRoleForText(this.$t('User.Freezed.Time')),
          ValidRoleFactory.getNumberDecimalRoleForText(this.$t('User.Freezed.Time'), 0),
          ValidRoleFactory.getNumberRangeRoleForText(this.$t('User.Freezed.Time'), 0, 999)
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
        return UserService.createUser(this.userForm.username,
          this.userForm.role,
          this.userForm.firstName,
          this.userForm.lastName,
          this.userForm.billGroupId,
          this.userForm.email,
          this.userForm.userGroupName,
          this.userForm.password);
      }
      if(this.mode == 'edit') {
        return UserService.updateUser(this.userId,
          this.userForm.role,
          this.userForm.firstName,
          this.userForm.lastName,
          this.userForm.billGroupId,
          this.userForm.email,
          this.userForm.userGroupName);
      }
      if(this.mode == 'delete') {
        return UserService.deleteUser(this.userId);
      }
      if(this.mode == 'import') {
        return UserService.importUser(this.userForm.username,
          this.userForm.role,
          this.userForm.firstName,
          this.userForm.lastName,
          this.userForm.billGroupId,
          this.userForm.email,
          this.userForm.homeDirectory);
      }
      if(this.mode == 'freezed') {
        return UserService.freezedUserByName(this.userId,
          this.userForm.freezedTimeDay,
          this.userForm.freezedTimeHour);
      }
      if(this.mode == 'unfreezed') {
        return UserService.unfreezedUserByName(this.userId);
      }
    },
    successMessageFormatter(res) {
      var user = res;
      if(this.mode == 'create') {
        return this.$t('User.Create.Success', {'name': user.username});
      }
      if(this.mode == 'edit') {
        return this.$t('User.Edit.Success', {'name': user.username});
      }
      if(this.mode == 'delete') {
        return this.$t('User.Delete.Success', {'name': this.userForm.username});
      }
      if(this.mode == 'import') {
        return this.$t('User.Import.Success', {'name': user.username});
      }
      if(this.mode == 'freezed') {
        return this.$t('User.Freezed.Success', {'name': this.userForm.username});
      }
      if(this.mode == 'unfreezed') {
        return this.$t('User.Unfreezed.Success', {'name': this.userForm.username});
      }
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    getUserInfo(id) {
      UserService.getUserById(id).then((res) => {
        this.initUserGroupOptions(res.userGroupName);
      })
    },
    initUserListOption() {
      UserService.getUserImportList().then((res) => {
        res.forEach((role) => {
          this.usernameOptions.push({
            value: role,
            label: role
          });
        });
      })
    },
    initUserGroupOptions(defaultUserGroupName) {
      if(this.ldapManaged) {
        UserGroupService.getAllUserGroups().then((res) => {
          var options = [];
          res.forEach((userGroup) => {
              options.push({
                value: userGroup.name,
                label: userGroup.name
              });
          });
          this.userGroupOptions = options;
          if(defaultUserGroupName) {
            this.userForm.userGroupName = defaultUserGroupName;
          } else if (this.userGroupOptions.length > 0) {
            this.userForm.userGroupName = this.userGroupOptions[0].value;
          } else {
            this.userForm.userGroupName = '';
          }
        }, (res) => {
          this.$message.error(res);
        });
      } else {
          this.userForm.userGroupName = defaultUserGroupName;
      }
    },
    initBillGroupOptions(defaultBillGroupId) {
      BillGroupService.getAllBillGroups().then((res) => {
        var options = [];
        res.forEach((billGroup) => {
          options.push({
            value: billGroup.id,
            label: billGroup.name
          });
        });
        this.billGroupOptions = options;
        if(defaultBillGroupId) {
          this.userForm.billGroupId = defaultBillGroupId;
        } else if (this.billGroupOptions.length > 0) {
          this.userForm.billGroupId = this.billGroupOptions[0].value;
        } else {
          this.userForm.billGroupId = null;
        }
      }, (res) => {
        this.$message.error(res);
      });
    },
    freezed(){
      if(this.mode != 'freezed' && this.mode != 'unfreezed') {
        return true;
      } else {
        return false;
      }
    },
    doCreate() {
      this.mode = 'create';
      this.userId = 0;
      this.userForm = {
        username: '',
        role: 'staff',
        firstName: '',
        lastName: '',
        billGroupId: null,
        userGroupName: '',
        email: '',
        homeDirectory: '',
        password: '',
        passwordCheck: ''
      };
      this.initUserGroupOptions();
      this.initBillGroupOptions();
      this.title = this.$t('User.Create.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doEdit(user) {
      this.mode = 'edit';
      this.userId = user.id;
      this.userForm = {
        username: user.username,
        role: user.role,
        firstName: user.firstName,
        lastName: user.lastName,
        billGroupId: null,
        userGroupName: '',
        email: user.email,
        homeDirectory: '',
        password: '',
        passwordCheck: ''
      };
      this.getUserInfo(user.id);
      this.initBillGroupOptions(user.billGroupId);
      this.title = this.$t('User.Edit.Title', {id: user.id});
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doDelete(user) {
      this.mode = 'delete';
      this.userId = user.id;
      this.userForm = {
        username: user.username,
        role: user.role,
        firstName: user.firstName,
        lastName: user.lastName,
        billGroupId: null,
        userGroupName: '',
        email: user.email,
        homeDirectory: '',
        password: '',
        passwordCheck: ''
      };
      this.getUserInfo(user.id);
      this.initBillGroupOptions(user.billGroupId);
      this.title = this.$t('User.Delete.Title', {id: user.id});
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doImport() {
      this.mode = 'import';
      this.userId = 0;
      this.userForm = {
        username: '',
        role: 'staff',
        firstName: '',
        lastName: '',
        billGroupId: null,
        userGroupName: '',
        email: '',
        homeDirectory: '',
        password: '',
        passwordCheck: ''
      };
      this.usernameOptions = [];
      this.initUserListOption();
      this.initUserGroupOptions();
      this.initBillGroupOptions();
      this.title = this.$t('User.Import.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doFreezed(user) {
      this.mode = 'freezed';
      this.userId = user.id;
      this.userForm = {
        username: user.username,
        role: '',
        firstName: '',
        lastName: '',
        billGroupId: null,
        userGroupName: '',
        email: '',
        homeDirectory: '',
        password: '',
        passwordCheck: '',
        freezedTimeDay: 0,
        freezedTimeHour: 0
      };
      this.title = this.$t('User.Freezed.Title', {id: user.id});
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doUnfreezed(user) {
      this.mode = 'unfreezed';
      this.userId = user.id;
      this.userForm = {
        username: user.username,
        role: '',
        firstName: '',
        lastName: '',
        billGroupId: null,
        userGroupName: '',
        email: '',
        homeDirectory: '',
        password: '',
        passwordCheck: ''
      };
      this.title = this.$t('User.Unfreezed.Title', {id: user.id});
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>
