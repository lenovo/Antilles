<style lang="css">
  .gpusView-charts-content {
    /*width: 100%;*/
    padding: 20px;
  }
  .gpusViewNoData {
    padding: 20px 0;
    text-align: center;
  }
  .gpusView-monitor-gpu-chart {
    height: 180px;
  }
  .gpusPagination {
		text-align: center;
	}
</style>
<template lang="html">
  <div class="gpusView-charts-content">
    <p v-if='nodes.length == 0' class="gpusViewNoData">{{$t('NodeGpus.Monitor.No.Data')}}</p>
    <el-row v-else :gutter='20'>
      <el-col class="gpusView-monitor-gpu-chart"
        :lg='3' :md='4' :sm='6' :xs='12'
        v-for='(node, index) in nodes' :key='index'>
          <node-gpu-card ref='nodeGpuCard'
            :node='node'
            :value-type='valueType'
            :value-range='valuesRange'
            :is-reversal='isReversal'>

          </node-gpu-card>
      </el-col>
    </el-row>
    <div class="gpusPagination">
      <el-pagination
         @size-change="handleSizeChange"
         @current-change="handleCurrentChange"
         :current-page="currentPage"
         :page-size="pageSize"
         :total="total"
         layout="prev, pager, next, jumper">
       </el-pagination>
    </div>
  </div>
</template>

<script>
import NodeGpuCard from './node-gpu-card'
export default {
  data() {
    return {
      nodes: [],
      type: this.valueType || 'util',
      total: 0,
      pageSize: 18,
      currentPage: 1,
      valuesRange: this.controlRange || [0, 0],
      isReversal: this.colorInversion
    };
  },
  props: [
    'monitorNodes',
    'valueType',
    'pageOffset',
    'controlRange',
    'colorInversion'
  ],
  components: {
    'node-gpu-card': NodeGpuCard
  },
  mounted() {
    this.init();
  },
  watch: {
    monitorNodes(val, oldVal) {
      this.init();
    },
    controlRange(val, oldVal) {
      this.init();
      this.valuesRange = val;
    },
    colorInversion(val, oldVal) {
      this.init();
      this.isReversal = val;
    },
    pageOffset(val, oldVal) {
      this.init();
      // this.isReversal = val;
    },

  },
  methods: {
    init() {
      this.nodes = this.monitorNodes;
      this.total = this.pageOffset.total;
      this.pageSize = this.pageOffset.pageSize;
      this.currentPage = this.pageOffset.currentPage;
    },
    onOffsetChange() {
      this.$emit('offset-change', {
        total: this.total,
        pageSize: this.pageSize,
        currentPage: this.currentPage
      })
    },
    handleSizeChange(val) {
      this.onOffsetChange();
    },
    handleCurrentChange(val) {
      this.onOffsetChange();
    },
    onResize() {
      this.$nextTick(() => {
        this.$refs.nodeGpuCard.forEach((item) => {
          item.onResize();
        })
      })
    }
  }
}
</script>
