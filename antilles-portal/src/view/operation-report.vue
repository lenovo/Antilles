<template>
  <div class="report-table-style">
    <div class="reportFilter">
      <el-form :model="reportFilterForm">
        <el-form-item :label="$t('Report.Label.Index')" label-width="100px">
        <el-radio-group v-model="reportFilterForm.monitor_type" class="reportFilter-button">
          <el-radio-button label="cpu">{{$t('Report.Label.Index.CPU')}}</el-radio-button>
          <el-radio-button label="mem">{{$t('Report.Label.Index.Memory')}}</el-radio-button>
          <el-radio-button label="net">{{$t('Report.Label.Index.Network')}}</el-radio-button>
        </el-radio-group>
      </el-form-item>
        <el-form-item :label="$t('Report.Label.Node')" label-width="100px">
          <multi-node-selector class="reportFilter-button" id="tid_report-filter-node-select" :filter-type="'hostname'" :hostname-max="50" :allable="isAllable" @nodes-selected-change="nodeSelectChange"></multi-node-selector>
        </el-form-item>
      </el-form>
      <div class="antilles-date-picke">
        <el-button id="tid_report-submit" type="primary" @click="submit()" :disabled="isDisabled">{{$t("Report.Button.Preview")}}</el-button>
        <el-button @click="download()" :disabled="isDisabled">{{$t("Report.Button.Submit")}}</el-button>
      </div>
    </div>
    <div class="nodata" v-show="isShow">
      <div style="margin-top: 160px">
        <img src="../asset/image/report/nodata.png"
        style="height:60px;width: 80px">
      </div>
      <div style="margin-top:20px; color:#ccc;font-size: 16px;">{{$t('NodeGpus.Monitor.No.Data')}}</div>
    </div>

    <div class="reportPreview" v-show="show">
    <el-col :span="24">
      <el-tabs v-model="activeName">
        <el-tab-pane :label='$t("Report.Tab.Chart")' name="chart">
          <report-line :line="data_line"></report-line>
        </el-tab-pane>
      </el-tabs>
    </el-col>
    </div>
    <report-dialog ref="ReportDialog" />
  </div>
</template>
<script>
  import NodeSelect from '../widget/node-select'
  import ReportDialog from './report/report-dialog'
  import ReportLine from './report/report-line'
  import ReportService from '../service/report'
  import _ from "lodash"
  import MultiNodeSelector from '../widget/multi-node-selector'

  export default {
      components: {
        'node-selection':NodeSelect,
        'report-dialog':ReportDialog,
        'report-line':ReportLine,
        'multi-node-selector':MultiNodeSelector
      },
      data () {
        return {
          activeName:"chart",
          data_line:[],
          show:false,
          isShow:false,
          reportFilterForm:{
            node:[],
            monitor_type:'cpu'
          },
          isAllable:false
        };
      },
      computed:{
        isDisabled(){
          if (this.reportFilterForm.node.values.length==0&&this.isAllable==false){
            return true
          } else {
            return false
          }
        }
      },
      methods:{
        download(){
          var data={
            target:'operation',
            job_type:'node_running',
            monitor_type:this.reportFilterForm.monitor_type,
            node:this.reportFilterForm.node
          };
          this.$refs.ReportDialog.download(data).then((res) => {
          window.open(res);
        }, (res) => {
        });
        },
        nodeSelectChange(val){
          this.reportFilterForm.node = val;
        },
        submit(){
          var $this = this;
          var format=this.reportFilterForm.monitor_type == 'net' ? 'MB' : '%';
          ReportService.previewLogReport(this.reportFilterForm).then(function(res){          
            if(res.length>0){              
                $this.show = true;
                $this.isShow = false;              
            }else{
                $this.show = false;
                $this.isShow = true;
            }
            const hostname = [...new Set(res.map(item => item.hostname))];
            const time = [];
            var series = [];
            //var monitor_type = res[0]['type'];
            hostname.forEach(function(item){
              var line_data = [];
              _.filter(res,{'hostname':item})[0]['history'].forEach(function(cell){
                line_data.push([cell['time'],Number(cell['usage'])]);
                time.push(cell['time']);
              });
              series.push({
                name:item,
                type:'line',
                // stack: monitor_type,
                data:line_data
              });
            });
            var unique_time = [...new Set(time.map(item => item))];
            $this.data_line={
              time:unique_time,
              legend:hostname,
              series:series,
              format:format
            }
          },function(error){


          });
        }
      }
    }
</script>
