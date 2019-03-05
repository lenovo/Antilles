<style lang="css">
  .node-satus-chart {
    height: 100%;
  }
</style>
<template lang="html">
  <div class="height--100 p-20 dashboard-backgroud-color">
    <div ref="container" style="width: 100%; height: 100%;"></div>
  </div>
</template>

<script>
import ECharts from 'echarts'
export default {
  data() {
    return {
      innerChart: null,
      nodeStatus: null
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
  // mounted() {
  //   this.init();
  // },
  mounted() {
    this.$nextTick(() => {
      this.innerChart = ECharts.init(this.$refs.container);
      window.removeEventListener('resize', this.onResize);
      window.addEventListener('resize', this.onResize);
      this.onResize();
      this.init();
      gApp.$watch('isCollapse',(newValue, oldValue) => {
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
      var $this = this
      this.nodeStatus = this.node
      var option = {
        title: {
          text: this.$t('Dashboard.NodeStatus.Chart.Title', {'count': $this.nodeStatus.on + $this.nodeStatus.off}),
          left: 'left',
          textStyle: {
            fontSize: '14',
            color: '#333',
            fontWeight: '100',
            fontFamily: 'Micsoft Yahei'
          }
        },
        tooltip: {
          trigger: 'item',
          textStyle: {
            fontFamily: 'Micsoft Yahei'
          },
          formatter: "{b}: {c} ({d}%)"
        },
        legend: {
          top: 'bottom',
          right: '0',
          textStyle: {
            fontFamily: 'Micsoft Yahei'
          },
          data: [this.$t('Dashboard.NodeStatus.On'), this.$t('Dashboard.NodeStatus.Off')]
        },
        series: [
          {
            type:'pie',
            center : ['50%', '50%'],
            radius: ['50%', '70%'],
            x: 'center',
            y: 'center',
            avoidLabelOverlap: false,
            label: {
              show: false,
            },
            labelLine: {
              show: false,
            },
            data:[
                {
                    name: this.$t('Dashboard.NodeStatus.On'),
                    hoverAnimation: false,
                    value: this.nodeStatus.on,
                    itemStyle: {
                        normal : {
                            color: '#04A7ED',
                            label : {
                                show : false,
                                formatter:function () {
                                  return $this.nodeStatus.on + $this.nodeStatus.off;
                                },
                                position : 'center',
                                textStyle: {
                                    color : '#333333',
                                    fontSize : 18
                                }
                            },
                            labelLine : {
                                show : false
                            }
                        },
                        emphasis: {
                            color: '#04A7ED'
                        }
                    }

                },
                {
                    name: this.$t('Dashboard.NodeStatus.Off'),
                    hoverAnimation: false,
                    value:this.nodeStatus.off,
                    itemStyle: {
                        normal: {
                            color: '#EFF1F3',
                            label: {
                              show : false,
                              formatter:function () {
                                return $this.nodeStatus.on + $this.nodeStatus.off;
                              },
                              position : 'center',
                              textStyle: {
                                  color : '#333333',
                                  fontSize : 18
                              }
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
