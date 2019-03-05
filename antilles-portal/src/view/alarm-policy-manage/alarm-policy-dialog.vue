<style>
.el-form-item.is-error .not-valid .el-input__inner, .el-form-item.is-error .not-valid .el-textarea__inner {
    border-color: #bfcbd9;
}
#tid_alarm-policy-node .el-input{width: 210px;}
</style>
<template>
  <composite-form-dialog ref="innerDialog"
  :title="title" size="520px"
  :form-model="alarmPolicyForm"
  :form-rules="alarmPolicyRules"
  form-label-width='160px'
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
    <el-form-item :label="$t('Alarm.Policy.Name')" prop="name">
      <el-input id="tid_alarm-policy-name" v-model="alarmPolicyForm.name" :disabled="mode != 'create'"></el-input>
    </el-form-item>
    <div v-if="mode != 'delete'">
      <el-form-item :label="$t('Alarm.Policy.Monitor')" prop="monitor">
        <el-select id="tid_alarm-policy-monitor" v-model="alarmPolicyForm.monitor"
        @change="monitorChange()">
          <el-option
      v-for="item in AlarmTriggerMonitorEnums"
      :key="item"
      :label="$t('Alarm.Policy.'+ item)"
      :value="item"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item v-if="showCondition" :label="$t('Alarm.Policy.Condition')" :prop="alarmPolicyForm.AlarmInputRole.value && mode != 'delete' ? 'value':''">
        <div class="not-valid">
          <el-select id="tid_alarm-policy-condition" v-model="alarmPolicyForm.condition">
            <el-option
      v-for="item in alarmPolicyForm.AlarmInputRole.typeOptions"
      :key="item"
      :label="$t('Alarm.Policy.'+ item)"
      :value="item"></el-option>
          </el-select>
        </div>
        <el-input id="tid_alarm-policy-condition-value"
  v-model="alarmPolicyForm.value"
  v-if="alarmPolicyForm.AlarmInputRole.value">
     <template slot="append">{{alarmPolicyForm.AlarmInputRole.unit}}</template>
  </el-input>
      </el-form-item>
      <el-form-item :label="$t('Alarm.Policy.Duration')" :prop="mode != 'delete' ? 'duration' : ''">
        <el-input id="tid_alarm-policy-duration" v-model="alarmPolicyForm.duration" :disabled="!alarmPolicyForm.AlarmInputRole.duration">
          <template slot="append">S</template>
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('Alarm.Policy.Level')" :prop="mode != 'delete' ? 'level' : ''">
        <el-radio id="tid_alarm-policy-level-fatal" class="radio" v-model="alarmPolicyForm.level" label="fatal">{{$t("Alarm.PolicyLevel.fatal")}}</el-radio>
        <el-radio id="tid_alarm-policy-level-error" class="radio" v-model="alarmPolicyForm.level" label="error">{{$t("Alarm.PolicyLevel.error")}}</el-radio>
        <el-radio id="tid_alarm-policy-level-warn" class="radio" v-model="alarmPolicyForm.level" label="warn">{{$t("Alarm.PolicyLevel.warn")}}</el-radio>
        <el-radio id="tid_alarm-policy-level-info" class="radio" v-model="alarmPolicyForm.level" label="info">{{$t("Alarm.PolicyLevel.info")}}</el-radio>
      </el-form-item>
      <el-form-item :label="$t('Alarm.Policy.Nogify')">
        <el-select id="tid_alarm-policy-notify" v-model="alarmPolicyForm.nogify" multiple>
            <el-option
      v-for="item in AlarmNotifyList"
      :key="item.id"
      :label="item.name"
      :value="item.id"></el-option>
          </el-select>
      </el-form-item>
      <el-form-item :label="$t('Alarm.Policy.Node')">
        <multi-node-selector id="tid_alarm-policy-node" :nodes="alarmPolicyForm.node" @nodes-selected-change="nodeSelectChange" :hostname-max="50"></multi-node-selector>
      </el-form-item>
      <!-- <el-form-item :label="$t('Alarm.Policy.Email')">
        <el-input
  type="textarea"
  :rows="2"
  :placeholder="$t('Alarm.Policy.Hint.Comma')"
  v-model="alarmPolicyForm.email"></el-input>
      </el-form-item>
      <el-form-item :label="$t('Alarm.Policy.SMS')">
        <el-input
  type="textarea"
  :rows="2"
  :placeholder="$t('Alarm.Policy.Hint.Comma')"
  v-model="alarmPolicyForm.sms"></el-input>
      </el-form-item> -->
      <el-form-item :label="$t('Alarm.Policy.Script')">
        <el-select id="tid_alarm-policy-script" v-model="alarmPolicyForm.script" :placeholder="$t('Alarm.Policy.Hint.Select')">
          <el-option
      v-for="script in AlarmScriptList"
      :key="script"
      :label="script"
      :value="script"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('Alarm.Policy.Notice')">
        <el-checkbox id="tid_alarm-policy-notice-wechat" v-model="alarmPolicyForm.wechat">{{$t('Alarm.Policy.Notice.Wechat')}}</el-checkbox>
        <el-checkbox id="tid_alarm-policy-notice-sound" v-model="alarmPolicyForm.sound">{{$t('Alarm.Policy.Notice.Sound')}}</el-checkbox>
      </el-form-item>
      <el-form-item :label="$t('Alarm.Policy.Status')">
        <el-checkbox id="tid_alarm-policy-status" v-model="alarmPolicyForm.status">{{$t('Alarm.Policy.Notice.Open')}}</el-checkbox>
      </el-form-item>
    </div>
  </composite-form-dialog>
