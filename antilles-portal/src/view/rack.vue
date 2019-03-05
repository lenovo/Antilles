<style scoped>
.rack-top {
  background: #fff;
  margin-bottom: 20px;
  padding: 20px;
}

.rack-top-left-one {
  font-weight: bold;
  font-size: 16px;
}

.rack-top-left-two {
  font-size: 12px;
  color: #999;
  padding-left: 20px;
}

.rack-top-bottom {
  margin-top: 20px;
}

.rack-center-content {
  /* display: flex; */
  /* height: 100%;*/
}

.el-erp-mode-icon {
  margin: 0;
  /*color:#999;*/
}

.el-erp-mode-icon:checked {
  background: #40aaff;
  color: #fff;
}

.rack-right-span {
  color: #40aaff;
}

.rack-top-content {
  margin-bottom: 0;
  padding-bottom: 0;
  width: 100%;
}

.rack-border {
  background: white;
  min-width: 342px;
  margin-right: 20px;
}

.rack-content-inner {
  padding: 16px;
}

.mode-font {
  font-size: 20px;
  font-weight: 600;
}

.el-row.rack {
  margin-bottom: 15px;
  &:last-child {
    margin-bottom: 0;
  }
}

.active {
  color: #40aaff;
  border: 1px #40aaff solid !important;
  border-radius: 5px;
}

.rack-tab {
  padding: 4px 6px;
  border: 1px #dcdfe6 solid;
  border-radius: 5px;
  margin: 5px;
}

.rack {
  display: flex;
}
.mode-font {
  flex-grow: 6;
}
.rack-tab-div {
  flex-grow: 1;
  text-align: right;
  cursor: pointer;
}

</style>
<template>
<div>
<div v-if="rack!=null" class="p-10">
  <el-row class="rack-top">
    <el-col :span="18" class="rack-top-left">
      <span class="rack-top-left-one">{{rack.name}}</span>
      <span class="rack-top-left-two">{{formatLocation(rack.location.rowIndex, rack.location.colIndex)}}</span>
      <div class="rack-top-bottom">
        <el-radio-group v-model="modeSelected" style="color: #999">
          <el-radio-button v-for="mode in modeOptions" :key="mode.value" :label="mode.label" :title="mode.label">
            <i :class="mode.icon" class="el-erp-mode-icon"></i>
          </el-radio-button>
        </el-radio-group>
      </div>
    </el-col>
    <el-col :span="3">
      <span class="rack-right-span">{{formatCount(rack.nodeCount)}}</span>
      <div style="margin-top: 20px;">{{$t('Rack.TotalNodes')}}</div>
    </el-col>
    <el-col :span="3">
      <span class="rack-right-span">{{formatCount(formatEnergy(rack.energy))}}{{$t('MonitorRack.Room.Energy.Unit')}}</span>
      <br>
      <div style="margin-top: 20px;">{{$t('Rack.TotalEnergy')}}</div>
    </el-col>
  </el-row>
  <el-row class="rack-center-content" type='flex'>
    <div class="rack-border">
      <div class="rack-content-inner">
        <el-row class="rack">
          <div class="mode-font">{{this.modeName}}</div>
          <div class='rack-tab-div' :title="$t('Rack.View')" @click="changeType('view')"><i class="el-erp-view rack-tab" :class="{active: type=='view'}"></i></div>
          <div class='rack-tab-div' :title="$t('Rack.Data')" @click="changeType('data')"><i class="el-erp-data rack-tab" :class="{active: type=='data'}"></i></div>
        </el-row>
        <el-row>
          <div v-if="type=='view'" class="">
            <physical-rack class="" :rack-info="rack" :mode="mode" @node-click="onNodeClick"></physical-rack>
          </div>
          <physical-data v-if="type=='data'" :rack-info="rack" :mode="mode" v-on:show3D="changeNodesToShow"></physical-data>
        </el-row>
      </div>
    </div>
    <el-row class="rack-top rack-top-content" >
      <el-row>
        <node-panel v-if="nodeId > 0" :node-id="nodeId"></node-panel>
      </el-row>
    </el-row>
  </el-row>
