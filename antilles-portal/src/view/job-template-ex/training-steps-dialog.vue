<template>
  <composite-form-dialog
    class="training-steps-dialog"
    ref="innerDialog"
    :title="$t('JobTemplate.TrainingSteps.Dialog.Title')"
    size="580px"
    :form-model="innerForm"
    :form-rules="innerRules">
    <!--Log Every Steps-->
    <el-form-item prop="logEverySteps"
      label-width="180px" :label="$t('JobTemplate.TrainingSteps.LogEverySteps')">
      <el-input v-model="innerForm.logEverySteps"></el-input>
    </el-form-item>
    <!--Save Every Steps-->
    <el-form-item  prop="saveEverySteps"
      label-width="180px" :label="$t('JobTemplate.TrainingSteps.SaveEverySteps')">
      <el-input v-model="innerForm.saveEverySteps"></el-input>
    </el-form-item>
  </composite-form-dialog>
</template>
<script>
  import CompositeFormDialog from '../../component/composite-form-dialog'
  import ValidRoleFactory from '../../common/valid-role-factory'

  export default {
    components: {
      'composite-form-dialog': CompositeFormDialog
    },
    data() {
      return{
        innerForm: {
          logEverySteps: "",
          saveEverySteps: ""
        },
        innerRules: {
          logEverySteps: [
            ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.TrainingSteps.LogEverySteps')),
            ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.TrainingSteps.LogEverySteps')),
            ValidRoleFactory.getRangeRoleForNumber(this.$t('JobTemplate.TrainingSteps.LogEverySteps'), 1, 999999999)
          ],
          saveEverySteps: [
            ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.TrainingSteps.SaveEverySteps')),
            ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.TrainingSteps.SaveEverySteps')),
            ValidRoleFactory.getRangeRoleForNumber(this.$t('JobTemplate.TrainingSteps.SaveEverySteps'), 1, 999999999)
          ]
        }
      }
    },
    methods: {
      doSetting(setting) {
        return new Promise((resolve, reject) => {
          this.innerForm = {
            logEverySteps: String(setting.logEverySteps),
            saveEverySteps: String(setting.saveEverySteps)
          };
          this.$refs.innerDialog.emptyPopup().then((res) => {
            var setting = {
              logEverySteps: parseInt(this.innerForm.logEverySteps),
              saveEverySteps: parseInt(this.innerForm.saveEverySteps)
            };
            resolve(setting);
          }, (res) => {
            reject(res);
          });
        });
      }
    }
  }
</script>
