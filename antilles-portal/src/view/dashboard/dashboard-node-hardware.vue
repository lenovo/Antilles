<style scoped>

  .node-panel-card {
    padding: 10px;
  }
  .node-panel .cell span {
    display: block;
  }
  .node-panel .cell {
    background: #fff;
    padding: 20px;
    display: flex;
  }
  .node-panel .cell-card {
    background: #fff;
    padding: 20px;
  }
  .node-panel .cell-card ul{
    width: 50%;
  }
  .node-panel .cell-card .cell-top  {
    margin-bottom: 20px;
  }
  .node-panel .cell-card li {
    display: flex;
  }
  .node-panel .cell-card li .cell-title{
    display: block;
    flex-shrink: 0;
    width: 140px;
  }
  .node-panel .cell-card li .cell-logo{
    display: block;
    flex-shrink: 0;
    width: 16px;
  }
  .node-panel .cell-card li span+span, .node-panel .cell-card li span+div {
    display: block;
    width: 100%;
    text-align: right;
  }
  .node-panel .cell li span:first-child {
    margin-bottom: 20px;
  }
  .cell-icon{
    height: 20px;
    width: 20px;
    color:#5fb4f9;
  }
  .cell-content-icon-null{
    color: #CCCCCC;
  }
  .cell-content-icon-notnull{
    color: #5FB4F9;
  }
  .cell-content-span{
    display: inline;
  }
  .cel-content-cpu {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .dashboard-hardware-nodata {
    text-align: center;
    height: 58px;
    line-height: 58px;
    font-size: 20px;
  }
</style>
<template>
  <el-row id="tid_dashboard-node-hardware" class="node-panel">
    <el-col :xs="24" :sm="12" :md="12" :lg="6" class="node-panel-card">
      <div v-if='!initData' v-loading='true' class="cell-card dashboard-hardware-nodata"></div>
      <div v-else class="cell-card" style="display:flex;">
        <ul class="" style="flex-grow: 1;">
          <li class="cell-top">
            <span class="cell-title" style="width:55px;">{{$t('Hardware.CPU')}}</span>
            <span class="cell-rate">{{ $t('Dashboard.Unit.%',{'value': cpuStatus.rate})}}</span>
          </li>
          <li class="cell-bottom">
            <span class="cell-logo logo-cpu"><i class="el-erp-cpu cell-icon"></i></span>
            <span class="cell-content cell-content-cpu">{{ cpuStatus.used }}/{{ cpuStatus.total }} {{$t('Unit.CPU')}}</span>
          </li>
        </ul>
        <ul  v-if='gpuStatus && gpuStatus.total>0' style="margin-left:20px">
          <li class="cell-top">
            <span class="cell-title" style="width:55px;">{{$t('Hardware.GPU')}}</span>
            <span class="cell-rate">{{ $t('Dashboard.Unit.%',{'value': gpuStatus.rate})}}</span>
          </li>
          <li class="cell-bottom">
            <span class="cell-logo logo-cpu"><i class="el-erp-GPU cell-icon"></i></span>
            <span class="cell-content">{{ gpuStatus.used }}/{{ gpuStatus.total }} {{$t('Unit.GPU')}}</span>
          </li>
        </ul>
      </div>
    </el-col>
    <el-col :xs="24" :sm="12" :md="12" :lg="6"  class="node-panel-card">
      <div v-if='!initData' v-loading='true' class="cell-card dashboard-hardware-nodata"></div>
      <ul v-else class="cell-card">
        <li class="cell-top">
          <span class="cell-title">{{$t('Hardware.RAM')}}</span>
          <span class="cell-rate">{{ $t('Dashboard.Unit.%',{'value': memoryStatus.rate})}}</span>
        </li>
        <li class="cell-bottom">
          <span class="cell-logo logo-ram"><i class="el-erp-memory cell-icon"></i></span>
          <span class="cell-content">{{ memoryStatus.used }}/{{ memoryStatus.total }}</span>
        </li>
      </ul>
    </el-col>
    <el-col :xs="24" :sm="12" :md="12" :lg="6"  class="node-panel-card">
      <div v-if='!initData' v-loading='true' class="cell-card dashboard-hardware-nodata"></div>
      <ul v-else class="cell-card">
        <li class="cell-top">
          <span class="cell-title">{{$t('Hardware.Disk')}}</span>
          <span class="cell-rate">{{ $t('Dashboard.Unit.%',{'value': diskStatus.rate})}}</span>
        </li>
        <li class="cell-bottom">
          <span class="cell-logo logo-disk"><i class="el-erp-storage cell-icon"></i></span>
          <span class="cell-content">{{ diskStatus.used }}/{{ diskStatus.total }}</span>
        </li>
      </ul>
    </el-col>
    <el-col :xs="24" :sm="12" :md="12" :lg="6"  class="node-panel-card">
      <div v-if='!initData' v-loading='true' class="cell-card dashboard-hardware-nodata"></div>
      <ul v-else class="cell-card">
        <li class="cell-top">
          <span class="cell-title" style="width:90px;">{{$t('Hardware.Network')}}</span>
          <div>
            <span class="cell-content-span" style="font-size:12px;">{{ $t('Dashboard.Unit.Second',{'value':networkStatus.in}) }}</span>
            <i class="el-erp-write cell-content-icon" :title="$t('Hardware.Network.In')" :class="getNetworkIconColor(networkStatus.in)"></i>
          </div>
        </li>
        <li class="cell-bottom">
          <span class="cell-logo logo-network"><i class="el-erp-network cell-icon"></i></span>
          <div>
            <span class="cell-content-span" style="font-size:12px;">{{ $t('Dashboard.Unit.Second',{'value':networkStatus.out}) }}</span>
            <i class="el-erp-read cell-content-icon" :title="$t('Hardware.Network.Out')" :class="getNetworkIconColor(networkStatus.out)"></i>
          </div>
        </li>
      </ul>
    </el-col>
  </el-row>
</template>
<script>
import Format from '../../common/format'
export default {
  data() {
    return {
      span: 6,
      cpuStatus: null,
      gpuStatus: null,
      memoryStatus: null,
      diskStatus: null,
      networkStatus: null
    };
  },
  props: [
    'initData'
  ],
  mounted() {
    if(this.initData) {
      this.init()
    }
  },
  watch: {
    initData(val, oldVal) {
      if(val) {
        this.init()
      }
    }
  },
  methods: {
    init() {
      this.networkStatus = {
        in: Format.formatByteSize(this.initData.networkStatus.in, 'mb'),
        out: Format.formatByteSize(this.initData.networkStatus.out, 'mb')
      }
      this.cpuStatus = {
        total: this.initData.cpuStatus.total,
        used: this.initData.cpuStatus.used,
        rate: parseInt(this.initData.cpuStatus.used/this.initData.cpuStatus.total*100) || 0
      }
      this.gpuStatus = {
        total: this.initData.gpuStatus.total,
        used: this.initData.gpuStatus.used,
        rate: parseInt(this.initData.gpuStatus.used/this.initData.gpuStatus.total*100) || 0
      }
      this.memoryStatus = {
        total: Format.formatByteSize(this.initData.memoryStatus.total * Math.pow(2, 10)),
        used: Format.formatByteSize(this.initData.memoryStatus.used * Math.pow(2, 10)),
        rate: (this.initData.memoryStatus.used/this.initData.memoryStatus.total*100).toFixed(2)
      }
      this.diskStatus = {
        total: Format.formatByteSize(this.initData.diskStatus.total * Math.pow(2, 30)),
        used: Format.formatByteSize(this.initData.diskStatus.used * Math.pow(2, 30)),
        rate: (this.initData.diskStatus.used/this.initData.diskStatus.total*100).toFixed(2)
      }

    },
    format(number) {
      return Format.formatCount(number);
    },
    getNetworkIconColor(num){
      if(parseFloat(num) > 0) {
        return 'cell-content-icon-notnull';
      } else {
        return 'cell-content-icon-null';
      }
    }
  }
}
</script>
