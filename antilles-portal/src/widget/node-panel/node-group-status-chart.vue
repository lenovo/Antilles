<style lang="css">
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
        nodeStatus: null,
        nodeStatusColor: {
          busy: '#63B1D8',
          off: '#D4DFE2',
          free: '#94E8FB',
          running: '#82C9EE'
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
          var counts = this.processChartYCountData(this.initData.status)
          this.nodeStatus = {
            groups: {
              labels: this.processChartYLabelData(this.initData.group),
              counts: counts
            },
            status:this.processChartValueData(this.initData.status, counts)
          }
          this.draw(this.initData);
        }

      },
      draw(data) {
        var $this = this
        var option = {
            title: {
              text: this.$t('Dashboard.NodeGroupStatus.Chart.Title'),
              left: 'left',
              textStyle: {
                fontSize: '14',
                color: '#333',
                fontWeight: '100',
                fontFamily: 'Micsoft Yahei'
              }
            },
            tooltip : {
                trigger: 'axis',
                axisPointer : {
                    type : 'shadow'
                },
                textStyle: {
                  fontFamily: 'Micsoft Yahei'
                },
                formatter: function(a) {
                    var name = a[0].name
                    var num = 0 ;
                    var str = name
                    $this.nodeStatus.groups.labels.forEach((item, index) => {
                        if(item == name) {
                            num = index
                        }
                    })
                    for(var item in $this.nodeStatus.status){
                      var status = $this.$t('Dashboard.NodeGroupStatus.Chart.' + item.replace('_',''))
                        str+="<br />" + status + ": " + $this.initData.status[item][num]
                    }
                    return str
                }
            },
            legend: {
                top: 'top',
                right: '20px',
                textStyle: {
                  fontFamily: 'Micsoft Yahei'
                },
                data: (function (data) {
                  var legend = []
                  for (var key in data) {
                    legend.push($this.$t('Dashboard.NodeGroupStatus.Chart.' + key.replace('_','')))
                  }
                  return legend;
                })(this.nodeStatus.status)
            },
            grid: {
                top:'20%',
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis:  {
              name: '(%)',
              nameTextStyle: {
                padding: [25, 0, 0, 0]
              },
              show: true,
              type: 'value',
              splitLine: {
                show: false
              },
              axisLabel: {
                fontFamily: 'Micsoft Yahei'
              },
              interval: 10,
              // axisLabel: {
              //     formatter: '{value}%'
              // },
              max: 100
            },
            yAxis: (function (data) {
              var y = [];
              for (var item in data) {
                y.push({
                    type: 'category',
                    axisLine: {
                      show: false
                    },
                    axisTick: {
                      show: false
                    },
                    axisLabel: {
                      margin: 20,
                      fontFamily: 'Micsoft Yahei'
                    },
                    data: data[item]
                })
              }
              return y;
            })(this.nodeStatus.groups),
            series: (function (data) {
              var series = [];
              for (var key in data) {
                series.push({
                    name: $this.$t('Dashboard.NodeGroupStatus.Chart.' + key.replace('_','')),
                    type: 'bar',
                    stack: 'bar',
                    label: {
                        normal: {
                            show: false,
                            position: 'insideRight'
                        }
                    },
                    itemStyle: {
                        normal : {
                            color: $this.nodeStatusColor[key.replace('_','')]
                        }
                    },
                    data: data[key]
                })
              }
              return series;
            })(this.nodeStatus.status)
        };
        this.innerChart.setOption(option);
      },
      processChartYCountData(data) {

        // var arr = [0, 0, 0, 0, 0, 0];
        var arr = [0, 0, 0, 0];
        for (var key in data) {
          data[key].forEach((item, index) => {
            arr[index] += item
          })
        }
        return arr;
      },
      processChartYLabelData(groups) {
        var data = [];
        groups.forEach((item, index) => {
          index<=3?data.push(this.$t('Dashboard.NodeGroupStatus.Group.'+ item)):'';
        })
        return data;
      },
      processChartValueData(data, count) {
        var obj = {};
        for (var key in data) {
          var arr = [];
          data[key].forEach((item, index) => {
            var num = count[index]==0?0:item/count[index]*100;
            arr.push(num)
          })
          obj[key] = arr;
        }
        return obj;
      }

    }

}
</script>
