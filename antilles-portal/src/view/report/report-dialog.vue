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
  .reportFormat{
    padding: 10px 0;
  }
  .inline{
    margin-right: 20px;
  }
  .reportDialog-div-header{
    margin-top: 15px;
    margin-bottom: 15px;
  }
</style>
<template>
  <composite-form-dialog ref="innerDialog"
  :title="title" size="medium"
  :form-model="reportDownloadForm"
  :form-rules="reportDownloadRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
    <el-alert
    :title='$t("Report.Message.Dialog")'
    type="info"
    :closable="false"
    show-icon>
  </el-alert>
  <div style="margin-left: 20px;">
    <div class="reportDialog-div-header" v-show="target !='operation'">{{$t('Report.Label.Content')}}:</div>
    <el-form-item style="margin-left: -120px;" v-show="target !='operation'">
      <el-radio-group v-model="reportDownloadForm.content">
        <el-radio-button id="tid_report-filter-statistics" label="statistics">{{$t('Report.Label.Content.Stat')}}</el-radio-button>
        <el-radio-button id="tid_report-filter-details" label="details">{{$t('Report.Label.Content.Detail')}}</el-radio-button>
      </el-radio-group>
    </el-form-item>
    <div class="reportFormat">
    <div class="reportDialog-div-header">{{$t("Report.Title.Format")}}:</div>
    <el-row>
      <div>
        <div class="inline">
          <input type="radio" value="xls" id="tid_reportFormatExcel" class="reportFormatExcel" v-model="reportDownloadForm.format">
          <label for="tid_reportFormatExcel"></label>
        </div>
        <div class="inline" v-show="reportDownloadForm.content == 'statistics'">
          <input type="radio" value="pdf" id="tid_reportFormatPDF" class="reportFormatPDF" v-model="reportDownloadForm.format">
          <label for="tid_reportFormatPDF"></label>
        </div>
        <div class="inline">
          <input type="radio" value="html" id="tid_reportFormatHTML" class="reportFormatHTML" v-model="reportDownloadForm.format">
          <label for="tid_reportFormatHTML"></label>
        </div>
      </div>
    </el-row>
    <el-row class="reportFilter-div-header reportDirection" id="tid_reportDirection">
      <div v-show="reportDownloadForm.format == 'pdf' && reportDownloadForm.content == 'statistics'">
        <el-radio id="tid_reportPdfHorizontal" v-model="reportDownloadForm.direction" label="landscape">{{$t("Report.Direction.Horizontal")}}</el-radio>
        <el-radio id="tid_reportPdfVertical" v-model="reportDownloadForm.direction" label="vertical" :disabled="disableVertical">{{$t("Report.Direction.Vertical")}}</el-radio>
      </div>
    </el-row>
  </div>
  </div>
  </composite-form-dialog>
</template>
<script>
import CompositeFormDialog from '../../component/composite-form-dialog'
import ReportService from '../../service/report'

export default {
  data() {
    return {
      title:this.$t('Report.Button.Submit'),
      target:'job',
      disableVertical:false,
      reportDownloadForm: {
        content:'statistics',
        format:'xls',
        direction:'landscape',
        reportType:'job'
      },
      reportDownloadRules: {

      }
    };
  },
  components: {
    'composite-form-dialog': CompositeFormDialog
  },
  watch:{
    reportDownloadForm:{
      handler:function(){
        if(this.reportDownloadForm.content == 'details' && this.target!='operation'){
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
          job_type:this.reportDownloadForm.reportType,
          operation_type:this.reportDownloadForm.reportType,
          content:this.reportDownloadForm.content,
          level:'',
          user:this.reportDownloadForm.user,
          billGroup:this.reportDownloadForm.billgroup,
          node:this.reportDownloadForm.node,
          monitor_type:this.reportDownloadForm.monitor_type
        }
      };
      return ReportService.createReport(form);
    },
    successMessageFormatter(res) {
      return this.$t('Report.Message.Success');
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    download(data) {
      this.target = data.target;
      this.reportDownloadForm = {
        content:'statistics',
        format:'xls',
        direction:'landscape',
        start_time:data.start_time,
        end_time:data.end_time,
        user:data.user,
        node:data.node,
        billgroup:data.billgroup,
        reportType:data.job_type,
        monitor_type:data.monitor_type
      };
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>