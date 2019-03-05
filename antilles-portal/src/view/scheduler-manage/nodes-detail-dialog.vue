<template>
<composite-form-dialog ref="innerDialog"
  :title="title" size="500px"
  :form-model="nodesStateForm">
  <el-form-item :label="$t('Scheduler.Queue')">
    <el-input v-model="nodesStateForm.queue" disabled></el-input>
  </el-form-item>
  <el-form-item :label="$t('Scheduler.NodesState')">
    <el-select v-model="stateValue" placeholder="" @change="chooseNodes">
      <el-option
        v-for="item in stateOptions"
        :key="item.value"
        :label="item.label"
        :value="item.value">
      </el-option>
    </el-select>
  </el-form-item>
  <el-form-item :label="stateValue.slice(0,1).toUpperCase() + stateValue.slice(1)  + ' ' + $t('Scheduler.Nodes')">
    <el-input type="textarea" v-model="nodesStateForm.nodes" readonly></el-input>
  </el-form-item>
</composite-form-dialog>
</template>
<script>
import SchedulerService from '../../service/scheduler'
import CompositeFormDialog from '../../component/composite-form-dialog'

export default {
  data() {
    return {
      title: '',
      nodesStateForm: {
        queue: '',
        nodes: '',
      },
      tempNodesState:[],
      tempNodes:[],
      stateValue: '',
      stateOptions:[],
    };
  },
  components: {
    'composite-form-dialog': CompositeFormDialog
  },
  methods: {
    showNodes(queue) {
      SchedulerService.getQueue(queue.queueName).then((res)=> {
        this.nodesStateForm.queue = res.queue_name;
        this.nodesStateForm.nodes = Object.values(res.nodes_list)[0];
        this.stateValue = Object.keys(res.nodes_list)[0];
        this.tempNodesState = Object.keys(res.nodes_list);
        this.tempNodes = Object.values(res.nodes_list)
        this.stateOptions = [];
        for(var i=0;i<this.tempNodesState.length;i++){
          this.stateOptions.push({value: this.tempNodesState[i],label: this.tempNodesState[i]})
        }
      },(err)=> {

      })
      this.title = this.$t('SchedulerDialog.Title.Nodesdetail');
      return this.$refs.innerDialog.popup();
    },
    chooseNodes() {
      if(this.tempNodesState.indexOf(this.stateValue)!= -1){
        this.nodesStateForm.nodes = this.tempNodes[this.tempNodesState.indexOf(this.stateValue)];
      }
    }
  }
}
</script>
