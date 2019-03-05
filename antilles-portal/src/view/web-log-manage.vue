<template lang="html">
	<div class="height--100 p-10">
		<div class="table-style p-20" style="height: 500px;text-align: center;">
			<div>
				<div style="margin-top: 100px;"><img src="../asset/image/weblog/log.png"></div>
				<div style="color: #333333;font-size: 16px;margin-bottom: 10px;">{{$t("Menu.WebLogManage")}}</div>
				<!-- <div class="welcome-user">{{$t("WebLog.Hint")}}</div> -->
				<el-button type="primary" @click="DownloadLog()">{{$t('Image.Download')}}
				</el-button>
			</div>
		</div>
	</div>
</template>

<script>
import WeblogService from './../service/web-log'
export default {
  methods:{
  	DownloadLog(){
  		WeblogService.downloadWebLog();
  	}
  }
}
</script>
