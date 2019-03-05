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
        'queueing': {
          state: 'normal',
          loading: true,
          display: this.$t('Job.Status.Queueing')
        },
        'creating': {
          state: 'normal',
          loading: true,
          display: this.$t('Job.Status.Creating')
        },
        'running': {
          state: 'normal',
          loading: true,
          display: this.$t('Job.Status.Running')
        },
        'suspending': {
          state: 'normal',
          loading: true,
          display: this.$t('Job.Status.Suspending')
        },
        'waiting': {
          state: 'normal',
          loading: true,
          display: this.$t('Job.Status.Waiting')
        },
        'holding': {
          state: 'normal',
          loading: true,
          display: this.$t('Job.Status.Holding')
        },
        'error': {
          state: 'fatal',
          loading: false,
          display: this.$t('Job.Status.Error')
        },
        'cancelled': {
          state: 'warning',
          loading: false,
          display: this.$t('Job.Status.Cancelled')
        },
        'createfailed': {
          state: 'fatal',
          loading: false,
          display: this.$t('Job.Status.CreateFailed')
        }
      }
    }
  },
  props: [
    'status',
    'operateStatus'
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
    },
    operateStatus(val) {
      this.currentState = this.getCurrentState();
    }
  },
  methods: {
    getCurrentState() {
      if(this.operateStatus == 'cancelling' || (this.operateStatus == 'cancelled' && this.status == 'running')) {
        return {
          state: 'warning',
          loading: true,
          display: this.$t('Job.Status.Cancelling')
        };
      } else {
        return this.statusMapping[this.status];
      }
    }
  }
}
</script>
