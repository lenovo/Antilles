<style scoped>
</style>
<template>
<state-label
  :state="statusMapping[powerStatus].state"
  :loading="statusMapping[powerStatus].loading">{{statusMapping[powerStatus].display}}
</state-label>
</template>
<script>
import StateLabel from '../component/state-label'

export default {
  data() {
    return {
      statusMapping: {
        'off': {
          state: 'fatal',
          loading: false,
          display: this.$t('Node.PowerStatus.Off')
        },
        'on': {
          state: 'success',
          loading: false,
          display: this.$t('Node.PowerStatus.On')
        },
        'Off': {
          state: 'fatal',
          loading: false,
          display: this.$t('Node.PowerStatus.Off')
        },
        'On': {
          state: 'success',
          loading: false,
          display: this.$t('Node.PowerStatus.On')
        }
      }
    }
  },
  props: [
    'powerStatus'
  ],
  components: {
    'state-label': StateLabel
  }
}
</script>
