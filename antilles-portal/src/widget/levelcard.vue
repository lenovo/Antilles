<style>
   .level-card {
     width: 300px;
     height: 50px;
     left: 20px;
     bottom: 7px;
   }
</style>
<template>
  <div ref="levelcard" class="level-card" v-show="this.mode != 'common'"></div>
</template>
<script type="text/javascript">
  import EChart from 'echarts'
  export default {
    data() {
      return {
        chartObj: {},
        min_value : ['0'],
        // max_value : ['∞'],
        max_real : 100,
        levels : [],
        series_data : [],
        // color_level: ['#F6EFA6', '#EFD79B', '#E9BF8F', '#E2A684', '#DB8E79', '#D57B6F', '#D06D66', '#CA605D', '#C55255', '#BF444C'],
        // min_max: [[0,10],[10,20],[20,30],[30,40],[40,50],[50,60],[60,70],[70,80],[80,90],[90,100]],
        color_level: [],
        min_max: []
      }
    },
    props: ["colors", "ranges", "mode"],
    mounted() {
        this.chartObj = EChart.init(this.$refs.levelcard);
        this.color_level = this.colors;
        for (var i=0;i<this.color_level.length;i++){
            this.series_data.push([i,0,i+1]);
            this.levels.push(String('level'+String(i+1)));
        }
        this.drawLevelCard(this.mode)
    },
    watch: {
      mode(newVal) {
        this.drawLevelCard(newVal)
      }
    },
    computed:{
      max_value(){
        if (this.mode=="temp"){
          return ["100℃+"]
        } else if (this.mode=="energy"){
          return ["2000W+"]
        } else if(this.mode=="load"||this.mode=="job"){
          return ["100+"]
        }else if (this.mode=="cpu"||this.mode=="storage"||this.mode=="mem"){
          return ["100%"]
        }else if (this.mode=="network") {
          return ["50Gbps+"]
        }else {
          return [""]
        }
      }
    },
    methods: {
      drawLevelCard(mode) {
        if (mode == 'common') {
          return
        }
        var min = Number(this.ranges[mode][0])
        var max = Number(this.ranges[mode][1])
        var dict = {
          cpu: ' %',
          load: '',
          mem: ' %',
          storage: ' %',
          temp: ' ℃',
          energy: ' W',
          network: ' Mbps',
          job: ''
        }
        var unit = dict[mode]
        let options = this.getChartOption(min, max, unit,mode);
        this.chartObj.setOption(options);
      },
      getChartOption(min, max, unit,mode){
        var self = this
        let option = {
          tooltip: {
            position: 'top',
            formatter: function (value) {
              var index = Number(value['dataIndex'])
              var a = min + (max - min) / 10 * index
              var b = min + (max - min) / 10 * (index + 1)
              var result = ""
              if (mode=='network'){
                if (index==9){
                  result="≥"+`${a/1000}${'Gbps'}`
                }else {
                  result=`${a/1000}${'Gbps'} - ${b/1000}${'Gbps'}`
                }
              }
              else {
                if (index==9) {
                  if (mode=='temp'||mode=='energy'||mode=='load'||mode=='job'){
                    result="≥"+`${a}${unit}`
                  } else {
                    result=`${a}${unit} - ${b}${unit}`
                  }
                } else {
                  result=`${a}${unit} - ${b}${unit}`
                }
              }
              return result
            },
          },
          animation: false,
          grid: {
            height: '42%',
            left: '4%',
            right: '20%',
            y: '55%'
          },
          xAxis: {
            type: 'category',
            data: this.levels,
            splitArea: {
                show: true
            },
            show:false
          },
          yAxis: [{
            type: 'category',
            data: this.min_value,
            axisTick: {show: false},
            axisLine: {show: false},
            axisLabel: {
              margin: 5,
              fontFamily: 'Micsoft Yahei'
            },
          },
          {
            type: 'category',
            data: this.max_value,
            axisTick: {show: false},
            axisLine: {show: false},
            axisLabel: {
              margin:5,
              fontFamily: 'Micsoft Yahei'
            },
          }
          ],
          visualMap: {
            min: 0,
            max: 10,
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            show: false,
            bottom: '15%',
            inRange:{color: this.color_level}
          },
          series: [{
                name: 'Color Card',
                type: 'heatmap',
                data: this.series_data,
                label: {
                    normal: {
                        //show: true
                        show: false
                    }
                },
                itemStyle: {
                   emphasis: {
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        };
        return option;
      }
    }
  }
</script>
