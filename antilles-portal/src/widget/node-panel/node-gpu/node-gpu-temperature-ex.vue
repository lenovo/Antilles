<style lang="css">

</style>
<template lang="html">
  <div ref="container" class="node-monitor-chart-style" v-show="showChart"></div>
</template>

<script>
import Format from './../../../common/format'
import ECharts from 'echarts'
import GpuService from '../../../service/monitor-data'
export default {
  data() {
    return {
      innerChart: null,
      temperature: '-',
      showChart: true
    }
  },
  props: ['gpuData'],
  watch: {
    gpuData(val, oldVal) {
      this.processData(val)
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.innerChart = ECharts.init(this.$refs.container);
      window.removeEventListener('resize', this.onResize);
      window.addEventListener('resize', this.onResize);
      this.processData(this.gpuData);
      this.onResize();
      this.setOption();
    });
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResize);
  },
  methods: {
    onResize() {
      this.innerChart.resize();
    },
    processData(data) {
      if(data != ''&& !isNaN(Number(data))) {
        this.showChart = true
        this.temperature = data
        if(this.temperature%1 != 0) {
          this.temperature = this.temperature.toFixed(2);
        }
        this.setOption();
      } else {
        this.showChart = false
      }
    },
    setOption() {
      var $this = this;
      var option = {
        title: {
          text: this.$t('Node.Temp.Chart.title'),
          // left: 'left',
          // x: 10,
          // y: 10,
          textStyle: {
            fontSize: 14,
            color: "#333333"
          }
        },
        series: [
        {
          type: 'gauge',
          center: ['50%', '70%'],
          radius: '85%',
          detail: {
            color: '#5FB4F9',
            // formatter:'{value}℃',
            formatter: function (value) {
              if($this.temperature || $this.temperature == 0 ) {
                return String($this.temperature) + '℃';
              } else {
                return this.$t('Node.Temp.Chart.Nodata');
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
                color: [[this.temperature/100, '#5FB4F9'], [1, '#F8F8F8']],
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
            value: this.temperature
          }
        }]
      };
      this.innerChart.setOption(option);
    },
  }
}
</script>
