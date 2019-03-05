<style scoped>
  .node-information-line {

  }
  .node-information-line span {
    height: 36px;
    line-height: 36px;
  }
  .width200{
    width: 200px;
  }
  .node-information-item-name {

  }
  .node-information-item-value {

  }
</style>
<template>
<div>
  <el-row type='flex' class="node-information-line">
    <el-col class="node-information-item-name width200">
      <span>{{$t('Node.Type')}}</span>
    </el-col>
    <el-col class="node-information-item-value">
      <span>{{node.type}}</span>
    </el-col>
  </el-row>
  <el-row type='flex' class="node-information-line">
    <el-col class="node-information-item-name width200">
      <span>{{$t('Node.IP.BMC')}}</span>
    </el-col>
    <el-col class="node-information-item-value">
      <span>{{node.bmcIP}}</span>
    </el-col>
  </el-row>
  <el-row type='flex' class="node-information-line">
    <el-col class="node-information-item-name width200">
      <span>{{$t('Node.IP.OS')}}</span>
    </el-col>
    <el-col class="node-information-item-value">
      <span>{{node.osIP}}</span>
    </el-col>
  </el-row>
  <el-row type='flex' class="node-information-line">
    <el-col class="node-information-item-name width200">
      <span>{{$t('Node.CustomGroup')}}</span>
    </el-col>
    <el-col class="node-information-item-value">
      <span>{{node.groups}}</span>
    </el-col>
  </el-row>
  <el-row type='flex' class="node-information-line">
    <el-col class="node-information-item-name width200">
      <span>{{$t('Node.MachineType')}}</span>
    </el-col>
    <el-col class="node-information-item-value">
      <span>{{node.machineType}}</span>
    </el-col>
  </el-row>
</div>
</template>
<script>
export default {
  data() {
    return {
    };
  },
  props: [
    'node'
  ],
  methods: {
    init() {
      this.cpuStatus = {
        total: this.node.cpuTotal,
        used: 0,
        rate: parseInt(0/this.node.cpuTotal*100)
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
