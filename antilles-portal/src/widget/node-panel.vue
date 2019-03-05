<style scoped>
.border-1px {
  border: 1px solid #eee;
}
.node-panel-top {
  font-size: 16px;
  margin-bottom: 20px;
}
.actte{height: 20px;}
</style>
<template>
<div id="tid_node-panel" v-if="innerNode != null">
  <el-row class="node-panel-top">
    <el-col :span="12">
      {{innerNode.hostname}}
    </el-col>
    <el-col :span="12" align="right">
      <node-status-label id="tid_node-panel-status" :status="innerNode.status"></node-status-label>
      <alarm-policy-level-label id="tid_node-panel-alarm-level" :level="innerNode.alarmPolicyLevel"></alarm-policy-level-label>

      <el-dropdown trigger="click" class="act actte" @command="onActionCommand">
        <span class="demonstration">
          {{$t('Job.Action')}}<i class="el-icon-arrow-down el-icon--right"></i>
        </span>
        <el-dropdown-menu slot="dropdown">
          <el-dropdown-item id="tid_node-panel-power-on" v-if="innerNode.powerStatus == 'off'" :command="{fn:onPowerOnClick,argument:''}">{{$t('Node.Action.PowerOn')}}</el-dropdown-item>
          <el-dropdown-item id="tid_node-panel-power-off" v-if="innerNode.powerStatus == 'on'" :command="{fn:onPowerOffClick,argument:''}">{{$t('Node.Action.PowerOff')}}</el-dropdown-item>
          <el-dropdown-item id="tid_node-panel-console" :command="{fn:onConsoleClick,argument:''}">{{$t('Node.RemoteAccess.Console')}}</el-dropdown-item>
          <el-dropdown-item id="tid_node-panel-Shell" :command="{fn:onShellClick,argument:''}">{{$t('Node.RemoteAccess.Shell')}}</el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
    </el-col>
  </el-row>
  <el-row>
    <el-col :span="24">
      <div class="border-1px">
        <node-hardware id="tid_node-panel-hardware" :node="innerNode"></node-hardware>
      </div>
    </el-col>
  </el-row>
  <el-row>
    <el-col :span="24">
      <el-tabs id="tid_node-panel-tabs" v-model="nodeMonitorTab">
        <el-tab-pane :label="$t('NodePanel.Monitor')" name="nodeMonitorMonitor">
          <node-monitor id="tid_node-panel-monitor" :node-id="innerNode.id" :node="innerNode" ref="nodeMonitorMonitor"></node-monitor>
        </el-tab-pane>
        <el-tab-pane :label="$t('NodePanel.Gpu')" name="nodeMonitorGpu" v-if="innerNode.gpus.length>0">
          <node-gpu id="tid_node-panel-gpu" :node="innerNode" ref="nodeMonitorGpu"></node-gpu>
        </el-tab-pane>
        <el-tab-pane :label="$t('NodePanel.Alarm')" name="nodeMonitorAlarm">
          <node-alarm id="tid_node-panel-alarm" :node="innerNode"></node-alarm>
        </el-tab-pane>
        <el-tab-pane :label="$t('NodePanel.Job')" name="nodeMonitorJob">
          <node-job id="tid_node-panel-job" :node-id="innerNode.id" :is-gpus='Boolean(innerNode.gpus.length)'></node-job>
        </el-tab-pane>
        <el-tab-pane :label="$t('NodePanel.Information')" name="nodeMonitorInfo">
          <node-information id="tid_node-panel-information" :node="innerNode"></node-information>
        </el-tab-pane>
      </el-tabs>
    </el-col>
  </el-row>
  <node-action-dialog id="tid_node-panel-action-dialog" ref="actionDialog"></node-action-dialog>
  <web-terminal ref="webTerminal"></web-terminal>
</div>
</template>
<script>
import NodeHardware from './node-panel/node-hardware'
import NodeStatusLabel from './node-status-label'
import AlarmPolicyLevelLabel from './alarm-policy-level-label'
import NodeMonitor from './node-panel/node-monitor'
import NodeGpu from './node-panel/node-gpu'
import NodeAlarm from './node-panel/node-alarm'
import NodeJob from './node-panel/node-job'
import NodeInformation from './node-panel/node-information'
import NodeService from '../service/node'
import NodeDetailDialog from './nodes-table/node-detail-dialog'
import NodeActionDialog from './nodes-table/node-action-dialog'
import WebTerminal from './web-terminal'

export default {
  data() {
    return {
      innerNode: null,
      innerNodeId: 0,
      interval: 1000*30,
      nodeMonitorTab: 'nodeMonitorMonitor',
      timerId: 0
    }
  },
  components: {
    'node-hardware': NodeHardware,
    'node-status-label': NodeStatusLabel,
    'alarm-policy-level-label': AlarmPolicyLevelLabel,
    'node-monitor': NodeMonitor,
    'node-gpu': NodeGpu,
    'node-alarm': NodeAlarm,
    'node-job': NodeJob,
    'node-information': NodeInformation,
    'node-detail-dialog': NodeDetailDialog,
    'node-action-dialog': NodeActionDialog,
    'web-terminal': WebTerminal
  },
  props: [
    'nodeId'
  ],
  watch: {
    nodeId(val, oldVal) {
      this.innerNodeId = val;
      this.innerNode = null;
      if (this.timerId != 0) {
        clearTimeout(this.timerId)
      }

      this.refresh();
    },
    nodeMonitorTab(val, oldVal) {
      if (val == 'nodeMonitorMonitor') {
        this.$nextTick(() => {
          this.$refs.nodeMonitorMonitor.resizeChart()
        })
      }else if (val == 'nodeMonitorGpu') {
        this.$nextTick(() => {
          this.$refs.nodeMonitorGpu.resizeChart()

        })
      }
    }
  },
  mounted() {
    this.innerNodeId = this.nodeId;
    this.refresh();
  },
  beforeDestroy() {
    this.innerNodeId = 0;
  },
  methods: {
    refresh() {
      if (this.innerNodeId > 0 ) {
        NodeService.getNodeById(this.innerNodeId).then((res) => {
          if(this.innerNodeId == res.id) {
            this.innerNode = res;
            if (this.nodeMonitorTab == 'nodeMonitorGpu' && this.innerNode.gpus.length<=0) {
              this.nodeMonitorTab = 'nodeMonitorMonitor'
            }
            let self = this;
            this.timerId = setTimeout(() => {
              self.refresh();
            }, this.interval);
          }
        }, (res) => {
            this.$message.error(res);
        });
      }
    },
    onPowerOnClick() {
      this.$refs.actionDialog.doPowerOn(this.innerNode).then((res) => {
        // Reload table data
        this.$refs.nodesTable.fetchTableData(false);
      }, (res) => {
        // Do nothing
      });
    },
    onPowerOffClick() {
      this.$refs.actionDialog.doPowerOff(this.innerNode).then((res) => {
        // Reload table data
        this.$refs.nodesTable.fetchTableData(false);
      }, (res) => {
        // Do nothing
      });
    },
    onConsoleClick() {
      this.$refs.webTerminal.popupConsole(this.innerNode.hostname);
    },
    onShellClick() {
      this.$refs.webTerminal.popupShell(this.innerNode.hostname);
    },
    onActionCommand(command){
      let fn = command.fn;
      let argument = command.argument;
      fn(argument);
    }
  }
}
</script>
