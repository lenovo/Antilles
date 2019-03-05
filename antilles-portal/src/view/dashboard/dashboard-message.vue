<style lang="css">
  .dashboard-message-left{
    float: left;
  }
  .dashboard-message-right{
    float: right;
  }
  .dashboard-message-btn {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 5px;
    margin-right: 5px;
    cursor: pointer;
  }
  .message-color-alarm {
    background-color: #FF5454;
  }
  .message-color-warn {
    background-color: #F2B93F;
  }
  .message-color-info {
    background-color: #35C5AF;

  }
  .dashboard-message-card {
    padding: 15px 20px;
    background: #F8F8F8;
    display: flex;
    flex-direction: column;
    color:#666;
    font-size:12px;
  }
  .dashboard-message-line{
    width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;

  }
  .dashboard-message-name {

  }
  .dashboard-message-target {
    font-style: normal;
    border-radius: 2px;
    padding: 2px 4px;
    color: #fff;
  }

</style>
<template lang="html">
  <div id="tid_dashboard-message" class="dashboard-message">
    <el-row class="dashboard-message-title margin-bottom-20">
        <span class="dashboard-message-left">{{$t('Dashboard.Message.title')}}</span>
        <!-- <span class="dashboard-message-right">
          <i class="dashboard-message-btn message-color-alarm"></i>
          <i class="dashboard-message-btn message-color-warn"></i>
          <i class="dashboard-message-btn message-color-info" style="margin-right: 0;"></i>
        </span> -->
    </el-row>
    <div class="dashboard-message-contenter">
      <ul v-for='(item, index) in messageData' class="dashboard-message-card margin-bottom-20" :key='index'>
        <li class="dashboard-message-line" style="margin-bottom:10px;">
          <span class="dashboard-message-name dashboard-message-left">{{item.text}}</span>
          <!-- <i class="dashboard-message-target dashboard-message-right" :class="'message-color-'+item.level">{{$t('Dashboard.Message.Levle.' + item.level)}}</i> -->
        </li>
        <li class="dashboard-message-line">
          <span class="dashboard-message-time dashboard-message-right">{{item.time}}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import Format from './../../common/format'
export default {
  data() {
    return {
      messageData: []
    };
  },
  props: [
    'initData'
  ],
  mounted() {
    this.init();
  },
  watch: {
    initData(val, oldVal) {
      this.init();
    }
  },
  methods: {
    init() {
      if(this.initData && this.initData != []) {
        this.messageData = [];
        this.initData.forEach((item) => {
          this.messageData.push({
            text: this.getMessageText(item),
            time: Format.formatDateTime(item.actionTime)
          })
        })
      }
    },
    getMessageText(item) {
      var text = this.$t('Operation.Module.' + item.module) + ' ';
      if(item.target.length > 1) {
        for(var i=0;i<item.target.length;i++) {
          if(i<2){
            text += item.target[i].name + ', ';
          } else if(i==2){
            text += item.target[i].name + ', ... ';
          } else {
            break
          }
        }

      } else if(item.target.length = 1){
        text += item.target[0].name + ' ';
      }
      text += this.$t('Operation.Module.' + item.action);
      return text;
    }
  }
}
</script>
