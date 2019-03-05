<style scoped>
</style>
<template>
  <state-label
    :state="levelMapping[level].state"
    :loading="levelMapping[level].loading"
    v-if="level != null">{{levelMapping[level].display}}</state-label>
</template>
<script>
import StateLabel from '../component/state-label'

export default {
  data () {
    return {
      levelMapping: {
        'fatal': {
          state: 'fatal',
          loading: false,
          display: this.$t('Alarm.PolicyLevel.fatal')
        },
        'error': {
          state: 'error',
          loading: false,
          display: this.$t('Alarm.PolicyLevel.error')
        },
        'warn': {
          state: 'warning',
          loading: false,
          display: this.$t('Alarm.PolicyLevel.warn')
        },
        'info': {
          state: 'normal',
          loading: false,
          display: this.$t('Alarm.PolicyLevel.info')
        }
      }
    }
  },
  props: [
    'level'
  ],
  components: {
    'state-label': StateLabel
  }
}
</script>
