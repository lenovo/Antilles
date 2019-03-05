<style lang="css">

</style>
<template lang="html">
  <div ref="container" class="node-monitor-chart-style"></div>
</template>

<script>
import Format from './../../../common/format'
import ECharts from 'echarts'
import MonitorDataService from '../../../service/monitor-data'
export default {
  data() {
    return {
      innerChart: null,
      temperature: 0,
      autoRefresh: setInterval(this.refresh, this.interval)
    }
  },
  props: [
    'nodeId',
    'interval'
  ],
  watch: {
    nodeId(val, oldVal) {
      this.refresh()
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.innerChart = ECharts.init(this.$refs.container);
      window.removeEventListener('resize', this.resizeChart);
      window.addEventListener('resize', this.resizeChart);
      this.resizeChart();
      this.init();
      this.refresh()
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
    refresh() {
      var $this = this
      if (this.nodeId > 0) {
        MonitorDataService.getNodeDataByHour(this.nodeId, 'temperature', 1).then((res) => {
          res.data.forEach((item) => {
            // var curIndex = res.data.indexOf(item)
            // if (curIndex == res.data.length - 1) {
            //   this.temperature = item.values[0]
            // }
            this.temperature = res.current;
          });
          this.init();
          let self = this;
        }, (res) => {
          this.$message.error(res)
        })
      }
    },
    init() {
      var $this = this;
      var option = {
        title: {
          text: $this.$t('Node.Temp.Chart.title'),
          // left: 'left',
          // x: 10,
          // y: 10,
          textStyle: {
            fontSize: 14,
            color: "#333333"
          },
          padding: [10, 5]
        },
        series: [
        {
          type: 'gauge',
          center: ['50%', '70%'],
          radius: '85%',
          detail: {
            color: '#5FB4F9',
            formatter: function (value) {
              if($this.temperature || $this.temperature == 0 ) {
                return String($this.temperature) + '℃';
              } else {
                return $this.$t('Node.Temp.Chart.Nodata');
              };
            },
            offsetCenter: [0,'-22%'],
            fontSize: 14,
            textStyle: {
              fontSize: 17
            }
          },
          startAngle: 180,
          endAngle: 0,
          axisLine: {
            lineStyle: {
                color: [[$this.temperature/100, '#5FB4F9'], [1, '#F8F8F8']],
                width: 25
            }
          },
          splitLine: {
            show: false
          },
          axisTick: {
            show: false
          },
          axisLabel: {
            show: false
          },
          pointer: {
            show: false
          },
          data: {
            value: $this.temperature
          }
        }]
      };
      $this.innerChart.setOption(option);
    },
  }
}
</script>
