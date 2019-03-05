<style lang="css">
.select-file-input {
    width: 300px;
  }
  .job-detail-log .select-file-input {
    width: 500px;
  }
  .dialog-footer{
    padding-left: 10px;
    color: #333;
    font-size: 18px;
  }
  .showImgs{
    display: flex;
    flex-wrap: wrap;
    justify-content:center;
  }
  .selectImg{
    padding:1%;
    border:1px solid transparent;
    width: 30%;
    height:30%;
  }
  .selectImg:hover {
    box-shadow:  0px 0px 2px 3px #f1f1f1;;
    border-radius: 2px;
    cursor:pointer;
    opacity:9;
  }
  .create-jobtemplate-logo-show {
    box-sizing: border-box;
    border: 1px solid transparent;
    width: 180px;
    height: 40px;
    line-height: 0;
    object-fit: contain;
  }
</style>
<template lang="html">
  <div style="display:flex;">
      <el-input readonly  v-model="value" class="select-file-input" v-show="!iconShow"></el-input>
      <img :src="value" v-if="iconShow" class="create-jobtemplate-logo-show"/>
      <el-button @click="dialogTableVisible = true">{{$t('FileSelect.Select')}}</el-button>
      <el-button @click="onRestoreIcon(restoreIcon)" v-if='restoreIcon&&restoreIcon!=value'>{{$t('FileSelect.Restore')}}</el-button>
      <el-dialog  width="40%" :visible.sync="dialogTableVisible" left>
        <span slot="title" class="dialog-footer" style="text-align: left;">ICON</span>
        <div class="showImgs">
            <img  v-for="logo in defaultIcon" :src="logo" @click="selectIcon(logo)" class="selectImg">
        </div>
        <div slot="footer" class="dialog-footer" style="text-align: left;">
          <el-button @click="onCustomClick">{{$t('FileSelect.Browser')}}</el-button>
        </div>
      </el-dialog>
      <file-manager-dialog ref="fileManagerDialog"/>
  </div>
</template>

<script>
import FileManagerDialog from './file-manager-dialog'
import JobTemplateService from './../service/job-template.js'

export default {
  data () {
    return {
      defaultIcon: [],
      dialogTableVisible: false,
      iconShow: false
    }
  },
  props: [
    'value',
    'restoreIcon'
  ],
  components: {
    'file-manager-dialog': FileManagerDialog
  },
  mounted() {
    this.getDefaultIcon();
  },
  watch: {
    value(val, oldVal) {
      if(this.value.includes('data:image')) {
        this.iconShow = true;
      }
    }
  },
  methods: {
    selectIcon(logo){
      var _this = this;
      _this.dialogTableVisible= false;
      _this.convertImgToBase64(logo, function(base64Img){
           _this.iconShow = true;
           _this.$emit('input', base64Img);
     });

    },
    onCustomClick() {
      this.dialogTableVisible= false;
      this.iconShow = false;
      this.$refs.fileManagerDialog.selectFile(this.defaultFolder).then((path) => {
        this.$emit('input', path);
      });
    },
    onRestoreIcon(icon) {
      this.$emit('input', icon);
    },
    convertImgToBase64(url, callback, outputFormat){
       var canvas = document.createElement('CANVAS'),
    　　ctx = canvas.getContext('2d'),
    　　img = new Image;
    　　img.crossOrigin = 'Anonymous';
    　　img.onload = function(){
        　　canvas.height = img.height;
        　　canvas.width = img.width;
        　　ctx.drawImage(img,0,0);
        　　var dataURL = canvas.toDataURL(outputFormat || 'image/jpeg');
        　　callback.call(this, dataURL);
        　　canvas = null;
        };
    　　img.src = url;
    },
    getDefaultIcon() {
      JobTemplateService.getDefaultIcons().then((res)=> {
        this.defaultIcon = res;
      }, (res)=> {});
    }
  }
}

</script>
