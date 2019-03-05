<style>
</style>
<template>
	<div class="height--100 p-10">
		<div class="table-style">
			<composite-table id="tid_notify-group-table" ref="notifyGroupTable"
			:table-data-fetcher="tableDataFetcher"
			:default-sort="{ prop: 'name', order: 'ascending'	}"
			:search-enable="true"
			:search-props="['name']"
			:current-page="1"
			:page-sizes="[10, 20, 40, 50]"
			:page-size="10"
			:total="0">
				<ul slot="controller" class="composite-table-controller">
					<el-button id="tid_notify-group-create" type="primary" @click="onCreateClick">{{$t("UserGroup.Action.Create")}}</el-button>
				</ul>
				<el-table-column
					prop="name"
					:label="$t('NotifyGroup.Name')"
					sortable="custom"
					align="left">
				</el-table-column>
				<el-table-column
					prop="emails"
					:label="$t('NotifyGroup.Emails')"
					align="right"
					:formatter="columnFormatter">
				</el-table-column>
				<el-table-column
				prop="mobiles"
				:label="$t('NotifyGroup.Mobiles')"
				align="right"
				:formatter="columnFormatter">
				</el-table-column>
				<el-table-column
					:label="$t('Action')"
					align='center'>
					<template slot-scope="scope">
						<el-dropdown trigger="click" class="act" @command="onActionCommand">
							<span class="demonstration">
								{{$t('Job.Action')}}<i class="el-icon-arrow-down el-icon--right"></i>
							</span>
							<el-dropdown-menu slot="dropdown">
								<el-dropdown-item :command="{fn:onEditClick,argument:scope.row}">{{$t('Action.Edit')}}</el-dropdown-item>
								<el-dropdown-item :command="{fn:onDeleteClick,argument:scope.row}">{{$t('Action.Delete')}}</el-dropdown-item>
							</el-dropdown-menu>
						</el-dropdown>
					</template>
				</el-table-column>
			</composite-table>
			<notify-group-dialog ref="notifyGroupDialog" />
		</div>
	</div>
</template>
<script>
	import CompositeTable from '../component/composite-table'
	import NotifyGroupService from '../service/notify-group'
	import Format from '../common/format'
	import NotifyGroupDialog from './notify-group-manage/notify-group-dialog'

	export default {
		data() {
			return {
        tableDataFetcher: NotifyGroupService.getNotifyGroupsTableDataFetcher()
      }
		},
		components: {
			'composite-table': CompositeTable,
			'notify-group-dialog': NotifyGroupDialog
		},
    methods: {
      columnFormatter(row, column) {
				if(column.property=='emails') {
					return Format.formatCount(row['emails'].length);
				}
        if(column.property=='mobiles') {
          return Format.formatCount(row['mobiles'].length);
        }
      },
			onCreateClick() {
				this.$refs.notifyGroupDialog.doCreate().then((res) => {
					// Reload table data
					this.$refs.notifyGroupTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onEditClick(notifyGroup) {
				this.$refs.notifyGroupDialog.doEdit(notifyGroup).then((res) => {
					// Reload table data
					this.$refs.notifyGroupTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onDeleteClick(notifyGroup) {
				this.$refs.notifyGroupDialog.doDelete(notifyGroup).then((res) => {
					// Reload table data
					this.$refs.notifyGroupTable.fetchTableData(true);
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