</template>
<script>
import AlarmPolicyService from '../../service/alarm-policy'
import AlarmScriptService from '../../service/alarm-script'
import NotifuGroupService from '../../service/notify-group'
import CompositeFormDialog from '../../component/composite-form-dialog'
import ValidRoleFactory from '../../common/valid-role-factory'
import NodeSelect from '../../widget/node-select'
import MultiNodeSelector from '../../widget/multi-node-selector'

export default {
  data() {
    return {
      AlarmTriggerMonitorEnums:AlarmPolicyService.AlarmTriggerMonitorEnums,
      AlarmScriptList:[],
      AlarmNotifyList:[],
      getAlarmPolicyById: AlarmPolicyService.getAlarmPolicyById,
      title:'',
      mode: '',
      id: 0,
      showCondition:true,
      alarmPolicyForm: {
        name: '',
        monitor: 'CPU',
        condition: '',
        value: '50',
        duration: '60',
        level:'',
        nogify:'',
        node:[],
        email:'',
        sms:'',
        script:'',
        wechat:false,
        sound:false,
        status:false,
        AlarmInputRole: AlarmPolicyService.getTriggerInputRole('CPU')
      },
      alarmPolicyRules: {
        name: [
          ValidRoleFactory.getRequireRoleForText(this.$t('Alarm.Policy.Name')),
          ValidRoleFactory.getLengthRoleForText(this.$t('Alarm.Policy.Name'), 3, 20),
          ValidRoleFactory.getValidIdentityNameRoleForText(this.$t('Alarm.Policy.Name'))
        ],
        value: [
          ValidRoleFactory.getValidNumberRoleForText(this.$t('Alarm.Policy.Value')),
          ValidRoleFactory.getRequireRoleForText(this.$t('Alarm.Policy.Value')),
          ValidRoleFactory.getNumberRangeRoleForText(this.$t('Alarm.Policy.Value'),0,100),
          ValidRoleFactory.getNumberDecimalRoleForText(this.$t('Alarm.Policy.Value'),0)
        ],
        duration: [
          ValidRoleFactory.getValidNumberRoleForText(this.$t('Alarm.Policy.Duration')),
          ValidRoleFactory.getRequireRoleForText(this.$t('Alarm.Policy.Duration')),
          ValidRoleFactory.getNumberRangeRoleForText(this.$t('Alarm.Policy.Duration'),0,99999)
        ],
        level: [
          ValidRoleFactory.getRequireRoleForText(this.$t('Alarm.Policy.Level'))
        ]
      }
    };
  },
  mounted(){
    var $this=this;
    AlarmScriptService.getAllAlarmScripts().then(function(res){
      $this.AlarmScriptList = res;
    });
  },
  components: {
    'composite-form-dialog': CompositeFormDialog,
    'node-selection':NodeSelect,
    'multi-node-selector':MultiNodeSelector
  },
  methods: {
    submitForm() {
      if(this.mode == 'create') {
        return AlarmPolicyService.createAlarmPolicy(this.alarmPolicyForm);
      }
      if(this.mode == 'edit') {
        return AlarmPolicyService.updateAlarmPolicy(this.id, this.alarmPolicyForm);
      }
      if(this.mode == 'delete') {
        return AlarmPolicyService.deleteAlarmPolicy(this.id);
      }
    },
    successMessageFormatter(res) {
      var alarmPolicy = res;
      if(this.mode == 'create') {
        return this.$t('Alarm.Policy.Create.Success', {'name': this.alarmPolicyForm.name});
      }
      if(this.mode == 'edit') {
        return this.$t('Alarm.Policy.Edit.Success', {'name': this.alarmPolicyForm.name});
      }
      if(this.mode == 'delete') {
        return this.$t('Alarm.Policy.Delete.Success', {'name': this.alarmPolicyForm.name});
      }
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    initNotifyGroup(){
      const nogifyList = [];
      NotifuGroupService.getAllNotifyGroups().then(function(res){
        res.forEach(function(item){
          nogifyList.push({
            name:item.name,
            id:item.id
          });
        });
      });
        this.AlarmNotifyList = nogifyList;
    },
    doCreate() {
      this.initNotifyGroup();
      this.mode = 'create';
      this.alarmPolicyForm = {
        name: '',
        monitor: 'CPU',
        condition: 'Greater',
        value: 50,
        duration: '60',
        level:'',
        nogify:[],
        node:[],
        email:'',
        sms:'',
        script:'',
        wechat:false,
        sound:false,
        status:false,
        AlarmInputRole: AlarmPolicyService.getTriggerInputRole('CPU')
      };
      if(this.alarmPolicyForm.monitor == "Hardware" || this.alarmPolicyForm.monitor == "Network"){
        this.showCondition = false;
      } else {
        this.showCondition = true;
      }
      this.title = this.$t("Alarm.Policy.Dialog.Title");
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doEdit(id) {
      this.getAlarmPolicyById(id).then((res) => {
        var alarmPolicy = res;
        this.initNotifyGroup();
        this.mode = 'edit';
        this.id = alarmPolicy.id;
        this.alarmPolicyForm = {
          name: alarmPolicy.name,
          monitor: alarmPolicy.trigger.monitor,
          condition: alarmPolicy.trigger.type,
          value: alarmPolicy.trigger.value,
          duration: alarmPolicy.trigger.duration,
          level:alarmPolicy.level,
          nogify:alarmPolicy.targets,
          node:alarmPolicy.node,
          email:alarmPolicy.email,
          sms:alarmPolicy.sms,
          script:alarmPolicy.script,
          wechat:alarmPolicy.wechat,
          sound:alarmPolicy.sound,
          status:alarmPolicy.status,
          AlarmInputRole: AlarmPolicyService.getTriggerInputRole(alarmPolicy.trigger.monitor)
        };
        if(this.alarmPolicyForm.monitor == "Hardware" || this.alarmPolicyForm.monitor == "Network"){
          this.showCondition = false;
        } else {
          this.showCondition = true;
        }
        var maxLength = this.alarmPolicyForm.AlarmInputRole.unit == '%' ? 100 : 200;
        this.alarmPolicyRules.value = [
          ValidRoleFactory.getValidNumberRoleForText(this.$t('Alarm.Policy.Value')),
          ValidRoleFactory.getRequireRoleForText(this.$t('Alarm.Policy.Value')),
          ValidRoleFactory.getNumberRangeRoleForText(this.$t('Alarm.Policy.Value'),0, maxLength),
          ValidRoleFactory.getNumberDecimalRoleForText(this.$t('Alarm.Policy.Value'),0)
        ]
        this.title = this.$t('Alarm.Policy.Edit.Title', {name: alarmPolicy.name});
      }, (res) => {
        this.$message.error(res)
      })
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doDelete(id) {
      this.getAlarmPolicyById(id).then((res) => {
        var alarmPolicy = res;
        this.mode = 'delete';
        this.id = alarmPolicy.id;
        this.alarmPolicyForm = {
          name: alarmPolicy.name,
          monitor: alarmPolicy.type,
          condition: alarmPolicy.trigger.type,
          value: alarmPolicy.trigger.value,
          duration: alarmPolicy.trigger.duration,
          AlarmInputRole: AlarmPolicyService.getTriggerInputRole(alarmPolicy.type)
        };
        this.title = this.$t('Alarm.Policy.Delete.Title', {name: alarmPolicy.name});
      }, (res) => {
        this.$message.error(res)
      })
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    monitorChange(){
      this.alarmPolicyForm.AlarmInputRole = AlarmPolicyService.getTriggerInputRole(this.alarmPolicyForm.monitor);
      if(!this.alarmPolicyForm.AlarmInputRole.typeOptions.includes(this.alarmPolicyForm.condition)){
        this.alarmPolicyForm.condition = this.alarmPolicyForm.AlarmInputRole.typeOptions[0];
      }
      if(this.alarmPolicyForm.monitor == "Hardware" || this.alarmPolicyForm.monitor == "Network"){
        this.showCondition = false;
      } else {
        this.showCondition = true;
      }
      var maxLength = this.alarmPolicyForm.AlarmInputRole.unit == '%' ? 100 : 200;
      this.alarmPolicyRules.value = [
        ValidRoleFactory.getValidNumberRoleForText(this.$t('Alarm.Policy.Value')),
        ValidRoleFactory.getRequireRoleForText(this.$t('Alarm.Policy.Value')),
        ValidRoleFactory.getNumberRangeRoleForText(this.$t('Alarm.Policy.Value'),0, maxLength),
        ValidRoleFactory.getNumberDecimalRoleForText(this.$t('Alarm.Policy.Value'),0)
      ]
    },
    nodeSelectChange(val){
      this.alarmPolicyForm.node = val;
    }
  }
}
</script>
