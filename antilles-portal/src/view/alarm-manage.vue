<style>
  .composite-table-controller > li {
    float: left;
    list-style: none;
  }

  .alarm-manage > .el-row {
    border-radius: 3px;
  }

  .alarm-manage-condition {
    /*height: 150px;*/
    margin-bottom: 20px;

  }

  .alarm-manage-condition-line {
    margin-bottom: 20px;
  }

  .alarm-condition-search {
    display: flex;
    /*margin-right: 40px;*/
  }

  .alarm-condition-search > span {
    width: 100px;
    line-height: 36px;
    margin-right: 20px;
    color: #A0A0A0;
  }

  .alarm-manage-action {
    margin-right: 20px;
  }

  .alarmConditionSearch {
    float: right;
  }

  .alarm-search-date {
    display: flex;
    margin-left: 0;
  }

  .alarm-search-date > div {
    margin-left: 0;
  }

  .alarm-search-date-title {
    width: 100px;
    margin-right: 20px;
    line-height: 36px;
    color: #A0A0A0;
  }

  .dialogNote-cont {
    height: 80px;
    width: 100%;
    resize: none;
  }

  .alarm-table-note {
    min-height: 24px;
    color: #019fff;
    cursor: pointer;
  }

  .actionall-icon {
    margin-left: 8px;
    color: #fff;
  }

  .alarm-dropdown-menu {
    padding: 0;
    border-radius: 2px;
  }

  .alarm-dropdown-menu > li {
    padding: 10px 20px 0;
    border-top: 1px dashed #eee;
  }

  .alarm-dropdown-menu > li:first-child {
    border: none;
  }
  .alarm-query-button{
    margin-top:20px;
  }
