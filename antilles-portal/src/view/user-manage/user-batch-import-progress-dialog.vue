<style>
.progress .el-progress-bar__outer,.progress .el-progress-bar__inner{
  border-radius: 0px;
}
.progress-title{
  line-height: 40px;
}
.progress-percentage{
  text-align: right;
  line-height: 40px;
}
</style>

<template>
  <el-dialog
    :title="title"
    :visible.sync="dialogVisible"
    width="30%">
    <div class="progress">
      <p class="progress-title">{{$t('User.Import.Title.Importing')}}</p>
      <el-progress :show-text="false" :stroke-width="24" :percentage="percent"></el-progress>
      <p class="progress-percentage">{{finished}}/{{total}}</p>
    </div>
    <div slot="footer" class="dialog-footer">
      <el-button @click="dialogVisible = false">{{$t('User.Action.Close')}}</el-button>
      <el-button type="primary" @click="onCancelClick">{{$t('User.Action.Cancel')}}</el-button>
    </div>
  </el-dialog>
</template>

<script>
  import UserBatchImportService from '../../service/user-batch-import'

  export default {
    data() {
      return {
        title: this.$t('User.Batch.Import.Title'),
        dialogVisible: false,
        detailDialog: '',
        userTable: '',
        percent: 0,
        finished: 0,
        total: 0,
        timer: null
      };
    },
    watch:{
      dialogVisible:function() {
        if(this.dialogVisible){
          this.percent = 0;
          this.finished = '-';
          this.total = '-';
          const that = this;
          this.timer = setTimeout(function getImportstatu(){
            UserBatchImportService.getUsersImportStatu().then((res) => {
              if(res.status == 'importing' && res.progress){
                that.finished = res.progress.finished;
                that.percent = res.progress.finished/res.progress.total*100;
                that.total = res.progress.total;
              }else{
                clearTimeout(that.timer);
                that.detailDialog.show();
                that.dialogVisible = false;
                that.userTable.fetchTableData(true);
              }
            },(err) => {

            })
            that.timer = setTimeout(getImportstatu,500);
          },500);
        }else{
          clearTimeout(this.timer);
        }
      }
    },
    methods: {
      show(el,userTable) {
        this.dialogVisible = true;
        this.detailDialog = el;
        this.userTable = userTable;
      },
      onCancelClick() {
        this.dialogVisible = false;
        this.$confirm(this.$t('User.Import.Cancel.Tips'), this.$t('User.Import.Cancel.Title'), {
          confirmButtonText: this.$t('User.Import.Cancel.Action.Confirm'),
          cancelButtonText: this.$t('User.Import.Cancel.Action.Cancel'),
          type: 'warning'
        }).then(() => {
          this.dialogVisible = true;
          UserBatchImportService.cancelUsersImport().then((res)=>{
            clearTimeout(this.timer);
            this.detailDialog.show();
            this.dialogVisible = false;
            this.$message({
              type: 'success',
              message: this.$t('User.Import.Cancel.Success')
            });
          },(err)=>{
            this.$message({
              type: 'error',
              message: this.$t('Error.2212')
            });
          })
        }).catch(() => {
          this.dialogVisible = true;
        });
      }
    }
  };
</script>