<style>
</style>
<template>
	<div class="report-table-style">
		<div class="reportFilter">
			<el-form  class="reportTime" :model="ReportFilterForm">
			 <el-form-item :label="$t('Report.Title.Time')"  label-width="100px">
			     	<date-region-picker id="tid_report-time-picker" v-model="daterange" quick-pick="default"
			      @date-change="onDateChange" ref="dateSelect" class="reportFilter-button">
			      </date-region-picker>
			  </el-form-item>
			</el-form>
			<div class="antilles-date-picke">
				<el-button type="primary"  @click="alarmReport()" :disabled="isOK()">{{$t("Report.Button.Preview")}}
				</el-button>
				<el-button id="tid_report-submit"  @click="download()" :disabled="isOK()">{{$t("Report.Button.Submit")}}
				</el-button>
			</div>
		</div>
		<div class="nodata" v-show="show">
			<div style="margin-top: 160px">
				<img src="../asset/image/report/nodata.png"
				style="height:60px;width: 80px">
			</div>
			<div style="margin-top:20px; color:#ccc;font-size: 16px;">{{$t('NodeGpus.Monitor.No.Data')}}</div>
		</div>
		<report-alarm-alert ref='ReportAlarmAlert'></report-alarm-alert>

 	<el-row class="report-alarm-bottom"  v-show="okShow">
		<el-col :span="8">
		<div style="padding:20px;">
			<report-alarm-left ref='ReportAlarmLeft' :data-report-alarm-left="dataReportAlarmLeft"
			v-if="dataReportAlarmLeft != false"   @clickPie="filter" ></report-alarm-left>
		</div>
		</el-col>
		<el-col :span="16">
		<div style="padding:20px;" ref="reportRight">
			      <el-tabs v-model="activeName">
			        <el-tab-pane :label='$t("Report.Tab.Chart")' name="reportAlarmAxis">
			          <report-alarm-axis ref="reportAlarmAxis" v-if="dataReportAlarmAxis != false"
			          :data-report-alarm-axis="dataReportAlarmAxis" @click="changeAxis"
			          ></report-alarm-axis>
			        </el-tab-pane>
			        <el-tab-pane :label='$t("Report.Tab.Table")' name="reportAlarmTable"
			        @click="changeTable">
		          <report-alarm-table ref="reportAlarmTable"       :data-report-alarm-table="dataReportAlarmTable"></report-alarm-table>
		        </el-tab-pane>
		      </el-tabs>
		    </div>
		</el-col>
	</el-row>
