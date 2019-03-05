<style>
.learning-rate-editor .el-input {
  width: 300px;
}
</style>
<template>
  <div class="learning-rate-editor">
    <el-input v-model="beginValue"></el-input>
    <el-button @click="onSettingClick">{{settingButtonText}}</el-button>
    <learning-rate-dialog ref="decaySettingDialog"></learning-rate-dialog>
  </div>
</template>
<script>
  import LearningRateDialog from './learning-rate-dialog'
  import ValidRoleFactory from '../../common/valid-role-factory'

  export default {
    components:{
      'learning-rate-dialog': LearningRateDialog
    },
    data() {
      return {
        beginValue: String(this.value.beginValue),
        decay: {
          decayType: this.value.decayType,
          endValue: this.value.endValue,
          decayFactor: this.value.decayFactor,
          epochsPerDecay: this.value.epochsPerDecay,
          movingAverageDecay: this.value.movingAverageDecay
        }
      }
    },
    props: [ 'value' ],
    watch: {
      beginValue: function(val, oldVal) {
        this.onValueChanged();
      },
      decay: function(val, oldVal) {
        this.onValueChanged();
      }
    },
    computed: {
      settingButtonText() {
        if(this.decay.decayType == 'fixed') {
          return this.$t('JobTemplate.LearningRate.DecayType.Fixed');
        } else if(this.decay.decayType == 'exponential') {
          return this.$t('JobTemplate.LearningRate.DecayType.Exponential');
        } else if(this.decay.decayType == 'polynomial') {
          return this.$t('JobTemplate.LearningRate.DecayType.Polynomial');
        } else {
          return '';
        }
      }
    },
    methods: {
      onSettingClick() {
        this.$refs.decaySettingDialog.doSettingDecay(this.decay).then((res) => {
          this.decay = res;
        }, (res) => {
          // Do nothing
        });
      },
      onValueChanged() {
        var learningRate = {
          beginValue: Number(this.beginValue),
          decayType: this.decay.decayType,
          endValue: this.decay.endValue,
          decayFactor: this.decay.decayFactor,
          epochsPerDecay: this.decay.epochsPerDecay,
          movingAverageDecay: this.decay.movingAverageDecay
        };
        this.$emit('input', learningRate);
      }
    },
    getValidRules(paramName) {
      return {
        type: "object",
        required: true,
        fields: {
          beginValue: [
            ValidRoleFactory.getRequireRoleForNumber(paramName)
          ]
        }
      };
    }
  }
</script>
