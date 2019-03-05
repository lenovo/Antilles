<style>
.wechat-erweima{
	max-width: 220px;
	min-width: 160px;
	max-height: 220px;
	min-height: 160px;
}

</style>
<template>
	<div>
		<el-row>
			<el-col :span="24">
				<div class="section">
					<el-form :model="wechat" ref="wechat">
						<div>
							<el-radio-group id="tid_notify-adapter-wechat-enable" v-model="wechat.status" :disabled="disabled" class="notify-email-radio notify-header-radio" size="mini">
								<el-radio-button label="on">ON</el-radio-button>
								<el-radio-button label="off">OFF</el-radio-button>
							</el-radio-group>
						</div>
						<div class="notify-email-img">
							<img src="./../../asset/image/notify/wechat.png" alt="">
							<div>{{$t('AlarmSetting.Title.Wechat')}}</div>
						</div>

						<el-form-item style="margin-top:40px;text-align:center;">
              <img v-if="getImage" class="wechat-erweima notify-wechat-qrcode" id="tid_notify-wechat-qrcode">
							<img :title="$t('AlarmSetting.Title.Wechat.Fail')" src="../../asset/image/notify/qr-error.png" v-else>
						</el-form-item>
						<el-form-item class="notify-footer" style="text-align: center;">
							<el-button id="tid_notify-adapter-wechat-test" type="primary" @click="testWechat('wechat')" :disabled="test"
							>{{$t("AlarmSetting.Button.Test")}}</el-button>
							<el-button id="tid_notify-adapter-wechat-confirm" type="primary" @click="confirmWechat('wechat')" :disabled="disabled">{{$t("AlarmSetting.Button.Confirm")}}</el-button>
						</el-form-item>
					</el-form>
				</div>
			</el-col>
		</el-row>
		<WechatDialog ref="WechatDialog" />
	</div>
</template>
<script>
	import ValidRoleFactory from '../../common/valid-role-factory'
	import WechatService from '../../service/notify-wechat'
	import WechatDialog from './notify-adapter-wechat-dialog'

	export default {
		components:{
			WechatDialog
		},
		data () {

			return {
				disabled:false,
				getImage:false,
				test:false,
				wechat:{
					status:'off'
				}
			}
		},
		mounted(){
			var $this = this;
			WechatService.getWechatImage().then(function(res){
				// cover blob image to base64 image url
				var fr = new FileReader();
				fr.onload = function(){
					var ab = this.result;
					var arr = new Uint8Array(ab);
					var raw = String.fromCharCode.apply(null, arr);
					var b64 = btoa(raw);
					var dataURL="data:image/jpeg;base64," + b64;
					document.querySelector(".notify-wechat-qrcode").src = dataURL;
				}
				fr.readAsArrayBuffer(res);
				// cover blob image to base64 image url
				$this.getImage = true;
			},function(error){
				$this.disabled = true;
			});
			WechatService.getWechat().then(function(res){
				$this.wechat.status = res.status;
				if($this.wechat.status == 'off'){
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
			testWechat(formName){
				this.$refs.WechatDialog.test(this.wechat);
			},
			confirmWechat(formName){
				var $this = this;
				$this.$refs.WechatDialog.confirmWechat($this.wechat).then(function(res){
					WechatService.getWechat().then(function(res){
						$this.wechat.status = res.status;
						if($this.wechat.status == 'off'){
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
		}
	}
</script>
