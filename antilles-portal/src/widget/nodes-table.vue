<style>
.node-table-hostname {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}
.el-dropdown__caret-button{line-height: 20px;font-size: 12px;}
</style>
<template>
  <div class="table-style">
      <composite-table id="tid_nodes-table"
      ref="nodesTable"
      :table-data-fetcher="tableDataFetcher"
      :default-sort="{ prop: 'hostname', order: 'ascending' }"
      :selection-enable="true"
      :search-enable="true"
      :search-props="['hostname', 'bmcIP', 'osIP']"
      :current-page="1"
      :page-sizes="[10, 20, 40, 50]"
      :page-size="10"
      :total="0"
      :external-filter="nodeExternalFilter"
      :auto-refresh="30*1000"
      @selection-change="onTableSelectionChange">
      <div slot="controller" class="composite-table-controller">
          <!-- <el-button id="nodes-multi-power-on"  @click="onMultiPowerOnClick()">{{$t("Node.Action.PowerOn")}}</el-button> -->
          <el-dropdown id="tid_nodes-multi-power-on" style="margin-right: 10px;"
            @command="onMultiPowerOnCommand">
            <el-button :disabled="hasNoSelectedNode">
              {{$t("Node.Action.PowerOn")}}
            </el-button>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item :command="{nextDevice: null}">{{$t('Node.Action.PowerOn')}}</el-dropdown-item>
              <el-dropdown-item :command="{nextDevice: 'setup'}">{{$t('Node.Action.PowerOn.Setup')}}</el-dropdown-item>
              <el-dropdown-item :command="{nextDevice: 'network'}">{{$t('Node.Action.PowerOn.Network')}}</el-dropdown-item>
              <el-dropdown-item :command="{nextDevice: 'cd'}">{{$t('Node.Action.PowerOn.CD')}}</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>

          <el-button id="tid_nodes-multi-power-off" :disabled="hasNoSelectedNode" @click="onMultiPowerOffClick()">{{$t("Node.Action.PowerOff")}}</el-button>
          <el-button id="tid_nodes-multi-console" :disabled="hasNoSelectedNode" @click="onMultiConsoleClick()">{{$t("Node.RemoteAccess.Console")}}</el-button>
          <el-button id="tid_nodes-multi-shell" :disabled="hasNoSelectedNode" @click="onMultiShellClick()">{{$t("Node.RemoteAccess.Shell")}}</el-button>
      </div>
      <el-table-column
        prop="hostname"
        :label="$t('Node.HostName')"
        sortable="custom"
        width="120">
        <template slot-scope="scope">
          <el-button class="node-table-hostname" type="text" :title='scope.row.hostname' @click="onDetailClick(scope.row)">{{scope.row.hostname}}</el-button>
        </template>
      </el-table-column>
      <el-table-column
        prop="status"
        :label="$t('Node.Status')"
        sortable="custom"
        align='left'
        width="120">
        <template slot-scope="scope">
          <node-status-label :status="scope.row.status"/>
        </template>
      </el-table-column>
      <el-table-column
          prop="powerStatus"
          :label="$t('Node.Power')"
          sortable="custom"
          align='left'
          width="100">
        <template slot-scope="scope">
          <node-power-status-label :power-status="scope.row.powerStatus"/>
        </template>
      </el-table-column>
      <el-table-column
          prop="type"
          :label="$t('Node.Type')"
          sortable="custom"
          align='center'
          width="120">
      </el-table-column>
      <el-table-column
          prop="bmcIP"
          :label="$t('Node.IP.BMC')"
          sortable="custom"
          align='center'
          width="150">
          <template slot-scope="scope">
            <el-button type="text" @click="onBMCClick(scope.row)">{{scope.row.bmcIP}}</el-button>
          </template>
      </el-table-column>
      <el-table-column
          prop="osIP"
          :label="$t('Node.IP.OS')"
          sortable="custom"
          align='center'
          width="150">
      </el-table-column>
      <el-table-column
          prop="hardware"
          :label="$t('Node.Hardware')"
          align='center'>
          <template slot-scope="scope">
            <el-popover
              placement="left"
              width="150"
              trigger="hover">
              <p>{{showHardware(scope.row, 'cpuTotal')}}</p>
              <p>{{showHardware(scope.row, 'ramTotal')}}</p>
              <p>{{showHardware(scope.row, 'diskTotal')}}</p>
              <p v-if='scope.row.gpus.length>0'>{{showHardware(scope.row, 'gpus')}}</p>
              <span slot="reference">{{columnFormatter(scope.row, 'hardware')}}</span>
            </el-popover>
          </template>
      </el-table-column>
      <el-table-column
          prop="groups"
          align='center'
          :label="$t('Node.CustomGroup')">
      </el-table-column>
      <el-table-column
          :label="$t('Node.Operation')"
          align='center'
          width="140">
        <template slot-scope="scope">
          <el-dropdown trigger="click" class="act" @command="onActionCommand">
						<span class="demonstration">
							{{$t('Job.Action')}}<i class="el-icon-arrow-down el-icon--right"></i>
						</span>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item :command="{fn:onPowerOffClick,argument:scope.row}" v-if="scope.row.powerStatus == 'on'">{{$t('Node.Action.PowerOff')}}</el-dropdown-item>
                <el-dropdown-item :command="{fn:onConsoleClick,argument:scope.row}">{{$t('Node.RemoteAccess.Console')}}</el-dropdown-item>
                <el-dropdown-item :command="{fn:onShellClick,argument:scope.row}">{{$t('Node.RemoteAccess.Shell')}}</el-dropdown-item>
                <el-dropdown-item :command="{fn:onPowerOnCommand,argument:{nextDevice: null, node: scope.row}}">{{$t('Node.Action.PowerOn')}}</el-dropdown-item>
                <el-dropdown-item :command="{fn:onPowerOnCommand,argument:{nextDevice: 'setup', node: scope.row}}">{{$t('Node.Action.PowerOn.Setup')}}</el-dropdown-item>
                <el-dropdown-item :command="{fn:onPowerOnCommand,argument:{nextDevice: 'network', node: scope.row}}">{{$t('Node.Action.PowerOn.Network')}}</el-dropdown-item>
                <el-dropdown-item :command="{fn:onPowerOnCommand,argument:{nextDevice: 'cd', node: scope.row}}">{{$t('Node.Action.PowerOn.CD')}}</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
        </template>
      </el-table-column>
    </composite-table>
    <node-detail-dialog id="tid_node-detail-dialog" ref="detailDialog"></node-detail-dialog>
    <node-action-dialog id="tid_node-action-dialog" ref="actionDialog"></node-action-dialog>
    <web-terminal ref="webTerminal" :popup="true"></web-terminal>
  </div>
