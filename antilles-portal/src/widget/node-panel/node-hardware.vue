<style scoped>
  .node-panel .cell span {
    display: block;
  }
  .node-panel .cell {
    background: #fff;
    padding: 20px;
  }
  .node-panel .cell li span:first-child {
    margin-bottom: 20px;
  }
  .node-panel .cell .cell-left {
    width: 120px;
  }
  .node-panel .cell .cell-right {
    width: 100%;
  }
  .node-panel .cell .cell-right span {
    text-align: right;
  }
  .cpuStatus-icon{
    display: block;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #5fb4f9;
    position: relative;
  }
  .cpuStatus-icon i{
    color: #fff;
    position: absolute;
    left: 5px;
    top:3px;
    font-size: 20px;
  }

  .node-panel-div{
    display: flex;
    padding:20px 10px;
    align-items: center;
    height:100px;
    box-sizing: border-box;
  }
  .node-panel-div-icon{
    width: 25%;
  }
  .cell-right{
    margin-top: 10px;
  }
</style>
<template>
  <el-row class="node-panel">
    <el-col v-if='cpuStatus' :lg="6" :md="8" :sm="24" :xs="24">
        <div class="node-panel-div">
          <div class="node-panel-div-icon">
            <span class="cpuStatus-icon"><i class="el-erp-cpu"></i></span>
          </div>
          <ul >
            <li class="cell-left">
              <span class="cell-title">{{$t('Hardware.CPU')}}</span>
              <span class="cell-logo logo-cpu"></span>
            </li>
            <li class="cell-right">
              <span class="cell-content">{{ cpuStatus.total }} {{$t('Unit.CPU')}}</span>
            </li>
          </ul>
        </div>
    </el-col>


    <el-col v-if='node.powerStatus == "off" || (gpuStatus && gpuStatus.total && gpuStatus.total>0)' :lg="6" :md="8" :sm="24" :xs="24">
        <div class="node-panel-div">
          <div class="node-panel-div-icon">
            <span class="cpuStatus-icon"><i class="el-erp-GPU"></i></span>
          </div>
          <ul >
            <li class="cell-left">
              <span class="cell-title">{{$t('Dashboard.NodeGroupStatus.Group.gpu')}}</span>
              <span class="cell-logo logo-cpu"></span>
            </li>
            <li class="cell-right">
              <span class="cell-content">{{ gpuStatus.total }} {{$t('Unit.GPU')}}</span>
            </li>
          </ul>
        </div>
    </el-col>


    <el-col v-if='memoryStatus' :lg="6" :md="8" :sm="24" :xs="24">
    <div class="node-panel-div">
          <div class="node-panel-div-icon">
            <span class="cpuStatus-icon"><i class="el-erp-memory"></i></span>
          </div>
        <ul  >
          <li class="cell-left">
            <span class="cell-title">{{$t('Hardware.RAM')}}</span>
            <span class="cell-logo logo-ram"></span>
          </li>
          <li class="cell-right">
           <!--  <span class="cell-rate">{{ memoryStatus.rate + '%'}}</span> -->
            <span class="cell-content">{{ memoryStatus.used }}/{{ memoryStatus.total }}</span>
          </li>
        </ul>
        </div>
    </el-col>
    <el-col v-if='diskStatus' :lg="6" :md="8" :sm="24" :xs="24">
    <div class="node-panel-div">
          <div class="node-panel-div-icon">
            <span class="cpuStatus-icon"><i class="el-erp-storage"></i></span>
          </div>
        <ul >
          <li class="cell-left">
            <span class="cell-title">{{$t('NodePanel.Disk')}}</span>
            <span class="cell-logo logo-disk"></span>
          </li>
          <li class="cell-right">
            <!-- <span class="cell-rate">{{ diskStatus.rate + '%'}}</span> -->
            <span class="cell-content">{{ diskStatus.used }}/{{ diskStatus.total }}</span>
          </li>
        </ul>
        </div>
    </el-col>
  </el-row>
</template>
<script>
import Format from '../../common/format'
export default {
  data() {
    return {
      cpuStatus: null,
      gpuStatus:null,
      memoryStatus: null,
      diskStatus: null
    };
  },
  props: [
    'node'
  ],
  mounted() {
    this.init();
  },
  methods: {
    init() {
      this.cpuStatus = {
        total: this.node.cpuTotal,
        used: 0,
        rate: parseInt(0/this.node.cpuTotal*100)
      }
      this.gpuStatus = {
        total: this.node.gpus.length,
        used: 0,
        rate: parseInt(0)
      }
      this.memoryStatus = {
        total: Format.formatByteSize(this.node.ramTotal),
        used: Format.formatByteSize(this.node.ramUsed),
        rate: parseInt(this.node.ramUsed/this.node.ramTotal*100)
      }
      this.diskStatus = {
        total: Format.formatByteSize(this.node.diskTotal),
        used: Format.formatByteSize(this.node.diskUsed),
        rate: parseInt(this.node.diskUsed/this.node.diskTotal*100)
      }

    },
    format(number) {
      return Format.formatCount(number);
    }
  }
}
</script>
