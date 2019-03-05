<style lang="css">
.dashboard-joblist-title{
  font-weight: bold;
  font-size:12px;
}
  .dashboard-joblist-col-left{
    float: left;
  }
  .dashboard-joblist-col-left a{
    color: #666;
  }
  .dashboard-joblist-col-right{
    float: right;
  }
  .dashboard-joblist-row {
    border-bottom: 1px solid #EEEEEE;
  }
  .dashboard-joblist-line {
    height: 32px;
    line-height: 32px;
  }
  .dashboard-joblist-content{
    font-size: 12px;
    color:#666;
  }
  .defaultCursor {
    cursor: default;
  }
</style>
<template lang="html">
  <div id="tid_dashboard-joblist">
    <div class="dashboard-joblist-title">
      <el-row class="dashboard-joblist-row">
          <span class="dashboard-joblist-line dashboard-joblist-col-left">{{ $t('Dashboard.JobList.Name') }}</span>
          <span class="dashboard-joblist-line dashboard-joblist-col-right">{{ status=='running'?$t('Job.RunDuration'):$t('Job.WaitDuration') }}</span>
      </el-row>
    </div>
    <div v-if='initJobListData' class="dashboard-joblist-content">
      <el-row v-for='(item, index) in initJobListData' :key='index' class="dashboard-joblist-row">
          <span class="dashboard-joblist-line dashboard-joblist-col-left">
            <a href="javascript:;" @click="processJobHref(item)" :class="notStaff?'defaultCursor':''">{{ item.name }}</a>
          </span>
          <span class="dashboard-joblist-line dashboard-joblist-col-right">{{ item.showTime }}</span>
      </el-row>
    </div>
    <el-row class="dashboard-joblist-row" style="border: 0;">
        <a href="javascript:;" @click="onMoreClick()"
          class="dashboard-joblist-line dashboard-joblist-col-right dashboard-more">{{ $t('Dashboard.More') }}</a>
    </el-row>
  </div>
</template>

<script>
import Format from './../../common/format'
export default {
  data() {
    return {
      notStaff: this.$store.state.auth.access != 'staff',
      initJobListData: null,
      refreshTimeout: null,
      jobHref: '#/main/',
      moreHref: '#/main/job-manage/' + this.status,
      refreshInterval: 30000
    };
  },
  props: [
    'initData',
    'status'
  ],
  mounted() {
    this.init();
  },
  watch: {
    initData(val, oldVal) {
      this.init();
    }//,
    // status() {
    //   this.moreHref = '#/main/job-manage/' + this.status
    // }
  },
  methods: {
    init() {
      if(this.initData && this.initData != [] && this.initData !== true){
        this.initJobListData = [];
        var status = this.status == 'running'? 'runDuration':'waitDuration';
        this.initData.forEach((item) => {
          item.showTime = Format.formatDuration(item[status]);
          this.initJobListData.push(item)
        })
      }

    },
    processJobHref(job) {
      if(this.notStaff) {
        return;
      }
      this.$router.push({ path: '/main/job/' + job.id });
    },
    onMoreClick() {
      this.$router.push({ path: `/main/job-manage/${this.status}` });
    }
  }
}
</script>
