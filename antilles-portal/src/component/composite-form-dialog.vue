<style>
.composite-form-dialog .el-form-item__content {
  width: 300px;
}

.composite-form-dialog .el-form-item .el-select {
  width: 100%;
}

.composite-form-dialog .el-dialog__body {
  padding-right: 40px;
}
</style>
<template>
  <el-dialog id="tid_popup-dialog" ref="popupDialog"
    :title="title"
    :width="size"
    :visible.sync="dialogVisible"
    :close-on-press-escape="!submitting"
    :close-on-click-modal="!submitting"
    :show-close="!submitting"
    class="composite-form-dialog"
    @close="onDialogClose"
    :append-to-body="!notChangeParent">
    <el-form id="tid_popup-dialog-form" :model="formModel" :rules="formRules" ref="innerForm" v-show="!submitting" :label-width="labelWidth">
      <slot></slot>
    </el-form>
    <div slot="footer" class="dialog-footer">
      <el-button id="tid_popup-dialog-cancel" @click="onCancelClick" v-show="!submitting">{{ cancelButtonText }}</el-button>
      <el-button id="tid_popup-dialog-submit" type="primary" @click="onSubmitClick" :loading="submitting">{{ submitButtonText }}</el-button>
    </div>
  </el-dialog>
</template>
<script>
import Utils from '../common/utils'

export default {
  data() {
    var buttonsText = this.getButtonsText(this.type);
    return {
      labelWidth: this.formLabelWidth?this.formLabelWidth:'120px',
      submitting: false,
      dialogVisible: false,
      innerResolve: null,
      innerReject: null,
      autoReject: true,
      cancelButtonText: buttonsText[1],
      submitButtonText: buttonsText[0]
    };
  },
  props: [
    'title',
    'size',
    'formModel',
    'formRules',
    'formLabelWidth',
    'successMessageFormatter',
    'errorMessageFormatter',
    'notChangeParent',
    'externalValidate',
    'type'
  ],
  watch: {
    formLabelWidth(val, oldVal) {
      this.labelWidth = val?val:'120px';
    }
  },
  methods: {
    getButtonsText(type) {
      if(type) {
        if(type == 'confirm') {
          return [this.$t('Dialog.Yes'), this.$t('Dialog.No')];
        }
        if(type == 'submit') {
          return [this.$t('Dialog.Submit'), this.$t('Dialog.Cancel')];
        }
      }
      return [this.$t('Dialog.Ok'), this.$t('Dialog.Cancel')]
    },
    onCancelClick() {
      this.dialogVisible = false;
    },
    onDialogClose() {
      if(this.autoReject) {
        this.innerReject();
      }
    },
    onSubmitClick() {
      if(this.externalValidate) {
        this.externalValidate((extValid) => {
          this.$refs.innerForm.validate((valid) => {
            if(extValid && valid) {
              this.doSubmit();
            } else {
              return false;
            }
          });
        });
      } else {
        this.$refs.innerForm.validate((valid) => {
          if(valid) {
            this.doSubmit();
          } else {
            return false;
          }
        });
      }
    },
    doSubmit() {
      this.submitting = true;
      if(this.submitHandler) {
        this.submitHandler().then((res) => {
          this.autoReject = false;
          this.dialogVisible = false;
          var message = this.$t('Dialog.DefaultSubmitMessage.Success');
          if(this.successMessageFormatter) {
            message = this.successMessageFormatter(res);
          }
          this.$message({
            message: message,
            type: 'success'
          });
          this.innerResolve(res);
        },(res) => {
          // Do not reject when error, then the promise is not broken user can resubmit.
          //this.autoReject = false;
          this.submitting = false;
          var message = this.$t('Dialog.DefaultSubmitMessage.Fail');
          if(this.errorMessageFormatter) {
            message = this.errorMessageFormatter(res);
          }
          this.$message({
            message: message,
            type: 'error'
          });
          // Do not reject when error, then the promise is not broken user can resubmit.
          //this.innerReject(res);
        });
      } else {
        this.autoReject = false;
        this.dialogVisible = false;
        this.innerResolve(true);
      }
    },
    popup(submitHandler) {
      if(this.$refs.innerForm) {
        this.$refs.innerForm.resetFields();
      }
      this.submitHandler = submitHandler;
      this.submitting = false;
      this.dialogVisible = true;
      return new Promise((resolve, reject) => {
        this.innerResolve = resolve;
        this.innerReject = reject;
      });
    },
    emptyPopup() {
      return this.popup(null);
    }
  }
}
</script>
