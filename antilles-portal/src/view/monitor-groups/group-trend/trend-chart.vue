<style>
  .TrendChart{
    width: 100%;
    height: 275px;
    border: 1px solid #eeeeee;
  }
</style>
<template>
  <div :id="tendencyCategory+'TrendChart'" class="TrendChart"></div>
</template>
<script>
  import ECharts from "echarts"
  import MonitorDataService from "../../../service/monitor-data"
  import Format from "../../../common/format"
  import ElCol from "element-ui/packages/col/src/col";

  export default {
    components: {ElCol},
    data(){
      return {
        dataFetcherMap: {
          'hour': MonitorDataService.getNodeGroupDataByHour,
          'day': MonitorDataService.getNodeGroupDataByDay,
          'week': MonitorDataService.getNodeGroupDataByWeek,
          'month': MonitorDataService.getNodeGroupDataByMonth
        },
        trendChartObj: {},
        nextStartTime: 0,
        setTimeoutId: 0,
        timeoutValue: 10*1000,
        axisData: {
          xAxis: [],
          yAxis: []
        },
        maxValueNum: 120,
        chartName: {}
      }
    },
    props:[
      "groupId",
      "tendencyCategory",
      "timeUnit",
      "chartTitle"
    ],
    watch: {
      "groupId": function (curGroupId) {
        this.fetchChartData(curGroupId, this.timeUnit);
      },
      "timeUnit": function (curTimeUnit) {
        this.fetchChartData(this.groupId, curTimeUnit);
      }
    },
    mounted(){
      this.$nextTick(() => {
        this.chartName = {
          'load': this.$t('Trend.Chart.Title.load'),
          'cpu': this.$t('Trend.Chart.Title.cpu') + " (%)",
          'ram': this.$t('Trend.Chart.Title.ram') + " (%)",
          'disk': this.$t('Trend.Chart.Title.disk') + " (%)",
          'network': this.$t('Trend.Chart.Title.network') + " (" + this.$t('Trend.Chart.Network.Unit') + ")",
          'energy': this.$t('Trend.Chart.Title.energy') + " (" + this.$t('Trend.Chart.Energy.Unit') + ")",
          'temperature': this.$t('Trend.Chart.Title.temperature') + " (\u2103)",
          'job': this.$t('Trend.Chart.Title.job')
        };
        this.trendChartObj = ECharts.init(document.getElementById(this.tendencyCategory+'TrendChart'));
        this.fetchChartData(this.groupId, this.timeUnit);
        window.removeEventListener('resize', this.onResize);
        window.addEventListener('resize', this.onResize);
      })
    },
    beforeDestroy() {
      window.removeEventListener('resize', this.onResize);
      if(this.setTimeoutId > 0)
        clearTimeout(this.setTimeoutId);
    },
    methods:{
      fetchChartData(groupId, timeUnit, startTime){
        if(this.setTimeoutId > 0)
          clearTimeout(this.setTimeoutId);
        if(!startTime){
          this.axisData.xAxis = [];
          this.axisData.yAxis = [];
        }
        let category = this.tendencyCategory.toLowerCase();
        let latestNum = 1;
        this.dataFetcherMap[timeUnit.toLowerCase()](groupId, category, latestNum, startTime).then((res) => {
          let dataSet = res.data;
          if(category == 'energy') {
            dataSet.forEach((ds) => {
              let energy = ds.values[0];
              if(energy && energy != '-') {
                ds.values[0] = Format.formatEnergy(energy, 1000);
              }
            });
          }
          // if(dataSet.length > 0){
            this.drawTrendCharts(dataSet);
            this.refreshChartData(groupId, timeUnit);
          // }
        }, (res) => {
          // Do nothing
        })
      },
      refreshChartData(groupId, timeUnit){
        let _this = this;
        _this.setTimeoutId = setTimeout(function(){
          // _this.fetchChartData(groupId, timeUnit, _this.nextStartTime);
          _this.fetchChartData(groupId, timeUnit);
        }, _this.timeoutValue);
      },
      onResize(){
        this.trendChartObj.resize();
      },
      drawTrendCharts(dataSet){
        let tendencyChart = this.trendChartObj;
        this.getAxisData(dataSet);
        let series = this.getChartSeries();
        let options = this.getEChartOption(series);
        tendencyChart.setOption(options);
      },
      getAxisData(dataSet){
        let yDataSet = [];
        dataSet.forEach((ds) => {
          // if(this.axisData.xAxis.length > this.maxValueNum)
          //   this.axisData.xAxis.shift();
          this.nextStartTime = ds.time;
          this.axisData.xAxis.push(ds.time);
          yDataSet.push(ds.values);
        });
        this.getYAxisFromDataSet(yDataSet);
      },
      getYAxisFromDataSet(yDataSet){
        let yAxis = [];
        if(!yDataSet || yDataSet[0] == null)
          return yAxis;
        var _this = this;
        for(let i=0; i<yDataSet[0].length; i++){
          let temp = [];
          yDataSet.forEach((d) => {
            // if(d[i] == null || d[i] == undefined)
            //   d[i] = 0;
            if(_this.axisData.yAxis[i] == undefined)
              _this.axisData.yAxis[i] = [];
            // if(_this.axisData.yAxis[i].length > this.maxValueNum)
            //   _this.axisData.yAxis[i].shift();
            _this.axisData.yAxis[i].push(d[i]);
          });
        }
      },
      getChartSeries(){
        let seriesData = [];
        let _yAxis = this.axisData.yAxis;
        let lineColor = ["#ff4069", "#40aaff"];
        if(this.tendencyCategory.toLowerCase() == 'network'){
          ["input", "output"].map((item, index) => {
            seriesData.push({
              name:this.$t("Trend.Chart.Title.Network." + item),
              type:'line',
              symbol:'none',
              smooth: true,
              itemStyle : {
                normal : {
                  lineStyle:{
                    shadowBlur: 6,
                    shadowColor: lineColor[index],
                    color: lineColor[index],
                    width: 1
                  },
                  color: lineColor[index]
                }
              },
              data: _yAxis[index]
            })
          });
        }else{
          seriesData.push({
            name:this.$t("Trend.Chart.Title." + this.tendencyCategory),
            type:'line',
            symbol:'none',
            smooth: true,
            itemStyle : {
              normal : {
                lineStyle:{
                  shadowBlur: 6,
                  shadowColor: '#f1f8fe',
                  color:'#40aaff',
                  width:1
                },
                color: '#40aaff'
              }
            },
            data: _yAxis[0]
          })
        }
        return seriesData;
      },
      getEChartOption(seriesData){
        var self = this
        let title = this.chartName[this.tendencyCategory]
        var options = {
          title: {
            text: title,
            textStyle:{
              fontSize:14,
              fontWeight:"normal"
            },
            padding:[20,10]
          },
          tooltip: {
            trigger: 'axis',
            formatter: function (params) {
              let timeFormat = "hh:mm MM-dd";
              if (params.length == 1) {
                var o = params[0]
                var formatedTime = Format.formatDateTime(new Date(o.name), timeFormat);
                var unit = self.tendencyCategory == 'energy'?'kW':MonitorDataService.unitEnums[self.tendencyCategory];
                return `${formatedTime}<br>
                        ${o.marker}${o.seriesName} : ${o.value}${unit}
                        `;
              }
  						var a = params[0]
  						var b = params[1]
              var formatedTime = Format.formatDateTime(new Date(a.name), timeFormat);
  						return `${formatedTime}<br>
  										${a.marker}${a.seriesName} : ${a.value}MB/s<br>
  										${b.marker}${b.seriesName} : ${b.value}MB/s
  										`;
  					}
          },
          grid : {
            left: 50,
            right: 25,
            bottom: 35
          },
          legend: {
            data:[],
            right:0
          },
          toolbox: {
            show: false
          },
          xAxis:  {
            type: 'category',
            boundaryGap: false,
            axisLine: {
              lineStyle: {
                color: '#AAAAAA'
              }
            },
            axisLabel: {
              textStyle: {
                color: '#999999'
              },
              formatter: function(value){
                var timeFormat = ['day', 'hour']
                if (timeFormat.includes(self.timeUnit.toLowerCase())) {
                  return Format.formatDateTime(new Date(value), 'hh:mm');
                } else {
                  return Format.formatDateTime(new Date(value), 'MM-dd');
                }
              }
            },
            axisTick: {
                show: false
            },
            data: this.axisData.xAxis
          },
          yAxis: {
            type: 'value',
            axisLine: {
              show: false
            },
            axisLabel: {
              formatter: '{value}',
              textStyle: {
                color: '#999999'
              }
            },
            axisTick: {
              show: false
            }
          },
          series:seriesData
        };
        if (this.tendencyCategory == 'job') {
          var values = seriesData[0].data.map(function (item) {
            if (item == '-') {
              return 0
            } else {
              return item
            }
          })
          var maxValue = Math.max.apply(null, values)
          if (maxValue < 5) {
            options.yAxis.max = 5
          } else {
            options.yAxis.max = null
          }
        }
        var percentOption = ['cpu', 'disk', 'ram']
        if (percentOption.includes(this.tendencyCategory)) {
          options.yAxis.min = 0
          options.yAxis.max = 100
        }
        return options;
      }
    }
  }
</script>
