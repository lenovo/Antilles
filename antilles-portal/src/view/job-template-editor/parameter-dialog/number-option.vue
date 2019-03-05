<style lang="css">
</style>
<template lang="html">
  <div class="">
    <el-form-item :label="$t('JobTemplate.Parameters.Min.Value')" prop="minValue">
      <el-input id="tid_jobTemplate-parameter-minValue" v-model="formParameter.minValue" @change='minValueFunction'></el-input>
    </el-form-item>
    <el-form-item :label="$t('JobTemplate.Parameters.Max.Value')" prop="maxValue">
      <el-input id="tid_jobTemplate-parameter-maxValue" v-model="formParameter.maxValue" @change='maxValueFunction'></el-input>
    </el-form-item>
    <el-form-item :label="$t('JobTemplate.Parameters.Float.Length')" prop="floatLength">
      <el-input id="tid_jobTemplate-parameter-floatLength" v-model="formParameter.floatLength"></el-input>
    </el-form-item>
  </div>
</template>

<script>
export default {
  props: [
    'formParameter',
    'formRules',
    'maxValueFunction',
    'minValueFunction'
  ]
}
</script>
