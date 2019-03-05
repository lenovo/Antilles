
<template lang="html">
  <composite-form-dialog ref="innerDialog"
    :title="title" :size="mode == 'edit'?'500px':'300px'"
    :form-model="alarmForm"
    :form-rules="alarmRules"
    :successMessageFormatter="successMessageFormatter"
    :errorMessageFormatter="errorMessageFormatter">
    <el-form-item prop="comment" v-if="mode == 'edit'" :label="$t('Alarm.Table.title.comment')">
      <el-input type="textarea" v-model="alarmForm.comment" :disabled="mode == 'delete'"></el-input>
    </el-form-item>
    <div v-if='mode != "edit"'>{{ $t('Alarm.Action.tips') }}</div>
  </composite-form-dialog>
</template>

<script>

import AlarmService from '../service/alarm'
import CompositeFormDialog from '../component/composite-form-dialog'
import ValidRoleFactory from '../common/valid-role-factory'

export default {
  data () {
    return {
      title: '',
      mode: '',
      alarmId: 0,
      //alarmName: '',
      actionAll: 'All',
      idList: [],
      statusList: [],
      levelList: [],
      timeRange: [],
      alarmForm: {
        comment: ''
      },
      alarmRules: {
        comment: [
          ValidRoleFactory.getLengthRoleForText(this.$t('Alarm.Table.title.comment'), 0, 100)
        ]
      }
    }
  },
  components: {
    'composite-form-dialog': CompositeFormDialog
  },
  methods: {
    submitForm() {
      if(this.mode == 'edit') {
        return AlarmService.updateAlarmComment(this.alarmId, this.alarmForm.comment);
      }
      if(this.mode == 'confirm') {
        return AlarmService.confirmAlarms(this.idList, this.statusList, this.levelList, this.timeRange);
      }
      if(this.mode == 'fix') {
        return AlarmService.fixAlarms(this.idList, this.statusList, this.levelList, this.timeRange);
      }
      if(this.mode == 'delete') {
        return AlarmService.deleteAlarms(this.idList, this.statusList, this.levelList, this.timeRange);
      }
    },
    successMessageFormatter(res) {
      if(this.mode == 'edit') {
        return this.$t('Alarm.Comment.Edit.Success');
        //return this.$t('Alarm.Comment.Edit.Success', {'name': this.alarmName});
      } else {
        return this.$t('Alarm.Action.Success', {'action': this.$t('Alarm.Action.'+this.mode)});
      }
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    setAction(action, idList ,filter) {
      this.title = this.$t('Alarm.Action.'+ action);
      if(action.indexOf(this.actionAll) !== -1) {
        idList = [];
      }
      this.idList = idList;
      this.statusList = filter.status.values;
      this.levelList = filter.policyLevel.values;
      this.timeRange = filter.createTime.values;
    },
    doEdit(alarm) {
      this.mode = 'edit';
      this.alarmId = alarm.id;
      //this.alarmName = alarm.policyName;
      this.alarmForm = {
        comment: alarm.comment
      };
      this.title = this.$t('Alarm.Comment.Edit.Title', {id: alarm.id});
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doConfirm(action, idList ,filter) {
      this.mode = 'confirm';
      this.setAction(action, idList ,filter);
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doFix(action, idList ,filter) {
      this.mode = 'fix';
      this.setAction(action, idList ,filter);
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doDelete(action, idList ,filter) {
      this.mode = 'delete';
      this.setAction(action, idList ,filter);
      return this.$refs.innerDialog.popup(this.submitForm);
    },
  }
}
</script>
