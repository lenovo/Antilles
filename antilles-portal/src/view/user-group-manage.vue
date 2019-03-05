<style>
.user-group-controller{
	max-width: 100%;
	text-align: left;
}

</style>
<template>
<div class="height--100 p-10">
	<div class="table-style">
		<composite-table id="tid_user-group-table" ref="userGroupTable"
			:table-data-fetcher="tableDataFetcher"
			:default-sort="{ prop: 'id', order: 'ascending'	}"
			:search-enable="true"
			:search-props="['name']"
			:current-page="1"
			:page-sizes="[10, 20, 40, 50]"
			:page-size="10"
			:total="0">
			<ul slot="controller" class="user-group-controller">
				<li>
					<el-button v-show='isLDAPManaged'  id="tid_user-group-create" type="primary" @click="onCreateClick">{{$t('UserGroup.Action.Create')}}</el-button>&nbsp;
				</li>
			</ul>
			<el-table-column
			 prop="id"
			 :label="$t('UserGroup.Gid')"
			 sortable="custom"
			 align="left">
		 </el-table-column>
		  <el-table-column
	      prop="name"
	      :label="$t('UserGroup.Name')"
	      sortable="custom"
				align="left">
	    </el-table-column>
			<el-table-column
				:label="$t('Action')"
				align='center'
				width="120" v-if="isLDAPManaged">
				<template slot-scope="scope">
					<el-button size="small"  @click="onEditClick(scope.row)" class="table-icon-button no-border" v-if="false"
					title="edit">
						<i class="el-erp-edit"></i>
					</el-button>
					<el-button size="small" v-if='isLDAPManaged' :title="$t('Action.Delete')" @click="onDeleteClick(scope.row)" class="table-icon-button no-border">
						<i class="el-erp-delete"></i>
					</el-button>
				</template>
			</el-table-column>
		</composite-table>
		<user-group-dialog id="tid_user-group-dialog" ref="userGroupDialog" />
	</div>
</div>
</template>
<script>
	import CompositeTable from '../component/composite-table'
	import UserGroupService from '../service/user-group'
	import Format from '../common/format'
	import UserGroupDialog from './user-group-manage/user-group-dialog'
	import AuthService from'../service/auth'
	export default {
		data() {
			return {
        tableDataFetcher: UserGroupService.getUserGroupsTableDataFetcher(),
				isLDAPManaged: AuthService.isLDAPManaged(),
      }
		},
		components: {
			'composite-table': CompositeTable,
			'user-group-dialog': UserGroupDialog
		},
    methods: {
      onCreateClick() {
				this.$refs.userGroupDialog.doCreate().then((res) => {
					// Reload table data
					this.$refs.userGroupTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onEditClick(userGroup) {
				this.$refs.userGroupDialog.doEdit(userGroup).then((res) => {
					// Reload table data
					this.$refs.userGroupTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onDeleteClick(userGroup) {
				this.$refs.userGroupDialog.doDelete(userGroup).then((res) => {
					// Reload table data
					this.$refs.userGroupTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			}
    }
	}
</script>
