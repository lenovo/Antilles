<template>
  <div>
    <el-input style="width:300px;" v-model="psWorkerDisplay" :disabled="true"></el-input>
    <el-button @click="onSettingClick">{{modeText}}</el-button>
    <ps-worker-dialog ref="settingDialog"></ps-worker-dialog>
  </div>
</template>
<script>
  import PsWorkerDialog from './ps-worker-dialog'

  export default {
    data(){
      return {
        psWorkerDisplay: '',
        setting: {
          mode: this.value.mode,
          psNumber: this.value.psNumber,
          workerNumber: this.value.workerNumber,
          gpuPerWorker: this.value.gpuPerWorker
        }
      }
    },
    props:[ 'value', 'nodes', 'gpuPerNode', 'workerAutoPolicy' ],
    components: {
      'ps-worker-dialog': PsWorkerDialog
    },
    computed: {
      modeText() {
        if(this.setting.mode == 'auto') {
          return this.$t('JobTemplate.PSWorker.Mode.Auto');
        }
        if(this.setting.mode == 'manual') {
          return this.$t('JobTemplate.PSWorker.Mode.Manual');
        }
        return '';
      }
    },
    watch: {
      'nodes': function(val, oldVal) {
        this.resetPSWorker();
      },
      'gpuPerNode': function(val, oldVal) {
        this.resetPSWorker();
      }
    },
    mounted() {
      this.onValueChange();
    },
    methods: {
      resetPSWorker() {
        this.setting.mode = 'auto';
        this.setting.psNumber = this.nodes;
        if(this.gpuPerNode > 0) {
          if(this.workerAutoPolicy == 'one_node_one_worker') {
            this.setting.workerNumber = this.nodes;
            this.setting.gpuPerWorker = this.gpuPerNode;
          }
          if(this.workerAutoPolicy == 'one_gpu_one_worker') {
            this.setting.workerNumber = this.nodes * this.gpuPerNode;
            this.setting.gpuPerWorker = 1;
          }
        } else {
          this.setting.workerNumber = this.nodes;
          this.setting.gpuPerWorker = 0;
        }
        this.onValueChange();
      },
      onSettingClick() {
        this.$refs.settingDialog.doSetting(this.setting, this.nodes, this.gpuPerNode).then((res) => {
          this.setting = res;
          if(this.setting.mode == 'auto') {
            this.resetPSWorker();
          }
          this.onValueChange();
        }, (res) => {
          // Do nothing
        });
      },
      onValueChange() {
        var psWorker = {
          mode: this.setting.mode,
          psNumber: this.setting.psNumber,
          workerNumber: this.setting.workerNumber,
          gpuPerWorker: this.setting.gpuPerWorker
        };
        this.psWorkerDisplay = psWorker.psNumber + " PS, " + psWorker.workerNumber + " Worker";
        this.$emit('input', psWorker);
      }
    }
  }
</script>
