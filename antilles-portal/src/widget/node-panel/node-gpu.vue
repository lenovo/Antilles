<style lang="css">
.node-gpu-chart {
  height: 200px;
}
.node-gpu-tab tr.current-row>td {
  background: #DFEAF3;
}
</style>

<template lang="html">
  <div class="node-gpu-tab">
    <el-table
      ref='nodeGpuTable'
      :data="tableData"
      :row-key='rowKey'
      highlight-current-row
      :expand-row-keys='expandRowkeys'
      @expand-change='onExpandChange'
      style="width: 100%">
      <el-table-column type="expand">
        <template slot-scope="props">
          <el-row :gutter="10" style="width:800px;">
              <el-col :lg="8" :md="12" :sm="24" :xs="24" class="node-gpu-chart">
                <node-gpu-used :gpu-data='props.row.util.history' ref='nodeGpuUsed'></node-gpu-used>
              </el-col>
              <el-col :lg="8" :md="12" :sm="24" :xs="24" class="node-gpu-chart">
                <node-gpu-memory :gpu-data='props.row.memory.history' ref='nodeGpuMemory'></node-gpu-memory>
              </el-col>
              <el-col :lg="8" :md="12" :sm="24" :xs="24" class="node-gpu-chart">
                <node-gpu-temp :gpu-data='props.row.temperature.history' ref='nodeGpuTemp'></node-gpu-temp>
              </el-col>
          </el-row>
        </template>
      </el-table-column>
      <el-table-column
        :label="$t('NodePanel.GPU.Index')"
        width='100px'
        prop="index">
        <template slot-scope="props">{{"GPU " + props.row.index}}</template>
      </el-table-column>
      <el-table-column
        :label="$t('NodePanel.GPU.Type')"
        prop="type">
      </el-table-column>
      <el-table-column
        :label="$t('NodePanel.GPU.Status')"
        width='140px'
        prop="used">
        <template slot-scope="scope"><node-status-label :status="scope.row.used"/></template>
      </el-table-column>
      <el-table-column
        :label="$t('NodePanel.GPU.Util')"
        width='120px'
        prop="util">
        <template slot-scope="props">{{ props.row.util.current + '%'}}</template>
      </el-table-column>
      <el-table-column
        :label="$t('NodePanel.GPU.Memory')"
        width='120px'
        prop="memory">
        <template slot-scope="props">{{ props.row.memory.current + '%'}}</template>
      </el-table-column>
      <el-table-column
        :label="$t('NodePanel.GPU.Temp')"
        width='120px'
        prop="temperature">
        <template slot-scope="props">{{ props.row.temperature.current + "℃"}}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import NodeStatusLabel from '../node-status-label.vue'
import NodeGpuUsed from './node-gpu/node-gpu-used'
import NodeGpuMemory from './node-gpu/node-gpu-memory'
import NodeGpuTemp from './node-gpu/node-gpu-temperature'
import NodeGpuThumbNail from './node-gpu/node-gpu-thumbnail'
import GpuService from '../../service/monitor-data'
export default {
  data(){
    return {
      tableData: [],
      expandRowkeys: [],
      data: this.node,
      gpus: []
    };
  },
  components: {
    'node-status-label': NodeStatusLabel,
    'node-gpu-used': NodeGpuUsed,
    'node-gpu-memory': NodeGpuMemory,
    'node-gpu-temp': NodeGpuTemp,
    'node-gpu-thumbnail': NodeGpuThumbNail
  },
  props: ['node'],
  mounted() {
    if(this.data != null) {
      this.gpus = this.data.gpus;
      this.refresh();
    }

  },
  watch: {
    node(val, oldVal) {
      if(val != null) {
        this.data = this.node;
        this.gpus = this.data.gpus;
        this.refresh();
      }
    }
  },
  methods: {
    refresh() {
      this.getTableData().then((res) => {
        this.tableData = res;
        // this.expandRowkeys = [res[0].index]
      })
    },
    getTableData() {
      return new Promise((resolve, reject) => {
        var dataReqs = [];
        this.gpus.forEach((item) => {
          dataReqs.push(this.getGpuData(this.data.id, item.index, item.type, item.used));
        })
        Promise.all(dataReqs).then((res) => {
          resolve(res);
        })
      });

    },
    getGpuData(id, index, type, used) {
      var _this = this;
      return new Promise((resolve, reject) => {
        var ramReq = GpuService.getNodeGpuDataByHour(id, index, 'ram');
        var utilReq = GpuService.getNodeGpuDataByHour(id, index, 'util');
        var tempReq = GpuService.getNodeGpuDataByHour(id, index, 'temperature');
        Promise.all([ramReq, utilReq, tempReq]).then((res) => {
          var gpuData = {
            index: index,
            type: type,
            used: used?'busy':'idle',
            memory: {current: _this.formatter(res[0].current), history: res[0].data},
            util: {current: _this.formatter(res[1].current), history: res[1].data},
            temperature: {current: _this.formatter(res[2].current), history: res[2].data}
          };
          resolve(gpuData)
        }, (res) => {
          this.$message.error(res);
        })
      });
    },
    formatter(value) {
      return  Math.round(value * 10) / 10
    },
    rowKey(row) {
      return row.index;
    },
    onExpandChange(row) {
      if (this.expandRowkeys[0] != row.index) {
        this.expandRowkeys = [row.index];
        this.$refs.nodeGpuTable.setCurrentRow(row)
      } else {
        this.expandRowkeys = [];
        this.$refs.nodeGpuTable.setCurrentRow()
      }
    },
    resizeChart() {
      // refresh the node gpus charts
      if(this.gpus.length > 0 && this.tableData.length > 0) {
        this.onResize(this.$refs.nodeGpuUsed);
        this.onResize(this.$refs.nodeGpuMemory);
        this.onResize(this.$refs.nodeGpuTemp);
      }
    },
    onResize(doms) {
      if (doms)
        if(doms.length>1) {
          doms.forEach((dom) => {
            dom.onResize();
          })
        } else {
          doms.onResize();
        }
    }
  }
}
</script>
