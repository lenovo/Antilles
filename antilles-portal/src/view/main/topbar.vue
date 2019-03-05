<style>
.main-header {
  width: 100%;
  height: 60px;
  box-sizing: border-box;
  background-color: #fff;
  display: flex;
}
.main-header>div{
  box-sizing: border-box;
  height: 100%;
}
.main-header-left {
  width: 400px;
  padding: 23px;
  display: flex;
  justify-content: left;
}
.main-header-left .main-tab {
  display: inline-block;
  height: 20px;
  width: 20px;
  margin-right: 10px;
  background: url('../../asset/image/main/tab.png') no-repeat;
}
.main-header-right {
  flex: 1 1 auto;
  padding-top: 20px;
  display: flex;
  justify-content: flex-end;
}
.main-header-right>span {
  margin-right: 30px;
}
.welcome-user {
  color: #999;
}
</style>
<template>
  <nav class="main-header">
    <div class="main-header-left">
      <span id="tid_topbar-shift" class="main-tab" @click='shiftMenuSize'></span>
      <span class="main-heaser-title"></span>
    </div>
    <div class="main-header-right">
      <span class="welcome-user">{{ $t('Welcome.User', {'name': userName}) }}</span>
      <globalsearch></globalsearch>
      <alarmstatus id="tid_topbar-alarm-status"></alarmstatus>
      <userstatus id="tid_topbar-user-status" :user-name="userName" :user-id='userId' :user-group='userGroup'></userstatus>
    </div>
  </nav>
</template>
<script>
  import Userstatus from './../../widget/user-status'
  import Alarmstatus from './../../widget/alarm-status'
  import Globalsearch from './../../widget/search'
  import UserService from './../../service/user'

  export default {
    data () {
      return {
        userName: '',
        userId: '',
        userGroup: '',
        refreshTimeout: null
      }
    },
    mounted() {
      this.getUser()
    },
    components: {
      Userstatus ,
      Alarmstatus,
      Globalsearch
    },
    beforeDestroy() {
      clearTimeout(this.refreshTimeout);
    },
    methods: {
      shiftMenuSize () {
        gApp.isCollapse = !gApp.isCollapse
      },
      getUser() {
        UserService.getUserById(this.$store.state.auth.userid).then((res) => {
          this.userName = res.realName ? res.realName : '';
          this.userName = this.userName?this.userName:this.$store.state.auth.username;
          this.userId = res.id;
          this.userGroup = res.userGroupName;
          this.refreshTimeout = setTimeout(()=>{this.getUser()}, 60000)
        }, (res) => {
          console.log("Can't get user info");
        })
      }
    }
  }
</script>
