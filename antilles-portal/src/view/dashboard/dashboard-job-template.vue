<style lang="css">
.dashboard-template {
  overflow: hidden;
}
  .dashboard-template-left{
    float: left;
  }
  .dashboard-template-right{
    float: right;
  }
  .dashboard-template-card {
    padding: 15px 20px;
    background: #F8F8F8;
    position: relative;
    display: flex;
  }
  .dashboard-template-line{
    width: 100%;

  }

  .dashboard-template-logo {
    /* width: 68px; */
    height: 20px;
    margin-right: 40px;
    object-fit: contain;
    position: absolute;
    top: 38%;

  }
  .dashboard-template-name {
    line-height: 40px;
    color: #000;
    margin-left: 110px;
  }
</style>
<template lang="html">
  <div id="tid_dashboard-job-template" class="dashboard-template">
    <el-row class="dashboard-template-title margin-bottom-20">
        <span class="dashboard-template-left">{{$t('Dashboard.Job.Template.Title')}}</span>
        <a href="#/main/job-template-store" class="dashboard-template-right dashboard-more">{{$t('Dashboard.More')}}</a>
    </el-row>
    <div v-if='templateData' class="dashboard-template-contenter">
      <a v-for='(item, index) in templateData'
        :key='index' :href="getTemplateLocation(item.code)"
        class="dashboard-template-card margin-bottom-20">
        <img class="dashboard-template-logo" :src="item.logo"/>
        <span class="dashboard-template-name">{{item.name}}</span>
      </a>
    </div>
  </div>
</template>

<script>
import DashboardService from './../../service/dashboard-monitor'
export default {
  data() {
    return {
      templateData: []
    };
  },
  props: [
    'initData'
  ],
  mounted() {
    if(this.initData.length>0){
      this.init();
    }
  },
  watch: {
    initData(val, oldVal) {
      if(val !== oldVal) {
        this.init();
      }
    },
  },
  methods: {
    init() {
      DashboardService.getTemplateEnums().then((res) => {
        this.templateData = [];
        this.initData.forEach((item) => {
          res.forEach((resItem) => {
            if(item.type == resItem.code && this.templateData.length<5) {
              this.templateData.push(resItem)
            }
          })

        })
      }, (res) => {

      })
    },
    getTemplateLocation(code) {
      return '#/main/job-template/'+ code;
    }

  }
}
</script>
