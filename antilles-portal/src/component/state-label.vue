<style>
.state-label {
  border-radius: 4px;
  color: #fff;
  display: inline-block;
  width:16px;
  height:16px;
  vertical-align: middle;
  text-align: center;
  font-size: 12px;
  line-height: 15px;
}
.state-label-bg-normal {
  background-color: #0096E7 ;
}
.state-label-bg-success {
  background-color: #6BCB01;
}
.state-label-bg-warning {
  background-color: #FFC107;
}
.state-label-bg-error {
  background-color: #FF6A00;
}
.state-label-bg-fatal {
  background-color: #E51c23;
}
</style>
<template>
<span>
  <span class="state-label" :class="'state-label-bg-' + state">
  <i class="el-icon-loading" v-if="loading"></i>
  </span>
  <slot></slot>
</span>
</template>
<script>
export default {
  props: {
    state: {
      type: String,
      required: true,
      validator: function(value) {
        return ['normal', 'success', 'warning', 'error', 'fatal'].indexOf(value) >= 0;
      }
    },
    loading: {
      type: Boolean,
      default: false
    }
  }
}
</script>
