<style>
.file-icon-select .el-dialog__body{
  padding:0 20px;
}
</style>
<template>
<div class="height--100 p-10">
<div class="job-template-editor-container file-icon-select table-style b-w p-20">
  <el-form :model="formModel" :rules="formRules" ref="innerForm" label-width="200px">
    <el-row>
      <el-collapse v-model="activeNames">
        <el-collapse-item :title="$t('JobTemplate.BaseInformation')" name="base">
          <el-form-item :label="$t('JobTemplate.Name')" prop="name">
            <el-input v-model="formModel.name" style="width: 300px"></el-input>
          </el-form-item>
          <el-form-item :label="$t('JobTemplate.Logo')" prop="logo">
            <file-icon-select ref="fileAlertSelect"  v-model="formModel.logo" :restore-icon='restoreIcon'/>
            <span>{{$t('JobTemplate.Logo.size')}}</span>
          </el-form-item>
          <el-form-item :label="$t('JobTemplate.Description')" prop="description">
            <el-input v-model="formModel.description" style="width: 300px"></el-input>
          </el-form-item>
        </el-collapse-item>

        <el-collapse-item :title="$t('JobTemplate.Parameters')" name="param">
          <parameters-editor
            :parameters="formModel.parameters">
          </parameters-editor>
        </el-collapse-item>
        <el-collapse-item :title="$t('JobTemplate.TemplateFile')" name="file">
          <template-file-editor ref="templateFileEditor"
            :content="formModel.fileTemplate">
          </template-file-editor>
        </el-collapse-item>
      </el-collapse>
    </el-row>
    <el-row style="margin-top: 20px">
      <el-button type="primary"
        @click="onSubmitClick"
        v-loading.fullscreen.lock="submitting">{{$t('JobTemplate.Submit')}}</el-button>
        <el-button
          @click="onBackClick"
          v-loading.fullscreen.lock="submitting">{{$t('JobTemplate.Cancel')}}</el-button>
    </el-row>
  </el-form>
</div>
</div>
</template>
<script>
import JobTemplateService from '../service/job-template'
import ValidRoleFactory from '../common/valid-role-factory'
import ParametersEditor from './job-template-editor/parameters-editor'
import TemplateFileEditor from './job-template-editor/template-file-editor'
import FileIconSelect from '../component/file-icon-select'

export default {
  data() {
    return {
      activeNames: ['base', 'param', 'file'],
      restoreIcon:'',
      code: '',
      jobTemplate: null,
      formModel: {
        name: '',
        logo: '',
        description: '',
        parameters: [],
        fileTemplate: '#!/bin/bash\n#SBATCH --job-name={{job_name}}\n#SBATCH --workdir={{job_workspace}}\n#SBATCH --partition={{job_queue}}'
      },
      formRules: {
        name: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Name')),
          ValidRoleFactory.getValidIdentityNameRoleForText(this.$t('JobTemplate.Name')),
          ValidRoleFactory.getLengthRoleForText(this.$t('JobTemplate.Name'), 3, 20)
        ],
        logo: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Logo'))
        ],
        description: [
          ValidRoleFactory.getLengthRoleForText(this.$t('JobTemplate.Description'), 0, 100)
        ]
      },
      submitting: false
    };
  },
  components: {
    'parameters-editor': ParametersEditor,
    'template-file-editor': TemplateFileEditor,
    'file-icon-select': FileIconSelect
  },
  watch: {
    "formModel.logo": function (val, oldVal) {
      if(val.indexOf("data:image/jpeg;base64,") == 0) {
        this.formRules.logo = [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Logo'))
        ];
      } else {
        this.formRules.logo = [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Logo')),
          ValidRoleFactory.getSuffixValid(this.$t('JobTemplate.Logo'), ["jpeg","jpg","png","bmp"])
        ];
      }
    }
  },
  mounted() {
    if(this.$route.params.code) {
      this.code = this.$route.params.code;
      this.jobTemplate = null;
      this.init();
    } else {
      this.formModel.parameters = [{
          id: 'job_name',
          name: this.$t('Job.Name'),
          class: 'base',
          dataType: 'string',
          must: true,
          type: 'system',
          input: 'input',
          maxLength: 32
        },
        {
          id: 'job_workspace',
          name: this.$t('Job.Workspace'),
          class: 'param',
          dataType: 'folder',
          must: true,
          type: 'system'
        },
        {
          id: 'job_queue',
          name: this.$t('Job.Queue'),
          class: 'resource',
          dataType: 'queue',
          must: true,
          type: 'system'
        }];
    }
  },
  methods: {
    init() {
      JobTemplateService.getJobTemplate(this.code).then((res) => {
        if(this.$route.path.includes('job-template-editor/copy')){
          this.formModel.name = res.name + '_' + 'copy';
        }else{
          this.formModel.name = res.name;
        }
        this.formModel.logo = res.logo;
        this.formModel.description = res.description;
        this.formModel.parameters = res.params;
        this.formModel.fileTemplate = res.templateFileContent;
        this.restoreIcon = res.logo;
      }, (res) => {
        this.$message.error(res);
      });
    },
    onSubmitClick() {
      this.$refs.innerForm.validate((valid) => {
        if(valid) {
          if(this.formModel.parameters.length <= 0) {
            this.$message.error(this.$t('Valid.Require', {'name': this.$t('JobTemplate.Parameters')}))
            return false;
          }
          var fileTemplateContent = this.$refs.templateFileEditor.getContent();
          if(fileTemplateContent.length <= 0) {
            this.$message.error(this.$t('Valid.Require', {'name': this.$t('JobTemplate.TemplateFile')}))
             console.log(fileTemplateContent);
            return false;
          }
          this.submitting = true;
          var submitPromise = null;
          var mode = '';
          if(this.code == '' || this.$route.path.includes('job-template-editor/copy')) {
            mode = 'Create'
            submitPromise = JobTemplateService.createJobTemplate(this.formModel.name,
              this.formModel.logo,
              this.formModel.description,
              this.formModel.parameters,
              fileTemplateContent);
          } else {
            mode = 'Update'
            submitPromise = JobTemplateService.updateJobTemplate(this.code,
              this.formModel.name,
              this.formModel.logo,
              this.formModel.description,
              this.formModel.parameters,
              fileTemplateContent);
          }
          submitPromise.then((res) => {
            this.submitting = false;
            var jobTemplate = res;
            var message = this.$t(`JobTemplate.Submit.${mode}.Success`, {id: jobTemplate.id, name: jobTemplate.name});
            this.$message.success(message);
            if(this.$route.path.includes('job-template-editor/copy')){
              this.$router.push({ path: '../../job-template-store/mytemplates' });
            }else{
              this.$router.push({ path: '../job-template-store/mytemplates' });
            }
          }, (res) => {
            this.submitting = false;
            this.$message.error(res);
          });
        } else {
          return false;
        }
      });
    },
    onBackClick() {
      this.$confirm(this.$t('JobTemplate.Cancel.Text'), '', {
        confirmButtonText: this.$t('Global.Btn.confirm'),
        cancelButtonText: this.$t('Global.Btn.cancel'),
        type: 'warning'
      }).then(() => {
        window.history.back();
      }).catch(() => {
      });
    }
  }
}
</script>
