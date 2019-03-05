<style scoped>
</style>
<template>
<div ref="container" class="node-monitor-chart-style"></div>
</template>
<script>
import ECharts from 'echarts'
import MonitorDataService from '../../../service/monitor-data'
import Format from '../../../common/format'

export default {
	data() {
		return {
      innerChart: null,
      autoRefresh: setInterval(this.refresh, this.interval)
    }
	},
	props: [
		'nodeId',
    'interval'
	],
	watch: {
    nodeId(val, oldVal) {
    	this.clear();
      this.refresh();
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.innerChart = ECharts.init(this.$refs.container);
      window.removeEventListener('resize', this.resizeChart);
      window.addEventListener('resize', this.resizeChart);
      this.resizeChart();
      this.init();
      this.refresh();
      gApp.$watch('isCollapse', (newValue, oldValue) => {
        setTimeout(() => {
          this.resizeChart();
        },300)
      })
    });
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeChart);
    clearInterval(this.autoRefresh)
  },
	methods: {
    resizeChart() {
      this.innerChart.resize();
    },
    init() {
      var option = {
				tooltip: {
					trigger: 'axis',
					formatter: function (params) {
						var a = params[0]
						var b = params[1]
						var time = a.value[0]
						return `${Format.formatDateTime(time, 'hh:mm MM-dd')}<br>
										${a.marker}${a.seriesName} : ${a.value[1]}MB/s<br>
										${b.marker}${b.seriesName} : ${b.value[1]}MB/s
										`;
					}
				},
				grid: {
          top: 40,
          bottom: 30,
          left: 50,
          right: 30
        },
        title: {
          text: this.$t('NodeDetail.Network') + ' (MB/s)',
          textStyle: {
            fontSize: 14,
            color: "#333333"
          },
					padding: [10, 5]
        },
        /*
        legend: {
        	x: 'right',
          data: [
          	{
          		name: this.$t('NodeDetail.Network.In'),
          		icon: 'stack'
          	},
          	{
          		name: this.$t('NodeDetail.Network.Out'),
          		icon: 'stack'
          	}
          ]
        },
        */
        xAxis: {
          type: 'time',
          axisLabel: {
						formatter: function(value) {
							value = new Date(value);
							var hours = value.getHours();
							var minutes = value.getMinutes();
							if (hours < 10) hours = '0' + hours;
							if (minutes < 10) minutes = '0' + minutes;
							return hours + ':' + minutes;
						}
          },
          splitLine: {
            show: false
          },
          axisLine: {
          	lineStyle: {
          		color: '#AAAAAA'
          	}
          },
          axisTick: {
            show: false
          }
        },
        yAxis:{
          name: '',
          axisLine: {
          	lineStyle: {
              color: '#AAAAAA'
            },
          	show: false
          },
          axisTick: {
            show: false
          }
        },
        series: [{
          name: this.$t('NodeDetail.Network.In'),
          type: 'line',
					symbol:'none',
					smooth: true,
          data: this.netInData,
          itemStyle: {
          	normal: {
          		lineStyle: {
          			shadowBlur: 6,
								shadowColor: "#ff4069",
								color: "#ff4069",
                width: 1
          		},
							color: "#ff4069",
          	}
          }
        },
        {
        	name: this.$t('NodeDetail.Network.Out'),
					type: 'line',
					symbol:'none',
					smooth: true,
          data: this.netOutData,
          itemStyle: {
          	normal: {
          		lineStyle: {
          			color: '#40aaff',
          			shadowBlur: 6,
          			shadowColor: '#40aaff',
          			width: 1
          		},
							color: '#40aaff',
          	}
          }
        }]
      };
      this.innerChart.setOption(option);
    },
    parseNetIn(timeSeriesItem) {
    	return {
    		value: [
    			timeSeriesItem.time,
    			timeSeriesItem.values[0]
    		]
    	}
    },
    parseNetOut(timeSeriesItem) {
    	return {
    		value: [
    			timeSeriesItem.time,
    			timeSeriesItem.values[1]
    		]
    	}
    },
    parseTime(time) {
    	var hours = time.getHours();
    	var minutes = time.getMinutes();
    	var seconds = time.getSeconds();
    	if (hours < 10) hours = '0' + hours;
    	if (minutes < 10) minutes = '0' + minutes;
    	if (seconds < 10) seconds = '0' + seconds;
    	return hours + ':' + minutes + ':' + seconds;
    },
    clear() {
      this.innerChart.setOption({
        series: [{
          data: []
        },{
          data: []
        }]
      });
    },
    refresh() {
    	if (this.nodeId > 0) {
        var getNetworkData = MonitorDataService.getNodeDataByHour(this.nodeId, 'network', 1);
        Promise.all([getNetworkData]).then((res) => {
    			var netInData = [];
      		var netOutData = [];
      		res[0].data.forEach((item) => {
      			netInData.push(this.parseNetIn(item));
      			netOutData.push(this.parseNetOut(item));
      		});
      	  this.innerChart.setOption({
            series: [{
              data: netInData
            },{
              data: netOutData
            }]
          });
          let self = this;
        }, (res)=> {
          this.$message.error(res);
        });
      }
    }
  }
}
</script>
