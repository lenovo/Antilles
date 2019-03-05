<style>

</style>
<template>
	<composite-form-dialog ref="innerDialog"
  :title="title" size="500px"
  :form-model="SMS"
  :form-rules="SMSRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
		<el-form-item :label="$t('AlarmSetting.SMS.Number')" :prop="show?'number':''" v-if="show">
        	<el-input id="tid_notify-adapter-sms-number" v-model="SMS.number"></el-input>
      </el-form-item>

			<p v-if="!show">{{$t('AlarmSetting.Confirm.Message')}}</p>
	</composite-form-dialog>
</template>
<script>
	import ValidRoleFactory from '../../common/valid-role-factory'
	import CompositeFormDialog from '../../component/composite-form-dialog'
	import SMSService from '../../service/notify-sms'

	export default {
		components:{
			'composite-form-dialog': CompositeFormDialog
		},
		data () {
			return {
				show:true,
				title:this.$t("AlarmSetting.Button.Test"),
				SMS:{
					number:'',
					config:{},
				},
				SMSRules:{
					'number':[
						ValidRoleFactory.getRequireRoleForText(this.$t('AlarmSetting.SMS.Number')),
						ValidRoleFactory.getMobileRole(this.$t('AlarmSetting.SMS.Number'))
					]
				}
          }

		},
	    methods: {
	    	submitForm(){
	    		if(this.show){
	    			return SMSService.testSMS(this.SMS);
	    		} else {
	    			return SMSService.updateSMS(this.SMS.config);
	    		}
	    	},
		    successMessageFormatter(res) {
		      if(this.show){
		      	return this.$t('AlarmSetting.SMS.Test.Success',{'number': this.SMS.number});
		      } else {
		      		return this.$t('AlarmSetting.SMS.Success');
		      }
		    },
		    errorMessageFormatter(res) {
		      var errMsg = res;
		      return this.$t(errMsg);
		    },
		    confirmSMS(config){
		    	this.show = false;
		    	this.title = this.$t("AlarmSetting.Button.Confirm.Dialog");
		    	this.SMS = {
		    		config
		    	};
		    	return this.$refs.innerDialog.popup(this.submitForm);
		    },
		    sendSMS(config){
		    	this.show = true;
		    	this.title = this.$t("AlarmSetting.Button.Test");
		    	this.SMS = {
		    		config
		    	};
		    	return this.$refs.innerDialog.popup(this.submitForm);
		    }
	    }
	}
</script>
