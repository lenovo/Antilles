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
        <el-collapse-item :title="$t('JobTemplate.BaseInformation')" name="base">
          <el-form-item :label="$t('JobTemplate.JobName')" prop="jobName">
            <el-input v-model="formModel.jobName" style="width: 300px" :disabled="job != null"></el-input>
          </el-form-item>
          <el-form-item v-for="param in filterParams(jobTemplate.params, 'include', 'workingdir')" :key="param.id" :label="param.label" :prop="param.id">
            <file-select v-if="param.type=='folder'" v-model="formModel[param.id]" type="folder" :disabled="isParamDisabled(param)">
            </file-select>
          </el-form-item>
        </el-collapse-item>
        <el-collapse-item :title="$t('JobTemplate.Parameters')" name="param" v-if="jobTemplate.params.length > 0">
          <el-form-item v-for="param in filterParams(jobTemplate.params, 'exclude', 'workingdir')" :key="param.id" :label="param.label" :prop="param.id">
            <el-checkbox-group v-if="param.type=='checkbox'" v-model="formModel[param.id]" :disabled="isParamDisabled(param)">
              <el-checkbox v-for="option in param.options" :key="option.value" :label="option.label"></el-checkbox>
            </el-checkbox-group>
            <el-select v-if="param.type=='select'" v-model="formModel[param.id]" :disabled="isParamDisabled(param)">
              <el-option
                v-for="item in param.options"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
            <file-select v-if="param.type=='file'" v-model="formModel[param.id]" type="file" default-folder="MyFolder" :disabled="isParamDisabled(param)">
            </file-select>
            <file-select v-if="param.type=='folder'" v-model="formModel[param.id]" type="folder" :disabled="isParamDisabled(param)">
            </file-select>
            <el-input v-if="param.type=='string'" v-model="formModel[param.id]" style="width: 300px" :disabled="isParamDisabled(param)">
            </el-input>
            <el-input v-if="param.type=='number'" v-model="formModel[param.id]" style="width: 300px" :disabled="isParamDisabled(param)">
            </el-input>
            <el-input type="textarea" v-if="param.type=='text'" v-model="formModel[param.id]" style="width: 600px;" :autosize="{minRows: 10}" resize="none" :disabled="isParamDisabled(param)">
            </el-input>
          </el-form-item>
        </el-collapse-item>
        <el-collapse-item :title="$t('JobTemplate.ResourceOptions')" name="resource" v-if="jobTemplate.resourceOptions.length > 0">
          <el-form-item :label="$t('JobTemplate.Queue')" prop="queue" v-if="jobTemplate.resourceOptions.indexOf('queue') >= 0">
            <el-select v-model="formModel.queue">
              <el-option
                v-for="item in queueOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
            <queue-resource v-if="scheduler=='slurm'" :queue-options="queueOptions" :queue="formModel.queue"></queue-resource>
          </el-form-item>
          <el-form-item :label="$t('JobTemplate.Nodes')" prop="nodes" v-if="jobTemplate.resourceOptions.indexOf('nodes') >= 0">
            <el-input v-model="formModel.nodes" style="width: 300px" @change="onNodesChanged()"></el-input>
          </el-form-item>
          <el-form-item :label="$t('JobTemplate.Exclusive')" prop="exclusive" v-if="jobTemplate.resourceOptions.indexOf('exclusive') >= 0">
            <el-checkbox v-model="formModel.exclusive"></el-checkbox>
          </el-form-item>
          <el-form-item :label="coresPerNodeLabel" prop="coresPerNode" v-if="jobTemplate.resourceOptions.indexOf('coresPerNode') >= 0" v-show="!formModel.exclusive">
            <el-input v-model="formModel.coresPerNode" style="width: 300px" :disabled="disableNodeResource">
              <template slot="append">{{$t('JobTemplate.CoresPerNode.Unit')}}</template>
            </el-input>
          </el-form-item>
          <el-form-item :label="gpusPerNodeLabel" prop="gpusPerNode" v-if="jobTemplate.resourceOptions.indexOf('gpusPerNode') >= 0">
            <el-input v-model="formModel.gpusPerNode" style="width: 300px" :disabled="disableNodeResource">
              <template slot="append">{{$t('JobTemplate.GpusPerNode.Unit')}}</template>
            </el-input>
          </el-form-item>
          <el-form-item :label="$t('JobTemplate.RAMSize')" prop="ramSize" v-if="jobTemplate.resourceOptions.indexOf('ramSize') >= 0" v-show="!formModel.exclusive">
            <el-input v-model="formModel.ramSize" style="width: 300px" :disabled="disableNodeResource">
              <template slot="append">{{$t('JobTemplate.RAMSize.Unit')}}</template>
            </el-input>
          </el-form-item>
          <el-form-item :label="$t('JobTemplate.RunTime')" prop="runTime" v-if="jobTemplate.resourceOptions.indexOf('runTime') >= 0">
            <el-input v-model="formModel.runTime" style="width: 300px">
              <template slot="append">{{$t('JobTemplate.RunTime.Unit')}}</template>
            </el-input>
          </el-form-item>
          <el-form-item :label="$t('JobTemplate.Resumable')" prop="resumable" v-if="jobTemplate.resourceOptions.indexOf('resumable') >= 0">
            <el-select v-model="formModel.resumable">
              <el-option :label="$t('JobTemplate.Resumable.Enable')" value="enable"></el-option>
              <el-option :label="$t('JobTemplate.Resumable.Disable')" value="disable"></el-option>
            </el-select>
          </el-form-item>
        </el-collapse-item>
        <el-collapse-item :title="$t('JobTemplate.NotifyOptions')" name="notify" v-if="jobTemplate.notifyOptions.length > 0">
          <el-form-item :label="$t('JobTemplate.Triggers')" prop="triggers" v-if="jobTemplate.notifyOptions.indexOf('triggers') >= 0">
            <el-checkbox-group v-model="formModel.triggers" :disabled="job != null">
              <el-checkbox v-for="option in triggerOptions" :key="option.value" :label="option.label"></el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item :label="$t('JobTemplate.Email')" prop="email" v-if="jobTemplate.notifyOptions.indexOf('email') >= 0">
            <el-input v-model="formModel.email" style="width: 300px" :disabled="job != null"></el-input>
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
import JobService from '../service/job'
import ValidRoleFactory from '../common/valid-role-factory'
import FileSelect from '../component/file-select'
import JobActionDialog from '../widget/job-action-dialog'
import queueResource from '../widget/queue-resource'
import AccessService from '../service/access'

