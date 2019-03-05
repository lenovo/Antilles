<style media="screen">
</style>
<template>
	<div class="height--100 p-10">
		<div class="table-style">
			<composite-table id="tid_user-table" ref="userTable"
				:table-data-fetcher="tableDataFetcher"
				:default-sort="{ prop: 'username', order: 'descending'	}"
				:search-enable="true"
				:search-props="['username', 'billGroupName']"
				:current-page="1"
				:page-sizes="[10, 20, 40, 50]"
				:page-size="10"
				:total="0">
				<div slot="controller" class="composite-table-controller">
					<el-button id="tid_user-create" v-if="ldapManaged" type="primary" @click="onCreateClick">{{$t('User.Action.Create')}}</el-button>
					<el-button id="tid_user-import" v-if="!ldapManaged" type="primary" @click="onImportClick">{{$t('User.Action.Import')}}</el-button>
					<el-button id="tid_user-batch-import" type="primary" @click="onBatchImportClick">{{$t('User.Action.BatchImport')}}</el-button>
					<el-button id="tid_user-batch-export" type="primary" @click="onExportClick">{{$t('User.Action.Export')}}</el-button>
        </div>
				<el-table-column
		      prop="id"
		      :label="$t('User.Id')"
			  	align="center"
		      width="160">
		    </el-table-column>
			  <el-table-column
		      prop="username"
		      :label="$t('User.Username')"
		      sortable="custom"
			  align="center"
		      width="160">
		    </el-table-column>
				<el-table-column
		      prop="role"
		      :label="$t('User.Role')"
		      sortable="custom"
					align="center"
		      width="160"
					:formatter="columnFormatter">
		    </el-table-column>
				<!-- <el-table-column
					prop="realName"
					:label="$t('User.RealName')"
					sortable="custom"
					align="center"
					width="160">
				</el-table-column> -->
				<!-- <el-table-column
		      prop="userGroupName"
		      :label="$t('UserGroup')"
		      sortable="custom"
					align="center"
		      width="160"
					v-if="ldapManaged">
		    </el-table-column> -->
				<el-table-column
		      prop="billGroupName"
		      :label="$t('BillGroup')"
		      sortable="custom"
					align="center"
		      width="160">
		    </el-table-column>
				<!-- <el-table-column
		      prop="email"
		      :label="$t('User.Email')"
		      sortable="custom"
					align="left">
		    </el-table-column> -->
				<el-table-column
		      prop="loginTime"
		      :label="$t('User.LoginTime')"
					sortable="custom"
					align="center"
					:formatter="columnFormatter">
		    </el-table-column>
				<el-table-column
		      prop="thawTime"
		      :label="$t('User.ThawTime')"
					align="center"
					:formatter="columnFormatter">
		    </el-table-column>
				<el-table-column
					:label="$t('User.Freezed.Status')"
					align='center'
					width="140">
					<template slot-scope="scope">
						<span>{{scope.row.freezed?$t('User.Freezed.Suspended'):'-'}}</span>
					</template>
				</el-table-column>
				<el-table-column
					:label="$t('Action')"
					align='center'
					width="140">
					<template slot-scope="scope">
						<el-dropdown trigger="click" class="act" @command="onActionCommand">
							<span class="demonstration">
								{{$t('Job.Action')}}<i class="el-icon-arrow-down el-icon--right"></i>
							</span>
							<el-dropdown-menu slot="dropdown">
								<el-dropdown-item :command="{fn:onInfoClick,argument:scope.row.id}">{{$t('Action.Info')}}</el-dropdown-item>
								<el-dropdown-item :command="{fn:onEditClick,argument:scope.row}">{{$t('Action.Edit')}}</el-dropdown-item>
                <el-dropdown-item :command="{fn:onChangePasswordClick,argument:scope.row}" :disabled="scope.row.role == 'admin'">{{$t('User.Action.ChangePassword')}}</el-dropdown-item>
                <el-dropdown-item :command="{fn:onDeleteClick,argument:scope.row}">{{$t('Action.Delete')}}</el-dropdown-item>
                <el-dropdown-item v-if='scope.row.role!="admin"&&!scope.row.freezed' :command="{fn:onSuspend,argument:scope.row}">{{$t('Action.Suspend')}}</el-dropdown-item>
                <el-dropdown-item v-if='scope.row.role!="admin"&&scope.row.freezed' :command="{fn:onResume,argument:scope.row}">{{$t('Action.Resume')}}</el-dropdown-item>
							</el-dropdown-menu>
						</el-dropdown>
					</template>
				</el-table-column>
			</composite-table>
			<user-dialog id="tid_user-dialog" ref="userDialog" />
			<user-password-dialog id="tid_user-password-dialog" ref="userPasswordDialog" />
			<user-batch-import-dialog id="user-batch-import-dialog" ref="userBatchImportDialog" />
			<user-batch-import-progress-dialog id="user-batch-import-progress-dialog" ref="userBatchImportProgressDialog" />
			<user-batch-import-busy-dialog id="user-batch-import-busy-dialog" ref="userBatchImportBusyDialog" />
			<user-batch-import-detail-dialog id="user-batch-import-detail-dialog" ref="userBatchImportDetailDialog" />
		</div>
	</div>

