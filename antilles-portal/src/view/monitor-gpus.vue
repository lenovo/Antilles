<style>
	.MonitorGroupAction{
    margin-bottom:20px;
		background: #fff;
	}
	.MonitorGroupAction .el-col {
		margin-top: 20px;
	}
	.gpus-view {
		display: flex;
		flex-direction: column;
	}
	.gpusView-content {
		background: #fff;
		position: relative;
	}
	.gpus-controlRange {
		display: flex
	}
	.controlRange {
		width: 100%;
		margin: 0 10px;
	}
	.controlRangeMin, .controlRangeMax {
		line-height: 38px;
	}
	.controlRangeMin {
		margin-right: 5px;
	}
	.controlRangeMax {
		margin-right: 20px;
	}
	.ColorInversion {
		padding-top: 8px;
	}
	.gpusView-content .gpu-used-label {
		height: 20px;
    padding-top: 20px;
    padding-right: 20px;
	}
	.gpusView-content .gpu-u-inner {
	  text-align: center;
		width: 70px;
	  height: 20px;
    line-height: 20px;
		background: #f8f8f8;
	  border-radius: 4px;
		float: right;
	}
	.gpusView-content .gpu-u-pic {
	  background: #6bcb01;
	  display: inline-block;
	  width: 12px;
	  height: 12px;
	  border-radius: 4px;
	  transform: translateY(10%);
	}
	.gpusView-content .gpu-u-word {
	  display: inline-block;
	  font-size: 12px;
	  transform: translateY(10%);
	  height: 12px;
	  color: #999999;
	}
	.gpusView-content-title {
		position: absolute;
		padding-top: 20px;
		padding-left: 20px;
	}
	.gpusView-content-title h3{
		color: #333;
		font-weight: inherit;
	}
</style>
<template>
	<div class="height--100 gpus-view p-10">
      <div class="MonitorGroupAction" style="padding: 0 20px 20px">
				<el-row>
				    <el-col :lg="6" :md="8" :sm="24" :xs="24">
							<el-select id="tid_monitor-groups-group"  v-model="nodeGroupId" @change="onNodeGroupChange">
								<el-option
										v-for="group in nodeGroups"
										:key="group.id"
										:label="group.name"
										:value="group.id">
								</el-option>
							</el-select>

				    </el-col>
						<el-col :lg="8" :md="16" :sm="24" :xs="24">
							<el-radio-group id="tid_monitor-gpus-type" v-model="selected"  @change='onViewTypeChange'>
								<el-radio-button label="util">{{$t("NodeGpus.Tab.Title.Util")}}</el-radio-button>
								<el-radio-button label="memory">{{$t("NodeGpus.Tab.Title.Mem")}}</el-radio-button>
								<el-radio-button label="temperature">{{$t("NodeGpus.Tab.Title.Temp")}}</el-radio-button>
							</el-radio-group>
						</el-col>
						<el-col :lg="10" :md="18" :sm="24" :xs="24" class="gpus-controlRange">
							<div class="controlRangeMin">
								{{$t('NodeGpus.ControlRange.Min', {'unit': controlRangeUnit})}}
							</div>
							<div class="controlRange">
								<el-slider
									:class="colorInversion?'color-back':'color-just'"
									v-model="controlRange"
									@change='onControlRangeChange'
									range
									:max="100">
								</el-slider>
							</div>
							<div class="controlRangeMax">
								{{$t('NodeGpus.ControlRange.Max', {'unit': controlRangeUnit})}}
							</div>
							<div class="ColorInversion">

								<el-checkbox v-model="colorInversion" @change='onColorInversionChange'>{{$t('NodeGpus.Color.Inversion')}}</el-checkbox>
							</div>
						</el-col>
				</el-row>
      </div>

			<div class="gpusView-content">
				<div class="gpusView-content-title">
					<h3>{{$t(`NodeGpus.Content.Title.${selected}`)}}</h3>
				</div>
				<div class="gpu-used-label">
					<div class="gpu-u-inner">
						<span class="gpu-u-pic"></span>
						<span class="gpu-u-word">{{$t('NodePanel.Gpu.Used')}}</span>
					</div>
				</div>
				<monitor-node-gpus
					:monitor-nodes='nodes'
					:value-type='selected'
					:page-offset='offset'
					:control-range='controlRange'
					:color-inversion='colorInversion'
					@offset-change='onOffsetChange'></monitor-node-gpus>

      </div>
	</div>
</template>
<script>
	import MonitorNdoeGpus from '../widget/monitor-node-gpus'
  import NodeGroupService from '../service/node-group'
	import MonitorService from '../service/monitor-data'

  export default {
    data() {
      return {
				nodeGroupId: '',
        nodeGroups: [],
				selected: 'util',
				nodes: [],
				offset: {
					total: 0,
					pageSize: 24,
					currentPage: 1,
				},
				controlRange: this.stringToNumberArr(this.$store.getters['settings/getGpuutil'].split(',')),
				colorInversion: this.$store.getters['settings/getGpuutilColor'],
				controlRangeUnit: '%',
				refreshTimeout: null,
				refreshInterval: 30000
      }
    },
    components: {
			'monitor-node-gpus': MonitorNdoeGpus
    },
		beforeDestroy() {
			clearTimeout(this.refreshTimeout);
		},
    mounted() {
			NodeGroupService.getAllNodeGroups().then((res) => {
				if(res.length > 0) {
					this.nodeGroupId = res[0].id;
				}
				this.nodeGroups = res;
				this.refresh(true);
			}, (res) => {
				this.$message.error(res);
			})
    },
    methods: {
			refresh(interval) {
				var $this = this;
				MonitorService.getNodeGpuDataByGroup(this.nodeGroupId,this.selected , this.offset).then((res) => {
					$this.nodes = res.nodesGpus;
					var offset = {
						total: res.total,
						pageSize: res.pageSize,
						currentPage: res.currentPage,
					}
					$this.offset = offset;

					if(interval) {
						$this.refreshTimeout = setTimeout(() => {
							$this.refresh(true);
						}, $this.refreshInterval)
					}
				})
			},
			onNodeGroupChange() {
				this.offset = {
					total: 0,
					pageSize: 24,
					currentPage: 1,
				}
				this.refresh();
			},
			onViewTypeChange(val) {
				this.controlRangeUnit = val == 'temperature'?'℃':'%';
				this.controlRange = this.stringToNumberArr(this.$store.getters[`settings/getGpu${val}`].split(','));
				this.colorInversion = this.$store.getters[`settings/getGpu${val}Color`];
				this.refresh();
			},
			onOffsetChange(val) {
				this.offset = val;
				this.refresh();
			},
			onControlRangeChange(val) {
				if(val) {
	        this.$store.dispatch(`settings/setGpu${this.selected}`, val.join())
	      }
			},
			onColorInversionChange(val) {
				this.$store.dispatch(`settings/setGpu${this.selected}Color`, this.colorInversion)
			},
			stringToNumberArr(val) {
				var arr = [];
				val.forEach((str) => {
					arr.push(Number(str));
				})
				return arr;
			}
    }
  }
</script>