</style>
<template>
  <div id="tid_alarm-manage" class="alarm-manage table-top-manage p-10">
    <!-- alarm condition -->
    <el-row class="alarm-manage-condition b-w p-20">
      <!-- first line ( status level ) -->
      <el-row class="alarm-manage-condition-line">
        <!-- status -->
        <el-col :span="12" class="alarm-condition-search">
          <span>{{$t('Alarm.Status')}}</span>
          <el-select id="tid_alarm-status" v-model="dataFilter.status.values"
                     @change="onAlarmSearchStatusChange"
                     multiple size="40" placeholder="">
            <el-option
              v-for="status in statusOptions"
              :key="status.value"
              :label="status.label"
              :value="status.value">
            </el-option>
          </el-select>
        </el-col>
        <!-- level -->
        <el-col :span="12" class="alarm-condition-search">
          <span>{{$t('Alarm.PolicyLevel')}}</span>
          <el-select id="tid_alarm-level" v-model="dataFilter.policyLevel.values"
                     @change="onAlarmSearchLevelChange"
                     size="40" multiple placeholder="">
            <el-option
              v-for="policyLevel in policyLevelOptions"
              :key="policyLevel.value"
              :label="policyLevel.label"
              :value="policyLevel.value">
            </el-option>
          </el-select>
        </el-col>
      </el-row>
      <!-- two line ( date ) -->
      <el-row class="alarm-search-date">
        <span class="alarm-search-date-title">{{$t('Alarm.Screen.selectDate')}}</span>
        <date-region-picker ref='dateRegionPicker'
                            v-model="pickerSearchDate"
                            quick-pick="default"
                            @date-change="onDateChange">
        </date-region-picker>
      </el-row>
      <el-row class="alarm-query-button">
        <el-button type="primary" @click="Query">{{$t('Alarm.Action.Query')}}</el-button>
      </el-row>
    </el-row>
    <!-- alarm table -->
    <el-row class="table-styles">
      <composite-table ref="alarmTable" id="tid_alarm-manage-table"
                       :table-data-fetcher="tableDataFetcher"
                       :selection-enable="true"
                       :default-sort="{ prop: 'createTime', order: 'descending' }"
                       :current-page="1"
                       :page-sizes="[10, 20, 50, 100]"
                       :page-size="20"
                       :total="0"
                       :searchEnable="true"
                       :searchProps="['id', 'policyName', 'comment']"
                       :externalFilter="dataFilterTemp"
                       @selection-change="onSelectionChange"
                       :auto-refresh="30*1000"
      >
        <ul slot="controller" class="composite-table-controller">
          <li class="alarm-manage-action">
            <el-button id="tid_alarm-confirm-btn" :disabled="alarmActionIsDisabled"
                       @click="alarmConfirm('confirm')">{{$t('Alarm.Action.confirm')}}
            </el-button>
          </li>
          <li class="alarm-manage-action">
            <el-button id="tid_alarm-fix-btn" :disabled="alarmActionIsDisabled" @click="alarmFix('fix')">
              {{$t('Alarm.Action.fix')}}
            </el-button>
          </li>
          <li class="alarm-manage-action">
            <el-button id="tid_alarm-btn" :disabled="alarmActionIsDisabled" @click="alarmDelete('delete')">
              {{$t('Alarm.Action.delete')}}
            </el-button>
          </li>
          <el-dropdown id="tid_alarm-action-all" trigger="click" @command="alarmAction">
            <el-button type="primary">
              {{ $t('Alarm.Action.actionAll') }}
              <i class="el-icon-caret-bottom actionall-icon"></i>
            </el-button>
            <el-dropdown-menu slot="dropdown" class="alarm-dropdown-menu">
              <el-dropdown-item command='confirmAll'>{{ $t('Alarm.Action.confirmAll') }}</el-dropdown-item>
              <el-dropdown-item command='fixAll'>{{ $t('Alarm.Action.fixAll') }}</el-dropdown-item>
              <el-dropdown-item command='deleteAll'>{{ $t('Alarm.Action.deleteAll') }}</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
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
          sortable="custom"
          width="200">
          <template slot-scope='scope'>
            <nobr :title="scope.row.policyName">{{ scope.row.policyName }}</nobr>
          </template>
        </el-table-column>
        <el-table-column
          prop="policyLevel"
          :label="$t('Alarm.Table.title.policyLevel')"
          sortable="custom"
          align='left'
          width="150">
          <template slot-scope="scope">
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
          width="150">
          <template slot-scope='scope'>{{ $t('Alarm.Status.' + scope.row.status) }}</template>
        </el-table-column>
        <el-table-column
          prop="createTime"
          :label="$t('Alarm.Table.title.createTime')"
          sortable="custom"
          width="150"
          :formatter="columnFormatter">
        </el-table-column>
        <el-table-column
          prop="nodeName"
          :label="$t('Alarm.Table.title.nodeName')"
          sortable="custom"
          width="130">
          <template slot-scope="scope">
            <span>{{scope.row.nodeName}}</span>
            <span v-if="scope.row.gpuId != null">:gpu{{scope.row.gpuId}}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="comment"
          :label="$t('Alarm.Table.title.comment')">
          <template slot-scope="scope">
            <!-- single alarm popover comment -->
            <div class="ellipsis">
              <p style=""
                 class="alarm-table-note"
                 @click="alarmEditComment(scope.row)">{{ scope.row.comment }}<span
                v-if="scope.row.comment.length<1">{{$t('User.Password.edit')}}</span></p>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          :label="$t('Alarm.Table.title.operation')"
          align='center'
          width="160">
          <template slot-scope="scope">
            <el-dropdown trigger="click" class="act" @command="onActionCommand">
							<span class="demonstration">
								{{$t('Job.Action')}}<i class="el-icon-arrow-down el-icon--right"></i>
							</span>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item id="tid_alarm-confirm-icon"
                                  :disabled="scope.row.status=='present'?false:true"
                                  :command="{fn:alarmConfirm,argument0:'confirm',argument1:scope.row.id}">
                  {{$t('Alarm.Action.confirm')}}
                </el-dropdown-item>
                <el-dropdown-item id="tid_alarm-fix-icon"
                                  :disabled="scope.row.status!='resolved'?false:true"
                                  :command="{fn:alarmFix,argument0:'fix',argument1:scope.row.id}">
                  {{$t('Alarm.Action.fix')}}
                </el-dropdown-item>
                <el-dropdown-item id="tid_alarm-delete-icon"
                                  :command="{fn:alarmDelete,argument0:'delete',argument1:scope.row.id}">
                  {{$t('Alarm.Action.delete')}}
                </el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </template>
        </el-table-column>
      </composite-table>
    </el-row>
    <!-- dialog comment -->
    <alarm-dialog ref="alarmDialog"/>
  </div>
