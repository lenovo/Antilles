<style>
</style>
<template>
<el-select v-model="innerValue" :clearable='true' :placeholder="innerPlaceholder">
  <el-option
    v-for="item in options"
    :key="item.value"
    :label="item.label"
    :value="item.value">
  </el-option>
</el-select>
</template>
<script>
import QueueService from '../service/queue'

export default {
  data() {
    return {
      options: [],
      innerValue: '',
      innerPlaceholder: this.placeholder ? this.placeholder : this.$t('MultiQueueSelector.Placeholder')
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
        // if(this.compareValues(this.value, val)) {
        //   return;
        // }
        // this.value.splice(0, this.value.length);
        // this.innerValue.forEach((one) => {
        //   this.value.push(one);
        // });
        if(val) {
          this.$emit('input', [this.innerValue]);
        } else {
          this.$emit('input', []);
        }
      },
      deep: false
    }
  },
  methods: {
    initOptions() {
      this.options = [];
      QueueService.getAllQueues().then((res) => {
        res.forEach((queue) => {
          this.options.push({
            value: queue.name,
            label: queue.name
          });
        });
        // this.value.forEach((one) => {
        //   this.innerValue.push(one);
        // });
        if(this.value.length>0) {
          this.innerValue = this.value[0];
        }

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
    }
  }
}
</script>
