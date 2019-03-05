<template>
	<composite-form-dialog ref="innerDialog"
	:title="title" size="300px"
  :form-model='actionForm'
	:successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
		<div>{{this.getConfirmMessage()}}</div>
	</composite-form-dialog>
</template>

<script>
import CompositeFormDialog from '../../component/composite-form-dialog'
import NodeService from '../../service/node'

export default {
	data() {
		return {
      mode: 'on',
			title: '',
			nodeId: '',
      actionForm: {
        hostname: ''
      },
			nextDevice: null
		}
	},
  components: {
    'composite-form-dialog': CompositeFormDialog
  },
  methods: {
  	submitForm() {
      if (this.mode == 'on') {
        if(this.nodeId instanceof Array) {
					var nodePromiseArr = [];
					this.nodeId.forEach((id) => {
						nodePromiseArr.push(NodeService.powerOnNode(id, this.nextDevice));
					});
					return Promise.all(nodePromiseArr);
        } else {
          return NodeService.powerOnNode(this.nodeId, this.nextDevice);
        }
      }
      if (this.mode == 'off') {
        if(this.nodeId instanceof Array) {
					var nodePromiseArr = [];
					this.nodeId.forEach((id) => {
						nodePromiseArr.push(NodeService.powerOffNode(id, this.nextDevice));
					});
          return Promise.all(nodePromiseArr);
        } else {
          return NodeService.powerOffNode(this.nodeId);
        }
      }
  	},
		getConfirmMessage() {
			if(this.mode == 'on') {
				if(this.nextDevice == 'setup') {
					return this.$t('Node.Action.PowerOn.Setup.Confirm', {'name': this.actionForm.hostname});
				} else if (this.nextDevice == 'network') {
					return this.$t('Node.Action.PowerOn.Network.Confirm', {'name': this.actionForm.hostname});
				} else if (this.nextDevice == 'cd') {
					return this.$t('Node.Action.PowerOn.CD.Confirm', {'name': this.actionForm.hostname});
				} else {
					return this.$t('Node.Action.PowerOn.Confirm', {'name': this.actionForm.hostname});
				}
			} else {
				return this.$t('Node.Action.PowerOff.Confirm', {'name': this.actionForm.hostname});
			}
		},
  	successMessageFormatter(res) {
  		if (this.mode == 'on') {
        return this.$t('Node.Action.PowerOn.Success', {'name': this.actionForm.hostname});
      }
      if (this.mode == 'off') {
        return this.$t('Node.Action.PowerOff.Success', {'name': this.actionForm.hostname});
      }
  	},
  	errorMessageFormatter(res) {
      var errMsg = res;
      return this.$t(errMsg);
    },
    doPowerOn(node, nextDevice) {
      this.mode = 'on';
      this.nodeId = node.id;
			this.nextDevice = nextDevice;
      this.actionForm = {
        hostname: node.hostname
      };
    	this.title = this.$t('Node.Action.PowerOn.Title');
    	return this.$refs.innerDialog.popup(this.submitForm);
    },
    doMultiPowerOn(nodes, nodeList, nextDevice) {
      var nodeName = [];
      nodes.forEach(function(item,index){
        nodeName.push(item.hostname);
      });
      this.mode = 'on';
      this.nodeId = nodeList;
			this.nextDevice = nextDevice;
      this.actionForm = {
        hostname: nodeName.toString()
      };
      this.title = this.$t('Node.Action.PowerOn.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doPowerOff(node) {
      this.mode = 'off';
      this.nodeId = node.id;
      this.actionForm = {
        hostname: node.hostname
      };
      this.title = this.$t('Node.Action.PowerOff.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    },
    doMultiPowerOff(nodes,nodeList){
      var nodeName = [];
      nodes.forEach(function(item,index){
        nodeName.push(item.hostname);
      });
      this.mode = 'off';
      this.nodeId = nodeList;
      this.actionForm = {
        hostname: nodeName.toString()
      };
      this.title = this.$t('Node.Action.PowerOff.Title');
      return this.$refs.innerDialog.popup(this.submitForm);
    }
  }
}
</script>
