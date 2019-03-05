<style>
  .TrendContainer{
    background: #fff;
    padding-top: 20px;
  }
  .TendencyChartContent{
    padding: 0 10px 20px;
    /*padding-bottom: 20px;
    padding-right: 10px;*/
  }
  .TrendChartItem{
    /*margin-left: 20px;*/
    margin-top: 20px;
  }
</style>
<template>
  <div class="TrendContainer">
    <div style="padding-left:20px;">
      <el-select id="tid_group-trend-time-select" v-model="trendTimeUnit" @change="onTrendTimeIntervalChange">
        <el-option
            v-for="timeInterval in trendIntervalOption"
            :key="timeInterval.value"
            :label="timeInterval.name"
            :value="timeInterval.value">
        </el-option>
      </el-select>
    </div>
    <div id="tid_group-trend-chart-list" class="TendencyChartContent">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6"
          v-for="(category, index) in trendChartCategory"
          class="TrendChartItem"
          :key="index">
          <trend-chart
              :group-id="currentSelectedGroupId"
              :tendency-category=category
              :time-unit="trendTimeUnit">
          </trend-chart>
        </el-col>
      </el-row>
    </div>
  </div>
</template>
<script>

  import TrendChart from "./group-trend/trend-chart.vue"

  export default {
    data() {
      return {
        trendIntervalOption: [
          {
            value: "hour",
            name: this.$t("Trend.Time.Interval.Hour")
          },
          {
            value: "day",
            name: this.$t("Trend.Time.Interval.Day")
          },
          {
            value: "week",
            name: this.$t("Trend.Time.Interval.Week")
          },
          {
            value: "month",
            name: this.$t("Trend.Time.Interval.Month")
          }
        ],
        trendTimeUnit: "hour",
        tendencyCharts: {},
        trendChartCategory: ['load', 'cpu', 'ram', 'disk', 'network', 'energy', 'temperature', 'job']
      }
    },
    props: [
      "currentSelectedGroupId"
    ],
    components: {
      "trend-chart": TrendChart
    },
    methods: {
      onTrendTimeIntervalChange(){
        // Do nothing
      }
    }
  }
</script>
