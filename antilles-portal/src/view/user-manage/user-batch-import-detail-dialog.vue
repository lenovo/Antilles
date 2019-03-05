<style>
  .import-table-title{
    padding:0 20px;
  }
  .import-table-title li{
    float: left;
  }
  .import-table-title li:last-child{
    float: right;
  }
  .import-table-title li:nth-child(2){
    margin:0 40px;
  }
  .clearfix:after{
    content: "020";
    display: block;
    height: 0;
    clear: both;
    visibility: hidden;
  }

  .clearfix {
    zoom: 1;
  }
</style>

<template>
  <el-dialog
    :title="title"
    :visible.sync="dialogVisible"
    width="70%">
    <div>
      <ul class="import-table-title clearfix">
        <li>
          <span>{{$t('User.Import.Title.FinishTime')}}:</span>
          <span>{{finishTime}}</span>
        </li>
        <li>
          <span>{{$t('User.Import.Title.Success')}}:</span>
          <span>{{success}} users</span>
        </li>
        <li>
          <span>{{$t('User.Import.Title.Fail')}}:</span>
          <span>{{failUsers}} users</span>
        </li>
        <li>
          <el-checkbox class="detailbox" @change="shouFailedUsers" v-model="showFailed">{{$t('User.Import.Title.OnlyShowFailedUsers')}}</el-checkbox>
        </li>
      </ul>
    </div>
    <div>
      <composite-table id="import_detail_view-table"
			ref="importDetailViewTable"
      :table-data-fetcher="tableDataFetcher"
      :default-sort="{ prop: 'username', order: 'descending'	}"
			:current-page="1"
      :externalFilter="dataFilter"
			:page-sizes="[10, 20, 40, 50]"
			:page-size="10"
			:total="0">
        <el-table-column
          prop="row"
          :label="$t('User.Import.Table.Title.Row')"
          sortable="custom"
          align="center"
          width="">
        </el-table-column>
        <el-table-column
          prop="username"
          :label="$t('User.Import.Table.Title.Username')"
          sortable="custom"
          align="center"
          width="">
        </el-table-column>
        <el-table-column
          prop="role"
          :label="$t('User.Import.Table.Title.Role')"
          sortable="custom"
          align="center"
          width="">
        </el-table-column>
        <el-table-column
          prop="lastName"
          :label="$t('User.Import.Table.Title.LastName')"
          sortable="custom"
          align="center"
          width="">
        </el-table-column>
        <el-table-column
          prop="firstName"
          :label="$t('User.Import.Table.Title.FirstName')"
          sortable="custom"
          align="center"
          width="">
        </el-table-column>
        <el-table-column
          prop="billGroup"
          :label="$t('User.Import.Table.Title.BillingGroup')"
          sortable="custom"
          align="center"
          width="">
        </el-table-column>
        <el-table-column
          prop="email"
          :label="$t('User.Import.Table.Title.Email')"
          align='center'
          width="">
        </el-table-column>
        <el-table-column
          :label="$t('User.Import.Table.Title.Result')"
          align='center'
          width="">
          <template slot-scope="scope">
            <span v-if="scope.row.status=='success'">{{'success'}}</span>
            <span v-else>{{scope.row.errorMessage}}</span>
          </template>
        </el-table-column>
      </composite-table>
    </div>
    <div slot="footer" class="dialog-footer">
      <el-button @click="dialogVisible = false">{{$t('User.Action.Close')}}</el-button>
    </div>
  </el-dialog>
</template>

<script>
  import CompositeTable from '../../component/composite-table'
  import userBatchImportService from '../../service/user-batch-import'

  export default {
    data() {
      return {
        tableDataFetcher: {},
        title: this.$t('User.Import.Detail.Title'),
        dialogVisible: false,
        showFailed: false,
        dataFilter: {},
        success: 0,
        finishTime: '',
        failUsers: 0
      };
    },
    components: {
			'composite-table': CompositeTable
    },
    watch: {
      dialogVisible: function() {
        if(this.dialogVisible){
          this.tableDataFetcher = userBatchImportService.getUsersTableDataFetcher();
          userBatchImportService.getUsersImportStatu().then((res)=>{
            if(res.last_importing){
              this.finishTime = res.last_importing.finish_time;
              this.success = res.last_importing.success;
              this.failUsers = res.last_importing.finished - res.last_importing.success;
              this.$refs.importDetailViewTable.fetchTableData(true);
            }
          },(err)=>{
            this.$message.error(err);
          })
        }
      }
    },
    methods: {
      show() {
        this.dialogVisible = true;
      },
      shouFailedUsers() {
        if(this.showFailed){
          this.dataFilter = {
            status:{
              values:['error'],
              type: 'in'
            }
          };
        }else{
          this.dataFilter = {};
        }
      }
    }
  };
</script>