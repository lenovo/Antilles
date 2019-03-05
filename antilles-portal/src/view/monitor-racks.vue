<style>
  .MonitorRoomContainer{
    background-color: #ffffff;
    padding: 20px;
  }
  .MonitorRowContainer{
    margin-top:20px;
  }
  .RowList{
    background-color: #ffffff;
    padding: 20px;
  }
  .RackList{
    margin-left: 20px;
    background-color: #ffffff;
    padding: 20px;
  }
  .RowItem{
    border-radius: 5px;
    /*background-color: #f8f8f8;*/
    /*color: #000000;*/
    border: 0px #000000 solid;
    margin-bottom: 10px;
    width:100%;
  }
  .rowInfo{
    text-align: center;
    padding-top:10px;
  }
</style>
<template>
    <div class="p-10">
      <el-row :span="24" type="flex" justify="space-between" v-for="(room,index) in rooms" :key="index" class="MonitorRoomContainer">
        <el-col :span="16">
          <el-row id="tid_monitor-racks-roomname"><h3>{{room.roomName}}</h3></el-row>
          <el-row style="margin-top: 20px;">
            <el-col id="tid_monitor-racks-location" :span="8"><img src="./../asset/image/monitor/monitor_house.png"/> <span>{{room.location}}</span></el-col>
            <el-col id="tid_monitor-racks-nodes":span="8"><img src="./../asset/image/monitor/monitor_node.png"/> <span>{{room.nodeNumber}}</span><span style="padding-left: 5px;">{{$t("MonitorRack.Room.Node.Unit")}}</span></el-col>
            <el-col id="tid_monitor-racks-energy":span="8"><img src="./../asset/image/monitor/monitor_power.png"/> <span>{{roomEnergy}}</span><span style="padding-left: 5px;">{{$t("MonitorRack.Room.Energy.Unit")}}</span></el-col>
          </el-row>
        </el-col>
        <el-col :span="8">
        </el-col>
      </el-row>
      <el-row :span="24" type="flex" justify="space-between" class="MonitorRowContainer">
        <el-col id="tid_monitor-racks-row-list" :span="7" class="RowList">
          <div v-for="(row,rowIndex) in rows" :key="rowIndex">
            <el-button class="RowItem" @click="onSelectRowItem(row.rowId)"
              :type="row.rowId == currentRowId ? 'primary' : 'normal'">
              <el-row>
                <el-col :span="8">
                  <div class="rowInfo">
                    <h3>{{row.rowName}}</h3>
                  </div>
                </el-col>
                <el-col :span="5">
                  <div>{{row.totalRacks}}</div>
                  <div style="margin-top:5px;">{{$t("MonitorRack.RowList.Rack")}}</div>
                </el-col>
                <el-col :span="5">
                  <div>{{row.totalNode}}</div>
                  <div style="margin-top:5px;">{{$t("MonitorRack.RowList.Node")}}</div>
                </el-col>
                <el-col :span="5">
                  <div>{{formatEnergy(row.totalEnergy)}} {{$t("MonitorRack.Room.Energy.Unit")}}</div>
                  <div style="margin-top:5px;">{{$t("MonitorRack.RowList.Energy")}}</div>
                </el-col>
              </el-row>
            </el-button>
          </div>
        </el-col>
        <el-col :span="17" class="RackList">
          <div style="display: flex;flex-wrap: wrap;">
            <div id="tid_monitor-racks-rack-thumbnail-list" style="margin-right: 20px;margin-top:10px;" v-for="rack in racks" @click="redirectToRackDetail(rack.rackId)">
              <rack-thumbnail height='240px' width='96px'
                 notify_num="" :nodes="rack.nodeNumber" :energy="rack.energy" :used-number="rack.usedNumber" :off-number="rack.offNumber" :busy-number="rack.busyNumber" :free-number="rack.freeNumber" :rack-name="rack.rackName">
              </rack-thumbnail>
            </div>
          </div>
        </el-col>
      </el-row>

    </div>
</template>

<script>
  import RackThumbnail from '../widget/rack-thumbnail'
  import RoomService from '../service/room'
  import Format from './../common/format'
  export default {
    data() {
      return {
        rooms: [],
        rows: [],
        racks: [],
        roomEnergy: '',
        currentRowId: null,
        refreshTimeout: null,
        refreshInterval: 30000
      }
    },
    components: {
      "rack-thumbnail": RackThumbnail
    },
    mounted(){
      this.getRooms();
      this.getRows();
    },
    beforeDestroy() {
			clearTimeout(this.refreshTimeout);
		},
    watch: {
      "currentRowId": function (newRowId) {
        this.getRacks(newRowId);
      },
      rows(val, oldVal) {
        var roomEnergy = 0;
        val.forEach((row) => {
          roomEnergy += row.totalEnergy
        });
        this.roomEnergy = this.formatEnergy(roomEnergy);
      }
    },
    methods: {
      getRooms(){
        RoomService.getAllRooms().then((res) => {
          this.rooms = res.data;
        })
      },
      getRows(){
        RoomService.getAllRowListItems().then((res) => {
          if(res.data.length>0){
            this.rows = res.data;
            this.currentRowId = this.currentRowId?this.currentRowId:this.rows[0].rowId;
            this.refreshTimeout = setTimeout(() => {
              this.getRooms();
              this.getRows();
              this.getRacks(this.currentRowId);
            },this.refreshInterval)
          }
        })
      },
      getRacks(rowId){
        RoomService.getAllRacksByRowId(rowId).then((res) => {
          this.racks = res.data;
        })
      },
      onSelectRowItem(rowId){
        this.currentRowId = rowId;
      },
      redirectToRackDetail(rackId){
        let path = './rack/' + rackId;
        this.$router.push(path);
      },
      formatEnergy(energy) {
        return Format.formatEnergy(energy, 1000) //1000w = 1kW
      }
    }
  }
</script>
