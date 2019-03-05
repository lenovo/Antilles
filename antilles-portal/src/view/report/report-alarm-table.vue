<template>
	 <composite-table ref="reportAlarmTable"        
	 	:table-data="dataReportAlarmTable"
        v-if="dataReportAlarmTable.length>0"
        :default-sort="{ prop: 'createTime', order: 'descending'}"
        :current-page="1"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="20"
        :total="dataReportAlarmTable.length"
        :searchEnable="false">        
        <el-table-column prop='alarm_time'
        align="right"
        sortable
        :label="$t('Alarm.Table.title.createTime')">
        </el-table-column>
        <el-table-column v-for="(item, index) in tables" :key='index' :prop='item.prop' sortable align="right" 
        :label="item.label">
        </el-table-column>       
        </composite-table>
</template>
<script>
	import CompositeTable from '../../component/composite-table'
	export default{
		components:{
		'composite-table':CompositeTable
		},
		props:['dataReportAlarmTable'],
		data(){
			return{
                tables:[
                {
                    label:this.$t('Alarm.PolicyLevel.fatal'),
                    prop:'critical'
                },
                {
                    label:this.$t('Alarm.PolicyLevel.error'),
                    prop:'error'
                },
                {
                    label:this.$t('Alarm.PolicyLevel.warn'),
                    prop:'warning'
                },
                {
                    label:this.$t('Alarm.PolicyLevel.info'),
                    prop:'info'
                },
                {
                    label:this.$t('Alarm.Table.title.Total'),
                    prop:'num_total'
                }
                ]
			};
		},
		methods:{
			onDataFetchError(errMsg){
				this.$message.error(this.$t(errMsg));
			},
            reLayout() {
                this.$refs.reportAlarmTable.reLayout();
            }
		}
	}

</script>