</template>
<script>
	import UserDialog from './user-manage/user-dialog'
	import UserBatchImportDialog from './user-manage/user-batch-import-dialog'
	import UserBatchImportProgressDialog from './user-manage/user-batch-import-progress-dialog'
	import UserBatchImportBusyDialog from './user-manage/user-batch-import-busy-dialog'
	import UserBatchImportDetailDialog from './user-manage/user-batch-import-detail-dialog'
	import UserPasswordDialog from './user-manage/user-password-dialog'
	import CompositeTable from '../component/composite-table'
	import UserService from '../service/user'
	import Format from '../common/format'
	import AuthService from '../service/auth'
	import UserBatchImportService from '../service/user-batch-import'

	export default {
		data() {
			return {
        tableDataFetcher: UserService.getUsersTableDataFetcher(),
				ldapManaged: AuthService.isLDAPManaged()
      }
		},
		components: {
			'composite-table': CompositeTable,
			'user-dialog': UserDialog,
			'user-password-dialog': UserPasswordDialog,
			'user-batch-import-dialog': UserBatchImportDialog,
			'user-batch-import-progress-dialog': UserBatchImportProgressDialog,
			'user-batch-import-busy-dialog': UserBatchImportBusyDialog,
			'user-batch-import-detail-dialog': UserBatchImportDetailDialog
		},
    methods: {
      columnFormatter(row, column) {
				if(column.property == 'role') {
					return UserService.getUserRoleDisplayName(row['role']);
				}
				if(column.property == 'loginTime') {
					return Format.formatDateTime(row['loginTime']);
				}
				if(column.property == 'thawTime') {
					if(row.freezed) {
						return Format.formatDateTime(row['thawTime']);
					} else {
						return Format.formatCount(0);
					}
				}
      },
			onCreateClick() {
				this.$refs.userDialog.doCreate().then((res) => {
					// Reload table data
					this.$refs.userTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onEditClick(user) {
				this.$refs.userDialog.doEdit(user).then((res) => {
					// Reload table data
					this.$refs.userTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onInfoClick(id) {
				this.$router.push({path: `/main/user/${id}`});
			},
			onChangePasswordClick(user) {
				this.$refs.userPasswordDialog.doChangePassword(user).then((res) => {
					// Reload table data
					this.$refs.userTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onDeleteClick(user) {
				this.$refs.userDialog.doDelete(user).then((res) => {
					// Reload table data
					this.$refs.userTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onImportClick() {
				this.$refs.userDialog.doImport().then((res) => {
					// Reload table data
					this.$refs.userTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onSuspend(row) {
				this.$refs.userDialog.doFreezed(row).then((res) => {
					// Reload table data
					this.$refs.userTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onResume(row) {
				this.$refs.userDialog.doUnfreezed(row).then((res) => {
					// Reload table data
					this.$refs.userTable.fetchTableData(true);
				}, (res) => {
					// Do nothing
				});
			},
			onBatchImportClick() {
				UserBatchImportService.getUsersImportStatu().then((res) =>{
					const showLast = res.last_importing?true:false;
					if(res.status == 'idle'){
						this.$refs.userBatchImportDialog.show(this.$refs.userBatchImportDetailDialog,this.$refs.userBatchImportProgressDialog,this.$refs.userTable,showLast);
					}else if(res.status == 'importing'){
						this.$refs.userBatchImportProgressDialog.show(this.$refs.userBatchImportDetailDialog,this.$refs.userTable);
					}else{
						this.$refs.userBatchImportBusyDialog.show(this.$refs.userBatchImportDetailDialog,showLast);
					}
				},(err) =>{
					this.$message.error(err);
				})
			},
			onExportClick() {
				UserBatchImportService.getUsersExport().then((res)=>{
					window.open('/download/' + res.data);
				},(err)=>{

				})
			},
      onActionCommand(command){
        let fn = command.fn;
        let argument = command.argument;
        fn(argument);
      }
    }
	}
</script>
