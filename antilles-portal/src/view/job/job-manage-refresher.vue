<style>
</style>
<template>
</template>
<script>
import JobService from '../../service/job'

export default {
  data() {
    return {
      jobRowRefresh: 'job-row'
    }
  },
  props: [
    'job-row',
    'interval'
  ],
  mounted() {

  },
  watch: {
    jobRowRefresh(val, oldVal) {
      this.refresh();
    }
  },
  methods: {
    refresh() {
      JobService.getJobById(this.jobRowRefresh.id).then((res) => {
        if(this.jobRowRefresh.id == res.id) {
          this.jobRowRefresh.schedulerId = res.schedulerId;
          this.jobRowRefresh.userId = res.userId;
          this.jobRowRefresh.name = res.name;
          this.jobRowRefresh.queue = res.queue;
          this.jobRowRefresh.submitTime = res.submitTime;
          this.jobRowRefresh.beginTime = res.beginTime;
          this.jobRowRefresh.finishTime = res.finishTime;
          this.jobRowRefresh.status = res.status;

          /*
          if(this.billGroup.accountStatus == 'operating') {
            let self = this;
            setTimeout(() => {
              self.refresh();
            }, this.interval);
          }
          */
        }
      }, (res) => {
          this.$message.error(res);
      });
    }
  }
}
</script>