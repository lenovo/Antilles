<template>
<composite-form-dialog ref="innerDialog"
  :title="title" size="500px"
  :form-model="jobTemplateForm"
  :form-rules="jobTemplateRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
  <el-form-item :label="$t('JobTemplate.Name')" prop="name">
    <el-input id="tid_job-template-name" v-model="jobTemplateForm.name" :disabled="true"></el-input>
  </el-form-item>
  <el-form-item :label="$t('JobTemplate.Category')" v-if="mode == 'publish'">
    <el-select v-model="category">
      <el-option
        v-for="item in categoryOption"
        :key="item.value"
        :label="item.label"
        :value="item.value">
      </el-option>
  </el-select>
  </el-form-item>
  <el-form-item :label="$t('JobTemplate.Category.Other')" prop="category" v-if="mode == 'publish' && category == 'Other'">
    <el-input id="tid_job-template-category" v-model="jobTemplateForm.category"></el-input>
  </el-form-item>
</composite-form-dialog>
</template>
<script>
import JobTemplateService from '../../service/job-template'
import CompositeFormDialog from '../../component/composite-form-dialog'
import ValidRoleFactory from '../../common/valid-role-factory'

export default {
  data() {
    return {
      title: '',
      mode: '',
      category: 'HPC',
      categoryOption:[
        {value: 'HPC', label: this.$t('JobTemplateStore.Category.HPC')},
        {value: 'General', label: this.$t('JobTemplateStore.Category.General')},
        {value: 'Other', label: this.$t('JobTemplateStore.Category.Other')}
      ],
      jobTemplate: null,
      jobTemplateForm: {},
      jobTemplateRules: {
        category: [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Category')),
          ValidRoleFactory.getLengthRoleForText(this.$t('JobTemplate.Category'), 2, 10),
          ValidRoleFactory.getValidSystemNameRoleForText(this.$t('JobTemplate.Category'), true),
          {
            validator(rule, value, callback, source, options) {
              var errors = [];
              if (value.toLowerCase()  == 'all') {
                errors.push(new Error(window.gApp.$t('Valid.Text.SystemName.NoAll', {'name': window.gApp.$t('JobTemplate.Category'), 'value': value})))
              }
              callback(errors);
            }
          }
        ]
      }
    };
  },
  components: {
    'composite-form-dialog': CompositeFormDialog
  },
  watch: {
    category(val, oldVal) {
      if(val != 'Other') {
        this.jobTemplateForm.category = val;
      } else {
        this.jobTemplateForm.category = '';
      }
    }
  },
  methods: {
    submitForm() {
      if(this.mode == 'delete') {
        return JobTemplateService.deleteJobTemplate(this.jobTemplate.code);
      }
      if(this.mode == 'publish') {
        return JobTemplateService.publishJobTemplate(this.jobTemplate.code, this.jobTemplateForm.category);
      }
      if(this.mode == 'unpublish') {
        return JobTemplateService.unpublishJobTemplate(this.jobTemplate.code);
      }
    },
    successMessageFormatter(res) {
      var jobTemplate = res;
      if(this.mode == 'delete') {
        return this.$t('JobTemplate.Delete.Success', {'name': this.jobTemplate.name});
      }
      if(this.mode == 'publish') {
        return this.$t('JobTemplate.Publish.Success', {'name': this.jobTemplate.name});
      }
      if(this.mode == 'unpublish') {
        return this.$t('JobTemplate.Unpublish.Success', {'name': this.jobTemplate.name});
      }
    },
    errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    doDelete(jobTemplate) {
      this.mode = 'delete';
      this.jobTemplate = jobTemplate;
      this.jobTemplateForm = {
        name: jobTemplate.name
      };
      this.title = this.$t('JobTemplate.Delete.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doPublish(jobTemplate) {
      this.mode = 'publish';
      this.jobTemplate = jobTemplate;
      this.jobTemplateForm = {
        name: jobTemplate.name,
        category: jobTemplate.category || 'HPC'
      };
      this.title = this.$t('JobTemplate.Publish.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doUnpublish(jobTemplate) {
      this.mode = 'unpublish';
      this.jobTemplate = jobTemplate;
      this.jobTemplateForm = {
        name: jobTemplate.name
      };
      this.title = this.$t('JobTemplate.Unpublish.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>
