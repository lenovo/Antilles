<template>
	<div style="width:100%;height:500px;" ref="reportLeft">
	</div>
</template>
<script>
	import Format from './../../common/format'
	import EChart from 'echarts'

export default{
	components:{},
	props:['pie', 'dataReportAlarmLeft'],
	data(){
		return {
			pieObject:{},
			p: this.dataReportAlarmLeft
		};
	},
	mounted(){
		var $this=this;
		this.$nextTick(function(){
			this.pieObject=EChart.init(this.$refs.reportLeft);
			this.pieObject.on('click',function(para){
				$this.$emit('clickPie',para);
			});
			this.draw();
			window.addEventListener('resize', this.onResize);
		})
		this.$watch('dataReportAlarmLeft',(val, oldVal) => {
			this.p = val;
			this.pieObject.resize();
			this.draw();
		},{deep: true})
	},
	beforeDestroy() {
		    window.removeEventListener('resize', this.onResize);
		},
	methods:{
		onResize(){
				this.pieObject.resize();
			},
		draw:function(){
			var $this = this;
			var option={
				tooltip:{
					tigger:'item',
					formatter: function (data) {
						if(data.name == "critical"){
							data.name= "fatal"							
						}else if(data.name == "warning"){
							data.name= "warn"
						}
            			return  $this.$t(`Alarm.PolicyLevel.${data.name}`)  + `: ${data.data.value}<br>
            			${Format.formatNumber(data.percent,1)}% `
                	}
				},			
				legend:{
					top:'bottom',
					x:'center',
					formatter: function (name) {
						if(name == "critical"){
							name = "fatal"							
						}else if(name == "warning"){
							name = "warn"
						}					
            			return $this.$t(`Alarm.PolicyLevel.${name}`);
                	} ,               	
					data:this.dataReportAlarmLeft.legend
				},
				series:[
					{
						type:'pie',
						color:['#E51C23','#FF6A00','#FFC107','#0096E7'],
						radius:['50%','65%'],
						avoidLabelOverlap: false,
						selectedMode: 'single',
						label:{
							normal:{
								show:false,
								position:'center',
								formatter: '{c}'
							},
							emphasis:{
								show:true,
								textStyle:{
									fontSize:'30',
									fontWeight:'bold'
								}
							}
						},
						labelLine:{
							normal:{
								show:false
							}
						},
						data:this.dataReportAlarmLeft.data						
					}
				]
			}
			this.pieObject.setOption(option);
		}
	}
}
</script>