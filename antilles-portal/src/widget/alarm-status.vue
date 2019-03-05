<style media="screen">
.alarmstatus {
  cursor: pointer;
}
.alarmstatus-label{
  width: 200px;
  height: 100px;
  padding:0;
  margin:0;
  font-size:14px;
  color:#333;
}
.alarmstatus-item i {
  font-size: 20px;
}
.alarmstatus-icon-default {
  color: #999;
}
.alarmstatus-icon-yello {
  color: #ffc107;
}
.alarmstatus-list {
  box-sizing: border-box;
  width: 100%;
  height: 50px;
  padding:0 20px;
}
.alarmstatus-list:last-child{
  border-top:1px solid #eee;
}
.alarmstatus-list-title{
  height: 30px;
  padding:20px 0 0;
}
.alarmstatus-title-left {
  display: inline-block;
}
.alarmstatus-title-right{
  display: inline-block;
  color:#40aaff;
  float: right;
  cursor: pointer;
}
.alarmstatus-list i{
  font-style: normal;
}
.alarmstatus-switch{
  float: right;
}
</style>
<template>
  <span class="alarmstatus" v-if="notStaff" :title='$t("Alarm")'>
    <el-popover ref="popoverAlarm" placement="bottom" title=""
    popper-class="alarmstatus-label"
    trigger="hover">
      <ul class="alarmstatus-cont">
        <li class="alarmstatus-list">
          <div class="alarmstatus-list-title">
            <span class="alarmstatus-title-left">{{ $t('Alarm') }}</span>
            <span id="tid_alarm-jump-btn" class="alarmstatus-title-right" @click='toAlarmView'>{{ $t('Alarm.ViewAll') }}</span>
          </div>
        </li>
        <li class="alarmstatus-list">
          <div class="alarmstatus-list-title">
          <i>{{ $t('Alarm.Voice') }}</i>
          <span class="alarmstatus-switch">
              <el-switch id="tid_alarm-sound-switch" v-model="alarmSwitch" @change='alarmSoundSwitch'></el-switch>
          </span>
          </div>
        </li>
      </ul>
    </el-popover>
    <el-badge :value="alarmData.count" :hidden='!alarmData.count' :max="99" class="alarmstatus-item" v-popover:popoverAlarm>
      <i :class="alarmData.count>0?'el-erp-alerts alarmstatus-icon-yello':'el-erp-noalerts alarmstatus-icon-default'"></i>
    </el-badge>
    <audio src="../../static/audio/alarm.mp3" ref='alarmAudio'></audio>
    <!-- <alarm-status-refresh :alarm-sound-data='alarmData' :interval='refreshInterval' ></alarm-status-refresh> -->
  </span>
</template>
<script type="text/javascript">
  // import AlarmStatusRefresh from './alarm-status/alarm-status-refresher'
  import AlarmService from './../service/alarm'
  export default {
    data() {
      return {
        notStaff: this.$store.state.auth.access != 'staff',
        alarmSwitch: this.$store.getters['settings/isSound'],
        refreshInterval: 30000,
        refreshTimeout: null,
        alarmData: {
          count: 0,
          isSound: false
        }
      }
    },
    components: {
      // 'alarm-status-refresh': AlarmStatusRefresh
    },
    mounted() {
      this.init();
      // this.$watch('alarmData.count', (val, oldVal) => {
      //   if(this.notStaff && this.alarmData.isSound && this.alarmSwitch) {
      //     this.$refs.alarmAudio.play();
      //   }
      // })
    },
    beforeDestroy() {
      clearTimeout(this.refreshTimeout);
      this.refreshTimeout = null;
    },
    watch: {
      alarmData(val, oldVal) {
        if(this.notStaff && this.alarmData.isSound && this.alarmSwitch) {
          this.$refs.alarmAudio.play();
          setTimeout(()=>{this.$refs.alarmAudio.load()},3000)
        }
      }
    },
    methods: {
      init() {
        if(this.notStaff) {
          AlarmService.getAlarmSound().then((res) => {
            // this.alarmData.count = res.count;
            // this.alarmData.isSound = res.isSound;
            this.alarmData = res;
            this.refreshTimeout = setTimeout(() => {
              this.init();
            }, this.refreshInterval)

          }, (res) => {
            this.$message(res)
          })
        }

      },
      toAlarmView() {
        this.$router.push({path: '/main/alarm-manage'})
      },
      alarmSoundSwitch() {
        // this.alarmSwitch?this.$refs.alarmAudio.play():"";
        this.$store.dispatch('settings/setAlarmSound',this.alarmSwitch);
      }

    }
  }
</script>
