<style>
 .reportAlertAlarm{
    margin:20px 20px 15px;
  }
  .reportAlert{
    margin: 0px 20px 15px;
  }
  .reportFormats .inline {
    display: inline-block;
  }
  .reportFormats input[type="radio"] {
    display: none;
  }
  .reportDirection input[type="radio"] {
    display: inline-block;
  }
  .reportFormats input[type="radio"] ~ label {
    display: inline-block;
    width: 60px;
    height: 60px;
  }
  .reportFormatExcel ~ label{
    background-image: url('./../../asset/image/report/excel.png');
  }
  .reportFormatExcel:checked ~ label{
    background-image: url('./../../asset/image/report/excel_check.png');
  }
  .reportFormatPDF ~ label{
    background-image: url('./../../asset/image/report/pdf.png');
  }
  .reportFormatPDF:checked ~ label{
    background-image: url('./../../asset/image/report/pdf_check.png');
  }
  .reportFormatHTML ~ label{
    background-image: url('./../../asset/image/report/html.png');
  }
  .reportFormatHTML:checked ~ label{
    background-image: url('./../../asset/image/report/html_check.png');
  }

  .inline{
    margin-right: 20px;
  }
  .reportDialog-div-header{
    margin-top: 15px;
    margin-bottom: 15px;
  }
  /*.reportLevel-button{
    width:100%;
  }*/
</style>
<template>
<composite-form-dialog ref="innerDialog"
  :title="title" size="medium"
  :form-model="reportDownloadForm"
  :form-rules="reportDownloadRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">  
    <el-alert :title="$t('Report.Message.Dialog')" type="info" show-icon></el-alert>
    <el-form label-width="20px">
      <div class="reportAlertAlarm"  v-show="target !='operation'">{{$t('Report.Label.Content')}}</div>  
      <el-radio-group v-model="labelPosition"  v-show="target !='operation'" @change='onLabelPositionChange' class="reportAlert">
        <el-radio-button label="statistics">{{$t('Report.Label.Content.Stat')}}</el-radio-button>
        <el-radio-button label="details">{{$t('Report.Label.Content.Detail')}}</el-radio-button>
      </el-radio-group> 

      <div v-show="labelPosition == 'details'">
      <el-form label-width="20px">
          <div class="reportAlert" prop="level">{{$t('Report.Label.Level')}}</div>
          <div prop="level" class="reportAlert">
            <el-radio-group v-model="level" @change='onAlarmLevelChange'>
              <el-radio-button  v-for="(item, index) in object" :key='index' :label="item.value">{{item.label}}</el-radio-button>
            </el-radio-group>       
          </div>

          <div class="reportAlert">{{$t('Report.Label.Node')}}</div>         
         <multi-node-selector ref="multiNodeSelector" class="reportAlert" @nodes-selected-change="nodeSelectedChange" :hostname-max="50"></multi-node-selector>
        </el-form>
      </div>
      <div class="reportFormats">
        <div class="reportAlert">{{$t('Report.Title.Format')}}</div>
        <div class="inline reportAlert">
          <input type="radio" value="xls" id="tid_reportFormatExcel" class="reportFormatExcel" v-model="reportDownloadForm.format">
          <label for="tid_reportFormatExcel"></label>
        </div>
        <div class="inline" v-show="labelPosition !== 'details'">
          <input type="radio" value="pdf" id="tid_reportFormatPDF" class="reportFormatPDF" v-model="reportDownloadForm.format">
          <label for="tid_reportFormatPDF"></label>
        </div>
        <div class="inline">
          <input type="radio" value="html" id="tid_reportFormatHTML" class="reportFormatHTML" v-model="reportDownloadForm.format">
          <label for="tid_reportFormatHTML"></label>
        </div>
        </div>
  
    <div v-show="reportDownloadForm.format == 'pdf' && labelPosition !== 'details'" class="reportAlert">
        <el-radio id="tid_reportPdfHorizontal" v-model="reportDownloadForm.direction" label="landscape">{{$t("Report.Direction.Horizontal")}}</el-radio>
        <el-radio id="tid_reportPdfVertical" v-model="reportDownloadForm.direction" label="vertical" :disabled="disableVertical">{{$t("Report.Direction.Vertical")}}</el-radio>
    </div>
    </el-form>  
   </composite-form-dialog>
  
</template>
<script>
  import ReportService from '../../service/report'
  import CompositeFormDialog from '../../component/composite-form-dialog'
  import MultiNodeSelector from '../../widget/multi-node-selector'

export default {
  components:{
    'composite-form-dialog' :CompositeFormDialog,
    'multi-node-selector':MultiNodeSelector 
  },
  data() {
    return {
      title:this.$t('Report.Button.Submit'),
      target:'alarm',
      disableVertical:false,
      labelPosition:"statistics",
      innerValue: [],
      radioAll:'',
      level: '',
      reportDownloadForm: {
        level:'all',
        content:'statistics',
        format:'xls',
        direction:'landscape',
        reportType:'Alarm',
        node: {
              "value_type":'hostname',
              "values":[]
              }
      },
      object:[
      {
      
        label: this.$t('Report.Label.Level.All'),
        value: "all"
      },
      {
        label: this.$t('Alarm.PolicyLevel.fatal'),
        value: "fatal"
      },
      {
        label: this.$t('Alarm.PolicyLevel.error'),
        value: "error"
      },
      {
        label: this.$t('Alarm.PolicyLevel.warn'),
        value: "warn"
      },
      {
        label: this.$t('Alarm.PolicyLevel.info'),
        value: "info"
      }
      ],
      reportDownloadRules:{
      }      
    }    
  },
  watch:{
    reportDownloadForm:{
      handler:function(){
        if(this.labelPosition == 'details' && this.target!='operation'){
          this.reportDownloadForm.direction = 'landscape';
          this.disableVertical = true;
        } else {
          this.disableVertical = false;
        }
      },
      deep:true
    }
  },
  methods: {
    submitForm() {
      var form={
        reportType:this.target,
        format:this.reportDownloadForm.format,
        start_time:this.reportDownloadForm.start_time,
        end_time:this.reportDownloadForm.end_time,
        direction:this.reportDownloadForm.direction,
        filterData:{
          node:this.reportDownloadForm.node,
          level:this.reportDownloadForm.level,
          content:this.labelPosition
        }
      };    
      return ReportService.createReport(form);
    },
    successMessageFormatter(res){
        this.labelPosition = "statistics";
        this.reportDownloadForm.content= this.labelPosition;
        return this.$t('Report.Message.Success');
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    download(data) {
      this.target = data.target;
      this.level = "all";
      this.reportDownloadForm = {
        content:data.content,
        format:'xls',
        direction:'landscape',
        start_time:data.start_time,
        end_time:data.end_time,
        node:data.node,
        level:data.radioAll
      };
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    onLabelPositionChange(val) {
      this.reportDownloadForm.details = this.labelPosition;
      // this.level = "all";
      // this.reportDownloadForm.format='xls';
      // this.$refs.alarmNodeSelector.doClear()
    },
    onAlarmLevelChange(val) {
      this.reportDownloadForm.level = val;
    },
    nodeSelectedChange(val){      
      this.reportDownloadForm.node = val;
    }
  }
}



</script>