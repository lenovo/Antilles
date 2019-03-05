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
      memory: [],
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
      this.setOption();
      this.onResize();
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
      var values = [];
      if(data.length > 0) {
        this.showChart = true
        data.forEach(t => {
          let time = t.time
          let value = t.values[0]
          values.push({'value':[time, value]});
        })
        this.memory = values
        this.setOption();
      } else {
        this.showChart = false
      }
    },
    setOption() {
      var self = this
      var option = {
          title: {
              text: self.$t('NodeDetail.Memory.Title') + ' (%)',
              textStyle: {
                  fontSize: 14,
                  color: "#333333",
              },
              padding: [10, 5]
          },
          grid: {
            top: 40,
            bottom: 30,
            left: 40,
            right: 30
          },
          tooltip: {
              trigger: 'axis',
              formatter: function (params) {
                var o = params[0]
                var time = o.value[0]
                return `${Format.formatDateTime(time, 'hh:mm MM-dd')}<br>
                        ${o.marker}${o.seriesName} : ${o.value[1]}%
                        `;
              }
          },
          /*
          legend: {
            top: 'top',
            right: '20px',
            data: ['CPU', 'LOAD']
          },
          */
          xAxis: {
            type: 'time',
            splitLine: {
              show: false
            },
            axisLine: {
              lineStyle: {
                color: '#AAAAAA'
              }
            },
            axisLabel: {
              color: '#999999',
              formatter: function(value){
                return Format.formatDateTime(new Date(value), 'hh:mm');
              }
            },
            axisTick: {
              show: false
            }
          },
          yAxis: {
              name: '',
              type: 'value',
              axisLine: {
                  lineStyle: {
                      color: '#AAAAAA'
                  },
                  show: false
              },
              axisTick: {
                show: false
              },
              min: 0,
              max: 100
          },
          color: ['#5fb4f9'],
          series: [{
              name: self.$t('NodeDetail.Memory.Title'),
              type: 'line',
              // yAxisIndex: 0,
              showSymbol: false,
              data: self.memory,
              itemStyle: {
                  normal: {
                      lineStyle: {
                          color: '#5fb4f9'
                      },
                      areaStyle: {
                          type: 'default',
                          color: '#edf7ff'
                      }
                  }
              }
          }]
      };
      this.innerChart.setOption(option);
    },
  }
}
</script>
