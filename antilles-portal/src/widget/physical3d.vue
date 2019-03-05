<style media="screen">
  .svg-container {
    margin: 0 auto!important;
  }
  .physical-3d .el-dialog {
    min-width: 450px;
  }
  .block-3d {
    display: block !important;
    height: 450px;
    border: 1px #999 dashed;
  }
  .modebar {
    display: none;
  }
</style>
<template lang="html">
  <el-dialog
    id="tid_popup-dialog"
    ref="popupDialog"
    :title="title"
    center
    :visible.sync="dialogVisible"
    :before-close="onDialogClose"
    :close-on-press-escape="!dialogVisible"
    :close-on-click-modal="!dialogVisible"
    >
    <div ref="container" class="block-3d" v-show="loaded"></div>
  </el-dialog>
</template>

<script>
import MonitorDataService from '../service/monitor-data'
import Format from '../common/format'

export default {
  data() {
    return {
      nodes: null,
      type: '',
      data: [],
      loaded: false,
      name: '',
      timerId: 0,
      interval: 30000,
      dialogVisible: false,
      loading: '',
      title: this.$t("PhysicalView.3D.title")
    }
  },
  created() {
      this.reset();
  },
  props: [
    "mode",
    "nodesData",
    "enableShow"
  ],
  watch: {
    "$route": "reset",
    loaded(newVal, oldVal) {
      var self = this
      if (newVal) {
        this.loading.close()
        this.showChart()
      }
    },
    enableShow(newVal, oldVal) {
      if (newVal) {
        this.dialogVisible = true
        this.$nextTick(() => {
          this.loading = this.$loading({
            lock: true,
            text: this.$t('Topology.Visualization.Loading'),
            background: 'white',
            target: document.querySelector('.block-3d')
          });
        });
        this.nodes = this.nodesData
        this.loaded = false
        this.formatType()
        if (this.mode != 'common') {
          this.formatName()
          this.getData()
        }
      }
    }
  },
  methods: {
    onDialogClose(done) {
      this.reset()
      $jq(".block-3d").html('')
    },
    reset() {
      this.loaded = false
      this.$store.dispatch('settings/setShow3D', false)
      this.dialogVisible = false
    },
    getData() {
      var self = this
      this.data = []
      this.loaded = false
      var node = this.nodes[0]
      this.getNodeData(node, 0)
    },
    showChart() {
      var data = this.data
      var layout = {
        title: '',
				showlegend: true,
				autosize: true,
				width: 500,
				height: 420,
				margin: {
					autoexpand: false,
					l: 0,
					r: 0,
					b: 0,
					t: 0,
					pad: 0
				},
				scene: {
					xaxis: {title: 'x',type:'category'},
					yaxis: {title: 'y',type:'category'},
					zaxis: {title: 'z'}
				}
			}
      Plotly.newPlot(this.$refs.container, data, layout, {showLink: false})
    },
    getNodeData(node, index) {
      var self = this
      var name = self.$t(`Rack.Mode.${self.name}`)
      var x = []
      var y = []
      var z = []
      MonitorDataService.getNodeDataByHour(node.id, self.type, 1).then(res => {
        if (res.data.length == 0) {
          var time = new Date()
          x = [[node.hostname, ' ']]
          y = [[time, time]]
          z = [[0, 0]]
        }
        for (var i = 0; i < res.data.length; i++) {
          var data = res.data[i]
          var d = this.formatData(data, node.hostname)
          x.push(d[0])
          y.push(d[1])
          z.push(d[2])
        }
        var plotlyObj = {
          x: x,
          y: y,
          z: z,
          name: name,
          type: 'surface',
          opacity: 0.9,
          showscale: true
        };
        self.data.push(plotlyObj)
        if (index == (self.nodes.length - 1)) {
          self.loaded = true
        } else {
          index += 1
          node = self.nodes[index]
          self.getNodeData(node, index)
        }
      }, error => {
        self.loading.close()
        self.$message(error)
      })
    },
    formatData(data, name) {
      var formatType = 'hh:mm:ss'
      var time = Format.formatDateTime(data.time, formatType)
      var y_inner = [time, time]
      var x_inner = [name, ' ']
      if (this.mode == 'network') {
        var valueAdd = data.values[0] + data.values[1]
      } else {
        var valueAdd = data.values[0]
      }
      var z_inner = [valueAdd, valueAdd]
      return [x_inner, y_inner, z_inner]
    },
    formatType() {
      var m = this.mode
      var dict = {
        temp: 'temperature',
        mem: 'ram',
        storage: 'disk'
      }
      if (dict[m] != undefined) {
        this.type = dict[m]
      } else {
        this.type = m
      }
    },
    formatName() {
      var m = this.mode
      var dict = {
        temp: 'Temperature',
        mem: 'Memory',
        storage: 'Storage',
        cpu: 'CPU',
        load: 'Load',
        energy: 'Energy',
        network: 'Network'
      }
      if (dict[m] != undefined) {
        this.name = dict[m]
      }
    },
  }
}
</script>
