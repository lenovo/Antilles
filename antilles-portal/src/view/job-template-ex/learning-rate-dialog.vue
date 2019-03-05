<template>
  <composite-form-dialog
    class="learning-rate-dialog"
    ref="innerDialog"
    :title="$t('JobTemplate.LearningRate.Dialog.Title')"
    size="580px"
    :form-model="innerForm"
    :form-rules="innerRules">
    <!--Decay Type-->
    <el-form-item prop="decayType"
      label-width="180px" :label="$t('JobTemplate.LearningRate.DecayType')">
      <el-select v-model="innerForm.decayType">
        <el-option
          v-for="option in decayTypeOptions"
          :key="option.value"
          :label="option.label"
          :value="option.value">
        </el-option>
      </el-select>
    </el-form-item>
    <!--End Learning Rate-->
    <el-form-item prop="endValue" v-if="innerForm.decayType!='fixed'"
      label-width="180px" :label="$t('JobTemplate.LearningRate.EndValue')">
      <el-input v-model="innerForm.endValue"></el-input>
    </el-form-item>
    <!--Decay Factor-->
    <el-form-item prop="decayFactor" v-if="innerForm.decayType!='fixed'"
      label-width="180px" :label="$t('JobTemplate.LearningRate.DecayFactor')" >
      <el-input v-model="innerForm.decayFactor"></el-input>
    </el-form-item>
    <!--Epoches Per Decay-->
    <el-form-item prop="epochsPerDecay" v-if="innerForm.decayType!='fixed'"
      label-width="180px" :label="$t('JobTemplate.LearningRate.EpochsPerDecay')">
      <el-input v-model="innerForm.epochsPerDecay"></el-input>
    </el-form-item>
    <!--Moving Average Decay-->
    <el-form-item prop="movingAverageDecay" v-if="innerForm.decayType!='fixed'"
      label-width="180px" :label="$t('JobTemplate.LearningRate.MovingAverageDecay')">
      <el-input v-model="innerForm.movingAverageDecay"></el-input>
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
      return {
        decayTypeOptions: [
          {
            'value': 'fixed',
            'label': this.$t('JobTemplate.LearningRate.DecayType.Fixed')
          },
          {
            'value': 'exponential',
            'label': this.$t('JobTemplate.LearningRate.DecayType.Exponential')
          },
          {
            'value': 'polynomial',
            'label': this.$t('JobTemplate.LearningRate.DecayType.Polynomial')
          }
        ],
        innerForm: {
          decayType: 'fixed',
          endValue: '',
          decayFactor: '',
          epochsPerDecay: '',
          movingAverageDecay: ''
        },
        innerRules: {
        }
      }
    },
    watch: {
      'innerForm.decayType': function(val, oldVal) {
        this.initRules(val);
      }
    },
    methods: {
      initRules(decayType) {
        if(decayType == 'fixed') {
          this.innerRules = {};
        } else {
          this.innerRules = {
            endValue: [
              ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.LearningRate.EndValue')),
              ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.LearningRate.EndValue'))
            ],
            decayFactor: [
              ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.LearningRate.DecayFactor')),
              ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.LearningRate.DecayFactor'))
            ],
            epochsPerDecay: [
              ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.LearningRate.EpochsPerDecay')),
              ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.LearningRate.EpochsPerDecay'))
            ],
            movingAverageDecay: [
              ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.LearningRate.MovingAverageDecay'))
            ]
          };
        }
      },
      doSettingDecay(decay) {
        return new Promise((resolve, reject) => {
          this.innerForm = {
            decayType: decay.decayType,
            endValue: String(decay.endValue),
            decayFactor: String(decay.decayFactor),
            epochsPerDecay: String(decay.epochsPerDecay),
            movingAverageDecay: String(decay.movingAverageDecay)
          };
          this.$refs.innerDialog.emptyPopup().then((res) => {
            var movingAverageDecay = '';
            if(!isNaN(parseFloat(this.innerForm.movingAverageDecay))) {
              movingAverageDecay = parseFloat(this.innerForm.movingAverageDecay);
            }
            var decay = {
              decayType: this.innerForm.decayType,
              endValue: parseFloat(this.innerForm.endValue),
              decayFactor: parseFloat(this.innerForm.decayFactor),
              epochsPerDecay: parseInt(this.innerForm.epochsPerDecay),
              movingAverageDecay: movingAverageDecay
            };
            resolve(decay);
          }, (res) => {
            reject(res);
          });
        });
      }
    }
  }
</script>
