
<style lang="css">

</style>

<template lang="html">
  <el-select id="tid_node-select"
    v-model="nodeSelectedvalue"
    filterable
    multiple
    default-first-option
    :placeholder="innerPlaceholder">
    <el-option
      v-for="item in nodeSelectOptions"
      :key="item.value"
      :label="item.label"
      :value="item.value">
    </el-option>
  </el-select>
</template>

<script>

import NodesService from './../service/node'

export default {
  data() {
    return {
      nodeSelectOptions: [],
      nodeSelectedvalue: this.selectedNodes || [],
      innerPlaceholder: this.placeholder ? this.placeholder : this.$t('MultiNodeSelector.Placeholder')
    }
  },
  props: [
    'selectedNodes',
    'bindProperty',
    'placeholder'
  ],
  mounted () {
    this.$watch('nodeSelectedvalue',(newval, oldVal) => {
      if(this.nodeSelectedvalue.length > 10){
        this.nodeSelectedvalue.splice(this.nodeSelectedvalue.length-1, 1);
      }
      this.$emit('nodes-selected-change',this.nodeSelectedvalue);
    })
    this.$watch('selectedNodes',(newval, oldVal) => {
      this.nodeSelectedvalue = newval;
    })
    NodesService.getAllNodes().then((res) => {
      res.forEach((item) => {
        this.nodeSelectOptions.push({
          value: this.bindProperty ? item[this.bindProperty] : item.id,
          label: item.hostname
        });
      })
    },(res) => {
      this.$message(res)
    })
  },
  methods: {

  }
}
</script>
