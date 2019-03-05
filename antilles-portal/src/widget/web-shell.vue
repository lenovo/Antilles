<style scoped>
.web-shell .el-row {
	margin-bottom: 10px;
}
</style>
<template>
<div class="web-shell">
  <el-row>
    <el-col :span="24">
      <el-select v-model="hostname">
        <el-option
          v-for="item in nodes"
          :key="item.hostname"
          :label="item.hostname"
          :value="item.hostname">
        </el-option>
      </el-select>
    </el-col>
  </el-row>
  <el-row>
    <div ref="terminalContainer" style="width: 100%; min-width: 300px; min-height: 600px"></div>
  </el-row>
  <web-terminal ref="webTerminal"></web-terminal>
</div>
</template>
<script>
import NodeService from '../service/node'
import WebTerminal from './web-terminal'

export default {
  data() {
    return {
      nodes: [],
      hostname: ''
    }
  },
  components: {
    'web-terminal': WebTerminal
  },
  watch: {
    hostname(val, oldVal) {
      this.openTerminal(val);
    }
  },
  mounted() {
    this.initNodes();
  },
  methods: {
    initNodes() {
      NodeService.getAllNodes('login').then((res) => {
				this.nodes = res
				if(res.length<=0) {
					NodeService.getAllNodes('head').then((res) => {
						this.nodes = res
						if(this.nodes.length > 0) {
		          this.hostname = this.nodes[0].hostname;
		        }
					})
				}
        // res.forEach((node) => {
        //   if(node.type == 'login') {
        //     this.nodes.push(node);
        //   }
        // });
				// // If there is no login node, using head node.
				// if(this.nodes.length <= 0) {
				// 	res.forEach((node) => {
	      //     if(node.type == 'head') {
	      //       this.nodes.push(node);
	      //     }
	      //   });
				// }
        if(this.nodes.length > 0) {
          this.hostname = this.nodes[0].hostname;
        }
      }, (res) => {
        this.$message.error(res);
      });
    },
    openTerminal(hostname) {
      this.$refs.webTerminal.initShell(hostname, this.$refs.terminalContainer);
    },
		autoResizeTerminalWindows() {
			this.$refs.webTerminal.autoResizeTerminalWindows();
		}
  }
}
</script>
