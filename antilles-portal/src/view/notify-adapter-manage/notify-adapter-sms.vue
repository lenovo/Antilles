<style>
</style>
<template>
	<div>
		<el-row>
			<el-col :span="24">
				<div class="section">
					<el-form :model="SMS" :rules="SMSRules" ref="SMS" label-width="140px">
						<el-radio-group id="tid_notify-adapter-sms-enable" v-model="SMS.status" :disabled="disabled" class="notify-email-radio notify-header-radio" size="mini">
							<el-radio-button label="on" >ON</el-radio-button>
							<el-radio-button label="off">OFF</el-radio-button>
						</el-radio-group>
						<div class="notify-email-img">
							<img src="./../../asset/image/notify/sms.png" alt="">
							<div>{{$t('AlarmSetting.Title.SMS')}}</div>
						</div>

						<el-form-item :label="$t('AlarmSetting.SMS.Port')" style="margin-top: 20px">
					        <el-select id="tid_notify-adapter-sms-port" v-model="SMS.port" :disabled="SMS.status == 'off'">
					            <el-option
					      v-for="item in portList"
					      :key="item"
					      :label="item"
					      :value="item"></el-option>
					          </el-select>
					      </el-form-item>
					      <el-form-item :label="$t('AlarmSetting.SMS.Modem')">
					        <el-select id="tid_notify-adapter-sms-modem" v-model="SMS.modem" :disabled="SMS.status == 'off'">
					            <el-option
					      v-for="item in modemList"
					      :key="item"
					      :label="item"
					      :value="item"></el-option>
					          </el-select>
					      </el-form-item>
					      <el-form-item :label="$t('AlarmSetting.SMS.Limit')">
					        <el-select id="tid_notify-adapter-sms-limit" v-model="SMS.limit" :disabled="SMS.status == 'off'">
					            <el-option
					      v-for="item in limitList"
					      :key="item"
					      :label="item"
					      :value="item"></el-option>
					          </el-select>
					      </el-form-item>
					      <el-form-item :label="$t('AlarmSetting.SMS.Limit.Sended')">
					        <label>{{SMS.number}}</label>
					      </el-form-item>
					    <!--   <el-form-item :label="$t('AlarmSetting.SMS.Number')" prop="number">
							<el-input v-model="SMS.number" :placeholder="$t('AlarmSetting.SMS.Number')" :disabled="SMS.status == 'off'"></el-input>
						</el-form-item> -->
						<div style="text-align: center;margin-bottom:22px;">
							<el-button id="tid_notify-adapter-sms-test" type="primary" @click="testSMS('SMS')" :disabled="test">{{$t("AlarmSetting.Button.Test")}}</el-button>
							<el-button id="tid_notify-adapter-sms-confirm" type="primary" @click="confirmSMS('SMS')" :disabled="disabled">{{$t("AlarmSetting.Button.Confirm")}}</el-button>
						</div>
					</el-form>
				</div>
			</el-col>
		</el-row>
		<SMSDialog ref="TestSMSDialog" />
	</div>
</template>
<script>
	import ValidRoleFactory from '../../common/valid-role-factory'
	import SMSService from '../../service/notify-sms'
	import SMSDialog from './notify-adapter-sms-dialog'

	export default {
		components:{
			SMSDialog
		},
		data () {
			return {
				disabled:false,
				test:false,
				portList:["ttyS0", "ttyS1", "ttyS2", "ttyS3"],
				modemList:['GPRS'],
				limitList:[300,500,800,1000],
				SMS:{
					status:'off',
					port:'ttyS0',
					modem:'GPRS',
					limit:300,
					number:0
				},
				SMSRules:{
					'number':[
						ValidRoleFactory.getValidNumberRoleForText(this.$t('AlarmSetting.SMS.Number')),
						ValidRoleFactory.getMobileRole(this.$t('AlarmSetting.SMS.Number'))
					]
				}
          }

		},
		mounted(){
			var $this = this;
			SMSService.getNotifySMS().then(function(res){
				$this.SMS.status = res.status;
				$this.SMS.port = res.port;
				$this.SMS.modem = res.modem;
				$this.SMS.limit = res.limit;
				$this.SMS.number = res.number;
				if($this.SMS.status == 'off'){
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
			testSMS(formName){
				var $this = this;
				this.$refs[formName].validate(function(valid){
					if(valid){
						$this.$refs.TestSMSDialog.sendSMS($this.SMS).then(
							function(res){
								SMSService.getNotifySMS().then(function(res){
									$this.SMS.status = res.status;
									$this.SMS.port = res.port;
									$this.SMS.modem = res.modem;
									$this.SMS.limit = res.limit;
									$this.SMS.number = res.number;
									if($this.SMS.status == 'off'){
										$this.test = true;
									} else {
										$this.test = false;
									}
								},function(error){
									$this.disabled = true;
								});
							},function(error){});
					}
				});
			},
			confirmSMS(formName){
				var $this = this;
				this.$refs[formName].validate(function(valid){
					if(valid || $this.SMS.status == 'off'){
						$this.$refs.TestSMSDialog.confirmSMS($this.SMS).then(function(res){
							SMSService.getNotifySMS().then(function(res){
								$this.SMS.status = res.status;
								$this.SMS.port = res.port;
								$this.SMS.modem = res.modem;
								$this.SMS.limit = res.limit;
								$this.SMS.number = res.number;
								if($this.SMS.status == 'off'){
									$this.test = true;
								} else {
									$this.test = false;
								}
							},function(error){
								$this.disabled = true;
							});
						},function(res){

						});
					}
				});
			}
	    }
	}
</script>
