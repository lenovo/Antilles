<template lang="html">
	<div class="height--100 p-10">
		<div class="table-style p-20" style="height: 500px;text-align: center;">
			<div>
				<div style="margin-top: 100px;"><img src="../asset/image/weblog/log.png"></div>
				<div style="color: #333333;font-size: 16px;margin-bottom: 10px;">{{$t("Menu.OperationLogManage")}}</div>
				<date-region-picker id="tid_report-time-picker" v-model="daterange" quick-pick=""
		          @date-change="onDateChange" ref="dateSelect" style="margin-left: 50px;"></date-region-picker>
				<el-button type="primary" @click="DownloadLog()" :disabled="isOK()" style="margin-top: 10px;">{{$t('Image.Download')}}
				</el-button>
			</div>
		</div>
		<report-dialog ref="ReportDialog" />
	</div>
</template>

<script>
import DateRegionPicker from "../component/date-region-picker"
import ReportDialog from './report/report-dialog'
export default {
  components:{
  	'date-region-picker': DateRegionPicker,
  	'report-dialog':ReportDialog
  },
  data(){
  	return {
  		daterange:['',''],
  	  	isOK:function(){
  	          	if(this.daterange.includes("")){
  	          		return true;
  	          	} else {
  	          		return false;
  	          	}
  	          }
  	      }
  },
  methods:{
  	DownloadLog(){
  		var data={
      			target:'operation',
      			job_type:'log',
      			start_time:(new Date(this.daterange[0])).valueOf(),
      			end_time:(new Date(this.daterange[1])).valueOf()
      		};
      		this.$refs.ReportDialog.download(data).then((res) => {
					window.open(res);
				}, (res) => {
				});
  	},
  	onDateChange(val){
	        this.daterange = val;
      	}
  }
}
</script>