</template>
<script>
  import CompositeTable from '../component/composite-table'
  import NodeService from '../service/node'
  import WebTerminal from './web-terminal'
  import NodeStatusLabel from './node-status-label.vue'
  import NodePowerStatusLabel from './node-power-status-label'
  import NodeDetailDialog from './nodes-table/node-detail-dialog'
  import NodeActionDialog from './nodes-table/node-action-dialog'
  import Format from '../common/format'

  export default {
    data() {
      return {
        tableDataFetcher: NodeService.getNodesTableDataFetcher(),
        hasNoSelectedNode: true,
        selectedNodeId:[],
        terminalData: []
      }
    },
    props:[
      "nodeExternalFilter"
    ],
    components: {
      'composite-table': CompositeTable,
      'node-status-label': NodeStatusLabel,
      'node-power-status-label': NodePowerStatusLabel,
      'node-detail-dialog': NodeDetailDialog,
      'node-action-dialog': NodeActionDialog,
      'web-terminal': WebTerminal
    },
    methods: {
      showHardware(row, type) {
        if(type == 'cpuTotal') {
          return this.$t('Node.Hardware.CPU', {value: row['cpuTotal']});
        } else if(type == 'ramTotal') {
          return this.$t('Node.Hardware.Memory', {value: Format.formatByteSize(row['ramTotal'])});
        } else if(type == 'diskTotal') {
          return this.$t('Node.Hardware.Storage', {value: Format.formatByteSize(row['diskTotal'])});
        } else if(type == 'gpus') {
          return this.$t('Node.Hardware.GPU', {value: row['gpus'].length});
        }
      },
      columnFormatter(row, column) {
				if(column == 'hardware') {
					var items = [
            row['cpuTotal'] + ' ' + this.$t('Unit.CPU'),
            Format.formatByteSize(row['ramTotal'])
          ];
          if(row['gpus'] && row['gpus'].length > 0) {
            items.push(row['gpus'].length + ' ' + this.$t('Node.Table.Unit.GPUs'));
          }
          return items.join(' / ');
				}
      },
      onActionCommand(command){
        let fn = command.fn;
        let argument = command.argument;
        fn(argument);
      },
      onPowerOnCommand(command) {
        this.$refs.actionDialog.doPowerOn(command.node, command.nextDevice).then((res) => {
          // Reload table data
					this.$refs.nodesTable.fetchTableData(false);
				}, (res) => {
					// Do nothing
				});
      },
      onMultiPowerOnCommand(command) {
        this.$refs.actionDialog.doMultiPowerOn(this.terminalData, this.selectedNodeId, command.nextDevice).then((res) => {
          // Reload table data
          this.$refs.nodesTable.fetchTableData(false);
        }, (res) => {
          // Do nothing
        });
      },
      onPowerOffClick(node) {
        this.$refs.actionDialog.doPowerOff(node).then((res) => {
          // Reload table data
					this.$refs.nodesTable.fetchTableData(false);
				}, (res) => {
					// Do nothing
				});
      },
      onMultiPowerOffClick() {
        this.$refs.actionDialog.doMultiPowerOff(this.terminalData, this.selectedNodeId).then((res) => {
          // Reload table data
          this.$refs.nodesTable.fetchTableData(false);
        }, (res) => {
          // Do nothing
        });
      },
      onConsoleClick(node) {
        this.$refs.webTerminal.popupConsole(node.hostname);
      },
      onMultiConsoleClick() {
        this.terminalData.forEach((node) => {
          this.$refs.webTerminal.popupConsole(node.hostname);
        });
      },
      onShellClick(node) {
        this.$refs.webTerminal.popupShell(node.hostname);
      },
      onMultiShellClick() {
        this.terminalData.forEach((node) => {
          this.$refs.webTerminal.popupShell(node.hostname);
        });
      },
      onBMCClick(node) {
        window.open("https://"+node.bmcIP);
      },
      onTableSelectionChange(selection) {
        let _this = this;
        _this.terminalData.length = 0;
        _this.selectedNodeId = [];
        selection.forEach((node, index) => {
          _this.selectedNodeId.push(node.id);
          _this.terminalData.push({
            hostname: node.hostname,
            number: index
          });
        });
        if(_this.selectedNodeId.length > 0){
          _this.hasNoSelectedNode = false;
        } else {
          _this.hasNoSelectedNode = true;
        }
      },
      onDetailClick(node) {
        this.$refs.detailDialog.showDetail(node.id);
      }
    }
  }
</script>
