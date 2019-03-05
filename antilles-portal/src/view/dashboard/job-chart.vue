<style lang="css">
</style>
<template lang="html">
<div id="tid_dashboard-job-chart" ref="container" style="width: 100%; height: 100%; min-height:200px;">JOB</div>
</template>

<script>
import Format from './../../common/format'
import ECharts from 'echarts'
export default {
  data() {
      return {
        innerChart: null,
        jobChartStatusColor: {
          running: '#5FB4F9',
          waiting: '#ADE3FA'
        }
      }
    },
    props: [
      'initData'
    ],
    watch: {
      initData(val, oldVal) {
        this.init();
      }
    },
    // mounted() {
    //   this.init();
    //
    // },
    mounted() {
      this.$nextTick(() => {
        this.innerChart = ECharts.init(this.$refs.container);
        window.removeEventListener('resize', this.onResize);
        window.addEventListener('resize', this.onResize);
        this.onResize();
        this.init();
        gApp.$watch('isCollapse', (newValue, oldValue) => {
          setTimeout(() => {
            this.onResize();
          },300)
        })
      });

    },
    beforeDestroy() {
      window.removeEventListener('resize', this.onResize);
    },
    methods: {
      onResize() {
        this.innerChart.resize();
      },

      init() {
        if(this.initData){
          var data = {
            data: {
              waiting: [],
              running: [],
            },
            time: []
          }
          this.initData.forEach((item) => {
            data.data.waiting.push(item.waiting);
            data.data.running.push(item.running);
            data.time.push(Format.formatDateTime(item.time));
          })
          this.draw(data);
        }

      },
      draw(data) {
        var $this = this
        var option = {
          tooltip : {
            trigger: 'axis',
            textStyle: {
              fontFamily: 'Micsoft Yahei'
            },
            axisPointer: {
                type: 'cross',
                label: {
                    backgroundColor: '#6a7985'
                }
            }
          },
          legend: {
              top: 'top',
              right: '20px',
              textStyle: {
                fontFamily: 'Micsoft Yahei'
              },
              data:(function (data) {
                var legend = []
                for (var key in data) {
                  legend.push($this.$t('Dashboard.JobChart.Status.' + key.replace('_','')))
                }
                return legend;
              })(data.data)
          },

          grid: {
              top:'30px',
              left: '3%',
              right: '6%',
              bottom: '3%',
              containLabel: true
          },
          xAxis : [
              {
                  type : 'category',
                  boundaryGap : false,
                  axisLabel: {
                    fontFamily: 'Micsoft Yahei',
                    formatter: function(value, index) {
                      return value.split(' ')[0] + '\n' + value.split(' ')[1];
                    },
                    // rotate: -45
                  },
                  data : data.time
              }
          ],
          yAxis : [
              {
                  type : 'value',
                  minInterval: 1,
                  axisLabel: {
                    fontFamily: 'Micsoft Yahei'
                  },
              }
          ],
          series : (function (data) {
            var series = [];
            for (var key in data) {
              key = key.replace('_','');
              series.push({
                  name:$this.$t('Dashboard.JobChart.Status.'+key),
                  type:'line',
                  stack: 'occupied',
                  areaStyle: {normal: {}},
                  itemStyle: {
                      normal : {
                          color: $this.jobChartStatusColor[key]
                      }
                  },
                  data: data[key]
              })
            }
            return series;
          })(data.data)
        };
        this.innerChart.setOption(option);
      }

    }

}
</script>
