
<template>
  <div class="reportPreview">
    <el-col :span="8" v-show="preview.twoColumns">
      <report-pie :pie="data_pie" @clickPie="filter"></report-pie>
    </el-col>
    <el-col :span="preview.twoColumns?16:24">
      <el-tabs v-model="activeName" @tab-click="changeTab">
        <el-tab-pane :label='$t("Report.Tab.Chart")' name="chart">
          <el-radio-group v-model="chartType" @change="handleClick">
            <el-radio-button label="job">{{$t("Trend.Chart.Title.job")}}</el-radio-button>
            <el-radio-button label="CPU"></el-radio-button>
            <el-radio-button label="GPU"></el-radio-button>
          </el-radio-group>
          <div>
          <report-bar :bar="data_bar" v-show="chartType == 'job'"></report-bar>
          <report-essemble :essemble="data_essemble" v-show="chartType != 'job'"></report-essemble>
          </div>
        </el-tab-pane>
        <el-tab-pane :label='$t("Report.Tab.Table")' name="table">
        <report-table :table="data_table" :job_type="preview.job_type"></report-table>
        </el-tab-pane>
      </el-tabs>
    </el-col>
  </div>
</template>
<script>
import ReportPie from "./report-pie"
import ReportBar from "./report-bar"
import ReportEssemble from "./report-essemble"
import ReportTable from "./report-table"
import _ from "lodash"
import ReportService from "../../service/report"

  export default {
      components:{
        'report-pie':ReportPie,
        'report-bar':ReportBar,
        'report-essemble':ReportEssemble,
        'report-table':ReportTable
      },
      props: ['preview'],
      data () {
        return {
          activeName:"chart",
          chartType:"job",
          rawData:[],
          filterData:[],
          data_pie:{},
          data_table:[],
          data_bar:{},
          data_essemble:{},
          get_pie:function(data){
            var pieData=[];
            const unique = [...new Set(data.map(item => item.name))];
            unique.forEach(function(item){
              pieData.push({
                value:_.sumBy(_.filter(data, { 'name': item }),'job_count'),
                name:item
              });
            });
            return {
              data:pieData,
              legend:unique
            };
          },
          get_bar:function(data){
            var y=[];
            const uniqueTime = [...new Set(data.map(item => item.start_time))];
            uniqueTime.forEach(function(item){
              y.push(_.sumBy(_.filter(data, { 'start_time': item }),'job_count'));
            });
            return {
              x:uniqueTime,
              y:y
            }
          },
          get_essemble:function(data){
            var cpuTime=[],
                cpuCount=[],
                gpuTime=[],
                gpuCount=[];
            const uniqueTime = [...new Set(data.map(item => item.start_time))];
            uniqueTime.forEach(function(item){
              var subtotal=_.filter(data, { 'start_time': item });
              cpuCount.push(_.sumBy(subtotal,'cpu_count'));
              cpuTime.push(_.sumBy(subtotal,'cpu_runtime'));
              gpuCount.push(_.sumBy(subtotal,'gpu_count'));
              gpuTime.push(_.sumBy(subtotal,'gpu_runtime'));
            });
            
            return {
              time:uniqueTime,
              CPUTime:cpuTime,
              CPUCount:cpuCount,
              GPUTime:gpuTime,
              GPUCount:gpuCount,
              type:this.chartType
            }
          },
          get_table:function(data){
            var table_data=[];
            if(this.preview.job_type == 'job'){
              const uniqueTime = [...new Set(data.map(item => item.start_time))];
              uniqueTime.forEach(function(item){
                var subtotal=_.filter(data, { 'start_time': item });
                table_data.push({
                  'start_time':item,
                  'job_count':_.sumBy(subtotal,'job_count'),
                  'cpu_count':_.sumBy(subtotal,'cpu_count'),
                  'cpu_runtime':_.sumBy(subtotal,'cpu_runtime'),
                  'gpu_count':_.sumBy(subtotal,'gpu_count'),
                  'gpu_runtime':_.sumBy(subtotal,'gpu_runtime')
                });
              });
              return table_data
            } else {
              const uniqueName = [...new Set(data.map(item => item.name))];
              uniqueName.forEach(function(item){
                var subtotal=_.filter(data, { 'name': item });
                const uniqueTime = [...new Set(subtotal.map(item => item.start_time))];
                uniqueTime.forEach(function(t){
                  var subtotal_time=_.filter(subtotal, { 'start_time': t });
                  table_data.push({
                    'start_time':t,
                    'name':item,
                    'job_count':_.sumBy(subtotal_time,'job_count'),
                    'cpu_count':_.sumBy(subtotal_time,'cpu_count'),
                    'cpu_runtime':_.sumBy(subtotal_time,'cpu_runtime'),
                    'gpu_count':_.sumBy(subtotal_time,'gpu_count'),
                    'gpu_runtime':_.sumBy(subtotal_time,'gpu_runtime')
                  });
                })
              });
              return table_data
            }
          }
        };
      },
      methods:{
        handleClick(type) {
          switch(type){
            case 'job':
              this.data_bar=this.get_bar(this.filterData);
            break;
            case 'CPU':
              this.data_essemble=this.get_essemble(this.filterData);
            break;
            case 'GPU':
              this.data_essemble=this.get_essemble(this.filterData);
            break;
            default:
            break;
          }
        },
        filter(data){
          if(data.data.selected){
            this.filterData=_.filter(this.rawData,{'name':data.data.name});
            console.log(this.filterData);
          } else {
            this.filterData=this.rawData;
          }
        },
        changeTab(event){
          this.data_bar=this.get_bar(this.filterData);
          this.data_essemble=this.get_essemble(this.filterData);
          this.data_table.splice(0, this.data_table.length);
            this.get_table(this.filterData).forEach((item) => {
              this.data_table.push(item);
            });
        }
      },
      watch:{
        preview:{
          handler:function(){
                var $this=this;
                var type=this.preview.job_type;
                if(!isNaN(this.preview.start_time)){
                  ReportService.previewJobReport(this.preview).then(function(res){
                    $this.rawData=_.sortBy(res,['start_time']);
                    $this.filterData=$this.rawData;
                    $this.data_pie=$this.get_pie($this.rawData);
                  },function(error){

                  });
                  } else {
                    $this.rawData=[];
                    $this.filterData=$this.rawData;
                    $this.data_pie=$this.get_pie($this.rawData);
                  }
            },
          deep:true
        },
        filterData:{
          handler:function(){
            this.data_bar=this.get_bar(this.filterData);
            this.data_essemble=this.get_essemble(this.filterData);
            this.data_table.splice(0, this.data_table.length);
            this.get_table(this.filterData).forEach((item) => {
              this.data_table.push(item);
            });
          },
          deep:true
        }
      }
    }
</script>