</template>
<script>
  import CompositeTable from '../component/composite-table'
  import DateRegionPicker from '../component/date-region-picker'
  import AlarmTablelevel from '../widget/alarm-policy-level-label.vue'
  import AlarmDialog from '../widget/alarm-dialog'
  import AlarmService from '../service/alarm'
  import AlarmPolicyService from '../service/alarm-policy'
  import Format from '../common/format'

  export default {
    data() {
      return {
        statusOptions: [],
        policyLevelOptions: [],
        dataFilter: {
          status: {
            values: ['present'],
            type: "in"
          },
          policyLevel: {
            values: [],
            type: "in"
          },
          createTime: {
            values: [new Date(0), new Date('2100/1/1')],
            type: "range"
          }
        },
        dataFilterTemp: {},
        pickerSearchDate: ['', ''],
        dialogNoteVisible: false,
        alarmActionIsDisabled: true,
        comment: '',
        alarmActionIds: [],
        tableDataFetcher: AlarmService.getAlarmTableDataFetcher()
      }
    },
    components: {
      'composite-table': CompositeTable,
      'date-region-picker': DateRegionPicker,
      'alarm-table-level': AlarmTablelevel,
      'alarm-dialog': AlarmDialog
    },
    mounted() {
      AlarmService.AlarmStatusEnums.forEach((item) => {
        this.statusOptions.push({
          value: item,
          label: this.$t('Alarm.Status.' + item)
        });
      })
      AlarmPolicyService.AlarmPolicyLevelEnums.forEach((item) => {
        this.policyLevelOptions.push({
          value: item,
          label: this.$t('Alarm.PolicyLevel.' + item)
        });
      })
      this.Query();
    },
    methods: {
      onAlarmSearchStatusChange(val) {
        this.$refs.dateRegionPicker.clear();
      },
      onAlarmSearchLevelChange(val) {

      },
      onDateChange(pickerDate) {
        var newDate = [];
        newDate[0] = pickerDate[0] ? pickerDate[0] : new Date(0);
        newDate[1] = pickerDate[1] ? pickerDate[1] : new Date();
        this.dataFilter.createTime.values = newDate
      },
      alarmEditComment(alarm) {
        //this.comment = comment;

        this.$refs.alarmDialog.doEdit(alarm).then((res) => {
          // Reload table data
          this.$refs.alarmTable.fetchTableData();
        }, (res) => {
          // Do nothing
        });
      },
      alarmConfirm(command, id) {
        var ids = id != undefined ? [id] : this.alarmActionIds;
        this.$refs.alarmDialog.doConfirm(command, ids, this.dataFilter).then((res) => {
          // Reload table data
          this.$refs.alarmTable.fetchTableData();
        }, (res) => {
          // Do nothing
        });
      },
      alarmFix(command, id) {
        var ids = id != undefined ? [id] : this.alarmActionIds;
        this.$refs.alarmDialog.doFix(command, ids, this.dataFilter).then((res) => {
          // Reload table data
          this.$refs.alarmTable.fetchTableData();
        }, (res) => {
          // Do nothing
        });
      },
      alarmDelete(command, id) {
        var ids = id != undefined ? [id] : this.alarmActionIds;
        this.$refs.alarmDialog.doDelete(command, ids, this.dataFilter).then((res) => {
          // Reload table data
          this.$refs.alarmTable.fetchTableData(true);
        }, (res) => {
          // Do nothing
        });
      },
      alarmAction(command) {
        if (command == 'confirmAll') {
          this.alarmConfirm(command);
        }
        if (command == 'fixAll') {
          this.alarmFix(command);
        }
        if (command == 'deleteAll') {
          this.alarmDelete(command);
        }
      },
      onActionDone(isrefresh) {
        this.$refs.alarmTable.fetchTableData(isrefresh);
      },
      onSelectionChange(selection) {
        this.alarmActionIds = [];
        if (selection.length > 0) {
          selection.forEach((alarm) => {
            this.alarmActionIds.push(alarm.id);
          })
        }
        this.alarmActionIsDisabled = selection.length <= 0 ? true : false
      },
      columnFormatter(row, column) {
        return Format.formatDateTime(row[column.property]);
      },
      onActionCommand(command){
        let fn = command.fn;
        let argument0 = command.argument0;
        let argument1 = command.argument1;
        fn(argument0,argument1);
      },
      Query() {
        this.dataFilterTemp = JSON.parse(JSON.stringify(this.dataFilter));
      }
    }
  }
</script>
