<style media="screen">
.rackthumbnail {
}
.rackthumbnail-icon {
  background-image: url('./../asset/image/rack/rack-thumbnail.png');
  background-repeat: no-repeat;
  background-size: 100% 100%;
  cursor: pointer;
}
.box-text{
    text-align: center;
    position: relative;
    background-color : #F8F8F8;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>


<template>
  <div>
  <!-- <div>
    <p :style="getTittleStyle()">{{rackname}}</p>
  </div> -->
  <div v-popover:name class="rackthumbnail">
    <el-popover
      ref="name"
      placement="top-start"
      width="10"
      trigger="hover"
      >
      <div>
        <p :style="getTittleStyle()">{{rackName}}</p>
      </div>
    </el-popover>
    <el-badge :value="alarmCont" :max="99" class="alarmstatus-item">
      <div class="rackthumbnail-icon" :style="rackContainerStyle">
          <div :style="getInnerboxStyle()">
              <div :style="getTittleboxStyle()">
                <div class="box-text">
                  <div>
                    <p :style="getNodeInfoStyle()">{{nodes}}</p>
                    <p :style="getEnergyInfoStyle()">Nodes</p>
                  </div>
                </div>
              </div>
              <div :style="getTittleboxStyle()">
                <div  class="box-text">
                    <div>
                      <p :style="getNodeInfoStyle()">{{formatEnergy(energy)}}</p>
                      <p :style="getEnergyInfoStyle()">Energy</p>
                    </div>
                </div>
              </div>
              <div :style="getTittleboxStyle()">
                <div ref="container" :style="getChartStyle()"></div>
              </div>
              <div style="text-align:right;color:#999;font-size:10px">{{rackName}}</div>                
          </div>
      </div>
    </el-badge>
  </div>
  </div>
</template>

<script type="text/javascript">
  import ECharts from 'echarts'
  import Format from './../common/format'
  export default {
    data() {
      return {
        alarmCont: this.notify_num,
        rackContainerStyle: {
          display: 'block',
          height: '0px',
          width: '0px'
        },
        innerChart: null,
      }
    },
    mounted() {
      this.init();
      this.$watch(() => {
        return [this.usedNumber, this.offNumber, this.busyNumber, this.freeNumber];
      },(val, oldVal) => {
        this.initChart();
      })
    },
    props: ["height", "width", "notify_num", "nodes",
    "energy", "usedNumber", "offNumber", "busyNumber", "freeNumber", "rackName"],
    methods: {
      getRackBackgroundImg(imageName){
        return './../asset/image/rack/' + imageName;
      },
      init(){
        this.rackContainerStyle = {
          display: 'block',
          height: this.height,
          width: this.width
        };
        this.innerChart = ECharts.init(this.$refs.container);
        this.initChart();
      },
      getInnerboxStyle(){
        var innerbox_css = {
            width: '100%',
            height: '100%',
            padding: '10px '+'10px ' + String(parseInt(parseFloat(this.height.substring(0, this.height.length - 1))*0.12)) + 'px ' + '10px',
            'box-sizing': 'border-box'
        };
        return innerbox_css;
      },
      getTittleboxStyle(){
        var littlebox_css = {
          height: String(parseInt(parseFloat(this.height.substring(0, this.height.length - 1))*0.28)) + 'px',
          padding: '5px',
          'box-sizing': 'border-box',
        };
        return littlebox_css;
      },
      getTittleStyle(){
        var tittle_css = {
          'text-align': 'center',
          'color': '#40aaff',
          'font-size': '14px',
           // 'width': '10px'
        };
        return tittle_css;
      },
      getNodeInfoStyle(){
        var nodeInfoStyle = {
          'text-align': 'center',
          'vertical-align': 'middle',
          // 'padding-top': '20%',
          'color': '#40aaff',
          'font-size': '14px'
        };
        return nodeInfoStyle;
      },
      getEnergyInfoStyle(){
        var energyInfoStyle = {
          'text-align': 'center',
          'vertical-align': 'middle',
          'color': '#999999',
          'font-size': '12px'
        };
        return energyInfoStyle;
      },
      getChartStyle(){
        var chartStyle = {
          width: String(parseInt(this.width.substring(0, this.width.length - 1))-30) + 'px',
          height: '100%',
          'background-color' : '#F8F8F8'
        };
        return chartStyle;
      },
      initChart() {
        var option = {
          tooltip: {
            trigger: 'item',
            formatter: function(item){
              return item.name + ": " + item.value
            }
          },
          backgroundColor: '#F8F8F8',
          color:["#63b1d8", "#82c9ee", "94e9fc", "#e6eef0"],
          series: [
            {
              name:'Rack State',
              type:'pie',
              hoverAnimation: false,
              radius: ['50%', '70%'],
              avoidLabelOverlap: false,
              label: {
                normal: {
                  show: false,
                  position: 'center'
                },
                emphasis: {
                  show: false,
                  textStyle: {
                      fontSize: '10',
                      fontWeight: 'bold'
                  }
                }
              },
              labelLine: {
                normal: {
                    show: false
                }
              },
              data:[
                {value:this.usedNumber, name:'on'},
                {value:this.busyNumber, name:'busy'},
                {value:this.freeNumber, name:'idle'},
                {value:this.offNumber, name:'off'}
              ]
            }
          ]
        };
        this.innerChart.setOption(option);
      },
      formatEnergy(energy) {
        return Format.formatEnergy(energy, 1000) //1000W = 1kW
      }
    },
  }
</script>
