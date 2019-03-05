<style>
  .pyhsical-table {
    width: 302px;
    padding: 0 !important;
  }
</style>
<template>
  <div>
    <composite-table class="pyhsical-table" id="tid_rack-table-data"
      ref="pyhsicalTable"
      :table-data="data"
      :table-data-fetcher="tableDataFetcher"
      :selection-enable="true"
      @selection-change="onSelectionChange"
      :default-sort="{prop: 'id', order: 'descending' }"
      :search-enable="false"
      :search-props="['id']"
      :current-page="1"
      :page-sizes="[]"
      :page-size="0"
      :total="total"
      :auto-refresh="10*1000">
      <div slot="controller" class="composite-table-controller">
        <el-button id="tid_ai-pyhsical-3D" type="primary" :disabled="!enable3D" @click="on3DClick">{{'3D'}}</el-button>
      </div>
      <el-table-column prop="hostname" :label="this.$t('Rack.Mode.Common')" sortable="custom" align='left' width="80">
      </el-table-column>
      <el-table-column :prop="propName" :label="labelName" sortable="custom" align='right' :width="width">
        <template slot-scope="scope">
          <node-power-status-label v-if="scope.column.property=='status'" :power-status="scope.row.status"></node-power-status-label>
          <span v-else-if="scope.column.property=='network'">{{scope.row.network[0]}}</span>
          <span v-else>{{formatterColumn(scope.row, scope.column)}}</span>
        </template>
      </el-table-column>
      <el-table-column v-if="propName=='network'" prop="network" :label="this.$t('NodeDetail.Network.Out')" sortable="custom" align='left' :width="width">
        <template slot-scope="scope">
          <span>{{scope.row.network[1]}}</span>
        </template>
      </el-table-column>
    </composite-table>
  </div>
</template>
<script>
import CompositeTable from '../component/composite-table'
import RackService from '../service/rack'
import NodePowerStatusLabel from '../widget/node-power-status-label'

export default {
  data() {
    return {
      data: this.rackInfo.nodes,
      tableDataFetcher: '',
      enable3D: false,
      nodes: [],
      total: this.rackInfo.nodes.length
    }
  },
  computed: {
    labelName() {
      var m = this.mode
      var dict = {
        temp: 'Temperature',
        mem: 'Memory',
        storage: 'Storage',
        cpu: 'CPU',
        load: 'Load',
        energy: 'Energy',
        network: 'Network',
        common: 'Common.status'
      }
      var name = dict[m]
      if (name == 'Network') {
        return this.$t("NodeDetail.Network.In")
      }
      return this.$t(`Rack.Mode.${name}`)
    },
    propName() {
      var m = this.mode
      var dict = {
        temp: 'temperature',
        mem: 'memoryUsed',
        storage: 'diskUsed',
        cpu: 'cpuUsed',
        load: 'load',
        energy: 'energy',
        network: 'network',
        common: 'status'
      }
      var name = dict[m]
      return name
    },
    width() {
      var w = 160
      if (this.mode == 'network') {
        w = 80
      }
      return w
    }
  },
  components: {
    'composite-table': CompositeTable,
    'node-power-status-label': NodePowerStatusLabel,
  },
  props: [
    'mode',
    'rackInfo'
  ],
  watch: {
    mode(val, oldVal) {
      this.data = this.rackInfo.nodes
      this.enable3D = (val != 'common') && (this.nodes.length > 0)
    }
  },
  methods: {
    onSelectionChange(selection) {
      var nodes = []
      if (selection.length > 0){
        selection.forEach(node => {
          nodes.push(node);
        })
      }
      this.nodes = nodes
      this.enable3D = selection.length > 0 && (this.mode != 'common')
    },
    formatterColumn(row, column) {
      var unitKey = column.property
      var percent = ['cpuUsed', 'diskUsed', 'memoryUsed', 'load']
      var dict = {
        temperature: ' ℃',
        energy: ' W',
        percent: ' %'
      }
      var value = row[unitKey]
      if (percent.includes(unitKey)){
        unitKey = 'percent'
      }
      if (dict[unitKey]) {
        value += dict[unitKey]
      } else if (unitKey == 'network') {
        let [x, y] = value.split(',')
        value = `In: ${x} Out: ${y}`
      }
      return value
    },
    on3DClick() {
      this.$emit('show3D', this.nodes)
    }
  }
}
</script>
