<style>
.lh-20 label{
  line-height: 20px;
}
</style>
<template>
<composite-form-dialog ref="innerDialog"
  :type="type"
  :title="title" size="530px"
  form-label-width="180px"
  :form-model="schedulerForm"
  :form-rules="FormRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
  <el-form-item :label="$t('Scheduler.Queue')" prop="queue">
    <el-input v-model="schedulerForm.queue" :disabled="mode == 'delete' || mode =='edit' || mode =='setQueueState'"></el-input>
  </el-form-item>
  <el-form-item :label="$t('Scheduler.Nodes')" prop="nodes" v-if="mode != 'setQueueState'">
    <el-input type="textarea" v-model="schedulerForm.nodes" :disabled="mode == 'delete'"></el-input>
  </el-form-item>
  <el-form-item :label="$t('Scheduler.Default')" v-if="mode == 'create' || mode == 'edit'">
    <el-checkbox v-model="schedulerForm.isDefault"></el-checkbox>
  </el-form-item>
  <el-form-item :label="$t('Scheduler.Priority')" prop="priority" v-if="mode == 'create' || mode == 'edit'">
    <el-input v-model="schedulerForm.priority" :disabled="mode == 'delete'"></el-input>
  </el-form-item>
  <el-form-item :label="$t('Scheduler.MaxTime')" v-if="mode == 'create' || mode == 'edit'" >
    <el-checkbox v-model="schedulerForm.maxTime.unlimited">UNLIMITED</el-checkbox>
  </el-form-item>
  <el-form-item v-if="!schedulerForm.maxTime.unlimited && (mode == 'create' || mode == 'edit')" prop="maxTime.value" >
    <el-input v-model="schedulerForm.maxTime.value">
      <template slot="append">{{$t('Scheduler.Days') + '-' + $t('Scheduler.Hours') + ':' + $t('Scheduler.Mins')}}</template>
    </el-input>
  </el-form-item>
  <el-form-item :label="$t('Scheduler.OverSubscribe')" v-if="mode == 'create' || mode == 'edit'">
    <el-select v-model="schedulerForm.overSubscribeValue.value">
      <el-option
        v-for="item in overSubscribeOptions"
        :key="item.value"
        :label="item.label"
        :value="item.value">
      </el-option>
    </el-select>
  </el-form-item>
  <el-form-item class="lh-20" :label="$t('Scheduler.OverSubscribeNumber')" prop="overSubscribeValue.number" v-if="(mode == 'create' || mode == 'edit') && (schedulerForm.overSubscribeValue.value == 'YES' || schedulerForm.overSubscribeValue.value == 'FORCE')">
    <el-input v-model="schedulerForm.overSubscribeValue.number"></el-input>
  </el-form-item>
  <el-form-item :label="$t('Scheduler.UserGroups')" v-if="mode == 'create' || mode == 'edit'">
    <el-select v-model="schedulerForm.userGroupsValue" multiple placeholder="All">
      <el-option
        v-for="item in userGroupsOptions"
        :key="item.value"
        :label="item.label"
        :value="item.value">
      </el-option>
    </el-select>
  </el-form-item>
  <el-form-item :label="$t('Scheduler.State')" v-if="mode == 'create' || mode == 'edit' || mode == 'delete'">
    <el-select v-model="schedulerForm.stateValue" :disabled="mode == 'delete'">
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
import UserGroupsService from '../../service/user-group'
import CompositeFormDialog from '../../component/composite-form-dialog'
import ValidRoleFactory from '../../common/valid-role-factory'

