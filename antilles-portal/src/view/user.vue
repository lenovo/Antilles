<style lang="css">
.user-detail .cell span {
  display: block;
}
.user-detail .cell {
  background: #fff;
  padding: 20px;
}
.user-detail .cell li span:first-child {
  margin-bottom: 20px;
}
.user-detail .cell .cell-left {
  width: 120px;
}
.user-detail .cell .cell-right {
  width: 100%;
}
.user-detail .cell .cell-right span {
  text-align: right;
}
.user-detail-icon{
  display: block;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #5fb4f9;
  position: relative;
}
.user-detail-icon i{
  color: #fff;
  position: absolute;
  left: 5px;
  top:3px;
  font-size: 20px;
}

.user-detail-div{
  display: flex;
  align-items: center;
}
.user-detail-div-icon{
  width: 15%;
}
.cell-right{
  margin-top: 10px;
}
</style>
<template lang="html">
  <div v-if='user' class="user-detail m-10 b-w p-20">
    <h3 class="m-b-20">{{user.username}}</h3>
    <el-row class="m-b-10">
      <el-col :lg="6" :md="8" :sm="24" :xs="24">
          <div class="user-detail-div">
            <div class="user-detail-div-icon">
              <span class="user-detail-icon"><i class="el-erp-email"></i></span>
            </div>
            <ul >
              <li class="cell-left">
                <span class="cell-title">{{$t('User.Detail.Email')}}</span>
                <span class="cell-logo logo-cpu"></span>
              </li>
              <li class="cell-right">
                <span class="cell-content">{{ user.email }} &nbsp;</span>
              </li>
            </ul>
          </div>
      </el-col>
      <el-col :lg="6" :md="8" :sm="24" :xs="24">
          <div class="user-detail-div">
            <div class="user-detail-div-icon">
              <span class="user-detail-icon"><i class="el-erp-id"></i></span>
            </div>
            <ul >
              <li class="cell-left">
                <span class="cell-title">{{$t('User.Detail.Id')}}</span>
                <span class="cell-logo logo-cpu"></span>
              </li>
              <li class="cell-right">
                <span class="cell-content">{{ user.id }}</span>
              </li>
            </ul>
          </div>
      </el-col>
      <el-col :lg="6" :md="8" :sm="24" :xs="24">
          <div class="user-detail-div">
            <div class="user-detail-div-icon">
              <span class="user-detail-icon"><i class="el-erp-role"></i></span>
            </div>
            <ul >
              <li class="cell-left">
                <span class="cell-title">{{$t('User.Detail.Role')}}</span>
                <span class="cell-logo logo-cpu"></span>
              </li>
              <li class="cell-right">
                <span class="cell-content">{{ $t(`Access.${user.role }`)}}</span>
              </li>
            </ul>
          </div>
      </el-col>
    </el-row>
    <el-row>
      <el-collapse v-model="activeName" accordion>
        <el-collapse-item :title="$t('User.Detail.Information')" name="info">
          <p class="p-l-20 m-b-10">{{$t('User.Detail.CreateTime')}}<span class="p-l-20">{{columnFormatter(user.createTime)}}</span></p>
          <p class="p-l-20 m-b-10">{{$t('User.Detail.LatestLogin')}}<span class="p-l-20">{{columnFormatter(user.loginTime)}}</span></p>
        </el-collapse-item>
        <el-collapse-item v-if='user.userGroup' :title="$t('User.Detail.Group')" name="userGroup">
          <p class="p-l-20 m-b-10">{{$t('User.Detail.Group.Name')}}<span class="p-l-20">{{user.userGroup.name}}</span></p>
        </el-collapse-item>
        <el-collapse-item v-if='user.billGroup' :title="$t('User.Detail.BillGroup')" name="billGroup">
          <p class="p-l-20 m-b-10">{{$t('User.Detail.BillGroup.Name')}}<span class="p-l-20">{{user.billGroup.name}}</span></p>
          <p class="p-l-20 m-b-10">{{$t('User.Detail.BillGroup.Balance')}}<span class="p-l-20">{{ currency }}{{user.billGroup.accountBalance}}</span></p>
          <p class="p-l-20 m-b-10">{{$t('User.Detail.BillGroup.Rate')}}<span class="p-l-20">{{ currency }}{{user.billGroup.chargeRate}}</span></p>
          <p class="p-l-20 m-b-10">{{$t('User.Detail.BillGroup.UsedCredits')}}<span class="p-l-20">{{ currency }}{{user.billGroup.accountConsumed}}</span></p>
        </el-collapse-item>
      </el-collapse>
    </el-row>
  </div>
</template>

<script>
import UserService from '../service/user'
import Format from '../common/format'
export default {
  data () {
    return {
      currency: this.$store.getters['settings/getCurrency'],
      userId: null,
      user: null,
      activeName: 'info'
    }
  },
  created() {
      this.getData();
  },
  mounted() {

  },
  methods: {
    columnFormatter(time) {
      return Format.formatDateTime(time);
    },
    getData() {
      this.userId = Number(window.location.hash.split('/')[window.location.hash.split('/').length -1]);
      UserService.getUserById(this.userId).then((res) => {
        this.user = res
      })
    }
  }
}
</script>
