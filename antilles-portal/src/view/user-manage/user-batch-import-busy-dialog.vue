<style>
.dialog-footer{
  position: relative;
}
.view-last-result{
  position: absolute;
  left:0;
}
</style>

<template>
  <el-dialog
    :title="title"
    :visible.sync="dialogVisible"
    width="30%">
    <div>
      <p>{{$t('User.Import.Occupied.Tips1')}}</p>
      <p>{{$t('User.Import.Occupied.Tips2')}}</p>
    </div>
    <div slot="footer" class="dialog-footer">
      <el-button v-if="showLast" type="primary" class="view-last-result" @click="viewLastResult">{{$t('User.Action.ViewLastResult')}}</el-button>
      <el-button @click="dialogVisible = false">{{$t('User.Action.Close')}}</el-button>
    </div>
  </el-dialog>
</template>

<script>

  export default {
    data() {
      return {
        title: this.$t('User.Batch.Import.Title'),
        dialogVisible: false,
        detailDialog: '',
        showLast: false
      };
    },
    methods: {
      show(el,showLast) {
        this.showLast = showLast;
        this.dialogVisible = true;
        this.detailDialog = el;
      },
      viewLastResult() {
        this.detailDialog.show();
        this.dialogVisible = false;
      }
    }
  };
</script>