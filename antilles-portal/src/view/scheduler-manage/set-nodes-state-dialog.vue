<style scoped>
  .content{
    width:600px !important;
  }
  .quering{
    position:absolute;
    left:0;
    background-color:#fff;
    border:0 solid #fff;
    color:#000;
    top:-15px;
  }
  .detailbox{
    position:absolute;
    left:548px;
    top:-15px;
  }
  .detail-title-box{
    margin-bottom:0;
    position:relative;
    height:20px;
  }
</style>
<template>
<composite-form-dialog ref="innerDialog"
  :type="'submit'"
  :title="title" size="800px"
  :form-model="nodesForm"
  :form-rules="FormRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
  <el-form-item :label="$t('Scheduler.Nodes')" prop="nodesExpress">
    <el-input class="content" type="textarea" v-model="nodesForm.nodesExpress" @blur="queryNodesStates"></el-input>
  </el-form-item>
  <el-form-item class="detail-title-box">
    <el-button :loading="loading" v-if="loading" type="primary" size="small" class="quering">{{$t('Scheduler.Action.Query')}}</el-button>
    <el-checkbox v-model="nodesForm.detail" class="detailbox">{{$t('Scheduler.NodesState.Detail')}}</el-checkbox>
  </el-form-item>
  <el-form-item :label="$t('Scheduler.CurrentState')">
    <el-input class="content" :value="nodesForm.detail?nodesForm.statesDetail:nodesForm.states" type="textarea" :autosize="{ minRows: 4,maxRows: 15}" readonly></el-input>
  </el-form-item>
  <el-form-item :label="$t('Scheduler.NewState')">
    <el-select class="content" v-model="action">
      <el-option
        v-for="item in actionOptions"
        :key="item.value"
        :label="item.label"
        :value="item.value">
      </el-option>
    </el-select>
  </el-form-item>
</composite-form-dialog>
</template>
<script>
import SchedulerService from '../../service/scheduler'
import CompositeFormDialog from '../../component/composite-form-dialog'
import ValidRoleFactory from '../../common/valid-role-factory'

export default {
  data() {
    return {
      title: '',
      mode: '',
      loading: false,
      nodesForm: {
        nodesExpress: '',
        detail: false,
        states: '',
        statesDetail: ''
      },
      FormRules: {
        nodesExpress: [
          ValidRoleFactory.getRequireRoleForText(this.$t('Scheduler.Nodes')),
          ValidRoleFactory.getNodesExpressionRoleForText(this.$t('Scheduler.Nodes'))
        ]
      },
      action: 'RESUME',
      actionOptions:[{
        value: 'RESUME',
        label: 'RESUME'
      }, {
        value: 'DOWN',
        label: 'DOWN'
      }],
    };
  },
  components: {
    'composite-form-dialog': CompositeFormDialog
  },
  methods: {
    submitForm() {
      return SchedulerService.setNodesState(this.action,this.nodesForm.nodesExpress);
    },
    successMessageFormatter(res) {
      return this.$t('Scheduler.Queue.SetNodesState.Success');
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    queryNodesStates() {
      if(this.nodesForm.nodesExpress){
        this.loading = true;
        SchedulerService.getNodesState(this.nodesForm.nodesExpress).then((res) => {
          this.nodesForm.statesDetail = res.details;
          var tempStr = '';
          for(var i=0,len=res.node_states.nodes.length;i<len;i++){
            tempStr += res.node_states.nodes[i] + ':' + res.node_states.states[i] + '\n';
          }
          this.nodesForm.states = tempStr; 
          this.loading = false;
        },(err) => {
          this.nodesForm.states = err;
          this.nodesForm.statesDetail = err;
          this.loading = false;
        })
      }else{
        return false;
      }
    },
    setNodesStatus(queue) {
      this.nodesForm.states = '';
      this.nodesForm.statesDetail = '';
      this.action = 'RESUME';
      this.title = this.$t('SchedulerDialog.SetNodesState.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>
