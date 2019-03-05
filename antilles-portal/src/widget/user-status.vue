<style media="screen">
.user-status {
  cursor: pointer;
}
.user-status-label{
  width: 200px !important;
  width: 100%;
  margin:0;
  padding:0;
  font-size: 14px;
  color:#333;
}
.user-status-icon {
  display: inline-block;
  height: 24px;
  width: 24px;
  background: url('./../asset/image/main/user.png') no-repeat;
}
.user-status-log-out {
  display: inline-block;
  height: 14px;
  width: 14px;
  background: url('./../asset/image/main/log-out.png') no-repeat;
  float: right;
  margin:7px 0 5px;
  cursor: pointer;
}
.user-status-title{
  padding:20px 20px 10px;
}
.user-status-username {
  box-sizing: border-box;
  color: #999;
  width: 100%;
  height: 30px;
  padding:0 20px 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.user-status-pass-edit {
  display: inline-block;
  font-style: normal;
  color: #5FB4F9;
  cursor: pointer;
  position: relative;
  margin-left: 20px;
  top: -4px;
  font-size: 18px;
}
.user-status-row {
  box-sizing: border-box;
  width: 100%;
  height: 50px;
  padding:15px 20px;
  border-top: 1px solid #eee;
}
.user-status-row>a{
  color: #333;
}
.user-status-row>i{
  width: 16px;
  height: 16px;
  margin-top: 2px;
}
.user-status-row i.el-icon-circle-check{
  color: #5fb4f9;
}
</style>
<template>
  <span class="user-status">
    <el-popover ref="popoverUser" placement="bottom" width="275" title=""
    popper-class="user-status-label"
    trigger="hover">
    <div class="user-status-title">
       <i class="user-status-icon"></i>
       <i id="tid_antilles-change-password" :title="$t('User.Change.Password')" class="user-status-pass-edit  el-erp-changepassword" @click="changePassword"></i>
       <i id="tid_antilles-logout" class="user-status-log-out" :title='$t("Logout")' @click="logout"></i>
    </div>
    <!-- <p class="user-status-username">{{ $t('User.Status.Id', {'id': userId}) }}</p> -->
    <p class="user-status-username" :title='userName'>{{ $t('User.Status.Username', {'name': userName}) }}</p>
    <!-- <p class="user-status-username">{{ $t('User.Group', {'group': userGroup}) }}</p> -->
    <ul id="tid_antilles-user-role-action" class="user-status-content">
      <li class="user-status-row" v-for="(access, index) in accessList"
        @click='shiftAccess(access)' :key="index">
        <a href="javascript:void(0)">{{$t("Access." + access)}}</a>
        <i class="el-icon--right" :class="currentAccess == access ? 'el-icon-circle-check' : ''"></i>
      </li>
    </ul>
    </el-popover>
    <i class="user-status-icon" v-popover:popoverUser></i>
    <change-password-dialog ref="changePasswordDialog"/>
  </span>
</template>
<script type="text/javascript">
  import AuthService from '../service/auth'
  import AccessService from '../service/access'
  import ChangePasswordDialog from './user-status/change-password-dialog'

  export default {
    data() {
      return {
        //userName: this.$store.state.auth.username,
        currentAccess: this.$store.state.auth.access,
        accessList: AccessService.getAvailableAccessByRole(this.$store.state.auth.role)
      }
    },
    props: [
      'userName',
      'userId',
      'userGroup'
    ],
    components: {
      'change-password-dialog': ChangePasswordDialog
    },
    methods: {
      shiftAccess(access) {
        AccessService.shiftAccess(access);
      },
      changePassword() {
        this.$refs.changePasswordDialog.doChangePassword().then((res) => {
					// Do nothing
          AuthService.logout();
				}, (res) => {
					// Do nothing
				});
      },
      logout() {

        this.$confirm(this.$t('Logout.Tip.Text'), this.$t("Logout"), {
          confirmButtonText: this.$t('Global.Btn.confirm'),
          cancelButtonText: this.$t('Global.Btn.cancel'),
          type: 'warning'
        }).then(() => {
          AuthService.logout();
        }).catch(() => {

        });


      }
    }
  }
</script>
