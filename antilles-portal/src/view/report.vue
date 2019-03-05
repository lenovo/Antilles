<style>
	.reportFormat .inline {
		display: inline-block;
	}
	.reportFormat input[type="radio"] {
		display: none;
	}
	.reportDirection input[type="radio"] {
		display: inline-block;
	}
	.reportFormat input[type="radio"] ~ label {
		display: inline-block;
		width: 60px;
		height: 60px;
	}
	.reportFormatExcel ~ label{
		background-image: url('./../asset/image/report/excel.png');
	}
	.reportFormatExcel:checked ~ label{
		background-image: url('./../asset/image/report/excel_check.png');
	}
	.reportFormatPDF ~ label{
		background-image: url('./../asset/image/report/pdf.png');
	}
	.reportFormatPDF:checked ~ label{
		background-image: url('./../asset/image/report/pdf_check.png');
	}
	.reportFormatHTML ~ label{
		background-image: url('./../asset/image/report/html.png');
	}
	.reportFormatHTML:checked ~ label{
		background-image: url('./../asset/image/report/html_check.png');
	}
	/*.reportFormatVertical ~ label{
		background-image: url('./../asset/image/report/vertical.png');
	}
	.reportFormatVertical:checked ~ label{
		background-image: url('./../asset/image/report/vertical_check.png');
	}
	.reportFormatHorizontal ~ label{
		background-image: url('./../asset/image/report/horizonal.png');
	}
	#reportFormatHorizontal:checked ~ label{
		background-image: url('./../asset/image/report/horizonal_check.png');
	}*/

	.reportTime{
		border-top:1px dashed #eee;
		padding: 20px 0;
	}
	.reportFormat{
		padding: 10px 0;
		border-top:1px dashed #eee;
	}
	.reportFilter-div-header{
		padding: 10px 0 20px;
		font-size:16px;
	}
	.inline{
		margin-right: 20px;
	}

</style>
<template>
	<div class="height--100 p-10">
		<div class="reportFilter">
			<ReportFilter :filters="filterType" @report_filter="reportFilter"></ReportFilter>

			<div id="tid_reportTime" v-show="showTime" class="reportTime">
				<div class="reportFilter-div-header"><label style="color: #ff6666;">*</label>{{$t("Report.Title.Time")}}</div>
				<div class="antilles-date-picke">
					<date-region-picker id="tid_report-time-picker" v-model="daterange" quick-pick="default"
		          @date-change="onDateChange" ref="dateSelect">
		          </date-region-picker>
				</div>
			</div>

			<div id="tid_reportFormat" class="reportFormat">
				<div class="reportFilter-div-header">{{$t("Report.Title.Format")}}</div>
				<el-row class="reportFilter-div-header">
					<div class="antilles-date-picke">
						<div class="inline">
							<input type="radio" value="xls" id="tid_reportFormatExcel" class="reportFormatExcel" v-model="format">
							<label for="tid_reportFormatExcel"></label>
						</div>
						<div class="inline">
							<input type="radio" value="pdf" id="tid_reportFormatPDF" class="reportFormatPDF" v-model="format">
							<label for="tid_reportFormatPDF"></label>
						</div>
						<div class="inline">
							<input type="radio" value="html" id="tid_reportFormatHTML" class="reportFormatHTML" v-model="format">
							<label for="tid_reportFormatHTML"></label>
						</div>
					</div>
				</el-row>
				<el-row class="reportFilter-div-header reportDirection" id="tid_reportDirection">
					<div v-show="format == 'pdf'" class="antilles-date-picke">
						<el-radio id="tid_reportPdfVertical" class="radio" v-model="direction" label="vertical" :disabled='vertical'>{{$t("Report.Direction.Vertical")}}</el-radio>
        		<el-radio id="tid_reportPdfHorizontal" class="radio" v-model="direction" label="landscape">{{$t("Report.Direction.Horizontal")}}</el-radio>
					</div>
				</el-row>
			</div>
			<div class="antilles-date-picke">
				<el-button id="tid_report-submit" type="primary" :disabled="isOK()"  @click="submit()">{{$t("Report.Button.Submit")}}
				</el-button>
			</div>
		</div>
	</div>
</template>
<script>
  import DateRegionPicker from '../component/date-region-picker'
  import ReportFilter from './report/report-filter'
  import ReportService from '../service/report'

  const NotShowTime = ['node_running','node_user','user_login','user_storage'];

  export default {
  	  components: {
	      'date-region-picker': DateRegionPicker,
	      ReportFilter
	    },
      data () {
        return {
          format:'xls',
          daterange:['',''],
          filterType:'job',
          showTime:true,
          direction:"vertical",
          reportFilterForm:{
          	job_type:"job",
            operation_type:"log",
            content:"statistics",
            level:"all",
            user:[],
            node:[],
            billGroup:[],
            monitor_type:'cpu'
          },
					vertical: false,
          isOK:function(){
          	if(this.daterange.includes("") && !NotShowTime.includes(this.reportFilterForm.operation_type)){
          		return true;
          	} else {
          		return false;
          	}
          }
        };
      },
      methods:{
      	submit(){
					this.clearInvalidData();
      		const form={
      			start_time:(new Date(this.daterange[0])).valueOf(),
      			end_time:(new Date(this.daterange[1])).valueOf(),
      			format:this.format,
      			filterData:this.reportFilterForm,
      			reportType:this.filterType,
      			direction:this.direction
      		};
      		// 将接收的数据渲染到页面
      		ReportService.createReport(form).then((res) => {
						var reportUrl = res;
						window.open(reportUrl);
					}, (res) => {
						this.$message.error(res);
					});
      	},
      	onDateChange(val){
	        this.daterange = val;
      	},
      	reportFilter(val){
      		this.reportFilterForm = val;
      		if(NotShowTime.includes(this.reportFilterForm.operation_type)){
      			this.showTime = false;
      		} else {
      			this.showTime = true;
      		}
      	},
				verticalIsDisabled(arr) {
					if(
						arr[0]!='operation'&&arr[2]=='details'
					) {
						this.vertical = true;
						this.direction = 'landscape'
					} else {
						this.vertical = false;
						this.direction = 'vertical'
					}
				},
				clearInvalidData() {
					if(this.filterType == 'job') {
						if(this.reportFilterForm.job_type == 'billgroup') {
							this.reportFilterForm.user = [];
						}else {
							this.reportFilterForm.billGroup = [];
						}
						return ;
					}
					if(this.filterType == 'alarm') {
						if(this.reportFilterForm.content == 'statistics') {
							this.reportFilterForm.node = [];
						}
						return ;
					}
					if(this.filterType == 'operation') {
						if(this.reportFilterForm.operation_type == 'log') {
							this.reportFilterForm.user = [];
							this.reportFilterForm.node = [];
						}else if(this.reportFilterForm.operation_type == ('user_login' || 'user_storage')){
							this.reportFilterForm.node = [];
						}else if(this.reportFilterForm.operation_type == ('node_user' || 'node_running')){
							this.reportFilterForm.user = [];
						}
						return ;
					}
				}

      },
      mounted(){
      	this.filterType = window.location.hash.split('report-')[1];
				this.$watch(() => {
					return [
						this.filterType,
						this.reportFilterForm.job_type,
						this.reportFilterForm.content
					];
				}, (val, oldVal) => {
					this.verticalIsDisabled(val);
				})
      },
      watch:{
      	$route(val){
      		this.filterType = val.path.split('report-')[1];
      		this.format = 'xls';
      		this.daterange = ['',''];
      		this.$refs.dateSelect.clear();
      	}
      }

    }
</script>
