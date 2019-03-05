<style lang="css">
</style>
<template lang="html">
  <div class="">
    <el-form-item :label="$t('JobTemplate.Parameters.Max.Length')" prop="maxLength">
      <el-input id="tid_jobTemplate-parameter-maxLength" v-model="formParameter.maxLength"></el-input>
    </el-form-item>
    <el-form-item :label="$t('JobTemplate.Parameters.Invalid')" prop="Invalid">
      <el-select id="tid_jobTemplate-parameter-invalid" v-model="formParameter.invalid">
        <el-option
          v-for="item in invalidOption"
          :key="item.value"
          :label="item.label"
          :value="item.value">
        </el-option>
      </el-select>
    </el-form-item>
  </div>
</template>

<script>
export default {
  data() {
    return {
      invalid: ['none', 'default', 'phone', 'email'],
      invalidOption: []
    };
  },
  props: [
    'formParameter',
    'formRules'
  ],
  mounted() {
    this.invalidOption = this.processSelectOption(this.invalid);
  },
  methods: {
    processSelectOption(arr) {
      var array = [];
      arr.forEach((item) => {
        array.push({ label: this.$t(`JobTemplate.Parameters.Invalid.${item}`), value: item })
      });
      return array;
    },
  }
}
</script>
