<style>
  .report-line{
    width: 100%;
    height: 400px;
  }
</style>
<template>
  <div>
    <div id="report-line" class="report-line"></div>
  </div>
</template>
<script>
import EChart from 'echarts'
  export default {
      components:{

      },
      props: ['line'],
      data () {
        return {
          lineObject:{}
        };
      },
      mounted(){
        var $this=this;
         this.$nextTick(function(){
          this.lineObject=EChart.init(document.getElementById("report-line"));
          window.removeEventListener('resize', this.lineObject.resize);
          window.addEventListener('resize', this.lineObject.resize);
         });
      },
      methods:{
        draw:function(data){         
          var format = this.line.format;
          var option = {
          tooltip: {
              trigger: 'axis',
              formatter:function(para){                
                var str = para[0]['axisValueLabel']+'<br>';                         
                para.forEach(function(i){                  
                  var seriesValue=i['value'].slice(1,2);
                  str = str+i['seriesName']+' : '+seriesValue+format+'<br>';
                });
                return str;
            }     
    },
    legend: {
        data:data.legend
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        data:data.time
    },
    yAxis: {
        type: 'value'
    },    
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
    series: data.series
    // series: {
    //     name: data.series.name,   
    //     type:'line'
    //   }
    };
        this.lineObject.clear();
        this.lineObject.setOption(option);
        this.lineObject.resize();
        }
      },
      watch:{
        line:{
          handler:function(){
                this.draw(this.line);
            },
          deep:true
        }
      }
    }
</script>