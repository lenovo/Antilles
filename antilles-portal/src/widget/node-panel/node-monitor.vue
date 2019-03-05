<style scoped>
  .col-style {
    height: 200px;
    /*width: 32%;
     border: 1px solid #eee;
    margin-left: 1%; */
    margin-bottom: 10px;
  }
  .node-monitor-chart-style {
    width: 100%;
    height: 100%;
    border: 1px solid #eee;
    box-sizing: border-box
  }
</style>
<template>
<div>
  <el-row :gutter="10">
    <el-col :lg="8" :md="12" :sm="24" :xs="24" class="col-style">
      <node-cpu-chart id="tid_node-monitor-cpu-chart" :node-id="nodeId" :interval="30*1000" ref="chartCpu"></node-cpu-chart>
    </el-col>
    <el-col :lg="8" :md="12" :sm="24" :xs="24" class="col-style">
      <node-load-chart id="tid_node-monitor-load-chart" :node-id="nodeId" :interval="30*1000" ref="chartLoad"></node-load-chart>
    </el-col>
    <el-col :lg="8" :md="12" :sm="24" :xs="24" class="col-style">
      <node-temperature-chart id="tid_node-monitor-temperature-chart" :node-id="nodeId" :interval="30*1000" ref="chartTemp"></node-temperature-chart>
    </el-col>
    <el-col :lg="8" :md="12" :sm="24" :xs="24" class="col-style">
      <node-energy-chart id="tid_node-monitor-energy-chart" :node-id="nodeId" :interval="30*1000" ref="chartEnergy"></node-energy-chart>
    </el-col>
    <el-col :lg="8" :md="12" :sm="24" :xs="24" class="col-style">
      <node-ram-chart id="tid_node-monitor-ram-chart" :node-id="nodeId" :interval="30*1000" ref="chartRam"></node-ram-chart>
    </el-col>
    <el-col :lg="8" :md="12" :sm="24" :xs="24" class="col-style">
      <node-network-chart id="tid_node-monitor-network-chart" :node-id="nodeId" :interval="30*1000" ref="chartNetwork"></node-network-chart>
    </el-col>
    <el-col :lg="8" :md="12" :sm="24" :xs="24" class="col-style">
      <node-disk-chart id="tid_node-monitor-disk-chart" :node="node" ref="chartDisk"></node-disk-chart>
    </el-col>
  </el-row>
  <!--
  <el-row style="margin-top: 15px">

  </el-row>
-->
</div>
</template>
<script>
import NodeCpuChart from './node-monitor/node-cpu-chart'
import NodeLoadChart from './node-monitor/node-load-chart'
import NodeTemperatureChart from './node-monitor/node-temperature-chart'
import NodeEnergyChart from './node-monitor/node-energy-chart'
import NodeRamChart from './node-monitor/node-ram-chart'
import NodeNetworkChart from './node-monitor/node-network-chart'
import NodeDiskChart from './node-monitor/node-disk-chart'

export default {
  components: {
    'node-cpu-chart': NodeCpuChart,
    'node-load-chart': NodeLoadChart,
    'node-temperature-chart': NodeTemperatureChart,
    'node-energy-chart': NodeEnergyChart,
    'node-ram-chart': NodeRamChart,
    'node-network-chart': NodeNetworkChart,
    'node-disk-chart': NodeDiskChart
  },
  props: [
    'nodeId',
    'node'
  ],
  methods: {
    resizeChart() {
      this.$refs.chartDisk.resizeChart();
      this.$refs.chartNetwork.resizeChart();
      this.$refs.chartRam.resizeChart();
      this.$refs.chartEnergy.resizeChart()
      this.$refs.chartTemp.resizeChart()
      this.$refs.chartCpu.resizeChart()
      this.$refs.chartLoad.resizeChart()
    }
  }
}
</script>
