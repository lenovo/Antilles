<style>
.notify-email-ssl{
	margin: 20px 0 20px;
}
</style>
<template>
	<div>
		<el-row>
			<el-col :span="24">
				<div class="section">
					<el-form :model="mail" :rules="mailRules" ref="mail" class="notify-email-form" label-width="130px">
						<el-radio-group id="tid_notify-adapter-email-enable" v-model="mail.status" :disabled="disabled" class="notify-email-radio notify-header-radio" size="mini" @change="changeStatus()">
							<el-radio-button label="on">ON</el-radio-button>
							<el-radio-button label="off">OFF</el-radio-button>
						</el-radio-group>
						<div class="notify-email-img">
							<img src="./../../asset/image/notify/mail.png" alt="">
							<div>{{$t('AlarmSetting.Title.Mail')}}</div>
						</div>

						<el-form-item label="SSL" class="notify-email-ssl">
							<el-radio id="tid_notify-adapter-email-mode-null" class="radio" v-model="mail.ssl" label="0" :disabled="mail.status == 'off'" style="margin-left: 0px;">{{$t('AlarmSetting.Mail.SSL.Null')}}</el-radio>
							<el-radio id="tid_notify-adapter-email-mode-ssl" class="radio" v-model="mail.ssl" label="SSL" :disabled="mail.status == 'off'" style="margin-left: 0px;">SSL</el-radio>
							<el-radio id="tid_notify-adapter-email-mode-tls" class="radio" v-model="mail.ssl" label="TLS" :disabled="mail.status == 'off'" style="margin-left: 0px;">TLS</el-radio>
						</el-form-item>

						<el-form-item :label="$t('AlarmSetting.Label.Mail.Name')" prop="id">
							<el-input id="tid_notify-adapter-email-smtp-name" v-model="mail.id" :placeholder="$t('AlarmSetting.Mail.ID')" :disabled="mail.status == 'off'"></el-input>
						</el-form-item>
						<el-form-item :label="$t('AlarmSetting.Label.Mail.Password')" prop="password">
							<el-input id="tid_notify-adapter-email-smtp-password" type="password" v-model="mail.password" :placeholder="$t('AlarmSetting.Mail.Password')" :disabled="mail.status == 'off'"></el-input>
						</el-form-item>
						<el-form-item  :label="$t('AlarmSetting.Label.Mail.SMTPAddress')" prop="address">
							<el-input id="tid_notify-adapter-email-smtp-address" v-model="mail.address" :placeholder="$t('AlarmSetting.Mail.Address')" :disabled="mail.status == 'off'"></el-input>
						</el-form-item>
						<el-form-item :label="$t('AlarmSetting.Label.Mail.SMTPPort')" prop="port">
							<el-input id="tid_notify-adapter-email-smtp-port" v-model="mail.port" :placeholder="$t('AlarmSetting.Mail.Port')" :disabled="mail.status == 'off'"></el-input>
						</el-form-item>
						<el-form-item :label="$t('AlarmSetting.Mail.Sender')" prop="mailbox">
							<el-input id="tid_notify-adapter-email-sender" v-model="mail.mailbox" :placeholder="$t('AlarmSetting.Mail.Mailbox')" :disabled="mail.status == 'off'"></el-input>
						</el-form-item>
						<div style="text-align: center;margin-bottom:22px;">
							<el-button id="tid_notify-adapter-email-test" type="primary" @click="testMail('mail')" :disabled="test">{{$t("AlarmSetting.Button.Test")}}</el-button>
							<el-button id="tid_notify-adapter-email-confirm" type="primary" @click="confirmMail('mail')" :disabled="disabled">{{$t("AlarmSetting.Button.Confirm")}}</el-button>
						</div>
					</el-form>
				</div>
			</el-col>
		</el-row>
		<EmailDialog ref="TestEmailDialog" />
	</div>