export default {
  data() {
    return {
      title: '',
      mode: '',
      type: 'submit',
      overSubscribeOptions: [{
        value: 'NO',
        label: 'NO'
      }, {
        value: 'YES',
        label: 'YES'
      }, {
        value: 'EXCLUSIVE',
        label: 'EXCLUSIVE'
      }, {
        value: 'FORCE',
        label: 'FORCE'
      }],
      userGroupsOptions:[],
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
      schedulerForm: {
        queue: '',
        nodes: '',
        priority: '1',
        isDefault:true,
        maxTime:{
          unlimited:true,
          value: ''
        },
        userGroupsValue: [],
        stateValue: 'UP',
        overSubscribeValue: {
          value:'NO',
          number: '4'
        }
      },
      FormRules: {
        queue: [
          ValidRoleFactory.getRequireRoleForText(this.$t('Scheduler.Queue')),
          ValidRoleFactory.getLengthRoleForText(this.$t('Scheduler.Queue'), 3, 20),
          ValidRoleFactory.getValidIdentityNameRoleForText(this.$t('Scheduler.Queue'))
        ],
        nodes:[
          ValidRoleFactory.getRequireRoleForText(this.$t('Scheduler.Nodes')),
          ValidRoleFactory.getNodesExpressionRoleForText(this.$t('Scheduler.Nodes'))
        ],
        priority:[
          ValidRoleFactory.getValidNumberRoleForText(this.$t('Scheduler.Priority')),
          ValidRoleFactory.getNumberRangeRoleForText(this.$t('Scheduler.Priority'),0,65533),
          ValidRoleFactory.getRequireRoleForText(this.$t('Scheduler.Priority'))
        ],
        'overSubscribeValue.number':[
          ValidRoleFactory.getValidNumberRoleForText(this.$t('Scheduler.OverSubscribeNumber')),
          ValidRoleFactory.getNumberRangeRoleForText('Scheduler.OverSubscribeNumber',1,32767),
          ValidRoleFactory.getRequireRoleForText(this.$t('Scheduler.OverSubscribeNumber'))
        ],
        'maxTime.value':[
          ValidRoleFactory.getRequireRoleForText(this.$t('Scheduler.MaxTime')),
          ValidRoleFactory.getMaxTimeForText(this.$t('Scheduler.MaxTime')),
          ValidRoleFactory.getMaxTimeRangeRoleForText(this.$t('Scheduler.MaxTime')),
        ]
      }
    };
  },
  components: {
    'composite-form-dialog': CompositeFormDialog
  },
  created() {
    // get the user groups
    const that = this;
    UserGroupsService.getAllUserGroups().then((res)=> {
      res.forEach((obj) => {
        that.userGroupsOptions.push({value:obj.name,label:obj.name});
      });
    },(err)=> {
    })
  },
  methods: {
    submitForm() {
      if(this.mode == 'create') {
        var maxTime = this.schedulerForm.maxTime.unlimited
        ?'UNLIMITED'
        :this.schedulerForm.maxTime.value;
        var overSubscribe = this.schedulerForm.overSubscribeValue.value == 'YES' || this.schedulerForm.overSubscribeValue.value == 'FORCE'
        ?this.schedulerForm.overSubscribeValue.value + ':' + parseInt(this.schedulerForm.overSubscribeValue.number)
        :this.schedulerForm.overSubscribeValue.value;
        return SchedulerService.createQueue(this.schedulerForm.queue,this.schedulerForm.nodes,this.schedulerForm.isDefault,this.schedulerForm.priority,maxTime,overSubscribe,this.schedulerForm.userGroupsValue,this.schedulerForm.stateValue);
      }
      if(this.mode == 'edit') {
        var maxTime = this.schedulerForm.maxTime.unlimited
        ?'UNLIMITED'
        :this.schedulerForm.maxTime.value;
        var overSubscribe = this.schedulerForm.overSubscribeValue.value == 'YES' || this.schedulerForm.overSubscribeValue.value == 'FORCE'
        ?this.schedulerForm.overSubscribeValue.value + ':' + parseInt(this.schedulerForm.overSubscribeValue.number)
        :this.schedulerForm.overSubscribeValue.value;
        return SchedulerService.updateQueue(this.schedulerForm.queue,this.schedulerForm.nodes,this.schedulerForm.isDefault,this.schedulerForm.priority,maxTime,overSubscribe,this.schedulerForm.userGroupsValue,this.schedulerForm.stateValue);
      }
      if(this.mode == 'delete') {
        return SchedulerService.deleteQueue(this.schedulerForm.queue);
      }
      if(this.mode == 'setQueueState') {
        return SchedulerService.setQueueState(this.schedulerForm.queue,this.newStateValue);
      }
    },
    successMessageFormatter(res) {
      if(this.mode == 'create') {
        return this.$t('Scheduler.Queue.Create.Success');
      }
      if(this.mode == 'edit') {
        return this.$t('Scheduler.Queue.Edit.Success');
      }
      if(this.mode == 'delete') {
        return this.$t('Scheduler.Queue.Delete.Success');
      }
      if(this.mode == 'setQueueState') {
        return this.$t('Scheduler.Queue.SetState.Success');
      }
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    doCreate() {
      this.mode = 'create';
      this.schedulerForm = {
          queue: '',
          nodes: '',
          priority: 1,
          isDefault: true,
          maxTime:{
            unlimited:true,
            value: ''
          },
          userGroupsValue: [],
          stateValue: 'UP',
          overSubscribeValue: {
            value:'YES',
            number: 4
          }
        };
      this.stateOptions = [{
        value: 'UP',
        label: 'UP'
      }, {
        value: 'DOWN',
        label: 'DOWN'
      }];
      this.title = this.$t('SchedulerDialog.CreateQueue.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doEdit(queue) {
      this.mode = 'edit';
      this.stateOptions = [{
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
      }];
      SchedulerService.getQueue(queue.queueName).then((res)=> {
        this.schedulerForm = {
          queue: res.queue_name,
          nodes: Object.values(res.nodes_list).toString(),
          priority: res.priority,
          isDefault:res.default,
          maxTime:res.max_time == 'UNLIMITED'
          ?{unlimited:true,value:''}
          :{unlimited:false,value:res.max_time},
          userGroupsValue: res.user_groups[0] == 'ALL' ? [] : res.user_groups.toString().split(','),
          stateValue: res.avail,
          overSubscribeValue: {
            value:  (res.over_subscribe.includes('YES') || res.over_subscribe.includes('FORCE'))?(res.over_subscribe.includes('YES')?'YES':'FORCE'):res.over_subscribe,
            number: (res.over_subscribe.includes('YES') || res.over_subscribe.includes('FORCE'))?(res.over_subscribe.includes('YES')?parseInt(res.over_subscribe.slice(4,res.over_subscribe.length)):parseInt(res.over_subscribe.slice(6,res.over_subscribe.length))):''
          }
        }
      },(err)=> {

      })
      this.title = this.$t('SchedulerDialog.EditQueue.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doDelete(queue) {
      this.mode = 'delete';
      SchedulerService.getQueue(queue.queueName).then((res)=> {
        this.schedulerForm.queue = res.queue_name;
        this.schedulerForm.nodes = Object.values(res.nodes_list).toString();
        this.currentStateValue = res.avail;
      },(err)=> {

      })
      this.title = this.$t('SchedulerDialog.DeleteQueue.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>
