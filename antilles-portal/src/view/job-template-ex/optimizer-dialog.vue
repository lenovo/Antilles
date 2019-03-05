<style lang="css">
</style>

<template lang="html">
  <composite-form-dialog
    ref="innerDialog"
    :title="$t('JobTemplate.Optimizer.Dialog.Title')"
    size="580px"
    :form-model="innerForm"
    :form-rules="innerRules">
    <el-form-item v-for="(param, index) in optimizerParams"
      :label="$t(param.label)" label-width="180px"
      :prop="param.key" :key="index">
      <el-input v-if="param.type == 'number'"
        v-model="innerForm[param.key]"></el-input>
      <el-checkbox v-if="param.type == 'bool'"
        v-model="innerForm[param.key]"></el-checkbox>
    </el-form-item>
  </composite-form-dialog>
</template>

<script>
import ValidRoleFactory from '../../common/valid-role-factory'
import CompositeFormDialog from '../../component/composite-form-dialog'
import OptimizerDefine from './optimizer-define'

export default {
  data() {
    return {
      innerForm: {},
      innerRules: {},
      optimizerType: '',
      optimizerParams: []
    };
  },
  components: {
      'composite-form-dialog': CompositeFormDialog
  },
  methods: {
    doSetting(type, setting) {
      return new Promise((resolve, reject) => {
        this.optimizerType = type;
        for(var i=0; i<OptimizerDefine.optimizers.length; i++) {
          var optimizer = OptimizerDefine.optimizers[i];
          if(optimizer.key == type) {
            this.optimizerParams = optimizer.params;
            break;
          }
        };
        var form = new Object();
        var rule = new Object();
        for(var i=0; i<this.optimizerParams.length; i++) {
          var param = this.optimizerParams[i];
          form[param.key] = setting[type][param.key];
          rule[param.key] = [];
          if(param.type == 'number') {
            rule[param.key].push(ValidRoleFactory.getRequireRoleForText(this.$t(param.label)));
            rule[param.key].push(ValidRoleFactory.getValidNumberRoleForText(this.$t(param.label)));
          }
        }
        this.innerForm = form;
        this.innerRules = rule;
        this.$refs.innerDialog.emptyPopup().then((res) => {
          var newSetting = new Object();
          for(var i=0; i<OptimizerDefine.optimizers.length; i++) {
            var optimizer = OptimizerDefine.optimizers[i];
            newSetting[optimizer.key] = new Object();
            for(var j=0; j<optimizer.params.length; j++) {
              var param = optimizer.params[j];
              if(optimizer.key == type) {
                newSetting[optimizer.key][param.key] = this.innerForm[param.key];
              } else {
                newSetting[optimizer.key][param.key] = setting[optimizer.key][param.key];
              }
            }
          }
          resolve(newSetting);
        }, (res) => {
          reject(res);
        });
      });
    }
  }
}
</script>