</template>
<script>
	import ValidRoleFactory from '../../common/valid-role-factory'
	import EmailService from '../../service/notify-email'
	import EmailDialog from "./notify-adapter-email-dialog"

	export default {
		components:{
			EmailDialog
		},
		data () {
			return {
				disabled:false,
				test:false,
				mail:{
					status:'off',
					ssl:'0',
					id:'',
					password:'',
					address:'',
					port:'',
					mailbox:''
				},
				mailRules:{
					'id':[ValidRoleFactory.getRequireRoleForText(this.$t('AlarmSetting.Mail.ID.Promot'))],
					'password':[
					ValidRoleFactory.getRequireRoleForText(this.$t('AlarmSetting.Mail.Password.Promot'))
						],
					'address':[
					ValidRoleFactory.getRequireRoleForText(this.$t('AlarmSetting.Mail.Address.Promot'))
						],
					'port':[
					ValidRoleFactory.getRequireRoleForText(this.$t('AlarmSetting.Mail.Port.Promot')),
					ValidRoleFactory.getValidNumberRoleForText(this.$t('AlarmSetting.Mail.Port.Promot'))
						],
					'mailbox':[
					ValidRoleFactory.getRequireRoleForText(this.$t('AlarmSetting.Mail.Mailbox.Promot')),
					ValidRoleFactory.getEmailRole(this.$t('AlarmSetting.Mail.Mailbox.Promot'))
						]
				}
          }
		},
		mounted(){
			var $this = this;
			EmailService.getNotifyEmail().then(function(res){
				$this.mail.status = res.status;
				$this.mail.ssl = res.ssl;
				$this.mail.id = res.id;
				$this.mail.password = res.password;
				$this.mail.address = res.address;
				$this.mail.port = res.port;
				$this.mail.mailbox = res.mailbox;
				$this.changeStatus();
				if($this.mail.status == 'off'){
					$this.test = true;
				} else {
					$this.test = false;
				}
			},function(error){
				$this.test = true;
				$this.disabled = true;
			});
		},
	    methods: {
			testMail(formName){
				var $this = this;
				this.$refs[formName].validate(function(valid){
					if(valid){
						$this.$refs.TestEmailDialog.sendEmail($this.mail);
					}
				});
			},
			changeStatus(){
					if(this.mail.status == 'off'){
						this.mailRules.id=[];
						this.mailRules.password=[];
						this.mailRules.address=[];
						this.mailRules.port=[];
						this.mailRules.mailbox=[];
					} else {
						this.mailRules.id=[
							ValidRoleFactory.getRequireRoleForText(this.$t('AlarmSetting.Mail.ID.Promot'))
						];
						this.mailRules.password=[
							ValidRoleFactory.getRequireRoleForText(this.$t('AlarmSetting.Mail.Password.Promot'))
						];
						this.mailRules.address=[
							ValidRoleFactory.getRequireRoleForText(this.$t('AlarmSetting.Mail.Address.Promot'))
						];
						this.mailRules.port=[
							ValidRoleFactory.getRequireRoleForText(this.$t('AlarmSetting.Mail.Port.Promot')),
							ValidRoleFactory.getValidNumberRoleForText(this.$t('AlarmSetting.Mail.Port.Promot'))
						];
						this.mailRules.mailbox=[
							ValidRoleFactory.getRequireRoleForText(this.$t('AlarmSetting.Mail.Mailbox.Promot')),
							ValidRoleFactory.getEmailRole(this.$t('AlarmSetting.Mail.Mailbox.Promot'))
						];
					}
				},
			confirmMail(formName){
				var $this = this;
				this.$refs[formName].validate(function(valid){
					if(valid || $this.mail.status == 'off'){
						$this.$refs.TestEmailDialog.confirmSetting($this.mail).then(function(res){
							EmailService.getNotifyEmail().then(function(res){
								$this.mail.status = res.status;
								$this.mail.ssl = res.ssl;
								$this.mail.id = res.id;
								$this.mail.password = res.password;
								$this.mail.address = res.address;
								$this.mail.port = res.port;
								$this.mail.mailbox = res.mailbox;
								if($this.mail.status == 'off'){
									$this.test = true;
								} else {
									$this.test = false;
								}
							},function(error){
								$this.disabled = true;
							});
						},function(error){

						});
					}
				});
			}
	    }
	}
</script>
