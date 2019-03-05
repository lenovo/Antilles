
<style lang="css">
	.composite-table-controller > li {
		float: left;
		list-style: none;
	}
	.operationLog-manage>.el-row {
		border-radius: 3px;
	}
	.operation-search {
		margin-bottom: 20px;
	}
	.operationLog-manage .composite-table-header {
		margin: 0;
	}
	.operation-search-condition {
		display: inline-block;
		width: 100px;
		height: 36px;
		line-height: 36px;
		margin-right: 20px;
		color: #A0A0A0;
	}
	.width-150{
		width:150px;
	}
	.operation-flex{
		display: flex;
	}
	/*.operation-search{
		display: flex;
		margin-top:20px;
	}*/
	.operation-search>div{
		margin-left: 0;
	}
	.operation-table-target {
		/*color: #019fff;
		cursor: pointer;*/
	}
	.operation-dialog-content {
		height: 100px;
		overflow-y: scroll;

	}
	.operation-dialog-content  P{
		margin-bottom: 5px;
	}
	.operation-search-line {
		margin-bottom: 20px;
	}
	.tid_operation-operator>div{
		text-overflow:ellipsis;
		overflow: hidden;
	}
	.operation-query-button{
		margin-top:20px;
	}

</style>

<template lang="html">
	<div id="tid_operation-manage" class="operationLog-manage table-top-manage p-10">
		<!--Search screen -->
		<el-row class="operation-search b-w p-20">
			<el-row class="operation-search-line">
				<!-- operator select -->
				<el-col :span="12" class="operation-flex">
					<span class="operation-search-condition">{{$t('Operation.Screen.operator')}}</span>
					<multi-user-selector :allable="true" :filter-type="'username,usergroup,billinggroup'" :users-value="[]" :users-type="'username'" @change="userSelectChange"></multi-user-selector>
				</el-col>
				<!-- module & operation select -->
				<el-col :span="12" class="operation-flex">
						<span class="operation-search-condition width-150">{{$t('Operation.Screen.module')}}</span>
						<el-cascader id="tid_opertion-module"
						expand-trigger="hover"
						:clearable='true'
						:options="ModuleOptions"
						v-model="ModuleSelectedOptions"
						@change='onScreenModuleChenge'
						></el-cascader>
				</el-col>

			</el-row>
			<el-row class="operation-flex">
				<!-- date select -->
				<span class="operation-search-condition">{{$t('Operation.Screen.date')}}</span>
				<date-region-picker
					v-model="pickerSearchDate"
					quick-pick="default"
					@date-change="onDateChange">
				</date-region-picker>
			</el-row>
			<el-row class="operation-query-button">
				<el-button type="primary" @click="Query">{{$t('Operation.Action.Query')}}</el-button>
			</el-row>
		</el-row>
		<!-- operation table -->
		<el-row class="table-styles">
			<composite-table id="tid_operation-manage-table" ref="operationTable"
				:table-data-fetcher="tableDataFetcher"
				:selection-enable="false"
				:default-sort="{ prop: 'actionTime', order: 'descending' }"
				:current-page="1"
				:page-sizes="[10, 20, 50, 100]"
				:page-size="10"
				:total="0"
				:searchEnable="false"
				:externalFilter="dataFilterTemp"
				>

				<el-table-column
					prop="logId"
					:label="$t('Operation.Table.title.logId')"
					sortable="custom"
					align='center'
					width="100">
				</el-table-column>
				<el-table-column
					prop="userName"
					:label="$t('Operation.Table.title.userName')"
					sortable="custom"
					align='center'>
				</el-table-column>
				<el-table-column
					prop="module"
					:label="$t('Operation.Table.title.module')"
					sortable="custom"
					align='center'>
					<template slot-scope='scope'>{{$t('Operation.Module.' + scope.row.module)}}</template></el-table-column>
				<el-table-column
					prop="action"
					:label="$t('Operation.Table.title.action')"
					sortable="custom"
					align='center'><template slot-scope='scope'>{{$t('Operation.Module.' + scope.row.action)}}</template></el-table-column>
				<el-table-column
					:label="$t('Operation.Table.title.target')">
					<template slot-scope='scope'>
						<p class="operation-table-target">{{ onCheckDetail(scope.row) }}</p>
					</template>
				</el-table-column>
				<el-table-column
					prop="actionTime"
					:label="$t('Operation.Table.title.actionTime')"
					sortable="custom"
					width="200"
					:formatter="columnFormatter">
				</el-table-column>
			</composite-table>
		</el-row>
	</div>
</template>

<script>

import CompositeTable from '../component/composite-table'
import DateRegionPicker from '../component/date-region-picker'
import NodeSelect from '../widget/node-select'
import OperationService from './../service/operation'
import Format from '../common/format'
import MultiUserSelector from './../widget/multi-user-selector'

export default {
	data () {
		return {
			ModuleSelectedOptions: [''],
			dataFilter: {
				userName: {
					value_type: "username",
					values: [],
					type: "in"
				},
				module: {
					values: [],
					type: "in"
				},
				action: {
					values: [],
					type: 'in'
				},
				actionTime: {
					values: [new Date(0),new Date()],
					type: "range"
				}
			},
			dataFilterTemp: {},
			ModuleOptions: [],
			pickerSearchDate: [],
			tableDataFetcher: OperationService.getOperationTableDataFetcher()
		}
	},
	components: {
		'composite-table': CompositeTable,
		'date-region-picker': DateRegionPicker,
		'node-select': NodeSelect,
		'multi-user-selector':MultiUserSelector
	},
	mounted () {
		this.ModuleOptions = this.analyzeModule(OperationService.ModuleEnums);
	},

	methods: {
		onScreenModuleChenge(val) {
			if(val.length > 0) {
				this.dataFilter.module.values = [val[0]];
				this.dataFilter.action.values = [val[1]];
			} else {
				this.dataFilter.module.values = [];
				this.dataFilter.action.values = [];
			}
		},
		onDateChange (dateRange) {
			var newDate = [];
			newDate[0] = dateRange[0]?dateRange[0]:new Date(0);
			newDate[1] = dateRange[1]?dateRange[1]:new Date();
			this.dataFilter.actionTime.values = newDate;
		},
		analyzeModule(modules) {
			let options = [];
			modules.forEach((module) => {
				if(module.children) {
					module.children = this.analyzeModule(module.children)
				}
				options.push({
					value: module.value,
					label: this.$t('Operation.Module.' + module.value),
					children: module.children
				})

			})
			return options
		},

		onCheckDetail (log) {
			var target = ''
			log.target.forEach((obj, index) => {
				if(index == log.target.length - 1){
					target += obj.name
				} else {
					target += obj.name + ', '
				}
			})
			return target;
		},

		columnFormatter(row, column) {
			return Format.formatDateTime(row[column.property]);
		},
    userSelectChange(val){
		  this.dataFilter.userName.value_type=val.value_type;
      this.dataFilter.userName.values=val.values;
		},
		Query() {
			this.dataFilterTemp = JSON.parse(JSON.stringify(this.dataFilter));
		}
	}
}
</script>
