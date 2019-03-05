<style scoped>
.job-detail-line {
  border-radius: 2px;
  background: #fff;
  padding: 5px 20px;
}

.job-detail-p{
	margin-bottom: 10px;
}

.padding20 {
  padding: 20px;
}

.margin-top20 {
  margin-top: 20px;
}

.margin-bottom20 {
  margin-bottom: 20px;
}

.margin-bottom40 {
  margin-bottom: 40px;
}

.margin-right20 {
  margin-right: 20px;
}

.job-detail-p>p {
  margin-bottom: 10px;
  font-size: 18px;
}

.job-detail-div {
  display: inline-block;
  margin-left: 10px;
}

.job-detail-div>button {
  margin-left: 30px;
}

.job-detail-template {
  margin-bottom: 20px;
  color: #999;
}

.gpus-controlRange {
  display: flex
}
.controlRange {
  width: 100%;
  margin: 0 10px;
}
.controlRangeMin, .controlRangeMax {
  line-height: 36px;
}
.controlRangeMax {
  margin-right: 20px;
}
.ColorInversion {
  padding-top: 8px;
}
.job-detail-tab .gpu-used-label {
  padding-top: 8px;
  margin-left: 10px;
}
.job-detail-tab .gpu-u-inner {
  text-align: center;
  width: 56px;
  height: 20px;
  line-height: 20px;
  background: #f8f8f8;
  border-radius: 4px;
}
.job-detail-tab .gpu-u-pic {
  background: #6bcb01;
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 4px;
  transform: translateY(10%);
}
.job-detail-tab .gpu-u-word {
  display: inline-block;
  font-size: 12px;
  transform: translateY(10%);
  height: 12px;
  color: #999999;
}
.job_type {
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap
}