</div>
<div class="">
  <physical-3d :nodes-data="nodesToShow" :mode="mode" class="physical-3d" :enable-show="this.$store.state.settings.show3D"></physical-3d>
</div>
</div>
</template>
<script>
import PhysicalRack from '../widget/physicalrack'
import RackService from '../service/rack'
import Format from '../common/format'
import NodePanel from '../widget/node-panel'
import PhysicalData from './physical-data'
import Physical3D from '../widget/physical3d'


export default {
  data() {
    return {
      rack: null,
      totalNodes: 0,
      totalEnergy: 0,
      mode: 'common',
      modeSelected: this.$t('Rack.Mode.Common'),
      nodeId: 0,
      levelColors: ['#F6EFA6', '#EFD79B', '#E9BF8F', '#E2A684', '#DB8E79', '#D57B6F', '#D06D66', '#CA605D', '#C55255', '#BF444C'],
      levelRanges: [[0,10],[10,20],[20,30],[30,40],[40,50],[50,60],[60,70],[70,80],[80,90],[90,100]],
      modeOptions: [{
          value: 'common',
          label: this.$t('Rack.Mode.Common'),
          icon: 'el-erp-rack'
        }
        ,
        {
          value: 'temp',
          label: this.$t('Rack.Mode.Temperature'),
          icon: 'el-erp-temperature'
        }
        ,
        {
          value: 'energy',
          label: this.$t('Rack.Mode.Energy'),
          icon: 'el-erp-monitor_power'
        },
        {
          value: 'load',
          label: this.$t('Rack.Mode.Load'),
          icon: 'el-erp-load'
        },
        {
          value: 'cpu',
          label: this.$t('Rack.Mode.CPU'),
          icon: 'el-erp-cpu'
        },
        {
          value: 'mem',
          label: this.$t('Rack.Mode.Memory'),
          icon: 'el-erp-memory'
        },
        {
          value: 'storage',
          label: this.$t('Rack.Mode.Storage'),
          icon: 'el-erp-storage_1'
        },
        {
          value: 'network',
          label: this.$t('Rack.Mode.Network'),
          icon: 'el-erp-network'
        }
        ],
      type: 'view',
      nodesToShow: []
    }
  },
  computed: {
    modeName() {
      var self = this
      var m = this.mode
      var dict = {
        temp: 'Temperature',
        mem: 'Memory',
        storage: 'Storage',
        cpu: 'CPU',
        load: 'Load',
        energy: 'Energy',
        network: 'Network',
        common: 'Common'
      }
      var name = dict[m]
      return this.$t(`Rack.Mode.${name}`)
    }
  },
  components: {
    'physical-rack': PhysicalRack,
    'node-panel': NodePanel,
    'physical-data': PhysicalData,
    'physical-3d': Physical3D,
  },
  mounted() {
    this.init(this.$route.params.id);
  },
  watch: {
    modeSelected(val, oldVal) {
      this.modeOptions.forEach((option) => {
        if (option.label == val) {
          this.mode = option.value;
        }
      });
    }
  },
  methods: {
    init(rackId) {
      RackService.getRackById(rackId).then((res) => {
          this.rack = res;
          if (this.rack.nodes.length > 0) {
            this.onNodeClick(this.rack.nodes[0].id);
          }
        },
        (res) => {
          this.$message.error(res);
        });
    },
    formatLocation(row, column) {
      return this.$t('Rack.Location', {
        row: row,
        column: column
      });
    },
    formatCount(count) {
      return Format.formatCount(count);
    },
    onNodeClick(nodeId) {
      this.nodeId = nodeId;
    },
    changeType(val, oldVal) {
      this.type = val
    },
    changeNodesToShow(nodes) {
      this.$store.dispatch('settings/setShow3D', true)
      this.nodesToShow = nodes
    },
    formatEnergy(energy) {
      return Format.formatEnergy(energy, 1000) // 1000w = 1kw
    }
  }
}
</script>
