<style>
  .report-pie{
    width: 100%;
    height: 500px;
  }
</style>
<template>
  <div>
    <div id="report-pie" class="report-pie"></div>
  </div>
</template>
<script>
  import Format from './../../common/format'
  import EChart from 'echarts'
  export default {
      components:{

      },
      props: ['pie'],
      data () {
        return {
          pieObject:{}
        };
      },
      mounted(){
        var $this=this;
         this.$nextTick(function(){
          this.pieObject=EChart.init(document.getElementById("report-pie"));
          this.pieObject.on('click',function(para){
            $this.$emit('clickPie',para);
          });
          window.removeEventListener('resize', this.pieObject.resize);
          window.addEventListener('resize', this.pieObject.resize);
         });
      },
      methods:{
        draw:function(data){
          var option = {
          tooltip: {
              trigger: 'item',
              formatter: function (data) {
                        return `${data.name}: ${data.data.value}<br>
                        ${Format.formatNumber(data.percent,1)}%`
                      }
          },
          legend: {
              x: 'center',
              y:'bottom',
              data:this.pie.legend
          },
          series: [
              {
                  name:'user',
                  type:'pie',
                  radius: ['50%', '70%'],
                  avoidLabelOverlap: false,
                  selectedMode: 'single',
                  label: {
                      normal: {
                          show: false,
                          position: 'center',
                          formatter: '{c}'
                      },
                      emphasis: {
                          show: true,
                          textStyle: {
                              fontSize: '30',
                              fontWeight: 'bold'
                          }
                      }
                  },
                  labelLine: {
                      normal: {
                          show: false
                      }
                  },
                  data:this.pie.data
              }
          ]
      };
              this.pieObject.setOption(option);
              this.pieObject.resize();
              }
            },
            watch:{
              pie:{
                handler:function(){
                      this.draw(this.pie);
                  },
                deep:true
              }
            }
          }
</script>