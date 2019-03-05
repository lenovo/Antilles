<template>
  <div id="tid_reportFilter">
    <div class="reportFilter-div-header">{{$t("Report.Title.Filter")}}</div>
    <el-form :model="ReportFilterForm" :rules="ReportFilterRules">
      <el-form-item :label="$t('Report.Label.Type')" prop="type" v-if="filters == 'job'" label-width="100px">
        <el-radio-group v-model="ReportFilterForm.job_type" class="reportFilter-button">
          <el-radio-button id="tid_report-filter-type-job" label="job" >{{$t('Report.Label.Type.Job')}}</el-radio-button>
          <el-radio-button id="tid_report-filter-type-user" label="user">{{$t('Report.Label.Type.User')}}</el-radio-button>
          <el-radio-button id="tid_report-filter-type-billgroup" label="billgroup">{{$t('Report.Label.BillGroup')}}</el-radio-button>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item :label="$t('Report.Action.Label.Type')" prop="operation_type" v-if="filters == 'operation'" label-width="100px">
        <el-radio-group v-model="ReportFilterForm.operation_type" class="reportFilter-button">
          <el-radio-button id="tid_report-filter-type-log" label="log">{{$t('Report.Label.Operation.Log')}}</el-radio-button>
          <el-radio-button id="tid_report-filter-type-node-running" label="node_running">{{$t('Report.Label.Operation.NodeRunning')}}</el-radio-button>
          <!-- <el-radio-button id="tid_report-filter-type-node-user" label="node_user">{{$t('Report.Label.Operation.NodeUser')}}</el-radio-button>
          <el-radio-button id="tid_report-filter-type-user-login" label="user_login">{{$t('Report.Label.Operation.UserLogin')}}</el-radio-button>
          <el-radio-button id="tid_report-filter-type-user-storage" label="user_storage">{{$t('Report.Label.Operation.UserStorage')}}</el-radio-button> -->
        </el-radio-group>
      </el-form-item>

      <el-form-item :label="$t('Report.Label.Content')" prop="content" v-if="filters != 'operation'" label-width="100px">
        <el-radio-group v-model="ReportFilterForm.content" class="reportFilter-button">
          <el-radio-button id="tid_report-filter-statistics" label="statistics">{{$t('Report.Label.Content.Stat')}}</el-radio-button>
          <el-radio-button id="tid_report-filter-details" label="details">{{$t('Report.Label.Content.Detail')}}</el-radio-button>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item :label="$t('Report.Label.Level')" prop="level" v-if="filters == 'alarm'" label-width="100px">
        <el-radio-group v-model="ReportFilterForm.level" class="reportFilter-button">
          <el-radio-button id="tid_report-filter-level-all" label="all">{{$t('Report.Label.Level.All')}}</el-radio-button>
          <el-radio-button id="tid_report-filter-level-fatal" label="fatal">{{$t('Alarm.PolicyLevel.fatal')}}</el-radio-button>
          <el-radio-button id="tid_report-filter-level-error" label="error">{{$t('Alarm.PolicyLevel.error')}}</el-radio-button>
          <el-radio-button id="tid_report-filter-level-warn" label="warn">{{$t('Alarm.PolicyLevel.warn')}}</el-radio-button>
          <el-radio-button id="tid_report-filter-level-info" label="info">{{$t('Alarm.PolicyLevel.info')}}</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item :label="$t('Report.Label.Node')" v-if="(filters == 'alarm' && ReportFilterForm.content == 'details') || ReportFilterForm.operation_type.startsWith('node')" label-width="100px">
        <node-selection id="tid_report-filter-node-select" @nodes-selected-change="nodeSelectChange" class="reportFilter-button" bindProperty="hostname" :placeholder="$t('Select.All')"></node-selection>
      </el-form-item>
      <el-form-item :label="$t('Report.Label.User')" v-if="(filters == 'job' && ReportFilterForm.job_type != 'billgroup') || ReportFilterForm.operation_type.startsWith('user')" label-width="100px">
        <user-selection id="tid_report-filter-user-select" @change="userSelectionChange" :value="ReportFilterForm.user" bind-property="username" :placeholder="$t('Select.All')" class="reportFilter-button"></user-selection>
      </el-form-item>
      <el-form-item :label="$t('Report.Label.BillGroup')" v-if="ReportFilterForm.job_type == 'billgroup'" label-width="100px">
        <el-select id="tid_report-filter-billgroup-select" v-model="ReportFilterForm.billGroup" class="reportFilter-button" multiple :placeholder="$t('Select.All')">
          <el-option
            v-for="item in billOption"
            :key="item.id"
            :label="item.name"
            :value="item.name"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('Report.Label.Index')" v-if="ReportFilterForm.operation_type == 'node_running'" label-width="100px">
        <el-select id="tid_report-filter-monitor-select" v-model="ReportFilterForm.monitor_type" class="reportFilter-button">
          <el-option
            v-for="item in indexOption"
            :key="item.key"
            :label="item.label"
            :value="item.value"></el-option>
        </el-select>
      </el-form-item>
    </el-form>
  </div>
</template>
<script>
import NodeSelect from '../../widget/node-select'
import UserSelect from '../../widget/multi-user-selector'
import BillGroupService from '../../service/bill-group'

  export default {
      components:{
        'node-selection':NodeSelect,
        'user-selection':UserSelect
      },
      props: ['filters'],
      mounted(){
        var $this = this;
        BillGroupService.getAllBillGroups().then(function(res){
          $this.billOption = res;
        },function(error){

        });
      },
      data () {
        return {
          ReportFilterForm:{
            job_type:"job",
            operation_type:"log",
            content:"statistics",
            level:"all",
            user:[],
            node:[],
            billGroup:[],
            monitor_type:'cpu'
          },
          billOption:[],
          indexOption:[
            {
              key:'cpu',
              value:'cpu',
              label:this.$t('Report.Label.Index.CPU')
            },
            {
              key:'memory',
              value:'mem',
              label:this.$t('Report.Label.Index.Memory')
            },
            {
              key:'network',
              value:'net',
              label:this.$t('Report.Label.Index.Network')
            }
          ],
          ReportFilterRules:{},
          update:function(){
          this.$emit('report_filter',this.ReportFilterForm);
          }
        };
      },
      methods:{
        nodeSelectChange(val){
          this.ReportFilterForm.node = val;
        },
        userSelectionChange(val){
          this.ReportFilterForm.user = val;
        }
      },
      watch:{
        ReportFilterForm:{
          handler:function(){
                this.update();
            },
          deep:true
        },
        filters(val){
          this.ReportFilterForm = {
            job_type:"job",
            operation_type:"log",
            content:"statistics",
            level:"all",
            user:[],
            node:[],
            billGroup:[],
            monitor_type:'cpu'
          };
        }
      }
    }
</script>
