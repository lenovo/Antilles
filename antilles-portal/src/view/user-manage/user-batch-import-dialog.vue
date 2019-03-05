<style>
.dialog-footer{
  position: relative;
}
.view-last-result{
  position: absolute;
  left:0;
}
.file-select-body{
  height: 40px;
  line-height: 40px;
  position: relative;
}
.file-select-input{
  position: absolute;
  right: 90px;
  width: 365px;
}
.file-select-label{
  line-height: 40px;
}
.sample-file{
  margin-left: 100px;
  line-height: 40px;
  text-decoration: underline;
  color: #38AAF2;
}
.file-select-body .el-upload--text{
  position: absolute;
  right: 0;
  top:0;
}
.file-select-body .el-upload-list--text{
  width: 350px;
  position: absolute;
  top: -2px;
  right: 97px;
}
.file-select-body .el-upload-list__item:hover {
  background-color: #fff;
}
</style>

<template>
  <el-dialog
    :title="title"
    :visible.sync="dialogVisible"
    width="580px">
    <div class="file-select-body">
      <span class="">{{$t('User.Import.Title.ImportFile')}}</span>
      <el-input class="file-select-input" size="small" readonly></el-input>
      <el-upload
        ref="upload"
        :limit="1"
        name="upload"
        :headers="{authorization: 'Jwt ' + token}"
        accept=".csv"
        action="/api/users/import"
        :on-change="handleChange"
        :show-file-list="true"
        :on-success="handleSuccess"
        :on-error="handleError"
        :auto-upload="false">
        <el-button size="small" type="primary" @click="chooseFile">{{$t('User.Action.Browse')}}</el-button>
      </el-upload>
    </div>
    <a href="/static/samplefile.csv" class="sample-file" download="">{{$t('User.Import.Title.SampleFile')}}</a>
    <div slot="footer" class="dialog-footer">
      <el-button type="primary" class="view-last-result" v-if="showLast" @click="viewLastResult">{{$t('User.Action.ViewLastResult')}}</el-button>
      <el-button @click="dialogVisible = false">{{$t('User.Action.Close')}}</el-button>
      <el-button :loading="loading" type="primary" @click="onImportClick">{{$t('User.Action.Import')}}</el-button>
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
        userTable: '',
        progressDialog: '',
        token: window.gApp.$store.state.auth.token,
        showLast: false,
        loading: false
      };
    },
    methods: {
      show(detailDialog,progressDialog,userTable,showLast) {
        this.showLast = showLast;
        this.dialogVisible = true;
        this.detailDialog = detailDialog;
        this.progressDialog = progressDialog;
        this.userTable = userTable;
      },
      onImportClick() {
        if(this.$refs.upload.uploadFiles.length == 0){
          this.$message.warning(this.$t('User.Import.FileSelect.Tips'));
          return false;
        }
        this.loading = true;
        this.$refs.upload.submit();
      },
      handleChange(file,fileList) {

      },
      handleSuccess(response,file,FileList) {
        this.progressDialog.show(this.detailDialog,this.userTable);
        this.dialogVisible = false;
        this.$refs.upload.clearFiles();
        this.loading = false;
      },
      handleError(err,file,FileList) {
        this.$refs.upload.clearFiles();
        this.loading = false;
        this.$message.error(this.$t('Error.' + JSON.parse(err.message).errid))
      },
      chooseFile() {
        this.$refs.upload.clearFiles();
      },
      viewLastResult() {
        this.detailDialog.show();
        this.dialogVisible = false;
      }
    }
  };
</script>