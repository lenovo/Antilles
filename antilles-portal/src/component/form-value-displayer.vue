<style>
.form-value {
  width: 100%;
  display: inline-block;
  font-weight: bold;
}
</style>
<template>
  <div class="form-value">{{value}}</div>
</template>
<script>
export default {
  props: [
    'value'
  ]
}
</script>
