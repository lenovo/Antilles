<style>

</style>
<template>
	<composite-form-dialog ref="innerDialog"
  :title="title" size="500px"
  :form-model="Wechat"
  :form-rules="WechatRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
		<p>{{$t(`AlarmSetting.${mode}.Message`)}}</p>
	</composite-form-dialog>
</template>
<script>
	import ValidRoleFactory from '../../common/valid-role-factory'
	import CompositeFormDialog from '../../component/composite-form-dialog'
	import WechatService from '../../service/notify-wechat'

	export default {
		components:{
			'composite-form-dialog': CompositeFormDialog
		},
		data () {
			return {
				show:true,
				mode: '',
				title:this.$t("AlarmSetting.Button.Test"),
				Wechat:{
					status:'off'
				},
				WechatRules:{

				}
          }

		},
	    methods: {
	    	submitForm(){
	    		if(this.show){
	    			return WechatService.testWechat(this.Wechat);
	    		} else {
	    			return WechatService.updateWechat(this.Wechat);
	    		}
	    	},
		    successMessageFormatter(res) {
		      if(this.show){
		      	return this.$t('AlarmSetting.Wechat.Test.Success');
		      } else {
		      	return this.$t('AlarmSetting.Wechat.Success');
		      }
		    },
		    errorMessageFormatter(res) {
		      var errMsg = res;
		      return this.$t(errMsg);
		    },
		    confirmWechat(config){
		    	this.show = false;
					this.mode = 'Confirm'
		    	this.title = this.$t("AlarmSetting.Button.Confirm.Dialog");
		    	this.Wechat.status = config.status;
		    	return this.$refs.innerDialog.popup(this.submitForm);
		    },
		    test(config){
		    	this.show = true;
					this.mode = 'Test'
		    	this.title = this.$t("AlarmSetting.Button.Test");
		    	this.Wechat.status = config.status;
		    	return this.$refs.innerDialog.popup(this.submitForm);
		    }
	    }
	}
</script>
