<style media="screen">
	.vnc-cannot-content {
		background: #fff;
		padding: 100px 0 200px;
		text-align: center;
	}
	.vnc-cannot-tip {
		margin-top: 20px;
		font-size: 20px;
	}
</style>
<template>
	<div class="height--100 p-10">
		<div class="">
			<composite-table v-show='autoRefresh' id="tid_vnc-table" ref="VNCTable"
				:table-data-fetcher="tableDataFetcher"
				@table-data-fetch-error='tableDataFetchError'
				:default-sort="{ prop: 'name', order: 'ascending'	}"
				:search-enable="true"
				:search-props="['name' , 'username']"
				:current-page="1"
				:page-sizes="[10, 20, 40, 50]"
				:page-size="10"
				:total="0"
				:auto-refresh='autoRefresh'
				:show-error-message='false'>
				<ul slot="controller" class="composite-table-controller">
					<el-button style="opacity: 0;"></el-button>
				</ul>
				<el-table-column
		      prop="name"
		      :label="$t('VNC.Title.Name')"
		      sortable="custom"
		     ></el-table-column>
				<el-table-column
		      prop="host"
		      :label="$t('VNC.Title.Host')"
		      sortable="custom"
					align="center"
		      ></el-table-column>
				<el-table-column
		      prop="port"
		      :label="$t('VNC.Title.Port')"
		      sortable="custom"
					align="center"
		      ></el-table-column>
				<el-table-column
					prop="username"
					:label="$t('VNC.Title.Username')"
					align='center'
					sortable="custom"
					></el-table-column>
				<el-table-column
					prop="pid"
					:label="$t('VNC.Title.Pid')"
					align='center'
					sortable="custom"
					></el-table-column>
				<el-table-column
					prop="index"
					:label="$t('VNC.Title.Index')"
					align='center'
					sortable="custom"
					></el-table-column>
				<el-table-column
					prop="status"
					:label="$t('VNC.Title.Status')"
					align='center'
					sortable="custom"
					></el-table-column>
				<el-table-column
					prop="operation"
					:label="$t('VNC.Title.Operation')"
					align='center'
					sortable="custom"
					>
					<template slot-scope="scope">
						<el-button size="small" @click="OpenVNC(scope.row)" class="table-icon-button no-border" :title="$t('VNC.Button.Open')">
						<i class="el-erp-vnc_open"></i></el-button>
						<el-button v-if="$store.state.auth.role == 'admin'" size="small" class="table-icon-button no-border"  @click="DeleteVNC(scope.row)" :title="$t('Alarm.Policy.Button.Delete')">
						<i class="el-erp-delete"></i></el-button>
					</template>
				</el-table-column>
			</composite-table>
			<div v-if='!autoRefresh' class="vnc-cannot-content">
				<img class="vnc-cannot-img" src="../asset/image/vnc-cannot.png">
				<p class="vnc-cannot-tip">{{$t('Error.RestAPI.Unavailable')}}</p>
			</div>
			<VNCDialog ref="DeleteVNCDialog" />
		</div>
	</div>
</template>
<script>
	import CompositeTable from '../component/composite-table'
	import VNCService from '../service/vnc'
	import VNCDialog from './vnc/vnc-dialog'
	import Format from '../common/format'

	export default {
		components: {
			'composite-table': CompositeTable,
			VNCDialog
		},
		data(){
			var username = this.$store.state.auth.access == 'admin'?'':this.$store.state.auth.username;
			return {
				tableDataFetcher: VNCService.getVNCTableDataFetcher(username),
				autoRefresh: 30*1000
			}
		},
		mounted(){

		},
		beforeDestroy(){

		},
		methods:{
			OpenVNC(data){
				var origin = location.origin;
        var params = {
            autoconnect: '1',
            // path: '/websockify',
            port: '443',
						encrypt: true,
            token: data.id,
        }
        var query_params = [];
        for( var k in params ){
            query_params.push(k+'='+params[k]);
        }
        var query = query_params.join('&')

        var target = origin+'/novnc/?'+query
        window.open(target);
			},
			DeleteVNC(data){
				var $this = this;
				this.$refs.DeleteVNCDialog.deleteVNC(data).then(function(res){
					$this.$refs.VNCTable.fetchTableData(true);
				},function(error){

				});
			},
			tableDataFetchError(err) {
				if(err.status == 502){
					this.autoRefresh = false;
				} else {
					this.$message.error(err.message);
				}
			}

		}
	}
</script>
