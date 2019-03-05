<style>
  .HealthContainer{
     background: #fff;
     padding: 20px;
  }
  .HealthChartContent{
    margin-top: 20px;
  }
</style>
<template>
  <div class="HealthContainer">
    <div>
      <el-button-group id="tid_group-health-mode-select">
        <el-button v-for="(item,index) in healthCategoryEnum"
                   :key="index"
                   :type="currentSelectedHealthCategory == item ? 'primary' : 'normal'"
                   :group-id="currentSelectedGroupId"
                   @click="onHealthActionButtonClick(item)"
                   :title="chartBtnTitle[item]">
            <i :class="itemBtnIcon[item]"></i>
        </el-button>
      </el-button-group>
    </div>
    <div class="HealthChartContent">
      <health-chart :health-category="currentSelectedHealthCategory" :group-id="currentSelectedGroupId"></health-chart>
    </div>
  </div>
</template>
<script>
  import MonitorDataService from '../../service/monitor-data'
  import HealthChart from './group-health/health-chart.vue'
  export default {
    data(){
      return {
        currentSelectedHealthCategory:"temperature",
        healthCategoryEnum: this.sortHealthCategoryEnum(MonitorDataService.DataCategoryEnums),
        itemBtnIcon: {
          'load': 'el-erp-load',
          'cpu': 'el-erp-cpu',
          'ram': 'el-erp-memory',
          'disk': 'el-erp-storage',
          'network': 'el-erp-network',
          'energy': 'el-erp-monitor_power',
          'temperature': 'el-erp-temperature',
          'job': 'el-erp-job'
        },
        chartBtnTitle: {

        }
      }
    },
    components: {
      'health-chart': HealthChart
    },
    mounted(){
      this.$nextTick(() => {
        this.chartBtnTitle = {
          'load': this.$t('Trend.Chart.Title.load'),
          'cpu': this.$t('Trend.Chart.Title.cpu'),
          'ram': this.$t('Trend.Chart.Title.ram'),
          'disk': this.$t('Trend.Chart.Title.disk'),
          'network': this.$t('Trend.Chart.Title.network'),
          'energy': this.$t('Trend.Chart.Title.energy'),
          'temperature': this.$t('Trend.Chart.Title.temperature'),
          'job': this.$t('Trend.Chart.Title.job')
        };
      })
    },
    props: [
      "currentSelectedGroupId"
    ],
    methods: {
      onHealthActionButtonClick(category){
        this.currentSelectedHealthCategory = category;
      },
      sortHealthCategoryEnum(healthCategoryEnum){
        var sortRule={
          'load':3,
          'cpu':4,
          "ram":5,
          "disk":6,
          "network":7,
          "energy":2,
          "temperature":1,
          "job":8
        };
        return healthCategoryEnum.sort((a,b)=>sortRule[a]-sortRule[b])
      }
    }
  }
</script>
