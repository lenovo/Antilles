<style>
	.MonitorGroupAction{
    margin-bottom:20px;
		background: #fff;
	}
	.group-view {
		display: flex;
		flex-direction: column;
	}
</style>
<template>
	<div class="height--100 group-view p-10">
      <div class="MonitorGroupAction p-20">
        <el-select id="tid_monitor-groups-group" v-model.number="nodeGroupId" @change="onNodeGroupChange">
          <el-option
              v-for="group in nodeGroups"
              :key="group.id"
              :label="group.name"
              :value="group.id">
          </el-option>
        </el-select>
        <el-button-group style="margin-left:35px;" v-if="nodeGroups.length > 0">
          <el-button id="tid_monitor-groups-list" :type="displayedContentType == 'list' ? 'primary' : 'normal'" @click="onActionButtonClick('list')">{{$t("NodeGroup.Tab.Title.List")}}</el-button>
          <el-button id="tid_monitor-groups-trend" :type="displayedContentType == 'trend' ? 'primary' : 'normal'" @click="onActionButtonClick('trend')">{{$t("NodeGroup.Tab.Title.Trend")}}</el-button>
          <el-button id="tid_monitor-groups-healthy" :type="displayedContentType == 'healthy' ? 'primary' : 'normal'" @click="onActionButtonClick('healthy')">{{$t("NodeGroup.Tab.Title.Health")}}</el-button>
        </el-button-group>
      </div>

			<div class="table-top-manage" v-if="nodeGroups.length > 0">
        <group-list
            :node-external-filter="nodeExternalFilter"
            v-if="displayedContentType == 'list'">
        </group-list>
        <group-trend
            :current-selected-group-id="nodeGroupId"
            v-if="displayedContentType == 'trend'">
        </group-trend>
        <group-health
            :current-selected-group-id="nodeGroupId"
            v-if="displayedContentType == 'healthy'">
        </group-health>
      </div>
	</div>
</template>
<script>
  import GroupList from './monitor-groups/group-list.vue'
	import GroupTrend from './monitor-groups/group-trend.vue'
	import GroupHealth from './monitor-groups/group-health.vue'

  import NodeGroupService from '../service/node-group'
  import NodeService from '../service/node'

  export default {
    data() {
      return {
        nodeExternalFilter: {},
        displayedContentType: 'list',
        nodeGroupId: '',
        nodeGroups: []
      }
    },
    components: {
      'group-list': GroupList,
			'group-trend': GroupTrend,
			'group-health': GroupHealth
    },
    mounted() {
      this.initNodeGroupOptions();
    },
    methods: {
      onActionButtonClick(type){
        this.displayedContentType = type;
      },
      initNodeGroupOptions(){
        NodeGroupService.getAllNodeGroups().then((res) => {
					if(res.length > 0) {
						this.nodeGroupId = res[0].id;
					}
					this.nodeGroups = res;
					this.onNodeGroupChange();
        }, (res) => {
					this.$message.error(res);
        })
      },
      onNodeGroupChange() {
				var nodeGroupName = '';
				for(var i=0; i<this.nodeGroups.length; i++) {
					if(this.nodeGroups[i].id == this.nodeGroupId) {
						nodeGroupName = this.nodeGroups[i].name;
					}
				}
        this.nodeExternalFilter = {
          groups: {
            values: [nodeGroupName],
            type: "in"
          }
        };
      }
    }
  }
</script>
