<template>
	<composite-form-dialog ref="innerDialog"
  :title="title" size="500px"
  :form-model="vnc"
  :form-rules="vncRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
	</composite-form-dialog>
</template>
<script>
	import ValidRoleFactory from '../../common/valid-role-factory'
	import VNCService from '../../service/vnc'
	import CompositeFormDialog from '../../component/composite-form-dialog'

	export default {
		components:{
			'composite-form-dialog': CompositeFormDialog
		},
		data () {
			return {
				title:this.$t("VNC.Delete.Confirm",{'name': ''}),
				vnc:{
				},
				vncRules:{
				}
          }
		},
	    methods: {
			submitForm(){
	    		return VNCService.deleteVNC(this.vnc.id);
	    	},
		    successMessageFormatter(res) {
		      return this.$t('VNC.Delete.Success');
		    },
		    errorMessageFormatter(res) {
		      var errMsg = res;
		      return this.$t(errMsg);
		    },
		    deleteVNC(data){
		    	this.vnc = data;
		    	this.title = this.$t("VNC.Delete.Confirm",{'name': data.name});
		    	return this.$refs.innerDialog.popup(this.submitForm);
		    }
	    }
	}
</script>
