<style scoped>
	.status {
		border-radius: 4px;
	  color: #fff;
	  font-size: 12px;
		color: white;
		display: inline-block;
		width: 16px;
		height: 16px;
		vertical-align: middle;
	}
	.on {
		background-color: #45CB84;
	}
	.off {
		background-color: #999999;
	}
</style>
<template>
<div class="height--100 p-10">
	<div class="table-style">
		<composite-table id="tid_alarm-policy-table" ref="alarmPolicyTable"
			:table-data-fetcher="tableDataFetcher"
			:default-sort="{ prop: 'id', order: 'ascending'	}"
			:search-enable="true"
			:search-props="['id', 'name']"
			:current-page="1"
			:page-sizes="[10, 20, 40, 50]"
			:page-size="10"
			:total="0">
			<ul slot="controller" class="composite-table-controller">
				<el-button id="tid_alarm-policy-create" type="primary" @click="onCreateClick">{{$t('Alarm.Policy.Button.Add')}}</el-button>
			</ul>
			<el-table-column
	      prop="id"
	      :label="$t('Alarm.Policy.Id')"
	      sortable="custom"
	     ></el-table-column>
			<el-table-column
	      prop="name"
	      :label="$t('Alarm.Policy.Name')"
	      sortable="custom"
				align="center"
	      ></el-table-column>

			<el-table-column
		  prop="level"
	      :label="$t('Alarm.Policy.Level')"
	      sortable="custom"
				align="left"
	      >
				<template slot-scope="scope">
					<alarm-table-level
						alarm-level-size="normal"
						:level='scope.row.level'></alarm-table-level>
				</template>
			</el-table-column>
			<el-table-column
			prop="status"
	      :label="$t('Alarm.Policy.Status')"
	      sortable="custom"
				align="left"
	      >
				<template slot-scope="scope">
					<span v-if="scope.row.status">
						<span class="status on"></span><span>&nbsp;ON</span>
					</span>
					<span v-else>
						<span class="status off"></span><span>&nbsp;OFF</span>
					</span>
				</template>
			</el-table-column>

			<el-table-column
				:label="$t('Alarm.Policy.Operation')"
				align='center'>
				<template slot-scope="scope">
					<el-dropdown trigger="click" class="act" @command="onActionCommand">
						<span class="demonstration">
							{{$t('Job.Action')}}<i class="el-icon-arrow-down el-icon--right"></i>
						</span>
						<el-dropdown-menu slot="dropdown">
							<el-dropdown-item :command="{fn:onEditClick,argument:scope.row}">{{$t('Alarm.Policy.Button.Edit')}}</el-dropdown-item>
							<el-dropdown-item :command="{fn:onDeleteClick,argument:scope.row}">{{$t('Alarm.Policy.Button.Delete')}}</el-dropdown-item>
						</el-dropdown-menu>
					</el-dropdown>
				</template>
			</el-table-column>
		</composite-table>
		<alarm-policy-dialog id="tid_alarm-policy-dialog" ref="AlarmPolicyDialog" />
	</div>
</div>
</template>
<script>
	import CompositeTable from '../component/composite-table'
	import AlarmPolicyService from '../service/alarm-policy'
	import Format from '../common/format'
	import AlarmPolicyDialog from './alarm-policy-manage/alarm-policy-dialog'
	import AlarmTablelevel from '../widget/alarm-policy-level-label.vue'

	export default {
		components: {
			'composite-table': CompositeTable,
			'alarm-policy-dialog': AlarmPolicyDialog,
			'alarm-table-level': AlarmTablelevel
		},
		data(){
			return {
				tableDataFetcher: AlarmPolicyService.getAlarmPolicyTableDataFetcher()
			}
		},
		methods:{
			onCreateClick() {
				this.$refs.AlarmPolicyDialog.doCreate().then((res) => {
					// Reload table data
					this.$refs.alarmPolicyTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onEditClick(row){
				this.$refs.AlarmPolicyDialog.doEdit(row.id).then((res) => {
					// Reload table data
					this.$refs.alarmPolicyTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onDeleteClick(row){
				this.$refs.AlarmPolicyDialog.doDelete(row.id).then((res) => {
					// Reload table data
					this.$refs.alarmPolicyTable.fetchTableData(true);
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
