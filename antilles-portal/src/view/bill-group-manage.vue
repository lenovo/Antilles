<style>
</style>
<template>
<div class="height--100 p-10">
	<div class="table-style">
		<!-- <h1>Bill Group Manage</h1> -->
		<composite-table id="tid_billgroup-table"
			ref="billGroupTable"
			:table-data-fetcher="tableDataFetcher"
			:default-sort="{ prop: 'id', order: 'ascending'	}"
			:search-enable="true"
			:search-props="['name', 'description']"
			:current-page="1"
			:page-sizes="[10, 20, 40, 50]"
			:page-size="10"
			:total="0">
			<ul slot="controller">
				<el-button id="tid_billgroup-create" type="primary" @click="onCreateClick">{{$t('BillGroup.Action.Create')}}</el-button>
			</ul>
		  <el-table-column
	      prop="id"
	      :label="$t('BillGroup.Id')"
	      sortable="custom"
		  align="center"
	      width="100">
	    </el-table-column>
		  <el-table-column
	      prop="name"
	      :label="$t('BillGroup.Name')"
	      sortable="custom"
				align="center"
	      width="200">
	    </el-table-column>
			<el-table-column
				prop="chargeRate"
				:label="$t('BillGroup.ChargeRate')"
				sortable="custom"
				align="right"
				width="120">
			</el-table-column>
			<el-table-column
				prop="totalComputingTime"
				:label="$t('BillGroup.TotalComputingTime.WithUnit')"
				sortable="custom"
				align="right"
				width="180"
				:formatter="columnFormatter">
			</el-table-column>
			<el-table-column
				prop="accountConsumed"
				:label="$t('BillGroup.AccountConsumed')"
				sortable="custom"
				align="right"
				width="180"
				:formatter="columnFormatter">
			</el-table-column>
			<el-table-column
				prop="accountBalance"
				:label="$t('BillGroup.AccountBalance')"
				sortable="custom"
				align="right"
				width="180"
				:formatter="columnFormatter">
			</el-table-column>
			<el-table-column
	      prop="description"
	      :label="$t('BillGroup.Description')"
				min-width='100'>
	    </el-table-column>
			<el-table-column
				:label="$t('Action')"
				align='center'
				width="120">
				<template slot-scope="scope">
					<el-dropdown trigger="click" class="act" @command="onActionCommand">
            <span class="demonstration">
              {{$t('Job.Action')}}<i class="el-icon-arrow-down el-icon--right"></i>
            </span>
						<el-dropdown-menu slot="dropdown">
							<el-dropdown-item :command="{fn:onEditClick,argument:scope.row}" :disabled="scope.row.accountStatus == 'operating'">{{$t('Action.Edit')}}</el-dropdown-item>
							<el-dropdown-item :command="{fn:onAccountOperateClick,argument:scope.row}" :disabled="scope.row.accountStatus == 'operating'">{{$t('Action.Accounting')}}</el-dropdown-item>
							<el-dropdown-item :command="{fn:onDeleteClick,argument:scope.row}" :disabled="scope.row.accountStatus == 'operating'">{{$t('Action.Delete')}}</el-dropdown-item>
						</el-dropdown-menu>
					</el-dropdown>
				</template>
			</el-table-column>
		</composite-table>
		<bill-group-dialog id="tid_billgroup-dialog" ref="billGroupDialog" />
		<account-operate-dialog id="tid_billgroup-operate-dialog" ref="accountOperateDialog" />
	</div>
</div>
</template>
<script>
	import CompositeTable from '../component/composite-table'
	import BillGroupService from '../service/bill-group'
	import Format from '../common/format'
	import BillGroupDialog from './bill-group-manage/bill-group-dialog'
	import AccountOperateDialog from './bill-group-manage/account-operate-dialog'

	export default {
		data() {
			return {
        tableDataFetcher: BillGroupService.getBillGroupsTableDataFetcher()
      }
		},
		components: {
			'composite-table': CompositeTable,
			'bill-group-dialog': BillGroupDialog,
			'account-operate-dialog': AccountOperateDialog
		},
    methods: {
      columnFormatter(row, column) {
				if(column.property=='numberOfMembers') {
					return Format.formatCount(row['numberOfMembers']);
				}
				if(column.property=='accountBalance') {
					return Format.formatMoney(row['accountBalance']);
				}
				if(column.property=='totalComputingTime') {
					return Format.formatComputingTime(row['totalComputingTime']/3600);
				}
				if(column.property=='accountConsumed') {
					return Format.formatMoney(row['accountConsumed']);
				}
      },
			onCreateClick() {
				this.$refs.billGroupDialog.doCreate().then((res) => {
					// Reload table data
					this.$refs.billGroupTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onEditClick(billGroup) {
				this.$refs.billGroupDialog.doEdit(billGroup).then((res) => {
					// Reload table data
					this.$refs.billGroupTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onDeleteClick(billGroup) {
				this.$refs.billGroupDialog.doDelete(billGroup).then((res) => {
					// Reload table data
					this.$refs.billGroupTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onAccountOperateClick(billGroup) {
				this.$refs.accountOperateDialog.doOperate(billGroup).then((res) => {
					// Reload table data
					this.$refs.billGroupTable.fetchTableData(true);
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
