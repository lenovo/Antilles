<style scoped>
</style>
<template>
<degree-label
  :max="statusSortList.length-1"
  :current="statusSortList.indexOf(status)">{{statusDisplay}}</degree-label>
</template>
<script>
import DegreeLabel from '../component/degree-label'

export default {
  data() {
    return {
      statusSortList: ['off', 'idle', 'busy']
      // statusSortList: ['off', 'idle', 'used', 'busy']
    }
  },
  computed: {
    statusDisplay() {
      if (this.status == 'off') {
        return this.$t('NodeStatus.Off');
      }
      if (this.status == 'idle') {
        return this.$t('NodeStatus.Idle');
      }
      // if (this.status == 'used') {
      //   return this.$t('NodeStatus.Used');
      // }
      if (this.status == 'busy') {
        return this.$t('NodeStatus.Busy');
      }
    }
  },
  props: [
    "status"
  ],
  components: {
    'degree-label': DegreeLabel
  }
}
</script>
