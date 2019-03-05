<style>
  .report-bar{
    width: 100%;
    height: 400px;
  }
</style>
<template>
  <div>
    <div id="report-bar" class="report-bar"></div>
  </div>
</template>
<script>
import EChart from 'echarts'
  export default {
      components:{

      },
      props: ['bar'],
      data () {
        return {
          barObject:{}
        };
      },
      mounted(){
          this.barObject=EChart.init(document.getElementById("report-bar"));
      },
      methods:{
        draw:function(data){
          this.barObject.resize();
          var $this = this;
          var option={
          color: ['#3398DB'],
           tooltip : {
              trigger: 'axis',
               axisPointer:{
                  type : 'shadow'                   
                },
                formatter: function (data) {                     
                    if(data[0].seriesName == "job"){
                      data[0].seriesName = "Job"
                    }                    
                    return `${data[0].name}<br>` + $this.$t(`Report.Label.Type.${data[0].seriesName}`) + `: ${data[0].value}`         
                  }                               
          },
          grid: {
              left: '3%',
              right: '4%',
              bottom: '10%',
              containLabel: true
          },
          xAxis : [
              {
                  type : 'category',
                  data : this.bar.x,
                  axisTick: {
                      alignWithLabel: true
                  }
              }
          ],
          yAxis : [
              {
                  type : 'value'
              }
          ],
        dataZoom: [{
            type: 'inside',
            start: 0,
            end: 80
        }, {
            start: 0,
            end: 80,
            handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
            handleSize: '80%',
            handleStyle: {
                color: '#fff',
                shadowBlur: 3,
                shadowColor: 'rgba(0, 0, 0, 0.6)',
                shadowOffsetX: 2,
                shadowOffsetY: 2
        }
        }],
          series : [
              {
                  name:'job',
                  type:'bar',
                  barWidth: '60%',
                  data:this.bar.y
              }
          ]
      };
                this.barObject.setOption(option);
              }
            },
            watch:{
              bar:{
                handler:function(){
                      this.draw(this.bar);
                  },
                deep:true
              }
            }
    }
</script>