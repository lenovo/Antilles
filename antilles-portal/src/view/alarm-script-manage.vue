<style>
</style>
<template>
<div class="height--100 p-10">
	<div class="table-style">
		<composite-table id="tid_alarm-script-table" ref="alarmScriptTable"
			:table-data-fetcher="tableDataFetcher"
			:default-sort="{ prop: 'name', order: 'ascending'	}"
			:search-enable="true"
			:search-props="['name']"
			:current-page="1"
			:page-sizes="[10, 20, 40, 50]"
			:page-size="10"
			:total="0">
			<ul slot="controller" class="composite-table-controller">
				<el-button style="opacity: 0;"></el-button>
			</ul>
			<el-table-column
	      prop="name"
	      :label="$t('Alarm.Script.Name')"
	      sortable="custom"
				align="left">
			</el-table-column>
			<el-table-column
	      prop="fileSize"
	      :label="$t('Alarm.Script.Size')"
	      sortable="custom"
				align="right"
				width='200'
				:formatter="columnFormatter">
			</el-table-column>
			<el-table-column
				prop="createTime"
				:label="$t('Alarm.Script.Time')"
				align='center'
				sortable="custom"
				:formatter="columnFormatter">
			</el-table-column>
		</composite-table>
	</div>
</div>
</template>
<script>
import CompositeTable from '../component/composite-table'
import AlarmScriptService from '../service/alarm-script'
import Format from '../common/format'

export default {
	data() {
		return {
			tableDataFetcher: AlarmScriptService.getAlarmScriptsTableDataFetcher()
		}
	},
	components: {
		'composite-table': CompositeTable
	},
	methods: {
		columnFormatter(row,column) {
			if(column.property == 'fileSize') {
				return Format.formatByteSize(row.fileSize);
			}
			if(column.property == 'createTime') {
				return Format.formatDateTime(row.createTime);
			}
		}
	}
}
</script>
