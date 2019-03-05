<template>
  <composite-form-dialog
    ref="innerDialog"
    size="580px"
    :title="$t('JobTemplate.PSWorker.Dialog.Title')"
    :form-model="innerForm"
    :form-rules="innerRules">
    <el-form-item :label="$t('JobTemplate.PSWorker.Mode')" label-width="180px">
      <el-select v-model="innerForm.mode">
        <el-option value="auto" :label="$t('JobTemplate.PSWorker.Mode.Auto')"></el-option>
        <el-option value="manual" :label="$t('JobTemplate.PSWorker.Mode.Manual')"></el-option>
      </el-select>
    </el-form-item>
    <el-form-item prop="psNumber" v-if="innerForm.mode == 'manual'"
      :label='$t("JobTemplate.PSWorker.PSNumber")' label-width="180px">
      <el-input v-model="innerForm.psNumber"></el-input>
    </el-form-item>
    <el-form-item prop="workerNumber" v-if="innerForm.mode == 'manual'"
      :label='$t("JobTemplate.PSWorker.WorkerNumber")' label-width="180px">
      <el-input v-model="innerForm.workerNumber" :disabled="gpuPerNode > 0"></el-input>
    </el-form-item>
    <el-form-item prop="gpuPerWorker" v-if="innerForm.mode == 'manual' && gpuPerNode > 0"
      :label='$t("JobTemplate.PSWorker.GPUPerWorker")' label-width="180px">
      <el-input v-model="innerForm.gpuPerWorker"></el-input>
    </el-form-item>
  </composite-form-dialog>
</template>
<script>
  import CompositeFormDialog from '../../component/composite-form-dialog'
  import ValidRoleFactory from '../../common/valid-role-factory'

  export default {
    data() {
      return {
        innerForm: {
          mode: 'auto',
          psNumber: '1',
          workerNumber: '1',
          gpuPerWorker: '1'
        },
        innerRules: {
        },
        nodes: 0,
        gpuPerNode: 0
      }
    },
    components: {
      'composite-form-dialog': CompositeFormDialog
    },
    watch: {
      'innerForm.mode': function(val, oldVal) {
        this.initRules();
      },
      'innerForm.gpuPerWorker': function(val, oldVal) {
        if(this.gpuPerNode > 0) {
          let gpuPerWorker = parseInt(val);
          if(!isNaN(gpuPerWorker) && gpuPerWorker > 0 && gpuPerWorker <= this.gpuPerNode) {
            if(this.gpuPerNode % gpuPerWorker == 0) {
              this.innerForm.workerNumber = String(this.nodes * this.gpuPerNode / gpuPerWorker);
            } else {
              this.innerForm.workerNumber = '';
            }
          } else {
            this.innerForm.workerNumber = '';
          }
        }        
      }
    },
    methods: {
      initRules() {
        var rules = new Object();
        if(this.innerForm.mode == 'manual') {
          rules['psNumber'] = [
            ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.PSWorker.PSNumber')),
            ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.PSWorker.PSNumber')),
            ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.PSWorker.PSNumber'), 1, 9999)
          ];
          rules['workerNumber'] = [
            ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.PSWorker.WorkerNumber')),
            ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.PSWorker.WorkerNumber')),
            ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.PSWorker.WorkerNumber'), 1, 9999)
          ];
          rules['gpuPerWorker'] = [
            ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.PSWorker.WorkerNumber')),
            ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.PSWorker.WorkerNumber')),
            ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.PSWorker.WorkerNumber'), 1, this.gpuPerNode)
          ];
        }
        this.innerRules = rules;
      },
      doSetting(setting, nodes, gpuPerNode) {
        return new Promise((resolve, reject) => {
          this.nodes = nodes;
          this.gpuPerNode = gpuPerNode;
          this.innerForm = {
            mode: setting.mode,
            psNumber: String(setting.psNumber),
            workerNumber: String(setting.workerNumber),
            gpuPerWorker: String(setting.gpuPerWorker)
          };
          this.$refs.innerDialog.emptyPopup().then((res) => {
            var newSetting = {
              mode: this.innerForm.mode,
              psNumber: parseInt(this.innerForm.psNumber),
              workerNumber: parseInt(this.innerForm.workerNumber),
              gpuPerWorker: parseInt(this.innerForm.gpuPerWorker)
            };
            resolve(newSetting);
          }, (res) => {
            reject(res);
          });
        });
      }
    }
  }
</script>
