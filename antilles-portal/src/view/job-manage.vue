<style>
.job-tab {
  margin-bottom: 20px;
}

.job-tab-span {
  display: inline-block;
  width: 120px;
  text-align: left;
}
.job-tab-div {
  margin-top: 20px;
}
.job-manage-hr {
  background: #E9EEF2;
  height: 1.5px;
  width: 100%;
  margin-bottom: 20px;
}
</style>
<template>
	<div class="table-top-manage p-10">
	<div class="job-tab b-w p-20" v-loading="loading">
		<el-row class="">
			<el-col :span="10" justify="left">
        <span class="job-tab-span">{{$t('JobManager.Filter.StatusType')}}</span>
        <el-radio-group id="tid_job-manage-filter-status" v-model="statusTypeLabel">
          <el-radio-button v-for="type in statusTypes" :key="type.type" :label="type.label"></el-radio-button>
        </el-radio-group>
      </el-col>
      <el-col :span="14" justify="left">
        <span class="job-tab-span">{{$t('JobManager.Filter.Submission')}}</span>
        <el-radio-group id="tid_job-manage-filter-submission" v-model="defaultSubmitTime" @change='submitTimeChange'>
          <el-radio-button :label="1">{{$t('JobManager.SubmitTime.Month',{value: 1})}}</el-radio-button>
          <el-radio-button :label="3">{{$t('JobManager.SubmitTime.Month',{value: 3})}}</el-radio-button>
          <el-radio-button :label="6">{{$t('JobManager.SubmitTime.Month',{value: 6})}}</el-radio-button>
          <el-radio-button :label="0">{{$t('JobManager.SubmitTime.All')}}</el-radio-button>
        </el-radio-group>
        </el-col>
    </el-row>
    <el-row class="job-tab-div">
      <el-col :span="10" justify="left">
        <span class="job-tab-span">{{$t('JobManager.Filter.Queue')}}</span>
        <multi-queue-selector id="tid_job-manage-filter-queue" v-model="dataFilter.queue.values" :placeholder="$t('Select.All')"></multi-queue-selector>
      </el-col>
			<el-col :span="14" justify="left" v-if="this.$store.state.auth.access != 'staff'">
        <span class="job-tab-span">{{$t('JobManager.Filter.SubmitUser')}}</span>
        <multi-user-selector id="tid_job-manage-filter-user" bind-property="username" :placeholder="$t('Select.All')" :users-value="[]" :users-type="'username'" :filter-type="'username,usergroup,billinggroup'"  @change="changeValue" :allable="true"></multi-user-selector>
      </el-col>
    </el-row>
  </div>
  <div v-if="isHR" class="job-manage-hr"></div>
  <div style="height: 100%">
    <el-row class="">
      <el-col>
        <composite-table id="tid_job-mamange-table" ref="jobTable" class="table-style"
          :table-data-fetcher="tableDataFetcher"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="10"
          :search-enable="true"
          :search-props="['id', 'name', 'schedulerId']"
          :default-sort="{ prop: 'id', order: 'descending' }"
          :current-page="1"
          :externalFilter='dataFilter'
          @loading-change='loadingChange'
          :auto-refresh="10*1000">
          <ul slot="controller" class="composite-table-controller">
            <li>&nbsp</li>
          </ul>
          <el-table-column prop="id" :label="$t('Job.Id')" sortable="custom" align="center" width="80">
          </el-table-column>
          <el-table-column prop="name" :label="$t('Job.Name')" sortable="custom" align="center" v-if="this.$store.state.auth.access == 'staff'">
            <template slot-scope='scope'>
              <a href="javascript:;" @click="onDetailClick(scope.row)" class="el-button el-button--text el-button--wrap">{{scope.row.name}}</a>
							<!-- el-button type="text" @click="onDetailClick(scope.row)">{{scope.row.name}}</el-button -->
						</template>
          </el-table-column>
          <el-table-column prop="name" :label="$t('Job.Name')" sortable="custom" align="center" v-if="this.$store.state.auth.access != 'staff'">
          </el-table-column>
          <el-table-column prop="schedulerId" :label="$t('Job.SchedulerId')" sortable="custom" align="center" width='160'>
          </el-table-column>
          <el-table-column prop="status" :label="$t('Job.Status')" sortable="custom" align="left" width="150">
            <template slot-scope="scope">
							<job-status-label :status="scope.row.status" :operate-status="scope.row.operateStatus"></job-status-label>
						</template>
          </el-table-column>
          <el-table-column prop="queue" :label="$t('Job.Queue')" sortable="custom" align="center" width="100">
          </el-table-column>
          <el-table-column prop="submitTime" :label="$t('Job.SubmitTime')" sortable="custom" align="center" width='180' :formatter="columnFormatter" v-if="statusType != 'running'">
          </el-table-column>
          <el-table-column prop="waitDuration" :label="$t('Job.WaitDuration')" align="center" width='180' :formatter="columnFormatter" v-if="statusType == 'waiting'">
          </el-table-column>
          <el-table-column prop="beginTime" :label="$t('Job.BeginTime')" sortable="custom" align="center" width='180' :formatter="columnFormatter" v-if="statusType == 'running'">
          </el-table-column>
          <el-table-column prop="runDuration" :label="$t('Job.RunDuration')" align="center" width='180' :formatter="columnFormatter" v-if="statusType == 'running'">
          </el-table-column>
          <el-table-column prop="finishTime" :label="$t('Job.FinishTime')" sortable="custom" align="center" width='180' :formatter="columnFormatter" v-if="statusType == 'finished'">
          </el-table-column>
          <el-table-column prop="submitUser" :label="$t('Job.SubmitUser')" sortable="custom" align="center" width="130" v-if="this.$store.state.auth.access != 'staff'">
          </el-table-column>
          <el-table-column :label="$t('Action')" align='center' width="160" v-if="this.$store.state.auth.access == 'staff' || this.$store.state.auth.featureCodes.indexOf('prc') >= 0">
            <template slot-scope='scope'>
              <el-dropdown trigger="click" class="act" @command="onActionCommand">
                <span class="demonstration">
                  {{$t('Job.Action')}}<i class="el-icon-arrow-down el-icon--right"></i>
                </span>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item :command="{fn:onCancelClick,argument:scope.row}" v-show="isActionAvailable(scope.row, 'cancel')">{{$t('Job.Action.Cancel')}}</el-dropdown-item>
                  <el-dropdown-item :command="{fn:onRerunClick,argument:scope.row}" v-show="isActionAvailable(scope.row, 'rerun')">{{$t('Job.Action.Rerun')}}</el-dropdown-item>
                  <el-dropdown-item :command="{fn:onDeleteClick,argument:scope.row}" v-show="isActionAvailable(scope.row, 'delete')">{{$t('Job.Action.Delete')}}</el-dropdown-item>
                  <el-dropdown-item :command="{fn:onHoldClick,argument:scope.row}" v-show="isActionAvailable(scope.row, 'hold')">{{$t('Job.Action.Hold')}}</el-dropdown-item>
                  <el-dropdown-item :command="{fn:onReleaseClick,argument:scope.row}" v-show="isActionAvailable(scope.row, 'release')">{{$t('Job.Action.Release')}}</el-dropdown-item>
                  <el-dropdown-item :command="{fn:onPauseClick,argument:scope.row}" v-show="isActionAvailable(scope.row, 'pause')">{{$t('Job.Action.Pause')}}</el-dropdown-item>
                  <el-dropdown-item :command="{fn:onResumeClick,argument:scope.row}" v-show="isActionAvailable(scope.row, 'resume')">{{$t('Job.Action.Resume')}}</el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
            </template>
          </el-table-column>
        </composite-table>
        <job-action-dialog id="tid_job-manange-action-dialog" ref="jobActionDialog" />
        <file-manager-dialog id="tid_job-manange-file-dialog" ref="fileManager" />
      </el-col>
    </el-row>
  </div>
