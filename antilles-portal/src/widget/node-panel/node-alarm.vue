<style scoped>
</style>
<template>
<composite-table id="tid_node-alarm-table" ref="alarmTable"
  :table-data-fetcher="tableDataFetcher"
  :selection-enable="false"
  :default-sort="{ prop: 'id', order: 'ascending'	}"
  :current-page="1"
  :page-sizes="[10, 20, 50, 100]"
  :page-size="20"
  :total="0"
  :searchEnable="false"
  :searchProps="['id', 'policyName']"
  :externalFilter="dataFilter"
  >
  </ul>
  <el-table-column
    prop="id"
    :label="$t('Alarm.Table.title.id')"
    sortable="custom"
    align='center'
    width="80">
  </el-table-column>
  <el-table-column
    prop="policyName"
    :label="$t('Alarm.Table.title.policyName')"
    sortable="custom">
    <template slot-scope='scope'>
      <nobr :title="scope.row.policyName">{{ scope.row.policyName }}</nobr>
    </template>
  </el-table-column>
  <el-table-column
    prop="policyLevel"
    :label="$t('Alarm.Table.title.policyLevel')"
    sortable="custom"
    align='left'
    width="120">
    <template  slot-scope="scope">
      <!-- show single alarm level color -->
      <!-- <p class="alarm-level" :class="scope.row.policyLevel?alarmLevelCss(scope.row.policyLevel):''">{{ scope.row.policyLevel }}</p> -->
      <alarm-table-level
      alarm-level-size="normal"
      :level='scope.row.policyLevel'>
      </alarm-table-level>
    </template>
  </el-table-column>
  <el-table-column
    prop="status"
    :label="$t('Alarm.Table.title.status')"
    sortable="custom"
    align='center'
    width="120">
    <template slot-scope='scope'>{{ $t('Alarm.Status.' + scope.row.status) }}</template>
  </el-table-column>
  <el-table-column
    prop="createTime"
    :label="$t('Alarm.Table.title.createTime')"
    sortable="custom"
    width="160"
    :formatter="columnFormatter">
  </el-table-column>
</composite-table>
</template>
<script>
import CompositeTable from '../../component/composite-table'
import AlarmTablelevel from '../alarm-policy-level-label.vue'
import AlarmService from '../../service/alarm'
import AlarmPolicyService from '../../service/alarm-policy'
import Format from '../../common/format'

export default {
  data () {
    return {
      dataFilter: {
        status: {
          values: ['present', 'confirmed'],
          type: "in"
        },
        nodeName: {
          values: [this.node.hostname],
          type: "in"
        }
      },
      tableDataFetcher: AlarmService.getAlarmTableDataFetcher()
    }
  },
  components: {
    'composite-table': CompositeTable,
    'alarm-table-level': AlarmTablelevel
  },
  props: [
    'node'
  ],
  mounted () {
  },
  methods: {
    columnFormatter(row, column) {
      return Format.formatDateTime(row[column.property]);
    }
  }
}
</script>
