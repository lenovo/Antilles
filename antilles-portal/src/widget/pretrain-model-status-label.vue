<style scoped>
</style>
<template>
<state-label
  :state="currentState.state"
  :loading="currentState.loading">{{currentState.display}}</state-label>
</template>
<script>
import StateLabel from '../component/state-label'
export default {
  data() {
    return {
      currentState: {
        state: 'success',
        loading: false,
        display: ''
      },
      statusMapping: {
        'completed': {
          state: 'success',
          loading: false,
          display: this.$t('Job.Status.Completed')
        },
        'error': {
          state: 'fatal',
          loading: false,
          display: this.$t('Job.Status.Error')
        },
        'uploading': {
          state: 'normal',
          loading: true,
          display: this.$t('Job.Status.Uploading')
        },
      }
    }
  },
  props: [
    'status'
  ],
  components: {
    'state-label': StateLabel
  },
  mounted() {
    this.currentState = this.getCurrentState();
  },
  watch: {
    status(val) {
      this.currentState = this.getCurrentState();
    }
  },
  methods: {
    getCurrentState() {
      return this.statusMapping[this.status];
    }
  }
}
</script>
