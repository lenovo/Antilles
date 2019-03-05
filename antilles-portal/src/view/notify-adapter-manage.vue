<style>
	.notify-content {
		background: #fff;
		padding: 20px;
	}
	.notify-header-radio {
		position: absolute;
		right: 0;
	}
	.notify-email-img {
		text-align: center;
	}
</style>
<template>
	<div class="p-10">
		<el-row  type="flex" :gutter="20" style="flex-wrap: wrap;">
			<el-col :xs="24" :sm="24" :md="12" :lg="8">
				<MailSetting class="table-style notify-content"></MailSetting>
			</el-col>
			<el-col :xs="24" :sm="24" :md="12" :lg="8">
				<SmsSetting class="table-style notify-content"></SmsSetting>
			</el-col>
			<el-col :xs="24" :sm="24" :md="12" :lg="8">
				<WechatSetting class="table-style notify-content"></WechatSetting>
			</el-col>
		</el-row>
	</div>
</template>
<script>
	import MailSetting from './notify-adapter-manage/notify-adapter-email'
	import SmsSetting from './notify-adapter-manage/notify-adapter-sms'
	import WechatSetting from './notify-adapter-manage/notify-adapter-wechat'

	export default {
		components: {
			MailSetting,
			SmsSetting,
			WechatSetting
		}
	}
</script>