</style>
<template>
	<div class="p-10">
    <div v-show="!newWindow" class="">
  		<el-row class="job-detail-line padding20 margin-bottom20" v-if="job != null">
  			<el-row class="job-detail-p">
  				<el-col :span="6">
  					<span>{{ job.name }}</span>
  					<div class="job-detail-div">
  						<job-status-label :status="job.status" :operate-status="job.operateStatus"></job-status-label>
  					</div>
  				</el-col>
  				<div style="color: #999">
            <el-col :span="3" align="left"><span>{{ $t("JobDetail.Template") }}</span></el-col>
            <el-col :span="3" align="left"><span>{{ $t("JobDetail.NumberOfCpuCores") }} / {{ $t("JobDetail.NumberOfNodes") }}</span></el-col>
            <el-col :span="3" align="left" v-if='job.numberOfGpus'><span>{{ $t("Job.Gpu") }}</span></el-col>
  					<el-col :span="3" align="left"><span>{{ $t("JobDetail.Queue") }} / {{ $t("Job.SchedulerId") }}</span></el-col>
  					<el-col :span="3" align="left"><span>{{ $t("JobDetail.Submit.Time") }}</span></el-col>
  					<el-col :span="3" align="left" ><span>{{ $t("JobDetail.End.Time") }}</span></el-col>
  				</div>
        </el-row>
    		<el-row>
    			<el-col :span="6"  justify="start">
            <el-button size="small" :title="$t('Job.Action.Browse')"
              @click="onBrowseClick" class="table-icon-button" v-show="isBrowseable">
              <i class="el-erp-browse"></i>
            </el-button>
            <el-button size="small" :title="$t('Job.Action.Cancel')"
              @click="onCancelClick" class="table-icon-button" v-show="isCancelable">
              <i class="el-erp-cancel"></i>
            </el-button>
            <el-button size="small" :title="$t('Job.Action.Rerun')"
              @click="onRerunClick" class="table-icon-button" v-show="isRerunable">
              <i class="el-erp-button_rerun"></i>
            </el-button>
            &nbsp;
    			</el-col>
          <el-col :span="3" align="left" class="job_type">
    				<span :title="getJobDisplayType()">{{ getJobDisplayType() }}</span>
    			</el-col>
          <el-col :span="3" align="left">
            <el-popover
              ref="execPopover"
              placement="bottom"
              :title="$t('JobDetail.ExecHosts.Title')"
              width="200"
              trigger="click"
              :content="formatExecHosts(job.execHosts)">
            </el-popover>
            <el-button type="text" style="padding: 0px" v-popover:execPopover>{{ job.numberOfCpuCores }} / {{ job.numberOfNodes }}</el-button>
          </el-col>
          <el-col :span="3" v-if='job.numberOfGpus' align="left">
            <el-popover
              ref="GpuexecPopover"
              placement="bottom"
              :title="$t('JobDetail.ExecHosts.Title')"
              width="200"
              trigger="click"
              :content="formatExecHosts(job.gpuExecHosts)">
            </el-popover>
            <el-button type="text" style="padding: 0px" v-popover:GpuexecPopover>{{ job.numberOfGpus }}</el-button>
          </el-col>
          <el-col :span="3" align="left">
    				<span>{{ job.queue }} / {{ job.schedulerId }}</span>
    			</el-col>
    			<el-col :span="3" align="left">
    				<span>{{ formatTime(job.submitTime) }}</span>
    			</el-col>
    			<el-col :span="3" align="left">
    				<span v-if="['completed', 'error', 'cancelled', 'createfailed'].indexOf(job.status) > -1">
              {{ formatTime(job.finishTime) }}
            </span>
    			</el-col>
    		</el-row>
      </el-row>
      <el-row class="job-detail-line" v-if="job != null">
        <el-tabs v-model="defaultDisplay" @tab-click='onTabsClick' class="job-detail-tab">
          <el-tab-pane :label="$t('JobDetail.Monitor')" name="monitor" style="padding-left: 10px; padding-right: 10px">
            <log-viewer :workspace="job.workingDirectory"
              :default-file="defaultLogFile"
              :mapping-path="job.workspace"
              ref='logViewer'>
            </log-viewer>
          </el-tab-pane>
          <el-tab-pane :label="$t('JobDetail.Console')" name="console" style="padding-left: 10px; padding-right: 10px">
            <web-shell ref="webShell"></web-shell>
          </el-tab-pane>
          <el-tab-pane v-if='job.jobFilename' :label="$t('JobDetail.JobFile')" name="detail" style="padding-left: 10px; padding-right: 10px">
            <job-file-viewer :fileName="job.jobFilename"
            :mapping-path="job.workspace"
            :workspace="job.workingDirectory">
            </job-file-viewer>
          </el-tab-pane>
          <el-tab-pane :label='$t("Job.Gpu")' name='gpu' v-if='job.numberOfGpus && job.status == "running"'>
            <el-row>
              <el-col :lg="12" :md="12" :sm="24" :xs="24" style="display: flex;">
                <el-radio-group id="tid_job-gpus-type" v-model="selected"  style="margin-left:20px;" @change='onViewTypeChange'>
                  <el-radio-button label="util">{{$t("NodeGpus.Tab.Title.Util")}}</el-radio-button>
                  <el-radio-button label="memory">{{$t("NodeGpus.Tab.Title.Mem")}}</el-radio-button>
                  <el-radio-button label="temperature">{{$t("NodeGpus.Tab.Title.Temp")}}</el-radio-button>
                </el-radio-group>
                <div class="gpu-used-label">
        					<div class="gpu-u-inner">
        						<span class="gpu-u-pic"></span>
        						<span class="gpu-u-word">{{$t('NodePanel.Gpu.Used')}}</span>
        					</div>
        				</div>
              </el-col>
              <el-col :lg="12" :md="12" :sm="24" :xs="24" class="gpus-controlRange" style="padding: 0 20px;">
  							<div class="controlRangeMin">
  								{{$t('NodeGpus.ControlRange.Min', {'unit': controlRangeUnit})}}
  							</div>
  							<div class="controlRange">
  								<el-slider
  									:class="colorInversion?'color-back':'color-just'"
  									v-model="controlRange"
  									@change='onControlRangeChange'
  									range
  									:max="100">
  								</el-slider>
  							</div>
  							<div class="controlRangeMax">
  								{{$t('NodeGpus.ControlRange.Max', {'unit': controlRangeUnit})}}
  							</div>
  							<div class="ColorInversion">
  								<el-checkbox v-model="colorInversion" @change='onColorInversionChange'>{{$t('NodeGpus.Color.Inversion')}}</el-checkbox>
  							</div>
  						</el-col>
            </el-row>
            <gpu-monitor
            ref='gpuMonitor'
            :monitor-nodes='nodes'
            :value-type='selected'
            :page-offset='offset'
            :control-range='controlRange'
            :color-inversion='colorInversion'
            @offset-change='onOffsetChange'>

            </gpu-monitor>
          </el-tab-pane>
        </el-tabs>
      </el-row>
    </div>
    <div v-show="newWindow" class="job-detail-line padding20 margin-bottom20">
      <el-row>
        <el-col :span="24" align="right" >
        </el-col>
      </el-row>
      <el-row>
      </el-row>
    </div>
    <job-action-dialog ref="jobActionDialog" />
    <file-manager-dialog id="tid_job-manange-file-dialog" ref="fileManager" />
  </div>
