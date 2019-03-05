<template>
  <div>
    <composite-table ref="reportTable"
        :table-data="table"
        :default-sort="{ prop: 'createTime', order: 'descending' }"
        :current-page="1"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="20"
        :total="0"
        :searchEnable="false"
        >
          <el-table-column
        prop="start_time"
        :label="$t('Report.Table.Time')"
        sortable="custom"
        align="center"
       ></el-table-column>
       <el-table-column
        v-if="job_type != 'job'"
        prop="name"
        :label="name_label()"
        sortable="custom"
        align="right"
       ></el-table-column>
       <el-table-column
        prop="job_count"
        :label="$t('Report.Table.Job')"
        sortable="custom"
        align="right"
       ></el-table-column>
       <el-table-column
        prop="cpu_count"
        :label="$t('Report.Table.CPU')"
        sortable="custom"
        align="right"
       ></el-table-column>
       <el-table-column
        prop="cpu_runtime"
        :label="'CPU '+$t('Report.Chart.Time')"
        sortable="custom"
        align="right"></el-table-column>
       <el-table-column
        prop="gpu_count"
        :label="$t('Report.Table.GPU')"
        sortable="custom"
        align="right"
       ></el-table-column>
       <el-table-column
        prop="gpu_runtime"
        :label="'GPU '+$t('Report.Chart.Time')"
        sortable="custom"
        align="right"
       ></el-table-column>
        </composite-table>
  </div>
</template>
<script>
import CompositeTable from '../../component/composite-table'
  export default {
      components:{
        'composite-table': CompositeTable
      },
      props: ['table','job_type'],
      data () {
        return {
          name_label:function(){
            if(this.job_type == 'user'){
              return this.$t('LDAP.Login.Username');
            } else {
              return this.$t('BillGroup');
            }
          }
        };
      }
    }
</script>
