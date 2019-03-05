
<style lang="css">
  .ui-resizable {
      position: absolute;
  }
</style>

<template lang="html">
  <div class="antilles-fileManager"></div>
</template>

<script>
export default {
  data () {
    return {
      defaultFilePath: this.initPath?this.processFilePath(this.initPath) : 'MyFolder',
      defaultSelectType: this.mode ? this.mode == 'folder'? 'choosefolder':'choosefile':'',
      isPopManager: false,
      width: '',
      height: ''
    }
  },
  props: [
    "initPath",
    "mode"
  ],
  mounted () {
    this.getDataHash();
  },
  watch: {
    'initPath':function(val, oldVal){
      this.defaultFilePath = val?this.processFilePath(val) : 'MyFolder',
      this.create();
    }
  },
  beforeDestroy() {
    $jq('.elfinder-quicklook').trigger('close');
  },
  methods: {
    ajaxBeforeSend(req) {
      var token = this.$store.state.auth.token;
      req.setRequestHeader('authorization', 'Jwt ' + token);
    },
    create() {
      this.getDataHash();
    },
    processFilePath(path) {
      if(path.substr(path.length - 1,1) == '/') {
        path = path.substring(0,path.length - 1);
      }
      return path;
    },
    getDataHash() {
      var self = this;
      // Setup ajax for ELFinder
      $jq.ajaxSetup({
        beforeSend: self.ajaxBeforeSend
      });
      $jq.ajax({
          url: '/api/files-connector/',
          type: 'GET',
          dataType: 'json',
          data: {"cmd": "hash", "path": self.defaultFilePath},
      }).done(function (data) {
          self.$store.dispatch('elfinder/setStorage',data.hash);
          self.showManager();
      });

    },
    showManager() {
      var self = this;
      self.isPopManager = $jq('.antilles-fileManager').elfinder({
        url: '/api/files-connector/',
        lang: 'en',
        defaultView: 'list',
        width: self.width,
        height: self.height,
        useBrowserHistory: false,
        resizable: false,
        uiOptions: {
            // toolbar configuration
            toolbar: [
                ['back' , 'forward'],
                ['home'], [self.defaultSelectType], ['reload'],
                [ 'upload', 'download'],
                ['mkdir', 'mkfile','rm'],
                ['search'],
                ['sort']//,
                // ['info']
            ]
        },
        handlers: {
            init: function (event, elfinderInstance) {
              if(self.mode){
                $jq('.elfinder-button-icon-'+self.defaultSelectType).parent().css("width", "100px");
                $jq('.elfinder-button-icon-'+self.defaultSelectType).parent().css("cursor", "default");
                $jq('.elfinder-button-icon-'+self.defaultSelectType).css("padding-left", "20px");
                $jq('.elfinder-button-icon-'+self.defaultSelectType).css("font-family", 'Arial, "Microsoft YaHei", "微软雅黑", sans-serif');
                $jq('.elfinder-button-icon-'+self.defaultSelectType).css("font-size", "14px");
                $jq('.elfinder-button-icon-'+self.defaultSelectType).css("display", "inline");
                $jq('.elfinder-button-icon-'+self.defaultSelectType).text(self.$t('Elfinder.Select.' + self.mode));
              }
            }
        },
        commands: [
          'choosefolder', 'choosefile','open', 'reload', 'home', 'up', 'back',
          'forward', 'getfile', 'quicklook', 'download', 'rm', 'duplicate',
          'rename', 'mkdir', 'mkfile', 'upload', 'copy', 'cut', 'paste', 'edit',
          'extract', 'archive', 'search', 'info', 'view', 'help',
          'sort', 'netmount'
        ],
        contextmenu: {
            // navbarfolder menu
            navbar: ['open', '|', 'rm', '|'],

            // current directory menu
            cwd: ['reload', 'back', '|', 'upload', 'mkdir', 'mkfile'],

            // current directory file menu
            files: [
                'download', '|', 'rm', '|', 'edit', 'rename', '|', 'quicklook', 'extract', 'archive'
            ]
        },

        chooseFileCallback: function (file) {
          self.$emit('selected',file.path);
          // self.clear();
            // current.validateMPIProg(current);
        },
        getFolderCallback(file) {
          self.$emit('selected',file.path);
          // self.clear();
        }
      }).elfinder('instance');
    }

  }

}
</script>
