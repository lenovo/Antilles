<style>
   .HealthChart{
     width:100%;
     height:600px;
   }
   .HealthChartPage{
     float: right;
     margin-right: 10%;
   }
  .health-chart_level-card{margin-left: 50%;transform: translateX(-50%);margin-bottom: 3%}
</style>
<template>
  <el-row>
    <el-col :span="22" :offset="1">
      <div :id="healthCategory+'HealthChart'" class="HealthChart"></div>
      <level-card
        class="health-chart_level-card"
        :colors="levelColors"
        :ranges="levelRanges"
        :mode="mode[healthCategory]">
      </level-card>
      <div class="HealthChartPage" v-if="totalDataNum > 0">
        <el-pagination id="tid_health-chart-page"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[200, 400, 800, 1000]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalDataNum">
        </el-pagination>
      </div>
      <node-detail-dialog id="tid_node-detail-dialog" ref="detailDialog"></node-detail-dialog>
    </el-col>
  </el-row>
</template>
<script>
  import EChart from 'echarts'
  import MonitorDataService from '../../../service/monitor-data'
  import NodeDetailDialog from '../../../widget/nodes-table/node-detail-dialog'
  import LevelCard from '../../../widget/levelcard'
  export default {
    components: {
      'node-detail-dialog': NodeDetailDialog,
      'level-card':LevelCard
    },
    data() {
      return {
        healthChartObj: {},
        xRatioInitValue:3,
        yRatioInitValue:2,
        currentPage: 1,
        totalDataNum: 0,
        pageSize: 200,
        setTimeoutId: 0,
        refreshIntervalValue: 30*1000,
        heatDataSet: [],
        mode:{
          'temperature':'temp',
          'energy':'energy',
          'load':'load',
          'cpu':'cpu',
          'ram':'mem',
          'disk':'storage',
          'network':'network',
          'job':'job'
        },
        levelRanges: {
          temp: [0, 100],
          energy: [0, 2000],
          load: [0, 100],
          cpu: [0, 100],
          mem: [0, 100],
          storage: [0, 100],
          network: [0, 50000],
          job: [0,100]
        },
        levelColors: ['#F6EFA6', '#EFD79B', '#E9BF8F', '#E2A684', '#DB8E79', '#D57B6F', '#D06D66', '#CA605D', '#C55255', '#BF444C'],
      }
    },
    props: [
      "healthCategory",
      "groupId"
    ],
    mounted(){
      this.$nextTick(() => {
        this.healthChartObj = EChart.init(document.getElementById(this.healthCategory+'HealthChart'));
        this.fetchHeatChartData(this.groupId, this.healthCategory);
        window.removeEventListener('resize', this.onResize);
        window.addEventListener('resize', this.onResize);
        let self = this;
        this.healthChartObj.on('click', function (params) {
          self.$refs.detailDialog.showDetail(params.data.id);
        });
      })
    },
    beforeDestroy() {
      window.removeEventListener('resize', this.onResize);
      if(this.setTimeoutId > 0)
        clearTimeout(this.setTimeoutId);
    },
    watch:{
      "groupId": function (newGroupId) {
        if (this.healthChartObj) {
          this.healthChartObj.clear();
        }
        this.fetchHeatChartData(newGroupId, this.healthCategory);
      },
      "healthCategory": function (newCategory) {
        if (this.healthChartObj) {
          this.healthChartObj.clear();
        }
        this.fetchHeatChartData(this.groupId, newCategory);
      }
    },
    methods: {
      fetchHeatChartData(groupId, category){
        if(this.setTimeoutId > 0)
          clearTimeout(this.setTimeoutId);
        MonitorDataService.getGroupHeatData(groupId, category).then((res) => {
          this.heatDataSet = res.data;
          // if(this.heatDataSet.length>0){
            this.totalDataNum = this.heatDataSet.length;
            let currentHeatData = this.getInterceptDataByPage();
            this.drawHeatChart(currentHeatData);
          // }
          this.refreshHealthChartData();
        }, (res) => {
          // Do nothing
        })

      },
      refreshHealthChartData(){
        let _this = this;
        _this.setTimeoutId = setTimeout(function(){
          _this.fetchHeatChartData(_this.groupId, _this.healthCategory)
        }, _this.refreshIntervalValue);
      },
      getInterceptDataByPage(){
        let startIndex = this.pageSize * (this.currentPage - 1);
        let endIndex = this.pageSize * this.currentPage;
        // console.log('startIndex, endIndex', startIndex, endIndex);
        let dataSet = this.heatDataSet.slice(startIndex, endIndex);
        return dataSet;
      },
      onResize(){
        this.healthChartObj.resize();
      },
      drawHeatChart(dataSet){
        let axisLen = this.autoAllocationAxisLength(dataSet);
        if (dataSet.length > 0) {
          var series = this.getSeriesData(dataSet, axisLen);
          var options = this.getChartOption(series.seriesData, series.minValue, series.maxValue, axisLen);
        } else {
          var options = this.getChartOption([], 0, 0, axisLen);
        }
        this.healthChartObj.setOption(options);
      },
      autoAllocationAxisLength(dataSet){
        var xAxisLen = 0
        var yAxisLen = 0
        var ps = this.pageSize
        if (ps == 200) {
          xAxisLen = 20
          yAxisLen = 10
        } else if (ps == 400) {
          xAxisLen = 20
          yAxisLen = 20
        } else if (ps == 800) {
          xAxisLen = 40
          yAxisLen = 20
        } else {
          xAxisLen = 40
          yAxisLen = 25
        }
        return {
          xAxisLen,
          yAxisLen
        }
      },
      getSeriesData(dataSet, axisLen){
          let xAxisMaxLength = axisLen.xAxisLen;
          let yAxisMaxLength = axisLen.yAxisLen;
          let seriesData = [];
          let xAxis = 0;
          let yAxis = 0;
          let tempArray = [];
          dataSet.map((ds, index) => {
            xAxis = parseInt(index%xAxisMaxLength);
            yAxis = yAxisMaxLength - 1 - parseInt(index/xAxisMaxLength);
            let value = ds.value == null ? -99 : ds.value;
            tempArray.push(value);
            seriesData.push({
              name:this.$t("Trend.Chart.Title." + this.healthCategory),
              value: [xAxis, yAxis, value],
              id: ds.id,
              hostname: ds.hostname
            })
          });

          if(xAxis>0 && xAxis<xAxisMaxLength-1){
            for(let x=xAxis+1; x<xAxisMaxLength; x++){
              seriesData.push([x,yAxis,"-"])
            }
            yAxis--;
          }
          for(let y=yAxis-1; y>=0; y--){
            for(let x=0;x<xAxisMaxLength;x++){
              seriesData.push([x,y,'-'])
            }
          }
          let minValue = Math.min.apply(null, tempArray);
          let maxValue = Math.max.apply(null, tempArray);
          minValue = minValue < 0 ? 0 : minValue;
          maxValue = maxValue < 0 ? 0 : maxValue;
          return {
            seriesData,
            minValue,
            maxValue
          };
      },
      getChartOption(seriesData, minValue, maxValue, axisLen){
        var self = this
        let option = {
          tooltip: {
            position: 'top',
            formatter: function (param) {
              let valueDisplay = param.data.value[2] + MonitorDataService.unitEnums[self.healthCategory];
              if(param.data.value[2] < 0) {
                valueDisplay = "-";
              }
              let ret = window.gApp.$t("Health.Chart.Tooltip.Hostname") + ": " + param.data.hostname + "<br/>"
              + param.name + ": " + valueDisplay;
              return ret;
            }
          },
          animation: false,
          grid: {
            bottom: 5,
            height: '85%',
            y: '10%'
          },
          xAxis: {
            type: 'category',
            data: (() => {
              let tmp = [];
              for(let i=1;i<=axisLen.xAxisLen;i++){
                tmp.push("");
              }
              return tmp;
            })(),
            splitLine: {
              show: true,
              lineStyle: {
                color: '#eeeeee',
                width: 1
              }
            },
            axisTick: {
                show: false
            },
            axisLine: {
              lineStyle: {
                color: '#AAAAAA'
              }
            }
          },
          yAxis: {
            type: 'category',
            data: (() => {
              let tmp = [];
              for(let i=1;i<=axisLen.yAxisLen;i++){
                tmp.push("");
              }
              return tmp;
            })(),
            splitLine: {
              show: true,
              lineStyle: {
                color: '#eeeeee',
                width: 1
              }
            },
            axisTick: {
              show: false
            },
            axisLine: {
              lineStyle: {
                color: '#AAAAAA'
              }
            },
          },
          visualMap: {
            show:false,
            min:this.levelRanges[this.mode[this.healthCategory]][0],
            max:this.levelRanges[this.mode[this.healthCategory]][1]
          },
          series: [{
            type: 'heatmap',
            data: seriesData,
            label: {
              normal: {
                formatter: function(data) {
                  if(data.data && data.data.value[2] < 0) {
                    return '';
                  }
                },
                show: true
              }
            },
            itemStyle: {
              emphasis: {
                shadowBlur: 10,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }]
        };
        return option;
      },
      handleSizeChange(newSize){
        if (this.healthChartObj) {
          this.healthChartObj.clear();
        }
        this.pageSize = newSize;
        let currentHeatData = this.getInterceptDataByPage();
        this.drawHeatChart(currentHeatData);
        // this.fetchHeatChartData(this.groupId, this.healthCategory)
      },
      handleCurrentChange(newPage){
        this.currentPage = newPage;
        // console.log("this.category", this.groupId, this.healthCategory);
        // this.fetchHeatChartData(this.groupId, this.healthCategory)
        let currentHeatData = this.getInterceptDataByPage();
        this.drawHeatChart(currentHeatData);
      }
    }
  }
</script>
