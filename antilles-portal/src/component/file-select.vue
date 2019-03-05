<style scoped>
.select-file-input {
  width: 300px;
}
.job-detail-log .select-file-input {
	width: 500px;
}
</style>
<template>
<div style="display:inline;">
  <el-input readonly v-model="currentPath" class="select-file-input" :disabled="disabled"></el-input>
  <el-button @click="onBrowserClick" :disabled="disabled">{{$t('FileSelect.Browser')}}</el-button>
  <file-manager-dialog ref="fileManagerDialog" />
</div>
</template>
<script>
import FileManagerDialog from './file-manager-dialog'

export default {
  data() {
    return {
      currentPath: ''
    }
  },
  props: [
    'value',
    'defaultFolder',
    'type',
    'disabled'
  ],
  components: {
    'file-manager-dialog': FileManagerDialog
  },
  mounted() {
    this.currentPath = this.value;
  },
  watch: {
    value(val, oldVal) {
      this.currentPath = val;
    }
  },
  methods: {
    onBrowserClick() {
      if(this.type=='file') {
        this.$refs.fileManagerDialog.selectFile(this.defaultFolder).then((path) => {
          this.currentPath = path;
          this.$emit('input', this.currentPath);
        });
      }
      if(this.type=='folder') {
        this.$refs.fileManagerDialog.selectFolder(this.defaultFolder).then((path) => {
          this.currentPath = path;
          this.$emit('input', this.currentPath);
        });
      }
    }
  }
}

</script>
