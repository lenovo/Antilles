<style lang="css">

</style>
<template lang="html">
  <div ref="container" class="node-monitor-chart-style"></div>
</template>

<script>
import Format from './../../../common/format'
import ECharts from 'echarts'
export default {
  data() {
    return {
      innerChart: null,
      diskRate: {
      	used: 0,
      	total: 0
      }
    }
  },
  props: [
    'node'
  ],
  watch: {
    node(val, oldVal) {
      this.init();
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.innerChart = ECharts.init(this.$refs.container);
      window.removeEventListener('resize', this.resizeChart);
      window.addEventListener('resize', this.resizeChart);
      this.resizeChart();
      this.init();
      gApp.$watch('isCollapse', (newValue, oldValue) => {
        setTimeout(() => {
          this.resizeChart();
        },300)
      })
    });
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeChart);
  },
  methods: {
    resizeChart() {
      this.innerChart.resize();
    },

    init() {
      var $this = this;
      if (this.node == null || this.node == undefined || this.node == '') {
      	return
      }
      // this.diskRate.used = this.node.diskUsed == 0 ? 15.72 : this.node.diskUsed;
      // this.diskRate.total = this.node.diskTotal == 0 ? 0 : this.node.diskTotal;
      this.diskRate.used = this.node.diskUsed
      this.diskRate.total = this.node.diskTotal
      var option = {
        title: {
          text: this.$t('Node.Disk.Chart.Title'),
          //left: 'left',
          // x: 10,
          // y: 10,
          textStyle: {
            fontSize: 14,
            color: "#333333"
          },
          padding: [10, 5]
        },
        tooltip: {
          trigger: 'item',
          formatter: function (p) {
            return `${p.name}: ${Format.formatNumber(p.percent, 1)}%<br>
                    ${Format.formatByteSize(p.value)}
                    `
          }
        },
        // legend: {
        //   top: 'top',
        //   right: '20px',
        //   data: [this.$t('Node.Disk.Chart.Total'), this.$t('Node.Disk.Chart.Used')]
        // },
        series: [
          {
            type:'pie',
            center: ['50%', '55%'],
            radius: ['50%', '70%'],
            x: 'center',
            y: 'center',
            data:[
                {
                    name: this.$t('Node.Disk.Chart.Used'),
                    hoverAnimation: false,
                    value: this.diskRate.used,
                    label: {
                      normal : {
                          show : true,
                          formatter:function () {
                            return Format.formatByteSize($this.diskRate.total);
                          },
                          position : 'center',
                          textStyle: {
                              color : '#333333',
                              fontSize : 18
                          }
                      },
                      emphasis: {
                          color: '#04A7ED'
                      }
                    },
                    labelLine : {
                        show : false
                    },
                    itemStyle: {
                      color: '#04A7ED',

                    }

                },
                {
                    name: this.$t('Node.Disk.Chart.Total'),
                    hoverAnimation: false,
                    value:this.diskRate.total-this.diskRate.used,
                    itemStyle: {
                        normal: {
                            color: '#EFF1F3',
                            label: {
                                show :false,
                            },
                            labelLine : {
                                show : false
                            }
                        },
                        emphasis: {
                            color: '#EFF1F3'
                        }
                    }

                }
            ]
          }
        ]
      };
      this.innerChart.setOption(option);
    },


  }
}
</script>