</div>
</template>
<script>
	import ReportService from '../service/report'
	import DateRegionPicker from '../component/date-region-picker'
	import ReportAlarmAlert from "./report/report-alarm-alert"
	import ReportAlarmLeft from "./report/report-alarm-left"
	import reportAlarmAxis from "./report/report-alarm-axis"
	import reportAlarmTable from "./report/report-alarm-table"

	export default{
		components: {
	      'date-region-picker': DateRegionPicker,ReportAlarmAlert,ReportAlarmLeft,reportAlarmAxis,reportAlarmTable
	    },
	data() {
		var $this=this;
		return{
			daterange:['',''],
			show:false,
			okShow:false,
			filterData:[],
			ReportFilterForm:{
				level:'all',
				node:{
				      "value_type":'hostname',
				      "values":[]
				    }
			},
			activeName:'reportAlarmAxis',
			dataReportAlarmLeft:false,
			get_dataReportAlarmLeft:function(data){				
				var critical=0,error=0,warning=0,info=0;
				data.forEach(function(item){
					critical=critical+item.critical;
					error=error+item.error;
					warning=warning+item.warning;
					info=info+item.info;
				});
				if(error == 0 && critical == 0 && info == 0 && warning == 0)
					{return {legend:[],data:[]}}
				return {
					legend:["critical","error","warning","info"],
					data:[	
						{value:critical,name:'critical'}, 
				        {value:error,name:'error'}, 
				        {value:warning,name:'warning'}, 
				        {value:info,name:'info'}]
					}
		
			},
			dataReportAlarmAxis: false,
			get_dataReportAlarmAxis:function(data){				
				data.sort(function(a,b){
					return Date.parse(a.alarm_time)-Date.parse(b.alarm_time);
				})
				var alarm_time= [], error= [],info=[],warning=[],critical=[];
				for(var item in data){
					alarm_time.push(data[item].alarm_time);
					for(var i in data[item]){
						if(i !=='alarmTime'&& i !== "numTotal"){
							if(i =='critical'){
								critical.push(data[item][i])
							}if(i =='error'){
								error.push(data[item][i])
							}if(i =='warning'){
								warning.push(data[item][i])
							}if(i =='info'){
								info.push(data[item][i])
							}
						}
					}
				}
				return {
					alarmTime:alarm_time,
					critical:critical,
					error:error,
					warning:warning,
					info:info
				}
		},
		dataReportAlarmTable:[],
		get_dataReportAlarmTable:function(data){
			this.dataReportAlarmTable.splice(0, this.dataReportAlarmTable.length);
			data.forEach((item) => {
          		this.dataReportAlarmTable.push(item);
			})
        	return this.dataReportAlarmTable;
		}
	}
	},
	watch:{
		filterData:{ 
			handler:function(){
				this.dataReportAlarmAxis=this.get_dataReportAlarmAxis(this.filterData);
				this.dataReportAlarmTable.slice(0,this.filterData.length);
				this.get_dataReportAlarmTable(this.filterData).forEach((item)=>{this.filterData.push(item)
				});
		},
		deep:true
		},
		activeName(newVal, oldVal) {
	      var self = this;
	      if(newVal=='reportAlarmAxis') {
	        this.$nextTick(() => {
	          self.$refs.reportAlarmAxis.onResize();
	        });
	      } else if(newVal=='reportAlarmTable') {
	        this.$nextTick(() => {
	          self.$refs.reportAlarmTable.reLayout();
	        });
	      }
	    }
	},

	methods:{
	 filter(data){
	 	var $this=this;
    	if(data.data.selected){
    		var filtered=[];
    		 $this.rawData.forEach(function(item){    		 
    			if(item[data.data.name]>0){    				
    				var temp={};
    				temp['alarm_time']=item['alarm_time'];
    	 			temp[data.data.name]=item[data.data.name];
    				filtered.push(temp);
    			}
    		});
			this.dataReportAlarmAxis=$this.get_dataReportAlarmAxis(filtered);
			//$this.get_dataReportAlarmTable(filtered);			
    	}else{
			this.dataReportAlarmAxis=$this.get_dataReportAlarmAxis($this.rawData);
			//$this.get_dataReportAlarmTable($this.rawData);
    	}
    },
   	changeAxis(){
		$this.get_dataReportAlarmAxis(this.rawData);
    },
    changeTable(){
    	$this.get_dataReportAlarmTable(this.rawData);
    },
	onDateChange(val){
		this.daterange = val;
	},
	isOK:function(){
      	if(this.daterange.includes("")){
      		return true;
      	} else {
      		return false;
      	}
    },
	download(){
			var data={
				target:'alarm',
				start_time:(new Date(this.daterange[0])).valueOf(),
				end_time:(new Date(this.daterange[1])).valueOf(),
				level:this.ReportFilterForm.level,
				node:this.ReportFilterForm.node
			};
			this.$refs.ReportAlarmAlert.download(data).then((res)=>{
				window.open(res);
			}, (res) => {
			})
		},		
		alarmReport() {
			var form = {
				start_time: (new Date(this.daterange[0])).valueOf()/1000,
				end_time  : (new Date(this.daterange[1])).valueOf()/1000,
				timezone_offset:(new Date().getTimezoneOffset())
			}
			var $this=this;
			this.isShow=false;
			ReportService.alarmReport(form).then((res) => {
				if(res.length<1){
					this.show=true;
					this.okShow=false;
				}
				else{
					this.show=false;
					this.okShow=true;
				}
				$this.rawData=res;
				$this.dataReportAlarmLeft=
				$this.get_dataReportAlarmLeft(res);
				$this.dataReportAlarmAxis=$this.get_dataReportAlarmAxis(res);
				$this.get_dataReportAlarmTable(res);
			})
		}
	}
}


</script>
