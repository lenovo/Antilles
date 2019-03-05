<style>
   .node-gpu-chart{
       width: 100%;
       height: 100%;
       border: 1px solid #eee;
       box-sizing: border-box
   }
   .HealthChartPage{
   }
</style>

<template>
  <div ref="container" class="node-gpu-chart"></div>
</template>

<script type="text/javascript">
  import ECharts from 'echarts'
  export default {
    data() {
      return {
        innerChart: null,
        nodeGpus:{
          id: 0,
          hostname: '',
          values: [],
          used: []
        },
        type: 'util',
        range: [0, 0],
        barColors: ['#33AAFF', '#d9eeff'],
        series_data_max : [],
        fixed_bar_width : 20
      }
    },
    props: [
      "node",
      "valueType",
      "valueRange",
      "isReversal"
    ],
    watch: {
      node(val, oldVal) {
        this.init_data();
        this.init_chart();
      },
      valueRange(val, oldVal) {
        this.range = val;
        this.init_chart();
      },
      isReversal(val, oldVal) {
        // this.barColors = val?['#afd5ff', '#33AAFF']:['#33AAFF', '#afd5ff'];
        this.init_chart();
      }
    },
    mounted() {
      this.$nextTick(() => {
        this.init_data();
        this.innerChart = ECharts.init(this.$refs.container);
        window.removeEventListener('resize', this.onResize);
        window.addEventListener('resize', this.onResize);
        this.onResize();
        this.init_chart();
      })
    },
    beforeDestroy() {
      window.removeEventListener('resize', this.onResize);
    },
    methods: {
      init_data() {
        this.nodeGpus = this.node;
        this.nodeGpus.values.forEach((value, index) => {
          if(value) {
            this.nodeGpus.values[index] = value.toFixed(0);
          } else {
            this.nodeGpus.values[index] = 0;
          }
        })
        this.series_data_max = this.modifyGapData(this.nodeGpus.values);
        this.type = this.valueType || this.type;
        this.range = this.valueRange;
        var arrayLength = this.nodeGpus.values.length;
      },
      onResize() {
          this.innerChart.resize();
      },
      init_chart(){
        var $this = this;
        var option = {
          title: {
              text: $this.nodeGpus.hostname,
              textStyle: {
                fontSize: 12,
                fontWeight: 500,
                fontFamily: "Microsoft YaHei",
                color: "#666666",
              },
          },
          tooltip: {
              trigger: 'axis',
              axisPointer: {
                  type: 'shadow'
              },
              formatter: function(p) {
                var util = $this.$t(`NodeGpus.Monitor.Chart.${$this.type}`, {'value': p[1].data})
                return `GPU ${p[1].dataIndex}<br />${util}`
              }
          },
          grid: {
              left: '20px',
              top:'40px',
              bottom: '20px',
              right: '20px'
          },
          yAxis: {
              show:false,
              type: 'value',
              name: 'Days',
              axisLabel: {
                  formatter: '{value}'
              }
          },
          xAxis: [
            {
              type: 'category',
              data: $this.nodeGpus.used,
              show: false
            },
            {
              type: 'category',
              data: $this.nodeGpus.used,
              axisTick: {show: false},
              axisLine: {show: false},
              axisLabel: {
                width: 10,
                formatter: function (value) {
                    return '{' + value + '|}';
                 },
                margin: 0,
                interval: 0,
                rich: {
                  value: {
                    lineHeight: 10,
                    align: 'center'
                  },
                  '1': {
                    height: 5,
                    width: $this.fixed_bar_width,
                    align: 'center',
                    backgroundColor: '#6bcb01',
                  },
                  '0': {},
                }
              }
            }
          ],
          series: [
              {
                  type: 'bar',
                  itemStyle: {
                      normal: {color: 'rgba(0,0,0,0.05)'}
                  },
                  barGap:'-100%',
                  barCategoryGap:'50',
                  barWidth: String($this.fixed_bar_width)+'px',
                  data: $this.series_data_max,
                  animation: false
              },
              {
                  // name: 'GPU usage(%)',
                  type: 'bar',
                  data: $this.nodeGpus.values,
                  label: {
                      normal: {
                          formatter: function(val) {

                            if($this.reversal(val)) {
                              return val.data;
                            } else {
                              return '';
                            }
                          },
                          show: true,
                          position: "insideTop",
                          textColor:"#333",
                          textBorderColor: '#333',
                          textBorderWidth: 0
                      }
                  },
                  barWidth: String($this.fixed_bar_width)+'px',
                  itemStyle: {
                      normal: {
                          color: function(val) {
                              if($this.reversal(val)) {
                                  return $this.barColors[0]
                              } else {
                                  return $this.barColors[1]
                              }

                          },
                          shadowBlur: 10,
                          shadowColor: '#fff'
                      },
                      emphasis: {
                          shadowBlur: 10,
                          shadowColor: 'rgba(0, 0, 0, 0.5)'
                      }
                  },
              },
          ]
        };

        $this.innerChart.setOption(option);
      },
      reversal(val) {
        var isShowLabel = val.data >= this.range[0] && val.data <= this.range[1];
        if(this.isReversal) {
          isShowLabel = val.data <= this.range[0] || val.data >= this.range[1];
        }
        return isShowLabel;
      },
      modifyGapData(values) {
        var arr = [];
        values.forEach((item) => {
          arr.push(100);
        })
        return arr;
      }
    }
  }
</script>
