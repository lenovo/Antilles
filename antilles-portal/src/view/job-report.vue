
<template>
	<div class="report-table-style">
		<div class="reportFilter">
			<el-form :model="reportFilterForm">
				<el-col :span="12">
				<el-form-item :label="$t('Report.Label.Type')" label-width="100px">
					<el-radio-group v-model="reportFilterForm.job_type" class="reportFilter-button">
						<el-radio-button id="tid_report-filter-type-job" label="job" >{{$t('Report.Label.Type.Job')}}</el-radio-button>
            <el-radio-button id="tid_report-filter-type-billgroup" label="billgroup">{{$t('Report.Label.BillGroup')}}</el-radio-button>
						<el-radio-button id="tid_report-filter-type-user" label="user">{{$t('Report.Label.Type.User')}}</el-radio-button>						
					</el-radio-group>
				</el-form-item>
			</el-col>     
			<el-col :span="12" v-if="reportFilterForm.job_type == 'job'" key="job">
				<el-form-item :label="$t('Report.Label.User')" label-width="100px">
					<multi-user-selector id="tid_report-filter-user-select" 
					@change="userSelectionChange" 
					:users-value="[]"
					filter-type="username,usergroup,billinggroup" 
					class="reportFilter-button" 
					:allable="true"></multi-user-selector>
				</el-form-item>
			</el-col>
			<el-col :span="12" v-if="reportFilterForm.job_type == 'user'" key="user">
				<el-form-item :label="$t('Report.Label.User')" label-width="100px">
					<multi-user-selector id="tid_report-filter-user-select" 
					@change="userSelectionChange" 
					:users-value="[]" 
					filter-type="username" 
					class="reportFilter-button" 
					:allable="true"></multi-user-selector>
				</el-form-item>
			</el-col>
			<el-col :span="12" v-if="reportFilterForm.job_type == 'billgroup'">
				<el-form-item :label="$t('Report.Label.BillGroup')" label-width="100px">
					<el-select id="tid_report-filter-billgroup-select" v-model="reportFilterForm.billGroup" class="reportFilter-button" multiple :placeholder="$t('Select.All')">
						<el-option
		            v-for="item in billOption"
		            :key="item.id"
		            :label="item.name"
		            :value="item.name"></el-option>
					</el-select>
				</el-form-item>
			</el-col>
			</el-form>
			<div id="tid_reportTime" class="reportTime">
				<el-form :model="reportFilterForm">
					<el-form-item :label="$t('Report.Title.Time')" label-width="100px">
						<date-region-picker id="tid_report-time-picker" v-model="daterange" quick-pick="default"
		          @date-change="onDateChange" ref="dateSelect" style="margin-left: 50px;"></date-region-picker>
					</el-form-item>
				</el-form>
			</div>
			<div class="antilles-date-picke">
				<el-button id="tid_report-submit" type="primary" :disabled="isOK()"  @click="submit()">{{$t("Report.Button.Preview")}}</el-button>
				<el-button :disabled="isOK()"  @click="download()">{{$t("Report.Button.Submit")}}</el-button>
			</div>
		</div>
		<report-dialog ref="ReportDialog"/>
    <div class="nodata" v-show="isShow">
      <div style="margin-top: 160px">
        <img src="../asset/image/report/nodata.png" style="height:60px;width: 80px">
      </div>
      <div style="margin-top:20px; color:#ccc;font-size: 16px;">{{$t('NodeGpus.Monitor.No.Data')}}</div>
    </div>
		<report-preview v-show="show" ref="reportPreview" :preview="preview" />
	</div>
</template>
<script>
  import DateRegionPicker from '../component/date-region-picker'
  import MultiUserSelector from '../widget/multi-user-selector'
  import ReportDialog from './report/report-dialog'
  import BillGroupService from '../service/bill-group'
  import ReportPreview from './report/report-preview'
  import ReportService from "../service/report"

  export default {
  	  components: {
	      'date-region-picker': DateRegionPicker,
	      'report-dialog':ReportDialog,
	      'multi-user-selector':MultiUserSelector,
	      'report-preview':ReportPreview
	    },
      data () {
        return {
          show:false,
          isShow:false,
          daterange:['',''],
          billOption:[],
          preview:{},
          reportFilterForm:{
          	job_type:"job",
            user:{
							values: [],
							value_type: ''
						},
            billGroup:[]
          },
          isOK:function(){
          	if(this.daterange.includes("")){
          		return true;
          	} else {
          		return false;
          	}
          }
        };
      },
      mounted(){
      	var $this = this;
        BillGroupService.getAllBillGroups().then(function(res){
          $this.billOption = res;
        },function(error){

        });
      },
      watch:{
      	reportFilterForm:{
      		handler:function(){
      			var twoColumns= this.reportFilterForm.job_type == 'job'? false:true;
      			this.preview={
		      			twoColumns:twoColumns
		      		};
      		},
      		deep:true
      	}
      },
      methods:{
      	download(){
      		var data={
      			target:'job',
      			start_time:(new Date(this.daterange[0])).valueOf(),
      			end_time:(new Date(this.daterange[1])).valueOf(),
      			job_type:this.reportFilterForm.job_type,
      			user:this.reportFilterForm.user,
      			billgroup:this.reportFilterForm.billGroup
      		};
      		this.$refs.ReportDialog.download(data).then((res) => {            
					window.open(res);
				}, (res) => {
				});
      	},
      	userSelectionChange(val){
          this.reportFilterForm.user = val;
				},
      	submit(){
      		var twoColumns= this.reportFilterForm.job_type == 'job'? false:true;
          var $this = this;
          this.preview = {
            target:'job',
            twoColumns:twoColumns,
            start_time:(new Date(this.daterange[0])).valueOf(),
            end_time:(new Date(this.daterange[1])).valueOf(),
            job_type:this.reportFilterForm.job_type,
            user:this.reportFilterForm.user,
            billgroup:this.reportFilterForm.billGroup
          };
          ReportService.previewJobReport(this.preview).then(function(res){
            if(res.length<1){
              $this.show = false;
              $this.isShow = true;
            }else{
              $this.show = true;
              $this.isShow = false;
            }
          });
      	},
      	onDateChange(val){
	        this.daterange = val;
      	}
      }
    }
</script>
