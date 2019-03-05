<style>

</style>
<template>
	<composite-form-dialog ref="innerDialog"
  :title="title" size="500px"
  :form-model="mail"
  :form-rules="mailRules"
  :successMessageFormatter="successMessageFormatter"
  :errorMessageFormatter="errorMessageFormatter">
		<el-form-item :label="$t('AlarmSetting.Mail.Mailbox.Sender')" :prop="show?'address':''" v-if="show">
        	<el-input id="tid_notify-adapter-email-sender" v-model="mail.address"></el-input>
      </el-form-item>
			<p v-if="!show">{{$t('AlarmSetting.Confirm.Message')}}</p>
	</composite-form-dialog>
</template>
<script>
	import ValidRoleFactory from '../../common/valid-role-factory'
	import EmailService from '../../service/notify-email'
	import CompositeFormDialog from '../../component/composite-form-dialog'

	export default {
		components:{
			'composite-form-dialog': CompositeFormDialog
		},
		data () {
			return {
				show:true,
				title:this.$t("AlarmSetting.Button.Test"),
				mail:{
					address:'',
					config:{}
				},
				mailRules:{
					'address':[
						ValidRoleFactory.getRequireRoleForText(this.$t('AlarmSetting.Mail.Mailbox.Sender')),
						ValidRoleFactory.getEmailRole(this.$t('AlarmSetting.Mail.Mailbox.Sender'))
					]
				}
          }
		},
	    methods: {
			submitForm(){
				if(this.show){
					return EmailService.testMail(this.mail);
				} else {
					return EmailService.updateMail(this.mail.config);
				}

	    	},
		    successMessageFormatter(res) {
		      if(this.show){
		      	return this.$t('AlarmSetting.Mail.Test.Success',{'number': this.mail.address});
		      } else {
		      	return this.$t('AlarmSetting.Mail.Success');
		      }
		    },
		    errorMessageFormatter(res) {
		      var errMsg = res;
		      return this.$t(errMsg);
		    },
		    confirmSetting(config){
		    	this.show = false;
		    	this.title = this.$t("AlarmSetting.Button.Confirm.Dialog");
		    	this.mail = {
		    		config
		    	};
		    	return this.$refs.innerDialog.popup(this.submitForm);
		    },
		    sendEmail(config){
		    	this.show = true;
		    	this.title = this.$t("AlarmSetting.Button.Test");
		    	this.mail = {
		    		address:'',
		    		config
		    	};
		    	return this.$refs.innerDialog.popup(this.submitForm);
		    }
	    }
	}
</script>
