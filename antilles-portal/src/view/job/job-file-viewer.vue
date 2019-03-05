<style lang="css">
#detail_edit {
  margin-top: 20px;
  min-height: 450px;
}
#jobFileSelector .select-file-input{
    width: 500px;
}
</style>

<template>
    <div>
        <file-select ref="jobFileSelector" 
        id="jobFileSelector" 
        type="file" 
        :default-folder="innerWorkspace" 
        v-model="fileFullPath"></file-select>
        <div id="detail_edit" class="grid-content height--100"></div>
    </div>
</template>

<script>
import JobService from "../../service/job"
import FileSelect from '../../component/file-select'

export default {
    data(){
        return {
            editor: '',
            fileFullPath: this.fileName,
            filePath: this.fileName.replace("MyFolder/",""),
            innerWorkspace: ''
        }
    },
    props: [
        'fileName',
        "workspace",
        'mappingPath'
    ],
    components: {
        'file-select': FileSelect
    },
    mounted() {
        if(this.workspace) {
            this.innerWorkspace = this.workspace;
        }
        this.updateJobFile();
        this.$refs.jobFileSelector.$on('input',function(path){
            this.filePath = path.replace("MyFolder/","");
            this.updateJobFile();
        }.bind(this))
    },
    methods: {
        updateJobFile(){
            var that = this;
            this.editor = ace.edit("detail_edit");
            this.editor.setFontSize(16);
            this.editor.setReadOnly(true);
            JobService.getJobLog(this.filePath,0,0).then(function(res){
                var contain = res.lines.join("\n");
                that.editor.setValue(contain, -1);
            })
        }
    }
}
</script>
