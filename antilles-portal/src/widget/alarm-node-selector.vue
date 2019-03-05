<style>
</style>
<template>
<el-select v-model="innerValue" multiple :placeholder="innerPlaceholder">
  <el-option
    v-for="item in options"
    :key="item.value"
    :label="item.label"
    :value="item.value">
  </el-option>
</el-select>
</template>
<script>
import NodeService from '../service/node'

export default {
  data() {
    return {
      options: [],
      innerValue: [],
      innerPlaceholder: this.placeholder ? this.placeholder : this.$t('MultiNodeSelector.Placeholder')
    };
  },
  props: [
    'value',
    'placeholder'
  ],
  mounted() {
    this.initOptions();
  },
  watch: {
    innerValue: {
      handler: function(val, oldVal) {
        if(this.compareValues(this.value, val)) {
          return;
        }
        this.value.splice(0, this.value.length);
        this.innerValue.forEach((one) => {
          this.value.push(one);
        });
        this.$emit('change', this.innerValue);
      },
      deep: false
    }

  },
  methods: {
    initOptions() {
      this.options = [];
      NodeService.getAllNodes().then((res) => {
        //console.log("RES",res)
        res.forEach((node) => {
          this.options.push({
            value: node.hostname,
            label: node.hostname
          });
        });
        this.value.forEach((one) => {
          this.innerValue.push(one);
        });
        
      }, (res) => {
        this.$message.error(res);
      });
    },
    compareValues(arr1, arr2) {
      if(arr1.length != arr2.length) {
        return false;
      }
      for(var i=0; i<arr1.length; i++) {
        if(arr1[0] != arr2[0]) {
          return false;
        }
      }
      return true;
    },
    doClear() {
      this.innerValue = [];
    }
  }
}
</script>
