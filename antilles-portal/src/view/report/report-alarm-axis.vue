<template>
	<div ref="ReportAlarmAxis" style="width: 100%;height:500px;">
	</div>
	
</template>
<script>
	import EChart from "echarts"
	export default{
		component:{},
		props:['bar','dataReportAlarmAxis'],
		data(){
			return{
				barObject:{},
				p:this.dataReportAlarmAxis
			}
		},
		mounted(){		
			var $this=this;
			 $this.$nextTick(function(){
				 $this.barObject=EChart.init( $this.$refs.ReportAlarmAxis); 		
				this.draw();
				window.addEventListener('resize', this.onResize);
			})			
			this.$watch('dataReportAlarmAxis',(val, oldVal) => {
				this.p = val;
			  	this.barObject.resize();
				this.draw();
			},{deep: true})
		},
		 beforeDestroy() {
		    window.removeEventListener('resize', this.onResize);
		 },
		methods:{ 	
			onResize(){
				this.barObject.resize();
			}, 		
			draw:function(){
				var $this = this;
				var option = {
				    tooltip : {
				        trigger: 'axis',
				        axisPointer:{
				        	type : 'shadow'  
				        },
				    	formatter: function (data) {				    		
				    		if(data[0].seriesName == "critical"){
								data[0].seriesName = "fatal"							
							}
							if(data[2].seriesName == "warning"){
								data[2].seriesName = "warn"
							}
			    			return `${data[0].name}<br>`+$this.$t(`Alarm.PolicyLevel.${data[0].seriesName}`) +` : ${data[0].value}<br>`+$this.$t(`Alarm.PolicyLevel.${data[1].seriesName}`) +` : ${data[1].value}<br>`
							    		   +$this.$t(`Alarm.PolicyLevel.${data[2].seriesName}`) +` : ${data[2].value}<br>`
							    		   +$this.$t(`Alarm.PolicyLevel.${data[3].seriesName}`) +` : ${data[3].value}<br>`;
          				}
				    },
				    color:['#E51C23','#FF6A00','#FFC107','#0096E7'],
				    barWidth: '25%',
				    grid: {
				        left: '3%',
				        right: '4%',
				        bottom: '3%',
				        containLabel: true
				    },
				    xAxis : [
				        {
				            type : 'category',
				            data : this.dataReportAlarmAxis.alarmTime,				            
				            'axisLabel':{
				            	'interval':0,
				            	'rotate':60
				            },
				            axisPointer: {
				              type: 'shadow'
				          }
				        }
				    ],
				    yAxis : [
				        {
				            type : 'value',
				            minInterval: 1
				        }
				    ],
				    series :(function(){
				    	var serise = [];
				    	for(var key in $this.dataReportAlarmAxis) {				    		
				    		if(key != 'alarmTime' ) {
				    			serise.push({
				    				name: key,
				    				type: 'bar',
				    				stack: 'error',
				    				data: $this.dataReportAlarmAxis[key]
				    			})
				    		}
				    	}
				    	return serise;
				    })()
				};
				this.barObject.setOption(option);
			}

		}
 }

</script>