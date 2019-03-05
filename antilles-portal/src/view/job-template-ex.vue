<style scoped>
/*.el-checkbox-group {
  width: 100%;
  display: inline-block;
}*/
.job-template-title{
  margin-bottom: 20px;
  margin-top: 15px;
}
.logo-title{
  font-size:16px;
  font-weight: bold;
  margin-bottom: 14px;
}
.logo-description{
  font-size:14px;
}
.job-template-container {
  background: #fff;
  box-sizing: border-box;
  height:100%;
  padding: 20px;
}
.job-template-logo img {
  width: 180px;
  height: 40px;
  line-height: 0;
  object-fit: contain;
}
.tips-link {
  color: #409eff;
  text-decoration: none;
}
</style>
<template>
<div class="height--100 p-10">
<div class="job-template-container">
  <el-row class="job-template-title" v-if="jobTemplate!=null">
    <el-col :xs="24" :sm="9" :md="7" :lg="5"  class="job-template-logo">
      <img :src="jobTemplate.logo"/>
    </el-col>
    <el-col :xs="24" :sm="15" :md="17" :lg="19">
    <div class="logo-title">
        {{jobTemplate.name}}
    </div>
    <div class="logo-description">
        {{jobTemplate.description}}
    </div>
    </el-col>
  </el-row>
  <el-form :model="formModel" :rules="formRules" ref="innerForm" label-width="200px" v-if="jobTemplate!=null">
    <el-row>
      <el-collapse v-model="activeNames">
        <el-collapse-item v-for="(paramGroup, index) in paramGroups" :key='index' :title="paramGroup.title" :name="paramGroup.name">
          <el-form-item v-for="param in paramGroup.params" :key="param.id" :label="param.name" :prop="param.id" v-show="paramVisible[param.id]">
            <el-input v-if="param.type=='string' && param.mode=='input'" v-model="formModel[param.id]" style="width: 300px" @focus="emptyCall">
            </el-input>
            <el-input v-if="param.type=='number' && param.mode=='input'" v-model="formModel[param.id]" style="width: 300px" @focus="emptyCall">
            </el-input>
            <el-select v-if="(param.type=='string' || param.type=='number') && param.mode=='select'" v-model="formModel[param.id]">
              <el-option
                v-for="item in param.options"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
            <el-checkbox v-if="param.type=='boolean'" v-model="formModel[param.id]">
            </el-checkbox>
            <file-select v-if="param.type=='file'" v-model="formModel[param.id]" type="file" default-folder="MyFolder">
            </file-select>
            <file-select v-if="param.type=='folder'" v-model="formModel[param.id]" type="folder">
            </file-select>
            <el-select v-if="param.type=='image'" v-model="formModel[param.id]" style="width: 300px">
              <el-option
                v-for="item in imageOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
            <el-select v-if="param.type=='queue'" v-model="formModel[param.id]">
              <el-option
                v-for="item in queueOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
            <queue-resource v-if="param.type=='queue' && scheduler=='slurm'" :queue-options="queueOptions" :queue="formModel[param.id]"></queue-resource>
            <learning-rate-editor v-if="param.type=='ext.learning_rate'" v-model="formModel[param.id]"></learning-rate-editor>
            <optimizer-editor v-if="param.type=='ext.optimizer'" v-model="formModel[param.id]"></optimizer-editor>
            <training-steps-editor v-if="param.type=='ext.training_steps'" v-model="formModel[param.id]"></training-steps-editor>
            <ps-worker-editor v-if="param.type=='ext.psworker'" v-model="formModel[param.id]"
              :nodes="context[param.nodesField]"
              :gpu-per-node="context[param.gpuPerNodeField]"
              :worker-auto-policy="param.workerAutoPolicy">
            </ps-worker-editor>
            <span v-if="param.tips">
              <a :href="param.tips.url" class="tips-link" v-if="param.tips.type == 'link'" target="_blank">{{param.tips.name}}</a>
            </span>
          </el-form-item>
        </el-collapse-item>
      </el-collapse>
    </el-row>
    <el-row style="margin-top: 20px">
      <el-button type="primary"
        @click="onSubmitClick"
        v-loading.fullscreen.lock="submitting">{{$t('JobTemplate.Submit')}}</el-button>
    </el-row>
    <job-action-dialog id="tid_job-manange-action-dialog" ref="jobActionDialog" />
  </el-form>
