<style>
</style>
<template>
</template>
<script>
import BillGroupService from '../../service/bill-group'
export default {
  props: [
    'billGroup',
    'interval'
  ],
  mounted() {
    if(this.billGroup.accountStatus == 'operating') {
      this.refresh();
    }
  },
  watch: {
    billGroup(val, oldVal) {
      if(val.accountStatus == 'operating') {
        this.refresh();
      }
    }
  },
  methods: {
    refresh() {
      BillGroupService.getBillGroupById(this.billGroup.id).then((res) => {
        if(this.billGroup.id == res.id) {
          this.billGroup.totalComputingTime = res.totalComputingTime;
          this.billGroup.accountConsumed = res.accountConsumed;
          this.billGroup.accountBalance = res.accountBalance;
          this.billGroup.accountStatus = res.accountStatus;
          if(this.billGroup.accountStatus == 'operating') {
            let self = this;
            setTimeout(() => {
              self.refresh();
            }, this.interval);
          }
        }
      }, (res) => {
          this.$message.error(res);
      });
    }
  }
}
</script>