export default {
  data() {
    return {
      activeNames: ['base', 'param', 'resource', 'notify'],
      code: '',
      job: null,
      title: location.search,
      description:location.search,
      jobTemplate: null,
      // formModel: {
      //   jobName: ''
      // },
      // formRules: {
      //   jobName: [
      //     ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.JobName')),
      //     ValidRoleFactory.getLengthRoleForText(this.$t('JobTemplate.JobName'), 3, 20)
      //   ]
      // },
      formModel: null,
      formRules: null,
      queueOptions: [],
      triggerOptions: [],
      submitting: false,
      scheduler: '',
      disableNodeResource: true,
    };
  },
  components: {
    'file-select': FileSelect,
    'job-action-dialog': JobActionDialog,
    'queue-resource': queueResource
  },
  computed: {
    coresPerNodeLabel: function() {
      if(!this.formModel.hasOwnProperty('nodes')) {
        return this.$t('JobTemplate.CoresPerNode.SingleNode');
      } else {
        return this.$t('JobTemplate.CoresPerNode');
      }
    },
    gpusPerNodeLabel: function() {
      if(!this.formModel.hasOwnProperty('nodes')) {
        return this.$t('JobTemplate.GpusPerNode.SingleNode');
      } else {
        return this.$t('JobTemplate.GpusPerNode');
      }
    }
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
  methods: {
    init() {
      JobTemplateService.getJobTemplate(this.code).then((res) => {
        this.localizeParams(res.params);
        var formModel = new Object();
        var formRules = new Object();
        if(this.job) {
          formModel.jobName = this.job.name;
        } else {
          formModel.jobName = '';
        }
        formRules.jobName = [
          ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.JobName')),
          ValidRoleFactory.getLengthRoleForText(this.$t('JobTemplate.JobName'), 3, 20),
          ValidRoleFactory.getValidIdentityNameRoleForText(this.$t('JobTemplate.JobName'))
        ];
        res.params.forEach((param) => {
          formModel[param.id] = this.getFormValue(this.job, param);
          if(param.type=='checkbox') {
            // No rule
          }
          else if(param.type=='number') {
            var numberRules = [];
            if(param.required) {
              numberRules.push(ValidRoleFactory.getRequireRoleForText(param.label));
            }
            numberRules.push(ValidRoleFactory.getValidNumberRoleForText(param.label));
            if(param.hasOwnProperty('min') && param.hasOwnProperty('max')) {
              numberRules.push(ValidRoleFactory.getNumberRangeRoleForText(param.label, param.min, param.max));
            }
            if(param.hasOwnProperty('decimal')) {
              numberRules.push(ValidRoleFactory.getNumberDecimalRoleForText(param.label, param.decimal));
            }
            formRules[param.id] = numberRules;
          }
          else {
            if(param.required) {
              formRules[param.id] = [
                ValidRoleFactory.getRequireRoleForText(param.label)
              ]
            }
          }
        });
        this.initResourceOptions(res.resourceOptions, formModel, formRules);
        this.initNotifyOptions(res.notifyOptions, formModel, formRules);
        this.jobTemplate = res;
        this.formModel = formModel;
        this.formRules = formRules;
        this.onNodesChanged();
      }, (res) => {
        this.$message.error(res);
      });
    },
    getLocalizeLabel(lang, labels) {
      if(labels[lang]) {
        return labels[lang];
      }
      return labels['en'];
    },
    localizeParams(params) {
      var lang = this.$i18n.locale;
      params.forEach((param) => {
        param.label = this.getLocalizeLabel(lang, param.label);
        if(param.options) {
          param.options.forEach((option) => {
            option.label = this.getLocalizeLabel(lang, option.label);
          });
        }
      });
    },
    initResourceOptions(options, formModel, formRules) {
      options.forEach((option) => {
        if(option=='queue') {
          formModel.queue = '';
          formRules.queue = [
            ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Queue'))
          ];
          this.initQueue();
        }
        if(option=='nodes') {
          formModel.nodes = '1';
          formRules.nodes = [
            ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Nodes')),
            ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.Nodes')),
            ValidRoleFactory.getNumberDecimalRoleForText(this.$t('JobTemplate.Nodes'), 0),
            ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.Nodes'), 1, 9999)
          ];
        }
        if(option=='exclusive') {
          formModel.exclusive = true;
        }
        if(option=='coresPerNode') {
          formModel.coresPerNode = '1';
          formRules.coresPerNode =  [
            ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.CoresPerNode')),
            ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.CoresPerNode')),
            ValidRoleFactory.getNumberDecimalRoleForText(this.$t('JobTemplate.CoresPerNode'), 0),
            ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.CoresPerNode'), 1, 9999)
          ];
        }
        if(option=='gpusPerNode') {
          formModel.gpusPerNode = '';
          formRules.gpusPerNode = [
            ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.GpusPerNode')),
            ValidRoleFactory.getNumberDecimalRoleForText(this.$t('JobTemplate.GpusPerNode'), 0),
            ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.GpusPerNode'), 1, 9999)
          ];
        }
        if(option=='ramSize') {
          formModel.ramSize = '';
          formRules.ramSize = [
            ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.RAMSize')),
            ValidRoleFactory.getNumberDecimalRoleForText(this.$t('JobTemplate.RAMSize'), 0),
            ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.RAMSize'), 1, 9999)
          ];
        }
        if(option=='runTime') {
          formModel.runTime = '';
          formRules.runTime = [
            ValidRoleFactory.getValidNumberRoleForText(this.$t('JobTemplate.RunTime')),
            ValidRoleFactory.getNumberDecimalRoleForText(this.$t('JobTemplate.RunTime'), 2),
            ValidRoleFactory.getNumberRangeRoleForText(this.$t('JobTemplate.RunTime'), 1, 999)
          ];
        }
        if(option=='resumable') {
          formModel.resumable = 'enable';
          formRules.resumable = [
            ValidRoleFactory.getRequireRoleForText(this.$t('JobTemplate.Queue'))
          ];
        }
        if(option=='psWorker') {
          formModel.psWorker = {
            mode: 'auto',
            psNumber: 1,
            workerNumber: 1,
            gpuPerWorker: 1
          };
        }
      });
    },
    initNotifyOptions(options, formModel, formRules) {
      options.forEach((option) => {
        if(option=='triggers') {
          formModel.triggers = [];
          formRules.triggers = [];
          this.initTrigger();
        }
        if(option=='email') {
          formModel.email = '';
          formRules.email = [
            ValidRoleFactory.getEmailRole(this.$t('JobTemplate.Email'))
          ];
        }
      });
    },
    initQueue() {
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
          this.formModel.queue = this.queueOptions[0].value;
        }
      }, (res) => {
        this.$message.error(res);
      });
    },
    initTrigger() {
        this.triggerOptions.push({
          value: 'suspend',
          label: this.$t('JobTemplate.Trigger.Suspend')
        });
        this.triggerOptions.push({
          value: 'finish',
          label: this.$t('JobTemplate.Trigger.Finish')
        });
    },
    getParams() {
      var obj = new Object();
      this.jobTemplate.params.forEach((param) => {
        if(param.type=='checkbox') {
          obj[param.id] = [];
          this.formModel[param.id].forEach((checkedLabel) => {
            for(var i=0; i<param.options.length; i++) {
              if(param.options[i].label == checkedLabel) {
                obj[param.id].push(param.options[i].value);
              }
            }
          });
        }
        else if(param.type=='number') {
          var val = parseFloat(this.formModel[param.id]);
          if(val) {
            obj[param.id] = val;
          } else {
            obj[param.id] = 0;
          }
        }
        else {
          obj[param.id] = this.formModel[param.id];
        }
      });
      return obj;
    },
    getFormValue(job, param) {
      if(param.type=='checkbox') {
        var result = [];
        var checkedValues = [];
        if(job) {
          checkedValues = job.req.params[param.id]
        }
        if(param.default) {
          checkedValues = param.default.split(',');
        }
        checkedValues.forEach((value) => {
          for(var i=0; i<param.options.length; i++) {
            if(param.options[i].value == value) {
              result.push(param.options[i].label);
            }
          }
        });
        return result;
      }
      if(param.type=='number') {
        if(job) {
          return String(job.req.params[param.id]);
        }
        if(param.default) {
          return String(param.default);
        }
        return '';
      }
      if(job) {
        return job.req.params[param.id];
      }
      if(param.default) {
        return param.default;
      }
      return '';
    },
    getResourceParams() {
      var obj = new Object();
      this.jobTemplate.resourceOptions.forEach((option) => {
        if(option=='nodes' || option=='coresPerNode' || option=='gpusPerNode' || option=='ramSize' || option=='runTime') {
          var val = parseFloat(this.formModel[option]);
          if(val) {
            obj[option] = val;
          } else {
            obj[option] = 0;
          }
        } else {
          obj[option] = this.formModel[option];
        }
      });
      return obj;
    },
    getNotifyParams() {
      var obj = new Object();
      this.jobTemplate.notifyOptions.forEach((option) => {
        if(option == 'triggers') {
          obj[option] = [];
          this.formModel[option].forEach((checkedLabel) => {
            for(var i=0; i<this.triggerOptions.length; i++) {
              if(this.triggerOptions[i].label == checkedLabel) {
                obj[option].push(this.triggerOptions[i].value);
              }
            }
          });
        } else {
          obj[option] = this.formModel[option];
        }
      });
      return obj;
    },
    doCreateJob(nextUrl) {
      var params = this.getParams();
      var resourceParams = this.getResourceParams();
      var notifyParams = this.getNotifyParams();
      this.submitting = true;
      JobService.createJob(this.code, this.formModel.jobName, params, resourceParams, notifyParams).then((res) => {
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
    onNodesChanged() {
      if(!this.formModel.hasOwnProperty('nodes')) {
        this.disableNodeResource = false;
        return;
      }
      if(this.formModel.nodes && parseInt(this.formModel.nodes) > 0) {
        this.disableNodeResource = false;
      } else {
        this.disableNodeResource = true;
        if(this.formModel.coresPerNode) {
          this.formModel.coresPerNode = '';
        }
        if(this.formModel.gpusPerNode) {
          this.formModel.gpusPerNode = '';
        }
        if(this.formModel.ramSize) {
          this.formModel.ramSize = '';
        }
      }
    },
    filterParams(params, method, paramIds) {
      let result = [];
      params.forEach((param) => {
        if(method == 'include' && paramIds.indexOf(param.id) >= 0) {
          result.push(param);
        }
        if(method == 'exclude' && paramIds.indexOf(param.id) < 0) {
          result.push(param);
        }
      });
      return result;
    }
  }
}
</script>
