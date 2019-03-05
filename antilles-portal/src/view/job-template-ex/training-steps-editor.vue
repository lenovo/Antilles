<style>
  .training-steps-editor .el-input{width: 300px;}
</style>
<template>
  <div class="training-steps-editor">
    <el-input v-model="maxSteps"></el-input>
    <el-button @click="onSettingClick">{{$t('JobTemplate.TrainingSteps.Setting')}}</el-button>
    <training-steps-dialog ref="settingDialog"></training-steps-dialog>
  </div>
</template>
<script>
  import TrainingStepsDialog from './training-steps-dialog'
  import ValidRoleFactory from '../../common/valid-role-factory'

  export default {
    components:{
      'training-steps-dialog': TrainingStepsDialog
    },
    data() {
      return {
        maxSteps: String(this.value.maxSteps),
        setting: {
          logEverySteps: this.value.logEverySteps,
          saveEverySteps: this.value.saveEverySteps
        }
      }
    },
    props: [ 'value' ],
    watch: {
      maxSteps: function(val, oldVal) {
        this.onValueChanged();
      },
      setting: function(val, oldVal) {
        this.onValueChanged();
      }
    },
    methods: {
      onSettingClick() {
        this.$refs.settingDialog.doSetting(this.setting).then((res) => {
          this.setting = res;
        }, (res) => {
          // Do nothing
        });
      },
      onValueChanged() {
        var trainingSteps = {
          maxSteps: Number(this.maxSteps),
          logEverySteps: this.setting.logEverySteps,
          saveEverySteps: this.setting.saveEverySteps
        };
        this.$emit('input', trainingSteps);
      }
    },
    getValidRules(paramName) {
      return {
        type: "object",
        required: true,
        fields: {
          maxSteps: [
            ValidRoleFactory.getRequireRoleForNumber(paramName),
            ValidRoleFactory.getDecimalRoleForNumber(paramName, 0),
            ValidRoleFactory.getRangeRoleForNumber(paramName, 1, 999999999)
          ]
        }
      };
    }
  }
</script>