</div>
</template>
<script>
import CompositeTable from "../component/composite-table"
import JobService from "../service/job"
import JobActionDialog from '../widget/job-action-dialog'
import MultiUserSelector from '../widget/multi-user-selector'
import MultiQueueSelector from '../widget/multi-queue-selector'
import JobStatusLabel from '../widget/job-status-label'
import FileManagerDialog from '../component/file-manager-dialog'
import Format from '../common/format'
import Collection from '../common/collection'
import Utils from '../common/utils'

export default {
  data() {
    var statusTypes = [{
        type: 'running',
        label: this.$t('JobManager.StatusType.Running'),
        status: JobService.JobWebStatusEnums.running
      },
      {
        type: 'waiting',
        label: this.$t('JobManager.StatusType.Waiting'),
        status: JobService.JobWebStatusEnums.waiting
      },
      {
        type: 'finished',
        label: this.$t('JobManager.StatusType.Finished'),
        status: JobService.JobWebStatusEnums.finished
      }
    ];
    var defaultStatusIndex = 0;
    if(this.$route.params.status) {
      for(var i=0; i<statusTypes.length; i++) {
        if(statusTypes[i].type == this.$route.params.status) {
          defaultStatusIndex = i;
          break;
        }
      }
    }
    return {
      tableDataFetcher: JobService.getJobTableDataFetcher(this.$store.state.auth.access),
      currentUserRole: '',
      statusType: statusTypes[defaultStatusIndex].type,
      statusTypeLabel: statusTypes[defaultStatusIndex].label,
      defaultSubmitTime: 1,
      statusTypes: statusTypes,
      loading: false,
      dataFilter: {
        status: {
          values: statusTypes[defaultStatusIndex].status,
          type: 'in'
        },
        queue: {
          values: [],
          type: 'in'
        },
        submitUser: {
          value_type: 'username',
          values: this.$store.state.auth.access == 'staff' ? [this.$store.state.auth.username] : [],
          type: 'in'
        },
        submitTime: {
          values: [new Date(new Date() - (86400000 * 30)), new Date('2100/1/1')],
          type: 'range'
        }
      }
    }
  },
  components: {
    "composite-table": CompositeTable,
    'job-action-dialog': JobActionDialog,
    'multi-user-selector': MultiUserSelector,
    'multi-queue-selector': MultiQueueSelector,
    'job-status-label': JobStatusLabel,
    'file-manager-dialog': FileManagerDialog
  },
  watch: {
    statusTypeLabel(val, oldVal) {
      for (var i = 0; i < this.statusTypes.length; i++) {
        if (this.statusTypes[i].label == val) {
          this.statusType = this.statusTypes[i].type;
          this.dataFilter.status.values = this.statusTypes[i].status;
        }
      }
    }
  },
  computed: {
    isHR: function () {
      return this.$store.state.auth.access == 'staff' && this.$route.path.indexOf('expert-mode')>=0;
    }
  },
  methods: {
    onDetailClick(job) {
      this.$router.push({ path: '/main/job/' + job.id });
    },
    loadingChange(val) {
      this.loading = val;
    },
    isActionAvailable(job, action) {
      var actions = [];
      var jobActions = JobService.getJobActions(job.operateStatus, job.status, job.type);
      var accessActions = JobService.getJobActionsByAccess(this.$store.state.auth.access);
      jobActions.forEach((jobAction) => {
        accessActions.forEach((accessAction) => {
          if(jobAction == accessAction) {
            actions.push(jobAction);
          }
        });
      });
      return actions.indexOf(action) >= 0;
    },
    onCancelClick(job) {
      this.$refs.jobActionDialog.doCancel(job).then((res) => {
        // Reload table data
        this.$refs.jobTable.fetchTableData(true);
      }, (res) => {
        // Do nothing
      });
    },
    onDeleteClick(job) {
      this.$refs.jobActionDialog.doDelete(job).then((res) => {
        this.$refs.jobTable.fetchTableData(true);
      }, (res) => {
        // Do nothing
      });
    },
    onRerunClick(job) {
      this.$refs.jobActionDialog.doRerun(job).then((res) => {
        this.$refs.jobTable.fetchTableData(true);
      }, (res) => {
        // Do nothing
      });
    },
    onBrowseClick(job) {
      var path = job.workingDirectory.replace(job.workspace, 'MyFolder');
      this.$refs.fileManager.openManager(path);
    },
    onHoldClick(job) {
      this.$refs.jobActionDialog.doHold(job).then((res) => {
        this.$refs.jobTable.fetchTableData(true);
      }, (res) => {
        // Do nothing
      });
    },
    onReleaseClick(job) {
      this.$refs.jobActionDialog.doRelease(job).then((res) => {
        this.$refs.jobTable.fetchTableData(true);
      }, (res) => {
        // Do nothing
      });
    },
    onPauseClick(job) {
      this.$refs.jobActionDialog.doPause(job).then((res) => {
        this.$refs.jobTable.fetchTableData(true);
      }, (res) => {
        // Do nothing
      });
    },
    onResumeClick(job) {
      this.$router.push({ path: '/main/job-template/resume/' + job.id });
    },
    columnFormatter(row, column) {
      if(['submitTime', 'beginTime', 'finishTime'].indexOf(column.property) >= 0) {
        return Format.formatDateTime(row[column.property]);
      }
      if(['waitDuration', 'runDuration'].indexOf(column.property) >= 0) {
        return Format.formatDuration(row[column.property]);
      }
    },
    onActionCommand(command){
      let fn = command.fn;
      let argument = command.argument;
      fn(argument);
    },
    changeValue(data){
      this.dataFilter.submitUser.value_type = data.value_type;
      this.dataFilter.submitUser.values = data.values;
    },
    submitTimeChange(val) {
      var submissionRange = [new Date(0), new Date('2100/1/1')];
      if(val) {
        submissionRange = [new Date(new Date() - (86400000 * 30 * val)), new Date('2100/1/1')]
      }
      this.dataFilter.submitTime.values = submissionRange;
    }
  }
}
</script>
