<template>
		<composite-table id="tid_nodel-job-table" ref="jobTable"
			:table-data-fetcher="tableDataFetcher"
			:default-sort="{ prop: 'id', order: 'ascending'	}"
			:search-enable="false"
			:search-props="['id', 'name']"
			:current-page="1"
			:page-sizes="[10, 20, 40, 50]"
			:page-size="10"
      :auto-refresh="30*1000"
			:total="0">
      <el-table-column
        prop="id"
        :label="$t('Job.Id')"
        sortable="custom"
        align="center"
				width="100">
      </el-table-column>
      <el-table-column
        prop="name"
        :label="$t('Job.Name')"
        sortable="custom"
        align="center">
        <template slot-scope='scope'>
          <p @click="onDetailClick(scope.row)">{{scope.row.name}}</p>
        </template>
      </el-table-column>
      <el-table-column
        prop="schedulerId"
        :label="$t('Job.SchedulerId')"
        sortable="custom"
        align="center">
      </el-table-column>
      <el-table-column
        prop="submitUser"
        :label="$t('Job.SubmitUser')"
        sortable="custom"
        align="center">
      </el-table-column>
      <el-table-column
        prop="queue"
        :label="$t('Job.Queue')"
        sortable="custom"
        align="center"
				width="100">
      </el-table-column>
      <el-table-column
				v-show="isGpus"
        prop="usedGpus"
        :label="$t('Job.Gpu')"
        sortable="custom"
        align="center"
				width="80">
      </el-table-column>
      <el-table-column
        prop="beginTime"
        :label="$t('Job.BeginTime')"
        sortable="custom"
        align="center"
        :formatter="columnFormatter">
      </el-table-column>
		</composite-table>
</template>
<script>
	import CompositeTable from '../../component/composite-table'
	import JobService from '../../service/job'
	import Format from '../../common/format'

	export default {
		data() {
			return {
        tableDataFetcher: JobService.getRunningJobsTableDataFetcher(this.nodeId)
      }
		},
		components: {
			'composite-table': CompositeTable
		},
    props: [
      'nodeId',
			'isGpus'
    ],
    methods: {
      columnFormatter(row, column) {
				if(column.property == 'beginTime') {
					return Format.formatDateTime(row['beginTime']);
				}
      }
    }
	}
</script>