</div>
</div>
</template>
<script>
import JobTemplateService from '../service/job-template'
import QueueService from '../service/queue'
import ImageService from '../service/image'
import JobService from '../service/job'
import ValidRoleFactory from '../common/valid-role-factory'
import FileSelect from '../component/file-select'
import JobActionDialog from '../widget/job-action-dialog'
import QueueResource from '../widget/queue-resource'
import AccessService from '../service/access'
import LearningRateEditor from './job-template-ex/learning-rate-editor'
import OptimizerEditor from './job-template-ex/optimizer-editor'
import TrainingStepsEditor from './job-template-ex/training-steps-editor'
import PSWorkerEditor from './job-template-ex/ps-worker-editor'

export default {
  data() {
    return {
      activeNames: ['base', 'param', 'resource'],
      code: '',
      job: null,
      jobTemplate: null,
      formModel: null,
      formRules: null,
      queueOptions: [],
      imageOptions: [],
      submitting: false,
      scheduler: '',
      paramGroups: [
        {
          'name': 'base',
          'title': this.$t('JobTemplate.BaseInformation'),
          'params': []
        },
        {
          'name': 'param',
          'title': this.$t('JobTemplate.Parameters'),
          'params': []
        },
        {
          'name': 'resource',
          'title': this.$t('JobTemplate.ResourceOptions'),
          'params': []
        },
        {
          'name': 'adv_param',
          'title': this.$t('JobTemplate.AdvancedParameters'),
          'params': []
        }
      ],
      paramVisible: {},
      paramTriggerCache: {},
      context: {}
    };
  },
  components: {
    'file-select': FileSelect,
    'job-action-dialog': JobActionDialog,
    'queue-resource': QueueResource,
    'learning-rate-editor': LearningRateEditor,
    'optimizer-editor': OptimizerEditor,
    'training-steps-editor': TrainingStepsEditor,
    'ps-worker-editor': PSWorkerEditor
  },
  created() {
    this.scheduler=AccessService.getScheduler();
  },
  mounted() {
    if(this.$route.params.code) {
      this.code = this.$route.params.code;
      this.job = null;
      this.init();
    }
    if(this.$route.params.jobId) {
      JobService.getJobById(this.$route.params.jobId).then((res) => {
        this.job = res;
        this.code = this.job.type;
        this.init();
      }, (res) => {
        this.$message.error(res);
      });
    }
  },
  watch: {
    formModel: {
      handler(val, oldVal) {
        let context = this.getParams(val);
        this.context = context;
        this.jobTemplate.params.forEach((param) => {
          if(param.visible) {
            this.paramVisible[param.id] = eval(param.visible);
          }
          if(param.valueTrigger) {
            let oldOne = null;
            if(this.paramTriggerCache.hasOwnProperty(param.id)) {
              oldOne = this.paramTriggerCache[param.id];
            }
            let newOne = eval(param.valueTrigger);
            let currentOne = context[param.id];
            if(oldOne != newOne) {
              this.formModel[param.id] = newOne;
            }
            this.paramTriggerCache[param.id] = newOne;
          }
        })
      },
      deep: true
    }
  },
  methods: {
    init() {
      JobTemplateService.getJobTemplate(this.code).then((res) => {
        var formModel = new Object();
        var formRules = new Object();
        res.params = this.formatFields(res.params);
        this.paramVisible = {};
        this.localizeParams(res.params);
        res.params.forEach((param) => {
          this.paramGroups.forEach((group) => {
            if(param.group == group.name) {
              group.params.push(param);
            }
          });
          formModel[param.id] = this.getFormValue(this.job, param);
          var rules = [];
          var minLength = 0;
          if(param.require) {
            minLength = 1;
            rules.push(ValidRoleFactory.getRequireRoleForText(param.name));
          }
          if(param.type == 'string') {
            if(param.mode == 'input') {
              if(param.id=='job_name') {
                minLength = 3;
                rules.push(ValidRoleFactory.getValidIdentityNameRoleForText(param.name));
              }
              rules.push(ValidRoleFactory.getLengthRoleForText(param.name, minLength, Number(param.maxLength)));
              if(param.validPolicy == 'default') {
                rules.push(ValidRoleFactory.getValidIdentityNameRoleForText(param.name));
              } else if(param.validPolicy == 'phone') {
                rules.push(ValidRoleFactory.getMobileRole(param.name));
              } else if(param.validPolicy == 'email') {
                rules.push(ValidRoleFactory.getEmailRole(param.name));
              }
            }
          }
          else if(param.type == 'number') {
            rules.push(ValidRoleFactory.getValidNumberRoleForText(param.name));
            if(param.hasOwnProperty('min') && param.hasOwnProperty('max')) {
              rules.push(ValidRoleFactory.getNumberRangeRoleForText(param.name, param.min, param.max));
            }
            if(param.hasOwnProperty('decimal')) {
              rules.push(ValidRoleFactory.getNumberDecimalRoleForText(param.name, param.decimal));
            }
          }
          else if(param.type == 'image') {
            this.initImage(param.id, param.hypervisor, param.framework);
          }
          else if(param.type == 'queue') {
            this.initQueue(param.id);
          }
          else if(param.type == 'ext.learning_rate') {
            rules = LearningRateEditor.getValidRules(param.name);
          }
          else if(param.type == 'ext.training_steps') {
            rules = TrainingStepsEditor.getValidRules(param.name);
          }
          formRules[param.id] = rules;
          // Set param visible
          this.paramVisible[param.id] = true;
        });
        // Remove the group that not contains param.
        var paramGroups = new Array();
        this.paramGroups.forEach((group) => {
          if(group.params.length > 0) {
            paramGroups.push(group);
          }
        });
        this.paramGroups = paramGroups;
        this.jobTemplate = res;
        this.formModel = formModel;
        this.formRules = formRules;
      }, (res) => {
        this.$message.error(res);
      });
    },
    getLocalizeVal(lang, label) {
      if(label[lang]) {
        return label[lang];
      }
      if(label['en']) {
        return label['en'];
      }
      return label;
    },
    formatFields(params) {
      var result = [];
      params.forEach((param) => {
        var obj = new Object();
        obj.id = param.id;
        obj.name = param.name;
        obj.group = param.class;
        obj.require = param.must;
        obj.type = param.dataType;
        if(obj.type == 'string') {
          obj.mode = param.input;
          if(obj.mode == 'input') {
            obj.maxLength = param.maxLength;
            obj.validPolicy = param.invalid;
          }
          if(obj.mode == 'select') {
            obj.options = [];
            param.selectOption.forEach((option) => {
              obj.options.push({
                value: option.value,
                label: option.label
              });
            });
          }
        }
        else if(obj.type == 'number') {
          obj.mode = param.input;
          if(obj.mode == 'input') {
            obj.min = param.minValue;
            obj.max = param.maxValue;
            obj.decimal = param.floatLength;
          }
          if(obj.mode == 'select') {
            obj.options = [];
            param.selectOption.forEach((option) => {
              obj.options.push({
                value: option.value,
                label: option.label
              });
            });
          }
        }
        else if(obj.type == 'image') {
          obj.hypervisor = 'singularity';
          obj.framework = param.framework;
        }
        else if(obj.type == 'ext.psworker'){
          obj.nodesField = param.nodesField;
          obj.gpuPerNodeField = param.gpuPerNodeField;
          obj.workerAutoPolicy = param.workerAutoPolicy;
        }
        if(param.hasOwnProperty('defaultValue')) {
          obj.default = param.defaultValue;
        }
        if(param.hasOwnProperty('visible')) {
          obj.visible = param.visible;
        }
        if(param.hasOwnProperty('tips')) {
          obj.tips = param.tips;
        }
        if(param.hasOwnProperty('valueTrigger')) {
          obj.valueTrigger = param.valueTrigger;
        }
        result.push(obj);
      });
      return result;
    },
    localizeParams(params) {
      var lang = this.$i18n.locale;
      params.forEach((param) => {
        param.name = this.getLocalizeVal(lang, param.name);
        if(param.options) {
          param.options.forEach((option) => {
            option.label = this.getLocalizeVal(lang, option.label);
          });
        }
        if(param.tips) {
          if(param.tips.type == 'link') {
            param.tips.name = this.getLocalizeVal(lang, param.tips.name);
          }
        }
      });
    },
    initImage(paramId, hypervisor, framework) {
      ImageService.getAllImages().then((res) => {
        res.forEach((image) => {
          if(this.job) {
            this.imageOptions.push({
              value: image.deployName,
              label: image.name
            });
          } else {
            if(image.framework == framework && image.hypervisorType == hypervisor) {
              if((image.username == this.$store.state.auth.username && image.type == 'PRIVATE') ||
                  image.type == 'SYSTEM') {
                if((image.hypervisorType == 'docker' && image.status == 'deployed') ||
                    (image.hypervisorType == 'singularity' && image.status == 'uploaded')) {
                  this.imageOptions.push({
                    value: image.deployName,
                    label: image.name
                  });
                }
              }
            }
          }
        });
        if(this.imageOptions.length > 0 && this.formModel[paramId] == '') {
          this.formModel[paramId] = this.imageOptions[0].value;
        }
      });
    },
    initQueue(paramId) {
      QueueService.getAllQueues().then((res) => {
        res.forEach((queue) => {
          this.queueOptions.push({
            state: queue.state,
            value: queue.name,
            label: queue.name,
            totalCores: queue.totalCores,
            totalNodes: queue.totalNodes,
            maxNodes: queue.maxNodes,
            maxCoresPerNode: queue.maxCoresPerNode,
            defineMemoryPerNode: queue.defineMemoryPerNode,
            maxMemoryPerNode: queue.maxMemoryPerNode,
            walltime: queue.walltime
          });
        });
        if(this.queueOptions.length > 0) {
          this.formModel[paramId] = this.queueOptions[0].value;
        }
      }, (res) => {
        this.$message.error(res);
      });
    },
    getParams(formModel) {
      var obj = new Object();
      this.jobTemplate.params.forEach((param) => {
        if(param.type=='number') {
          var val = parseFloat(formModel[param.id]);
          if(val) {
            obj[param.id] = val;
          } else {
            obj[param.id] = 0;
          }
        }
        else if((param.type=='file' || param.type=='folder') && this.jobTemplate.workspace) {
          obj[param.id] = formModel[param.id].replace('MyFolder', this.jobTemplate.workspace);
        }
        else {
          obj[param.id] = formModel[param.id];
        }
      });
      return obj;
    },
    getFormValue(job, param) {
      if(job) {
        return job.req.params[param.id];
      }
      if(param.hasOwnProperty('default')) {
        return param.default;
      }
      return '';
    },
    doCreateJob(nextUrl) {
      var params = this.getParams(this.formModel);
      this.submitting = true;
      JobService.createJobEx(this.jobTemplate, params).then((res) => {
        this.submitting = false;
        var job = res;
        if(job.schedulerId && job.schedulerId > 0) {
          var message = this.$t('Job.Submit.Success', {id: job.id, name: job.name, schedulerId: job.schedulerId});
          this.$message.success(message);
          if(nextUrl) {
            this.$router.push({ path: nextUrl});
          } else {
            this.$router.push({ path: '../job/' + job.id });
          }
        } else {
          var message = this.$t('Job.Submit.Error', {id: job.id, name: job.name});
          this.$message.error(message);
        }
      }, (res) => {
        this.submitting = false;
        this.$message.error(res);
      });
    },
    doResumeJob() {
      this.$refs.jobActionDialog.doResume(this.job).then((res) => {
        this.doCreateJob('../../job-manage');
      }, (res) => {
        // Do nothing
      });
    },
    onSubmitClick() {
      this.$refs.innerForm.validate((valid) => {
        if(valid) {
          this.$confirm(this.$t('JobTemplate.Submit.Tip'), this.$t('JobTemplate.Submit.Tip.Title'), {
            confirmButtonText: this.$t('JobTemplate.Submit.Submit'),
            cancelButtonText: this.$t('JobTemplate.Submit.Cancel'),
            type: 'warning'
          }).then(() => {
            if(this.job == null) {
              this.doCreateJob();
            } else {
              this.doResumeJob();
            }
          }).catch(() => {
          });
        } else {
          return false;
        }
      });
    },
    isParamDisabled(param) {
      return this.job != null && param.resumeEditable != true;
    },
    emptyCall(param) {
      // This call is a workaround for space key not working on some case.
      //console.log(param);
    }
  }
}
</script>
