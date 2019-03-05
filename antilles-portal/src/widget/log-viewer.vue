<style scoped>
.job-detail-log .el-row {
	margin-bottom: 10px;
}
</style>
<template>
	<div class='job-detail-log'>
		<el-row>
			<el-col :span="14">
				<file-select ref="fileSelect" type="file"
					:default-folder="innerWorkspace"
					v-model="innerFile">
				</file-select>
			</el-col>
			<el-col :span="10" align="right">
				<el-checkbox v-model="autoRefresh" @change='onAutoRefreshChange' unchecked>{{ $t("LogViewer.Auto.Refresh") }}</el-checkbox>
				<el-button
					@click="refreshLog(true)"
					:disabled="autoRefresh">
					{{ $t("LogViewer.Refresh") }}
				</el-button>
			</el-col>
		</el-row>
		<el-row>
			<textarea id="model-log" readonly @blur='modelLogBlur' ref="output" rows="25" style="width: 100%;overflow-y: scroll;resize:none;"></textarea>
		</el-row>
	</div>
</template>
<script>
	import JobService from '../service/job'
	import FileSelect from "../component/file-select"

	export default {
		data() {
			return {
				innerWorkspace: '',
				innerFile: '',
				autoRefresh: true,
				autoRefreshInterval: 10 * 1000,
				innerLines: '',
				lines: [],
				offset: 0,
				autoRefreshTimerId: 0,
				scrollHeight:0
			}
		},
		props: [
			"workspace",
			"defaultFile",
			'mappingPath'
		],
		watch: {
			innerFile(val, oldVal) {
				this.init();
			},
			defaultFile(val, oldVal) {
				this.innerFile = val;
			},
			$route(val, oldVal) {
				this.init();
			}
		},
		mounted() {
			if(this.workspace) {
				this.innerWorkspace = this.workspace;
			}
			if(this.defaultFile) {
				this.innerFile = this.defaultFile;
			}
			this.scrollHeight = this.$refs.output.scrollHeight - this.$refs.output.scrollTop;
		},
		beforeDestroy() {
			if(this.autoRefreshTimerId > 0) {
				clearTimeout(this.autoRefreshTimerId);
			}
		},
		components: {
			"file-select": FileSelect
		},
		methods: {
			init() {
				if(this.autoRefreshTimerId > 0) {
					clearTimeout(this.autoRefreshTimerId);
				}
				this.$refs.output.innerHTML = '';
				this.innerLines = '';
				this.lines = [];
				this.offset = 0;
				this.refreshLog();
			},
			refreshLog(isRefresh) {
				if(this.autoRefreshTimerId > 0) {
					clearTimeout(this.autoRefreshTimerId);
				}
				var filename = this.innerFile;
				// The backend only accept the relative directory base on MyFolder/ for SSRB
				// if(this.mappingPath) {
				// 		filename = this.innerFile.replace('MyFolder', this.mappingPath);
				// } else {
				// 		filename = this.innerFile.replace('MyFolder/', '');
				// }
				filename = this.innerFile.replace('MyFolder/', '');
				JobService.getJobLog(filename, this.offset).then((res) => {
					if(res.lines.length > 0){
						this.lines = this.lines.concat(res.lines);
						if (this.lines.length > 500) {
							this.lines.splice(0, this.lines.length - 500);
						}
						// if((this.autoRefresh && ((this.$refs.output.scrollHeight - this.$refs.output.scrollTop)
						// 												== this.scrollHeight || this.$refs.output.scrollTop == 0))
						// 		|| isRefresh){
						if(this.autoRefresh || isRefresh){
							this.offset = res.offset;
							this.scrollHeight = this.$refs.output.scrollHeight - this.$refs.output.scrollTop;
							this.$refs.output.innerHTML = this.lines.join('\n');
							// document.getElementById('model-log').innerText=document.getElementById('model-log').innerText+this.lines.join('\n');
							this.setScrollHeight();
						}
					}
					if(this.autoRefresh && this.autoRefreshInterval>0) {
						let self = this;
						this.autoRefreshTimerId = setTimeout(self.refreshLog, this.autoRefreshInterval);
					}
				}, (res) => {
					this.$message.error(res);
				});
			},
			onAutoRefreshChange(val) {
				if(val) {
					this.refreshLog();
				} else {
					if(this.autoRefreshTimerId > 0) {
						clearTimeout(this.autoRefreshTimerId);
					}
				}
			},
			modelLogBlur() {
				// if(this.$refs.output){
				// 	this.refreshLog(true);
				// }
			},
			setScrollHeight(){
				if(this.$refs.output.scrollTop == 0) {
					this.$refs.output.scrollTop = 9999;
				} else {
					this.$refs.output.scrollTop = this.$refs.output.scrollHeight;
				}
			}
		}
	}
</script>
