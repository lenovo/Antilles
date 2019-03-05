<style lang="css">
</style>
<template lang="html">
  <div>
    <el-select v-model="type" @change="onTypeChange">
      <el-option
        v-for="optimizer in optimizers"
        :key="optimizer.key"
        :label="$t(optimizer.label)"
        :value="optimizer.key">
      </el-option>
    </el-select>
    <el-button @click='onSettingClick'>{{$t('JobTemplate.Optimizer.Setting')}}</el-button>
    <optimizer-dialog ref="settingDialog"></optimizer-dialog>
  </div>
</template>
<script>
import OptimizerDialog from './optimizer-dialog'
import OptimizerDefine from './optimizer-define'

export default {
  data() {
    return {
      type: this.value.type,
      setting: {
        adadelta: {
          decayRate: this.value.adadelta.decayRate
        },
        adagrad: {
          initAccumulator: this.value.adagrad.initAccumulator
        },
        adam: {
          beta1: this.value.adam.beta1,
          beta2: this.value.adam.beta2,
          epsilon: this.value.adam.epsilon
        },
        ftrl: {
          learningRatePower: this.value.ftrl.learningRatePower,
          initAccumulator: this.value.ftrl.initAccumulator,
          l1: this.value.ftrl.l1,
          l2: this.value.ftrl.l2
        },
        momentum: {
          momentum: this.value.momentum.momentum
        },
        sgd: {
          gradientNorm: this.value.sgd.gradientNorm,
          maxGradientNorm: this.value.sgd.maxGradientNorm,
          gradientNormGlobalFirst: this.value.sgd.gradientNormGlobalFirst
        },
        rmsprop: {
          momentum: this.value.rmsprop.momentum,
          decayRate: this.value.rmsprop.decayRate
        }
      },
      optimizers: OptimizerDefine.optimizers
    }
  },
  components: {
    'optimizer-dialog': OptimizerDialog
  },
  props: [ 'value' ],
  methods: {
    onSettingClick() {
      this.$refs.settingDialog.doSetting(this.type, this.setting).then((res) => {
        this.setting = res;
        this.onValueChange();
      }, (res) => {
        // Do nothing
      });
    },
    onTypeChange() {
      this.onValueChange();
    },
    onValueChange() {
      var optimizer = {
        type: this.type,
        adadelta: {
          decayRate: this.setting.adadelta.decayRate
        },
        adagrad: {
          initAccumulator: this.setting.adagrad.initAccumulator
        },
        adam: {
          beta1: this.setting.adam.beta1,
          beta2: this.setting.adam.beta2,
          epsilon: this.setting.adam.epsilon
        },
        ftrl: {
          learningRatePower: this.setting.ftrl.learningRatePower,
          initAccumulator: this.setting.ftrl.initAccumulator,
          l1: this.setting.ftrl.l1,
          l2: this.setting.ftrl.l2
        },
        momentum: {
          momentum: this.setting.momentum.momentum
        },
        sgd: {
          gradientNorm: this.setting.sgd.gradientNorm,
          maxGradientNorm: this.setting.sgd.maxGradientNorm,
          gradientNormGlobalFirst: this.setting.sgd.gradientNormGlobalFirst
        },
        rmsprop: {
          momentum: this.setting.rmsprop.momentum,
          decayRate: this.setting.rmsprop.decayRate
        }
      };
      this.$emit('input', optimizer);
    }
  }
}
</script>