</template>
<script>
import JobService from "../service/job"
import MonitorService from '../service/monitor-data'
import JobStatusLabel from "../widget/job-status-label"
import JobActionDialog from '../widget/job-action-dialog'
import LogViewer from "../widget/log-viewer"
import GpuMonitor from '../widget/monitor-node-gpus'
import JobFileViewer from "./job/job-file-viewer"
import Format from '../common/format'
import WebShell from '../widget/web-shell'
import FileManagerDialog from '../component/file-manager-dialog'

export default {
  data() {
    return {
      path: '',
      newWindow: false,
      jobId: 0,
      job: null,
      defaultDisplay: 'monitor',
      defaultLogFile: '',
      isInited: false,
      showToolBar: true,
      nodes: [],
      offset: {
        total: 0,
        pageSize: 24,
        currentPage: 1,
      },
      selected: 'util',
      controlRange: this.stringToNumberArr(this.$store.getters['settings/getGpuutil'].split(',')),
      colorInversion: this.$store.getters['settings/getGpuutilColor'],
      controlRangeUnit: '%',
      autoRefreshInterval: 10 * 1000,
      autoRefreshTimerId: 0
    }
  },
  components: {
    "job-status-label": JobStatusLabel,
    "job-action-dialog": JobActionDialog,
    "log-viewer": LogViewer,
    "web-shell": WebShell,
    "gpu-monitor": GpuMonitor,
    'file-manager-dialog': FileManagerDialog,
    'job-file-viewer': JobFileViewer
  },
  mounted() {
    this.jobId = parseInt(this.$route.params.id);
    this.refreshJob();
  },
  beforeDestroy() {
    if(this.autoRefreshTimerId > 0) {
      clearTimeout(this.autoRefreshTimerId);
    }
  },
  watch: {
    '$route.params.id'(val, oldVal) {
      this.jobId = parseInt(val);
      this.refreshJob();
    },
    defaultDisplay(val, oldVal) {
      var self = this;
      if(val == 'monitor') {
        this.$nextTick(() => {
          self.$refs.logViewer.setScrollHeight();
        });
      } else  {
        this.$nextTick(() => {
          self.$refs.webShell.autoResizeTerminalWindows();
        });
      }
    }
  },
  computed: {
    isBrowseable() {
      return JobService.getJobActions(this.job.operateStatus, this.job.status, this.job.type).indexOf('browse') >= 0;
    },
    isCancelable() {
      return JobService.getJobActions(this.job.operateStatus, this.job.status, this.job.type).indexOf('cancel') >= 0;
    },
    isRerunable() {
      return JobService.getJobActions(this.job.operateStatus, this.job.status, this.job.type).indexOf('rerun') >= 0;
    }
  },
  methods: {
    refreshJob() {
      if(this.autoRefreshTimerId > 0) {
				clearTimeout(this.autoRefreshTimerId);
			}
      JobService.getJobById(this.jobId).then((res) => {
        var job = res;
        this.job = job;

        if(job.type == 'vnc' && job.schedulerId) {
          this.defaultLogFile = job.workingDirectory + '/vnc_' + job.schedulerId + '.log';
        }
        else if(job.outputFilename && job.workingDirectory && job.workspace) {
          this.defaultLogFile = job.outputFilename.replace(job.workspace, 'MyFolder');
        }
        else if(job.type != 'general' && job.type != 'cmd' && job.type != 'file')
        {
          this.defaultLogFile = job.workingDirectory + '/' + job.name + '-' + job.id + '.out';
        }

        if(this.defaultDisplay == 'gpu' && this.job.status != 'running') {
          this.defaultDisplay = 'monitor'
        }
        if(this.job.numberOfGpus>0 && this.job.status == 'running') {
          this.getGpuMonitor();
        }
        if(this.autoRefreshInterval > 0) {
          let self = this;
          this.autoRefreshTimerId = setTimeout(self.refreshJob, this.autoRefreshInterval);
        }
      }, (res) => {
        this.$message.error(res);
      });

    },
    getGpuMonitor() {
      MonitorService.getNodeGpuDataByJob(this.job.id, this.selected, this.offset).then((res) => {
        this.nodes = res.nodesGpus;
        var offset = {
          total: res.total,
          pageSize: res.pageSize,
          currentPage: res.currentPage,
        }
        this.offset = offset;
      })
    },
    formatTime(time) {
      return Format.formatDateTime(time);
    },
    onCancelClick() {
      this.$refs.jobActionDialog.doCancel(this.job).then((res) => {
        this.refreshJob();
      }, (res) => {
        // Do nothing
      });
    },
    onBrowseClick(job) {
      var path = this.job.workingDirectory.replace(this.job.workspace, 'MyFolder');
      this.$refs.fileManager.openManager(path);
    },
    onRerunClick() {
      this.$refs.jobActionDialog.doRerun(this.job).then((res) => {
        this.$router.push({ path: '/main/job/' + res.id });
      }, (res) => {
        // Do nothing
      });
    },
    onClickClose() {
      this.newWindow = false
    },
    onTabsClick() {
      if(this.defaultDisplay == 'gpu') {
        this.$refs.gpuMonitor.onResize();
      }
    },
    showNewWindow(path) {
      this.path = path
      this.newWindow = true
    },
    formatExecHosts(val) {
      if(val == '') {
        return '-';
      }
      return val;
    },
    onControlRangeChange(val) {
      if(val) {
        this.$store.dispatch(`settings/setGpu${this.selected}`, val.join())
      }
    },
    onColorInversionChange(val) {
      this.$store.dispatch(`settings/setGpu${this.selected}Color`, this.colorInversion)
    },
    onOffsetChange(offset) {
      this.offset = offset;
      this.getGpuMonitor();
    },
    onViewTypeChange(val) {
      this.controlRangeUnit = val == 'temperature'?'℃':'%';
      this.controlRange = this.stringToNumberArr(this.$store.getters[`settings/getGpu${val}`].split(','));
      this.colorInversion = this.$store.getters[`settings/getGpu${val}Color`];
      this.getGpuMonitor();
    },
    stringToNumberArr(val) {
      var arr = [];
      val.forEach((str) => {
        arr.push(Number(str));
      })
      return arr;
    },
    getJobDisplayType() {
      if(this.job.type == "file" && this.job.req && this.job.req.params.template_id
      && isNaN(this.job.req.params.template_id)) {
        return this.job.req.params.template_id;
      } else {
        return this.job.type;
      }
    }

  }
}
</script>
