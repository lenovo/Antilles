<style lang="css">

</style>
<template lang="html">

  <el-dialog ref="popupDialog" :title="dialogTitle" :visible.sync="isRender" class="FileManagerDialog" :append-to-body="true">
    <file-manager v-if='isRender' ref='fileManager' :init-path="initPath" :mode='mode' @selected='onSelected'/> 
  </el-dialog>
  
</template>

<script>
import FileManager from './file-manager'
export default {
  data () {
    return {      
      isRender: false,
      dialogTitle:'',
      initPath: '',
      mode:'',
      innerResolve: null,
      innerReject: null
    }
  },
  components: {
    FileManager
  },
  mounted() {
    this.$watch('isRender', (newVal, oldVal) => {
      if(!newVal)
        this.clearFileManager();
    })
  },
  methods: {
    selectFile(initPath) {
      this.setOptions(initPath, 'file');
      return new Promise((resolve, reject) => {
        this.innerResolve = resolve;
        this.innerReject = reject;
      });
    },
    selectFolder(initPath) {
      this.setOptions(initPath, 'folder');
      return new Promise((resolve, reject) => {
        this.innerResolve = resolve;
        this.innerReject = reject;
      });
    },
    openManager(initPath, title) {
      this.setOptions(initPath, '', title);
    },
    setOptions (path, mode, title) {
      if (title) {
        this.dialogTitle = this.$t('Elfinder.Select.' + title)
      } else {
        this.dialogTitle = mode?this.$t('Elfinder.Select.' + mode):this.$t('Elfinder.Manager');
      }
      this.mode = mode;
      this.initPath = path;
      this.isRender = true;
    },
    clearFileManager() {
      $jq('.elfinder-contextmenu').prev('audio').remove();
      $jq('.elfinder-contextmenu').remove();
      $jq('.elfinder-quicklook.ui-draggable').remove();
    },
    onSelected(path){
      this.isRender = false;
      this.innerResolve(path);
    }
  }
}
</script>
