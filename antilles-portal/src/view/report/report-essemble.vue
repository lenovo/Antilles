<style>
  .report-essemble{
    width: 100%;
    height: 400px;
  }
</style>
<template>
  <div>
    <div id="report-essemble" class="report-essemble"></div>
  </div>
</template>
<script>
import EChart from 'echarts'
  export default {
      components:{

      },
      props: ['essemble'],
      data () {
        return {
          essembleObject:{}
        };
      },
      mounted(){
        this.essembleObject=EChart.init(document.getElementById("report-essemble"));
        this.draw();
        this.onResize();
        window.removeEventListener('resize',this.onResize);
        window.addEventListener('resize', this.onResize);
      },
      methods:{
        onResize(){
				  this.essembleObject.resize();
			  },
        draw:function(data){
          var option= {
            tooltip: {
                trigger: 'axis'
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '10%',
                containLabel: true
            },
            legend: {
                data:[this.essemble.type,this.$t("Report.Chart.Time")]
            },
          xAxis: [
              {
                  type: 'category',
                  data: this.essemble.time,
                  axisPointer: {
                      type: 'shadow'
                  }
              }
          ],
          yAxis: [
              {
                  type: 'value',
                  name: this.essemble.type
              },
              {
                  type: 'value',
                  name: this.$t("Report.Chart.Time")
              }
          ],
          series: [
              {
                  name:this.essemble.type,
                  type:'bar',
                  itemStyle:{
                    normal:{
                      color:'#868686'
                    }
                  },
                  data:this.essemble[this.essemble.type+'Count']
              },
              {
                  name:this.$t("Report.Chart.Time"),
                  type:'line',
                  yAxisIndex: 1,
                  data:this.essemble[this.essemble.type+'Time']
              }
          ]
        };
        this.essembleObject.setOption(option);
        }
      },
      watch:{
        essemble:{
          handler:function(val){
            this.draw();
            this.essembleObject.resize();
            },
          deep:true
        }
      }
    }
</script>