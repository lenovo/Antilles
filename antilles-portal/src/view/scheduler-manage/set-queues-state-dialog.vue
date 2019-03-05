<template>
<composite-form-dialog ref="innerDialog"
  :type="type"
  :title="title" size="500px"
  :form-model="queue"
  :form-rules="FormRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
  <el-form-item :label="$t('Scheduler.Queue')">
    <el-input v-model="queue.queueName" disabled></el-input>
  </el-form-item>
  <el-form-item :label="$t('Scheduler.CurrentState')">
    <el-input v-model="currentStateValue" disabled>
    </el-input>
  </el-form-item>
  <el-form-item :label="$t('Scheduler.NewState')">
    <el-select v-model="newStateValue">
      <el-option
        v-for="item in stateOptions"
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

export default {
  data() {
    return {
      title: '',
      mode: '',
      type: 'submit',
      stateOptions:[{
        value: 'UP',
        label: 'UP'
      }, {
        value: 'DOWN',
        label: 'DOWN'
      }, {
        value: 'DRAIN',
        label: 'DRAIN'
      }, {
        value: 'INACTIVE',
        label: 'INACTIVE'
      }],
      currentStateValue: 'UP',
      newStateValue: 'UP',
      queue:{
        queueName:''
      },
      FormRules:{}
    };
  },
  components: {
    'composite-form-dialog': CompositeFormDialog
  },
  methods: {
    submitForm() {
      if(this.mode == 'setQueueState') {
        return SchedulerService.setQueueState(this.queue.queueName,this.newStateValue);
      }
    },
    successMessageFormatter(res) {
      if(this.mode == 'setQueueState') {
        return this.$t('Scheduler.Queue.SetState.Success');
      }
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    setQueueStatus(queue) {
      this.mode = 'setQueueState';
      this.newStateValue = 'UP';
      SchedulerService.getQueue(queue.queueName).then((res)=> {
        this.queue.queueName = res.queue_name;
        this.currentStateValue = res.avail;
      },(err)=> {

      })
      this.title = this.$t('SchedulerDialog.SetQueueState.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>
