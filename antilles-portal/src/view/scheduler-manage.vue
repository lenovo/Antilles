<style scoped>
.highblue{
	color:#38AAF2;
	overflow: hidden;
	text-overflow:ellipsis;
	white-space: nowrap;
}
</style>
<template>
<div class="height--100 p-10">
	<div class="table-style">
		<!-- <h1>Scheduler View</h1> -->
		<composite-table id="scheduler_view-table"
			ref="schedulerViewTable"
			:table-data-fetcher="tableDataFetcher"
			:default-sort="{ prop: 'queueName', order: 'ascending'	}"
			:search-enable="true"
			:search-props="['queueName','queueState','priority','isDefault','userGroups','nodes']"
			:current-page="1"
			:page-sizes="[10, 20, 40, 50]"
			:page-size="10"
			:auto-refresh="30*1000"
			:total="0">
			<ul slot="controller">
				<el-button type="primary" @click="onCreateClick" class="">{{$t('Scheduler.Action.Create')}}</el-button>
				<el-button type="primary" @click="setNodesState" class="">{{$t('Scheduler.Action.SetNodesState')}}</el-button>
			</ul>
		  <el-table-column
	      prop="queueName"
	      :label="$t('Scheduler.Table.Title.QueueName')"
	      sortable="custom"
		    align="center"
	      width="">
	    </el-table-column>
		  <el-table-column
	      prop="queueState"
	      :label="$t('Scheduler.Table.Title.QueueState')"
	      sortable="custom"
				align="center"
	      width="180">
	    </el-table-column>
			<el-table-column
				prop="priority"
				:label="$t('Scheduler.Table.Title.Priority')"
				sortable="custom"
				align="center"
				width="180">
			</el-table-column>
			<el-table-column
				prop="isDefault"
				:label="$t('Scheduler.Table.Title.Default')"
				sortable="custom"
				align="center"
				width="180">
			</el-table-column>
			<el-table-column
				prop="userGroups"
				:label="$t('Scheduler.Table.Title.UserGroups')"
				sortable="custom"
				align="center"
				width="180">
			</el-table-column>
			<el-table-column
				prop="nodes"
				:label="$t('Scheduler.Table.Title.Nodes')"
				sortable="custom"
				align="center"
				width="">
				<template slot-scope="scope">
					<span @click="showNodesDetail(scope.row)" class="highblue" style="cursor:pointer">{{scope.row.nodes}}</span>
				</template>
			</el-table-column>
			<el-table-column
				:label="$t('Action')"
				align='center'
				width="200">
				<template slot-scope="scope">
					<el-dropdown trigger="click" class="act" @command="onActionCommand">
            <span class="demonstration">
              {{$t('Job.Action')}}<i class="el-icon-arrow-down el-icon--right"></i>
            </span>
						<el-dropdown-menu slot="dropdown">
							<el-dropdown-item :command="{fn:onEditClick,argument:scope.row}" >{{$t('Scheduler.Action.Edit')}}</el-dropdown-item>
							<el-dropdown-item :command="{fn:setQueueState,argument:scope.row}" >{{$t('Scheduler.Action.SetQueueState')}}</el-dropdown-item>
							<el-dropdown-item :command="{fn:onDeleteClick,argument:scope.row}" >{{$t('Scheduler.Action.Delete')}}</el-dropdown-item>
						</el-dropdown-menu>
					</el-dropdown>
				</template>
			</el-table-column>
		</composite-table>
		<queues-dialog ref="queuesDialog"/>
		<nodes-detail-dialog ref="nodesDetailDialog"/>
		<set-queues-state-dialog ref="setQueuesStateDialog"/>
		<set-nodes-state-dialog ref="setNodesStateDialog"/>
	</div>
</div>
</template>
<script>
	import CompositeTable from '../component/composite-table'
	import SchedulerService from '../service/scheduler'
	import queuesDialog from './scheduler-manage/queues-dialog'
	import nodesDetailDialog from './scheduler-manage/nodes-detail-dialog'
	import setQueuesStateDialog from './scheduler-manage/set-queues-state-dialog'
	import setNodesStateDialog from './scheduler-manage/set-nodes-state-dialog'
	import ValidRoleFactory from '../common/valid-role-factory'

	export default {
		data() {
			return {
        tableDataFetcher: SchedulerService.getSchedulerTableDataFetcher()
      }
		},
		components: {
			'composite-table': CompositeTable,
			'queues-dialog': queuesDialog,
			'nodes-detail-dialog': nodesDetailDialog,
			'set-queues-state-dialog': setQueuesStateDialog,
			'set-nodes-state-dialog': setNodesStateDialog
		},
    methods: {
			onCreateClick() {
				this.$refs.queuesDialog.doCreate().then((res) => {
					// Reload table data
					this.$refs.schedulerViewTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onEditClick(queue) {
				this.$refs.queuesDialog.doEdit(queue).then((res) => {
					// Reload table data
					this.$refs.schedulerViewTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onDeleteClick(queue) {
				this.$refs.queuesDialog.doDelete(queue).then((res) => {
					// Reload table data
					this.$refs.schedulerViewTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			showNodesDetail(queue) {
				this.$refs.nodesDetailDialog.showNodes(queue).then((res) => {
					// Reload table data
					this.$refs.schedulerViewTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			setQueueState(queue) {
				this.$refs.setQueuesStateDialog.setQueueStatus(queue).then((res) => {
					// Reload table data
					this.$refs.schedulerViewTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			setNodesState() {
				var queue={queueName:'test'}
				this.$refs.setNodesStateDialog.setNodesStatus(queue).then((res) => {
					// Reload table data
					this.$refs.schedulerViewTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
      onActionCommand(command){
        let fn = command.fn;
				let argument = command.argument;
        fn(argument);
      }
		}
	}
</script>
