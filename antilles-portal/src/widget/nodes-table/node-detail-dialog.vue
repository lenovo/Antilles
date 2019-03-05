<style>

</style>
<template>
  <el-dialog :title="$t('Node.Detail.Title')" width="900px" :visible.sync="dialogVisible">
    <node-panel id="tid_node-detail-panel" :node-id="nodeId" v-if="nodeId > 0" style="min-width: 850px;"></node-panel>
  </el-dialog>
</template>
<script>
import NodePanel from '../node-panel'

export default {
  data() {
    return {
      nodeId: 0,
      dialogVisible: false
    };
  },
  props: [
  ],
  components: {
    'node-panel': NodePanel
  },
  methods: {
    showDetail(nodeId) {
      this.nodeId = nodeId;
      this.dialogVisible = true;
    }
  }
}
</script>
