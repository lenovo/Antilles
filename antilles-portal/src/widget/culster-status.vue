<style media="screen">
.culsterstatus {
  flex: 0 0 auto;
  width: 100%;
  height: 50px;
  background-color: #343C4A;
  color: #fff;
}
.culsterstatus-cont {
  width: 100%;
  height: 100%;
}
.culsterstatus-cont span {
  height: 100%;
  background: #374151;
}
.culsterstatus-title {
  line-height: 50px;
  text-indent: 1.8em;
}
.culsterstatus-statusmin {
  display: block;
  width: 16px;
  height: 16px;
  position: relative;
  top: 17px;
  left: 24px;
}
.culsterstatus-statusmax i{
  float: right;
  width: 5px;
  height: 25px;
  margin-top: 10px;
  margin-right: 5px;
}
.culsterstatus-el-poover{
  background:#374151;
  color:#999;
  text-align: left;
  margin:0;
  padding: 0;
  border:0;
}
.culsterstatus-poover-ul li{
  padding: 10px;
}
.culsterstatus-poover-ul i{
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 5px;
  margin-right: 10px;
}
.status-normal {
  background: #4CC1B2;
}
.status-error {
  background: #FF5454;
}
</style>
<template>
  <div class="culsterstatus" v-if="notStaff">
    <el-popover  popper-class='culsterstatus-el-poover' visible-arrow=""
    ref="popovercolony" placement="right" title="" trigger="hover">
      <ul class="culsterstatus-poover-ul">
        <li><i :class="getStatusClass([sheduler])"></i><span>{{ $t('Cluster.Sheduler') }}</span></li>
        <li><i :class="getStatusClass([parallel])"></i><span>{{ $t('Cluster.ParallelFileSystem') }}</span></li>
      </ul>
    </el-popover>
    <div v-if="isMinMenu" class="culsterstatus-cont" v-popover:popovercolony>
      <i class="culsterstatus-statusmin" :class="getStatusClass([sheduler,parallel])"></i>
    </div>
    <div v-else class="culsterstatus-cont" v-popover:popovercolony>
      <el-col :span="20" class="culsterstatus-title">{{ name? name:$t('Cluster.name') }}</el-col>
      <el-col :span="4" class="culsterstatus-statusmax">
        <i :class="getStatusClass([sheduler,parallel])"></i>
      </el-col>
    </div>
  </div>
</template>
<script type="text/javascript">
import MonitorService from './../service/monitor-data'
export default {
  data () {
    return {
      isMinMenu: gApp.isCollapse,
      notStaff: this.$store.state.auth.access != 'staff',
      sheduler: '',
      parallel: '',
      name: this.$t('Cluster.name'),
      refreshTimeout: null,
      refreshInterval: 30000
    }
  },
  mounted () {
    var _this = this
    gApp.$watch('isCollapse',function (newValue, oldValue) {
      _this.isMinMenu = newValue
    });
    this.init();
  },
  beforeDestroy() {
    clearTimeout(this.refreshTimeout)
  },
  methods:{
    init() {
      MonitorService.getServiceStatus().then((res) => {
        this.sheduler = res.shedulerStatus;
        this.parallel = res.fileSystemStatus;
        this.name = res.name;
        if(this.notStaff) {
          this.refreshTimeout = setTimeout(() => {
            this.init();
          }, this.refreshInterval)
        }
      }, (res) => {

      })

    },
    getStatusClass(status) {
      if(status.includes('inactive')) {
        return 'status-error';
      } else if(status.includes('active')){
        return 'status-normal';
      } else {
        return '';
      }
    }
  }
}
</script>
